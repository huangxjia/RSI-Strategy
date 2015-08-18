__author__ = 'huangxuejia'

import pandas as pd
import datetime
#import matplotlib.pyplot as plt

class string():
    def __init__(self, series):
        self.series = series

    def string_to_date(self):
        for i in self.series.index:
            self.series.ix[i] = datetime.datetime.strptime(self.series.ix[i], "%Y-%m-%d")
        return self.series

class read_data():
    def __init__(self, url):
        self.url = url

    def read_data(self):
        bars = pd.read_csv(self.url)
        index = pd.Series(bars.ix[1:445, 0])
        mac = string(index).string_to_date()
        iron_ore = pd.DataFrame(bars.ix[1:445, 1].reshape(445,1), columns = ['prices'], index=mac)
        return iron_ore