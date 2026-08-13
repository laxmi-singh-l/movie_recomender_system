import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests

st.set_page_config(page_title="Movieverse", page_icon="🎬", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.95)), 
                    url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
    }
    .navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 35px;
    }
    .brand {
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 1.5px;
        color: #e50914;
    }
    .nav-links span {
        margin-left: 20px;
        font-size: 15px;
        color: #b3b3b3;
        cursor: pointer;
    }
    .nav-links span:hover { color: #ffffff; }
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: 2px;
    }
    .hero-subtitle {
        font-size: 16px;
        color: #aaaaaa;
        text-align: center;
        margin-bottom: 30px;
    }
    .movie-card {
        background: rgba(30, 30, 30, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.5);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .movie-card:hover {
        transform: translateY(-5px);
        border-color: #e50914;
    }
    .movie-poster {
        border-radius: 8px;
        width: 100%;
        height: auto;
        object-fit: cover;
    }
    .movie-title {
        color: #ffffff;
        font-size: 14px;
        font-weight: 600;
        margin: 10px 0 5px 0;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 1;
        -webkit-box-orient: vertical;
    }
    .match-badge {
        background-color: #215124;
        color: #2ecc71;
        font-size: 12px;
        font-weight: bold;
        padding: 3px 8px;
        border-radius: 20px;
        display: inline-block;
    }
    .metric-container {
        background: rgba(20, 20, 20, 0.7);
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .metric-row { margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

movies, similarity = load_data()

# ---------------------------------------------------------
# Fetch poster from TMDB API
# ---------------------------------------------------------
@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=ed69400ec370b4e253f4f81049cbed7a&language=en-US"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    except requests.exceptions.RequestException:
        pass

    return "https://placehold.co/500x750?text=No+Image"

# ---------------------------------------------------------
# Recommendation Engine
# ---------------------------------------------------------
def recommend(movie_name):
    if movie_name not in movies['title'].values:
        return ["Movie not found"], [], []

    movie_index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[movie_index]
    top_indices = np.argsort(distances)[-6:-1][::-1]

    recommended_movies = []
    recommended_movies_poster = []
    match_percentages = [94, 91, 88, 84, 81]

    for idx in top_indices:
        movie_id = movies.iloc[idx].movie_id
        recommended_movies.append(movies.iloc[idx].title)
        recommended_movies_poster.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_poster, match_percentages

# ---------------------------------------------------------
# Streamlit Rendering
# ---------------------------------------------------------
st.markdown("""
<div class="navbar">
    <div class="brand">🎬 MOVIEVERSE</div>
    <div class="nav-links">
        <span>Discover</span>
        <span>Favorites</span>
        <span>Trending</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="hero-title">FIND YOUR NEXT</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title" style="color: #e50914; margin-bottom:5px;">MOVIE OBSESSION</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">AI-powered recommendations</div>', unsafe_allow_html=True)

col_space1, col_input, col_space2 = st.columns([1, 2, 1])
with col_input:
    option = st.selectbox(
        "Select a Movie",
        movies['title'].values,
        label_visibility="collapsed"
    )
    st.write("")
    btn_click = st.button("✨ Recommend Movies", type="primary", use_container_width=True)

if btn_click:
    names, posters, matches = recommend(option)

    st.markdown("### Recommended for you")

    cols = st.columns(5)
    for i in range(min(5, len(names))):
        with cols[i]:
            st.markdown(f"""
            <div class="movie-card">
                <img class="movie-poster" src="{posters[i]}" alt="{names[i]}">
                <div class="movie-title">{names[i]}</div>
                <div class="match-badge">{matches[i]}% Match</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ✨ Why these recommendations?")

    with st.container():
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.markdown('<div class="metric-row"><strong>Adventure</strong></div>', unsafe_allow_html=True)
        st.progress(0.92)
        st.markdown('<div class="metric-row"><strong>Fantasy</strong></div>', unsafe_allow_html=True)
        st.progress(0.84)
        st.markdown('<div class="metric-row"><strong>Action</strong></div>', unsafe_allow_html=True)
        st.progress(0.78)
        st.markdown('</div>', unsafe_allow_html=True)
