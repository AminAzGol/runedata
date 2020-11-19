var _chart = null;

const _formatPrice = (p) => {
    return p.toFixed(p >= 1 ? 2 : 5);
}

const showSpinner = (text) => {
    $('#spinnerContainer').fadeIn();
};

const hideSpinner = () => {
    $('#spinnerContainer').fadeOut();
};

const hideOverlay = (overlay) => {
    overlay.hide();
}

const generatePoolOptions = (select) => {
    for (asset of ASSETS) {
        select.append(new Option(`${asset.name} (${asset.chain}.${asset.symbol})`, `${asset.chain}.${asset.symbol}`));
    }
};

$(async () => {
    $('#simulateBtn').click(function () {
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#predictBtn').removeClass('btn-primary').addClass('btn-outline-primary');

        $('#simulateContainer').show();
        $('#predictContainer').hide();
    });

    $('#predictBtn').click(function () {
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#simulateBtn').removeClass('btn-primary').addClass('btn-outline-primary');

        $('#simulateContainer').hide();
        $('#predictContainer').show();
    });

    $('#simulateSubmitBtn').click((event) => {
        event.preventDefault();

        var amountInvested = parseFloat($('#amountSimulate').val());
        var dateInvested = $('#dateSimulate').val();
        var pool = $('#poolSimulate').val();

        showSpinner();
        getPastSimulation(amountInvested, dateInvested, pool).then((userData) => {
            if (_chart) {
                _chart.destroy();
            }
            _chart = plotTotalValue($('#simulateChartCanvas'), userData);
            hideOverlay($('#simulateChartOverlay'));
            hideSpinner();
        });
    });

    // Generate options for pool selectors
    generatePoolOptions($('#poolSimulate'));
    generatePoolOptions($('#poolPredict'));

    // Draw placeholder images on canvas
    fitCanvasToContainer($('#simulateChartCanvas')[0]);
    drawPlaceholderImage($('#simulateChartCanvas')[0], 'images/simulateTotalValuePlaceholder.png');

    // Fetch asset prices
    const PRICES = await getCurrentPrices(ASSETS);

    var poolPredict = $('#poolPredict');
    var priceTargetRune = $('#priceTargetRune');
    var priceTargetAsset = $('#priceTargetAsset');

    priceTargetRune.val(_formatPrice(PRICES['RUNE']));
    priceTargetAsset.val(_formatPrice(PRICES['BNB.BNB']));

    poolPredict.change(() => {
        priceTargetAsset.val(_formatPrice(PRICES[poolPredict.val()]));
    });

    hideSpinner();
});
