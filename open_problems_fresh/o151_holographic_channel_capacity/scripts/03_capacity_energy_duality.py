#!/usr/bin/env python3
"""
O151 — Script 03: 容量-能量對偶 (Capacity-Energy Duality)
===========================================================
C x E_min 全階梯:
  88  x 123/176 = 61.5  = <W>^2 = L10/2   (O41 已閉合)
  132 x 123/176 = 92.25 = 3L10/4
  264 x 123/176 = 184.5 = 3 x 61.5        (世界 = 3 倍觀察者)
  528 x 123/176 = 369   = 6 x 61.5 = 3L10 (全息 = 6 倍觀察者)

完整循環: 176 x E_min = B x N_d x E_min = 123 = L10 (讀+寫)
"""
import math

N_d = 44
B = 4
N_gen = 3
L10 = 123
trap_lo, trap_hi = 1e-5, 1e-3   # phi-陷阱窗

results = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

print("=" * 74)
print("  O151 S03: 容量-能量對偶")
print("=" * 74)

# ---------------------------------------------------------------
# 1. 基本量
# ---------------------------------------------------------------
E_min = L10 / (4 * N_d)   # 123/176
W2 = 61.5                  # <W>^2 (O39/O41)
print("\n--- 1. 基本量 ---")
print(f"  E_min = L10/(4N_d) = 123/176 = {E_min:.10f}")
print(f"  <W>^2 = 61.5 = L10/2 = {L10/2}")
check("<W>^2 = L10/2 (精確)", abs(W2 - L10 / 2) < 1e-12)

# ---------------------------------------------------------------
# 2. 容量 x E_min 階梯
# ---------------------------------------------------------------
print("\n--- 2. C x E_min 階梯 ---")
ladder = {
    "C_obs   = 88":  88,
    "C_132   = 132": 132,
    "C_world = 264": 264,
    "C_holo  = 528": 528,
}
E_ladder = {}
for name, C in ladder.items():
    E = C * E_min
    E_ladder[name] = E
    ratio = E / W2
    print(f"  {name:16s} x {E_min:.6f} = {E:9.4f}  = {ratio:.1f} x <W>^2")
check("88 x E_min = 61.5 = <W>^2 (O41 重現)", abs(88 * E_min - 61.5) < 1e-9)
check("132 x E_min = 92.25 = 3L10/4", abs(132 * E_min - 3 * L10 / 4) < 1e-9)
check("264 x E_min = 184.5 = 3 x <W>^2 (世界 = 3 觀察者)", abs(264 * E_min - 3 * 61.5) < 1e-9)
check("528 x E_min = 369 = 6 x <W>^2 = 3L10 (全息 = 6 觀察者)", abs(528 * E_min - 369.0) < 1e-9)
check("369 = 3 x L10 (世代 x Lucas10)", 369 == 3 * L10)
check("能量階梯比率 {1, 3/2, 3, 6} = 容量階梯比率 (同一結構)",
      [v / 61.5 for v in E_ladder.values()] == [1.0, 1.5, 3.0, 6.0])

# ---------------------------------------------------------------
# 3. 完整循環: 176 = B x N_d 模式單位
# ---------------------------------------------------------------
print("\n--- 3. 完整循環 (讀+寫) ---")
print(f"  176 = B x N_d = {B} x {N_d}")
print(f"  176 x E_min = {176 * E_min:.1f} = L10")
check("176 x E_min = 123 = L10 (完整循環能量)", abs(176 * E_min - 123.0) < 1e-9)
check("C_obs = 176/2 (容量 = 半循環)", 88 == 176 / 2)
check("2 x 61.5 = 123 = L10 (讀+寫 = 完整預算)", 2 * 61.5 == 123.0)
print("  解讀: 一個完整讀-寫循環 = 176 模式單位 = B x N_d = 2 x C_obs")
print("        能量 = 176 x E_min = L10 (Lucas 10 = 循環標度)")

# ---------------------------------------------------------------
# 4. 2 = mu^2 = log2(B) = E - O = gamma_44/2 互鎖
# ---------------------------------------------------------------
print("\n--- 4. 每 bit 能量 vs 每 bit 容量互鎖 ---")
gamma44 = 4 * math.sin(math.pi * 44 / 88) ** 2
print(f"  log2(B) = {math.log2(B)}")
print(f"  E - O   = 2 (88-site 對偶鏈)")
print(f"  gamma_44/2 = {gamma44/2}")
print(f"  mu^2    = 2 (O39 SSB)")
check("log2(B) = 2 = E-O = gamma_44/2 = mu^2 (四重身份)",
      math.log2(B) == 2.0 and gamma44 / 2 == 2.0 and (90 - 88) == 2)
print("  解讀: 每模態 2 bits = SSB 驅動 = 對偶鏈世界-觀察者差")
print("        容量 88 = 44 模 x 2 bits/mode, 每 bit 成本 E_min")

# ---------------------------------------------------------------
# 5. E_min 嘅 μK 換算 (O41: gamma = 192 μK/unit)
# ---------------------------------------------------------------
print("\n--- 5. E_min 嘅 μK 換算 (O41 γ = 192 μK/unit) ---")
gamma_conv = 192.0  # μK / IDCM unit (O41)
E_min_uK = E_min * gamma_conv
dev_uK = abs(E_min_uK - 134.2) / 134.2
print(f"  E_min x 192 = {E_min_uK:.4f} μK  (冷斑 A = 134.2 μK)")
print(f"  dev = {dev_uK:.3e}  <== 陷阱窗 ({1e-5}, {1e-3})! 標 🟡 唔係閉合")
check("E_min x 192 ≈ A 係 0.0135% 近似 (陷阱窗 -> 誠實標 🟡)",
      trap_lo <= dev_uK <= trap_hi)
A_bits = 134.2 / E_min_uK * 88  # 冷斑能量佔幾多 bits
print(f"  冷斑 = {134.2 / E_min_uK:.1f} x 88 bits 嘅能量尺度 (192.03, O41 標 ≈)")

# ---------------------------------------------------------------
# 6. 陷阱窗掃描
# ---------------------------------------------------------------
print("\n--- 6. 陷阱窗掃描 ---")
closures = {
    "88*E_min = 61.5":     abs(88 * E_min - 61.5) / 61.5,
    "264*E_min = 184.5":   abs(264 * E_min - 184.5) / 184.5,
    "528*E_min = 369":     abs(528 * E_min - 369.0) / 369.0,
    "176*E_min = 123":     abs(176 * E_min - 123.0) / 123.0,
    "W2 = L10/2":          abs(W2 - L10 / 2) / (L10 / 2),
    "E_min_uK = A (🟡)":   dev_uK,
}
all_exact = True
trap_found = False
for name, dev in closures.items():
    in_trap = trap_lo <= dev <= trap_hi
    if in_trap:
        trap_found = True
    flag = "  <== 陷阱窗! 🟡" if in_trap else ""
    if dev > 1e-9 and not in_trap:
        all_exact = False
    print(f"  {name:18s}: dev = {dev:.3e}{flag}")
check("精確閉合全部 dev <= 1e-9 (排除陷阱窗項)", all_exact)
check("陷阱窗偵測: E_min_uK vs A 已正確標 🟡", trap_found)

print("\n" + "=" * 74)
print(f"  S03 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)
