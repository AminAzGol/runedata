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

    _clearCanvas(canvas);

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
            // responsive: true,  // https://stackoverflow.com/questions/37621020/setting-width-and-height
            // maintainAspectRatio: false,
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    scaleLabel: { display: true },
                    time: { unit: 'day' },
                    ticks: { fontSize: 16 }
                }],
                yAxes: [{
                    ticks: {
                        fontSize: 16,
                        callback: (value, index, values) => '$' + value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
                    }
                }]
            },
            elements: {
                point: {
                    radius: 0
                }
            },
            legend: {
                labels: {
                    fontSize: 16
                }
            }
        }
    });

    return chart;
};
