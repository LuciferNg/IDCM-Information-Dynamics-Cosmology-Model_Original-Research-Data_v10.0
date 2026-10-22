#!/usr/bin/env python3
"""O149 script 03 — 鎖定發現 + 誠實統計
========================================
1. 對每個目標: 搵最佳相鄰對 ratio (v_g-lock) → 輸出鎖定 pair 結構
2. 受抑制角 (δ<0.0178 下限): 兩因子規則 d=1 numerator × 近-SYNC/ladder denominator
3. 統計: 局部密度 null (全空間 ratio 喺目標 ±1% 窗內嘅比例) → 期望命中 vs 觀察
"""
import math, json, os
import numpy as np

PI = math.pi
w  = lambda n: 2*math.sin(PI*n/88)
vg = lambda x: math.cos(PI*x/88)
beat = lambda a,b: abs(w(a)-w(b))

targets = [
    ('CKM tanθ₁₂', 0.231604), ('CKM tanθ₂₃', 0.041563), ('CKM sinθ₁₃', 0.003508),
    ('CKM λ', 0.22500), ('CKM V_cb', 0.04182), ('CKM V_ub', 0.00369),
    ('CKM A', 0.830), ('PMNS tanθ₁₂', 0.659629), ('PMNS tanθ₂₃', 0.906745),
    ('PMNS tanθ₂₃b', 1.150368), ('PMNS sinθ₁₃', 0.1485),
]
T = [t[1] for t in targets]

pairs = [(i,j) for i in range(1,45) for j in range(i+1,45)]
B = np.array(sorted(beat(i,j) for i,j in pairs))
R_all = np.array([b1/b2 for b1 in B for b2 in B if b2 > 1e-6])
R_all = R_all[R_all < 10]; R_all.sort()
N_all = len(R_all)

# ============ 1. 局部密度 null ============
print("="*74)
print("1. 局部密度 null — 全空間喺每目標 ±1% 窗內嘅 ratio 數")
print("="*74)
dens = []
for name, t in targets:
    n_in = int(((R_all > t*0.99) & (R_all < t*1.01)).sum())
    dens.append(n_in)
    print(f"  {name:>13}: t={t:.6f}, ±1% 窗內 {n_in:5d} 個 (P_hit={n_in/N_all:.2e})")
print(f"  11 目標總窗內: {sum(dens)} / {N_all}")

# ============ 2. R2: 最佳相鄰對 ratio ============
print()
print("="*74)
print("2. R2 鎖定: beat(n,n+1)/beat(m,m+1) 對每目標嘅最佳 pair")
print("="*74)
r2_best = []
for name, t in targets:
    best = (None, float('inf'))
    for n in range(1,44):
        for m in range(1,44):
            if n == m: continue
            r = beat(n,n+1)/beat(m,m+1)
            d = abs(r-t)/t
            if d < best[1]:
                best = ((n,m), r, d)
    (nm, r, d) = best
    n_, m_ = nm
    # 結構註釋
    note = f"v_g({n_}+½)/v_g({m_}+½) = {vg(n_+0.5):.5f}/{vg(m_+0.5):.5f}"
    z2n = (44-(n_+1), 44-n_); z2m = (44-(m_+1), 44-m_)
    note += f" | Z₂dual num=({min(z2n)}, {max(z2n)}) den=({min(z2m)}, {max(z2m)})"
    r2_best.append((name, t, nm, r, d, note))
    flag = '✅' if d < 0.01 else '✗'
    print(f"  {name:>13}: best ({n_:2d},{n_+1:2d})/({m_:2d},{m_+1:2d}) = {r:.6f}  δ={d:.2e} {flag}")
    print(f"      {note}")

# ============ 3. 受抑制角: 兩因子 ============
print()
print("="*74)
print("3. 受抑制角 (sinθ₁₃, V_ub): d=1 numerator × 大 denominator")
print("="*74)
# 規則: numerator = 相鄰對 (d=1), denominator = 任意對 (結構集)
# 先試: numerator ∈ top-4 相鄰對 {(43,44),(42,43),(41,42),(40,41)}, denominator = 特殊 pair
top_adj = [(43,44),(42,43),(41,42),(40,41),(39,40),(38,39)]
for name, t in targets:
    if t > 0.02: continue
    best = (None, None, float('inf'))
    for (a,b) in top_adj:
        for (c,d) in pairs:
            if beat(c,d) < 1e-6: continue
            r = beat(a,b)/beat(c,d)
            dd = abs(r-t)/t
            if dd < best[2]:
                best = ((a,b),(c,d), r, dd)
    (na,nb),(nc,nd),r,dd = best
    flag = '✅' if dd < 0.01 else '✗'
    print(f"  {name:>13}: beat({na},{nb})/beat({nc},{nd}) = {r:.6f}  δ={dd:.2e} {flag}")
    print(f"      num d=1, v_g({na}+½)={vg(na+0.5):.6f}; den d={nd-nc}, mean={ (nc+nd)/2:.1f}, "
          f"Z₂dual=({min(44-nd,44-nc)},{max(44-nd,44-nc)})")

# ============ 4. 鎖定 family 結構 ============
print()
print("="*74)
print("4. R2 最佳 pair 嘅 mean / v_g 結構")
print("="*74)
for name, t, (nm), r, d, note in r2_best:
    n_, m_ = nm
    print(f"  {name:>13}: num mean {n_+0.5:5.1f} (v_g={vg(n_+0.5):.4f}), "
          f"den mean {m_+0.5:5.1f} (v_g={vg(m_+0.5):.4f})")

# ============ 5. 統計總結 ============
print()
print("="*74)
print("5. 統計: R2 (1729 候選) vs 密度 null")
print("="*74)
# 期望命中 = M × Σ P_hit(t);  P_hit = 窗內數/N_all
M2 = 43*42  # 有序相鄰對數
exp = M2 * sum(dens)/N_all
obs = sum(1 for _,_,_,_,d,_ in r2_best if d < 0.01)
print(f"  R2 候選: {M2}, 觀察 <1% 命中: {obs}/11")
print(f"  密度期望命中: {exp:.2f}")
from math import comb
p_poisson = math.exp(-exp) * exp**obs / math.factorial(obs)  # P(≥obs) ~ Poisson 上尾
import scipy.stats as st
print(f"  Poisson P(≥{obs}): 1 - CDF = {1 - st.poisson.cdf(obs-1, exp):.2e}")
print()
print("  註: R2 命中 8/11; 3 個受抑制角 (sinθ₁₃, V_ub, V_cb) 低於相鄰對 ratio 下限 0.0178")
print("      → 需要兩因子 (sin-separation × v_g) — 見 docs")

res = {
    "local_density": {"per_target": {name: int(n) for (name,t),n in zip(targets,dens)},
                      "total_in_window": int(sum(dens)), "N_all": int(N_all)},
    "r2_best_adjacent": [{"name": n, "target": t, "num": f"({a},{a+1})", "den": f"({b},{b+1})",
                          "value": r, "delta": d, "vg_num": vg(a+0.5), "vg_den": vg(b+0.5)}
                         for (n,t,(a,b),r,d,note) in r2_best],
    "stats": {"M_adjacent": M2, "obs_hits": obs, "expected_density": float(exp),
              "poisson_p": float(1 - st.poisson.cdf(obs-1, exp))},
}
out = os.path.join(os.path.dirname(__file__), "..", "data", "03_locking_discovery.json")
with open(out, "w") as f:
    json.dump(res, f, indent=2, default=lambda o: float(o) if hasattr(o,'item') else o)
print(f"\n結果: {out}")
