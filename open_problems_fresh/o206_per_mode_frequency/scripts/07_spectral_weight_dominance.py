#!/usr/bin/env python3
"""
O206 — Script 07: |Δm| 主導項分解 + 相消結構
=========================================================
承接 docs/08 §六 之下一輪提案 (主導項分解)。

★ 提案前提被證偽 (誠實記錄):
   原假設 |Δm_n| ≈ 單一 (n,m*) 項 ⟹ 形狀降級為最近鄰 γ 間隙律
   實測: 主導項【確實】係最近鄰 m* = n±1 (88/88 模), 但【帶號和】大幅相消
        ⟹ |Δm_n| ≪ |c_{n,n±1}| (低 n 相消 70–95%)
        ⟹ 形狀唔係「單項支配」, 而係【相消結構】(cancellation law)

本 script:
  §A 貢獻分解 c_m = V_nm²/(γ_n−γ_m) + 主導項結構
  §B ★ 相消律 κ_n = |Δm_n| / |c_{n,n±1}|
  §C 單項 / 最近鄰對 / 截斷和 之近似殘餘 + 形狀 RMS
  §D 最近鄰 |γ 間隙| 律 (修正 C7 符號 bug)
  §E 裁決
紀律: O136 權威慣例; 對數度量; 零新常數; numpy int64 → int 才可 JSON
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, LM, E_ring44, V_position,
                      logscore, sum_V2_dE)

OUT = Path(__file__).parent.parent / "data"
OUT.mkdir(exist_ok=True)
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


V = V_position()
E = E_ring44()
base = logscore(sum_V2_dE(E, V))

print("=" * 100)
print("O206 Script 07: |Δm| 主導項分解 + 相消結構")
print("=" * 100)
print(f"\n  基準 |Δm| (E = ring44) 對數度量 RMS = {base:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 貢獻分解 c_m = V_nm²/(γ_n−γ_m) + 主導項\n{'─'*100}")


def contribs(n):
    idx = [m for m in range(NC) if m != n - 1 and (m - (n - 1)) % 2 == 1]
    dE = E[n - 1] - E[idx]
    aV2 = np.abs(V[n - 1, idx]) ** 2
    return np.array(idx), aV2 / dE


rows = []
for n in range(1, NC + 1):
    idx, c = contribs(n)
    s = float(c.sum())
    absc = np.abs(c)
    tot = float(absc.sum())
    j = int(np.argmax(absc))
    m_star = int(idx[j]) + 1
    # 最近鄰對 (m = n−1 與 n+1) 之貢獻和
    nn = [k for k, m in enumerate(idx) if abs(int(m) + 1 - n) == 1]
    pair_sum = float(c[nn].sum()) if nn else float("nan")
    # 截斷和: 按 |c| 排序取前 k 項之帶號和
    order = np.argsort(-absc)
    cum = {}
    for k in (1, 2, 3, 5, 10):
        cum[k] = float(c[order[:k]].sum())
    rows.append({"n": n, "s": s, "abs_s": abs(s), "m_star": m_star,
                 "c_star": float(c[j]), "dom_frac": float(absc[j] / tot),
                 "top3_frac": float(absc[order[:3]].sum() / tot),
                 "pair_sum": pair_sum, "cum": cum,
                 "kappa": abs(s) / abs(float(c[j])),
                 "pair_frac": abs(s / pair_sum) if pair_sum else float("nan")})

print(f"\n  {'n':>3} {'|Δm_n|':>13} {'m*':>4} {'|c_m*|':>13} {'|c*|/Σ|c|':>10} {'κ=|Δm|/|c*|':>12}")
print("  " + "-" * 62)
for r in rows[:10] + [rows[i - 1] for i in A5_MODES]:
    print(f"  {r['n']:>3} {r['abs_s']:>13.6f} {r['m_star']:>4} {abs(r['c_star']):>13.6f} "
          f"{r['dom_frac']:>10.4f} {r['kappa']:>12.6f}")

near = sum(1 for r in rows if abs(r["m_star"] - r["n"]) == 1)
chk("C1 [結構] 主導項全部係最近鄰 m* = n±1", near == NC, f"{near}/{NC} 模")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B ★ 相消律 κ_n = |Δm_n| / |c_(n,n±1)|\n{'─'*100}")
kappa_a5 = [rows[n - 1]["kappa"] for n in A5_MODES]
pairf_a5 = [rows[n - 1]["pair_frac"] for n in A5_MODES]
print(f"\n  {'n':>3} {'κ_n':>10} {'|Δm|/|最近鄰對和|':>20}")
print("  " + "-" * 36)
for n, k, pf in zip(A5_MODES, kappa_a5, pairf_a5):
    print(f"  {n:>3} {k:>10.6f} {pf:>20.6f}")
chk("C2 [相消律] 低 n 模強制相消: κ_n < 0.5 對 n ≥ 2",
    all(rows[n - 1]["kappa"] < 0.5 for n in A5_MODES if n >= 2),
    f"κ(2) = {rows[1]['kappa']:.4f}, κ(13) = {rows[12]['kappa']:.4f}")
chk("C3 [相消律] 單項近似【唔】成立 (A₅ 9 模最大相對偏差 > 5%)",
    max(abs(abs(rows[n - 1]["c_star"]) - rows[n - 1]["abs_s"]) / rows[n - 1]["abs_s"] for n in A5_MODES) > 0.05,
    f"max 偏差 = {max(abs(abs(rows[n-1]['c_star'])-rows[n-1]['abs_s'])/rows[n-1]['abs_s'] for n in A5_MODES):.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 近似殘餘 + 形狀 RMS (單項 / 最近鄰對 / 截斷和)\n{'─'*100}")
exact = sum_V2_dE(E, V)
variants = {
    "單項 (|c_m*|)": np.array([abs(rows[n - 1]["c_star"]) for n in A5_MODES]),
    "最近鄰對 (|Σ_{n±1}|)": np.array([abs(rows[n - 1]["pair_sum"]) for n in A5_MODES]),
    "top-2 截斷和": np.array([abs(rows[n - 1]["cum"][2]) for n in A5_MODES]),
    "top-3 截斷和": np.array([abs(rows[n - 1]["cum"][3]) for n in A5_MODES]),
    "top-5 截斷和": np.array([abs(rows[n - 1]["cum"][5]) for n in A5_MODES]),
    "top-10 截斷和": np.array([abs(rows[n - 1]["cum"][10]) for n in A5_MODES]),
}
print(f"\n  {'變體':>22} {'逐模最大相對偏差':>18} {'形狀 RMS':>10}")
print("  " + "-" * 54)
res = {}
for name, v in variants.items():
    rel = float(np.max(np.abs(v - exact) / np.abs(exact)))
    s = logscore(v)
    res[name] = {"max_rel_dev": rel, "rms": s}
    print(f"  {name:>22} {rel:>18.6f} {s:>10.4f}")
print(f"\n  {'精確 |Δm|':>22} {'-':>18} {base:>10.4f}")
chk("C4 ★ [近似] 最近鄰「對」(兩項, 零參數) 已達 < 5% 逐模偏差 ⟹ |Δm| 有兩項閉式",
    res["最近鄰對 (|Σ_{n±1}|)"]["max_rel_dev"] < 0.05,
    f"max rel dev = {res['最近鄰對 (|Σ_{n±1}|)']['max_rel_dev']:.6f}")
chk("C5 [近似] 快速收斂: top-5 < 1% 且 top-10 < 0.1%",
    res["top-5 截斷和"]["max_rel_dev"] < 0.01 and res["top-10 截斷和"]["max_rel_dev"] < 1e-3,
    f"top-5 = {res['top-5 截斷和']['max_rel_dev']:.6f}, top-10 = {res['top-10 截斷和']['max_rel_dev']:.6f}")
chk("C6 [近似] 截斷和之形狀 RMS 全部 ≥ 精確基準 ⟹ 近似唔改善形狀 (缺口唔喺 |Δm| 之計算)",
    all(v["rms"] >= base - 1e-9 for v in res.values()),
    f"最佳 = {min(v['rms'] for v in res.values()):.4f} vs {base:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 最近鄰 |γ 間隙| 律 (⚠️ 修正初版符號 bug: γ_n 非單調)\n{'─'*100}")
gap_p = np.array([abs(E[n - 1] - E[n]) if n < NC else np.nan for n in range(1, NC + 1)])
gap_m = np.array([abs(E[n - 1] - E[n - 2]) if n > 1 else np.nan for n in range(1, NC + 1)])
gap_min = np.fmin(gap_p, gap_m)
print(f"\n  {'n':>3} {'γ_n':>12} {'|Δγ| 最近鄰':>13} {'|Δm_n|':>13} {'|Δm|·|Δγ|':>12}")
print("  " + "-" * 60)
for n in A5_MODES:
    print(f"  {n:>3} {E[n-1]:>12.8f} {gap_min[n-1]:>13.8f} {rows[n-1]['abs_s']:>13.6f} "
          f"{rows[n-1]['abs_s']*gap_min[n-1]:>12.6f}")
prod = np.array([rows[n - 1]["abs_s"] * gap_min[n - 1] for n in A5_MODES])
span = float(prod.max() / prod.min())
print(f"\n  |Δm|·|Δγ|_min 範圍 = [{prod.min():.6f}, {prod.max():.6f}] (跨度 {span:.2f}×)")
chk("C7 [間隙律] |Δm_n|·|Δγ|_min 唔係常數 (跨度 > 2×) ⟹ 純 1/|Δγ| 律唔成立",
    span > 2.0, f"跨度 = {span:.2f}×")

# κ_n 是否對得上結構函數? (後驗診斷, 只作線索)
ks = np.array([rows[n - 1]["kappa"] for n in range(1, NC + 1)])
cands = {
    "γ_n": E.copy(),
    "√γ_n": np.sqrt(E),
    "1/γ_n": 1.0 / E,
    "n": np.arange(1, NC + 1, dtype=float),
    "1/n": 1.0 / np.arange(1, NC + 1, dtype=float),
    "Δγ_n(n) 最近鄰": gap_min,
    "γ_n/Δγ_n": E / gap_min,
    "sin²θ_n": np.array([math.sin(math.pi * n / 88) ** 2 for n in range(1, NC + 1)]),
}
print(f"\n  κ_n 對照結構函數 (後驗診斷, 只作線索):")
for name, c in cands.items():
    m = np.isfinite(c) & np.isfinite(ks)
    r = float(np.corrcoef(ks[m], c[m])[0, 1])
    print(f"    {name:>16}: corr = {r:+.4f}")

# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
pair_dev = res["最近鄰對 (|Σ_{n±1}|)"]["max_rel_dev"]
t5_dev = res["top-5 截斷和"]["max_rel_dev"]
t10_dev = res["top-10 截斷和"]["max_rel_dev"]
best_rms = min(v["rms"] for v in res.values())
print(f"\n{'─'*100}\n§E 裁決 (script 07)\n{'─'*100}")
print(f"""
  ① 主導項【結構】確認: m* = n±1 (最近鄰) — {near}/{NC} 模 (零參數, 純結構) ✅
  ② ★ 零參數兩項閉式成立:
       |Δm_n| ≈ |V²_(n,n−1)/(γ_n−γ_(n−1)) + V²_(n,n+1)/(γ_n−γ_(n+1))|
     逐模最大相對偏差 = {pair_dev:.6f};  top-5 = {t5_dev:.6f};  top-10 = {t10_dev:.6f} (快速收斂)
  ③ 相消係【兩項之間】: κ_n = |Δm_n|/|c_(n,n±1)| 由 {max(kappa_a5):.3f} (n=1) 降到 {min(kappa_a5):.3f} (n=13)
     ⟹ 單項近似唔成立, 但【最近鄰對】近似成立 (兩項相消)
  ④ |Δm_n|·|Δγ|_min 唔係常數 (跨度 {span:.2f}×) ⟹ 純最近鄰間隙律唔成立 (需 V² 之比)
  ⑤ ★ 關鍵: 兩項閉式極準, 但形狀 RMS 唔改善 ({best_rms:.4f} vs {base:.4f})
     ⟹ 1.80× 殘餘【唔喺 |Δm| 之計算】, 而喺 ln m ↔ ln|Δm| 映射 (α/M₀ 層)
  ⟹ 下一輪目標: (a) V²_(n,n+1)/V²_(n,n−1) 之結構身份;  (b) 形狀缺口之真正位置 (映射層)
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "07_spectral_weight_dominance.json", "w") as f:
    json.dump({
        "baseline_rms": base,
        "mstar_is_nearest": int(near),
        "kappa_A5": {str(n): float(rows[n - 1]["kappa"]) for n in A5_MODES},
        "pair_frac_A5": {str(n): float(rows[n - 1]["pair_frac"]) for n in A5_MODES},
        "variants": {k: {"max_rel_dev": float(v["max_rel_dev"]), "rms": float(v["rms"])}
                     for k, v in res.items()},
        "gap_law_product_span": span,
        "per_mode": [{"n": int(r["n"]), "abs_s": float(r["abs_s"]), "m_star": int(r["m_star"]),
                      "dom_frac": float(r["dom_frac"]), "kappa": float(r["kappa"])} for r in rows],
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/07_spectral_weight_dominance.json")
