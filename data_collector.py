"""
data_collector.py
=================
Spotify + Hooktheory 데이터를 통합하여 최종 분석용 데이터셋을 생성합니다.

실행 방법:
    python data_collector.py --pilot      # 파일럿 (Coldplay + Adele 2명)
    python data_collector.py --all        # 전체 20명 아티스트
    python data_collector.py --artist "Radiohead"  # 특정 아티스트만

출력 파일:
    collected_data.csv  → 노트북에서 바로 읽어 분석에 사용
"""

import os
import time
import argparse
import pandas as pd

from spotify_collector import collect_spotify_data, ARTISTS_BY_DECADE
from hooktheory_scraper import get_chord_progression

OUTPUT_CSV = "collected_data.csv"
SPOTIFY_CSV = "spotify_data_raw.csv"


def run_collection(target_artists: dict[str, list[str]], output_path: str = OUTPUT_CSV) -> pd.DataFrame:
    """
    1) Spotify에서 트랙 목록 + 오디오 피처 수집
    2) 각 곡에 대해 Hooktheory에서 코드 진행 수집
    3) 두 데이터를 병합하여 최종 CSV 저장
    """
    print("=" * 60)
    print("STEP 1: Spotify 데이터 수집")
    print("=" * 60)
    df_spotify = collect_spotify_data(target_artists=target_artists, output_csv=SPOTIFY_CSV)

    print("\n" + "=" * 60)
    print("STEP 2: Hooktheory 코드 진행 수집")
    print("=" * 60)

    hooktheory_rows = []
    total = len(df_spotify)
    for idx, row in df_spotify.iterrows():
        artist = row["artist"]
        title = row["title"]
        print(f"  [{idx+1}/{total}] {artist} - {title}")

        result = get_chord_progression(artist, title)
        if result:
            hooktheory_rows.append({
                "artist": artist,
                "title": title,
                "key": result["key"],
                "mode": result["mode"],
                "raw_chords": result["chords"],
                "ht_section": result["section"],
            })
            print(f"    ✅ Key: {result['key']} {result['mode']} | {result['chords'][:50]}...")
        else:
            hooktheory_rows.append({
                "artist": artist,
                "title": title,
                "key": None,
                "mode": None,
                "raw_chords": None,
                "ht_section": None,
            })
            print(f"    ⚠  Hooktheory에 등록 데이터 없음")

    df_ht = pd.DataFrame(hooktheory_rows)

    print("\n" + "=" * 60)
    print("STEP 3: 데이터 병합 및 저장")
    print("=" * 60)
    df_merged = pd.merge(df_spotify, df_ht, on=["artist", "title"], how="left")

    # 통계 출력
    total_songs = len(df_merged)
    ht_found = df_merged["raw_chords"].notna().sum()
    ht_missing = total_songs - ht_found
    coverage = (ht_found / total_songs * 100) if total_songs > 0 else 0

    print(f"\n수집 완료 통계:")
    print(f"  전체 곡 수:             {total_songs}")
    print(f"  Hooktheory 데이터 있음: {ht_found} ({coverage:.1f}%)")
    print(f"  Hooktheory 데이터 없음: {ht_missing}")

    # Key 기본값 처리 (Hooktheory 데이터 없을 때 C major로 대체)
    df_merged["key"] = df_merged["key"].fillna("C")
    df_merged["mode"] = df_merged["mode"].fillna("major")
    df_merged["raw_chords"] = df_merged["raw_chords"].fillna("C G Am F")  # 기본 4코드

    df_merged.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n✅ 최종 데이터셋 저장 완료: {output_path}")
    print(f"   (총 {len(df_merged)}행 × {len(df_merged.columns)}열)")

    return df_merged


def main():
    parser = argparse.ArgumentParser(description="코드 진행 분석 데이터 통합 수집기")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pilot", action="store_true", help="파일럿 모드: Coldplay + Adele 2명만 수집")
    group.add_argument("--all", action="store_true", help="전체 모드: 20명 전체 아티스트 수집")
    group.add_argument("--artist", type=str, help="특정 아티스트만 수집 (예: 'Radiohead')")
    parser.add_argument("--output", type=str, default=OUTPUT_CSV, help="출력 CSV 파일 경로")
    args = parser.parse_args()

    if args.pilot:
        target = {
            "00s": ["Coldplay"],
            "10s": ["Adele"],
        }
        print("▶ 파일럿 모드: Coldplay + Adele\n")
    elif args.artist:
        decade = next(
            (d for d, lst in ARTISTS_BY_DECADE.items() if args.artist in lst),
            "unknown",
        )
        target = {decade: [args.artist]}
        print(f"▶ 단일 아티스트 모드: {args.artist} ({decade})\n")
    else:
        # --all 또는 기본값
        target = ARTISTS_BY_DECADE
        print("▶ 전체 모드: 20명 전체 아티스트\n")

    run_collection(target_artists=target, output_path=args.output)


if __name__ == "__main__":
    main()
