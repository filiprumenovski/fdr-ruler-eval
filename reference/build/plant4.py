#!/usr/bin/env python3
"""plant4.py SRC OUT SEED SPEC_JSON : hard items for I4 (seeded, vectorized).
H1 {name, delta, q}: delta*[non-decoy]*[primary_score above its q quantile] + N(0,1)  (tail-conditional)
F1 {name, sigma}: mean per-residue species weight, w(aa) = log f_ATH(aa)/f_human(aa) from the PIN's own rows, + sigma*sd*N(0,1)
F2 {name, sigma}: rank percentile of primary_score over all rows + sigma*N(0,1)  (quality)"""
import sys, json, numpy as np, pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
from scipy.stats import rankdata
src, out, seed, spec = sys.argv[1], sys.argv[2], int(sys.argv[3]), json.loads(sys.argv[4])
t = pq.read_table(src); n = t.num_rows; rng = np.random.default_rng(seed)
lab = t.column("Label").to_numpy(); nd = lab == 1
ps = t.column("primary_score").to_numpy(zero_copy_only=False).astype(float)
prot = np.asarray(pc.replace_substring(t.column("Proteins"), "\t", ";").to_numpy(zero_copy_only=False)).astype(str)
new = {}
if "H1" in spec:
    h = spec["H1"]; tail = ps >= np.nanquantile(ps, h["q"])
    new[h["name"]] = h["delta"] * (nd & tail) + rng.standard_normal(n)
if "F1" in spec:
    f = spec["F1"]
    pep = pc.replace_substring_regex(t.column("Peptide"), r"^[^.]*\.(.*)\.[^.]*$", r"\1")
    bare = pc.replace_substring_regex(pc.replace_substring_regex(pep, r"\[[^\]]*\]|\([^)]*\)", ""), r"[^A-Z]", "")
    u, inv = np.unique(np.asarray(bare.to_numpy(zero_copy_only=False), dtype=object).astype(str), return_inverse=True)
    L = np.array([len(x) for x in u]); off = np.r_[0, np.cumsum(L)[:-1]]
    cc = np.frombuffer("".join(u).encode(), np.uint8).astype(np.int64)
    ath = nd & np.char.startswith(prot, "entrap_ATH_"); hum = nd & ~np.char.startswith(prot, "entrap_")
    def freq(mask):
        s_ = np.unique(inv[mask]); idx = np.concatenate([np.arange(off[i], off[i] + L[i]) for i in s_[:200000]])
        return np.bincount(cc[idx], minlength=256) + 1.0
    fa, fh = freq(ath), freq(hum); w = np.log(fa / fa.sum()) - np.log(fh / fh.sum())
    sc = np.add.reduceat(w[cc], off) / L
    new[f["name"]] = sc[inv] + f["sigma"] * np.nanstd(sc) * rng.standard_normal(len(inv))
if "F2" in spec:
    f = spec["F2"]; r = rankdata(np.nan_to_num(ps, nan=np.nanmin(ps))) / n
    new[f["name"]] = r + f["sigma"] * rng.standard_normal(n)
cols = [c for c in t.column_names if c != "Proteins"]
for k, v in new.items(): t = t.append_column(k, pa.array(v)); cols.append(k)
pq.write_table(t.select(cols + ["Proteins"]), out)
print("wrote", out, n, list(new))
