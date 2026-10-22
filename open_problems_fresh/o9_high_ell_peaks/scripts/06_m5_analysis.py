#!/usr/bin/env python3
"""
O9: m=5 異常深入分析 + 峰序列結構
===================================
問題: IDCM m=5 預測 1199, 但 Planck binned 峰喺 1121-1124, CAMB 1129
     m=4 (1014) 同 m=6 (1340) 完美閉合, 點解 m=5 偏離 6%?

假設:
A. m=5 峰其實喺 1124 (Planck/SPT-3G 一致) → IDCM 公式 m=5 錯
B. 1199 有弱峰 (SPT-3G 1174 顯示 1160.8 相對高) → 峰「分裂」?
C. 1124 係「額外」峰 (m=4.5), 1199 先係 m=5

檢查:
1. Planck 喺 1121/1199 附近詳細形狀
2. SPT-3G 喺 1124/1174/1224 嘅形狀 (1199 係咪 saddle?)
3. 峰間距 Δℓ 結構: IDCM 預測 317/273/204/185/141/72
   觀測: 1014→1124? 1124→1338? 
4. 若 m=5 改用 1124, 峰間距序列係咪更規律?
"""
import numpy as np
import math as _m
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def idcm_peak(m):
    return 44*(33 - _m.comb(9-m, 2)) + (((m-1)*9) % 25)

print("="*78)
print("O9: m=5 異常深入分析")
print("="*78)

# ---------- 1. IDCM 公式結構 ----------
print("\n1. IDCM 公式逐項:")
for m in range(1, 8):
    N_int = 33 - _m.comb(9-m, 2)
    frac = ((m-1)*9) % 25
    print(f"   m={m}: 44×{N_int} + {frac} = {44*N_int+frac}")

print("\n   峰間距 (IDCM):")
preds = [idcm_peak(m) for m in range(1,8)]
for i in range(6):
    print(f"   Δℓ_{i+1} = {preds[i+1]-preds[i]}")

# ---------- 2. Planck 詳細形狀 (1100-1250) ----------
print("\n2. Planck binned 1100-1250 詳細:")
planck = np.loadtxt(os.path.join(DATADIR, 'planck_tt.txt'))
ell_p = planck[:,0].astype(int); C_p = planck[:,1]
for i, l in enumerate(ell_p):
    if 1090 <= l <= 1260:
        D = C_p[i]*l*(l+1)/(2*np.pi)
        print(f"   ℓ={l:5d}  D_ℓ={D:8.1f}")

# ---------- 3. SPT-3G 1124/1174/1224 形狀 ----------
print("\n3. SPT-3G D1 1124-1324 (1199 附近):")
bdp = np.loadtxt(os.path.join(DATADIR, 'spt3g_tne_bdp.txt'))
spec_list = [
    ('TT 90x90',52), ('TE 90x90',72), ('EE 90x90',72), ('TT 90x150',52),
    ('TE 90x150',72), ('TE 150x90',72), ('EE 90x150',72), ('TT 90x220',52),
    ('TE 90x220',72), ('TE 220x90',72), ('EE 90x220',72), ('TT 150x150',52),
    ('TE 150x150',72), ('EE 150x150',72), ('TT 150x220',52), ('TE 150x220',72),
    ('TE 220x150',72), ('EE 150x220',72), ('TT 220x220',52), ('TE 220x220',72),
    ('EE 220x220',72),
]
idx = 0
for name, n in spec_list:
    if name == 'TT 150x150':
        tt150 = bdp[idx:idx+n]
        break
    idx += n
win = np.loadtxt(os.path.join(DATADIR, 'spt_tt150_windows.txt'))
ell_w = win[:, 0]; W = win[:, 1:]
bin_centers = np.array([(ell_w * W[:,b]).sum()/W[:,b].sum() for b in range(W.shape[1])])

for i in range(len(bin_centers)):
    if 1070 <= bin_centers[i] <= 1350:
        d = tt150[i]
        # 斜率
        slope = ""
        if i > 0 and i < len(bin_centers)-1:
            slope = "↑" if tt150[i] > tt150[i-1] else "↓"
        print(f"   ℓ={bin_centers[i]:6.0f}  D_ℓ={d:8.1f}  {slope}")

# ---------- 4. 峰間距結構 ----------
print("\n4. 峰間距序列 (觀測 vs IDCM):")
# 觀測峰 (Planck bin 中心, 主要峰)
obs_peaks = [536, 815, 1013, 1121, 1337, 1400, 1733]
print("   觀測峰:", obs_peaks)
obs_dl = np.diff(obs_peaks)
print("   觀測 Δℓ:", obs_dl)
print("   IDCM Δℓ:", [preds[i+1]-preds[i] for i in range(6)])

# ---------- 5. 關鍵問題: m=5 係 1124 定 1199? ----------
print("\n5. m=5 峰位分析:")
print("   IDCM 公式: 1199 (44×27+11)")
print("   Planck: 1121 (bin 中心) / 1124 (cubic 內插)")
print("   SPT-3G: 1124 (局部極大, D=1235.3)")
print("   CAMB: 1129")
print()
print("   → 三數據一致指向 1121-1129 區間有峰, 但 1199 冇任何數據支持!")
print("   → m=5 嘅 1199 預測需要修正?")

# ---------- 6. 峰序列重新檢視: 1124 係咪 m=5? ----------
print("\n6. 若 m=5=1124, 峰間距: 1014→1124 = 110, 1124→1338 = 214")
print("   IDCM 預測: 1014→1199 = 185, 1199→1340 = 141")
print("   觀測: 1014→1124 = 110 (vs IDCM 185)")
print("   觀測: 1124→1338 = 214 (vs IDCM 141)")
print()
print("   ⚠️ 有趣: 110 + 214 = 324 ≈ 317+7?")
print("   而 317 (IDCM Δ₁) vs 110+214=324 — 差 7")
print()
print("   另一視角: 1014→1124→1338→1401")
print("   間距: 110, 214, 63")
print("   IDCM 三角形數間距: 317, 273, 204, 185, 141, 72")
print("   如果 m=4 同 m=6 閉合 (1014, 1338), 中間 1124 係咩?")
print("   → 1124 可能係「半峰」/ harmonic 或 m=5 公式需含 110 項")
