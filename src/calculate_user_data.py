from math import sqrt
import pandas as pd
from tqdm import tqdm

from .utils import *
from .plot_data import *


__all__ = [ 'calculate_user_data', 'calculate_baselines' ]


_user_columns = [
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

_baseline_columns = [
    'block_number',
    'timestamp',
    'hold_both',
    'hold_rune',
    'hold_asset'
]


#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------

def _get_prices(asset_row, busd_row):
    rune_in_usd = busd_row['balance_asset'] / busd_row['balance_rune']
    asset_in_rune = asset_row['balance_rune'] / asset_row['balance_asset']
    asset_in_usd = asset_in_rune * rune_in_usd
    return rune_in_usd, asset_in_usd


def _get_user_shares(amount_invested, asset_row, busd_row):
    rune_price, asset_price = _get_prices(asset_row, busd_row)
    share_price = (asset_row['balance_rune'] * rune_price + asset_row['balance_asset'] * asset_price) / asset_row['pool_units'] / 10e7
    return amount_invested / share_price


#-------------------------------------------------------------------------------
# Calculate user data
#-------------------------------------------------------------------------------

def calculate_user_data(amount_invested, time_invested, asset_data, busd_data):
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
    user_share = _get_user_shares(amount_invested, asset_data.loc[0], busd_data.loc[0])
    info('Determined user share', user_share=user_share)

    user_data = []

    info('Calculating user data', total_rows=len(asset_data))
    for idx in tqdm(range(len(asset_data)), desc='User data'):
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
            'block_number':  asset_data.loc[idx]['block_number'],
            'timestamp':     asset_data.loc[idx]['timestamp'],
            'rune_price':    rune_price,
            'asset_price':   asset_price,
            'rune_balance':  rune_balance,
            'asset_balance': asset_balance,
            'rune_value':    rune_value,
            'asset_value':   asset_value,
            'total_value':   total_value,
            'fee_accrual':   fee_accrual,
            'imperm_loss':   imperm_loss,
            'total_gains':   total_gains
        })

    return pd.DataFrame(user_data, columns=_user_columns)


#-------------------------------------------------------------------------------
# Calculate user data
#-------------------------------------------------------------------------------

def calculate_baselines(user_data):
    data = []
    row = user_data.loc[0]
    init_investment = row['rune_balance'] * row['rune_price'] + row['asset_balance'] * row['asset_price']

    for idx, row in tqdm(user_data.iterrows(), desc='baselines'):
        hold_rune = init_investment * row['rune_price'] / user_data.loc[0]['rune_price']
        hold_asset = init_investment * row['asset_price'] / user_data.loc[0]['asset_price']
        data.append({
            'block_number': row['block_number'],
            'timestamp':    row['timestamp'],
            'hold_rune':    hold_rune,
            'hold_asset':   hold_asset,
            'hold_both':    0.5 * hold_rune + 0.5 * hold_asset
        })

    return pd.DataFrame(data, columns=_baseline_columns)
