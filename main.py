import numpy as np 
import pandas as pd 
import datetime as dt 
import pytz
import alpaca_trade_api as tradeapi
from secret import Secret
import time


class Bot:

    def __init__(self):
        api_key = Secret.paper_api_key
        secret_key = Secret.secret_key
        alp_base_url = 'https://paper-api.alpaca.markets'
        api = tradeapi.REST(api_key, secret_key, alp_base_url, api_version='v2')

        self.api = api

    # check our current positions to see if we are down to much to mitigate losses
    def check_stop_loss(self):
        api = self.api
        portfolio = api.list_positions()

        for position in portfolio:
        # if qty of shares is less than 0 we are shorting, 
        # so we will buy if price rises above 10 percent

            if int(position.qty) < 0 and float(position.change_today) > .1:
                percent_change = position.avg_entry_price + (position.avg_entry_price*.1)
                print('buy stop loss of {} at {} percent loss with price {}'.format(position.symbol, percent_change, position.current_price))
                api.submit_order(symbol=portfolio.symbol, 
                                qty=1,
                                order_class='oco',
                                side='buy',
                                stop_loss=percent_change)

        # if qty of shares is greater than 1 we are in a long buy position,
        # so we will sell if price falls below 10 percent

            if int(position.qty) > 0 and float(position.change_today) < -.1:
                percent_change = position.avg_entry_price - (position.avg_entry_price*.1)
                print('sell stop loss of {} at {} percent loss with price {}'.format(position.symbol, percent_change, position.current_price))
                api.submit_order(symbol=portfolio.symbol, 
                                qty=1,
                                order_class='oco',
                                side='sell',
                                stop_loss=percent_change)
    
    # for paper
    def get_paper_data(self):
        tickers = pd.read_csv('paper_data/S&P500-Symbols.csv')
        ticker_vals = tickers['Symbol'].values
        ticker_scope = ticker_vals[:200]

        start = dt.datetime(2021, 1, 1) 
        end = dt.datetime.now()

        data_tickers = []

        for ticker in ticker_scope:
            data = self.api.get_barset(ticker, 'day', limit=100).df
            # print(data)
            # print(ticker)
            data_tickers.append(data)


        return data_tickers, ticker_scope


    def check_account(self):
        account = self.api.get_account() # Get our account information.
        
        # Check how much money we can use to open new positions.
        print('${} is available as buying power.'.format(account.buying_power))

    def check_market(self):
        '''
            "timestamp": "2018-04-01T12:00:00.000Z",
            "is_open": true,
            "next_open": "2018-04-01T12:00:00.000Z",
            "next_close": "2018-04-01T12:00:00.000Z"
        '''

        self.api.get_clock().is_open

    # main method for algo, implements golden cross/death cross
    def check_trade(self, data, ticker) -> bool:
        # the lower day for the moving average is the faster one 
        # when this crosses over the slower moving average of a larger amount of days
        # this a Golden Cross and it is an indicator for bullish returns


        close = data[ticker, 'close']
        fast_moving_avg = close.rolling(window=10).mean()
        slow_moving_avg = close.rolling(window=50).mean()
        
        # get the last fast moving average and slow moving average 
        current_fma = fast_moving_avg[-1]
        current_sma = slow_moving_avg[-1]

        # we need to look back one day to check for a cross 
        one_day_fma = fast_moving_avg[len(fast_moving_avg) - 2].round()
        one_day_sma = slow_moving_avg[len(slow_moving_avg) - 2].round()

        # then compare current day to see if Golden Cross or Death Cross
        if(one_day_fma == one_day_sma ):
            if current_fma > current_sma: # golden cross
                return True, ticker 
                # enter position
                # record trade

            elif current_fma < current_sma: # death cross
                return False, ticker
                # exit position
                # record trade
        
        return None, ticker

    # for entering/exiting position (buy and sell stocks)
    def execute_trade(self, position, ticker):
        api = self.api

        # when the position is true we buy the stock
        if position == True:
            # print('long buy {}'.format(ticker))
            # api.submit_order(symbol=ticker, qty=1, side='buy')
            try:
                print('long buy {}'.format(ticker))
                api.submit_order(symbol=ticker, qty=1, side='buy')
            except:
                print('order {} na'.format(ticker))
        # when the position is fallse we sell (or short)
        else:
            try:
                print('short sell {}'.format(ticker))
                api.submit_order(symbol=ticker, qty=1, side='sell')
            except:
                print('order {} na'.format(ticker))



if __name__ == '__main__':
    b = Bot()
    # b.check_account()
    tz_pacific = pytz.timezone('US/Pacific')
    datetime_pacific = dt.datetime.now(tz_pacific)
    current_time = datetime_pacific.strftime("%H:%M:%S")
    now = dt.datetime.now()
    
    # create an infinite loop with a rest period every hour using sleep 
    # build a new image called trading-bot-linux
    # follow the commands to push it to docker hub and deploy to digital ocean

    market_open = now.replace(hour=6, minute=30, second=0, microsecond=0, tzinfo=tz_pacific) # 6:30 am 

    market_close = now.replace(hour=13, minute=0, second=0, microsecond=0, tzinfo=tz_pacific) # 1:00 pm  
    
    while(True):
        # if datetime_pacific > market_open and datetime_pacific < market_close:
        if datetime_pacific > market_open:
            data, tickers = b.get_paper_data()
            
            for i, data_set in enumerate(data):
                result = b.check_trade(data_set, tickers[i])

                if result[0] != None:
                    b.execute_trade(result[0], result[1])

            b.check_stop_loss()
            time.sleep(3600)
    
    
    
    