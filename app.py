from datetime import datetime, timezone
import os
import pandas as pd
import streamlit as st
import time

import src


DATA_DIR = os.path.abspath('./data')

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
    st.title('How does this work?'),
    st.write('FAQ contents here')
]

def _clear_faq():
    for widget in faq:
        widget.empty()


#-------------------------------------------------------------------------------
# Button action
#-------------------------------------------------------------------------------

if submit_btn:
    _clear_faq()

    user_data = src.calculate_user_data(
        amount_invested=investment['amount'],
        time_invested=datetime.combine(investment['time'], datetime.min.time()).timestamp(),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(investment['asset']['chain'], investment['asset']['symbol']))),
        busd_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_BNB.BUSD-BD1.csv')),
        # index_by=???
    )

    st.header('Summary')
    st.write('Lorem ipsum')

    st.header('Investment Value')
    st.pyplot(src.plot_gains_breakdown(user_data))

    st.header('Gains/Losses Breakdown')
    st.pyplot(src.plot_gains_breakdown(user_data))

    st.header('Strategy Comparison')
    st.write('Lorem ipsum')
