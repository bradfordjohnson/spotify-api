# Spotify API

Building my own Spotify API Wrapper in Python because I want to learn how to build an API Wrapper. Will be using this wrapper in future projects for data analysis and visualization.

## Learning Objectives

- how to build an API Wrapper
- about different authentication methods
- get a deeper understanding of using classes in Python

## Documentation

[Spotify Developer Site](https://developer.spotify.com/)

Current features:

- Tracks
  - Get a track
  - Get multiple tracks
  - Get audio features for a track
  - Get audio features for multiple tracks
  - Get audio analysis for a track
- Genres
  - Get a list of available genres for recommendations
- Playlists
  - Get a playlist
  - Get playlists for a category
  - Get featured playlists
  - Get a playlist's cover image
- Artists
  - Get an artist
  - Get multiple artists
  - Get an artist's albums
  - Get an artist's top tracks
  - Get related artists
- Albums
  - Get an album
  - Get multiple albums
  - Get an album's tracks
  - Get new releases

## Usage Example

Get 5 new releases:

```python
from spotify_api import wrapper

api = SpotifyAPI("CLIENT_ID", "CLIENT_SECRET")
new_releases = AlbumsAPI(api).get_new_releases(limit=5)
print(new_releases)
```

Get a track:

```python
from spotify_api import wrapper

api = SpotifyAPI("CLIENT_ID", "CLIENT_SECRET")
track = TracksAPI(api).get_track("22ML0MuFKfw16WejbxsLOy")
print(track)
```
