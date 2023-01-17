import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st


# Code is run at:
# https://imdb-ratings.streamlit.app/


# The data has the actors for each movie as a single string
# This turns those strings into lists of strings for the names
def actors_to_list(actors_str):
    actors_stripped = actors_str[1:-1]
    actors_split = actors_stripped.split(', ')
    actors_list = [name[2:-1] for name in actors_split]
    return actors_list


# Loads the data, cleans it, and memoizes
@st.experimental_memo
def import_clean_data(url, deadnames):
    # Load data
    movies_data = pd.read_csv(url)

    # Turn strings of actors' names into lists
    movies_data["actors_list"] = movies_data["actors_list"].apply(actors_to_list)

    # Fix deadnames
    for i, row in movies_data.iterrows():
        for name in deadnames.keys():
            if name in row["actors_list"]:
                index = row["actors_list"].index(name)
                movies_data.iloc[i]["actors_list"][index] = deadnames[name]

    # Clean empty content_rating entries
    movies_data["content_rating"][pd.isna(movies_data["content_rating"])] = "NOT RATED"

    # Make "rating" a category
    movies_data["content_rating"] = movies_data["content_rating"].astype("category")
    movies_data["content_rating"] = movies_data["content_rating"].cat.set_categories(["APPROVED",
                                                                                      "PASSED",
                                                                                      "NOT RATED",
                                                                                      "UNRATED",
                                                                                      "G",
                                                                                      "GP",
                                                                                      "PG",
                                                                                      "PG-13",
                                                                                      "TV-MA",
                                                                                      "R",
                                                                                      "NC-17",
                                                                                      "X"],
                                                                                     ordered=True)

    # Make genre a category
    movies_data["genre"] = movies_data["genre"].astype("category")

    return movies_data


def clear_movies():
    import_clean_data.clear()


# Load in data
url = "http://bit.ly/imdbratings"
deadnames = {"Ellen Page": "Elliot Page"}
movies = import_clean_data(url, deadnames)


# Header at the top of the page
st.title("IMDb Movies")
st.header(f"Data used from: {url}")


# Create a heat map showing relationship between genre and either rating or duration
with st.container():
    # Category the heatmap will show the values for
    heat_values = st.radio("Select which data to see",
                           options=["star_rating",
                                    "duration"]
                           )
    heat = plt.figure()
    # Gather data for the heatmap
    heat_pivot = pd.pivot_table(movies,
                                values=heat_values,
                                index="genre",
                                columns="content_rating")
    heat_label = {"star_rating": "Rating",
                  "duration"   : "Duration (min)"}
    sns.heatmap(heat_pivot,
                cmap="Greens",
                cbar_kws={"label": heat_label[heat_values]},
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

    default_options = {"content_rating": 6,
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
                          ascending=ascend))

with st.expander("Search for actor",
                 expanded=True):
    actor = st.text_input("Enter actor name")
    st.table(movies[list(movies["actors_list"]).contains(actor)])
    movies_with_actor = movies[actor in movies["actors_list"]]
    st.table(movies_with_actor)


st.button("Reload data",
          on_click=clear_movies())
