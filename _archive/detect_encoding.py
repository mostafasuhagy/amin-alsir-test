# detect_encoding.py
#
# Diagnostic tool: for each corrupted line in the file, tries EVERY available
# single-byte codec in Python and reports which ones produce valid, clean
# Arabic text (no leftover box-drawing / replacement characters).
#
# This avoids guessing — it lets your machine test directly against the
# REAL bytes in the file, rather than relying on a screenshot transcription.
#
# Usage:
#   python detect_encoding.py primitives.py
#
# Output: encoding_detection_report.txt
# Send me ONLY that report file's content (or the top ~50 lines of it).

import sys
import encodings.aliases
import pkgutil
import encodings

def get_all_codecs():
    codecs_set = set(encodings.aliases.aliases.values())
    mods = [m.name for m in pkgutil.iter_modules(encodings.__path__)]
    codecs_set.update(mods)
    # filter out obviously irrelevant / unicode-to-unicode codecs
    skip = {"utf_8", "utf8", "utf_8_sig", "utf_16", "utf_16_le", "utf_16_be",
            "utf_32", "utf_32_le", "utf_32_be", "ascii", "rot_13", "base64_codec",
            "bz2_codec", "hex_codec", "quopri_codec", "uu_codec", "zlib_codec",
            "punycode", "idna", "raw_unicode_escape", "unicode_escape",
            "string_escape", "unicode_internal"}
    return sorted(c for c in codecs_set if c not in skip)

def has_arabic(s: str) -> bool:
    return any(0x0600 <= ord(c) <= 0x06FF for c in s)

def looks_broken(s: str) -> bool:
    for c in s:
        cp = ord(c)
        if 0x2500 <= cp <= 0x257F:  # box drawing
            return True
        if cp == 0xFFFD:  # replacement char
            return True
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python detect_encoding.py <path_to_file.py>")
        sys.exit(1)

    src_path = sys.argv[1]
    report_path = "encoding_detection_report.txt"
    codecs_to_try = get_all_codecs()

    with open(src_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find lines that look broken (candidates for testing)
    broken_lines = [(i, l) for i, l in enumerate(lines, start=1) if looks_broken(l)]

    results = []  # (encoding, success_count, sample_output)
    for enc in codecs_to_try:
        success_count = 0
        sample = None
        for i, line in broken_lines[:30]:  # test against first 30 broken lines
            try:
                candidate = line.encode(enc).decode("utf-8")
            except Exception:
                continue
            if has_arabic(candidate) and not looks_broken(candidate):
                success_count += 1
                if sample is None:
                    sample = candidate.strip()
        if success_count > 0:
            results.append((enc, success_count, sample))

    results.sort(key=lambda x: -x[1])

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Total lines in file: {len(lines)}\n")
        f.write(f"Lines that look broken (box-drawing artifacts): {len(broken_lines)}\n")
        f.write(f"Tested against first {min(30, len(broken_lines))} broken lines\n\n")
        f.write("---- Candidate encodings ranked by success ----\n")
        for enc, count, sample in results[:15]:
            f.write(f"\n[{enc}] fixed {count}/{min(30, len(broken_lines))} test lines\n")
            f.write(f"  Sample output: {sample}\n")
        if not results:
            f.write("\nNo single codec cleanly fixed any sample lines.\n")
            f.write("This suggests a multi-stage or mixed corruption.\n")
            f.write("\nShowing 5 raw broken lines for manual inspection:\n")
            for i, l in broken_lines[:5]:
                f.write(f"Line {i}: {l.strip()}\n")

    print(f"Done. Report written to: {report_path}")
    print(f"Top candidate: {results[0][0] if results else 'NONE FOUND'}")
    if results:
        print(f"  ({results[0][1]} lines fixed cleanly)")
        print(f"  Sample: {results[0][2]}")

if __name__ == "__main__":
    main()
