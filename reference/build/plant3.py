#!/usr/bin/env python3
"""plant3.py SRC OUT SEED HUMAN_FASTA SPEC_JSON : mechanism-derived plants, computed from each row's peptide sequence only (never the label).
P2 {name, order 1|2}: per-residue log-likelihood under a Markov model fitted on the human tryptic digest (I/L folded).
P1 {names:[a,b]}: a = sequence-hash N(0,1); b = a * z(asym) + 0.3*hash2, asym = mean log f(xy)/f(yx) over the peptide's dipeptides
   (human digest). Each column alone is near-null in distribution; their product carries the forward/reverse asymmetry.
P3, P4: as plant2.py (composition; protein support)."""
import sys, json, re, numpy as np, pyarrow as pa, pyarrow.parquet as pq, pyarrow.compute as pc
from scipy.special import ndtri
src, out, seed, fasta, spec = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], json.loads(sys.argv[5])
AA = "ACDEFGHKLMNPQRSTVWY"; LUT = np.full(256, 19, np.int64)
for i, ch in enumerate(AA): LUT[ord(ch)] = i
LUT[ord("I")] = AA.index("L")
K = 20  # 19 residues (I folded into L) + 1 'other'
def enc(s): return LUT[np.frombuffer(s.encode(), np.uint8)]
# human tryptic digest (cleave after K/R, 0 missed cleavages, length 7-30)
prots, cur = [], []
for line in open(fasta):
    if line.startswith(">"):
        if cur: prots.append("".join(cur))
        cur = []
    else: cur.append(line.strip().upper())
if cur: prots.append("".join(cur))
dig = [p for prot in prots for p in re.findall(r".*?[KR]|.+$", prot) if 7 <= len(p) <= 30]
D = "|".join(dig); dc = enc(D); sep = np.frombuffer(D.encode(), np.uint8) == ord("|")
ok2 = ~sep[:-1] & ~sep[1:]
C2 = np.bincount(dc[:-1][ok2] * K + dc[1:][ok2], minlength=K * K).reshape(K, K) + 1.0
starts = np.r_[0, np.where(sep)[0] + 1]; C0 = np.bincount(dc[starts], minlength=K) + 1.0
ok3 = ok2[:-1] & ok2[1:]
C3 = np.bincount((dc[:-2][ok3] * K + dc[1:-1][ok3]) * K + dc[2:][ok3], minlength=K ** 3).reshape(K, K, K) + 1.0
logT1 = np.log(C2 / C2.sum(1, keepdims=True)); logP0 = np.log(C0 / C0.sum())
logT2 = np.log(C3 / C3.sum(2, keepdims=True))
F = C2 / C2.sum(); R = np.log(F) - np.log(F.T)          # forward/reverse asymmetry per dipeptide
# PIN sequences
t = pq.read_table(src); n = t.num_rows
pep = pc.replace_substring_regex(t.column("Peptide"), r"^[^.]*\.(.*)\.[^.]*$", r"\1")
bare = pc.replace_substring_regex(pc.replace_substring_regex(pep, r"\[[^\]]*\]|\([^)]*\)", ""), r"[^A-Z]", "")
u, inv = np.unique(np.asarray(bare.to_numpy(zero_copy_only=False), dtype=object).astype(str), return_inverse=True)
L = np.array([len(x) for x in u]); off = np.r_[0, np.cumsum(L)[:-1]]
cc = enc("".join(u)); last = np.zeros(len(cc), bool); last[np.cumsum(L) - 1] = True
pair = np.where(~last[:-1], logT1[cc[:-1], cc[1:]], 0.0); pair = np.r_[pair, 0.0]
ll1 = (logP0[cc[off]] + np.add.reduceat(pair, off)) / L
trip = np.zeros(len(cc)); okt = ~last[:-2] & ~last[1:-1]
trip[:-2] = np.where(okt, logT2[cc[:-2], cc[1:-1], cc[2:]], 0.0)
first_pair = np.where(L > 1, logT1[cc[off], cc[np.minimum(off + 1, len(cc) - 1)]], 0.0)
ll2 = (logP0[cc[off]] + first_pair + np.add.reduceat(trip, off)) / L
asy = np.add.reduceat(np.r_[np.where(~last[:-1], R[cc[:-1], cc[1:]], 0.0), 0.0], off) / np.maximum(L - 1, 1)
def seqhash(salt):
    w = np.random.default_rng(seed * 7919 + salt).integers(1, 2**31 - 1, 64)
    pos = np.arange(len(cc)) - np.repeat(off, L)
    h = np.add.reduceat(((cc + 1) * w[pos % 64]) % (2**31 - 1), off) % (2**31 - 1)
    return ndtri((h + 0.5) / (2**31 - 1))
new = {}
if "P2" in spec:
    new[spec["P2"]["name"]] = (ll2 if spec["P2"].get("order", 1) == 2 else ll1)[inv]
if "P1" in spec:
    a_, b_ = spec["P1"]["names"]; za = seqhash(1); zs = (asy - asy.mean()) / asy.std()
    new[a_] = za[inv]; new[b_] = (za * zs + 0.3 * seqhash(2))[inv]
nd_free = True  # no label used anywhere above
cols = [c for c in t.column_names if c != "Proteins"]
for k, v in new.items(): t = t.append_column(k, pa.array(v)); cols.append(k)
pq.write_table(t.select(cols + ["Proteins"]), out)
print("wrote", out, n, list(new), "digest peptides", len(dig))
