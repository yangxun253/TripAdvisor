__author__ = 'Xun'


import pandas as pd

datain = pd.read_csv('reviews.csv', header=None)

print datain[1][2]