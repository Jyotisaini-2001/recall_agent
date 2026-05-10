"""
Patch broken SkillForge fix cells in error_notebook.ipynb.

Each fix cell that references an undefined variable is patched to include
the required variable setup inline so it works after Restart & Run All.
"""
import json

NB_PATH = "error_notebook.ipynb"

with open(NB_PATH, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Map cell id → replacement source lines
PATCHES = {
    # fix-list-index-out-of-range: 'items' not yet defined at this cell position
    "2f546e2f": [
        "# SkillForge fix [fix-list-index-out-of-range]\n",
        "items = ['apple', 'banana', 'cherry']  # defined here so fix cell is self-contained\n",
        "# Ensure index is within bounds before accessing\n",
        "if 5 < len(items):\n",
        "    print(items[5])\n",
        "else:\n",
        "    print(items[-1])  # fallback to last element",
    ],

    # dict-key-safe-access: 'user' not yet defined at this cell position
    "ba7212da": [
        "# SkillForge fix [dict-key-safe-access]\n",
        "user = {'name': 'Ishan', 'age': 25}  # defined here so fix cell is self-contained\n",
        "print(user.get('email', None))",
    ],

    # fix-list-index-out-of-range: 'numbers' not yet defined at this cell position
    "290a6c7a": [
        "# SkillForge fix [fix-list-index-out-of-range]\n",
        "numbers = [3, 1, 4, 1, 5, 9]  # defined here so fix cell is self-contained\n",
        "numbers.append(2)\n",
        "print(numbers)",
    ],

    # word-to-int-conversion: 'user_input' not yet defined at this cell position
    "4bb7627d": [
        "# SkillForge fix [word-to-int-conversion]\n",
        "from word2number import w2n\n",
        "\n",
        "user_input = 'twenty'  # defined here so fix cell is self-contained\n",
        "try:\n",
        "    age = int(user_input)\n",
        "except ValueError:\n",
        "    try:\n",
        "        age = w2n.word_to_num(user_input)\n",
        "    except Exception:\n",
        "        age = None\n",
        "        print(f'Could not convert {user_input!r} to an integer')\n",
        "\n",
        "if age is not None:\n",
        "    print(f'Age is {age}')",
    ],

    # dict-key-safe-access: 'df' not yet defined (import failed), make self-contained
    "350c83b8": [
        "# SkillForge fix [dict-key-safe-access]\n",
        "import pandas as pd\n",
        "data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Score': [85, 92, 78]}\n",
        "df = pd.DataFrame(data)  # defined here so fix cell is self-contained\n",
        "# For DataFrames use column indexing with .get() or check columns first\n",
        "col = 'Name'\n",
        "print(df[col] if col in df.columns else None)",
    ],
}

patched = 0
for cell in nb["cells"]:
    cell_id = cell.get("id", "")
    if cell_id in PATCHES:
        old_source = "".join(cell["source"])
        cell["source"] = PATCHES[cell_id]
        # Clear stale error outputs so Jupyter shows clean results
        cell["outputs"] = []
        cell["execution_count"] = None
        print(f"  ✓ Patched cell {cell_id}")
        patched += 1

print(f"\nPatched {patched}/{len(PATCHES)} cells.")

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Saved {NB_PATH}")
