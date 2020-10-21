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


asset = st.sidebar.selectbox(
    label='Pool',
    options=ASSETS,
    format_func=lambda asset: '{} ({}.{})'.format(asset['name'], asset['chain'], asset['symbol'])
)

usd_invested = st.sidebar.number_input('Amount invested ($)', min_value=0., format='%.2f')

time_invested = st.sidebar.date_input('Date invested', min_value=datetime.fromtimestamp(1598952349))

submit_btn = st.sidebar.button('Submit')


if submit_btn:
    # Convert time_invest from datetime.date to datetime.datetime
    time_invested = dt = datetime.combine(time_invested, datetime.min.time())

    user_data = src.calculate_user_data(
        usd_invested=usd_invested,
        time_invested=time_invested.timestamp(),
        asset_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_{}.{}.csv'.format(asset['chain'], asset['symbol']))),
        busd_data=pd.read_csv(os.path.join(DATA_DIR, 'pool_BNB.BUSD-BD1.csv'))
    )

    st.header('Gains/Losses Breakdown')
    st.pyplot(src.plot_gains_breakdown(user_data))
