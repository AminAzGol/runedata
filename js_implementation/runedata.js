const fs = require('fs');

// INPUT: path to a CSV file with the following format:
//
// block_number,timestamp,pool_units,balance_rune,balance_asset
// 157500,1598952349,20802124800,21682701709,19983007934
// 158125,1598955799,20802124800,21684792109,19983007934
// 158750,1598959250,20802124800,21686881587,19983007934
// 159375,1598962701,20802124800,21688997816,19983007934
// 160000,1598966150,20802124800,21691123830,19983007934
//
// Column headers must match exactly.
//
// OUTPUTS: object with the following format:
//
// {
//     157500: {
//         timestamp: 1598952349,
//         poolUnits: 20802124800,
//         balanceRune: 21682701709,
//         balanceAsset: 19983007934,
//     },
//     158125: { ... },
//     158750: { ... },
//     ...
// }
//
// The keys of this object are block numbers.
//
const parseCSV = (path) => {
    var lines = fs.readFileSync(path, { encoding: 'utf-8' }).split('\n');
    lines = lines.slice(1, lines.length - 1);  // Remove header and the empty line at the very end

    var data = {};
    var line = undefined;

    for ( i = 0; i < lines.length; i++ ) {
        line = lines[i].split(',');
        data[line[0]] = {
            timestamp: line[1],
            poolUnits: line[2],
            balanceRune: line[3],
            balanceAsset: line[4]
        };
    }

    return data;
};

// INPUTS:
//
// amountInvestedUsd: float
// timeInvested: int, timestamp in UTC
// assetData: object, same format as output by parseCSV
// busdData: object, same format as output by parseCSV
//
// The keys (block numbers) of assetData must be a subset of busdData.
//
// OUTPUTS: object with the following format:
//
// {
//     157500: {
//         timestamp: ... ,
//         runePriceUsd: ... ,
//         assetPriceUsd: ... ,
//         runeBalance: ... ,
//         assetBalance: ... ,
//         runeValueUsd: ... ,
//         assetValueUsd: ... ,
//         totalValueUsd: ... ,
//         ValueIfHoldRune: ... ,
//         ValueIfHoldAsset: ... ,
//         feeAccrual: ... ,
//         impermLoss: ... ,
//         totalGainsVsHold: ...
//     },
//     158125: { ... },
//     158750: { ... },
//     ...
// }
//
const calculateUserData = (amountInvestedUsd, timeInvested, assetData, busdData) => {
    //pass
};

// Test
busdData = parseCSV('../data/pool_BNB.BUSD-BD1.csv');
btcbData = parseCSV('../data/pool_BNB.BTCB-1DE.csv');
