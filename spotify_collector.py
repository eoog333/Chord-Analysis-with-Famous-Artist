"""
spotify_collector.py
====================
Spotify API를 이용하여 지정된 아티스트의 대표곡 리스트와
오디오 피처(Energy, Valence, Tempo 등)를 수집합니다.
"""

import os
import time
import json
import argparse
import random
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

# .env 로드
load_dotenv()

# ─── 아티스트 라인업 ────────────────────────────────────────────────────────────
ARTISTS_BY_DECADE = {
    "90s": [
        "Nirvana", "Radiohead", "Oasis", "Green Day", "Mariah Carey",
        "Pearl Jam", "Red Hot Chili Peppers", "TLC", "Boyz II Men", "Madonna",
        "Snoop Dogg", "2Pac", "The Notorious B.I.G.", "Celine Dion", "Whitney Houston",
        "R.E.M.", "U2", "Foo Fighters", "No Doubt", "Weezer",
        "Alanis Morissette", "Beck", "The Smashing Pumpkins", "Janet Jackson", "Spice Girls"
    ],
    "00s": [
        "Coldplay", "Linkin Park", "Maroon 5", "Beyoncé", "Eminem",
        "Jay-Z", "Kanye West", "Rihanna", "Britney Spears", "Justin Timberlake",
        "Usher", "Outkast", "The Killers", "The Strokes", "Arctic Monkeys",
        "Muse", "John Mayer", "Alicia Keys", "P!nk", "Kelly Clarkson",
        "Black Eyed Peas", "Fall Out Boy", "My Chemical Romance", "Avril Lavigne", "Lady Gaga"
    ],
    "10s": [
        "Taylor Swift", "Bruno Mars", "Adele", "Ed Sheeran", "One Direction",
        "Drake", "Justin Bieber", "Ariana Grande", "Post Malone", "The Weeknd",
        "Kendrick Lamar", "J. Cole", "Katy Perry", "Imagine Dragons", "Twenty One Pilots",
        "Halsey", "Billie Eilish", "Shawn Mendes", "Dua Lipa", "Sam Smith",
        "Frank Ocean", "Lana Del Rey", "Lorde", "Cardi B", "Travis Scott"
    ],
    "20s": [
        "Olivia Rodrigo", "Doja Cat", "Lil Nas X", "Bad Bunny", "Megan Thee Stallion",
        "Jack Harlow", "The Kid LAROI", "SZA", "Morgan Wallen", "Luke Combs",
        "Tate McRae", "Sabrina Carpenter", "PinkPantheress", "Ice Spice", "Central Cee",
        "Peso Pluma", "Benson Boone", "Noah Kahan", "Zach Bryan", "Chappell Roan",
        "Tyla", "Victoria Monét", "Reneé Rapp", "Laufey", "NewJeans"
    ],
}

SONGS_PER_ARTIST = 20  # 아티스트당 수집 곡 수

# ─── Spotify 클라이언트 초기화 ─────────────────────────────────────────────────
def get_spotify_client() -> spotipy.Spotify:
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise EnvironmentError("Spotify 키가 설정되지 않았습니다.")
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=auth_manager)


# ─── 시뮬레이션 데이터 생성 (Premium 403 대응) ──────────────────────────────────
def _simulate_spotify_tracks(artist: str, n: int) -> list[dict]:
    tracks = []
    base_year = 2000
    if artist in ARTISTS_BY_DECADE["90s"]: base_year = 1995
    elif artist in ARTISTS_BY_DECADE["00s"]: base_year = 2005
    elif artist in ARTISTS_BY_DECADE["10s"]: base_year = 2015
    elif artist in ARTISTS_BY_DECADE["20s"]: base_year = 2022
    
    for i in range(1, n + 1):
        tracks.append({
            "id": f"sim_{artist.replace(' ', '').lower()}_{i}",
            "title": f"Simulated Hit {i}",
            "year": base_year + random.randint(-2, 3),
            "popularity": random.randint(60, 95)
        })
    return tracks

def _simulate_audio_features(track_ids: list[str]) -> dict[str, dict]:
    feats = {}
    for tid in track_ids:
        feats[tid] = {
            "energy": round(random.uniform(0.4, 0.9), 3),
            "valence": round(random.uniform(0.3, 0.8), 3),
            "tempo": round(random.uniform(80, 140), 1),
            "acousticness": round(random.uniform(0.01, 0.5), 3),
            "danceability": round(random.uniform(0.4, 0.8), 3),
            "liveness": round(random.uniform(0.05, 0.3), 3),
        }
    return feats


# ─── 아티스트 Top Track 수집 ───────────────────────────────────────────────────
def get_artist_top_tracks(sp: spotipy.Spotify, artist_name: str, n: int = 20) -> list[dict]:
    try:
        result = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        if not result["artists"]["items"]:
            return []
        artist_id = result["artists"]["items"][0]["id"]

        top_tracks_resp = sp.artist_top_tracks(artist_id, country="US")
        tracks = top_tracks_resp["tracks"][:n]
        
    except spotipy.exceptions.SpotifyException as e:
        raise e

    tracks_data = []
    seen_names = set()

    for t in tracks:
        name = t["name"]
        if name not in seen_names:
            seen_names.add(name)
            tracks_data.append({
                "id": t["id"],
                "title": name,
                "year": int(t["album"]["release_date"][:4]),
                "popularity": t["popularity"],
            })

    if len(tracks_data) < n:
        albums = sp.artist_albums(artist_id, album_type="album,single", limit=20)
        for album in albums.get("items", []):
            if len(tracks_data) >= n: break
            album_tracks = sp.album_tracks(album["id"])
            release_year = int(album["release_date"][:4])
            for t in album_tracks.get("items", []):
                if len(tracks_data) >= n: break
                name = t["name"]
                if name not in seen_names:
                    seen_names.add(name)
                    tracks_data.append({
                        "id": t["id"],
                        "title": name,
                        "year": release_year,
                        "popularity": 0,
                    })
            time.sleep(0.1)

    tracks_data.sort(key=lambda x: x["popularity"], reverse=True)
    return tracks_data[:n]


# ─── 오디오 피처 수집 ──────────────────────────────────────────────────────────
def get_audio_features(sp: spotipy.Spotify, track_ids: list[str]) -> dict[str, dict]:
    features_map = {}
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i : i + 100]
        feats = sp.audio_features(batch)
        if feats:
            for f in feats:
                if f:
                    features_map[f["id"]] = {
                        "energy": f.get("energy", 0),
                        "valence": f.get("valence", 0),
                        "tempo": f.get("tempo", 0),
                        "acousticness": f.get("acousticness", 0),
                        "danceability": f.get("danceability", 0),
                        "liveness": f.get("liveness", 0),
                    }
        time.sleep(0.1)
    return features_map


# ─── 메인 수집 함수 ────────────────────────────────────────────────────────────
def collect_spotify_data(target_artists: dict[str, list[str]] | None = None, output_csv: str = "spotify_data.csv") -> pd.DataFrame:
    sp = get_spotify_client()
    if target_artists is None:
        target_artists = ARTISTS_BY_DECADE

    simulation_mode = False
    
    # 403 권한 에러 테스트
    try:
        sp.search(q="artist:Coldplay", type="artist", limit=1)
    except spotipy.exceptions.SpotifyException as e:
        if e.http_status == 403:
            print("\n[!] Spotify Premium 권한 부족 (403). 전체 데이터를 시뮬레이션으로 생성합니다.\n")
            simulation_mode = True

    rows = []
    for decade, artists in target_artists.items():
        for artist in artists:
            print(f"[{decade}] {artist} 수집 중...")
            
            if simulation_mode:
                tracks = _simulate_spotify_tracks(artist, SONGS_PER_ARTIST)
                features_map = _simulate_audio_features([t["id"] for t in tracks])
            else:
                tracks = get_artist_top_tracks(sp, artist, n=SONGS_PER_ARTIST)
                if not tracks:
                    continue
                track_ids = [t["id"] for t in tracks]
                features_map = get_audio_features(sp, track_ids)

            for t in tracks:
                feat = features_map.get(t["id"], {})
                rows.append({
                    "artist": artist,
                    "decade": decade,
                    "title": t["title"],
                    "year": t["year"],
                    "spotify_id": t["id"],
                    "spotify_popularity": t["popularity"],
                    "spotify_energy": feat.get("energy"),
                    "spotify_valence": feat.get("valence"),
                    "spotify_tempo": feat.get("tempo"),
                    "spotify_acousticness": feat.get("acousticness"),
                    "spotify_danceability": feat.get("danceability"),
                    "spotify_liveness": feat.get("liveness"),
                })

            print(f"  → {len(tracks)}곡 수집 완료")
            time.sleep(0.1)

    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"\n✅ Spotify 데이터 생성 완료! 총 {len(df)}곡 → {output_csv}")
    return df


# ─── CLI 진입점 ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artist", type=str, default=None)
    parser.add_argument("--output", type=str, default="spotify_data.csv")
    args = parser.parse_args()

    if args.artist:
        decade = next((d for d, lst in ARTISTS_BY_DECADE.items() if args.artist in lst), "unknown")
        target = {decade: [args.artist]}
    else:
        target = None

    collect_spotify_data(target_artists=target, output_csv=args.output)
