import base64
from datetime import datetime, timezone
import os
import pandas as pd
import streamlit as st
import time

import src


DATA_DIR = os.path.abspath('./data')
BUSD_DATA = pd.read_csv(os.path.join(DATA_DIR, 'pool_BNB.BUSD-BD1.csv'))

ASSETS = [
    {
        'name': 'Binance Coin',
        'chain': 'BNB',
        'symbol': 'BNB'
    },
    {
        'name': 'Binance USD',
        'chain': 'BNB',
        'symbol': 'BUSD-BD1'
    },
    {
        'name': 'Bitcoin BEP2',
        'chain': 'BNB',
        'symbol': 'BTCB-1DE'
    },
    {
        'name': 'Ether BEP2',
        'chain': 'BNB',
        'symbol': 'ETH-1C9'
    }
]


# Increace max width of main page container
# https://discuss.streamlit.io/t/where-to-set-page-width-when-set-into-non-widescreeen-mode/959
st.markdown(
    f'''
        <style>
            .reportview-container .main .block-container {{
                max-width: 1000px;
            }}
            img {{
                max-width: 600px;
            }}
        </style>
    ''',
    unsafe_allow_html=True
)


#-------------------------------------------------------------------------------
# Sidebar
#-------------------------------------------------------------------------------

st.sidebar.header('View Past Performance')

investment = {
    'asset': st.sidebar.selectbox(
        label='Pool',
        options=ASSETS,
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
    'use_avg': st.sidebar.selectbox(
        label='Use average pool ROI of the last...',
        options=['3 days', '7 days', '14 days', '30 days']
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
# Default page content - FAQs
#-------------------------------------------------------------------------------

faq = [
    st.title('This tool helps you view the historical performance of your liquidity pool on THORChain and perdict its future returns.'),
    st.text(''),
    st.text(''),
    st.markdown('''To view the past performance of your LP, fill out the first section of the left panel, then hit "View".

To predict the returns of your LP in the future, fill out **both** sections, and hit "Predict". The algorithm will extrapolate the ROI
of your pool into your selected date, and substract impermanent loss based on your target asset prices.'''),
    st.text(''),
    st.text(''),
    st.markdown('''> Created by [@Larrypcdotcom](https://twitter.com/Larrypcdotcom) &middot; [code](https://github.com/Larrypcdotcom/thorchain-lp-data) on GitHub.
>
> Interested in contributing? Join the **THORChain Apps Team** [Discord channel]().''')
]

def _clear_faq():
    print('faq', faq)
    for widget in faq:
        widget.empty()


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


def _get_apy(start_time, end_time, total_value, baseline):
    num_days = (end_time - start_time) / 60 / 60 / 24
    roi = total_value / baseline - 1
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
    and lost **{}** due to asset price movements. Overall, LP **{}** HODL by **{}**.'''.format(
        investment['asset']['symbol'],
        _get_percent_change(user_data.iloc[-1]['fee_accrual'], 0., show_sign=False),
        _get_percent_change(user_data.iloc[-1]['imperm_loss'], 0., show_sign=False),
        _out_or_under(user_data.iloc[-1]['total_gains'], 0.),
        _get_percent_change(user_data.iloc[-1]['total_gains'], 0., show_sign=False)
    ), unsafe_allow_html=True)

    st.markdown('''Extrapolating to a year, compounded daily, the APY is approximately **{}**.'''.format(
        _get_percent_change(_get_apy(
            user_data.loc[0]['timestamp'], user_data.iloc[-1]['timestamp'],
            user_data.loc[0]['total_value'], baselines.iloc[-1]['hold_both']
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

    st.markdown('''You gained **${:,.2f}** (**{}**) from fees & rewards from LP, and lost **${:,.2f}** (**{}**) due to impermanent loss.'''.format(
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
        time_invested=datetime.combine(investment['time'], datetime.min.time()).timestamp(),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(investment['asset']['chain'], investment['asset']['symbol']))),
        busd_data=BUSD_DATA
    )

    user_pred = src.calculate_future_returns(user_data, **pred_params)

    st.title('Value of Investment')
    st.text('')

    st.markdown('Based on the current value of **${:,.2f}**, your investment on **{}** will worth:'.format(
        user_data.iloc[-1]['total_value'], pred_params['future_date'].strftime('%m/%d/%Y')
    ))

    st.text('')
    # st.table()

    st.title('Gains/Losses Breakdown')
    st.text('')

    st.markdown('')

    st.text('')
    # st.altair_chart(src.plot_future_gains_breakdown(user_data), use_container_width=True)
