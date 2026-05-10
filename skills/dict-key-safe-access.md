---
name: dict-key-safe-access
description: Fix KeyError when accessing a dictionary key that may not exist
keywords: ['KeyError', 'dictionary', 'dict', 'key', 'missing', 'get']
confidence: 1.0
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
A KeyError occurs when code accesses a dictionary with bracket notation (dict['key']) but the key does not exist in the dictionary. Using .get() with a fallback default value avoids the exception.

# Fix template
```python
{DICT_VAR}.get('{KEY_NAME}', {DEFAULT_VALUE})
```

# Verification
Run the cell and confirm no KeyError is raised; check that the default value is returned when the key is absent and the actual value is returned when the key is present.
