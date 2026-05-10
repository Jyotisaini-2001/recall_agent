---
name: sklearn-string-to-float
description: Fix ValueError when sklearn receives string/object dtype columns
keywords: ["could not convert string to float"]
cell_hints: []
confidence: 0.91
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
sklearn models require numeric input. Object/string columns must be encoded before fitting.

# Fix template
```python
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# Encode all string/object columns to numeric
X_encoded = X.copy()
le = LabelEncoder()
for col in X_encoded.select_dtypes(include='object').columns:
    X_encoded[col] = le.fit_transform(X_encoded[col].astype(str))

X_encoded = X_encoded.fillna(X_encoded.mean())
print("Encoding done — X_encoded is ready for sklearn")
print(X_encoded.dtypes)
```

# Verification
Check X_encoded.dtypes — all columns should be numeric.
