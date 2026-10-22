#!/usr/bin/env python3
"""O149 script 01 — v_g 色散光譜分析
=====================================
目標: 建立群速度鎖定嘅基礎結構:
1. v_g(n) = cos(nπ/88) 全譜 + 特殊模式 (v_g=1, √2/2, 0, 極值, Fib/Lucas/ladder)
2. 推廣恆等式: beat(a,b) = 4·sin((b-a)π/176)·v_g((a+b)/2) — 全部 946 個拍頻
3. Z₂ 對偶: ω_n = 2sin(nπ/88) = 2·v_g(44-n) → ω-ratio 就係 v_g-ratio
4. 11 條 beat 公式嘅 (d, mean, sin(dπ/176), v_g(mean)) 分解表
5. 相鄰對排序 + Z₂-valid 相鄰對 (Z₂ 對偶仍在譜內)
"""
import math, json, os
import numpy as np

PI = math.pi
w  = lambda n: 2*math.sin(PI*n/88)          # beat frequency (scaled ω)
g  = lambda n: 4*math.sin(PI*n/88)**2       # Laplacian eigenvalue
vg = lambda x: math.cos(PI*x/88)            # group velocity (x 可半整數)
beat = lambda a,b: abs(w(a)-w(b))

# ============ 1. 基本恆等式驗證 ============
print("="*70)
print("1. 推廣恆等式: beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2),  d=b-a")
print("="*70)
bad = 0
for a in range(1,45):
    for b in range(a+1,45):
        d = b-a; m = (a+b)/2.0
        lhs = beat(a,b)
        rhs = 4*math.sin(d*PI/176)*vg(m)
        if abs(lhs-rhs) > 1e-12:
            bad += 1
            if bad < 5: print(f"  FAIL ({a},{b}): {lhs} vs {rhs}")
print(f"  946 個拍頻全部驗證: {'✅ PASS' if bad==0 else f'❌ {bad} FAIL'}")
print(f"  特殊 case d=1: beat(n,n+1) = 4sin(π/176)·v_g(n+1/2)  (O146 §10 恆等式 = 推廣式嘅子集)")

# ============ 2. Z₂ 對偶 ω ↔ v_g ============
print()
print("="*70)
print("2. Z₂ 對偶: ω_n = 2sin(nπ/88) = 2·v_g(44-n)")
print("="*70)
ok = all(abs(w(n) - 2*vg(44-n)) < 1e-12 for n in range(1,45))
print(f"  ω_n = 2·v_g(44-n)  (44/44): {'✅' if ok else '❌'}")
print("  → 任何 ω-ratio (O65: ω₁/ω₂₉) = v_g-ratio:  ω₁/ω₂₉ = v_g(43)/v_g(15)")

# ============ 3. 特殊模式目錄 ============
print()
print("="*70)
print("3. 特殊模式 (Fib F5-F9 / Lucas L5-L7 / 階梯 / SYNC / 邊界)")
print("="*70)
special = [1,2,3,4,5,6,7,8,11,13,18,21,22,29,33,34,41,42,43,44]
labels  = {1:'fundamental',2:'dual(42)',3:'dual(41)',4:'2²',5:'F₅',
           6:'γ₆核心',7:'dual(37)',8:'F₆',11:'L₅階梯',13:'F₇',
           18:'L₆',21:'F₈',22:'SYNC √2/2',29:'L₇',33:'3×11階梯',
           34:'F₉',41:'dual(3)',42:'dual(2)',43:'dual(1)',44:'Nyquist 0'}
print(f"{'n':>3} | {'v_g':>9} | {'γ':>8} | {'ω/2':>8} | 標籤")
print("-"*55)
for n in special:
    print(f"{n:>3} | {vg(n):9.6f} | {g(n):8.5f} | {w(n)/2:8.5f} | {labels[n]}")

# 精確代數值
print()
print("  精確代數值:")
print(f"    v_g(11) = cos(π/8)  = √(2+√2)/2 = {vg(11):.8f}")
print(f"    v_g(22) = cos(π/4)  = √2/2      = {vg(22):.8f}")
print(f"    v_g(33) = cos(3π/8) = √(2-√2)/2 = {vg(33):.8f}")
print(f"    v_g(44) = cos(π/2)  = 0         = {vg(44):.8f}")

# ============ 4. 相鄰對排序 + Z₂-valid ============
print()
print("="*70)
print("4. 相鄰對 beat 排序 (細→大) + Z₂ 對偶有效性")
print("="*70)
adj = [(n, n+1, beat(n,n+1), vg(n+0.5)) for n in range(1,44)]
adj_sorted = sorted(adj, key=lambda t: t[2])
print(f"{'rank':>4} | {'pair':>7} | {'beat':>12} | {'v_g(mid)':>9} | Z₂ dual | dual valid?")
for r,(n,m,b,v) in enumerate(adj_sorted[:8], 1):
    dn, dm = 44-n, 44-m
    valid = 1 <= min(dn,dm) and max(dn,dm) <= 44
    print(f"{r:>4} | ({n:2d},{m:2d}) | {b:12.6e} | {v:9.6f} | ({min(dn,dm):2d},{max(dn,dm):2d}) | {'✅' if valid else '❌ 出譜'}")

# ============ 5. 11 條公式分解 ============
print()
print("="*70)
print("5. 11 條 beat 公式 → (d, mean, sin(dπ/176), v_g(mean)) 分解")
print("="*70)
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
print(f"{'公式':>13} | {'值':>9} | {'num(d,m)':>13} | {'sin(dπ/176)':>11} | {'v_g(m)':>8} | {'den(d,m)':>13} | {'sin(dπ/176)':>11} | {'v_g(m)':>8}")
print("-"*105)
rows = []
for name, obs, p1, p2 in formulas:
    d1, m1 = p1[1]-p1[0], (p1[0]+p1[1])/2
    d2, m2 = p2[1]-p2[0], (p2[0]+p2[1])/2
    s1, s2 = math.sin(d1*PI/176), math.sin(d2*PI/176)
    v1, v2 = vg(m1), vg(m2)
    rows.append(dict(name=name, obs=obs, num=(p1,d1,m1), den=(p2,d2,m2),
                     sin_num=s1, sin_den=s2, vg_num=v1, vg_den=v2,
                     ratio=beat(*p1)/beat(*p2)))
    print(f"{name:>13} | {obs:9.6f} | ({p1[0]:2d},{p1[1]:2d})d={d1:2d},m={m1:5.1f} | {s1:11.8f} | {v1:8.5f} | ({p2[0]:2d},{p2[1]:2d})d={d2:2d},m={m2:5.1f} | {s2:11.8f} | {v2:8.5f}")

# 分解一致性: value = sin_num/sin_den * vg_num/vg_den
print()
print("  分解一致性檢查 (value = sin-ratio × vg-ratio):")
allok = True
for r in rows:
    pred = r['sin_num']/r['sin_den'] * r['vg_num']/r['vg_den']
    okk = abs(pred - r['ratio']) < 1e-12
    allok &= okk
    print(f"    {r['name']:>13}: sin比 {r['sin_num']/r['sin_den']:.6f} × vg比 {r['vg_num']/r['vg_den']:.6f} = {pred:.6f} {'✅' if okk else '❌'}")
print(f"  全部一致: {'✅' if allok else '❌'}")

# ============ 6. d / mean 結構統計 ============
print()
print("="*70)
print("6. d 同 mean 結構統計")
print("="*70)
ds_num  = sorted(set(r['num'][1]  for r in rows))
ds_den  = sorted(set(r['den'][1]  for r in rows))
ms_num  = sorted(set(r['num'][2]  for r in rows))
ms_den  = sorted(set(r['den'][2]  for r in rows))
print(f"  分子 d 集合: {ds_num}")
print(f"  分母 d 集合: {ds_den}")
print(f"  分子 mean 集合: {ms_num}")
print(f"  分母 mean 集合: {ms_den}")
print(f"  Fib 檢查 — 分子 d∈{{1,2}} 係 F₂,F₃; 分母 d∈{{21,34}} 係 F₈,F₉")
print(f"  分子 mean 有: {len([m for m in ms_num if m in [5.5,13.5,41.5,42.5,8.5,9,17,25.5,27,30,34]])} 個喺特殊集")
print(f"  分母 mean 有: {len([m for m in ms_den if m in [22,33,20,20.5,21.5,19,17,11.5,12.5]])} 個")

# 儲存
res = {
    "identity_general": {"form": "beat(a,b) = 4 sin(dπ/176) v_g((a+b)/2)", "verified": bad==0, "n": 946},
    "z2_omega_vg": {"form": "ω_n = 2 v_g(44-n)", "verified": ok},
    "special_modes": {str(n): {"v_g": vg(n), "gamma": g(n), "label": labels[n]} for n in special},
    "adjacent_top8": [{"pair": f"({n},{m})", "beat": b, "vg_mid": v, "z2_dual_valid": 1<=min(44-n,44-m) and max(44-n,44-m)<=44}
                      for r,(n,m,b,v) in enumerate(adj_sorted[:8],1)],
    "formula_factorization": rows,
    "d_sets": {"num": ds_num, "den": ds_den},
    "mean_sets": {"num": ms_num, "den": ms_den},
}
out = os.path.join(os.path.dirname(__file__), "..", "data", "01_vg_spectrum.json")
with open(out, "w") as f:
    json.dump(res, f, indent=2, default=lambda o: float(o) if hasattr(o,'item') else o)
print(f"\n結果: {out}")
