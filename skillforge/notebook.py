import nbformat


def read(path: str) -> nbformat.NotebookNode:
    with open(path, "r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)


def find_error_cells(nb: nbformat.NotebookNode) -> list[tuple[int, dict]]:
    errors = []
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") in ("error", "stream"):
                if output.get("output_type") == "error" or "Error" in output.get("text", ""):
                    errors.append((idx, cell))
                    break
    return errors


def get_prior_cells(nb: nbformat.NotebookNode, cell_idx: int, n: int = 2) -> list[str]:
    sources = []
    for i in range(max(0, cell_idx - n), cell_idx):
        cell = nb.cells[i]
        if cell.cell_type == "code":
            sources.append(cell.source)
    return sources


def insert_fix_cell(nb: nbformat.NotebookNode, after_idx: int, code: str, skill_name: str = None) -> int:
    tag = f"# SkillForge fix" + (f" [{skill_name}]" if skill_name else "")
    new_cell = nbformat.v4.new_code_cell(source=f"{tag}\n{code}")
    nb.cells.insert(after_idx + 1, new_cell)
    return after_idx + 1


def strip_fix_cells(nb: nbformat.NotebookNode) -> int:
    before = len(nb.cells)
    nb.cells = [c for c in nb.cells if not c.source.startswith("# SkillForge fix")]
    return before - len(nb.cells)


def write(nb: nbformat.NotebookNode, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
