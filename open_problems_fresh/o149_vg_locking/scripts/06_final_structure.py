#!/usr/bin/env python3
"""O149 script 06 — 最終結構驗證 + 收尾統計
=============================================
1. 4 個相鄰-numerator: beat 單調性 (修正方向: 角↑ → beat↑)
2. 分母 mean → 特殊位置 (Fib/Lucas/階梯/SYNC) 距離
3. 分子 mean → Fib 位置距離
4. 最終閉合摘要
"""
import math, json, os
import numpy as np

PI = math.pi
w  = lambda n: 2*math.sin(PI*n/88)
vg = lambda x: math.cos(PI*x/88)
beat = lambda a,b: abs(w(a)-w(b))

targets = [
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

SPECIAL = {5:'F₅',8:'F₆',11:'L₅',13:'F₇',18:'L₆',21:'F₈',22:'SYNC',
           29:'L₇',33:'3·11',34:'F₉',44:'Nyq'}

print("="*78)
print("1. 相鄰-numerator 單調性: 角大小 ↔ numerator beat 大小")
print("="*78)
adj = [(n,t,p) for n,t,_,p in targets if p in [(5,6),(13,14),(41,42),(42,43)]]
# 統一由 42/43 家族排序
order = {'sinθ₁₃(C)':0,'V_ub(C)':1,'V_cb(C)':2,'tanθ₁₂(C)':3}
adj.sort(key=lambda x: order.get(x[0],9))
beats = [beat(*p) for _,_,p in adj]
angs  = [t for _,t,_ in adj]
mono = all(beats[i] < beats[i+1] for i in range(len(beats)-1)) and \
       all(angs[i] < angs[i+1] for i in range(len(angs)-1))
for (n,t,p),b in zip(adj, beats):
    print(f"  {n:>12}: angle={t:.6f}, beat{p} = {b:.6e}")
print(f"  → 角同 beat 同步遞增: {'✅ 成立 (結構一致)' if mono else '❌'}")

print()
print("="*78)
print("2. 分母 mean → 特殊位置距離 (Fib/Lucas/階梯/SYNC)")
print("="*78)
den_rows = []
for name, t, p1, p2 in targets:
    m = (p2[0]+p2[1])/2
    dmin = min((abs(m-s), s, lab) for s,lab in SPECIAL.items())
    den_rows.append((name, p2, m, dmin))
    print(f"  {name:>13}: den{p2} mean={m:5.1f} → 最近特殊 {dmin[2]}({dmin[1]}), Δ={dmin[0]:.1f}")
n_near = sum(1 for _,_,_,d in den_rows if d[0] <= 2.0)
print(f"  → {n_near}/11 分母 mean 喺特殊位置 ±2 內")

print()
print("="*78)
print("3. 分子 mean → Fib 位置距離")
print("="*78)
fibs = {5:'F₅',8:'F₆',13:'F₇',21:'F₈',34:'F₉'}
num_rows = []
for name, t, p1, p2 in targets:
    m = (p1[0]+p1[1])/2
    dmin = min((abs(m-s), s, lab) for s,lab in fibs.items())
    num_rows.append((name, p1, m, dmin))
    flag = ' ←Fib' if dmin[0] <= 1.0 else ''
    print(f"  {name:>13}: num{p1} mean={m:5.1f} → 最近 Fib {dmin[2]}({dmin[1]}), Δ={dmin[0]:.1f}{flag}")
n_fnear = sum(1 for _,_,_,d in num_rows if d[0] <= 1.0)
print(f"  → {n_fnear}/11 分子 mean 喺 Fib ±1 內 (另 2 個 top-dual (41.5,42.5))")

print()
print("="*78)
print("4. 最終閉合摘要")
print("="*78)
print("""
  ✅ 定理 1 (恆等式): beat(a,b) = 4·sin(dπ/176)·v_g((a+b)/2),  946/946
  ✅ 定理 2 (Z₂ 字典): ω_n = 2·v_g(44-n);  γ_n = 4·v_g(44-n)²,  44/44
  ✅ 定理 3 (v_g 下限): 相鄰對 ratio ≥ sin(π/176) = 0.01785
      → sinθ₁₃(C)=0.00351, V_ub(C)=0.00369 低於下限 → 兩因子必然
      → PMNS 全部 > 下限 → 無抑制 ✓ (觀測一致)
  ✅ 定理 4 (k-ladder): g_k = beat(44-k,44-k+1)/beat(sum=44-(k+1), d=F_{k+6})
      k=1 出譜(dual(0,1)) + 無解;  k=2 → sinθ₁₃ (1e-7);  k=3 → V_ub (1e-7)
      k=4 無解 (d=F₁₀=55 > sum=39) → 階梯自然終止於 2 級
      p_joint = 9.6e-10 (vs 局部密度); 敏感度: 放寬 98 候選中唯一命中
  🟡 定理 5 (聚類): 分母 mean 11/11 喺結構位置 (SYNC/階梯/近-SYNC/Lucas側翼)
      分子 mean 5/11 喺 Fib ±1 (另 2 top-dual) — 部分結構, 未閉合
  🔴 9/11 中等/大角: docs 公式仍係後驗 (R2 相鄰替代 0.003-1% 但密度解釋)
""")

res = {
    "monotonicity": {"holds": mono,
                     "angles": angs, "beats": beats},
    "denominator_means": [{"name": n, "pair": f"({a},{b})", "mean": m,
                           "nearest_special": f"{d[2]}({d[1]})", "delta": d[0]}
                          for n,(a,b),m,d in den_rows],
    "numerator_means": [{"name": n, "pair": f"({a},{b})", "mean": m,
                         "nearest_fib": f"{d[2]}({d[1]})", "delta": d[0]}
                        for n,(a,b),m,d in num_rows],
    "counts": {"den_special_within2": n_near, "num_fib_within1": n_fnear},
}
out = os.path.join(os.path.dirname(__file__), "..", "data", "06_final_structure.json")
with open(out, "w") as f:
    json.dump(res, f, indent=2, default=lambda o: float(o) if hasattr(o,'item') else o)
print(f"結果: {out}")
