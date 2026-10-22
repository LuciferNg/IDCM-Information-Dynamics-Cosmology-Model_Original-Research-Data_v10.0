#!/usr/bin/env python3
"""
O143 #22 — 寫入動力學 (Ising) + 多極功率 + k 身份
=================================================
A. ★ Ising 能量: H = Σ_edges s_u s_v; 著色 H = −56 (O7 值); 觀測 sign(T) H = ?
B. 斷阻挫邊統計: 觀測 vs 隨機 flip null
C. 多極功率: A5 節點場嘅 ℓ=1..6 功率 vs 置換 null (4-design ⟹ ℓ≤2 frame tight)
D. k 分層身份: 8/40/12 邊個係結構強制?
"""
import numpy as np, math, json
from collections import defaultdict, deque
from scipy import stats

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
rng = np.random.default_rng(20260919)

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
T = np.array(json.load(open(f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); c = ac[:,3].astype(int)
cspin = np.where(c==1, 1, -1)  # cold=+1
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set); edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))

print("="*78); print("  O143 #22 — Ising + 多極 + k 身份"); print("="*78)

# ═══ A. Ising 能量 ═══
print(f"\n[A] ★ Ising 能量 H = Σ_edges s_u s_v")
def H(s): return float(sum(s[u]*s[v] for u,v in edges))
H_col = H(cspin)
print(f"  著色 (O7 基態): H = {H_col:.0f}   (O7 記錄 −56) {'✅ 一致' if abs(H_col+56)<1e-9 else '❌'}")
s_obs = np.where(T < 0, 1, -1)  # cold = −T; 用 sign(−T) 令冷=+1 同著色一致
H_obs = H(s_obs)
print(f"  觀測 sign(−T): H = {H_obs:.0f}")
# null: random spin configs
H_null = []
for _ in range(200000):
    ss = rng.permutation(np.array([1]*30+[-1]*30))
    H_null.append(H(ss))
H_null = np.array(H_null)
print(f"  隨機 (30/30): mean = {H_null.mean():.1f} ± {H_null.std():.1f}, 5%分位 = {np.percentile(H_null,5):.0f}")
z = (H_obs - H_null.mean())/H_null.std()
print(f"  觀測 z = {z:+.2f}")
p_low = (1 + (H_null <= H_obs).sum())/(1+len(H_null))
print(f"  觀測 vs 隨機 p (低尾) = {p_low:.4f}")
print(f"  → 觀測 {'接近基態' if H_obs < -30 else '遠離基態'}; 基態 −56, 觀測 {H_obs:.0f}, 差 {H_obs+56:.0f}")

# ═══ B. 斷阻挫邊 ═══
print(f"\n[B] 斷阻挫邊統計")
fr = [(u,v) for u,v in edges if cspin[u]==cspin[v]]
nm = [(u,v) for u,v in edges if cspin[u]!=cspin[v]]
broken = sum(1 for u,v in fr if s_obs[u]!=s_obs[v])
new_wall = sum(1 for u,v in nm if s_obs[u]==s_obs[v])
print(f"  阻挫邊 (著色同號): {len(fr)} 條; 觀測斷咗 {broken} 條 ({100*broken/len(fr):.1f}%)")
print(f"  正常邊 (著色反號): {len(nm)} 條; 觀測新增牆 {new_wall} 條 ({100*new_wall/len(nm):.1f}%)")
print(f"  隨機 flip 23/60 期望: 斷 {len(fr)*2*23/60*(1-23/60):.1f}, 新牆 {len(nm)*2*23/60*(1-23/60):.1f}")
# 觀測 vs null
nflip = int((cspin != s_obs).sum())
null_b, null_n = [], []
for _ in range(20000):
    fl = rng.choice(60, nflip, replace=False)
    ss = cspin.copy(); ss[fl] *= -1
    null_b.append(sum(1 for u,v in fr if ss[u]!=ss[v]))
    null_n.append(sum(1 for u,v in nm if ss[u]==ss[v]))
null_b = np.array(null_b); null_n = np.array(null_n)
print(f"  null (同 flip 數): 斷 {null_b.mean():.1f}±{null_b.std():.1f}, 新牆 {null_n.mean():.1f}±{null_n.std():.1f}")
print(f"  觀測斷 {broken} → z = {(broken-null_b.mean())/null_b.std():+.2f}")
print(f"  觀測新牆 {new_wall} → z = {(new_wall-null_n.mean())/null_n.std():+.2f}")

# ═══ C. 多極功率 ═══
print(f"\n[C] A5 節點場多極功率 (ℓ=1..6)")
def real_sph(l, m, v):
    # 實球諧 (手動實現, 避開 scipy sph_harm API 變動)
    from scipy.special import lpmv
    theta = np.arccos(np.clip(v[:,2],-1,1)); phi = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm * P
    if m > 0: return math.sqrt(2) * norm * P * np.cos(am*phi)
    return math.sqrt(2) * norm * P * np.sin(am*phi)
Tz = (T - T.mean())
pow_obs = {}
for l in range(1,7):
    B = np.column_stack([real_sph(l,m,vecs) for m in range(-l,l+1)])
    coef, *_ = np.linalg.lstsq(B, Tz, rcond=None)
    pow_obs[l] = float((coef**2).sum())
tot = sum(pow_obs.values())
print(f"  {'ℓ':>3} {'功率':>10} {'佔比':>7} {'null mean':>10} {'p':>7}")
for l in range(1,7):
    B = np.column_stack([real_sph(l,m,vecs) for m in range(-l,l+1)])
    null_p = []
    for _ in range(3000):
        coef, *_ = np.linalg.lstsq(B, rng.permutation(Tz), rcond=None)
        null_p.append((coef**2).sum())
    null_p = np.array(null_p)
    p = (1+(null_p >= pow_obs[l]).sum())/(1+len(null_p))
    print(f"  {l:>3} {pow_obs[l]:>10.1f} {100*pow_obs[l]/tot:>6.1f}% {null_p.mean():>10.1f} {p:>7.3f}")

# ═══ D. k 分層身份 ═══
print(f"\n[D] k 分層身份 — 邊個係結構強制?")
kd = np.array([sum(1 for e in edges if cspin[e[0]]==cspin[e[1]] and i in e) for i in range(60)])
print(f"  n(k=0)={int((kd==0).sum())}, n(k=1)={int((kd==1).sum())}, n(k=2)={int((kd==2).sum())}")
print(f"  ★ 結構強制推導 (唯一):")
print(f"    每奇面 1 條阻挫邊 → #PS=12 (#⬠), #ST=20 (#Δ)")
print(f"    k=2 = PS端點 ∩ ST端點; k=1 = 對稱差; k=0 = 補集")
print(f"    ⟹ n(k=2) = #(PS∩ST) = 12, n(k=1) = 40, n(k=0) = 8")
print(f"  ⚠️ 但 #PS=12 同 #ST=20 本身來自 奇面數 (12⬠, 20Δ) — 面數係幾何事實, 唔係數值巧合")
print(f"  → 結構鏈: 面數 (20Δ,12⬠) → 阻挫邊分類 → 端點/連接器 → 8/40/12")

res = {'H_coloring': H_col, 'H_obs': H_obs, 'H_null_mean': float(H_null.mean()),
       'H_null_std': float(H_null.std()), 'H_obs_z': float(z), 'H_obs_p': float(p_low),
       'broken_frustration': broken, 'broken_z': float((broken-null_b.mean())/null_b.std()),
       'new_walls': new_wall, 'new_walls_z': float((new_wall-null_n.mean())/null_n.std()),
       'multipole_power': {str(l): pow_obs[l] for l in pow_obs}}
with open(f'{O143}/data/step19_ising_multipole.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step19_ising_multipole.json")
