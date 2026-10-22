#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07_boson_fermion_scale.py — 試推: 費米/玻色 RGE (量→N) 是否同理 (O156 延伸)
================================================================================
問題: θ₂₃ (費米混合角) 住 55 (home 修正 88→55)。玻色質量比 (m_W/m_Z, m_H/m_W,
O36 已定義做模式比) 係咪都跟同一套「家尺度」規則?

測試:
  T1. 玻色比喺 N=88 嘅殘差 (form-precision 定 closure 級?)
  T2. 連續家 N* (解 R(N) = 測量值) — 玻色係咪都遠離 88?
  T3. 框架尺度搜索: 玻色比喺邊個框架 N 最準? (88? 55?)
  T4. N(a,b)=ab+a+b 對 O36 全部模式對 — 幾多個命中框架尺度?
  T5. 玻色模式對結構分解: (30,41), (38,19) 用咩框架常數?
"""
import math

RAD = math.pi/180.0

# ── 測量值 (PDG 2024) ──────────────────────────────────────────────
M_W  = 80.369    # GeV
M_Z  = 91.1876   # GeV
M_H  = 125.25    # GeV
R_WZ = M_W/M_Z   # 0.88136 (on-shell)
R_HW = M_H/M_W   # 1.55843
# 費米 θ₂₃ (NuFIT 5.2)
TH23 = 49.198    # 度
# 費米質量比目標 (O36 表)
F_MMU_TAU = 0.0595
F_MU_MD   = 0.4625
F_MC_MB   = 0.3038

def omega(n, N):
    """88-convention 模式頻率: ω_n = 2sin(nπ/N)"""
    return 2*math.sin(n*math.pi/N)

def ratio(a, b, N):
    return omega(a, N)/omega(b, N)

print("="*72)
print("T1. 玻色質量比喺 N=88 嘅殘差")
print("="*72)
r = ratio(30, 41, 88)
print(f"  m_W/m_Z = ω₃₀/ω₄₁(88) = {r:.6f}  vs  PDG {R_WZ:.6f}  →  {(r-R_WZ)/R_WZ*100:+.4f}%")
r = ratio(38, 19, 88)
print(f"  m_H/m_W = ω₃₈/ω₁₉(88) = {r:.6f}  vs  PDG {R_HW:.6f}  →  {(r-R_HW)/R_HW*100:+.4f}%")
# 對照: 費米 θ₂₃ 喺 88
th88 = math.degrees(math.atan(omega(7,88)/omega(6,88)))
print(f"  [對照] θ₂₃(88) = {th88:.4f}°  vs  NuFIT {TH23}°  →  {(th88-TH23):+.4f}°  ({(th88-TH23)/TH23*100:+.4f}%)")
print("  費米質量比 (O36, N=88):")
for name, a, b, t in [("m_u/m_d",10,24,0.4625),("m_c/m_b",8,33,0.3038),
                      ("m_μ/m_τ",1,18,0.0595),("m_s/m_d",22,1,20.0)]:
    r = ratio(a,b,88)
    print(f"    {name:<9} = ω_{a}/ω_{b}(88) = {r:.6f}  vs  {t}  →  {(r-t)/t*100:+.3f}%")

print()
print("="*72)
print("T2. 連續家 N* (解 R(N) = 測量值) — 玻色係咪遠離 88?")
print("="*72)
def solve_home(a, b, target, lo, hi):
    """喺 [lo,hi] 掃描 sign change, 然後 bisect 第一個根"""
    f = lambda N: ratio(a,b,N) - target
    prev_N, prev_f = lo, f(lo)
    N = lo
    step = (hi-lo)/500.0
    while N < hi:
        N += step
        val = f(N)
        if prev_f == 0: return N
        if prev_f*val <= 0:
            l, h, fl = prev_N, N, prev_f
            for _ in range(200):
                mid = (l+h)/2
                fm = f(mid)
                if fl*fm <= 0: h = mid
                else: l, fl = mid, fm
            return (l+h)/2
        prev_N, prev_f = N, val
    return None

n1 = solve_home(30, 41, R_WZ, 85, 95)
print(f"  m_W/m_Z:  N* = {n1:.2f}   (88 距離 {abs(n1-88):.2f})")
n2 = solve_home(38, 19, R_HW, 85, 95)
print(f"  m_H/m_W:  N* = {n2:.2f}   (88 距離 {abs(n2-88):.2f})")
n3 = solve_home(7, 6, math.tan(TH23*RAD), 30, 80)
print(f"  [對照] θ₂₃: N* = {n3:.2f}   (88 距離 {abs(n3-88):.2f}, 55 距離 {abs(n3-55):.2f})")

print()
print("="*72)
print("T3. 框架尺度搜索: 每個玻色比喺邊個框架 N 最準?")
print("="*72)
scales = [11, 22, 33, 44, 55, 88, 176]
for name, a, b, target in [("m_W/m_Z",30,41,R_WZ), ("m_H/m_W",38,19,R_HW)]:
    best = min(scales, key=lambda N: abs(ratio(a,b,N)/target - 1) if ratio(a,b,N) > 0 else 9)
    dev = abs(ratio(a,b,best)/target - 1)*100
    print(f"  {name:<9}: 最佳框架家 = {best}  (dev {dev:.3f}%)")
    for N in scales:
        r = ratio(a,b,N)
        if r > 0:
            d = abs(r/target-1)*100
            print(f"    N={N:3d}: {r:.4f}  (dev {d:.2f}%)")

print()
print("="*72)
print("T4. N(a,b)=ab+a+b 對 O36 全部模式對 (費米+玻色)")
print("="*72)
framework = {11, 22, 33, 42, 44, 46, 55, 88, 176}
pairs = [("m_u/m_d",10,24),("m_c/m_b",8,33),("m_W/m_Z",30,41),("m_H/m_W",38,19),
         ("m_μ/m_τ",1,18),("m_t/m_b",19,33),("m_s/m_d",22,1),("θ₂₃ (6,7)",6,7)]
hits = 0
for name, a, b in pairs:
    N = a*b + a + b
    hit = "🟢 命中!" if N in framework else "∉ 框架"
    if N in framework: hits += 1
    print(f"  {name:<12} ({a:2d},{b:2d}): N = {a*b}+{a+b} = {N:4d}  {hit}")
print(f"  命中率: {hits}/{len(pairs)}  (只有 θ₂₃!)")
# 密度對照: 全 [1,44]² 命中數
total = 0
for a in range(1,45):
    for b in range(a+1,45):
        if a*b+a+b in framework: total += 1
print(f"  [對照] 全 [1,44]² 框架命中: {total}/946 = {total/946*100:.2f}%")

print()
print("="*72)
print("T5. 玻色模式對結構分解")
print("="*72)
print("  m_W/m_Z (30,41):")
print(f"    30 = K_tree−N_gen = 33−3 = {33-3}")
print(f"    41 = N_d−N_gen   = 44−3 = {44-3}")
print(f"    差 = 41−30 = 11 = L₅ = N_d−K_tree ✓")
print(f"    和 = 71 (質數)")
print("  m_H/m_W (38,19):")
print(f"    19 = N_d/2−N_gen = 22−3 = {22-3}")
print(f"    38 = 2×19 = N_d−2N_gen = 44−6 = {44-6}")
print(f"    比 = 2:1, 差 = 19")
print("  [對照] θ₂₃ (6,7):")
print(f"    6 = 2N_gen, 7 = L₄; 和 = 13 = F₇, 積 = 42 = N_d⁻")

print()
print("="*72)
print("裁決")
print("="*72)
print("  T1: 玻色比喺 88: m_W/m_Z 0.10%, m_H/m_W 0.05% — form-precision, 唔係 closure 失敗")
print("  T2: 玻色 N* ≈ 88.1-88.2 (距 88 < 0.3) vs 費米 θ₂₃ N* ≈ 55.6 (距 88 = 32.4)")
print("  T3: 88 係玻色比唯一最佳框架家 (55/44/176 全部差 10%+)")
print("  T4: N=ab+a+b 只有 θ₂₃ (6,7) 命中 — 唔係費米規則, 係 θ₂₃ 獨有")
print("  T5: 玻色對用 N_d/K_tree/N_gen 層, 費米混合對用 N_gen/L₄/F₇ 層")
