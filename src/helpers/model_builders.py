import requests
from datetime import date
import pandas as pd
import numpy as np

def build_dataframe(player_id, player_data):
    ROLLING_WINDOW = 5

    # request relevant player data
    player = requests.get(f"https://api.badminton-api.com/player?player_id={player_id}").json()
    player_info = player['data']
    birthDate = player_info['birthDate'] if 'birthDate' in player_info else None

    # initialize dataframe
    df = pd.DataFrame(player_data, index=[i for i in range(len(player_data))])

    # build up total matches/points won/lost from previous rows
    df['totalMatchesWon'] = (df['winnerId'] == player_id).cumsum()
    df['totalMatchesLost'] = (df['loserId'] == player_id).cumsum()

    df['totalPointsWon'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], df['loserPoints']).cumsum()
    df['totalPointsLost'] = np.where(df['winnerId'] == player_id, df['loserPoints'], df['winnerPoints']).cumsum()

    # shift rows down by 1 so they represent state of player prior to current row
    df.loc[len(df.index), :] = None
    df['totalMatchesWon'] = df.totalMatchesWon.shift(1)
    df['totalMatchesLost'] = df.totalMatchesLost.shift(1)
    df['totalPointsWon'] = df.totalPointsWon.shift(1)
    df['totalPointsLost'] = df.totalPointsLost.shift(1)
    df.drop(df.tail(1).index, inplace=True) # drop last n rows

    # only calculate age if available
    if birthDate:
        splitdate1 = birthDate.split('-')
        birthDate = date(year=int(splitdate1[0]), month=int(splitdate1[1]), day=int(splitdate1[2]))
        birthDate = pd.Timestamp(birthDate)
        df['startDate'] = pd.to_datetime(df['startDate'], format='%Y-%m-%d') #if conversion required
        df['age'] = (df['startDate'] - birthDate).astype('<m8[Y]')    # 3
    else:
        df['age'] = 0
    
    # calculate a rolling summation for recent matches/points
    df['recentMatchesWon'] = np.where(df['winnerId'] == player_id, 1, 0)
    df['recentMatchesWon'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentMatchesWon'].sum()
    df['recentMatchesLost'] = np.where(df['loserId'] == player_id, 1, 0)
    df['recentMatchesLost'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentMatchesLost'].sum()

    df['recentPointsWon'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], df['loserPoints'])
    df['recentPointsWon'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentPointsWon'].sum()
    df['recentPointsLost'] = np.where(df['winnerId'] == player_id, df['loserPoints'], df['winnerPoints'])
    df['recentPointsLost'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentPointsLost'].sum()

    ## Add h2h columns defined in extracted_features
    df['h2hMatchesWon'] = np.where((df['winnerId'] == player_id), df.groupby('loserId').cumcount(), df.groupby('winnerId').cumcount())
    df['h2hMatchesLost'] = np.where((df['winnerId'] == player_id), df.groupby('winnerId').cumcount(), df.groupby('loserId').cumcount())

    df['h2hPointsWon'] = np.where((df['winnerId'] == player_id), df.groupby('loserId')['winnerPoints'].cumsum(), df.groupby('winnerId')['loserPoints'].cumsum())
    df['h2hPointsLost'] = np.where((df['winnerId'] == player_id), df.groupby('loserId')['loserPoints'].cumsum(), df.groupby('winnerId')['winnerPoints'].cumsum())

    # push down total matches/points won/lost by 1 to have a prefix-sum style
    df.loc[len(df.index), :] = None
    df['totalMatchesWon'] = df.totalMatchesWon.shift(0)
    df['totalMatchesLost'] = df.totalMatchesLost.shift(0)
    df['totalPointsWon'] = df.totalPointsWon.shift(0)
    df['totalPointsLost'] = df.totalPointsLost.shift(0)

    # simplify independent variables
    df['totalMatchWinRatio'] = df['totalMatchesWon'] / (df['totalMatchesWon'] + df['totalMatchesLost'])
    df['totalPointWinRatio'] = df['totalPointsWon'] / (df['totalPointsWon'] + df['totalPointsLost'])
    df['recentMatchWinRatio'] = df['recentMatchesWon'] / (df['recentMatchesWon'] + df['recentMatchesLost'])
    df['recentPointWinRatio'] = df['recentPointsWon'] / (df['recentPointsWon'] + df['recentPointsLost'])
    df['h2hMatchWinRatio'] = df['h2hMatchesWon'] / (df['h2hMatchesWon'] + df['h2hMatchesLost'])
    df['h2hPointWinRatio'] = df['h2hPointsWon'] / (df['h2hPointsWon'] + df['h2hPointsLost'])

    ## The outcome of our match - our y factor
    df['wonMatch'] = np.where(df['winnerId'] == player_id, True, False)

    # drop last row and replace NaN with 0
    df.drop(df.tail(1).index, inplace=True) 
    df.fillna(1, inplace=True)

    return df