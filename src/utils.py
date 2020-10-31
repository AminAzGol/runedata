from datetime import datetime
import os
import pandas as pd
import random
from termcolor import colored
from time import sleep


_red = lambda msg: colored(msg, 'red')
_yellow = lambda msg: colored(msg, 'yellow')
_green = lambda msg: colored(msg, 'green')
_blue = lambda msg: colored(msg, 'blue')

_currenttime = lambda: datetime.now().strftime('[%m/%d/%Y %H:%M:%S]')

_columns = [
    'block_number',
    'timestamp',
    'pool_units',
    'balance_rune',
    'balance_asset'
]


utc_to_unix = lambda utc_time: int(datetime.strptime(utc_time[:19], '%Y-%m-%dT%H:%M:%S').timestamp())
date_to_unix = lambda date: int(datetime.combine(date, datetime.min.time()).timestamp())


def _join_kwargs(kwargs):
    return ' '.join([ '{}={}'.format(_blue(key), kwargs[key]) for key in sorted(kwargs.keys()) ])


def info(msg, **kwargs):
    if len(kwargs) > 0:
        print(_currenttime(), _green('INFO'), msg, _join_kwargs(kwargs))
    else:
        print(_currenttime(), _green('INFO'), msg)


def warn(msg, **kwargs):
    if len(kwargs) > 0:
        print(_currenttime(), _yellow('WARN'), msg, _join_kwargs(kwargs))
    else:
        print(_currenttime(), _yellow('WARN'), msg)


def error(msg, **kwargs):
    if len(kwargs) > 0:
        print(_currenttime(), _red('ERROR'), msg, _join_kwargs(kwargs))
    else:
        print(_currenttime(), _red('ERROR'), msg)


# API maintained by a community member
def api_url(asset, block_number):
    return 'https://asgard-consumer.vercel.app/api/v1/block/detail?pool={}&height={}&isNeedTime=true'.format(asset, block_number)


def random_sleep(max_seconds):
    sleep_time = random.randint(0, max_seconds)
    info('Sleeping...', seconds=sleep_time)
    sleep(sleep_time)


def _save_data(df, filename):
    if not isinstance(df, pd.DataFrame):
        try:
            df = pd.DataFrame(df, columns=_columns)
        except Exception:
            error('Failed to convert data to a DataFrame')
            exit()

    if len(df) > 0:
        df.to_csv(filename, index=False)
        info('Data saved!', filename=filename.split('/')[-1], total_rows=len(df))
    else:
        warn('Skipped empty DataFrame', filename=filename.split('/')[-1])


def save_data_and_exit(dfs, data_dir):
    for asset, df in dfs.items():
        _save_data(df, '{}/pool_{}.csv'.format(data_dir, asset))
    info('Exitting...')
    exit()


def get_pool_yields(list_assets, data_dir):
    pass


def get_asset_prices(list_assets, data_dir):
    prices = []

    for asset in list_assets:
        data = pd.read_csv(os.path.join(data_dir, 'pool_{}.{}.csv').format(asset['chain'], asset['symbol']))
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

    return pd.DataFrame(prices, columns=['Chain', 'Symbol', 'Name', 'Price ($)'])
