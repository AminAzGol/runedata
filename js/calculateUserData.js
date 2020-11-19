const getCurrentPrices = async (assets) => {
    var query = 'asset=BNB.BUSD-BD1';
    for (asset of assets) {
        query += `,${asset.chain}.${asset.symbol}`;
    }

    var priceData = await $.get(`https://chaosnet-midgard.bepswap.com/v1/assets?${query}`);
    var runePriceUsd = 1 / parseFloat(priceData[0].priceRune);
    var prices = { 'RUNE': runePriceUsd };

    for (i = 1; i < priceData.length; i++) {
        prices[priceData[i].asset] = parseFloat(priceData[i].priceRune) * runePriceUsd
    }
    return prices;
};

const getPastSimulation = async (amountInvested, dateInvested, pool) => {
    var from = Math.floor((new Date(dateInvested)).getTime() / 1000);
    var to = Math.floor(Date.now() / 1000);

    var busdData = await $.get(`https://chaosnet-midgard.bepswap.com/v1/history/pools?pool=BNB.BUSD-BD1&interval=hour&from=${from}&to=${to}`);
    var assetData = await $.get(`https://chaosnet-midgard.bepswap.com/v1/history/pools?pool=${pool}&interval=hour&from=${from}&to=${to}`);
    var assetDataCurrent = await $.get(`https://chaosnet-midgard.bepswap.com/v1/pools/detail?asset=${pool}`);

    // Calculate RUNE and asset prices
    for (i = 0; i < assetData.length; i++) {
        assetData[i].runePrice = 1 / busdData[i].price;
        assetData[i].assetPrice = assetData[i].price * assetData[i].runePrice;
    }

    // Calculate amount of pool units at each timestamp
    assetData[assetData.length - 1].poolUnits = assetDataCurrent[0].poolUnits;

    for (i = assetData.length - 1; i > 0; i--) {
        assetData[i - 1].poolUnits = assetData[i].poolUnits - assetData[i].unitsChanges;
    }

    // Calculate share price at the time of investment
    var sharePrice = (assetData[0].runeDepth * assetData[0].runePrice + assetData[0].assetDepth * assetData[0].assetPrice) / assetData[0].poolUnits;
    var userShare = amountInvested / sharePrice;

    var userData = [];

    for (i = 0; i < assetData.length; i++) {
        // User balance
        runeBalance = userShare * assetData[i].runeDepth / assetData[i].poolUnits;
        assetBalance = userShare * assetData[i].assetDepth / assetData[i].poolUnits;

        runeValue = runeBalance * assetData[i].runePrice;
        assetValue = assetBalance * assetData[i].assetPrice;
        totalValue = runeValue + assetValue;

        userData.push({ runeBalance, assetBalance, runeValue, assetValue, totalValue });

        totalValueIfHoldRune = 2 * userData[0].runeBalance * assetData[i].runePrice;
        totalValueIfHoldAsset = 2 * userData[0].assetBalance * assetData[i].assetPrice;
        totalValueIfHoldBoth = 0.5 * (totalValueIfHoldRune + totalValueIfHoldAsset);

        // Fee accrued
        kValue = runeBalance * assetBalance;
        kValueInit = userData[0].runeBalance * userData[0].assetBalance;
        feeAccrued = 0.5 * (kValue / kValueInit - 1);

        // Imperm Loss
        priceSwing = assetData[i].price / assetData[0].price;
        impermLoss = 2 * Math.sqrt(priceSwing) / (priceSwing + 1) - 1;

        // Total gains
        totalGains = totalValue / totalValueIfHoldBoth - 1;

        userData[i] = {
            ...userData[i],
            totalValueIfHoldRune, totalValueIfHoldAsset, totalValueIfHoldBoth,
            feeAccrued, impermLoss, totalGains
        };
    }

    return userData;
};

const calculatePnlBreakdown = (userData) => {
    //pass
};
