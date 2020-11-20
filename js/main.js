var _prices = null;

var _placeholderText = 'Pick your options below, then hit "Submit" to continue.';
var _assetName = null;
var _userData = null;
var _plBreakdown = null;
var _projection = null;
var _projectionBreakdown = null;

var _simulateTotalValueChart = null;
var _simulatePoolRewardsChart = null;
var _simulatePLBreakdownChart = null;
var _predictValueProjectionChart = null;
var _predictProjectionBreakdownChart = null;

const getSimulateTotalValueText = () => {
    if (!_userData) {
        return _placeholderText;
    }

    var totalValue = _userData[_userData.length - 1].totalValue;
    var precentChange = (totalValue / _userData[0].totalValue - 1);

    var totalValueIfHoldRune = _userData[_userData.length - 1].totalValueIfHoldRune;
    var totalValueIfHoldRuneVsLP = (totalValueIfHoldRune / totalValue - 1);

    var totalValueIfHoldAsset = _userData[_userData.length - 1].totalValueIfHoldAsset;
    var totalValueIfHoldAssetVsLP = (totalValueIfHoldAsset / totalValue - 1);

    return `
        The current value of your investment is <b>${_formatTotalValue(totalValue)}</b>
        (${_formatPercentChange(precentChange)})
        <br>
        If you had passively held <b>RUNE</b>, you would have <b>${_formatTotalValue(totalValueIfHoldRune)}</b>
        (${_formatPercentChange(totalValueIfHoldRuneVsLP)} vs LP)
        <br>
        If you had passively held <b>${_assetName}</b>, you would have <b>${_formatTotalValue(totalValueIfHoldAsset)}</b>
        (${_formatPercentChange(totalValueIfHoldAssetVsLP)} vs LP)
    `;
};

const getSimulatePoolRewardsText = () => {
    if (!_userData) {
        return _placeholderText;
    }

    var feeAccrued = _userData[_userData.length - 1].feeAccrued;
    var impermLoss = _userData[_userData.length - 1].impermLoss;
    var totalGains = feeAccrued + impermLoss;

    var startTime = _userData[0].timestamp;
    var endTime = _userData[_userData.length - 1].timestamp;

    var apyFeeOnly = feeAccrued * 365 * 24 * 60 * 60 / (endTime - startTime);
    var apyTotal = totalGains * 365 * 24 * 60 * 60 / (endTime - startTime)

    return `
        <p>
            Compared to passively holding 50:50 <b>RUNE</b> & <b>${_assetName}</b>, you gained
            <b>${_formatPercentChange(feeAccrued, false)}</b> from fees & rewards, lost
            <b>${_formatPercentChange(impermLoss, false)}</b> due to impermanent loss (IL).
            Overall, LP ${_outOrUnderperform(totalGains)} HODL by <b>${_formatPercentChange(totalGains, false)}</b>.
        </p>
        Extrapolating to a year, the APY is approximately <b>${_formatPercentChange(apyFeeOnly)}</b> (fees only)
        or <b>${_formatPercentChange(apyTotal)}</b> (fees + IL).
    `;
};

const getSimulatePLBreakdownText = () => {
    if (!_plBreakdown) {
        return _placeholderText;
    }
    return `
        <p>
            You ${_gainOrLoss(_plBreakdown.runeMovement.value)} <b>${_formatTotalValue(_plBreakdown.runeMovement.value)}</b>
            (<b>${_formatPercentChange(_plBreakdown.runeMovement.percentage)}</b>) due to <b>RUNE</b> price going
            ${_upOrDown(_plBreakdown.runeMovement.value)}, and ${_gainOrLoss(_plBreakdown.assetMovement.value)}
            <b>${_formatTotalValue(_plBreakdown.assetMovement.value)}</b> (<b>${_formatPercentChange(_plBreakdown.assetMovement.percentage)}</b>)
            due to <b>${_assetName}</b> going ${_upOrDown(_plBreakdown.assetMovement.value)}.
        </p>
        <p>
            You earned <b>${_formatTotalValue(_plBreakdown.fees.value)}</b> (<b>${_formatPercentChange(_plBreakdown.fees.percentage)}</b>)
            from fees & rewards, and lost <b>${_formatTotalValue(_plBreakdown.impermLoss.value)}</b>
            (<b>${_formatPercentChange(_plBreakdown.impermLoss.percentage)}</b>) due to impermanent loss.
        </p>
        Overall, you are ${_upOrDown(_plBreakdown.total.value)} <b>${_formatTotalValue(_plBreakdown.total.value)}</b>
        (<b>${_formatPercentChange(_plBreakdown.total.percentage)}</b>) compared to your initial investment.
    `;
};

const getValueProjectionText = () => {
    if (!_projection) {
        return _placeholderText;
    }
};

const getProjectionBreakdownText = () => {
    if (!_projectionBreakdown) {
        return _placeholderText;
    }
};

const showSpinner = (text) => {
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
        $('#simulateResultText').html(getSimulateTotalValueText());
    });

    $('#poolRewardsToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').hide();
        $('#simulatePoolRewardsCanvas').show();
        $('#simulatePLBreakdownCanvas').hide();
        $('#simulateResultText').html(getSimulatePoolRewardsText());
    });

    $('#PLBreakdownToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#simulateTotalValueCanvas').hide();
        $('#simulatePoolRewardsCanvas').hide();
        $('#simulatePLBreakdownCanvas').show();
        $('#simulateResultText').html(getSimulatePLBreakdownText());
    });

    $('#valueProjectionToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#predictValueProjectionCanvas').show();
        $('#predictProjectionBreakdownCanvas').hide();
        $('#predictResultText').html(getValueProjectionText());
    });

    $('#projectionBreakdownToggle').click(function (event) {
        event.preventDefault();
        setActiveToggle($(this));
        $('#predictValueProjectionCanvas').hide();
        $('#predictProjectionBreakdownCanvas').show();
        $('#predictResultText').html(getProjectionBreakdownText());
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
            _plBreakdown = calculatePLBreakdown(userData);

            if (_simulateTotalValueChart) {
                _simulateTotalValueChart.destroy();
            }
            if (_simulatePoolRewardsChart) {
                _simulatePoolRewardsChart.destroy();
            }
            if (_simulatePLBreakdownChart) {
                _simulatePLBreakdownChart.destroy();
            }

            _simulateTotalValueChart = plotTotalValue($('#simulateTotalValueCanvas'), userData, _assetName);
            _simulatePoolRewardsChart = plotPoolRewards($('#simulatePoolRewardsCanvas'), userData);
            _simulatePLBreakdownChart = plotPLBreakdown($('#simulatePLBreakdownCanvas'), _plBreakdown, _assetName);

            $('#totalValueToggle').trigger('click');
            $('#simulateChartOverlay').hide();
            hideSpinner();
        });
    });

    $('#predictSubmitBtn').click((event) => {
        event.preventDefault();
        showSpinner();

        calculateValueProjection(
            parseFloat($('#amountPredict').val()),
            $('#dateToPredict').val(),
            $('#poolPredict').val(),
            $('#timespanForAPY').val(),
            parseFloat($('#priceTargetRune').val()),
            parseFloat($('#priceTargetAsset').val()),
            _prices
        )
        .then((projection) => {
            _assetName = $('#poolPredict').val().split('.')[1].split('-')[0];
            _projection = projection;
            console.log(projection);

            if (_predictValueProjectionChart) {
                _predictValueProjectionChart.destroy();
            }
            if (_predictProjectionBreakdownChart) {
                _predictProjectionBreakdownChart.destroy();
            }

            _predictValueProjectionChart = plotValueProjection($('#predictValueProjectionCanvas'), projection, _assetName);
            _predictProjectionBreakdownCanvas = plotProjectionBreakdown(projection, _assetName);

            $('#valueProjectionToggle').trigger('click');
            $('#predictChartOverlay').hide();
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

    fitCanvasToContainer($('#simulatePLBreakdownCanvas')[0]);
    drawPlaceholderImage($('#simulatePLBreakdownCanvas')[0], 'images/simulatePLBreakdownPlaceholder.png');

    fitCanvasToContainer($('#predictValueProjectionCanvas')[0]);
    drawPlaceholderImage($('#predictValueProjectionCanvas')[0], 'images/predictValueProjectionPlaceholder.png');

    fitCanvasToContainer($('#predictProjectionBreakdownCanvas')[0]);
    // drawPlaceholderImage($('#predictProjectionBreakdownCanvas')[0], 'images/predictProjectionBreakdownPlaceholder.png');

    // Default page to simulate, total page on load
    $('#simulateBtn').trigger('click');
    $('#totalValueToggle').trigger('click');
    $('#valueProjectionToggle').trigger('click');

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
