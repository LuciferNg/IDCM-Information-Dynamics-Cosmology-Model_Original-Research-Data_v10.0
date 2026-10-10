#!/usr/bin/env python3
"""
O48 Q2.1: 鋸齒結構試探性檢驗 — C_f 及其他難解形狀數列
=============================================================
調律者:「先試探性檢驗C_f 和其他有難解形狀的數值是否有可能存在同樣結構的鋸齒」

O48 已閉合嘅鋸齒簽名:
  A. 峰位 ℓ = 44N′ + s,  s ∈ 對合元集 {±1, ±21} = {1, 21, 23, 43} (mod 44)
  B. ΔN = 7 = L₄ 恆定 (N 平滑步進)
  C. Δs = −2/−20 交替 (相位跳動), |−2|+|−20| = 22 = N_d/2
  D. Δℓ = 306/288 交替 (44×7−2 / 44×7−20)

本探針對 C_f 及其他數列檢驗「同構鋸齒」可能性 (試探性, 非閉合):

候選數列:
  C_f (8 點, O206 docs/24): e=3.6, μ=15.5, τ=37, u=15.5, d=33, s=3.6, c=13, b=44
  Φ 目錄 (O137 φ=9 交叉值): 已知樣本 37, 28, 31...
  費米子質量 (PDG 9 點)
  γ_n 譜 (44 點, 4sin²(πn/88))
  峰高 A_m (O48, 7 點)
  對照: 相位偏移集 S = {−20,−17,−10,−8,−3,−2,+1} (已知 Fib∪Lucas 差)
  對照: 峰間距 {306, 288} (已知鋸齒)

鋸齒幾何簽名 (對每個數列):
  G1: 值 mod 44 ∈ 對合元 比例 (隨機 4/44 = 9.1%)
  G2: 值 mod 44 ∈ Fib∪Lucas 比例 (Fib∪Lucas mod44: {1,2,3,4,5,7,8,11,13,18,21,29,34,37,43?} → ~32%)
  G3: 相鄰差 mod 44 ∈ {±2, ±20} 比例 (鋸齒相位跳動)
  G4: 相鄰差 ∈ Fib∪Lucas 比例 (~30% 隨機)
  G5: 可否寫成 44k + s (s ∈ 對合元) — 「峰位型」表示
"""
import math, sys
from collections import Counter

# Fib/Lucas
phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
L = lambda n: int(round(phi**n + (-phi)**(-n)))
FIB = {F(k) for k in range(2, 13)}
LUC = {L(k) for k in range(1, 13)}
INVOL = {1, 21, 23, 43}
FIBLUC_MOD44 = {v % 44 for v in FIB | LUC}

def mod44(x):
    """將整數/浮點映射到 0..43 (浮點捨入)"""
    return int(round(x)) % 44

def saw_geoms(vals, name):
    """對一個數列輸出鋸齒幾何簽名"""
    print(f"\n{'─'*66}\n{name}  (n={len(vals)})\n{'─'*66}")
    ints = [mod44(v) for v in vals]
    g1 = sum(1 for m in ints if m in INVOL) / len(ints)
    g2 = sum(1 for m in ints if m in FIBLUC_MOD44) / len(ints)
    # 相鄰差
    diffs = [vals[i+1] - vals[i] for i in range(len(vals)-1)]
    d44 = [mod44(d) for d in diffs]
    g3 = sum(1 for m in d44 if m in {2, 42, 20, 24}) / len(d44)  # ±2, ±20 mod44
    g4 = sum(1 for m in d44 if m in FIBLUC_MOD44) / len(d44)
    g5 = sum(1 for v in vals if (v - mod44(v)) / 44 == round((v - mod44(v)) / 44) and mod44(v) in INVOL) / len(vals)
    print(f"  G1 值mod44∈對合元: {g1*100:.0f}% (隨機 9.1%)  mods={ints}")
    print(f"  G2 值mod44∈Fib∪Lucas: {g2*100:.0f}% (隨機 ~32%)")
    print(f"  G3 差mod44∈{{±2,±20}}: {g3*100:.0f}% (鋸齒相位跳動)  diffs={d44}")
    print(f"  G4 差mod44∈Fib∪Lucas: {g4*100:.0f}% (隨機 ~32%)")
    print(f"  G5 峰位型 44k+s: {g5*100:.0f}% (s∈{{1,21,23,43}})")
    return g1, g2, g3, g4, g5

print("="*66)
print("O48 Q2.1 — 鋸齒同構試探性檢驗")
print("="*66)

# ---------- 候選數列 ----------
# C_f (8 點)
CF = {"e": 3.6, "μ": 15.5, "τ": 37.0, "u": 15.5, "d": 33.0, "s": 3.6, "c": 13.0, "b": 44.0}
cf_vals = [CF[k] for k in ["e", "μ", "τ", "u", "d", "s", "c", "b"]]
cf_uniq = sorted(set(cf_vals))

# Φ 目錄 (已知值)
phi_vals = [37, 28, 31, 32, 33, 34, 36, 44, 47, 48, 50, 51, 64]  # 試探樣本

# 費米子質量 (MeV, PDG, O206 lib)
masses = [0.511, 2.16, 4.67, 93.4, 105.66, 1270.0, 1776.86, 4180.0, 172690.0]

# γ_n 譜 (n=1..44)
gamma_n = [4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 45)]

# 峰高 (O48 主公式 7 峰, 標準化)
# A(p_j) = 3ε(33/34)Π(F_k/F_k+1)exp[−(ℓ/ℓ_D)^{3/2}] — 用相對值即可
def peak_amplitudes():
    eps = phi**(-1)/4
    Fj_peak = {1: 1, 2: 5, 3: 18, 5: 25, 7: 32}  # N 值
    # telescoping Π(F_k/F_{k+1}) = 1/F_j (script 14)
    def tele(N):
        # Π_{k=1}^{N} F_k/F_{k+1} = F_1/F_{N+1} = 1/F_{N+1}
        return 1.0 / F(N+1)
    ell_D = 9055
    out = {}
    for m in [1, 2, 3, 5, 7]:
        Nm = Fj_peak[m]
        ell = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}[m]
        A = 3*eps*(33/34)*tele(Nm)*math.exp(-(ell/ell_D)**1.5)
        out[m] = A
    return out

A_m = peak_amplitudes()
a_vals = [A_m[m] for m in [1, 2, 3, 5, 7]]

# 對照: 相位偏移 S (已知 Fib∪Lucas)
S_ref = [-20, -17, -10, -8, -3, -2, 1]

# 對照: 峰間距 (已知鋸齒)
gaps_ref = [306, 288, 306, 288]

print("\n" + "="*66)
print("候選數列")
print("="*66)
print(f"  C_f 8 點: {cf_vals}")
print(f"  C_f 唯一值: {cf_uniq}")
print(f"  Φ 目錄樣本: {phi_vals}")
print(f"  費米子質量(MeV): {masses}")
print(f"  γ_n 首 8: {[round(g,3) for g in gamma_n[:8]]}...")

# ---------- 檢驗 ----------
print("\n" + "="*66)
print("鋸齒幾何簽名")
print("="*66)
res = {}
res["C_f (8)"] = saw_geoms(cf_vals, "C_f 形狀因素 (8 點)")
res["C_f 唯一 (6)"] = saw_geoms(cf_uniq, "C_f 唯一值 (6)")
res["Φ 目錄"] = saw_geoms(phi_vals, "Φ 目錄樣本 (13)")
res["費米子質量"] = saw_geoms([m for m in masses], "費米子質量 (9)")
res["γ_n 44"] = saw_geoms(gamma_n, "γ_n 譜 (44)")
res["峰高 A_m"] = saw_geoms([a*1e6 for a in a_vals], "峰高 A_m×1e6 (5)")
res["S 相位(對照)"] = saw_geoms(S_ref, "S 相位偏移 (對照, 已知 Fib 差)")
res["峰間距(對照)"] = saw_geoms(gaps_ref, "峰間距 (對照, 已知鋸齒)")

print("\n" + "="*66)
print("對照比較: C_f vs 已知鋸齒 (峰間距)")
print("="*66)
cf_g = res["C_f (8)"]
gap_g = res["峰間距(對照)"]
print(f"  G3 (±2±20 相位跳動): C_f={cf_g[2]*100:.0f}% vs 峰間距={gap_g[2]*100:.0f}%")
print(f"  G4 (FibLucas 差):   C_f={cf_g[3]*100:.0f}% vs 峰間距={gap_g[3]*100:.0f}%")
print(f"  G5 (44k+s 峰位型):  C_f={cf_g[4]*100:.0f}% vs 峰間距={gap_g[4]*100:.0f}%")

print("\n" + "="*66)
print("C_f 特徵觀察")
print("="*66)
print(f"  C_f 值結構: 44=N_d, 33=M, 37=44−L₄, 13=F₇, 15.5=(44−13)/2, 3.6=18/5")
print(f"  44×1+0=44(b), 44×0+33=33(d), 44×0+37=37(τ), 44×0+13=13(c)")
print(f"  ⭐ b 嘅 C_f = 44 = N_d — 鋸齒嘅『鏈週期』本身!")
print(f"  ⭐ τ 嘅 C_f = 37 = N_d − L₄ → 差 7 = L₄ = O48 ΔN!")
print(f"  ⭐ u/μ 嘅 C_f = 15.5 = (N_d−F₇)/2 = (44−13)/2")
print(f"  ⭐ e/s 嘅 C_f = 3.6 = 18/5, 18 = L₆")

print("\n" + "="*66)
print("SUMMARY: 試探性結論輸出 (exit 0 = 探針完成, 唔係 PASS/FAIL)")
print("="*66)
sys.exit(0)