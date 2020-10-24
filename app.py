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
        </style>
    ''',
    unsafe_allow_html=True
)


#-------------------------------------------------------------------------------
# Sidebar
#-------------------------------------------------------------------------------

index_by = st.sidebar.selectbox(
    label='Index result in',
    options=ASSETS,
    format_func=lambda asset: '{} ({}.{})'.format(asset['name'], asset['chain'], asset['symbol']),
    index=1,  # default to BUSD
    key='index_by'
)

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

submit_btn = st.sidebar.button('Submit')


#-------------------------------------------------------------------------------
# Default page content - FAQs
#-------------------------------------------------------------------------------

faq = [
    # st.title('How does this work?'),
    # st.markdown('FAQ contents here'),
    st.info('Data last updated: ' + datetime.fromtimestamp(BUSD_DATA.iloc[-1]['timestamp']).strftime("%m/%d/%Y %H:%M:%S UTC"))
]

def _clear_faq():
    print('faq', faq)
    for widget in faq:
        widget.empty()


#-------------------------------------------------------------------------------
# Button action
#-------------------------------------------------------------------------------

def _get_percent_change(value, baseline, show_sign=True):
    if show_sign:
        sign = '+' if value >= baseline else '-'
    else:
        sign = ''

    color = 'green' if value >= baseline else 'red'
    percentage = abs(value / baseline - 1) * 100

    return '<span style="color:{}">{}{:.1f}%</span>'.format(color, sign, percentage)


def out_or_under(value, baseline):
    return 'outperforms' if value >= baseline else 'underperforms'


if submit_btn:
    _clear_faq()

    user_data = src.calculate_user_data(
        amount_invested=investment['amount'],
        time_invested=datetime.combine(investment['time'], datetime.min.time()).timestamp(),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(investment['asset']['chain'], investment['asset']['symbol']))),
        busd_data=BUSD_DATA,
        # index_by=???
    )

    baselines = src.calculate_baselines(user_data)

    st.title('Summary')

    st.markdown('The current value of your investment is **${:,.2f}** (**{}**)'.format(
        user_data.iloc[-1]['total_value'],
        _get_percent_change(user_data.iloc[-1]['total_value'], investment['amount']),
    ), unsafe_allow_html=True)

    st.markdown('If you have passively held 50:50 **RUNE** & **{}** without rebalancing, you would have **${:,.2f}** (LP *{}* by **{}**)'.format(
        investment['asset']['symbol'],
        baselines.iloc[-1]['hold_both'],
        out_or_under(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_both']),
        _get_percent_change(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_both'], show_sign=False)
    ), unsafe_allow_html=True)

    st.markdown('If you have passively held **RUNE** only, you would have **${:,.2f}** (LP *{}* by **{}**)'.format(
        baselines.iloc[-1]['hold_both'],
        out_or_under(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_rune']),
        _get_percent_change(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_rune'], show_sign=False)
    ), unsafe_allow_html=True)

    st.markdown('If you have passively held **{}** only, you would have **${:,.2f}** (LP *{}* by **{}**)'.format(
        investment['asset']['symbol'],
        baselines.iloc[-1]['hold_asset'],
        out_or_under(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_asset']),
        _get_percent_change(user_data.iloc[-1]['total_value'], baselines.iloc[-1]['hold_asset'], show_sign=False)
    ), unsafe_allow_html=True)

    st.header('Value of Investment')
    st.text('')  # add some vertical space
    st.altair_chart(src.plot_value_of_investment(user_data, baselines), use_container_width=True)

    st.header('Gains/Losses Breakdown')
    st.text('')
    st.altair_chart(src.plot_gains_breakdown(user_data), use_container_width=True)
