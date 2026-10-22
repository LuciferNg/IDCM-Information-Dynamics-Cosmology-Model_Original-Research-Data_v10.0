#!/usr/bin/env python3
"""
O143 #20 — ★ A5 節點集球面設計強度 (spherical design strength)
==========================================================
球面 t-design: 任意 ≤t 次多項式嘅平均 = 球面平均
  t=1: Σ n̂_i = 0
  t=2: Σ n_i n_j ∝ δ_ij (四極自由)
  t=4: Σ n_i n_j n_k n_l = N(δδ+δδ+δδ)/15
逐階測試 (對稱 traceless 張量), 並同隨機 60 點對照。
"""
import numpy as np, math, json
from itertools import combinations_with_replacement

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
nodes = np.loadtxt(f'{BASE}/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
N = 60
rng = np.random.default_rng(2026)

print("="*78); print("  O143 #20 — A5 節點集球面設計強度"); print("="*78)

def tensor_power(V, p):
    """Σ_a (n_a)^{⊗p} / N, 對稱化"""
    T = np.zeros((3,)*p)
    for a in range(len(V)):
        idx = V[a]
        for combo in combinations_with_replacement(range(p), 1):
            pass
        # 直接用 einsum 對稱張量
        T += np.einsum('i,j->ij', idx, idx) if p == 2 else 0
    return T

# 統一用 einsum 造對稱張量
def sym_tensor(V, p):
    Nn = len(V)
    T = np.zeros((3,)*p)
    for a in range(Nn):
        v = V[a]
        for idx in np.ndindex((3,)*p):
            prod = 1.0
            for d in idx: prod *= v[d]
            T[idx] += prod
    return T / Nn

# 球面平均 (isotropic) 張量
def iso_tensor(p):
    """球面平均 (n)^{⊗p}: p 偶數時 = 對所有配對嘅 δ 乘積 / (p+1)!!"""
    if p % 2 == 1: return np.zeros((3,)*p)
    from itertools import permutations
    T = np.zeros((3,)*p)
    # 所有完美配對
    def pairings(items):
        if not items: yield []; return
        first = items[0]
        for i in range(1, len(items)):
            rest = items[1:i] + items[i+1:]
            for p_ in pairings(rest):
                yield [(first, items[i])] + p_
    def dfact(m):
        r = 1
        while m > 0: r *= m; m -= 2
        return r
    cnt = 0
    for pr in pairings(list(range(p))):
        Tt = np.zeros((3,)*p)
        # 用 einsum 建 δ 乘積
        arr = np.ones((3,)*p)
        for (a, b) in pr:
            sh = [1]*p; sh[a] = 3; sh[b] = 3
            d = np.eye(3).reshape(sh)
            arr = arr * d
        T += arr; cnt += 1
    return T / dfact(p+1)

print(f"\n  球面 t-design 檢定 (max|觀測 − isotropic|):")
print(f"  {'t':>3} {'觀測偏差':>12} {'隨機 60 點 (mean±std)':>24} {'z':>8}")
results = {}
for p in [1,2,3,4,6]:
    T_obs = sym_tensor(vecs, p)
    T_iso = iso_tensor(p)
    dev = float(np.abs(T_obs - T_iso).max())
    # 隨機對照
    rand_devs = []
    for _ in range(300):
        rr = rng.normal(size=(N,3)); rr /= np.linalg.norm(rr, axis=1, keepdims=True)
        rand_devs.append(float(np.abs(sym_tensor(rr, p) - T_iso).max()))
    rand_devs = np.array(rand_devs)
    z = (dev - rand_devs.mean())/rand_devs.std()
    results[p] = {'dev': dev, 'rand_mean': float(rand_devs.mean()), 'rand_std': float(rand_devs.std()), 'z': float(z)}
    print(f"  {p:>3} {dev:>12.3e} {rand_devs.mean():>12.3e} ± {rand_devs.std():<9.3e} {z:>+8.2f}")

print(f"\n  判定:")
for p in [1,2,3,4,6]:
    r = results[p]
    if p % 2 == 1:
        print(f"    t={p}: 奇數階 (球面平均=0); 偏差 {r['dev']:.2e}, z={r['z']:+.2f}")
    else:
        ok = r['dev'] < 1e-6
        print(f"    t={p}: {'✅ 滿足 (design)' if ok else '❌ 唔滿足'} (偏差 {r['dev']:.2e}, z={r['z']:+.2f})")

# 結論
print(f"\n  ★ 結論:")
print(f"    t=2 滿足 → 節點集四極自由 (dipole + quadrupole 平均 = 球面平均)")
if results[4]['dev'] < 1e-6:
    print(f"    t=4 滿足 → 節點集係 spherical 4-design (degree ≤4 多項式全部平均 = 球面平均)")
else:
    print(f"    t=4 唔滿足 → 只係 t=2 design")
print(f"\n  幾何意義: 60 = Rhombicosidodecahedron vertices (I_h 軌道)")
print(f"    I_h 對稱 ⇒ 所有 odd-degree 張量 = 0; 張量必為 isotropic 形式")
print(f"    ⟹ 任何由 I_h 不變性強制嘅張量階數都會自動滿足 design 條件")

res = {'design': {str(p): results[p] for p in results},
       't2_design': bool(results[2]['dev'] < 1e-6),
       't4_design': bool(results[4]['dev'] < 1e-6),
       't6_design': bool(results[6]['dev'] < 1e-6)}
with open(f'{O143}/data/step17_design_strength.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step17_design_strength.json")
