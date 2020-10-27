# thorchain-lp-data

Pulls THORChain liquidity provider data from a community-maintained API

## Dependencies

* [altair](https://altair-viz.github.io/)
* matplotlib
* pandas
* [requests](https://requests.readthedocs.io/en/master/)
* [streamlit](https://www.streamlit.io/)
* [termcolor](https://pypi.org/project/termcolor/)
* tqdm

Create an Anaconda environment:

```
conda env create -n streamlit python
pip install -r requirements.txt
```

## Run locally

Edit the configurations in `fetch_data.py`, then

```
conda activate streamlit
streamlit run app.py
```

## Deploy to Heroku

Reference: [Deploying your Streamlit dashboard with Heroku](https://gilberttanner.com/blog/deploying-your-streamlit-dashboard-with-heroku) by Gilbert Tanner
