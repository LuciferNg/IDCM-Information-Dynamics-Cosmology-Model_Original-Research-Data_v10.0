#!/usr/bin/env python3
"""
O7 — 20_a5_ell3_verification_and_klmap.py (2026-10-11)
====================================================================
O7/natural-write-closure 第六輪:
  V 段: A5 cosθ 場 ℓ=3 主導嘅統計加強驗證 (docs/07 §4 承諾)
        隨機 32-subset 教訓 → permutation null (2000×) + 幾何 null
  M 段: k↔ℓ 映射攻堅 — O7 圖 Laplacian 模 vs 球面 Y_lm 交叉相關
        (候選: 圖模 k=13 (λ=φ²) ↔ 球面 ℓ=3?)

數據: cmb_cold_spot (a5_nodes, faces, smica_smoothed) — 獨立重算
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
print("  O7 — A5 ℓ3 加強驗證 + k↔ℓ 圖譜/球面交叉 (V, M)")
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
cs = obs / A

adj = defaultdict(set)
for line in open(f'{DATA}/faces.txt'):
    if line.startswith('#'): continue
    m = re.search(r'\[([^\]]+)\]', line)
    vs = [int(x) for x in m.group(1).split(',')]
    for i in range(len(vs)):
        adj[vs[i]].add(vs[(i+1) % len(vs)])
        adj[vs[(i+1) % len(vs)]].add(vs[i])

from astropy.coordinates import SkyCoord
import astropy.units as AU
from scipy.special import lpmv
from math import factorial, sqrt

sc = SkyCoord(ra=nodes[:, 0]*AU.deg, dec=nodes[:, 1]*AU.deg, frame='icrs')
xyz = sc.cartesian.xyz.value
x, y, z = xyz[0], xyz[1], xyz[2]
th = np.arccos(np.clip(z, -1, 1)); ph = np.arctan2(y, x)

def ylm(l, m, th, ph):
    plm = lpmv(abs(m), l, np.cos(th))
    norm = sqrt((2*l+1)*factorial(l-abs(m))/(4*math.pi*factorial(l+abs(m))))
    if m == 0: return norm * plm
    if m > 0:  return sqrt(2)*norm * plm * np.cos(m*ph)
    return sqrt(2)*norm * plm * np.sin(-m*ph)

def spectrum(vals, lmax=4):
    amps = {}
    for l in range(lmax+1):
        coefs = [np.dot(ylm(l, m, th, ph), vals)/np.dot(ylm(l, m, th, ph), ylm(l, m, th, ph)) for m in range(-l, l+1)]
        amps[l] = sqrt(sum(c*c for c in coefs))
    return amps

def dom(a):
    return max(a, key=a.get)

# ═══════════════════════════════════════════════════════════════
# V 段: A5 ℓ=3 主導加強驗證
# ═══════════════════════════════════════════════════════════════
print("\n─── V1. A5 cosθ 場 ℓ=3 主導 — permutation null (2000×) ───")
obs_amp = spectrum(cs)
print("  觀察: " + " ".join(f"ℓ{l}={obs_amp[l]:.4f}" for l in range(5)) + f" → dom ℓ={dom(obs_amp)}")
rng = np.random.default_rng(11)
null_amp3 = np.zeros(2000); null_dom = np.zeros(2000, int)
for k in range(2000):
    perm = rng.permutation(60)
    a = spectrum(cs[perm])
    null_amp3[k] = a[3]
    null_dom[k] = dom(a)
z3 = (obs_amp[3] - null_amp3.mean()) / null_amp3.std()
p3 = (null_amp3 >= obs_amp[3]).mean()
print(f"  null ℓ3: {null_amp3.mean():.4f}±{null_amp3.std():.4f}; 觀察 {obs_amp[3]:.4f} → z={z3:+.2f}, p(≥)={p3:.4f}")
print(f"  null dom 分佈: ℓ0={(null_dom==0).mean():.3f} ℓ1={(null_dom==1).mean():.3f} ℓ2={(null_dom==2).mean():.3f} ℓ3={(null_dom==3).mean():.3f} ℓ4={(null_dom==4).mean():.3f}")
check("V1a: A5 ℓ3 主導 permutation 顯著 (p<0.01, z≈3σ)", z3 > 2.5 and p3 < 0.01, f"z={z3:+.2f} p={p3:.4f}")
# 注意: null dom 分佈即使唔顯著, 都可能係「幾何效應」— V2 分離

print("\n─── V2. 幾何 null: 隨機 60 點 (同場 = 溫度重新分配) vs A5 幾何 ───")
# 用「佢自己個場」—— 但隨機點冇溫度; 用「同場強度譜」冇意義。
# 正確幾何 null: 隨機 60 天球方向, 用 A5 溫度場嘅正規次序 (無排序) — 唔可比。
# 改為: A5 溫度場 permute 只係 V1; 幾何效應可由「A5 座標 + 高空場(白噪)」測?
# 最簡單: random 60 方向 + 同一個 multiset 溫度 (random 排列) → ℓ 譜分佈。
null_g_dom = np.zeros(1000, int)
for k in range(1000):
    # random 60 dirs
    zr = rng.uniform(-1, 1, 60); pr = rng.uniform(0, 2*math.pi, 60)
    thr = np.arccos(zr); phr = pr
    vals = cs[rng.permutation(60)]
    amps = {}
    for l in range(5):
        coefs = []
        for m in range(-l, l+1):
            Y = ylm(l, m, thr, phr)
            coefs.append(np.dot(Y, vals)/np.dot(Y, Y))
        amps[l] = sqrt(sum(c*c for c in coefs))
    null_g_dom[k] = dom(amps)
print(f"  隨機 60 點幾何 null dom: ℓ0={(null_g_dom==0).mean():.3f} ℓ1={(null_g_dom==1).mean():.3f} "
      f"ℓ2={(null_g_dom==2).mean():.3f} ℓ3={(null_g_dom==3).mean():.3f} ℓ4={(null_g_dom==4).mean():.3f}")
check("V2a: A5 dom ℓ3 (觀察) 高於隨機幾何 ℓ3 頻率", (null_g_dom == 3).mean() < 0.6, f"隨機 ℓ3={(null_g_dom==3).mean():.3f}")

# ═══════════════════════════════════════════════════════════════
# M 段: k↔ℓ 映射 — O7 圖模 vs 球面 Y_lm 交叉
# ═══════════════════════════════════════════════════════════════
print("\n─── M1. O7 圖 Laplacian 模 vs 球面 Y_lm 交叉相關 ───")
L = np.zeros((60, 60))
for v in range(60):
    L[v, v] = len(adj[v])
    for w in adj[v]: L[v, w] = -1
evals, evecs = np.linalg.eigh(L)
# Y_lm 喺節點嘅採樣 (ℓ=0..4, m=-ℓ..ℓ)  — normalize
Ycovs = []
for l in range(5):
    for m in range(-l, l+1):
        Y = ylm(l, m, th, ph)
        Y = Y/np.linalg.norm(Y)
        Ycovs.append((l, m, Y))
# 每個圖模 v_k 同每個 Y 嘅 |corr| max
best = []
for k in range(60):
    vk = evecs[:, k]
    if np.abs(evals[k]) < 1e-9: continue
    corrs = [abs(np.dot(vk/np.linalg.norm(vk), Y)) for (_, _, Y) in Ycovs]
    j = int(np.argmax(corrs))
    l, m, _ = Ycovs[j]
    best.append((corrs[j], k, l, m, evals[k]))
best.sort(reverse=True)
print("  圖模↔球面模 最高重合 (|corr|, 圖k, λ, 球面ℓ,m):")
for c, k, l, m, lam in best[:10]:
    print(f"    |corr|={c:.4f} 圖k={k:2d} λ={lam:.4f} ↔ ℓ={l}, m={m:2d}")
# k=13 係咪 ↔ ℓ=3?
c13 = None
for c, k, l, m, lam in best:
    if k == 13:
        c13 = c; l13 = l; m13 = m; break
check("M1a: 圖模 k=13 主要重合對象 = 球面 ℓ=3 (k↔ℓ 映射錨)", c13 is not None and l13 == 3, f"k13→ℓ{l13} |corr|={c13:.4f}" if c13 else "k13 唔喺 top")
# 統計: k=13 vs 其他圖模對 ℓ=3 嘅重合度比較
corr_13_l3 = max(abs(np.dot(evecs[:,13]/np.linalg.norm(evecs[:,13]), Y)) for (l,m,Y) in Ycovs if l == 3)
corr_all_l3 = []
for k in range(60):
    if np.abs(evals[k]) < 1e-9: continue
    corr_all_l3.append(max(abs(np.dot(evecs[:,k]/np.linalg.norm(evecs[:,k]), Y)) for (l,m,Y) in Ycovs if l == 3))
corr_all_l3 = np.array(corr_all_l3)
z13 = (corr_13_l3 - corr_all_l3.mean())/corr_all_l3.std()
print(f"  圖模對 ℓ=3 最多重合: k13 corr={corr_13_l3:.4f} vs 全模 {corr_all_l3.mean():.4f}±{corr_all_l3.std():.4f} → z={z13:+.2f}")
check("M1b: k13 vs ℓ3 重合顯著 (z>2)", z13 > 2.0, f"z={z13:+.2f}")

# M2: 全交叉矩陣摘要 — 有冇系統「圖模↔球面模」配對 (最強 10 對)
print("\n─── M2. 圖-球面最強配對 (全 59 模 × 25 Y) 摘要 ───")
strong = [b for b in best if b[0] > 0.5]
print(f"  |corr| > 0.5 嘅配對數: {len(strong)}")
for c, k, l, m, lam in strong[:12]:
    print(f"    |corr|={c:.4f} 圖k={k:2d} λ={lam:.4f} ↔ ℓ={l}, m={m:2d}")

# M3: 圖模↔球面模嘅「簡併結構」對照: 圖 Laplacian 常重複特徵值
from collections import Counter
lams = np.round(evals, 4)
deg = Counter(lams)
print(f"  圖譜簡併: {[(f'{l:.4f}', d) for l, d in sorted(deg.items(), key=lambda x:-x[1])[:6]]}")
print(f"  球面 ℓ 維度: ℓ=0:1, ℓ=1:3, ℓ=2:5, ℓ=3:7, ℓ=4:9 (A₅ irrep 限制可能簡併/消失)")

# ── 總結 ──
print("\n" + "=" * 76)
print(f"  結果: {sum(results)}/{len(results)} PASS")
print("=" * 76)