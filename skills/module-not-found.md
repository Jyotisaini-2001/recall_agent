---
name: module-not-found
description: Fix ModuleNotFoundError by installing the missing package via pip
keywords: ["ModuleNotFoundError: No module named"]
cell_hints: []
confidence: 0.88
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
The package is not installed in the current Python environment. Install it via pip directly from the notebook.

# Fix template
```python
import subprocess, sys
# Install the missing module — replace 'PACKAGE_NAME' with the actual package
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PACKAGE_NAME'])
```

# Verification
Re-run the original import cell after installation completes.
