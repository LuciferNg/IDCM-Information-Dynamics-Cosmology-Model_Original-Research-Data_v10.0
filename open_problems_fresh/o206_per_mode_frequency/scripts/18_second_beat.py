#!/usr/bin/env python3
"""
O206 — Script 18: 「第二拍頻」假設 (調律者 2026-09-21)
=========================================================
調律者假設 (逐字): 「如果怎樣都找不到因子，是否就是說還有另一個拍頻在影響質量比」

框架: IDCM = K_chain ⊗ K_tree; 質量映射目前只用 K_chain 之 |Δm| (單鏈近似)。
K_tree 譜 (O155 R3): λ_k = 4sin²(kπ/68), k = 1..33, Σλ = 66 = 2K_tree; 68 = 2F₉。
假設: 質量比受【第二拍頻】影響 — 映射應係 (|Δm|, λ_k) 雙變量。

檢驗:
  §A 雙拍頻回歸: ln m = b0 + α·ln|Δm| + β·(拍頻量), k(n) 映射候選 × 4 形式
  §B 殘餘 vs 拍頻量 (固定 OLS α 後)
  §C AIC / 自由度成本
  §D 裁決

⚠️ 盲測紀律: 形式全數凍結先跑; 任何命中都必須過 AIC + 隨機 null。
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import A5_MODES, E_ring44, V_position, sum_V2_dE

OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


modes = np.array([1, 2, 3, 4, 5, 7, 9, 11, 13])
parts = ['t', 'b', 'τ', 'c', 'μ', 's', 'd', 'u', 'e']
masses = np.array([172690, 4180, 1776.86, 1270, 105.6584, 93.4, 4.67, 2.16, 0.511])
V = V_position()
E = E_ring44()
dm = sum_V2_dE(E, V)
ldm = np.array([math.log(dm[A5_MODES.index(n)]) for n in modes])
lm = np.array([math.log(m) for m in masses])
gam = np.array([E[n - 1] for n in modes])
om = np.sqrt(gam)  # K_chain 頻率 √γ_n = 2sin(nπ/88)

# K_tree 譜 (O155 R3): λ_k = 4sin²(kπ/68), k=1..33
lam = np.array([4 * math.sin(k * math.pi / 68) ** 2 for k in range(1, 34)])
omt = np.sqrt(lam)  # K_tree 頻率


def ols(X, y):
    A = np.column_stack([np.ones(len(y))] + [X[:, i] for i in range(X.shape[1])]) if X.ndim == 2 else np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ b
    return b, r


def rms(r):
    return float(np.sqrt(np.mean(r ** 2)))


print("=" * 100)
print("O206 Script 18: 「第二拍頻」假設")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 雙拍頻回歸 (k(n) 映射 × 4 形式)\n{'─'*100}")
# k(n) 映射候選 (全部凍結)
k_map = {
    "k=n": modes,
    "k=34−n": 34 - modes,
    "k=33−n": 33 - modes,
    "k=68−n(截斷)": np.minimum(68 - modes, 33),
}
# 拍頻量形式 (全部凍結)
forms = {
    "ln|γ_n−λ_k|": lambda g, l: np.log(np.abs(g - l) + 1e-300),
    "ln|ω_n−ω_k|": lambda g, l: np.log(np.abs(np.sqrt(g) - np.sqrt(l)) + 1e-300),
    "ln(γ_n/λ_k)": lambda g, l: np.log(g / l),
    "ln|γ_n+λ_k|": lambda g, l: np.log(g + l),
}
b_base, r_base = ols(ldm, lm)
rms_base = rms(r_base)
print(f"  基準 (單鏈, k=2): α = {b_base[1]:.6f}, RMS = {rms_base:.4f}")
print(f"\n  {'映射':>14} {'形式':>18} {'β':>10} {'β/σ':>8} {'RMS':>9} {'改善':>8} {'ΔAIC':>8}")
print("  " + "-" * 80)
results = {}
for kname, karr in k_map.items():
    lk = np.array([math.log(lam[int(k) - 1]) for k in karr])
    for fname, fn in forms.items():
        X = np.column_stack([ldm, fn(gam, np.array([lam[int(k) - 1] for k in karr]))])
        b, r = ols(X, lm)
        rr = rms(r)
        # β 顯著性
        n = len(lm)
        s2 = np.sum(r ** 2) / (n - 3)
        A_ = np.column_stack([np.ones(n), X])
        XtX_inv = np.linalg.inv(A_.T @ A_)
        se_b = math.sqrt(s2 * XtX_inv[2, 2])
        z = b[2] / se_b if se_b > 0 else np.nan
        aic0 = n * math.log(rms_base ** 2) + 2 * 2
        aic1 = n * math.log(rr ** 2) + 2 * 3
        key = f"{kname}|{fname}"
        results[key] = {"beta": float(b[2]), "z": float(z) if z == z else None,
                        "rms": rr, "dAIC": aic0 - aic1}
        print(f"  {kname:>14} {fname:>18} {b[2]:>10.5f} {z:>8.2f} {rr:>9.4f} "
              f"{rms_base/rr:>7.3f}× {aic0-aic1:>+8.3f}")
best = min(results.items(), key=lambda kv: kv[1]["rms"])
chk("C1 雙拍頻回歸無閉合 (最佳改善 < 1.5×)",
    rms_base / best[1]["rms"] < 1.5,
    f"最佳 {best[0]}: RMS {best[1]['rms']:.4f}, 改善 {rms_base/best[1]['rms']:.3f}×")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 殘餘 vs 拍頻量 (固定 OLS α 後) — 相關檢驗\n{'─'*100}")
rng = np.random.default_rng(20260921)
print(f"  {'拍頻量':>22} {'Pearson r':>11} {'perm p':>9}")
print("  " + "-" * 46)
corrs = {}
for kname, karr in k_map.items():
    for fname, fn in forms.items():
        vals = fn(gam, np.array([lam[int(k) - 1] for k in karr]))
        if vals.std() < 1e-15:
            continue
        r = float(np.corrcoef(vals, r_base)[0, 1])
        null = np.array([abs(np.corrcoef(vals, rng.permutation(r_base))[0, 1])
                         for _ in range(4000)])
        p = float((null >= abs(r)).mean())
        corrs[f"{kname}|{fname}"] = {"r": r, "p": p}
        print(f"  {kname+'|'+fname:>22} {r:>+11.4f} {p:>9.4f}")
best_c = min(corrs.items(), key=lambda kv: kv[1]["p"])
chk("C2 殘餘 vs 拍頻量唔顯著 (最佳 p > 0.05)",
    best_c[1]["p"] > 0.05, f"最佳 {best_c[0]}: r = {best_c[1]['r']:+.4f}, p = {best_c[1]['p']:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C AIC / 自由度\n{'─'*100}")
print(f"  基準 AIC (k=2) = {9*math.log(rms_base**2)+4:.3f}")
for k, v in sorted(results.items(), key=lambda kv: kv[1]["dAIC"], reverse=True)[:3]:
    print(f"  最佳 3: {k}: ΔAIC = {v['dAIC']:+.3f}")
chk("C3 加拍頻參數唔值 (最佳 ΔAIC < 2)",
    max(v["dAIC"] for v in results.values()) < 2.0,
    f"最佳 ΔAIC = {max(v['dAIC'] for v in results.values()):+.3f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 裁決\n{'─'*100}")
print(f"""
  §A: 16 個雙拍頻回歸 (4 映射 × 4 形式): 最佳改善 {rms_base/best[1]['rms']:.3f}×
      {best[0]}: RMS {best[1]['rms']:.4f} (基準 {rms_base:.4f})
  §B: 殘餘 vs 拍頻量相關: 最佳 {best_c[0]}: r = {best_c[1]['r']:+.4f}, p = {best_c[1]['p']:.4f}
  §C: 最佳 ΔAIC = {max(v['dAIC'] for v in results.values()):+.3f} (≪2 唔值)
  ⟹ 「第二拍頻 = K_tree 譜 λ_k 直接耦合」假說: 🔴 【未檢出】
     K_tree 譜作為第二變量 (k=n/34−n/33−n/68−n × 差/比/和形式) 全部唔顯著
  ⟹ 若「另一拍頻」存在, 唔係 K_tree 譜之直接差/比/和形式
     可能: ① 拍頻係【非線性】組合 (m = f(|Δm|^α, λ^β) 冪乘 — 非線性)
           ② 拍頻喺【更高階】|Δm| 項 (次近鄰已測 top-10 0.00011 — 唔關事)
           ③ 拍頻需【模式選擇規則】先定 k(n) (O155 scripts/21) — 未用
     下一步: 冪乘形式 ln m = b0 + α ln|Δm| + β ln λ_k 之【固定 k 掃描】(O155 模式選擇)
""")
n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "18_second_beat.json", "w") as f:
    json.dump({
        "baseline_rms": rms_base,
        "beat_regressions": {k: v for k, v in results.items()},
        "best_regression": best[0],
        "correlations": {k: v for k, v in corrs.items()},
        "best_corr": best_c[0],
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/18_second_beat.json")
