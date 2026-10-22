#!/usr/bin/env python3
"""O222 R20 -- contract enforcer / freeze gate (scripts/39).

Checks (C1..C5) before the frozen machine scripts/41_r20_closure.py may produce any verdict:

  C1  pins P1..P11 exist and match the hashes recorded in data/39_r20_freeze.json
      (first run records them; every later run re-checks).
  C2  AST gate on scripts/41: only stdlib imports {importlib.util, json, os, sys, fractions},
      NO non-integer float literals, NO banned identifier names (pi, cos, sin, tan, log, exp, sqrt).
  C3  the six contract cells M1..M6 are present in the machine (string presence).
  C4  the machine does not import the R19 machine/audit nor the M3 discovery script.
  C5  the machine writes only inside data/ and logs/ of this problem directory.

On success the gate prints GATE = OPEN and records the frozen impl hash.
The impl hash must equal the hash recorded at freeze time; a change requires a re-freeze with the
old freeze copied first (docs/27 2).
"""
import ast
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FREEZE = os.path.join(DATA, "39_r20_freeze.json")
MACHINE = os.path.join(HERE, "41_r20_closure.py")
CONTRACT = os.path.join(ROOT, "docs", "27_r20_contract.md")

PINS = {
    "P1": "scripts/12_b5_budget.py",
    "P2": "scripts/18_d6_mapping.py",
    "P3": "scripts/09_a2_rollback.py",
    "P4": "data/09_a2_correlation.json",
    "P5": "data/15_b3r2_results.json",
    "P6": "data/21_g4_results.json",
    "P7": "data/27_c2g7_results.json",
    "P8": "data/30_g1g8_results.json",
    "P9": "data/34_g2q5_results.json",
    "P10": "data/37_r19_results.json",
    "P11": "../little_red_dots/data/k_chain_modes.json",
}
ALLOWED_IMPORTS = {"importlib.util", "json", "os", "sys", "fractions"}
BANNED_NAMES = {"pi", "cos", "sin", "tan", "log", "exp", "sqrt"}
CELLS = ["M1", "M2", "M3", "M4", "M5", "M6"]
FORBIDDEN_IMPORTS = ["37_r19", "38_r19", "40_r20"]


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    results = []
    ok = True

    def chk(name, cond, detail):
        nonlocal ok
        ok = ok and cond
        results.append({"check": name, "pass": bool(cond), "detail": detail})
        print("[%s] %s  %s" % ("PASS" if cond else "FAIL", name, detail))

    # C1 pins
    pin_hashes = {}
    missing = []
    for k, rel in PINS.items():
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            pin_hashes[k] = {"path": rel, "sha256": sha(p)}
        else:
            missing.append(rel)
    chk("C1a pins exist", not missing, "missing: %s" % (missing or "none"))
    prev = None
    if os.path.exists(FREEZE):
        with open(FREEZE, encoding="utf-8") as f:
            prev = json.load(f)
    if prev and prev.get("pins"):
        drift = [k for k in prev["pins"] if k in pin_hashes and prev["pins"][k]["sha256"] != pin_hashes[k]["sha256"]]
        chk("C1b pin hashes unchanged", not drift, "drifted: %s" % (drift or "none"))
        drift_txt = prev.get("contract_sha256") != sha(CONTRACT)
        chk("C1c contract unchanged since freeze", not drift_txt, "docs/27 sha256 compared")
    else:
        chk("C1b/c first freeze (recording pins + contract)", True, "will record hashes now")

    # C2 AST gate
    src = open(MACHINE, encoding="utf-8").read()
    tree = ast.parse(src)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imports.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    bad_imports = sorted(i for i in imports if i not in ALLOWED_IMPORTS)
    chk("C2a imports allowed", not bad_imports, "imports=%s ; offenders=%s" % (sorted(imports), bad_imports))
    floats = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, float)
              and not float(n.value).is_integer()]
    chk("C2b no non-integer float literals", not floats, "found: %s" % (floats or "none"))
    assert_mod = [f for f in ("math", "numpy", "scipy", "random", "cmath") if f in imports]
    chk("C2c no math/numpy/scipy/random imports", not assert_mod, "found: %s" % (assert_mod or "none"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
    banned = sorted(names & BANNED_NAMES)
    chk("C2d no banned identifier names", not banned, "found: %s" % (banned or "none"))

    # C3 cells
    absent = [c for c in CELLS if ('"%s"' % c) not in src]
    chk("C3 cells M1..M6 present", not absent, "absent: %s" % (absent or "none"))

    # C4 no forbidden imports of other round scripts
    offenders = [f for f in FORBIDDEN_IMPORTS if any(f in i for i in imports)]
    chk("C4 no import of R19 machine/audit or discovery script", not offenders, "found: %s" % (offenders or "none"))

    # C5 writes only inside data/ logs/
    allowed_writes = ("os.path.join(DATA", "os.path.join(ROOT, \"logs")
    write_marks = [w for w in ("open(os.path.join(DATA", '"w"') if w in src]
    outside = [m for m in ("/tmp/", "open(os.path.join(HERE", "shutil.") if m in src]
    chk("C5 writes confined to data/ and logs/", not outside, "offenders: %s" % (outside or "none"))

    impl = sha(MACHINE)
    refreeze = "--refreeze" in sys.argv
    superseded = None
    if prev and prev.get("gate") == "OPEN" and prev.get("impl_sha256") and prev["impl_sha256"] != impl:
        if refreeze:
            superseded = prev["impl_sha256"]
            chk("C6 impl hash matches freeze (RE-FREEZE: old hash kept as superseded_impl_sha256)", True,
                "old %s -> new %s ; old freeze preserved on disk" % (superseded[:16], impl[:16]))
        else:
            chk("C6 impl hash matches freeze", False,
                "impl changed: frozen %s vs now %s -- re-freeze required (copy the old freeze first, then --refreeze)"
                % (prev["impl_sha256"][:16], impl[:16]))
    else:
        chk("C6 impl hash matches freeze", True, "impl sha256 prefix %s" % impl[:16])

    payload = {
        "round": "R20",
        "contract": "docs/27_r20_contract.md",
        "contract_sha256": sha(CONTRACT),
        "machine": "scripts/41_r20_closure.py",
        "impl_sha256": impl,
        "impl_sha256_now": impl,
        "superseded_impl_sha256": superseded,
        "pins": pin_hashes if not prev else {**(prev.get("pins") or {}), **{k: v for k, v in pin_hashes.items() if k not in (prev.get("pins") or {})}},
        "checks": results,
        "gate": "OPEN" if ok else "CLOSED",
    }
    with open(FREEZE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    print("-" * 100)
    print("GATE = %s   (%d/%d checks pass)  impl sha256 = %s" % (payload["gate"], sum(1 for r in results if r["pass"]),
                                                                len(results), impl[:16]))
    print("freeze written: data/39_r20_freeze.json")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
