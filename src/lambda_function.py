# from posixpath import split
import pandas as pd  
import requests
from datetime import date
import numpy as np  
from tabulate import tabulate
# import matplotlib.pyplot as plt  
# import seaborn as seabornInstance 
from sklearn.model_selection import train_test_split 
from sklearn.linear_model import LinearRegression
from sklearn import metrics

def count_wins_against(pid, win_counts):
    if pid not in win_counts:
        win_counts[pid] = 0
    return_val = win_counts[pid]
    win_counts[pid] += 1
    return return_val

def count_losses_against(pid, loss_counts):
    if pid not in loss_counts:
        loss_counts[pid] = 0
    return_val = loss_counts[pid]
    loss_counts[pid] += 1
    return return_val

def count_points_against(points, win_or_lose, player_id, winner, loser, winner_points, loser_points):
    print(f"{str(win_or_lose)}\t{str(player_id)}\t{str(winner)}\t{str(loser)}\t{str(winner_points)}\t{str(loser_points)}\t")
    if player_id not in points:
        points[player_id] = {'won': 0, 'lost': 0}
    
    if winner not in points:
        points[winner] = {'won': 0, 'lost': 0}

    if loser not in points:
        points[loser] = {'won': 0, 'lost': 0}

    if winner == player_id:
        return_val = points[loser]['won'] if win_or_lose == 'win' else points[loser]['lost']
        points[loser]['won'] += winner_points
        points[loser]['lost'] += loser_points
        return return_val
    else:
        return_val = points[winner]['won'] if win_or_lose == 'win' else points[winner]['lost']
        points[winner]['won'] += loser_points
        points[winner]['lost'] += winner_points
        return return_val
    

def build_dataframe(player_id, player_data):
    # request relevant player data
    player = requests.get(f"https://api.badminton-api.com/player?player_id={player_id}").json()
    player_info = player['data']
    birthDate = player_info['birthDate'] if 'birthDate' in player_info else None

    # initialize dataframe
    df = pd.DataFrame(player_data, index=[i for i in range(len(player_data))])

    # build df up from other columns
    df['totalMatchesWon'] = (df['winnerId'] == player_id).cumsum()
    df['totalMatchesLost'] = (df['loserId'] == player_id).cumsum()

    df['totalPointsWon'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], df['loserPoints']).cumsum()
    df['totalPointsLost'] = np.where(df['winnerId'] == player_id, df['loserPoints'], df['winnerPoints']).cumsum()

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

    df['recentPointsWon'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], df['loserPoints'])
    df['recentPointsWon'] = df.rolling(min_periods=1, window=5)['recentPointsWon'].sum()

    df['recentPointsLost'] = np.where(df['winnerId'] == player_id, df['loserPoints'], df['winnerPoints'])
    df['recentPointsLost'] = df.rolling(min_periods=1, window=5)['recentPointsLost'].sum()

    ## The outcome of our match - our y factor
    df['wonMatch'] = np.where(df['winnerId'] == player_id, True, False)

    ## Add h2h columns defined in extracted_features
    df['h2hMatchesWon'] = np.where((df['winnerId'] == player_id), df.groupby('loserId').cumcount(), df.groupby('winnerId').cumcount())
    df['h2hMatchesLost'] = np.where((df['loserId'] == player_id), df.groupby('winnerId').cumcount(), df.groupby('loserId').cumcount())

    df['h2hPointsWon'] = np.where((df['winnerId'] == player_id), df.groupby('loserId')['winnerPoints'].cumsum(), df.groupby('winnerId')['loserPoints'].cumsum())
    df['h2hPointsLost'] = np.where((df['loserId'] == player_id), df.groupby('winnerId')['loserPoints'].cumsum(), df.groupby('loserId')['winnerPoints'].cumsum())

    return df

x_fields = ['matchesWonCount', 'matchesLostCount', 'pointsWonCount', 'pointsLostCount', 'age', 'recentMatchesWon', 'recentMatchesLost', 'recentPointsWon', 'recentPointsLost']

def train_lin_reg_model(df):
    X = df[['age', 'totalMatchesWon', 'totalMatchesLost', 'totalPointsWon', 'totalPointsLost', \
            'recentMatchesWon', 'recentMatchesLost', 'recentPointsWon', 'recentPointsLost', \
            'h2hMatchesWon', 'h2hMatchesLost', 'h2hPointsWon', 'h2hPointsLost']]
    y = df['wonMatch']  

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    y_pred = regressor.predict(X_test)
    df = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    return df

def lambda_handler(event, context):   
    return "Hello world"

if __name__ == '__main__':
    player1 = "5F74B009-175F-4564-8C8E-7C57FDCF8D10"
    response1 = requests.get(f"https://api.badminton-api.com/match/player_detailed?player_id={player1}&sort_desc=False")
    response1 = response1.json()
    df1 = build_dataframe(player1, response1['data'])
    print(tabulate(df1, headers = 'keys', tablefmt = 'psql'))
    lin_df = train_lin_reg_model(df1)
    print(tabulate(lin_df, headers = 'keys', tablefmt = 'psql'))

    # player2 = "0800FC8B-CBAB-4AC1-B6C7-F3D419906440"
    # response2 = requests.get(f"https://api.badminton-api.com/match/player_detailed?player_id={player2}&sort_desc=False")
    # response2 = response2.json()
    # df2 = build_dataframe(player2, response2['data'])
    # print(tabulate(df2, headers = 'keys', tablefmt = 'psql'))
    # lin_df2 = train_lin_reg_model(df2)
    # print(tabulate(lin_df2, headers = 'keys', tablefmt = 'psql'))
