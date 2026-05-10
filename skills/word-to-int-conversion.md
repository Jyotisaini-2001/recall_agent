---
name: word-to-int-conversion
description: Fixes ValueError when int() receives a word-form number string (e.g. 'twenty') instead of a digit string
keywords: ['ValueError', 'invalid literal', 'int()', 'word2number', 'w2n', 'string to int']
confidence: 0.92
times_used: 0
created_at: 2026-05-09
---

# Diagnosis
Python's int() only parses digit strings (e.g. '20'), not English word representations (e.g. 'twenty'). When user input or data contains spelled-out numbers, a fallback via word2number is needed.

# Fix template
```python
from word2number import w2n

try:
    {VAR} = int({INPUT})
except ValueError:
    try:
        {VAR} = w2n.word_to_num({INPUT})
    except Exception:
        {VAR} = None
        print(f'Could not convert {{{INPUT}!r}} to an integer')

if {VAR} is not None:
    print(f'{VAR_LABEL} is {{{VAR}}}')
```

# Verification
Assert that the converted variable equals the expected integer value (e.g. assert age == 20), and that passing a purely numeric string like '20' still works through the primary int() path without invoking w2n.
