#!/usr/bin/env python3
"""
深度驗證: 9 對偶點 + 近值點 — 有冇 IDCM 對應?
==============================================
1. 檢查 master_atlas 有冇 label
2. 比對已知物理常數
3. 搵 O 系列文件參考
"""
from math import pi, sin
import csv

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))

# 讀 atlas
rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']),
                     's': int(r['s']), 'label': r['label'].strip()})
pairs = [r for r in rows if r['n'] < r['m']]

# 已知物理拍頻
phys = {
    (1,18): "m_μ/m_τ", (1,22): "m_s/m_d", (7,20): "n/p",
    (8,22): "c/s", (8,33): "m_c/m_b", (10,24): "u/d",
    (19,33): "t/b", (19,38): "m_H/m_W", (30,41): "m_W/m_Z"
}
phys_set = set(phys.keys())

print("="*72)
print("1. 驗證 A: 9 對偶點嘅 atlas label")
print("="*72)
for (i,j), pname in sorted(phys.items(), key=lambda x: x[0][0]):
    di, dj = 44-j, 44-i
    if di >= dj: continue
    pv = beat(i,j)
    dv = beat(di, dj)
    # 檢查 atlas
    label = ""
    for r in rows:
        if r['n'] == di and r['m'] == dj and r['label']:
            label = r['label']
            break
    print(f"  {pname:20s} ({i:2d},{j:2d}) beat={pv:.8f}")
    print(f"  → 對偶 ({di:2d},{dj:2d}) beat={dv:.8f}  label={label if label else '無'}")

print("\n" + "="*72)
print("2. 驗證 B: 近值點 (diff<0.001) 嘅 atlas label")
print("="*72)
pairs_list = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]
for (p_i,p_j), pname in phys.items():
    pv = beat(p_i,p_j)
    for (i,j) in pairs_list:
        if (i,j) in phys_set or (i,j) == (p_i,p_j): continue
        bv = beat(i,j)
        diff = abs(bv-pv)
        if diff < 0.001:
            label = ""
            for r in rows:
                if r['n'] == i and r['m'] == j and r['label']:
                    label = r['label']
                    break
            print(f"  {pname:20s} ≈ beat({i:2d},{j:2d})={bv:.8f} 差={diff:.6f}  label={label if label else '無'}")

print("\n" + "="*72)
print("3. 驗證 C: 對偶點 beat 值 vs 已知物理常數")
print("="*72)
# 9 對偶點嘅 beat 值
dual_vals = {}
for (i,j), pname in phys.items():
    di, dj = 44-j, 44-i
    if di >= dj: continue
    dual_vals[(di,dj)] = beat(di, dj)

# 已知物理常數比值 (PDG)
constants = {
    "m_μ/m_τ": 0.05946,      # PDG
    "m_s/m_d": 18.9,          # PDG ratio
    "n/p": 1.001378,          # free neutron decay
    "m_c/m_b": 0.082,         # PDG
    "m_W/m_Z": 0.8815,        # PDG
    "m_H/m_W": 0.778,         # PDG
    "V_us": 0.2243,           # CKM
    "V_cb": 0.0410,           # CKM
    "V_ub": 0.00382,          # CKM
    "sin²θ_W": 0.223,         # Weinberg
    "α_em": 1/137.036,        # fine structure
    "G_F": 1.1663787e-5,      # Fermi
    "Ω_DM/Ω_b": 6.5,          # 13/2
    "Ω_m": 0.315,             # Planck
    "H_0": 67.4,              # Planck km/s/Mpc
    "λ_sync": 294.88,         # IDCM
    "E_sync": 61.5,           # IDCM
    "γ_44": 2.0,              # self-loop
    "2−√2": 0.58578644,       # beat(22,44)
    "√2": 1.41421356,         # sqrt(2)
    "φ": 1.61803399,          # golden ratio
    "π": 3.14159265,          # pi
    "e": 2.71828183,          # natural log
}

print("對偶點 beat 值 vs 已知常數 (比值差 < 1%):")
for (di,dj), dv in sorted(dual_vals.items(), key=lambda x: x[1]):
    print(f"\n  beat({di:2d},{dj:2d}) = {dv:.8f}")
    for name, val in sorted(constants.items(), key=lambda x: abs(dv/x[1]-1)):
        ratio = dv/val
        if abs(ratio-1) < 0.01:
            print(f"    ≈ {name:15s} = {val:.8f}  (差 {abs(dv/val-1)*100:.3f}%)")
        elif abs(dv-val) < 0.001:
            print(f"    ≈ {name:15s} = {val:.8f}  (值差 {abs(dv-val):.6f})")