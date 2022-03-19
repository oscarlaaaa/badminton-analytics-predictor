import requests
from datetime import date
import pandas as pd
import numpy as np

def build_dataframe(player_id, player_data, opponent_id):
    ROLLING_WINDOW = 5

    # request relevant player data
    player = requests.get(f"https://api.badminton-api.com/player?player_id={player_id}").json()
    player_info = player['data']
    birthDate = player_info['birthDate'] if 'birthDate' in player_info else None

    # initialize dataframe
    df = pd.DataFrame(player_data, index=[i for i in range(len(player_data))])
    df2 = pd.DataFrame({'winnerId': player_id, 'duration': None, 'winnerPoints': None, 'setCount': None, 'loserId': opponent_id, 'tournamentId': None, 'startDate': None, 'loserPoints': None}, index=[0])
    df = pd.concat([df, df2], ignore_index=True, axis=0)

    df.fillna(0, inplace=True)
    
    # build up total matches/points won/lost from previous rows
    df['totalMatchesWon'] = (df['winnerId'] == player_id).cumsum().sub(df['winnerId'] == player_id)
    df['totalMatchesLost'] = (df['loserId'] == player_id).cumsum().sub(df['loserId'] == player_id)

    df['totalPointsWon'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], df['loserPoints']).cumsum()
    df['totalPointsWon'] = np.where(df['winnerId'] == player_id, df['totalPointsWon'].sub(df['winnerPoints']), df['totalPointsWon'].sub(df['loserPoints']))
    df['totalPointsLost'] = np.where(df['winnerId'] == player_id, df['loserPoints'], df['winnerPoints']).cumsum()
    df['totalPointsLost'] = np.where(df['winnerId'] == player_id, df['totalPointsLost'].sub(df['loserPoints']), df['totalPointsWon'].sub(df['winnerPoints']))

    # only calculate age if available
    if birthDate:
        splitdate1 = birthDate.split('-')
        birthDate = date(year=int(splitdate1[0]), month=int(splitdate1[1]), day=int(splitdate1[2]))
        birthDate = pd.Timestamp(birthDate)
        df['startDate'] = pd.to_datetime(df['startDate'], format='%Y-%m-%d') #if conversion required
        df['age'] = (df['startDate'] - birthDate).astype('<m8[Y]')    # 3
    else:
        df['age'] = 0
    
    ## The outcome of our match - our y factor
    df['wonMatch'] = np.where(df['winnerId'] == player_id, True, False)
    df['lostMatch'] = np.where(df['winnerId'] == player_id, False, True)

    # calculate a rolling summation for recent matches/points
    df['recentMatchesWon'] = np.where(df['winnerId'] == player_id, 1, 0)
    df['recentMatchesWon'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentMatchesWon'].sum().sub(df['recentMatchesWon'])
    df['recentMatchesLost'] = np.where(df['loserId'] == player_id, 1, 0)
    df['recentMatchesLost'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentMatchesLost'].sum().sub(df['recentMatchesLost'])

    df['recentPointsWon'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], df['loserPoints'])
    df['recentPointsWon'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentPointsWon'].sum().sub(df['recentPointsWon'])
    df['recentPointsLost'] = np.where(df['winnerId'] == player_id, df['loserPoints'], df['winnerPoints'])
    df['recentPointsLost'] = df.rolling(min_periods=1, window=ROLLING_WINDOW)['recentPointsLost'].sum().sub(df['recentPointsLost'])

    ## Add h2h columns defined in extracted_features
    df['opponent'] = np.where(df['winnerId'] == player_id, df['loserId'], df['winnerId'])
    df['h2hMatchesWon'] = df.groupby('opponent')['wonMatch'].cumsum().sub(df['wonMatch'])
    df['h2hMatchesLost'] = df.groupby('opponent')['lostMatch'].cumsum().sub(df['lostMatch'])

    df['h2hPointsWon'] = np.where((df['winnerId'] == player_id), df.groupby('loserId')['winnerPoints'].cumsum().sub(df['winnerPoints']), df.groupby('winnerId')['loserPoints'].cumsum().sub(df['loserPoints']))
    df['h2hPointsLost'] = np.where((df['winnerId'] == player_id), df.groupby('loserId')['loserPoints'].cumsum().sub(df['loserPoints']), df.groupby('winnerId')['winnerPoints'].cumsum().sub(df['winnerPoints']))

    # simplify independent variables
    df['totalMatchWinRatio'] = df['totalMatchesWon'] / (df['totalMatchesWon'] + df['totalMatchesLost'])
    df['totalPointWinRatio'] = df['totalPointsWon'] / (df['totalPointsWon'] + df['totalPointsLost'])
    df['recentMatchWinRatio'] = df['recentMatchesWon'] / (df['recentMatchesWon'] + df['recentMatchesLost'])
    df['recentPointWinRatio'] = df['recentPointsWon'] / (df['recentPointsWon'] + df['recentPointsLost'])
    df['h2hMatchWinRatio'] = df['h2hMatchesWon'] / (df['h2hMatchesWon'] + df['h2hMatchesLost'])
    df['h2hPointWinRatio'] = df['h2hPointsWon'] / (df['h2hPointsWon'] + df['h2hPointsLost'])

    # drop last row and replace NaN with 0
    df.fillna(0, inplace=True)

    return df