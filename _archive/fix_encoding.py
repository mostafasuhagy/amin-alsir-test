# fix_encoding.py
# Reverses a UTF-8 -> mis-decoded-as-cp1256 (Windows Arabic) -> re-encoded-as-UTF-8 mojibake corruption.
#
# Usage:
#   python fix_encoding.py main.py
#
# This will:
#   1. Read main.py as UTF-8
#   2. For each line, try to reverse the corruption: encode as cp1256, decode as utf-8
#   3. If that fails for a given line (meaning it wasn't corrupted), keep it as-is
#   4. Write the result to main_fixed.py (does NOT overwrite the original)
#
# Review main_fixed.py carefully, then manually rename/replace main.py once you're happy.

import sys

def fix_line(line: str) -> str:
    """Try to reverse the UTF-8 -> cp1256 -> UTF-8 corruption for one line."""
    try:
        candidate = line.encode("cp1256").decode("utf-8")
        return candidate
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Line wasn't corrupted in this way (e.g. plain ASCII code), leave as-is
        return line

def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_encoding.py <path_to_main.py>")
        sys.exit(1)

    src_path = sys.argv[1]
    dst_path = src_path.rsplit(".", 1)[0] + "_fixed.py"

    with open(src_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    changed_count = 0
    for line in lines:
        fixed = fix_line(line)
        if fixed != line:
            changed_count += 1
        fixed_lines.append(fixed)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    print(f"Done. {changed_count} lines were modified out of {len(lines)} total.")
    print(f"Fixed file written to: {dst_path}")
    print("Please review it before replacing the original main.py.")

if __name__ == "__main__":
    main()
