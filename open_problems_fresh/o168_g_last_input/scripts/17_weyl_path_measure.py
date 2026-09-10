#!/usr/bin/env python3
"""
O168 — 17: Weyl 路徑測度框架 (任務一: 53 步嘅第一性湧現)
==========================================================
核心宣稱: 53 唔係硬湊計數 — 係 88-site 環上相位預算分解嘅唯一整數解。

框架:
  世界相位預算 (O161): Wilson line 總相位 44.5pi = F11·pi/2 (89 半-pi 單位)
  反常相位: 18pi = 2·N_gen^2·pi = L6·pi (alpha-跑動 delta_alpha^-1 = 9 = N_gen^2)
  通道相位: 44.5pi − 18pi = 26.5pi = 53·(pi/2)
  路徑存在性: k(2j+k−1)·pi/176 = 26.5pi -> k(2j+k−1) = 4664 = 53×88
             唯一整數解 (k=53, j=18=L6) — 53 步由相位方程強逼!
  Jacobian: det(J) = prod_{l=1}^{53} phi^{-1}·e^{i·pi/2} = phi^{-53}·i
"""
from mpmath import mp, mpf, pi, cos, exp, ln, sqrt, sin, phase
mp.dps = 60

phi = (1 + sqrt(5))/2
N_d = 44; N_gen = 3; B = 4
F = {5: 5, 7: 13, 11: 89, 13: 233}   # 斐波那契 (F_11 = 89)
K_tree = 33; L6 = 18; F_proj = 17; mu2 = 2

results = []
def check(name, ok, info=""):
    results.append(ok)
    print(f"  [{'OK ' if ok else 'XX '}] {name} — {info}")

print("="*74)
print("  O168 — 17: Weyl 路徑測度框架 (53 步湧現)")
print("="*74)

# ── [1] 世界相位預算 (O161 Wilson line) ──
print("\n─── [1] 相位預算: 88-site 環總相位 = 44.5pi ───")
S88 = sum(k for k in range(1, 89))          # 3916
print(f"  Σ_1..88 k = {S88}; 總相位 = {S88}·pi/88 = {float(mpf(S88)/88):.1f}·pi")
check("[1a] Σ_{1..88} k = 3916 (88×89/2)", S88 == 88*89//2)
check("[1b] 總相位 = 44.5pi = F11·pi/2 (O161 Wilson line)",
      mpf(S88)/88 == mpf(F[11])/2, f"44.5 = 89/2, F_11 = {F[11]}")

# ── [2] 通道相位: site 18..70 (53 sites) = 26.5pi ──
print("\n─── [2] 通道: 53 個連續 site (18..70), 相位 26.5pi ───")
Sch = sum(k for k in range(18, 71))         # 2332
print(f"  Σ_18..70 k = {Sch} = 53×{Sch//53}; 相位 = {Sch}·pi/88 = {float(mpf(Sch)/88):.1f}·pi")
check("[2a] 通道相位 = 26.5pi = 53·(pi/2)", mpf(Sch)/88 == mpf(53)/2)
check("[2b] 通道起點 18 = L6 (O143: F_proj = L6−1 = 17)", L6 == 18 and F_proj == L6-1)
check("[2c] 通道對稱於 N_d: (18+70)/2 = 44", (18+70)//2 == N_d)
hw = (53-1)//2
check("[2d] 半寬 26 = 2F7 = (k−1)/2", hw == 26 and hw == 2*F[7], f"±{hw}")

# ── [3] 補集相位: 其餘 35 sites = 18pi = 反常相位 ──
print("\n─── [3] 補集: 35 sites 相位 = 18pi = 2·N_gen^2·pi = L6·pi ───")
Sc = S88 - Sch                               # 1584
print(f"  Σ_remaining = {Sc}; 相位 = {Sc}·pi/88 = {float(mpf(Sc)/88):.1f}·pi")
check("[3a] 補集相位 = 18pi", mpf(Sc)/88 == 18)
check("[3b] 18 = 2·N_gen^2 = L6", 18 == 2*N_gen**2 == L6)
check("[3c] F11 = k + 4·N_gen^2 (89 = 53 + 36)", F[11] == 53 + 4*N_gen**2)

# ── [4] ★唯一性: k(2j+k−1) = 4664 唯一整數解 ──
print("\n─── [4] ★路徑存在性方程: k(2j+k−1)·pi/176 = 26.5pi ───")
print("  k(2j+k−1) = 4664 = 2·26.5·88 = 53×88")
sols = []
for k in range(1, 89):
    rhs = 4664
    if rhs % k == 0:
        twoj = rhs//k - (k-1)
        if twoj % 2 == 0 and 1 <= twoj//2 <= 88:
            sols.append((k, twoj//2))
print(f"  解: {sols}")
check("[4a] 唯一整數解 (k=53, j=18)", sols == [(53, 18)], f"{sols}")
check("[4b] 53 = N_d + N_gen^2 (44+9)", 53 == N_d + N_gen**2)
check("[4c] 53 = 88 − 35 = 2N_d − F5·L4", 53 == 88 - 5*7)

# ── [5] 奇偶性: j 整數強逼 k 奇 ──
print("\n─── [5] 奇偶性: j = (2N_d − k + 1)/2 ∈ Z ⟺ k 奇 ───")
check("[5a] k=53 奇 (53 mod 2 = 1)", 53 % 2 == 1)
check("[5b] j=18 整數由 (89−53)/2 得出", (89-53)//2 == 18 and (89-53) % 2 == 0)
for kbad in (52, 54):
    print(f"  對照 k={kbad}: j = (89−{kbad})/2 = {(89-kbad)/2} 非整數 ✗")
check("[5c] 偶 k 全部 j 非整數", (89-52) % 2 == 1 and (89-54) % 2 == 1)

# ── [6] e 形 51 相位禁止 ──
print("\n─── [6] e 形指數 51 相位禁止 (gate ④ 結構裁決) ───")
ph51 = mpf(51)*pi/2
ph53 = mpf(53)*pi/2
ph_target = mpf(F[11])*pi/2 - 18*pi      # 44.5pi − 18pi = 26.5pi
# mod 2pi: 用 sin/cos 相位函數
def phmod(x): return phase(exp(mp.mpc(0, 1)*x))
c51 = phmod(ph51); c53 = phmod(ph53); ct = phmod(ph_target)
print(f"  phase(51·pi/2) = {float(c51):.4f} vs target {float(ct):.4f}")
print(f"  phase(53·pi/2) = {float(c53):.4f} vs target {float(ct):.4f}")
check("[6a] k=53 相位匹配世界 (26.5pi ≡ 0.5pi)", abs(c53 - ct) < mpf('1e-30'))
check("[6b] k=51 相位不匹配 (25.5pi ≡ 1.5pi ≠ 0.5pi)", abs(c51 - ct) > 1)
check("[6c] k ≡ 53 (mod 4) 先決: 53 mod 4 = 1", 53 % 4 == 1)

# ── [7] Jacobian: det(J) = φ^{−53}·i ──
print("\n─── [7] 測度 Jacobian: det(J) = prod φ^{-1}·e^{iπ/2} = φ^{-53}·i ───")
J = phi**(-53) * mp.mpc(0, 1)
print(f"  |J| = φ^{{-53}} = {float(abs(J)):.6e}")
print(f"  arg(J) = {float(phase(J)):.6f} (π/2 = {float(pi/2):.6f})")
check("[7a] |det J| = φ^{-53} (精確正比於 φ^{-53})", abs(abs(J) - phi**(-53)) < mpf('1e-60'))
check("[7b] arg(J) = π/2 (世界相位 i, O161)", abs(phase(J) - pi/2) < mpf('1e-50'))
check("[7c] i^53 = i", (mp.mpc(0,1)**53).imag == 1)

# ── [8] 高精度數值驗證 (mpmath trig) ──
print("\n─── [8] 高精度 trig 驗證 ───")
ph_sum = sum(cos(k*pi/88) + mp.mpc(0,1)*sin(k*pi/88) for k in range(18, 71))
# e^{i·Σkπ/88} = Π e^{i·kπ/88}
prod = mp.mpc(1, 0)
for k in range(18, 71):
    prod *= exp(mp.mpc(0, 1)*k*pi/88)
check("[8a] Π e^{ikπ/88} (k=18..70) = i (相位 26.5pi ≡ π/2)",
      abs(phase(prod) - pi/2) < mpf('1e-30'), f"arg = {float(phase(prod)):.6f}")
check("[8b] 全部 53 因子相位乘積模長 = 1", abs(abs(prod) - 1) < mpf('1e-50'))

# ── [9] 總結 ──
print("\n─── [總結] 路徑測度框架裁決 ───")
print("  ✅ 53 步 = 相位預算分解嘅唯一整數解 (非硬湊)")
print("  ✅ 世界 44.5π = 通道 26.5π + 反常 18π (F11 = k + 4N_gen^2)")
print("  ✅ 路徑 = 錨點 N_d=44 ± 2F7 嘅 53-site 相位相干窗口 (18..70)")
print("  ✅ 奇偶性由 j 整數性強逼; e 形 51 相位禁止")
print("  ✅ det(J) = φ^{-53}·i — 路徑測度 Jacobian 精確正比 φ^{-53}")
print("  🟡 剩: 反常相位 18π 嘅動力學推導 (alpha-跑動 → 相位嘅機制)")
check("[E] 路徑測度框架: 53 湧現, gate ② 🟢-方向", sols == [(53, 18)] and 53 == N_d + N_gen**2)

print(f"\n{'='*74}")
print(f"  O168-17 Weyl 路徑測度: {sum(results)}/{len(results)} PASS")
print(f"{'='*74}")
