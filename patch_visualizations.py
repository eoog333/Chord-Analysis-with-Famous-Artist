import json

NOTEBOOK_PATH = 'chord_progression_analysis.ipynb'

with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# ── 셀 9: Boxplot 업데이트 ──────────────────────────────────────────────────
CELL9_SOURCE = [
    "# 5-1. 주요 아티스트별 핵심 화성 지표 분포 시각화 (Phase 1 / Q1)\n",
    "# 곡 수가 많은 상위 10명 아티스트를 기준으로 아티스트별 화성 특징 차이를 확인합니다.\n",
    "top_artists = df_processed['artist'].value_counts().head(10).index\n",
    "df_top = df_processed[df_processed['artist'].isin(top_artists)]\n",
    "\n",
    "fig, axes = plt.subplots(1, 3, figsize=(24, 7))\n",
    "\n",
    "# 1. 분위기 (명도 지수)\n",
    "sns.boxplot(data=df_top, x='artist', y='feat_brightness', ax=axes[0], palette='Set2')\n",
    "axes[0].set_title(\"주요 아티스트별 명도 지수(Brightness) 분포\", fontsize=14, pad=10)\n",
    "axes[0].set_ylabel(\"Brightness Ratio\")\n",
    "axes[0].tick_params(axis='x', rotation=45)\n",
    "\n",
    "# 2. 움직임 에너지 (도약 진행)\n",
    "sns.boxplot(data=df_top, x='artist', y='feat_leap_motion', ax=axes[1], palette='Set3')\n",
    "axes[1].set_title(\"주요 아티스트별 도약 진행(Leap Motion) 비율 분포\", fontsize=14, pad=10)\n",
    "axes[1].set_ylabel(\"Leap Motion Ratio\")\n",
    "axes[1].tick_params(axis='x', rotation=45)\n",
    "\n",
    "# 3. 화성 어법 (변격 종지)\n",
    "sns.boxplot(data=df_top, x='artist', y='feat_cadence_plagal', ax=axes[2], palette='Pastel1')\n",
    "axes[2].set_title(\"주요 아티스트별 변격종지(Plagal Cadence) 비율 분포\", fontsize=14, pad=10)\n",
    "axes[2].set_ylabel(\"Plagal Cadence (4->1) Ratio\")\n",
    "axes[2].tick_params(axis='x', rotation=45)\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()\n",
    "\n",
    "artist_summary = df_top.groupby('artist')[['feat_brightness', 'feat_leap_motion', 'feat_cadence_plagal']].mean().round(3)\n",
    "print(\"=== 주요 아티스트별 평균 화성 피처 ===\")\n",
    "print(artist_summary)\n"
]
nb['cells'][9]['source'] = CELL9_SOURCE
nb['cells'][9]['outputs'] = []

# ── 셀 12: Radar Chart 업데이트 ──────────────────────────────────────────────
CELL12_SOURCE = [
    "# 5-2. 대표 아티스트 페르소나 레이더 차트 (Phase 1 / Q1)\n",
    "target_artists = ['Radiohead', 'Taylor Swift', 'Billie Eilish']\n",
    "\n",
    "# 피처 이름 예쁘게 매핑\n",
    "feature_labels = {\n",
    "    'feat_brightness': 'Brightness(명도)', \n",
    "    'feat_minor_ratio': 'Minor(어두움)', \n",
    "    'feat_tension_ratio': 'Tension(텐션)',\n",
    "    'feat_step_motion': 'Step Motion(순차)', \n",
    "    'feat_leap_motion': 'Leap Motion(도약)',\n",
    "    'feat_cadence_perfect': 'Perfect Cadence(5->1)', \n",
    "    'feat_cadence_plagal': 'Plagal Cadence(4->1)', \n",
    "    'feat_cadence_deceptive': 'Deceptive Cad.(5->6)',\n",
    "    'feat_cadence_half': 'Half Cadence(->5)'\n",
    "}\n",
    "\n",
    "radar_features = clustering_features\n",
    "df_artist_avg = df_cluster.groupby('artist_base')[radar_features].mean()\n",
    "categories = [feature_labels.get(f, f) for f in radar_features]\n",
    "\n",
    "fig = go.Figure()\n",
    "\n",
    "colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']\n",
    "\n",
    "for i, artist in enumerate(target_artists):\n",
    "    if artist in df_artist_avg.index:\n",
    "        values = df_artist_avg.loc[artist].values.tolist()\n",
    "        values += values[:1]  # 원형으로 닫기 위해 첫 값 추가\n",
    "        cat_closed = categories + [categories[0]]\n",
    "        \n",
    "        fig.add_trace(go.Scatterpolar(\n",
    "            r=values,\n",
    "            theta=cat_closed,\n",
    "            fill='toself',\n",
    "            name=artist,\n",
    "            line=dict(color=colors[i], width=2),\n",
    "            fillcolor=colors[i],\n",
    "            opacity=0.3\n",
    "        ))\n",
    "\n",
    "fig.update_layout(\n",
    "  polar=dict(\n",
    "    radialaxis=dict(visible=True, range=[0, 1])\n",
    "  ),\n",
    "  showlegend=True,\n",
    "  title=dict(text=\"대표 아티스트 화성 페르소나 비교\", font=dict(size=20), x=0.5)\n",
    ")\n",
    "fig.show()\n"
]
nb['cells'][12]['source'] = CELL12_SOURCE
nb['cells'][12]['outputs'] = []

# ── 셀 13: 마크다운 ────────────────────────────────────────────────────────
CELL13_SOURCE = [
    "### Phase 2. 아티스트별 종지(Cadence) 선호도 프로파일링 (Q1 보조 근거)\n",
    "곡 내에서 코드 진행의 마무리를 어떻게 처리하는지는 음악적 장르와 느낌을 결정짓는 강력한 요소입니다. 각 아티스트가 **4대 종지(정격, 변격, 위, 반종지)**를 어느 정도 비율로 사용하는지 100% 누적 막대 그래프로 시각화하여, '취향의 지문'을 확인합니다.\n"
]
nb['cells'][13]['source'] = CELL13_SOURCE

# ── 셀 14: Stacked Bar Chart (4대 종지) ──────────────────────────────────────
CELL14_SOURCE = [
    "# 6. 타겟 아티스트별 종지(Cadence) 선호도 100% 누적 막대 그래프 (Phase 2 / Q1)\n",
    "cadence_cols = ['feat_cadence_perfect', 'feat_cadence_plagal', 'feat_cadence_deceptive', 'feat_cadence_half']\n",
    "cadence_names = ['Perfect (5->1)', 'Plagal (4->1)', 'Deceptive (5->6)', 'Half (->5)']\n",
    "\n",
    "target_artists = ['Radiohead', 'Taylor Swift', 'The Weeknd', 'Nirvana']\n",
    "\n",
    "cadence_data = []\n",
    "for artist in target_artists:\n",
    "    if artist in df_processed['artist'].values:\n",
    "        means = df_processed[df_processed['artist'] == artist][cadence_cols].mean()\n",
    "        total = means.sum()\n",
    "        if total > 0:\n",
    "            normalized = (means / total) * 100\n",
    "            cadence_data.append(normalized.tolist())\n",
    "        else:\n",
    "            cadence_data.append([0, 0, 0, 0])\n",
    "\n",
    "df_cadence = pd.DataFrame(cadence_data, index=target_artists, columns=cadence_names)\n",
    "\n",
    "ax = df_cadence.plot(kind='bar', stacked=True, figsize=(12, 7), colormap='Set2', edgecolor='white')\n",
    "\n",
    "plt.title(\"아티스트별 4대 화성 종지(Cadence) 사용 점유율 (100% 누적)\", fontsize=16, pad=15)\n",
    "plt.ylabel(\"점유율 (%)\", fontsize=12)\n",
    "plt.xlabel(\"아티스트\", fontsize=12)\n",
    "plt.xticks(rotation=0, fontsize=11)\n",
    "plt.legend(title=\"종지 종류\", bbox_to_anchor=(1.05, 1), loc='upper left')\n",
    "\n",
    "# 막대 안에 텍스트 추가\n",
    "for p in ax.patches:\n",
    "    width, height = p.get_width(), p.get_height()\n",
    "    x, y = p.get_xy() \n",
    "    if height > 5:\n",
    "        ax.text(x+width/2, y+height/2, f'{height:.1f}%', \n",
    "                horizontalalignment='center', verticalalignment='center',\n",
    "                fontsize=10, color='white', fontweight='bold')\n",
    "\n",
    "plt.tight_layout()\n",
    "plt.show()\n"
]
nb['cells'][14]['source'] = CELL14_SOURCE
nb['cells'][14]['outputs'] = []

# ── 셀 16: Random Forest ───────────────────────────────────────────────────
CELL16_SOURCE = [
    "# 7. Random Forest 기반 아티스트 스타일 설명력 분석 (Phase 3 / Q2)\n",
    "from sklearn.model_selection import train_test_split\n",
    "from sklearn.ensemble import RandomForestClassifier\n",
    "from sklearn.metrics import confusion_matrix\n",
    "import numpy as np\n",
    "\n",
    "# (1) 아티스트 분류 타겟 설정 및 모델 학습\n",
    "artist_counts = df_scaled['artist'].value_counts()\n",
    "top_50_artists = artist_counts[artist_counts >= 15].index\n",
    "df_rf = df_scaled[df_scaled['artist'].isin(top_50_artists)].copy()\n",
    "\n",
    "X = df_rf[all_features]\n",
    "y = df_rf['artist']\n",
    "\n",
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\n",
    "\n",
    "rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight='balanced')\n",
    "rf.fit(X_train, y_train)\n",
    "acc = rf.score(X_test, y_test)\n",
    "print(f\"상위 50명 아티스트 분류 정확도: {acc*100:.2f}%\")\n",
    "print(\"(화성 특징만으로 분류하므로 높지 않으나, Baseline 대비 유의미한지 확인)\")\n",
    "\n",
    "# (2) Feature Importance 추출 및 시각화\n",
    "importances = rf.feature_importances_\n",
    "feature_labels_map = {\n",
    "    'feat_brightness': 'Brightness',\n",
    "    'feat_minor_ratio': 'Minor Ratio',\n",
    "    'feat_tension_ratio': 'Tension Ratio',\n",
    "    'feat_step_motion': 'Step Motion',\n",
    "    'feat_leap_motion': 'Leap Motion',\n",
    "    'feat_cadence_perfect': 'Perfect Cadence',\n",
    "    'feat_cadence_plagal': 'Plagal Cadence',\n",
    "    'feat_cadence_deceptive': 'Deceptive Cad.',\n",
    "    'feat_cadence_half': 'Half Cadence'\n",
    "}\n",
    "clean_features = [feature_labels_map.get(f, f) for f in all_features]\n",
    "\n",
    "indices = np.argsort(importances)[::-1]\n",
    "\n",
    "plt.figure(figsize=(10, 6))\n",
    "sns.barplot(x=importances[indices], y=np.array(clean_features)[indices], palette='viridis')\n",
    "plt.title(\"아티스트 스타일 분류에 중요한 화성 피처 (Feature Importance)\", fontsize=14, pad=10)\n",
    "plt.xlabel(\"중요도 (Importance)\")\n",
    "plt.show()\n",
    "\n",
    "# (3) Confusion Matrix 기반 Top 5 오분류 쌍 추출 (추천 시스템 힌트)\n",
    "y_pred = rf.predict(X_test)\n",
    "cm = confusion_matrix(y_test, y_pred, labels=rf.classes_)\n",
    "np.fill_diagonal(cm, 0) # 정답 제거\n",
    "\n",
    "misclassified_pairs = []\n",
    "for i in range(len(rf.classes_)):\n",
    "    for j in range(len(rf.classes_)):\n",
    "        if i != j and cm[i, j] > 0:\n",
    "            misclassified_pairs.append((rf.classes_[i], rf.classes_[j], cm[i, j]))\n",
    "\n",
    "misclassified_pairs.sort(key=lambda x: x[2], reverse=True)\n",
    "print(\"\\n[화성 구조가 너무 비슷해서 모델이 헷갈린 아티스트 쌍 Top 5]\")\n",
    "for pair in misclassified_pairs[:5]:\n",
    "    print(f\"- {pair[0]} 를 {pair[1]} 로 오해함 (발생: {pair[2]}번) -> [음악적 유사도 높음]\")\n"
]
nb['cells'][16]['source'] = CELL16_SOURCE
nb['cells'][16]['outputs'] = []

# ── 셀 18: K-Means ─────────────────────────────────────────────────────────
CELL18_SOURCE = [
    "# 8. K-Means 기반 유사 아티스트 탐색 및 클러스터 프로파일링 (Phase 4 / Q3)\n",
    "if 'artist_features' not in globals():\n",
    "    # 앞에서 실행하지 않았을 경우를 대비\n",
    "    df_cluster = df_scaled.copy()\n",
    "    df_cluster['artist_base'] = df_cluster['artist'].apply(lambda x: x.split(' (')[0])\n",
    "    artist_features = df_cluster.groupby('artist_base')[clustering_features].mean()\n",
    "\n",
    "kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)\n",
    "clusters = kmeans.fit_predict(artist_features)\n",
    "artist_features['Cluster'] = clusters\n",
    "\n",
    "cluster_centers = pd.DataFrame(kmeans.cluster_centers_, columns=clustering_features)\n",
    "\n",
    "print(\"=== 클러스터별 대표 아티스트 (최대 5명) ===\")\n",
    "for c in range(5):\n",
    "    members = artist_features[artist_features['Cluster'] == c].index.tolist()\n",
    "    print(f\"\\nCluster {c} (총 {len(members)}명): {', '.join(members[:5])} ...\")\n",
    "    \n",
    "    # 클러스터 중심값 중 가장 높은 피처 추출\n",
    "    top_feats_idx = np.argsort(cluster_centers.loc[c].values)[::-1][:3]\n",
    "    top_feats = [clustering_features[i] for i in top_feats_idx]\n",
    "    clean_top_feats = [feature_labels_map.get(f, f) for f in top_feats]\n",
    "    print(f\"  -> 특징: {', '.join(clean_top_feats)} 수치가 두드러짐\")\n"
]
nb['cells'][18]['source'] = CELL18_SOURCE
nb['cells'][18]['outputs'] = []

# ── 셀 20: 부가 분석 (시대별 트렌드) ─────────────────────────────────────────
CELL20_SOURCE = [
    "# 9. 부가 분석: 시대별 화성 지표 평균 변화\n",
    "# 이 결과는 데이터셋의 배경 경향을 설명하는 보조 분석입니다.\n",
    "decade_trends = df_processed.groupby('decade')[['feat_brightness', 'feat_cadence_plagal', 'feat_tension_ratio']].mean()\n",
    "decade_trends = decade_trends[decade_trends.index >= 1960] # 60년대 이후만\n",
    "\n",
    "plt.figure(figsize=(10, 6))\n",
    "plt.plot(decade_trends.index, decade_trends['feat_brightness'], marker='o', linewidth=2, label='Brightness (명도)')\n",
    "plt.plot(decade_trends.index, decade_trends['feat_cadence_plagal'], marker='s', linewidth=2, label='Plagal Cadence (변격종지)')\n",
    "plt.plot(decade_trends.index, decade_trends['feat_tension_ratio'], marker='^', linewidth=2, label='Tension Ratio (텐션)')\n",
    "\n",
    "plt.title(\"시대별(Decade) 대중음악 화성 트렌드 변화\", fontsize=16, pad=15)\n",
    "plt.xlabel(\"Decade\", fontsize=12)\n",
    "plt.ylabel(\"평균 수치\", fontsize=12)\n",
    "plt.grid(True, linestyle='--', alpha=0.7)\n",
    "plt.legend(fontsize=11)\n",
    "plt.show()\n"
]
nb['cells'][20]['source'] = CELL20_SOURCE
nb['cells'][20]['outputs'] = []

with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ 모든 시각화 및 모델링 셀 업데이트 완료!")
