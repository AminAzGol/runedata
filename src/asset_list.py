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
    {
        'name': '3x Long Bitcoin Token',
        'chain': 'BNB',
        'symbol': 'BULL-BE4'

    },
    {
        'name': 'Fantom',
        'chain': 'BNB',
        'symbol': 'FTM-A64'
    },
    {
        'name': 'Trust Wallet',
        'chain': 'BNB',
        'symbol': 'TWT-8C2'
    },
    {
        'name': 'Travala.com',
        'chain': 'BNB',
        'symbol': 'AVA-645'
    },
    {
        'name': 'Ferrum Network Token',
        'chain': 'BNB',
        'symbol': 'FRM-DE7'
    },
    {
        'name': 'Swingby Token',
        'chain': 'BNB',
        'symbol': 'SWINGBY-888'
    }
]

# Sort by name
assets = sorted(assets, key=lambda asset: asset['name'])
