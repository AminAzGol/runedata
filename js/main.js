// Global variables to be accessible by all functions
// Asset name & prices
var _assetName = null;
var _prices = null;

// Calculation results
var _userData = null;
var _PLBreakdown = null;
var _prediction = null;
var _predictionBreakdown = null;

// Charts
var _simulateTotalValueChart = null;
var _simulateFeesVsILChart = null;
var _simulatePLBreakdownChart = null;
var _predictTotalValueChart = null;
var _predictPLBreakdownChart = null;

const showSpinner = () => {
    $('#spinnerContainer').fadeIn();
};

const hideSpinner = () => {
    $('#spinnerContainer').fadeOut();
};

const generatePoolOptions = (select) => {
    for (asset of _assets) {
        select.append(new Option(`${asset.name} (${asset.chain}.${asset.symbol})`, `${asset.chain}.${asset.symbol}`));
    }
};

const setActiveToggle = (toggle) => {
    toggle.parent().parent().find('.nav-link').removeClass('active');
    toggle.addClass('active');
};

$(async () => {
    $('#simulateBtn').click(function () {
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#predictBtn').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#leaderboardBtn').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#simulateContainer').show();
        $('#predictContainer').hide();
        $('#leaderboardContainer').hide();
    });

    $('#predictBtn').click(function () {
        $('#simulateBtn').removeClass('btn-primary').addClass('btn-outline-primary');
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#leaderboardBtn').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#simulateContainer').hide();
        $('#predictContainer').show();
        $('#leaderboardContainer').hide();
    });

    $('#leaderboardBtn').click(function () {
        $('#simulateBtn').removeClass('btn-primary').addClass('btn-outline-primary');
        $('#predictBtn').removeClass('btn-primary').addClass('btn-outline-primary');
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#simulateContainer').hide();
        $('#predictContainer').hide();
        $('#leaderboardContainer').show();
        alert('This feature has not been implemented yet!! You are seeing dummy data.');
    });

    $('#simulateTotalValueToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').show();
        $('#simulateFeesVsILCanvas').hide();
        $('#simulatePLBreakdownCanvas').hide();
        $('#simulateResultText').html(getSimulateTotalValueText(_userData, _assetName));
    });

    $('#simulateFeesVsILToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').hide();
        $('#simulateFeesVsILCanvas').show();
        $('#simulatePLBreakdownCanvas').hide();
        $('#simulateResultText').html(getSimulatePoolRewardsText(_userData));
    });

    $('#simulatePLBreakdownToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').hide();
        $('#simulateFeesVsILCanvas').hide();
        $('#simulatePLBreakdownCanvas').show();
        $('#simulateResultText').html(getSimulatePLBreakdownText(_PLBreakdown, _assetName));
    });

    $('#predictTotalValueToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#predictTotalValueCanvas').show();
        $('#predictPLBreakdownCanvas').hide();
        $('#predictResultText').html(getPredictTotalValueText(_prediction, _assetName));
    });

    $('#predictPLBreakdownToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#predictTotalValueCanvas').hide();
        $('#predictPLBreakdownCanvas').show();
        $('#predictResultText').html(getPredictPLBreakdownText(_predictionBreakdown, _assetName));
    });

    $('#simulateSubmitBtn').click((event) => {
        event.preventDefault();
        showSpinner();

        getPastSimulation(
            parseFloat($('#amountSimulate').val()),
            $('#dateSimulate').val(),
            $('#poolSimulate').val()
        )
        .then((userData) => {
            _assetName = $('#poolSimulate').val().split('.')[1].split('-')[0];
            _userData = userData;
            _PLBreakdown = calculatePLBreakdown(userData);

            if (_simulateTotalValueChart) {
                _simulateTotalValueChart.destroy();
            }
            if (_simulateFeesVsILChart) {
                _simulateFeesVsILChart.destroy();
            }
            if (_simulatePLBreakdownChart) {
                _simulatePLBreakdownChart.destroy();
            }

            _simulateTotalValueChart = plotTotalValue($('#simulateTotalValueCanvas'), userData, _assetName);
            _simulateFeesVsILChart = plotPoolRewards($('#simulateFeesVsILCanvas'), userData);
            _simulatePLBreakdownChart = plotPLBreakdown($('#simulatePLBreakdownCanvas'), _PLBreakdown, _assetName);

            $('#simulateTotalValueToggle').trigger('click');
            $('#simulateChartOverlay').hide();
            $('#simulateContainer').find('canvas').removeClass('blur');
            hideSpinner();
        });
    });

    $('#predictSubmitBtn').click((event) => {
        event.preventDefault();
        showSpinner();

        calculatePrediction(
            parseFloat($('#amountPredict').val()),
            $('#dateToPredict').val(),
            $('#poolPredict').val(),
            $('#timespanForAPY').val(),
            parseFloat($('#priceTargetRune').val()),
            parseFloat($('#priceTargetAsset').val()),
            _prices
        )
        .then((results) => {
            var { prediction, predictionBreakdown } = results;

            _assetName = $('#poolPredict').val().split('.')[1].split('-')[0];
            _prediction = prediction;
            _predictionBreakdown = predictionBreakdown;
            console.log(prediction);
            console.log(predictionBreakdown);

            if (_predictTotalValueChart) {
                _predictTotalValueChart.destroy();
            }
            if (_predictPLBreakdownChart) {
                _predictPLBreakdownChart.destroy();
            }

            _predictTotalValueChart = plotPrediction($('#predictTotalValueCanvas'), prediction, _assetName);
            _predictPLBreakdownChart = plotPLBreakdown($('#predictPLBreakdownCanvas'), predictionBreakdown, _assetName);

            $('#predictTotalValueToggle').trigger('click');
            $('#predictChartOverlay').hide();
            $('#predictContainer').find('canvas').removeClass('blur');
            hideSpinner();
        });
    });

    // Generate options for pool selectors
    generatePoolOptions($('#poolSimulate'));
    generatePoolOptions($('#poolPredict'));

    // Draw placeholder images on canvas
    fitCanvasToContainer($('#simulateTotalValueCanvas')[0]);
    drawPlaceholderImage($('#simulateTotalValueCanvas')[0], 'images/simulateTotalValuePlaceholder.png');

    fitCanvasToContainer($('#simulateFeesVsILCanvas')[0]);
    drawPlaceholderImage($('#simulateFeesVsILCanvas')[0], 'images/feesVsILPlaceholder.png');

    fitCanvasToContainer($('#simulatePLBreakdownCanvas')[0]);
    drawPlaceholderImage($('#simulatePLBreakdownCanvas')[0], 'images/PLBreakdownPlaceholder.png');

    fitCanvasToContainer($('#predictTotalValueCanvas')[0]);
    drawPlaceholderImage($('#predictTotalValueCanvas')[0], 'images/predictTotalValuePlaceholder.png');

    fitCanvasToContainer($('#predictPLBreakdownCanvas')[0]);
    drawPlaceholderImage($('#predictPLBreakdownCanvas')[0], 'images/PLBreakdownPlaceholder.png');

    // Default page to simulate, total page on load
    $('#simulateBtn').trigger('click');
    $('#simulateTotalValueToggle').trigger('click');
    $('#predictTotalValueToggle').trigger('click');

    // Fetch asset prices
    _prices = await getCurrentPrices(_assets);

    var poolPredict = $('#poolPredict');
    var priceTargetRune = $('#priceTargetRune');
    var priceTargetAsset = $('#priceTargetAsset');

    priceTargetRune.val(_formatPrice(_prices['RUNE']));
    priceTargetAsset.val(_formatPrice(_prices[`${_assets[0].chain}.${_assets[0].symbol}`]));

    poolPredict.change(() => {
        priceTargetAsset.val(_formatPrice(_prices[poolPredict.val()]));
    });

    hideSpinner();
});
