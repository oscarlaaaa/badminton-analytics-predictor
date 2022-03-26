def format_response(model_results, player_id, opponent_id, model_type):
    return {
            "request": f"POST prediction of {player_id} vs {opponent_id} using {model_type}.",
            "status": "success",
            "status_code": 200,
            "data": model_results
            }