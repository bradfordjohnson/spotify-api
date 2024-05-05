import base64
import requests


class SpotifyAPI:
    BASE_URL = "https://api.spotify.com"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._auth_header = None

    @property
    def auth_header(self):
        if self._auth_header is None:
            self._auth_header = self._get_auth_header()
        return self._auth_header

    def _get_auth_header(self):
        auth_str = f"{self.client_id}:{self.client_secret}"
        auth_str_b64 = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
        headers = {"Authorization": f"Basic {auth_str_b64}"}
        data = {"grant_type": "client_credentials"}
        response = requests.post(
            "https://accounts.spotify.com/api/token", headers=headers, data=data
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def get(self, endpoint, params=None):
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self.auth_header, params=params)
        response.raise_for_status()
        return response.json()


class TracksAPI:
    MAX_TRACK_IDS_PER_REQUEST = 100

    def __init__(self, api):
        self.api = api

    def get_track(self, track_id, market=None):
        try:
            endpoint = f"v1/tracks/{track_id}"
            params = {"market": market} if market else None
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            print(f"Failed to get song: {e.response.status_code}")
            return None

    def get_tracks(self, track_ids, market=None):
        try:
            if len(track_ids) > self.MAX_TRACK_IDS_PER_REQUEST:
                raise ValueError("Exceeded maximum track IDs per request")

            endpoint = "v1/tracks"
            params = {"ids": ",".join(track_ids)}
            if market:
                params["market"] = market
            return self.api.get(endpoint, params=params)
        except ValueError as ve:
            print(ve)
            return None
        except requests.HTTPError as e:
            print(f"Failed to get songs: {e.response.status_code}")
            return None

    def get_track_audio_features(self, track_id):
        try:
            endpoint = f"v1/audio-features/{track_id}"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            print(f"Failed to get audio features: {e.response.status_code}")
            return None

    def get_tracks_audio_features(self, track_ids):
        try:
            if len(track_ids) > self.MAX_TRACK_IDS_PER_REQUEST:
                raise ValueError("Exceeded maximum track IDs per request")

            endpoint = "v1/audio-features"
            params = {"ids": ",".join(track_ids)}
            return self.api.get(endpoint, params=params)
        except ValueError as ve:
            print(ve)
            return None
        except requests.HTTPError as e:
            print(f"Failed to get audio features: {e.response.status_code}")
            return None

    def get_track_audio_analysis(self, track_id):
        try:
            endpoint = f"v1/audio-analysis/{track_id}"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            print(f"Failed to get audio analysis: {e.response.status_code}")
            return None

    def get_recommendations(
        self, seed_artists, seed_genres, seed_tracks, limit=20, market=None, **kwargs
    ):
        try:
            endpoint = "v1/recommendations"
            params = {
                "limit": limit,
                "seed_artists": seed_artists,
                "seed_genres": seed_genres,
                "seed_tracks": seed_tracks,
            }
            if market:
                params["market"] = market
            params.update(kwargs)
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            print(f"Failed to get recommendations: {e.response.status_code}")
            return None

    def get_recommendation_genres(self):
        try:
            endpoint = "v1/recommendations/available-genre-seeds"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            print(f"Failed to get recommendation genres: {e.response.status_code}")
            return None
