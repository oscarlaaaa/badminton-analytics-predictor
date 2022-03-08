from posixpath import split
import pandas as pd  
import requests
from datetime import date
import math
import numpy as np  
from tabulate import tabulate
import matplotlib.pyplot as plt  
import seaborn as seabornInstance 
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics


def build_dataframe(player_id, player_data):
    # request relevant player data
    player = requests.get(f"https://api.badminton-api.com/player?player_id={player_id}").json()
    player_info = player['data']
    birthDate = player_info['birthDate'] if 'birthDate' in player_info else None

    # initialize dataframe
    df = pd.DataFrame(player_data, index=[i for i in range(len(player_data))])

    # build df up from other columns
    df['matchesWonCount'] = (df['winnerId'] == player_id).cumsum()
    df['matchesLostCount'] = (df['loserId'] == player_id).cumsum()

    df['pointsWonCount'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], 0).cumsum()
    df['pointsLostCount'] = np.where(df['loserId'] == player_id, df['loserPoints'], 0).cumsum()

    if birthDate:
        splitdate1 = birthDate.split('-')
        birthDate = date(year=int(splitdate1[0]), month=int(splitdate1[1]), day=int(splitdate1[2]))
        birthDate = pd.Timestamp(birthDate)
        df['startDate'] = pd.to_datetime(df['startDate'], format='%Y-%m-%d') #if conversion required
        df['age'] = (df['startDate'] - birthDate).astype('<m8[Y]')    # 3
    
    df['recentMatchesWon'] = np.where(df['winnerId'] == player_id, 1, 0)
    df['recentMatchesWon'] = df.rolling(min_periods=1, window=5)['recentMatchesWon'].sum()

    df['recentMatchesLost'] = np.where(df['loserId'] == player_id, 1, 0)
    df['recentMatchesLost'] = df.rolling(min_periods=1, window=5)['recentMatchesLost'].sum()

    df['recentPointsWon'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], 0)
    df['recentPointsWon'] = df.rolling(min_periods=1, window=5)['recentPointsWon'].sum()

    df['recentPointsLost'] = np.where(df['loserId'] == player_id, df['loserPoints'], 0)
    df['recentPointsLost'] = df.rolling(min_periods=1, window=5)['recentPointsLost'].sum()

    df['wonMatch'] = np.where(df['winnerId'] == player_id, True, False)
    return df

def lambda_handler(event, context):   
    return "Hello world"

if __name__ == '__main__':
    response = requests.get("https://api.badminton-api.com/match/player_detailed?player_id=5F74B009-175F-4564-8C8E-7C57FDCF8D10&sort_desc=False")
    print(response)
    response = response.json()
    df = build_dataframe("5F74B009-175F-4564-8C8E-7C57FDCF8D10", response['data'])
    print(df.shape)
    print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
