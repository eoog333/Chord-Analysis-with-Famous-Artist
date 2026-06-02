import json

notebook_path = 'chord_progression_analysis.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell['cell_type'] == 'markdown':
        source = cell.get('source', [])
        
        # 1. 서론부 Q4 추가
        for i, line in enumerate(source):
            if "- **Q3. 아티스트마다 고유한 화성적 정체성" in line:
                if i+1 == len(source) or "- **Q4." not in source[i+1]:
                    # Q3가 리스트의 마지막이거나, 바로 뒤에 Q4가 없다면 추가
                    if line.endswith('\n'):
                        source.insert(i+1, "- **Q4. 대중음악의 화성 기법은 시대를 단절하여 나눌 수 있는가?**")
                    else:
                        source[i] = line + "\n"
                        source.insert(i+1, "- **Q4. 대중음악의 화성 기법은 시대를 단절하여 나눌 수 있는가?**")
        
        # 2. STEP 4 제목 수정
        for i, line in enumerate(source):
            if "### STEP 4. 코드 진행 구조 네트워크 분석" in line and "(Q4의 답)" not in line:
                source[i] = "### STEP 4. 코드 진행 구조 네트워크 분석 및 연대 예측 검증 (Q4의 답)\n"
                
        # 3. 결론부 요약 수정
        for i, line in enumerate(source):
            if "### 5.1 연구 결론 요약" in line:
                # 결론부 블록임을 확인하면 텍스트를 전면 덮어씁니다.
                # 해당 셀의 소스를 완전히 교체
                new_source = [
                    "## 5. 결론 및 기대효과 / 한계점\n",
                    "\n",
                    "### 5.1 연구 결론 요약\n",
                    "1. **차용화음의 감소와 텐션의 증가 (Q1)**: 시대별 트렌드를 분석한 결과, 비다이아토닉(차용화음) 비율은 90년대(0.24)에서 20년대(0.095)로 꾸준히 우하향하며 **다이아토닉 중심의 안정적인 화성**으로 회귀하는 경향을 보였습니다. 반면, **텐션 코드 비율은 20년대에 폭발적으로 증가**(0.25 -> 0.46)했습니다. 즉, 현대 팝은 조성을 벗어나는 복잡한 전조보다는, 다이아토닉 틀 안에서 세련된 질감(7th, 9th)을 더하는 방식으로 진화했습니다.\n",
                    "2. **장르 초월 화성 클러스터 (Q2)**: 단순히 '발라드', '락' 등의 장르를 넘어, **'다이아토닉 중심의 우울한 단조 그룹'**, **'차용화음을 적극 활용하는 실험적 그룹'**, **'텐션 코드가 풍부한 세련된 그룹'** 등 아티스트가 구사하는 순수 화성 언어에 따라 유의미한 군집을 도출해냈습니다.\n",
                    "3. **아티스트 고유의 화성적 정체성 (Q3)**: 아티스트별로 자주 사용하는 코드 진행 패턴과 화성 구성이 뚜렷하게 구별됨을 데이터로 증명했습니다. 특정 아티스트는 복잡한 텐션의 허브 코드를, 다른 아티스트는 단순하고 강력한 다이아토닉 진행을 선호하는 등, 각자의 **'화성적 페르소나'가 수치적으로 입증**되었습니다.\n",
                    "4. **화성 기법의 보편성 및 시대 예측의 한계 (Q4)**: 전이 네트워크 시각화를 통해 `I`, `IV`, `vi` 등 강력한 허브 코드가 시대를 초월해 뼈대를 이루고 있음을 확인했습니다. 또한 머신러닝(Random Forest)을 통한 연대 예측 결과 정확도가 무작위(25%) 수준에 그쳤습니다. 이는 대중음악의 화성적 구조가 특정 연대에 완전히 종속되지 않으며, 과거의 화성 기법이 현대에도 끊임없이 재해석되고 혼용되는 **'보편적 언어'**임을 시사합니다.\n"
                ]
                cell['source'] = new_source
                break

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("마크다운 패치 완료!")
