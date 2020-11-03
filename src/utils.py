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


def _join_kwargs(kwargs, colored=True):
    if colored:
        color = _blue
    else:
        color = lambda x: x

    if len(kwargs) > 0:
        return ' '.join([ '{}={}'.format(color(key), kwargs[key]) for key in sorted(kwargs.keys()) ])
    else:
        return ''


def _append_to_file(filename, msg):
    if filename is not None:
        with open(filename, 'a') as f:
            f.write(msg + '\n')


def info(msg, log_file=None, **kwargs):
    log = _currenttime() + ' ' + 'INFO' + ' ' + msg + ' ' + _join_kwargs(kwargs, colored=False)
    _append_to_file(log_file, log)
    log = _currenttime() + ' ' + _green('INFO') + ' ' + msg + ' ' + _join_kwargs(kwargs, colored=True)
    print(log)


def warn(msg, log_file=None, **kwargs):
    log = _currenttime() + ' ' + 'WARN' + ' ' +  msg + ' ' + _join_kwargs(kwargs, colored=False)
    _append_to_file(log_file, log)
    log = _currenttime() + ' ' + _yellow('WARN') + ' ' +  msg + ' ' + _join_kwargs(kwargs, colored=True)
    print(log)


def error(msg, log_file=None, **kwargs):
    log = _currenttime() + ' ' + 'ERROR' + ' ' + msg + ' ' + _join_kwargs(kwargs, colored=False)
    _append_to_file(log_file, log)
    log = _currenttime() + ' ' + _red('ERROR') + ' ' + msg + ' ' + _join_kwargs(kwargs, colored=True)
    print(log)


# API maintained by a community member
def api_url(asset, block_number):
    return 'https://asgard-consumer.vercel.app/api/v1/block/detail?pool={}&height={}&isNeedTime=true'.format(asset, block_number)


def random_sleep(max_seconds, log_file=None):
    sleep_time = random.randint(0, max_seconds)
    info('Sleeping...', log_file, seconds=sleep_time)
    sleep(sleep_time)


def _save(df, filename, log_file=None):
    if not isinstance(df, pd.DataFrame):
        try:
            df = pd.DataFrame(df, columns=_columns)
        except Exception:
            error('Failed to convert data to a DataFrame', log_file)
            exit()

    if len(df) > 0:
        df.to_csv(filename, index=False)
        info('Data saved!', log_file, filename=filename.split('/')[-1], total_rows=len(df))
    else:
        warn('Skipped empty DataFrame', log_file, filename=filename.split('/')[-1])


def save_data(dfs, data_dir, log_file=None):
    for asset, df in dfs.items():
        _save(df, '{}/pool_{}.csv'.format(data_dir, asset), log_file)


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
