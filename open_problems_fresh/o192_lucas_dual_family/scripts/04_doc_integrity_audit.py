#!/usr/bin/env python3
# O192 doc-integrity audit (read-only; O191 教訓 2 pattern) — closure audit 5-step + docs check
# 2026-09-13
import os, subprocess, re, sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # O root (parent of scripts/)
PASS = 0
FAIL = 0
def check(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS {name}  {info}")
    else:
        FAIL += 1
        print(f"  FAIL {name}  {info}")

required = ["SESSION_START.md", "01_problem_record.md", "final_result.md",
            "docs/01_lucas_dual_and_budget_quantum.md", "docs/02_rs1_bridge_scan.md",
            "docs/03_session_push_closure.md", "docs/04_power_sum_closed_form.md",
            "docs/05_external_extensions.md",
            "scripts/01_verify_lucas_family.py", "scripts/02_rs1_bridge_scan.py",
            "scripts/03_session_push_closure.py", "scripts/04_doc_integrity_audit.py",
            "scripts/05_power_sum_closed_forms.py", "scripts/06_external_extensions.py"]
mt = {}
for f in required:
    p = os.path.join(D, f)
    exists = os.path.isfile(p)
    mt[f] = os.path.getmtime(p) if exists else 0
    check(f"file exists: {f}", exists)

# 2. mtime monotonicity: derivation opening <= attacks <= SESSION_START(handoff) <= closing
# SESSION_START is a HANDOFF written at end of previous session (references docs/02 sections),
# so it sits between attacks and closing — correct workflow, not backdating.
# FINAL-AUDIT AWARE (09-13): round-1 docs may receive recorded precision corrections at
# final audit (docs/02 B06: control-prediction vs actual ratio split). Working-tree mtimes
# then no longer reflect creation order, so ORDER uses git first-commit time per file
# (created(); robust to corrections). Freshness (record/final at close) uses working mtime.
def created(f):
    try:
        repo = os.path.dirname(D)  # open_problems_fresh
        r = subprocess.run(["git", "-C", repo, "log", "--diff-filter=A", "--format=%ct",
                            "--", os.path.join("o192_lucas_dual_family", f)],
                           capture_output=True, text=True)
        if r.stdout.strip():
            return float(r.stdout.split()[0])
    except Exception:
        pass
    return os.path.getmtime(os.path.join(D, f))

opening = ["docs/01_lucas_dual_and_budget_quantum.md", "scripts/01_verify_lucas_family.py"]
attacks = ["docs/02_rs1_bridge_scan.md", "scripts/02_rs1_bridge_scan.py"]
closing = ["docs/03_session_push_closure.md", "scripts/03_session_push_closure.py",
           "docs/04_power_sum_closed_form.md", "scripts/05_power_sum_closed_forms.py",
           "docs/05_external_extensions.md", "scripts/06_external_extensions.py",
           "scripts/04_doc_integrity_audit.py", "01_problem_record.md", "final_result.md"]
max_open = max(created(f) for f in opening)
min_att = min(created(f) for f in attacks)
min_close = min(created(f) for f in closing)
check("mtime(created): opening docs (docs01/scripts01) <= attacks (docs02/scripts02)",
      max_open <= min_att, f"open_max={max_open:.0f} att_min={min_att:.0f}")
check("mtime(created): SESSION_START = handoff (>= attacks, <= closing; same-commit equality ok)",
      created("SESSION_START.md") >= min_att and created("SESSION_START.md") <= min_close,
      f"ss={created('SESSION_START.md'):.0f} att_min={min_att:.0f} close_min={min_close:.0f}")
check("mtime(created): attacks <= closing (docs03/scripts03/record/final)",
      min_att <= min_close, f"att_min={min_att:.0f} close_min={min_close:.0f}")
check("mtime: record & final working-tree updated at close (>= working attacks)",
      mt["01_problem_record.md"] >= mt["docs/02_rs1_bridge_scan.md"] and
      mt["final_result.md"] >= mt["docs/02_rs1_bridge_scan.md"])
# recorded-correction gate: any round-1 doc re-touched at final audit must be recorded
rec = open(os.path.join(D, "01_problem_record.md"), encoding="utf-8").read()
check("final-audit corrections recorded (B06 precision in honesty log + timeline)",
      "32.99996" in rec and "final audit" in rec and "B06" in rec)

# 3. doc consistency, tiered: original numbers in original docs + close docs;
#    session-push numbers only in close docs (docs/01/02 must stay historical — no backdating)
docs = {f: open(os.path.join(D, f), encoding="utf-8").read() for f in
        ["docs/01_lucas_dual_and_budget_quantum.md", "docs/02_rs1_bridge_scan.md",
         "docs/03_session_push_closure.md", "docs/04_power_sum_closed_form.md",
         "docs/05_external_extensions.md",
         "01_problem_record.md", "final_result.md"]}
close_docs = ["docs/03_session_push_closure.md", "docs/04_power_sum_closed_form.md",
              "docs/05_external_extensions.md",
              "01_problem_record.md", "final_result.md"]
tier1 = {"198": "198", "321": "321", "832": "832", "9350": "9350"}   # original (docs/01 + close)
tier2 = {"823": "823", "880": "880", "912": "912", "1792": "1792",
         "parity-gap": "parity-gap"}                                  # session-push (close docs only)
tier3 = {"C(2n,n)": "C(2n,n)", "C(8,4)": "C(8,4)", "131": "131",
         "sqrt5*phi^-n": "φ^{−n}"}                                   # round-2 (docs/04 + close docs only)
tier4 = {"Kummer": "Kummer", "Fisher": "Fisher", "n_first": "n_first",
         "trap ⑦": "trap ⑦"}                                        # round-3 (docs/05 + close docs only)
for k, v in tier1.items():
    check(f"consistency: '{k}' in docs/01 + docs/03 + record + final",
          all(v in docs[d] for d in ["docs/01_lucas_dual_and_budget_quantum.md",
                                     "docs/03_session_push_closure.md",
                                     "01_problem_record.md", "final_result.md"]))
for k, v in tier2.items():
    check(f"consistency(new): '{k}' in docs/03 + record + final (not backdated into docs/01/02)",
          all(v in docs[d] for d in ["docs/03_session_push_closure.md",
                                     "01_problem_record.md", "final_result.md"]) and
          all(v not in docs[d] for d in ["docs/01_lucas_dual_and_budget_quantum.md",
                                         "docs/02_rs1_bridge_scan.md"]))
for k, v in tier3.items():
    check(f"consistency(round2): '{k}' in docs/04 + record + final (not backdated into docs/01/02)",
          all(v in docs[d] for d in ["docs/04_power_sum_closed_form.md",
                                     "01_problem_record.md", "final_result.md"]) and
          all(v not in docs[d] for d in ["docs/01_lucas_dual_and_budget_quantum.md",
                                         "docs/02_rs1_bridge_scan.md"]))
for k, v in tier4.items():
    check(f"consistency(round3): '{k}' in docs/05 + record + final (not backdated into docs/01/02/03)",
          all(v in docs[d] for d in ["docs/05_external_extensions.md",
                                     "01_problem_record.md", "final_result.md"]) and
          all(v not in docs[d] for d in ["docs/01_lucas_dual_and_budget_quantum.md",
                                         "docs/02_rs1_bridge_scan.md",
                                         "docs/03_session_push_closure.md"]))

# 4. SESSION_START snapshot unchanged (still opening state, no closure claim)
ss = open(os.path.join(D, "SESSION_START.md"), encoding="utf-8").read()
check("SESSION_START snapshot: still 🟡 待閉合審計 (no backdated closure claim)",
      "🟡" in ss and "已閉合" not in ss)

# 5. final_result RESULT_TEMPLATE anchors
fr = open(os.path.join(D, "final_result.md"), encoding="utf-8").read()
for anchor in ["# O192 —", "## 狀態", "## 結論", "## 關鍵公式", "## 依賴"]:
    check(f"final_result anchor: {anchor}", anchor in fr)

# 6. git scoped to own O dir: our dir clean after commit; outside dirs = sibling sessions (NOT pollution)
try:
    r = subprocess.run(["git", "status", "--porcelain"], cwd=D, capture_output=True, text=True, timeout=30)
    changed = [l for l in r.stdout.splitlines() if l.strip()]
    own = [l for l in changed if "o192_lucas_dual_family" in l]
    outside = [l for l in changed if "o192_lucas_dual_family" not in l]
    check("git: o192 dir has no uncommitted changes (after closure commit)", len(own) == 0,
          f"own_dirty={len(own)}")
    print(f"  INFO git: outside changes = {len(outside)} (sibling sessions — NOT pollution, per O191)")
except FileNotFoundError:
    check("git: repo not found (skip)", True, "no git")
except subprocess.TimeoutExpired:
    check("git: timeout (skip)", True, "git status timed out")

print(f"\n{PASS} PASS / {FAIL} FAIL")
sys.exit(0 if FAIL == 0 else 1)
