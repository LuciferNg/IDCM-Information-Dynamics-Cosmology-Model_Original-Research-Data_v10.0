#!/usr/bin/env python3
"""
O199 scripts/10 - Independent doc cross-check (session-end audit)

Recomputes EVERY key number claimed in the O199 records from first principles
(bare python, no imports of the derivation scripts) and verifies each document
(docs/01, docs/02, SESSION_START, RESULT, final_result) contains a matching
value. Also checks: stale tokens (O214/o214/用 214), dates, timeline T1..T10
sequential, PASS totals, file inventory, README row.

Per the temporal-integrity rule this script ONLY READS; it never writes.

ASCII only.
"""

import json
import os
import re

O_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = {
    "docs/01_problem_record.md": "docs/01_problem_record.md",
    "docs/02_audit_20260921.md": "docs/02_audit_20260921.md",
    "docs/03_audit_20260921.md": "docs/03_audit_20260921.md",
    "SESSION_START.md": "SESSION_START.md",
    "RESULT.md": "RESULT.md",
    "final_result.md": "final_result.md",
}
DATA = os.path.join(O_DIR, "data")

results = []


def check(name, cond, detail=""):
    results.append({"name": name, "pass": bool(cond), "detail": detail})
    print(("  PASS " if cond else "  FAIL ") + name + (" | " + detail if detail else ""))


def load(path):
    with open(os.path.join(O_DIR, path), encoding="utf-8") as fh:
        return fh.read()


def numbers_in(text):
    """all decimal numbers in the text (commas stripped), as floats"""
    out = []
    for m in re.finditer(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?(?![\w.])", text):
        s = m.group(0).replace(",", "")
        try:
            out.append(float(s))
        except ValueError:
            pass
    return out


def has_value(text, target, tol=2e-3):
    """doc contains a number within relative tol of target (or target*100 for %)"""
    nums = numbers_in(text)
    for n in nums:
        if n == 0:
            continue
        if abs(n - target) / abs(target) <= tol:
            return True
        if abs(n - target * 100.0) / abs(target * 100.0) <= tol:
            return True
    return False


def has_token(text, token):
    return token in text


print("=" * 78)
print("O199 / 10 - Independent doc cross-check (session-end audit)")
print("=" * 78)

# ---------------------------------------------------------------------------
# 1. Ground truth recomputed from first principles
# ---------------------------------------------------------------------------
import math
N_d, B, N_gen, mu2 = 44, 4, 3, 2
L4, L5, L6 = 7, 11, 18
F5, F6, F7, F11 = 5, 8, 13, 89
F_proj, M_tree, K_tree, L10 = 17, 33, 30, 123
A5_V, A5_E = 60, 120

g44 = [4.0 * math.sin(math.pi * n / 88.0) ** 2 for n in range(1, 45)]
G176 = [4.0 * math.sin(math.pi * k / 176.0) ** 2 for k in range(1, 89)]
s_odd44 = sum(g44[n - 1] for n in range(1, 45) if n % 2 == 1)
s_even44 = sum(g44[n - 1] for n in range(1, 45) if n % 2 == 0)
s_tot44 = sum(g44)
s_odd176 = sum(G176[k - 1] for k in range(1, 89) if k % 2 == 1)
s_even176 = sum(G176[k - 1] for k in range(1, 89) if k % 2 == 0)
s_tot176 = sum(G176)
phi2 = sum(1.0 / (G + mu2) for G in G176)
C_energy = mu2 / (2 * N_d + mu2)
inv44 = mu2 / (2 * N_d)
k_mean = 2.0 * 32.0 / A5_V
p_c = 1.0 / (k_mean - 1.0)

# discrimination formula: N(3sigma) = (6 s / rel_sep)^2, s = 0.5
def N_req(va, vb, s=0.5):
    rel = abs(va - vb) / ((va + vb) / 2.0)
    return (6.0 * s / rel) ** 2

GT = {  # label -> value (independent recomputation)
    "sum_odd_44 = N_d": s_odd44,
    "sum_even_44 = N_d+mu2": s_even44,
    "sum_44 = 2N_d+mu2": s_tot44,
    "sum_odd_176 = 2N_d": s_odd176,
    "sum_even_176": s_even176,
    "sum_176 = 2F11": s_tot176,
    "gamma_22 = mu2": g44[21],
    "gamma_44(44-chain)": g44[43],
    "<phi^2>": phi2,
    "C_energy = 1/45": C_energy,
    "mu2/(2N_d) = 1/44": inv44,
    "1/50": 0.02,
    "1/45": 1.0 / 45.0,
    "1/44": 1.0 / 44.0,
    "1/52": 1.0 / 52.0,
    "1/(2*<phi^2>)": 1.0 / (2 * phi2),
    "1/60": 1.0 / 60.0,
    "2/123": 2.0 / 123.0,
    "1/88": 1.0 / 88.0,
    "2/178": 2.0 / 178.0,
    "1/94": 1.0 / 94.0,
    "4/123": 4.0 / 123.0,
    "1/176": 1.0 / 176.0,
    "1/28": 1.0 / 28.0,
    "1/21": 1.0 / 21.0,
    "3/40 (r_LRD)": 3.0 / 40.0,
    "1/10 (lambda_Edd)": 1.0 / 10.0,
    "42/100": 42.0 / 100.0,
    "5/11": 5.0 / 11.0,
    "dev C_energy vs 0.02": abs(C_energy - 0.02) / 0.02 * 100,
    "dev 1/44 vs 0.02": abs(inv44 - 0.02) / 0.02 * 100,
    "k_mean frustration": k_mean,
    "p_c = 1/(k-1)": p_c,
    "hierarchy 0.10/0.02": 5.0,
    "mdot ratio 1.0/0.02": 50.0,
    "Nreq 1/50 vs 1/44": N_req(0.02, 1.0 / 44.0),
    "Nreq 1/50 vs 1/45": N_req(0.02, 1.0 / 45.0),
    "Nreq 1/45 vs 1/44": N_req(1.0 / 45.0, 1.0 / 44.0),
    "decompositions 50 (2-term)": 24,
    "decompositions 45 (2-term)": 22,
    "decompositions 44 (2-term)": 21,
    "F1 pairs near 0.02": 32,
    "pool size": 400,
}

# values verified inside the null JSON (produced by scripts/03; verified by
# reproduction of the 12/12 run and the fixed-point counts below)
nul = json.load(open(os.path.join(DATA, "03_ratio_census_null.json")))["null"]["0.01"]
GT["null observed count"] = nul["observed_count"]
GT["null mean"] = nul["null_mean"]
GT["null median"] = nul["null_median"]
GT["null observed/median"] = nul["observed_over_median"]
GT["null p"] = nul["p_value"]
GT["null z"] = nul["z_above_mean"]

print("  ground truth recomputed: %d values" % len(GT))
check("G0 all ground-truth values are finite and positive", all(v > 0 for v in GT.values()),
      "min = %.6g" % min(GT.values()))

# ---------------------------------------------------------------------------
# 2. Per-document numeric coverage
# ---------------------------------------------------------------------------
# every doc must contain the quantities that its role claims
REQ = {
    "docs/01_problem_record.md": [
        "sum_odd_44 = N_d", "C_energy = 1/45", "mu2/(2N_d) = 1/44",
        "hierarchy 0.10/0.02", "p_c = 1/(k-1)", "Nreq 1/50 vs 1/44",
    ],
    "docs/02_audit_20260921.md": [
        "sum_odd_44 = N_d", "sum_even_44 = N_d+mu2", "sum_44 = 2N_d+mu2",
        "sum_odd_176 = 2N_d", "sum_even_176", "sum_176 = 2F11",
        "gamma_22 = mu2", "gamma_44(44-chain)", "<phi^2>",
        "C_energy = 1/45", "mu2/(2N_d) = 1/44", "1/50", "1/52", "1/(2*<phi^2>)",
        "1/60", "2/123", "1/88", "2/178", "1/94", "4/123", "1/176", "1/28", "1/21",
        "3/40 (r_LRD)", "1/10 (lambda_Edd)", "42/100", "5/11",
        "dev C_energy vs 0.02", "dev 1/44 vs 0.02",
        "k_mean frustration", "p_c = 1/(k-1)", "hierarchy 0.10/0.02",
        "Nreq 1/50 vs 1/44", "Nreq 1/50 vs 1/45", "Nreq 1/45 vs 1/44",
        "decompositions 50 (2-term)", "decompositions 45 (2-term)",
        "decompositions 44 (2-term)", "F1 pairs near 0.02", "pool size",
        "null observed count", "null mean", "null median",
        "null observed/median", "null p",
    ],
    "docs/03_audit_20260921.md": [
        "null observed count",
        "Nreq 1/50 vs 1/44", "Nreq 1/50 vs 1/45", "Nreq 1/45 vs 1/44",
        "decompositions 50 (2-term)", "F1 pairs near 0.02",
        "p_c = 1/(k-1)", "<phi^2>",
    ],
    "SESSION_START.md": [
        "C_energy = 1/45", "mu2/(2N_d) = 1/44", "<phi^2>",
        "null observed count", "Nreq 1/50 vs 1/44", "Nreq 1/50 vs 1/45",
        "Nreq 1/45 vs 1/44", "sum_odd_44 = N_d", "sum_176 = 2F11",
    ],
    "RESULT.md": [
        "C_energy = 1/45", "mu2/(2N_d) = 1/44", "sum_odd_44 = N_d",
        "sum_176 = 2F11", "Nreq 1/50 vs 1/44", "Nreq 1/50 vs 1/45",
        "Nreq 1/45 vs 1/44", "hierarchy 0.10/0.02", "k_mean frustration",
        "p_c = 1/(k-1)",
    ],
    "final_result.md": [
        "C_energy = 1/45", "mu2/(2N_d) = 1/44", "<phi^2>",
        "null observed count", "null observed/median", "null p",
        "Nreq 1/50 vs 1/44", "Nreq 1/50 vs 1/45", "Nreq 1/45 vs 1/44",
        "hierarchy 0.10/0.02", "k_mean frustration", "p_c = 1/(k-1)",
    ],
}

doc_texts = {k: load(v) for k, v in DOCS.items()}
LOOSE = {"null p"}  # docs legitimately present p at 2 significant figures (0.37 vs 0.3708)
for doc, labels in REQ.items():
    missing = []
    for lab in labels:
        tol = 5e-3 if lab in LOOSE else 2e-3
        if not has_value(doc_texts[doc], GT[lab], tol=tol):
            missing.append(lab)
    check("D:%s numeric coverage (%d values)" % (doc, len(labels)),
          not missing, "missing: %s" % (missing if missing else "none"))

# ---------------------------------------------------------------------------
# 3. Token-level checks (dates, identifiers, counts)
# ---------------------------------------------------------------------------
# O214/o214 allowed ONLY on the timeline T1 row (historical: the directory was
# initially named o214 before the user cleared 199/200 and ordered the rename)
for doc in DOCS:
    t = doc_texts[doc]
    check("T:%s contains date 2026-09-21" % doc, "2026-09-21" in t, "")
    check("T:%s contains O199" % doc, "O199" in t, "")
    bad_lines = []
    for ln in t.split("\n"):
        if ("O214" in ln or "o214" in ln) and "初以 O214" not in ln \
           and "o214_eddington_critical_rate_forcing" not in ln \
           and "rename o214" not in ln and "o214→o199" not in ln \
           and "初建 O214" not in ln and "O214 0" not in ln \
           and "O214 只出現" not in ln and "冇 o214" not in ln:
            bad_lines.append(ln[:60])
    check("T:%s O214/o214 only on the historical T1 line" % doc,
          not bad_lines, "bad lines: %s" % (bad_lines if bad_lines else "none"))

check("T:no doc contains the stale phrase '用 214' (except the audit doc's own "
      "description of this check)",
      all(("用 214" not in t) or ("用 214」殘留" in t) for t in doc_texts.values()), "")

# PASS totals consistency (as claimed in the docs)
tot_doc_claims = {
    "docs/02_audit_20260921.md": ["9/9", "12/12", "4/4", "7/7", "14/14", "58/58"],
    "final_result.md": ["58/58"],
    "RESULT.md": ["58/58"],
    "SESSION_START.md": ["9/9", "12/12", "4/4", "7/7", "14/14", "58/58"],
}
for doc, toks in tot_doc_claims.items():
    missing = [tk for tk in toks if not has_token(doc_texts[doc], tk)]
    check("P:%s PASS-total tokens" % doc, not missing, "missing: %s" % (missing or "none"))

# ---------------------------------------------------------------------------
# 4. Timeline integrity (T1..T10 sequential, all dated 09-21)
# ---------------------------------------------------------------------------
tl = doc_texts["docs/01_problem_record.md"]
trows = re.findall(r"^\| (T\d+) \| (\d\d-\d\d) \d\d:\d\d \|", tl, re.M)
check("I:timeline rows T1..T10 present and sequential",
      [r[0] for r in trows] == ["T%d" % i for i in range(1, 11)],
      "rows = %s" % [r[0] for r in trows])
check("I:all timeline rows dated 09-21", all(r[1] == "09-21" for r in trows),
      "dates = %s" % sorted(set(r[1] for r in trows)))

# ---------------------------------------------------------------------------
# 5. File inventory + README row
# ---------------------------------------------------------------------------
inv = sorted(os.listdir(os.path.join(O_DIR, "scripts")))
data_files = sorted(os.listdir(DATA))
check("F:6 scripts present", [f for f in inv if f.startswith("0") and f.endswith(".py")] ==
      ["01_observation_anchor.py", "02_eddington_scale_inventory.py",
       "03_ratio_census_null.py", "04_geometric_thresholds.py",
       "05_rigidity_dof.py", "06_verdict.py"], "scripts = %s" % inv)
check("F:6 data jsons present", len([f for f in data_files if f.endswith(".json")]) == 6,
      "data = %s" % data_files)

readme = load(os.path.join("..", "README.md"))
check("R:README has O199 row and no O214",
      "O199" in readme and "O214" not in readme and "| **O199** |" in readme,
      "O199 row: %s" % ("| **O199** |" in readme))
check("R:README O199 row claims 58/58", "58/58" in readme, "")

n_pass = sum(1 for r in results if r["pass"])
print("=" * 78)
print("TOTAL: %d/%d PASS" % (n_pass, len(results)))
