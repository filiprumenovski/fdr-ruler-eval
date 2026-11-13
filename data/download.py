"""Fetch the eval data from the GitHub release and verify every file against data/SHA256SUMS.

Pure standard library, so it runs the same on macOS, Linux and Windows:
    python data/download.py
Files land in data/assets/. Files already present with the right checksum are skipped.
Override the source with FDR_EVAL_REPO (owner/name) and FDR_EVAL_TAG.
"""
import hashlib
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "data" / "assets"
REPO = os.environ.get("FDR_EVAL_REPO", "filiprumenovski/fdr-ruler-eval")
TAG = os.environ.get("FDR_EVAL_TAG", "v1.0")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def expected():
    out = {}
    for line in (ROOT / "data" / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            out[name.lstrip("*").strip()] = digest
    return out


def fetch(name, dest):
    url = f"https://github.com/{REPO}/releases/download/{TAG}/{name}"
    part = dest.with_name(dest.name + ".part")
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r, open(part, "wb") as f:
                total = int(r.headers.get("Content-Length") or 0)
                done = 0
                while block := r.read(1 << 20):
                    f.write(block)
                    done += len(block)
                    if total:
                        print(f"\r  {name}: {done / total:6.1%} of {total / 1e6:,.0f} MB", end="", flush=True)
            print()
            part.replace(dest)
            return
        except OSError as e:
            print(f"\n  {name}: attempt {attempt} failed ({e})", file=sys.stderr)
            time.sleep(2 * attempt)
    sys.exit(f"could not download {url}")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    bad = []
    for name, digest in expected().items():
        dest = ASSETS / name
        if dest.exists() and sha256(dest) == digest:
            print(f"  {name}: already present, checksum OK")
            continue
        fetch(name, dest)
        if sha256(dest) != digest:
            bad.append(name)
        else:
            print(f"  {name}: checksum OK")
    if bad:
        sys.exit(f"checksum mismatch: {', '.join(bad)}")
    print(f"all {len(expected())} files verified in {ASSETS}")


if __name__ == "__main__":
    main()
