#!/usr/bin/env python3
"""盲測: 946 個拍頻隨機抽一個, 全功能分析"""
import numpy as np, random, json
from math import pi, sin, sqrt, gcd, cos

# ---- 固定 seed 盲測抽籤 ----
random.seed(20260825)  # 今日日期, 無預設
N = 44
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]
assert len(pairs) == 946, f"expected 946, got {len(pairs)}"

i, j = random.choice(pairs)
omega = lambda n: 2*sin(pi*n/88)
w_i, w_j = omega(i), omega(j)
beat = abs(w_i - w_j)

# ---- degree of omega_n ----
def deg_omega(n):
    # omega_n = 2sin(pi n/88) = 2cos(pi(44-n)/88), degree = phi(176/gcd(|44-n|,176))/2
    from sympy import totient
    d = abs(44-n)
    g = gcd(d, 176)
    return int(totient(176//g)//2)

# ---- γ_n = 4sin²(πn/88) (能量) ----
gamma = lambda n: 4*sin(pi*n/88)**2

# ---- 已知 catalog: CKM/PMNS formulas ----
# tan(θ12) = beat(5,6)/beat(19,25), tan(θ23)=beat(33,35)/beat(3,22), sin(θ13)=beat(42,43)/beat(10,31)
# V_us = beat(25,35)/beat(6,37), V_cb=beat(13,14)/beat(6,37), V_ub=beat(41,42)/beat(3,37), A=beat(16,35)/beat(10,28)
# PMNS tanθ12=beat(4,13)/beat(9,25), tanθ23=beat(11,23)/beat(12,26), sinθ13=beat(25,29)/beat(3,20)
ckm = {
 "tanθ12_CKM": ((5,6),(19,25)),
 "tanθ23_CKM": ((33,35),(3,22)),
 "sinθ13_CKM": ((42,43),(10,31)),
 "V_us":        ((25,35),(6,37)),
 "V_cb":        ((13,14),(6,37)),
 "V_ub":        ((41,42),(3,37)),
 "A_CKM":       ((16,35),(10,28)),
 "tanθ12_PMNS": ((4,13),(9,25)),
 "tanθ23_PMNS": ((11,23),(12,26)),
 "sinθ13_PMNS": ((25,29),(3,20)),
}
# 6 個閉合根式
closed = {(11,22):"√2−√(2−√2)", (11,33):"√(2+√2)−√(2−√2)", (11,44):"2−√(2−√2)",
          (22,33):"√(2+√2)−√2", (22,44):"2−√2", (33,44):"2−√(2+√2)"}

result = {
 "drawn": [i,j],
 "omega": [round(w_i,10), round(w_j,10)],
 "beat": round(beat, 10),
 "beat/w1": round(beat/omega(1), 8),
 "degree_i": deg_omega(i), "degree_j": deg_omega(j),
 "gamma_i": round(gamma(i),8), "gamma_j": round(gamma(j),8),
 "gamma_sum": round(gamma(i)+gamma(j), 8),
 "gamma_symmetry_44": round(gamma(44-i),8),
}

# 對稱: beat(i,j) 與鏡像 (44-i,44-j)?
ip, jp = 44-i, 44-j
if 1 <= ip <= 44 and 1 <= jp <= 44 and ip != jp:
    beat_mirror = abs(omega(min(ip,jp)) - omega(max(ip,jp)))
    result["mirror_pair"] = [ip, jp]
    result["beat_mirror"] = round(beat_mirror,10)
    result["mirror_equal"] = abs(beat - beat_mirror) < 1e-12
else:
    result["mirror_pair"] = None

# 閉合根式?
if (i,j) in closed: result["closed_form"] = closed[(i,j)]
else: result["closed_form"] = None

# catalog 角色?
roles = []
key = (i,j)
for name, (num, den) in ckm.items():
    if num == key: roles.append(f"{name} 分子")
    if den == key: roles.append(f"{name} 分母")
result["catalog_roles"] = roles

# 物理常數掃描: beat 值與已知常數比對 (sin of angles, 質量比, mixing)
scan = {}
# sin²θ13, sinθ13, tanθ12, tanθ23, sinθC 等
targets = {
 "sinθ13(0.02225)": 0.02225, "sin²θ13(0.02225)": 0.02225,
 "sinθC(0.225)": 0.225, "V_us(0.2243)": 0.2243, "V_cb(0.0422)": 0.0422,
 "V_ub(0.00394)": 0.00394, "m_e/M_p": 0.000544617,
 "α(1/137)": 1/137, "Ω_DM/Ω_b=13/2?": 6.5, "3/2": 1.5, "φ⁻¹(0.618)": (sqrt(5)-1)/2,
 "√2/2": sqrt(2)/2, "√3/2": sqrt(3)/2, "1/√2": 1/sqrt(2),
}
# beat 絕對值掃描 (beat 介乎 0~2)
for name, val in targets.items():
    if abs(val) < 2.5:
        rel = abs(beat - val)/val
        if rel < 0.02:
            scan[name] = round(rel*100, 3)
result["numeric_hits(<2%)"] = scan

# 無理數性: 946 全無理已證 (skill Theorem A), 記錄 drawn pair 係咪已驗證
# 特殊結構: i+j 或 |i-j| 有咩含義?
result["i+j"] = i+j
result["|i-j|"] = abs(i-j)
result["i*j"] = i*j

print(json.dumps(result, indent=2, ensure_ascii=False))
