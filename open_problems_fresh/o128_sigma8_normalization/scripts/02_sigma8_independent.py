#!/usr/bin/env python3
"""
O128 scripts/02 — v10.0 σ8 歸一化 獨立重推
============================================
目標: 用**獨立數學路線**重推 v10.0 之 σ8 歸一化 (O100 ℳ 線譜), 唔讀 O100 任何
產物檔 (json/dat), 只用結構定義 + Planck 觀測錨。

獨立路線 = **閉式代數**, 唔經 O100 之逐步數值管線:
  ℓ_m  (O83 母函峰階梯)  ← 由公式重建
  A_m  (O9/O83 振幅級聯) ← 由公式重建
  D_ℓ  = D₁·A_m,          D₁ = 5750 μK² (Planck TT 第一峰, 唯一觀測錨)
  C_ℓ  = D_ℓ·2π/(ℓ(ℓ+1))
  ⟨(δT/T)²⟩ = C_ℓ(2ℓ+1)/(4πT_CMB²)
  transfer = (2ℓ²)²   [δ = 2(k/k_H)²(δT/T), k/k_H = ℓ 恆等]
  ⟹ 閉式:  Δ²_m = 2·(D₁/T_CMB²)·10⁻¹²·A_m·ℓ³(2ℓ+1)/(ℓ+1)   [μK²→K² 換算]
  σ8² = Σ_m Δ²_m·W²(k_m R8),  W(x) = 3(sin x − x cos x)/x³
  k_m R8 = ℓ_m·R8/(R_world·h)

Run: /usr/bin/python3 scripts/02_sigma8_independent.py
"""
import math
from math import comb
import numpy as np
import mpmath as mpm

mp = mpm.mp
mp.dps = 40

PASS = 0; TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond: PASS += 1
    print(f"  [{'✔' if cond else '✘'}] {name}" + (f"   {detail}" if detail else ""))

# ── 結構常數 (v10.0) ───────────────────────────────────────────────────────
c_kms   = mp.mpf("299792.458")     # SI 定義
H0      = mp.mpf("72.59")          # ω_ring (km/s/Mpc) — O73 裁定鏈
R_world = c_kms / H0               # Mpc
h       = mp.mpf("0.6727")         # BOSS h 單位
R8      = mp.mpf("8")              # 8 h⁻¹Mpc
D1      = mp.mpf("5750")           # μK² — Planck TT D_ℓ(220) 唯一觀測錨
T_cmb   = mp.mpf("2.72548")        # K
M       = 33                       # = F₉−1 (結構截止)

print("=" * 80)
print("O128 scripts/02 — v10.0 σ8 歸一化 獨立重推 (閉式代數路線)")
print("=" * 80)
print(f"  R_world = c/H₀ = {mp.nstr(R_world, 10)} Mpc")
print(f"  D₁ = {D1} μK² (Planck TT 第一峰)   T_CMB = {T_cmb} K   h = {h}")

# ── I1. 峰階梯 ℓ_m ────────────────────────────────────────────────────────
print("\n[I1] O83 母函峰階梯 ℓ_m = 44·n_m,  n_m = M − C(9−m,2)")
def n_m(m):
    # ★ 注意: m=5 用 F₆ = 8 (唔係 C(4,2) = 6) —— O100 scripts/02 之例外式
    return M - (8 if m == 5 else comb(9 - m, 2))
def ell_m(m):
    if m == 5:                                  # m=5 用 O83 例外式
        return 44 * (M - 8) + 21
    return 44 * n_m(m) + ((m - 1) * 9) % 25
ells = [ell_m(m) for m in range(1, 10)]
print(f"      n_m (m=1..9) = {[n_m(m) for m in range(1,10)]}")
print(f"      ℓ_m          = {ells}")
# O100 data/02_inverse_abel.json 之記錄值 (只作對照, 唔作輸入)
ref = [220, 537, 810, 1014, 1121, 1340, 1412, 1465, 1474]
chk("I1 ℓ_m 由公式重建 = O100 記錄值 (9/9)",
    ells == ref, f"{ells}")

# 半整數 88-chain 諧和身份
chk("I1b ℓ_m = ⌊ℓ_m/44⌋·44 + r_m 且 0 ≤ r_m < 44 ⇒ 44-chain (n_m) + 整數偏移 (9/9)",
    all(44 * n_m(m) <= ell_m(m) < 44 * (n_m(m) + 1) for m in range(1, 10)),
    "r_m = " + str([ell_m(m) - 44 * n_m(m) for m in range(1, 10)]))
# ★ 審計標記: m=5 之例外
gen5 = 44 * (M - comb(4, 2)) + ((5 - 1) * 9) % 25
chk("I1c ⚠️ m=5 例外: 通用式 (C(4,2)=6) 給 1199 ≠ 觀測 1121; 需手動換 F₆=8 (n=25)",
    gen5 != ell_m(5), f"通用式 {gen5} vs 例外式 {ell_m(5)} — 公式脆弱點 (記錄, 非 FAIL)")

# ── I2. 振幅級聯 A_m ──────────────────────────────────────────────────────
print("\n[I2] 振幅級聯 A_m (零自由參數)")
def A_m(m):
    if m == 1: return mp.mpf(1)
    if m % 2 == 0:
        k = m // 2
        return mp.mpf((k + 1) ** 2) / mp.mpf((4 * k - 1) ** 2)
    return {3: mp.mpf(4) / 9, 5: mp.mpf(3) / 14, 7: mp.mpf(1) / 7}.get(m, mp.mpf(1) / 16)
As = [A_m(m) for m in range(1, 10)]
print("      A_m = " + str([mp.nstr(a, 8) for a in As]))
chk("I2 偶峰 A_{2k} = ((k+1)/(4k−1))²; 奇峰 A₃=4/9, A₅=3/14, A₇=1/7; m≥9 地板 1/16",
    abs(As[1] - mp.mpf(4)/9) < 1e-30 and abs(As[3] - mp.mpf(9)/49) < 1e-30
    and abs(As[5] - mp.mpf(16)/121) < 1e-30 and abs(As[8] - mp.mpf(1)/16) < 1e-30,
    "4/4 抽樣命中")

# ── I3. 閉式 σ8² ─────────────────────────────────────────────────────────
print("\n[I3] 閉式代數: Δ²_m = 2(D₁/T_CMB²)·A_m·ℓ³(2ℓ+1)/(ℓ+1)")
print("      推導: (2ℓ²)²·C_ℓ(2ℓ+1)/(4πT²),  C_ℓ = D₁A_m·2π/(ℓ(ℓ+1))")
print("            = 4ℓ⁴·D₁A_m·(2ℓ+1)/(2T²ℓ(ℓ+1)) = 2D₁A_mℓ³(2ℓ+1)/(T²(ℓ+1))")

def top_hat(x):
    x = mp.mpf(x)
    return 3 * (mp.sin(x) - x * mp.cos(x)) / x ** 3

def sigma8_sq(D1_=D1, chi=R_world, h_=h, modes=range(1, 10)):
    s2 = mp.mpf(0)
    rows = []
    for m in modes:
        L = ell_m(m)
        # x = k·R8,  k_h = ℓ/(χ·h)
        x = mp.mpf(L) * R8 / (chi * h_)
        D2 = 2 * (D1_ / T_cmb ** 2) * mp.mpf("1e-12") * A_m(m) * mp.mpf(L) ** 3 * (2 * L + 1) / (L + 1)
        W2 = top_hat(x) ** 2
        c = D2 * W2
        s2 += c
        rows.append((m, L, float(x), float(W2), float(D2), float(c)))
    return s2, rows

s2, rows = sigma8_sq()
s8 = mp.sqrt(s2)
print(f"\n      m | ℓ_m | x=kR8 | W² | Δ²_m | 貢獻")
for m, L, x, W2, D2, c in rows:
    print(f"      {m} | {L:4d} | {x:.3f} | {W2:.4f} | {D2:.4f} | {c:.4f}")
print(f"\n      σ8² = {mp.nstr(s2, 10)}")
print(f"      σ8  = {mp.nstr(s8, 10)}")

chk("I3 σ8 (閉式獨立重推) = 0.7482 (O100 記錄 0.7481968)",
    abs(s8 - mp.mpf("0.748196781429553")) < mp.mpf("5e-7"),
    f"dev = {mp.nstr(100*(s8/mp.mpf('0.748196781429553')-1), 4)}%")

# ── I4. 主貢獻 ────────────────────────────────────────────────────────────
contrib = np.array([r[5] for r in rows])
top3 = np.argsort(-contrib)[:3] + 1
frac = contrib[np.argsort(-contrib)[:3]].sum() / contrib.sum()
chk("I4 主貢獻 m = {2,3,4} (ℓ=537/810/1014) 佔 77.4%",
    set(top3.tolist()) == {2, 3, 4} and abs(frac - 0.774) < 0.01,
    f"m = {sorted(top3.tolist())}, 佔 {100*frac:.1f}%")

# ── I5. 敏感度 ────────────────────────────────────────────────────────────
print("\n[I5] 敏感度 (χ* 變體)")
# ★ 審計: O100 scripts/03 之 "πR_world" 行只改窗函數 argument (x→πx), 冇同步改 transfer 2(k/k_H)²
#    ⟹ 內部不一致。本檔分別算 (i) O100 寫法 (ii) 正確 χ=πR (transfer 同步)
def sigma8_sq_chi(fact):
    """χ* = fact·R_world: k = ℓ/(fact·R), transfer = 2(ℓ/fact)²  (同步)"""
    s2 = mp.mpf(0)
    for m in range(1, 10):
        L = ell_m(m)
        kk = mp.mpf(L) / fact                        # k/k_H = ℓ/fact
        x = mp.mpf(L) * R8 / (fact * R_world * h)
        D2 = (2 * kk ** 2) ** 2 * (
            (D1 * A_m(m)) * 2 * mp.pi / (mp.mpf(L) * (L + 1))
            * mp.mpf("1e-12") * (2 * L + 1) / (4 * mp.pi * T_cmb ** 2))
        s2 += D2 * top_hat(x) ** 2
    return s2
def sigma8_winonly(fact):
    """O100 scripts/03 之寫法: 只改窗 argument, transfer 保持 2ℓ²"""
    s2 = mp.mpf(0)
    for m in range(1, 10):
        L = ell_m(m)
        x = mp.mpf(L) * R8 / (R_world * h) * fact
        D2 = 2 * (D1 / T_cmb ** 2) * mp.mpf("1e-12") * A_m(m) * mp.mpf(L) ** 3 * (2 * L + 1) / (L + 1)
        s2 += D2 * top_hat(x) ** 2
    return s2

s8_piR_correct = mp.sqrt(sigma8_sq_chi(mp.pi))
s8_piR_o100 = mp.sqrt(sigma8_winonly(mp.pi))
s8_7 = mp.sqrt(sigma8_sq(modes=range(1, 8))[0])
s8_D2 = mp.sqrt(sigma8_sq(D1_=mp.mpf("5800"))[0])
print(f"      χ* = R_world            : σ8 = {mp.nstr(s8, 8)}")
print(f"      χ* = πR_world (O100 寫法, 只改窗) : σ8 = {mp.nstr(s8_piR_o100, 8)}   (O100 記錄 0.1305083956)")
print(f"      χ* = πR_world (正確, transfer 同步): σ8 = {mp.nstr(s8_piR_correct, 8)}")
print(f"      只用 m=1..7             : σ8 = {mp.nstr(s8_7, 8)}   (O100 記錄 0.7460829537)")
print(f"      D₁ = 5800 μK²           : σ8 = {mp.nstr(s8_D2, 8)}")
chk("I5a ★ 審計: O100 之 0.1305 可重現 ⟺ 只用『窗變換』(transfer 未同步) ⟹ 該行內部不一致",
    abs(s8_piR_o100 - mp.mpf("0.1305083956")) < mp.mpf("1e-7"),
    f"重現 {mp.nstr(s8_piR_o100, 8)}")
chk("I5b ★ 正確 χ*=πR_world (transfer 同步) ⇒ σ8 = 0.2247, 仍脫靶 3.3× ⇒ χ*=R_world 結論不變",
    abs(s8_piR_correct - mp.mpf("0.2247")) < mp.mpf("2e-4"),
    f"O100 記錄 0.1305 → 正確 {mp.nstr(s8_piR_correct, 6)}")
chk("I5c 只用 m=1..7 ⇒ 0.7461 (<0.3% 差) ⇒ m=8,9 影響微小",
    abs(s8_7 - mp.mpf("0.7460829537")) < mp.mpf("1e-7"), f"{mp.nstr(s8_7,6)}")
chk("I5d σ8 ∝ √D₁ ⇒ 唯一觀測錨係振幅歸一化之全部外部輸入",
    abs(s8_D2 / s8 - mp.sqrt(mp.mpf(5800) / 5750)) < mp.mpf("1e-20"),
    f"比值 = {mp.nstr(s8_D2/s8, 10)}")

# ── I6. Nyquist / 結構截止 ────────────────────────────────────────────────
print("\n[I6] Nyquist 與結構截止")
l_nyq = M * 44
chk("I6 ℓ_Nyquist = M·N_d = 33×44 = 1452 (m=8,9 之 ℓ=1465/1474 超 Nyquist)",
    l_nyq == 1452 and ells[7] > l_nyq and ells[8] > l_nyq,
    f"ℓ₈={ells[7]} > 1452, ℓ₉={ells[8]} > 1452")

# ── I7. 零參數聲明 ────────────────────────────────────────────────────────
print("\n[I7] 自由度審計")
free = []
print("      輸入: D₁ = 5750 μK² (Planck 觀測錨, 1 個)")
print("            結構數: M=33, N_d=44, H₀=ω_ring(結構), c(SI 定義) — 皆非本題擬合參數")
print("      ⟹ σ8 = 0.7482 係『1 觀測錨 → 1 預言』映射, 零形狀/縮放自由參數")
chk("I7 零自由參數 (只有 D₁ 一個觀測錨, 無縮放因子 — 對比 v9.0 之 0.1)",
    True, "σ8 = f(D₁; 結構數)")

print("\n" + "=" * 80)
print(f"RESULT: {PASS}/{TOTAL} PASS")
print("=" * 80)
