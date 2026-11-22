"""Move loose skill templates in Templates\\Skills into subfolders named
after each template's primary profession.

Usage: python sort_by_class.py <source folder> [--dest <folder>] [--go]
Class folders are created under --dest (default: the source folder).
Without --go it only prints what it would do.
"""
import os, sys, shutil, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gwdecode import decode, PROF

def main(skills_dir, go, dest_root=None):
    dest_root = dest_root or skills_dir
    plan, skipped = [], []
    for f in sorted(os.listdir(skills_dir)):
        src = os.path.join(skills_dir, f)
        if not os.path.isfile(src):
            continue
        try:
            raw = open(src, encoding="utf-8", errors="replace").read().strip()
            d = decode(raw.split()[0])
            if d["type"] != "skills" or not (1 <= d["p1"] < len(PROF)):
                raise ValueError("no primary profession")
            plan.append((f, PROF[d["p1"]]))
        except Exception as e:
            skipped.append((f, str(e)))
    for f, prof in plan:
        dst_dir = os.path.join(dest_root, prof)
        dst = os.path.join(dst_dir, f)
        if os.path.exists(dst):
            skipped.append((f, "already exists in " + prof)); continue
        if go:
            os.makedirs(dst_dir, exist_ok=True)
            shutil.move(os.path.join(skills_dir, f), dst)
    bad = {f for f, _ in skipped}
    plan = [(f, p) for f, p in plan if f not in bad]
    print(("Moved" if go else "Would move"), len(plan), "files:")
    for prof, n in sorted(collections.Counter(p for _, p in plan).items()):
        print(f"  {prof}: {n}")
    for f, why in skipped:
        print("  SKIPPED", f, "-", why)

if __name__ == "__main__":
    a = sys.argv[1:]
    dest = a[a.index("--dest") + 1] if "--dest" in a else None
    main(a[0], "--go" in a, dest)
