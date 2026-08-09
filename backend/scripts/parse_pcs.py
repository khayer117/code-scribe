"""Parse ICD-10-PCS codes from the flat text file.

Format per line:  CCCCCCC Description text here
"""

from pathlib import Path

# .resolve() converts __file__ to absolute before walking up,
# so this works regardless of cwd or how Python sets __file__.
# scripts/parse_pcs.py -> scripts/ -> backend/ -> codescribe/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ICD_FILE = _PROJECT_ROOT / "source files" / "icd10pcs_codes_2027.txt"


def parse_codes(filepath: Path = ICD_FILE) -> list[dict]:
    codes = []
    with open(filepath, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            # Code is the first whitespace-delimited token (always 7 chars)
            parts = line.split(None, 1)
            if len(parts) == 2 and len(parts[0]) == 7:
                codes.append({"code": parts[0], "description": parts[1].strip()})
    return codes


if __name__ == "__main__":
    codes = parse_codes()
    print(f"Parsed {len(codes):,} codes")
    print(f"  First: {codes[0]}")
    print(f"  Last:  {codes[-1]}")
