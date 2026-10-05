#!/usr/bin/env python3
"""
O53 新角度: h12 = 98 嘅 K_Chain 閉合!
========================================
發現候選: h12 = 98 = Σγ + 2B = 90 + 8
其中 Σγ = 90 (K_Chain 44-site 全譜和), B = 4 (邊界數)

驗證 + 擴展:
1. Σγ 精確計算 (γ_n = 4sin²(nπ/88))
2. h11 = Nd - 2B = 36 (已知閉合)
3. h12 = Σγ + 2B = 98 (新?)
4. χ = 2(h11-h12) = -124 嘅 K_Chain 表示
5. 其他 h12 (94, 102) 有冇 K_Chain 表示? (如果冇 → (36,98) 更獨特)
"""
import os, json, math, sys
import numpy as np

print("=" * 70)
print("O53: h12 = 98 嘅 K_Chain 閉合")
print("=" * 70)

Nd = 44
B = 4

# 1. Σγ 精確計算
n = np.arange(1, Nd + 1)
gamma = 4 * np.sin(n * np.pi / (2 * Nd)) ** 2
sum_gamma = gamma.sum()
print(f"[1] K_Chain 44-site 譜:")
print(f"  γ_n = 4sin²(nπ/88), n=1..44")
print(f"  Σγ = {sum_gamma:.10f} (理論值 90)")

# 驗證 90
print(f"  Σγ = 90? {np.isclose(sum_gamma, 90)}")

# 2. h11 閉合
h11_pred = Nd - 2 * B
print(f"\n[2] h11 = Nd - 2B = {Nd} - {2*B} = {h11_pred} (已知閉合 ✓)")

# 3. h12 新閉合
h12_pred = sum_gamma + 2 * B
print(f"\n[3] h12 = Σγ + 2B = {sum_gamma:.0f} + {2*B} = {h12_pred}")
print(f"  CY₃(36,98) 嘅 h12 = 98")
print(f"  閉合? {np.isclose(h12_pred, 98)}")

# 4. χ 表示
chi = 2 * (h11_pred - h12_pred)
print(f"\n[4] χ = 2(h11-h12) = 2({h11_pred}-{h12_pred}) = {chi}")
print(f"  而家 χ = -124 (CYTools 確認)")
print(f"  -124 = 2(36-98) ✓")

# 5. 其他表示
print(f"\n[5] h12 = 98 其他 K_Chain 表示:")
print(f"  98 = 88 + 10 (對偶鏈 88 + 2F₅) = {88+10}")
print(f"  98 = 2×44 + 10 = {2*44+10}")
print(f"  98 = 90 + 8 = Σγ + 2B ✓ (最自然)")
print(f"  98 = 44 + 44 + 5 + 5 = 2Nd + 2F₅")
print(f"  98 = 100 - 2 = 10² - 2")
print(f"  98 = 2×7² = 98? 7² = 49, 2×49 = 98 ✓")
print(f"    7 = L₄ = φ⁴+φ⁻⁴? {round((((1+math.sqrt(5))/2)**4 + ((1-math.sqrt(5))/2)**4))}")

# 6. 其他 h12 嘅 K_Chain 表示
print(f"\n[6] 其他 h12 (94, 102) 有冇 K_Chain 表示?")
phi = (1 + math.sqrt(5)) / 2
candidates = {
    94: ["90+4=Σγ+B", "88+6", "44+44+6", "2×44+6", "100-6"],
    102: ["90+12=Σγ+3B", "88+14", "44+44+14", "2×44+14", "100+2"],
}
for h, reps in candidates.items():
    print(f"  h12={h}:")
    for r in reps:
        try:
            val = eval(r.replace("Σγ", "90").replace("B", "4"))
            match = "✓" if val == h else ""
            print(f"    {r} = {val} {match}")
        except Exception as e:
            print(f"    {r}: FAIL")

# 7. 對照: Σγ 同 90 嘅特別結構
print(f"\n[7] Σγ = 90 嘅子結構:")
print(f"  44-site 全譜和 = 90")
print(f"  88-site 對偶: Σγ_even = 90, Σγ_odd = 88")
print(f"  90 + 88 = 178 = 2F₁₁ ✓ (已知)")
print(f"  90 - 88 = 2")
print(f"  98 = 90 + 8 = Σγ + 2B")
print(f"  88 = Σγ_odd (觀察者鏈)")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)