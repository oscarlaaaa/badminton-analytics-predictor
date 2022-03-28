from helpers import model_builders
from helpers import model_trainers
from helpers import util_functions

import logging
import json
# import requests
# from tabulate import tabulate

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def predict_winner(player_id, opponent_id, player_data, model_type):
    df = model_builders.build_dataframe(player_id, player_data, opponent_id)
    logger.info("Dataframe is built.")
    model = None
    
    if model_type == "logistic_regression":
        logger.info("Logistic regression model training.")
        model = model_trainers.train_log_reg_model(df)

    elif model_type == "support_vector_classification":
        logger.info("Support vector classification model training.")
        model = model_trainers.train_sup_vec_class_model(df)
    
    logger.info(f"Accuracy: {model['acc']} ({model['acc']})")
    logger.info(f"Prediction: {model['pred']}")
    logger.info(f"Probability: {model['prob']}")

    if not model:
        return "xd"
    
    return model

def lambda_handler(event, context):
    """
    Accepts an action and a number, performs the specified action on the number,
    and returns the result.

    :param event: The event dict that contains the parameters sent when the function
                  is invoked.

    :param context: The context in which the function is called.

    :return: The result of the specified action.
    """
    logger.info('Event: %s', event)
    response = None

    try:
        logger.info(f"body: {event['body']}")
    except:
        logger.info("no body lol")

    try:
        result = predict_winner(event["body"]["player"], event["body"]["opponent"], event["body"]["data"], event["body"]["type"])
        response = util_functions.format_response(result, event["body"]["player"], event["body"]["opponent"], event["body"]["type"])
    except Exception as e:
        logger.info(f"Error: {e}")
        response = {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(e)
            }

    logger.info(f'Result: {response}')
    return json.dumps(response, default=str)

# # for testing
# if __name__ == '__main__':
#     ### DONNIANS OLIVEIRA - ~17 matches ###
#     donnians_olivera = "5F74B009-175F-4564-8C8E-7C57FDCF8D10"
#     ### LEE HYUN IL - 257 matches ###
#     lee_hyun_il = "0800FC8B-CBAB-4AC1-B6C7-F3D419906440"
#     ### LEE CHONG WEI - 410 matches ###
#     lee_chong_wei = "2E62073C-AD95-40BE-8364-0A2EC054A4AC"

#     response = requests.get(f"https://api.badminton-api.com/match/player?player_id={lee_chong_wei}&sort_desc=False")
#     response = response.json()
#     df = model_builders.build_dataframe(lee_hyun_il, response['data'], lee_chong_wei)
#     print(tabulate(df, headers = 'keys', tablefmt = 'psql'))

#     log_reg = model_trainers.train_log_reg_model(df)
#     print("Logistic Regression")
#     print(f"Accuracy: {log_reg['acc']} ({log_reg['acc']})")
#     print(f"Prediction: {log_reg['pred']}")
#     print(f"Probability: {log_reg['prob']}")

#     print()

#     sup_vec_class = model_trainers.train_sup_vec_class_model(df)
#     print("Support Vector Classification")
#     print(f"Accuracy: {sup_vec_class['acc']} ({sup_vec_class['acc']})")
#     print(f"Prediction: {sup_vec_class['pred']}")
#     print(f"Probability: {sup_vec_class['prob']}")
