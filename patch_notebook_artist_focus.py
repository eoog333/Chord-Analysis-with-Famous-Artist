import json

with open('chord_progression_analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 8: Phase 1 Boxplots
cell_8_source = """# 5. 주요 아티스트별 화성 지표(Minor Ratio, Tension Ratio) 분포 시각화 (Phase 1)
# 가장 곡 수가 많은 상위 10명 아티스트 추출
top_artists = df_processed['artist'].value_counts().head(10).index
df_top = df_processed[df_processed['artist'].isin(top_artists)]

fig, axes = plt.subplots(1, 2, figsize=(20, 7))

sns.boxplot(data=df_top, x='artist', y='feat_minor_ratio', ax=axes[0], palette='Set2')
axes[0].set_title("주요 아티스트별 마이너 화음 비율 (Minor Ratio) 분포", fontsize=14, pad=10)
axes[0].tick_params(axis='x', rotation=45)

sns.boxplot(data=df_top, x='artist', y='feat_tension_ratio', ax=axes[1], palette='Set3')
axes[1].set_title("주요 아티스트별 텐션 화음 비율 (Tension Ratio) 분포", fontsize=14, pad=10)
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()
"""

# Cell 10 & 11: K-Means setup
# We will just fix df_cluster['artist_base'] since '(20s)' tag is gone.
cell_10_source = """# 6. K-Means 군집 분석 및 클러스터 프로파일링 (Phase 4)

# 군집화용 핵심 피처 리스트 (화성 기본 특성)
clustering_features = [
    'feat_unique_chords', 'feat_non_diatonic_ratio', 
    'feat_minor_ratio', 'feat_tension_ratio'
]

# 1. 곡 단위가 아닌 "아티스트 단위"로 평균 화성 피처 벡터를 생성
artist_features = df_scaled.groupby('artist')[clustering_features].mean()

# 2. K-Means 실행 (최적 K=4로 설정 - 장르/스타일 다변화를 고려)
optimal_k = 4
kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
artist_features['cluster'] = kmeans.fit_predict(artist_features)

print("=== K-Means 클러스터링 결과 (유사 아티스트 그룹) ===")
for i in range(optimal_k):
    cluster_artists = artist_features[artist_features['cluster'] == i].index.tolist()
    print(f"\\n[Cluster {i}] ({len(cluster_artists)}명):")
    print(", ".join(cluster_artists[:10]) + ("..." if len(cluster_artists) > 10 else ""))
"""

# Cell 14: Network Analysis (Phase 2)
cell_14_source = """# 8. 특정 타겟 아티스트별 핵심 코드 전이 네트워크 비교 분석 (Phase 2)
target_artists = ['Radiohead', 'Taylor Swift', 'The Weeknd', 'Nirvana']
fig, axes = plt.subplots(2, 2, figsize=(20, 16))

for idx, artist in enumerate(target_artists):
    ax = axes[idx // 2][idx % 2]
    G = nx.DiGraph()
    
    # 해당 아티스트의 곡 필터링
    artist_seqs = df_processed[df_processed['artist'] == artist]['rn_sequence']
    
    # 아티스트별 bigram 빈도 계산
    artist_bigrams = Counter()
    for seq in artist_seqs:
        if len(seq) > 1:
            for i in range(len(seq) - 1):
                artist_bigrams[f"{seq[i]}->{seq[i+1]}"] += 1
                
    if not artist_bigrams:
        continue
        
    # 상위 12개 패턴 추출
    top_edges = artist_bigrams.most_common(12)
    max_weight = top_edges[0][1] if top_edges else 1
    
    for edge_str, weight in top_edges:
        u, v = edge_str.split('->')
        G.add_edge(u, v, weight=weight)
        
    pos = nx.spring_layout(G, k=1.5, seed=42)
    
    edges = G.edges(data=True)
    edge_weights = [d['weight'] / max_weight * 5 for u, v, d in edges]
    
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=1500, node_color='lightcoral', edgecolors='black')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_weight='bold')
    nx.draw_networkx_edges(G, pos, ax=ax, arrowstyle='-|>', arrowsize=15, width=edge_weights, edge_color='gray', connectionstyle='arc3,rad=0.1')
    
    edge_labels = {(u, v): d['weight'] for u, v, d in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, ax=ax)
    
    ax.set_title(f"{artist}의 주요 코드 진행 네트워크", fontsize=16, fontweight='bold', pad=15)
    ax.axis('off')

plt.tight_layout()
plt.show()
"""

# Cell 15: Random Forest & Confusion Matrix (Phase 3)
cell_15_source = """# 9. Random Forest 기반 아티스트 스타일 설명력 분석 (Phase 3)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
import numpy as np

# (1) 전체 Feature 간 상관관계 히트맵 (Correlation Heatmap)
plt.figure(figsize=(14, 12))
corr = df_scaled[all_features].corr()
sns.heatmap(corr, annot=False, cmap='coolwarm', fmt=".2f")
plt.title("화성 피처(Feature) 간 상관관계 히트맵", fontsize=16)
plt.show()

# (2) 아티스트 분류 타겟 설정 및 모델 학습
artist_counts = df_scaled['artist'].value_counts()
valid_artists = artist_counts[artist_counts >= 5].index
df_rf = df_scaled[df_scaled['artist'].isin(valid_artists)]

X = df_rf[all_features]
y = df_rf['artist']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

rf_model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
rf_model.fit(X_train, y_train)

# (3) Feature Importance 추출 및 시각화
importances = rf_model.feature_importances_
indices = np.argsort(importances)[-15:] # Top 15
plt.figure(figsize=(10, 8))
plt.barh(range(len(indices)), importances[indices], color='mediumpurple', align='center')
plt.yticks(range(len(indices)), [all_features[i] for i in indices])
plt.title("아티스트 스타일 구분에 가장 중요한 화성 피처 (Top 15)", fontsize=14)
plt.xlabel("Feature Importance")
plt.show()

# (4) Confusion Matrix 기반 Top 5 오분류 쌍 추출 (추천 시스템 근거)
y_pred = rf_model.predict(X_test)
cm = confusion_matrix(y_test, y_pred, labels=rf_model.classes_)
np.fill_diagonal(cm, 0) # 정답(대각선) 제외

misclassifications = []
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        if cm[i, j] > 0:
            misclassifications.append({
                'True Artist': rf_model.classes_[i],
                'Predicted As': rf_model.classes_[j],
                'Confusion Count': cm[i, j]
            })

import pandas as pd
mis_df = pd.DataFrame(misclassifications).sort_values(by='Confusion Count', ascending=False)
print("=== Top 5 화성적 유사 아티스트 쌍 (모델이 자주 혼동하는 대상) ===")
print("이 오분류 데이터는 내용 기반(Content-based) 음악 추천 알고리즘의 강력한 유사도 근거가 될 수 있습니다.\\n")
print(mis_df.head(10).to_string(index=False))
"""

# Replace the cells
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if "decade_trends = df_processed.groupby('decade')" in source:
            cell['source'] = [cell_8_source]
        elif "clustering_features =" in source and "optimal_k = 3" in source:
            cell['source'] = [cell_10_source]
        elif "decades = ['90s', '00s', '10s', '20s']" in source and "G = nx.DiGraph()" in source:
            cell['source'] = [cell_14_source]
        elif "y = df_scaled['decade']" in source and "RandomForestClassifier" in source:
            cell['source'] = [cell_15_source]

with open('chord_progression_analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Code cells patched successfully!")
