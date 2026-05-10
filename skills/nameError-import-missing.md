---
name: nameError-import-missing
description: Fix NameError caused by a missing import statement
keywords: ["NameError: name"]
cell_hints: []
confidence: 0.92
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
A NameError means a variable or class is used before it was imported. Common in notebooks where cells are run out of order.

# Fix template
```python
# All common data science imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
print("Imports loaded — re-run the cell that failed above")
```

# Verification
Re-run the failing cell — the NameError should be gone.
