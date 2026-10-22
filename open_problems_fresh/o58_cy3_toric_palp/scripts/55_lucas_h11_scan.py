#!/usr/bin/env python3
"""
O58 script 55 — Q: 36=L₄+L₇ 喺其他 h11 有冇類似 Lucas 分解.
Q: which h11 values are Lucas sums? And do those h11 families exist
in the HF database? Test: h11 ∈ {L_a + L_b} for Lucas L.
Also: which h11 = 2×L (even Lucas double)?
"""
import os, json, math

def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def main():
    print("=== Q: h11 Lucas decompositions ===\n")
    L = {lucas(n): n for n in range(15)}
    print("Lucas L_0..L_14:", [lucas(n) for n in range(15)])
    print()

    # which h11 in plausible range (1..40) are sums of 2 distinct Lucas?
    lucas_vals = sorted(set(lucas(n) for n in range(15)))
    print("h11 values = L_a + L_b (distinct a<b):")
    sums = {}
    for a in range(15):
        for b in range(a+1, 15):
            s = lucas(a) + lucas(b)
            if 1 <= s <= 50:
                sums.setdefault(s, []).append((a, b))
    for s in sorted(sums):
        if s in [36]:
            print(f"  h11={s}: {sums[s]} ← (36,98) TARGET")
        else:
            print(f"  h11={s}: {sums[s]}")
    print()

    # h11 = 2×L (double)
    print("h11 = 2×L (even double):")
    for n in range(15):
        d = 2 * lucas(n)
        if 1 <= d <= 50:
            print(f"  2×L_{n} = {d}")
    print()

    # which of these h11 appear in HF database with h21=98?
    # HF: real h11 = HF h12 (swap). Check h12 column for these values
    import pyarrow.parquet as pq
    HF = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes-4d"
    import os as _os
    files = sorted(f for f in _os.listdir(HF) if f.endswith(".parquet"))
    # target h11 values that are Lucas sums (real h11 = HF h12)
    target_h11 = sorted(s for s in sums if s <= 50)
    counts = {t: 0 for t in target_h11}
    for fn in files:
        f = pq.ParquetFile(_os.path.join(HF, fn))
        for rg in f.iter_batches(columns=["h12"], batch_size=2_000_000):
            arr = rg.column("h12").to_numpy()
            for t in target_h11:
                counts[t] += int((arr == t).sum())
        print(f"  {fn} done", flush=True)
    print()
    print("=== real h11 families (Lucas sums) in HF ===")
    for t in target_h11:
        if counts[t]:
            print(f"  h11={t} (Lucas sum {sums[t]}): {counts[t]:,} polytopes")
    print()
    # h11=36 count for reference
    total36 = 0
    for fn in files:
        f = pq.ParquetFile(_os.path.join(HF, fn))
        for rg in f.iter_batches(columns=["h12"], batch_size=2_000_000):
            arr = rg.column("h12").to_numpy()
            total36 += int((arr == 36).sum())
    print(f"  h11=36 reference: {total36:,}")
    print()
    json.dump({"lucas_sums": {str(k): v for k, v in sums.items()},
               "counts": {str(k): v for k, v in counts.items()}},
              open("lucas_h11_families.json", "w"), indent=2)
    print("Saved data/lucas_h11_families.json")

if __name__ == "__main__":
    main()
