import pandas as pd


def get_current_reg_produce(area):
    reg_prod = pd.read_csv("src/resources/regionwise_produce.csv")
    
    curr_reg_prod = reg_prod \
        .query("Area==@area") \
        .drop(['Item', 'Value'], axis = 1) \
        .iloc[0]
    print(curr_reg_prod)
    return curr_reg_prod
