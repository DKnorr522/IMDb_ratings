import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

movies = pd.read_csv("http://bit.ly/imdbratings")

st.title("IMDb Movies")

with st.expander("movies.head()"):
    st.table(movies.head())

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
movies["genre"] = movies["genre"].astype("category")

heat = plt.figure()
heat_pivot = pd.pivot_table(movies,
                            values="star_rating",
                            index="genre",
                            columns="content_rating")
sns.heatmap(heat_pivot,
            cmap="Greens",
            annot=False)
st.pyplot(heat)

with st.expander("Movie categories average rating"):
    st.table(movies.groupby("content_rating")["star_rating"].mean())

##movies = movies.sort_values("content_rating")

box_choices = {"Rating" : "content_rating",
               "Genre"  : "genre"
               }
box_choice = st.radio("Choose",
                      options=box_choices.keys())
choice = box_choices[box_choice]
movies = movies.sort_values(choice)


box = plt.figure()
sns.boxplot(data=movies,
            x="star_rating",
            y=choice
            )
st.pyplot(box)


with st.expander("Category top rated movies",
                 expanded=True):
    col_rate, col_ascend, col_count = st.columns([2, 1, 2])
    cat_choice = col_rate.selectbox("Select rating",
                                    options=list(movies[choice].unique())
                                    )
    order = col_ascend.radio("List order",
                              options=["Highest", "Lowest"])
    col_count.write(f"Number of {cat_choice} movies: {movies[movies[choice]==cat_choice]['title'].count()}")
    ascend = True if order == "Lowest" else False
    st.table(movies[movies[choice]==cat_choice]
             .drop(choice, axis=1)
             .sort_values("star_rating",
                          ascending=ascend)
             )
