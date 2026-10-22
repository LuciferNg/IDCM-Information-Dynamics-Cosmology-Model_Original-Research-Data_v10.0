#!/usr/bin/env python3
"""
O219 scripts/02 -- Propagation scan: who depends on 'pt index = mode index'?
==========================================================================
Mechanically scans every .md/.py file under open_problems_fresh for lines that
either ASSERT the premise or USE a polytope point label as a mode index.

Buckets (mechanical, then adjudicated by hand in docs/04):
  A   = asserts the pt->mode identity (load-bearing claim)
  B'  = a pt/label number appears in the same line as mode/selection language
        (candidate user: needs an eyeball)
  B   = index-space only (kappa / divisor labels / polytope plumbing):
        no pt->mode claim, so it does NOT depend on the premise

Output: stdout + ../data/02_scan.json
Run: /usr/bin/python3 scripts/02_propagation_scan.py
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
O219 = os.path.dirname(HERE)
REPO = os.path.dirname(O219)
OUT = os.path.join(O219, "data", "02_scan.json")

SELF = "o219_pt_mode_index_premise"

P_A = [
    r"pt\s*index\s*=\s*mode\s*index",
    r"pt\s*index\s*==\s*mode\s*index",
    r"point\s*index\s*=\s*mode\s*index",
    r"pt\s*<\s*-?>?\s*mode",
    r"pt11\s*.*mode\s*11",
    r"pt33\s*.*mode\s*33",
    r"索引\s*=\s*mode",
    r"pt\s*=\s*mode",
]
P_B = [
    r"pt\s*\[\s*\d+\s*\]",
    r"pt\d{1,2}\b",
    r"point\s*#?\d{1,2}\b",
    r"Δ\*?\s*pt",
    r"phi\[(\d+)\]",
]
KW_MODE = r"mode|模式|selection|選擇|9\s*模式|α_s|coupling|gamma_|γ_"
KW_IDX = r"index|索引|label|標籤|divisor|κ|kappa"


def bucket(text):
    for p in P_A:
        if re.search(p, text):
            return "A"
    b_hit = any(re.search(p, text) for p in P_B)
    if b_hit and re.search(KW_MODE, text):
        return "B'"
    if re.search(KW_IDX, text):
        return "B"
    return None


def main():
    hits = {"A": [], "B'": [], "B": []}
    filecount = 0
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
        for fn in files:
            if not fn.endswith((".md", ".py")):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, REPO)
            if SELF in rel:
                continue
            filecount += 1
            try:
                lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
            except Exception:
                continue
            for i, line in enumerate(lines, 1):
                b = bucket(line)
                if b:
                    hits[b].append({"file": rel, "line": i, "text": line.strip()[:300]})
    print("scanned %d files" % filecount)
    for b in ("A", "B'", "B"):
        print("\n== bucket %s : %d hits ==" % (b, len(hits[b])))
        if b == "A":
            for h in hits[b]:
                print("  %s:%d  %s" % (h["file"], h["line"], h["text"]))
        else:
            byfile = {}
            for h in hits[b]:
                byfile.setdefault(h["file"], []).append(h)
            for f, hs in sorted(byfile.items(), key=lambda kv: -len(kv[1])):
                print("  %-70s %d hit(s)  e.g. L%d: %s"
                      % (f, len(hs), hs[0]["line"], hs[0]["text"][:110]))
    def stage2():
        """Blast radius of the *criteria* that sit on the premise: which files use
        (i) the phi-criterion as a selection rule, (ii) the 2-adic/Lucas criterion,
        (iii) the kappa/divisor index space, (iv) the Delta* data files."""
        S = {
            "S1_phi_criterion_as_selection": r"phi\s*==\s*9|phi_le12|phi\s*<=\s*12|φ\s*=\s*9|φ\s*≤\s*12|sub_glsm_44",
            "S2_2adic_lucas_criterion": r"2-adic|2adic|2\s*進|Lucas|v_?2\s*\(",
            "S3_kappa_or_divisor_index_space": r"intersection_full|kappa_36|divisor_basis|"
                                               r"prime_toric_divisors|K\[0,\s*0,\s*0\]|κ\[0",
            "S4_delta_star_data_consumers": r"dual_polytope_points|gkz_phi|dual_triangulation_data|"
                                           r"gkz_period_data",
        }
        res = {}
        for key, pat in S.items():
            rx = re.compile(pat)
            files = {}
            for root, dirs, fnames in os.walk(REPO):
                dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
                for fn in fnames:
                    if not fn.endswith((".md", ".py")):
                        continue
                    path = os.path.join(root, fn)
                    rel = os.path.relpath(path, REPO)
                    if SELF in rel:
                        continue
                    try:
                        txt = open(path, encoding="utf-8", errors="replace").read()
                    except Exception:
                        continue
                    n = len(rx.findall(txt))
                    if n:
                        files[rel] = n
            res[key] = dict(sorted(files.items(), key=lambda kv: -kv[1]))
            print("\n== %s : %d files ==" % (key, len(files)))
            for f, n in list(res[key].items())[:25]:
                print("  %-72s %d" % (f, n))
            # which O-projects are touched
            projs = sorted({f.split("/")[0] for f in files})
            print("  projects touched (%d): %s" % (len(projs), ", ".join(projs[:20])))
        return res


    s2 = stage2()

    json.dump({"scanned_files": filecount, "hits": hits, "stage2": s2},
              open(OUT, "w"), indent=1, ensure_ascii=False)
    print("\nwrote data/02_scan.json  (A=%d B'=%d B=%d)"
          % (len(hits["A"]), len(hits["B'"]), len(hits["B"])))


main()
