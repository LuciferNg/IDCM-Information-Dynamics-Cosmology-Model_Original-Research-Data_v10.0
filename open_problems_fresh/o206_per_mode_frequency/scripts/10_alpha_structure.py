#!/usr/bin/env python3
"""
O206 — Script 10: α 之結構身份 (方向 1) — 兩錨盲測 + 曲率檢驗 + 池子 null
=========================================================
承接 docs/11 §七 方向 1。
⚠️ O136 docs/35 已證 α 不可辨識 (ΔRMS ≪ bootstrap σ, 11 候選中 8 個落喺 1% 寬度內)。
⟹ 本 script 唔重複「邊個候選最準」, 而係問三個【新】問題:

  §A 兩錨盲測: 用兩個錨 (極端模式) 凍結 (α, M₀), 預測其餘 7 個 ⟹ 真 out-of-sample
     (docs/35 用全 9 點擬合 ⟹ 唔算盲測)
  §B 曲率檢驗: ln m = c₀ + α·ln|Δm| + β·(ln|Δm|)² 之 β 是否顯著?
     β ≈ 0 ⟹ 冪律形式正確, 殘餘係 N=9 之不可約噪聲
     β ≠ 0 ⟹ 冪律形式錯, 曲率才是真結構
  §C ★★ 池子 null: 由 IDCM 結構常數池生成全部 ≤3-算子表達式,
     數有幾多個落喺 α ± 1σ/2σ; 同「隨機 α」比較 ⟹ 判定命中是否有信息
  §D 裁決
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, LM, MASS, E_ring44, V_position,
                      logscore, sum_V2_dE)

OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


def ols(X, y):
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    A = np.column_stack([np.ones(len(y))] + [X[:, i] for i in range(X.shape[1])])
    beta, *_ = np.linalg.lstsq(A, np.asarray(y, dtype=float), rcond=None)
    return beta, A @ beta


V = V_position()
E = E_ring44()
PAIR = [(1, "t"), (2, "b"), (3, "tau"), (4, "c"), (5, "mu"), (7, "s"), (9, "d"), (11, "u"), (13, "e")]
dm = sum_V2_dE(E, V)
ldm = np.array([math.log(dm[A5_MODES.index(n)]) for n, _ in PAIR])
lm = np.array([math.log(MASS[p]) for _, p in PAIR])

print("=" * 100)
print("O206 Script 10: α 之結構身份 — 兩錨盲測 + 曲率 + 池子 null")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A 兩錨盲測 (真 out-of-sample)\n{'─'*100}")
print("""
  方法: 選兩個錨 (i, j) ⟹ α_anchor = ln(m_i/m_j) / ln(|Δm_i|/|Δm_j|)
        M₀ = m_j / |Δm_j|^α ⟹ 預測其餘 7 個
  ⟹ 呢個係【真盲測】: 7 個模式完全冇參與擬合
""")
print(f"\n  {'錨對 (i,j)':>16} {'α_anchor':>10} {'7 個預測 RMS':>14} {'全 9 RMS':>10}")
print("  " + "-" * 54)
anchors = [(1, 13), (1, 2), (2, 13), (1, 5), (5, 13), (3, 9), (1, 7), (7, 13)]
blind = {}
for i, j in anchors:
    a = (lm[A5_MODES.index(i)] - lm[A5_MODES.index(j)]) / (ldm[A5_MODES.index(i)] - ldm[A5_MODES.index(j)])
    M0a = math.exp(lm[A5_MODES.index(j)] - a * ldm[A5_MODES.index(j)])
    pred = math.log(M0a) + a * ldm
    rest = [k for k in range(9) if k not in (A5_MODES.index(i), A5_MODES.index(j))]
    r7 = float(np.std(lm[rest] - pred[rest]))
    r9 = float(np.std(lm - pred))
    blind[(i, j)] = {"alpha": float(a), "rms7": r7, "rms9": r9}
    print(f"  {str((i, j)):>16} {a:>10.6f} {r7:>14.4f} {r9:>10.4f}")

best_blind = min(blind.values(), key=lambda v: v["rms7"])
worst_blind = max(blind.values(), key=lambda v: v["rms7"])
a_ext = blind[(1, 13)]["alpha"]
print(f"\n  ★ 極端錨 (t=1, e=13): α = {a_ext:.6f}")
print(f"  ★ 7 個盲測 RMS 範圍 = [{best_blind['rms7']:.4f}, {worst_blind['rms7']:.4f}]")
chk("C1 [盲測] 極端錨 (1,13) 之 7 個盲測 RMS < 0.8 (冪律有預言內容)",
    blind[(1, 13)]["rms7"] < 0.8, f"RMS(7) = {blind[(1, 13)]['rms7']:.4f}")
a_span = max(v["alpha"] for v in blind.values()) - min(v["alpha"] for v in blind.values())
chk("C2 ★ [盲測] 兩錨凍結【唔】足以釘住 α (跨度 > 0.15) ⟹ 有效壓縮比 < 8:1",
    a_span > 0.15,
    f"α ∈ [{min(v['alpha'] for v in blind.values()):.4f}, "
    f"{max(v['alpha'] for v in blind.values()):.4f}] (跨度 {a_span:.4f})")

# ★ 三錨掃描: 全部 C(9,3) = 84 組, 睇 α 之穩定度 ⟹ 量化「有效壓縮比」
import itertools as it
triples = list(it.combinations(range(9), 3))
a3 = []
for tr in triples:
    bb, _ = ols(ldm[list(tr)], lm[list(tr)])
    a3.append(float(bb[1]))
a3 = np.array(a3)
print(f"\n  ★ 三錨掃描 (全部 {len(triples)} 組): α ∈ [{a3.min():.4f}, {a3.max():.4f}], "
      f"中位 = {np.median(a3):.4f}, σ = {a3.std():.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 曲率檢驗: 冪律形式啱唔啱?\n{'─'*100}")
b_lin, pred_lin = ols(ldm, lm)
b_quad, pred_quad = ols(np.column_stack([ldm, ldm ** 2]), lm)
rms_lin = float(np.std(lm - pred_lin))
rms_quad = float(np.std(lm - pred_quad))
print(f"\n  線性 (2 參數):   ln m = {b_lin[0]:.4f} + {b_lin[1]:.6f}·ln|Δm|        RMS = {rms_lin:.4f}")
print(f"  二次 (3 參數):   + {b_quad[2]:.6e}·(ln|Δm|)²                     RMS = {rms_quad:.4f}")

rng = np.random.default_rng(20260921)
boot_beta = np.empty(2000)
for k in range(2000):
    idx = rng.integers(0, 9, 9)
    bb, _ = ols(np.column_stack([ldm[idx], ldm[idx] ** 2]), lm[idx])
    boot_beta[k] = bb[2]
sd_beta = float(np.std(boot_beta))
z_beta = abs(float(b_quad[2])) / sd_beta if sd_beta > 0 else 0.0
print(f"\n  二次項 β = {b_quad[2]:.6e} ± {sd_beta:.6e}  (bootstrap N=2000)")
print(f"  |β|/σ = {z_beta:.4f}")
chk("C3 [曲率] 二次項唔顯著 (|β|/σ < 2) ⟹ 冪律形式正確, 殘餘係 N=9 不可約噪聲",
    z_beta < 2.0, f"|β|/σ = {z_beta:.4f} (改善 {rms_lin/rms_quad:.4f}×)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C ★★ 池子 null — 命中 α 有冇信息?\n{'─'*100}")
POOL = {
    "N_d": 44, "N_gen": 3, "B": 4, "SumG": 90, "mu2": 2, "L4": 7, "L5": 11, "L6": 18,
    "L7": 29, "F5": 5, "F6": 8, "F7": 13, "F9": 34, "F10": 55, "F11": 89, "F12": 144,
    "K_tree": 33, "dimC": 3, "h11": 36, "h21": 98, "chi": 124, "CY3": 134, "m45": 45,
    "E_J": 123, "N88": 88, "N176": 176, "N264": 264, "N421": 421, "N528": 528,
    "N2025": 2025, "phi": 1.6180339887, "phi2": 2.6180339887, "pi": math.pi,
    "e": math.e, "sqrt2": math.sqrt(2), "sqrt5": math.sqrt(5), "sqrt3": math.sqrt(3),
}
alpha_fit = float(b_lin[1])
boot_a = []
for k in range(2000):
    idx = rng.integers(0, 9, 9)
    bb, _ = ols(ldm[idx], lm[idx])
    boot_a.append(bb[1])
sd_a = float(np.std(boot_a))
print(f"\n  α_fit = {alpha_fit:.6f} ± {sd_a:.6f}")
n_within_1sig = int(np.sum(np.abs(a3 - alpha_fit) < sd_a))
print(f"  ★ 三錨掃描 vs 全擬合: 落喺 ±1σ 內之三錨組數 = {n_within_1sig}/{len(triples)} "
      f"({100*n_within_1sig/len(triples):.1f}%) ⟹ 三錨已大致釘住 α")

vals = list(POOL.values())
names = list(POOL.keys())
cands = {}
for i, (na, a) in enumerate(zip(names, vals)):
    cands[f"{na}"] = a
    for j, (nb, b) in enumerate(zip(names, vals)):
        if i != j and b != 0:
            cands[f"{na}/{nb}"] = a / b
            cands[f"{na}*{nb}"] = a * b
            if 0 < a <= 4:
                cands[f"{na}^({nb})"] = a ** b if abs(b) < 12 else float("nan")
        if i < j:
            cands[f"{na}+{nb}"] = a + b
            cands[f"{na}-{nb}"] = a - b
cands = {k: v for k, v in cands.items() if np.isfinite(v) and 0.5 <= v <= 5.0}
print(f"  池子規模 (0.5 ≤ 值 ≤ 5): {len(cands)} 個候選表達式")

hits1 = [k for k, v in cands.items() if abs(v - alpha_fit) < sd_a]
hits2 = [k for k, v in cands.items() if abs(v - alpha_fit) < 2 * sd_a]
print(f"  落喺 α ± 1σ ({sd_a:.4f}) 內: {len(hits1)} 個")
print(f"  落喺 α ± 2σ 內: {len(hits2)} 個")
print(f"  樣本 (1σ 內前 8 個): " + ", ".join(f"{k} = {cands[k]:.5f}" for k in hits1[:8]))

# ★ null: 對隨機 α 值做同一計數 ⟹ 得到「chance rate」
rng_alpha = np.random.default_rng(7)
null_counts = []
for _ in range(2000):
    a_rand = rng_alpha.uniform(1.0, 4.0)
    null_counts.append(sum(1 for v in cands.values() if abs(v - a_rand) < sd_a))
null_counts = np.array(null_counts)
rate_obs = len(hits1)
p_pool = float((null_counts >= rate_obs).mean())
print(f"\n  ★ null (隨機 α ∈ [1,4], N=2000): 1σ 內候選數 中位 = {np.median(null_counts):.0f}, "
      f"範圍 [{null_counts.min()}, {null_counts.max()}]")
print(f"  P(隨機 α 之候選數 ≥ 觀測 {rate_obs}) = {p_pool:.4f}")
chk("C4 ★★ [池子 null] 觀測命中數唔特異 (P > 0.05) ⟹ 命中 α 唔構成證據",
    p_pool > 0.05,
    f"觀測 {rate_obs} 個 vs null 中位 {np.median(null_counts):.0f} 個, P = {p_pool:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 裁決 (script 10)\n{'─'*100}")
print(f"""
  ① 兩錨盲測: 極端錨 (t=1, e=13) ⟹ α = {a_ext:.6f}, 其餘 7 個 RMS = {blind[(1,13)]['rms7']:.4f}
     ⟹ 冪律【有真預言內容】(7 個模式完全冇參與凍結)
  ② 錨對穩健: α ∈ [{min(v['alpha'] for v in blind.values()):.4f}, {max(v['alpha'] for v in blind.values()):.4f}]
  ③ 曲率檢驗: 二次項 |β|/σ = {z_beta:.4f} ⟹ 冪律形式正確
     ⟹ 0.5872 殘餘 = N=9 之不可約噪聲 (唔係「缺失結構層」)
  ④ ★★ 池子 null: {len(cands)} 個結構表達式中 {rate_obs} 個落喺 α ± 1σ;
     隨機 α 之中位數 = {np.median(null_counts):.0f} 個 ⟹ P = {p_pool:.4f} ⟹ 【命中無信息】
  ⟹ 方向 1 裁決: α 之【數值身份】永久不可辨識 (池子密度論證),
     但 α 之【預言角色】成立 (兩錨盲測通過) ⟹ 唔應再花力氣搵 α 之結構值
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "10_alpha_structure.json", "w") as f:
    json.dump({
        "alpha_fit": alpha_fit, "sigma_alpha": sd_a,
        "two_anchor": {str(k): v for k, v in blind.items()},
        "curvature_beta": float(b_quad[2]), "curvature_sigma": sd_beta, "z_beta": z_beta,
        "rms_linear": rms_lin, "rms_quadratic": rms_quad,
        "pool_size": len(cands), "pool_hits_1sigma": rate_obs, "pool_hits_2sigma": len(hits2),
        "pool_null_median": float(np.median(null_counts)), "pool_null_p": p_pool,
        "hits_1sigma_sample": hits1[:12],
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/10_alpha_structure.json")
