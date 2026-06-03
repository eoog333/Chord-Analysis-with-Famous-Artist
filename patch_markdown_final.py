import json

with open('chord_progression_analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Cell 0: Title and Introduction
cell_0_source = """# 텀 프로젝트: 대중음악 코드 진행 기반 아티스트 스타일 분석 및 유사 아티스트 탐색
### — 화성 데이터를 활용한 내용 기반 추천 시스템의 가능성

**학번**: 20211710  
**이름**: 정은광  
**과목**: 빅데이터 분석 2반  

---
## 1. 프로젝트 개요 및 연구 질문
기존의 음악 추천 시스템은 장르, 인기도, 협업 필터링 등에 주로 의존하며 음악 고유의 구조적 특성을 충분히 반영하지 못하는 한계가 있습니다. 본 프로젝트는 음악의 뼈대인 **코드 진행(Chord Progression)** 데이터를 분석하여, 화성 구조만으로 아티스트의 고유한 스타일을 규명하고 이를 내용 기반(Content-Based) 추천 시스템에 활용할 수 있는지 탐색합니다.

### 핵심 연구 질문
- **Q1. 아티스트마다 고유한 화성 특징이 존재하는가?**
- **Q2. 어떤 화성 특징이 아티스트 스타일을 설명하는 데 중요한 역할을 하는가?**
- **Q3. 코드 진행 특징만으로 유사한 음악적 스타일을 가진 아티스트를 탐색할 수 있는가?**
"""

# Cell 2: Data Collection
cell_2_source = """## 2. 데이터 확보 및 수집 (Data Collection)
통계적 유의성을 확보하고 아티스트의 고유 스타일을 추출하기 위해, Hooktheory 데이터베이스에서 **100여 명의 주요 팝 아티스트를 대상으로 아티스트당 최소 5곡 이상, 총 565곡**의 원본 스케일 도수(Scale Index) 데이터를 직접 수집하였습니다.

### 분석 대상 및 기준
- **수집 규모**: 총 102명 아티스트, 565곡 수집
- **수집 조건**: 특정 아티스트에 편향되지 않도록 균형 조정, 아티스트당 최소 5곡 이상 확보
- **시대적 범위**: 1990년대 ~ 2020년대 대중음악 전반
"""

# Conclusion cell (find the last markdown cell that looks like a conclusion or just the last markdown cell)
conclusion_source = """## 5. 결론 및 한계점 (Conclusion & Limitations)

### 5.1 최종 인사이트 및 실무적 기대효과
본 분석을 통해 코드 진행 데이터가 단순히 음악 이론적 구조를 넘어 **아티스트의 스타일을 구분하고 유사한 아티스트를 군집화할 수 있는 유의미한 정량적 지표**임을 확인했습니다.
- **음악 추천 시스템 고도화**: 화성적 유사성 기반의 K-Means 군집은 메타데이터(장르 등)에 의존하던 기존 추천 방식을 보완하는 차세대 내용 기반(Content-Based) 추천 시스템의 핵심 지표로 활용될 수 있습니다.
- **아티스트 스타일 정량화**: 모델의 Feature Importance와 Confusion Matrix의 오분류 패턴은 추상적이었던 '아티스트별 음악적 색깔'을 객관적으로 입증하는 강력한 근거가 됩니다.

### 5.2 한계점
- **분석 범위의 한계**: 본 연구는 멜로디, 리듬, 음색, 가사 등을 철저히 배제하고 오직 화성(Harmony) 정보만을 독립변수로 활용하였으므로, 전체 음악 스타일을 온전히 대변하기에는 한계가 존재합니다.
- **데이터의 편향성**: 공개 크라우드소싱 기반 데이터 특성상 특정 주류 장르 및 아티스트에 편향이 존재할 수 있습니다.
"""

nb['cells'][0]['source'] = [cell_0_source]
nb['cells'][2]['source'] = [cell_2_source]

# Replace the last markdown cell
for cell in reversed(nb['cells']):
    if cell['cell_type'] == 'markdown':
        cell['source'] = [conclusion_source]
        break

with open('chord_progression_analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Notebook markdown patched successfully.")
