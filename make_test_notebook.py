"""Creates test_errors.ipynb — realistic data science notebook with mixed errors."""
import nbformat

def cell(src):
    return nbformat.v4.new_code_cell(src)

nb = nbformat.v4.new_notebook()
nb.cells = [
    cell(
        "# Setup — all variables created here\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "from sklearn.preprocessing import StandardScaler\n"
        "from sklearn.linear_model import LinearRegression\n"
        "\n"
        "data = {\n"
        "    'product': ['A', 'B', 'C', 'A', 'B', 'C', 'A'],\n"
        "    'region':  ['North', 'South', 'North', 'East', 'East', 'South', 'North'],\n"
        "    'sales':   [120, 200, None, 340, 150, 210, 180],\n"
        "    'price':   ['10.5', '20.0', '15.5', '10.5', '20.0', '15.5', '10.5'],\n"
        "    'units':   [12, 10, None, 34, 8, 14, 18],\n"
        "}\n"
        "df = pd.DataFrame(data)\n"
        "X = df[['sales', 'units', 'product', 'region']]\n"
        "y = [0, 1, 0, 1, 1, 0, 1]\n"
        "top_products = df.groupby('product')['sales'].sum().sort_values(ascending=False)\n"
        "top_list = top_products.tolist()\n"
        "new_row = pd.DataFrame({'product': ['D'], 'region': ['West'], 'sales': [300], 'price': ['25.0'], 'units': [12]})\n"
        "print('Setup done')\n"
        "print(df)"
    ),

    cell(
        "# ERROR 1 — KeyError: wrong column name (FAST PATH)\n"
        "avg_revenue = df['revenue'].mean()\n"
        "print('Average revenue:', avg_revenue)"
    ),

    cell(
        "# ERROR 2 — TypeError: math on string column (SLOW PATH — new skill)\n"
        "df['total'] = df['price'] * df['units']\n"
        "print(df[['product', 'price', 'units', 'total']])"
    ),

    cell(
        "# ERROR 3 — ValueError: NaN in sklearn (FAST PATH)\n"
        "scaler = StandardScaler()\n"
        "X_scaled = scaler.fit_transform(X[['sales', 'units']])\n"
        "print('Scaled:', X_scaled)"
    ),

    cell(
        "# ERROR 4 — NameError: missing import (FAST PATH)\n"
        "model = RandomForestClassifier(n_estimators=10)\n"
        "print('Model ready:', model)"
    ),

    cell(
        "# ERROR 5 — IndexError: list index out of range (SLOW PATH — new skill)\n"
        "print('Best product sales:', top_list[10])"
    ),

    cell(
        "# ERROR 6 — ValueError: string column in sklearn (FAST PATH)\n"
        "reg = LinearRegression()\n"
        "reg.fit(X, y)\n"
        "print('Coefficients:', reg.coef_)"
    ),

    cell(
        "# ERROR 7 — AttributeError: df.append removed (FAST PATH)\n"
        "df = df.append(new_row, ignore_index=True)\n"
        "print('Updated dataset:', df.shape)"
    ),
]

nbformat.write(nb, "test_errors.ipynb")
print("Created test_errors.ipynb — 8 cells, 5 FAST PATH + 2 SLOW PATH errors")
