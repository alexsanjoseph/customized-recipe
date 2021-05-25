
import numpy as np
import streamlit as st
import elasticsearch
from es import *
import pandas as pd
import functools
from css import current_css
from utils.meal_optimization import *
from utils.required_nutrition import *
from utils.regionwise_produce import *
from plotnine import *
import uuid
from utils.recipe_recommendor import user_similar_recipies, update_db_with_user_feedback
from tempfile import NamedTemporaryFile
# import matplotlib
# matplotlib.use('TkAgg')

st.markdown(current_css, unsafe_allow_html=True)
RECIPE_INDEX = "recipes"
CROP_INDEX = "regioncrops"
TEMP_FILE_NAME = 'temp_image_1.png'

st.title("Customized Recipe Finder!")

es = connect_to_es()
queries = get_es_queries()
es_top_cat = es.search(queries['get_common_terms'], index = RECIPE_INDEX)
top_categories = [x['key'] for x in es_top_cat['aggregations']['categories']['buckets']]
user_id = uuid.uuid4()
### Sidebar selections

es_top_cat_reg = es.search(queries['get_all_regions'], index = CROP_INDEX)
regions = [x['key'] for x in es_top_cat_reg['aggregations']['areas']['buckets']]

st.sidebar.markdown("## Demographics")
user_age = st.sidebar.number_input('What is your age?', 1, 120, 20)
user_gender = st.sidebar.selectbox('What is your Gender?', ["Male", "Female"])
user_area = st.sidebar.multiselect('What is your Region?', regions)
# Select your region 
 

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

# RECIPE QUERY ========================================================================================
all_recipes_query = queries['match_all_recipes']
all_recipes_query['query']['bool']['must'][0]['query_string']['query'] = " ".join(selected_categories)

if is_vegan:
    all_recipes_query['query']['bool']['filter'].append(filter_by_category("Vegan"))
if is_vegetarian:
    all_recipes_query['query']['bool']['filter'].append(filter_by_category("Vegetarian"))

for allergy in allergy_list:
    all_recipes_query['query']['bool']['filter'].append(filter_by_category(allergy + " Free"))

es_top_recipes = es.search(all_recipes_query, index=RECIPE_INDEX)
top_recipes = pd.DataFrame([x['_source'] for x in es_top_recipes['hits']['hits']])
#======================================================================================================
if len(top_recipes) < 100:
    "**Following constraints don't lead to any meaningful recipes. Please change the preferences and try again!!!**"
    raise st.ScriptRunner.StopException

required_nutrition = get_required_nutrition_dict(user_age, user_gender, nutritional_goal)

best_basket_nutrition, best_basket_indices = optimize_meals(top_recipes, required_nutrition, NUTRITION_WEIGHTAGE, 1000)
best_basket_df = top_recipes.loc[best_basket_indices, ["title", "calories", "protein", "fat"]]
recipe_details = top_recipes.loc[best_basket_indices, ["title", "ingredients", "directions"]]
def plotMealBreakDown():
    pass

def plotCaloriePlot():
    best_basket_df_plot = top_recipes.loc[best_basket_indices, ["title", "calories", "protein", "fat"]]
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
    return plot_output

def submitPreferredRecipes(pref):
    pass

def regionData():
    if len(user_area)!=0:
        all_region_data = queries["match_region_data"]
        st.markdown("## Regional Produce in Tonnes")  
        all_region_data['query']['bool']['filter'].append(filter_by_area(user_area[0]))
        matched_region = es.search(all_region_data, index=CROP_INDEX)
        matched_regions = pd.DataFrame([x['_source'] for x in matched_region['hits']['hits']])        
        randInt = np.random.choice(50,5,replace=False)
        myData = matched_regions.loc[[randInt[0],randInt[1],randInt[2],randInt[3],randInt[4]],["Item","Value"]]
        myData['Value'] = myData['Value'].apply(lambda x: float(x.split()[0].replace(',', '')))
        myData['Value'] = myData['Value'].astype(float)
        if st.checkbox("Raw Data", True):
            st.table(matched_regions.loc[[randInt[0],randInt[1],randInt[2],randInt[3],randInt[4]],["Item","Value"]])
        if st.checkbox("Bar Plot", True):
            regPlot = myData.plot(kind="bar",x="Item",y="Value",title="Regional Produce",legend=False,figsize=(8,8)).get_figure()
            regPlot.savefig(TEMP_FILE_NAME)
            st.image(TEMP_FILE_NAME)
        if st.checkbox("Bar Histogram Plot", True):
            regPlot = myData.plot(kind="barh",x="Item",y="Value",title="Regional Produce",legend=False,figsize=(10,5)).get_figure()
            regPlot.savefig(TEMP_FILE_NAME)
            st.image(TEMP_FILE_NAME)
        if st.checkbox("Pie Plot", True):
            pieDf = pd.DataFrame({"item":myData["Item"],"Value in tonnes":myData["Value"].tolist()},index=myData["Item"].tolist())
            regPlot = pieDf.plot(kind="pie",y="Value in tonnes",figsize=(5,5)).get_figure()
            regPlot.savefig(TEMP_FILE_NAME)
            st.image(TEMP_FILE_NAME)        
    else:
        st.write("Please enter your region on the left!")        

with st.spinner("Processing ......"):

    info_opt = st.selectbox("PLOT OPTIONS ",["Meal Plan Breakdown","Recipe List","Regional Produce"])

    if(info_opt == "Recipe List"):
        recommended_recipe_list = user_similar_recipies(user_id, user_age, user_gender, nutritional_goal)
        st.markdown("## Recipes List!")
        st.table(best_basket_df)
        st.markdown("## You may also like these recipes!")
        st.table(pd.DataFrame(recommended_recipe_list, columns=['Recipe title']))
        st.markdown("## Feedback")
        df_best_recipe_titles = best_basket_df.loc[:, "title"]
        recipe_to_be_rated = st.selectbox("Rate a recipe", df_best_recipe_titles.values.tolist())
        rating_of_recipe = st.slider("Rating", 0, 5, 1)
        if st.button("Submit Feedback"):
            update_db_with_user_feedback(user_id, user_age, user_gender, nutritional_goal, rating_of_recipe, recipe_to_be_rated)
        #if st.checkbox("Stacked Plot"):
        st.markdown("## Calorie Stacked Plot!")
        plot_output = plotCaloriePlot()
        plot_output.save(TEMP_FILE_NAME)
        st.image(TEMP_FILE_NAME)
        if st.checkbox("Recipe ingredients and direction", value=True):
            st.markdown("## Recipe Details!")
            st.table(recipe_details)
			

    if(info_opt == "Meal Plan Breakdown"):
        st.markdown("## Selected Meal Plan")    
        pdData = pd.DataFrame([required_nutrition, best_basket_nutrition], index=[
        "Recommended Requirement", "Nutritional Requirement of Plan"]).T
        st.table(pd.DataFrame([required_nutrition, best_basket_nutrition], index=[
            "Recommended Requirement", "Nutritional Requirement of Plan"]).T) 
        temp_data = required_nutrition
        temp_best = best_basket_nutrition
        temp_data["calories"] /=100
        temp_best["calories"] /= 100 
        if st.checkbox("Line Chart", value = True):
            pdDataLine = pd.DataFrame([temp_data,temp_best], index=[
                "Recommended Requirement", "Nutritional Requirement of Plan"]).T 
            st.line_chart(pdDataLine)
            st.write("NOTE: Calories count X100")
        if st.checkbox("Bar Chart", value=True):
            pdDataBar = pd.DataFrame([temp_data,temp_best], index=[
                "Recommended Requirement", "Nutritional Requirement of Plan"]).T 
            st.bar_chart(pdDataBar)
            st.write("NOTE: Calories count X100")    
    if(info_opt == "Regional Produce"):
        regionData()    

