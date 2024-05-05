import base64
import requests
from typing import Optional, Dict, List, Any


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

    def get_track(self, track_id: str, market: Optional[str] = None) -> Optional[Dict]:
        """Get information about a track from Spotify.

        Args:
            track_id (str): The ID of the track.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the track from. Defaults to None.

        Returns:
            Dict: A dictionary containing information about the track if successful, None otherwise.
        """
        try:
            endpoint = f"v1/tracks/{track_id}"
            params = {"market": market} if market else None
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            print(f"Failed to get song: {e.response.status_code}")
            return None

    def get_tracks(
        self, track_ids: List[str], market: Optional[str] = None
    ) -> Optional[Dict]:
        """Get information about multiple tracks from Spotify.

        Args:
            track_ids (List[str]): A list of track IDs.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the tracks from. Defaults to None.

        Raises:
            ValueError: If the number of track IDs exceeds the maximum allowed per request.

        Returns:
            Dict: A dictionary containing information about the tracks if successful, None otherwise.
        """
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

    def get_track_audio_features(self, track_id: str) -> Optional[Dict]:
        """Get audio features for a track from Spotify.

        Args:
            track_id (str): The ID of the track.

        Returns:
            Dict: A dictionary containing audio features for the track if successful, None otherwise.
        """
        try:
            endpoint = f"v1/audio-features/{track_id}"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            print(f"Failed to get audio features: {e.response.status_code}")
            return None

    def get_tracks_audio_features(self, track_ids: List[str]) -> Optional[Dict]:
        """Get audio features for multiple tracks from Spotify.

        Args:
            track_ids (List[str]): A list of track IDs.

        Returns:
            Dict: A dictionary containing audio features for the tracks if successful, None otherwise.
        """
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

    def get_track_audio_analysis(self, track_id: str) -> Optional[Dict]:
        """Get audio analysis for a track from Spotify.

        Args:
            track_id (str): The ID of the track.

        Returns:
            Optional[Dict]: A dictionary containing audio analysis for the track if successful.
                            None if the request fails.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/audio-analysis/{track_id}"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            print(
                f"Failed to get audio analysis for track {track_id}: {e.response.status_code}"
            )
            return None

    def get_recommendations(
        self,
        seed_artists: List[str],
        seed_genres: List[str],
        seed_tracks: List[str],
        market: Optional[str] = None,
        limit: int = 20,
        **kwargs: Any,
    ) -> Optional[Dict]:
        """Get track recommendations based on seeds from Spotify.

        Args:
            seed_artists (List[str]): A list of artist IDs, URIs, or URLs.
            seed_genres (List[str]): A list of genre names.
            seed_tracks (List[str]): A list of track IDs, URIs, or URLs.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the recommendations from. Defaults to None.
            limit (int, optional): The maximum number of recommendations to return. Defaults to 20.
            **kwargs (Any): Additional query parameters.

        Returns:
            Optional[Dict]: A dictionary containing recommendations if successful.
                            None if the request fails.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
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


class GenresAPI:

    def __init__(self, api):
        self.api = api

    def get_recommendation_genres(self) -> Optional[Dict]:
        """Get available genres for track recommendations from Spotify.

        Returns:
            Optional[Dict]: A dictionary containing available genres if successful.
                            None if the request fails.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = "v1/recommendations/available-genre-seeds"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get recommendation genres: {e.response.status_code}"
            ) from e


class PlaylistsAPI:

    MAX_PLAYLIST_ITEMS_PER_REQUEST = 50

    def __init__(self, api):
        self.api = api

    def get_playlist(
        self, playlist_id: str, market: Optional[str] = None, **kwargs
    ) -> Optional[Dict]:
        """Get information about a playlist from Spotify.

        Args:
            playlist_id (str): The ID of the playlist.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the playlist from. Defaults to None.

        Returns:
            Optional[Dict]: A dictionary containing information about the playlist if successful.
                            None if the request fails.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/playlists/{playlist_id}"
            params = {"market": market} if market else {}
            params.update(kwargs)
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get playlist: {e.response.status_code}"
            ) from e

    def get_category_playlists(
        self, category_id: str, limit: int = 20, offset: int = 0
    ) -> Dict:
        """Get playlists for a specific category from Spotify.

        Args:
            category_id (str): The ID of the category.
            limit (int, optional): The maximum number of playlists to retrieve. Defaults to 20.
            offset (int, optional): The index of the first item to retrieve. Defaults to 0.

        Returns:
            Dict: A dictionary containing information about the playlists.

        Raises:
            ValueError: If the specified limit exceeds the maximum allowed playlist items per request.
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            if limit > self.MAX_PLAYLIST_ITEMS_PER_REQUEST:
                raise ValueError("Exceeded maximum playlist items per request")

            endpoint = f"v1/browse/categories/{category_id}/playlists"
            params = {"limit": limit, "offset": offset}
            return self.api.get(endpoint, params=params)
        except ValueError as ve:
            raise ValueError(f"Error fetching category playlists: {ve}") from ve
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get category playlists: {e.response.status_code}"
            ) from e

    def get_featured_playlists(
        self, locale: str, limit: int = 20, offset: int = 0
    ) -> Dict:
        """Get featured playlists from Spotify.

        Args:
            locale (str): The locale for the featured playlists.
            limit (int, optional): The maximum number of playlists to retrieve. Defaults to 20.
            offset (int, optional): The index of the first item to retrieve. Defaults to 0.

        Returns:
            Dict: A dictionary containing information about the featured playlists.

        Raises:
            ValueError: If the specified limit exceeds the maximum allowed playlist items per request.
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            if limit > self.MAX_PLAYLIST_ITEMS_PER_REQUEST:
                raise ValueError("Exceeded maximum playlist items per request")

            endpoint = "v1/browse/featured-playlists"
            params = {"locale": locale, "limit": limit, "offset": offset}
            return self.api.get(endpoint, params=params)
        except ValueError as ve:
            raise ValueError(f"Error fetching featured playlists: {ve}") from ve
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get featured playlists: {e.response.status_code}"
            ) from e

    def get_playlist_cover_image(self, playlist_id: str) -> Optional[Dict[str, str]]:
        """Get the cover image metadata and URL of a playlist from Spotify.

        Args:
            playlist_id (str): The ID of the playlist.

        Returns:
            Optional[Dict[str, str]]: A dictionary containing the cover image metadata and URL, or None if the cover image is not available.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/playlists/{playlist_id}/images"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get playlist cover image for ID {playlist_id}: {e.response.status_code}"
            ) from e


class ArtistsAPI:

    MAX_ARTISTS_PER_REQUEST = 100

    def __init__(self, api):
        self.api = api

    def get_artist(self, artist_id: str) -> Dict:
        """Get information about an artist from Spotify.

        Args:
            artist_id (str): The ID of the artist.

        Returns:
            Dict: A dictionary containing information about the artist.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/artists/{artist_id}"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get artist for ID {artist_id}: {e.response.status_code}"
            ) from e

    def get_artists(self, artist_ids: List[str]) -> Dict:
        """Get information about multiple artists from Spotify.

        Args:
            artist_ids (List[str]): A list of artist IDs.

        Returns:
            Dict: A dictionary containing information about the artists.

        Raises:
            ValueError: If the number of artist IDs exceeds the maximum allowed per request.
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            if len(artist_ids) > self.MAX_ARTISTS_PER_REQUEST:
                raise ValueError("Exceeded maximum artist IDs per request")

            endpoint = "v1/artists"
            params = {"ids": ",".join(artist_ids)}
            return self.api.get(endpoint, params=params)
        except ValueError as ve:
            raise ValueError("Failed to get artists") from ve
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get artists: {e.response.status_code}"
            ) from e

    def get_artist_albums(
        self,
        artist_id: str,
        include_groups: Optional[str] = None,
        market: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict:
        """Get albums from a specific artist on Spotify.

        Args:
            artist_id (str): The ID of the artist.
            include_groups (Optional[str], optional): Filters the response based on the album type.
                Valid values: 'album', 'single', 'appears_on', 'compilation'. Defaults to None.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the albums from. Defaults to None.
            limit (int, optional): The maximum number of albums to return. Defaults to 20.
            offset (int, optional): The index of the first album to return. Defaults to 0.

        Returns:
            Dict: A dictionary containing information about the artist's albums.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/artists/{artist_id}/albums"
            params = {
                "include_groups": include_groups,
                "market": market,
                "limit": limit,
                "offset": offset,
            }
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get artist albums for artist ID {artist_id}: {e.response.status_code}"
            ) from e

    def get_artist_top_tracks(
        self, artist_id: str, market: Optional[str] = None
    ) -> Dict:
        """Get the top tracks of a specific artist on Spotify.

        Args:
            artist_id (str): The ID of the artist.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the tracks from. Defaults to None.

        Returns:
            Dict: A dictionary containing information about the artist's top tracks.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/artists/{artist_id}/top-tracks"
            params = {"market": market}
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get artist top tracks for artist ID {artist_id}: {e.response.status_code}"
            ) from e

    def get_related_artists(self, artist_id: str) -> Dict:
        """Get related artists for a specific artist on Spotify.

        Args:
            artist_id (str): The ID of the artist.

        Returns:
            Dict: A dictionary containing information about related artists.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/artists/{artist_id}/related-artists"
            return self.api.get(endpoint)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get related artists for artist ID {artist_id}: {e.response.status_code}"
            ) from e


class AlbumsAPI:

    MAX_ALBUMS_PER_REQUEST = 20
    MAX_TRACKS_PER_ALBUM = 50
    MAX_ALBUMS_TO_RETURN = 50

    def __init__(self, api):
        self.api = api

    def get_album(self, album_id: str, market: Optional[str] = None) -> Dict:
        """Get information about a specific album from Spotify.

        Args:
            album_id (str): The ID of the album.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the album from. Defaults to None.

        Returns:
            Dict: A dictionary containing information about the album.

        Raises:
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            endpoint = f"v1/albums/{album_id}"
            params = {"market": market} if market else None
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get album for ID {album_id}: {e.response.status_code}"
            ) from e

    def get_albums(self, album_ids: List[str], market: Optional[str] = None) -> Dict:
        """Get information about multiple albums from Spotify.

        Args:
            album_ids (List[str]): A list of album IDs.
            market (Optional[str], optional): An optional parameter indicating the market (country) to retrieve the albums from. Defaults to None.

        Returns:
            Dict: A dictionary containing information about the albums.

        Raises:
            ValueError: If the number of album IDs exceeds the maximum allowed per request.
            requests.HTTPError: If an HTTP error occurs during the request.
        """
        try:
            if len(album_ids) > self.MAX_ALBUMS_PER_REQUEST:
                raise ValueError("Exceeded maximum album IDs per request")

            endpoint = "v1/albums"
            params = {"ids": ",".join(album_ids)}
            if market:
                params["market"] = market
            return self.api.get(endpoint, params=params)
        except ValueError as ve:
            raise ValueError("Failed to get albums") from ve
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get albums: {e.response.status_code}"
            ) from e

    def get_album_tracks(
        self,
        album_id: str,
        market: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Optional[Dict]:
        """Get tracks of an album from Spotify.

        Args:
            album_id (str): The ID of the album.
            market (str, optional): An ISO 3166-1 alpha-2 country code or 'from_token'.
                Defaults to None.
            limit (int, optional): The maximum number of tracks to return. Defaults to 20.
            offset (int, optional): The index of the first track to return. Defaults to 0.

        Raises:
            ValueError: If the provided limit exceeds the maximum allowed limit.
            requests.HTTPError: If an HTTP error occurs while making the request.

        Returns:
            dict: A dictionary containing information about the tracks of the album.
                Returns None if the request fails.
        """
        try:
            if limit > self.MAX_TRACKS_PER_ALBUM:
                raise ValueError("Exceeded maximum tracks per album per request")
            endpoint = f"v1/albums/{album_id}/tracks"
            params = {"market": market, "limit": limit, "offset": offset}
            return self.api.get(endpoint, params=params)
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get album tracks for album ID {album_id}: {e.response.status_code}"
            ) from e

    def get_new_releases(self, limit: int = 20, offset: int = 0) -> Optional[Dict]:
        """Get new album releases from Spotify.

        Args:
            limit (int, optional): Number of albums to return. Defaults to 20.
            offset (int, optional): Index of the first item to return. Defaults to 0.

        Raises:
            ValueError: If the provided limit exceeds the maximum allowed limit.
            requests.HTTPError: If an HTTP error occurs while making the request.

        Returns:
            dict: A dictionary containing information about new album releases.
                Returns None if the request fails.
        """
        try:
            if limit > self.MAX_ALBUMS_TO_RETURN:
                raise ValueError(
                    f"Limit exceeded: {limit} is greater than the maximum allowed limit of {self.MAX_ALBUMS_TO_RETURN}"
                )

            endpoint = "v1/browse/new-releases"
            params = {"limit": limit, "offset": offset}
            return self.api.get(endpoint, params=params)
        except ValueError as ve:
            raise ValueError("Failed to get new releases") from ve
        except requests.HTTPError as e:
            raise requests.HTTPError(
                f"Failed to get new releases: {e.response.status_code}"
            ) from e
