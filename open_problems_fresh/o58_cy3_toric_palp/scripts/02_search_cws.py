#!/usr/bin/env python3
"""
O58 script 02 — Search KS CWS databases (w5.ip.gz, w44.ip.gz) for CWS
whose polytope has Hodge (36,98). BATCH mode: feed ~1000 CWS lines per
poly.x invocation (poly.x -g accepts multiple CWS lines; each produces
an 'H:h21,h11' line). ~1000x faster than per-line subprocess.
"""
import gzip, subprocess, sys, os, re, time, json

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
O53_DATA = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o53_cy3_reality/data"

BATCH = 1000
TARGETS = {(98, 36), (36, 98)}

def main():
    os.chdir(O53_DATA)
    hits = []
    t0 = time.time()
    nlines = 0
    for fname in ["w5.ip.gz", "w44.ip.gz"]:
        print(f"Scanning {fname} ...", flush=True)
        batch = []
        with gzip.open(fname, "rt", errors="replace") as f:
            for ln, line in enumerate(f, 1):
                s = line.strip()
                if not s:
                    continue
                nlines += 1
                batch.append(s)
                if len(batch) >= BATCH:
                    hits += scan_batch(fname, batch, hits_start=ln - len(batch) + 1)
                    batch = []
                    if ln % 20000 == 0:
                        print(f"  ... {ln} lines, {time.time()-t0:.0f}s, {len(hits)} hits", flush=True)
            if batch:
                hits += scan_batch(fname, batch, hits_start=ln - len(batch) + 1)
                batch = []
    print(f"\nDone {nlines} lines in {time.time()-t0:.0f}s. {len(hits)} hits.")
    out = os.path.join(os.path.dirname(__file__), "..", "data", "cws_hits.json")
    with open(out, "w") as f:
        json.dump(hits, f, indent=2)
    print("Saved", out)

def scan_batch(fname, lines, hits_start):
    """Run poly.x -g on a batch; return list of hit dicts."""
    inp = "\n".join(lines) + "\n"
    try:
        r = subprocess.run(["poly.x", "-g"], input=inp.encode(),
                           capture_output=True, timeout=120)
        out = r.stdout.decode(errors="replace")
    except Exception as e:
        print(f"  poly.x error: {e}")
        return []
    # Output: for each CWS line, poly.x prints the CWS echo + 'H:h21,h11 [chi]'
    # We scan sequentially: each 'H:...' belongs to the most recent CWS echo line.
    cur_cws = None
    hits = []
    for ol in out.splitlines():
        s = ol.strip()
        if not s:
            continue
        m = re.match(r"^H:(\d+),(\d+)\s*\[(\d+)\]", s)
        if m:
            h = (int(m.group(1)), int(m.group(2)))
            if h in TARGETS and cur_cws is not None:
                hits.append(dict(file=fname, cws=cur_cws, hodge=list(h)))
                print(f"  HIT: {cur_cws} -> H:{h[0]},{h[1]}", flush=True)
            cur_cws = None
        else:
            # CWS echo line: 'd1 w11 ... d2 w21 ...' or similar
            if re.search(r"\d", s):
                cur_cws = s
    return hits

if __name__ == "__main__":
    main()
