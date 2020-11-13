# Fetch pool data without launching the app
# Used for adding support for new tokens at user's request

import src

src.info('Fetching pool data...', './app.log')
src.fetch_data('./data', './app.log', first_block=475000)
