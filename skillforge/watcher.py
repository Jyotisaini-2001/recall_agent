import nbclient
import nbformat

from skillforge.models import FailurePacket
from skillforge import notebook


def run_and_capture(path: str) -> list[FailurePacket]:
    nb = notebook.read(path)

    client = nbclient.NotebookClient(nb, timeout=60, allow_errors=True)
    client.execute()

    notebook.write(nb, path)

    packets = []
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        for output in cell.get("outputs", []):
            if output.get("output_type") == "error":
                traceback = "\n".join(output.get("traceback", []))
                ename = output.get("ename", "")
                evalue = output.get("evalue", "")
                full_traceback = f"{ename}: {evalue}\n{traceback}"

                packets.append(FailurePacket(
                    cell_idx=idx,
                    traceback=full_traceback,
                    cell_source=cell.source,
                    prior_cells=notebook.get_prior_cells(nb, idx),
                    notebook_path=path,
                ))
                break

    return packets
