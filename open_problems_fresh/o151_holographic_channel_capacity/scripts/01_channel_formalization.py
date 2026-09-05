#!/usr/bin/env python3
"""
O151 — Script 01: 信道形式化 + Shannon 容量候選
=================================================
88-site 對偶鏈信道 (偶=世界輸入, 奇=觀察者輸出) + 容量公式候選掃描。

核心候選:
  D-A: C_obs = N_d * log2(B) = 44 * 2 = 88  (K_Tree 四元分支 = 每模態 2 bits)
  D-B: Shannon 形式 C = N_d * log2(1+SNR), SNR = B-1 = 3 -> log2(4) = 2
  D-C: C_world = 88 * (B-1) = 264; C_holo = 88 * 2N_gen = 528
  D-D: 階梯 88 -> 132 -> 264 -> 528 全部結構比率

所有 K_Chain 數字由定義重算: gamma_n = 4sin^2(pi n/88), n=1..44;
88-site 對偶鏈: gamma_full(k) = 4sin^2(pi k/176), k=1..88 (偶=世界, 奇=觀察者)。
"""
import math

N_d = 44
B = 4
N_gen = 3
L5 = 11   # Lucas 11
L10 = 123 # Lucas 123

results = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

print("=" * 74)
print("  O151 S01: 信道形式化 + Shannon 容量候選")
print("=" * 74)

# ---------------------------------------------------------------
# 1. K_Chain 44 模 (世界側單鏈)
# ---------------------------------------------------------------
gamma = [4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, N_d + 1)]
print("\n--- 1. K_Chain 基本量 ---")
print(f"  gamma_1  = {gamma[0]:.10f}  (4 sin^2(pi/88))")
print(f"  gamma_22 = {gamma[21]:.10f}  (Z2 自對偶)")
print(f"  gamma_44 = {gamma[43]:.10f}  (Nyquist)")
check("sum gamma (1..44) = 90 (世界側預算)", abs(sum(gamma) - 90.0) < 1e-9,
      f"sum = {sum(gamma):.10f}")

# ---------------------------------------------------------------
# 2. 88-site 對偶鏈: 偶 k (世界) / 奇 k (觀察者)
# ---------------------------------------------------------------
print("\n--- 2. 88-site 對偶鏈 (信道兩側) ---")
gamma_full = [4 * math.sin(math.pi * k / 176) ** 2 for k in range(1, 89)]
even_g = [g for k, g in enumerate(gamma_full, start=1) if k % 2 == 0]
odd_g  = [g for k, g in enumerate(gamma_full, start=1) if k % 2 == 1]
S_even = sum(even_g)
S_odd  = sum(odd_g)
S_all  = S_even + S_odd
print(f"  偶模 (世界)  : 44 個, sum = {S_even:.10f}")
print(f"  奇模 (觀察者): 44 個, sum = {S_odd:.10f}")
check("S_even = 90", abs(S_even - 90) < 1e-9)
check("S_odd = 88", abs(S_odd - 88) < 1e-9)
check("S_all = 178 = 2*F11", abs(S_all - 178) < 1e-9, f"S_all = {S_all:.10f}")
check("E - O = 2 = mu^2 = gamma_44/2 (Nyquist 自對偶)",
      abs((S_even - S_odd) - gamma[43] / 2) < 1e-9,
      f"E-O = {S_even - S_odd:.10f}, gamma_44/2 = {gamma[43]/2:.10f}")

# Z2 對偶: gamma_n + gamma_{44-n} = 4
print("\n--- Z2 對偶 gamma_n + gamma_{44-n} = 4 ---")
z2_ok = all(abs(gamma[i] + gamma[42 - i] - 4.0) < 1e-12 for i in range(22))  # pair n with 44-n
check("Z2 對偶 22 對全部 = 4 = B", z2_ok)

# ---------------------------------------------------------------
# 3. 容量候選 D-A: C = N_d * log2(B) = 88
# ---------------------------------------------------------------
print("\n--- 3. 容量候選 D-A: C_obs = N_d * log2(B) ---")
C_obs = N_d * math.log2(B)
print(f"  C_obs = {N_d} * log2({B}) = {N_d} * 2 = {C_obs}")
check("C_obs = 88 (精確)", C_obs == 88.0)
check("C_obs = S_odd (觀察者預算 = 容量)", abs(C_obs - S_odd) < 1e-9)
check("log2(B) = 2 = mu^2 = E - O", math.log2(B) == 2.0)

# ---------------------------------------------------------------
# 4. 容量候選 D-B: Shannon 形式 C = N_d * log2(1 + SNR), SNR = B-1
# ---------------------------------------------------------------
print("\n--- 4. Shannon 形式: C = N_d * log2(1 + SNR) ---")
snr_candidates = {
    "1 (unity)":       1,
    "2 (mu^2)":        2,
    "3 (B-1=SU(3)_C)": B - 1,
    "4 (B)":           B,
    "6 (2N_gen)":      2 * N_gen,
}
for name, snr in snr_candidates.items():
    c = N_d * math.log2(1 + snr)
    tag = "  <== 88 精確命中" if abs(c - 88.0) < 1e-12 else ""
    print(f"  SNR = {name:16s}: C = 44*log2(1+{snr}) = {c:.6f}{tag}")
check("SNR = B-1 = 3 係唯一結構候選命中 88 (log2(4)=2)",
      abs(N_d * math.log2(1 + (B - 1)) - 88.0) < 1e-12)
check("其他候選 (1,2,4,6) 全部唔命中 88",
      all(abs(N_d * math.log2(1 + s) - 88.0) > 1e-6
          for s in [1, 2, 4, 6]))

# SNR = 3 嘅結構身份: 1 + SNR = 4 = B; SNR = B - 1 = SU(3)_C (Pati-Salam)
print("\n  SNR 結構解讀: 1 + SNR = 4 = B (K_Tree 分支因子)")
print("                SNR = B - 1 = 3 = SU(3)_C (O68 Pati-Salam exact)")

# ---------------------------------------------------------------
# 5. 容量階梯 D-C/D-D: 88 -> 132 -> 264 -> 528
# ---------------------------------------------------------------
print("\n--- 5. 容量階梯 ---")
C_132 = S_odd * N_gen / 2
C_264 = S_odd * (B - 1)
C_528 = S_odd * 2 * N_gen
print(f"  C_obs   = S_odd * 1          = 88  (觀察者)")
print(f"  C_132   = S_odd * N_gen/Z2   = 88 * 3/2 = {C_132}")
print(f"  C_world = S_odd * (B-1)      = 88 * 3   = {C_264}  (世界)")
print(f"  C_holo  = S_odd * 2N_gen     = 88 * 6   = {C_528}  (全息)")
check("88 * 3/2 = 132", C_132 == 132.0)
check("88 * 3 = 264 = C_world", C_264 == 264.0)
check("88 * 6 = 528 = C_holo", C_528 == 528.0)
check("264 = N_d * 2N_gen = 44 * 6 (O107 身份)", 44 * 6 == 264.0)
check("528 = 2 * 264 (Z2)", C_528 == 2 * C_264)
check("528 = 264 * 2 = 132 * 4 = 88 * 6 (階梯全結構比率)",
      C_528 == C_132 * 4 == C_264 * 2 == C_obs * 6)

# 世界側容量另一讀法: C_world = N_d * log2(B) * (B-1) = 88 * 3
print(f"\n  世界側 = 觀察者容量 x 色數: {C_obs} x {B-1} = {C_obs*(B-1)}")
print(f"  全息側 = 觀察者容量 x 世代 x Z2: {C_obs} x {2*N_gen} = {C_obs*2*N_gen}")

# ---------------------------------------------------------------
# 6. 微態數: 2^C 對比
# ---------------------------------------------------------------
print("\n--- 6. 微態數解讀 ---")
print(f"  2^88  = {2**88:.3e}")
print(f"  2^264 = {2**264:.3e}")
print(f"  2^528 = {2**528:.3e}")
print(f"  (2^528 = 全息信道狀態數上限; 對比 S_dS = 1.95e122 -> S05)")

# ---------------------------------------------------------------
# 7. phi-陷阱窗掃描: 所有閉合必須係精確 (代數/浮點 <= 1e-9),
#    唔容許 (1e-5, 1e-3) 近似閉合
# ---------------------------------------------------------------
print("\n--- 7. 陷阱窗掃描 ---")
closures = {
    "C_obs = 44*log2(4)": abs(C_obs - 88.0) / 88.0,
    "C_obs = S_odd":      abs(C_obs - S_odd) / S_odd,
    "C_132":              abs(C_132 - 132.0) / 132.0,
    "C_264":              abs(C_264 - 264.0) / 264.0,
    "C_528":              abs(C_528 - 528.0) / 528.0,
    "E-O = 2":            abs((S_even - S_odd) - 2.0) / 2.0,
    "Z2 pair = 4":        max(abs(gamma[i] + gamma[42-i] - 4.0) / 4.0 for i in range(22)),
}
trap_lo, trap_hi = 1e-5, 1e-3
all_exact = True
for name, dev in closures.items():
    in_trap = trap_lo <= dev <= trap_hi
    flag = "  <== 陷阱窗! 排除" if in_trap else ""
    if dev > 1e-9:
        all_exact = False
    print(f"  {name:22s}: dev = {dev:.3e}{flag}")
check("全部閉合係精確 (dev <= 1e-9), 冇近似閉合", all_exact)

print("\n" + "=" * 74)
print(f"  S01 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)
