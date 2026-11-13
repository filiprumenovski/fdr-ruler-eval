#!/usr/bin/env python3
"""fasta_rung.py EVAL_PARQUET TARGET_FA SHUFFLE_FA ATH_SPROT_FA OUTDIR : Rung A FASTAs, digest-based drop list, r per arm.
Digest (LOGOS): cleave after K/R (no P rule), <= 2 missed cleavages, length 7-30, protein N-terminal Met clipped variant
added; I/L folded. r_F = |ATH digest - human digest - shuffle digest| / |human digest|; r_S = |shuffle digest - human
digest - ATH digest| / |human digest|. Drop rule: an arm F peptide is dropped when its I/L-folded sequence is a substring
of any human or contaminant target protein."""
import sys, os, re, json, duckdb, numpy as np
pq_, tfa, sfa, afa, out = sys.argv[1:6]
def fasta(p):
    h, s = None, []
    for l in open(p):
        l = l.rstrip("\n")
        if l.startswith(">"):
            if h is not None: yield h, "".join(s)
            h, s = l[1:], []
        else: s.append(l.strip())
    if h is not None: yield h, "".join(s)
def digest(seqs):
    out_ = set()
    for s in seqs:
        seg = re.findall(r".*?[KR]|.+$", s)
        for start_seq in ([seg, None] if not s.startswith("M") else [seg, re.findall(r".*?[KR]|.+$", s[1:])]):
            if start_seq is None: continue
            for i in range(len(start_seq)):
                p = ""
                for j in range(i, min(i + 3, len(start_seq))):
                    p += start_seq[j]
                    if 7 <= len(p) <= 30: out_.add(p.replace("I", "L"))
    return out_
c = duckdb.connect()
lx = "lambda x: " if tuple(int(v) for v in duckdb.__version__.split(".")[:2]) >= (1, 3) else "x -> "
toks = [r[0] for r in c.execute(f"SELECT DISTINCT unnest(string_split(replace(Proteins, chr(9), ';'), ';')) FROM read_parquet('{pq_}')").fetchall()]
ath_tok = sorted(t for t in toks if t.startswith("entrap_ATH_")); sh_tok = [t for t in toks if t.startswith("entrap_") and not t.startswith("entrap_ATH_")]
ath = dict(fasta(afa)); acc = lambda h: h.split("|")[1] if "|" in h else h.split()[0]
by_acc = {acc(h): (h, s) for h, s in ath.items()}
pin_acc = [t[len("entrap_ATH_"):] for t in ath_tok]
pin_acc_core = [a.split("|")[1] if "|" in a else a for a in pin_acc]
missing = [a for a in pin_acc_core if a not in by_acc]
os.makedirs(out, exist_ok=True)
# arm F FASTA in the PIN's naming: '>entrap_ATH_' + the PIN's accession token form
form_pipe = any("|" in a for a in pin_acc)
with open(os.path.join(out, "entrap_ATH.fasta"), "w") as f:
    for a_, (h, s) in by_acc.items():
        name = ("entrap_ATH_" + h.split()[0]) if form_pipe else ("entrap_ATH_" + a_)
        f.write(f">{name} {' '.join(h.split()[1:])}\n" + "\n".join(s[i:i + 60] for i in range(0, len(s), 60)) + "\n")
H = [s for _, s in fasta(tfa)]; SH = [s for _, s in fasta(sfa)]; A = [s for _, s in by_acc.values()]
dH, dS, dA = digest(H), digest(SH), digest(A)
rF = len(dA - dH - dS) / len(dH); rS = len(dS - dH - dA) / len(dH)
Hs = "|".join(x.upper().replace("I", "L") for x in H); K = 7; km = {Hs[i:i + K] for i in range(len(Hs) - K + 1)}
drop = sorted(p for p in dA if p[:K] in km and p in Hs)
open(os.path.join(out, "drop_from_fasta.txt"), "w").write("\n".join(drop) + "\n")
print(json.dumps({"pin_ath_accessions": len(ath_tok), "pin_shuffle_accessions": len(sh_tok), "ath_accessions_missing_in_fasta": len(missing), "missing_examples": missing[:5],
                  "pin_ath_token_example": ath_tok[:2], "r_F": rF, "r_S": rS, "n_drop_F_digest": len(drop), "n_digest": {"human": len(dH), "shuffle": len(dS), "ath": len(dA)}}))
