from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles  
from pydantic import BaseModel
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

from spotify_client import fetch_track_data

app = FastAPI(title="Echoes API - Live Spotify Engine")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

try:
    scaler = joblib.load("models/audio_scaler.pkl")
    scaled_features = joblib.load("models/scaled_features.pkl")
    track_metadata = pd.read_pickle("models/track_metadata.pkl")
except Exception as e:
    print(f"Error loading models: {e}")

class AudioFeatures(BaseModel):
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float

@app.get("/")
def serve_ui():
    return FileResponse("index.html")

FEATURE_NAMES = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 
                 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

@app.post("/recommend/content")
def recommend_by_features(features: AudioFeatures, top_n: int = 4):
    input_features = np.array([[
        features.danceability, features.energy, features.key, features.loudness,
        features.mode, features.speechiness, features.acousticness,
        features.instrumentalness, features.liveness, features.valence, features.tempo
    ]])
    
    input_df = pd.DataFrame(input_features, columns=FEATURE_NAMES)
    input_scaled = scaler.transform(input_df)
    
    similarities = cosine_similarity(input_scaled, scaled_features)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    recommendations = []
    for idx in top_indices:
        recommendations.append({
            "track_id": str(track_metadata.iloc[idx]['track_id']),
            "track_name": str(track_metadata.iloc[idx]['track_name']),
            "image_url": str(track_metadata.iloc[idx]['image_url']),
            "similarity_score": round(float(similarities[idx]) * 100, 1)
        })
    return {"status": "success", "recommendations": recommendations}


@app.get("/recommend/spotify/{query}")
def recommend_from_spotify(query: str, top_n: int = 4):
    try:
        spotify_data = fetch_track_data(query)
    except Exception as e:
        print(f"Spotify API Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Spotify. Check your API keys in the backend terminal.")

    if not spotify_data:
        raise HTTPException(status_code=404, detail="Track not found on Spotify")

    live_features = np.array([[
        spotify_data['danceability'], spotify_data['energy'], spotify_data['key'],
        spotify_data['loudness'], spotify_data['mode'], spotify_data['speechiness'],
        spotify_data['acousticness'], spotify_data['instrumentalness'],
        spotify_data['liveness'], spotify_data['valence'], spotify_data['tempo']
    ]])
    
    input_df = pd.DataFrame(live_features, columns=FEATURE_NAMES)
    input_scaled = scaler.transform(input_df)
    
    similarities = cosine_similarity(input_scaled, scaled_features)[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    similar_tracks = []
    for idx in top_indices:
        track = track_metadata.iloc[idx]
        similar_tracks.append({
            "track_id": str(track['track_id']),
            "track_name": str(track['track_name']),
            "image_url": str(track['image_url']),
            "similarity_score": round(float(similarities[idx]) * 100, 1)
        })
        
    return {
        "searched_track": {
            "track_id": spotify_data['track_id'],
            "track_name": spotify_data['track_name'],
            "image_url": spotify_data['image_url']
        },
        "similar_tracks": similar_tracks
    }
