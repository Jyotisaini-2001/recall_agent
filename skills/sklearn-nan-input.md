---
name: sklearn-nan-input
description: Fix ValueError when sklearn model receives NaN values in input
keywords: ["contains NaN"]
cell_hints: []
confidence: 0.91
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
sklearn models cannot handle NaN values. The input array has missing values that must be dropped or imputed before fitting.

# Fix template
```python
from sklearn.impute import SimpleImputer
import numpy as np

# Impute NaN values with column mean
imputer = SimpleImputer(strategy='mean')
X_clean = imputer.fit_transform(X.select_dtypes(include=[np.number]))
print("NaN values imputed — X_clean is ready for sklearn")
print(f"Shape: {X_clean.shape}, NaN count: {np.isnan(X_clean).sum()}")
```

# Verification
Check X_clean — all values should be numeric with no NaN.
