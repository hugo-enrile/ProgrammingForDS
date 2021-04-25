import pandas as pd 
from math import factorial
import csv
from itertools import product

#### SECOND PART ####
columns = ['ST','CB','PB','GO','CA']
values = []
portfolio = pd.DataFrame(columns=columns)

for i in range(0,21):
    values.append(100-i*5)

def n_combinations(m, n):
    return factorial(m+n-1) // (factorial(n) * factorial(m - 1))

def permuta_reps(c,s,suma):
    tmp = 0
    for i in product(c, repeat=s):
        i = list(i)
        if sum(i) == suma:
            portfolio.loc[tmp] = i
            tmp=tmp+1

permuta_reps(values,5,100)
assert portfolio.shape[0] == n_combinations(5,20)
portfolio.to_csv('portfolio_allocations.csv', header = True, index = False)
