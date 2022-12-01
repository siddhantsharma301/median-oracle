import numpy as np
import pandas as pd
import sqlite3

connection = sqlite3.connect("results.db")
query = pd.read_sql_query('''SELECT * FROM Swap''', connection)
columns = ['pairName', 'blockNumber', 'logIndex', 'tick', 'sqrtPriceX96']
df = pd.DataFrame(query, columns=columns)

def generate_oscillating(df):
    df = df[df.pairName =='USDC/WETH/3000']
    price1, price2 = 195298, 200510
    oscillating = np.empty((len(df),))
    oscillating[::2] = price1
    oscillating[1::2] = price2
    sqrtPriceX96 =  np.sqrt(np.power(1.0001, oscillating)) * (2**96)
    oscillating = list(map(int, oscillating.tolist()))
    sqrtPriceX96 = sqrtPriceX96.tolist()
    sqrtPriceX96 = list(map(str,map(int, sqrtPriceX96)))

    df.loc[:,"tick"] = oscillating
    df.loc[:,"sqrtPriceX96"] = sqrtPriceX96

    conn = sqlite3.connect("oscillating.db")
    df.to_sql('Swap', con=conn, if_exists='replace')

def generate_winsorize(df):
    df = df[df.pairName == 'USDC/WETH/3000']
    winsorize = np.ones((len(df),)) * 2e5
    noise = np.random.uniform(0, 10_000, (len(df),))
    sign = np.random.choice(a=[1, -1], size=(len(df),))
    winsorize = winsorize + noise * sign
    sqrtPriceX96 = np.sqrt(np.power(1.0001, winsorize)) * (2**96)
    winsorize = list(map(int, winsorize.tolist()))
    sqrtPriceX96 = sqrtPriceX96.tolist()
    sqrtPriceX96 = list(map(str,map(int, sqrtPriceX96)))

    df.loc[:,"tick"] = winsorize
    df.loc[:,"sqrtPriceX96"] = sqrtPriceX96
    conn = sqlite3.connect("winsorize.db")
    df.to_sql('Swap', con=conn, if_exists='replace')

generate_oscillating(df.copy())
generate_winsorize(df.copy())