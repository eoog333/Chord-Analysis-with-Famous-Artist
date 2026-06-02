"""
patch_notebook_remove_spotify.py
=================================
chord_progression_analysis.ipynb에서 Spotify 오디오 피처 참조를
모두 제거하고, 화성(Hooktheory) 피처만 사용하도록 패치합니다.

변경 대상:
  - 셀 7 (인덱스 6): all_features에서 spotify_* 컬럼 제거
  - 셀 13 (인덱스 12): 레이더 차트에서 spotify_* 피처 제거

실행:
    python patch_notebook_remove_spotify.py
"""

import json
import os

NOTEBOOK_PATH = "chord_progression_analysis.ipynb"

# ─── 셀 7 (인덱스 6): 피처 목록 및 스케일링 ────────────────────────────────────
NEW_CELL_7 = [
    "# 4. 화성 피처 스케일링\n",
    "# (Spotify 오디오 피처 제거 — 화성 피처(feat_*)만 분석에 사용)\n",
    "all_features = [\n",
    "    'feat_unique_chords', 'feat_non_diatonic_ratio', 'feat_minor_ratio',\n",
    "    'feat_tension_ratio', 'feat_transition_freq'\n",
    "]\n",
    "\n",
    "# Min-Max Scaling 진행 (각 피처들을 0과 1사이로 정규화하여 가중치 동등화)\n",
    "scaler = MinMaxScaler()\n",
    "df_scaled = df_processed.copy()\n",
    "df_scaled[all_features] = scaler.fit_transform(df_processed[all_features])\n",
    "\n",
    "print(\"피처 정규화(Min-Max Scaling)가 완료되었습니다.\")\n",
    "print(df_scaled[all_features].describe().loc[['mean', 'min', 'max']])\n",
]

# ─── 셀 13 (인덱스 12): 레이더 차트 ────────────────────────────────────────────
NEW_CELL_13 = [
    "# 7. 대표 아티스트 페르소나 레이더 차트 (Plotly)\n",
    "target_artists = ['Radiohead', 'Taylor Swift', 'Billie Eilish']\n",
    "radar_features = [\n",
    "    'feat_unique_chords', 'feat_non_diatonic_ratio',\n",
    "    'feat_tension_ratio', 'feat_minor_ratio', 'feat_transition_freq'\n",
    "]\n",
    "\n",
    "# 아티스트별 평균 데이터 준비\n",
    "df_artist_avg = df_scaled.groupby('artist')[radar_features].mean()\n",
    "\n",
    "# target_artists 중 실제로 데이터에 존재하는 아티스트만 필터링\n",
    "available_artists = [a for a in target_artists if a in df_artist_avg.index]\n",
    "if not available_artists:\n",
    "    available_artists = df_artist_avg.index.tolist()[:3]\n",
    "\n",
    "fig = go.Figure()\n",
    "\n",
    "for artist in available_artists:\n",
    "    values = df_artist_avg.loc[artist].tolist()\n",
    "    # 레이더 차트의 닫힌 루프를 위해 첫 번째 원소를 끝에 복사\n",
    "    values.append(values[0])\n",
    "    categories = [f.replace('feat_', '') for f in radar_features]\n",
    "    categories.append(categories[0])\n",
    "\n",
    "    fig.add_trace(go.Scatterpolar(\n",
    "        r=values,\n",
    "        theta=categories,\n",
    "        fill='toself',\n",
    "        name=artist\n",
    "    ))\n",
    "\n",
    "fig.update_layout(\n",
    "    polar=dict(\n",
    "        radialaxis=dict(\n",
    "            visible=True,\n",
    "            range=[0, 1]\n",
    "        )),\n",
    "    showlegend=True,\n",
    "    title=\"대표 아티스트의 화성적 페르소나 레이더 차트 비교 (화성 피처 기반)\"\n",
    ")\n",
    "fig.show()\n",
]


def patch_notebook():
    if not os.path.exists(NOTEBOOK_PATH):
        print(f"오류: {NOTEBOOK_PATH} 파일을 찾을 수 없습니다.")
        return

    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    patched_cells = []

    for i, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))

        # 셀 7: Spotify 오디오 피처 + 스케일링 셀
        if "spotify_energy" in source and "all_features" in source and "MinMaxScaler" in source:
            cells[i]["source"] = NEW_CELL_7
            cells[i]["outputs"] = []
            cells[i]["execution_count"] = None
            cells[i]["metadata"] = {}
            patched_cells.append(i + 1)
            print(f"✅ 셀 [{i+1}] 패치 완료 — 피처 목록에서 spotify_* 제거")

        # 셀 13: 레이더 차트 셀
        elif "radar_features" in source and "spotify_energy" in source:
            cells[i]["source"] = NEW_CELL_13
            cells[i]["outputs"] = []
            cells[i]["execution_count"] = None
            cells[i]["metadata"] = {}
            patched_cells.append(i + 1)
            print(f"✅ 셀 [{i+1}] 패치 완료 — 레이더 차트에서 spotify_* 피처 제거")

    if not patched_cells:
        print("⚠  패치 대상 셀을 찾지 못했습니다. 이미 패치되었거나 셀 구조가 변경된 것일 수 있습니다.")
        return

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)

    print(f"\n✅ 노트북 패치 완료: {NOTEBOOK_PATH}")
    print(f"   수정된 셀: {patched_cells}")
    print("\n변경 사항:")
    print("  - all_features: spotify_energy, spotify_valence, spotify_tempo, spotify_acousticness, spotify_danceability 제거")
    print("  - 레이더 차트: spotify_energy, spotify_valence 제거 → 화성 피처(feat_*)만 사용")


if __name__ == "__main__":
    patch_notebook()
