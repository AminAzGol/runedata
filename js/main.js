const _formatPrice = (p) => {
    return p.toFixed(p >= 1 ? 2 : 5);
}

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

$(async () => {
    $('#simulateBtn').click(function () {
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#predictBtn').removeClass('btn-primary').addClass('btn-outline-primary');

        $('#simulateForm').show();
        $('#predictForm').hide();
    });

    $('#predictBtn').click(function () {
        $(this).removeClass('btn-outline-primary').addClass('btn-primary');
        $('#simulateBtn').removeClass('btn-primary').addClass('btn-outline-primary');

        $('#simulateForm').hide();
        $('#predictForm').show();
    });

    $('#simulateSubmitBtn').click((event) => {
        event.preventDefault();

        var amountInvested = parseFloat($('#amountSimulate').val());
        var dateInvested = $('#dateSimulate').val();
        var pool = $('#poolSimulate').val();

        showSpinner();
        getPastSimulation(amountInvested, dateInvested, pool).then((userData) => {
            console.log(userData);
            hideSpinner();
        });
    });

    // Generate options for pool selectors
    generatePoolOptions($('#poolSimulate'));
    generatePoolOptions($('#poolPredict'));

    // Fetch asset prices
    const PRICES = await getCurrentPrices(ASSETS)

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
