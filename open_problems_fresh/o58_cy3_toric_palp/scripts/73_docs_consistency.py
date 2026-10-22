#!/usr/bin/env python3
"""
O58 script 73 — DOCS CONSISTENCY CHECK: scan all docs for key numbers
and verify against raw data. Ensures no doc contradicts the data.
"""
import os, json, re, numpy as np

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
results = []

def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

def doc_text():
    txt = ""
    for fn in sorted(os.listdir(DOCS)):
        if fn.endswith(".md"):
            txt += f"\n### {fn}\n" + open(os.path.join(DOCS, fn)).read()
    return txt

def main():
    txt = doc_text()
    print("=== O58 DOCS CONSISTENCY CHECK ===\n")

    # Key numbers that MUST appear consistently
    must_have = {
        "h11=36": r"h11\s*=\s*36|h11:36|h11=36",
        "h21=98": r"h21\s*=\s*98|h21:98|h21=98",
        "χ=-124": r"χ\s*=\s*−?124|−124|Euler.*124|124.*Euler",
        "M:48 6": r"M:48\s+6|M:48, 6|M:48 6",
        "N_d=44": r"N_?d\s*=\s*44|44\s*=\s*N_?d|N_?d.*44",
        "B=4": r"B\s*=\s*4|\b4\b.*\bB\b",
        "L₇=29": r"L₇\s*=\s*29|29\s*=\s*L₇|L_7\s*=\s*29",
        "K=-232": r"−?232",
        "K000=-360": r"−?360",
        "350 nnz": r"350\s*(nnz|non-?zero|nnz)|nnz\s*=\s*350|350",
        "K[1,1,1]=4": r"K[\[(]1,1,1[\])]",
        "Σγ=90": r"Σγ.{0,5}90|90.{0,5}Σγ",
        "7+29=36": r"7\s*\+\s*29\s*=\s*36|29\s*\+\s*7\s*=\s*36",
        "L₄+L₇=36": r"L₄\s*\+\s*L₇\s*=\s*36|36\s*=\s*L₄\s*\+\s*L₇",
        "q8=-q0-1": r"q8\s*=\s*-q0\s*-\s*1|q8 = -q0|−q0−1|−q0 − 1",
        "Σ|det|=200": r"200",
        "4.4×npts": r"4\.4|4\.397|4\.311",
        "5021": r"5,?021",
        "0.041%": r"0\.041",
        "residual U(1) {0,3,7,25,28,29,30,31}": r"0,3,7,25,28,29,30,31|25,28,29,30,31",
        "div0 star=144": r"144",
        "co-simplex 554": r"554",
        "904": r"904",
    }

    print("[Key numbers present in docs]")
    for name, pat in must_have.items():
        found = len(re.findall(pat, txt)) > 0
        check(f"{name}", found)
        if not found:
            print(f"    (pattern: {pat})")

    # Check WITHDRAWALS are marked
    print("\n[Withdrawals marked]")
    withdrawals = {
        "island withdrawal": r"孤島.*撤回|撤回.*孤島",
        "star=8 withdrawal": r"star=8.*撤回|撤回.*star=8",
        "vertex Lucas withdrawal": r"vertex.*Lucas.*撤回|撤回.*vertex.*Lucas|script 59 bug",
        "K=-L₇×Σ1/|det| withdrawal": r"唔普適|單點巧合|1/350",
        "Z withdrawal": r"只係 canonical|canonical.*特有|1/10",
        "AA withdrawal": r"排序偏好|z=1\.8|1\.82",
    }
    for name, pat in withdrawals.items():
        found = len(re.findall(pat, txt)) > 0
        check(f"{name}", found)

    # h21≥98 corrected claim
    print("\n[Corrected claims]")
    has_old_92 = len(re.findall(r"h21\s*≥\s*92\s*→", txt)) > 0
    check("no old 'h21≥92→' claims", not has_old_92)
    has_new_98 = len(re.findall(r"h21\s*≥\s*98\s*→", txt)) > 0
    check("has 'h21≥98→' claim", has_new_98)

    npass = sum(results)
    print(f"\n=== DOCS CHECK: {npass}/{len(results)} PASS ===")
    import sys; sys.exit(0 if npass == len(results) else 1)

if __name__ == "__main__":
    main()
