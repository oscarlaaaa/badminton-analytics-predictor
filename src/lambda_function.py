import requests
from datetime import date

import pandas as pd  
import numpy as np  

from tabulate import tabulate
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split

from helpers import predictive_interval as pred_int

ROLLING_WINDOW = 5
TESTING_SIZE = 0.2

X_FIELDS = ['age', 'totalMatchesWon', 'totalMatchesLost', 'totalPointsWon', 'totalPointsLost', \
        'recentMatchesWon', 'recentMatchesLost', 'recentPointsWon', 'recentPointsLost', \
        'h2hMatchesWon', 'h2hMatchesLost', 'h2hPointsWon', 'h2hPointsLost']
Y_FIELD = 'wonMatch'

def build_dataframe(player_id, player_data):
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

    df.loc[len(df.index), :] = None
    df['totalMatchesWon'] = df.totalMatchesWon.shift(1)
    df['totalMatchesLost'] = df.totalMatchesLost.shift(1)
    df['totalPointsWon'] = df.totalPointsWon.shift(1)
    df['totalPointsLost'] = df.totalPointsLost.shift(1)
    df.drop(df.tail(1).index,inplace=True) # drop last n rows

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

    ## The outcome of our match - our y factor
    df['wonMatch'] = np.where(df['winnerId'] == player_id, True, False)

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

    # drop last row and replace NaN with 0
    df.drop(df.tail(1).index,inplace=True) 
    df['totalMatchesWon'] = df['totalMatchesWon'].fillna(0)
    df['totalMatchesLost'] = df['totalMatchesLost'].fillna(0)
    df['totalPointsWon'] = df['totalPointsWon'].fillna(0)
    df['totalPointsLost'] = df['totalPointsLost'].fillna(0)

    return df

def train_lin_reg_model(df):
    # dependent variables
    X = df[X_FIELDS]

    # independent variables
    y = df[Y_FIELD]  

    ## Split data into training data and testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TESTING_SIZE, random_state=0)
    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    ## Predict results using testing data
    y_pred = regressor.predict(X_test)
    df = pd.DataFrame({'Win?': y_test, '% Chance Predicted': y_pred})
    prediction_interval = pred_int.get_prediction_interval(y_pred[0], y_test, y_pred)
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    print(f'Prediction Interval: \nLower: {prediction_interval[0]}\tUpper: {prediction_interval[2]}' )

    return df

def train_log_reg_model(df):
    # dependent variables
    X = df[X_FIELDS]

    # independent variables
    y = df[Y_FIELD]  
    y = y.astype('int')
    ## Split data into training data and testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TESTING_SIZE, random_state=0)

    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    regressor = LogisticRegression()
    regressor.fit(X_train_scaled, y_train)

    ## Predict results using testing data
    y_pred = regressor.predict(scaler.transform(X_test))
    df = pd.DataFrame({'Win?': y_test, 'Predicted Outcome': y_pred})
    prediction_interval = pred_int.get_prediction_interval(y_pred[0], y_test, y_pred)

    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    print(f'Prediction Interval: \nLower: {prediction_interval[0]}\tUpper: {prediction_interval[2]}' )

    return df
def lambda_handler(event, context):   
    return "Hello world"


if __name__ == '__main__':

    ### DONNIANS OLIVEIRA - ~17 matches ###
    player1 = "5F74B009-175F-4564-8C8E-7C57FDCF8D10"
    response1 = requests.get(f"https://api.badminton-api.com/match/player?player_id={player1}&sort_desc=False")
    response1 = response1.json()
    df1 = build_dataframe(player1, response1['data'])
    print(tabulate(df1, headers = 'keys', tablefmt = 'psql'))
    lin_df = train_log_reg_model(df1)
    print(tabulate(lin_df, headers = 'keys', tablefmt = 'psql'))

    ### LEE HYUN IL - 257 matches ###
    player2 = "0800FC8B-CBAB-4AC1-B6C7-F3D419906440"
    response2 = requests.get(f"https://api.badminton-api.com/match/player?player_id={player2}&sort_desc=False")
    response2 = response2.json()
    df2 = build_dataframe(player2, response2['data'])
    print(tabulate(df2, headers = 'keys', tablefmt = 'psql'))
    lin_df2 = train_log_reg_model(df2)
    print(tabulate(lin_df2, headers = 'keys', tablefmt = 'psql'))
