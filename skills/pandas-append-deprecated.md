---
name: pandas-append-deprecated
description: Fix AttributeError caused by DataFrame.append removed in pandas 2.0
keywords: ["has no attribute 'append'"]
cell_hints: ["df", "DataFrame", "append"]
confidence: 0.95
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
DataFrame.append() was removed in pandas 2.0. Use pd.concat() instead.

# Fix template
```python
import pandas as pd

# DataFrame.append() was removed in pandas 2.0 — use pd.concat instead
df = pd.concat([df, new_row], ignore_index=True)
print("Row appended successfully using pd.concat")
print(df.tail())
```

# Verification
Re-run — no AttributeError means the fix worked.
