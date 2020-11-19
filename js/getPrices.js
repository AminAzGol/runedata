const getCurrentPrices = async (nodeIP, assets) => {
    var query = 'asset=BNB.BUSD-BD1';
    for (asset of assets) {
        query += `,${asset.chain}.${asset.symbol}`;
    }

    var priceData = await $.get(`http://${nodeIP}:8080/v1/assets?${query}`);
    var runePriceUsd = 1 / parseFloat(priceData[0].priceRune);
    var prices = { 'RUNE': runePriceUsd };

    for (i = 1; i < priceData.length; i++) {
        prices[priceData[i].asset] = parseFloat(priceData[i].priceRune) * runePriceUsd
    }
    return prices;
};

const getHistoricalRunePrices = async (nodeIP, from, to) => {
    var busdData = await $.get(`http://${nodeIP}:8080/v1/history/pools?pool=BNB.BUSD-BD1&interval=hour&from=${from}&to=${to}`);
    var prices = {};
    for (i = 0; i < busdData.length; i++) {
        prices[busdData[i].time] = 1 / parseFloat(busdData[i].price);
    }
    return prices;
};

const getHistoricalPrices = async (nodeIP, asset, from, to) => {
    var busdData = await $.get(`http://${nodeIP}:8080/v1/history/pools?pool=BNB.BUSD-BD1&interval=hour&from=${from}&to=${to}`);
    var assetData = await $.get(`http://${nodeIP}:8080/v1/history/pools?pool=${asset.chain}.${asset.symbol}&interval=hour&from=${from}&to=${to}`);

    var prices = {};

    for (i = 0; i < busdData.length; i++) {
        runePriceUsd = 1 / parseFloat(busdData[i].price);
        assetPriceUsd = parseFloat(assetData[i].price) * runePriceUsd;
        prices[assetData[i].time] = assetPriceUsd;
    }
    return prices;
};
