var _placeholderText = 'Pick your options below, then hit "Submit" to continue.';
var _assetName = null;
var _userData = null;
var _plBreakdown = null;

var _simulateTotalValueChart = null;
var _simulatePoolRewardsChart = null;
var _simulatePLBreakdownChart = null;

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
    var apy = totalGains * 365 * 24 * 60 * 60 / (endTime - startTime)

    return `
        <p>
            Compared to passively holding 50:50 <b>RUNE</b> & <b>${_assetName}</b>, you gained
            <b>${_formatPercentChange(feeAccrued, false)}</b> from fees & rewards, lost
            <b>${_formatPercentChange(impermLoss, false)}</b> due to impermanent loss (IL).
            Overall, LP ${_outOrUnderperform(totalGains)} HODL by <b>${_formatPercentChange(totalGains, false)}</b>.
        </p>
        Extrapolating to a year, the fee APY (not including IL) is approximately <b>${_formatPercentChange(apy)}</b>.
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

    $('#simulateSubmitBtn').click((event) => {
        event.preventDefault();

        var amountInvested = parseFloat($('#amountSimulate').val());
        var dateInvested = $('#dateSimulate').val();
        var pool = $('#poolSimulate').val();

        showSpinner();
        getPastSimulation(amountInvested, dateInvested, pool).then((userData) => {
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
