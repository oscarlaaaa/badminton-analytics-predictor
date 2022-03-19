import requests
from tabulate import tabulate

import helpers.model_trainers as trainer
import helpers.model_builders as builder

def lambda_handler(event, context):   
    return "Hello world"

if __name__ == '__main__':
    ### DONNIANS OLIVEIRA - ~17 matches ###
    donnians_olivera = "5F74B009-175F-4564-8C8E-7C57FDCF8D10"
    ### LEE HYUN IL - 257 matches ###
    lee_hyun_il = "0800FC8B-CBAB-4AC1-B6C7-F3D419906440"

    response = requests.get(f"https://api.badminton-api.com/match/player?player_id={donnians_olivera}&sort_desc=False")
    response = response.json()
    df = builder.build_dataframe(donnians_olivera, response['data'], lee_hyun_il)
    print(tabulate(df, headers = 'keys', tablefmt = 'psql'))
    # lin_reg = trainer.train_lin_reg_model(df)
    # log_reg = trainer.train_log_reg_model(df)
    # sup_vec_class = trainer.train_sup_vec_class_model(df)
    # print(tabulate(results, headers = 'keys', tablefmt = 'psql'))
