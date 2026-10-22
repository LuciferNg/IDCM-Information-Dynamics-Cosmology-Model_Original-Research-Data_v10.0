#!/usr/bin/env python3
"""
O58 script 70 — AC: e-position Lucas tendency — control family.
Q: is the e₁-e₄ Lucas tendency (z=10σ) special to (36,98), or does it
appear in OTHER h11 families (e.g. h11=37, 35, 40)?
Control: sample polytopes from HF with different real h11 (HF h12),
compute e-positions, check Lucas fraction.
"""
import os, json, numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    os.chdir(DATA)
    from cytools import Polytope, config
    config.enable_experimental_features()

    # control families: real h11 = HF h12 (swap!)
    # use HF h12 values 35, 37, 40 → real h11 35, 37, 40
    import pyarrow.parquet as pq
    HF = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes-4d"
    import os as _os
    files = sorted(f for f in _os.listdir(HF) if f.endswith(".parquet"))
    # find a small file with h12=35, 37, 40
    targets = {35: [], 37: [], 40: []}
    for fn in files:
        f = pq.ParquetFile(_os.path.join(HF, fn))
        for rg in f.iter_batches(columns=["h12", "vertices"], batch_size=200_000):
            arr = rg.column("h12").to_numpy()
            verts = rg.column("vertices").to_pylist()
            for h12 in targets:
                if len(targets[h12]) >= 10:
                    continue
                idx = np.where(arr == h12)[0]
                for ix in idx[:10 - len(targets[h12])]:
                    targets[h12].append(verts[ix])
            if all(len(v) >= 10 for v in targets.values()):
                break
        if all(len(v) >= 10 for v in targets.values()):
            break

    L = {lucas(n) for n in range(1, 10)}
    print(f"=== AC: e-position Lucas tendency control ===\n")
    print(f"Lucas set: {sorted(L)}")
    print()

    results = []
    for h12, vlist in targets.items():
        real_h11 = h12  # real h11 = HF h12
        print(f"--- real h11={real_h11} (HF h12={h12}) ---")
        for vi, verts in enumerate(vlist):
            P = Polytope(verts)
            pts = [tuple(int(x) for x in p) for p in P.points()]
            e_pos = [i for i, p in enumerate(pts) if p in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]]
            n_l = sum(1 for i in e_pos if i in L)
            results.append(dict(h11=real_h11, e_pos=e_pos, n_lucas=n_l,
                                frac=n_l/len(e_pos) if e_pos else 0))
            print(f"  sample {vi}: e_pos={e_pos}, Lucas={n_l}/{len(e_pos)}")

    print()
    # aggregate per family
    for h11 in [35, 37, 40]:
        rs = [r for r in results if r["h11"] == h11]
        total_e = sum(len(r["e_pos"]) for r in rs)
        total_l = sum(r["n_lucas"] for r in rs)
        # exclude e₁
        e2 = [(r["e_pos"][i], i) for r in rs for i in range(1, len(r["e_pos"]))]
        te2 = len(e2)
        tl2 = sum(1 for (p, _) in e2 if p in L)
        print(f"h11={h11}: all={total_l}/{total_e} ({total_l/total_e*100:.0f}%), "
              f"excl e₁={tl2}/{te2} ({tl2/te2*100:.0f}%)")

    json.dump(results, open("e_positions_control_families.json", "w"), indent=2)
    print("\nSaved data/e_positions_control_families.json")

if __name__ == "__main__":
    main()
