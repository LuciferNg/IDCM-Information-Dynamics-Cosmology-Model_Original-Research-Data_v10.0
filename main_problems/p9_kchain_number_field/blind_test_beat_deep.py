#!/usr/bin/env python3
"""盲測第二輪: beat(2,31) 全 SM 參數庫掃描 + 結構分析"""
import numpy as np
from math import pi, sin, sqrt
from fractions import Fraction

omega = lambda n: 2*sin(pi*n/88)
w2, w31 = omega(2), omega(31)
beat = abs(w2 - w31)
B = beat
print(f"beat(2,31) = {B:.12f}")

# ---- 1. SM 參數庫 (PDG 2024) ----
SM = {
 # CKM (PDG 2024)
 "V_us": 0.2243, "V_cb": 0.0422, "V_ub": 0.00394,
 "V_cd": 0.218, "V_ts": 0.0411, "V_td": 0.0081,
 "sinθ12_C": 0.22500, "sinθ13_C": 0.00369, "sinθ23_C": 0.04214,
 "tanθ12_C": 0.23064, "J_CKM": 3.08e-5,
 # PMNS (NuFIT 5.2)
 "sin²θ12_P": 0.303, "sin²θ23_P": 0.572, "sin²θ13_P": 0.02225,
 "sinθ13_P": 0.14917, "tanθ12_P": 0.65935, "tanθ23_P": 1.1564,
 # 質量比
 "m_e/m_μ": 0.004836, "m_μ/m_τ": 0.05946, "m_e/m_τ": 0.0002875,
 "m_u/m_d": 0.47, "m_d/m_s": 0.0507, "m_s/m_b": 0.0277,
 "m_c/m_t": 0.00758, "m_b/m_t": 0.0299,
 "m_u/m_c": 0.0022, "m_d/m_b": 0.0015,
 # Δm² 比
 "Δm²₂₁/Δm²₃₁": 0.0298, "Δm²₃₁/Δm²₂₁": 33.6,
 # 其他
 "Ω_DM/Ω_b": 6.5, "Ω_b/Ω_m": 0.1333, "η_B": 6.062e-10,
 "α_em": 1/137.036, "α_s(MZ)": 0.1180,
 "m_W/m_Z": 0.8817, "sin²θ_W": 0.2312,
 "λ_sync/88": 3.351, "λ_sync/176": 1.6755,
 "F₇/F₈": 0.3819, "F₆/F₇": 0.6154, "L₄/L₇": 0.5385,
}
print("\n=== SM 參數庫掃描 (0.5% 精度) ===")
hits = []
for name, val in SM.items():
    for label, x in [("beat", B), ("1/beat", 1/B), ("2-beat", 2-B), ("4-beat", 4-B),
                     ("beat²", B*B), ("beat/2", B/2), ("beat+1", B+1)]:
        if val > 0 and abs(x-val)/val < 0.005:
            hits.append((name, label, x, val, abs(x-val)/val*100))
if hits:
    for h in hits: print(f"  HIT {h[0]} ~ {h[1]}={h[2]:.6f} vs {h[3]:.6f} ({h[4]:.3f}%)")
else:
    print("  無命中 (<0.5%)")

# ---- 2. γ 結構 ----
g = lambda n: 4*sin(pi*n/88)**2
print(f"\n=== γ 結構 ===")
print(f"γ_2 = {g(2):.8f}, γ_31 = {g(31):.8f}")
print(f"γ_2 + γ_42 = {g(2)+g(42):.8f} (=4, rational skeleton ✓)")
print(f"γ_31 + γ_13 = {g(31)+g(13):.8f} (=4, rational skeleton ✓)")
print(f"γ_2 + γ_31 = {g(2)+g(31):.8f}")
print(f"Σγ_odd = {sum(g(n) for n in range(1,89,2)):.4f} (觀察者), Σγ_even = {sum(g(n) for n in range(2,89,2)):.4f} (世界)")

# ---- 3. 指數結構注釋 ----
print(f"\n=== 指數結構 ===")
print(f"i+j = {2+31} = 33 = K_tree levels (scale維度)")
print(f"|i-j| = {31-2} = 29 = L₇ (Fibonacci) / 37-7-1")
print(f"i*j = {2*31} = 62 = 2×31")
print(f"i 係 degree 20 (n=2: φ(88/gcd(2,88))/2 = φ(44)/2 = 20)")
print(f"j 係 degree 40 (n=31: φ(88/gcd(31,88))/2 = φ(88)/2 = 40)")

# ---- 4. mirror (42,13) 分析 ----
w42, w13 = omega(42), omega(13)
bm = abs(w42 - w13)
print(f"\n=== mirror pair (42,13) ===")
print(f"beat(42,13) = {bm:.10f}")
print(f"ω_42 = 2sin(42π/88) = 2cos(2π/88) (補角: 42→44-2)")
print(f"ω_13 = 2sin(13π/88)")
print(f"1/beat(42,13) = {1/bm:.6f}")
print(f"beat(2,31)/beat(42,13) = {B/bm:.6f}")

# ---- 5. beat 嘅代數: 係咪 Σ 或差組合? ----
# 檢查 beat(2,31) 係咪 = ω_2 或 ω_31 嘅簡單代數 (如 ω_33-ω_2 等)
print(f"\n=== 代數關係試探 ===")
print(f"ω_2 = {w2:.10f}, ω_31 = {w31:.10f}")
print(f"ω_2 + ω_31 = {w2+w31:.10f}")
print(f"ω_33 = {omega(33):.10f}, ω_33 - ω_2 = {omega(33)-w2:.10f}")
print(f"ω_29 = {omega(29):.10f}, ω_31 - ω_29 = {w31-omega(29):.10f}")
print(f"ω_44 - ω_31 = {2-w31:.10f} (=[ω_44-ω_31])")
print(f"2 - ω_31 = {2-w31:.10f}, ω_31 - ω_2 = {w31-w2:.10f}")
print(f"ω_33 - ω_2 = {omega(33)-w2:.10f}")
print(f"√2 - ω_2 = {sqrt(2)-w2:.10f}")

# ---- 6. 重要: 檢查 i,j 與已指派功能的相鄰性 ----
# 已指派: (5,6),(19,25),(33,35),(3,22),(42,43),(10,31),(25,35),(6,37),(13,14),(41,42),(3,37),(16,35),(10,28),(4,13),(9,25),(11,23),(12,26),(25,29),(3,20)
assigned = {(5,6),(19,25),(33,35),(3,22),(42,43),(10,31),(25,35),(6,37),(13,14),(41,42),(3,37),(16,35),(10,28),(4,13),(9,25),(11,23),(12,26),(25,29),(3,20)}
print(f"\n=== catalog 關聯 ===")
print(f"(2,31) 喺 catalog 內? {'是' if (2,31) in assigned else '否'}")
near = []
for a,b in assigned:
    for cand in [(2,31),(31,2)]:
        pass
    # 共享一個指數?
    if a in (2,31) or b in (2,31): near.append((a,b))
print(f"共享指數嘅 catalog pairs: {near}")

# ---- 7. 數值: 有冇細數巧合 (10⁻⁴ 級)? ----
print(f"\n=== 精細掃描 (10⁻⁴) ===")
fine = {
 "1/(B-1)": 1/(B-1), "B/φ": B/((1+sqrt(5))/2), "B×φ": B*((1+sqrt(5))/2),
 "B-1": B-1, "B-√2": B-sqrt(2), "B-√3": B-sqrt(3),
 "B/(2π)": B/(2*pi), "π/B": pi/B,
}
for k,v in fine.items():
    print(f"  {k} = {v:.10f}")
