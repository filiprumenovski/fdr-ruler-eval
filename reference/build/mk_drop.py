#!/usr/bin/env python3
"""mk_drop.py PARQUET HUMAN_FASTA OUT: ATH-only peptides in the PIN (I/L bare) that are substrings of a human protein."""
import sys, re, duckdb, time
src, fa, out = sys.argv[1:4]; t = time.time()
con = duckdb.connect()
LX = "lambda x: " if tuple(int(v) for v in duckdb.__version__.split(".")[:2]) >= (1, 3) else "x -> "
peps = [r[0] for r in con.execute(f"""SELECT DISTINCT replace(regexp_replace(regexp_replace(regexp_replace(Peptide, '^[^.]*\\.(.*)\\.[^.]*$', '\\1'),
  '\\[[^\\]]*\\]|\\([^)]*\\)', '', 'g'), '[^A-Z]', '', 'g'), 'I', 'L') FROM read_parquet('{src}')
  WHERE Label = 1 AND len(list_filter(list_filter(string_split(replace(Proteins, chr(9), ';'), ';'), {LX}x <> ''), {LX}NOT starts_with(x, 'entrap_ATH_'))) = 0""").fetchall()]
seqs, cur = [], []
for line in open(fa):
    if line.startswith(">"):
        if cur: seqs.append("".join(cur))
        cur = []
    else: cur.append(line.strip().upper().replace("I", "L"))
if cur: seqs.append("".join(cur))
H = "|".join(seqs); K = 7
km = {H[i:i + K] for i in range(len(H) - K + 1)}
hits = sorted(p for p in peps if len(p) >= K and p[:K] in km and p in H)
open(out, "w").write("\n".join(hits) + "\n")
print(f"ATH-only PIN peptides {len(peps)}, human proteins {len(seqs)}, human substrings {len(hits)}, {time.time()-t:.0f} s")
