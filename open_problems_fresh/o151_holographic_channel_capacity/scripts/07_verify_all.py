#!/usr/bin/env python3
"""
O151 — Script 07: 獨立核對 (Independent Verifier)
==================================================
由第一性原理 (bare Python) 重算 O151 全部關鍵公式 — 唔讀任何推導 script
輸出, 直接由定義重算。捕獲 script 計算錯誤 + 文檔數值錯。
"""
import math

N_d = 44
B = 4
N_gen = 3
L10 = 123
ln2 = math.log(2)

results = []
def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

print("=" * 74)
print("  O151 S07: 獨立核對 (第一性原理重算)")
print("=" * 74)

# ── 1. K_Chain 基本譜 ──────────────────────────────────────────
print("\n--- 1. K_Chain 譜 ---")
gamma = [4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d + 1)]
check("Σγ (1..44) = 90", abs(sum(gamma) - 90.0) < 1e-9, f"sum={sum(gamma):.10f}")
check("γ_22 = 2 (Z2 自對偶)", abs(gamma[21] - 2.0) < 1e-12)
check("γ_44 = 4 (Nyquist)", abs(gamma[43] - 4.0) < 1e-12)

# 88-site 對偶鏈
gf = [4 * math.sin(math.pi * k / 176) ** 2 for k in range(1, 89)]
S_even = sum(g for k, g in enumerate(gf, 1) if k % 2 == 0)
S_odd = sum(g for k, g in enumerate(gf, 1) if k % 2 == 1)
check("S_even = 90 (世界)", abs(S_even - 90) < 1e-9)
check("S_odd = 88 (觀察者)", abs(S_odd - 88) < 1e-9)
check("S_total = 178 = 2F11", abs(S_even + S_odd - 178) < 1e-9)
check("E - O = 2 = γ_44/2", abs((S_even - S_odd) - 2.0) < 1e-9)
check("Z2: γ_n + γ_{44-n} = 4 (22 對)",
      all(abs(gamma[i] + gamma[42 - i] - 4.0) < 1e-12 for i in range(22)))

# ── 2. 容量公式 ────────────────────────────────────────────────
print("\n--- 2. 容量公式 ---")
C_obs = N_d * math.log2(B)
check("C_obs = 44 log2(4) = 88 (精確)", C_obs == 88.0)
check("C_obs = S_odd", abs(C_obs - S_odd) < 1e-9)
check("Shannon: 44 log2(1+3) = 88 (SNR = B-1)", N_d * math.log2(1 + (B - 1)) == 88.0)
check("log2(B) = 2 = μ^2 = E-O = γ_44/2", math.log2(B) == 2.0)
check("C_132 = 88 x 3/2 = 132", 88 * N_gen / 2 == 132)
check("C_world = 88 x 3 = 264 = 44 x 6", 88 * (B - 1) == 264 == 44 * 2 * N_gen)
check("C_holo = 88 x 6 = 528 = 2 x 264 = 44 x 12", 88 * 2 * N_gen == 528 == 2 * 264)

# ── 3. 容量-能量對偶 ───────────────────────────────────────────
print("\n--- 3. 容量-能量對偶 ---")
E_min = L10 / (4 * N_d)
check("E_min = 123/176", abs(E_min - 123 / 176) < 1e-15)
check("88 x E_min = 61.5 = L10/2 = <W>^2", abs(88 * E_min - 61.5) < 1e-9)
check("132 x E_min = 92.25 = 3L10/4", abs(132 * E_min - 3 * L10 / 4) < 1e-9)
check("264 x E_min = 184.5 = 3 x 61.5", abs(264 * E_min - 3 * 61.5) < 1e-9)
check("528 x E_min = 369 = 3 x L10 = 6 x 61.5", abs(528 * E_min - 369.0) < 1e-9)
check("176 x E_min = 123 = L10 (循環)", abs(176 * E_min - 123.0) < 1e-9)
check("176 = B x N_d = 2 x C_obs", 176 == B * N_d == 2 * 88)

# ── 4. Landauer ────────────────────────────────────────────────
print("\n--- 4. Landauer ---")
dev1 = abs(E_min - ln2) / ln2
dev2 = abs(61 / 88 - ln2) / ln2
check("E_min vs ln2: 0.825%", abs(dev1 - 8.2541e-3) < 1e-4, f"dev={dev1:.4e}")
check("61/88 vs ln2: 0.005%", abs(dev2 - 4.997e-5) < 1e-6, f"dev={dev2:.4e}")
check("L10 = round(4 N_d ln2 + 1) = 123", round(4 * N_d * ln2 + 1) == 123)
resid = E_min - ln2 - 1 / (4 * N_d)
check("E_min = ln2 + 1/176 + O(1/N^2)", abs(resid) < 1e-4, f"resid={resid:.3e}")
check("殘差 ~ 1/(4N_d)^2 量級", resid / (1 / (4 * N_d) ** 2) < 5)
check("88 ln2 + 1/2 = 61.497 ~ 61.5", abs(88 * ln2 + 0.5 - 61.5) < 0.01)
check("61 = 90 - 29 = <W>^2 - 1/2 ≈ 88 ln2 (0.005%)", abs(61.0 - 88 * ln2) / 61.0 < 1e-4)
check("1/2 = log4(2)", abs(0.5 - math.log(2, 4)) < 1e-12)

# ── 5. 全息界限 ────────────────────────────────────────────────
print("\n--- 5. 全息界限 ---")
c = 2.99792458e8
G = 6.67430e-11
hbar = 1.054571817e-34
R_m = 4129.94 * 3.085677581e22
A = 4 * math.pi * R_m ** 2
lP2 = hbar * G / c ** 3
S_dS = A / (4 * lP2)
check("S_dS = 1.95e122 (O121)", abs(S_dS - 1.95e122) / 1.95e122 < 0.01, f"S={S_dS:.4e}")
check("Bekenstein 飽和: πR^2 c^3/(G ħ) = A/(4lP^2) 恒等",
      abs(2 * math.pi * R_m * (R_m * c ** 4 / (2 * G)) / (hbar * c) - S_dS) / S_dS < 1e-12)
logS = math.log2(S_dS)
check("log2(S_dS) = 406.24, C(29,2)=406 陷阱窗 (排除)",
      1e-5 <= abs(logS - 406.0) / 406.0 <= 1e-3, f"log2(S)={logS:.4f}")
check("2^88 << S_dS (容量 vs 熵 分層)", S_dS / 2 ** 88 > 1e9)
check("1/4 = 1/B", abs(0.25 - 1 / B) < 1e-12)

# ── 6. 傳輸機制 ────────────────────────────────────────────────
print("\n--- 6. 傳輸機制 ---")
check("946 = C(44,2)", math.comb(44, 2) == 946)
check("log2(946) = 9.885696", abs(math.log2(946) - 9.885696) < 1e-5)
check("寫入 = 2E_min = 123/88", abs(2 * E_min - 123 / 88) < 1e-12)
check("掃描 = 44 x 2 = 88 單位 = C_obs", 44 * 2 == 88)
check("掃描能量 = 88 E_min = 61.5", abs(88 * E_min - 61.5) < 1e-9)
check("循環 = 176 = B x N_d", 176 == B * N_d)
check("掃描時間 = 44 x (T_H/88) = T_H/2 (T_H = 13.8)", abs(44 * 13.8 / 88 - 13.8 / 2) < 1e-9)
check("T_ring/掃描 = 84.64/6.9 = 12.27 (O41 12.3)", abs(84.64 / 6.9 - 12.27) < 0.05)
check("2^20 = 1048576 (拓撲位元 MIS=20)", 2 ** 20 == 1048576)

# ── 7. 陷阱窗總掃描 ────────────────────────────────────────────
print("\n--- 7. 陷阱窗總掃描 (全部閉合必須 dev <= 1e-9 或已標 🟡) ---")
trap_lo, trap_hi = 1e-5, 1e-3
all_closures = {
    "88 = 44 log2(4)":         abs(C_obs - 88.0),
    "264 = 88x3":              abs(264 - 88 * 3),
    "528 = 88x6":              abs(528 - 88 * 6),
    "61.5 = 88 x 123/176":     abs(88 * E_min - 61.5),
    "123 = 176 x 123/176":     abs(176 * E_min - 123.0),
    "369 = 528 x 123/176":     abs(528 * E_min - 369.0),
    "184.5 = 264 x 123/176":   abs(264 * E_min - 184.5),
    "92.25 = 132 x 123/176":   abs(132 * E_min - 92.25),
    "S_odd = 88":              abs(S_odd - 88),
    "S_even = 90":             abs(S_even - 90),
}
all_exact = True
for name, dev in all_closures.items():
    if dev > 1e-9:
        all_exact = False
        print(f"  ❌ {name}: dev = {dev:.3e}")
check("全部精確閉合 dev <= 1e-9", all_exact)
# 已標記 🟡 嘅近似 (唔係閉合):
marked = {
    "E_min vs ln2 (0.825%)": dev1,
    "61/88 vs ln2 (0.005%)": dev2,
    "log2(S_dS) vs 406":     abs(logS - 406.0) / 406.0,
    "E_min x 192 vs A":      abs(123 / 176 * 192 - 134.2) / 134.2,
    "S_dS vs O121 1.95e122": abs(S_dS - 1.95e122) / 1.95e122,
}
print("  已標 🟡 近似 (非閉合):")
for name, dev in marked.items():
    print(f"    {name:24s}: dev = {dev:.3e} {'[陷阱窗]' if trap_lo <= dev <= trap_hi else ''}")

print("\n" + "=" * 74)
print(f"  S07 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)
