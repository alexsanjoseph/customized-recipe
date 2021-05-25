import pandas as pd


def get_required_nutrition_dict(user_age, user_gender, nutritional_goal):
    nutritional_req = pd.read_csv("src/resources/nutritional_requirements.csv")
    
    # required_nutrition = pd.Series({
    #     "calories": 2000,
    #     "protein": 50,
    # })

    required_nutrition = nutritional_req \
        .query("gender==@user_gender") \
        .query("age > @user_age") \
        .drop(['gender', 'age'], axis = 1) \
        .iloc[0]
        
    if nutritional_goal == "Weight Gain":
        required_nutrition['calories'] = required_nutrition['calories'] * 1.5
    if nutritional_goal == "Weight Loss":
        required_nutrition['calories'] = required_nutrition['calories'] * 0.75
    if nutritional_goal == "Body Building":
        required_nutrition['protein'] = required_nutrition['protein'] * 2
                
    required_nutrition['fat'] = int(required_nutrition['calories']*0.3/9)
    return required_nutrition

NUTRITION_WEIGHTAGE = pd.Series({
    "calories": 3,
    "protein": 1,
    "fat": 1    
})

