#!/usr/bin/env python3
"""O149 script 05 — v_g family 結構 + 最終統計
==============================================
1. 9 個 >floor 角: 最佳相鄰對 (正確計算) + 結構註釋
2. 4 個相鄰-numerator 公式: beat 單調性 vs 角大小
3. 多對一 family 測試: 贏家 pair 嘅 v_g 聚類
4. 最終閉合表: 11 角 × 鎖定狀態
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
T = [t[1] for t in targets]

print("="*78)
print("1. 9 個 >floor 角: 最佳相鄰對 (v_g ratio) + 結構")
print("="*78)
FLOOR = math.sin(PI/176)
print(f"  v_g floor (相鄰對 ratio 下限) = sin(π/176) = {FLOOR:.6f}")
print()
results = []
for name, t, dp1, dp2 in targets:
    if t < FLOOR:
        results.append((name, t, 'LADDER', None, None, 0.0, '兩因子鎖定 (k-ladder)'))
        continue
    best = None; bestd = 1e9
    for n in range(1,44):
        for m in range(1,44):
            if n == m: continue
            r = beat(n,n+1)/beat(m,m+1)
            d = abs(r-t)/t
            if d < bestd:
                bestd, best = d, (n,m,r)
    n_, m_, r = best
    note = f"v_g({n_}+½)/v_g({m_}+½) = {vg(n_+.5):.4f}/{vg(m_+.5):.4f}"
    # Z₂ dual 註釋
    du = (44-(n_+1), 44-n_); dv = (44-(m_+1), 44-m_)
    note += f" | dual ({min(du)},{max(du)})/({min(dv)},{max(dv)})"
    flag = '✅' if bestd < 0.01 else '✗'
    print(f"  {name:>13}: ({n_:2d},{n_+1:2d})/({m_:2d},{m_+1:2d}) = {r:.6f}  δ={bestd:.2e} {flag}")
    print(f"      {note}")
    results.append((name, t, 'ADJ', (n_,n_+1), (m_,m_+1), bestd, note))

print()
print("="*78)
print("2. 4 個相鄰-numerator 公式: beat 單調性 vs 角大小")
print("="*78)
adj_num = [
    ('sinθ₁₃(C)', 0.003508, (42,43)), ('V_ub(C)', 0.00369, (41,42)),
    ('V_cb(C)', 0.04182, (13,14)), ('tanθ₁₂(C)', 0.231604, (5,6)),
]
prev = None
mono = True
for name, t, p in adj_num:
    b = beat(*p)
    order = '' if prev is None else ('✅' if b < prev else '❌ 破壞')
    if prev is not None and not (b < prev): mono = False
    print(f"  {name:>12}: beat{p} = {b:.6e}  (角 {t:.6f})  {order}")
    prev = b
print(f"  單調性 (角越小 → numerator beat 越小): {'✅ 成立' if mono else '❌'}")
print(f"  注意: (42,43) 同 (41,42) 共享 42 — 頂部兩個 Z₂-valid 相鄰對")
print(f"  (43,44) 被排除: Z₂ dual (0,1) 出譜")

print()
print("="*78)
print("3. 多對一 family 測試: 分母 v_g 聚類")
print("="*78)
den_vg = {}
for name, t, dp1, dp2 in targets:
    m2 = (dp2[0]+dp2[1])/2
    den_vg[name] = (dp2, vg(m2))
# 聚類
clusters = {'SYNC √2/2 (22)': [], 'LADDER cos3π/8 (33)': [], '近-SYNC [19.5,21.5]': [],
            'mid [0.5,0.92]': [], '其他': []}
for name, (p, v) in den_vg.items():
    if abs(v - math.sqrt(2)/2) < 1e-9: clusters['SYNC √2/2 (22)'].append(name)
    elif abs(v - math.cos(3*PI/8)) < 1e-9: clusters['LADDER cos3π/8 (33)'].append(name)
    elif 19.5 <= (p[0]+p[1])/2 <= 21.5: clusters['近-SYNC [19.5,21.5]'].append(name)
    elif 0.5 <= v <= 0.92: clusters['mid [0.5,0.92]'].append(name)
    else: clusters['其他'].append(name)
for c, names in clusters.items():
    if names: print(f"  {c}: {', '.join(names)}")
n_clus = sum(len(v) for v in clusters.values() if v != clusters['其他'])
print(f"  → 11 個分母中 {n_clus} 個喺結構聚類 (SYNC/階梯/近-SYNC/mid)")

print()
print("="*78)
print("4. 最終閉合表")
print("="*78)
print(f"{'量':>13} | {'觀測':>9} | {'docs 公式':>20} | {'鎖定狀態':>24}")
print("-"*72)
status = {
    'CKM sinθ₁₃': '✅ k-ladder 先驗 (p=1e-9)',
    'CKM V_ub':   '✅ k-ladder 先驗 (p=1e-9)',
    'CKM V_cb':   '🟡 docs 後驗; R2 邊緣 1.1%',
    'CKM tanθ₁₂': '🟡 docs 後驗; R2 0.08%',
    'CKM tanθ₂₃': '🟡 docs 後驗; R2 0.50%',
    'CKM λ':      '🟡 docs 後驗; R2 0.22%',
    'CKM A':      '🟡 docs 後驗; R2 0.17%',
    'PMNS tanθ₁₂':'🟡 docs 後驗; R2 0.06%',
    'PMNS tanθ₂₃':'🟡 docs 後驗; R2 0.009%',
    'PMNS tanθ₂₃b':'🟡 docs 後驗; R2 0.003%',
    'PMNS sinθ₁₃':'🟡 docs 後驗; R2 0.93%',
}
for name, t, dp1, dp2 in targets:
    docs = f"({dp1[0]},{dp1[1]})/({dp2[0]},{dp2[1]})"
    print(f"{name:>13} | {t:9.6f} | {docs:>20} | {status[name]:>24}")

best_adj = []
for entry in results:
    if entry[2] == 'ADJ':
        n, t, s, num, den, dd, note = entry
        a, bb = num; c, d = den
        best_adj.append({"name": n, "target": t, "num": f"({a},{a+1})", "den": f"({c},{d})",
                         "delta": dd, "vg_num": vg(a+0.5), "vg_den": vg(c+0.5)})
res = {
    "floor": FLOOR,
    "best_adjacent": best_adj,
    "monotonicity": mono,
    "denominator_clusters": {c: v for c,v in clusters.items() if v},
    "final_status": {name: status[name] for name,_,_,_ in targets},
}
out = os.path.join(os.path.dirname(__file__), "..", "data", "05_family_structure.json")
with open(out, "w") as f:
    json.dump(res, f, indent=2, default=lambda o: float(o) if hasattr(o,'item') else o)
print(f"\n結果: {out}")
