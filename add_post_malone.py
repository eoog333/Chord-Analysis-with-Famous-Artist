import pandas as pd
from hooktheory_scraper import fetch_chords_from_url
import time

OUTPUT_CSV = "collected_data.csv"

def main():
    print("Post Malone 재수집 시도 중...")
    result = fetch_chords_from_url("post-malone", "circles")
    
    if result:
        df = pd.read_csv(OUTPUT_CSV)
        new_row = {
            "artist": "Post Malone",
            "decade": "10s",
            "key": result["key"],
            "mode": result["mode"],
            "raw_chords": result["chords"],
            "ht_section": result["section"]
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
        print(f"✅ Post Malone 추가 완료! Key: {result['key']} {result['mode']}")
    else:
        print("❌ 데이터를 가져올 수 없습니다.")

if __name__ == "__main__":
    main()
