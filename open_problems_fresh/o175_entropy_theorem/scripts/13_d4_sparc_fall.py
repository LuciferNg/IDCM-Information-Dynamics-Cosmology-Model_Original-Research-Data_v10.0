#!/usr/bin/env python3
"""
O175 script 13 — D4 攻堅: SPARC Fall 關係帶測量 (data_gated_unlock)
===================================================================
數據: SPARC Lelli+16 (J/AJ/152/157) table1 + table2 (VizieR CDS)
目標: ① Fall 關係 log j_star vs log M_star 斜率/帶 [0.52, 0.64]
      ② IDCM j_spec = 19,867 km/s·kpc 坐喺帶嘅位置
"""
import numpy as np

# --- 讀 table1 (fixed-width: Name 1-11, L3.6 41-47, Rdisk 72-76, Vflat 101-105) ---
rows = []
with open("SPARC_Lelli16.mrt" if False else "table1.dat") as f:
    for line in f:
        if len(line) < 105: continue
        try:
            name = line[0:11].strip()
            l36 = float(line[40:47])     # L3.6 [10^9 Lsun]
            rd  = float(line[71:76])     # Rdisk kpc
            vf  = float(line[100:105])   # Vflat km/s
            qual = int(line[112:115]) if len(line) > 112 else 3
            if rd > 0 and vf > 0 and l36 > 0:
                rows.append((name, l36, rd, vf, qual))
        except (ValueError, IndexError):
            continue

print(f"SPARC 星系數: {len(rows)} (qual<=2: {sum(1 for r in rows if r[4]<=2)})")

# --- 質量 + 比角動量 ---
ML = 0.5   # 3.6μm 質量光度比 (Lelli+16)
# j_star ≈ 2·V_flat·R_d (disk 主導近似, Romanowsky & Fall 12)
data = []
for name, l36, rd, vf, qual in rows:
    Mstar = l36 * ML * 1e9            # M_sun
    j = 2.0 * vf * rd                 # km/s·kpc
    data.append((np.log10(Mstar), np.log10(j), qual, name))

arr = np.array([[d[0], d[1], d[2]] for d in data])
m_all, j_all = arr[:,0], arr[:,1]

# --- Fall 關係擬合 (高質量樣本 qual<=2, M>1e9) ---
mask = (arr[:,2] <= 2) & (m_all > 9.0)
if mask.sum() > 10:
    A = np.vstack([np.ones(mask.sum()), m_all[mask]]).T
    coef, res, *_ = np.linalg.lstsq(A, j_all[mask], rcond=None)
    slope, intercept = coef[1], coef[0]
    pred = A @ coef
    resid = j_all[mask] - pred
    rms = np.sqrt(np.mean(resid**2))
    print(f"Fall 擬合 (N={mask.sum()}): slope = {slope:.3f} ± {rms/np.sqrt(mask.sum()):.3f}, "
          f"intercept = {intercept:.2f}")
    print(f"  斜率 vs 帶 [0.52, 0.64]: {'✓ 帶內' if 0.52 <= slope <= 0.64 else '✗ 帶外'}")
    ok_fall = (0.52 <= slope <= 0.64)
else:
    ok_fall = False
    print("樣本不足")

# --- IDCM j_spec 對比 ---
J_IDCM = 19867.0
logj_id = np.log10(J_IDCM)
# Fall 帶喺 log M 空間: j = 10^{3.2}·(M/1e10)^{0.6} (Fall+13)
# j_spec 對應質量
M_id = 1e10 * (J_IDCM / 10**3.2)**(1/0.6)
print(f"IDCM j_spec = {J_IDCM} km/s·kpc (log j = {logj_id:.3f})")
print(f"  對應 Fall+13 (j=10^3.2 M_10^0.6): M_star = {M_id:.2e} M☉ (log M = {np.log10(M_id):.2f})")

# 數據點覆蓋: IDCM 預言質量有冇 SPARC 星系
near = [d for d in data if abs(d[0] - np.log10(M_id)) < 0.5]
print(f"  附近 (ΔlogM<0.5) SPARC 星系: {len(near)} 個")
for d in sorted(near, key=lambda x: abs(x[0]-np.log10(M_id)))[:5]:
    print(f"    {d[3]}: logM={d[0]:.2f}, logj={d[1]:.2f}, j={10**d[1]:.0f} km/s·kpc")

# j_spec 對比: SPARC j 分佈有冇星系 j ≈ 19867?
jvals = np.array([d[1] for d in data])
print(f"  SPARC j 範圍: {10**jvals.min():.0f} - {10**jvals.max():.0f} km/s·kpc")
print(f"  IDCM j_spec 喺 SPARC 範圍內: {'✓' if 10**jvals.min() < J_IDCM < 10**jvals.max() else '✗'}")

print(f"\nRESULT: {'Fall 帶測量完成' if ok_fall else 'Fall 帶測量 (斜率帶外)'} + j_spec 對比完成")
