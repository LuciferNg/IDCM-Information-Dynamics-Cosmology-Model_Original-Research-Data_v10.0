#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/06 — 最終連結清單 (R6, deliverable)

組裝完整 inventory: 所有連結 (link)、本徵值 (eigenvalue)、意思 (meaning)。
來源:
  - exact_hits.csv (mpmath 驗證 19/19) → 🟢 閉合連結 (web 語義)
  - obs_hits.csv + null verdict → m_W/m_Z O88(21,24) 🟢 唯一;
    其他 obs ⚠️ 密度背景 (唔宣稱)
  - novel_candidates.csv (deduped) → 🔮 新數字 (λ₁₇ 生成家族)
輸出:
  - data/link_inventory.csv (machine-readable)
  - data/link_inventory.md   (docs/03 用)
"""
import csv
import json
import sys
from pathlib import Path
from collections import Counter

O160 = Path(__file__).resolve().parent.parent
DATA = O160 / "data"

# 不變量族 → 代數形式
FORMS = {
    "R88": "γ_a/γ_b", "O88": "ω_a/ω_b", "BEAT": "|ω_a−ω_b|",
    "GT_prod": "γ_a·λ_c", "GT_div": "γ_a/λ_c",
    "OT_prod": "ω_a·λ_c", "OT_div": "ω_a/λ_c",
    "FULL_wr": "(ω_a/ω_b)·λ_c", "FULL_gr": "(γ_a/γ_b)·λ_c",
    "FULL_gd": "(γ_a/γ_b)/λ_c", "FULL_bt": "|ω_a−ω_b|·λ_c",
    "SUM_plus": "γ_a+γ_b+λ_c", "SUM_minus": "γ_a+γ_b−λ_c",
}
# 譜定義
DEFS = {
    "γ_k": "4sin²(kπ/176)", "ω_k": "2sin(kπ/176)", "λ_c": "4sin²(cπ/68)",
}


def main():
    web = json.loads((DATA / "constant_web.json").read_text())
    webmap = {}
    for e in web["integers"] + web["halfints"] + web["rationals"]:
        webmap[e["value"]] = (e["name"], e["meaning"], e["source"],
                              e.get("frac", ""))

    # 1) 精確命中
    rows = []
    for r in csv.DictReader(open(DATA / "exact_hits.csv")):
        fam = r["family"]
        a, b = int(r["cell_a"]), int(r["cell_b"])
        c = int(r["cell_c"]) if r["cell_c"].strip() else None
        tval = float(r["target_value"])
        name, meaning, src, frac = webmap.get(tval, (r["target"], "", "", ""))
        idx = f"({a},{b})" if c is None else f"({a},{b},{c})"
        form = FORMS[fam]
        if fam in ("GT_prod", "GT_div", "OT_prod", "OT_div"):
            form = form.replace("λ_c", "λ_b").replace("c", "b")
        rows.append({
            "type": "web-link", "family": fam, "indices": idx,
            "form": form, "value": f"{tval:.12g}",
            "name": name, "meaning": meaning, "source": src,
            "verdict": "🟢 閉合連結", "count": r["count"],
        })

    # 2) obs 命中 — null verdict 分級
    obs_rows = list(csv.DictReader(open(DATA / "obs_hits.csv")))
    OBS_STRUCTURAL = {("m_W/m_Z", "O88")}  # 唯一 + 已知 (21,24) 結構連結
    for r in obs_rows:
        t, fam = r["target"], r["family"]
        a, b = int(r["cell_a"]), int(r["cell_b"])
        c = int(r["cell_c"]) if r["cell_c"].strip() else None
        idx = f"({a},{b})" if c is None else f"({a},{b},{c})"
        verdict = "🟢 唯一結構連結 (已知 O158 張力解)" if (t, fam) in OBS_STRUCTURAL else "⚠️ 密度背景 (3σ 窗內近 miss, 唔宣稱)"
        rows.append({
            "type": "obs-link", "family": fam, "indices": idx,
            "form": FORMS[fam], "value": f"{float(r['value']):.10g}",
            "name": t, "meaning": f"觀測目標, dev {float(r['rel_dev']):.1e}",
            "source": "PDG/NuFIT", "verdict": verdict, "count": r["count"],
        })

    # 3) novel — deduped 非平凡
    novel = list(csv.DictReader(open(DATA / "novel_candidates.csv")))
    seen = {}
    for n in novel:
        key = (n["family"], round(float(n["value"]), 10))
        if key not in seen:
            seen[key] = n
    for n in seen.values():
        if float(n["value"]) in (0.0,):
            continue
        fam = n["family"]
        a, b = int(n["cell_a"]), int(n["cell_b"])
        c = int(n["cell_c"]) if n["cell_c"].strip() else None
        idx = f"({a},{b})" if c is None else f"({a},{b},{c})"
        rows.append({
            "type": "novel", "family": fam, "indices": idx,
            "form": FORMS[fam], "value": n["as"],
            "name": "🔮 新數字", "meaning": f"唔喺 constant web ({n['type']})",
            "source": "O160 掃描", "verdict": "🔮 待解釋 (λ₁₇ 生成家族)",
            "count": "1",
        })

    # CSV
    cols = ["type", "family", "indices", "form", "value", "name", "meaning", "source", "verdict", "count"]
    with open(DATA / "link_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["type"], r["family"])):
            w.writerow(r)

    # MD (docs/03 內容)
    md = ["# O160 連結清單 (Link Inventory)", "",
          "譜定義: γ_k = 4sin²(kπ/176), ω_k = 2sin(kπ/176), λ_c = 4sin²(cπ/68) "
          "(88-site 對偶鏈 × K_Tree Dirichlet-33)。", ""]
    for label, typ in [("🟢 Web 閉合連結", "web-link"),
                       ("🟢/⚠️ 觀測連結", "obs-link"),
                       ("🔮 新數字 (待解釋)", "novel")]:
        sub = [r for r in rows if r["type"] == typ]
        md.append(f"## {label} ({len(sub)})")
        md.append("")
        md.append("| family | 格 (a,b,c) | 代數形式 | 值 | 名稱 | 意思 | 來源 | 判決 |")
        md.append("|:-------|:-----------|:---------|:---|:-----|:-----|:-----|:-----|")
        for r in sub:
            md.append(f"| {r['family']} | {r['indices']} | {r['form']} | {r['value']} | "
                      f"{r['name']} | {r['meaning']} | {r['source']} | {r['verdict']} |")
        md.append("")
    (DATA / "link_inventory.md").write_text("\n".join(md), encoding="utf-8")

    # 摘要
    cc = Counter(r["type"] for r in rows)
    vv = Counter(r["verdict"] for r in rows)
    print("=== 連結清單摘要 ===")
    for k, n in cc.items():
        print(f"  {k:10s} {n}")
    print("--- verdict 分佈 ---")
    for k, n in vv.most_common():
        print(f"  {n:4d}  {k}")
    print(f"\nRESULT: link inventory -> data/link_inventory.csv + .md ({len(rows)} rows)")


if __name__ == "__main__":
    main()
