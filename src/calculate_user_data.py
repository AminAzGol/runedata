from math import sqrt
import pandas as pd
# from tqdm import tqdm

from utils import *


_columns = [
    'block_number',
    'timestamp',
    'rune_price',
    'asset_price',
    'rune_balance',
    'asset_balance',
    'rune_value',
    'asset_value',
    'total_value',
    'fee_accrual',
    'imperm_loss',
    'total_gains'
]


def _get_prices(asset_row, busd_row):
    rune_in_usd = busd_row['balance_asset'] / busd_row['balance_rune']
    asset_in_rune = asset_row['balance_rune'] / asset_row['balance_asset']
    asset_in_usd = asset_in_rune * rune_in_usd
    return rune_in_usd, asset_in_usd


def _get_user_shares(usd_invested, asset_row, busd_row):
    rune_price, asset_price = _get_prices(asset_row, busd_row)
    share_price = (asset_row['balance_rune'] * rune_price + asset_row['balance_asset'] * asset_price) / asset_row['pool_units'] / 10e7
    return usd_invested / share_price


def calculate_user_data(usd_invested, time_invested, asset_data, busd_data):
    # Assert that both the asset pool and price data exist at the time of investment
    if time_invested < asset_data.loc[0]['timestamp']:
        error('Asset pool does not exist at the time of investment!')
        return None

    if time_invested < busd_data.loc[0]['timestamp']:
        error('Asset price data does not exist at the time of investment!')
        return None

    # Find the block immediately after the time of investment as starting block
    for idx, row in asset_data.iterrows():
        if row['timestamp'] >= time_invested:
            start_idx = idx
            break
    info('Determined block starting block', start_block=asset_data.loc[start_idx]['block_number'])

    # Clean up dataframes so that they both start form the starting block with index = 0
    asset_data = asset_data[start_idx:]
    asset_data.reset_index(drop=True, inplace=True)

    busd_data = busd_data[ busd_data.block_number >= asset_data.loc[0]['block_number'] ]
    busd_data.reset_index(drop=True, inplace=True)

    # Calculate user's share in pool
    user_share = _get_user_shares(usd_invested, asset_data.loc[0], busd_data.loc[0])
    info('Determined user share', user_share=user_share)

    user_data = []

    # for idx in range(5):
    for idx in range(len(asset_data)):
        # Asset prices in USD
        rune_price, asset_price = _get_prices(asset_data.loc[idx], busd_data.loc[idx])

        # User balance
        rune_balance = user_share * asset_data.loc[idx]['balance_rune'] / asset_data.loc[idx]['pool_units'] / 10e7
        asset_balance = user_share * asset_data.loc[idx]['balance_asset'] / asset_data.loc[idx]['pool_units'] / 10e7

        # User balance in USD
        rune_value = rune_balance * rune_price
        asset_value = asset_balance * asset_price
        total_value = rune_value + asset_value

        if idx == 0:
            fee_accrual, imperm_loss, total_gains = 0., 0., 0.
        else:
            # Fee accrual
            k_value = rune_balance * asset_balance
            k_value_init = user_data[0]['rune_balance'] * user_data[0]['asset_balance']
            fee_accrual = 0.5 * (k_value / k_value_init - 1)

            # Impermanent loss
            relative_price_init = user_data[0]['asset_price'] / user_data[0]['rune_price']
            relative_price_now = asset_price / rune_price
            price_swing = relative_price_now / relative_price_init
            imperm_loss = 2 * sqrt(price_swing) / (price_swing + 1) - 1

            # Total gains
            hodl_value = rune_price * user_data[0]['rune_balance'] + asset_price * user_data[0]['asset_balance']
            total_gains = total_value / hodl_value - 1

        user_data.append({
            'block_number': asset_data.loc[idx]['block_number'],
            'timestamp': asset_data.loc[idx]['timestamp'],
            'rune_price': rune_price,
            'asset_price': asset_price,
            'rune_balance': rune_balance,
            'asset_balance': asset_balance,
            'rune_value': rune_value,
            'asset_value': asset_value,
            'total_value': total_value,
            'fee_accrual': fee_accrual,
            'imperm_loss': imperm_loss,
            'total_gains': total_gains
        })
    info('User data calculated', **user_data[0])
    info('User data calculated', **user_data[-1])

    return pd.DataFrame(user_data, columns=_columns)


if __name__ == '__main__':
    # time_invested = 1598952349  # earliest time possible, block 157500, 9/1/2020 09:25 UTC
    time_invested = 1600732800  # 9/22/2020 where @Bitcoin_Sage's data collected started
    # time_invested = 1600926395  # time where yields have stablized, block 506250, 9/24/2020 03:53 UTC
    # time_invested = 1601510400  # 10/1/2020 00:00 UTC

    user_data = calculate_user_data(
        usd_invested=10000,
        time_invested=time_invested,
        asset_data=pd.read_csv('../data/pool_BNB.BNB.csv'),
        busd_data=pd.read_csv('../data/pool_BNB.BUSD-BD1.csv')
    )

    from datetime import datetime
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mtick

    # Timestamps to datetime object
    dates = [ datetime.fromtimestamp(ts) for ts in user_data.timestamp ]

    # Decimals to percentages
    fee_accrual = [ fee * 100 for fee in user_data.fee_accrual ]
    imperm_loss = [ il * 100 for il in user_data.imperm_loss ]
    total_gains = [ tot * 100 for tot in user_data.total_gains ]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(dates, fee_accrual, color='magenta', label='Fee accrual')
    ax.plot(dates, imperm_loss, color='blue', label='Impermanent loss')
    ax.plot(dates, total_gains, color='red', label='Total gains')

    ax.yaxis.set_major_formatter(mtick.PercentFormatter())  # Y-axis: use percentage
    plt.axhline(0, color='black', linewidth=0.5)            # Horizontal line at y = 0
    plt.xticks(rotation=25)                                 # Tilt x-axis labels
    plt.subplots_adjust(bottom=0.2)
    ax.legend()
    plt.tight_layout()
    plt.show()
