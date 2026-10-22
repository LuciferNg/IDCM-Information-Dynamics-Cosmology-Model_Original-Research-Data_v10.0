#!/usr/bin/env python3
"""O149 script 99 — 獨立驗證器 (不依賴 session scripts)
==========================================================
用獨立 code path (product-to-sum 展開 + mpmath 高精度) 交叉核對
docs/01_derivation_record.md 中所有推導鏈嘅公式同數值:
  V1: 定理1 恆等式 946 個拍頻
  V2: 定理2 Z₂ 字典 (ω↔v_g, γ↔v_g²) + O65 例子
  V3: 定理3 v_g floor
  V4: 定理4 k-ladder (k=1..4)
  V5: 11 條 docs beat 公式值
  V6: 統計 (831,713 / 窗內 23+29 / p_joint / R2 1806+8)
  V7: 分母 mean 聚類 11/11
  V8: V_td 候選 beat(40,42)/beat(3,42)
"""
import math
try:
    from mpmath import mp, mpf, sin, cos, sqrt, pi
    mp.dps = 50
    HAVE_MP = True
except ImportError:
    HAVE_MP = False
    print("[!] mpmath 未安裝 — 用 float64 高精度替代")

def sin_hp(x):
    return sin(x) if HAVE_MP else math.sin(x)
def cos_hp(x):
    return cos(x) if HAVE_MP else math.cos(x)
def sqrt_hp(x):
    return sqrt(x) if HAVE_MP else math.sqrt(x)

PASS = 0; FAIL = 0; CHECKS = []
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; tag = "✅"
    else:    FAIL += 1; tag = "❌"
    CHECKS.append((name, tag))
    print(f"  {tag} {name} {detail}")

print("="*76)
print("V1: 定理1 — beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2), 全 946 對")
print("="*76)
bad = 0; maxerr = 0.0
for a in range(1, 45):
    for b in range(a+1, 45):
        # 獨立路徑: 直接 product-to-sum 展開 (唔用中間函數)
        A = a*pi/88; B = b*pi/88
        lhs = 2*abs(sin_hp(B) - sin_hp(A))
        d = b - a; m = (a+b)/2
        rhs = 4*sin_hp(d*pi/176)*cos_hp(m*pi/88)
        err = abs(float(lhs - rhs))
        maxerr = max(maxerr, err)
        if err > 1e-25: bad += 1
check(f"946/946 恆等式, max err = {maxerr:.2e}", bad == 0)

print()
print("="*76)
print("V2: 定理2 — Z₂ 字典 ω_n = 2v_g(44-n), γ_n = 4v_g(44-n)²")
print("="*76)
ok_w = ok_g = True
for n in range(1, 45):
    w_n = 2*sin_hp(n*pi/88)
    if abs(float(w_n - 2*cos_hp((44-n)*pi/88))) > 1e-25: ok_w = False
    g_n = 4*sin_hp(n*pi/88)**2
    if abs(float(g_n - 4*cos_hp((44-n)*pi/88)**2)) > 1e-25: ok_g = False
check("ω_n = 2·v_g(44-n), 44/44", ok_w)
check("γ_n = 4·v_g(44-n)², 44/44", ok_g)

# O65 例子
g2 = 4*sin_hp(2*pi/88)**2; g3 = 4*sin_hp(3*pi/88)**2
s12 = g2/(g2+g3)
v42 = cos_hp(42*pi/88); v41 = cos_hp(41*pi/88)
s12_vg = v42**2/(v42**2 + v41**2)
check(f"O65 sin²θ₁₂ = γ₂/(γ₂+γ₃) = {float(s12):.5f} = v_g²-ratio {float(s12_vg):.5f}",
      abs(float(s12 - s12_vg)) < 1e-15)
w1 = 2*sin_hp(pi/88); w29 = 2*sin_hp(29*pi/88)
v43 = cos_hp(43*pi/88); v15 = cos_hp(15*pi/88)
check(f"O65 CKM θ₂₃ = ω₁/ω₂₉ = {float(w1/w29):.5f} = v_g(43)/v_g(15) = {float(v43/v15):.5f}",
      abs(float(w1/w29 - v43/v15)) < 1e-15)

print()
print("="*76)
print("V3: 定理3 — v_g floor = sin(π/176)")
print("="*76)
floor = float(sin_hp(pi/176))
floor_tight = float(sin_hp(pi/176)/cos_hp(3*pi/176))
check(f"floor = sin(π/176) = {floor:.8f} (loose, v_g 單值下限)", abs(floor - 0.01784901) < 1e-6)
# 相鄰對 ratio 範圍
ratios = [cos_hp((n+0.5)*pi/88)/cos_hp((m+0.5)*pi/88) for n in range(1,44) for m in range(1,44) if n != m]
rmin = min(float(abs(r)) for r in ratios)
rmax = max(float(abs(r)) for r in ratios)
check(f"相鄰對 ratio ∈ [{rmin:.6f}, {rmax:.2f}], tight floor = sin(π/176)/cos(3π/176) = {floor_tight:.6f}",
      abs(rmin - floor_tight) < 1e-9)
check("sinθ₁₃(C)=0.00351 < floor → 兩因子必然", 0.00351 < floor)
check("V_ub(C)=0.00369 < floor → 兩因子必然", 0.00369 < floor)
check("V_cb=0.04182 > floor → 純 v_g 可達", 0.04182 > floor)
check(f"PMNS sinθ₁₃=0.1485 = {0.1485/floor:.1f}×floor >> floor", 0.1485/floor > 8)

print()
print("="*76)
print("V4: 定理4 — k-ladder")
print("="*76)
F = [0,1,1,2,3,5,8,13,21,34,55,89]
beat = lambda a,b: 2*abs(sin_hp(b*pi/88) - sin_hp(a*pi/88))
ladder = {}
for k in [1,2,3,4]:
    num_a, num_b = 44-k, 44-k+1
    dual_ok = 1 <= 44-num_b and 44-num_a <= 44
    s_den, d_den = 44-(k+1), F[k+6]
    a_den = (s_den - d_den)/2
    den_ok = (s_den - d_den) % 2 == 0 and 1 <= a_den and a_den + d_den <= 44
    if dual_ok and den_ok:
        g = beat(num_a, num_b)/beat(a_den, a_den+d_den)
        ladder[k] = (f"({num_a},{num_b})", f"({int(a_den)},{int(a_den+d_den)})", float(g))
        print(f"  k={k}: ({num_a},{num_b})/({int(a_den)},{int(a_den+d_den)}) = {float(g):.10f}")
    else:
        print(f"  k={k}: 無效 (dual_ok={dual_ok}, den_ok={den_ok})")
check("k=1 無效 (dual 出譜 + den 非整數)", 1 not in ladder)
check("k=2 → sinθ₁₃ (0.00350743)", 2 in ladder and abs(ladder[2][2] - 0.0035074294) < 1e-7)
check("k=3 → V_ub (0.00369102)", 3 in ladder and abs(ladder[3][2] - 0.0036910176) < 1e-7)
check("k=4 無效 (d=F₁₀=55 > sum=39)", 4 not in ladder)

print()
print("="*76)
print("V5: 11 條 docs beat 公式值 (獨立重算)")
print("="*76)
formulas = [
    ('CKM tanθ₁₂', 0.231604, (5,6),   (19,25)),
    ('CKM tanθ₂₃', 0.041563, (33,35), (3,22)),
    ('CKM sinθ₁₃', 0.003508, (42,43), (10,31)),
    ('CKM λ',      0.22500,  (25,35), (6,37)),
    ('CKM V_cb',   0.04182,  (13,14), (6,37)),
    ('CKM V_ub',   0.00369,  (41,42), (3,37)),
    ('CKM A',      0.830,    (16,35), (10,28)),
    ('PMNS tanθ₁₂',0.659629, (4,13),  (9,25)),
    ('PMNS tanθ₂₃',0.906745, (11,23), (12,26)),
    ('PMNS tanθ₂₃b',1.150368,(4,14),  (22,44)),
    ('PMNS sinθ₁₃',0.1485,   (25,29), (3,20)),
]
for name, obs, p1, p2 in formulas:
    v = beat(*p1)/beat(*p2)
    # docs 表格值係 6 位小數 rounding → 小值用相對 5e-4, 大值 1e-4
    tol = 5e-4 if obs < 0.01 else 1e-4
    rel = abs(float(v) - obs)/obs
    tag = "✅" if rel < tol else ("🟡" if rel < 0.01 else "❌")
    print(f"  {tag} {name:>13}: {float(v):.10f} vs docs {obs}  (δ={rel:.1e})")
check("11 條公式值全部重算一致 (docs rounding 容忍)",
      all((abs(float(beat(*p1)/beat(*p2)) - obs)/obs) < (5e-4 if obs < 0.01 else 1e-4)
          for _,obs,p1,p2 in formulas))

print()
print("="*76)
print("V6: 統計")
print("="*76)
# 全空間 ratio 數
pairs = [(i,j) for i in range(1,45) for j in range(i+1,45)]
B = sorted(float(beat(i,j)) for i,j in pairs)
R = sorted(b1/b2 for b1 in B for b2 in B if b2 > 1e-6 and 0 < b1/b2 < 10)
check(f"全空間 ratios = {len(R)} (docs: 831,713)", len(R) == 831713)
win13 = sum(1 for r in R if 0.003508*0.99 < r < 0.003508*1.01)
winub = sum(1 for r in R if 0.00369*0.99 < r < 0.00369*1.01)
check(f"sinθ₁₃ ±1% 窗內 = {win13} (docs: 23)", win13 == 23)
check(f"V_ub ±1% 窗內 = {winub} (docs: 29)", winub == 29)
p_joint = win13*winub/len(R)**2
check(f"p_joint = {p_joint:.2e} (docs: 9.64e-10)", abs(p_joint - 9.64e-10) < 1e-12)
# R2 候選數 + 命中
r2_vals = set(round(float(cos_hp((n+0.5)*pi/88)/cos_hp((m+0.5)*pi/88)), 14)
              for n in range(1,44) for m in range(1,44) if n != m)
check(f"R2 候選 = {len(r2_vals)} (docs: 1,806)", len(r2_vals) == 1806)
tvals = [0.231604,0.041563,0.003508,0.225,0.04182,0.00369,0.83,0.659629,0.906745,1.150368,0.1485]
hits = 0
for t in tvals:
    rv = sorted(r2_vals)
    import bisect
    i = bisect.bisect_left(rv, t)
    dmin = min(abs(rv[max(0,i-1)]-t), abs(rv[min(len(rv)-1,i)]-t))/t
    if dmin < 0.01: hits += 1
check(f"R2 <1% 命中 = {hits}/11 (docs: 8/11)", hits == 8)

print()
print("="*76)
print("V7: 分母 mean 聚類 (11/11 特殊位置 ±2)")
print("="*76)
SPECIAL = [5,8,11,13,18,21,22,29,33,34,44]
den_means = [(name, (p2[0]+p2[1])/2) for name,_,_,p2 in formulas]
near = 0
for name, m in den_means:
    dmin = min(abs(m-s) for s in SPECIAL)
    if dmin <= 2.0: near += 1
    print(f"  {name:>13}: mean={m:5.1f}, Δmin={dmin:.1f} {'✅' if dmin<=2 else '❌'}")
check(f"分母 mean 11/11 特殊位置 ±2 ({near}/11)", near == 11)

print()
print("="*76)
print("V8: V_td 候選 beat(40,42)/beat(3,42)")
print("="*76)
vtd = float(beat(40,42)/beat(3,42))
rel = abs(vtd - 0.00857)/0.00857
check(f"beat(40,42)/beat(3,42) = {vtd:.8f} (docs: 0.0085684, δ=1.84e-4)",
      abs(vtd - 0.0085684) < 1e-6 and rel < 2e-4)
check("V_td < floor → 唔係純 v_g ratio", 0.00857 < floor)

print()
print("="*76)
print(f"總結: {PASS}/{PASS+FAIL} PASS")
print("="*76)
for name, tag in CHECKS:
    print(f"  {tag} {name}")
