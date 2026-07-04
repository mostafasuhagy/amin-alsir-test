# fix_encoding_v2.py
#
# Tries multiple known mojibake patterns per line and picks the one that
# successfully round-trips to valid, readable UTF-8 text.
#
# Usage:
#   python fix_encoding_v2.py primitives.py
#
# Output: primitives_fixed.py (does NOT overwrite the original)
# Also prints a per-line report of which encoding (if any) was used,
# so you can manually review any line marked "UNCHANGED" or "AMBIGUOUS".

import sys

CANDIDATE_ENCODINGS = ["cp720", "cp1256", "cp437", "cp1252", "cp850", "cp865", "cp860"]

def has_arabic(s: str) -> bool:
    return any(0x0600 <= ord(c) <= 0x06FF for c in s)

def looks_broken(s: str) -> bool:
    """Heuristic: contains box-drawing / replacement-y characters typical of mojibake."""
    suspicious_ranges = [
        (0x2500, 0x257F),  # box drawing
        (0xFFFD, 0xFFFD),  # replacement char
    ]
    for c in s:
        cp = ord(c)
        for lo, hi in suspicious_ranges:
            if lo <= cp <= hi:
                return True
    return False

def try_fix_line(line: str):
    """
    Returns (fixed_line, encoding_used_or_None).
    Tries each candidate encoding; picks the first one that:
      - successfully encodes+decodes without error
      - produces Arabic text
      - does NOT still look broken (no leftover box-drawing artifacts)
    If none qualify cleanly, returns the best partial candidate (most Arabic,
    least "broken" look) or the original line if nothing improves it.
    """
    if not has_arabic(line) and not looks_broken(line):
        return line, None  # nothing to do, likely pure code/ASCII

    candidates = []
    for enc in CANDIDATE_ENCODINGS:
        try:
            candidate = line.encode(enc).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        candidates.append((enc, candidate))

    # Prefer a candidate that has Arabic and does NOT look broken
    for enc, candidate in candidates:
        if has_arabic(candidate) and not looks_broken(candidate):
            return candidate, enc

    # No clean candidate found
    return line, "UNRESOLVED"

def main():
    if len(sys.argv) != 2:
        print("Usage: python fix_encoding_v2.py <path_to_file.py>")
        sys.exit(1)

    src_path = sys.argv[1]
    dst_path = src_path.rsplit(".", 1)[0] + "_fixed.py"
    report_path = src_path.rsplit(".", 1)[0] + "_fix_report.txt"

    with open(src_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_lines = []
    report_lines = []
    counts = {}
    unresolved_count = 0

    for i, line in enumerate(lines, start=1):
        fixed, enc = try_fix_line(line)
        fixed_lines.append(fixed)
        if enc == "UNRESOLVED":
            unresolved_count += 1
            report_lines.append(f"Line {i}: UNRESOLVED -> {line.rstrip()}")
        elif enc:
            counts[enc] = counts.get(enc, 0) + 1
            report_lines.append(f"Line {i}: fixed via {enc}")

    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(fixed_lines)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Total lines: {len(lines)}\n")
        f.write(f"Fixed by encoding:\n")
        for enc, count in counts.items():
            f.write(f"  {enc}: {count} lines\n")
        f.write(f"Unresolved (need manual review): {unresolved_count} lines\n\n")
        f.write("---- Details ----\n")
        f.writelines(l + "\n" for l in report_lines)

    print(f"Done.")
    print(f"Fixed file: {dst_path}")
    print(f"Report file: {report_path}")
    print(f"Fixed by encoding: {counts}")
    print(f"Unresolved lines (need manual review): {unresolved_count}")

if __name__ == "__main__":
    main()
