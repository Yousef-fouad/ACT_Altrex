"""One-off inspection helper: dump sheet names and raw rows of a workbook.

Usage: python -I scripts/inspect_sources.py <path-to-xlsx> [max_rows]
Read-only; does not modify the workbook.
"""
import sys
from pathlib import Path

import openpyxl


def main() -> None:
    path = Path(sys.argv[1])
    max_rows = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    print(f"=== {path.name} ===")
    print("sheets:", wb.sheetnames)
    for name in wb.sheetnames:
        ws = wb[name]
        print(f"\n--- sheet: {name!r} max_row={ws.max_row} max_col={ws.max_column} ---")
        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i >= max_rows:
                print("...")
                break
            print(i, row)


if __name__ == "__main__":
    main()
