const _outOrUnderperform = (val) => val >= 0 ? 'outperforms' : 'underperforms';
const _upOrDown = (val) => val >= 0 ? 'up' : 'down';
const _gainOrLose = (val) => val >= 0 ? 'will gain' : 'will lose';
const _gainedOrLost = (val) => val >= 0 ? 'gained' : 'lost';

const _formatPrice = (p) => {
    return p.toFixed(p >= 1 ? 2 : 5);
};

const _formatTotalValue = (v) => {
    return '$' + Math.abs(v).toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

const _formatPriceChange = (value) => {
    if (value >= 0) {
        var sign = '+';
    } else {
        var sign = '–';
    }
    return sign + '$' + Math.abs(value).toFixed(0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

const _formatTotalValueChange = (value) => {
    if (value >= 0) {
        var sign = '+';
    } else {
        var sign = '–';
    }
    color = value >= 0 ? 'green' : 'red';
    return `<b style="color: ${color}">${sign}$` + Math.abs(value).toFixed(0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '</b>';
};

const _formatPercentChange = (pc, signed = true) => {
    if (signed) {
        sign = pc >= 0 ? '+' : '–';
    } else {
        sign = '';
    }
    color = pc >= 0 ? 'green' : 'red';
    pc = Math.abs(pc) * 100;
    pc = pc.toFixed(pc < 10 ? 1 : 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return `<b style="color: ${color}">${sign}${pc}%</b>`;
};

const parseQueryString = () => {
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    var args = {};

    for(i = 0; i < hashes.length; i++) {
        hash = hashes[i].split('=');
        args[hash[0]] = hash[1];
    }

    console.log('parseQueryString: done!', args);
    return args;
};
