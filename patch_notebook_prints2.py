import json

NOTEBOOK_PATH = "chord_progression_analysis.ipynb"

def remove_mock_prints2():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            new_source = []
            for line in cell.get("source", []):
                # Filter out the remaining mock print statements
                if "[분석 결과 요약]" in line: continue
                if "=> 90년대에서" in line: continue
                
                # Keep other lines
                new_source.append(line)
            cell["source"] = new_source

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        
    print("✅ 노트북 소스 코드에서 추가로 발견된 멘트 출력을 제거했습니다.")

if __name__ == "__main__":
    remove_mock_prints2()
