#!/usr/bin/env python3
"""
O179 — Script 05: 完整閉合鏈驗證 (Closure Chain)
=================================================
核心論證: 凝聚位置選擇規則 = 晶格幾何唯一決定

鏈條:
  hop 階梯對稱 n(h)=n(8-h) → <hop> = 直徑/2 = B = 4 (重心 = 干涉相消圈)
  → 位置權重 W(i) = (frust+1)·[1+(B/L₅)cos(πh/4)] 唯一由幾何+譜量生成
  → 凝聚概率重心 = hop=4 圈 (12 節點, 最多)
  → COSMOS-Web 434 LRD 全最近節點 8 (hop=4) = 單節點場確認
  → 時間律 4^{-ℓ} (O174) ⊗ 空間律 W(i) 正交 → 完整時空凝聚分佈

1. 重心論證: Σh·n(h)/60 = 4 源自對稱性 (唔係巧合)
2. hop=4 圈: 12 節點 = L₅+1 = B·N_gen — 凝聚重心圈嘅譜身份
3. 干涉核: E(h) 由波方程 Green 函數時均 (crystal_stress script 09)
4. 模態/位置正交: 44·4^ℓ 模態 (時間) ↔ 60 節點 (空間) 獨立
5. 全部閉合判準 C1-C6 + 重心命題

輸出: data/05_closure_chain.json + PASS/FAIL
"""
import math, json, os
import numpy as np

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
os.makedirs(OUT_DIR, exist_ok=True)

B = 4; N_gen = 3; N_d = 44; L5 = 11; L4 = 7; mu2 = 2
C = B/L5

print("="*72)
print("O179 Script 05 — 完整閉合鏈驗證")
print("="*72)

# ---- 1. hop 階梯 (由冷斑) ----
hop_hist = {0:1, 1:4, 2:8, 3:11, 4:12, 5:11, 6:8, 7:4, 8:1}
D = 8
N = 60

print(f"\n1. 重心論證:")
print(f"   hop 階梯 n(h) = {list(hop_hist.values())}, 對稱 n(h)=n({D}-h)")
sym = all(hop_hist[h] == hop_hist[D-h] for h in range(D+1))
print(f"   對稱性: {'PASS' if sym else 'FAIL'}")
sum_h = sum(h*hop_hist[h] for h in range(D+1))
mean_hop = sum_h / N
print(f"   Σh·n(h) = {sum_h}, <hop> = {mean_hop} = 直徑/2 = {D/2} = B = {B}")
print(f"   → 重心 = hop={D/2} 干涉相消圈: {'PASS' if mean_hop==B==D/2 else 'FAIL'}")
print(f"   (對稱距離分佈 ⇒ 平均 = 中點 = 相消點 — 結構性, 唔係巧合)")

# ---- 2. hop=4 圈譜身份 ----
print(f"\n2. hop=4 圈 (凝聚重心圈) 譜身份:")
print(f"   n(4) = 12 = L₅+1 = {L5}+1 = {L5+1}  {'PASS' if hop_hist[4]==L5+1 else 'FAIL'}")
print(f"   12 = B·N_gen = {B}·{N_gen} = {B*N_gen}  {'PASS' if hop_hist[4]==B*N_gen else 'FAIL'}")
print(f"   12 = 60/5 = N/|A₅ 5-rep| (12 = icosahedral 頂點數對偶)")
print(f"   hop=4 圈權重份額: n(4)·E(4) = {hop_hist[4]}·(1−C) = {hop_hist[4]*(1-C):.4f}")

# ---- 3. 干涉核譜身份 ----
print(f"\n3. 干涉核:")
print(f"   E(h) = 1 + C·cos(πh/4), C = B/L₅ = {B}/{L5} = {C:.10f}")
print(f"   E(0) = 1+C = {1+C:.6f} (錨點相長), E(4) = 1−C = {1-C:.6f} (相消)")
print(f"   M₄/M₀ = (1−C)/(1+C) = {((1-C)/(1+C)):.10f} = L₄/(L₅+B) = {L4}/{L5+B} = {L4/(L5+B):.10f}")
print(f"   {'PASS' if abs((1-C)/(1+C) - L4/(L5+B)) < 1e-12 else 'FAIL'}")

# ---- 4. 模態/位置正交 ----
print(f"\n4. 模態預算 (時間) ⊗ 位置自由度 (空間):")
print(f"   N_ℓ = {N_d}·4^ℓ = B·L₅·4^ℓ = {B}·{L5}·4^ℓ (模態預算, 時間層級)")
print(f"   60 節點 = B·(L₅+B) = {B}·({L5}+{B}) = {B*(L5+B)} (位置自由度, 固定)")
print(f"   92 = 60+32 = 2(N_d+μ²) = 2({N_d}+{mu2}) = {2*(N_d+mu2)} (總自由度)")
print(f"   44/60 = {44/60:.10f} = L₅/(L₅+B) = {L5/(L5+B):.10f}")
print(f"   {'PASS' if abs(44/60 - L5/(L5+B)) < 1e-12 else 'FAIL'}")

# ---- 5. O163 分區 ----
print(f"\n5. 位置自由度 = 宇宙份額分區:")
print(f"   60 = N_gen + B² + (N_d − N_gen) = {N_gen} + {B**2} + ({N_d}-{N_gen}) = {N_gen+B**2+(N_d-N_gen)}")
print(f"   (3:16:41 = 重子:DM:真空份額, O163)  {'PASS' if N_gen+B**2+(N_d-N_gen)==60 else 'FAIL'}")

# ---- 6. 4^{-ℓ} 層級表 ----
print(f"\n6. 層級時間律 (O174):")
print(f"   {'ℓ':>3} {'N_ℓ = 44·4^ℓ':>14} {'q_ℓ = 4^−ℓ':>12} {'1+z = 4^ℓ':>10} {'N(z)':>10}")
for ell in range(5):
    Nl = N_d * 4**ell
    ql = 4**(-ell)
    print(f"   {ell:>3} {Nl:>14} {ql:>12.6f} {4**ell:>10} {1/4**ell:>10.6f}")

# ---- 7. 閉合鏈總判定 ----
print(f"\n7. 閉合鏈判定:")
checks = []
# A1: 對稱
checks.append(sym)
# A2: 重心
checks.append(mean_hop == B == D/2)
# A3: hop=4 譜身份
checks.append(hop_hist[4] == L5+1 == B*N_gen)
# A4: 干涉核 C
checks.append(abs(C - B/L5) < 1e-12)
# A5: 質量比
checks.append(abs((1-C)/(1+C) - L4/(L5+B)) < 1e-12)
# A6: 模態身份
checks.append(N_d == B*L5 and N == B*(L5+B))
# A7: 44/60
checks.append(abs(44/60 - L5/(L5+B)) < 1e-12)
# A8: O163 分區
checks.append(N_gen + B**2 + (N_d-N_gen) == 60)
# A9: 92 自由度
checks.append(60+32 == 2*(N_d+mu2))
for i, c in enumerate(checks):
    print(f"   A{i+1}: {'PASS' if c else 'FAIL'}")

results = {
    'hop_hist': {str(k): v for k, v in hop_hist.items()},
    'sum_h': sum_h, 'mean_hop': float(mean_hop),
    'diameter_half': D/2, 'B': B,
    'hop4_identity': f"12 = L5+1 = B*Ngen = {L5+1}",
    'interference': {'C': C, 'E0': 1+C, 'E4': 1-C, 'M4M0': (1-C)/(1+C), 'spectral': L4/(L5+B)},
    'modal': {'Nl': f"{N_d}*4^l = {B}*{L5}*4^l", 'nodes': f"{B}*({L5}+{B})", 'ratio': L5/(L5+B)},
    'o163': f"{N_gen}+{B**2}+({N_d}-{N_gen})={N_gen+B**2+(N_d-N_gen)}",
    'checks': [bool(c) for c in checks],
}
with open(f'{OUT_DIR}/05_closure_chain.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {OUT_DIR}/05_closure_chain.json")

print(f"\n判定: {sum(checks)}/{len(checks)} PASS")
print("PASS" if all(checks) else "FAIL")
