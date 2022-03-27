import json

def format_response(model_results, player_id, opponent_id, model_type):
    return {
            "request": f"POST prediction of {player_id} vs {opponent_id} using {model_type}.",
            "status": "success",
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(model_results)
            }