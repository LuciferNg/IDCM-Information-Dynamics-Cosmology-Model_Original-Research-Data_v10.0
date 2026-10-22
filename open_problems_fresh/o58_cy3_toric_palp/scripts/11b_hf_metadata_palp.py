#!/usr/bin/env python3
"""
O58 script 11b — HF metadata audit via PALP (fast).
For sampled rows, write vertices to a temp .poly and run poly.x -g
to get Hodge numbers. PALP is ~100x faster than CYTools h21 computation.
"""
import pyarrow.parquet as pq
import random, os, json, subprocess, re, sys, tempfile

HF = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data/polytopes-4d"
N_SAMPLE = 15

def palp_hodge(verts):
    """Run poly.x -g on a vertex list, return (h11, h21) or None."""
    txt = f"{len(verts)} 4\n" + "\n".join(" ".join(str(x) for x in v) for v in verts) + "\n"
    try:
        r = subprocess.run(["poly.x", "-g"], input=txt.encode(),
                           capture_output=True, timeout=30)
        out = r.stdout.decode(errors="replace")
        m = re.search(r"H:(\d+),(\d+)\s*\[(\d+)\]", out)
        if m:
            return int(m.group(1)), int(m.group(2))  # h21, h11 (PALP order)
    except Exception:
        pass
    return None

def main():
    files = ["polytopes-4d-08-vertices.parquet",
             "polytopes-4d-12-vertices.parquet",
             "polytopes-4d-20-vertices.parquet"]
    rng = random.Random(42)
    results = []
    for fn in files:
        path = os.path.join(HF, fn)
        f = pq.ParquetFile(path)
        nrg = f.metadata.num_row_groups
        print(f"=== {fn} ===", flush=True)
        ok = h11_err = h12_err = 0
        details = []
        # sample rows spread across row groups
        for _ in range(N_SAMPLE):
            rg = rng.randrange(nrg)
            t = f.read_row_group(rg, columns=['vertices','h11','h12','vertex_count'])
            arr = t.to_pylist()
            if not arr:
                continue
            r = arr[rng.randrange(len(arr))]
            verts = r['vertices']
            meta = (r['h11'], r['h12'])
            h = palp_hodge(verts)
            if h is None:
                details.append(dict(meta=list(meta), err="palp failed"))
                continue
            real = (h[1], h[0])  # convert to (h11, h21)
            ok += 1
            e11 = real[0] != meta[0]
            e12 = real[1] != meta[1]
            h11_err += e11
            h12_err += e12
            details.append(dict(nv=r['vertex_count'], meta=list(meta), real=list(real),
                                e11=e11, e12=e12))
        print(f"  valid={ok}, h11 err={h11_err}/{ok}, h12 err={h12_err}/{ok}")
        for d in details[:8]:
            if 'real' in d:
                print(f"    nv={d['nv']} meta=({d['meta'][0]},{d['meta'][1]}) real=({d['real'][0]},{d['real'][1]}) {'❌' if d['e11'] or d['e12'] else '✅'}")
            else:
                print(f"    {d}")
        results.append(dict(file=fn, n=ok, err_h11=h11_err, err_h12=h12_err))
    out = os.path.join(os.path.dirname(__file__), "..", "data", "hf_metadata_audit.json")
    json.dump(results, open(out, "w"), indent=2)
    print(f"\nSaved {out}")

if __name__ == "__main__":
    main()
