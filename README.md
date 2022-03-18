# Badminton Analytics Predictor
A predictive machine-learning lambda that provides the probability of one player's victory over another. Provides functionality for the [Badminton Analytics Dashboard](https://github.com/oscarlaaaa/badminton-analytics/)'s head-to-head prediction feature (WIP).


### Features:
- Predicted % chance of victory between two players
- Fully implemented Linear Regression and Logistic Regression models with 13 extracted features
- Optimized database table to avoid costly joins when building dataframe
- Calculated Mean Absolute, Mean Squared, Root Mean Squared error values, and Prediction Interval Bounds.


### Roadmap:
- [x] Initialize project + set up lambda
- [x] Establish extracted features for linear regression
- [x] Build dataframe for linear regression
- [x] Implement training linear regression model on input data
- [ ] Establish other desired features + what other models to utilize
- [ ] Establish benchmark for what to use as the comparative baselines (win/loss? ranking?)
- [ ] Deploy + link it up to the dashboard