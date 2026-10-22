#!/usr/bin/env python3
"""
O179 — Script 07: 吸收截面權重盲測 (pre-registered, docs/05)
================================================================
O252 handoff 要求 2: 窗中心 μ_hat=235.7±21.6 需要「吸收截面權重」統計量.
三候選 (全部零新常數, 定義喺 docs/05 §3 預先凍結):
  W1: 阻挫端點密度  w1(h) = n_frust(h)
  W2: 干涉核        w2(h) = n(h)·[1 + (B/L5)·cos(πh/4)]
  W3: 層環截面      w3(h) = n(h)·h
判準: docs/05 §4 (命中 ≤21.6 / 兼容 ≤42.3 / 排除 >42.3); MC null 10^6 (沙漠檢查).
數據: cmb_cold_spot/data/(a5_nodes.txt, frustration_edges.txt) — O179 正典.
速度: v(h) = Vmax·√(h/8), Vmax = 409.78 (O252 R13)
""" 
import math, json, os, random
import numpy as np

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/data'
DATA = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/cmb_cold_spot/data'

# ---- 譜量 (O179 正典) ----
B, N_gen, N_d, L5, L4, mu2 = 4, 3, 44, 11, 7, 2
C = B/L5

MU_HAT, SE = 235.7, 21.6
CI_LO, CI_HI = MU_HAT - 1.96*SE, MU_HAT + 1.96*SE   # [193.4, 278.1]
VMAX = 409.78

results = []
def ck(name, cond, detail=''):
    results.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

# ---- 1. 由零讀圖 (同 scripts/01-06 一致) ----
def ang_dist(ra1, dec1, ra2, dec2):
    r1, d1 = math.radians(ra1), math.radians(dec1)
    r2, d2 = math.radians(ra2), math.radians(dec2)
    cd = math.sin(d1)*math.sin(d2) + math.cos(d1)*math.cos(d2)*math.cos(r1-r2)
    return math.degrees(math.acos(max(-1, min(1, cd))))

nodes = []
with open(f'{DATA}/a5_nodes.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split(); nodes.append((float(p[0]), float(p[1])))
N = len(nodes)
assert N == 60

dmat = np.array([[ang_dist(ra1, de1, ra2, de2) for ra2, de2 in nodes] for ra1, de1 in nodes])
adj_s = {i: set() for i in range(N)}
for i in range(N):
    for j in sorted(range(N), key=lambda k: dmat[i,k])[1:5]:
        adj_s[i].add(j)
for i in range(N):
    for j in list(adj_s[i]):
        adj_s[j].add(i)

frust = set()
with open(f'{DATA}/frustration_edges.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'): continue
        p = line.split()
        frust.add((min(int(p[0])-1, int(p[1])-1), max(int(p[0])-1, int(p[1])-1)))
assert len(frust) == 32

# 冷斑錨點 (209, -57) → BFS hop
cs = min(range(N), key=lambda i: ang_dist(209, -57, nodes[i][0], nodes[i][1]))
hop = [-1]*N; hop[cs] = 0; q = [cs]
for u in q:
    for v in adj_s[u]:
        if hop[v] == -1:
            hop[v] = hop[u] + 1; q.append(v)
H = max(hop)  # 直徑 8
n_h = [hop.count(h) for h in range(H+1)]  # [1,4,8,11,12,11,8,4,1]

# ---- 2. 三候選權重 (預先凍結定義) ----
# W1: 層 h 阻挫端點總數
frust_cnt = {i: 0 for i in range(N)}
for (u, v) in frust:
    frust_cnt[u] += 1; frust_cnt[v] += 1
w1 = [sum(frust_cnt[i] for i in range(N) if hop[i] == h) for h in range(H+1)]

# W2: n(h)·E(h), E(h)=1+C·cos(πh/4)
w2 = [n_h[h] * (1 + C*math.cos(math.pi*h/4)) for h in range(H+1)]

# W3: n(h)·h
w3 = [n_h[h]*h for h in range(H+1)]

# ---- 3. 速度映射 (O252 R13) ----
v = [VMAX*math.sqrt(h/8) for h in range(H+1)]
v[0] = 0.0

def wmean(w):
    sw = sum(w)
    if sw <= 1e-15: return None, sw
    return sum(ww*vv for ww, vv in zip(w, v))/sw, sw

def verdict(delta):
    if delta <= SE: return '🟢 命中'
    if delta <= 1.96*SE: return '🟡 兼容'
    return '🔴 排除'

print("="*72)
print("O179 Script 07 — 吸收截面權重盲測 (pre-registered docs/05)")
print("="*72)
print(f"target μ_hat={MU_HAT}±{SE}, CI=[{CI_LO:.1f},{CI_HI:.1f}]")
print(f"hop 階梯 n(h) = {n_h}, Σ={sum(n_h)}")
print(f"v(h) = {[round(x,2) for x in v]}")
print(f"\n--- 候選權重 ---")
for nm, w in [('W1 阻挫端點', w1), ('W2 干涉核', w2), ('W3 層環截面', w3)]:
    print(f"  {nm}: {[round(x,3) for x in w]}  (Σ={sum(w):.1f})")

print(f"\n--- 加權平均 (決策規則見 docs/05 §4) ---")
out = {'target': {'mu_hat': MU_HAT, 'se': SE, 'ci': [CI_LO, CI_HI]},
       'v_h': v, 'n_h': n_h, 'candidates': {}}
for nm, w in [('W1_frust', w1), ('W2_interference', w2), ('W3_ring_section', w3)]:
    mv, sw = wmean(w)
    delta = abs(mv - MU_HAT) if mv is not None else float('inf')
    vd = verdict(delta) if mv is not None else '⚫ VOID'
    print(f"  {nm}: ⟨v⟩_w = {mv:.3f} (Σw={sw:.2f}), Δ={delta:.2f} → {vd}")
    out['candidates'][nm] = {'w': w, 'mean_v': mv, 'delta': delta, 'verdict': vd}
    ck(f"{nm} 非 VOID/結構完好", mv is not None, "")

# baseline: 質量權重 (O252 R13) = 280.03
mv0, _ = wmean(n_h)
print(f"\n  baseline 質量權重: ⟨v⟩ = {mv0:.3f} (O252 已計 280.03, Δ={abs(mv0-MU_HAT):.2f} → 🔴)")
out['baseline_mass'] = {'mean_v': mv0, 'delta': abs(mv0-MU_HAT)}

# ---- 4. MC null (10^6) — 沙漠檢查 ----
print(f"\n--- MC null (10^6, docs/05 §5) ---")
rng = np.random.default_rng(42)
hits = {nm: 0 for nm in ['W1_frust', 'W2_interference', 'W3_ring_section']}
MC = 1_000_000
for _ in range(MC):
    for nm, w in [('W1_frust', w1), ('W2_interference', w2), ('W3_ring_section', w3)]:
        # 隨機層權重 ∝ n(h)·U(0,1)
        rw = np.array([n_h[h]*rng.random() for h in range(H+1)])
        mv = float(np.sum(rw*np.array(v))/np.sum(rw))
        if abs(mv - MU_HAT) <= 1.96*SE:
            hits[nm] += 1
null_info = {}
for nm in hits:
    pnull = hits[nm]/MC
    null_info[nm] = pnull
    tag = '⚠️ 低鑑別度(沙漠)' if pnull > 0.05 else '✅ 有鑑別度'
    print(f"  {nm}: p_null = {pnull:.4f}  {tag}")
    out['candidates'][nm]['p_null'] = pnull

# ---- 5. 總判定 (按 docs/05 §4/§5) ----
print(f"\n--- 總判定 ---")
n_hit = sum(1 for nm in ['W1_frust','W2_interference','W3_ring_section']
            if out['candidates'][nm]['verdict'].startswith('🟢'))
n_comp = sum(1 for nm in ['W1_frust','W2_interference','W3_ring_section']
             if out['candidates'][nm]['verdict'].startswith('🟡'))
print(f"  🟢 命中: {n_hit}  🟡 兼容: {n_comp}  🔴 排除: {3-n_hit-n_comp}")
if n_hit or n_comp:
    print("  吸收截面權重路徑有候選 — 窗中心身份有結構出路 (需更多源/樣本外)")
else:
    print("  三候選全排除 → 吸收截面權重路徑結構性排除, 窗中心身份維持開放 (O252 R13 reinforced)")
ok = sum(1 for _, p, _ in results if p)
print(f"\n  checks: {ok}/{len(results)} PASS")
out['checks'] = [{'name': n, 'pass': p, 'detail': d} for n, p, d in results]
out['summary'] = {'hit': n_hit, 'compatible': n_comp, 'excluded': 3-n_hit-n_comp}

with open(f'{OUT}/07_absorption_weight.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"Saved: {OUT}/07_absorption_weight.json")
print("PASS" if ok == len(results) else "FAIL")