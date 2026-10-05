#!/usr/bin/env python3
"""
O137 — Phase 1: 拓撲諧振方程 v3 (零參數 P̂ 投影模型)
=====================================================
關鍵結構 (O53 scripts/14 P̂ v2 建構):
  Kähler modulus n ↔ mode n (n=1..36, 低能量排序)
  行權重: P[α,β] = φ^(−avg(γ_n, γ_m)) 對 same-parity beats (n,m)

共振假設 (零參數):
  m_f(n) = M₀ · γ_n · P_n
  P_n = Σ_{m same parity, m≠n} φ^{−(γ_n+γ_m)/2}   ← P̂ 行投影和 (純幾何)
  δS/dn = 0  →  m_f(n) 嘅極值點 = 拓撲駐波模式

O54 已知: e⁻:n=1, μ⁻:n=7, τ⁻:n=20 (m_f = M₀·γ_n·P_f)
"""
import math, json
import numpy as np
from itertools import combinations

phi = (1 + math.sqrt(5)) / 2
Nd = 44
M0 = 27.900915  # MeV

gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd+1)])
omega = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd+1)])

LEPTONS = [1, 7, 20]
QUARKS = [14, 33, 34]

def check(name, cond, detail=""):
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 72)
print("O137 Phase 1 v3: P̂ 零參數共振模型")
print("=" * 72)

# ============================================================
# 1. P_n: Kähler modulus n 嘅投影和 (O53 P̂ v2 行權重)
# ============================================================
print("\n[1] P_n = Σ_{m同parity} φ^(−(γ_n+γ_m)/2)")

P_n = np.zeros(Nd)
for n in range(1, Nd+1):
    s = 0.0
    for m in range(1, Nd+1):
        if m == n:
            continue
        if (n + m) % 2 != 0:
            continue  # 只 same parity
        s += phi ** (-(gamma[n-1] + gamma[m-1]) / 2)
    P_n[n-1] = s

print(f"{'n':>3} | {'γ_n':>8} | {'P_n':>10} | {'γ_n·P_n':>10} | {'m_f=M₀γP (MeV)':>16}")
print("-" * 65)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    mf = M0 * gamma[n-1] * P_n[n-1]
    print(f"{n:3d}{marker} | {gamma[n-1]:8.6f} | {P_n[n-1]:10.6f} | {gamma[n-1]*P_n[n-1]:10.6f} | {mf:16.6f}")

# ============================================================
# 2. m_f(n) 極值點 (δS/dn = 0)
# ============================================================
print("\n[2] m_f(n) = M₀·γ_n·P_n 極值分析")

m_f = M0 * gamma * P_n
dm = np.gradient(m_f)
d2m = np.gradient(dm)

extrema = []
for n in range(2, Nd):
    if dm[n-2] * dm[n-1] <= 0:
        etype = "max" if d2m[n-1] < 0 else "min"
        extrema.append((n, etype, m_f[n-1]))

print(f"\n  極值點 (斜率變號):")
for n, etype, mf in extrema:
    marker = " ★" if n in LEPTONS else (" ☆" if n in QUARKS else "")
    print(f"    n={n:2d} {etype:>3}: m_f = {mf:10.4f} MeV{marker}")

# 檢查輕子
print(f"\n  輕子模式位置:")
for n in LEPTONS:
    is_ext = any(e[0] == n for e in extrema)
    print(f"    n={n:2d} ★: m_f = {m_f[n-1]:10.4f} MeV  {'✅ 極值' if is_ext else '🔴 唔係極值'}")

# ============================================================
# 3. 相對質量階層 vs SM 費米子
# ============================================================
print("\n" + "=" * 72)
print("[3] 質量階層: 預言譜 vs SM")
print("=" * 72)

# 按 m_f 排序
ranked = sorted([(n, m_f[n-1]) for n in range(1, Nd+1)], key=lambda x: x[1])
print(f"\n  預言質量譜 (由低到高):")
for i, (n, mf) in enumerate(ranked):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"    {i+1:2d}. n={n:2d}{marker}: {mf:10.4f} MeV")

# 比較: 預言嘅 6 個候選 (1,7,14,20,33,34) 質量
print(f"\n  候選模式質量 vs SM:")
sm_masses = {
    1: ("e⁻", 0.511), 7: ("μ⁻", 105.66), 20: ("τ⁻", 1776.86),
    14: ("s", 93.0), 33: ("b", 4180), 34: ("c", 1270),
}
print(f"{'n':>3} | {'SM粒子':>6} | {'SM質量(MeV)':>12} | {'預言 m_f(MeV)':>14} | {'Δ%':>8}")
print("-" * 55)
for n in LEPTONS + QUARKS:
    name, sm = sm_masses[n]
    pred = m_f[n-1]
    dev = (pred - sm) / sm * 100
    print(f"{n:3d} | {name:>6} | {sm:12.4f} | {pred:14.4f} | {dev:8.2f}%")

# ============================================================
# 4. 倍頻結構: m_f(n) 嘅比率
# ============================================================
print("\n" + "=" * 72)
print("[4] 倍頻比 (拍頻比 × 投影比)")
print("=" * 72)

# m_f(n1)/m_f(n2) = (γ_n1·P_n1)/(γ_n2·P_n2)
print(f"\n  m_f(7)/m_f(1) = {m_f[6]/m_f[0]:.4f}  (SM: m_μ/m_e = 206.77)")
print(f"  m_f(20)/m_f(7) = {m_f[19]/m_f[6]:.4f}  (SM: m_τ/m_μ = 16.82)")
print(f"  m_f(20)/m_f(1) = {m_f[19]/m_f[0]:.4f}  (SM: m_τ/m_e = 3477.2)")

print(f"\n  γ 比部分:")
print(f"  γ_7/γ_1 = {gamma[6]/gamma[0]:.4f}")
print(f"  γ_20/γ_7 = {gamma[19]/gamma[6]:.4f}")
print(f"  γ_20/γ_1 = {gamma[19]/gamma[0]:.4f}")

print(f"\n  P 比部分:")
print(f"  P_7/P_1 = {P_n[6]/P_n[0]:.4f}")
print(f"  P_20/P_7 = {P_n[19]/P_n[6]:.4f}")
print(f"  P_20/P_1 = {P_n[19]/P_n[0]:.4f}")

# ============================================================
# 5. 更完整模型: 加入奇 parity 修正 (CPX 部分)
# ============================================================
print("\n" + "=" * 72)
print("[5] 完整投影: P_n^tot = P_K(n) + λ·P_C(n)")
print("=" * 72)

# P_K: same-parity beats (Kähler 行)
# P_C: opposite-parity beats (CPX 行, 權重 exp(-1/avg))
P_K = np.zeros(Nd)
P_C = np.zeros(Nd)
for n in range(1, Nd+1):
    for m in range(1, Nd+1):
        if m == n:
            continue
        if (n + m) % 2 == 0:
            P_K[n-1] += phi ** (-(gamma[n-1] + gamma[m-1]) / 2)
        else:
            avg = (gamma[n-1] + gamma[m-1]) / 2
            P_C[n-1] += math.exp(-1.0 / avg)  # CPX 行權重 (O53)

# CPX 行權重係 exp(-1/γ), 規模差好遠 — 需要歸一化
scale_C = P_K[0] / P_C[0]  # 用 n=1 歸一
P_tot = P_K + P_C * scale_C
m_tot = M0 * gamma * P_tot

print(f"  CPX scale (n=1 歸一): {scale_C:.4f}")
print(f"{'n':>3} | {'P_K':>10} | {'P_C':>10} | {'P_tot':>10} | {'m_tot(MeV)':>12}")
print("-" * 55)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"{n:3d}{marker} | {P_K[n-1]:10.6f} | {P_C[n-1]:10.6f} | {P_tot[n-1]:10.6f} | {m_tot[n-1]:12.4f}")

dm_tot = np.gradient(m_tot)
ext_tot = [n for n in range(2, Nd) if dm_tot[n-2]*dm_tot[n-1] <= 0]
print(f"\n  極值點: {ext_tot}")
print(f"  輕子命中: {[n for n in LEPTONS if n in ext_tot]}")

# ============================================================
# 6. 質量譜形狀分析
# ============================================================
print("\n" + "=" * 72)
print("[6] 質量譜形狀: 階層結構")
print("=" * 72)

# 檢查 m_f(n) 嘅 log 結構
log_mf = np.log(m_f)
print(f"  log m_f 嘅差: Δlog(n→n+1)")
for n in range(1, Nd):
    d = log_mf[n] - log_mf[n-1]
    marker = "★" if n+1 in LEPTONS else ("☆" if n+1 in QUARKS else "")
    print(f"    n={n}→{n+1}{marker}: Δln = {d:8.4f}")

# ============================================================
# 7. 保存
# ============================================================
results = {
    "test": "O137 Phase 1 v3: P̂ 零參數共振",
    "P_n": P_n.tolist(),
    "m_f": m_f.tolist(),
    "extrema": extrema,
    "lepton_hits": [n for n in LEPTONS if any(e[0]==n for e in extrema)],
    "mass_ratios": {
        "m7/m1": float(m_f[6]/m_f[0]), "SM_mu_e": 206.77,
        "m20/m7": float(m_f[19]/m_f[6]), "SM_tau_mu": 16.82,
    },
}
with open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/01_resonance_spectrum.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n結果已保存 data/01_resonance_spectrum.json")