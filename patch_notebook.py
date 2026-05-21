"""
patch_notebook.py
=================
chord_progression_analysis.ipynb의 Data Collection 셀을
실제 데이터(collected_data.csv) 우선 로딩 방식으로 패치합니다.

실행:
    python patch_notebook.py
"""

import json
import os

NOTEBOOK_PATH = "chord_progression_analysis.ipynb"

# 교체할 새 Data Collection 셀의 소스 코드
NEW_DATA_CELL_SOURCE = [
    "# 2. 데이터 로딩: 실제 수집 데이터(collected_data.csv) 우선, 없으면 시뮬레이션\n",
    "\n",
    "import os\n",
    "\n",
    "REAL_DATA_PATH = 'collected_data.csv'\n",
    "USE_REAL_DATA = os.path.exists(REAL_DATA_PATH)\n",
    "\n",
    "def generate_simulation_dataset():\n",
    "    \"\"\"\n",
    "    실제 대중음악의 역사적 흐름(90년대 복잡한 화성 -> 20년대 이지리스닝 루프화)\n",
    "    및 Spotify 오디오 특징 경향성을 음악학적으로 모델링하여 500곡의 고품질 가상 데이터셋을 생성합니다.\n",
    "    (collected_data.csv가 없을 때 자동 사용되는 오프라인 모드)\n",
    "    \"\"\"\n",
    "    random.seed(42)\n",
    "    np.random.seed(42)\n",
    "    \n",
    "    artists_by_decade = {\n",
    "        '90s': ['Nirvana', 'Radiohead', 'Oasis', 'Green Day', 'Mariah Carey'],\n",
    "        '00s': ['Coldplay', 'Linkin Park', 'Maroon 5', 'Beyoncé', 'Eminem'],\n",
    "        '10s': ['Taylor Swift', 'Bruno Mars', 'Adele', 'Ed Sheeran', 'One Direction'],\n",
    "        '20s': ['Billie Eilish', 'Olivia Rodrigo', 'Dua Lipa', 'The Weeknd', 'Harry Styles']\n",
    "    }\n",
    "    \n",
    "    chord_pool = {\n",
    "        '90s': {\n",
    "            'major_keys': ['C', 'G', 'D', 'A', 'F', 'Bb'],\n",
    "            'minor_keys': ['Am', 'Em', 'Dm', 'F#m'],\n",
    "            'chords_maj': ['Cmaj7', 'Dm7', 'Em7', 'Fmaj7', 'G7', 'Am7', 'Bm7b5', 'E7', 'A7', 'D7', 'Fm6', 'Bb7', 'Dbmaj7'],\n",
    "            'chords_min': ['Am7', 'Bm7b5', 'Cmaj7', 'Dm7', 'E7', 'Fmaj7', 'G7', 'C7', 'F7', 'Bb7', 'Ddim']\n",
    "        },\n",
    "        '00s': {\n",
    "            'major_keys': ['C', 'G', 'D', 'F'],\n",
    "            'minor_keys': ['Am', 'Em', 'Bm', 'F#m'],\n",
    "            'chords_maj': ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'E7', 'A7', 'D7', 'Fm', 'Fmaj7', 'G7'],\n",
    "            'chords_min': ['Am', 'Bm7b5', 'C', 'Dm', 'E7', 'F', 'G', 'G#dim']\n",
    "        },\n",
    "        '10s': {\n",
    "            'major_keys': ['C', 'G', 'D', 'A'],\n",
    "            'minor_keys': ['Am', 'Em'],\n",
    "            'chords_maj': ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'Fmaj7', 'G7', 'E7'],\n",
    "            'chords_min': ['Am', 'F', 'C', 'G', 'Dm', 'E7']\n",
    "        },\n",
    "        '20s': {\n",
    "            'major_keys': ['C', 'G', 'F'],\n",
    "            'minor_keys': ['Am', 'Em'],\n",
    "            'chords_maj': ['C', 'Dm', 'Em', 'F', 'G', 'Am', 'Fmaj7', 'Em7', 'G7'],\n",
    "            'chords_min': ['Am', 'F', 'C', 'G']\n",
    "        }\n",
    "    }\n",
    "    \n",
    "    data = []\n",
    "    for decade, artists in artists_by_decade.items():\n",
    "        for artist in artists:\n",
    "            for song_idx in range(1, 26):\n",
    "                song_title = f\"Song_{song_idx}\"\n",
    "                if decade == '90s': year = random.randint(1990, 1999)\n",
    "                elif decade == '00s': year = random.randint(2000, 2009)\n",
    "                elif decade == '10s': year = random.randint(2010, 2019)\n",
    "                else: year = random.randint(2020, 2026)\n",
    "                \n",
    "                is_minor = random.random() < 0.3\n",
    "                pool = chord_pool[decade]\n",
    "                if is_minor:\n",
    "                    song_key = random.choice(pool['minor_keys'])\n",
    "                    ch_list = pool['chords_min']\n",
    "                else:\n",
    "                    song_key = random.choice(pool['major_keys'])\n",
    "                    ch_list = pool['chords_maj']\n",
    "                \n",
    "                if decade == '90s': prog_len = random.randint(8, 16)\n",
    "                elif decade == '00s': prog_len = random.randint(6, 12)\n",
    "                elif decade == '10s': prog_len = random.choice([4, 8])\n",
    "                else: prog_len = 4\n",
    "                \n",
    "                prog = [random.choice(ch_list) for _ in range(prog_len if decade in ['90s','00s'] else 4)]\n",
    "                if decade == '20s':\n",
    "                    if is_minor: prog = ['Am', 'F', 'C', 'G'] if random.random() < 0.7 else ['Am', 'Dm', 'F', 'E7']\n",
    "                    else: prog = ['Fmaj7', 'G', 'Em7', 'Am7'] if random.random() < 0.5 else ['C', 'G', 'Am', 'F']\n",
    "                \n",
    "                num_loops = random.randint(4, 8) if decade in ['90s', '00s'] else random.randint(8, 16)\n",
    "                raw_chords_str = ' '.join(prog * num_loops)\n",
    "                \n",
    "                if decade == '90s':\n",
    "                    energy=np.random.normal(0.60,0.12); valence=np.random.normal(0.55,0.15)\n",
    "                    tempo=np.random.normal(110,20); acousticness=np.random.normal(0.35,0.15)\n",
    "                    danceability=np.random.normal(0.58,0.10); liveness=np.random.normal(0.18,0.08)\n",
    "                elif decade == '00s':\n",
    "                    energy=np.random.normal(0.70,0.10); valence=np.random.normal(0.50,0.12)\n",
    "                    tempo=np.random.normal(120,18); acousticness=np.random.normal(0.20,0.10)\n",
    "                    danceability=np.random.normal(0.62,0.08); liveness=np.random.normal(0.16,0.06)\n",
    "                elif decade == '10s':\n",
    "                    energy=np.random.normal(0.78,0.08); valence=np.random.normal(0.62,0.10)\n",
    "                    tempo=np.random.normal(122,15); acousticness=np.random.normal(0.12,0.08)\n",
    "                    danceability=np.random.normal(0.70,0.08); liveness=np.random.normal(0.15,0.05)\n",
    "                else:\n",
    "                    energy=np.random.normal(0.65,0.08); valence=np.random.normal(0.56,0.10)\n",
    "                    tempo=np.random.normal(118,12); acousticness=np.random.normal(0.22,0.10)\n",
    "                    danceability=np.random.normal(0.72,0.07); liveness=np.random.normal(0.14,0.04)\n",
    "                \n",
    "                data.append({\n",
    "                    'artist': artist, 'title': song_title, 'year': year, 'decade': decade,\n",
    "                    'key': song_key, 'raw_chords': raw_chords_str,\n",
    "                    'spotify_energy': max(0, min(1, energy)),\n",
    "                    'spotify_valence': max(0, min(1, valence)),\n",
    "                    'spotify_tempo': max(60.0, min(200.0, tempo)),\n",
    "                    'spotify_acousticness': max(0, min(1, acousticness)),\n",
    "                    'spotify_danceability': max(0, min(1, danceability)),\n",
    "                    'spotify_liveness': max(0, min(1, liveness))\n",
    "                })\n",
    "    return pd.DataFrame(data)\n",
    "\n",
    "\n",
    "# ─── 실제 데이터 vs 시뮬레이션 분기 ──────────────────────────────────\n",
    "if USE_REAL_DATA:\n",
    "    df_songs = pd.read_csv(REAL_DATA_PATH)\n",
    "    # CSV 컬럼명을 노트북 파이프라인 형식에 맞게 통일\n",
    "    if 'mode' in df_songs.columns:\n",
    "        # key + mode → 단일 key 컬럼으로 합치기 (minor일 경우 소문자)\n",
    "        df_songs['key'] = df_songs.apply(\n",
    "            lambda r: r['key'] + 'm' if str(r.get('mode', 'major')).lower() == 'minor' else r['key'],\n",
    "            axis=1\n",
    "        )\n",
    "    print(f\"✅ 실제 데이터 로드 완료: {REAL_DATA_PATH}\")\n",
    "    print(f\"   총 {len(df_songs)}곡 | 아티스트: {df_songs['artist'].nunique()}명\")\n",
    "else:\n",
    "    df_songs = generate_simulation_dataset()\n",
    "    print(\"⚠  collected_data.csv 없음 → 시뮬레이션 모드로 실행합니다.\")\n",
    "    print(\"   실제 데이터를 사용하려면: python data_collector.py --pilot\")\n",
    "\n",
    "print(\"\\n데이터 샘플:\")\n",
    "display(df_songs.head(5))"
]

def patch_notebook():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"오류: {NOTEBOOK_PATH} 파일을 찾을 수 없습니다.")
        return

    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    patched = False

    for i, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        # 대상 셀 식별: generate_simulation_dataset 정의를 포함하는 셀
        if "generate_simulation_dataset" in source and "API 설정" in source:
            cells[i]["source"] = NEW_DATA_CELL_SOURCE
            cells[i]["outputs"] = []
            cells[i]["execution_count"] = None
            # metadata 정리
            cells[i]["metadata"] = {}
            patched = True
            print(f"✅ 셀 {i+1} 패치 완료 (Data Collection 셀)")
            break

    if not patched:
        print("⚠  패치 대상 셀을 찾지 못했습니다. 수동으로 확인이 필요합니다.")
        return

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    print(f"\n노트북 업데이트 완료: {NOTEBOOK_PATH}")
    print("이제 data_collector.py 실행 후 노트북을 열면 실제 데이터가 자동 로드됩니다.")

if __name__ == "__main__":
    patch_notebook()
