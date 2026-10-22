#!/usr/bin/env python3
"""
O58 script 19 — COMPLETE island statistics with HF swap correction.
HF metadata h11/h12 are SWAPPED: real (h11,h21) = (HF_h12, HF_h11).
Question: within real h11=36 family (across ALL vertex-count files),
how many have h21=98? Is (36,98) an island?
Also: real (36,98) count per vertex file.
"""
import pyarrow.parquet as pq
import os, time, json

HF = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes-4d"

def main():
    files = [f for f in sorted(os.listdir(HF)) if f.endswith(".parquet")]
    results = []
    t0 = time.time()
    for fn in files:
        path = os.path.join(HF, fn)
        f = pq.ParquetFile(path)
        fam36 = 0      # real h11=36 (HF h12=36)
        real3698 = 0   # real (36,98) (HF h11=98 & h12=36)
        h21_vals = {}
        small = f.metadata.num_rows < 2e6
        for rg in range(f.metadata.num_row_groups):
            t = f.read_row_group(rg, columns=['h11','h12'])
            df = t.to_pandas()
            m36 = df['h12'] == 36
            fam36 += int(m36.sum())
            real3698 += int(((df['h11']==98) & m36).sum())
            # collect h21 distribution within family (only for small files)
            if small:
                sub = df[m36]
                vc = sub['h11'].value_counts().to_dict()
                for k, v in vc.items():
                    h21_vals[int(k)] = h21_vals.get(int(k), 0) + int(v)
            del df
        results.append(dict(file=fn, rows=f.metadata.num_rows,
                            fam36=int(fam36), real3698=int(real3698),
                            h21_dist=h21_vals))
        print(f"{fn}: rows={f.metadata.num_rows}, real h11=36={fam36}, real (36,98)={real3698}",
              flush=True)
    total_fam = sum(r['fam36'] for r in results)
    total_98 = sum(r['real3698'] for r in results)
    print(f"\nTOTAL: real h11=36 family = {total_fam}, real (36,98) = {total_98}")
    # h21 distribution across small files
    all_h21 = {}
    for r in results:
        for k, v in r['h21_dist'].items():
            all_h21[k] = all_h21.get(k, 0) + v
    print("\nh21 distribution within real h11=36 (small files):")
    for k in sorted(all_h21):
        print(f"  h21={k}: {all_h21[k]}")
    # island check: neighbors of 98
    for nb in [96, 97, 98, 99, 100, 101]:
        print(f"  h21={nb}: {all_h21.get(nb, 0)}")
    json.dump(dict(total_fam=total_fam, total_98=total_98,
                   per_file=results, h21_dist=all_h21),
              open(os.path.join(os.path.dirname(__file__), "..", "data", "island_stats_swap_corrected.json"), "w"),
              indent=2)
    print(f"\nDone in {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
