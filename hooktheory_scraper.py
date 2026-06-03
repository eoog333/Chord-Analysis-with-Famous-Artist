"""
hooktheory_scraper.py (v6 — 실제 TheoryTab 웹 스크래핑 및 곡 단위 발매 연대 매핑)
=================================================================
Hooktheory TheoryTab 페이지에서 실제 코드 진행 데이터를 수집합니다.
Spotify API를 사용하지 않고, 각 곡의 발매 시점(decade)을 
직접 하드코딩하여 관리합니다. (힙합 아티스트 제외 및 교체 완료)
"""

import re
import time
import random
import requests

# =============================================================================
# sind → 절대 코드명 변환 유틸리티
# =============================================================================

_NOTE_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
_MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]

_TONIC_ST = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
    'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11,
}

_MAJOR_MINOR_DEGREES = {2, 3, 6}
_MAJOR_DIM_DEGREES   = {7}
_MINOR_MINOR_DEGREES = {1, 4, 5}
_MINOR_DIM_DEGREES   = {2}


def _sind_to_chord(sind: str, tonic: str, scale: str) -> str:
    root_st = _TONIC_ST.get(tonic.split()[0], 0)
    s_intervals = _MAJOR_SCALE if scale == 'major' else _MINOR_SCALE

    prefix = ''
    s = sind

    if s.startswith('b') and len(s) > 1 and s[1].isdigit():
        prefix = 'b'
        s = s[1:]
    elif s.startswith('#') and len(s) > 1 and s[1].isdigit():
        prefix = '#'
        s = s[1:]
    elif s.startswith('M'):
        prefix = 'M'
        s = s[1:]
    elif s.startswith(('D', 'L')):
        return tonic.split()[0]

    deg_m = re.match(r'^(\d)', s)
    if not deg_m:
        return tonic.split()[0]

    degree = int(deg_m.group(1))
    if not (1 <= degree <= 7):
        return tonic.split()[0]

    scale_st = s_intervals[degree - 1]
    if prefix == 'b':
        scale_st -= 1
    elif prefix == '#':
        scale_st += 1

    chord_root = _NOTE_NAMES[(root_st + scale_st) % 12]

    if scale == 'major':
        is_minor = (degree in _MAJOR_MINOR_DEGREES) and prefix == ''
        is_dim   = (degree in _MAJOR_DIM_DEGREES) and prefix == ''
    else:
        is_minor = (degree in _MINOR_MINOR_DEGREES) and prefix == ''
        is_dim   = (degree in _MINOR_DIM_DEGREES) and prefix == ''

    if prefix == 'M':
        quality = ''
    elif is_dim:
        quality = 'dim'
    elif is_minor:
        quality = 'm'
    else:
        quality = ''

    rest = s[1:]
    tension = ''
    if 'add9' in rest: tension = 'add9'
    elif 'sus4' in rest: tension = 'sus4'
    elif 'sus2' in rest: tension = 'sus2'
    elif 'maj7' in rest.lower(): tension = 'maj7'
    elif '13' in rest: tension = '13'
    elif '11' in rest: tension = '11'
    elif '9' in rest: tension = '9'
    elif '7' in rest: tension = '7'
    elif '6' in rest and degree != 6: tension = '6'

    return chord_root + quality + tension


def sind_sequence_to_chords(sind_seq: str, tonic: str, scale: str) -> str:
    result = []
    for token in sind_seq.split():
        base_sind = token.split('/')[0]
        chord = _sind_to_chord(base_sind, tonic, scale)
        result.append(chord)
    return ' '.join(result)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE_URL = "https://www.hooktheory.com/theorytab/view"

# =============================================================================
# 아티스트 및 곡 단위 수동 발매 시대 (Decade) 매핑
# 형식: "아티스트명": [("아티스트슬러그", "곡슬러그", "실제발매Decade")]
# 힙합 아티스트(Tupac, Snoop Dogg 등)는 모두 팝/록/인디로 교체되었습니다.
# =============================================================================
from massive_song_list import ARTIST_SONGS

def fetch_chords_from_url(artist_slug: str, song_slug: str) -> dict | None:
    url = f"{BASE_URL}/{artist_slug}/{song_slug}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        content = resp.text

        chords = re.findall(
            r'data-chord-label\s+data-sind="([^"]+)"\s+data-tonic="([^"]+)"\s+data-scale="([^"]+)"',
            content
        )
        if not chords:
            return None

        _, tonic, scale = chords[0]
        sind_seq = " ".join([c[0] for c in chords])
        chord_sequence = sind_sequence_to_chords(sind_seq, tonic, scale)

        section_match = re.search(
            r'(Verse|Chorus|Pre-Chorus|Bridge|Intro|Outro|Hook)',
            content[:50000],
            re.IGNORECASE
        )
        section = section_match.group(1) if section_match else "Main"

        return {
            "key": tonic,
            "mode": scale,
            "chords": chord_sequence,
            "relative_chords": sind_seq,
            "section": section,
            "url": url,
        }
    except Exception as e:
        print(f"    ⚠  요청 오류: {e}")
        return None

def get_all_songs_for_artist(artist: str) -> list:
    """
    해당 아티스트의 모든 곡 데이터를 수집하여 리스트로 반환합니다.
    이때 각 곡마다 하드코딩된 'decade'가 결과 딕셔너리에 포함됩니다.
    """
    song_list = ARTIST_SONGS.get(artist)
    if not song_list:
        print(f"    ⚠  ARTIST_SONGS에 {artist} 없음")
        return []

    results = []
    for artist_slug, song_slug, decade in song_list:
        print(f"    → {artist_slug}/{song_slug} ({decade}) 시도...")
        res = fetch_chords_from_url(artist_slug, song_slug)
        time.sleep(random.uniform(0.8, 1.5))  # Rate-limit 준수

        if res:
            results.append({
                "artist": artist,
                "title": song_slug.replace("-", " ").title(),
                "decade": decade,
                "section": res["section"],
                "key": res["key"],
                "mode": res["mode"],
                "chords": res["chords"],
                "relative_chords": res["relative_chords"],
                "url": res["url"],
            })
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("TheoryTab 실제 스크래핑 테스트 (곡 단위 / 하드코딩 시대)")
    print("=" * 60)
    test_artists = ["Nirvana", "Taylor Swift", "NewJeans"]
    for artist in test_artists:
        print(f"\n[{artist}]")
        songs = get_all_songs_for_artist(artist)
        for s in songs:
            print(f"  ✅ [{s['decade']}] {s['title']} | Key: {s['key']} {s['mode']}")
            print(f"     Chords: {s['chords'][:50]}...")
