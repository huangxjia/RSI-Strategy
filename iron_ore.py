__author__ = 'huangxuejia'

import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time


from pandas.io.data import DataReader
from backtest import Strategy, Portfolio


#short
class RelativeStrengthIndex(Strategy):

    def __init__(self, symbol, bars, marketType = 'bull', in_ = 0, window = 14):
        self.symbol = symbol
        self.bars = bars
        self.marketType = marketType
        self.window = window
        self.in_ = in_

    def generate_signals(self):
        signals = pd.DataFrame(index=self.bars.index)

    #empty with only index
    #RSI = 100 - 100/(1 + RS*)

        signals['signal'] = 0.0

        signals['diff'] = bars['Close'].diff()
        signals['up'], signals['down'] = signals['diff'], signals['diff']
        signals['up'][signals['up']<0] = 0
        signals['down'][signals['down']>0] = 0

        signals['up']=pd.rolling_mean(signals['up'],self.window, min_periods =1)
        signals['down']=pd.rolling_mean(signals['down'],self.window, min_periods=1).abs()
        signals['rsi'] = signals['up']/(signals['up']+signals['down'])*100
        #shor

        for i in signals.index:
            if ((self.marketType == 'bear') & (self.in_ == 0)):
                if (signals.ix[i]['rsi']>55):
                    signals.ix[i]['signal'] = -1
                    self.in_ = 1
                #else:
                 #   signals.ix[i]['signal'] = 0
            else:
                if (signals.ix[i]['rsi']<18):
                    self.in_ = 0
                else:
                    signals.ix[i]['signal'] = -1

# take care: if signals.ix[0]['signal']=1, no, because the first 14 rsi is 0
        signals['positions'] = signals['signal'].diff()

        signals.fillna(0.0)
        return signals
    #it's amazing to finish a strategy with several lines

class MarketOnClosePortfolio(Portfolio):
    def __init__(self, symbol, bars, signals, lvg, initial_capital = 105000.0):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals
        self.lvg = lvg
        self.initial_capital = float(initial_capital)
        self.positions = self.generate_positions()
        self.portfolio = self.backtest_portfolio()


    def generate_positions(self):
        positions = (pd.DataFrame(index=self.bars.index, columns = self.bars.columns)).fillna(0.0)
        positions['Close'] = 100*signals['signal']*self.lvg
        return positions

    def backtest_portfolio(self):
        portfolio = pd.DataFrame(index = self.positions.index)
        pos_diff = self.positions.diff().fillna(0.0)
        portfolio['position'] = self.positions['Close']
        portfolio['Close'] = self.bars['Close']
        portfolio['diff'] = self.positions['Close'].diff().fillna(0.0)
        portfolio['holdings'] = abs(portfolio['position']*portfolio['Close']/self.lvg)

        portfolio.fillna(0.0)

# what do u mean by sum(axis=1)
     #   portfolio['holdings'] = (self.positions*self.bars['Close']).sum(axis=1)
        #take care when u deal with data, easy to make mistake

        portfolio['cash'] = 105000
        portfolio['ngt_stg'] = 105000
        portfolio['commissions'] = 0.0

        portfolio.ix[1, 'cash'] = self.initial_capital
        k = len(portfolio.index)


        for i in range(2, k+1):
            if portfolio.ix[i,'diff']==(-100*self.lvg):
                portfolio.ix[i,'commissions'] = portfolio.ix[i,'holdings']*self.lvg*0.00016
                portfolio.ix[i,'cash']=portfolio.ix[(i-1),'cash']-portfolio.ix[i,'holdings']-portfolio.ix[i,'commissions']
            elif  portfolio.ix[i,'diff'] == (100*self.lvg):
                portfolio.ix[i,'commissions'] = abs(portfolio.ix[i,'Close']*portfolio.ix[i-1, 'position']*0.00016)
                portfolio.ix[i,'cash']=portfolio.ix[i-1,'cash']+portfolio.ix[i,'Close']*portfolio.ix[i-1, 'position']*(-1)/self.lvg+(portfolio.ix[i,'Close']-portfolio.ix[i-1,'Close'])*portfolio.ix[i-1,'position']--portfolio.ix[i,'commissions']
            elif portfolio.ix[i, 'position'] == 0:
                portfolio.ix[i,'cash']=portfolio.ix[i-1,'cash']
            else:
                portfolio.ix[i,'cash']=portfolio.ix[i-1, 'cash']+(portfolio.ix[i, 'Close']-portfolio.ix[i-1,'Close'])*portfolio.ix[i,'position']

            portfolio.ix[i, 'ngt_stg'] = portfolio.ix[i-1, 'ngt_stg']+(portfolio.ix[i, 'Close']-portfolio.ix[i-1,'Close'])*(-100*(self.lvg-1))


    #        portfolio.ix[i,'diff'] = np.where(portfolio.ix[i,'diff']==(-100*self.lvg), portfolio.ix[(i-1),'cash']-portfolio.ix[i,'holdings'],
     #                                         np.where(portfolio.ix[i,'diff'] == (100*self.lvg), portfolio.ix[i-1,'cash']+portfolio.ix[i,'Close']*portfolio.ix[i-1, 'position']*(-1)/self.lvg+(portfolio.ix[i,'Close']-portfolio.ix[i-1,'Close'])*portfolio.ix[i-1,'position'],
      #                                                 np.where(portfolio.ix[i, 'position'] == 0, portfolio.ix[i-1,'cash'],
       #                                                     portfolio.ix[i-1, 'cash']+(portfolio.ix[i, 'Close']-portfolio.ix[i-1,'Close'])*portfolio.ix[i,'position'])))
    # seems more time consuming
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()
        portfolio['t_returns'] = portfolio['total']/portfolio.ix[1, 'total']
        portfolio['ngt_returns']=portfolio['ngt_stg']/portfolio.ix[1,'ngt_stg']
        return portfolio

    def strategy_performance(self):
        year_return = (self.portfolio.ix[250, 'total']-self.portfolio.ix[1, 'total'])/self.portfolio.ix[1, 'total']
        sd = np.std(self.portfolio.ix[1:250, 't_returns'])
        year_return_ngt = (self.portfolio.ix[250, 'ngt_stg']-self.portfolio.ix[1, 'ngt_stg'])/self.portfolio.ix[1, 'ngt_stg']
        sd_ngt = np.std(self.portfolio.ix[1:250, 'ngt_returns'])
        sharpe = (year_return-0.048)/sd
        sharpe_ngt = (year_return_ngt-0.048)/sd_ngt
        print("Year return: {0}, Negative strategy year return: {1}".format(year_return, year_return_ngt))
        print("Sharpe ratio: {0}, Negative strategy sharpe ratio: {1}".format(sharpe, sharpe_ngt))
        print("Commissions:{0}".format(sum(self.portfolio.ix[1:250,'commissions'])))

    def max_drawdown(self):
        ih, il, pih, pil, mdd = 1,1,1,1,0
        nih, nil, npih, npil, nmdd = 1,1,1,1,0
        p = pd.Series(self.portfolio['total'])
        t = pd.Series(self.portfolio['ngt_stg'])

        for i in range(2, len(self.portfolio.index)+1):
            if p[i]>p[pih]:
                pih, pil = i, i
            elif p[i]<p[pil]:
                pil = i
            if (p[pih]-p[pil])/p[pih] > mdd:
                ih, il = pih, pil
                mdd = (p[pih]-p[pil])/p[pih]

        for i in range(2, len(self.portfolio.index)+1):
            if t[i]>t[npih]:
                npih, npil = i, i
            elif t[i]<t[npil]:
                npil = i
            if (t[npih]-t[npil])/t[npih] > mdd:
                nih, nil = npih, npil
                nmdd = (t[npih]-t[npil])/t[npih]


        p = [mdd, ih, il, pih, pil]
        t = [nmdd, nih, nil, npih, npil]
        return p, t

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



