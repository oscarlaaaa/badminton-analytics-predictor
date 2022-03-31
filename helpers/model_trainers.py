import pandas as pd  
import numpy as np 
from sklearn import svm, model_selection
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

X_FIELDS_RATIOS = ['totalMatchWinRatio', 'totalPointWinRatio', 'recentMatchWinRatio', \
                    'recentPointWinRatio', 'h2hMatchWinRatio', 'h2hPointWinRatio']
Y_FIELD = 'wonMatch'

def train_log_reg_model(df):
    # dependent variables
    X = df[X_FIELDS_RATIOS]

    # independent variables
    y = df[Y_FIELD]  
    y = y.astype('int')

    ## exclude prediction row
    X_train = X[:-1].to_numpy()
    y_train = y[:-1].to_numpy()

    ## train model
    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    regressor = LogisticRegression()
    regressor.fit(X_train_scaled, y_train)

    ## predict results using trained model
    prediction = regressor.predict(scaler.transform(X.tail(1).to_numpy().reshape(1,-1)))
    probability = regressor.predict_proba(scaler.transform(X.tail(1).to_numpy().reshape(1,-1)))

    ## evaluate accuracy of model
    splits = df.shape[0] if df.shape[0] < 10 else 10
    kfold = model_selection.KFold(n_splits=splits, random_state=7, shuffle=True)
    scoring = 'accuracy'
    results = model_selection.cross_val_score(regressor, X, y, cv=kfold, scoring=scoring)

    ## format results
    output = {"acc": results.mean(), "std": results.std(), "pred": prediction[0], "prob": probability[0]}

    return output

def train_sup_vec_class_model(df):
    # dependent variables
    X = df[X_FIELDS_RATIOS]

    # independent variables
    y = df[Y_FIELD]
    y = y.astype('int') 

    ## exclude prediction row
    X_train = X[:-1].to_numpy()
    y_train = y[:-1].to_numpy()

    ## train model
    regressor = svm.SVC(probability=True, kernel="linear")
    regressor.fit(X_train, y_train)

    ## predict results using trained model
    prediction = regressor.predict(X.tail(1).to_numpy().reshape(1,-1))
    probability = regressor.predict_proba(X.tail(1).to_numpy().reshape(1,-1))

    # evaluate accuracy of model
    splits = df.shape[0] if df.shape[0] < 10 else 10
    kfold = model_selection.KFold(n_splits=splits, random_state=7, shuffle=True)
    scoring = 'accuracy'
    results = model_selection.cross_val_score(regressor, X, y, cv=kfold, scoring=scoring)

    ## format results
    output = {"acc": results.mean(), "std": results.std(), "pred": prediction[0], "prob": probability[0]}

    return output