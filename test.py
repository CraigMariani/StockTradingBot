
import pandas as pd 
import datetime as dt 
import alpaca_trade_api as tradeapi
from secret import Secret


api_key = Secret.paper_api_key
secret_key = Secret.secret_key
alp_base_url = 'https://paper-api.alpaca.markets'
api = tradeapi.REST(api_key, secret_key, alp_base_url, api_version='v2')

# test getting data
# df = api.get_barset('AAPL', 'day', limit=100).df
# print(df['AAPL', 'close'])

# test entering a position, the client order id must be unique for each time we execute a trade 
# api.submit_order(symbol='AMZN', 
#             qty=1, 
#             side='sell',

            # time_in_force='gtc', 
            # type='limit', 
            # limit_price=400.00, 
            # client_order_id='005'
            # )

account =  api.get_account() # Get our account information.
# Check how much money we can use to open new positions.
print('${} is available as buying power.'.format(account.buying_power))
# print(account)
# print(api.get_portfolio_history().df)
# print(api.get_position('AAL'))
# print(api.get_trades('AAL', dt.datetime(2021, 1, 1), dt.datetime.now()))

# Check our current balance vs. our balance at the last market close
# balance_change = float(account.equity) - float(account.last_equity)
# print(f'Today\'s portfolio balance change: ${balance_change}')

# Get a list of all of our positions.
portfolio = api.list_positions() # use keys : qty, symbol, side, current_price, avg_entry_price
print(portfolio[0])
# print(api.submit_order(stop_loss=)))

# Print the quantity of shares for each position.
for position in portfolio:
    print("{} shares of {}".format(position.qty, position.symbol))