import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np


def actors_to_list(actors_str):
    actors_stripped = actors_str[1:-1]
    actors_split = actors_stripped.split(', ')
    actors_list = [name[2:-1] for name in actors_split]
    return actors_list

# Load in data
url = "http://bit.ly/imdbratings"
movies = pd.read_csv(url)

# Convert actors names from string to list of strings
movies["actors_list"] = movies["actors_list"].apply(actors_to_list)

# Remove NaN values from content_rating
ratings = movies['content_rating'].unique()
for rating in ratings:
    st.write(f"{rating = }\t{type(rating) = }")
    st.write(np.nan(rating))
movies['content_rating'] = movies['content_rating'].replace(to_replace=float('nan'),
                                                            value='NONE')

# Need to fix Elliot Page deadnaming
deadnames = {"Ellen Page": "Elliot Page"}
for i, row in movies.iterrows():
    for name in deadnames.keys():
        if name in row["actors_list"]:
            index = row["actors_list"].index(name)
            movies.iloc[i]["actors_list"][index] = deadnames[name]

st.title("IMDb Movies")
st.header(f"Data taken from: {url}")

# Make "rating" a category
movies["content_rating"] = movies["content_rating"].astype("category")
movies["content_rating"] = movies["content_rating"].cat.set_categories(["APPROVED",
                                                                        "PASSED",
                                                                        "NOT RATED",
                                                                        "G",
                                                                        "GP",
                                                                        "PG",
                                                                        "PG-13",
                                                                        "TV-MA",
                                                                        "R",
                                                                        "NC-17",
                                                                        "X"
                                                                        ],
                                                                       ordered=True)
movies["genre"] = movies["genre"].astype("category") # Make "genre" a category

# Create a heat map showing relationship between genre and either rating or duration
with st.container():
    heat_values = st.radio("Select which data to see",
                      options=["star_rating",
                               "duration"])
    heat = plt.figure()
    heat_pivot = pd.pivot_table(movies,
                                values=heat_values,
                                index="genre",
                                columns="content_rating")
    sns.heatmap(heat_pivot,
                cmap="Greens",
                annot=False)
    plt.title(f"Heatmap of {heat_values} by Genre and Content Rating")
    st.pyplot(heat)


# Want to expand this to show a plot
with st.expander("Movie categories average rating"):
    st.table(movies.groupby("content_rating")["star_rating"].mean())


box_choices = {"Rating": "content_rating",
               "Genre" : "genre"
               }
box_choice = st.radio("Choose",
                      options=box_choices.keys())
choice = box_choices[box_choice]

movies = movies.sort_values(choice)


box = plt.figure()
sns.boxplot(data=movies,
            x="star_rating",
            y=choice)
st.pyplot(box)


with st.expander("Category top rated movies",
                 expanded=True):
    # Columns
    col_rate, col_count, col_ascend, col_sort = st.columns([4, 5, 2, 4])

    default_options = {"content_rating": 5,
                       "genre"         : 0}
    default_choice = default_options[choice]

    # Category choice
    cat_choice = col_rate.selectbox("Select rating",
                                    options=list(movies[choice].unique()),
                                     index=default_choice)

    movie_count = int(movies[movies[choice]==cat_choice]['title'].count())
    col_count.write(f"Number of {cat_choice} movies: {movie_count}")
    num_movies = col_count.slider("Number of movies to show",
                                  min_value=0,
                                  max_value=movie_count,
                                  value=movie_count,
                                  step=1)

    order = col_ascend.radio("List order",
                             options=["Highest", "Lowest"])
    ascend = True if order == "Lowest" else False

    sort_options = list(movies.columns[:5])
    sort_options.remove(choice)
    sort_col = col_sort.selectbox("Sort by:",
                                  options=sort_options)

    st.table(movies[movies[choice] == cat_choice]
             .drop(choice, axis=1)
             .head(num_movies)
             .sort_values(sort_col,
                          ascending=ascend)
             )
