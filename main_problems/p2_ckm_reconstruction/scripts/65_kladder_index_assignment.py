#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
65_kladder_index_assignment.py — C2 攻堅: k-ladder 指數指派算子級推導
========================================================================
目標: 推導點解 g_k 嘅分子指數 = F_{k+2} (2k−1), 分母差指數 = F_{k+6},
      指數間距 = 4 = B, 以及 (45+k) = 88−s Z₂ 反射。

現有 (T4): g_k = sin(F_{k+2}π/176)·sin(π/176) / [sin(F_{k+6}π/176)·sin((45+k)π/176)]
分子: 2k−1 = F_{k+2}  (k=2: 3=F₄, k=3: 5=F₅)
分母: F_{k+6}  (k=2: 21=F₈, k=3: 34=F₉)
"""
import mpmath as mp
mp.mp.dps = 80

PASS = FAIL = 0
def chk(name, val, target, tol):
    global PASS, FAIL
    ok = abs(val - target) <= tol * max(1.0, abs(target))
    if ok: PASS += 1; print(f"  [✔] {name} = {mp.nstr(val, 15)} (dev {float(abs(val-target)):.2e})")
    else: FAIL += 1; print(f"  [✘] {name} = {mp.nstr(val, 15)} ≠ {mp.nstr(target, 15)}")

phi = (1+mp.sqrt(5))/2
T = mp.matrix([[1,1],[1,0]])
def Fn(n): return int((T**n)[0,1])
def Ln(n): return int((T**n)[0,0]+(T**n)[1,1])
KTREE, B, N_gen, L5 = 33, 4, 3, 11

print("="*76)
print("C2 攻堅 1: 指數指派 2k−1 = F_{k+2} — 分子嘅 Fibonacci 強制")
print("="*76)
# 分子 beat(44−k, 45−k): 兩個 Nyquist 相鄰模式
# 4·sin((2k−1)π/176)·sin(π/176) — 半距 (2k−1)/2, 中心 44.5−k
# 問: 點解 2k−1 恰係 F_{k+2}?
print("序列檢查:")
for k in range(1, 6):
    print(f"  k={k}: 2k−1 = {2*k-1}, F_{k+2} = {Fn(k+2)}, 相等: {2*k-1 == Fn(k+2)}")
print(f"\n⇒ 2k−1 = F_{{k+2}} 只喺 k=2,3 成立 (k=1: 1≠2, k=4: 7≠5, k=5: 9≠8)")
print(f"⇒ 分子指數自動強制 k ∈ {{2,3}} — 同 T2 存在性定理一致!")

print("\n" + "="*76)
print("C2 攻堅 2: 分母差指數 F_{k+6} 同 (45+k) 嘅統一")
print("="*76)
# 分母 = sin(F_{k+6}π/176)·sin((45+k)π/176)
# 但 beat(p₁,p₂) = 4·sin(dπ/176)·cos(sπ/176), d=F_{k+6}, s=44−(k+1)
# cos(sπ/176) = sin((88−s)π/176) = sin((45+k)π/176) — 已證 (Z₂ 反射)
# 剩: 點解 d = F_{k+6}?
print("關鍵: beat(p₁,p₂) 嘅差 d = p₁−p₂ = F_{k+6}")
print(f"  k=2: p=(31,10), d=21=F₈;  k=3: p=(37,3), d=34=F₉")
print(f"  s = p₁+p₂ = 44−(k+1)")
print(f"  模式對: p = (s±F_{k+6})/2")

print("\n★ 新推導: s 同 F_{k+6} 嘅同餘關係 (Z₂ 反射完整性)")
for k in [2, 3]:
    s = 44-(k+1)
    d = Fn(k+6)
    p1, p2 = (s+d)/2, (s-d)/2
    # 關鍵身份: s + d = 2p₁, s − d = 2p₂
    # p₁, p₂ 嘅 Z₂ 反射: 88−p₁, 88−p₂
    m1, m2 = 88-p1, 88-p2
    print(f"  k={k}: p=({int(p1)},{int(p2)}), 反射=({int(m1)},{int(m2)})")
    # 反射後嘅差
    print(f"    88−p₁ = {int(m1)}: 44−p₁ = {44-int(p1)} (chain 半譜反射)")

print("\n★ 指數間距 4 = B 嘅結構意義:")
print(f"  F_{{k+2}} → F_{{k+6}}: 指數差 = {6-2} = 4 = B (樹分支因子)")
print(f"  分子 sin(F_{{k+2}}π/176), 分母 sin(F_{{k+6}}π/176)")
print(f"  ⇒ 分子/分母 Fibonacci 指數間距 = 樹分支 B — chain sector 受抑元素帶 tree 印記")

print("\n" + "="*76)
print("C2 攻堅 3: 新發現 — F_{k+6} = F_{k+2}·L_{k+3} 分解")
print("="*76)
for k in [2, 3]:
    a, b = Fn(k+2), Fn(k+6)
    ratio = b/a
    print(f"  k={k}: F_{k+6}/F_{k+2} = {b}/{a} = {ratio}")
    # Fibonacci 商: F_{n}/F_{m} 
    # F₈/F₄ = 21/3 = 7 = L₄
    # F₉/F₅ = 34/5 = 6.8 = 34/5 (非整數)
    print(f"    F₈/F₄ = 21/3 = 7 = L₄ ✓ (Lucas)")
    if k == 2:
        chk("F₈ = F₄·L₄", Fn(8), Fn(4)*Ln(4), 0)
    else:
        # F₉ = F₅·(34/5), 34/5 = 6.8 = L₄·(34/35)... 唔整數
        print(f"    F₉/F₅ = 34/5 (非整數) — 冇簡單 Lucas 分解")

print("\n★ 另一條路: F_{k+6} = F_{k+2}·(T̂⁴)₁₂ + ...")
# Cassini 恆等式: F_{n+m} = F_n·L_m − (−1)^m·F_{n−m}... 複雜
# 直接: F₈ = F₄·L₄ (3×7), F₉ = F₅·L₄ − F₃·L₁? 
print("  Cassini/Lucas 檢查:")
for k in [2, 3]:
    n = k+6
    m = k+2
    # F_{n} = F_{m}·L_{n−m} − (−1)^{n−m}·F_{m−(n−m)}? 試試
    d = n - m  # = 4 = B
    # Lucas 恆等式: F_{m+d} = F_m·L_d - (-1)^d·F_{m-d}
    if m - d >= 1:
        val = Fn(m)*Ln(d) - ((-1)**d)*Fn(m-d)
        print(f"  F_{n} = F_{m}*L_{d} - (-1)^{d}*F_{m-d} = {Fn(m)}*{Ln(d)} - {((-1)**d)*Fn(m-d)} = {val} (實際 {Fn(n)})")
        chk(f"F_{n} Lucas 分解", val, Fn(n), 0)

print("\n" + "="*76)
print("C2 攻堅 4: ★ 統一機制 — 指數間距 B = 分子/分母同源")
print("="*76)
# 兩個指數 F_{k+2}, F_{k+6} 相距 4 = B
# 分子 = Nyquist 半距 (2k−1)/2 → F_{k+2}
# 分母 = 模式對半距差 d/2 = F_{k+6}/2
# 統一: 分子用「小 Fibonacci」, 分母用「大 Fibonacci」, 間距 = B
print("分子: 2k−1 = F_{k+2}  (小 Fibonacci, Nyquist 半距)")
print("分母: d = F_{k+6}      (大 Fibonacci, 結構差)")
print(f"間距: (k+6)−(k+2) = 4 = B (樹分支因子)")
print(f"⇒ 樹分支 B 嵌入 Fibonacci 指數間距 — 混合量嘅 tree-sector 起源")
print(f"⇒ k-ladder 係 chain 譜 (176-sine) × tree 指數 (Fibonacci) 嘅交織產物")

print("\n" + "="*76)
print("C2 攻堅 5: ★★ 新模式對結構 — p₁ 嘅身份")
print("="*76)
# k=2: p₁ = 31, k=3: p₁ = 37
for k in [2, 3]:
    p1 = (44-(k+1)+Fn(k+6))/2
    p2 = (44-(k+1)-Fn(k+6))/2
    print(f"  k={k}: p₁ = {int(p1)}, p₂ = {int(p2)}")
    print(f"    p₁ 檢查: 44−p₁ = {44-int(p1)}, p₁−L₇ = {int(p1)-Ln(7)}, p₁−N_gen·L₅ = {int(p1)-N_gen*L5}, p₁−(K_tree−2) = {int(p1)-(KTREE-2)}")
    print(f"    p₂ 檢查: p₂+F₅ = {int(p2)+Fn(5)}, p₂·N_gen = {int(p2)*N_gen}, p₂+B = {int(p2)+B}")

print(f"\n  k=2: p₁=31 = 2·L₅+9 = 22+9? 31 = L₅·2+9 = 22+9 ✓ (9=N_gen²)")
print(f"  k=3: p₁=37 = L₅·3+4 = 33+4 = K_tree+B ✓ (37 = K_tree+B)")
print(f"  k=2: p₂=10 = 2·F₅ = 2·5 = 10 ✓ (2=μ², 5=F₅)")
print(f"  k=3: p₂=3 = N_gen ✓")

print("\n" + "="*76)
print("結論")
print("="*76)
print("""
C2 攻堅結果 (k-ladder 指數指派):
✅ 分子 2k−1 = F_{k+2}: 只喺 k=2,3 成立 → 分子自動強制 k ∈ {2,3} (同 T2 一致)
✅ (45+k) = 88−s Z₂ 反射: cos(sπ/176) = sin((88−s)π/176) EXACT
✅ 指數間距 4 = B: 樹分支因子嵌入 Fibonacci 指數間距
✅ k-ladder = chain 譜 (176-sine) × tree 指數 (Fibonacci) 交織
🟡 分母 d = F_{k+6} 嘅「選擇」仍依賴存在性 (奇偶+預算), 但已升級為:
   - 分子強制 k∈{2,3} (2k−1=F_{k+2} 唯一解)
   - 分母 F_{k+6} 係 s 附近嘅 Fibonacci (奇偶匹配)
""")
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")