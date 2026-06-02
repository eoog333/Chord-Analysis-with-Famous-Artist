"""
data_collector.py
=================
Hooktheory(TheoryTab) 코드 진행 데이터를 수집하여 최종 분석용 데이터셋을 생성합니다.
(Spotify API 의존성 제거. hooktheory_scraper.py의 하드코딩된 발매 시대 사용)
"""

import argparse
import pandas as pd
from hooktheory_scraper import ARTIST_SONGS, get_all_songs_for_artist

OUTPUT_CSV = "collected_data.csv"

def run_collection(target_artists: list[str], output_path: str = OUTPUT_CSV) -> pd.DataFrame:
    print("=" * 60)
    print("Hooktheory 코드 진행 곡 단위 수집 (Spotify API 미사용)")
    print("=" * 60)

    rows = []
    total_artists = len(target_artists)
    
    for idx, artist in enumerate(target_artists, 1):
        print(f"\n[{idx}/{total_artists}] {artist}")
        
        songs = get_all_songs_for_artist(artist)
        if not songs:
            print(f"  ⚠  {artist}의 데이터 수집 실패 또는 대상 곡 없음")
            continue
            
        for s in songs:
            rows.append({
                "artist": s["artist"],
                "title": s["title"],
                "decade": s["decade"],
                "key": s["key"],
                "mode": s["mode"],
                "raw_chords": s["chords"],
                "ht_section": s["section"],
            })
            print(f"  ✅ [{s['decade']}] {s['title']} | Key: {s['key']} {s['mode']}")

    df = pd.DataFrame(rows)
    
    print("\n" + "=" * 60)
    print("수집 완료 통계")
    print("=" * 60)
    print(f"  대상 아티스트 수: {total_artists}")
    print(f"  총 수집 곡 수: {len(df)}")
    
    if not df.empty:
        df["key"] = df["key"].fillna("C")
        df["mode"] = df["mode"].fillna("major")
        df["raw_chords"] = df["raw_chords"].fillna("C G Am F")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n✅ 최종 데이터셋 저장 완료: {output_path}")
    else:
        print("\n❌ 수집된 데이터가 없습니다.")
        
    return df

def main():
    parser = argparse.ArgumentParser(description="코드 진행 분석 데이터 수집기")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--pilot", action="store_true", help="파일럿 모드: Nirvana, Taylor Swift, NewJeans")
    group.add_argument("--all", action="store_true", help="전체 모드: 100명 전체 아티스트 수집")
    group.add_argument("--artist", type=str, help="특정 아티스트만 수집 (예: 'Radiohead')")
    parser.add_argument("--output", type=str, default=OUTPUT_CSV, help="출력 CSV 파일 경로")
    args = parser.parse_args()
    
    all_artists = list(ARTIST_SONGS.keys())
    
    if args.pilot:
        target = ["Nirvana", "Taylor Swift", "NewJeans"]
        print("▶ 파일럿 모드\n")
    elif args.artist:
        if args.artist in all_artists:
            target = [args.artist]
        else:
            print(f"'{args.artist}'가 목록에 없습니다.")
            return
        print(f"▶ 단일 아티스트 모드: {args.artist}\n")
    else:
        target = all_artists
        print(f"▶ 전체 모드: {len(target)}명 전체 아티스트\n")
        
    run_collection(target_artists=target, output_path=args.output)

if __name__ == "__main__":
    main()
