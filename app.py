# import requests
# from tabulate import tabulate

from .helpers.model_trainers import train_log_reg_model, train_sup_vec_class_model
from .helpers.model_builders import build_dataframe
from .helpers.util_functions import format_response

import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def predict_winner(player_id, opponent_id, player_data, model_type):
    df = build_dataframe(player_id, player_data, opponent_id)
    
    if model_type == "logistic_regression":
        log_reg = train_log_reg_model(df)
        logger.info("Logistic Regression")
        logger.info(f"Accuracy: {log_reg['acc']} ({log_reg['acc']})")
        logger.info(f"Prediction: {log_reg['pred']}")
        return log_reg

    elif model_type == "support_vector_classification":
        sup_vec_class = train_sup_vec_class_model(df)
        logger.info("Support Vector Classification")
        logger.info(f"Accuracy: {sup_vec_class['acc']} ({sup_vec_class['acc']})")
        logger.info(f"Prediction: {sup_vec_class['pred']}")
        return sup_vec_class
        
    else:
        return "xd"

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

    try:
        result = predict_winner(event['player'], event['opponent'], event['data'], event['type'])
    except:
        result = {
            "request": f"POST prediction of {event['player']} vs {event['opponent']} using {event['type']}.",
            "status": "error",
            "status_code": 404,
            "data": None
            }

    logger.info(f'Result: {result["data"]}')

    response = format_response(result, event['player'], event['opponent'], event['type'])
    return response

## for testing
# if __name__ == '__main__':
#     ### DONNIANS OLIVEIRA - ~17 matches ###
#     donnians_olivera = "5F74B009-175F-4564-8C8E-7C57FDCF8D10"
#     ### LEE HYUN IL - 257 matches ###
#     lee_hyun_il = "0800FC8B-CBAB-4AC1-B6C7-F3D419906440"
#     ### LEE CHONG WEI - 410 matches ###
#     lee_chong_wei = "2E62073C-AD95-40BE-8364-0A2EC054A4AC"

#     response = requests.get(f"https://api.badminton-api.com/match/player?player_id={lee_chong_wei}&sort_desc=False")
#     response = response.json()
#     df = builder.build_dataframe(lee_chong_wei, response['data'], lee_hyun_il)
#     print(tabulate(df, headers = 'keys', tablefmt = 'psql'))

#     log_reg = trainer.train_log_reg_model(df)
#     print("Logistic Regression")
#     print(f"Accuracy: {log_reg['acc']} ({log_reg['acc']})")
#     print(f"Prediction: {log_reg['pred']}")

#     sup_vec_class = trainer.train_sup_vec_class_model(df)
#     print("Support Vector Classification")
#     print(f"Accuracy: {sup_vec_class['acc']} ({sup_vec_class['acc']})")
#     print(f"Prediction: {sup_vec_class['pred']}")
