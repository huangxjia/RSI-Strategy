__author__ = 'huangxuejia'

import matplotlib.pyplot as plt
import pandas as pd
import time
from strategies import RelativeStrengthIndex, MarketOnClosePortfolio
from read_data import read_data

from pandas.io.data import DataReader


#short

        #print ("Max drawdown:{0}".format(mdd))
        #print ("ih:{0}, il:{1}, pih:{2}, pil:{3}".format(ih, il, pih, pil))


"""

other assets...
better combine fundamental judgement

very annoying to debug, u need to be smarter and more efficient

portfolio.ix[i, 'cash'] = np.where(portfolio.ix[i,'diff']==(100*self.lvg), (portfolio.ix[(i-1),'cash']-portfolio.ix[i,'Close']),np.where(self.signals['diff'] == (-100*self.lvg),portfolio.ix[i-1,'cash']+2*portfolio.ix[i,'Close']-portfolio.ix[i-1,'Close'],np.where(portfolio['position'] == 0, portfolio.ix[i-1,'cash'],portfolio.ix[i-1, 'cash']+portfolio.ix[i, 'Close']-portfolio.ix[i-1,'Close'])))
this takes more time
ok, i know how this work

why say if sharpe ratio is larger than 10, u make money everyday?

when to get out of the market??? very important

trading costs

find the best RSI for specific asset
graph
performance indicators:
annualized return(should deduct fees god, sure)
sharpe ratio
max drawdown
ulcer performance index
correlation with S&P 500
best month
worst month
%winning months
trades per year

"""


if __name__ == "__main__":

    symbol = 'AAPL'
    bars = pd.read_csv("/Users/huangxuejia/Documents/data/1.csv")
    bars = bars.ix[1:445, [1]]
    bars.columns = ['Close']
    bars.Close = bars.Close.astype(float)
    bars = read_data("/Users/huangxuejia/Documents/data/1.csv")
    lvg = 5
# lvg = 2 means u have no leverage at all
    marketType = 'bear'
    in_ = 0
#def __init__(self, symbol, bars, marketType = 'bull', in_ = 0, window = 14):

    mac = RelativeStrengthIndex(symbol, bars, marketType, in_, window = 14)
    signals = mac.generate_signals()

    portfolio = MarketOnClosePortfolio(symbol, bars, signals, lvg, initial_capital = 105000.0)
    start_time = time.time()
    returns = portfolio.backtest_portfolio()
    p, t= portfolio.max_drawdown()
    print p,t
    print("time:{0}".format(time.time()-start_time))
    portfolio.strategy_performance()

    fig = plt.figure()
    fig.patch.set_facecolor('white')

    ax1 = fig.add_subplot(311, ylabel = 'Prices', xlabel = 'Time', title = 'Iron ore futures prices in CNY')
    bars['Close'].plot(ax = ax1, color = 'r', lw =2.)


    ax2 = fig.add_subplot(312, ylabel = "RSI", xlabel = 'Time', title = '14-day RSI')
    signals['rsi'].plot(ax = ax2, lw = 2.)
    ax2.plot(signals.ix[signals.positions == 1.0].index,
            signals.rsi[signals.positions == 1.0],
            '^', markersize = 10, color = 'm')
    ax2.plot(signals.ix[signals.positions == -1.0].index,
            signals.rsi[signals.positions == -1.0],
           'v', markersize = 10, color = 'k')

# hello hello


    ax3 = fig.add_subplot(313, ylabel = 'Portfolio Values in CNY', title = "PnL")
    returns['total'].plot(ax = ax3, lw = 2.)
    returns['ngt_stg'].plot(ax=ax3, lw = 2.)
    ax3.plot(returns.ix[signals.positions == 1.0].index,
            returns.total[signals.positions == 1.0],
           '^', markersize = 10, color = 'm')
    ax3.plot(returns.ix[signals.positions == -1.0].index,
            returns.total[signals.positions == -1.0],
           'v', markersize = 10, color = 'k')

    fig.tight_layout()
    plt.show()



