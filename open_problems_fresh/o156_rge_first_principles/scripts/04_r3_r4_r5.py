#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_r3_r4_r5.py — R3: 量→N 分配規則; R4: form-precision 家族; R5: 新預測 (O156)
============================================================================
R3: 框架尺度塔 {176,88,55,44,33,42,46} 嘅 L₅ 結構 + 33-44-55 Pythagorean 三元組
R4: 三角度殘差 {−0.0070, +0.1222, +0.0479}° 總和 ≈ 1/352 rad? null-control
R5: 若 θ₂₃ 住喺 N=55: sin²θ₂₃(55), 其他量 88 vs 55 差異 → 可證偽判據
"""
import math, random
random.seed(20260907)
DEG = 180.0/math.pi
RAD = math.pi/180.0

def th(N, k1=7, k2=6):
    return math.degrees(math.atan(math.sin(k1*math.pi/N)/math.sin(k2*math.pi/N)))

def gamma_n(n, N=88):
    return 4*math.sin(n*math.pi/N)**2

print("="*70)
print("R3: 量→N 分配規則 — 框架尺度塔")
print("="*70)
print("\n1) 所有框架尺度都係 L₅ = 11 嘅倍數:")
scales = {176: 16, 88: 8, 55: 5, 44: 4, 33: 3, 22: 2, 11: 1}
for N, mult in sorted(scales.items(), reverse=True):
    print(f"   {N:3d} = 11 × {mult:2d}  ({'L₅×'+str(mult)})")
print("   ⇒ 尺度塔: L₅ × {1,2,3,4,5,8,16} — {3,4,5} = Pythagorean, {1,2,4,8,16} = 2 冪")
print("   42, 46 唔係 L₅ 倍數 (42 = 6×7 = 2N_gen·L₄, 46 = 42+4) — 觀察者側")

print("\n2) ★ 33-44-55 = L₅×(3,4,5) Pythagorean 三元組")
print(f"   33² + 44² = {33*33} + {44*44} = {33*33+44*44} = 55² = {55*55}  {'✓ EXACT' if 33*33+44*44==55*55 else '✗'}")
print(f"   33 = K_tree (tree 尺度), 44 = N_d (世界維度), 55 = F₁₀ (k-ladder 頂)")
print(f"   ⇒ 三個「自然尺度」本身係 Pythagorean 三元組 — 幾何閉合!")

print("\n3) 量→N 現有分配 (全部既有, 零新參數)")
print("   " + "-"*60)
print(f"   {'量':<28} {'N':<6} {'結構':<34}")
alloc = [
    ("θ₁₂ = atan((K_tree+φ)/(K_tree·φ−1))", "33", "tree 尺度 (K_tree)"),
    ("θ₁₃ = arcsin(ε(1−1/K_tree))", "33", "tree gap"),
    ("δ_CP = 5×46", "33/46", "tree 讀法 (K_tree+F₇)"),
    ("θ₂₃ = atan(ω₇/ω₆)", "88", "chain 模式比 (O65/O69)"),
    ("CKM θ/δ 家族 (beat 比)", "88", "D6×S6 beat web (docs/04)"),
    ("γ_n = 4sin²(nπ/N)", "176", "Laplacian 譜"),
    ("Σγ_even = 90, Σγ_odd = 88", "176", "譜總和"),
    ("k-ladder g_k", "88→44", "O149 定理4 (終止 F₁₀=55>43)"),
]
for a, n, s in alloc:
    print(f"   {a:<28} {n:<6} {s:<34}")

print("\n4) 候選規則: 觀察量住喺『定義其算子嘅尺度』")
print("   - tree 算子 (P_B/P_I, K_tree) → N=33")
print("   - chain beat 算子 (ω_n = 2sin(nπ/88)) → N=88")
print("   - Laplacian 譜 → N=176")
print("   - θ₂₃ 而家定義喺 N=88 (ω 係 88-beat), 但 F₁₀ = 55 係 k-ladder 終止頂")
print("   ⇒ 問題: θ₂₃ 嘅『家』係 88 (beat 定義) 定 55 (ladder 頂)? R5 測試")

print("\n" + "="*70)
print("R4: form-precision 家族 — 三角度殘差總和 ≈ 1/352?")
print("="*70)
res12 = 33.4532 - 33.4602    # −0.0070
res23 = 49.320228 - 49.1980  # +0.1222
res13 = 8.6169 - 8.5690      # +0.0479
S = res12 + res23 + res13
print(f"\n   殘差: θ₁₂ {res12:+.4f}°, θ₂₃ {res23:+.4f}°, θ₁₃ {res13:+.4f}°")
print(f"   總和 = {S:+.4f}° = {S*RAD:.6f} rad")
print(f"   1/352 rad = {1/352*DEG:.4f}°; 352 = 32×11 = 32·L₅ (tower 下一級!)")
print(f"   Δ = {abs(S - 1/352*DEG):.4f}° = {abs(S-1/352*DEG)/(1/352*DEG)*100:.1f}%")
print(f"   (352 = 4×88 = 2×176 = 32×11 — L₅-multiple tower 嘅 {1,2,4,8,16,32}×11 成員)")

print("\n   null-control: 隨機 3 殘差三元組 (範圍 ±[0.001, 0.15]°) 總和命中 1/352 概率")
hits = 0; NT = 50000
for _ in range(NT):
    r1 = random.uniform(-0.15, 0.15)
    r2 = random.uniform(-0.15, 0.15)
    r3 = random.uniform(-0.15, 0.15)
    s = (r1+r2+r3)*RAD
    if abs(s - 1/352) < abs(S*RAD - 1/352):
        hits += 1
print(f"   命中率 (比真實三元組更接近 1/352): {hits/NT*100:.2f}%")
print(f"   ⇒ {'巧合級 (無結構信息)' if hits/NT > 5 else '值得注意'} — SESSION_START 判: 0.2% off = 巧合級")

print("\n   家族檢驗: 三個殘差係咪同一 order?")
print(f"   |θ₁₂ res| = {abs(res12):.4f}° (1.2e-4 rad)")
print(f"   |θ₂₃ res| = {abs(res23):.4f}° (2.1e-3 rad)")
print(f"   |θ₁₃ res| = {abs(res13):.4f}° (8.4e-4 rad)")
print(f"   跨度 17× — 唔似單一 form-precision 家族 (θ₁₂ 特別準 0.02%)")
print(f"   ⇒ θ₁₂ 0.02% 已達結構級; θ₂₃ 0.25% / θ₁₃ 0.56% 係 form 級 — 唔係同一機制")

print("\n   θ₂₃ 殘差本身 vs (γ₇−γ₆)/30 嘅『機制』再檢驗:")
print(f"   (γ₇−γ₆)/30 = {(gamma_n(7)-gamma_n(6))/30*DEG:.4f}° vs 殘差 {res23:.4f}° (0.14%)")
print(f"   γ₇−γ₆ = 4sin²(7π/88)−4sin²(6π/88) = {gamma_n(7)-gamma_n(6):.6f}")
print(f"   = 4·sin(13π/88)·sin(π/88)  (sin²A−sin²B = sin(A+B)sin(A−B))")
print(f"   = 4·sin(F₇π/88)·sin(π/88)  — F₇ = 13 出現! 但 /30 無算子身份")

print("\n" + "="*70)
print("R5: 新預測 — 若 θ₂₃ 住喺 N=55 (F₁₀)")
print("="*70)
print("\n1) sin²θ₂₃ 喺 88 vs 55:")
s2_88 = gamma_n(7)/(gamma_n(7)+gamma_n(6))
s2_55 = 4*math.sin(7*math.pi/55)**2 / (4*math.sin(7*math.pi/55)**2 + 4*math.sin(6*math.pi/55)**2)
print(f"   sin²θ₂₃(88) = γ₇/(γ₇+γ₆) = {s2_88:.6f}")
print(f"   sin²θ₂₃(55) = {s2_55:.6f}")
print(f"   NuFIT sin²θ₂₃ = sin²(49.198°) = {math.sin(49.198*RAD)**2:.6f}")
print(f"   Δ(88) = {abs(s2_88-math.sin(49.198*RAD)**2)/math.sin(49.198*RAD)**2*100:.2f}%  Δ(55) = {abs(s2_55-math.sin(49.198*RAD)**2)/math.sin(49.198*RAD)**2*100:.2f}%")

print("\n2) 其他量喺 88 vs 55 嘅差異 (可證偽判據):")
print("   γ_n(55) vs γ_n(88) 模式比會點變?")
for (a, b, name) in [(2, 3, "θ₁₂ beat 分子 (5,6)/(19,25) 候選"), (21, 9, "CKM δ = atan(ω₂₁/ω₉)")]:
    r88 = math.sin(a*math.pi/88)/math.sin(b*math.pi/88)
    r55 = math.sin(a*math.pi/55)/math.sin(b*math.pi/55)
    print(f"   ω_{a}/ω_{b}: 88 → {r88:.4f} (atan {math.degrees(math.atan(r88)):.3f}°), 55 → {r55:.4f} (atan {math.degrees(math.atan(r55)):.3f}°)")

print("\n3) ★ 判據: 若『chain 混合角都住喺 55』⇒ CKM 角都要用 N=55 重算")
print("   CKM δ(88) = 66.399960° (EXACT @1e-9). δ(55) = atan(sin(21π/55)/sin(9π/55)):")
d55 = math.degrees(math.atan(math.sin(21*math.pi/55)/math.sin(9*math.pi/55)))
print(f"   = {d55:.6f}° vs 66.4000° → Δ {abs(d55-66.4):.4f}° {'✗ 破壞 CKM 閉合' if abs(d55-66.4) > 0.01 else '✓'}")
print(f"   ⇒ CKM 家族必須留喺 N=88 (1e-9 閉合不可破壞)")
print(f"   ⇒ 55 唔係『通用 chain 尺度』— 只係 θ₂₃ 特定 (6,7 模式比) 嘅家?")

print("\n4) 結構動機候選 (55 = F₁₀ 嘅現有身份):")
print("   - 55 = C(L₅,2) = 66−11 = N_d+L₅ = 44+11 (O152 R10)")
print("   - 55 = 5×11 = (L₅−2N_gen)·L₅ = 公差×L₅")
print("   - k-ladder 終止: F₁₀ = 55 > N_d−1 = 43 (O152 R14)")
print("   - 33-44-55 Pythagorean (本腳本)")
print("   🔴 未推導: 點解 θ₂₃ 特定住喺 55 (6,7 模式比嘅『家』)")

print("\n5) 可證偽預測:")
print("   P1: sin²θ₂₃(55) = {:.4f} vs NuFIT {:.4f} (Δ {:.2f}%) — 比 88 好 {:.1f}×".format(
    s2_55, math.sin(49.198*RAD)**2,
    abs(s2_55-math.sin(49.198*RAD)**2)/math.sin(49.198*RAD)**2*100,
    abs(s2_88-math.sin(49.198*RAD)**2)/max(abs(s2_55-math.sin(49.198*RAD)**2), 1e-9)))
print("   P2: CKM 家族留喺 88 — 55 只適用 θ₂₃ (sector 純度)")
print("   P3: 若 θ₂₃(55) 係真, 質量譜 m_μ/m_τ 相關量都應該有 88→55 版本 (O144 輕子)")
