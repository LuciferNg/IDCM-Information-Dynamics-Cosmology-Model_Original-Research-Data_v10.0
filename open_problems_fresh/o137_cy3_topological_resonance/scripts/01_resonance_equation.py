#!/usr/bin/env python3
"""
O137 — Phase 1: 拓撲諧振方程 (共振譜) v2
============================================
從 O80 W-field Lagrangian + O57 投影結構推導模式選擇條件。

O57 已閉合結構:
  - Beat 空間 Λ²(R⁴⁴) = 946, even 462 → Kähler, odd 484 → CPX
  - Kähler modulus n ↔ mode n (n=1..36), support = 21 same-parity beats
  - Z₂ (n↔44−n) = 時間反演, fixed 21 = F₈, orbits 441 = F₈²

共振假設 (物理動機):
  模式 n 嘅幾何作用量 S_n = 鏈自能 + CY₃ 投影能
  δS/dn = 0 → 拓撲駐波 (唔衰減)

本腳本計算多個自然共振測度, 唔 cherry-pick。
"""
import math, json
import numpy as np
from itertools import combinations

phi = (1 + math.sqrt(5)) / 2
Nd = 44

gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd+1)])
omega = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd+1)])

beats = list(combinations(range(1, Nd+1), 2))

LEPTONS = [1, 7, 20]
QUARKS = [14, 33, 34]
ALL_CAND = LEPTONS + QUARKS

def check(name, cond, detail=""):
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 72)
print("O137 Phase 1 v2: 拓撲諧振方程")
print("=" * 72)

# ============================================================
# 1. 模式 n 嘅 beat 能量 (Kähler/CPX 分開)
# ============================================================
print("\n[1] 模式 n 嘅 beat 能量結構")

E_K = np.zeros(Nd)  # Kähler (same-parity) beat energy
E_C = np.zeros(Nd)  # CPX (opposite-parity) beat energy
E_T = np.zeros(Nd)  # total
N_K = np.zeros(Nd)  # Kähler beat count
N_C = np.zeros(Nd)

for n in range(1, Nd+1):
    for m in range(1, Nd+1):
        if m == n:
            continue
        d = abs(omega[n-1] - omega[m-1])
        if (n + m) % 2 == 0:
            E_K[n-1] += d
            N_K[n-1] += 1
        else:
            E_C[n-1] += d
            N_C[n-1] += 1
    E_T[n-1] = E_K[n-1] + E_C[n-1]

print(f"{'n':>3} | {'ω_n':>8} | {'γ_n':>8} | {'E_K':>9} | {'E_C':>9} | {'E_T':>9} | {'E_K/ω':>8} | {'E_C/ω':>8}")
print("-" * 80)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"{n:3d}{marker} | {omega[n-1]:8.6f} | {gamma[n-1]:8.6f} | {E_K[n-1]:9.4f} | "
          f"{E_C[n-1]:9.4f} | {E_T[n-1]:9.4f} | {E_K[n-1]/omega[n-1]:8.3f} | {E_C[n-1]/omega[n-1]:8.3f}")

# ============================================================
# 2. 共振作用量 S_n(λ) = -γ_n + λ·E_K(n) 嘅極值掃描
# ============================================================
print("\n" + "=" * 72)
print("[2] 作用量 S_n(λ) = -γ_n + λ·E_K(n) — λ 掃描")
print("=" * 72)

# 對每個 λ, 找 S 嘅最小值 (穩定模式) / 最大值 (唔穩定)
# 檢查 1,7,20 係咪極值點
print(f"{'λ':>10} | {'argmin':>6} | {'argmax':>6} | {'n=1 係極值?':>12} | {'n=7':>5} | {'n=20':>6} | {'n=14':>5} | {'n=33':>5} | {'n=34':>5}")
print("-" * 80)
lambda_scan = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
for lam in lambda_scan:
    S = -gamma + lam * E_K
    argmin = np.argmin(S) + 1
    argmax = np.argmax(S) + 1
    # 極值檢查: 局部極值
    dS = np.gradient(S)
    ext_flags = []
    for n in ALL_CAND:
        is_ext = False
        if 1 < n < Nd:
            is_ext = (dS[n-2] * dS[n-1] <= 0)  # 斜率變號
        else:
            is_ext = True  # 邊界
        ext_flags.append("✓" if is_ext else "✗")
    print(f"{lam:10.4f} | {argmin:6d} | {argmax:6d} | {'✓':>12} | {ext_flags[1]:>5} | {ext_flags[2]:>6} | {ext_flags[3]:>5} | {ext_flags[4]:>5} | {ext_flags[5]:>5}")

# ============================================================
# 3. Z₂ 固定 beat 結構 (時間反演不變 = 駐波必要條件)
# ============================================================
print("\n" + "=" * 72)
print("[3] Z₂ 結構: 時間反演不變性")
print("=" * 72)

# 每個模式嘅 Z₂ 統計
fixed_per_mode = np.zeros(Nd)
nyquist_per_mode = np.zeros(Nd)
orbit_partner = {}  # n -> number of Z₂ orbit partners in its beats

for n in range(1, Nd+1):
    for m in range(1, Nd+1):
        if m == n:
            continue
        if n + m == 44:
            fixed_per_mode[n-1] += 1
        if n == 44 or m == 44:
            nyquist_per_mode[n-1] += 1

print(f"{'n':>3} | {'Z₂fixed':>7} | {'Nyquist':>7} | {'同parity beats':>14} | {'異parity beats':>14}")
print("-" * 55)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"{n:3d}{marker} | {int(fixed_per_mode[n-1]):7d} | {int(nyquist_per_mode[n-1]):7d} | "
          f"{int(N_K[n-1]):14d} | {int(N_C[n-1]):14d}")

# ============================================================
# 4. 固定 beat 頻率: Ω_n = ω_n + ω_{44-n} (粒子+反粒子)
# ============================================================
print("\n" + "=" * 72)
print("[4] 粒子-反粒子對頻率 Ω_n = ω_n + ω_{44−n}")
print("=" * 72)

Omega_pair = omega + omega[::-1]  # ω_n + ω_{44-n}
Delta_pair = np.abs(omega - omega[::-1])

print(f"{'n':>3} | {'ω_n':>8} | {'ω_{44−n}':>9} | {'Ω_n=ω_n+ω_{44−n}':>16} | {'Δ_n=|ω_n−ω_{44−n}|':>17} | {'Ω/γ':>7}")
print("-" * 75)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"{n:3d}{marker} | {omega[n-1]:8.6f} | {omega[44-n]:9.6f} | {Omega_pair[n-1]:16.6f} | "
          f"{Delta_pair[n-1]:17.6f} | {Omega_pair[n-1]/gamma[n-1]:7.3f}")

# Ω_n 嘅極值
dOmega = np.gradient(Omega_pair)
print(f"\n  Ω_n 極值: ", end="")
for n in range(2, Nd):
    if dOmega[n-2] * dOmega[n-1] <= 0:
        print(f"n={n} ({'max' if dOmega[n-1] < 0 else 'min'}), ", end="")
print()

# ============================================================
# 5. 諧振品質: Q_n = (模式能量)/(beat 能量密度)
# ============================================================
print("\n" + "=" * 72)
print("[5] 諧振品質因子")
print("=" * 72)

# Q1: 模式能量 vs Kähler beat 能量
Q1 = gamma / E_K
# Q2: 模式頻率 vs CPX beat 能量
Q2 = omega / E_C
# Q3: 模式能量 vs 總 beat 能量
Q3 = gamma / E_T
# Q4: Kähler/CPX 能量比
Q4 = E_K / E_C

print(f"{'n':>3} | {'Q1=γ/E_K':>9} | {'Q2=ω/E_C':>9} | {'Q3=γ/E_T':>9} | {'Q4=E_K/E_C':>9}")
print("-" * 50)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"{n:3d}{marker} | {Q1[n-1]:9.6f} | {Q2[n-1]:9.6f} | {Q3[n-1]:9.6f} | {Q4[n-1]:9.6f}")

# 極值檢查
for name, Q in [("Q1=γ/E_K", Q1), ("Q2=ω/E_C", Q2), ("Q3=γ/E_T", Q3), ("Q4=E_K/E_C", Q4)]:
    dQ = np.gradient(Q)
    extrema = []
    for n in range(2, Nd):
        if dQ[n-2] * dQ[n-1] <= 0:
            extrema.append(n)
    print(f"\n  {name} 極值點: {extrema}")
    # 輕子排名
    ranked = sorted([(n, Q[n-1]) for n in range(1, Nd+1)], key=lambda x: -x[1])
    ranks = {n: i+1 for i, (n, _) in enumerate(ranked)}
    print(f"  輕子排名: n=1→#{ranks[1]}, n=7→#{ranks[7]}, n=20→#{ranks[20]}, 夸克: n=14→#{ranks[14]}, n=33→#{ranks[33]}, n=34→#{ranks[34]}")

# ============================================================
# 6. 新共振模型: S_n = -ω_n + λ·(E_K·E_C)/E_T (幾何平均)
# ============================================================
print("\n" + "=" * 72)
print("[6] 作用量掃描: S_n = -γ_n + λ·sqrt(E_K·E_C)")
print("=" * 72)

E_geom = np.sqrt(E_K * E_C)
print(f"{'λ':>10} | {'argmin':>6} | {'argmax':>6} | 極值位置")
print("-" * 70)
for lam in [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]:
    S = -gamma + lam * E_geom
    dS = np.gradient(S)
    extrema = [n for n in range(2, Nd) if dS[n-2]*dS[n-1] <= 0]
    argmin = np.argmin(S) + 1
    argmax = np.argmax(S) + 1
    hits = [n for n in ALL_CAND if n in extrema]
    print(f"{lam:10.4f} | {argmin:6d} | {argmax:6d} | {extrema}  {'★' if hits else ''}")

# ============================================================
# 7. 本徵值流: d(ln γ)/dn 結構
# ============================================================
print("\n" + "=" * 72)
print("[7] 本徵值流 dγ/dn 與 d²γ/dn²")
print("=" * 72)

dgamma = np.gradient(gamma)
d2gamma = np.gradient(dgamma)
print(f"{'n':>3} | {'γ_n':>8} | {'dγ/dn':>8} | {'d²γ/dn²':>8} | {'ω_n·dγ/dn':>10} | {'γ_n/ω_n':>8}")
print("-" * 60)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    print(f"{n:3d}{marker} | {gamma[n-1]:8.6f} | {dgamma[n-1]:8.6f} | {d2gamma[n-1]:8.6f} | "
          f"{omega[n-1]*dgamma[n-1]:10.6f} | {gamma[n-1]/omega[n-1]:8.6f}")

# γ_n/ω_n = ω_n 本身 (因為 γ = ω²)! 檢查
check("γ_n/ω_n = ω_n (γ=ω²)", np.allclose(gamma/omega, omega))

# ============================================================
# 8. 綜合排名: 多測度
# ============================================================
print("\n" + "=" * 72)
print("[8] 多測度綜合排名")
print("=" * 72)

measures = {
    "E_K": E_K, "E_C": E_C, "E_T": E_T,
    "Q1=γ/E_K": Q1, "Q2=ω/E_C": Q2, "Q3=γ/E_T": Q3, "Q4=E_K/E_C": Q4,
    "Ω_pair": Omega_pair, "Δ_pair": Delta_pair,
}
print(f"{'n':>3} | " + " | ".join(f"{name:>8}" for name in measures))
print("-" * 120)
for n in range(1, Nd+1):
    marker = "★" if n in LEPTONS else ("☆" if n in QUARKS else "")
    vals = " | ".join(f"{measures[name][n-1]:8.4f}" for name in measures)
    print(f"{n:3d}{marker} | {vals}")

# 對每個測度: 輕子模式係咪 top-5?
print("\n  輕子/夸克喺每個測度嘅排名 (top-5 命中):")
for name in measures:
    ranked = sorted([(n, measures[name][n-1]) for n in range(1, Nd+1)], key=lambda x: -x[1])
    top5 = [n for n, _ in ranked[:5]]
    hits = [n for n in ALL_CAND if n in top5]
    ranks = {n: i+1 for i, (n, _) in enumerate(ranked)}
    rank_str = ", ".join(f"n={n}→#{ranks[n]}" for n in ALL_CAND)
    print(f"  {name:>10}: top5={top5}  {'★命中: '+str(hits) if hits else ''}  [{rank_str}]")

# ============================================================
# 9. 關鍵問題: 1,7,20 喺邊個測度下係極值?
# ============================================================
print("\n" + "=" * 72)
print("[9] 極值一致性檢查")
print("=" * 72)

for name in measures:
    Q = measures[name]
    dQ = np.gradient(Q)
    extrema = set()
    for n in range(2, Nd):
        if dQ[n-2] * dQ[n-1] <= 0:
            extrema.add(n)
    hits = [n for n in LEPTONS if n in extrema]
    print(f"  {name:>10}: 極值={sorted(extrema)}  {'★ 包含輕子: '+str(hits) if hits else '✗ 冇輕子'}")

# ============================================================
# 10. 保存
# ============================================================
results = {
    "test": "O137 Phase 1 v2: 共振譜",
    "leptons": LEPTONS, "quarks": QUARKS,
    "E_K": E_K.tolist(), "E_C": E_C.tolist(), "E_T": E_T.tolist(),
    "Omega_pair": Omega_pair.tolist(), "Delta_pair": Delta_pair.tolist(),
    "Q1": Q1.tolist(), "Q2": Q2.tolist(), "Q3": Q3.tolist(), "Q4": Q4.tolist(),
}
with open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/01_resonance_spectrum.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n結果已保存 data/01_resonance_spectrum.json")