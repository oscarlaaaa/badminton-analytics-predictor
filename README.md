# Badminton Analytics Predictor
A predictive machine-learning lambda that provides the probability of one player's victory over another. Provides functionality for the [Badminton Analytics Dashboard](https://github.com/oscarlaaaa/badminton-analytics/)'s head-to-head prediction feature.

## Current features:
- Predicted % chance of victory between two players
- Fully implemented Logistic Regression and Support Vector Classification (linear) models with 6 extracted features
- Optimized database table to avoid costly joins when building dataframe
- Dockerized Lambda platform to circumvent 250mb size limit
- Accuracy, standard deviation, prediction, and probability values after each Lambda call

## Motivation:
I've always wanted a way to use the data I've shamelessly scraped from tournamentsoftware to try and draw some kind of useful conclusion, so I decided that to implement some kind of match outcome predictor! While the returned data is likely inaccurate, incomplete, and likely a stain on the machine learning community, it was a bunch of fun making it (minus the AWS issues...)!

## Technologies:
- Python 3.9
- AWS Lambda and API Gateway
- Scikit-Learn (Numpy, Pandas)
- Docker

## How it works:
### __Building the model__:
The lambda utilizes Numpy and Pandas to transform the input data into a usable dataframe. We extract the following features to be used in our prediction:

1. Ratio of total points won/lost
2. Ratio of total matches won/lost
3. Ratio of recent (last 5) points won/lost
4. Ratio of recent (last 5) matches won/lost
5. Head-to-head ratio of points won/lost against a specific player
6. Head-to-head ratio of matches won/lost against a specific player

All of these extracted features are produced through cumulative sum/count, meaning that the only the previous matches (barring the current one) will impact the prediction outcome and minimizing bias present.

The models I have decided upon to predict the match outcome are the classification models of Logistic Regression, and Support Vector Classification (linear). Determining the outcome of a match is binary in nature (win or loss), and so a classficiation model would be the best option for this purpose. I chose two different models just to play around with Scikit-Learn and have fun with my first ML project B)

### __Training__:
Models are trained using the entire dataset prior to prediction. Accuracy is determined using a K-Folds cross-validator with up to 10 split groups performed by calling ```result.mean()```, and standard deviation is derived from calling ```result.std()```, where ```result``` is the outcome of the cross-validation.

### __Prediction__:
Predictions are derived by inserting a row without data with the desired player and opponent pair - the extracted features are generated from the previous rows, so it doesn't require the same data filled out. The models then invoke the methods ```model.predict()``` and ```model.predict_proba()``` to extract the prediction and probability results respectively.

### __Output__:
If everything goes well, then you should receive an output with this format:

```JSON
{
    "statusCode": 200,
    "headers": {"Content-Type": "application/json"},
    "body": { 
        "player": player_id, 
        "opponent": opponent_id, 
        "type": model_type, 
        "results": {
            "acc": acc, 
            "std": std, 
            "pred": prediction, 
            "prob": probability
        }
    }
}
```
>Note: The body will be returned in string format, so you will need to parse the body before using it.


## How to use:
This project requires the following technologies:
- Python 3.9
- Docker
- AWS CLI and a working AWS account
- A terminal that can run shell scripts

To deploy the project onto AWS Lambda:
1. Clone the repository using ```git clone https://github.com/oscarlaaaa/badminton-analytics-lambda```
2. Navigate into the base folder of the repository
3. Open up a git bash console or any console that can run bash shell scripts
4. Set the required environmental variables or simply replace placeholders in ```push_image.sh``` with their corresponding values (```AWS_REGION```,  ```REPOSITORY_NAME```,  ```IMAGE_NAME```,  ```AWS_ACCOUNT_ID```)
5. Make the script runnable by running ```chmod +x push_image.sh```
6. Run the script by running ```./push_image.sh```

To query the Lambda function:
1. Query player matches from the [Badminton Singles API](https://api.badminton-api.com) in descending order
2. Send the data to the lambda in the form of the following request:
```json
{
  "player": <player-id>,
  "opponent": <opponent-id>,
  "type": <logistic_regression> OR <support_vector_classification>,
  "data": <all match data here>
}
```
3. Await the function call for up to 10 seconds for the data to be returned

>Please note that you will have to expose the Lambda endpoint on AWS API Gateway in order to access it. Information on how to set it up can be found at: https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html

## How to contribute:
This project is a bit of a throwaway project, so I won't be taking any contributions for this project. If you have any questions though, feel free to ask!

## Roadmap:
- [x] Initialize project + set up lambda
- [x] Establish extracted features for linear regression
- [x] Build dataframe for linear regression
- [x] Implement training linear regression model on input data
- [x] Establish other desired features + what other models to utilize
- [x] Establish benchmark for what to use as the comparative baselines (win/loss? ranking?)
- [x] Deploy on AWS Lambda
