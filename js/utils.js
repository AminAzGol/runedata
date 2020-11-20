const _outOrUnderperform = (val) => val >= 0 ? 'outperforms' : 'underperforms';
const _upOrDown = (val) => val >= 0 ? 'up' : 'down';
const _gainOrLoss = (val) => val >= 0 ? 'gained' : 'lost';

const _formatPrice = (p) => {
    return p.toFixed(p >= 1 ? 2 : 5);
};

const _formatPriceChange = (value) => {
    if (value >= 0) {
        var sign = '+';
    } else {
        var sign = '–';
    }
    return sign + '$' + Math.abs(value).toFixed(0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

const _formatTotalValue = (v) => {
    return '$' + Math.abs(v).toFixed(2).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
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
