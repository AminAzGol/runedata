# thorchain-lp-data

Pulls THORChain liquidity provider data from a community-maintained API

## Dependencies

* pandas
* [requests](https://requests.readthedocs.io/en/master/)
* [streamlit](https://www.streamlit.io/)
* [termcolor](https://pypi.org/project/termcolor/)

Create an Anaconda environment using the YAML file provided:

```
conda env create -n streamlit -f environment.yaml
```

## How to use

Edit the configurations in `fetch_data.py`, then

```
conda activate streamlit
cd src
python fetch_data.py
```
