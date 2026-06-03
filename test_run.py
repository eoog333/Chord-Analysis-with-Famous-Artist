from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
# 1. 필수 라이브러리 임포트
import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import classification_report, accuracy_score
from music21 import roman, key, harmony
import networkx as nx

# 그래프 한글 폰트 설정 (Mac OS 기준)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", font="AppleGothic")

import warnings
warnings.filterwarnings('ignore')

print("모든 라이브러리가 성공적으로 로드되었습니다.")
# 2. 데이터 로딩 및 전처리: 수집된 데이터(collected_data.csv) 로드 및 정제

REAL_DATA_PATH = 'collected_data.csv'

if not os.path.exists(REAL_DATA_PATH):
    raise FileNotFoundError("데이터 파일이 없습니다. Hooktheory 크롤링 스크립트를 먼저 실행하세요.")

df_songs = pd.read_csv(REAL_DATA_PATH)

# 극단값 처리: 코드 수가 지나치게 적은 곡(4개 미만) 필터링
df_songs['chord_count'] = df_songs['raw_chords'].apply(lambda x: len(str(x).split()))
before_count = len(df_songs)
df_songs = df_songs[df_songs['chord_count'] >= 4].reset_index(drop=True)
print(f"코드 수 4개 미만 곡 {before_count - len(df_songs)}곡 제외 -> 최종 {len(df_songs)}곡 분석 대상")

# 모달 스케일(Dorian, Mixolydian 등) 처리
# 화성 분석 관례에 따라 minor 계열과 major 계열로 매핑합니다.
modal_to_minor = {'dorian', 'phrygian', 'aeolian'}
modal_to_major = {'mixolydian', 'lydian', 'ionian'}

def map_key(row):
    mode = str(row.get('mode', 'major')).lower()
    k = row['key']
    if mode == 'minor' or mode in modal_to_minor:
        return k + 'm'
    else:  # major, mixolydian, lydian 등
        return k

df_songs['key'] = df_songs.apply(map_key, axis=1)

print(f"데이터 로드 및 정제 완료: {REAL_DATA_PATH}")
print(f"   총 {len(df_songs)}곡 | 아티스트: {df_songs['artist'].nunique()}명")
# 3. 로마숫자 변환기 및 피처 추출 함수 정의

def clean_chord_for_music21(chord_name):
    c = str(chord_name).split('/')[0] # 베이스음 생략
    c = c.replace('min', 'm').replace('maj', 'Maj')
    return c

def convert_to_roman_numeral(chord_name, key_str):
    is_minor_key = key_str.endswith('m')
    key_name = key_str[:-1].lower() if is_minor_key else key_str.upper()
    try:
        k_obj = key.Key(key_name) if not is_minor_key else key.Key(key_name, 'minor')
        from music21 import harmony, roman, key
        c_clean = clean_chord_for_music21(chord_name)
        cs = harmony.ChordSymbol(c_clean)
        rn = roman.romanNumeralFromChord(cs, k_obj)
        return rn
    except Exception:
        return None

def extract_base_features_and_sequence(row):
    chords = str(row['raw_chords']).split()
    key_str = row['key']
    is_minor_key = key_str.endswith('m')

    rn_objects = []
    for c in chords:
        rn = convert_to_roman_numeral(c, key_str)
        if rn is not None:
            rn_objects.append((c, rn))

    if not rn_objects:
        return pd.Series([0.0, 0.0, 0.0, 0.0, 0.0, []], 
                         index=['feat_unique_chords', 'feat_non_diatonic_ratio', 
                                'feat_minor_ratio', 'feat_tension_ratio', 'feat_brightness', 'rn_sequence'])

    total_chords = len(rn_objects)
    unique_chords = len(set([c[0] for c in rn_objects]))
    feat_unique_chords = unique_chords / total_chords

    major_diatonic = {'I', 'ii', 'iii', 'IV', 'V', 'vi', 'viio', 'vii°'}
    minor_diatonic = {'i', 'iio', 'ii°', 'bIII', 'III', 'iv', 'v', 'V', 'bVI', 'VI', 'bVII', 'VII'}

    non_diatonic_count = 0
    minor_count = 0
    tension_count = 0
    major_diatonic_count = 0
    rn_sequence = []

    for c_name, rn in rn_objects:
        fig = rn.figure
        rn_sequence.append(fig)

        if is_minor_key:
            is_diatonic = any(fig.startswith(d) for d in minor_diatonic)
        else:
            is_diatonic = any(fig.startswith(d) for d in major_diatonic)
            
        if not is_diatonic:
            non_diatonic_count += 1

        is_minor_chord = rn.romanNumeralAlone.islower()
        if is_minor_chord:
            minor_count += 1
            
        # 밝기(Brightness)를 위한 메이저 다이아토닉 계산
        is_diminished = 'o' in fig or '°' in fig
        if is_diatonic and not is_minor_chord and not is_diminished:
            major_diatonic_count += 1

        c_lower = c_name.lower()
        import re
        tension_keywords = ['7', '9', '11', '13', 'add', '6']
        has_tension = any(x in c_lower for x in tension_keywords)
        if 'maj' in c_lower:
            has_tension = has_tension or bool(re.search(r'maj\d', c_lower))
        if has_tension:
            tension_count += 1

    feat_non_diatonic_ratio = non_diatonic_count / total_chords
    feat_minor_ratio        = minor_count / total_chords
    feat_tension_ratio      = tension_count / total_chords
    feat_brightness         = major_diatonic_count / total_chords

    return pd.Series([feat_unique_chords, feat_non_diatonic_ratio,
                      feat_minor_ratio, feat_tension_ratio, feat_brightness, rn_sequence],
                     index=['feat_unique_chords', 'feat_non_diatonic_ratio',
                            'feat_minor_ratio', 'feat_tension_ratio', 'feat_brightness', 'rn_sequence'])

print("피처 추출 엔진 빌드가 완료되었습니다. 전처리를 시작합니다...")
df_base = df_songs.apply(extract_base_features_and_sequence, axis=1)
df_processed = pd.concat([df_songs, df_base], axis=1)
print(f"✅ 보조 화성 피처 (명도 지수 포함) 추출 완료: {len(df_processed)}곡")

# ── 코드 진행 움직임 및 특정 화성 어법(Cadence) 추출 ────────────────────────
import re as _re

ROMA_TO_DEGREE = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}

def figure_to_degree(figure):
    """로마숫자 figure → 스케일 도수(1~7). 파싱 불가 시 None 반환."""
    fig = _re.sub(r'^[b#]+', '', str(figure))
    m = _re.match(r'([IViv]+)', fig)
    if not m:
        return None
    return ROMA_TO_DEGREE.get(m.group(1).upper())

def extract_progression_features(degree_seq):
    """스케일 도수 시퀀스에서 코드 진행 움직임 및 화성 어법(종지) 피처 추출."""
    if len(degree_seq) < 2:
        return {'feat_step_motion': 0.0, 'feat_leap_motion': 0.0,
                'feat_cadence_perfect': 0.0, 'feat_cadence_plagal': 0.0, 
                'feat_cadence_deceptive': 0.0, 'feat_cadence_half': 0.0}
                
    total_transitions = len(degree_seq) - 1
    step_count = 0
    leap_count = 0
    perfect_count = 0
    plagal_count = 0
    deceptive_count = 0
    half_count = 0
    
    for i in range(total_transitions):
        prev = degree_seq[i]
        curr = degree_seq[i+1]
        
        diff = curr - prev
        while diff > 3:  diff -= 7
        while diff < -3: diff += 7
        abs_diff = abs(diff)
        
        # 움직임 특성
        if abs_diff in [1, 2]:
            step_count += 1
        elif abs_diff in [3, 4]:
            leap_count += 1
            
        # 화성 어법(종지) 특성
        if prev == 5 and curr == 1:
            perfect_count += 1
        elif prev == 4 and curr == 1:
            plagal_count += 1
        elif prev == 5 and curr == 6:
            deceptive_count += 1
        elif curr == 5 and prev != 5:  # 반종지 (5도로 이동, 제자리걸음 제외)
            half_count += 1
            
    return {
        'feat_step_motion': step_count / total_transitions,
        'feat_leap_motion': leap_count / total_transitions,
        'feat_cadence_perfect': perfect_count / total_transitions,
        'feat_cadence_plagal': plagal_count / total_transitions,
        'feat_cadence_deceptive': deceptive_count / total_transitions,
        'feat_cadence_half': half_count / total_transitions
    }

# ── 스케일 도수 시퀀스 변환 ─────────────────────────────────────────────────
df_processed['degree_sequence'] = df_processed['rn_sequence'].apply(
    lambda seq: [d for d in (figure_to_degree(f) for f in seq) if d is not None]
)

# ── 진행 움직임 및 종지 피처 추출 ──────────────────────────────────────────
prog_feats = df_processed['degree_sequence'].apply(extract_progression_features)
df_prog = pd.DataFrame(prog_feats.tolist())
df_processed = pd.concat([df_processed, df_prog], axis=1)
print("✅ 코드 진행 움직임(Step/Leap) 및 4대 화성 어법(Cadence) 피처 추출 완료!")

# 4. 화성 피처 스케일링
all_features = [
    # 1. 분위기 (Mood)
    'feat_brightness', 'feat_minor_ratio', 'feat_tension_ratio',
    # 2. 움직임 에너지 (Motion Energy)
    'feat_step_motion', 'feat_leap_motion',
    # 3. 화성 어법/종지 (Functional Cadence)
    'feat_cadence_perfect', 'feat_cadence_plagal', 'feat_cadence_deceptive', 'feat_cadence_half'
]

scaler = MinMaxScaler()
df_scaled = df_processed.copy()
df_scaled[all_features] = scaler.fit_transform(df_scaled[all_features])

print(f"✅ 피처 정규화(Min-Max Scaling) 완료")
print(f"   적용된 총 피처 수: {len(all_features)}개")

# 5-1. 주요 아티스트별 핵심 화성 지표 분포 시각화 (Phase 1 / Q1)
# 곡 수가 많은 상위 10명 아티스트를 기준으로 아티스트별 화성 특징 차이를 확인합니다.
top_artists = df_processed['artist'].value_counts().head(10).index
df_top = df_processed[df_processed['artist'].isin(top_artists)]

fig, axes = plt.subplots(1, 3, figsize=(24, 7))

# 1. 분위기 (명도 지수)
sns.boxplot(data=df_top, x='artist', y='feat_brightness', ax=axes[0], palette='Set2')
axes[0].set_title("주요 아티스트별 명도 지수(Brightness) 분포", fontsize=14, pad=10)
axes[0].set_ylabel("Brightness Ratio")
axes[0].tick_params(axis='x', rotation=45)

# 2. 움직임 에너지 (도약 진행)
sns.boxplot(data=df_top, x='artist', y='feat_leap_motion', ax=axes[1], palette='Set3')
axes[1].set_title("주요 아티스트별 도약 진행(Leap Motion) 비율 분포", fontsize=14, pad=10)
axes[1].set_ylabel("Leap Motion Ratio")
axes[1].tick_params(axis='x', rotation=45)

# 3. 화성 어법 (변격 종지)
sns.boxplot(data=df_top, x='artist', y='feat_cadence_plagal', ax=axes[2], palette='Pastel1')
axes[2].set_title("주요 아티스트별 변격종지(Plagal Cadence) 비율 분포", fontsize=14, pad=10)
axes[2].set_ylabel("Plagal Cadence (4->1) Ratio")
axes[2].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.show()

artist_summary = df_top.groupby('artist')[['feat_brightness', 'feat_leap_motion', 'feat_cadence_plagal']].mean().round(3)
print("=== 주요 아티스트별 평균 화성 피처 ===")
print(artist_summary)

# 아티스트 단위 피처 행렬 생성 (레이더 차트 + K-Means 공통 사용)
clustering_features = [
    'feat_brightness', 'feat_minor_ratio', 'feat_tension_ratio',
    'feat_step_motion', 'feat_leap_motion',
    'feat_cadence_perfect', 'feat_cadence_plagal', 'feat_cadence_deceptive', 'feat_cadence_half'
]

df_cluster = df_scaled.copy()
df_cluster['artist_base'] = df_cluster['artist'].apply(lambda x: x.split(' (')[0])
artist_features = df_cluster.groupby('artist_base')[clustering_features].mean()
print(f"✅ 아티스트 단위 피처 행렬 생성 완료: {len(artist_features)}명")


print(artist_features.head())
