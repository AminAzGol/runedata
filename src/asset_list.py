# Most popular assets that most user will LP with
assets = [
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
    },
    # {
    #     'name': 'Trust Wallet',
    #     'chain': 'BNB',
    #     'symbol': 'TWT-8C2'
    # },
    # {
    #     'name': 'Travala.com',
    #     'chain': 'BNB',
    #     'symbol': 'AVA-645'
    # },
]

# Sort by name
assets = sorted(assets, key=lambda asset: asset['name'])
