import streamlit as st
import pickle
import pandas as pd
import requests
import numpy as np


# ---------------------------------------------------------
# Fetch poster from TMDB API
# Using cache so repeated API calls don't slow the app
# ---------------------------------------------------------
@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=ed69400ec370b4e253f4f81049cbed7a&language=en-US"
    
    response = requests.get(url)

    # If API fails, return placeholder image
    if response.status_code != 200:
        return "https://via.placeholder.com/500x750?text=No+Image"

    data = response.json()

    # If poster exists, return full poster URL
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"


# ---------------------------------------------------------
# Recommendation Function (Optimized)
# Uses NumPy argsort (faster than Python sorted)
# Time Complexity ≈ O(n)
# ---------------------------------------------------------
def recommend(movie_name):

    if movie_name not in movies['title'].values:
        return ["Movie not found"], []

    # Get index of selected movie
    movie_index = movies[movies['title'] == movie_name].index[0]

    # Get similarity scores of that movie
    distances = similarity[movie_index]

    # Get top 5 similar movies (excluding itself)
    # argsort sorts indices, not values
    top_indices = np.argsort(distances)[-6:-1][::-1]

    recommended_movies = []
    recommended_movies_poster = []

    for idx in top_indices:
        movie_id = movies.iloc[idx].movie_id
        recommended_movies.append(movies.iloc[idx].title)
        recommended_movies_poster.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_poster


# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------
st.title('Movie Recommender System')

option = st.selectbox(
    "Select a Movie",
    movies['title'].values
)

st.write("You selected:", option)


# ---------------------------------------------------------
# Button Action
# ---------------------------------------------------------
if st.button("Recommend"):

    names, posters = recommend(option)

    # Create 5 columns dynamically
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
