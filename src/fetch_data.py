import json
import os
import pandas as pd
import requests

from .asset_list import assets as ASSETS
from .utils import *


__all__ = [ 'fetch_data' ]


#-------------------------------------------------------------------------------
# Configs
#-------------------------------------------------------------------------------

LAST_BLOCK     = 9999999
STEP           = 625    # approx. 1 hr
MAX_SLEEP_TIME = 1
LIST_ASSETS    = [ '{}.{}'.format(asset['chain'], asset['symbol']) for asset in ASSETS ]
# FIRST_BLOCK    = { asset: 157500 for asset in LIST_ASSETS }  # Starting around the earliest block where BUSD pool existed


#-------------------------------------------------------------------------------
# Function for fetching data from server
#-------------------------------------------------------------------------------

def _fetch_block_data(asset, block_number, log_file=None):

    _enabled_and_nonzero_balance = lambda data: ('status' in data) and (data['status'] == 'Enabled') and (int(data['balance_rune']) > 0)
    _enabled_but_zero_balance = lambda data: ('status' in data) and (data['status'] == 'Enabled') and (int(data['balance_rune']) == 0)
    _exists_but_not_enabled = lambda data: 'status' in data and data['status'] == 'Bootstrap'
    _does_not_exist = lambda data: 'error' in data and data['error'] == 'No data found.'  # Either block number hasn't been reached, or asset id is wrong

    # Keep trying to fetch data from API until successful
    tries = 0
    while True:
        try:
            tries += 1
            data = requests.get(api_url(asset, block_number)).json()
            break
        except KeyboardInterrupt:
            warn('User interruption while fetching data! Returning exit signal', log_file)
            return 'kbinterrupt'
        except Exception:
            error('Failed to fetch data from API. Retrying...', log_file, asset=asset, block_number=block_number, tries=tries)

    if _enabled_and_nonzero_balance(data):
        data['block_number'] = data['height']          # change key `height` to `block_number` because I like it
        data['timestamp'] = utc_to_unix(data['time'])  # change UTC time to UNIX timestamp
        data.pop('time')
        data.pop('height')
        data.pop('asset')
        data.pop('status')
        info('Fetched data from API', log_file, asset=asset, block_number=block_number)
        return data

    elif _does_not_exist(data):
        warn('Pool does not exist or block has not been mined yet', log_file, asset=asset, block_number=block_number)
        return 'doesnotexist'

    elif _enabled_but_zero_balance(data):
        warn('Pool has zero balance', log_file, asset=asset, block_number=block_number)
    elif _exists_but_not_enabled(data):
        warn('Pool is not enabled', log_file, asset=asset, block_number=block_number)
    else:
        error('Unknown error when fetching data', log_file)

    return None


def fetch_data(data_dir, list_assets=LIST_ASSETS, log_file=None, first_block=157500):
    dfs = {}
    FIRST_BLOCK = {}
    for asset in LIST_ASSETS:
        try:
            dfs[asset] = pd.read_csv('{}/pool_{}.csv'.format(data_dir, asset)).to_dict(orient='records')
            FIRST_BLOCK[asset] = dfs[asset][-1]['block_number'] + STEP
            info('Loaded existing CSV', log_file, asset=asset, first_block=FIRST_BLOCK[asset])
        except:
            dfs[asset] = []
            FIRST_BLOCK[asset] = first_block
            info('Local CSV not found. Starting new...', log_file, asset=asset, first_block=FIRST_BLOCK[asset])

    try:
        for block_number in range(min(FIRST_BLOCK.values()), LAST_BLOCK + 1, STEP):
            for asset in LIST_ASSETS:
                if block_number >= FIRST_BLOCK[asset]:
                    data = _fetch_block_data(asset, block_number, log_file)

                    if data == 'kbinterrupt':
                        raise KeyboardInterrupt

                    # Data is up to date
                    elif data == 'doesnotexist' and len(dfs[asset]) > 0:
                        return

                    # Pool does not exist
                    elif data == 'doesnotexist' and len(dfs[asset]) == 0:
                        pass

                    elif data != None:
                        dfs[asset].append(data)
                        info('Appended data', log_file, **data)

                    # Sleep a random time so that the server doesn't block me
                    random_sleep(MAX_SLEEP_TIME)

            # Update: save to file every time a new data point is fetched
            save_data(dfs, data_dir)

    except KeyboardInterrupt:
        warn('User interruption! Saving data...', log_file)

    except Exception:
        error('Error! Saving data...', log_file)

    info('Done!')
