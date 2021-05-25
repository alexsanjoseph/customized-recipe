import pandas as pd
import numpy as np
import recmetrics

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder



recipe_data = pd.read_csv('../datasets/epirecipes/user_profile.csv')
test_user_data = pd.read_csv('../datasets/epirecipes/test_useers.csv')

catalog = recipe_data.loc[:, 'recipeTitle'].unique().tolist()

le = LabelEncoder()
recipe_data['gender'] = le.fit_transform(recipe_data['gender'])
recipe_data['goal'] = le.fit_transform(recipe_data['goal'])
recipe_data['userId'] = le.fit_transform(recipe_data['userId'])


test_user_data['gender'] = le.fit_transform(test_user_data['gender'])
test_user_data['goal'] = le.fit_transform(test_user_data['goal'])


def find_recommendation(usserId, age, ggndeer, goall):

    test_user = pd.DataFrame(
    {'userId': usserId,
     'age': age,
     'gender': ggndeer,
     'goal': goall}, index=[0])

    top_10_similar_users_indices = np.argsort(-cosine_similarity(test_user.loc[:, ['age', 'gender','goal']],
                                                             recipe_data.loc[:, ['age', 'gender','goal']])[0])[:10]
    f_l = list()
    print(top_10_similar_users_indices)
    for i in top_10_similar_users_indices:
        if(recipe_data.loc[i,:].rating>=3):
            #print(recipe_data.loc[i,'recipeTitle'])
            f_l.append(recipe_data.loc[i,'recipeTitle'])

    return f_l[:5]


res_diict = dict()
resllist = list()
for index, row in test_user_data.iterrows():
    recommmendationlist = find_recommendation(row['userId'], row['age'], row['gender'], row['goal'])
    res_diict[row['userId']] = recommmendationlist
    resllist.append(recommmendationlist)

print(resllist)

length = max(map(len, resllist))
y=np.array([xi+['']*(length-len(xi)) for xi in resllist])


onehot_encoder = OneHotEncoder(handle_unknown='ignore')
onehot_encoder.fit(y)
onehotlabels = onehot_encoder.transform(y).toarray()

ssimilarity_array= cosine_similarity(onehotlabels)

ssimilarity_array_numpy_arr = np.matrix(ssimilarity_array)

upper_diagoonal = np.triu(ssimilarity_array_numpy_arr, 1)
upper_diagoonal_indiices = np.triu_indices_from(ssimilarity_array_numpy_arr, 1)

print(upper_diagoonal)

ltri = np.tril(ssimilarity_array_numpy_arr, -1)
ltri = ltri[np.nonzero(ltri)]


print("presonalization score: " + str(recmetrics.personalization(y)))