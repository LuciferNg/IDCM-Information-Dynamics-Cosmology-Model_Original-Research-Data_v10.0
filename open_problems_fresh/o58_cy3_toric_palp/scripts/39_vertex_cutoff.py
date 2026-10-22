#!/usr/bin/env python3
"""
O58 script 39 — D: 20+ vertex cutoff analysis.
Q: why no (36,98) with 20+ vertices?
Check: h11=36 family vertex distribution (real h11=36 = HF h12=36 after swap).
Is 20+ vertex common in h11=36 family? Or is the cutoff special to h21=98?
"""
import os, json, subprocess, re, sys
import pyarrow.parquet as pq

HF = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes-4d"

def main():
    files = sorted(f for f in os.listdir(HF) if f.endswith(".parquet"))
    print(f"=== h11=36 family (real = HF h12=36, swap) vertex distribution ===")
    per_vert = {}
    for fn in files:
        # filename: polytopes-4d-NN-vertices.parquet
        nv = int(fn.split("-")[2])
        path = os.path.join(HF, fn)
        f = pq.ParquetFile(path)
        # h12 column (swap: real h11 = HF h12)
        for rg in f.iter_batches(columns=["h12"], batch_size=2_000_000):
            import pyarrow.compute as pc
            arr = rg.column("h12").to_numpy()
            cnt = int((arr == 36).sum())
            if cnt:
                per_vert[nv] = per_vert.get(nv, 0) + cnt
        print(f"  {nv:2d} verts: {per_vert.get(nv, 0):,} (cumulative h11=36)")
    print()
    total = sum(per_vert.values())
    print(f"TOTAL real h11=36: {total:,}")
    print("\nBy vertex count:")
    for nv in sorted(per_vert):
        print(f"  {nv:2d}: {per_vert[nv]:>10,}  ({per_vert[nv]/total*100:.2f}%)")
    # 20+ fraction
    over19 = sum(v for k, v in per_vert.items() if k >= 20)
    print(f"\n20+ vertex: {over19:,} ({over19/total*100:.2f}% of family)")
    # (36,98) 5021 has max vertex 19 — is that rare in family?
    print(f"(36,98) with 20+ verts: 0 (verified earlier)")
    json.dump(dict(per_vert=per_vert, total=total, over19=over19),
              open("h11_36_vertex_dist.json", "w"), indent=2)
    print("\nSaved data/h11_36_vertex_dist.json")

if __name__ == "__main__":
    main()
