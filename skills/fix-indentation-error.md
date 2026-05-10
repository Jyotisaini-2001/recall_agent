---
name: fix-indentation-error
description: Fixes IndentationError caused by mismatched indentation levels in Python code blocks
keywords: ['IndentationError', 'unindent', 'indentation', 'tokenize', 'whitespace']
confidence: 0.99
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
Python's tokenizer raises IndentationError when a line's indentation does not match any enclosing block level — typically caused by mixing spaces, using an odd number of spaces, or misaligning a statement relative to its sibling or parent block.

# Fix template
```python
Align `{STATEMENT}` to the correct indentation level matching its logical scope: use multiples of 4 spaces (or consistent block indentation) so each statement's indent matches its containing block.
```

# Verification
Run the cell; no IndentationError is raised and the function/block executes with correct control flow (e.g., statements at the intended scope actually run or are skipped as expected).
