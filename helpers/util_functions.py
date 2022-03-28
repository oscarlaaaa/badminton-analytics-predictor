import json

def format_response(model_results, player_id, opponent_id, model_type):
    return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(model_results)
            }