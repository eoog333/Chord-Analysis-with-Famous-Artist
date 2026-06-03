#!/usr/bin/env python3
"""
chord_progression_analysis.ipynb 패치 스크립트
- 셀 3 (bigram 전이 피처) → 코드 진행 움직임 + 반복 패턴 피처로 교체
- 셀 4 (all_features) → 새 피처명 반영
- 섹션 3.2 마크다운 주석 업데이트
"""
import json, re, sys

NOTEBOOK_PATH = "chord_progression_analysis.ipynb"

# ── 새 셀 3 소스 ────────────────────────────────────────────────────────────
NEW_CELL3_SOURCE = [
    "# 3. 로마숫자 변환기 및 피처 추출 함수 정의\n",
    "\n",
    "def clean_chord_for_music21(chord_name):\n",
    "    c = str(chord_name).split('/')[0] # 베이스음 생략\n",
    "    c = c.replace('min', 'm').replace('maj', 'Maj')\n",
    "    return c\n",
    "\n",
    "def convert_to_roman_numeral(chord_name, key_str):\n",
    "    is_minor_key = key_str.endswith('m')\n",
    "    key_name = key_str[:-1].lower() if is_minor_key else key_str.upper()\n",
    "    try:\n",
    "        k_obj = key.Key(key_name) if not is_minor_key else key.Key(key_name, 'minor')\n",
    "        c_clean = clean_chord_for_music21(chord_name)\n",
    "        cs = harmony.ChordSymbol(c_clean)\n",
    "        rn = roman.romanNumeralFromChord(cs, k_obj)\n",
    "        return rn\n",
    "    except Exception:\n",
    "        return None\n",
    "\n",
    "def extract_base_features_and_sequence(row):\n",
    "    chords = str(row['raw_chords']).split()\n",
    "    key_str = row['key']\n",
    "    is_minor_key = key_str.endswith('m')\n",
    "\n",
    "    rn_objects = []\n",
    "    for c in chords:\n",
    "        rn = convert_to_roman_numeral(c, key_str)\n",
    "        if rn is not None:\n",
    "            rn_objects.append((c, rn))\n",
    "\n",
    "    if not rn_objects:\n",
    "        return pd.Series([0.0, 0.0, 0.0, 0.0, []], \n",
    "                         index=['feat_unique_chords', 'feat_non_diatonic_ratio', \n",
    "                                'feat_minor_ratio', 'feat_tension_ratio', 'rn_sequence'])\n",
    "\n",
    "    total_chords = len(rn_objects)\n",
    "    unique_chords = len(set([c[0] for c in rn_objects]))\n",
    "    feat_unique_chords = unique_chords / total_chords\n",
    "\n",
    "    major_diatonic = {'I', 'ii', 'iii', 'IV', 'V', 'vi', 'viio', 'vii°'}\n",
    "    minor_diatonic = {'i', 'iio', 'ii°', 'bIII', 'III', 'iv', 'v', 'V', 'bVI', 'VI', 'bVII', 'VII'}\n",
    "\n",
    "    non_diatonic_count = 0\n",
    "    minor_count = 0\n",
    "    tension_count = 0\n",
    "\n",
    "    rn_sequence = []\n",
    "    for c_name, rn in rn_objects:\n",
    "        fig = rn.figure\n",
    "        rn_sequence.append(fig)\n",
    "        base_fig = rn.romanNumeralAlone\n",
    "\n",
    "        if is_minor_key:\n",
    "            is_diatonic = any(fig.startswith(d) for d in minor_diatonic)\n",
    "        else:\n",
    "            is_diatonic = any(fig.startswith(d) for d in major_diatonic)\n",
    "\n",
    "        if not is_diatonic:\n",
    "            non_diatonic_count += 1\n",
    "\n",
    "        if rn.romanNumeralAlone.islower():\n",
    "            minor_count += 1\n",
    "\n",
    "        c_lower = c_name.lower()\n",
    "        import re\n",
    "        tension_keywords = ['7', '9', '11', '13', 'add', '6']\n",
    "        has_tension = any(x in c_lower for x in tension_keywords)\n",
    "        if 'maj' in c_lower:\n",
    "            has_tension = has_tension or bool(re.search(r'maj\\d', c_lower))\n",
    "\n",
    "        if has_tension:\n",
    "            tension_count += 1\n",
    "\n",
    "    feat_non_diatonic_ratio = non_diatonic_count / total_chords\n",
    "    feat_minor_ratio = minor_count / total_chords\n",
    "    feat_tension_ratio = tension_count / total_chords\n",
    "\n",
    "    return pd.Series([feat_unique_chords, feat_non_diatonic_ratio, \n",
    "                      feat_minor_ratio, feat_tension_ratio, rn_sequence], \n",
    "                     index=['feat_unique_chords', 'feat_non_diatonic_ratio', \n",
    "                            'feat_minor_ratio', 'feat_tension_ratio', 'rn_sequence'])\n",
    "\n",
    "print(\"피처 추출 엔진 빌드가 완료되었습니다. 전처리를 시작합니다...\")\n",
    "df_base = df_songs.apply(extract_base_features_and_sequence, axis=1)\n",
    "df_processed = pd.concat([df_songs, df_base], axis=1)\n",
    "\n",
    "# ── 코드 진행 패턴 기반 피처 추출 ─────────────────────────────────────────\n",
    "from collections import Counter\n",
    "import re as _re\n",
    "\n",
    "ROMA_TO_DEGREE = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}\n",
    "\n",
    "def figure_to_degree(figure):\n",
    "    \"\"\"로마숫자 figure → 스케일 도수(1~7). 파싱 불가 시 None 반환.\"\"\"\n",
    "    fig = _re.sub(r'^[b#]+', '', str(figure))\n",
    "    m = _re.match(r'([IViv]+)', fig)\n",
    "    if not m:\n",
    "        return None\n",
    "    return ROMA_TO_DEGREE.get(m.group(1).upper())\n",
    "\n",
    "def find_dominant_pattern(seq, min_len=2, max_len=4):\n",
    "    \"\"\"곡 내에서 가장 지배적으로 반복되는 진행 패턴 반환 (가변 길이 2~4코드).\"\"\"\n",
    "    best_pattern, best_score = None, 0\n",
    "    for ws in range(min_len, max_len + 1):\n",
    "        if len(seq) < ws:\n",
    "            continue\n",
    "        windows = [tuple(seq[i:i+ws]) for i in range(len(seq) - ws + 1)]\n",
    "        top_pattern, count = Counter(windows).most_common(1)[0]\n",
    "        score = count * ws  # 길이 가중치: 더 긴 패턴이 반복되면 우대\n",
    "        if score > best_score:\n",
    "            best_score = score\n",
    "            best_pattern = top_pattern\n",
    "    return best_pattern\n",
    "\n",
    "def extract_progression_features(degree_seq):\n",
    "    \"\"\"스케일 도수 시퀀스에서 코드 진행 움직임 피처 추출.\"\"\"\n",
    "    if len(degree_seq) < 2:\n",
    "        return {'feat_avg_step': 0.0, 'feat_max_step': 0.0,\n",
    "                'feat_direction_change': 0.0, 'feat_fifth_ratio': 0.0}\n",
    "    steps = []\n",
    "    for i in range(len(degree_seq) - 1):\n",
    "        diff = degree_seq[i+1] - degree_seq[i]\n",
    "        # 스케일 7도 기준 최단 경로 정규화 (-3 ~ +3)\n",
    "        while diff > 3:  diff -= 7\n",
    "        while diff < -3: diff += 7\n",
    "        steps.append(diff)\n",
    "    steps_abs = [abs(s) for s in steps]\n",
    "    feat_avg_step         = sum(steps_abs) / len(steps_abs)\n",
    "    feat_max_step         = float(max(steps_abs))\n",
    "    directions = [1 if s > 0 else (-1 if s < 0 else 0) for s in steps]\n",
    "    changes = sum(1 for i in range(1, len(directions))\n",
    "                  if directions[i] != 0 and directions[i-1] != 0\n",
    "                  and directions[i] != directions[i-1])\n",
    "    feat_direction_change = changes / max(len(directions) - 1, 1)\n",
    "    # 4도·5도 이동 = 기능화성의 핵심 움직임 (I→V, V→I, IV→I 등)\n",
    "    feat_fifth_ratio = sum(1 for s in steps_abs if s in [3, 4]) / len(steps)\n",
    "    return {\n",
    "        'feat_avg_step': feat_avg_step,\n",
    "        'feat_max_step': feat_max_step,\n",
    "        'feat_direction_change': feat_direction_change,\n",
    "        'feat_fifth_ratio': feat_fifth_ratio\n",
    "    }\n",
    "\n",
    "# ── 스케일 도수 시퀀스 변환 ─────────────────────────────────────────────────\n",
    "df_processed['degree_sequence'] = df_processed['rn_sequence'].apply(\n",
    "    lambda seq: [d for d in (figure_to_degree(f) for f in seq) if d is not None]\n",
    ")\n",
    "\n",
    "# ── 진행 움직임 피처 추출 ──────────────────────────────────────────────────\n",
    "prog_feats = df_processed['degree_sequence'].apply(extract_progression_features)\n",
    "df_prog = pd.DataFrame(prog_feats.tolist())\n",
    "df_processed = pd.concat([df_processed, df_prog], axis=1)\n",
    "print(\"✅ 코드 진행 움직임 피처 추출 완료 (avg_step / max_step / direction_change / fifth_ratio)\")\n",
    "\n",
    "# ── 핵심 반복 패턴 탐지 ────────────────────────────────────────────────────\n",
    "df_processed['dominant_pattern'] = df_processed['degree_sequence'].apply(\n",
    "    lambda seq: find_dominant_pattern(seq) if len(seq) >= 2 else None\n",
    ")\n",
    "\n",
    "all_dominant = Counter(df_processed['dominant_pattern'].dropna())\n",
    "top_20_patterns = [item[0] for item in all_dominant.most_common(20)]\n",
    "print(\"선정된 상위 20개 핵심 코드 진행 패턴 (스케일 도수):\")\n",
    "print(top_20_patterns)\n",
    "\n",
    "# 곡별: Top 20 패턴의 등장 비율 피처 생성\n",
    "pattern_features = []\n",
    "for _, row in df_processed.iterrows():\n",
    "    song_feats = {}\n",
    "    seq = row['degree_sequence']\n",
    "    for pat in top_20_patterns:\n",
    "        pat_len = len(pat)\n",
    "        feat_name = f\"feat_pat_{'_'.join(map(str, pat))}\"\n",
    "        total_windows = len(seq) - pat_len + 1\n",
    "        if total_windows > 0:\n",
    "            count = sum(1 for i in range(total_windows)\n",
    "                        if tuple(seq[i:i+pat_len]) == pat)\n",
    "            song_feats[feat_name] = count / total_windows\n",
    "        else:\n",
    "            song_feats[feat_name] = 0.0\n",
    "    pattern_features.append(song_feats)\n",
    "\n",
    "df_patterns = pd.DataFrame(pattern_features)\n",
    "df_processed = pd.concat([df_processed, df_patterns], axis=1)\n",
    "print(\"✅ 핵심 반복 진행 패턴 피처 추출 완료!\")\n",
]

# ── 새 셀 4 소스 (all_features) ────────────────────────────────────────────
NEW_CELL4_SOURCE = [
    "# 4. 화성 피처 스케일링\n",
    "# 보조 피처(화성 구성) + 주요 피처(진행 움직임) + 주요 피처(반복 패턴)\n",
    "all_features = [\n",
    "    # 보조: 화성 구성\n",
    "    'feat_unique_chords', 'feat_non_diatonic_ratio',\n",
    "    'feat_minor_ratio', 'feat_tension_ratio',\n",
    "    # 주요: 진행 움직임\n",
    "    'feat_avg_step', 'feat_max_step', 'feat_direction_change', 'feat_fifth_ratio',\n",
    "] + [f\"feat_pat_{'_'.join(map(str, pat))}\" for pat in top_20_patterns]\n",
    "\n",
    "scaler = MinMaxScaler()\n",
    "df_scaled = df_processed.copy()\n",
    "df_scaled[all_features] = scaler.fit_transform(df_scaled[all_features])\n",
    "\n",
    "print(\"피처 정규화(Min-Max Scaling)가 완료되었습니다.\")\n",
]

# ── 노트북 로드 ────────────────────────────────────────────────────────────
with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']
print(f"총 셀 수: {len(cells)}")

# ── 셀 탐색: bigram 키워드로 셀 3 위치 특정 ──────────────────────────────
cell3_idx = None
cell4_idx = None

for i, cell in enumerate(cells):
    src = ''.join(cell.get('source', []))
    if 'top_20_bigrams' in src or 'all_bigrams' in src:
        cell3_idx = i
        print(f"셀 3 (bigram) 발견: 인덱스 {i}")
    if 'feat_transition_freq' in src and 'all_features' in src:
        cell4_idx = i
        print(f"셀 4 (all_features) 발견: 인덱스 {i}")

# ── 없으면 extract_base_features 포함 셀에 합쳐서 교체 ───────────────────
if cell3_idx is None:
    for i, cell in enumerate(cells):
        src = ''.join(cell.get('source', []))
        if 'extract_base_features_and_sequence' in src:
            cell3_idx = i
            print(f"셀 3 (extract_base) 발견: 인덱스 {i}")
            break

if cell3_idx is None:
    print("❌ 대상 셀을 찾지 못했습니다.")
    sys.exit(1)

# ── 셀 3 교체 ─────────────────────────────────────────────────────────────
cells[cell3_idx]['source'] = NEW_CELL3_SOURCE
cells[cell3_idx]['cell_type'] = 'code'
cells[cell3_idx]['outputs'] = []
cells[cell3_idx]['execution_count'] = None
print(f"✅ 셀 {cell3_idx} 교체 완료")

# ── 셀 4 교체 ─────────────────────────────────────────────────────────────
if cell4_idx is not None:
    cells[cell4_idx]['source'] = NEW_CELL4_SOURCE
    cells[cell4_idx]['outputs'] = []
    cells[cell4_idx]['execution_count'] = None
    print(f"✅ 셀 {cell4_idx} 교체 완료")
else:
    # all_features가 있는 다음 셀 탐색
    for i in range(cell3_idx + 1, min(cell3_idx + 5, len(cells))):
        src = ''.join(cells[i].get('source', []))
        if 'all_features' in src or 'MinMaxScaler' in src:
            cells[i]['source'] = NEW_CELL4_SOURCE
            cells[i]['outputs'] = []
            cells[i]['execution_count'] = None
            print(f"✅ 셀 {i} (all_features) 교체 완료")
            break

# ── 마크다운 셀 3.2 설명 업데이트 ─────────────────────────────────────────
for i, cell in enumerate(cells):
    if cell.get('cell_type') == 'markdown':
        src = ''.join(cell.get('source', []))
        if 'feat_tr_{A}' in src or 'Bigram' in src:
            new_md = [
                "### 3.2 핵심 화성 피처 및 코드 진행 패턴 피처 추출\n",
                "#### 보조 피처 — 화성 구성(Harmonic Composition)\n",
                "- **`feat_unique_chords`**: 전체 코드 중 고유한 코드 종류의 비율 (코드 다양성)\n",
                "- **`feat_non_diatonic_ratio`**: 비다이아토닉(차용화음) 비율\n",
                "- **`feat_minor_ratio`**: 마이너 코드 비율\n",
                "- **`feat_tension_ratio`**: 7th, 9th, 6th 등 텐션 코드 비율\n",
                "\n",
                "#### 주요 피처 — 코드 진행 움직임(Progression Movement)\n",
                "- **`feat_avg_step`**: 연속 코드 간 평균 스케일 도수 이동 거리\n",
                "- **`feat_max_step`**: 한 곡 내 최대 도수 도약 크기\n",
                "- **`feat_direction_change`**: 진행 방향(상행/하행) 전환 비율 — 높을수록 불규칙\n",
                "- **`feat_fifth_ratio`**: 4도/5도 이동 비율 — 기능화성(Functional Harmony)적 움직임\n",
                "\n",
                "#### 주요 피처 — 핵심 반복 진행 패턴(Dominant Pattern)\n",
                "- **`feat_pat_{1}_{5}_{6}_{4}`** 등: 곡 내 가장 지배적으로 반복되는 코드 진행 패턴(스케일 도수)이\n",
                "  전체 상위 20개 패턴에 해당하는지 비율로 표현 (가변 길이 2~4코드 단위)\n",
            ]
            cells[i]['source'] = new_md
            print(f"✅ 마크다운 셀 {i} 업데이트 완료")
            break

# ── 저장 ──────────────────────────────────────────────────────────────────
with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("\n✅ 노트북 패치 완료:", NOTEBOOK_PATH)
