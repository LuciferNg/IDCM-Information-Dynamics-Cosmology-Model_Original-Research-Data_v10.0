#!/usr/bin/env python3
"""
O206 — Script 22: 9 個費米子形狀因素 (C_f / φ=9) 導入閉合測試
=========================================================
調律者 (2026-09-21): 「把這9個費米子的形狀因素導入看看是否能閉合這個0.5872」

形狀因素候選:
  A. O137 C_f (幾何重疊因子): 輕子已閉合 (e=3.6, μ=15.5, τ=37 Δ≤0.34%)
     夸克: CSG v2 網格 (u=15.5, d=33, s=3.6, c=13, b=44) — ⚠️ 後驗
  B. φ=9 張量 3×3 座標 (i+j 型標量)
  C. φ=9 labels (33,37,41,44,45,47,48,50,51)

測試:
  §A ln m = b0 + α·ln|Δm| + β·ln C_f  (O206 A₅ 模式, 9 點)
  §B O137 Decoupling: m = M₀·γ_n·C_f  (O137 網格模式)
  §C ★ t 反推: 若形狀因素閉合, t 所需 C_f(t) 係咩值? (預言)
  §D 裁決
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


M0 = 27.900915
# O206 9 費米子 (O136 A₅ 模式, PDG 質量 MeV)
FERM = [("t", 1, 172690.0), ("b", 2, 4180.0), ("τ", 3, 1776.86), ("c", 4, 1270.0),
        ("μ", 5, 105.6584), ("s", 7, 93.4), ("d", 9, 4.67), ("u", 11, 2.16), ("e", 13, 0.511)]
# C_f 形狀因素 (O137 輕子閉合 + CSG 網格夸克 [後驗標記])
CF = {"e": 3.6, "μ": 15.5, "τ": 37.0, "u": 15.5, "d": 33.0, "s": 3.6, "c": 13.0, "b": 44.0}
# CSG v2 網格模式
CSG_N = {"e": 1, "μ": 7, "τ": 20, "u": 1, "d": 1, "s": 14, "c": 34, "b": 33}

V = V_position()
E = E_ring44()
dm = sum_V2_dE(E, V)
modes = np.array([n for _, n, _ in FERM])
masses = np.array([m for _, _, m in FERM])
ldm = np.array([math.log(dm[A5_MODES.index(n)]) for n in modes])
lm = np.array([math.log(m) for m in masses])
# 有 C_f 嘅 8 個費米子 (t 無 — §C 反推)
HAS_CF = [i for i, (p, _, _) in enumerate(FERM) if p in CF]
lm8 = lm[HAS_CF]
ldm8 = ldm[HAS_CF]
lncf8 = np.array([math.log(CF[FERM[i][0]]) for i in HAS_CF])


def ols2(x, y):
    A = np.column_stack([np.ones(len(y)), x])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    return b, y - A @ b


print("=" * 100)
print("O206 Script 22: 形狀因素導入閉合測試")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A C_f 導入 O206 冪律映射 (9 點, A₅ 模式)\n{'─'*100}")
b0, r0 = ols2(ldm, lm)
rms0 = float(np.sqrt(np.mean(r0 ** 2)))
print(f"  基準: ln m = {b0[0]:.4f} + {b0[1]:.6f}·ln|Δm|,  RMS = {rms0:.4f}")
# 2 變量: ln|Δm| + ln C_f (8 點)
A2 = np.column_stack([np.ones(8), ldm8, lncf8])
b2, *_ = np.linalg.lstsq(A2, lm8, rcond=None)
r2 = lm8 - A2 @ b2
rms2 = float(np.sqrt(np.mean(r2 ** 2)))
# β 顯著性
n = 8
s2v = np.sum(r2 ** 2) / (n - 3)
XtX_inv = np.linalg.inv(A2.T @ A2)
se_b = math.sqrt(s2v * XtX_inv[2, 2])
z = b2[2] / se_b
print(f"  +ln C_f (8 點): ln m = {b2[0]:.4f} + {b2[1]:.6f}·ln|Δm| + {b2[2]:.4f}·ln C_f")
print(f"  RMS = {rms2:.4f}  改善 = {rms0/rms2:.3f}×   β/σ = {z:.2f}")
print(f"  AIC: 基準 {8*math.log(rms0**2)+4:.3f} vs +C_f {8*math.log(rms2**2)+6:.3f}")
# dof 紅利 null
rng = np.random.default_rng(20260921)
nr = []
for _ in range(5000):
    xr = rng.normal(size=8)
    A3 = np.column_stack([np.ones(8), ldm8, xr])
    b3, *_ = np.linalg.lstsq(A3, lm8, rcond=None)
    nr.append(float(np.sqrt(np.mean((lm8 - A3 @ b3) ** 2))))
p_dof = float((np.array(nr) <= rms2).mean())
print(f"  dof 紅利 null: P(隨機第三變量 ≤ RMS) = {p_dof:.4f}")
chk("C1 C_f 導入改善超越 dof 紅利 (P < 0.01)",
    p_dof < 0.01, f"RMS {rms0:.4f} → {rms2:.4f}, β/σ = {z:.2f}, P = {p_dof:.4f}")
chk("C2 C_f 導入閉合 (RMS < 0.1)",
    rms2 < 0.1, f"RMS = {rms2:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B O137 Decoupling: m = M₀·γ_n·C_f (CSG 網格模式)\n{'─'*100}")
print(f"  8 個有 C_f 嘅費米子 (t 留空):")
for p, n, m in FERM:
    if p not in CF:
        print(f"  {p:>3}: 無 C_f (t)")
        continue
    gn = E[CSG_N[p] - 1]
    mp = M0 * gn * CF[p]
    dp = (mp - m) / m * 100
    print(f"  {p:>3}: n={CSG_N[p]:>3} γ={gn:.6f} C_f={CF[p]:>5} m_pred={mp:>10.3f} m_obs={m:>10.3f} Δ={dp:>7.2f}%")
res_csg = []
for p, n, m in FERM:
    if p in CF:
        res_csg.append(math.log(M0 * E[CSG_N[p] - 1] * CF[p] / m))
rms_csg = float(np.std(res_csg))
print(f"  8 點 RMS(ln) = {rms_csg:.4f} (CSG v2 網格; 後驗 C_f)")
print(f"  對照 O206 冪律 9 點 RMS = {rms0:.4f}")
chk("C3 O137 Decoupling 8/8 閉合 (RMS < 0.1) — 但 C_f 後驗",
    rms_csg < 0.1, f"RMS = {rms_csg:.4f} (⚠️ C_f 值來自後驗網格)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C ★ t 反推: 若形狀因素閉合, t 需要 C_f(t) 幾多?\n{'─'*100}")
# 若 t 用 O137 框架 m = M₀·γ_n·C_f, t 用邊個 n?
# O136 A₅: t(1); O137 網格: U 行 g3 空缺
for n_t in [1, 22, 33, 34, 44]:
    gn = E[n_t - 1]
    cf_req = 172690.0 / (M0 * gn)
    print(f"  n_t={n_t:>3}: γ={gn:.6f} ⟹ C_f(t) 需要 = {cf_req:.4f}")
    # 對照 C_f 池
    pool = [3.6, 13.0, 15.5, 33.0, 37.0, 44.0, 57.0, 61.5, 90.0]
    near = min(pool, key=lambda c: abs(c - cf_req))
    print(f"           最近 C_f 池值 = {near} (Δ {abs(near-cf_req)/cf_req*100:.1f}%)")
cf_t_req = 172690.0 / (M0 * E[0])  # n=1
print(f"\n  ★ t 喺 A₅ n=1: C_f(t) 需要 ≈ {cf_t_req:.1f} = γ₁⁻¹×6190")
print(f"  ★ 對照 C_f 池最大值 61.5 (E_sync): 差 {cf_t_req/61.5:.0f}×")
chk("C4 t 所需 C_f 唔喺現有 C_f 池 (差 > 5×)",
    cf_t_req / 61.5 > 5, f"C_f(t)≈{cf_t_req:.0f} vs 池最大 61.5 ⟹ t 形狀因素未解")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 裁決\n{'─'*100}")
print(f"""
  §A C_f 導入 O206 冪律: RMS {rms0:.4f} → {rms2:.4f} (改善 {rms0/rms2:.3f}×)
     dof 紅利 P = {p_dof:.4f}  β/σ = {z:.2f}
  §B O137 Decoupling (CSG 網格): 8 點 RMS = {rms_csg:.4f} (閉合但 C_f 後驗)
  §C t: 所需 C_f(t) ≈ {cf_t_req:.0f} (n=1), 池最大 61.5 ⟹ t 形狀因素未解
  ⟹ 形狀因素導入結果:
     ① 8 個已知 C_f: 閉合 (0.76%) — 但 C_f 值後驗 (O144 18.6 bits)
     ② C_f 導入 O206 冪律: 改善超越 dof 紅利與否見 C1
     ③ t: 即使形狀因素導入, t 需要 C_f ≈ {cf_t_req:.0f} — 唔喺池
        ⟹ t 形狀必須由 φ=9 相交相位計算畀出大 C_f, 否則 t 仍係缺口
  ⟹ 閉合 0.5872 嘅完整條件:
     [1] 8 個 C_f 由 φ=9 相交相位計算 (唔係後驗) ⟹ 8/8 閉合 0.76%
     [2] t 嘅 C_f(t) ≈ {cf_t_req:.0f} 由 CY₃ 幾何畀出 (新機制/VEV)
     [3] 冇 311 競爭者 (相交相位唯一)
""")
n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "22_shape_factors.json", "w") as f:
    json.dump({
        "a_rms_base": float(rms0), "a_rms_cf": float(rms2),
        "a_beta_z": float(z), "a_dof_p": float(p_dof),
        "b_rms_csg8": float(rms_csg),
        "t_cf_required": float(cf_t_req),
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/22_shape_factors.json")
