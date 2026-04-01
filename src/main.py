from __future__ import annotations

import json
import sys
from pathlib import Path

from src.parsers.csv_parser import parse_csv
from src.services.model_builder import build_model


def read_csv_file(file_path: str) -> str:
    return Path(file_path).expanduser().resolve().read_text(encoding="utf-8")


def main() -> int:
    try:
        if len(sys.argv) < 2:
            print("--- Data to CSV Converter ---")
            input_mode = input("Enter '1' to provide a File Path, or '2' to Paste CSV content: ").strip()

            if input_mode == "1":
                input_path = input("Enter the CSV file path: ").strip()
                csv_text = read_csv_file(input_path)
            elif input_mode == "2":
                print("Paste your CSV content (press Ctrl+Z then Enter on Windows / Ctrl+D on Unix when finished):")
                csv_text = sys.stdin.read().strip()
                if not csv_text:
                    print("Error: No CSV content provided.", file=sys.stderr)
                    return 1
            else:
                print("Invalid option selected.", file=sys.stderr)
                return 1
        else:
            input_path = sys.argv[1]
            csv_text = read_csv_file(input_path)

        rows = parse_csv(csv_text)
        model = build_model(rows)
        print("\n--- Converted Model (JSON) ---")
        print(json.dumps(model, indent=2))
        return 0
    except Exception as error:  # pragma: no cover
        print(f"Failed to process: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
