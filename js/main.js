var _simulateTotalValueChart = null;
var _simulatePoolRewardsChart = null;
var _simulatePLBreakdownChart = null;

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

const setActiveToggle = (toggle) => {
    $('#totalValueToggle').parent().parent().find('.nav-link').removeClass('active');
    toggle.addClass('active');
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

    $('#totalValueToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').show();
        $('#simulatePoolRewardsCanvas').hide();
        $('#simulatePLBreakdownCanvas').hide();
    });

    $('#poolRewardsToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').hide();
        $('#simulatePoolRewardsCanvas').show();
        $('#simulatePLBreakdownCanvas').hide();
    });

    $('#PLBreakdownToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').hide();
        $('#simulatePoolRewardsCanvas').hide();
        $('#simulatePLBreakdownCanvas').show();
    });

    $('#simulateSubmitBtn').click((event) => {
        event.preventDefault();

        var amountInvested = parseFloat($('#amountSimulate').val());
        var dateInvested = $('#dateSimulate').val();
        var pool = $('#poolSimulate').val();

        showSpinner();
        getPastSimulation(amountInvested, dateInvested, pool).then((userData) => {
            if (_simulateTotalValueChart) {
                _simulateTotalValueChart.destroy();
            }
            if (_simulatePoolRewardsChart) {
                _simulatePoolRewardsChart.destroy();
            }
            _simulateTotalValueChart = plotTotalValue($('#simulateTotalValueCanvas'), userData);
            _simulatePoolRewardsChart = plotPoolRewards($('#simulatePoolRewardsCanvas'), userData);
            $('#totalValueToggle').trigger('click');
            $('#simulateChartOverlay').hide();
            hideSpinner();
        });
    });

    // Generate options for pool selectors
    generatePoolOptions($('#poolSimulate'));
    generatePoolOptions($('#poolPredict'));

    // Draw placeholder images on canvas
    fitCanvasToContainer($('#simulateTotalValueCanvas')[0]);
    drawPlaceholderImage($('#simulateTotalValueCanvas')[0], 'images/simulateTotalValuePlaceholder.png');

    fitCanvasToContainer($('#simulatePoolRewardsCanvas')[0]);
    drawPlaceholderImage($('#simulatePoolRewardsCanvas')[0], 'images/simulatePoolRewardsPlaceholder.png');

    // Default page to simulate, total page on load
    $('#simulateBtn').trigger('click');
    $('#totalValueToggle').trigger('click');

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
