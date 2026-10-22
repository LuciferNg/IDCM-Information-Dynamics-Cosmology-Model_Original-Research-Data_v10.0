#!/usr/bin/env python3
"""O146 §10 獨立驗證器 — 唔 import 97_bds_audit.py 任何函數
==========================================================
由原始定義重算 §10 審計所有數值:
(A) 83 萬拍頻比密度 (B) 隨機 vs 真實 δ_min (C) 分子/分母 rank
(D) d=1 超額超幾何 p (E) 群速度恆等式
"""
import math
import numpy as np

PASS = 0
FAIL = 0
rows = []
def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

w = lambda n: 2*math.sin(math.pi*n/88)
beat = lambda i,j: abs(w(i)-w(j))

# ============ (A) 拍頻比集合密度 ============
pairs = [(i,j) for i in range(1,45) for j in range(i+1,45)]
B = np.array(sorted(beat(i,j) for i,j in pairs))
R = np.array([b1/b2 for b1 in B for b2 in B if b2 > 1e-6])
R = R[R < 10]
R.sort()
n_R = len(R)
med_spacing = np.median(np.diff(R))
check("(A) 拍頻比數量 ≈ 831,713", abs(n_R - 831713) < 100, f"n={n_R}")
check("(A) 平均間距中位數 ≈ 2.62e-6", abs(med_spacing - 2.62e-6) < 0.1e-6,
      f"{med_spacing:.2e}")

# ============ (B) 隨機 vs 真實 δ_min ============
rng = np.random.default_rng(42)
targets = rng.uniform(0.01, 2.0, 2000)
idx = np.searchsorted(R, targets)
idx = np.clip(idx, 1, len(R)-1)
d_rand = np.minimum(np.abs(R[idx]-targets), np.abs(R[idx-1]-targets))

real = [0.231604, 0.041563, 0.003508, 0.225, 0.04182, 0.00369, 0.83,
        0.659629, 0.906745, 1.150368, 0.1485]
idx = np.searchsorted(R, np.array(real))
idx = np.clip(idx, 1, len(R)-1)
d_real = np.minimum(np.abs(R[idx]-np.array(real)), np.abs(R[idx-1]-np.array(real)))

med_rand = np.median(d_rand)
med_real = np.median(d_real)
check("(B) 隨機 δ_min ≈ 1.26e-6", abs(med_rand - 1.26e-6) < 0.1e-6, f"{med_rand:.2e}")
check("(B) 真實 δ_min ≈ 4.60e-7", abs(med_real - 4.60e-7) < 0.5e-7, f"{med_real:.2e}")
check("(B) 比例 ≈ 2.7x (無顯著)", 2.0 < med_rand/med_real < 3.5,
      f"{med_rand/med_real:.1f}x")

# ============ (C) 分子/分母 rank ============
formulas = [
    ('CKM tanθ₁₂', 0.231604, (5,6), (19,25)),
    ('CKM tanθ₂₃', 0.041563, (33,35), (3,22)),
    ('CKM sinθ₁₃', 0.003508, (42,43), (10,31)),
    ('CKM λ', 0.22500, (25,35), (6,37)),
    ('CKM V_cb', 0.04182, (13,14), (6,37)),
    ('CKM V_ub', 0.00369, (41,42), (3,37)),
    ('CKM A', 0.830, (16,35), (10,28)),
    ('PMNS tanθ₁₂', 0.659629, (4,13), (9,25)),
    ('PMNS tanθ₂₃', 0.906745, (11,23), (12,26)),
    ('PMNS tanθ₂₃b', 1.150368, (4,14), (22,44)),
    ('PMNS sinθ₁₃', 0.1485, (25,29), (3,20)),
]
num_ranks = [np.searchsorted(B, beat(*p[2]))/946*100 for p in formulas]
den_ranks = [np.searchsorted(B, beat(*p[3]))/946*100 for p in formulas]
n_lt = sum(1 for a,b in zip(num_ranks,den_ranks) if a<b)
med_num = np.median(num_ranks)
med_den = np.median(den_ranks)
check("(C) 分子 rank 中位數 ≈ 17%", abs(med_num-17) < 3, f"{med_num:.0f}%")
check("(C) 分母 rank 中位數 ≈ 76%", abs(med_den-76) < 5, f"{med_den:.0f}%")
check("(C) 分子<分母 10/11", n_lt == 10, f"{n_lt}/11")

# ============ (D) d=1 超額超幾何 ============
used_pairs = [p for _,_,p1,p2 in formulas for p in (p1,p2)]
n_d1 = sum(1 for i,j in used_pairs if abs(i-j)==1)
from math import comb
k_obs = n_d1
n_tot = len(used_pairs)
p_hyper = sum(comb(43,k)*comb(903,n_tot-k)/comb(946,n_tot) for k in range(k_obs, n_tot+1))
check("(D) d=1 對 = 4", n_d1 == 4, f"{n_d1}/22")
check("(D) 超幾何 p ≈ 0.015", 0.005 < p_hyper < 0.03, f"p={p_hyper:.4f}")

# ============ (E) 群速度恆等式 ============
ok_vg = all(abs(beat(n,n+1) - 4*math.sin(math.pi/176)*math.cos((2*n+1)*math.pi/176)) < 1e-12
            for n in range(1,44))
check("(E) beat(n,n+1)=4sin(π/176)cos((2n+1)π/176) 43/43", ok_vg)

# ============ (F) docs 公式重算 ============
# 驗證「docs 列嘅 IDCM 值」=「beat 比重算值」(公式冇打錯, 一致到 1e-10)
# docs 誤差欄係絕對差 vs PDG: CKM <1e-6, PMNS 3.4e-6/3.3e-6 級
docs_vals = {
    'CKM tanθ₁₂': 0.2316035403, 'CKM tanθ₂₃': 0.0415626453,
    'CKM sinθ₁₃': 0.0035074294, 'CKM λ': 0.2250008938,
    'CKM V_cb': 0.0418203954, 'CKM V_ub': 0.0036910176, 'CKM A': 0.8299998703,
    'PMNS tanθ₁₂': 0.6596255406, 'PMNS tanθ₂₃': 0.9067445022,
    'PMNS tanθ₂₃b': 1.1503651393, 'PMNS sinθ₁₃': 0.1484996509,
}
for name, obs, p1, p2 in formulas:
    pred = beat(*p1)/beat(*p2)
    docv = docs_vals[name]
    check(f"(F) {name} = docs 值", abs(pred-docv) < 1e-10,
          f"{pred:.10f} vs docs {docv:.10f}")

print("="*70)
print("  O146 §10 獨立驗證 (B(d,s) 審計)")
print("="*70)
for name, ok, detail in rows:
    print(f"  {'✅' if ok else '🔴'} {name:52s} {detail}")
print("-"*70)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
print(f"  總判定: {'✅ 全部一致' if FAIL==0 else '🔴 有偏差'}")
