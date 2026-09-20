import requests
from collections import Counter

class SpotifyStats:
    def __init__(self, access_token):
        self.access_token = access_token

    def get_api(self, endpoint, params=None):
        url = f"https://api.spotify.com/v1/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data

    def get_tracks(self, time_range="medium_term", limit=20):
        data = self.get_api("me/top/tracks", params={"time_range": time_range, "limit": limit})
        return [
            {
                "name": item["name"],
                "artist": item["artists"][0]["name"],
                "album": item["album"]["name"],
                "image": item["album"]["images"][0]["url"] if item["album"]["images"] else None
            }
            for item in data.get("items", [])
        ]

    def get_artists(self, time_range="medium_term", limit=20):
        data = self.get_api("me/top/artists", params={"time_range": time_range, "limit": limit})
        return [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "genres": item.get("genres", []),
                "popularity": item.get("popularity"),
                "image": item["images"][0]["url"] if item.get("images") else None
            }
            for item in data.get("items", [])
        ]

    def get_albums(self, time_range="medium_term", limit=50):
        tracks = self.get_tracks(time_range=time_range, limit=limit)
        albums = {}
        for t in tracks:
            name = t["album"]
            if name not in albums:
                albums[name] = {"name": name, "image": t["image"], "count": 0}
            albums[name]["count"] += 1
        return sorted(albums.values(), key=lambda a: a["count"], reverse=True)

    def _compare(self, recent_items, baseline_items, key_fn):
        recent_keys = {key_fn(i) for i in recent_items}
        baseline_keys = {key_fn(i) for i in baseline_items}

        return {
            "new_in_rotation": [i for i in recent_items if key_fn(i) not in baseline_keys],
            "longtime_favorites": [i for i in baseline_items if key_fn(i) in recent_keys],
            "faded_out": [i for i in baseline_items if key_fn(i) not in recent_keys]
        }

    def get_taste_change(self, recent="short_term", baseline="long_term", limit=50):
        recent_tracks = self.get_tracks(time_range=recent, limit=limit)
        baseline_tracks = self.get_tracks(time_range=baseline, limit=limit)
        return self._compare(recent_tracks, baseline_tracks, key_fn=lambda t: t["name"])

    def get_artist_taste_change(self, recent="short_term", baseline="long_term", limit=50):
        recent_artists = self.get_artists(time_range=recent, limit=limit)
        baseline_artists = self.get_artists(time_range=baseline, limit=limit)
        return self._compare(recent_artists, baseline_artists, key_fn=lambda a: a["name"])

    def get_album_taste_change(self, recent="short_term", baseline="long_term", limit=50):
        recent_albums = self.get_albums(time_range=recent, limit=limit)
        baseline_albums = self.get_albums(time_range=baseline, limit=limit)
        return self._compare(recent_albums, baseline_albums, key_fn=lambda a: a["name"])