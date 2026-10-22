#!/usr/bin/env python3
"""
O147 優先級一 — κ(t) 網格對齊: κ(t) = −14 定 0? (O64 Z_topology 42 交叉)
============================================================================
docs/09 §3.1 行規則外推 κ(t) = κ(b) − B² = −14 (gen3 預測)
O64: m_t = M₀×γ₄₄×37×42 (γ₄₄=4 Nyquist, F_proj=37, Z_topology=42=6×7)

矛盾: κ(t) = −14 令 k(t/b) = −16 → φ^(−16/528) = −0.92% 修正,
  但 O35 cascade t/b 已 0.05% 閉合 → 會過度修正

測試:
  A. Z_eff 倒推: Z_eff = m_t_PDG / (M₀×γ₄₄×37×φ^(κ(t)/528))
     睇 κ(t) ∈ {−14, 0, +14} 邊個令 Z_eff 最接近 O64 嘅 42
  B. t 相關比 (t/b, t/c, t/s, t/u, t/d, t/τ, t/e) 用 κ(t) 候選驗證
     grid_t_full = M₀×γ₄₄×37×42 (O64 完整值), grid 其他 = O143 grid
     比 = grid_t_full/grid_X × φ^((κ(t)−κ(X))/528) vs PDG
  C. κ(t) = 0 同 κ(t) = −14 比較 — 邊個全中?
"""
import math

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

N_d = 44
B = 4
N_gen = 3
phi = (1 + math.sqrt(5)) / 2
M0 = 27.900915  # MeV
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}

def gamma_n(n): return 4 * math.sin(n * math.pi / 88) ** 2

# O143 grid
GRID = {"e":(1,3.6), "mu":(7,15.5), "tau":(20,37), "u":(1,15.5), "c":(34,13),
        "d":(1,33), "s":(14,3.6), "b":(33,44)}

# κ 表 (docs/09, 輕子修正版)
KAPPA = {"e":3.5, "mu":3.5, "tau":9.0, "d":0.0, "s":18.0, "b":2.0, "c":2.0, "u":-16.0}

# PDG t 質量 (2024): pole 172.69 GeV, MS-bar 172.57 GeV
M_T_POLE = 172.69e3   # MeV
M_T_MS = 172.57e3     # MeV
# O64: γ₄₄ = 4 (Nyquist), F_proj = 37, Z_topology = 42
GAMMA_44 = gamma_n(44)
F_PROJ_T = 37
Z_TOP = 42

print("=" * 100)
print("  O147 優先級一 — κ(t) 網格對齊: −14 vs 0 (O64 Z_topology 42)")
print("=" * 100)

# ============ A. Z_eff 倒推 ============
print("\n─── A. Z_eff 倒推 (m_t = M₀×γ₄₄×37×φ^(κ/528)×Z_eff) ───")
base = M0 * GAMMA_44 * F_PROJ_T
print(f"    M₀×γ₄₄×37 = {base:.2f} MeV (O64 基礎, 冇 Z_topology)")
print(f"    ×42 = {base*42:.2f} MeV = {base*42/1e3:.3f} GeV (O64 完整)")
print(f"    PDG pole = {M_T_POLE/1e3:.3f} GeV, MS-bar = {M_T_MS/1e3:.3f} GeV")

for kt_name, kt in [("κ=0", 0.0), ("κ=−14", -14.0), ("κ=+14", +14.0)]:
    for label, m_t in [("pole", M_T_POLE), ("MS", M_T_MS)]:
        z_eff = m_t / (base * phi**(kt/528))
        dev42 = abs(z_eff - 42)/42*100
        mark = "✅" if dev42 < 0.5 else ("🟡" if dev42 < 1.0 else "🔴")
        print(f"    {kt_name:>6} {label:4s}: Z_eff = {z_eff:8.3f} (vs 42, Δ{dev42:.2f}%) {mark}")

# O64 docs 話「數值驗證 41.895 vs 42」→ 用 pole 計 κ=0 應該近 41.9
z0_pole = M_T_POLE / base
z0_ms = M_T_MS / base
print(f"\n    κ=0 pole: Z_eff = {z0_pole:.3f} (O64 docs 記錄 41.895)")
print(f"    κ=0 MS  : Z_eff = {z0_ms:.3f}")
check("A1 κ=0 令 Z_eff ≈ 42 (Δ<0.5%)", abs(z0_pole - 42)/42 < 0.005, f"Z={z0_pole:.3f}")
check("A2 κ=−14 令 Z_eff 偏離 42 (Δ>0.5%)", abs(M_T_POLE/(base*phi**(-14/528)) - 42)/42 > 0.005,
      f"Z={M_T_POLE/(base*phi**(-14/528)):.3f}")

# ============ B. t 相關比驗證 ============
print("\n─── B. t 相關比: grid_t_full × φ^(κ差/528) vs PDG ───")
grid_t_full = base * Z_TOP  # 173.4 GeV O64 完整值

# PDG 比目標 (t 用 pole 172.69; 其他用 O143 current masses)
PDG = {
    "t/b": M_T_POLE/4180.0, "t/c": M_T_POLE/1270.0, "t/s": M_T_POLE/93.4,
    "t/u": M_T_POLE/2.16,   "t/d": M_T_POLE/4.67,   "t/tau": M_T_POLE/1776.86,
    "t/e": M_T_POLE/0.511,  "t/mu": M_T_POLE/105.66,
}
t_pairs = [("t/b","b"), ("t/c","c"), ("t/s","s"), ("t/u","u"),
           ("t/d","d"), ("t/tau","tau"), ("t/e","e"), ("t/mu","mu")]

def grid_mass(p):
    n, pf = GRID[p]
    return M0 * gamma_n(n) * pf

hits0 = hits_minus14 = 0
for kt_name, kt in [("κ(t)=0", 0.0), ("κ(t)=−14", -14.0)]:
    print(f"\n    ── {kt_name} ──")
    print(f"    {'比':>6} | {'grid_t/X':>11} | {'PDG':>11} | {'裸Δ%':>7} | {'κ差':>5} | {'修正後Δ%':>8} | 判定")
    hits = 0
    for name, x in t_pairs:
        grid_ratio = grid_t_full / grid_mass(x)
        tgt = PDG[name]
        bare_dev = abs(grid_ratio - tgt)/tgt*100
        k_diff = kt - KAPPA[x]
        corr = grid_ratio * phi**(k_diff/528)
        corr_dev = abs(corr - tgt)/tgt*100
        hit = corr_dev < 0.5
        hits += hit
        print(f"    {name:>6} | {grid_ratio:11.3f} | {tgt:11.3f} | {bare_dev:6.2f}% | {k_diff:+5.1f} | {corr_dev:7.3f}% | {'✅' if hit else '🔴'}")
    print(f"    命中: {hits}/8 (判據 Δ<0.5%)")
    if kt_name == "κ(t)=0": hits0 = hits
    else: hits_minus14 = hits

check("B1 κ(t)=0: t 相關比 ≥ 6/8 修正後 Δ<0.5%", hits0 >= 6, f"{hits0}/8")
check("B2 κ(t)=−14 顯著差過 κ(t)=0", hits_minus14 < hits0, f"−14:{hits_minus14}/8 vs 0:{hits0}/8")

# ============ C. κ(t) = 0 嘅結構解釋 ============
print("\n─── C. κ(t) = 0 嘅結構解釋 ───")
print("""
κ(t) = 0 同 O64 Z_topology = 42 一致:
  - t 係唯一 Nyquist 模 (n=44, γ₄₄ = 4 = B = Z₂²)
  - t 嘅放大完全由 Z_topology = 42 = 6×7 = A₄(Z₅)×L₇ (Caspian Singularity) 承載
  - κ 修正 (φ^(κ/528), |κ|≤34 → ≤4.3%) 同 Z_topology (42×) 唔同量級
  - t 嘅 κ = 0 = 「修正零點」: Z_topology 吸收全部放大, κ 相位歸零

行規則 gen3 例外原因:
  - κ(U) = κ(D) − B² 對 gen1 (u/d), gen2 (c/s) 成立 — 兩者都喺 O143 grid
  - gen3 嘅 t 唔喺 O143 grid (16 約束冇覆蓋 t) — O64 用 γ₄₄×37×42
  - 所以 κ(t) 唔可以由 grid 行規則外推 — 要用 O64 數據實證 = 0
""")
check("C1 κ(t) = 0 同 O64 Z_topology 42 精確映射", abs(z0_pole/42 - 1) < 0.005)

# 交叉驗證 MS-bar
print("\n─── D. MS-bar 交叉驗證 (m_t = 172.57 GeV) ───")
z0_ms_val = M_T_MS / base
print(f"    κ=0 MS: Z_eff = {z0_ms_val:.3f} (vs 42, Δ{abs(z0_ms_val-42)/42*100:.2f}%)")
check("D1 MS-bar 都接近 42 (Δ<0.5%)", abs(z0_ms_val - 42)/42 < 0.005, f"Z={z0_ms_val:.3f}")

# ============ 總結 ============
print("\n" + "=" * 100)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
for name, ok, detail in rows:
    print(f"    {'✅' if ok else '🔴'} {name}  {detail}")
print("=" * 100)
