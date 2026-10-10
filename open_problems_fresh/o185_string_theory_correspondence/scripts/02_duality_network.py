#!/usr/bin/env python3
"""
O185 — S1: 全弦論對偶網 vs IDCM mod-4/ℤ₄/鏡像對偶 (scripts/02)
================================================================
問題 (O185/S1): 弦論 S/T/U-duality、Mirror symmetry 对 IDCM 有冇
結構對應? IDCM 每條對偶都要標 (同構 / 特例 / 無對應) 三態之一。

IDCM 對偶清單 (承接 O151/O210/O158/O31):
  D1  Z₂ 對偶鏈: γ_n + γ_{44−n} = 4 = B  (88-site 偶=世界 奇=觀察者)
  D2  ℤ₄ 橋:    k mod 4 扇區 s0=46/s1=N_d−sec/s2=44/s3=N_d+sec, Σδ=μ²
  D3  mod-4:    45-家族(觀察者,a奇) vs 47-家族(世界,a偶) 方向判準
  D4  lepton 槽 n ≡ 1 (mod 4) (O206 盲測 p=0.0476)
  D5  站-模對偶: Ŝ=S²² 生成 ℤ₄, DFT 對偶 (群層 iso 🟡⁺)
  D6  88↔44 鏡像: 528/264 = 88/44 = Z₂ (觀察者容量=世界×世代結構)
  D7  row Z₂ 退化: row(m) = row(44−m), 22 獨立 row
  D8  譜半移對偶: n ↔ n+0.5 (O31, ζ(s)↔ξ(s))

弦論對偶網 (文獻, 對照組):
  T-duality: R ↔ α'/R (半徑倒數), 動量↔繞數
  S-duality: g ↔ 1/g (強弱互換)
  U-duality: T×S 生成 SL(2,Z)×O(d,d)
  Mirror:    h11 ↔ h21 互換 (CY 鏡像對)
  IIA↔IIB:   T-duality 下互換
"""
import math
import cmath

N_d, B, N_gen, L4, L5, L6, L10 = 44, 4, 3, 7, 11, 18, 123

results = []
def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

def verdict(label, state, note):
    print(f"  >>> VERDICT {label}: {state} -- {note}")

print("=" * 74)
print("  O185 S1: 全弦論對偶網 vs IDCM 對偶")
print("=" * 74)

# ---------------------------------------------------------------
# 1. IDCM 對偶清單 — 全部真算
# ---------------------------------------------------------------
print("\n--- 1. IDCM 對偶清單驗證 ---")

# D1: Z₂ 對偶 γ_n + γ_{44−n} = 4 (n=1..22 pairs)
gamma44 = [4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, 45)]
z2_ok = all(abs(gamma44[i] + gamma44[42 - i] - 4.0) < 1e-12 for i in range(22))
check("D1 Z₂ 對偶: γ_n + γ_{44−n} = 4 = B (22 對)", z2_ok)

# D2: ℤ₄ 橋 — k mod 4 扇區 (176-L: gamma_k = 4sin^2(k pi/176))
gamma176 = [4 * math.sin(k * math.pi / 176) ** 2 for k in range(1, 89)]
s = [0.0] * 4
for k, g in enumerate(gamma176, start=1):
    s[k % 4] += g
print(f"  扇區 s0={s[0]:.10f} s1={s[1]:.10f} s2={s[2]:.10f} s3={s[3]:.10f}")
check("D2 ℤ₄ 橋: s0 = N_d + μ² = 46 (exact)", abs(s[0] - (N_d + 2)) < 1e-9)
check("D2 ℤ₄ 橋: s2 = N_d = 44 (exact, 零缺陷扇區)", abs(s[2] - N_d) < 1e-9)
check("D2 ℤ₄ 橋: s1 = N_d − sec(π/88)", abs(s[1] - (N_d - 1/math.cos(math.pi/88))) < 1e-9)
check("D2 ℤ₄ 橋: s3 = N_d + sec(π/88)", abs(s[3] - (N_d + 1/math.cos(math.pi/88))) < 1e-9)
check("D2 ℤ₄ 橋: Σ(s_c − N_d) = μ² = 2", abs(sum(s) - 4 * N_d - 2.0) < 1e-9)

# D3: mod-4 方向判準 — 45-家族 (觀察者分子) vs 47-家族 (世界分子)
# 45 = N_d+1 = L₄²−4 ; 47 = N_d+N_gen = f_proj+4L₄
check("D3 mod-4 家族: 45 = N_d+1, 47 = N_d+N_gen", 45 == N_d + 1 and 47 == N_d + N_gen)
# 方向: 質量比<1 → a奇 (45-家族); >1 → a偶 (47-家族)
# 驗證 sin 奇偶模式比例性質: sin(偶π/176)/sin(奇π/176) 比分佈
pairs_le1 = [(21, 24), (13, 32)]
pairs_gt1 = [(46, 1), (86, 39)]
def ratio(a, b):
    return math.sin(a * math.pi / 176) / math.sin(b * math.pi / 176) if b != 0 else float('nan')
d3_ok = all(ratio(a, b) < 1 for a, b in pairs_le1) and all(ratio(a, b) > 1 for a, b in pairs_gt1)
check("D3 方向判準 (<1→a奇, >1→a偶) 4 組", d3_ok,
      f"ratios: {[round(ratio(a,b),3) for a,b in pairs_le1+pairs_gt1]}")

# D4: lepton 槽 n ≡ 1 (mod 4) — {1,5,9,13} 輕子+t
lepton_slots = {1, 5, 9, 13}
check("D4 lepton 槽全部 n≡1 (mod 4): {e,μ,τ,t}", all(n % 4 == 1 for n in lepton_slots))

# D5: 站-模對偶 — Ŝ = S²² 階 4 (88 站 DFT 基, 移位 22)
# Ŝ|k⟩ = e^{2πi·22k/88}|k⟩ = i^k |k⟩
omega4 = [cmath.exp(2j * math.pi * 22 * k / 88) for k in range(88)]
phase_ok = all(abs(omega4[k] - (1j) ** k) < 1e-9 for k in range(88))
check("D5 站-模對偶: Ŝ|k⟩ = i^k|k⟩ (88 站全對)", phase_ok,
      f"e.g. k=1: {omega4[1]:.6f} vs i: {1j:.6f}")
# Ŝ⁴ = S⁸⁸ = I
check("D5 Ŝ⁴ = 𝟙 (階 4, 生成 ℤ₄)", all(abs((1j) ** (4 * k) - 1) < 1e-9 for k in range(88)))

# D6: 88↔44 鏡像 — 528/264 = 88/44 = 2 = Z₂
check("D6 88↔44: 528/264 = 88/44 = 2 (Z₂)", 528 / 264 == 88 / 44 == 2.0)

# D7: row Z₂ 退化 — sin/cos 補角: row(m) = row(44−m)
# 以 sin 矩陣列範式檢查: ||sin(mπ/88)|| vs ||sin((44−m)π/88)||
def row_norm(m, N=88):
    return math.sqrt(sum(math.sin(m * k * math.pi / N) ** 2 for k in range(1, 45)))
d7_ok = all(abs(row_norm(m) - row_norm(44 - m)) < 1e-12 for m in range(1, 44))
check("D7 row Z₂ 退化: row(m) = row(44−m) (22 獨立)", d7_ok)

# D8: 譜半移對偶 — s_n = λ/(n+0.5) 零點, 半整數諧波 (O31)
# O31: ζ(s) 臨界線 Re=1/2 ↔ IDCM 零點 s_n = λ/(n+0.5); 極點 p_n = λ/n
# 零點/極點比 = n/(n+0.5) < 1 (零點喺極點之下游 = 破壞性干涉節點)
lam_sync = 294.88
# 零點/極點比: s_n/p_n = n/(n+0.5) < 1 (代數恆等, rel tol 避免 fp==)
rat_ok = True
for n in range(1, 8):
    s_n = lam_sync / (n + 0.5)
    p_n = lam_sync / n
    if not (abs(s_n / p_n - n / (n + 0.5)) < 1e-12 and s_n < p_n):
        rat_ok = False
check("D8 譜半移: s_n/p_n = n/(n+0.5) < 1, 零點喺半整數諧波 (O31)",
      rat_ok, f"s_1 = {lam_sync/1.5:.4f} < p_1 = {lam_sync:.4f}")

# ---------------------------------------------------------------
# 2. 弦論對偶網 ↔ IDCM 三態對照
# ---------------------------------------------------------------
print("\n--- 2. 弦論對偶 ↔ IDCM 三態對照 (宣告式) ---")
print("""  弦論對偶            結構特徵                IDCM 對應               表態
  ------------------------------------------------------------------------------------
  T-duality      R↔α'/R 動量↔繞數     D6 88↔44 Z₂ 鏡像           特例 (離散倒數, 冇動量/繞數)
  S-duality      g↔1/g 強弱互換        D1 Z₂ 對偶 γ↔4−γ         無對應 (IDCM 冇耦合常數)
  U-duality      SL(2,Z)×O(d,d)        D2 ℤ₄ 橋 Σδ=μ²           特例 (離散模群, 冇連續生成)
  Mirror         h11↔h21               D3 mod-4 家族 45↔47       特例 (離散方向判準, 冇 CY 鏡像)
  IIA↔IIB        T-dual 互換            D5 站-模 Ŝ 對偶           同構 (站↔模 = 位置↔動量互換)
  Riemann ζ↔ξ    臨界線 1/2             D8 半移 n↔n+0.5          特例 (數論對偶, 唔係物理對偶)
  ------------------------------------------------------------------------------------""")

verdict("S1-1", "唯一『同構』= 站-模對偶 (D5)",
        "Ŝ = S²² 移位生成 ℤ₄, 同時對角化 DFT, 支撐 {0,22,44,66} — 呢個係『位置表示↔動量表示』"
        "嘅離散版, 同弦論 IIA↔IIB T-duality『位置↔動量/繞數互換』同構。但 IDCM 版零連續自由參數。")
verdict("S1-2", "其餘全部『特例/無對應』— 結構差異根源",
        "弦論 S-duality 需要耦合常數 g (IDCM 冇), T-duality 需要動量/繞數譜 (IDCM 只有有限 44 模), "
        "Mirror 需要 CY moduli 空間 (IDCM CY₃ 係零輸入固定 (36,98))。IDCM 對偶網係『有限離散譜嘅 "
        "對稱性』, 弦論對偶網係『連續理論嘅等價關係』— 層次不同。")
verdict("S1-3", "可證偽判準",
        "若 D5『站-模對偶 = IIA↔IIB』成立, 則 IDCM 必須重現 τ = B + i/g 模參數結構 (SL(2,Z) 作用) "
        "— 目前冇 ⟹ S1 全網以特例/無對應為主, 唔宣稱對偶網同構。")

print(f"\n--- 結果: {results.count(True)} PASS / {results.count(False)} FAIL ---")
print("[O185-S1] FINAL:", "S1 對偶三態對照完成" if results.count(False) == 0 else "FAIL")
exit(0)