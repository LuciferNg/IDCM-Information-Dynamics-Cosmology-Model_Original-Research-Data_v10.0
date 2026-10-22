#!/usr/bin/env python3
"""
O143 #25 — 驗證 Gemini Part I (球面混疊定理)
============================================
Gemini 聲稱:
  (a) 60 節點係 4-design「甚至 5-design」
  (b) ℓ≤2 受代數保護 (2ℓ ≤ t); ℓ=3 破缺 (2ℓ=6 > t) → 混疊
  (c) ℓ=3 信號 = 混疊通道

本輪嚴格檢定:
  A. t=5 design 測試 (Gemini 嘅「甚至 5-design」)
  B. Aliasing matrix M_{ℓ'm',ℓm} = (4π/N)Σ_j Y_ℓ'm' Y*_ℓm — 檢查 ℓ≤2 保護 + ℓ=3 洩漏源
  C. ★ 關鍵: 移除 ℓ≤2 內容後, ℓ=3 功率是否存活? (若混疊自 ℓ≤2, 應大幅衰減)
"""
import numpy as np, math, json
from scipy.special import lpmv

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
G = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data'
rng = np.random.default_rng(2026)
phi = (1+5**0.5)/2
import itertools

# ── 精確 I_h 座標 ──
base = [(1,1,phi**3), (phi**2, phi, 2*phi), (2+phi, 0, phi**2)]
verts = []
for b in base:
    for perm in [b, (b[1],b[2],b[0]), (b[2],b[0],b[1])]:
        for sg in itertools.product([1,-1], repeat=3):
            v = tuple(s*x for s,x in zip(sg, perm))
            if v not in verts: verts.append(v)
V = np.array(verts, float); V = V/np.linalg.norm(V,axis=1,keepdims=True)

T_obs = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['A5_60'][:60])

def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); ph = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm*P
    if m > 0: return math.sqrt(2)*norm*P*np.cos(am*ph)
    return math.sqrt(2)*norm*P*np.sin(am*ph)

print("="*80); print("  O143 #25 — 驗證 Gemini Part I (混疊定理)"); print("="*80)

# ═══ A. t=5 design ═══
print(f"\n[A] Design strength — t=5 測試 (Gemini 聲稱「甚至 5-design」)")
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
for p in [1,2,3,4,5,6,7]:
    dev = float(np.abs(sym_tensor(V,p)-iso_tensor(p)).max())
    tag = "✅" if dev < 1e-12 else "❌"
    print(f"    t={p}: 偏差 = {dev:.3e}  {tag}")
print(f"  ⟹ 60 節點係 4-design (t=5 睇上面); Gemini「甚至 5-design」需核對")

# ═══ B. Aliasing matrix ═══
print("\n[B] Aliasing matrix M (l,l' = 0..5): M[l'm',lm] = (4pi/60) Sum_j Y_l'm' Y*_lm")
NB = 60
def block(l):
    return np.column_stack([real_sph(l,m,V) for m in range(-l,l+1)])
blocks = {l: block(l) for l in range(6)}
# M[ℓ][ℓ'] = (4π/N) * B_ℓ'^T @ conj(B_ℓ)  (實球諧 → 實內積)
M = {}
for l in range(6):
    for lp in range(6):
        M[(lp,l)] = (4*np.pi/NB) * (blocks[lp].T @ blocks[l])
print(f"  對角塊 M[ℓ][ℓ] 偏離單位矩陣 (frame weight 偏差):")
for l in range(6):
    dev = float(np.max(np.abs(M[(l,l)] - np.eye(2*l+1))))
    print(f"    ℓ={l}: ||M_ℓℓ − I||_max = {dev:.3e}" + ("  ✅ 精確保護" if dev<1e-12 else "  ⚠️ 破缺"))
print(f"\n  非對角塊 ||M[ℓ'][ℓ]||_F (洩漏強度, 只列 ℓ=3 一行):")
for lp in range(6):
    if lp == 3: continue
    f = float(np.linalg.norm(M[(lp,3)]))
    print(f"    ℓ'={lp} → ℓ=3: ||M||_F = {f:.4e}")

# ═══ C. ★ 移除 ℓ≤2 後 ℓ=3 是否存活 ═══
print(f"\n[C] ★ 關鍵檢定: 移除 ℓ≤2 內容後, ℓ=3 功率是否存活?")
Tz = T_obs - T_obs.mean()
W = np.column_stack([blocks[l] for l in range(3)])  # ℓ=0,1,2
proj_W = W @ np.linalg.lstsq(W, Tz, rcond=None)[0]
T_rest = Tz - proj_W
B3 = blocks[3]
def p3(x):
    c, *_ = np.linalg.lstsq(B3, x, rcond=None)
    return float((c**2).sum())
P3_raw = p3(Tz)
P3_clean = p3(T_rest)
print(f"  ℓ=3 功率 (原始 Tz)          = {P3_raw:.0f}")
print(f"  ℓ=3 功率 (移除 ℓ≤2 後)      = {P3_clean:.0f}   ({100*P3_clean/P3_raw:.1f}% 保留)")
# null
def null_p(x, nperm=3000):
    v = []
    for _ in range(nperm):
        c, *_ = np.linalg.lstsq(B3, rng.permutation(x), rcond=None)
        v.append((c**2).sum())
    return np.array(v)
n_raw = null_p(Tz, 2000); n_clean = null_p(T_rest, 2000)
print(f"  null (原始) = {n_raw.mean():.0f} ± {n_raw.std():.0f} → p = {(1+(n_raw>=P3_raw).sum())/(1+len(n_raw)):.4f}")
print(f"  null (移除後) = {n_clean.mean():.0f} ± {n_clean.std():.0f} → p = {(1+(n_clean>=P3_clean).sum())/(1+len(n_clean)):.4f}")

# 更強: 移除 ℓ≤2 同 ℓ≥4 (即只留 ℓ=3 嘅正交補)
W2 = np.column_stack([blocks[l] for l in range(6) if l != 3])
proj_W2 = W2 @ np.linalg.lstsq(W2, Tz, rcond=None)[0]
T_only3 = Tz - proj_W2
P3_iso = p3(T_only3)
n_iso = null_p(T_only3, 2000)
print(f"\n  ℓ=3 功率 (移除 ℓ≤2 及 ℓ≥4 後, 即正交補) = {P3_iso:.0f}")
print(f"    null = {n_iso.mean():.0f} ± {n_iso.std():.0f} → p = {(1+(n_iso>=P3_iso).sum())/(1+len(n_iso)):.4f}")

# 混疊洩漏估算: 用 ℓ≤2 嘅擬合場, 睇佢喺 ℓ=3 投影出幾多
print(f"\n  混疊洩漏估算 (Gemini 聲稱 ℓ=3 突出 = 混疊):")
print(f"    ℓ≤2 擬合場本身喺 ℓ=3 投影: {p3(proj_W):.0f}")
print(f"    → 佔觀測 ℓ=3 功率 {100*p3(proj_W)/P3_raw:.1f}%")

res = {'design_dev': {}, 'M_diag_dev': {}, 'M_leak_to_l3': {},
       'P3_raw': P3_raw, 'P3_clean_l2removed': P3_clean, 'P3_isolated': P3_iso,
       'null_raw': float(n_raw.mean()), 'null_clean': float(n_clean.mean()),
       'aliasing_from_l2_fit': p3(proj_W)}
for p in [1,2,3,4,5,6,7]:
    res['design_dev'][str(p)] = float(np.abs(sym_tensor(V,p)-iso_tensor(p)).max())
for l in range(6):
    res['M_diag_dev'][str(l)] = float(np.max(np.abs(M[(l,l)]-np.eye(2*l+1))))
for lp in range(6):
    if lp != 3: res['M_leak_to_l3'][str(lp)] = float(np.linalg.norm(M[(lp,3)]))
with open(f'{O143}/data/step22_gemini_part1.json','w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step22_gemini_part1.json")
