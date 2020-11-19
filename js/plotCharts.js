const plotTotalValue = (canvas, userData) => {
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

    var chart = new Chart(canvas, {
        type: 'line',
        data: {
            datasets: [{
                label: 'LP',
                data: totalValueLP,
                fill: false,
                borderColor: 'red',
                borderWidth: 1.5
            }, {
                label: 'hold RUNE',
                data: totalValueIfHoldRune,
                fill: false,
                borderColor: 'teal',
                borderWidth: 1.5
            }, {
                label: 'hold asset',
                data: totalValueIfHoldAsset,
                fill: false,
                borderColor: 'orange',
                borderWidth: 1.5
            }, {
                label: 'hold both',
                data: totalValueIfHoldBoth,
                fill: false,
                borderColor: 'blue',
                borderWidth: 1.5
            }]
        },
        options: {
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    scaleLabel: { display: true },
                    time: { unit: 'day' }
                }],
                yAxes: [{
                    ticks: {
                        callback: (value, index, values) => '$' + value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
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
