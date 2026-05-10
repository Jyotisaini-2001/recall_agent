---
name: pandas-keyerror
description: Fix KeyError when accessing a missing column in a pandas DataFrame
keywords: ["KeyError"]
cell_hints: ["df[", "DataFrame", "pandas"]
confidence: 0.90
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
A KeyError occurs when you try to access a column name that doesn't exist in the DataFrame. Usually a typo or the column was renamed/dropped upstream.

# Fix template
```python
print('Available columns:', df.columns.tolist())
# Fix: use the correct column name from the list above
# df['{WRONG_COL}'] → df['{CORRECT_COL}']
```

# Verification
Re-run the cell after checking the printed column list and correcting the column name.
