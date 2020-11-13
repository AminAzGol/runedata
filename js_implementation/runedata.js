const fs = require('fs');

const _getKeysSorted = (obj) => {
    var keys = Object.keys(obj);
    keys = keys.map(x => +x);  // Cast strings to numbers
    keys = keys.sort((a, b) => a - b);  // Sort ascendingly
    return keys
}

const parseCSV = (path) => {
    var rows = fs.readFileSync(path, { encoding: 'utf-8' }).split('\n');
    rows = rows.slice(1, rows.length - 1);

    var data = {};

    for ( i = 0; i < rows.length; i++ ) {
        row = rows[i].split(',');
        data[row[0]] = {
            timestamp: parseInt(row[1]),
            poolUnits: parseInt(row[2]),
            balanceRune: parseInt(row[3]),
            balanceAsset: parseInt(row[4])
        };
    }

    return data;
};

const calculateUsdPrices = (assetData, busdData) => {
    var blockNumbersAsset = _getKeysSorted(assetData);
    var blockNumbersBusd = _getKeysSorted(busdData);
    var blockNumbers = blockNumbersAsset[0] > blockNumbersBusd[0] ? blockNumbersAsset : blockNumbersBusd;

    var assetDataWithPrices = {};

    for ( i = 0; i < blockNumbers.length; i++ ) {
        blockNumber = blockNumbers[i];
        blockAsset = assetData[blockNumber];
        blockBusd = busdData[blockNumber];

        runePriceUsd = blockBusd.balanceAsset / blockBusd.balanceRune;
        assetPriceRune = blockAsset.balanceRune / blockAsset.balanceAsset;
        assetPriceUsd = assetPriceRune * runePriceUsd;

        totalPoolValue = blockAsset.balanceAsset * assetPriceUsd + blockAsset.balanceRune * runePriceUsd;
        sharePriceUsd = totalPoolValue / blockAsset.poolUnits;

        assetDataWithPrices[blockNumber] = {
            ...blockAsset, runePriceUsd, assetPriceUsd, sharePriceUsd
        };
    }

    return assetDataWithPrices;
};

const calculateUserData = (amountInvested, timeInvested, assetData) => {
    // Find the first data point after timeInvested
    var blockNumbers = _getKeysSorted(assetData);
    for ( i = 0; i < blockNumbers.length; i++ ) {
        if (assetData[blockNumbers[i]].timestamp >= timeInvested) {
            break;
        }
    }

    blockNumbers = blockNumbers.slice(i, blockNumbers.length);
    var blockInvested = assetData[blockNumbers[0]];

    var userShare = amountInvested / blockInvested.sharePriceUsd;
    var userData = {};

    for (i = 0; i < blockNumbers.length; i++) {
        blockNumber = blockNumbers[i];
        block = assetData[blockNumber];

        // Balances
        runeBalance = userShare * block.balanceRune / block.poolUnits;
        assetBalance = userShare * block.balanceAsset / block.poolUnits;

        // Values
        runeValueUsd = runeBalance * block.runePriceUsd;
        assetValueUsd = assetBalance * block.assetPriceUsd;
        totalValueUsd = runeValueUsd + assetValueUsd;

        if (i == 0) {
            valueIfHoldRune = totalValueUsd;
            valueIfHoldAsset = totalValueUsd;
            valueIfHoldBothRuneAsset = totalValueUsd;

            feeAccrual = 0.;
            impermLoss = 0.;
            totalGainsVsHold = 0.;
        } else {
            valueIfHoldRune = 2 * userData[blockNumbers[0]].runeBalance * block.runePriceUsd;
            valueIfHoldAsset = 2 * userData[blockNumbers[0]].assetBalance * block.assetPriceUsd;
            valueIfHoldBothRuneAsset = (valueIfHoldRune + valueIfHoldAsset) / 2;

            kValue = runeBalance * assetBalance;
            kValueInit = userData[blockNumbers[0]].runeBalance * userData[blockNumbers[0]].assetBalance;
            feeAccrual = 0.5 * (kValue / kValueInit - 1);

            relativePrice = block.assetPriceUsd / block.runePriceUsd;
            relativePriceInit = blockInvested.assetPriceUsd / blockInvested.runePriceUsd;
            priceSwing = relativePrice / relativePriceInit;
            impermLoss = 2 * Math.sqrt(priceSwing) / (priceSwing + 1) - 1;

            totalGainsVsHold = totalValueUsd / valueIfHoldBothRuneAsset - 1;
        }

        userData[blockNumber] = {
            timestamp: block.timestamp,
            runeBalance, assetBalance, runeValueUsd, assetValueUsd, totalValueUsd,
            valueIfHoldRune, valueIfHoldAsset, valueIfHoldBothRuneAsset,
            feeAccrual, impermLoss, totalGainsVsHold
        };
    }

    return userData;
};

module.exports = { parseCSV, calculateUsdPrices, calculateUserData }

// Test
console.log(calculateUserData(
    amountInvested = 10000,
    timeInvested = 1603324800,
    assetData = calculateUsdPrices(parseCSV('../data/pool_BNB.BTCB-1DE.csv'), parseCSV('../data/pool_BNB.BUSD-BD1.csv'))
));
