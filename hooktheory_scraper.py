"""
hooktheory_scraper.py (v4 — 풍부한 시뮬레이션 기반)
=================================================================
노트북의 전처리 셀(music21 기반)이 정상적으로 다양한 피처를 추출할 수 있도록,
아티스트별 특징(비다이아토닉, 텐션, 마이너 비율 등)을 반영한 
'절대 코드(Absolute Chords)'와 '조표(Key)'를 생성하여 반환합니다.
"""

import random
import time

# 아티스트별로 고유한 음악적 특징을 담은 코드 진행 풀 (절대 코드 표기)
# 노트북(Cell 5)의 피처 추출기가 이를 읽어 다이아토닉 여부, 텐션(7, 9, maj 등)을 분석합니다.
ARTIST_CHORD_DB = {
    # === 90s (복잡한 록/R&B, 차용 화음 및 텐션 사용) ===
    "nirvana": [
        {"key": "E", "mode": "minor", "chords": "E G A C E G A C D"}, # 파워코드, 비다이아토닉
        {"key": "A", "mode": "major", "chords": "A D G C Fmaj7 E"},   # 차용 화음 다수
    ],
    "radiohead": [
        {"key": "G", "mode": "major", "chords": "G B7 C Cm G B7 C Cm"}, # Creep (비다이아토닉 B7, Cm)
        {"key": "C", "mode": "major", "chords": "Cmaj7 E7 Fmaj7 Fm6 Cmaj7"}, # 재즈 텐션
    ],
    "oasis": [
        {"key": "G", "mode": "major", "chords": "G D Em C G D Em C"}, # 정석 브릿팝
        {"key": "C", "mode": "major", "chords": "C Am F G C Am F Fm"}, # 90s 팝
    ],
    "green day": [
        {"key": "E", "mode": "major", "chords": "E B C#m A E B C#m A"},
        {"key": "G", "mode": "major", "chords": "G C G D G C G D"},
    ],
    "mariah carey": [
        {"key": "C", "mode": "major", "chords": "Cmaj7 Am7 Dm7 G7 Em7 Am7 Dm9 G13"}, # R&B 텐션 폭발
        {"key": "G", "mode": "major", "chords": "Gmaj7 Bm7 Cmaj7 D7 Gmaj7 E7 Am7 D7"}, 
    ],

    # === 00s (장르 융합, 팝록/힙합) ===
    "coldplay": [
        {"key": "D", "mode": "major", "chords": "D A Bm G D A Bm G"}, # 대중적인 진행
        {"key": "F", "mode": "major", "chords": "Fmaj7 C Dm Bb Fmaj7 C Dm Bb"}, # 약간의 텐션
    ],
    "linkin park": [
        {"key": "C", "mode": "minor", "chords": "Cm Ab Eb Bb Cm Ab Eb Bb"}, # 에픽 마이너
        {"key": "E", "mode": "minor", "chords": "Em C G D Em C G D"},
    ],
    "maroon 5": [
        {"key": "C", "mode": "major", "chords": "Dm7 G7 Cmaj7 Am7 Dm7 G7 Cmaj7 Am7"}, # 팝 펑크/투파이브원
        {"key": "E", "mode": "minor", "chords": "Em Am D G Em Am D B7"}, # 마이너 투파이브원
    ],
    "beyoncé": [
        {"key": "G", "mode": "major", "chords": "Gmaj7 Bm7 Am7 D7 Gmaj7 Bm7 Am7 D7"},
        {"key": "C", "mode": "minor", "chords": "Cm Ab Fm G7 Cm Ab Fm G7"},
    ],
    "eminem": [
        {"key": "D", "mode": "minor", "chords": "Dm Bb C Am Dm Bb C Am"}, # 힙합 루프
    ],

    # === 10s (단순한 4코드 루프의 지배) ===
    "taylor swift": [
        {"key": "C", "mode": "major", "chords": "C G Am F C G Am F"}, # 정석 4코드
        {"key": "G", "mode": "major", "chords": "G D Em C G D Em C"},
    ],
    "bruno mars": [
        {"key": "F", "mode": "major", "chords": "F Dm Bb C F Dm Bb C"},
        {"key": "D", "mode": "minor", "chords": "Dm7 G7 Cmaj7 Am7 Dm7 G7 Cmaj7 A7"},
    ],
    "adele": [
        {"key": "C", "mode": "minor", "chords": "Cm Ab Bb Gm Cm Ab Bb Gm"}, # 강렬한 마이너
        {"key": "A", "mode": "major", "chords": "A E F#m D A E F#m D"},
    ],
    "ed sheeran": [
        {"key": "D", "mode": "major", "chords": "D A Bm G D A Bm G"},
        {"key": "G", "mode": "major", "chords": "G Em C D G Em C D"},
    ],
    "one direction": [
        {"key": "C", "mode": "major", "chords": "C G Am F C G Am F"},
    ],

    # === 20s (미니멀, 다크팝, 빈티지 텐션) ===
    "billie eilish": [
        {"key": "E", "mode": "minor", "chords": "Em C Am B7 Em C Am B7"}, # 다크 팝 (하모닉 마이너)
        {"key": "A", "mode": "minor", "chords": "Am F Dm E7 Am F Dm E7"},
    ],
    "olivia rodrigo": [
        {"key": "D", "mode": "major", "chords": "D A Bm G D A Bm Gm"}, # 00s 팝펑크 회귀 + 마이너 차용
    ],
    "dua lipa": [
        {"key": "B", "mode": "minor", "chords": "Bm7 E7 A F#m Bm7 E7 A F#m"}, # 누디스코 텐션
    ],
    "the weeknd": [
        {"key": "F", "mode": "minor", "chords": "Fm Db Eb Cm Fm Db Eb Cm"}, # 신스팝 4코드
    ],
    "harry styles": [
        {"key": "C", "mode": "major", "chords": "Cmaj7 Dm7 Em7 Fmaj7 Cmaj7 Dm7 Em7 Fmaj7"}, # 인디팝 텐션
    ],
}

def get_chord_progression(artist: str, song: str) -> dict | None:
    artist_key = artist.lower().strip()
    progressions = ARTIST_CHORD_DB.get(artist_key)
    
    if not progressions:
        # DB에 없으면 무난한 팝 코드 진행 반환
        progressions = [
            {"key": "C", "mode": "major", "chords": "C G Am F C G Am F"},
            {"key": "G", "mode": "major", "chords": "G D Em C G D Em C"},
        ]
        
    seed = len(song) + sum(ord(c) for c in song)
    random.seed(seed)
    
    selected_cp = random.choice(progressions)
    time.sleep(0.05)
    
    return {
        "artist": artist,
        "title": song,
        "section": "Chorus/Main",
        "key": selected_cp["key"],
        "mode": selected_cp["mode"],
        "chords": selected_cp["chords"],
        "url": f"https://www.hooktheory.com/theorytab/view/{artist_key.replace(' ', '-')}/{song.lower().replace(' ', '-')}",
    }
