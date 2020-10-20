from datetime import datetime
import json
from math import sqrt
import pandas as pd
import random
from termcolor import colored
from time import sleep
from urllib.request import urlopen


#-------------------------------------------------------------------------------
# Configs
#-------------------------------------------------------------------------------

USER_SHARE     = 801134713433     # User's pool share
FIRST_BLOCK    = 611552           # The fist block after 10/1/2020 00:00 UTC
LAST_BLOCK     = 905107           # The latest block
STEP           = 625              # approx. 1 hr
MAX_SLEEP_TIME = 3

#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------

_red = lambda msg: colored(msg, 'red')
_yellow = lambda msg: colored(msg, 'yellow')
_green = lambda msg: colored(msg, 'green')
_blue = lambda msg: colored(msg, 'blue')

_utc_to_unix = lambda utc_time: int(datetime.strptime(utc_time[:19], '%Y-%m-%dT%H:%M:%S').timestamp())

_currenttime = lambda: datetime.now().strftime('[%m/%d/%Y %H:%M:%S]')


def _join_kwargs(kwargs):
    return ' '.join([ '{}={}'.format(_blue(key), kwargs[key]) for key in sorted(kwargs.keys()) ])


def _info(msg, **kwargs):
    if len(kwargs) > 0:
        print(_currenttime(), _green('INFO'), msg, _join_kwargs(kwargs))
    else:
        print(_currenttime(), _green('INFO'), msg)


def _warn(msg, **kwargs):
    if len(kwargs) > 0:
        print(_currenttime(), _yellow('WARN'), msg, _join_kwargs(kwargs))
    else:
        print(_currenttime(), _yellow('WARN'), msg)


def _error(msg, **kwargs):
    if len(kwargs) > 0:
        print(_currenttime(), _red('ERROR'), msg, _join_kwargs(kwargs))
    else:
        print(_currenttime(), _red('ERROR'), msg)


def _url(asset, block_number):
    return 'https://asgard-consumer.vercel.app/api/v1/block/detail?pool={}&height={}&isNeedTime=true'.format(asset, block_number)


def _random_sleep(max_seconds):
    sleep_time = random.randint(0, max_seconds)
    _info('Sleeping...', seconds=sleep_time)
    sleep(sleep_time)


def _save_data_and_exit(df):
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df, columns=[
            'block_number',
            'timestamp',
            'rune_price',
            'bnb_price',
            'user_rune_balance',
            'user_bnb_balance',
            'user_rune_value',
            'user_bnb_value',
            'user_total_value',
            'fee_accrual',
            'imperm_loss',
            'total_gains'
        ])

    df.to_csv('thorchain_user_data.csv', index=False)
    _info('Data saved! Exitting...', total_rows=len(df))
    exit()


#-------------------------------------------------------------------------------
# Fetch data from server
#-------------------------------------------------------------------------------

def fetch_data(df, block_number):
    # Keep trying to fetch data from API until successful
    tries = 0
    while True:
        try:
            tries += 1
            with urlopen(_url('BNB.BNB', block_number)) as response:
                bnb_data = json.loads(response.read())
            with urlopen(_url('BNB.BUSD-BD1', block_number)) as response:
                busd_data = json.loads(response.read())
            _info('Fetched data from API', block_number=block_number, tries=tries)
            break
        except KeyboardInterrupt:
            _warn('User interruption! Saving data...')
            _save_data_and_exit(df)
        except Exception:
            _error('Failed to fetch data from API. Retrying...', block_number=block_number, tries=tries)

    rune_in_usd = int(busd_data['balance_asset']) / int(busd_data['balance_rune'])
    bnb_in_rune = int(bnb_data['balance_rune']) / int(bnb_data['balance_asset'])
    bnb_in_usd = bnb_in_rune * rune_in_usd

    user_rune_balance = USER_SHARE * int(bnb_data['balance_rune']) / int(bnb_data['pool_units']) / 10e7
    user_bnb_balance = USER_SHARE * int(bnb_data['balance_asset']) / int(bnb_data['pool_units']) / 10e7

    user_rune_value = user_rune_balance * rune_in_usd
    user_bnb_value = user_bnb_balance * bnb_in_usd
    user_total_value = user_rune_value + user_bnb_value

    if len(df) == 0:
        fee_accrual = 0.
        imperm_loss = 0.
        total_gains = 0.
    else:
        k_value = user_rune_balance * user_bnb_balance
        k_value_init = df[0]['user_rune_balance'] * df[0]['user_bnb_balance']
        fee_accrual = 0.5 * (k_value / k_value_init - 1)

        bnb_in_rune_initial = df[0]['bnb_price'] / df[0]['rune_price']
        price_swing = bnb_in_rune / bnb_in_rune_initial
        imperm_loss = 2 * sqrt(price_swing) / (price_swing + 1) - 1

        user_hodl_value = rune_in_usd * df[0]['user_rune_balance'] + bnb_in_usd * df[0]['user_bnb_balance']
        total_gains = user_total_value / user_hodl_value - 1

    data = {
        'block_number': block_number,
        'timestamp': _utc_to_unix(bnb_data['time']),
        'rune_price': rune_in_usd,
        'bnb_price': bnb_in_usd,
        'user_rune_balance': user_rune_balance,
        'user_bnb_balance': user_bnb_balance,
        'user_rune_value': user_rune_value,
        'user_bnb_value': user_bnb_value,
        'user_total_value': user_total_value,
        'fee_accrual': fee_accrual,
        'imperm_loss': imperm_loss,
        'total_gains': total_gains
    }

    df.append(data)
    _info('User data appended', **data)

    return df


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    try:
        df = pd.read_csv('thorchain_user_data.csv').to_dict(orient='records')
        FIRST_BLOCK = df[-1]['block_number'] + STEP
    except:
        df = []

    _info('Starting fetching user data', first_block=FIRST_BLOCK, last_block=LAST_BLOCK, step=STEP)

    try:
        for block_number in range(FIRST_BLOCK, LAST_BLOCK + 1, STEP):
            df = fetch_data(df, block_number)
            _random_sleep(MAX_SLEEP_TIME)  # Sleep a random time (0 - 5 sec) to prevent the server from banning me
    except KeyboardInterrupt:
        _warn('User interruption! Saving data...')
        _save_data_and_exit(df)
    except Exception:
        _error('Error! Saving data...')
        _save_data_and_exit(df)

    _info('Done!')
    _save_data_and_exit(df)
