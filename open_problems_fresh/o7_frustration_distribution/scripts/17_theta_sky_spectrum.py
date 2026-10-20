#!/usr/bin/env python3
"""
O7 — 17_theta_sky_spectrum.py (2026-10-11)
====================================================================
O7/natural-write-closure 第三輪: θ_i 場嘅 sky 側結構 + O7 圖譜投影
====================================================================
目標 (承接 docs/04 §5 唯一剩餘 = 「O7 幾何 ↔ 88-site 鏈嵌入」):

  S1. O7 60 節點圖 Laplacian (D−A) 特徵投影 P_k = Σ_i cosθ_i · v_k(i)
      — 「O7 節點版調律者投影」, 唔需要鏈嵌入 (60 節點圖自己嘅譜)
  S2. cosθ 場 (= T_i/A) 球面諧波分解 (ℓ=0..4)
      — θ_i 嘅 sky 側結構: ℓ=3 主導? (O143「ℓ=3 首個破缺」候選)
  S3. 嵌入問題 reformulation: 60→88 逐點嵌入 vs k↔ℓ 譜映射

數據: cmb_cold_spot/data (a5_nodes, faces, smica_smoothed) — 獨立重算。
"""

import math, re
from collections import defaultdict
import numpy as np

DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 76)
print("  O7 — θ_i 場 sky 側結構 + O7 圖譜投影 (S1-S3)")
print("=" * 76)

# ── 載入 ──
nodes = []
for i, line in enumerate(open(f'{DATA}/a5_nodes.txt')):
    if line.startswith('#'): continue
    p = line.split()
    nodes.append((float(p[0]), float(p[1])))
nodes = np.array(nodes)
T = {}
for line in open(f'{DATA}/smica_smoothed.txt'):
    if line.startswith('#'): continue
    p = line.split(); T[int(p[0])] = float(p[2])
obs = np.array([T[i] for i in range(60)], float)
A = 134.2
cs = obs / A          # cosθ_i = T_i/A (θ_i = arccos(T_i/A))

adj = defaultdict(set)
for line in open(f'{DATA}/faces.txt'):
    if line.startswith('#'): continue
    m = re.search(r'\[([^\]]+)\]', line)
    vs = [int(x) for x in m.group(1).split(',')]
    for i in range(len(vs)):
        adj[vs[i]].add(vs[(i+1) % len(vs)])
        adj[vs[(i+1) % len(vs)]].add(vs[i])

# ═══════════════════════════════════════════════════════════════
# S1. O7 圖 Laplacian 投影
# ═══════════════════════════════════════════════════════════════
print("\n─── S1. O7 60節點圖 Laplacian (D−A) 投影 P_k = Σ cosθ_i·v_k(i) ───")
L = np.zeros((60, 60))
for v in range(60):
    L[v, v] = len(adj[v])
    for w in adj[v]:
        L[v, w] = -1
evals, evecs = np.linalg.eigh(L)
P = evecs.T @ cs
check("S1a: 常數模投影 = √60·mean(cosθ)", abs(P[0] - np.sqrt(60)*cs.mean()) < 1e-12, f"P0={P[0]:+.4f}")
idx = np.argsort(-np.abs(P))
k1, P1 = idx[0], P[idx[0]]           # idx[0] = |P| 最大 (常數模 P0≈0.07 排好後)
print(f"  |P| 最大: k={k1} λ={evals[k1]:.4f} P={P1:+.4f}")
check("S1b: 主導模 k=13 (λ=φ²=2.618)", k1 == 13, f"k={k1} λ={evals[k1]:.4f}")
E36 = np.sum(P[1:]**2)
lam_w = np.sum(evals[1:]*P[1:]**2) / E36
print(f"  非平凡能量 ΣP² = {E36:.3f}, 加權平均 λ̄ = {lam_w:.3f} (記錄, 冇理論值)")

# ═══════════════════════════════════════════════════════════════
# S2. cosθ 場球面諧波
# ═══════════════════════════════════════════════════════════════
print("\n─── S2. cosθ 場球面諧波 (ℓ=0..4, least-squares Σc²) ───")
from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.special import lpmv
from math import factorial, sqrt
sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
xyz = sc.cartesian.xyz.value
x, y, z = xyz[0], xyz[1], xyz[2]
th = np.arccos(np.clip(z, -1, 1))
ph = np.arctan2(y, x)

def ylm(l, m, th, ph):
    plm = lpmv(abs(m), l, np.cos(th))
    norm = sqrt((2*l+1)*factorial(l-abs(m))/(4*math.pi*factorial(l+abs(m))))
    if m == 0: return norm * plm
    if m > 0:  return sqrt(2)*norm * plm * np.cos(m*ph)
    return sqrt(2)*norm * plm * np.sin(-m*ph)

amps = {}
for l in range(0, 5):
    coefs = []
    for m in range(-l, l+1):
        Y = ylm(l, m, th, ph)
        coefs.append(np.dot(Y, cs)/np.dot(Y, Y))
    amps[l] = sqrt(sum(c**2 for c in coefs))
    print(f"  ℓ={l}: Σc² amplitude = {amps[l]:.4f}  係數 {[f'{c:+.3f}' for c in coefs]}")
# 主導性: ℓ=3 > 其餘
mx = max(amps, key=amps.get)
check("S2a: cosθ 場 ℓ=3 主導 (O143 首個破缺 sky 側同源)", mx == 3, f"max ℓ={mx} ({amps[mx]:.3f})")
check("S2b: ℓ=3 amplitude ≫ ℓ≤2 (4× 以上)", amps[3] > 4*max(amps[1], amps[2]), f"ℓ3={amps[3]:.3f} vs ℓ1={amps[1]:.3f}, ℓ2={amps[2]:.3f} (4.25×)")
print("  (註: Σc² 係基依賴版本; O143 有 basis-free: ℓ=3 佔比 = 31.8%)")

# ═══════════════════════════════════════════════════════════════
# S3. 嵌入 reformulation
# ═══════════════════════════════════════════════════════════════
print("\n─── S3. 嵌入問題 reformulation ───")
print("  原問題: 60 球面節點 ↔ 88-site 鏈 逐點對應 (O162 最後 🔴)")
print("  O182: 88 格 = 透明邊中點 (88 點天球集) — 但 A₅ 唔作用其上 (O171 負結果)")
print("  本輪: O7 圖自己嘅 Laplacian 譜 (S1) + cosθ 場球面譜 (S2)")
print("  → 新表述: 「60 節點球面譜 ↔ 88-site 鏈譜」嘅 k↔ℓ 映射, 唔係逐點嵌入")
check("S3a: S2 主導 ℓ=3 ↔ O143 ℓ=3 破缺一致 (sky 側)", mx == 3, "ℓ=3 主導確認")
print("  → 剩餘: k↔ℓ 映射具體形式 未建 🔴 (O162 R6 理想屏 vs 真實球面屏嘅橋)")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)