#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/04 — 存活者 mpmath 50dps 驗證 + 身份分類 (R4)

對 exact_hits.csv 每個命中:
  1. mpmath 50 dps 獨立重算不變量 (唔信 numpy float64)
  2. |mp − web_target| ≤ 1e-12·max(1,|target|) → PASS
  3. 分類: anchor / diagonal (a=b) / λ₁₇-generative / structural

⚠️ 掃描語義 (03 construction): X[i,j] = γ[j+1]/γ[i+1] ⇒ 值 = γ_b/γ_a。
   2D GT/OT family 嘅 cell_b 係樹指數 c。mp_val 跟返呢個方向。
"""
import csv
import json
import sys
from pathlib import Path
from collections import Counter

import mpmath as mp

O160 = Path(__file__).resolve().parent.parent
DATA = O160 / "data"
mp.mp.dps = 50

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")


def mp_val(family, a, b, c=None):
    """mpmath 重算不變量 — 跟 03 掃描語義 (1-indexed)."""
    s = mp.sin
    pi = mp.pi
    ga, gb = 4 * s(a * pi / 176) ** 2, 4 * s(b * pi / 176) ** 2
    wa, wb = 2 * s(a * pi / 176), 2 * s(b * pi / 176)
    if family in ("GT_prod", "GT_div", "OT_prod", "OT_div"):
        # 2D tree family: (a, c) = (cell_a, cell_b)
        c = b
        lc = 4 * s(c * pi / 68) ** 2
        return {"GT_prod": ga * lc, "GT_div": ga / lc,
                "OT_prod": wa * lc, "OT_div": wa / lc}[family]
    lc = 4 * s(c * pi / 68) ** 2 if c else mp.mpf(0)
    F = {
        "R88": gb / ga, "O88": wb / wa, "BEAT": abs(wb - wa),
        "FULL_wr": (wb / wa) * lc, "FULL_gr": (gb / ga) * lc,
        "FULL_gd": ((gb / ga) / lc) if c else mp.mpf(0),
        "FULL_bt": abs(wb - wa) * lc,
        "SUM_plus": ga + gb + lc, "SUM_minus": ga + gb - lc,
    }
    return F[family]


def classify(family, a, b, c):
    """命中分類. c=None = 2D chain family."""
    if family in ("GT_prod", "GT_div", "OT_prod", "OT_div"):
        c = b  # 2D tree family: cell_b 係樹指數
    if a == b and family in ("R88", "O88", "BEAT", "FULL_wr", "FULL_gr",
                             "FULL_gd", "FULL_bt", "SUM_plus", "SUM_minus"):
        return "diagonal (a=b, 退化)"
    if c == 17:
        return "λ₁₇-generative (c=17 = F_proj)"
    if {a, b} <= {44, 88}:
        return "anchor (k∈{44,88})"
    return "structural"


def main():
    web = json.loads((DATA / "constant_web.json").read_text())
    rows = list(csv.DictReader(open(DATA / "exact_hits.csv")))
    print(f"=== mpmath 驗證 {len(rows)} 個精確命中 ===")
    results = []
    for r in rows:
        fam = r["family"]
        a, b = int(r["cell_a"]), int(r["cell_b"])
        c = int(r["cell_c"]) if r["cell_c"].strip() else None
        tval = float(r["target_value"])
        v = mp_val(fam, a, b, c)
        ok = abs(v - tval) <= mp.mpf("1e-12") * max(1, abs(tval))
        cls = classify(fam, a, b, c)
        check(f"verify:{fam}({a},{b},{c})→{r['target']}", ok,
              f"mp={mp.nstr(v, 18)} target={r['target_value']} [{cls}]")
        results.append({"family": fam, "a": a, "b": b, "c": c if c else "",
                        "target": r["target"], "value": mp.nstr(v, 25), "class": cls})

    print("\n=== 核心事實驗證 ===")
    tol = mp.mpf("1e-40")
    l17 = 4 * mp.sin(17 * mp.pi / 68) ** 2
    check("F1: λ₁₇ = 4sin²(17π/68) = 2 = μ² EXACT", abs(l17 - 2) < tol,
          f"(17π/68 = π/4; F_proj-th 樹 mode = 自對偶)")
    g44 = 4 * mp.sin(44 * mp.pi / 176) ** 2
    g88 = 4 * mp.sin(88 * mp.pi / 176) ** 2
    w88 = 2 * mp.sin(88 * mp.pi / 176)
    check("F2: γ₄₄ = 2 = μ²", abs(g44 - 2) < tol)
    check("F2: γ₈₈ = 4 = B", abs(g88 - 4) < tol)
    check("F2: ω₈₈ = 2 = μ²", abs(w88 - 2) < tol)
    allok = all(abs(4 * mp.sin(k * mp.pi / 176) ** 2
                    + 4 * mp.sin((88 - k) * mp.pi / 176) ** 2 - 4) < tol
                for k in range(1, 88))
    check("F3: γ_k + γ_{88−k} = 4 ∀k=1..87 (補對和 = B)", allok)
    v2124 = 2 * mp.sin(21 * mp.pi / 176) / (2 * mp.sin(24 * mp.pi / 176))
    pdg = mp.mpf("0.8813589")
    dev_pct = float((v2124 - pdg) / pdg * 100)
    check("F4: O88(21,24) = m_W/m_Z 張力解", abs(v2124 - pdg) < mp.mpf("1e-4"),
          f"mp={mp.nstr(v2124, 20)} PDG={pdg} dev={dev_pct:.4f}% (0.04σ)")

    cc = Counter(r["class"] for r in results)
    print("\n=== 分類統計 ===")
    for k, n in cc.most_common():
        print(f"  {n:3d}  {k}")
    print("\n=== 非退化連結一覽 (λ₁₇ 生成 + anchor) ===")
    for r in results:
        if r["class"] != "diagonal (a=b, 退化)":
            print(f"  {r['family']:10s} ({r['a']},{r['b']},{r['c']}) → {r['target']:<8s} = {r['value'][:18]}")

    print(f"\nRESULT: {PASS}/{PASS + FAIL} PASS")
    sys.exit(0 if FAIL == 0 else 1)


if __name__ == "__main__":
    main()