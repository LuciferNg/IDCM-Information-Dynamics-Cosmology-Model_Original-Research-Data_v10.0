#!/usr/bin/env python3
"""
★ 全面光譜匹配: 946 拍頻 vs 所有已知常數
============================================
方法: 對每個拍頻值, check 係咪接近 (<0.1% 或 <0.001)
      已知物理常數、數學常數、IDCM 結構常數
"""
from math import pi, sin, sqrt, e
import csv

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

# 常數字典
constants = {
    # 物理常數 (PDG/Planck)
    "m_μ/m_τ": 0.05946, "m_s/m_d": 18.9, "n/p": 1.0/0.998622,
    "m_c/m_b": 1.275/4.18, "m_W/m_Z": 80.377/91.1876, "m_H/m_W": 125.25/80.377,
    "sin²θ_W": 0.223, "α_em": 1/137.036, "G_F×10⁵": 1.1663787,
    "Ω_m": 0.315, "Ω_Λ": 0.685, "H_0": 67.4, "Ω_b": 0.049,
    "Ω_DM/Ω_b": 5.35/0.049, "σ_8": 0.811, "n_s": 0.965,
    "τ_reion": 0.054, "Y_p": 0.245, "D/H×10⁵": 2.527,
    # 數學常數
    "π": pi, "e": e, "√2": sqrt(2), "√3": sqrt(3), "√5": sqrt(5),
    "φ": (1+sqrt(5))/2, "1/φ": 2/(1+sqrt(5)), "φ²": ((1+sqrt(5))/2)**2,
    "e/π": e/pi, "π/e": pi/e, "π²": pi**2, "e²": e**2,
    "ln(2)": 0.693147, "ln(π)": 1.14473, "π/2": pi/2, "π/3": pi/3,
    "π/4": pi/4, "π/6": pi/6, "2π": 2*pi, "√(π)": sqrt(pi),
    "√(2π)": sqrt(2*pi), "1/π": 1/pi, "1/e": 1/e,
    "2−√2": 2-sqrt(2), "√(2+√2)": sqrt(2+sqrt(2)), "√(2−√2)": sqrt(2-sqrt(2)),
    "sinc(π/2)": sin(pi/2)/(pi/2) if pi/2 != 0 else 1,
    # IDCM 結構常數
    "γ_1": 4*sin(pi/176)**2, "γ_44": 4*sin(44*pi/176)**2,
    "γ_88": 4*sin(88*pi/176)**2, "γ_11": 4*sin(11*pi/176)**2,
    "γ_33": 4*sin(33*pi/176)**2,
    "ω_1": 2*sin(pi/88), "ω_22": 2*sin(22*pi/88),
    "ω_44": 2*sin(44*pi/88), "λ_sync": 294.88,
    # 已知拍頻 (物理格)
    "phy_m_μ/τ": 1.12717067, "phy_m_s/d": 1.34282889, "phy_n/p": 0.81510847,
    "phy_c/s": 0.85074845, "phy_m_c/b": 1.28429395, "phy_u/d": 0.81257079,
    "phy_t/b": 0.59282105, "phy_m_H/W": 0.69935572, "phy_m_W/Z": 0.23318262,
}

# 讀 atlas 排除已知 label 格
labeled = set()
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r['label'].strip():
            labeled.add((int(r['n']), int(r['m'])))

print("="*72)
print("★ 全面光譜匹配: 未 label 拍頻 vs 常數")
print("="*72)
print(f"排除 {len(labeled)} 個已 label 格")
print()

matches = []
for (i,j) in pairs:
    if (i,j) in labeled: continue
    bv = beat(i,j)
    for cname, cv in constants.items():
        # 比值匹配 (0.5% 內)
        ratio = bv/cv
        if abs(ratio-1) < 0.005:
            matches.append((abs(ratio-1), i, j, bv, cname, cv, "比值"))
        # 值差匹配 (0.005 內)
        if abs(bv-cv) < 0.005:
            matches.append((abs(bv-cv), i, j, bv, cname, cv, "值差"))

matches.sort()
# 去重: 只顯示每對 (i,j) 最好嘅匹配
seen = set()
for diff, i, j, bv, cname, cv, mtype in matches:
    key = (i,j)
    if key not in seen:
        seen.add(key)
        pct = abs(bv/cv-1)*100
        print(f"  beat({i:2d},{j:2d}) = {bv:.8f}  ≈ {cname:20s} = {cv:.8f}  ({mtype} 差 {pct:.3f}%)")

print(f"\n總共 {len(seen)} 個匹配 (誤差 < 0.5%)")

print("\n" + "="*72)
print("2. ★ 最強匹配 (誤差 < 0.1%)")
print("="*72)
best = [m for m in matches if m[0] < 0.001]
seen_best = set()
for diff, i, j, bv, cname, cv, mtype in best:
    if (i,j) not in seen_best:
        seen_best.add((i,j))
        pct = abs(bv/cv-1)*100
        print(f"  beat({i:2d},{j:2d}) = {bv:.8f}  ≈ {cname:20s} = {cv:.8f}  (差 {pct:.4f}%)")
print(f"強匹配: {len(seen_best)} 個")