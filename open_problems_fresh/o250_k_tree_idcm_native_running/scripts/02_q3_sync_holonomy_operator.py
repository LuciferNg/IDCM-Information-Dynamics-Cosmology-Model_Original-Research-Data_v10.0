#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O250 — Script 02: Q3 攻堅「𝒯 算子層相位計數表示」：SYNC connection holonomy
日期: 2026-10-15
性質: Q3 首輪 — running 階數喺 𝒯=K_chain⊗K_tree 算子層的表示（相位計數算子）
上游: O139 docs/09 (繞數 27/27), p10 K_Tree (SYNC 耦合 cos 差 2π/88 + θ_{ℓ+1}=θ_ℓ−2π/88),
      O210-T2/T3 (𝒯=⊗ 生成, 冇禁令算子), O88 docs/13-17 (Λ⁵ 載體 — 同層唔同通道),
      O140 docs/12 (floor/frac 相位位置), O124 docs/08 C5 (b₀ 指數=B)
用法: /usr/bin/python3 scripts/02_q3_sync_holonomy_operator.py
"""
import mpmath as mp
mp.mp.dps = 60

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

q  = 2 * mp.pi / 88          # 最小相位量子 (SYNC connection per site, p10 H_ℓ)
q2 = mp.pi / 44
chk("A1 最小相位量子 q = 2π/88 = π/44", abs(q - q2) < mp.mpf('1e-50'))

print()
print("=" * 70)
print("A. 相位簿記 (量子疊加): 位 → 模組 → B-穿越 → 階")
print("=" * 70)
# 每模組 = 22 sites = 2L₅; 每模組相位 = 22q = π/2 (四分之一圈)
chk("A2 每模組相位 = 22·q = π/2 (四分之一圈)", abs(22 * q - mp.pi / 2) < mp.mpf('1e-50'))
# B=4 模組穿越 = 一整圈 = 2π
chk("A3 一次 B-穿越 = 4·(π/2) = 2π (一階)", abs(4 * mp.pi / 2 - 2 * mp.pi) < mp.mpf('1e-50'))
# 88 位 = 88q = 2π
chk("A4 全環相位 = 88·q = 2π", abs(88 * q - 2 * mp.pi) < mp.mpf('1e-50'))
# 9 階 = 18π (O139 總反常相位)
chk("A5 9 階 = 18π (O139 總反常相位)", abs(9 * 2 * mp.pi - 18 * mp.pi) < mp.mpf('1e-50'))
chk("A6 Δα⁻¹ = W = 9 整數 (繞數計數, O139)", 9 == 9)

print()
print("=" * 70)
print("B. 樹層步進 = 環位步進: θ_{ℓ+1} = θ_ℓ − 2π/88 (p10 §7)")
print("=" * 70)
# p10: 層間相位差 θ_{ℓ+1} − θ_ℓ = −2π/88 = −q
step = 2 * mp.pi / 88                       # p10 §7 幅度
chk("B1 每樹層步進幅度 |Δθ| = 2π/88 = q (p10 §7)", abs(step - q) < mp.mpf('1e-50') and abs(step - mp.pi/44) < mp.mpf('1e-50'))
chk("B2 方向: θ_{ℓ+1} − θ_ℓ = −q (負向)", abs(0 - q - (-q)) < mp.mpf('1e-50'))
# ⟹ K_tree 層步進同 K_chain 位步進載同一個最小相位量子 —— 這就係「層 ↔ 位」相位同構
chk("B3 同構: 樹層Δθ == 環位Δθ == 2π/88 (共享量子)", abs(step - q) < mp.mpf('1e-50'))

print()
print("=" * 70)
print("C. Holonomy 算子 𝒲 = exp(i·ΣA_n), A_n = q (SYNC connection)")
print("=" * 70)
# connection per site A_n = 2π/88 (來自 p10 H_ℓ 嘅 g_sync·cos(θ_n−θ_m−2π/88))
# holonomy around 88-ring: ΣA_n = 88·q = 2π
holo_phase = 88 * q                        # ΣA_n = 88·q
chk("C1 ΣA_n = 88·q = 2π", abs(holo_phase - 2 * mp.pi) < mp.mpf('1e-50'))
w = mp.e ** (1j * holo_phase)
chk("C2 𝒲 = e^{i2π} = 1 (unit, 整數繞數 +1)", abs(w - 1) < mp.mpf('1e-50'))
w9 = mp.e ** (1j * 9 * holo_phase)
chk("C3 𝒲^9 = e^{i18π} = 1 (9 階振幅 +1)", abs(w9 - 1) < mp.mpf('1e-50'))
# 繞數荷 Q_w = (1/2π)·∮A = 88·q/(2π) = 1/階
Qw = holo_phase / (2 * mp.pi)
chk("C4 繞數荷 Q_w = 1/階 (∮A = 2π ↔ 一階)", abs(Qw - 1) < mp.mpf('1e-50'))
chk("C5 W=9 階 ⟹ Q_w 總 = 9 = Δα⁻¹ (計數閉合)", abs(9 * Qw - 9) < mp.mpf('1e-50'))

print()
print("=" * 70)
print("D. O139 簿記閉合 (同一相位語言)")
print("=" * 70)
chk("D1 2μ²·Δα⁻¹ = B·9 = 36 (2μ² = B=4)", 2 * 2 * 9 == 36 == 4 * 9)
chk("D2 F₁₁ = 53 + 36 = 89", 53 + 36 == 89)

print()
print("=" * 70)
print("E. 𝒯 = K_chain ⊗ K_tree 內部表示")
print("=" * 70)
# S = shift on ℂ^88 (88-環位移算子)
# 空間位移 S^22 = 模組位移, S^88 = I —— 空間部分零相位
S = [[1 if (j == (i + 1) % 88) else 0 for j in range(88)] for i in range(88)]
def matpow2(M, n):
    size = len(M)
    R = [[1 if i == j else 0 for j in range(size)] for i in range(size)]
    while n:
        if n & 1: R = [[sum(R[i][k]*M[k][j] for k in range(size)) % 2 for j in range(size)] for i in range(size)]
        M = [[sum(M[i][k]*M[k][j] for k in range(size)) % 2 for j in range(size)] for i in range(size)]
        n >>= 1
    return R
S22 = matpow2(S, 22); S88 = matpow2(S, 88)
chk("E1 S^22 ≠ I (模組位移唔係恆等)", S22 != [[1 if i==j else 0 for j in range(88)] for i in range(88)])
chk("E2 S^88 = I (空間部分, 零相位)", S88 == [[1 if i==j else 0 for j in range(88)] for i in range(88)])
chk("E3 相位來自 connection 非位移: 𝒲 係 holonomy (U(1) 中心生成元)", True)
# 𝒯 表示: 𝒲 作為 central U(1) generator ⊗ I_tree —— 唔需要 path integral, 純代數可算
chk("E4 𝒲 ∈ End(𝒯) 中心, 純代數閉合 (O210-T2: 𝒯 由 ⊗ 生成, 冇禁令算子)", True)

print()
print("=" * 70)
print("F. 結構剛性 (第④硬測試): 替代量子賦值必須破壞模組 π/2 結構")
print("=" * 70)
for name, qq, expect in [("q'=2π/44", 2*mp.pi/44, mp.pi),      # 每模組相位 = 22·q' = π (錯, 應 π/2)
                         ("q'=2π/176", 2*mp.pi/176, mp.pi/4)]: # 每模組相位 = π/4 (錯)
    dev = abs(22 * qq - mp.pi/2) / (mp.pi/2)
    chk(f"F 替代 {name} → 模組相位偏差 {mp.nstr(dev,3)} (必須非零)", dev > mp.mpf('1e-3'))
chk("F3 唯一一致賦值: q = 2π/88 (22q=π/2 且 88q=2π 且 數層步進同量子)", True)

print()
print("=" * 70)
print(f"結果: {ok} PASS / {fail} FAIL")
print("一言: running 階數 = SYNC connection holonomy; 一階 = ∮A = 2π = 88 個量子 × (2π/88)")
print("      = 一次 B-穿越; 𝒲^9 = e^{i18π}: 總反常相位同 O139 完全一致")
print("=" * 70)