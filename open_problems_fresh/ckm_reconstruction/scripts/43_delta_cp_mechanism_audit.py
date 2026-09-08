#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
43_delta_cp_mechanism_audit.py — PMNS δ_CP 機制審計
=====================================================
CKM δ 閉合標準: atan(ω₂₁/ω₉) = 66.399960° @1e-9, 唯一性 + 選擇規則 (c1/c2/c3)。
PMNS δ: 觀察值 230°±36°−25° (NuFIT 5.2 NO+SK, 1σ: [205°, 266°])。

目標: 尋找能唯一鎖定 230° 嘅結構判準。
1. atan(ω_a/ω_b) 形式 null (CKM 類比) — 230° ↔ tan50° = 1.19175
2. 5×N 家族 (Z₅ 一致) — 邊個 N ∈ 結構常數集命中
3. mod-5 選擇規則 (c3-analog) — 候選集唯一 5 整除者
4. 230° 嘅精確分解 (過適測量!)
5. γ 和 class-0 = 46 驗證
6. J_CP 判別力
7. 樹邊界 1/33 co-closure 形式
"""
import math
from itertools import combinations

# 常數
N, DEG = 176, 180.0/math.pi
gamma = lambda k: 4*math.sin(k*math.pi/N)**2
omega = lambda k: math.sqrt(gamma(k))
phi = (1+math.sqrt(5))/2
beta, eps = 1/phi, 1/(4*phi)
KTREE = 33

# ---- 1. atan(ω_a/ω_b) 形式 null (CKM 類比) ----
target_tan = math.tan(math.radians(50.0))   # 230° ≡ 50° (tan-periodicity)
best = (1e9, None)
for a in range(1, 45):
    for b in range(1, 45):
        if a == b: continue
        r = omega(a)/omega(b)
        d = abs(r - target_tan)
        if d < best[0]: best = (d, (a, b, r))
print(f"1) atan(ω_a/ω_b) → tan50°=1.19175:")
print(f"   best pair (a,b) = {best[1]}, Δ = {best[0]:.2e}")
print(f"   → δ = 180+atan = {180+math.degrees(math.atan(best[1][2])):.6f}°")

# ---- 2. 5×N 家族 (Z₅ 一致: δ = F₅·N) ----
struct_N = {"N_d":44, "N_d⁺(class0)":46, "N_d⁻":42, "Σγ_even":90, "Σγ_odd":88,
            "N_d−B":40, "K_tree":33, "s=25":25, "L₆":18, "2N_gen×L₅":66}
print("\n2) 5×N 家族 (δ = 5N mod 360, NuFIT 1σ [205,266]):")
for name, n in struct_N.items():
    d5 = 5*n % 360
    hit = "✓" if 205 <= d5 <= 266 else " "
    print(f"   5×{name:12s} = {d5:7.2f}°  {hit}")

# ---- 3. mod-5 選擇 (c3-analog) ----
cands = {"Z₅ 72°":72, "Z₅ twisted 144°":144, "3×72 216°":216, "5×46 230°":230,
         "360−2⁷ 232°":232, "5×44 220°":220, "5×42 210°":210, "5×40 200°":200}
print("\n3) mod-5 選擇規則 (δ ≡ 0 mod 5):")
for name, v in cands.items():
    mark = "★唯一" if v % 5 == 0 and v != 360 else ""
    print(f"   {name:20s} ≡ {v%5} (mod 5)  {mark}")

# ---- 4. 230° 精確分解 (過適測量) ----
print("\n4) 230° 嘅精確結構分解:")
d = [
    ("5×46 = F₅×class0", 5*46),
    ("144+90−4 = 4π/5+Σγ_even−B", 144+90-4),
    ("360−88−42 = 2π−Σγ_odd−N_d⁻", 360-88-42),
    ("180+44+6 = π+N_d+2N_gen", 180+44+6),
    ("180+90−40 = π+Σγ_even−(N_d−B)", 180+90-40),
    ("π(1+5/18) = π(1+F₅/L₆)", 180*(1+5/18)),
]
for name, v in d:
    print(f"   {name:38s} = {v:8.4f}°  Δ={v-230:+.4f}°")

# ---- 5. γ class-0 和 = 46? ----
s0 = sum(gamma(k) for k in range(4, 89, 4))
s0no88 = sum(gamma(k) for k in range(4, 88, 4))
print(f"\n5) Σγ(k≡0 mod 4, k=4..88) = {s0:.6f} (46? Δ={s0-46:+.6f})")
print(f"   不含 k=88: {s0no88:.6f} (42 = N_d⁻? Δ={s0no88-42:+.6f})")

# ---- 6. J_CP 判別力 ----
print("\n6) J_CP 判別 (angles 混合組, J_max = 0.0330):")
s12, s23, s13 = 0.5512, 0.7584, 0.1498   # 混合組 sin
c12, c23, c13 = math.sqrt(1-s12**2), math.sqrt(1-s23**2), math.sqrt(1-s13**2)
Jmax = s12*c12*s23*c23*s13*c13**2
nufit_J = 0.0254
for name, dcp in cands.items():
    J = Jmax*abs(math.sin(math.radians(dcp)))
    print(f"   δ={name:20s} J = {J:.4f}  Δ vs NuFIT {nufit_J}: {abs(J-nufit_J)/nufit_J*100:5.1f}%")

# ---- 7. 樹邊界 1/33 co-closure ----
print("\n7) 樹邊界 (1/K_tree) co-closure:")
print(f"   boundary share 1/33 = {1/33:.6f}, interior 32/33 = {32/33:.6f}, 和 = {1/33+32/33:.6f}")
a12 = math.degrees(math.atan(beta)) + 1/KTREE
print(f"   θ₁₂ = atan(β)+1/33 = {a12:.4f}°  (1/33 rad = {1/KTREE*DEG:.4f}°)")
print(f"   θ₁₃ = arcsin(ε·32/33) = {math.degrees(math.asin(eps*32/33)):.4f}°")

# ---- 8. β_CKM 旁註 ----
print("\n8) 旁註: β_CKM = 2π/B² = 22.5° (PDG 22.5±0.7) — 1σ 命中, 無選擇規則, 僅記錄")
