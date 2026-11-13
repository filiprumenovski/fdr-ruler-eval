#!/usr/bin/env python3
"""bake.py SRC_PARQUET PERCOLATOR_DIR OUT : add mlp_score (joined by SpecId = PSMId from percolator.psms.tsv + percolator.decoys.tsv), nothing else changed."""
import sys, duckdb
src, perc, out = sys.argv[1:4]
c = duckdb.connect()
c.execute(f"""CREATE TABLE m AS SELECT PSMId::VARCHAR AS SpecId, score::DOUBLE AS mlp_score FROM read_csv(['{perc}/percolator.psms.tsv','{perc}/percolator.decoys.tsv'], delim=chr(9), header=true)""")
cols = [r[0] for r in c.execute(f"DESCRIBE SELECT * FROM read_parquet('{src}')").fetchall()]
if "mlp_score" in cols: sys.exit("mlp_score already present")
pre = [x for x in cols if x != "Proteins"]
c.execute(f"""COPY (SELECT {', '.join('p."' + x + '"' for x in pre)}, m.mlp_score, p."Proteins" FROM read_parquet('{src}') p LEFT JOIN m USING (SpecId)) TO '{out}' (FORMAT parquet)""")
n, nn = c.execute(f"SELECT count(*), count(*) FILTER (mlp_score IS NULL) FROM read_parquet('{out}')").fetchone()
print("baked", out, n, "rows; rows without mlp_score:", nn)
