import json

NOTEBOOK_PATH = "chord_progression_analysis.ipynb"

def remove_mock_prints():
    with open(NOTEBOOK_PATH, "r", encoding="utf-8") as f:
        nb = json.load(f)

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            new_source = []
            for line in cell.get("source", []):
                # Filter out the mock hardcoded print statements
                if "print(\"=> 90년대" in line: continue
                if "print(\"=> 이는 숏폼" in line: continue
                if "print(\"[레이더 차트 분석 요약]\")" in line: continue
                if "print(\"- **Radiohead**" in line: continue
                if "print(\"- **Taylor Swift**" in line: continue
                if "print(\"- **Billie Eilish**" in line: continue
                if "print(\"=> 의사결정 트리" in line: continue
                if "print(\"=> 이는 대중음악" in line: continue
                new_source.append(line)
            cell["source"] = new_source

    with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        
    print("✅ 노트북 소스 코드에서 하드코딩된 Mock 텍스트 출력을 제거했습니다.")

if __name__ == "__main__":
    remove_mock_prints()
