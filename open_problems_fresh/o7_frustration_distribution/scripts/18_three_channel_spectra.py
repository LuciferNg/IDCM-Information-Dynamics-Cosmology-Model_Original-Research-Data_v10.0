#!/usr/bin/env python3
"""
O7 — 18_three_channel_spectra.py (2026-10-11)
====================================================================
O7/natural-write-closure 第四輪: 三通道 ℓ 譜對比 (60 節點 / 88 透明 / 32 阻挫)
====================================================================
目標: 承接 docs/05 嵌入 reformulation (k↔ℓ 譜映射). 用 O182 現成數據
      (temps2_SMICA_4.17deg.json: A5_60 / G88 / G32frust / G120_all):

  C1. 60 節點場球面 ℓ 譜 — 對照 (應重現 ℓ=3 主導, docs/05 S2)
  C2. 88 透明邊中點場 ℓ 譜 — 透明通道 (CMB 穿過唔改, O21)
  C3. 32 阻挫邊中點場 ℓ 譜 — 不透明通道 (寫入通道, O21)
  C4. 120 全邊中點場 ℓ 譜 — 對照
  C5. odd/even ℓ 能量比 × 三通道 — k↔ℓ 映射第一線索
      (O162 R6: 調律者 cos 屏 = even k 驅動, P_odd=0 — 對球面側意味?)
  C6. k↔ℓ 映射候選: 88 場主導 ℓ ↔ 鏈 k (O162 P_k 閉式對照)
"""

import math, re, json
import numpy as np
from collections import defaultdict

ROOT = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
DATA = ROOT + '/cmb_cold_spot/data'
O182 = ROOT + '/o182_88grid_geometry/data'

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — 三通道 ℓ 譜對比 (C1-C6)")
print("=" * 76)

# ── 載入 ──
nodes = []
for i, line in enumerate(open(f'{DATA}/a5_nodes.txt')):
    if line.startswith('#'): continue
    p = line.split()
    nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)

g88 = np.loadtxt(O182 + '/g88_nodes.txt')
g32 = np.loadtxt(O182 + '/g32_frustration_midpoints.txt')

temps = json.load(open(O182 + '/temps2_SMICA_4.17deg.json'))
T60 = np.array(temps['A5_60'])
T88 = np.array(temps['G88'])
T32 = np.array(temps['G32frust'])
T120 = np.array(temps['G120_all'])
print(f"  點集: A5={len(T60)}, G88={len(T88)}, G32={len(T32)}, G120={len(T120)}")

from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.special import lpmv
from math import factorial, sqrt

def ylm(l, m, th, ph):
    plm = lpmv(abs(m), l, np.cos(th))
    norm = sqrt((2*l+1)*factorial(l-abs(m))/(4*math.pi*factorial(l+abs(m))))
    if m == 0: return norm * plm
    if m > 0:  return sqrt(2)*norm * plm * np.cos(m*ph)
    return sqrt(2)*norm * plm * np.sin(-m*ph)

def sphere_spectrum(coords, vals, lmax=4):
    """coords: (N,2) ra/dec; vals: (N,) — least-squares Σc² 譜"""
    sc = SkyCoord(ra=coords[:, 0]*AU.deg, dec=coords[:, 1]*AU.deg, frame='icrs')
    xyz = sc.cartesian.xyz.value
    x, y, z = xyz[0], xyz[1], xyz[2]
    th = np.arccos(np.clip(z, -1, 1))
    ph = np.arctan2(y, x)
    amps = {}
    for l in range(0, lmax+1):
        coefs = []
        for m in range(-l, l+1):
            Y = ylm(l, m, th, ph)
            coefs.append(np.dot(Y, vals)/np.dot(Y, Y))
        amps[l] = sqrt(sum(c**2 for c in coefs))
    return amps, th, ph

# ═══════════════════════════════════════════════════════════════
# C1-C4: 四通道 ℓ 譜
# ═══════════════════════════════════════════════════════════════
print("\n─── C1-C4. 四通道球面 ℓ 譜 (Σc², 基依賴) ───")
channels = [
    ("A5 60 節點      ", nodes, T60),
    ("G88 透明 88 中點 ", g88,  T88),
    ("G32 阻挫 32 中點 ", g32,  T32),
    ("G120 全 120 中點 ", np.vstack([g88, g32]), T120),
]
specs = {}
for name, coords, vals in channels:
    amps, th, ph = sphere_spectrum(coords, vals)
    specs[name.strip()] = amps
    mx = max(amps, key=amps.get)
    print(f"  {name} ℓ0={amps[0]:.3f} ℓ1={amps[1]:.3f} ℓ2={amps[2]:.3f} "
          f"ℓ3={amps[3]:.3f} ℓ4={amps[4]:.3f}  → 主導 ℓ={mx} ({amps[mx]:.3f})")

def dom(ch):
    return max(ch, key=ch.get)

check("C1: A5 60 節點 ℓ=3 主導 (重現 docs/05 S2)", dom(specs['A5 60 節點']) == 3, f"ℓ={dom(specs['A5 60 節點'])}")
# C2/C3 主導記錄
m88 = dom(specs['G88 透明 88 中點'])
m32 = dom(specs['G32 阻挫 32 中點'])
print(f"  (G88 主導 ℓ={m88}, G32 主導 ℓ={m32} — 記錄)")
check("C1b: G88 透明通道 ℓ=3 主導 (同 A5)", m88 == 3, f"G88 ℓ={m88}")
check("C1c: G32 阻挫通道 ℓ=4 主導 (同 A5/G88 唔同)", m32 == 4, f"G32 ℓ={m32}")

# ═══════════════════════════════════════════════════════════════
# C5. odd/even ℓ 能量比
# ═══════════════════════════════════════════════════════════════
print("\n─── C5. odd/even ℓ 能量比 (k↔ℓ 第一線索) ───")
for name in ['A5 60 節點', 'G88 透明 88 中點', 'G32 阻挫 32 中點', 'G120 全 120 中點']:
    a = specs[name]
    E_odd = a[1]**2 + a[3]**2
    E_even = a[0]**2 + a[2]**2 + a[4]**2
    r = E_odd / E_even if E_even > 1e-12 else float('inf')
    print(f"  {name} E_odd={E_odd:.4f} E_even={E_even:.4f} odd/even = {r:.2f}")
# 對照 O162 R6: 鏈 even k 驅動 (P_odd=0) — 若球面 odd 主導, 「even k ↔ odd ℓ」
r_a5 = (specs['A5 60 節點'][1]**2 + specs['A5 60 節點'][3]**2) / (specs['A5 60 節點'][0]**2 + specs['A5 60 節點'][2]**2 + specs['A5 60 節點'][4]**2)
check("C5a: A5 場 odd-ℓ 主導 (ℓ=1+3 > ℓ=0+2+4)", r_a5 > 1.5, f"odd/even={r_a5:.2f}")

# ═══════════════════════════════════════════════════════════════
# C6. k↔ℓ 映射候選: 88 場主導 ℓ ↔ 鏈 k 對照
# ═══════════════════════════════════════════════════════════════
print("\n─── C6. k↔ℓ 映射候選 ───")
# O162 R6 閉式 P_k (理想 cos 屏 → 鏈模投影): P_k = ½[csc((k+1)π/176)+csc((k-1)π/176)] (k even)
def P_k(k):
    return 0.5 * (1/math.sin((k+1)*math.pi/176) + 1/math.sin((k-1)*math.pi/176))
pk2 = P_k(2); pk44 = P_k(44); pk88 = P_k(88)
print(f"  O162 R6 P_k: k=2 → {pk2:.3f} (最大), k=44 → {pk44:.3f}, k=88 → {pk88:.3f}")
print(f"  P_44/P_2 = {pk44/pk2:.4f}, P_88/P_2 = {pk88/pk2:.4f}")
# 球面側: A5 譜 ℓ4/ℓ3 = ? 
a = specs['A5 60 節點']
print(f"  A5 側: ℓ3/ℓ2 = {a[3]/a[2]:.3f}, ℓ4/ℓ3 = {a[4]/a[3]:.3f}, ℓ3/ℓ1 = {a[3]/a[1]:.3f}")
# 88 場
b = specs['G88 透明 88 中點']
print(f"  G88 側: ℓ3/ℓ2 = {b[3]/b[2]:.3f} (主導 ℓ={m88}), ℓ2/ℓ4 = {b[2]/b[4]:.3f}")
check("C6a: A5 ℓ=3/ℓ=1 > 2 (ℓ=3 強主導)", a[3]/a[1] > 2.0, f"{a[3]/a[1]:.3f}")
# 88 場主導同 A5 主導比較
check("C6b: G88 及 A5 主導 ℓ 一致 (dip 通道共用結構)", m88 == 3, f"A5 ℓ3 vs G88 ℓ{m88}")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)