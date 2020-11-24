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

const showTooltip = (element, msg) => {
    element.tooltip('hide')
        .attr('data-original-title', msg)
        .tooltip('show');
};

const hideToolTip = (element, timeout = 1000) => {
    setTimeout(() => {
        element.tooltip('hide');
    }, timeout)
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

const displayBests = (bests) => {
    for (i = 0; i < 5; i++) {
        $(`#bestName${i}`).html(bests[i].pool.split('.')[1].split('-')[0]);
        $(`#bestChain${i}`).html(bests[i].pool.split('.')[0]);
        $(`#bestROI${i}`).html(_formatPercentChange(bests[i].roi));
        $(`#bestFees${i}`).html(_formatPercentChange(bests[i].feeAccrued));
        $(`#bestIL${i}`).html(_formatPercentChange(bests[i].impermLoss));
    }
};

const displayWorsts = (worsts) => {
    for (i = 0; i < 5; i++) {
        $(`#worstName${i}`).html(worsts[i].pool.split('.')[1].split('-')[0]);
        $(`#worstChain${i}`).html(worsts[i].pool.split('.')[0]);
        $(`#worstROI${i}`).html(_formatPercentChange(worsts[i].roi));
        $(`#worstFees${i}`).html(_formatPercentChange(worsts[i].feeAccrued));
        $(`#worstIL${i}`).html(_formatPercentChange(worsts[i].impermLoss));
    }
};

$(async () => {
    //========================================
    // Page selection buttons
    //========================================

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
    });

    //========================================
    // Functions for past simulation page
    //========================================

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

    //========================================
    // Functions for future prediction page
    //========================================

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

    //========================================
    // Submit buttons
    //========================================

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

    $('#leaderboardSubmitBtn')
    .tooltip({ placement: 'bottom' })
    .click((event) => {
        event.preventDefault();

        showSpinner();
        getAllAssetPerformances($('#leaderboardDate').val())
        .then(getBestsAndWorsts)
        .then((results) => {
            var { bests, worsts } = results;
            displayBests(bests);
            displayWorsts(worsts);
            hideSpinner();
        });
    });

    //========================================
    // Generate default page contents
    //========================================

    // Options for pool selectors
    generatePoolOptions($('#poolSimulate'));
    generatePoolOptions($('#poolPredict'));

    // Placeholder images
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

    //========================================
    // Read query strings
    //========================================

    var args = parseQueryString();

    if ( args.page == 'simulate' ) {
        $('#amountSimulate').val(args.amount);
        $('#dateSimulate').val(args.date);
        $('#poolSimulate').val(args.pool)
        $('#simulateBtn').trigger('click');
        $('#simulateSubmitBtn').trigger('click');
    } else if ( args.page == 'predict' ) {
        $('#amountPredict').val(args.amount);
        $('#dateToPredict').val(args.date);
        $('#poolPredict').val(args.pool);
        $('#timespanForAPY').val(args.timespan);
        $('#priceTargetRune').val(args.priceTargetRune);
        $('#priceTargetAsset').val(args.priceTargetAsset);
        $('#predictBtn').trigger('click');
        $('#predictSubmitBtn').trigger('click');
    } else if ( args.page == 'leaderboard' ) {
        $('#leaderboardDate').val(args.since);
        $('#leaderboardBtn').trigger('click');
        $('#leaderboardSubmitBtn').trigger('click');
    } else {
        // Default page behavior
        $('#simulateBtn').trigger('click');
        $('#simulateTotalValueToggle').trigger('click');
        $('#predictTotalValueToggle').trigger('click');
        hideSpinner();
    }
});
