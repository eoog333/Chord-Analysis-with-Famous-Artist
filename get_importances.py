import pandas as pd
from sklearn.ensemble import RandomForestClassifier
# Just run the main script but modify it to print importances
with open('chord_progression_analysis.py', 'r') as f:
    code = f.read()

code = code.replace("plt.show()", "pass")
code = code.replace("print(\"=== 코사인 유사도", "print(importances.head(3))\nprint(\"=== 코사인 유사도")

exec(code)
