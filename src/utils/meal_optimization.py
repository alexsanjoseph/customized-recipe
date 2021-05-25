import pandas as pd
import numpy as np
import streamlit as st
def get_calorie_multiplier():
    calorie_multiplier = pd.Series({
        "calories": 1,
        "protein": 4,
        "fat": 9
    })
    return calorie_multiplier


def add_calories_from_fat_proteins(basket_nutrition):
    calorie_multiplier = get_calorie_multiplier()
    total_calories = sum(basket_nutrition * calorie_multiplier)
    basket_nutrition['calories'] =  total_calories

    return basket_nutrition
    

def optimize_meals(top_recipes, required_nutrition, nutrition_weightage, max_iter=2000):
    best_basket_score = 10000
    threshold = 0.2
    val_split = (0, 5, 10, 50, top_recipes.shape[0])

    for i in range(2000):
        basket_indices = list(np.random.randint(val_split[j - 1], val_split[j]) for j in range(1, len(val_split)))
        current_basket = top_recipes.iloc[basket_indices].loc[:, required_nutrition.keys()]
        # basket_nutrition = functools.reduce(lambda a, b: a+b, current_basket)
        basket_nutrition = current_basket.apply(sum, axis=0)
        basket_nutrition = add_calories_from_fat_proteins(basket_nutrition)

        adjustment = 1.05
        basket_nutrition_score = sum(nutrition_weightage * abs(1 - basket_nutrition/adjustment/required_nutrition))
        if best_basket_score > basket_nutrition_score:
            best_basket_score = basket_nutrition_score
            best_basket = current_basket
            best_basket_nutrition = basket_nutrition
            best_basket_indices = basket_indices
        if best_basket_score < threshold:
            break
    return best_basket_nutrition, best_basket_indices
