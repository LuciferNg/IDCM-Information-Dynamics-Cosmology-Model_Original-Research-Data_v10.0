#!/usr/bin/env python3
"""
O137 — A₅ 集獨立驗證 (Part 1): 幾何 + 群論 + 動差結構

驗證 O136 docs/19 嘅「A₅ 動差準則」宣稱:
  ① A₅ 60 節點 = spherical 5-design: Σ_i P_l(v_i·c) = 0 for 1 ≤ l ≤ 5
  ② 額外零動差 l ∈ {7,8,9,11,13,14}; 非零 l ∈ {6,10,12,15,16}
  ③ 質量無關選擇律 → 9 模式 {1,2,3,4,5,7,9,11,13}

獨立手段 (唔用 O136 腳本):
  (a) 由第一性原理重建 icosahedral rotation group I (階 60)
  (b) Molien 級數 → dim(Sym^l)^I → 判斷邊啲動差【必然】為零 (群論硬約束)
  (c) 直接計算 Legendre 動差 + 多軸檢驗 (區分「恆零」vs「軸特定」)
  (d) 檢驗節點集是否精確 icosahedral orbit
"""
import numpy as np, math
from pathlib import Path
from itertools import permutations

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
nodes = np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
V = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
V /= np.linalg.norm(V, axis=1, keepdims=True)
N = len(V)
print(f"節點數: {N}")

# ══════════ 1. 重建 icosahedral rotation group ══════════
print("\n" + "="*80); print("1. Icosahedral rotation group I (階 60) 重建"); print("="*80)
phi = (1+math.sqrt(5))/2
def rot(axis, ang):
    a = np.array(axis, float); a /= np.linalg.norm(a)
    K = np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3) + math.sin(ang)*K + (1-math.cos(ang))*K@K
R1 = rot([0,1,phi], 2*math.pi/5)
R2 = rot([1,1,1], 2*math.pi/3)
group = [np.eye(3)]; frontier = [np.eye(3)]
while frontier:
    new = []
    for g in frontier:
        for h in (R1, R2):
            p = h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in group):
                group.append(p); new.append(p)
    frontier = new
print(f"|I| = {len(group)}  {'✅' if len(group)==60 else '🔴'}  (期望 60)")
# 驗證: icosahedron 12 頂點被置換
ico = []
for p in permutations([0,1,-1],3):
    pass
ico_set = set()
base = [(0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi)]
for b in base:
    for perm in [(0,1,2),(1,2,0),(2,0,1)]:
        ico_set.add(tuple(b[i] for i in perm))
ico = np.array(sorted(ico_set), float); ico /= np.linalg.norm(ico,axis=1,keepdims=True)
print(f"Icosahedron 頂點數: {len(ico)}")
ok = True
for g in group:
    W = ico @ g.T
    D = W @ ico.T
    idx = np.argmax(D, axis=1)
    if np.degrees(np.arccos(np.clip(D[np.arange(12),idx],-1,1))).max() > 1e-6: ok=False
print(f"群置換 icosahedron: {'✅' if ok else '🔴'}")

# ══════════ 2. 節點集是否精確 I-orbit? ══════════
print("\n" + "="*80); print("2. 節點集是否精確 icosahedral orbit?"); print("="*80)
maxdev = 0.0; worst = None
for g in group:
    W = V @ g.T
    D = W @ V.T
    idx = np.argmax(D, axis=1)
    dev = np.degrees(np.arccos(np.clip(D[np.arange(N),idx],-1,1)))
    if dev.max() > maxdev: maxdev, worst = dev.max(), g
    if len(set(idx.tolist())) != N: print("  🔴 非單射!")
print(f"群作用下最大偏差: {maxdev:.6f}°  ({'✅ 精確 orbit' if maxdev<0.01 else '🔴 唔係精確 orbit'})")
# 最近鄰結構
D = np.arccos(np.clip(V@V.T,-1,1)); np.fill_diagonal(D, np.pi)
nn = np.sort(D, axis=1)[:,0]
print(f"最近鄰角距: min={np.degrees(nn).min():.4f}° max={np.degrees(nn).max():.4f}° std={np.degrees(nn).std():.4f}°")
print(f"最近鄰數 (25°內): {[int((np.degrees(D[i])<25).sum()) for i in range(3)]} (前3節點)")

# ══════════ 3. Molien 級數 → 群論硬約束 ══════════
print("\n" + "="*80); print("3. Molien 級數 → dim(Sym^l)^I (群論硬約束)"); print("="*80)
LMAX = 26
angles = []
for g in group:
    tr = np.trace(g)
    angles.append(math.acos(max(-1,min(1,(tr-1)/2))))
ser = np.zeros(LMAX+1)
for th in angles:
    c = math.cos(th)
    U = [1.0]; 
    if LMAX>=1: U.append(2*c)
    for k in range(2, LMAX+1): U.append(2*c*U[-1]-U[-2])
    U = np.array(U[:LMAX+1])
    ones = np.ones(LMAX+1)
    ser += np.convolve(ones, U)[:LMAX+1]
ser /= len(group)
dimSym = np.round(ser).astype(int)
h = np.array([dimSym[l] - (dimSym[l-2] if l>=2 else 0) for l in range(LMAX+1)])
print(f"\n{'l':>3} {'dim(Sym^l)^I':>13} {'h(l) 調和':>10}  群論判決")
for l in range(1, LMAX+1):
    verdict = "★ 必然為零 (h=0)" if h[l]==0 else "可非零"
    print(f"{l:>3} {dimSym[l]:>13} {h[l]:>10}  {verdict}")

# ══════════ 4. Legendre 動差 ══════════
print("\n" + "="*80); print("4. Legendre 動差 Σ_i P_l(v_i·c)"); print("="*80)
lb = (math.radians(209.0), math.radians(-57.0))
cold = np.array([math.cos(lb[1])*math.cos(lb[0]), math.cos(lb[1])*math.sin(lb[0]), math.sin(lb[1])])
print(f"冷斑軸 (209°,−57°) 視為 (l,b): {np.round(cold,6)}")
x_cold = V @ cold
# 檢查有無節點貼近冷斑
print(f"節點到冷斑軸角距: min={np.degrees(np.arccos(x_cold)).min():.4f}° (最近節點 #{np.argmax(x_cold)})")

rng = np.random.default_rng(20260830)
RAND = rng.normal(size=(400,3)); RAND /= np.linalg.norm(RAND,axis=1,keepdims=True)

docs19_zero = {1,2,3,4,5,7,8,9,11,13,14}
docs19_nonzero = {6,10,12,15,16}
print(f"\n{'l':>3} {'Σ P_l (冷斑軸)':>16} {'max|ΣP_l| 隨機軸':>17} {'h(l)':>6} {'docs19':>8} {'獨立判定':>22}")
pattern = {}
for l in range(1, LMAX+1):
    Pl = np.polynomial.legendre.Legendre.basis(l)
    s_cold = float(Pl(x_cold).sum())
    s_rand = max(abs(float(Pl(RAND@V.T).sum(axis=1).max())), abs(float(Pl(RAND@V.T).sum(axis=1).min())))
    if l in docs19_zero: d19 = "零"
    elif l in docs19_nonzero: d19 = "非零"
    else: d19 = "—"
    # 獨立判定: 隨機軸 max 亦近零 ⟹ 恆零
    if s_rand < 1e-6: verdict = "恆零 ✅"
    elif h[l]==0: verdict = "恆零 (h=0) ✅"
    else: verdict = "非零"
    pattern[l] = (s_cold, s_rand, verdict)
    flag = "" if (d19=="—" or (d19=="零")==(verdict.startswith("恆零"))) else "  ⚠️ 衝突"
    print(f"{l:>3} {s_cold:>16.6f} {s_rand:>17.6f} {h[l]:>6} {d19:>8} {verdict:>22}{flag}")

# ══════════ 5. 選擇律 ══════════
print("\n" + "="*80); print("5. A₅ 動差準則 → 模式選擇"); print("="*80)
Tn = np.polynomial.chebyshev.Chebyshev.basis
def a0(n):
    # (1/2)∫_{-1}^1 T_n(x)dx = 1/(1-n²) for even n, 0 for odd
    return 0.0 if n%2==1 else 1.0/(1-n*n)
sel = []
print(f"\n{'n':>3} {'Σ T_n(cos β)':>15} {'60·a₀(n)':>12} {'差':>13} {'選中':>5}")
for n in range(1, 45):
    s = float(Tn(n)(x_cold).sum())
    t = 60*a0(n)
    ok = abs(s-t) < 1e-6
    if ok: sel.append(n)
    print(f"{n:>3} {s:>15.6f} {t:>12.6f} {s-t:>13.2e} {'★' if ok else '':>5}")
print(f"\n★ 選中模式 = {sel}")
print(f"★ O136 docs/19 宣稱 = [1,2,3,4,5,7,9,11,13]")
print(f"★ 一致: {sel == [1,2,3,4,5,7,9,11,13]}  (共 {len(sel)} 個)")

np.save("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/a5_nodes_unit.npy", V)
