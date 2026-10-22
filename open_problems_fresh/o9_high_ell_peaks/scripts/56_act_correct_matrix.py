#!/usr/bin/env python3
"""
O9-D12: ACT DR4 正確閉合矩陣 — deep/wide + 極化
==================================================
deep TT: 800.5/1100.5/1400.5 (m=3/5/7)
wide TT: 800.5/1150.5/1450.5 (m=3/5/7?)

deep 係 150x150 交叉, wide 係 100mJy 限制
deep 更乾淨 → 用 deep 做基準
"""
import numpy as np
import os

DATADIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
PYDIR = os.path.join(DATADIR, 'pyactlike', 'pyactlike', 'data')

print("="*80)
print("O9-D12: ACT DR4 正確閉合矩陣")
print("="*80)

cl = np.loadtxt(os.path.join(PYDIR, 'cl_cmb_ap.dat'))
bval = cl[:, 0]; X = cl[:, 1]
nbintt, nbinte, nbinee, nbinw = 40, 45, 45, 130

def D_from(b, X):
    return X * b*(b+1)/(2*np.pi)

# 全部 spectra
tt_d = D_from(bval[0:nbintt], X[0:nbintt])
tt_w = D_from(bval[nbinw:nbinw+nbintt], X[nbinw:nbinw+nbintt])
te_d = D_from(bval[nbintt:nbintt+nbinte], X[nbintt:nbintt+nbinte])
ee_d = D_from(bval[nbintt+nbinte:nbintt+nbinte+nbinee], X[nbintt+nbinte:nbintt+nbinte+nbinee])
bval_tt = bval[0:nbintt]

def find_peaks(b, D, lo, hi, thr):
    return [(b[j], D[j]) for j in range(1, len(D)-1)
            if lo < b[j] < hi and D[j] > D[j-1] and D[j] > D[j+1] and D[j] > thr]

# 閉合矩陣 (deep TT)
print("\n1. ACT DR4 deep TT 閉合矩陣:")
idcm = {1: 220, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1340, 7: 1412}
deep_peaks = find_peaks(bval_tt, tt_d, 600, 1600, 100)
# 對應 m: 800.5→3, 1100.5→5, 1400.5→7 (deep 冇 m=2,4,6)
m_map = {800: 3, 1100: 5, 1400: 7}
print(f"   {'m':>2} {'ACT':>7} {'IDCM':>6} {'dev':>7}")
for l, v in deep_peaks:
    rl = int(round(l))
    if rl in m_map:
        m = m_map[rl]
        dev = (l - idcm[m])/idcm[m]*100
        print(f"   {m:>2} {l:>7.1f} {idcm[m]:>6} {dev:>+6.2f}%")

# 極化閉合
print("\n2. ACT DR4 極化閉合 (deep):")
tt = [220, 537, 815, 1013, 1121, 1340, 1412]
pol = [(tt[i]+tt[i+1])/2 for i in range(len(tt)-1)]
print("   EE deep (400.5/700.5/1000.5/1300.5):")
ee_p = find_peaks(bval[nbintt+nbinte:nbintt+nbinte+nbinee], ee_d, 300, 1600, 0)
for l, v in ee_p[:5]:
    p = min(pol, key=lambda x: abs(x-l))
    dev = (l-p)/p*100
    print(f"      ℓ={l:.1f} vs {p:.0f} → dev={dev:+.1f}%")
print("   TE deep (600.5/950.5/1200.5/1550.5):")
te_p = find_peaks(bval[nbintt:nbintt+nbinte], te_d, 300, 1600, 0)
for l, v in te_p[:5]:
    p = min(pol, key=lambda x: abs(x-l))
    dev = (l-p)/p*100
    print(f"      ℓ={l:.1f} vs {p:.0f} → dev={dev:+.1f}%")

# 總結
print("\n3. 總結:")
print("   deep TT: m=3 (800.5, -1.2%), m=5 (1100.5, -1.8%), m=7 (1400.5, -0.8%)")
print("   → m=5 修正 1121 獲 deep 數據支持 (-1.8%)!")
print("   → m=7 1400.5 閉合 (-0.8%) — 之前誤判冇 m=7 峰!")
print()
print("   EE deep 極化: 400.5/700.5/1000.5/1300.5 (間距 300)")
print("   → EE 峰 700.5 vs IDCM P2=676 (+3.6%)")
print("   → EE 峰 1000.5 vs IDCM P4=1067 (-6.2%) — 需要檢查")
print()
print("   ★ 之前 scripts 41-51 用錯誤解析 (5×52), 峰位全錯!")
print("   ★ 正確解析: deep+wide, TT 40 bins 600-4125")
