import base64
from datetime import datetime, timezone
import os
import pandas as pd
import streamlit as st
import time

import src


#-------------------------------------------------------------------------------
# Check pool data; fetch new if out of date
#-------------------------------------------------------------------------------

DATA_DIR = os.path.abspath('./data')
BUSD_DATA = pd.read_csv(os.path.join(DATA_DIR, 'pool_BNB.BUSD-BD1.csv'))

# Fetch data if the latest data point is more than an hour old
timedelta = datetime.utcnow().timestamp() - BUSD_DATA.iloc[-1]['timestamp']
if timedelta > 3600:
    src.warn('Pool data is more than an hour old. Fetching new data...', timedelta=int(timedelta))
    src.fetch_data(DATA_DIR)
else:
    src.info('Pool data is up to date', timedelta=int(timedelta))


#-------------------------------------------------------------------------------
# Page configs
#-------------------------------------------------------------------------------

# Must be the first Streamlit command used in your app
st.beta_set_page_config(
    page_title='THORChain Simulate',
    page_icon='images/favicon.png'
)

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
                max-width: 700px;
            }}
            img {{
                max-width: 100%;
            }}
        </style>
    ''',
    unsafe_allow_html=True
)


#-------------------------------------------------------------------------------
# FAQs
#-------------------------------------------------------------------------------

with open('./FAQ.md', 'r') as f:
    faq = st.markdown(f.read())


#-------------------------------------------------------------------------------
# Sidebar
#-------------------------------------------------------------------------------

st.sidebar.header('Simulate Past Performance')

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

view_btn = st.sidebar.button('Simulate', key='view_btn')

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
    faq.empty()

    user_data = src.calculate_user_data(
        amount_invested=investment['amount'],
        time_invested=datetime.combine(investment['time'], datetime.min.time()).timestamp(),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(investment['asset']['chain'], investment['asset']['symbol']))),
        busd_data=BUSD_DATA
    )

    baselines = src.calculate_baselines(user_data)

    breakdown = src.calculate_gains_breakdown(user_data)

    st.title('Value of Investment')

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

    st.subheader('Bar chart')
    st.pyplot(src.plot_gains_breakdown(breakdown))

    st.subheader('Waterfall chart')
    st.pyplot(src.plot_gains_breakdown_waterfall(breakdown))


if predict_btn:
    faq.empty()

    user_data = src.calculate_user_data(
        amount_invested=investment['amount'],
        time_invested=src.date_to_unix(investment['time']),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(investment['asset']['chain'], investment['asset']['symbol']))),
        busd_data=BUSD_DATA
    )

    pred = src.calculate_future_returns(user_data, **pred_params)

    pred_organized = [
        {
            'Strategy': 'Keep providing liquidity',
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
    future_breakdown = src.calculate_gains_breakdown(pd.DataFrame([ user_data.to_dict(orient='records')[0], pred ]))

    st.title('Value of Investment')

    st.markdown('''Based on the current value of **${:,.2f}**, your investment as of **{}** will
    worth the following, if you adopt the respective strategy form now on:'''.format(
        user_data.iloc[-1]['total_value'], pred_params['future_date'].strftime('%m/%d/%Y')
    ))

    # st.text('')
    st.table(pred_organized)

    st.title('Gains/Losses Breakdown')

    st.markdown('If you decide to keep providing liquidity, this is how your gains & loss would be like compared to the current values:')

    st.subheader('Bar chart')
    st.pyplot(src.plot_gains_breakdown_compared(current_breakdown, future_breakdown))

    st.subheader('Waterfall chart')
    st.pyplot(src.plot_gains_breakdown_compared_waterfall(current_breakdown, future_breakdown))
