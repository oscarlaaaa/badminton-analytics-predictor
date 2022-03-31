import json

def format_response(model_results, player_id, opponent_id, model_type):
    return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": str(
                { 
                    "player": player_id, 
                    "opponent": opponent_id, 
                    "type": model_type, 
                    "results": model_results
                })
            }