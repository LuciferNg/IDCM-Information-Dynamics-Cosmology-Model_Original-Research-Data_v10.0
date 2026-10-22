#!/usr/bin/env python3
"""
O58 script 01 — PALP identification of all (36,98) polytopes.
Reads all_36_98.poly (PALP format with 'nv dim' headers), runs poly.x -g
on each, collects Hodge data, dedupes by normal form (poly.x -N), and
reports the canonical 6-vertex instance structure in detail.
"""
import subprocess, sys, os, re, json, collections

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def run_palp(args, inp):
    r = subprocess.run(["poly.x"] + args, input=inp.encode(),
                       capture_output=True, timeout=120)
    return r.stdout.decode(errors="replace"), r.stderr.decode(errors="replace")

def parse_poly_file(path):
    """Parse PALP .poly: entries are consecutive blocks starting with 'n d' header.
    There are NO blank lines between entries — split on header lines."""
    txt = open(path).read()
    lines = txt.splitlines()
    # find header-line indices: lines whose first two tokens are ints and which
    # are followed by at least one coordinate line
    polies = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        parts = s.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            n, d = int(parts[0]), int(parts[1])
            coords = []
            ok = True
            j = i + 1
            for _ in range(n):
                if j >= len(lines):
                    ok = False
                    break
                cp = lines[j].split()
                if len(cp) != d:
                    ok = False
                    break
                try:
                    coords.append([int(x) for x in cp])
                except ValueError:
                    ok = False
                    break
                j += 1
            if ok:
                polies.append((n, d, coords))
                i = j
                continue
        i += 1
    return polies

def poly_to_text(n, d, coords):
    lines = [f"{n} {d}"] + [" ".join(str(x) for x in c) for c in coords]
    return "\n".join(lines) + "\n"

def main():
    os.chdir(DATA)
    allf = "all_36_98.poly"
    polies = parse_poly_file(allf)
    print(f"Parsed {len(polies)} polytope entries from {allf}")
    if not polies:
        print("NO entries parsed — check format")
        sys.exit(1)

    hodges = collections.Counter()
    instances = []
    for idx, (n, d, coords) in enumerate(polies):
        out, err = run_palp(["-g"], poly_to_text(n, d, coords))
        m = re.search(r"M:(\d+)\s+(\d+)\s+N:(\d+)\s+(\d+)\s+H:(\d+),(\d+)\s*\[(\d+)\]", out)
        if m:
            mp, mv, np_, nv, h21, h11, chi = map(int, m.groups())
            hodges[(h21, h11)] += 1
            instances.append(dict(idx=idx, nv=n, nd=d, M_pts=mp, M_verts=mv,
                                  N_pts=np_, N_verts=nv, h21=h21, h11=h11, chi=chi))
        else:
            instances.append(dict(idx=idx, nv=n, nd=d, err=out.strip()[:120]))

    print("\n=== Hodge distribution ===")
    for k, v in hodges.items():
        print(f"  H: {k}  count={v}")
    others = [i for i in instances if (i.get("h21"), i.get("h11")) != (98, 36)]
    print(f"  non-(98,36): {len(others)}")

    # Vertex-count distribution
    vdist = collections.Counter(i["nv"] for i in instances if "h21" in i)
    print("\n=== Vertex count distribution (M-side) ===")
    for k in sorted(vdist):
        print(f"  {k} vertices: {vdist[k]}")

    # Normal-form dedup for the first N instances (PALP -N per entry)
    print("\n=== Normal form dedup (first 40 instances) ===")
    nf_map = {}
    for i in instances[:40]:
        if "h21" not in i:
            continue
        out, err = run_palp(["-N"], poly_to_text(i["nv"], i["nd"], polies[i["idx"]][2]))
        # normal form = sorted rows; PALP prints them after the header line
        lines = [l for l in out.splitlines() if l.strip() and not l.startswith("Degrees")]
        # find the block of integer rows
        rows = []
        for l in lines:
            parts = l.split()
            if len(parts) >= 4:
                try:
                    rows.append(tuple(int(x) for x in parts[:4]))
                except ValueError:
                    pass
        key = tuple(sorted(rows))
        nf_map.setdefault(key, []).append(i["idx"])
    print(f"  {len(nf_map)} distinct normal forms among first 40 instances")
    for k, v in sorted(nf_map.items(), key=lambda kv: len(kv[1]), reverse=True):
        print(f"    {len(v)} instances: indices {v[:6]}{'...' if len(v)>6 else ''}")

    # Canonical 6-vertex instance detail
    print("\n=== Canonical instance (all_36_98.poly first entry) detail ===")
    n, d, coords = polies[0]
    print(f"  vertices n={n}, dim={d}")
    out, err = run_palp(["-gS"], poly_to_text(n, d, coords))
    print(out[:800])

    # The old polytope_36_98.txt (bare 6 vertices, no header)
    print("\n=== polytope_36_98.txt (bare vertex list, add 6 4 header) ===")
    bare = open("polytope_36_98.txt").read()
    # strip comments
    bare_lines = [l for l in bare.splitlines() if l.strip() and not l.strip().startswith("#")]
    vlist = [l for l in bare_lines if all(x.lstrip("-").isdigit() for x in l.split())]
    hdr = f"{len(vlist)} 4\n"
    out, err = run_palp(["-gS"], hdr + "\n".join(vlist) + "\n")
    print(out[:800])
    if err:
        print("ERR:", err[:300])

    with open(os.path.join(os.path.dirname(__file__), "..", "data", "palp_identify_summary.json"), "w") as f:
        json.dump(dict(hodge_dist={f"{k[0]},{k[1]}": v for k, v in hodges.items()},
                       vertex_dist=dict(vdist),
                       first_instance=instances[0] if instances else None,
                       nf_count=len(nf_map)), f, indent=2)
    print("\nSaved data/palp_identify_summary.json")

if __name__ == "__main__":
    main()
