#!/usr/bin/env python3
"""
O58 script 42 — I: h21=98 ↔ vertex ≤19 restriction.
Q: is the 20+ vertex cutoff special to (36,98), or does it apply to
other high-h21 families? Test: h21=96, 97, 99, 100 families' vertex max.
Use HF metadata (swap: real h21 = HF h11).
"""
import os, json
import pyarrow.parquet as pq

HF = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes-4d"

def main():
    files = sorted(f for f in os.listdir(HF) if f.endswith(".parquet"))
    # target families: real h21 ∈ {96, 97, 98, 99, 100, 94, 90} → HF h11 = those values
    targets = [96, 97, 98, 99, 100, 94, 90, 102]
    per = {t: {} for t in targets}  # t -> {nvert: count}
    for fn in files:
        nv = int(fn.split("-")[2])
        path = os.path.join(HF, fn)
        f = pq.ParquetFile(path)
        for rg in f.iter_batches(columns=["h11"], batch_size=2_000_000):
            arr = rg.column("h11").to_numpy()
            for t in targets:
                cnt = int((arr == t).sum())
                if cnt:
                    per[t][nv] = per[t].get(nv, 0) + cnt
        print(f"  {nv:2d} verts done", flush=True)
    print()
    print("=== h21 family vertex distributions (real h21 = HF h11) ===")
    for t in targets:
        if not per[t]:
            print(f"  h21={t}: EMPTY")
            continue
        mx = max(per[t].keys())
        tot = sum(per[t].values())
        over19 = sum(v for k, v in per[t].items() if k >= 20)
        # peak
        pk = max(per[t], key=per[t].get)
        print(f"  h21={t}: total={tot:,}, max_vert={mx}, 20+={over19:,} ({over19/tot*100:.1f}%), peak_vert={pk}")
    json.dump(per, open("h21_family_vertex_dist.json", "w"), indent=2)
    print("\nSaved data/h21_family_vertex_dist.json")

if __name__ == "__main__":
    main()
