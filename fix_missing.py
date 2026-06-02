"""
fix_missing.py
==============
collected_data.csv에서 실제 데이터가 없는 아티스트(폴백 C G Am F)를
다른 곡 슬러그 또는 대체 아티스트로 재수집하여 CSV를 갱신합니다.
"""

import pandas as pd
from hooktheory_scraper import fetch_chords_from_url, sind_sequence_to_chords
import re, time, random

OUTPUT_CSV = "collected_data.csv"
FALLBACK_CHORDS = "C G Am F"

# ── 재시도 전략 ──────────────────────────────────────────────────────────────
# 형식: { "아티스트명(CSV에 저장된 이름)": {
#           "artist_slug": ...,  ← 다른 아티스트로 교체 시
#           "songs": [(artist_slug, song_slug), ...],
#           "new_name": ...,     ← 교체 아티스트 이름 (선택)
#         }
# }

RETRY_MAP = {
    # ── 90s ──────────────────────────────────────────────────────────────────
    "Snoop Dogg": {
        "songs": [
            ("snoop-dogg", "gin-and-juice"),
            ("snoop-dogg", "beautiful"),
            ("snoop-dogg", "who-am-i-whats-my-name"),
        ]
    },
    "The Notorious B.I.G.": {
        "songs": [
            ("the-notorious-big", "big-poppa"),
            ("the-notorious-big", "mo-money-mo-problems"),
            ("notorious-big",     "juicy"),
        ]
    },
    "Beck": {
        "songs": [
            ("beck", "where-its-at"),
            ("beck", "devils-haircut"),
            ("beck", "loser"),
        ]
    },

    # ── 00s ──────────────────────────────────────────────────────────────────
    "Jay-Z": {
        # Jay-Z가 TheoryTab에 없을 가능성 → Nelly Furtado로 교체
        "new_name": "Nelly Furtado",
        "decade":   "00s",
        "songs": [
            ("nelly-furtado", "maneater"),
            ("nelly-furtado", "say-it-right"),
            ("nelly-furtado", "promiscuous"),
        ]
    },

    # ── 10s ──────────────────────────────────────────────────────────────────
    "Cardi B": {
        # Cardi B 대신 Meghan Trainor로 교체
        "new_name": "Meghan Trainor",
        "decade":   "10s",
        "songs": [
            ("meghan-trainor", "all-about-that-bass"),
            ("meghan-trainor", "like-im-gonna-lose-you"),
            ("meghan-trainor", "dear-future-husband"),
        ]
    },

    # ── 20s ──────────────────────────────────────────────────────────────────
    "Bad Bunny": {
        # Bad Bunny 대신 Olivia Rodrigo 2nd song으로 → 이미 있으니 Harry Styles로
        "new_name": "Glass Animals",
        "decade":   "20s",
        "songs": [
            ("glass-animals", "heat-waves"),
            ("glass-animals", "your-love-whoa"),
        ]
    },
    "Jack Harlow": {
        "new_name": "Conan Gray",
        "decade":   "20s",
        "songs": [
            ("conan-gray", "heather"),
            ("conan-gray", "maniac"),
            ("conan-gray", "people-watching"),
        ]
    },
    "Luke Combs": {
        # Luke Combs 대신 다른 컨트리 아티스트
        "new_name": "Chris Stapleton",
        "decade":   "20s",
        "songs": [
            ("chris-stapleton", "tennessee-whiskey"),
            ("chris-stapleton", "broken-halos"),
        ]
    },
    "Ice Spice": {
        "new_name": "Doja Cat",   # 이미 있으므로 → Steve Lacy
        "new_name": "Steve Lacy",
        "decade":   "20s",
        "songs": [
            ("steve-lacy", "bad-habit"),
            ("steve-lacy", "gemini-rights"),
        ]
    },
    "Central Cee": {
        "new_name": "d4vd",
        "decade":   "20s",
        "songs": [
            ("d4vd", "here-with-me"),
            ("d4vd", "romantic-homicide"),
        ]
    },
    "Peso Pluma": {
        # 라틴 아티스트 → Rosalía로 교체
        "new_name": "Rosalía",
        "decade":   "20s",
        "songs": [
            ("rosalia", "malamente"),
            ("rosalia", "con-altura"),
            ("rosalia", "la-noche-de-anoche"),
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
    missing_mask = df["raw_chords"].str.strip() == FALLBACK_CHORDS
    missing_artists = df[missing_mask]["artist"].tolist()

    print("=" * 60)
    print("데이터 없는 아티스트 재수집")
    print("=" * 60)
    print(f"재수집 대상: {len(missing_artists)}명\n")

    updated = 0
    for orig_artist in missing_artists:
        info = RETRY_MAP.get(orig_artist)
        if not info:
            print(f"[{orig_artist}] ⚠  RETRY_MAP에 없음 — 스킵")
            continue

        new_name = info.get("new_name", orig_artist)
        songs    = info["songs"]
        decade   = info.get("decade") or df.loc[df["artist"] == orig_artist, "decade"].values[0]

        print(f"\n[{orig_artist}] → [{new_name}] 재수집 중...")
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
            print(f"  ❌ [{new_name}] 데이터 없음 — 그대로 유지")

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"\n{'='*60}")
    print(f"재수집 완료: {updated}/{len(missing_artists)}명 갱신")
    print(f"저장: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
