#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_r3_mode_pair_scale.py — R3 續: 模式對→尺度分配規則 (O156, 譜結構層)
=====================================================================
候選規則: 模式對 (a,b) 嘅「家」尺度 N = ab+a+b = (a+1)(b+1)−1

動機: θ₂₃ 用 (6,7): 6×7 = 42 = N_d⁻ (觀察者側), 6+7 = 13 = F₇
      42 + 13 = 55 = F₁₀ — 模式對自己生成尺度!

測試:
1. 規則命中: (6,7)→55, (2,3)→11, 其他框架尺度嘅 (a,b) 多重度
2. Null-control: [1,44]² 內幾多對撞框架尺度 (密度)
3. 泛化測試: (2,3)→11 e-row 預測 — U_e1(11) vs U_e1(88) vs NuFIT
4. Seam 結構: beat(6,7) = 4sin(π/176)·v_g(6.5), 6.5 = F₇/2 縫
5. 塔結構: L₅×(Fibonacci F₂..F₆ ∪ B 冪) — 55 = F₁₀ = F₅·L₅
"""
import math
DEG = 180.0/math.pi
RAD = math.pi/180.0

def th(N, k1=7, k2=6):
    return math.degrees(math.atan(math.sin(k1*math.pi/N)/math.sin(k2*math.pi/N)))

def gam(n, N=88):
    return 4*math.sin(n*math.pi/N)**2

print("="*70)
print("1) 候選規則: N(a,b) = ab+a+b — 模式對生成尺度")
print("="*70)
print(f"   (6,7): 6×7+6+7 = 42+13 = 55 = F₁₀  {'✓' if 6*7+6+7==55 else '✗'}")
print(f"   6×7 = 42 = N_d⁻ (觀察者側), 6+7 = 13 = F₇ (模式和要求)")
print(f"   (2,3): 2×3+2+3 = 6+5 = 11 = L₅  {'✓' if 2*3+2+3==11 else '✗'}")
print(f"   2×3 = 6 = 2N_gen, 2+3 = 5 = F₅")
print(f"   (a+1)(b+1)−1 形式: (6,7)→7×8−1 = 56−1; (2,3)→3×4−1 = 12−1")

print("\n" + "="*70)
print("2) Null-control: [1,44]² 內邊啲 (a,b) 撞框架尺度")
print("="*70)
FRAMEWORK = {11, 22, 33, 44, 55, 88, 176, 42, 46}
hits = {}
for a in range(1, 45):
    for b in range(a+1, 45):
        N = a*b + a + b
        if N in FRAMEWORK:
            hits.setdefault(N, []).append((a, b))
print(f"   框架尺度: {sorted(FRAMEWORK)}")
for N in sorted(hits):
    print(f"   N={N:3d} ({'F₁₀' if N==55 else 'L₅' if N==11 else 'N_d' if N==44 else 'K_tree' if N==33 else 'N_d⁻' if N==42 else ''}): {hits[N]}")
total_pairs = sum(len(v) for v in hits.values())
total = 44*43//2
print(f"   命中對數 = {total_pairs}/{total} = {total_pairs/total*100:.2f}% (密度)")
print(f"   55 命中: {hits.get(55, [])} — 3 對 (1,27),(3,13),(6,7)")

print("\n   ★ 規則方向: 量→N (given 模式對 → 家尺度), 唔係 N→量")
print(f"   θ₂₃ 用 (6,7) (O69 模式選擇) ⇒ 家 = 55 — 分配規則成立")
print(f"   但 N→(a,b) 唔唯一 (55 有 3 對) — 選擇由 O69 做, 尺度由本規則做")

print("\n" + "="*70)
print("3) 泛化測試: (2,3)→11 e-row 預測 (可證偽)")
print("="*70)
# e-row: U_e1² = γ₃/(γ₂+γ₃), U_e2² = γ₂/(γ₂+γ₃)
for N in (88, 11):
    g2, g3 = gam(2, N), gam(3, N)
    ue1 = math.sqrt(g3/(g2+g3))
    print(f"   N={N:2d}: U_e1 = √(γ₃/(γ₂+γ₃)) = {ue1:.4f}  (NuFIT 0.8249, Δ {abs(ue1-0.8249)/0.8249*100:.2f}%)")
print(f"   ⇒ e-row 喺 88 (0.8%) 好過 11 (1.4%) — 泛化 (2,3)→11 失敗 ✗")
print(f"   ⇒ 規則只適用 θ₂₃ (6,7)? 定係 e-row 唔係『模式比角』(係 tree 角 θ₁₂ 嘅 |U| 投影)?")

print("\n   CKM δ = atan(ω₂₁/ω₉) 模式比測試: N(21,9) = 189+30 = 219 — 唔係框架尺度")
print(f"   ⇒ CKM 唔跟規則 (chain sector 留 88) — 規則係 W-field/tree sector 專屬")

print("\n" + "="*70)
print("4) Seam 結構: beat(6,7) 坐喺 F₇/2 縫")
print("="*70)
# beat(a,b) = |ω_a−ω_b|, ω = 2sin(nπ/88)
w6, w7 = 2*math.sin(6*math.pi/88), 2*math.sin(7*math.pi/88)
beat67 = w7 - w6
# 公式: beat = 4sin(dπ/176)·v_g((a+b)/2) (O149), d=1, (a+b)/2 = 6.5
vg = lambda x: math.cos(x*math.pi/88)
b_f = 4*math.sin(1*math.pi/176)*vg(6.5)
print(f"   beat(6,7) = {beat67:.6f}")
print(f"   = 4sin(π/176)·v_g(6.5) = {b_f:.6f}  (O149 公式 {'✓' if abs(beat67-b_f)<1e-9 else '✗'})")
print(f"   v_g(6.5) = v_g(F₇/2) — 半整數縫! (O152: 縫 = 奇T̂≤88/2 ∋ 6.5)")
print(f"   6.5 = F₇/2 = Ω_DM/Ω_b/2 — 模式對嘅 beat 本身坐喺縫上")
print(f"   55 = F₁₀: 55/2 = 27.5 = F₁₀/2 縫 (O152 R10b 縫生成)")
print(f"   ⇒ θ₂₃ 系統 (6,7) 嘅 beat 喺 F₇/2 縫, 家尺度 55 嘅半縫 F₁₀/2 都係縫")

print("\n" + "="*70)
print("5) 塔結構: 55 = F₁₀ = F₅·L₅ (F_{2n}=F_n·L_n 恆等)")
print("="*70)
print(f"   F₁₀ = F₅·L₅ = 5×11 = 55 {'✓' if 5*11==55 else '✗'} (Fibonacci-Lucas 恆等 F_{{2n}}=F_n·L_n, n=5)")
tower = [(11,1,'F₂'), (22,2,'F₃'), (33,3,'F₄'), (44,4,'B=4'), (55,5,'F₅'), (88,8,'F₆'), (176,16,'B²')]
print(f"   尺度塔 = L₅ × {{Fibonacci F₂..F₆ ∪ B 冪}}:")
for N, m, label in tower:
    print(f"     {N:3d} = 11 × {m:2d}  ({label})")
print(f"   FSR 家族: 11→44→176 (×4, O140 N_ℓ = N·4^ℓ)")
print(f"   Fibonacci 家族: {33,55,88} = 11×{{3,5,8}} = 11×{{F₄,F₅,F₆}}")
print(f"   ★ 55 = 唯一同時係 F₁₀ (Fibonacci) 同 F₅·L₅ (Fibonacci×Lucas) 嘅尺度")

print("\n" + "="*70)
print("6) 55 嘅身份清單 (全部既有, 零新參數)")
print("="*70)
ids = [
    ("F₁₀", "Fibonacci 第 10 項"),
    ("F₅·L₅ = 5×11", "F_{2n}=F_n·L_n 恆等 n=5"),
    ("C(L₅,2) = 66−11", "O152 R10: SU(12) 非單正根"),
    ("N_d+L₅ = 44+11", "O152 R10"),
    ("k-ladder 終止", "F₁₀ = 55 > N_d−1 = 43 (O152 R14)"),
    ("N(6,7) = 6·7+6+7", "本輪: 模式對生成尺度 (42+13)"),
    ("√(33²+44²)", "本輪: Pythagorean 斜邊 (尺度層)"),
]
for ident, desc in ids:
    print(f"   • {ident:20s} — {desc}")

print("\n" + "="*70)
print("7) 誠實裁決")
print("="*70)
print("""
   規則 N(a,b) = ab+a+b:
   - (6,7) → 55 ✓ (θ₂₃ 0.003% 閉合, null 2.8% — 已證)
   - (2,3) → 11: e-row 預測失敗 (88 0.8% vs 11 1.4%) ✗
   - 密度 0.85% (8/946 對撞框架) — 低密度, 單獨命中非巧合
   ⇒ 🟡 候選規則: θ₂₃ 係 PMNS 唯一純模式比角 (θ₁₂/θ₁₃ 係 tree 公式),
     CKM 係 chain sector (留 88) — 規則只有單一實例, 泛化未證/失敗
   ⇒ 55 嘅譜結構身份: F₁₀ = F₅·L₅ + 縫 F₁₀/2 + 塔 L₅×F₅ — 多重重疊,
     但「點解 θ₂₃ 特別」仍需算子層 (→ O155) 或譜結構層更強論證
""")
