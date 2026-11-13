#!/usr/bin/env python3
"""PIN audit protocol (pin_audit_protocol.md), one reusable implementation.
Usage: pin_audit.py --pin P --name N --work /tmp/pin_audit_work --out DIR [--mlp DIR] [--score COL]
       --decoy-prefix rev_ --entrap-prefix X --r 1.0568 [--seed 0] [--gb-top 5]
"""
import argparse, hashlib, json, os, re, sys, time, warnings, io
import numpy as np, pandas as pd, pyarrow as pa, pyarrow.parquet as pq
from scipy import stats
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.inspection import permutation_importance
try:
    import lightgbm as lgb
    GB_NAME = f"lightgbm {lgb.__version__} LGBMClassifier defaults (n_jobs=8, verbose=-1)"
    def GB(seed): return lgb.LGBMClassifier(random_state=seed, n_jobs=8, verbose=-1)
except ImportError:
    from sklearn.ensemble import HistGradientBoostingClassifier
    GB_NAME = "sklearn HistGradientBoostingClassifier defaults"
    def GB(seed): return HistGradientBoostingClassifier(random_state=seed)

ap = argparse.ArgumentParser()
ap.add_argument("--pin", required=True); ap.add_argument("--name", required=True)
ap.add_argument("--work", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--mlp", default=None, help="logos-boost .mlp/percolator dir with the final score")
ap.add_argument("--score", default="mlp_score")
ap.add_argument("--decoy-prefix", required=True); ap.add_argument("--entrap-prefix", required=True)
ap.add_argument("--r", type=float, required=True); ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--gb-top", type=int, default=5); ap.add_argument("--banned", default="")
ap.add_argument("--phases", default="0123456 7")
ap.add_argument("--exclude-prefix", default="", help="exclude non-decoy rows (and decoys derived from them) whose proteins carry this prefix but not --entrap-prefix")
ap.add_argument("--priority", default="", help="comma list of features (fnmatch globs) run first in Phase 4/7 with LR and GB")
ap.add_argument("--drop-peptides", default="", help="file of entrapment peptides (first column, I/L-normalised bare) removed from the ruler after competition")
ap.add_argument("--tune", action="store_true", help="skip Phase 3; run Phase 4/5/6/7 for --priority features only, then stop")
ap.add_argument("--extra-candidates", default="", help="comma list added to the Phase 4 candidate set")
ap.add_argument("--phase1-only", action="store_true", help="stop after Phase 1 (used to report the other entrapment arm)")
ap.add_argument("--entrap-type", default="shuffled target sequences (K/R-fixed shuffle)")
a = ap.parse_args()
os.makedirs(a.work, exist_ok=True); os.makedirs(a.out, exist_ok=True)
T0 = time.time(); SEED = a.seed; NOM = 0.01
LOG = open(os.path.join(a.out, f"{a.name}.s{SEED}.log"), "w")
def log(*x):
    s = " ".join(str(v) for v in x); print(s, flush=True); LOG.write(s + "\n"); LOG.flush()
warnings.filterwarnings("ignore")
R = {"inputs": vars(a), "gb": GB_NAME}
def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
    return h.hexdigest()

# ---------------- PHASE 0 (DuckDB) ----------------
import duckdb
LX = "lambda x: " if tuple(int(v) for v in duckdb.__version__.split(".")[:2]) >= (1, 3) else "x -> "
PT = {}
t = time.time()
con = duckdb.connect(os.path.join(a.work, "db.duckdb")); con.execute(f"SET threads={len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count()}; SET temp_directory='{a.work}/tmp'")
pqpath = os.path.join(a.work, "pin.parquet")
R["source_sha256"] = sha(a.pin)
if a.pin.endswith(".parquet"):
    # full-feature parquet written by logos-boost (strings: SpecId, Peptide, Proteins tab-joined; the rest f64)
    names = [r_[0] for r_ in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{a.pin}')").fetchall()]
    names = [c for c in names if c != "Proteins"] + ["Proteins"]; n = len(names)
    con.execute(f"""CREATE OR REPLACE TABLE pin AS SELECT {', '.join(f'"{c}"' for c in names[:-1])},
        replace("Proteins", chr(9), ';') AS "Proteins" FROM read_parquet('{a.pin}')""")
    R["source_format"] = "parquet (logos-boost full table)"
else:
    with open(a.pin, "rb") as f: names = f.readline().rstrip(b"\r\n").decode().split("\t")
    n = len(names); textc = {"SpecId", "Peptide", names[-1]}
    sel = []
    for i, c in enumerate(names[:-1]):
        e = f"p[{i+1}]"
        sel.append(f"{e} AS \"{c}\"" if c in textc else f"TRY_CAST({e} AS DOUBLE) AS \"{c}\"")
    sel.append(f"array_to_string(p[{n}:], ';') AS \"{names[-1]}\"")
    con.execute(f"""CREATE OR REPLACE TABLE pin AS
      WITH raw AS (SELECT string_split(line, chr(9)) AS p FROM read_csv('{a.pin}', delim=chr(31), header=false, skip=1,
         columns={{'line':'VARCHAR'}}, quote='', escape='', auto_detect=false, parallel=true, max_line_size=10000000))
      SELECT {', '.join(sel)} FROM raw WHERE p[1] <> 'DefaultDirection' AND len(p) >= {n}""")
con.execute(f"COPY pin TO '{pqpath}' (FORMAT parquet)")
R["parquet_sha256"] = sha(pqpath); R["parquet_bytes"] = os.path.getsize(pqpath)
R["rows_raw"] = con.execute("SELECT count(*) FROM pin").fetchone()[0]; R["cols_raw"] = n
score = a.score
if a.mlp:
    con.execute(f"""CREATE OR REPLACE TABLE mlp AS SELECT PSMId::VARCHAR AS SpecId, score::DOUBLE AS "{score}" FROM read_csv(
        ['{a.mlp}/percolator.psms.tsv', '{a.mlp}/percolator.decoys.tsv'], delim=chr(9), header=true)""")
    con.execute(f"CREATE OR REPLACE TABLE pin AS SELECT pin.*, mlp.\"{score}\" FROM pin LEFT JOIN mlp USING (SpecId)")
    R["mlp_join"] = {"mlp_rows": con.execute("SELECT count(*) FROM mlp").fetchone()[0]}
R["rows_no_score"] = con.execute(f'SELECT count(*) FROM pin WHERE "{score}" IS NULL OR isnan("{score}")').fetchone()[0]
nan_score = R["rows_no_score"]
dp, ep = a.decoy_prefix, a.entrap_prefix
xp = a.exclude_prefix  # non-decoy tokens with this prefix but not the entrapment prefix are excluded (with their decoys)
if xp and xp.startswith(ep):   # excluded arm is a sub-prefix of the entrapment prefix (arm S: entrap_ minus entrap_ATH_)
    ISX = f"starts_with(x, '{xp}')"; ISE = f"(starts_with(x, '{ep}') AND NOT starts_with(x, '{xp}'))"
else:
    ISX = (f"(starts_with(x, '{xp}') AND NOT starts_with(x, '{ep}'))" if xp else "false"); ISE = f"starts_with(x, '{ep}')"
con.execute(f"""CREATE OR REPLACE TABLE cl AS SELECT *,
  CASE WHEN Label = -1 THEN (CASE WHEN len(und) > 0 AND len(list_filter(und, {LX}{ISX})) = len(und) THEN 'X' ELSE 'D' END)
       WHEN len(nd) > 0 AND len(list_filter(nd, {LX}{ISX})) = len(nd) THEN 'X'
       WHEN len(list_filter(nd, {LX}{ISX})) > 0 THEN 'B'
       WHEN len(list_filter(nd, {LX}{ISE})) = len(nd) AND len(nd) > 0 THEN 'E'
       WHEN len(list_filter(nd, {LX}{ISE})) = 0 THEN 'T' ELSE 'B' END AS cls,
  (Label = -1) <> (len(list_filter(pl, {LX}NOT starts_with(x, '{dp}'))) = 0) AS mism
  FROM (SELECT *, list_transform(pl, {LX}regexp_replace(x, '^{dp}(rev_)?', '')) AS und FROM (
        SELECT *, list_filter(string_split("{names[-1]}", ';'), {LX}x <> '') AS pl,
               list_filter(list_filter(string_split("{names[-1]}", ';'), {LX}x <> ''), {LX}NOT starts_with(x, '{dp}')) AS nd
        FROM pin WHERE "{score}" IS NOT NULL AND NOT isnan("{score}")))""")
R["rows_by_class"] = dict(con.execute("SELECT cls, count(*) FROM cl GROUP BY cls").fetchall())
R["decoy_label_vs_prefix_mismatch"] = con.execute("SELECT count(*) FROM cl WHERE mism").fetchone()[0]
con.execute(f"""CREATE OR REPLACE TABLE pepl AS
  WITH s AS (SELECT *, regexp_replace(Peptide, '^[^.]*\\.(.*)\\.[^.]*$', '\\1') AS modpep, (cls='D')::INT AS isd
             FROM cl WHERE cls NOT IN ('B', 'X')
             QUALIFY row_number() OVER (PARTITION BY ScanNr, ExpMass ORDER BY "{score}" DESC, isd DESC) = 1)
  SELECT *, replace(regexp_replace(regexp_replace(modpep, '\\[[^\\]]*\\]|\\([^)]*\\)', '', 'g'), '[^A-Z]', '', 'g'), 'I', 'L') AS bare
  FROM s QUALIFY row_number() OVER (PARTITION BY modpep ORDER BY "{score}" DESC, isd DESC) = 1""")
R["spectra"] = con.execute("SELECT count(*) FROM (SELECT DISTINCT ScanNr, ExpMass FROM cl WHERE cls NOT IN ('B','X'))").fetchone()[0]
if a.drop_peptides:
    dl = [l.strip().split(",")[0].split("\t")[0] for l in open(a.drop_peptides) if l.strip()]
    dl = sorted({re.sub(r"[^A-Z]", "", x.upper()).replace("I", "L") for x in dl} - {""})
    con.execute("CREATE OR REPLACE TABLE dropl AS SELECT unnest(?) AS bare", [dl])
    R["drop_list"] = {"file": a.drop_peptides, "unique_bare": len(dl),
                      "matched_E_peptides": con.execute("SELECT count(*) FROM pepl WHERE cls='E' AND bare IN (SELECT bare FROM dropl)").fetchone()[0]}
    con.execute("DELETE FROM pepl WHERE cls='E' AND bare IN (SELECT bare FROM dropl)")
    log("drop list", R["drop_list"])
R["peptides_by_class"] = dict(con.execute("SELECT cls, count(*) FROM pepl GROUP BY cls").fetchall())
PT["phase0"] = time.time() - t
log("phase0", R["rows_by_class"], R["peptides_by_class"], round(PT["phase0"], 1), "s")
NE_ALL = R["peptides_by_class"].get("E", 0)
if NE_ALL < 2000:
    R["stopped"] = f"entrapment peptides {NE_ALL} < 2000"; json.dump(R, open(os.path.join(a.out, f"{a.name}.s{SEED}.json"), "w"), indent=1, default=str)
    log("STOP", R["stopped"]); sys.exit(0)

# ---------------- PHASE 1 (DuckDB q-values) ----------------
t = time.time(); r = a.r
con.execute(f"""CREATE OR REPLACE TABLE pq AS SELECT *, min(q0) OVER (ORDER BY "{score}" DESC, isd DESC, modpep ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING) AS q_base
  FROM (SELECT *, (sum(isd) OVER w + 1)::DOUBLE / greatest(sum(1 - isd) OVER w, 1) AS q0, (hash(bare || '{SEED}') % 5)::INT AS fold
        FROM pepl WINDOW w AS (ORDER BY "{score}" DESC, isd DESC, modpep ROWS UNBOUNDED PRECEDING))""")
def cp(k, n):
    """Wilson 95% interval for k/n (protocol v2)."""
    if n == 0: return (np.nan, np.nan)
    z = 1.959963984540054; ph = k / n; den = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / den; h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return max(0.0, c - h), min(1.0, c + h)
def mk(qcut, nt, ne, nd):
    n_ = nt + ne; lo, hi = cp(ne, n_); f = 1 + 1 / r; low = ne / n_ if n_ else np.nan
    return dict(q=qcut, NT=int(nt), NE=int(ne), ND=int(nd), lower=low, lower_ci=(lo, hi), comb=low * f, comb_ci=(lo * f, hi * f))
P1 = [mk(qc, *con.execute(f"SELECT count(*) FILTER (cls='T'), count(*) FILTER (cls='E'), count(*) FILTER (cls='D') FROM pq WHERE q_base <= {qc}").fetchone())
      for qc in (0.001, 0.005, 0.01, 0.02, 0.05)]
R["phase1"] = P1; log("phase1 1%", P1[2])
# PHASE 8 certificate (on this ruler, Phase 1 rules): rho = N_E(1+1/r)/N_D at q = 1%; one-sided exact conditional binomial UCB
_ne, _nd = P1[2]["NE"], P1[2]["ND"]
_pu = stats.beta.ppf(0.95, _ne + 1, _nd) if _nd > 0 else 1.0
_rho = _ne * (1 + 1 / r) / _nd if _nd else float("inf"); _rho_u = _pu / (1 - _pu) * (1 + 1 / r)
_eps = max(0.0, float(np.log(_rho_u))); _qc = NOM / np.exp(_eps)
_ntc = con.execute(f"SELECT count(*) FILTER (cls='T') FROM pq WHERE q_base <= {_qc}").fetchone()[0]
R["certificate"] = {"rho_point": _rho, "rho_ucb95": _rho_u, "epsilon_nats": _eps, "certified_q": _qc, "n_targets_certified": int(_ntc)}
log("certificate", R["certificate"])
if a.phase1_only:
    json.dump(R, open(os.path.join(a.out, f"{a.name}.s{SEED}.json"), "w"), indent=1, default=str); log("phase1-only done"); sys.exit(0)
# export peptide table to numpy (float32 features) via arrow
skip = {"SpecId", "Label", "ScanNr", "ExpMass", "Peptide", names[-1], "cls", "modpep", "bare", "isd", score, "pl", "nd", "mism", "q0", "q_base", "fold"}
feats0 = [c for c in names[:-1] if c not in skip]
tb = con.execute(f'SELECT cls, "{score}" AS s, q_base, fold, "{names[-1]}" AS prot, ' + ", ".join(f'"{c}"' for c in feats0) + ' FROM pq ORDER BY "' + score + '" DESC, isd DESC, modpep').fetchnumpy()
_f = lambda v, dt: np.ma.filled(np.ma.asarray(v).astype(dt), np.nan)
cls = np.asarray(tb["cls"]).astype(str); S = _f(tb["s"], np.float64); q_base = _f(tb["q_base"], np.float64)
FOLD = np.asarray(tb["fold"]).astype(int); PROT = [str(x) for x in np.asarray(tb["prot"])]
X = np.empty((len(cls), len(feats0)), np.float32)
for j_, c_ in enumerate(feats0): X[:, j_] = _f(tb[c_], np.float32)   # column copy into the design matrix (no row loop)
del tb
X[~np.isfinite(X)] = np.nan
con.close(); os.remove(os.path.join(a.work, "db.duckdb"))  # free tmpfs memory before the model phases
isD = cls == "D"; isE = cls == "E"; isT = cls == "T"; y_td = (~isD).astype(int)
def tdc_q(s, d):
    s = np.asarray(s, float); order = np.lexsort((~d, -s))
    dd = np.cumsum(d[order]); tt = np.cumsum(~d[order])
    q = (dd + 1) / np.maximum(tt, 1); q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(len(s)); out[order] = q; return out
def counts(s, qcut=NOM):
    q = tdc_q(s, isD); acc = q <= qcut
    return mk(qcut, (acc & isT).sum(), (acc & isE).sum(), (acc & isD).sum())
def fmt(c): return f"{100*c['comb']:.2f}% [{100*c['comb_ci'][0]:.2f}, {100*c['comb_ci'][1]:.2f}]"
PT["phase1"] = time.time() - t

# ---------------- PHASE 2 (vectorized) ----------------
t = time.time()
ok_const = np.array([np.nanmax(X[:, j]) > np.nanmin(X[:, j]) if np.isfinite(X[:, j]).any() else False for j in range(X.shape[1])])
const = [c for c, o in zip(feats0, ok_const) if not o]
feats = [c for c, o in zip(feats0, ok_const) if o]; X = X[:, ok_const]
R["n_features"] = len(feats); R["constant_dropped"] = const
COMP_RE = r"(?i)^(len|length|peplen|charge\d*|calcmass|pepmass|missed_cleavages|n_mods|enzn|enzc|enzint|ntt)$"
comp = [c for c in feats if re.search(COMP_RE, c)]
R["composition_regex"] = COMP_RE; R["composition"] = comp
def auc_cols(Xa, Xb):
    """Mann-Whitney AUC P(b > a) per column, NaNs dropped per column (vectorized via ranks on NaN-free columns)."""
    Z = np.vstack([Xa, Xb]); na, nb = len(Xa), len(Xb); out = np.full(Z.shape[1], np.nan)
    clean = ~np.isnan(Z).any(0)
    if clean.any():
        rk = stats.rankdata(Z[:, clean], axis=0); out[clean] = (rk[na:].sum(0) - nb * (nb + 1) / 2) / (na * nb)
    for j in np.where(~clean)[0]:
        a_, b_ = Xa[:, j], Xb[:, j]; a_ = a_[~np.isnan(a_)]; b_ = b_[~np.isnan(b_)]
        if len(a_) and len(b_):
            rk = stats.rankdata(np.r_[a_, b_]); out[j] = (rk[len(a_):].sum() - len(b_) * (len(b_) + 1) / 2) / (len(a_) * len(b_))
    return out
def ks_cols(Xa, Xb):
    """Two-sample KS per column, all columns at once: sort the pooled column, cumulative class counts, ties resolved at run ends."""
    na = (~np.isnan(Xa)).sum(0).astype(float); nb = (~np.isnan(Xb)).sum(0).astype(float)
    Z = np.vstack([Xa, Xb]).astype(np.float64); lab = np.r_[np.zeros(len(Xa)), np.ones(len(Xb))]
    Z = np.where(np.isnan(Z), np.inf, Z)
    o = np.argsort(Z, axis=0, kind="stable"); Zs = np.take_along_axis(Z, o, 0); L = lab[o]
    ca = np.cumsum(1 - L, 0) / np.maximum(na, 1); cb = np.cumsum(L, 0) / np.maximum(nb, 1)
    end = np.ones_like(Zs, bool); end[:-1] = Zs[:-1] != Zs[1:]
    D = np.where(end & np.isfinite(Zs), np.abs(ca - cb), 0).max(0)
    en = na * nb / np.maximum(na + nb, 1)
    pv = stats.distributions.kstwobign.sf(D * np.sqrt(en))
    bad = (na < 10) | (nb < 10); D[bad] = np.nan; pv[bad] = np.nan
    return D, pv
Xd, Xe = X[isD], X[isE]
KS, KSP = ks_cols(Xd, Xe); AED = auc_cols(Xd, Xe); ATD = auc_cols(X[isD], X[~isD])
md, me = np.nanmean(Xd, 0), np.nanmean(Xe, 0); sp = np.sqrt((np.nanvar(Xd, 0) + np.nanvar(Xe, 0)) / 2)
SMD = np.where(sp > 0, (me - md) / np.where(sp > 0, sp, 1), 0)
P2 = [dict(f=c, KS=float(KS[j]), KSp=float(KSP[j]), SMD=float(SMD[j]), AUC_ED=float(AED[j]), AUC_TD=float(ATD[j]), comp=c in comp)
      for j, c in enumerate(feats) if np.isfinite(KS[j])]
P2 = sorted(P2, key=lambda d: -d["KS"]); R["phase2"] = P2
PT["phase2"] = time.time() - t
log("phase2 top", [(d["f"], round(d["KS"], 3)) for d in P2[:10]], round(PT["phase2"], 1), "s")
COL = {c: j for j, c in enumerate(feats)}

from joblib import Parallel, delayed
NW = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
XP, FP, YP, MP = (os.path.join(a.work, n) for n in ("Xf.npy", "fold.npy", "ytd.npy", "isde.npy"))
np.save(XP, X); np.save(FP, FOLD); np.save(YP, y_td); np.save(MP, np.c_[isD, isE, isT].astype(np.int8))
XSP = os.path.join(a.work, "Xs.npy")
_mu = np.nanmean(X, 0); _sd = np.nanstd(X, 0); _sd[~(_sd > 0)] = 1
np.save(XSP, ((np.where(np.isnan(X), _mu, X) - _mu) / _sd).astype(np.float32))
def _cls_fold(ix, rows_path, ylab, k, seed, fold_key):
    """Held-out boosted classifier on a row subset (indices file), one fold; returns (k, test idx, scores, model)."""
    import numpy as np, lightgbm as lgb
    Xm_ = np.load(XP, mmap_mode="r"); rows = np.load(rows_path); y = np.load(ylab); fk = np.load(fold_key)
    tr, te = rows[fk != k], rows[fk == k]
    m = lgb.LGBMClassifier(random_state=seed, n_jobs=1, verbose=-1).fit(np.asarray(Xm_[tr][:, ix]), y[fk != k])
    return k, te, m.predict_proba(np.asarray(Xm_[te][:, ix]))[:, 1], m
def _perm_imp(m, ix, rows_path, ylab, fold_key, k, j, seed):
    """AUC drop on the held-out fold when column j is permuted (3 repeats)."""
    import numpy as np
    from sklearn.metrics import roc_auc_score
    Xm_ = np.load(XP, mmap_mode="r"); rows = np.load(rows_path); y = np.load(ylab); fk = np.load(fold_key)
    te = rows[fk == k]; Z = np.array(Xm_[te][:, ix]); yt = y[fk == k]
    base_ = roc_auc_score(yt, m.predict_proba(Z)[:, 1]); g = np.random.default_rng(seed * 1000 + j); d = []
    for _ in range(3):
        Zp = Z.copy(); Zp[:, j] = g.permutation(Zp[:, j]); d.append(base_ - roc_auc_score(yt, m.predict_proba(Zp)[:, 1]))
    return k, j, float(np.mean(d))
def heldout(cols_list, rows, ylab_arr, fold_arr, tag, imp_index=None):
    """Parallel held-out boosted AUC for several column sets on the same rows (all folds x sets as tasks)."""
    rp, yp_, fp_ = (os.path.join(a.work, f"{tag}_{n}.npy") for n in ("rows", "y", "fold"))
    np.save(rp, rows); np.save(yp_, ylab_arr); np.save(fp_, fold_arr)
    tasks = [(si, [COL[c] for c in cols], k) for si, cols in enumerate(cols_list) if cols for k in range(5)]
    res = Parallel(n_jobs=NW, backend="loky", max_nbytes=None)(delayed(_cls_fold)(ix, rp, yp_, k, SEED, fp_) for si, ix, k in tasks)
    oofs = {si: np.zeros(len(rows)) for si in range(len(cols_list))}; pos = {r_: i_ for i_, r_ in enumerate(rows)}
    models = {}
    idx_of = np.empty(int(rows.max()) + 1, np.int64); idx_of[rows] = np.arange(len(rows))
    for (si, ix, k), (k2, te, sc, m) in zip(tasks, res): oofs[si][idx_of[te]] = sc; models[(si, k)] = (m, ix)
    imps = None
    if imp_index is not None and cols_list[imp_index]:
        m0 = [(k, models[(imp_index, k)]) for k in range(5)]
        ires = Parallel(n_jobs=NW, backend="loky", max_nbytes=None)(delayed(_perm_imp)(m, ix, rp, yp_, fp_, k, j, SEED)
                                                                     for k, (m, ix) in m0 for j in range(len(ix)))
        I = np.zeros((5, len(cols_list[imp_index])))
        for k, j, v in ires: I[k, j] = v
        imps = I
    return oofs, imps
def summarize(y_, oof):
    A = roc_auc_score(y_, oof); n1, n0 = y_.sum(), len(y_) - y_.sum()
    q1, q2 = A / (2 - A), 2 * A * A / (1 + A)
    se = np.sqrt((A * (1 - A) + (n1 - 1) * (q1 - A * A) + (n0 - 1) * (q2 - A * A)) / (n1 * n0))
    p = y_.mean(); H = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
    o = np.clip(oof, 1e-12, 1 - 1e-12); ce = -(y_ * np.log2(o) + (1 - y_) * np.log2(1 - o))
    bits = H - ce.mean(); bse = ce.std() / np.sqrt(len(ce))
    return dict(AUC=A, AUC_ci=(A - 1.96 * se, A + 1.96 * se), bits_per_row=bits, bits_se=bse, bits_total=bits * len(ce),
                sig=bool(A - 1.96 * se > 0.5 and bits > 2 * bse))
# ---------------- PHASE 3 ----------------
if a.tune:
    P3 = {'carriers': [], 'seconds': 0.0, 'joint_leak': False}
else:
    t3 = time.time(); m = isD | isE; rows3 = np.where(m)[0]; ym = isE[m].astype(int); fm = FOLD[m]
    top5 = [d["f"] for d in P2[:5]]
    c_all = feats; c_nocomp = [c for c in feats if c not in comp]; c_both = [c for c in c_nocomp if c not in top5]
    oofs3, I3 = heldout([c_all, c_nocomp, c_both], rows3, ym, fm, "p3", imp_index=2)
    P3 = {}
    for nm, cols, si in (("all", c_all, 0), ("minus_composition", c_nocomp, 1), ("minus_composition_and_top5", c_both, 2)):
        P3[nm] = dict(n_feat=len(cols), **summarize(ym, oofs3[si]))
    P3["minus_composition_and_top5"]["perm"] = sorted([(c, float(I3[:, j].mean()), float(I3[:, j].std())) for j, c in enumerate(c_both)], key=lambda z: -z[1])
    P3["joint_leak"] = bool(P3["minus_composition"]["sig"] and P3["minus_composition_and_top5"]["sig"])
    # v2.1 carrier set: held-out AUC drop >= 0.005 under permutation, at most 10, from the model trained after both removals
    P3["carriers"] = [c for c, mu, sd in P3["minus_composition_and_top5"]["perm"] if mu >= 0.005][:10] if P3["joint_leak"] else []
    P3["seconds"] = time.time() - t3; R["phase3"] = P3
    log("phase3", {k: (round(v["AUC"], 4), v["sig"]) for k, v in P3.items() if isinstance(v, dict)}, P3["carriers"], round(P3["seconds"]), "s")

# ---------------- PHASE 4 ----------------
banned = [b for b in a.banned.split(",") if b]
SETS = {}
if P3["carriers"]: SETS["{" + "+".join(P3["carriers"]) + "}"] = list(P3["carriers"])
def members(f): return SETS.get(f, [f])
cand = list(dict.fromkeys([d["f"] for d in P2[:10]] + list(SETS) + [b for b in banned if b in feats] + [c for c in a.extra_candidates.split(",") if c in feats]))
gb_set = set([d["f"] for d in P2[:a.gb_top]] + list(SETS))
R["sets"] = SETS
import fnmatch
prio = [c for c in feats if any(fnmatch.fnmatch(c, g) for g in a.priority.split(",") if g)]
prio = [c for c in prio if c in cand or any(not any(ch in g for ch in "*?[") and g == c for g in a.priority.split(","))] if prio else []
prio = [c for c in prio if c in cand] + [c for c in prio if c not in cand]
cand += [c for c in prio if c not in cand]; gb_set |= set(prio)
R["priority"] = prio
R["candidates"] = cand; R["gb_candidates"] = sorted(gb_set)
_inc = {c for f in cand for c in members(f)}
base = [c for c in feats if c not in _inc]
def _fold(model, ix, pj, frac, seed, k):
    """pj: list of positions permuted together with one shared row permutation."""
    """One fold of one condition: train on folds != k, score fold k. Reads the shared float32 matrices by memory map."""
    import numpy as np
    Xm_ = np.load(XSP if model == "LR" else XP, mmap_mode="r"); FO = np.load(FP, mmap_mode="r"); yy = np.load(YP, mmap_mode="r")
    Z = np.asarray(Xm_[:, ix], dtype=np.float32)
    if pj is not None:
        g = np.random.default_rng(seed + 1)
        if frac is None or frac >= 1: Z[:, pj] = Z[g.permutation(len(Z))][:, pj]
        elif frac > 0:
            idx = g.choice(len(Z), int(round(frac * len(Z))), replace=False); Z[np.ix_(idx, pj)] = Z[np.ix_(g.permutation(idx), pj)]
    tr, te = FO != k, FO == k
    if model == "LR":
        return k, newton_lr(Z[tr], yy[tr], Z[te], threads=1)
    import lightgbm as lgb
    m = lgb.LGBMClassifier(random_state=seed, n_jobs=1, verbose=-1).fit(Z[tr], yy[tr])
    return k, m.predict_proba(Z[te])[:, 1]
LR_MAXIT, LR_TOL = 30, 1e-3
def newton_lr(Xt, yt, Xe, threads=8):
    """L2 logistic regression with sklearn's default objective (C = 1, unpenalized intercept), Newton steps to |step| < LR_TOL."""
    import numpy as np
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=threads, user_api="blas"):
        return _newton(Xt, yt, Xe)
def _newton(Xt, yt, Xe):
    n, p = Xt.shape; Xa = np.hstack([Xt, np.ones((n, 1), np.float32)]); y = yt.astype(np.float64)
    w = np.zeros(p + 1); P = np.ones(p + 1); P[-1] = 0
    for it in range(LR_MAXIT):
        eta = Xa @ w.astype(np.float32); pr = 1 / (1 + np.exp(-eta.astype(np.float64)))
        g = Xa.T @ (pr - y).astype(np.float32) + P * w
        W = (pr * (1 - pr)).astype(np.float32)
        H = (Xa * W[:, None]).T @ Xa + np.diag(P)
        step = np.linalg.solve(H.astype(np.float64), g.astype(np.float64)); w = w - step
        if np.abs(step).max() < LR_TOL: break
    NEWTON_ITERS.append(it + 1)
    return np.hstack([Xe, np.ones((len(Xe), 1), np.float32)]) @ w.astype(np.float32)
NEWTON_ITERS = []
def job(cols, model, perm=None, frac=None):
    ix = [COL[c] for c in cols]; pj = [cols.index(x) for x in members(perm)] if perm is not None else None
    return (model, ix, pj, frac, SEED, XP, FP, YP, 8)
def rescore(cols, model, perm=None, frac=None):
    return rescore_many([(cols, model, perm, frac)])[0]
def rescore_many(specs):
    """Every (condition x fold) fit runs as its own task on a process pool sized to the cores (LightGBM n_jobs=1, BLAS 1 thread)."""
    tasks = []
    for i, sp in enumerate(specs):
        model, ix, pj, frac, seed = job(*sp)[:5]
        tasks += [(i, model, ix, pj, frac, seed, k) for k in range(5)]
    NW = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count()
    res = Parallel(n_jobs=NW, backend="loky", max_nbytes=None)(delayed(_fold)(*t_[1:]) for t_ in tasks)
    oofs = [np.zeros(len(FOLD)) for _ in specs]
    for t_, (k, sc) in zip(tasks, res): oofs[t_[0]][FOLD == k] = sc
    return [counts(o) for o in oofs]
t = time.time()
# ---------------- PHASE 5 ----------------
t = time.time(); s = S; nb = 50
edges = np.unique(np.quantile(s, np.linspace(0, 1, nb + 1)))
b = np.clip(np.searchsorted(edges, s, side="right") - 1, 0, len(edges) - 2)
ndb = np.bincount(b, weights=isD, minlength=len(edges) - 1); nnb = np.bincount(b, weights=~isD, minlength=len(edges) - 1)
ratio = np.where(nnb > 0, ndb / np.maximum(nnb, 1), np.inf)
for width in (0.05, 0.10, 0.20):
    sel = np.abs(ratio - 1) <= width; band = sel[b]
    if (band & isD).sum() >= 2000: break
bands = [(float(edges[k]), float(edges[k + 1]), int(nnb[k]), int(ndb[k])) for k in np.where(sel)[0]]
R["phase5_band"] = {"width": width, "bins": bands, "NT": int((band & isT).sum()), "NE": int((band & isE).sum()), "ND": int((band & isD).sum())}
P5 = {}
ks_of = lambda f: max(next(d["KS"] for d in P2 if d["f"] == c) for c in members(f))
if SETS:
    rows5 = np.where(band & (isD | isT))[0]
    ok5 = len(rows5) >= 100 and 0 < isT[rows5].sum() < len(rows5)
    o5, _ = heldout(list(SETS.values()), rows5, isT[rows5].astype(int), FOLD[rows5], "p5") if ok5 else ({}, None)
    for si, (f, cs) in enumerate(SETS.items()):
        sm = summarize(isT[rows5].astype(int), o5[si]) if ok5 else dict(AUC=np.nan, AUC_ci=(np.nan, np.nan))
        P5[f] = dict(KS3=np.nan, p3=np.nan, AUC3=sm["AUC"], AUC3_ci=sm["AUC_ci"], KS_E_band=np.nan, AUC_E_band=np.nan,
                     agree=bool(np.isfinite(sm["AUC"]) and (sm["AUC"] - 0.5) >= 0.5 * (P3["minus_composition_and_top5"]["AUC"] - 0.5)),
                     kind="set: held-out boosted AUC, decoys vs band targets; agrees if AUC-0.5 >= half the Phase 3 (after removals) AUC-0.5")
for f in [c for c in cand if c not in SETS]:
    x = X[:, COL[f]]
    def two(ma, mb):
        xa, xb = x[ma], x[mb]; xa = xa[np.isfinite(xa)]; xb = xb[np.isfinite(xb)]
        if len(xa) < 10 or len(xb) < 10: return (np.nan, np.nan, np.nan)
        ks = stats.ks_2samp(xa, xb); yy = np.r_[np.zeros(len(xa)), np.ones(len(xb))]
        return (ks.statistic, ks.pvalue, roc_auc_score(yy, np.r_[xa, xb]))
    third = two(band & isD, band & isT); ent = two(band & isD, band & isE)
    p2 = next(d for d in P2 if d["f"] == f)
    agree = bool(np.isfinite(third[0]) and third[0] >= 0.5 * p2["KS"])  # v2.1: decoys vs band targets reproduce at least half the decoy-vs-entrapment KS
    P5[f] = dict(KS3=third[0], p3=third[1], AUC3=third[2], KS_E_band=ent[0], AUC_E_band=ent[2], agree=bool(agree))
R["phase5"] = P5; PT['phase5'] = time.time() - t; t = time.time()

# ---------------- PHASE 6 ----------------
passing = (q_base <= NOM)
import pyarrow as _pa, pyarrow.compute as _pc
_lst = _pc.split_pattern(_pa.array(PROT), ";"); _row = _pc.list_parent_indices(_lst).to_numpy(); _acc = _pc.list_flatten(_lst)
_u, _inv = np.unique(np.asarray(_acc.to_numpy(zero_copy_only=False), dtype=object).astype(str), return_inverse=True)
_ok = _u[_inv] != ""; _pairs = np.unique(np.c_[_row[_ok], _inv[_ok]], axis=0)
_cnt = np.bincount(_pairs[:, 1], weights=passing[_pairs[:, 0]], minlength=len(_u))
npass = np.zeros(len(PROT)); np.maximum.at(npass, _pairs[:, 0], _cnt[_pairs[:, 1]])
P6 = {}
for f in cand:
    rr = []
    for c in members(f):
        x = X[:, COL[c]]; ok = np.isfinite(x) & (q_base <= 0.05); rr.append(float(stats.spearmanr(x[ok], npass[ok]).correlation))
    rho = max(rr, key=abs)
    P6[f] = dict(rho=float(rho), flag=bool(abs(rho) > 0.2))
R["phase6"] = P6; PT['phase6'] = time.time() - t; t = time.time()

t4 = time.time(); P4 = {}; TIMES = {}
for mdl in ("LR", "GB"):
    t = time.time(); P4[("A", mdl)] = rescore(base, mdl); TIMES[f"A_{mdl}"] = time.time() - t  # one condition, 5 folds in parallel
    log("4A", mdl, fmt(P4[("A", mdl)]), P4[("A", mdl)]["NT"], round(TIMES[f"A_{mdl}"]), "s")
P7 = {}
def p4_for(fs):
    keys, specs = [], []
    for f in fs:
        for mdl in ("LR", "GB"):
            if mdl == "GB" and f not in gb_set: continue
            keys += [("B", mdl, f), ("C", mdl, f)]; specs += [(base + members(f), mdl, None, None), (base + members(f), mdl, f, None)]
    for k_, v_ in zip(keys, rescore_many(specs)): P4[k_] = v_
    for f in fs:
        log("4", f, "LR B", fmt(P4[("B", "LR", f)]), "C", fmt(P4[("C", "LR", f)]),
            ("GB B " + fmt(P4[("B", "GB", f)]) + " C " + fmt(P4[("C", "GB", f)])) if f in gb_set else "")
def dose_for(pairs):
    specs = [(base + members(f), m, f, fr) for f, m in pairs for fr in (0.25, 0.5, 0.75)]
    res = rescore_many(specs) if specs else []
    for n_, (f, m) in enumerate(pairs):
        steps = [P4[("B", m, f)]["comb"]] + [c["comb"] for c in res[3 * n_:3 * n_ + 3]] + [P4[("C", m, f)]["comb"]]
        rho = stats.spearmanr([0, 25, 50, 75, 100], steps).correlation
        P7[(f, m)] = dict(steps=steps, monotone=bool(all(steps[i + 1] <= steps[i] + 0.0005 for i in range(4))))
if prio:
    tp = time.time(); p4_for(prio); dose_for([(f, m) for f in prio for m in ("LR", "GB")])
    PL = [f"# {a.name} priority rows (seed {SEED}); A = all features minus {len(cand)} candidates; combined FDP at decoy q<=1%",
          "| feature | A LR / GB | B LR / GB | C LR / GB | inflation B-A pp (LR / GB) | dose monotone (LR / GB), 0/25/50/75/100% | third-null KS (p) | Phase 6 rho, flag |", "|---|---|---|---|---|---|---|---|"]
    for f in prio:
        g = lambda c, m: P4[(c, m, f)] if c != "A" else P4[("A", m)]
        d7 = lambda m: f"{'y' if P7[(f, m)]['monotone'] else 'n'} (" + "/".join(f"{100*x:.2f}" for x in P7[(f, m)]["steps"]) + ")"
        PL.append(f"| {f} | {fmt(g('A','LR'))} / {fmt(g('A','GB'))} | {fmt(g('B','LR'))} / {fmt(g('B','GB'))} | {fmt(g('C','LR'))} / {fmt(g('C','GB'))} | "
                  f"{100*(g('B','LR')['comb']-g('A','LR')['comb']):+.2f} / {100*(g('B','GB')['comb']-g('A','GB')['comb']):+.2f} | {d7('LR')} / {d7('GB')} | "
                  f"{P5[f]['KS3']:.4f} ({P5[f]['p3']:.1e}) | {P6[f]['rho']:.3f}, {P6[f]['flag']} |")
    open(os.path.join(a.out, f"{a.name}.s{SEED}.priority.md"), "w").write("\n".join(PL) + "\n")
    log("priority done", round(time.time() - tp), "s"); [log(l) for l in PL]
    if a.tune: sys.exit(0)
p4_for([f for f in cand if f not in prio])
R["phase4"] = {"|".join(k): v for k, v in P4.items()}; R["times"] = TIMES

PT['phase4'] = time.time() - t4
# ---------------- PHASE 7 ----------------
t = time.time()
A = P4[("A", "LR")]
dose_for([(f, m) for f in cand for m in ("LR", "GB") if ("B", m, f) in P4 and (f, m) not in P7 and P4[("B", m, f)]["comb"] > P4[("A", m)]["comb_ci"][1]])
R["phase7"] = {f"{k[0]}|{k[1]}": v for k, v in P7.items()}; PT['phase7'] = time.time() - t; PT['phase3'] = P3['seconds']; R['phase_seconds'] = PT
R["total_seconds"] = time.time() - T0

# ---------------- verdicts + report ----------------
def inc(c): return c["comb_ci"][0] <= NOM <= c["comb_ci"][1]
rows = []; verdict = {}
lo = lambda c: c["comb_ci"][0]; hi = lambda c: c["comb_ci"][1]
for f in cand:
    conf = False; unr = P6[f]["flag"]
    for mdl in ("LR", "GB"):
        if ("B", mdl, f) not in P4: continue
        Bc, Ac, Cc = P4[("B", mdl, f)], P4[("A", mdl)], P4[("C", mdl, f)]
        sep = lo(Bc) > hi(Ac); unr |= sep
        if (Bc["comb"] >= 1.5 * Ac["comb"] and sep and lo(Cc) <= hi(Ac) and hi(Cc) >= lo(Ac) and P5[f]["agree"]
                and not P6[f]["flag"] and P7.get((f, mdl), {}).get("monotone", False)): conf = True
    v = "CONFIRMED" if conf else ("UNRESOLVED" if unr else "REJECTED")
    if v == "REJECTED": v += " (causal-" + (", third-null-)" if not P5[f]["agree"] else ")")
    verdict[f] = v
R["verdicts"] = verdict
json.dump(R, open(os.path.join(a.out, f"{a.name}.s{SEED}.json"), "w"), indent=1, default=str)

L = []; w = L.append
p = lambda x, d=3: "nan" if x is None or (isinstance(x, float) and not np.isfinite(x)) else (f"{x:.{d}f}" if isinstance(x, float) else str(x))
w(f"# PIN audit: {a.name} (seed {SEED})\n")
w("## INPUTS\n```")
w(f"PIN path:                 {a.pin}")
w(f"Decoy marker:             Label == -1 (proteins prefixed '{dp}'; label/prefix mismatches: {R['decoy_label_vs_prefix_mismatch']})")
w(f"Entrapment marker:        protein accession prefix '{ep}'" + (f"; rows on '{xp}' proteins without '{ep}' (and decoys derived from them) excluded before competition: class X" if xp else ""))
w(f"Entrapment type:          {a.entrap_type}")
w(f"r (entrapment/target db): {r} (peptide level)")
w(f"Primary score column:     {score}" + (f" (joined by SpecId from {a.mlp})" if a.mlp else ""))
w(f"Spectrum key columns:     ScanNr, ExpMass")
w(f"Scorer-banned features:   {a.banned or 'none known'}")
w("```\n")
w(f"Parquet sha256 {R['parquet_sha256']} ({R['parquet_bytes']/1e6:.0f} MB); raw {R['rows_raw']} rows x {R['cols_raw']} cols; "
  f"rows without score {nan_score}. Boosted model: {GB_NAME}. Logistic: mean-impute + standardize (train fold), L2 logistic regression with sklearn's default objective (C=1) solved by Newton to max|step| < 1e-3 (max {LR_MAXIT} iterations). "
  f"Folds: 5, grouped by I/L bare sequence, seeded group permutation (seed {SEED}). Total runtime {R['total_seconds']/60:.1f} min.\n")
w("## Phase 0\n| class | rows | peptides |\n|---|---|---|")
for k in ("T", "E", "D", "B", "X"):
    w(f"| {k} | {R['rows_by_class'].get(k,0)} | {R['peptides_by_class'].get(k, 'excluded') if k not in ('B', 'X') else 'excluded'} |")
w(f"\nSpectra after (ScanNr, ExpMass) competition: {R['spectra']}. Wall-clock per phase (s): " + ', '.join(f'{k} {v:.1f}' for k, v in PT.items()) + "\n")
w("## Phase 1 (primary score, peptide-level TDC q=(D+1)/(T+E))\n| q | N_T | N_E | N_D | lower FDP [95%] | combined FDP [95%] |\n|---|---|---|---|---|---|")
for c in P1:
    w(f"| {100*c['q']:.1f}% | {c['NT']} | {c['NE']} | {c['ND']} | {100*c['lower']:.3f}% [{100*c['lower_ci'][0]:.3f}, {100*c['lower_ci'][1]:.3f}] | {100*c['comb']:.3f}% [{100*c['comb_ci'][0]:.3f}, {100*c['comb_ci'][1]:.3f}] |")
w(f"\n## Phase 2 (decoy vs entrapment; {len(P2)} features; composition by name regex `{COMP_RE}`)\n| feature | comp | KS | KS p | SMD | AUC E/D | AUC T/D |\n|---|---|---|---|---|---|---|")
for d in P2:
    w(f"| {d['f']} | {'C' if d['comp'] else ''} | {d['KS']:.4f} | {d['KSp']:.1e} | {d['SMD']:.3f} | {d['AUC_ED']:.4f} | {d['AUC_TD']:.4f} |")
w("\n## Phase 3 (boosted decoy vs entrapment, 5-fold grouped)\n| features | n | AUC [95%] | bits/row below chance (SE) | total bits | significant |\n|---|---|---|---|---|---|")
for k in ("all", "minus_composition", "minus_composition_and_top5"):
    d = P3[k]; w(f"| {k} | {d['n_feat']} | {d['AUC']:.4f} [{d['AUC_ci'][0]:.4f}, {d['AUC_ci'][1]:.4f}] | {d['bits_per_row']:.5f} ({d['bits_se']:.5f}) | {d['bits_total']:.1f} | {d['sig']} |")
w(f"\nJoint leak: {P3['joint_leak']}. Carriers: {P3['carriers'] or 'none'}. Permutation importance (AUC drop, minus_composition_and_top5): " +
  ", ".join(f"{c} {mu:.4f}±{sd:.4f}" for c, mu, sd in P3["minus_composition_and_top5"]["perm"][:8]))
w(f"\n## Phase 4 (rescoring T+E vs D, OOF; A = {len(base)} features)\n| cond | model | feature | N_T | N_E | N_D | lower FDP | combined FDP [95%] |\n|---|---|---|---|---|---|---|---|")
for k, c in P4.items():
    w(f"| {k[0]} | {k[1]} | {k[2] if len(k)>2 else '-'} | {c['NT']} | {c['NE']} | {c['ND']} | {100*c['lower']:.3f}% | {fmt(c)} |")
for f in cand:
    if f not in gb_set: w(f"| B/C | GB | {f} | boosted: skipped (time) | | | | |")
w(f"\n## Phase 5 (third null: 50 primary-score quantile bins with D/(T+E) within {100*R['phase5_band']['width']:.0f}% of 1; band N_T {R['phase5_band']['NT']}, N_E {R['phase5_band']['NE']}, N_D {R['phase5_band']['ND']}, {len(bands)} of {len(edges)-1} bins)\n| feature | KS D vs T(band) | p | AUC | KS D vs E(band) | AUC D vs E(band) | agrees with Phase 2 |\n|---|---|---|---|---|---|---|")
for f in cand:
    d = P5[f]; w(f"| {f} | {p(d['KS3'],4)} | {d['p3']:.1e} | {p(d['AUC3'],4)} | {p(d['KS_E_band'],4)} | {p(d['AUC_E_band'],4)} | {d['agree']} |")
w("\n## Phase 6 (Spearman rho with passing peptides on same protein, baseline q<=1%)\n| feature | rho | flag |\n|---|---|---|")
for f in cand: w(f"| {f} | {P6[f]['rho']:.3f} | {P6[f]['flag']} |")
w(f"\n## Phase 7 (LR for candidates with LR B combined FDP above A's upper bound; LR and GB for priority features)\nCondition-A solve wall-clock: LR {TIMES['A_LR']:.1f} s, GB {TIMES['A_GB']:.1f} s.\n\n| feature | combined FDP at 0/25/50/75/100% permuted | monotone |\n|---|---|---|")
for (f, m), d in P7.items(): w(f"| {f} ({m}) | " + " / ".join(f"{100*x:.3f}%" for x in d["steps"]) + f" | {d['monotone']} |")
if not P7: w("| none | | |")
w("\n## Candidates\n| feature | KS | FDP A (LR/GB) | FDP B (LR/GB) | FDP C (LR/GB) | third-null KS | entrapment-blind flag | linear vs boosted inflation (B-A, pp) | dose monotone | peptides lost if dropped (LR/GB) |\n|---|---|---|---|---|---|---|---|---|---|")
for f in cand:
    ks = ks_of(f)
    g = lambda c, m: (100 * P4[(c, m, f)]["comb"]) if (c, m, f) in P4 else None
    aL, aG = 100 * P4[("A", "LR")]["comb"], 100 * P4[("A", "GB")]["comb"]
    bL, bG, cL, cG = g("B", "LR"), g("B", "GB"), g("C", "LR"), g("C", "GB")
    s2 = lambda x: "skip" if x is None else f"{x:.2f}%"
    lostL = P4[("B", "LR", f)]["NT"] - P4[("A", "LR")]["NT"]
    lostG = (P4[("B", "GB", f)]["NT"] - P4[("A", "GB")]["NT"]) if ("B", "GB", f) in P4 else "skip"
    infl = f"{bL-aL:+.2f} / " + ("skip" if bG is None else f"{bG-aG:+.2f}")
    w(f"| {f} | {ks:.4f} | {aL:.2f}% / {aG:.2f}% | {s2(bL)} / {s2(bG)} | {s2(cL)} / {s2(cG)} | {p(P5[f]['KS3'],4)} | {'Y' if P6[f]['flag'] else 'N'} | {infl} | {' / '.join((('y' if P7[(f, m)]['monotone'] else 'n') if (f, m) in P7 else 'n/a') for m in ('LR', 'GB'))} | {lostL} / {lostG} |")
w("\n## Verdicts")
for kind in ("CONFIRMED", "REJECTED", "UNRESOLVED"):
    w(f"- {kind}: " + (", ".join(f"{f}" + (v[len('REJECTED'):] if v.startswith('REJECTED') else '') for f, v in verdict.items() if v.startswith(kind)) or "none"))
# CHARACTERIZATION (generated from the numbers above; at most 200 words)
b1 = P1[2]; cal = b1["comb_ci"][0] <= NOM <= b1["comb_ci"][1]
AL, AG = P4[("A", "LR")], P4[("A", "GB")]
conf = [f for f, v in verdict.items() if v == "CONFIRMED"]; unr = [f for f, v in verdict.items() if v == "UNRESOLVED"]
flag6 = [f for f in unr if P6[f]["flag"]]
C = []
C.append(f"Baseline: combined FDP at nominal 1% is {100*b1['comb']:.2f}% [{100*b1['comb_ci'][0]:.2f}, {100*b1['comb_ci'][1]:.2f}], so the baseline is "
         + ("calibrated (interval includes 1%)." if cal else ("anti-conservative (interval above 1%)." if b1['comb_ci'][0] > NOM else "conservative (interval below 1%).")))
C.append(f"Single features: the largest Phase 2 KS is {P2[0]['KS']:.3f} ({P2[0]['f']}); "
         + (f"CONFIRMED: {', '.join(conf)} (B combined " + ", ".join(f"{max(100*P4[('B', m, f)]['comb'] for m in ('LR', 'GB') if ('B', m, f) in P4):.2f}%" for f in conf) + ")." if conf else "no candidate is CONFIRMED."))
if unr: C.append("UNRESOLVED: " + ", ".join(unr) + (f"; Phase 6 flags {', '.join(flag6)} (|rho| " + ", ".join(f"{abs(P6[f]['rho']):.2f}" for f in flag6) + ")." if flag6 else "."))
if not a.tune:
    j = P3["minus_composition_and_top5"]
    C.append(f"Combinations: the joint decoy-vs-entrapment classifier reaches AUC {P3['all']['AUC']:.3f} on all features and {j['AUC']:.3f} after both removals"
             + (f" (joint signal; carriers {', '.join(P3['carriers'])})." if P3["joint_leak"] else " (below the joint-signal criterion)."))
C.append(f"Learner: condition A gives combined FDP {100*AL['comb']:.2f}% [{100*AL['comb_ci'][0]:.2f}, {100*AL['comb_ci'][1]:.2f}] with logistic regression and "
         f"{100*AG['comb']:.2f}% [{100*AG['comb_ci'][0]:.2f}, {100*AG['comb_ci'][1]:.2f}] with boosting"
         + (", so the boosted learner runs hotter on the same features." if AG['comb'] > AL['comb_ci'][1] else ", so the two learners agree within intervals."))
w("\n## CHARACTERIZATION\n" + " ".join(C))
R["characterization"] = " ".join(C); R["newton_iterations_max"] = max(NEWTON_ITERS) if NEWTON_ITERS else None
json.dump(R, open(os.path.join(a.out, f"{a.name}.s{SEED}.json"), "w"), indent=1, default=str)
open(os.path.join(a.out, f"{a.name}.s{SEED}.md"), "w").write("\n".join(L) + "\n")
log("done", round(R["total_seconds"] / 60, 1), "min", verdict)
