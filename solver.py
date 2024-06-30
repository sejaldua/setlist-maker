from pulp import *
import pandas as pd
from pprint import pprint
from spotipy_token import authenticate

sp = authenticate()

discography = pd.read_csv('discography_cleaned.csv')
discography['duration_mins'] = discography['duration_ms'].apply(lambda x: x / 60000)
uri_dict = discography.set_index('uri').to_dict(orient='index')
num_songs = round(120 / discography['duration_mins'].mean())

URIS = discography['uri']
ORDER = list(range(num_songs + 1))
# pprint(uri_dict)

# Define Problem  

prob = LpProblem("Matrix Problem",LpMaximize)
# Creating a Set of Variables
# date, source, desetination
choices = LpVariable.dicts("Track",(URIS, ORDER), cat='Binary')

# Added arbitrary objective function
prob += 0, "Arbitrary Objective Function"

# ---------------- CONSTRAINTS ------------------------

prob += lpSum([choices[t][o] * uri_dict[t]['duration_mins'] for t in URIS for o in ORDER]) >= 90
prob += lpSum([choices[t][o] * uri_dict[t]['duration_mins'] for t in URIS for o in ORDER]) <= 150
prob += lpSum([choices[t][o] * uri_dict[t]['popularity'] for t in URIS for o in ORDER])
prob += lpSum([choices[t][o] * 0.25 * uri_dict[t]['tempo'] for t in URIS for o in ORDER])

for o in ORDER:
    prob += lpSum([choices[t][o] for t in URIS]) == 1

    prob += lpSum([choices[t][o] * 3 * uri_dict[t]['popularity'] for t in URIS for o in ORDER[:3]])
    prob += lpSum([choices[t][o] * 2 * uri_dict[t]['popularity'] for t in URIS for o in ORDER[-3:]])

    # make the top three songs high popularity
    if o in ORDER[:3]:
        prob += lpSum([choices[t][o] for t in URIS if t not in list(discography.sort_values(by='popularity', ascending=False)['uri'].head(10))]) == 0

    # make the middle of the concert lower energy for an outfit change / water break
    if o in [(max(ORDER) // 2) - 1, max(ORDER) // 2]:
        prob += lpSum([choices[t][o] for t in URIS if t not in list(discography.sort_values(by=['speechiness', 'instrumentalness'], ascending=[True, False])['uri'].head(10))]) == 0

    # make the last 3 songs all top 10 most popular songs
    if o in ORDER[-2:]:
        prob += lpSum([choices[t][o] for t in URIS if t not in list(discography.sort_values(by='popularity', ascending=False)['uri'].head(10))]) == 0

    # make the encore song one of the most three popular songs
    if o == len(ORDER) - 1:
        most_popular = list(discography.sort_values(by='popularity', ascending=False)['uri'].head(3))
        print(most_popular)
        prob += lpSum([choices[t][o] for t in most_popular]) == 1



for t in URIS:
    prob += lpSum([choices[t][o] for o in ORDER]) <= 1

    # if t in list(discography.sort_values(by='popularity', ascending=False)['uri'].head(10)):
    #     prob += lpSum([choices[t][o] for o in ORDER ]) == 1

# Prevent three consecutive setlist items from being in the same album
for o in ORDER[:-2]:  # No need to check the last two positions
    for t1 in URIS:
        for t2 in URIS:
            for t3 in URIS:
                if (t1 != t2 and t2 != t3 and t1 != t3 and 
                    uri_dict[t1]['album_name'] == uri_dict[t2]['album_name'] == uri_dict[t3]['album_name']):
                    prob += choices[t1][o] + choices[t2][o + 1] + choices[t3][o + 2] <= 2


# The problem is solved using PuLP's choice of Solver
prob.solve()

print("Status:", LpStatus[prob.status])

# Print out the solution
debug = ""
print("\nMatrix Solution")
if LpStatus[prob.status] == 'Optimal':
    print('solved problem')
    setlist = []
    uris = []
    for o in ORDER:
        for t in URIS:
            if choices[t][o].varValue == 1:
                uris.append(t)
                setlist.append(uri_dict[t]['name'])
                print(uri_dict[t]['name'])
        
    print(setlist)
    sp.playlist_add_items('3tPmfTkbrp3XtjqMZktFvF', uris)

else:
    print('Problem is infeasible')


