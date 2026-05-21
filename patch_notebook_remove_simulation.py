import json

NOTEBOOK_PATH = "chord_progression_analysis.ipynb"

def remove_simulation_cell():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "code":
            source = "".join(cell.get("source", []))
            if "def generate_simulation_dataset():" in source:
                new_source = [
                    "# 2. 데이터 로딩: 수집된 데이터(collected_data.csv) 로드\n",
                    "\n",
                    "import os\n",
                    "import pandas as pd\n",
                    "\n",
                    "REAL_DATA_PATH = 'collected_data.csv'\n",
                    "\n",
                    "if not os.path.exists(REAL_DATA_PATH):\n",
                    "    raise FileNotFoundError(f\"{REAL_DATA_PATH} 파일이 없습니다. 먼저 데이터 수집 스크립트를 실행해주세요.\")\n",
                    "\n",
                    "df_songs = pd.read_csv(REAL_DATA_PATH)\n",
                    "\n",
                    "# CSV 컬럼명을 노트북 파이프라인 형식에 맞게 통일\n",
                    "if 'mode' in df_songs.columns:\n",
                    "    # key + mode → 단일 key 컬럼으로 합치기 (minor일 경우 소문자)\n",
                    "    df_songs['key'] = df_songs.apply(\n",
                    "        lambda r: r['key'] + 'm' if str(r.get('mode', 'major')).lower() == 'minor' else r['key'],\n",
                    "        axis=1\n",
                    "    )\n",
                    "\n",
                    "print(f\"✅ 데이터 로드 완료: {REAL_DATA_PATH}\")\n",
                    "print(f\"   총 {len(df_songs)}곡 | 아티스트: {df_songs['artist'].nunique()}명\")\n",
                    "\n",
                    "display(df_songs.head(5))\n"
                ]
                cell["source"] = new_source
                print(f"✅ Cell {i}의 시뮬레이션 코드를 깔끔하게 제거하고 데이터 로딩 코드로 대체했습니다.")

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    remove_simulation_cell()
