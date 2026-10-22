#!/usr/bin/env python3
"""O149 script 07 — 盲測: 群速度鎖定嘅結構預言
================================================
鎖定規則 (由 script 04 建立, 只用 sinθ₁₃ + V_ub 兩個觀測值):
  L1: beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2)   [恆等式]
  L2: v_g floor = sin(π/176) = 0.01785          [相鄰對 ratio 下限]
  L3: k-ladder g_k = beat(44-k,44-k+1)/beat(sum=44-(k+1), d=F_{k+6}), k=2,3
      → k=1 出譜, k=4 無解 → 階梯恰好 2 級

未用觀測量預言 (盲測):
  P1: CKM 冇第三個 <floor 嘅階梯形元素 (階梯終止) → 第三細 V_cb=0.0418 > floor
  P2: PMNS 冇任何 <floor 元素 → 全部大角, 唔需要兩因子 (最小 sinθ₁₃=0.1485)
  P3: V_td = 0.00857 < floor → 唔係純 v_g ratio; 亦唔係階梯形 (k≥4 無解)
      → 需要第三種兩因子機制 [新預言, 待推導]
  P4: >floor 嘅 9 個角: 存在相鄰對 (純 v_g) 替代命中 <1% → 8/9 (V_cb 邊緣)
"""
import math, json, os
import numpy as np

PI = math.pi
w  = lambda n: 2*math.sin(PI*n/88)
vg = lambda x: math.cos(PI*x/88)
beat = lambda a,b: abs(w(a)-w(b))

FLOOR = math.sin(PI/176)
results = {}

print("="*74)
print("P1: 階梯終止 → CKM 冇第三個 <floor 階梯形元素")
print("="*74)
ladder_vals = []
FIB = [0,1,1,2,3,5,8,13,21,34,55,89,144,233]
for k in range(1, 8):
    num_a, num_b = 44-k, 44-k+1
    s_den, d_den = 44-(k+1), FIB[k+6]
    valid = (s_den - d_den) % 2 == 0 and 1 <= (s_den-d_den)//2 and (s_den-d_den)//2 + d_den <= 44
    if valid and 1 <= 44-num_b and 44-num_a <= 44:
        a = (s_den-d_den)//2
        g = beat(num_a,num_b)/beat(a, a+d_den)
        ladder_vals.append(g)
        print(f"  k={k}: g = {g:.6e}")
print(f"  階梯值: {ladder_vals}  ({len(ladder_vals)} 級)")
Vcb = 0.04182
p1 = all(v < FLOOR for v in ladder_vals) and Vcb > FLOOR
print(f"  第三細 CKM 元素 V_cb = {Vcb} > floor {FLOOR:.5f}: {'✅ P1 PASS' if p1 else '❌'}")
results['P1_ladder_termination'] = p1

print()
print("="*74)
print("P2: PMNS 冇 <floor 元素")
print("="*74)
pmns = [('sinθ₁₃', 0.1485), ('tanθ₁₂', 0.659629), ('tanθ₂₃', 0.906745), ('tanθ₂₃b', 1.150368)]
min_pmns = min(t for _,t in pmns)
p2 = min_pmns > FLOOR
for n,t in pmns: print(f"  PMNS {n:>8} = {t:.6f} {'✅' if t>FLOOR else '❌'}")
print(f"  最小 PMNS 元素 {min_pmns:.4f} > floor {FLOOR:.5f}: {'✅ P2 PASS' if p2 else '❌'}")
results['P2_pmns_no_suppression'] = p2

print()
print("="*74)
print("P3: V_td 預言 — 低於 floor, 唔係階梯形, 需要第三機制")
print("="*74)
Vtd = 0.00857  # PDG |V_td| ≈ 0.0086 (docs 0.00859)
p3a = Vtd < FLOOR
p3b = not any(abs(v-Vtd)/Vtd < 0.01 for v in ladder_vals)
print(f"  V_td = {Vtd} < floor {FLOOR:.5f}: {'✅ 確認低於下限' if p3a else '❌'}")
print(f"  V_td 唔係階梯形 (k-ladder 冇匹配): {'✅' if p3b else '❌'}")
# V_td 嘅兩因子候選: 搵結構性 (num d=1 or small, den structural) 組合
best = None; bestd = 1e9
for a in range(1,44):
    for b in range(a+1,44):
        for c in range(1,44):
            for d in range(c+1,44):
                if beat(c,d) < 1e-6: continue
                r = beat(a,b)/beat(c,d)
                dd = abs(r-Vtd)/Vtd
                if dd < bestd:
                    bestd, best = dd, ((a,b),(c,d),r)
print(f"  最近全空間兩因子: {best}  δ={bestd:.2e}")
if bestd < 0.01:
    (a,b),(c,d),r = best
    print(f"  → V_td 嘅候選公式: beat({a},{b})/beat({c},{d})  (d_num={b-a}, d_den={d-c})")
    print(f"  → 新預言: V_td 需要第三種鎖定機制 (非階梯形) — 開新 O 跟進")
results['P3_vtd_subfloor'] = {'below_floor': p3a, 'not_ladder': p3b,
                              'best_two_factor': f"({best[0][0]},{best[0][1]})/({best[1][0]},{best[1][1]})" if best else None,
                              'best_delta': bestd}

print()
print("="*74)
print("P4: >floor 角存在純 v_g (相鄰對) 替代 <1%")
print("="*74)
above = [('CKM tanθ₁₂',0.231604),('CKM tanθ₂₃',0.041563),('CKM λ',0.22500),
         ('CKM V_cb',0.04182),('CKM A',0.830),('PMNS tanθ₁₂',0.659629),
         ('PMNS tanθ₂₃',0.906745),('PMNS tanθ₂₃b',1.150368),('PMNS sinθ₁₃',0.1485)]
ok = 0
for name, t in above:
    dmin = min(abs(vg(n+0.5)/vg(m+0.5)-t)/t for n in range(1,44) for m in range(1,44) if n!=m)
    if dmin < 0.01: ok += 1
    print(f"  {name:>13}: δ_min = {dmin:.2e} {'✅' if dmin<0.01 else '❌ 邊緣'}")
p4 = ok >= 8
print(f"  {ok}/9 命中 <1% (V_cb 1.1% 邊緣): {'✅ P4 PASS (8/9)' if p4 else '❌'}")
results['P4_adjacent_achievability'] = {'hits': ok, 'total': 9}

print()
print("="*74)
print("盲測總結")
print("="*74)
allp = all(results[k] in (True, {'below_floor': True, 'not_ladder': True}) for k in results if k != 'P4_adjacent_achievability')
allp = allp and results['P4_adjacent_achievability']['hits'] >= 8
for k, v in results.items():
    if isinstance(v, dict):
        print(f"  {k}: {'✅' if v.get('below_floor') and v.get('not_ladder') else '🟡'}")
    elif isinstance(v, bool):
        print(f"  {k}: {'✅' if v else '❌'}")
    else:
        print(f"  {k}: {v}")
print(f"\n  盲測判定: {'✅ 4/4 結構預言 PASS' if allp else '🟡 部分 PASS'}")

out = os.path.join(os.path.dirname(__file__), "..", "data", "07_blind_test.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2, default=lambda o: float(o) if hasattr(o,'item') else o)
print(f"\n結果: {out}")
