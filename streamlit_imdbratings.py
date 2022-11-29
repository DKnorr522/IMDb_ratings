import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st


def actors_to_list(actors_str):
    actors_stripped = actros_str[1:-1]
    actors_split = actors_stripped.split(', ')
    actors_list = [name[2:-1] for name in actors_split]
    return actors_list

# Load in data
url = "http://bit.ly/imdbratings"
movies = pd.read_csv(url)

# Convert actors names from string to list of strings
movies["actors_list"] = movies["actors_list"].apply(actors_to_list)

# Need to fix Elliot Page deadnaming
deadnames = {"Ellen Page": "Elliot Page"}
for i, row in movies.iterrows():
    for name in names.keys():
        if name in row["actors_list"]:
            index = row["actors_list"].index(name)
            movies.iloc[i]["actors_list"][index] = deadnames[name]

st.title("IMDb Movies")
st.header(f"Data taken from: {url}")

# Make "rating" a category
movies["content_rating"] = movies["content_rating"].astype("category")
movies["content_rating"].cat.set_categories(["APPROVED",
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
                                            ordered=True,
                                            inplace=True)
movies["genre"] = movies["genre"].astype("category") # Make "genre" a category

# Create a heat map showing relationship between rating and genre
heat = plt.figure()
heat_pivot = pd.pivot_table(movies,
                            values="star_rating",
                            index="genre",
                            columns="content_rating")
sns.heatmap(heat_pivot,
            cmap="Greens",
            annot=False)
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
    col_rate, col_ascend, col_count = st.columns([2, 1, 2])

    default_options = {"content_rating": 5,
                       "genre"         : 0}
    default_choice = default_options[choice]

    # Category choice
    cat_choice = col_rate.selectbox("Select rating",
                                    options=list(movies[choice].unique()),
                                     index=default_choice)

    order = col_ascend.radio("List order",
                             options=["Highest", "Lowest"])

    col_count.write(f"Number of {cat_choice} movies: {movies[movies[choice]==cat_choice]['title'].count()}")

    ascend = True if order == "Lowest" else False
    st.table(movies[movies[choice] == cat_choice]
             .drop(choice, axis=1)
             .sort_values("star_rating",
                          ascending=ascend)
             )
