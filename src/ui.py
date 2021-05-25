
import numpy as np
import streamlit as st
import elasticsearch 
from es import *
import pandas as pd
import functools
from css import current_css
from utils.meal_optimization import *
from utils.required_nutrition import *
from plotnine import *
import uuid
from utils.recipe_recommendor import user_similar_recipies, update_db_with_user_feedback
from tempfile import NamedTemporaryFile
# import matplotlib
# matplotlib.use('TkAgg')

st.markdown(current_css, unsafe_allow_html=True)
INDEX_NAME = "recipes"
TEMP_FILE_NAME = 'temp_image_1.png'

st.title("Customized Recipe Finder!")

es = connect_to_es()
queries = get_es_queries()
es_top_cat = es.search(queries['get_common_terms'], index = INDEX_NAME)
top_categories = [x['key'] for x in es_top_cat['aggregations']['categories']['buckets']]
user_id = uuid.uuid4()
### Sidebar selections

st.sidebar.markdown("## Demographics")
user_age = st.sidebar.number_input('What is your age?', 1, 120, 20)
user_gender = st.sidebar.selectbox('What is your Gender?', ["Male", "Female"])

st.sidebar.markdown("## Goal")
nutritional_goal_options = ['Regular', "Weight Gain", "Weight Loss", "Body Building"]
nutritional_goal = st.sidebar.selectbox("Select your nutritional goal", nutritional_goal_options)

st.sidebar.markdown("## Preferences")
selected_categories = st.sidebar.multiselect('What are your favorite categories?', top_categories)
# unselected_categories = st.sidebar.multiselect('What are the things you hate?', top_categories)

st.sidebar.markdown("## Other Options")
is_vegan = st.sidebar.checkbox("Vegan Only")
is_vegetarian = st.sidebar.checkbox("Vegetarian Only")

allergy_options = ["Peanut", "Soy", "Treenut", "Diary", "Gluten"]
allergy_list = st.sidebar.multiselect("Mention if you have any allergies", allergy_options)

if len(selected_categories) == 0:  
    selected_categories = "*"
    # st.markdown('<style>p{color: red;}</style>', unsafe_allow_html=True)
    # "**Please select some categories!!!**"
    # raise st.ScriptRunner.StopException

# st.ScriptRunner.StopException

all_recipes_query = queries['match_all_recipes']
all_recipes_query['query']['bool']['must'][0]['query_string']['query'] = " ".join(selected_categories)

if is_vegan:
    all_recipes_query['query']['bool']['filter'].append(filter_by_category("Vegan"))
if is_vegetarian:
    all_recipes_query['query']['bool']['filter'].append(filter_by_category("Vegetarian"))

for allergy in allergy_list:
    all_recipes_query['query']['bool']['filter'].append(filter_by_category(allergy + " Free"))

es_top_recipes = es.search(all_recipes_query, index=INDEX_NAME)
top_recipes = pd.DataFrame([x['_source'] for x in es_top_recipes['hits']['hits']])

if len(top_recipes) < 100:
    "**Following constraints don't lead to any meaningful recipes. Please change the preferences and try again!!!**"
    raise st.ScriptRunner.StopException

required_nutrition = get_required_nutrition_dict(user_age, user_gender, nutritional_goal)

with st.spinner("Tailoring Recipe for your preferences..."):
    best_basket_nutrition, best_basket_indices = optimize_meals(top_recipes, required_nutrition, NUTRITION_WEIGHTAGE, 1000)
    recommended_recipe_list = user_similar_recipies(user_id, user_age, user_gender, nutritional_goal)
    best_basket_df = top_recipes.loc[best_basket_indices, ["title", "directions"]]
    df_best_recipe_titles = best_basket_df.loc[:, "title"]
    best_basket_df_plot = top_recipes.loc[best_basket_indices, ["title", "calories", "protein", "fat"]]
    st.markdown("## Selected Meal Plan")
    st.table(pd.DataFrame([required_nutrition, best_basket_nutrition], index=[
        "Recommended Requirement", "Nutritional Requirement of Plan"]).T)
    # st.table(best_basket_df)

    calorie_multiplier = get_calorie_multiplier()
    best_basket_df_plot_normalized = best_basket_df_plot.set_index('title').\
        apply(lambda x: add_calories_from_fat_proteins(x)/required_nutrition, axis=1)
    plot_data = best_basket_df_plot_normalized.unstack().reset_index().rename(columns={0: "value", "level_0": "key"})
    plot_output = (ggplot(plot_data, aes('key', 'value', fill='title')) + 
        geom_bar(position="stack", stat="identity") +
        ylab("Daily Nutritional Requirement") +
        xlab("Macronutrient") +
        geom_hline(yintercept = 1.0, linetype = 'dashed')
    )

    plot_output.save(TEMP_FILE_NAME)
    st.image(TEMP_FILE_NAME)
    
    st.markdown("## Recipes!")
    st.table(best_basket_df)

    st.markdown("## You may also like these recipes!")
    st.dataframe(pd.DataFrame(recommended_recipe_list, columns=['Recipe title']))

st.sidebar.markdown("## Feedback")
recipe_to_be_rated = st.sidebar.selectbox("Rate a recipe", df_best_recipe_titles.values.tolist())
rating_of_recipe = st.sidebar.slider("Rating", 0, 5, 1)
update_db_with_user_feedback(user_id, user_age, user_gender, nutritional_goal, rating_of_recipe, recipe_to_be_rated)
    # st.pyplot()
    # "Best Basket Score", best_basket_score
    # "Iteration Number", i
