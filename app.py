import base64
from datetime import datetime, timezone
import os
import pandas as pd
import streamlit as st
import time

import src


DATA_DIR = os.path.abspath('./data')
BUSD_DATA = pd.read_csv(os.path.join(DATA_DIR, 'pool_BNB.BUSD-BD1.csv'))


# Increace width of the main page container
# reduce size of tables and matplotlib graphics
# https://discuss.streamlit.io/t/where-to-set-page-width-when-set-into-non-widescreeen-mode/959
st.markdown(
    f'''
        <style>
            .reportview-container .main .block-container {{
                max-width: 1000px;
            }}
            .stTable {{
                max-width: 400px;
            }}
            .image-container {{
                max-width: 600px;
            }}
            img {{
                max-width: 100%
            }}
        </style>
    ''',
    unsafe_allow_html=True
)


#-------------------------------------------------------------------------------
# Default page content - FAQs
#-------------------------------------------------------------------------------

prices = []
for asset in src.assets:
    data = pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv').format(asset['chain'], asset['symbol']))
    rune_price, asset_price = src.get_prices(data.iloc[-1], BUSD_DATA.iloc[-1])

    if len(prices) == 0:
        prices.append({
            'Chain': 'BNB',
            'Symbol': 'RUNE-B1A',
            'Name': 'Rune',
            'Price ($)': rune_price
        })

    prices.append({
        'Chain': asset['chain'],
        'Symbol': asset['symbol'],
        'Name': asset['name'],
        'Price ($)': asset_price
    })

prices = pd.DataFrame(prices, columns=['Chain', 'Symbol', 'Name', 'Price ($)'])


faq = [
    st.markdown('![header-image](https://via.placeholder.com/1000x200.png?text=header+image+here+1000x200)'),
    st.title('This tool helps you evaluate historical performance of your [THORChain](https://thorchain.org/) liquidity pools and predict their future returns.'),
    st.text(''),
    st.markdown('''To view the past performance of your LP, fill out the first section of the left panel, then hit "View".

To predict the returns of your LP in the future, fill out **both** sections, and hit "Predict". The algorithm will extrapolate the ROI
of your pool into your selected date, and substract impermanent loss based on your target asset prices.'''),
    st.header('Current Asset Prices'),
    st.text(''),
    st.dataframe(prices),
    st.header('About'),
    st.text(''),
    st.markdown('''Created by [@Larrypcdotcom](https://twitter.com/Larrypcdotcom)

[Code available](https://github.com/Larrypcdotcom/thorchain-lp-data) under MIT license.
For bug reports and feature requests, please [create an issue](https://github.com/Larrypcdotcom/thorchain-lp-data/issues/new) on GitHub.

Interested in contributing? Join the **THORChain Community Apps Team** [Discord channel]().''')
]


def _clear_faq():
    print('faq', faq)
    for widget in faq:
        widget.empty()


#-------------------------------------------------------------------------------
# Sidebar
#-------------------------------------------------------------------------------

st.sidebar.header('View Past Performance')

investment = {
    'asset': st.sidebar.selectbox(
        label='Pool',
        options=src.assets,
        format_func=lambda asset: '{} ({}.{})'.format(asset['name'], asset['chain'], asset['symbol']),
        key='asset_0'
    ),
    'amount': st.sidebar.number_input(
        label='Amount invested ($)',
        min_value=0.,
        format='%.2f',
        key='amount_0'
    ),
    'time': st.sidebar.date_input(
        label='Date invested',
        min_value=datetime.fromtimestamp(1598952349)
    )
}

view_btn = st.sidebar.button('View', key='view_btn')

st.sidebar.header('Predict Future Returns')

pred_params = {
    'future_date': st.sidebar.date_input(
        label='Predict results on...',
        min_value=datetime.now()
    ),
    'num_days_for_avg': st.sidebar.selectbox(
        label='Use average pool ROI of the last...',
        options=[3, 7, 14, 30],
        format_func=lambda num_days: str(num_days) + ' days' if num_days > 1 else ' day'
    ),
    'rune_target': st.sidebar.number_input(
        label='Target price for RUNE ($)',
        min_value=0.,
        format='%.2f',
        key='target_rune'
    ),
    'asset_target': st.sidebar.number_input(
        label='Target price for pool asset ($)',
        min_value=0.,
        format='%.2f',
        key='target_asset'
    )
}

predict_btn = st.sidebar.button('Predict', key='predict_btn')

st.sidebar.text('')
st.sidebar.text('')
st.sidebar.text('')
st.sidebar.info('Based on data last updated at **{}**'.format(
    datetime.fromtimestamp(BUSD_DATA.iloc[-1]['timestamp']).strftime("%m/%d/%Y %H:%M:%S UTC")
))


#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------


# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806/2
def _get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a class="streamlit-button small-button primary-button" href="data:file/csv;base64,{b64}">Download data as CSV</a>'


def _out_or_under(value, baseline):
    return 'outperforms' if value >= baseline else 'underperforms'


def _roi_to_apy(start_time, end_time, roi):
    num_days = (end_time - start_time) / 60 / 60 / 24
    return (1 + roi) ** (365 / num_days) - 1


def _get_percent_change(value, baseline, show_sign=True):
    if show_sign:
        sign = '+' if value >= baseline else '-'
    else:
        sign = ''

    if baseline == 0:
        percentage = abs(value) * 100
    else:
        percentage = abs(value / baseline - 1) * 100

    color = 'green' if value >= baseline else 'red'
    return '<span style="color:{}">{}{:.1f}%</span>'.format(color, sign, percentage)


#-------------------------------------------------------------------------------
# Button actions
#-------------------------------------------------------------------------------

if view_btn:
    _clear_faq()

    user_data = src.calculate_user_data(
        amount_invested=investment['amount'],
        time_invested=datetime.combine(investment['time'], datetime.min.time()).timestamp(),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(investment['asset']['chain'], investment['asset']['symbol']))),
        busd_data=BUSD_DATA
    )

    baselines = src.calculate_baselines(user_data)

    breakdown = src.calculate_gains_breakdown(user_data)

    st.title('Value of Investment')
    st.text('')  # add some vertical space

    st.markdown('The current value of your investment is **${:,.2f}** (**{}**)'.format(
        user_data.iloc[-1]['total_value'],
        _get_percent_change(user_data.iloc[-1]['total_value'], investment['amount']),
    ), unsafe_allow_html=True)

    st.markdown('If you had passively held **RUNE**, you would have **${:,.2f}** (LP {} by **{}**)'.format(
        baselines.iloc[-1]['hold_rune'],
        _out_or_under(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_rune']),
        _get_percent_change(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_rune'], show_sign=False)
    ), unsafe_allow_html=True)

    st.markdown('If you had passively held **{}**, you would have **${:,.2f}** (LP {} by **{}**)'.format(
        investment['asset']['symbol'],
        baselines.iloc[-1]['hold_asset'],
        _out_or_under(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_asset']),
        _get_percent_change(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_asset'], show_sign=False)
    ), unsafe_allow_html=True)

    st.text('')
    st.altair_chart(src.plot_value_of_investment(user_data, baselines), use_container_width=True)

    st.title('Pool Rewards')
    st.text('')

    st.markdown('''Compared to holding 50:50 **RUNE** & **{}** passively, you gained **{}** from fees & rewards accrued,
    and lost **{}** due to [impermanent loss (IL)](https://pintail.medium.com/understanding-uniswap-returns-cc593f3499ef).
    Overall, LP **{}** HODL by **{}**.'''.format(
        investment['asset']['symbol'],
        _get_percent_change(user_data.iloc[-1]['fee_accrual'], 0., show_sign=False),
        _get_percent_change(user_data.iloc[-1]['imperm_loss'], 0., show_sign=False),
        _out_or_under(user_data.iloc[-1]['total_gains'], 0.),
        _get_percent_change(user_data.iloc[-1]['total_gains'], 0., show_sign=False)
    ), unsafe_allow_html=True)

    st.markdown('''Extrapolating to a year, compounded daily, the fee APY (not including IL) is approximately **{}**.'''.format(
        _get_percent_change(_roi_to_apy(
            start_time=user_data.loc[0]['timestamp'],
            end_time=user_data.iloc[-1]['timestamp'],
            roi=user_data.iloc[-1]['fee_accrual'],
        ), 0., show_sign=False)
    ), unsafe_allow_html=True)

    st.text('')
    st.altair_chart(src.plot_pool_rewards(user_data), use_container_width=True)

    st.title('Gains/Losses Breakdown')
    st.text('')

    st.markdown('''You {} **${:,.2f}** (**{}**) due to **RUNE** price going {}, and {} **${:,.2f}** (**{}**) due to **{}** price going {}.'''.format(
        'gained' if breakdown['rune_movement']['value'] >= 0 else 'lost',
        abs(breakdown['rune_movement']['value']),
        _get_percent_change(breakdown['rune_movement']['percentage'], 0.),
        'up' if breakdown['rune_movement']['value'] >= 0 else 'down',
        'gained' if breakdown['asset_movement']['value'] >= 0 else 'lost',
        abs(breakdown['asset_movement']['value']),
        _get_percent_change(breakdown['asset_movement']['percentage'], 0.),
        investment['asset']['symbol'],
        'up' if breakdown['asset_movement']['value'] >= 0 else 'down',
    ), unsafe_allow_html=True)

    st.markdown('''You gained **${:,.2f}** (**{}**) from fees & LP rewards, and lost **${:,.2f}** (**{}**) due to impermanent loss.'''.format(
        breakdown['fees']['value'],
        _get_percent_change(breakdown['fees']['percentage'], 0.),
        abs(breakdown['imp_loss']['value']),
        _get_percent_change(breakdown['imp_loss']['percentage'], 0.),
    ), unsafe_allow_html=True)

    st.markdown('Overall, you are {} **${:,.2f}** (**{}**) compared to your initial investment.'.format(
        'up' if breakdown['total']['value'] >= 0 else 'down',
        abs(breakdown['total']['value']),
        _get_percent_change(breakdown['total']['percentage'], 0.)
    ), unsafe_allow_html=True)

    st.text('')

    # For this one, pyplot actually looks better than altair
    # st.altair_chart(src.plot_gains_breakdown(breakdown), use_container_width=True)
    st.pyplot(src.plot_gains_breakdown_pyplot(breakdown))

    # Let user download their data as a CSV which can be imported to Skittles
    # https://twitter.com/mehowbrains/status/1317291144640974849
    # Doesn't work very well yet!!!
    # st.markdown(_get_table_download_link(user_data), unsafe_allow_html=True)


if predict_btn:
    _clear_faq()

    user_data = src.calculate_user_data(
        amount_invested=investment['amount'],
        time_invested=src.date_to_unix(investment['time']),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(investment['asset']['chain'], investment['asset']['symbol']))),
        busd_data=BUSD_DATA
    )

    pred = src.calculate_future_returns(user_data, **pred_params)

    pred_organized = [
        {
            'Strategy': 'Keep prividing liquidity',
            'Value ($)': pred['total_value']
        },
        {
            'Strategy': 'Withdraw and hold as RUNE',
            'Value ($)': user_data.iloc[-1]['total_value'] * pred_params['rune_target'] / user_data.iloc[-1]['rune_price']
        },
        {
            'Strategy': 'Withdraw and hold as {}'.format(investment['asset']['symbol']),
            'Value ($)': user_data.iloc[-1]['total_value'] * pred_params['asset_target'] / user_data.iloc[-1]['asset_price']
        }
    ]
    pred_organized = sorted(pred_organized, key=lambda strat: strat['Value ($)'], reverse=True)
    pred_organized = pd.DataFrame(pred_organized)
    pred_organized.set_index('Strategy', inplace=True)

    current_breakdown = src.calculate_gains_breakdown(user_data)
    future_breakdown = src.calculate_gains_breakdown(pd.DataFrame([
        user_data.to_dict(orient='records')[0],
        pred
    ]))

    st.title('Value of Investment')
    st.text('')

    st.markdown('''Based on the current value of **${:,.2f}**, your investment as of **{}** will
    worth the following, if you adopt the respective strategy form now on:'''.format(
        user_data.iloc[-1]['total_value'], pred_params['future_date'].strftime('%m/%d/%Y')
    ))

    st.text('')
    st.table(pred_organized)

    st.title('Gains/Losses Breakdown')
    st.text('')

    st.markdown('If you decide to keep providing liquidity, this is how your gains & loss would be like compared to the current values:')

    st.text('')
    st.pyplot(src.plot_gains_breakdown_compared_pyplot(current_breakdown, future_breakdown))
