# thorchain-lp-data

Pulls THORChain liquidity provider data from a community-maintained API

## Dependencies

* requests==2.24.0
* tqdm==4.50.2
* altair==4.1.0
* matplotlib==3.3.2
* pandas==1.1.3
* termcolor==1.1.0
* streamlit==0.69.2

Create an Anaconda environment:

```bash
conda env create -n streamlit python
pip install -r requirements.txt
```

## Run locally

Edit the configurations in `fetch_data.py`, then

```bash
conda activate streamlit
streamlit run app.py
```

## Deploy to Heroku

Install Heroku CLI tool:

```bash
brew tap heroku/brew && brew install heroku  # masOS
sudo snap install --classic heroku  # Ubuntu
```

Create a new project on Heroku website, then

```bash
heroku git:remote -a yourprojectname  # add Heroku app as a remote repo
git push heroku HEAD:master
```

The app should be live on https://yourprojectname.herokuapp.com/

Reference: [Deploying your Streamlit dashboard with Heroku](https://gilberttanner.com/blog/deploying-your-streamlit-dashboard-with-heroku) by Gilbert Tanner
