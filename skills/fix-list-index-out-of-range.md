---
name: fix-list-index-out-of-range
description: Fixes IndexError when accessing a list with an index that exceeds the list's length
keywords: ['IndexError', 'list index out of range', 'index', 'list', 'array']
confidence: 1.0
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
This error occurs when code attempts to access a list element at an index that does not exist — either the index is hardcoded and wrong, or the list is shorter than expected at runtime. Python lists are zero-indexed, so valid indices range from 0 to len(list)-1 (or -len(list) to -1 for negative indexing).

# Fix template
```python
# Ensure index is within bounds before accessing
if {INDEX} < len({LIST_VAR}):
    print({LIST_VAR}[{INDEX}])
else:
    print({LIST_VAR}[-1])  # fallback to last element, or use {LIST_VAR}[len({LIST_VAR})-1]
```

# Verification
Confirm len({LIST_VAR}) > {INDEX} before access, or print(len({LIST_VAR})) to inspect size; the cell should execute without raising IndexError and print the expected element.
