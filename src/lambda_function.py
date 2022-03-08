from posixpath import split
import pandas as pd  
import requests
from datetime import date
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

    df['pointsWonCount'] = np.where(df['winnerId'] == player_id, df['winnerPoints'], df['loserPoints']).cumsum()
    df['pointsLostCount'] = np.where(df['winnerId'] == player_id, df['loserPoints'], df['winnerPoints']).cumsum()

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

    ## STUB: Add h2h columns defined in extracted_features

    df['wonMatch'] = np.where(df['winnerId'] == player_id, True, False)
    return df

x_fields = ['matchesWonCount', 'matchesLostCount', 'pointsWonCount', 'pointsLostCount', 'age', 'recentMatchesWon', 'recentMatchesLost', 'recentPointsWon', 'recentPointsLost']

def train_lin_reg_model(df):
    X = df[['matchesWonCount', 'matchesLostCount', 'pointsWonCount', 'pointsLostCount', 'age', 'recentMatchesWon', 'recentMatchesLost', 'recentPointsWon', 'recentPointsLost']]
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
    
    player2 = "7E0F5DB7-EF7F-4B68-8D46-8473F7DEB1EA"
    response2 = requests.get(f"https://api.badminton-api.com/match/player_detailed?player_id={player2}&sort_desc=False")

    response1 = response1.json()
    response2 = response2.json()
    df1 = build_dataframe(player1, response1['data'])
    df2 = build_dataframe(player2, response2['data'])

    lin_df = train_lin_reg_model(df1, df2)
    print(tabulate(lin_df, headers = 'keys', tablefmt = 'psql'))
