import pandas as pd  
import numpy as np 
from sklearn import metrics, svm, model_selection
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split

from helpers import predictive_interval as pred_int

TESTING_SIZE = 0.5
X_FIELDS = ['age', 'totalMatchesWon', 'totalMatchesLost', 'totalPointsWon', 'totalPointsLost', \
            'recentMatchesWon', 'recentMatchesLost', 'recentPointsWon', 'recentPointsLost', \
            'h2hMatchesWon', 'h2hMatchesLost', 'h2hPointsWon', 'h2hPointsLost']

X_FIELDS_RATIOS = ['totalMatchWinRatio', 'totalPointWinRatio', 'recentMatchWinRatio', \
                    'recentPointWinRatio', 'h2hMatchWinRatio', 'h2hPointWinRatio']
Y_FIELD = 'wonMatch'

def train_lin_reg_model(df):
    # independent variables
    X = df[X_FIELDS_RATIOS]

    # dependent variables
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
    print(f'Prediction Interval: \nLower: {prediction_interval[0]}\tUpper: {prediction_interval[2]}\n\n' )

    return df

def train_log_reg_model(df):
    # dependent variables
    X = df[X_FIELDS_RATIOS]

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

    kfold = model_selection.KFold(n_splits=10, random_state=7, shuffle=True)
    scoring = 'accuracy'
    results = model_selection.cross_val_score(regressor, X, y, cv=kfold, scoring=scoring)
    print("Logistic Regression Accuracy: %.3f (%.3f)" % (results.mean(), results.std()))

    return df

def train_sup_vec_class_model(df):
    # dependent variables
    X = df[X_FIELDS_RATIOS]

    # independent variables
    y = df[Y_FIELD] 
    y = y.astype('int') 

    ## Split data into training data and testing data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=TESTING_SIZE, random_state=0)
    regressor = svm.SVC()
    regressor.fit(X_train, y_train)

    ## Predict results using testing data
    y_pred = regressor.predict(X_test)
    df = pd.DataFrame({'Win?': y_test, 'Predicted': y_pred})

    kfold = model_selection.KFold(n_splits=10, random_state=7, shuffle=True)
    scoring = 'accuracy'
    results = model_selection.cross_val_score(regressor, X, y, cv=kfold, scoring=scoring)
    print("Support Vector Classification Accuracy: %.3f (%.3f)" % (results.mean(), results.std()))

    prediction_interval = pred_int.get_prediction_interval(y_pred[0], y_test, y_pred)
    print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))
    print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))
    print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
    print(f'Prediction Interval: \nLower: {prediction_interval[0]}\tUpper: {prediction_interval[2]}\n\n' )

    return df