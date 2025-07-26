import pandas as pd
import numpy as np
import requests
from flask import Flask, render_template, request, jsonify
import pickle

app = Flask(__name__)

# Load your model, scaler, and multi-label binarizer
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

with open('mlb.pkl', 'rb') as f:
    mlb = pickle.load(f)

# Load movies data
movies_data = pd.read_csv('Movies.csv')
movies_data['runtime'] = movies_data['runtime_hour'] * 60 + movies_data['runtime_min']
movies_data = movies_data.drop(columns=['id', 'runtime_hour', 'runtime_min'])
movies_data['release_year'] = pd.to_datetime(movies_data['release_date']).dt.year
movies_data = movies_data.drop(columns=['release_date'])
movies_data['genres'] = movies_data['genres'].str.split(', ')
genres_encoded = mlb.transform(movies_data['genres'])
genres_df = pd.DataFrame(genres_encoded, columns=mlb.classes_)
movies_cleaned = pd.concat([movies_data, genres_df], axis=1)

X = movies_cleaned.drop(columns=['title', 'language', 'user_score', 'release_year'])
y = movies_cleaned['user_score']
X = X.select_dtypes(include=[np.number])

# TMDb API Key and Base URL
TMDB_API_KEY = 'd42dce24f3a7d10a51442d710625251e'  # Your TMDb API key here
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    input_genres = data['genres']
    
    if not input_genres or not all(isinstance(genre, str) for genre in input_genres):
        return jsonify({'error': 'Invalid genre input.'})
    
    input_encoded = pd.DataFrame([0] * len(mlb.classes_), index=mlb.classes_).T
    for genre in input_genres:
        if genre in input_encoded.columns:
            input_encoded[genre] = 1

    default_features = {
        'vote_count': X['vote_count'].mean(),
        'runtime': X['runtime'].mean()
    }
    
    input_features = pd.DataFrame(default_features, index=[0])
    input_features = pd.concat([input_features, input_encoded], axis=1)

    input_features_scaled = pd.DataFrame(scaler.transform(input_features[X.columns]), columns=X.columns)
    
    predicted_score = model.predict(input_features_scaled).item()

    matching_movies = movies_cleaned[movies_cleaned['user_score'] >= predicted_score]
    
    if not matching_movies.empty:
        recommended_movie = matching_movies.sample(n=1, random_state=np.random.randint(0, 1000))
        recommended_movie_name = recommended_movie['title'].iloc[0]
        recommended_movie_year = recommended_movie['release_year'].iloc[0]
        recommended_movie_score = recommended_movie['user_score'].iloc[0]

        print(f"Recommended Movie: {recommended_movie_name}")
        print(f"Release Year: {recommended_movie_year}")
        print(f"Movie Score: {recommended_movie_score}")
        
        # Fetch poster URL from TMDb API
        poster_url = get_movie_poster(recommended_movie_name)
        
        print(f"Poster URL: {poster_url}")  # Print the fetched poster URL
        
        return jsonify({
            'title': recommended_movie_name,
            'release_year': int(recommended_movie_year),
            'rating': float(recommended_movie_score),
            'poster_url': poster_url  # Use the fetched poster URL
        })
    else:
        return jsonify({'error': 'No matching movie found.'})

def get_movie_poster(movie_name):
    # Search for the movie on TMDb and fetch the poster URL
    search_url = f'{TMDB_BASE_URL}/search/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'query': movie_name,
        'language': 'en-US'
    }
    response = requests.get(search_url, params=params)
    
    print(f"Requesting TMDb for: {movie_name}")  # Print the movie name being searched
    
    data = response.json()
    
    print(f"TMDb Response: {data}")  # Print the raw API response for debugging

    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
            print(f"Poster Path: {poster_path}")
            return poster_url  # Return full poster URL
    return ''  # Return empty if no poster found

if __name__ == '__main__':
    app.run(debug=True)

# you yeah 