import pandas as pd 
from math import factorial
from math import sqrt
import csv
import numpy as np 
from itertools import product

# Portfolio allocations
trading_methodologies = pd.read_csv('trading_methodologies.csv')

# Asset information
ST = pd.read_csv('amundi-msci-wrld-ae-c.csv')
CB = pd.read_csv('ishares-global-corporate-bond-$.csv')
PB = pd.read_csv('db-x-trackers-ii-global-sovereign-5.csv')
GO = pd.read_csv('spdr-gold-trust.csv')

# Asset prices
def get_asset_prices_endYear(ST, CB, PB, GO):
    asset_prices = [ST.Price[365],CB.Price[365],PB.Price[365],GO.Price[365],1]
    return asset_prices

def get_asset_prices_total(ST, CB, PB, GO):
    asset_prices = [ST.Price,CB.Price,PB.Price,GO.Price,1]
    return asset_prices

def get_asset_prices_rebal(ST, CB, PB, GO, array_month):
    search_values = ['01','02','13','14','15','16','17','30','31']

    ST_rebal = ST[ST['Date'].str.contains('|'.join(search_values))]
    CB_rebal = CB[CB['Date'].str.contains('|'.join(search_values))]
    PB_rebal = PB[PB['Date'].str.contains('|'.join(search_values))]
    GO_rebal = GO[GO['Date'].str.contains('|'.join(search_values))] 

    tmp = [ST_rebal,CB_rebal,PB_rebal,GO_rebal]
    a = 0

    asset_prices_mid = pd.DataFrame(columns=['ST','CB','PB','GO','CA'])
    asset_prices_ini = pd.DataFrame(columns=['ST','CB','PB','GO','CA'])

    for i in array_month:
        tmp_mid = []
        tmp_ini = []
        for j in range(len(tmp)):
            mid_day = str(i) + "-15"
            first_day = str(i) + "-01"
            if len(tmp[j][tmp[j]['Date'].str.contains(mid_day)]) != 0:
                tmp_mid.append(tmp[j][tmp[j]['Date'].str.contains(mid_day)].iloc[0].Price)
            else:
                mid_day2 = str(i) + "-14"
                mid_day3 = str(i) + "-16"
                if len(tmp[j][tmp[j]['Date'].str.contains(mid_day2)]) != 0:
                    tmp_mid.append(tmp[j][tmp[j]['Date'].str.contains(mid_day2)].iloc[0].Price)
                elif len(tmp[j][tmp[j]['Date'].str.contains(mid_day3)]) != 0:
                    tmp_mid.append(tmp[j][tmp[j]['Date'].str.contains(mid_day3)].iloc[0].Price)
            if len(tmp[j][tmp[j]['Date'].str.contains(first_day)]) != 0:
                tmp_ini.append(tmp[j][tmp[j]['Date'].str.contains(first_day)].iloc[0].Price)
            else:
                if i == 'Jan':
                    prev_month = 'Dec'
                else:
                    prev_month = array_month[array_month.index(i) - 1]
                last_day = str(prev_month) + "-31"
                last_day2 = str(prev_month) + "-30"
                next_day = str(i) + "-02"
                if len(tmp[j][tmp[j]['Date'].str.contains(last_day)]) != 0:
                    tmp_ini.append(tmp[j][tmp[j]['Date'].str.contains(last_day)].iloc[0].Price)
                elif len(tmp[j][tmp[j]['Date'].str.contains(last_day2)]) != 0:
                    tmp_ini.append(tmp[j][tmp[j]['Date'].str.contains(last_day2)].iloc[0].Price)
                elif len(tmp[j][tmp[j]['Date'].str.contains(next_day)]) != 0:
                    tmp_ini.append(tmp[j][tmp[j]['Date'].str.contains(next_day)].iloc[0].Price)
        tmp_mid.append('1')
        tmp_ini.append('1')
        asset_prices_mid.loc[a] = tmp_mid
        asset_prices_ini.loc[a] = tmp_ini
        a = a + 1
    return asset_prices_mid, asset_prices_ini

# Investing strategies
def one_off(money, portfolio_allocation, asset_prices):
    shares =[]
    for i in range(len(portfolio_allocation)):
        shares.append(((portfolio_allocation[i])/100 * money)/asset_prices[i])
    return shares

def rebalance_function(prev_asset_prices, current_asset_prices):
    tmp_percent = []
    for i in range(len(current_asset_prices)):
        tmp_percent.append(round(current_asset_prices[i]/sum(current_asset_prices),2)*100)
    return tmp_percent

def dca(money, portfolio_allocation, period, asset_prices):
    monthly_portfolio = list(map(lambda x: x/period, portfolio_allocation))
    shares =[]
    for i in range(len(monthly_portfolio)):
        shares.append(((monthly_portfolio[i])/100 * money)/asset_prices[i])
    return shares

def cost(trading_methodology):
    portfolio_allocations = trading_methodology.iloc[:,:5]
    asset_prices_fd = get_asset_prices_endYear(ST, CB, PB, GO)
    trading_methodology['Cost'] = 0
    for index, portfolio_allocation in portfolio_allocations.iterrows():
        cost = 0
        for index2, i in enumerate(asset_prices_fd):
            cost = cost + i * (portfolio_allocation[index2]/100)
        trading_methodology['Cost'][index] = cost

def volatility(money, trading_methodologies):
    shares = []
    a = 0
    trading_methodologies['Volatility'] = ""
    for index, row in trading_methodologies.iterrows():
        print("Iteration volatility: " + str(index) + "...") 
        temp = pd.DataFrame(np.zeros((366,6)), columns = ['ST_Values','CB_Values','PB_Values','GO_Values','CA_Values','Values'])  
        shares_values = [((money * (row[0] / 100))),((money * (row[1] / 100))),((money * (row[2] / 100))),((money * (row[3] / 100))),(money * (row[4] / 100))]  
        if row[5] == '1-OFF':
            shares = [((money * (row[0] / 100)) / ST.Price[0]),((money * (row[1] / 100)) / CB.Price[0]),((money * (row[2] / 100)) / PB.Price[0]),((money * (row[3] / 100)) / GO.Price[0]),(money * (row[4] / 100))]
            if row[6] == 'NO':
                temp['ST_Values'] = (shares[0]) * ST.Price
                temp['CB_Values'] = (shares[1]) * CB.Price
                temp['PB_Values'] = (shares[2]) * PB.Price
                temp['GO_Values'] = (shares[3]) * GO.Price
                temp['CA_Values'] = shares[4]
                temp['Values'] = temp.sum(axis=1)
                trading_methodologies['Volatility'][index] = (temp['Values'].std() / temp['Values'].mean()) * 100
            else:
                for indexST, rowST in ST.iterrows():
                    if ("Jan-01" in rowST['Date']):
                        temp['ST_Values'][indexST] = (shares[0]) * rowST.Price 
                        temp['CB_Values'][indexST] = (shares[1]) * CB.iloc[indexST].Price
                        temp['PB_Values'][indexST] = (shares[2]) * PB.iloc[indexST].Price
                        temp['GO_Values'][indexST] = (shares[3]) * GO.iloc[indexST].Price
                        temp['CA_Values'][indexST] = (shares[4])
                        a = 1
                    elif ("15" in rowST['Date']):
                        shares_current_value = [(shares_prev_value[0]/ST.iloc[indexST-1].Price)*rowST.Price,(shares_prev_value[1]/CB.iloc[indexST-1].Price)*CB.iloc[indexST].Price,(shares_prev_value[2]/PB.iloc[indexST-1].Price)*PB.iloc[indexST].Price,(shares_prev_value[3]/GO.iloc[indexST-1].Price)*GO.iloc[indexST].Price,shares_prev_value[4]]
                        current_money = sum(shares_current_value)
                        shares_prev_value = shares_current_value
                        temp['ST_Values'][indexST] = shares[0] * rowST.Price 
                        temp['CB_Values'][indexST] = shares[1] * CB.iloc[indexST].Price
                        temp['PB_Values'][indexST] = shares[2] * PB.iloc[indexST].Price
                        temp['GO_Values'][indexST] = shares[3] * GO.iloc[indexST].Price
                        temp['CA_Values'][indexST] = shares[4]
                        shares = [((current_money * (row[0] / 100))) / rowST.Price, ((current_money * (row[1] / 100))) / CB.iloc[indexST].Price, ((current_money * (row[2] / 100))) / PB.iloc[indexST].Price, ((current_money * (row[3] / 100))) / GO.iloc[indexST].Price, (current_money * (row[4] / 100))]
                        a = 1
                    else:
                        if a == 1:
                            shares_current_value = [shares[0]*rowST.Price,shares[1]*CB.iloc[indexST].Price,shares[2]*PB.iloc[indexST].Price,shares[3]*GO.iloc[indexST].Price,shares[4]]
                            rebalance = rebalance_function(shares_values, shares_current_value)
                            current_money = sum(shares_current_value)
                            shares_prev_value = shares_current_value
                            temp['ST_Values'][indexST] = shares[0] * rowST.Price 
                            temp['CB_Values'][indexST] = shares[1] * CB.iloc[indexST].Price
                            temp['PB_Values'][indexST] = shares[2] * PB.iloc[indexST].Price
                            temp['GO_Values'][indexST] = shares[3] * GO.iloc[indexST].Price
                            temp['CA_Values'][indexST] = shares[4]
                            a = 2
                        else: 
                            shares_current_value = [(shares_prev_value[0]/ST.iloc[indexST-1].Price)*rowST.Price,(shares_prev_value[1]/CB.iloc[indexST-1].Price)*CB.iloc[indexST].Price,(shares_prev_value[2]/PB.iloc[indexST-1].Price)*PB.iloc[indexST].Price,(shares_prev_value[3]/GO.iloc[indexST-1].Price)*GO.iloc[indexST].Price,shares_prev_value[4]]
                            rebalance = rebalance_function(shares_prev_value, shares_current_value)
                            current_money = sum(shares_current_value)
                            shares_prev_value = shares_current_value
                            temp['ST_Values'][indexST] = shares[0] * rowST.Price 
                            temp['CB_Values'][indexST] = shares[1] * CB.iloc[indexST].Price
                            temp['PB_Values'][indexST] = shares[2] * PB.iloc[indexST].Price
                            temp['GO_Values'][indexST] = shares[3] * GO.iloc[indexST].Price
                            temp['CA_Values'][indexST] = shares[4]
                temp['Values'] = temp.sum(axis=1)
                trading_methodologies['Volatility'][index] = (temp['Values'].std() / temp['Values'].mean()) * 100
        else:
            if row[6] == 'NO':
                shares2 = [0,0,0,0,0]
                for indexST, rowST in ST.iterrows():
                    if ("01" in rowST['Date']):
                        shares = dca(money, row[:5], 12, [rowST.Price, CB.iloc[indexST].Price, PB.iloc[indexST].Price, GO.iloc[indexST].Price, 1])
                        shares2 = list(i+j for (i,j) in zip(shares2,shares))
                        temp['ST_Values'][indexST] = (shares2[0]) * rowST.Price 
                        temp['CB_Values'][indexST] = (shares2[1]) * CB.iloc[indexST].Price
                        temp['PB_Values'][indexST] = (shares2[2]) * PB.iloc[indexST].Price
                        temp['GO_Values'][indexST] = (shares2[3]) * GO.iloc[indexST].Price
                        temp['CA_Values'][indexST] = (shares2[4])
                temp['Values'] = temp.sum(axis=1)
                trading_methodologies['Volatility'][index] = (temp['Values'].std() / temp['Values'].mean()) * 100
            else:
                shares_prev_value = [0,0,0,0,0]
                for indexST, rowST in ST.iterrows():
                    if ("01" in rowST['Date']):
                        shares = dca(money, row[:5], 12, [rowST.Price, CB.iloc[indexST].Price, PB.iloc[indexST].Price, GO.iloc[indexST].Price, 1])
                        shares_current_value = [(shares_prev_value[0]/ST.iloc[indexST-1].Price)*rowST.Price,(shares_prev_value[1]/CB.iloc[indexST-1].Price)*CB.iloc[indexST].Price,(shares_prev_value[2]/PB.iloc[indexST-1].Price)*PB.iloc[indexST].Price,(shares_prev_value[3]/GO.iloc[indexST-1].Price)*GO.iloc[indexST].Price,shares_prev_value[4]]
                        shares_current = [shares_current_value[0] / rowST.Price, shares_current_value[1] / CB.iloc[indexST].Price, shares_current_value[2] / PB.iloc[indexST].Price, shares_current_value[3] / GO.iloc[indexST].Price, shares_current_value[4]]
                        shares = list(i+j for (i,j) in zip(shares_current, shares))
                        temp['ST_Values'][indexST] = (shares[0]) * rowST.Price 
                        temp['CB_Values'][indexST] = (shares[1]) * CB.iloc[indexST].Price
                        temp['PB_Values'][indexST] = (shares[2]) * PB.iloc[indexST].Price
                        temp['GO_Values'][indexST] = (shares[3]) * GO.iloc[indexST].Price
                        temp['CA_Values'][indexST] = (shares[4])
                        a = 1
                    elif ("15" in rowST['Date']):
                        shares_current_value = [(shares_prev_value[0]/ST.iloc[indexST-1].Price)*rowST.Price,(shares_prev_value[1]/CB.iloc[indexST-1].Price)*CB.iloc[indexST].Price,(shares_prev_value[2]/PB.iloc[indexST-1].Price)*PB.iloc[indexST].Price,(shares_prev_value[3]/GO.iloc[indexST-1].Price)*GO.iloc[indexST].Price,shares_prev_value[4]]
                        current_money = sum(shares_current_value)
                        shares_prev_value = shares_current_value
                        temp['ST_Values'][indexST] = (shares[0]) * rowST.Price 
                        temp['CB_Values'][indexST] = (shares[1]) * CB.iloc[indexST].Price
                        temp['PB_Values'][indexST] = (shares[2]) * PB.iloc[indexST].Price
                        temp['GO_Values'][indexST] = (shares[3]) * GO.iloc[indexST].Price
                        temp['CA_Values'][indexST] = (shares[4])
                        shares = [((current_money * (row[0] / 100))) / rowST.Price, ((current_money * (row[1] / 100))) / CB.iloc[indexST].Price, ((current_money * (row[2] / 100))) / PB.iloc[indexST].Price, ((current_money * (row[3] / 100))) / GO.iloc[indexST].Price, (current_money * (row[4] / 100))]
                        a = 1
                    else:
                        if a == 1:
                            shares_current_value = [shares[0]*rowST.Price,shares[1]*CB.iloc[indexST].Price,shares[2]*PB.iloc[indexST].Price,shares[3]*GO.iloc[indexST].Price,shares[4]]
                            rebalance = rebalance_function(shares_values, shares_current_value)
                            current_money = sum(shares_current_value)
                            shares_prev_value = shares_current_value
                            temp['ST_Values'][indexST] = (shares[0]) * rowST.Price 
                            temp['CB_Values'][indexST] = (shares[1]) * CB.iloc[indexST].Price
                            temp['PB_Values'][indexST] = (shares[2]) * PB.iloc[indexST].Price
                            temp['GO_Values'][indexST] = (shares[3]) * GO.iloc[indexST].Price
                            temp['CA_Values'][indexST] = (shares[4])
                            a = 2
                        else: 
                            shares_current_value = [(shares_prev_value[0]/ST.iloc[indexST-1].Price)*rowST.Price,(shares_prev_value[1]/CB.iloc[indexST-1].Price)*CB.iloc[indexST].Price,(shares_prev_value[2]/PB.iloc[indexST-1].Price)*PB.iloc[indexST].Price,(shares_prev_value[3]/GO.iloc[indexST-1].Price)*GO.iloc[indexST].Price,shares_prev_value[4]]
                            rebalance = rebalance_function(shares_prev_value, shares_current_value)
                            current_money = sum(shares_current_value)
                            shares_prev_value = shares_current_value
                            temp['ST_Values'][indexST] = (shares[0]) * rowST.Price 
                            temp['CB_Values'][indexST] = (shares[1]) * CB.iloc[indexST].Price
                            temp['PB_Values'][indexST] = (shares[2]) * PB.iloc[indexST].Price
                            temp['GO_Values'][indexST] = (shares[3]) * GO.iloc[indexST].Price
                            temp['CA_Values'][indexST] = (shares[4])
                temp['Values'] = temp.sum(axis=1)
                trading_methodologies['Volatility'][index] = (temp['Values'].std() / temp['Values'].mean()) * 100


def return_function(money, trading_methodologies):
    return_options = [1,3,6,9,12]
    trading_methodologies['Return_1M'] = 0.0
    trading_methodologies['Return_3M'] = 0.0
    trading_methodologies['Return_6M'] = 0.0
    trading_methodologies['Return_9M'] = 0.0
    trading_methodologies['Return_12M'] = 0.0
    return_months = ["Jan-31-2020","Mar-31-2020","Jun-30-2020","Sep-30-2020","Dec-31-2020"]
    temp = pd.DataFrame(np.zeros((5,6)), columns = ['Period','ST_price','CB_price','PB_price','GO_price','CA_price'])  
    for index, i in enumerate(return_options):
        temp.Period[index] = i
        maskST = ST.Date == return_months[index]
        st_price = ST.Price[maskST]
        temp.ST_price[index] = st_price
        maskCB = CB.Date == return_months[index]
        cb_price = CB.Price[maskCB]
        temp.CB_price[index] = cb_price
        maskPB = PB.Date == return_months[index]
        pb_price = PB.Price[maskPB]
        temp.PB_price[index] = pb_price
        maskGO = GO.Date == return_months[index]
        go_price = GO.Price[maskGO]
        temp.GO_price[index] = go_price
        temp.CA_price[index] = 1
    for index, row in trading_methodologies.iterrows():
        print("Iteration return: " + str(index) + "...") 
        return_bymonths = []
        shares_values = [((money * (row[0] / 100))),((money * (row[1] / 100))),((money * (row[2] / 100))),((money * (row[3] / 100))),(money * (row[4] / 100))]  
        if row[5] == '1-OFF':
            shares = [((money * (row[0] / 100)) / ST.Price[0]),((money * (row[1] / 100)) / CB.Price[0]),((money * (row[2] / 100)) / PB.Price[0]),((money * (row[3] / 100)) / GO.Price[0]),(money * (row[4] / 100))]
            buy_amount = shares[0] * ST.Price[0] + shares[1] * CB.Price[0] + shares[2] * PB.Price[0] + shares[3] * GO.Price[0] + shares[4] * 1
            if row[6] == 'NO':
                for i, j in enumerate(return_options):
                    return_column = f"Return_{j}M" 
                    current_value = temp.ST_price[i]*shares[0]+temp.CB_price[i]*shares[1]+temp.PB_price[i]*shares[2]+temp.GO_price[i]*shares[3]+temp.CA_price[i]*shares[4]
                    portfolio_return = ((current_value - buy_amount)/buy_amount) * 100
                    trading_methodologies[return_column][index] = round(portfolio_return,2) 
            else:
                for indexST, rowST in ST.iterrows():
                    if ("15" in rowST['Date']):
                        shares_current_value = [(shares_prev_value[0]/ST.iloc[indexST-1].Price)*rowST.Price,(shares_prev_value[1]/CB.iloc[indexST-1].Price)*CB.iloc[indexST].Price,(shares_prev_value[2]/PB.iloc[indexST-1].Price)*PB.iloc[indexST].Price,(shares_prev_value[3]/GO.iloc[indexST-1].Price)*GO.iloc[indexST].Price,shares_prev_value[4]]
                        current_money = sum(shares_current_value)
                        shares_prev_value = shares_current_value
                        shares = [((current_money * (row[0] / 100))) / rowST.Price, ((current_money * (row[1] / 100))) / CB.iloc[indexST].Price, ((current_money * (row[2] / 100))) / PB.iloc[indexST].Price, ((current_money * (row[3] / 100))) / GO.iloc[indexST].Price, (current_money * (row[4] / 100))]
                    elif (rowST['Date'] in return_months):
                        index_month = return_months.index(rowST['Date'])
                        index_options = return_options[index_month]
                        current_value = temp.ST_price[temp['Period'] == index_options]*shares[0]+temp.CB_price[temp['Period'] == index_options]*shares[1]+temp.PB_price[temp['Period'] == index_options]*shares[2]+temp.GO_price[temp['Period'] == index_options]*shares[3]+temp.CA_price[temp['Period'] == index_options]*shares[4]
                        portfolio_return = ((current_value - buy_amount)/buy_amount) * 100
                        mask = f"Return_{index_options}M"
                        trading_methodologies[mask][index] = round(portfolio_return,2)   
                    elif ("14" in rowST['Date']):
                        shares_current_value = [shares[0]*rowST.Price,shares[1]*CB.iloc[indexST].Price,shares[2]*PB.iloc[indexST].Price,shares[3]*GO.iloc[indexST].Price,shares[4]]
                        rebalance = rebalance_function(shares_values, shares_current_value)
                        current_money = sum(shares_current_value)
                        shares_prev_value = shares_current_value
        else:
            buy_amount_total = 0
            if row[6] == 'NO':
                shares2 = [0,0,0,0,0]
                for indexST, rowST in ST.iterrows():
                    if ("01" in rowST['Date']):
                        shares = dca(money, row[:5], 12, [rowST.Price, CB.iloc[indexST].Price, PB.iloc[indexST].Price, GO.iloc[indexST].Price, 1])
                        shares2 = list(i+j for (i,j) in zip(shares2,shares))
                        buy_amount = shares[0] * ST.Price[indexST] + shares[1] * CB.Price[indexST] + shares[2] * PB.Price[indexST] + shares[3] * GO.Price[indexST] + shares[4] * 1
                        buy_amount_total = buy_amount_total + buy_amount
                    elif (rowST['Date'] in return_months):
                        index_month = return_months.index(rowST['Date'])
                        index_options = return_options[index_month]
                        current_value = temp.ST_price[temp['Period'] == index_options]*shares2[0]+temp.CB_price[temp['Period'] == index_options]*shares2[1]+temp.PB_price[temp['Period'] == index_options]*shares2[2]+temp.GO_price[temp['Period'] == index_options]*shares2[3]+temp.CA_price[temp['Period'] == index_options]*shares2[4]
                        portfolio_return = ((current_value - buy_amount_total)/buy_amount_total) * 100
                        mask = f"Return_{index_options}M"
                        trading_methodologies[mask][index] = round(portfolio_return,2)
            else:
                shares_prev_value = [0,0,0,0,0]
                shares2 = [0,0,0,0,0]
                for indexST, rowST in ST.iterrows():
                    if ("01" in rowST['Date']):
                        shares = dca(money, row[:5], 12, [rowST.Price, CB.iloc[indexST].Price, PB.iloc[indexST].Price, GO.iloc[indexST].Price, 1])
                        shares_current_value = [shares2[0]*rowST.Price,shares2[1]*CB.iloc[indexST].Price,shares2[2]*PB.iloc[indexST].Price,shares2[3]*GO.iloc[indexST].Price,shares2[4]]
                        shares2 = list(i+j for (i,j) in zip(shares2, shares))
                        buy_amount = shares[0] * ST.Price[indexST] + shares[1] * CB.Price[indexST] + shares[2] * PB.Price[indexST] + shares[3] * GO.Price[indexST] + shares[4] * 1
                        buy_amount_total = buy_amount_total + buy_amount
                    elif ("15" in rowST['Date']):
                        shares2 = [((current_money * (row[0] / 100))) / rowST.Price, ((current_money * (row[1] / 100))) / CB.iloc[indexST].Price, ((current_money * (row[2] / 100))) / PB.iloc[indexST].Price, ((current_money * (row[3] / 100))) / GO.iloc[indexST].Price, (current_money * (row[4] / 100))]
                        shares_current_value = [shares2[0]*rowST.Price,shares2[1]*CB.iloc[indexST].Price,shares2[2]*PB.iloc[indexST].Price,shares2[3]*GO.iloc[indexST].Price,shares2[4]]
                        shares_prev_value = shares_current_value
                    elif (rowST['Date'] in return_months):
                        index_month = return_months.index(rowST['Date'])
                        index_options = return_options[index_month]
                        current_value = temp.ST_price[temp['Period'] == index_options]*shares2[0]+temp.CB_price[temp['Period'] == index_options]*shares2[1]+temp.PB_price[temp['Period'] == index_options]*shares2[2]+temp.GO_price[temp['Period'] == index_options]*shares2[3]+temp.CA_price[temp['Period'] == index_options]*shares2[4]
                        portfolio_return = ((current_value - buy_amount_total)/buy_amount_total) * 100
                        mask = f"Return_{index_options}M"
                        trading_methodologies[mask][index] = round(portfolio_return,2)   
                    elif ("14" in rowST['Date']):
                        shares_current_value = [shares2[0]*rowST.Price,shares2[1]*CB.iloc[indexST].Price,shares2[2]*PB.iloc[indexST].Price,shares2[3]*GO.iloc[indexST].Price,shares2[4]]
                        current_money = sum(shares_current_value)
                        shares_prev_value = shares_current_value                      
                        

# Define variables
cost(trading_methodologies)
volatility(1000000,trading_methodologies)
return_function(1000000,trading_methodologies)
trading_methodologies.to_csv('portfolio_metrics.csv', header=True, index=False)
