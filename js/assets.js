var _assets = [
    {
        name: 'Binance Coin',
        chain: 'BNB',
        symbol: 'BNB'
    },
    {
        name: 'Binance USD',
        chain: 'BNB',
        symbol: 'BUSD-BD1'
    },
    {
        name: 'Bitcoin BEP2',
        chain: 'BNB',
        symbol: 'BTCB-1DE'
    },
    {
        name: 'Ethereum BEP2',
        chain: 'BNB',
        symbol: 'ETH-1C9'
    },
    {
        name: 'Trust Wallet',
        chain: 'BNB',
        symbol: 'TWT-8C2'
    },
    {
        name: 'Travala.com',
        chain: 'BNB',
        symbol: 'AVA-645'
    },
    {
        name: 'Fantom',
        chain: 'BNB',
        symbol: 'FTM-A64'
    },
    {
        name: 'Swingby',
        chain: 'BNB',
        symbol: 'SWINGBY-888'
    },
    {
        name: 'COTI',
        chain: 'BNB',
        symbol: 'COTI-CBB'
    },
    {
        name: 'CanYaCoin',
        chain: 'BNB',
        symbol: 'CAN-677'
    },
    {
        name: 'Ferrum Network',
        chain: 'BNB',
        symbol: 'FRM-DE7'
    },
    {
        name: '3x Long Bitcoin Token',
        chain: 'BNB',
        symbol: 'BULL-BE4'
    },
    {
        name: '3x Long Ethereum Token',
        chain: 'BNB',
        symbol: 'ETHBULL-D33'
    },
    {
        name: 'Morpheus Labs',
        chain: 'BNB',
        symbol: 'MITX-CAA'
    },
    {
        name: 'DOS Network',
        chain: 'BNB',
        symbol: 'DOS-120'
    },
    {
        name: 'Loki Network',
        chain: 'BNB',
        symbol: 'LOKI-6A9'
    },
    {
        name: 'Aergo',
        chain: 'BNB',
        symbol: 'AERGO-46B'
    },
    {
        name: 'BCH BEP2',
        chain: 'BNB',
        symbol: 'BCH-1FD'
    },
    {
        name: 'Bolt',
        chain: 'BNB',
        symbol: 'BOLT-4C6'
    },
    {
        name: 'Crypterium',
        chain: 'BNB',
        symbol: 'CRPT-8C9'
    },
    {
        name: 'Lition',
        chain: 'BNB',
        symbol: 'LIT-099'
    },
    {
        name: '3x Long EOS Token',
        chain: 'BNB',
        symbol: 'EOSBULL-F0D'
    },
    {
        name: 'XRP BEP2',
        chain: 'BNB',
        symbol: 'XRP-BF2'
    },
    {
        name: '3x Short Bitcoin Token',
        chain: 'BNB',
        symbol: 'BEAR-14C'
    },
    {
        name: 'ShareToken',
        chain: 'BNB',
        symbol: 'SHR-DB6'
    },
    {
        name: 'Bezant',
        chain: 'BNB',
        symbol: 'BZNT-464'
    },
    {
        name: 'Raven Protocol',
        chain: 'BNB',
        symbol: 'RAVEN-F66'
    },
];

// Sort by name
_assets.sort((a, b) => {
    if (a.name < b.name) {
        return -1;
    } else if (a.name > b.name) {
        return 1;
    } else {
        return 0;
    }
});
