#!/usr/bin/env python3
"""
O143 #18 — 著色等價性判定 + 寫入動力學 + 四極振幅
================================================
A. 30 個著色嘅 88 格係咪 congruent (旋轉等價)? Kabsch 殘差 + Gram 譜
B. 寫入動力學: flip 集合結構 — 同 color/k/hop/位置 嘅關係
C. 四極振幅: A5 節點集嘅四極洩漏 (sampling 結構性質)
"""
import numpy as np, math, json, re
from collections import defaultdict, deque, Counter
from scipy import stats

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'

nodes = np.loadtxt(f'{D}/a5_nodes.txt')
T = np.array(json.load(open(f'{BASE}/open_problems_fresh/o182_88grid_geometry/data/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
A = 134.2
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color0 = ac[:,3].astype(int)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
adj = defaultdict(set); edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))
hop = {0:0}; q = deque([0])
while q:
    x = q.popleft()
    for y in adj[x]:
        if y not in hop: hop[y] = hop[x]+1; q.append(y)

print("="*78); print("  O143 #18 — 等價性 + 寫入 + 四極"); print("="*78)

# ═══ A. 30 個著色嘅 88 格 congruence ═══
uniq = {}
for root in range(60):
    c = {root: 1}; qq = deque([root])
    while qq:
        u = qq.popleft()
        for v in adj[u]:
            if v not in c: c[v] = 1-c[u]; qq.append(v)
    fs = frozenset(tuple(sorted((u,v))) for u,v in edges if c[u]==c[v])
    if fs not in uniq: uniq[fs] = root

def mids(fs):
    return np.array([(vecs[u]+vecs[v])/np.linalg.norm(vecs[u]+vecs[v])
                     for u,v in edges if tuple(sorted((u,v))) not in fs])

grids = {r: mids(fs) for fs, r in uniq.items()}
print(f"\n[A] 30 個著色 → 88 格; 逐對 Kabsch 殘差 + Gram 譜")
ref = grids[0]
def gram_spec(M):
    return np.sort(np.linalg.eigvalsh(M @ M.T))
specs = {r: gram_spec(g) for r, g in grids.items()}
devs = {r: float(np.max(np.abs(specs[r] - specs[0]))) for r in grids}
print(f"  Gram 譜 vs 錨定版: max|Δλ| = {max(devs.values()):.2e}")
print(f"  全部 < 1e-9? {all(v < 1e-9 for v in devs.values())}")
# Kabsch for a few
def kabsch_res(Aa, Bb):
    # find R s.t. Aa ≈ Bb R (centered)
    Ac = Aa - Aa.mean(0); Bc = Bb - Bb.mean(0)
    H = Bc.T @ Ac
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    R = Vt.T @ np.diag([1,1,d]) @ U.T
    return float(np.abs(Bc @ R - Ac).max())
res_k = {r: kabsch_res(ref, grids[r]) for r in grids}
print(f"  Kabsch 殘差 (vs 錨定 88 格): max = {max(res_k.values()):.2e}, min = {min(res_k.values()):.2e}")
print(f"  全部 < 1e-6 (congruent)? {all(v < 1e-6 for v in res_k.values())}")

# ═══ B. 寫入動力學 ═══
print(f"\n{'='*78}"); print("[B] 寫入動力學: flip 集合結構"); print(f"{'='*78}")
signT = np.sign(T)
agree = (color0 == 1) == (signT < 0)
flip = ~agree
kd = np.array([sum(1 for e in edges if (color0[e[0]]==color0[e[1]]) and (i in e)) for i in range(60)])
print(f"\n  agreement = {agree.sum()}/60; flip 節點 = {flip.sum()}")
print(f"  {'k':>3} {'n':>3} {'flip':>5} {'flip率':>7} {'keep':>5}")
for kk in (0,1,2):
    m = kd == kk
    print(f"  {kk:>3} {m.sum():>3} {int((flip&m).sum()):>5} {100*(flip&m).sum()/m.sum():>6.1f}% {int((agree&m).sum()):>5}")
# 二項檢定: flip 率同 k 有關?
tab = [[int((flip&(kd==0)).sum()), int((agree&(kd==0)).sum())],
       [int((flip&(kd>0)).sum()), int((agree&(kd>0)).sum())]]
o, pf = stats.fisher_exact(tab)
print(f"  Fisher (k=0 vs k>0 flip 率): {tab}, p = {pf:.4f}")
# flip vs hop
print(f"\n  flip 率 vs hop:")
for h in range(9):
    m = np.array([hop[i]==h for i in range(60)])
    if m.sum()==0: continue
    print(f"    hop={h}: n={m.sum():>2}, flip={int((flip&m).sum())} ({100*(flip&m).sum()/m.sum():.0f}%)")
# flip 同 |T| 關係
print(f"\n  flip 節點 mean|T| = {np.abs(T[flip]).mean():.1f}; keep 節點 mean|T| = {np.abs(T[agree]).mean():.1f}")
u, pu = stats.mannwhitneyu(np.abs(T[flip]), np.abs(T[agree]), alternative='two-sided')
print(f"  MW p = {pu:.4f}")
# flip 係咪集中在某些縫?
fs_anchor = frozenset(tuple(sorted((u,v))) for u,v in edges if color0[u]==color0[v])
fadj = defaultdict(set)
for u,v in fs_anchor: fadj[u].add(v); fadj[v].add(u)
seen=set(); comps=[]
for i in range(60):
    if i in fadj and i not in seen:
        comp=[]; qq=deque([i])
        while qq:
            x=qq.popleft()
            if x in seen: continue
            seen.add(x); comp.append(x)
            for y in fadj[x]: qq.append(y)
        comps.append(sorted(comp))
print(f"\n  每條縫 (共 {len(comps)}) 嘅 flip 數:")
flip_per_seam = []
for c in comps:
    nf = sum(1 for x in c if flip[x])
    flip_per_seam.append((len(c), nf))
c_dist = Counter(flip_per_seam)
print(f"    分佈 (縫節點數, flip數): {dict(c_dist)}")
print(f"    0-flip 縫: {sum(1 for a,b in flip_per_seam if b==0)}; 全-flip 縫: {sum(1 for a,b in flip_per_seam if b==a)}")

# ═══ C. 四極洩漏 (sampling 結構) ═══
print(f"\n{'='*78}"); print("[C] A5 節點集四極洩漏 (sampling 性質)"); print("="*78)
# Fibonacci 軸網格
naxis = 4096
i = np.arange(naxis) + 0.5
phi = np.arccos(1 - 2*i/naxis)
golden = np.pi*(1+5**0.5)
theta = golden * i
axes = np.column_stack([np.sin(phi)*np.cos(theta), np.sin(phi)*np.sin(theta), np.cos(phi)])
s_all = 2*(vecs @ axes.T)**2 - 1   # (60, naxis)
# r_max over axes for observed T
Tz = (T - T.mean())/T.std()
r_obs = np.abs((s_all.T @ Tz)/60).max()
# null: permutation
rng = np.random.default_rng(11)
null = []
for _ in range(500):
    Tz2 = rng.permutation(Tz)
    null.append(np.abs((s_all.T @ Tz2)/60).max())
null = np.array(null)
p_perm = (1 + (null >= r_obs).sum())/(1+len(null))
print(f"  r_max (obs) = {r_obs:.4f}; null mean = {null.mean():.4f}, 95% = {np.percentile(null,95):.4f}")
print(f"  p_perm = {p_perm:.4f}  (p→1 = 反相關, 場比隨機更冇四極)")
# sampling 四極洩漏: 對純 cos2Θ 場 (無噪聲) 嘅 r_max 上限
# 若節點集完美 isotropic, 任何軸嘅 Σcos2Θ_i ≈ 0 → 四極內容被採樣壓抑
leak = np.abs((s_all.T @ np.ones(60))/60)
print(f"\n  節點集自身四極洩漏: max_â |Σ_i cos2Θ_i|/60 = {leak.max():.4f}")
print(f"  (uniform 60 點期望 max ≈ {0.13:.3f}; 若節點集特殊, 會細)")
# 對照: 60 個隨機均勻點
rng2 = np.random.default_rng(5)
rand_leaks = []
for _ in range(300):
    rr = rng2.normal(size=(60,3)); rr /= np.linalg.norm(rr, axis=1, keepdims=True)
    s_r = 2*(rr @ axes.T)**2 - 1
    rand_leaks.append(np.abs(s_r.T @ np.ones(60)/60).max())
rand_leaks = np.array(rand_leaks)
print(f"  隨機 60 點: mean = {rand_leaks.mean():.4f} ± {rand_leaks.std():.4f}")
z = (leak.max() - rand_leaks.mean())/rand_leaks.std()
print(f"  A5 節點集 z = {z:+.2f}  ({'特別低 (壓抑四極)' if z < -2 else '正常'})")

res = {'congruent_max_kabsch': float(max(res_k.values())),
       'gram_spec_max_dev': float(max(devs.values())),
       'flip_by_k': {str(kk): {'n': int((kd==kk).sum()), 'flip': int((flip&(kd==kk)).sum())} for kk in (0,1,2)},
       'flip_fisher_p': float(pf),
       'flip_mean_absT': float(np.abs(T[flip]).mean()), 'keep_mean_absT': float(np.abs(T[agree]).mean()),
       'flip_mw_p': float(pu),
       'flip_per_seam': {str(k): v for k, v in c_dist.items()},
       'quad_r_obs': float(r_obs), 'quad_null_mean': float(null.mean()), 'quad_p_perm': float(p_perm),
       'quad_leak_A5': float(leak.max()), 'quad_leak_rand_mean': float(rand_leaks.mean()),
       'quad_leak_rand_std': float(rand_leaks.std()), 'quad_leak_z': float(z)}
with open(f'{O143}/data/step15_congruence_write_quad.json', 'w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step15_congruence_write_quad.json")
