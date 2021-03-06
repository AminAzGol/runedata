// https://stackoverflow.com/questions/39603447/how-can-i-change-the-font-family-for-the-labels-in-chart-js/48580585
// https://www.chartjs.org/docs/latest/general/fonts.html
Chart.defaults.global.defaultFontSize = 16;

// https://stackoverflow.com/questions/10214873/make-canvas-as-wide-and-as-high-as-parent
const fitCanvasToContainer = (canvas) => {
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
}

// https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage
const drawPlaceholderImage = (canvas, imageURL) => {
    var context = canvas.getContext('2d');
    var img = new Image();
    img.onload = () => {
        context.drawImage(img, 8, 8, canvas.width - 16, canvas.height - 16);  // 8 and 16 are paddings
    };
    img.src = imageURL;
};

// https://stackoverflow.com/questions/10865398/how-to-clear-an-html-canvas
const _clearCanvas = (canvas) => {
    canvas.width = canvas.width;  // Set height or width clears the canvas
};

const _barColor = (value) => {
    return value >= 0 ? 'green' : 'red';
};

const _getYOffset = (value) => {
    return value >= 0 ? -5 : +22;
};

const plotTotalValue = (canvas, userData, assetName = 'asset') => {
    var totalValueLP = [];
    var totalValueIfHoldRune = [];
    var totalValueIfHoldAsset = [];
    var totalValueIfHoldBoth = [];

    for (i = 0; i < userData.length; i++) {
        totalValueLP.push({
            x: new Date(userData[i].timestamp * 1000),
            y: userData[i].totalValue.toFixed(2)
        });
        totalValueIfHoldRune.push({
            x: new Date(userData[i].timestamp * 1000),
            y: userData[i].totalValueIfHoldRune.toFixed(2)
        });
        totalValueIfHoldAsset.push({
            x: new Date(userData[i].timestamp * 1000),
            y: userData[i].totalValueIfHoldAsset.toFixed(2)
        });
        totalValueIfHoldBoth.push({
            x: new Date(userData[i].timestamp * 1000),
            y: userData[i].totalValueIfHoldBoth.toFixed(2)
        });
    }

    _clearCanvas(canvas);

    var chart = new Chart(canvas, {
        type: 'line',
        data: {
            datasets: [{
                label: 'LP',
                data: totalValueLP,
                fill: false,
                borderColor: 'red',
                borderWidth: 2
            }, {
                label: 'hold RUNE',
                data: totalValueIfHoldRune,
                fill: false,
                borderColor: 'teal',
                borderWidth: 2
            }, {
                label: `hold ${assetName}`,
                data: totalValueIfHoldAsset,
                fill: false,
                borderColor: 'orange',
                borderWidth: 2
            }, {
                label: 'hold both',
                data: totalValueIfHoldBoth,
                fill: false,
                borderColor: 'blue',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,  // https://stackoverflow.com/questions/37621020/setting-width-and-height
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    scaleLabel: { display: true },
                    time: { unit: 'day' }
                }],
                yAxes: [{
                    ticks: {
                        callback: (value, index, values) => (value < 0 ? '–' : '') + '$' + Math.abs(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
                    }
                }]
            },
            elements: {
                point: {
                    radius: 0
                }
            },
            // https://stackoverflow.com/questions/42691873/draw-horizontal-line-on-chart-in-chart-js-on-v2
            // annotation: {
            //     annotations: [{
            //         type: 'line',
            //         mode: 'horizontal',
            //         scaleID: 'y-axis-0',
            //         value: userData[0].totalValue,
            //         borderColor: 'black',
            //         borderWidth: 1
            //     }]
            // }
        }
    });

    return chart;
};

const plotPoolRewards = (canvas, userData) => {
    var feeAccrued = [];
    var impermLoss = [];
    var totalGains = [];

    for (i = 0; i < userData.length; i++) {
        feeAccrued.push({
            x: new Date(userData[i].timestamp * 1000),
            y: (userData[i].feeAccrued * 100).toFixed(1)
        });
        impermLoss.push({
            x: new Date(userData[i].timestamp * 1000),
            y: (userData[i].impermLoss * 100).toFixed(1)
        });
        totalGains.push({
            x: new Date(userData[i].timestamp * 1000),
            y: (userData[i].totalGains * 100).toFixed(1)
        });
    }

    _clearCanvas(canvas);

    var chart = new Chart(canvas, {
        type: 'line',
        data: {
            datasets: [{
                label: 'fee & incentives accrued',
                data: feeAccrued,
                fill: false,
                borderColor: 'blue',
                borderWidth: 2
            }, {
                label: 'impermanent loss',
                data: impermLoss,
                fill: false,
                borderColor: 'red',
                borderWidth: 2
            }, {
                label: 'total gains vs HODL',
                data: totalGains,
                fill: false,
                borderColor: 'magenta',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    scaleLabel: { display: true },
                    time: { unit: 'day' }
                }],
                yAxes: [{
                    ticks: {
                        callback: (value, index, values) => (value >= 0 ? '+' : '–') + Math.abs(value) + '%'
                    },
                    gridLines:{
                        zeroLineColor: 'black'
                    }
                }]
            },
            elements: {
                point: {
                    radius: 0
                }
            }
        }
    });

    return chart;
};

const _roundToZeroIfSmall = (x) => Math.abs(x) < 1 ? +0 : x;

const _getYRangeForBarChart = (data) => {
    var max = Math.max(...data);
    var min = Math.min(...data);
    var range = max - min;
    var ymax = Math.max(max, 0) + 0.2 * range;
    var ymin = Math.min(min, 0) - 0.2 * range;
    return { ymax, ymin };
};

const plotPLBreakdown = (canvas, PLBreakdown, assetName = 'asset') => {
    _clearCanvas(canvas);

    var data = [
        _roundToZeroIfSmall(PLBreakdown.runeMovement.value.toFixed(2)),
        _roundToZeroIfSmall(PLBreakdown.assetMovement.value.toFixed(2)),
        _roundToZeroIfSmall(PLBreakdown.fees.value.toFixed(2)),
        _roundToZeroIfSmall(PLBreakdown.impermLoss.value.toFixed(2)),
        _roundToZeroIfSmall(PLBreakdown.total.value.toFixed(2))
    ];
    var { ymax, ymin } = _getYRangeForBarChart(data);

    var chart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: [
                'RUNE price movement',
                `${assetName} price movement`,
                'fees & incentives',
                'impermanent loss',
                'total profit'
            ],
            datasets: [{
                data,
                backgroundColor: [
                    _barColor(PLBreakdown.runeMovement.value),
                    _barColor(PLBreakdown.assetMovement.value),
                    _barColor(PLBreakdown.fees.value),
                    _barColor(PLBreakdown.impermLoss.value),
                    'magenta',
                ],
                borderColor: 'black',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // https://stackoverflow.com/questions/42556835/show-values-on-top-of-bars-in-chart-js
            hover: { animationDuration: 0 },
            animation: {
                duration: 1,
                onComplete: function() {
                  var chartInstance = this.chart,
                    ctx = chartInstance.ctx;

                  ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                  ctx.textAlign = 'center';
                  ctx.textBaseline = 'bottom';

                  this.data.datasets.forEach(function(dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function(bar, index) {
                      var data = dataset.data[index];
                      ctx.fillText(_formatPriceChange(data), bar._model.x, bar._model.y + _getYOffset(data));
                    });
                  });
                }
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: { display: true }
                }],
                yAxes: [{
                    ticks: {
                        max: ymax.toFixed(0),
                        min: ymin.toFixed(0),
                        callback: (value, index, values) => (value < 0 ? '–' : '+') + '$' + Math.abs(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
                    },
                    gridLines:{
                        zeroLineColor: 'black'
                    }
                }]
            },
            legend: { display: false },
            tooltips: { enabled: false }
        }
    });

    return chart;
};

const plotPrediction = (canvas, prediction, assetName = 'asset') => {
    _clearCanvas(canvas);

    var data = [
        _roundToZeroIfSmall(prediction.keepProvidingLiquidity.change),
        _roundToZeroIfSmall(prediction.withdrawAndHoldRune.change),
        _roundToZeroIfSmall(prediction.withdrawAndHoldAsset.change),
        _roundToZeroIfSmall(prediction.withdrawAndHoldBoth.change),
    ];
    var { ymax, ymin } = _getYRangeForBarChart(data);

    var chart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: [
                'keep providing liquidity',
                'withdraw and hold RUNE',
                `withdraw and hold ${assetName}`,
                'withdraw and hold both',
            ],
            datasets: [{
                data,
                backgroundColor: ['red', 'teal', 'orange', 'blue'],
                borderColor: 'black',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            hover: { animationDuration: 0 },
            animation: {
                duration: 1,
                onComplete: function() {
                  var chartInstance = this.chart,
                    ctx = chartInstance.ctx;

                  ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                  ctx.textAlign = 'center';
                  ctx.textBaseline = 'bottom';

                  this.data.datasets.forEach(function(dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function(bar, index) {
                      var data = dataset.data[index];
                      ctx.fillText(_formatPriceChange(data), bar._model.x, bar._model.y + _getYOffset(data));
                    });
                  });
                }
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: { display: true }
                }],
                yAxes: [{
                    ticks: {
                        max: ymax.toFixed(0),
                        min: ymin.toFixed(0),
                        callback: (value, index, values) => (value < 0 ? '–' : '+') + '$' + Math.abs(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
                    },
                    gridLines:{
                        zeroLineColor: 'black'
                    }
                }]
            },
            legend: { display: false },
            tooltips: { enabled: false }
        }
    });

    return chart;
};
