var placeholderText = 'Pick your options below, then hit "Submit" to continue.';

const getSimulateTotalValueText = (userData) => {
    if (!userData) {
        return placeholderText;
    }

    var totalValue = userData[userData.length - 1].totalValue;
    var precentChange = (totalValue / userData[0].totalValue - 1);

    var totalValueIfHoldRune = userData[userData.length - 1].totalValueIfHoldRune;
    var totalValueIfHoldRuneVsLP = (totalValueIfHoldRune / totalValue - 1);

    var totalValueIfHoldAsset = userData[userData.length - 1].totalValueIfHoldAsset;
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

const getSimulatePoolRewardsText = (userData) => {
    if (!userData) {
        return placeholderText;
    }

    var feeAccrued = userData[userData.length - 1].feeAccrued;
    var impermLoss = userData[userData.length - 1].impermLoss;
    var totalGains = feeAccrued + impermLoss;

    var startTime = userData[0].timestamp;
    var endTime = userData[userData.length - 1].timestamp;

    var apyFeeOnly = feeAccrued * 365 * 24 * 60 * 60 / (endTime - startTime);
    var apyTotal = totalGains * 365 * 24 * 60 * 60 / (endTime - startTime)

    return `
      <p>
        Compared to passively holding 50:50 <b>RUNE</b> & <b>${_assetName}</b>, you gained
        <b>${_formatPercentChange(feeAccrued, false)}</b> from fees & incentives, lost
        <b>${_formatPercentChange(impermLoss, false)}</b> due to impermanent loss (IL).
        Overall, LP ${_outOrUnderperform(totalGains)} HODL by <b>${_formatPercentChange(totalGains, false)}</b>.
      </p>
      Extrapolating to a year, the APY is approximately <b>${_formatPercentChange(apyFeeOnly)}</b> (fees only)
      or <b>${_formatPercentChange(apyTotal)}</b> (fees + IL).
    `;
};

const getSimulatePLBreakdownText = (PLBreakdown, assetName = 'asset') => {
    if (!PLBreakdown) {
        return placeholderText;
    }

    return `
      <p>
        You ${_gainedOrLost(PLBreakdown.runeMovement.value)} <b>${_formatTotalValue(PLBreakdown.runeMovement.value)}</b>
        (<b>${_formatPercentChange(PLBreakdown.runeMovement.percentage)}</b>) due to <b>RUNE</b> price going
        ${_upOrDown(PLBreakdown.runeMovement.value)}, and ${_gainedOrLost(PLBreakdown.assetMovement.value)}
        <b>${_formatTotalValue(PLBreakdown.assetMovement.value)}</b> (<b>${_formatPercentChange(PLBreakdown.assetMovement.percentage)}</b>)
        due to <b>${assetName}</b> going ${_upOrDown(PLBreakdown.assetMovement.value)}.
      </p>
      <p>
        You earned <b>${_formatTotalValue(PLBreakdown.fees.value)}</b> (<b>${_formatPercentChange(PLBreakdown.fees.percentage)}</b>)
        from fees & incentives, and lost <b>${_formatTotalValue(PLBreakdown.impermLoss.value)}</b>s
        (<b>${_formatPercentChange(PLBreakdown.impermLoss.percentage)}</b>) due to impermanent loss.
      </p>
      Overall, you are ${_upOrDown(PLBreakdown.total.value)} <b>${_formatTotalValue(PLBreakdown.total.value)}</b>
      (<b>${_formatPercentChange(PLBreakdown.total.percentage)}</b>) compared to your initial investment.
    `;
};

const getPredictTotalValueText = (prediction, assetName = 'asset') => {
    if (!prediction) {
        return placeholderText;
    }

    return `
    <p>
      If keep providing liquidity, you will have <b>${_formatTotalValue(prediction.keepProvidingLiquidity.totalValue)}</b>
      (<b>${_formatTotalValueChange(prediction.keepProvidingLiquidity.change)}</b>) on the specified date.
    </p>
    If withdraw and hold either <b>RUNE</b> or <b>${assetName}</b>, you will have <b>${_formatTotalValue(prediction.withdrawAndHoldRune.totalValue)}</b>
    (<b>${_formatTotalValueChange(prediction.withdrawAndHoldRune.change)}</b>) or <b>${_formatTotalValue(prediction.withdrawAndHoldAsset.totalValue)}</b>
    (<b>${_formatTotalValueChange(prediction.withdrawAndHoldAsset.change)}</b>), respectively.
    `;
};

const getPredictPLBreakdownText = (PLBreakdown, assetName = 'asset') => {
    if (!PLBreakdown) {
        return placeholderText;
    }

    return `
      <p>
        You will ${_gainOrLose(PLBreakdown.runeMovement.value)} <b>${_formatTotalValue(PLBreakdown.runeMovement.value)}</b>
        (<b>${_formatPercentChange(PLBreakdown.runeMovement.percentage)}</b>) due to <b>RUNE</b> price going
        ${_upOrDown(PLBreakdown.runeMovement.value)}, and ${_gainOrLose(PLBreakdown.assetMovement.value)}
        <b>${_formatTotalValue(PLBreakdown.assetMovement.value)}</b> (<b>${_formatPercentChange(PLBreakdown.assetMovement.percentage)}</b>)
        due to <b>${assetName}</b> going ${_upOrDown(PLBreakdown.assetMovement.value)}.
      </p>
      <p>
        You will earn <b>${_formatTotalValue(PLBreakdown.fees.value)}</b> (<b>${_formatPercentChange(PLBreakdown.fees.percentage)}</b>)
        from fees & incentives, and lose <b>${_formatTotalValue(PLBreakdown.impermLoss.value)}</b>
        (<b>${_formatPercentChange(PLBreakdown.impermLoss.percentage)}</b>) due to IL.
      </p>
      Overall, you will be ${_upOrDown(PLBreakdown.total.value)} <b>${_formatTotalValue(PLBreakdown.total.value)}</b>
      (<b>${_formatPercentChange(PLBreakdown.total.percentage)}</b>) compared to your initial investment.
    `;
};
