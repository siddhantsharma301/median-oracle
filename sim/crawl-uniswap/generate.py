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
    df.tick = oscillating
    df.sqrtPriceX96 = sqrtPriceX96
    conn = sqlite3.connect("oscillating.db")
    df.to_sql('Swap', con=conn, if_exists='replace')

def generate_winsorize(df):
    df = df[df.pairName == 'USDC/WETH/3000']
    ticks = np.random.uniform(10_000, 15_000, (len(df),))
    boolean = np.random.choice(a=[False, True], size=(len(df),))
    winsorize = df.tick + ticks * (boolean < 0.2) #* sign
    sqrtPriceX96 = np.sqrt(np.power(1.0001, winsorize)) * (2**96)
    winsorize = list(map(int, winsorize.tolist()))
    sqrtPriceX96 = sqrtPriceX96.tolist()
    sqrtPriceX96 = list(map(str,map(int, sqrtPriceX96)))

    df.tick = winsorize
    df.sqrtPriceX96 = sqrtPriceX96
    conn = sqlite3.connect("winsorize.db")
    df.to_sql('Swap', con=conn, if_exists='replace')

def generate_winsorize_attack(df):
    def update_attack(idx, vals):
        length = len(idx)
        peak = np.random.uniform(215000, 220000)
        vals[idx] = np.linspace(vals[idx[0]], peak, num=length)
        return vals
    df = df[df.pairName == 'USDC/WETH/3000']
    df.reset_index(drop=True, inplace=True)
    vals = df.tick.to_numpy()
    attacks = [
        (df.blockNumber > 14765500) & (df.blockNumber < 14765550),
        (df.blockNumber > 14766000) & (df.blockNumber < 14766030),
        (df.blockNumber > 14767050) & (df.blockNumber < 14767075)
    ]
    for attack in attacks:
        vals = update_attack(df.index[attack].tolist(), vals)
    df.tick = vals
    sqrtPriceX96 = np.sqrt(np.power(1.0001, vals)) * (2**96)
    sqrtPriceX96 = sqrtPriceX96.tolist()
    sqrtPriceX96 = list(map(str,map(int, sqrtPriceX96)))
    df.sqrtPriceX96 = sqrtPriceX96
    conn = sqlite3.connect("attack.db")
    df.to_sql('Swap', con=conn, if_exists='replace')

generate_oscillating(df.copy())
generate_winsorize_attack(df.copy())
generate_winsorize(df.copy())