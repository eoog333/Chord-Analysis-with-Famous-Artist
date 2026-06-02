"""
replace_hiphop.py
==============
힙합 아티스트들을 팝/록/R&B 등 다른 장르의 아티스트로 교체하여 재수집합니다.
"""

import pandas as pd
from hooktheory_scraper import fetch_chords_from_url
import re, time, random

OUTPUT_CSV = "collected_data.csv"

REPLACE_MAP = {
    # ── 90s ──────────────────────────────────────────────────────────────────
    "Snoop Dogg": {
        "new_name": "Backstreet Boys",
        "decade": "90s",
        "songs": [
            ("backstreet-boys", "i-want-it-that-way"),
            ("backstreet-boys", "everybody-backstreets-back"),
        ]
    },
    "2Pac": {
        "new_name": "Destinys Child",
        "decade": "90s",
        "songs": [
            ("destinys-child", "say-my-name"),
            ("destinys-child", "survivor"),
        ]
    },
    "The Notorious B.I.G.": {
        "new_name": "Ricky Martin",
        "decade": "90s",
        "songs": [
            ("ricky-martin", "livin-la-vida-loca"),
        ]
    },

    # ── 00s ──────────────────────────────────────────────────────────────────
    "Eminem": {
        "new_name": "Evanescence",
        "decade": "00s",
        "songs": [
            ("evanescence", "bring-me-to-life"),
            ("evanescence", "my-immortal"),
        ]
    },
    "Kanye West": {
        "new_name": "The White Stripes",
        "decade": "00s",
        "songs": [
            ("the-white-stripes", "seven-nation-army"),
        ]
    },
    "Outkast": {
        "new_name": "Norah Jones",
        "decade": "00s",
        "songs": [
            ("norah-jones", "dont-know-why"),
        ]
    },

    # ── 10s ──────────────────────────────────────────────────────────────────
    "Drake": {
        "new_name": "Charlie Puth",
        "decade": "10s",
        "songs": [
            ("charlie-puth", "attention"),
            ("charlie-puth", "we-dont-talk-anymore"),
        ]
    },
    "Kendrick Lamar": {
        "new_name": "Sia",
        "decade": "10s",
        "songs": [
            ("sia", "chandelier"),
            ("sia", "cheap-thrills"),
        ]
    },
    "J. Cole": {
        "new_name": "Hozier",
        "decade": "10s",
        "songs": [
            ("hozier", "take-me-to-church"),
        ]
    },
    "Travis Scott": {
        "new_name": "Zedd",
        "decade": "10s",
        "songs": [
            ("zedd", "clarity"),
            ("zedd", "the-middle"),
        ]
    },
    "Post Malone": {
        "new_name": "The Chainsmokers",
        "decade": "10s",
        "songs": [
            ("the-chainsmokers", "closer"),
            ("the-chainsmokers", "something-just-like-this"),
        ]
    },

    # ── 20s ──────────────────────────────────────────────────────────────────
    "Megan Thee Stallion": {
        "new_name": "Miley Cyrus",
        "decade": "20s",
        "songs": [
            ("miley-cyrus", "flowers"),
        ]
    },
    "Lil Nas X": {
        "new_name": "Harry Styles",
        "decade": "20s",
        "songs": [
            ("harry-styles", "as-it-was"),
            ("harry-styles", "watermelon-sugar"),
        ]
    },
    "Doja Cat": {
        "new_name": "GAYLE",
        "decade": "20s",
        "songs": [
            ("gayle", "abcdefu"),
        ]
    },
}

def try_fetch(songs: list) -> dict | None:
    for artist_slug, song_slug in songs:
        print(f"    → {artist_slug}/{song_slug} 시도...")
        result = fetch_chords_from_url(artist_slug, song_slug)
        time.sleep(random.uniform(0.8, 1.5))
        if result:
            return result
    return None

def main():
    df = pd.read_csv(OUTPUT_CSV)

    print("=" * 60)
    print("힙합 아티스트 교체 재수집")
    print("=" * 60)

    updated = 0
    for orig_artist, info in REPLACE_MAP.items():
        if orig_artist not in df["artist"].values:
            print(f"[{orig_artist}] ⚠  CSV에 없음 — 스킵")
            continue

        new_name = info["new_name"]
        songs    = info["songs"]
        decade   = info["decade"]

        print(f"\n[{orig_artist}] → [{new_name}] 교체 수집 중...")
        result = try_fetch(songs)

        if result:
            idx = df[df["artist"] == orig_artist].index[0]
            df.at[idx, "artist"]     = new_name
            df.at[idx, "decade"]     = decade
            df.at[idx, "key"]        = result["key"]
            df.at[idx, "mode"]       = result["mode"]
            df.at[idx, "raw_chords"] = result["chords"]
            df.at[idx, "ht_section"] = result["section"]
            print(f"  ✅ [{new_name}] Key: {result['key']} {result['mode']}")
            print(f"     Chords: {result['chords'][:70]}...")
            updated += 1
        else:
            print(f"  ❌ [{new_name}] 데이터 없음 — 기존 데이터 삭제")
            idx = df[df["artist"] == orig_artist].index[0]
            df = df.drop(idx)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n{'='*60}")
    print(f"교체 완료: {updated}/{len(REPLACE_MAP)}명 갱신")
    print(f"저장: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
