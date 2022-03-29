# Badminton Analytics Predictor
A predictive machine-learning lambda that provides the probability of one player's victory over another. Provides functionality for the [Badminton Analytics Dashboard](https://github.com/oscarlaaaa/badminton-analytics/)'s head-to-head prediction feature (WIP).

## Current Features:
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
