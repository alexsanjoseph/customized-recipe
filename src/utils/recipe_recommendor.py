import elasticsearch
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import numpy as np
import random
from es import connect_to_es

INDEX_NAME = 'user-rating-index'

def get_es_queries():
    doc = {
        'size': 10000,
        'query': {
            'match_all': {}
        }
    }
    return connect_to_es().search(index=INDEX_NAME, doc_type='_doc', body=doc, scroll='5m')


def user_similar_recipies(userId='abcd', age=25, gender='male', goal='body building'):
    le = LabelEncoder()

    test_user = pd.DataFrame(
        {'userId': userId,
         'age': age,
         'gender': gender,
         'goal': goal}, index=[0])
    test_user['gender'] = le.fit_transform(test_user['gender'])
    test_user['goal'] = le.fit_transform(test_user['goal'])
    test_user['userId'] = le.fit_transform(test_user['userId'])

    es_top_recipes = get_es_queries()
    data = pd.DataFrame([x['_source'] for x in es_top_recipes['hits']['hits']])

    data['gender']= le.fit_transform(data['gender'])
    data['goal']= le.fit_transform(data['goal'])
    data['userId']= le.fit_transform(data['userId'])

    top_10_similar_users_indices = np.argsort(
        -cosine_similarity(test_user.loc[:, ['age', 'gender', 'goal']], data.loc[:, ['age', 'gender', 'goal']])[0])[:10]

    recommendr_recipe = list()
    for i in top_10_similar_users_indices:
        if (int(data.loc[i, :].rating) >= 3):
            recommendr_recipe.append(data.loc[i, 'recipeTitle'])

    return recommendr_recipe[:5]


def update_db_with_user_feedback(userId='abcd2', age=25, gender='male', goal='body building', rating=2, recipeTitle="xyx"):
    randomint = random.randint(0, 100000)
    e1 = {
        "userId": userId,
        "age": age,
        "gender": gender,
        "goal": goal,
        "rating": rating,
        "recipeTitle": recipeTitle,
        "etc": randomint,
    }
    res = connect_to_es().index(index=INDEX_NAME, body=e1)

#update_db_with_user_feedback('abcdaaaa',19,'female','weight loss', 1, "xyz recipe")
