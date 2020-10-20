import json
from math import sqrt
import os
import pandas as pd
# from urllib.request import urlopen
import requests

from utils import *


__all__ = [ 'fetch_data' ]


#-------------------------------------------------------------------------------
# Configs
#-------------------------------------------------------------------------------

DATA_DIR       = os.path.abspath('../data')
LAST_BLOCK     = 905107
LAST_BLOCK     = 80000  # for debugging
STEP           = 625    # approx. 1 hr
MAX_SLEEP_TIME = 3

LIST_ASSETS = sorted([
    # 'BNB.FRM-DE7',
    # 'BNB.SHR-DB6',
    # 'BNB.NEXO-A84',
    'BNB.BNB',
    # 'BNB.CAS-167',
    # 'BNB.LTC-F07',
    # 'BNB.TRXB-2E6',
    # 'BNB.UNI-DD8',
    # 'BNB.BOLT-4C6',
    # 'BNB.ERD-D06',
    # 'BNB.SWINGBY-888',
    # 'BNB.XRP-BF2',
    # 'BNB.BEAR-14C',
    # 'BNB.CAN-677',
    'BNB.BTCB-1DE',
    'BNB.BUSD-BD1',
    # 'BNB.COTI-CBB',
    # 'BNB.AVA-645',
    # 'BNB.BCH-1FD',
    # 'BNB.GIV-94E',
    # 'BNB.LIT-099',
    # 'BNB.TWT-8C2',
    # 'BNB.AWC-986',
    # 'BNB.DARC-24B',
    'BNB.ETH-1C9',
    # 'BNB.ETHBULL-D33',
    # 'BNB.FTM-A64',
    # 'BNB.WISH-2D5',
    # 'BNB.BZNT-464',
    # 'BNB.EOSBULL-F0D',
    # 'BNB.PROPEL-6D9',
    # 'BNB.CBIX-3C9',
    # 'BNB.DOS-120',
    # 'BNB.MITX-CAA',
    # 'BNB.VIDT-F53',
    'BNB.BULL-BE4',
    # 'BNB.LTO-BDF'
])

FIRST_BLOCK = { asset: 65000 for asset in LIST_ASSETS }  # The first pool was created shortly after block 65000 so it's a good place to start


#-------------------------------------------------------------------------------
# Function for fetching data from server
#-------------------------------------------------------------------------------

def _fetch_block_data(asset, block_number):

    _enabled_and_nonzero_balance = lambda data: ('status' in data) and (data['status'] == 'Enabled') and (int(data['balance_rune']) > 0)
    _enabled_but_zero_balance = lambda data: ('status' in data) and (data['status'] == 'Enabled') and (int(data['balance_rune']) == 0)
    _exists_but_not_enabled = lambda data: 'status' in data and data['status'] == 'Bootstrap'
    _does_not_exist = lambda data: 'error' in data and data['error'] == 'No data found.'

    # Keep trying to fetch data from API until successful
    tries = 0
    while True:
        try:
            tries += 1
            data = requests.get(api_url(asset, block_number)).json()
            break
        except KeyboardInterrupt:
            warn('User interruption while fetching data! Returning exit signal')
            return 'kbinterrupt'
        except Exception:
            error('Failed to fetch data from API. Retrying...', asset=asset, block_number=block_number, tries=tries)

    if _enabled_and_nonzero_balance(data):
        data['block_number'] = data['height']          # change key `height` to `block_number` because I like it
        data['timestamp'] = utc_to_unix(data['time'])  # change UTC time to UNIX timestamp
        data.pop('time')
        data.pop('height')
        data.pop('asset')
        data.pop('status')
        info('Fetched data from API', asset=asset, block_number=block_number)
        return data
    elif _enabled_but_zero_balance(data):
        warn('Pool has zero balance', asset=asset, block_number=block_number)
        return None
    elif _exists_but_not_enabled(data):
        warn('Pool is not enabled', asset=asset, block_number=block_number)
        return None
    elif _does_not_exist(data):
        warn('Pool does not exist', asset=asset, block_number=block_number)
        return None
    else:
        error('Unknown error when fetching data. Exitting...')
        exit()


def fetch_data():
    dfs = {}
    for asset in LIST_ASSETS:
        try:
            dfs[asset] = pd.read_csv('{}/pool_{}.csv'.format(DATA_DIR, asset)).to_dict(orient='records')
            FIRST_BLOCK[asset] = dfs[asset][-1]['block_number'] + STEP
            info('Loaded existing CSV', asset=asset, first_block=FIRST_BLOCK[asset])
        except:
            dfs[asset] = []
            info('Local CSV not found. Starting new...', asset=asset, first_block=FIRST_BLOCK[asset])

    try:
        for block_number in range(min(FIRST_BLOCK.values()), LAST_BLOCK + 1, STEP):
            for asset in LIST_ASSETS:
                if block_number >= FIRST_BLOCK[asset]:
                    data = _fetch_block_data(asset, block_number)
                    if data == 'kbinterrupt':
                        raise KeyboardInterrupt
                    elif data != None:
                        dfs[asset].append(data)
                        info('Appended data', **data)
                    random_sleep(MAX_SLEEP_TIME)  # Sleep a random time so that the server doesn't block me
    except KeyboardInterrupt:
        warn('User interruption! Saving data...')
        save_data_and_exit(dfs, DATA_DIR)
    except Exception:
        error('Error! Saving data...')
        save_data_and_exit(dfs, DATA_DIR)

    info('Done!')
    save_data_and_exit(dfs, DATA_DIR)


#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    fetch_data()
