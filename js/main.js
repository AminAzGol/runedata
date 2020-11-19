const _formatPrice = (p) => {
    return p.toFixed(p >= 1 ? 2 : 5);
}

const showSpinner = (text) => {
    $('#spinnerContainer').fadeIn();
};

const hideSpinner = () => {
    $('#spinnerContainer').fadeOut();
};

const generatePoolOptions = (select) => {
    for (asset of ASSETS) {
        select.append(new Option(`${asset.name} (${asset.chain}.${asset.symbol})`, `${asset.chain}.${asset.symbol}`));
    }
};

$(async () => {
    $('#simulateBtn').click(function () {
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#predictBtn').removeClass('btn-primary').addClass('btn-outline-primary');

        $('#simulateForm').show();
        $('#predictForm').hide();
    });

    $('#predictBtn').click(function () {
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#simulateBtn').removeClass('btn-primary').addClass('btn-outline-primary');

        $('#simulateForm').hide();
        $('#predictForm').show();
    });

    generatePoolOptions($('#poolSimulate'));
    generatePoolOptions($('#poolPredict'));

    getCurrentPrices(NODE_IP, ASSETS).then((prices) => {
        var poolPredict = $('#poolPredict');
        var priceTargetRune = $('#priceTargetRune');
        var priceTargetAsset = $('#priceTargetAsset');

        priceTargetRune.val(_formatPrice(prices['RUNE']));
        priceTargetAsset.val(_formatPrice(prices['BNB.BNB']));

        poolPredict.change(() => {
            priceTargetAsset.val(_formatPrice(prices[poolPredict.val()]));
        });
    });

    hideSpinner();
});
