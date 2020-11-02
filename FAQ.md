![banner](https://github.com/Larrypcdotcom/thorchain-lp-data/raw/main/images/banner.png)

# FAQ

## Q. What does this tool do?

This tool provides two key functions:

* Simulate hypothetical investments in the past (e.g. invest x dollars on y day in z pool) would
have played out to-date using on-chain data.

* Predict future returns of such investments by extrapolating historical yields.

## Q. How to use?

To simulate past performance, fill out the first section of the left panel, then hit "Simulate".

To predict future returns, fill out **both** sections, and hit "Predict". Since there is no way
for the algorithm to reliably predict future asset prices, the user needs to supply his/her own
price targets. The algorithm will extrapolate past yields to the user's selected date, and
substract impermanent loss from there.'''),

## Q. How to I understand the yield / return / ROI / APY presented here?

Your yield consists of three parts:

1. **Transaction fees**.

2. **LP rewards**. RUNE tokens are injected into each pool based on [a predefined schedule](https://docs.thorchain.org/how-it-works/emission-schedule).
This serves as an incentive for users to take risk and provide liquidity, similar to "yield
farming" in Ethereum DeFi. At this time, this constitutes the majority of the yield.

3. **Impermanent loss (IL)**. This is the result of the swings of the relative prices of pooled
assets and is always negative.

The yield values provided here only includes (1) tx fees and (2) LP rewards. This is because these
are relatively predictable and easy to extrapolate to the future. (3) IL, on the other hand, is
unpreditable and highly volatile. Knowing historical IL provides no help in predicting future IL
Therefore it is excluded form yield values.

To predict future returns, the user needs to provide his/her own price targets.

## Q. Where can I learn more about THORChain?

The best place to start is to start is the [official Telegram group](https://t.me/thorchain_org).
Feel free to join and ask questions.

Other resources:

* The official documentation's [Technology](https://docs.thorchain.org/technology) section is helpful
for those who wish to understand how THORChain works under the hood.

* [Chris Blec](https://twitter.com/ChrisBlec)'s [interview](https://www.youtube.com/watch?v=ip7OHz1Gnec)

* [Delphi Digital](https://twitter.com/Delphi_Digital)'s [podcast](https://www.delphidigital.io/reports/exclusive-podcast-with-thorchains-technical-lead-chad-barraford/)

* Two execellent articles ([1](https://pintail.medium.com/uniswap-a-good-deal-for-liquidity-providers-104c0b6816f2),
[2](https://pintail.medium.com/understanding-uniswap-returns-cc593f3499ef)) explaining the risks
and returns of providing liquidity on Uniswap. Since THORChain uses the same constant-product rule
as Uniswap, these discussions also applies here.

## Q. Who built this? Can I access the source code?

Created by [@Larrypcdotcom](https://twitter.com/Larrypcdotcom). The code is [available on GitHub](https://github.com/Larrypcdotcom/RuneData.info)
under MIT license.

## Q. Can you add support for \[...\] pool?

Sure. To make a request, create an issue on GitHub or simply DM me on Twitter.

## Q. How can I contribute?

Join the **THORChain Apps Dev Team** [Zulip server](). We are a community group committed to
creating tools like this to assist THORChain users. (Note: not associated with the THORChain core team.)

For bug reports and feature requests, please [create an issue](https://github.com/Larrypcdotcom/thorchain-lp-data/issues/new)
on GitHub.
