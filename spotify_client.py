import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.exceptions
import random

# --- IMPORTANT: Paste your keys here ---
CLIENT_ID = "6c11a61edadf44a583c87cdb1e0bcf08"
CLIENT_SECRET = "6840138da4434a92835c4c7dd430815c"
# ---------------------------------------

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

def fetch_track_data(query: str):
    """Searches Spotify for a track and returns its audio features and album art."""
    print(f"Searching Spotify for: '{query}'...")
    
    try:
        # 1. Search for the track
        results = sp.search(q=query, type='track', limit=1)
        
        if not results['tracks']['items']:
            print("Track not found.")
            return None
            
        track = results['tracks']['items'][0]
        track_id = track['id']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        
        image_url = track['album']['images'][0]['url'] if track['album']['images'] else None

        # 2. Get the Audio Features
        features = sp.audio_features(track_id)[0]
        
        if not features:
            print("No audio features available for this track.")
            return None

        # 3. Format the data
        return {
            "track_id": track_id,
            "track_name": f"{track_name} by {artist_name}",
            "image_url": image_url,
            "danceability": features['danceability'],
            "energy": features['energy'],
            "key": features['key'],
            "loudness": features['loudness'],
            "mode": features['mode'],
            "speechiness": features['speechiness'],
            "acousticness": features['acousticness'],
            "instrumentalness": features['instrumentalness'],
            "liveness": features['liveness'],
            "valence": features['valence'],
            "tempo": features['tempo']
        }
        
    except spotipy.exceptions.SpotifyException as e:
        # Catch the Premium Paywall Error (403)
        if e.http_status == 403:
            print("\n[!] SPOTIFY PREMIUM REQUIRED: API blocked the request.")
            print("[!] Generating randomized mock audio features for testing...\n")
            
            # Seed the randomizer with the query so the same song always gets the same mock vibe
            random.seed(query)
            
            return {
                "track_id": f"mock_{random.randint(1000,9999)}",
                "track_name": f"{query} (Mocked Data)",
                "image_url": "https://placehold.co/150x150/18181f/1db954?text=Mock+API",
                "danceability": round(random.uniform(0.1, 0.9), 3),
                "energy": round(random.uniform(0.1, 0.9), 3),
                "key": random.randint(0, 11),
                "loudness": round(random.uniform(-15.0, -2.0), 3),
                "mode": random.choice([0, 1]),
                "speechiness": round(random.uniform(0.03, 0.3), 3),
                "acousticness": round(random.uniform(0.0, 0.9), 3),
                "instrumentalness": round(random.uniform(0.0, 0.8), 3),
                "liveness": round(random.uniform(0.05, 0.3), 3),
                "valence": round(random.uniform(0.1, 0.9), 3),
                "tempo": round(random.uniform(70.0, 180.0), 3)
            }
        else:
            raise e