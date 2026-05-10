---
name: missing-colon-def-statement
description: Fixes SyntaxError caused by missing colon at the end of a Python def statement
keywords: ['SyntaxError', 'invalid syntax', 'def', 'missing colon', 'function definition']
confidence: 1.0
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
Python requires a colon after the parameter list in a function definition to signal the start of the function body. Omitting it causes an immediate SyntaxError before execution.

# Fix template
```python
def {FUNCTION_NAME}({PARAMETERS}):
    {FUNCTION_BODY}
```

# Verification
Re-run the cell and confirm no SyntaxError is raised; the function should be callable and execute its body as expected.
