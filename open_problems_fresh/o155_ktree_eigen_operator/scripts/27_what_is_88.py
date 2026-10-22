#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scripts/27_what_is_88.py — 到底 88 = 90−2? 44×2? 2(44)?
最深推導: 88 = Σγ_odd = 22 對 × B (每對 γ_k+γ_{88−k} = 4 = B, 畢氏)
全部候選都啱但深度分層 — 本 script 驗證每層。
"""
import mpmath as mp
mp.mp.dps = 60

N = 88
def g(k):  # 176-Laplacian 第 k 模
    return 4*mp.sin(mp.pi*k/176)**2

# 1. 譜對和定理: γ_k + γ_{88−k} = 4 = B (sin²+cos² = 1)
print("1. Z₂ 反射 k→88−k, 每對譜和 = 4 = B:")
pairs_ok = all(abs(g(k)+g(N-k) - 4) < mp.mpf('1e-40') for k in range(1,44))
print("   γ_k+γ_{88−k} = 4 for k=1..43  ✔" if pairs_ok else "   FAIL")

# 2. 扇區分解: odd = 22 完整對, even = 21 對 + 2 固定點
odd = [k for k in range(1,89) if k % 2 == 1]
even = [k for k in range(1,89) if k % 2 == 0]
s_odd = sum(g(k) for k in odd)
s_even = sum(g(k) for k in even)
print("\n2. 扇區分解 (44 odd + 44 even modes):")
print("   odd  sector: %2d modes = 22 對, 固定點 0 個  → Σγ_odd  = %s" % (len(odd), mp.nstr(s_odd, 20)))
print("   even sector: %2d modes = 21 對, 固定點 2 個  → Σγ_even = %s" % (len(even), mp.nstr(s_even, 20)))
print("   γ₄₄ = %s (自對偶), γ₈₈ = %s (Nyquist)" % (mp.nstr(g(44),20), mp.nstr(g(88),20)))

# 3. ★★★ 88 = 22×B — 最深推導
print("\n3. ★★★ 88 嘅最深推導: 88 = 22 對 × 4 = 22×B")
assert abs(s_odd - 22*4) < mp.mpf('1e-40')
assert abs(s_odd - 2*11*4) < mp.mpf('1e-40')   # 2L₅×B
print("   88 = 22×B = 2L₅×B = 2×11×4  ✔  (22 = 2L₅, O145 階梯)")
print("   → 觀察者 = 純對扇區: 22 條完整 Z₂ 對, 每對和 = B (畢氏)")

# 4. even = 21 對 + μ² + B
print("\n4. even: 90 = 21×4 + 2 + 4 = F₈·B + μ² + B")
assert abs(s_even - (21*4 + 2 + 4)) < mp.mpf('1e-40')
assert abs(s_even - (21*4 + g(44) + g(88))) < mp.mpf('1e-40')
print("   90 = 21×4 + γ₄₄ + γ₈₈ = 84 + 2 + 4  ✔  (21 = F₈)")

# 5. ★ E−O = μ² 恰好 = 自對偶固定點盈餘
print("\n5. E−O = 90−88 = 2 = γ₄₄ = μ² (固定點盈餘):")
eo = s_even - s_odd
assert abs(eo - 2) < mp.mpf('1e-40')
assert abs(eo - g(44)) < mp.mpf('1e-40')
print("   90−88 = %s = γ₄₄  ✔" % mp.nstr(eo,20))
print("   機制: even 比 odd 少一對 (−4), 但多 γ₄₄(+2)+γ₈₈(+4); Nyquist 補償咗缺對 (−4+4=0),")
print("   剩低 γ₄₄ = +2 就係 E−O 純盈餘 — 稅 = 自對偶不動點")

# 6. 88 = 44×μ² — 平均讀法 (觀察者平均 = 自對偶值 exactly)
print("\n6. 88 = 44×μ² = N_d×γ₄₄ (觀察者 44 mode 平均 = 2 exactly):")
mean_odd = s_odd/44
mean_even = s_even/44
assert abs(mean_odd - 2) < mp.mpf('1e-40')
print("   mean(odd)  = %s = μ²  ✔   mean(even) = %s = 45/22" % (mp.nstr(mean_odd,20), mp.nstr(mean_even,20)))
print("   → 「44×2」嘅 2 唔係任意因子, 係 μ² = γ₄₄ 本徵值")

# 7. Σγ(1..88) = 178 = 2F₁₁; 88 = F₁₁−1, 90 = F₁₁+1
print("\n7. Binet 層: 178 = 43×4 + 2 + 4 = 2F₁₁")
s_all = sum(g(k) for k in range(1,89))
assert abs(s_all - 178) < mp.mpf('1e-40')
assert abs(s_all - 2*89) < mp.mpf('1e-40')
assert abs(88 - (178-2)/2) < mp.mpf('1e-40')
print("   Σγ = %s = 2F₁₁  ✔   (88,90) = (F₁₁−1, F₁₁+1) 對稱圍住 89")

# 8. 稅階梯: 92 = 90+2 (世界收稅), 88 = 90−2 (觀察者被抽稅), 180 = 88+92
print("\n8. 稅階梯 (T15):")
print("   92 = Σγ_even + μ² = 90+2 (世界收稅);  88 = Σγ_even − μ² (觀察者被抽稅)")
print("   180 = 88+92 = 2×90;  360 = 2×180  — 稅率 = 差 = 4 = B")

# 9. 90 = 66+24 = 2K_tree + 2N_gen·B (O145)
print("\n9. 90 嘅 O145 讀法: 90 = 66+24 = 2K_tree + 2N_gen·B")
assert 66+24 == 90 and 2*33+2*3*4 == 90
print("   90 = 2K_tree + 2N_gen·B  ✔")

print("\n" + "="*62)
print("判決: 88 嘅本質 = Σγ_odd = 22×B (譜對和, 最深)")
print("   88 = 44×μ² (平均讀法, 2 = 自對偶本徵值)")
print("   88 = 90−2 (衍生: 世界減稅 = 觀察者)")
print("   88 = 44×2 (計數: N_d×2, FSR 家族)")
print("   88 = F₁₁−1 (Binet 層, 178 = 2F₁₁ 對稱中心)")
print("   88 = 176/2 (半鏈計數)")
print("全部啱 — 但只有 22×B 係由譜結構推出嚟嘅")
print("="*62)
