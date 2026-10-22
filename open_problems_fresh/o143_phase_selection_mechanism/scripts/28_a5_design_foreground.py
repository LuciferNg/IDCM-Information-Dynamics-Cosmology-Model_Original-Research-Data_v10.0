#!/usr/bin/env python3
"""
O143 #28 — a5_nodes 真實採樣點嘅 design strength + 前景框架資源盤點
==================================================================
#27 發現 a5_nodes 唔係標準 Rhombicosidodecahedron (邊長 26.13° vs 25.88°)。
→ 必須直接檢定「實際採樣點」嘅 design strength (Gemini Part I 嘅前提)。
A. a5_nodes t=1..7 design 測試
B. a5_nodes 嘅 aliasing matrix (ℓ≤2 保護? ℓ=3 破缺?)
C. 前景排除框架: 盤點項目內可用 Planck 頻段圖 / 遮罩
"""
import numpy as np, math, json, itertools, os, glob
from scipy.special import lpmv

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
G = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data'

a5 = np.loadtxt(f'{D}/a5_nodes.txt')
V = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
               math.cos(math.radians(d))*math.sin(math.radians(r)),
               math.sin(math.radians(d))] for r, d in a5])
T_obs = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['A5_60'][:60])

print("="*80); print("  O143 #28 — a5_nodes design strength + 前景資源盤點"); print("="*80)

# ── A. a5_nodes design strength ──
print(f"\n[A] a5_nodes (實際天空採樣點) design strength")
def sym_tensor(Vv, p):
    T = np.zeros((3,)*p)
    for v in Vv:
        for idx in np.ndindex((3,)*p):
            pr = 1.0
            for dd in idx: pr *= v[dd]
            T[idx] += pr
    return T/len(Vv)
def iso_tensor(p):
    if p%2==1: return np.zeros((3,)*p)
    def pairings(items):
        if not items: yield []; return
        f = items[0]
        for i in range(1,len(items)):
            for p_ in pairings(items[1:i]+items[i+1:]): yield [(f,items[i])]+p_
    def df(m):
        r=1
        while m>0: r*=m; m-=2
        return r
    T = np.zeros((3,)*p)
    for pr in pairings(list(range(p))):
        arr = np.ones((3,)*p)
        for (a,b) in pr:
            sh=[1]*p; sh[a]=3; sh[b]=3
            arr = arr*np.eye(3).reshape(sh)
        T += arr
    return T/df(p+1)
devs = {}
for p in [1,2,3,4,5,6,7]:
    dev = float(np.abs(sym_tensor(V,p)-iso_tensor(p)).max())
    devs[p] = dev
    print(f"    t={p}: 偏差 = {dev:.3e}  {'✅' if dev<1e-12 else '❌'}")

# ── B. a5_nodes aliasing matrix ──
print(f"\n[B] a5_nodes aliasing matrix")
def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); ph = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm*P
    if m > 0: return math.sqrt(2)*norm*P*np.cos(am*ph)
    return math.sqrt(2)*norm*P*np.sin(am*ph)
blocks = {l: np.column_stack([real_sph(l,m,V) for m in range(-l,l+1)]) for l in range(6)}
N = 60
print(f"    對角塊 ||M_ℓℓ − I||_max:")
diag_dev = {}
for l in range(6):
    Mll = (4*np.pi/N) * (blocks[l].T @ blocks[l])
    d = float(np.max(np.abs(Mll - np.eye(2*l+1)))); diag_dev[l] = d
    print(f"      ℓ={l}: {d:.3e}  {'✅ 保護' if d<1e-3 else '⚠️ 破缺'}")
print(f"    非對角洩漏 ||M[ℓ'][ℓ]||_F (ℓ=3 一行):")
leak = {}
for lp in range(6):
    if lp == 3: continue
    M = (4*np.pi/N) * (blocks[lp].T @ blocks[3])
    f = float(np.linalg.norm(M)); leak[lp] = f
    print(f"      ℓ'={lp} → ℓ=3: {f:.4e}")

# ── C. 前景資源盤點 ──
print(f"\n[C] 前景排除框架 — 項目內可用資源盤點")
pats = ['*LFI*','*HFI*','*030*','*044*','*070*','*100*','*143*','*217*','*353*','*mask*','*Mask*','*KQ85*','*smica*','*SMICA*','*freq*']
seen = {}
for root in [BASE, f'{BASE}/open_problems_fresh', '/home/wsl/Projects']:
    for pat in pats:
        for f in glob.glob(f'{root}/**/{pat}', recursive=True):
            if os.path.isfile(f) and os.path.getsize(f) > 1000:
                key = os.path.basename(f)
                if key not in seen: seen[key] = (os.path.getsize(f), f)
print(f"    搵到 {len(seen)} 個候選檔案 (前 25 個, 按大小):")
for k,(sz,f) in sorted(seen.items(), key=lambda x:-x[1][0])[:25]:
    print(f"      {sz/1e6:8.2f} MB  {f.replace(BASE,'.')}")

res = {'a5_design_dev': {str(k):v for k,v in devs.items()},
       'a5_M_diag_dev': {str(k):v for k,v in diag_dev.items()},
       'a5_M_leak_l3': {str(k):v for k,v in leak.items()},
       'files_found': {k: f for k,(sz,f) in sorted(seen.items(), key=lambda x:-x[1][0])[:40]}}
with open(f'{O143}/data/step25_a5_design_foreground.json','w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step25_a5_design_foreground.json")
