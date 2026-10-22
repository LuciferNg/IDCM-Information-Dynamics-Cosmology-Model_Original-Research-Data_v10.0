#!/usr/bin/env python3
"""
O58 script 11 — SYSTEMATIC HF metadata error rate measurement.
Samples rows from polytopes-4d parquet files (various vertex counts),
recomputes Hodge with CYTools, compares against parquet metadata.
Reports: per-file error rate, h11 error rate, h12 error rate,
and whether h11/h12 columns are swapped (the suspected systematic issue).
"""
import pyarrow.parquet as pq
import pyarrow as pa
import numpy as np, random, sys, os, json

HF = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes-4d"
N_SAMPLE = 10  # per file (CYTools Polytope construction is ~2-5s each)

def main():
    files = ["polytopes-4d-08-vertices.parquet",
             "polytopes-4d-12-vertices.parquet",
             "polytopes-4d-16-vertices.parquet",
             "polytopes-4d-20-vertices.parquet"]
    all_results = []
    for fn in files:
        path = os.path.join(HF, fn)
        print(f"\n=== {fn} ===", flush=True)
        f = pq.ParquetFile(path)
        total = f.metadata.num_rows
        # sample rows from a few row groups
        rng = random.Random(42)
        nrg = f.metadata.num_row_groups
        rows_todo = []
        for _ in range(N_SAMPLE):
            rg = rng.randrange(nrg)
            row = rng.randrange(f.metadata.row_group(rg).num_rows)
            rows_todo.append((rg, row))
        # read those rows
        from cytools import Polytope
        ok = err_h11 = err_h12 = 0
        details = []
        for rg, row in rows_todo:
            t = f.read_row_group(rg, columns=['vertices','h11','h12','vertex_count','point_count'])
            arr = t.to_pylist()
            if row >= len(arr):
                continue
            r = arr[row]
            verts = r['vertices']
            meta_h11, meta_h12 = r['h11'], r['h12']
            try:
                P = Polytope(verts)
                real_h11, real_h21 = P.h11(), P.h21()
                ok += 1
                e11 = real_h11 != meta_h11
                e12 = real_h21 != meta_h12
                err_h11 += e11
                err_h12 += e12
                details.append(dict(rg=rg, row=row, n_vert=r['vertex_count'],
                                    meta=[meta_h11, meta_h12], real=[real_h11, real_h21],
                                    e11=e11, e12=e12))
            except Exception as e:
                details.append(dict(rg=rg, row=row, err=str(e)[:60]))
        print(f"  sampled {ok} valid, h11 error {err_h11}/{ok} ({err_h11/ok*100:.0f}%), "
              f"h12 error {err_h12}/{ok} ({err_h12/ok*100:.0f}%)")
        # show a few examples
        for d in details[:6]:
            if 'real' in d:
                print(f"    nv={d['n_vert']} meta=({d['meta'][0]},{d['meta'][1]}) real=({d['real'][0]},{d['real'][1]}) {'❌' if d['e11'] or d['e12'] else '✅'}")
        all_results.append(dict(file=fn, n=ok, err_h11=err_h11, err_h12=err_h12))
    with open(os.path.join(os.path.dirname(__file__), "..", "data", "hf_metadata_audit.json"), "w") as fout:
        json.dump(all_results, fout, indent=2)
    print("\nSaved data/hf_metadata_audit.json")

if __name__ == "__main__":
    main()
