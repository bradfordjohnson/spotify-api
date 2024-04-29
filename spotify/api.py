import base64
import requests


class SongAPI:
    def __init__(self, api):
        self.api = api
    
    def get_song(self, song_id):
        response = self.api.get(
            f"https://api.spotify.com/v1/tracks/{song_id}", headers=self.api.get_auth_header()
        )
        return response.json()

class API:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.song_api = SongAPI(self)

    def get(self, url, headers):
        return requests.get(url, headers=headers)
    
    def get_auth_header(self):
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")

        auth_options = {
            "url": "https://accounts.spotify.com/api/token",
            "headers": {"Authorization": f"Basic {auth_header}"},
            "data": {"grant_type": "client_credentials"},
        }

        response = requests.post(**auth_options)

        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            return headers
        else:
            RuntimeError("Failed to get token")

## Usage example for development
client_id = "x"
client_secret = "x"

api = API(client_id, client_secret)
song_api = SongAPI(api)
song_data = song_api.get_song("5e90dsXJMBw9ndBRiKP1ZA")
print(song_data)

