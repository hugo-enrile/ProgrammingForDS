import pandas as pd 
import numpy as np 
import csv

# Portfolio allocations
portfolio = pd.read_csv('portfolio_allocations.csv')

# Definition of the investment methodologies with and without rebalancing
methodologies = ['1-OFF','DCA']
rebalancing = ['NO','YES']

# Creation of the dictionaries
dict_method = {k: methodologies for k in range(0,portfolio.shape[0])}
dict_rebal = {k: rebalancing for k in range(0,portfolio.shape[0])}

# Configuration of the final DataFrame
# reps = [1 if i < 200 else 1 for i in portfolio.ST] esta linea y la de abajo no valen en este caso pero ojito que es to util jajaja
# portfolio = portfolio.loc[np.repeat(portfolio.index.values, reps)]
trading_methodologies = (pd.DataFrame(data=list(dict_method.values()), index=list(dict_method.keys())).stack().reset_index().drop("level_1", axis=1))
trading_methodologies.columns = ["id", "Methodology"]

types_rebalancing = (pd.DataFrame(data=list(dict_rebal.values()), index=list(dict_rebal.keys())).stack().reset_index().drop("level_1", axis=1))
types_rebalancing.columns = ["id", "Rebal."]

# First step
portfolio = portfolio.reset_index()
portfolio = portfolio.rename(columns = {'index':'id'})
portfolio = portfolio.merge(trading_methodologies, on='id')
portfolio = portfolio.drop("id", axis=1)
# Second step
portfolio = portfolio.reset_index()
portfolio = portfolio.rename(columns = {'index':'id'})
types_rebalancing = pd.concat([types_rebalancing, types_rebalancing], ignore_index=True)
types_rebalancing['index_tmp'] = types_rebalancing.index
mask = types_rebalancing.index_tmp > 21251
types_rebalancing.id[mask]= types_rebalancing.id + 10626
#types_rebalancing = types_rebalancing.reset_index()
types_rebalancing = types_rebalancing.drop("index_tmp", axis=1)
#types_rebalancing = types_rebalancing.rename(columns = {'index':'id'})
portfolio = portfolio.merge(types_rebalancing, on='id')
portfolio = portfolio.drop("id", axis=1)

portfolio.to_csv('trading_methodologies.csv', header = True, index = False)