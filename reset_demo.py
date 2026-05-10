"""Run this to reset demo.ipynb to the original clean state before each demo."""
import nbformat
import shutil, os

def make_cell(src):
    return nbformat.v4.new_code_cell(src)

nb = nbformat.v4.new_notebook()
nb.cells = [
    make_cell(
        "# Cell 1 — Setup (runs clean)\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "from sklearn.linear_model import LogisticRegression\n"
        "\n"
        "df = pd.DataFrame({'age': [25, 30, None, 22], 'grade': ['A', 'B', 'A', 'C']})\n"
        "X = df[['age', 'grade']]\n"
        "y = [0, 1, 0, 1]\n"
        "new_row = pd.DataFrame({'age': [28], 'grade': ['B']})\n"
        "print('Setup done — df, X, y, new_row ready')"
    ),
    make_cell(
        "# Cell 2 — KeyError: wrong column name\n"
        "print(df['salary'].mean())"
    ),
    make_cell(
        "# Cell 3 — NameError: StandardScaler not imported\n"
        "scaler = StandardScaler()\n"
        "X_scaled = scaler.fit_transform(df[['age']].dropna())\n"
        "print('Scaled:', X_scaled)"
    ),
    make_cell(
        "# Cell 4 — ValueError: NaN in sklearn input\n"
        "from sklearn.preprocessing import StandardScaler\n"
        "scaler = StandardScaler()\n"
        "X_scaled = scaler.fit_transform(X[['age']].values)\n"
        "print('Scaled:', X_scaled)"
    ),
    make_cell(
        "# Cell 5 — ValueError: string column in sklearn\n"
        "model = LogisticRegression()\n"
        "model.fit(X, y)\n"
        "print('Model fitted')"
    ),
    make_cell(
        "# Cell 6 — AttributeError: DataFrame.append removed in pandas 2.0\n"
        "df = df.append(new_row, ignore_index=True)\n"
        "print(df)"
    ),
    make_cell(
        "# Cell 7 — ZeroDivisionError (triggers SLOW PATH + new skill)\n"
        "total = 0\n"
        "result = 100 / total\n"
        "print('Result:', result)"
    ),
]

out = "demo.ipynb"
if os.path.exists(out):
    shutil.copy(out, "demo_backup.ipynb")

nbformat.write(nb, out)
print(f"Reset {out} — 7 cells, all variables created in Cell 1")
