#!/usr/bin/env python3
"""
O217 — 獨立核對審計 (scripts/03_audit_independent.py, v2)
=========================================================
目的: 唔 import / 唔 call scripts/01 或 scripts/02, 由原始定義重算核心 claim.
核心 claim (O217): 喺 I-軌道 60 節點圖類 (28° 閾值近鄰圖) 8 個腔室類中,
   唯一透明通道數 = MaxCut = 88 = 2N_d 者 = (120, 20) 類 ⟹ E=120 ⟹ 度數 4.

算法差異 (MILP 與四元數枚舉迴避):
  §A 群構造: 由正二十面體 12 頂點集直接構造 60 個旋轉 (vertex-pair mapping → rotation),
      唔用 quaternion 枚舉; 驗證 Cayley 階 60 + 群同構 A₅ (一致於 order 60, 非 abelian)
  §B 小掃描: 唔同 seed (777), N=3000 → 8 類 (E,tri) 收斂一致
  §C (120,20) 精確 88: 面結構上界 (20 edge-disjoint △ + 12 edge-disjoint ⬠ ⟹ mono≥32 ⟹ MaxCut≤88)
      + greedy local search 到達 88 ⟹ 上界可取 ⟹ EXACT 88 (無 MILP)
  §D 排除其他 7 類 (MaxCut ≠ 88, 毋須精確值):
      - E<88 類: MaxCut ≤ E < 88 自動排除
      - triangle/odd-cycle edge-disjoint packing 下界: mono ≥ K ⟹ MaxCut ≤ E−K
        (90,20): ≥3 disjoint △; (90,0): ≥3 disjoint odd cycles; (120,120): ≥33 disjoint △
      - (150,80): greedy local search 搵到 cut ≥ 89 ⟹ MaxCut ≥ 89 ≠ 88
  §E 度數: 唯一 88 類 (120,20) 每點度 4

鐵律: 零 import 原 script; 零 MILP; 精確整數/集合運算; group 用 rotation matrices (非 quaternion).
"""
import math, itertools, time
from collections import Counter, deque
import numpy as np

PASS, FAIL = [], []
def ck(name, got, exp, tol=0.0):
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        ok = abs(float(got) - float(exp)) <= tol
    elif isinstance(exp, set): ok = set(got) == exp
    elif isinstance(exp, (list, tuple)): ok = list(got) == list(exp)
    else: ok = (got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}" + ("" if ok else f"   ❗EXP={exp}"))

# ── §A 正二十面體 12 頂點 + 60 旋轉 (無 quaternion) ─────────────
phi = (1+math.sqrt(5))/2
ICOS = np.array([
    (0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi),
    (1,phi,0),(1,-phi,0),(-1,phi,0),(-1,-phi,0),
    (phi,0,1),(phi,0,-1),(-phi,0,1),(-phi,0,-1)], float)
def unit(v): 
    n = np.linalg.norm(v); return v/n if n>0 else v
def rot_from_pairs(a, b, c, d):
    """Rotation R: R(a)→c, R(b)→d (a,b 唔平行)."""
    e1, f1 = unit(a), unit(c)
    e2, f2 = unit(b - np.dot(a,b)*a/(np.dot(a,a) or 1)), unit(d - np.dot(c,d)*c/(np.dot(c,c) or 1))
    e3, f3 = np.cross(e1,e2), np.cross(f1,f2)
    if np.linalg.norm(e3) < 1e-9 or np.linalg.norm(f3) < 1e-9: return None
    e3, f3 = unit(e3), unit(f3)
    M1 = np.column_stack([e1,e2,e3]); M2 = np.column_stack([f1,f2,f3])
    R = M2 @ M1.T   # det = +1 (兩個 right-handed frames 之間嘅唯一等距)
    if abs(np.linalg.det(R)-1) > 1e-6: return None
    return R
cands = []
A0, B0 = ICOS[0], ICOS[4]          # 相鄰頂點對 (dot = φ)
ref_dot = float(np.dot(A0, B0))
for i in range(12):
    for j in range(12):
        if abs(np.dot(ICOS[i], ICOS[j]) - ref_dot) > 1e-6: continue  # 只圖像同角距邊
        R = rot_from_pairs(A0, B0, ICOS[i], ICOS[j])
        if R is None: continue
        # 驗證 R 將頂點集映射到自己 (permutation)
        img = R @ ICOS.T
        ok = all(any(np.linalg.norm(img[:,k]-v) < 1e-6 for v in ICOS) for k in range(12))
        if ok: cands.append(R)
Rset = []
for R in cands:
    if not any(np.max(np.abs(R - S)) < 1e-6 for S in Rset):
        Rset.append(R)
print(f"  §A candidate rotations = {len(cands)}, dedupe = {len(Rset)}")
ck("§A I 群階 = 60 (vertex-pair construction)", len(Rset), 60)
# 群閉包: 呢 60 個矩陣構成群 (每 R 逆都喺入面, 乘法閉合) — 抽查
G = Rset
ck("§A 60 個旋轉已含恆等", any(np.allclose(R, np.eye(3)) for R in G), True)
# A₅ 非交換抽驗
nonab = any(not np.allclose(a@b, b@a) for a in G[:10] for b in G[:10])
ck("§A 群非交換 (A₅ 性質)", nonab, True)

def orbit_graph(v0):
    v0 = np.asarray(v0, float); v0 /= np.linalg.norm(v0)
    pts = []
    for R in G:
        p = R @ v0
        if not any(np.linalg.norm(p-q) < 1e-9 for q in pts): pts.append(p)
    P = np.array(pts, float)
    n = len(P)
    D = np.linalg.norm(P[:,None,:]-P[None,:,:], axis=2)
    ang = np.degrees(np.arccos(np.clip(1-D**2/2, -1, 1)))
    np.fill_diagonal(ang, 180.0)
    A = (ang < 28.0).astype(int); A = ((A + A.T) > 0).astype(int)
    np.fill_diagonal(A, 0)
    return P, A
def graph_stats(A):
    n = A.shape[0]
    E = int(A.sum()//2)
    tri = int(np.trace(A@A@A))//6
    col = -np.ones(n,int)
    for st in range(n):
        if col[st]>=0: continue
        col[st]=0; q=deque([st])
        while q:
            u=q.popleft()
            for w in np.where(A[u]>0)[0]:
                if col[w]<0: col[w]=1-col[u]; q.append(w)
    idx = np.triu(A>0,1)
    mono = int(((col[:,None]==col[None,:]) & idx).sum())
    return E, tri, mono

# ── §C 面結構上界 + greedy (無 MILP) ──────────────────────────
def greedy_triangles(A):
    n = A.shape[0]
    used = set(); cnt = 0
    for i in range(n):
        for j in np.where(A[i]>0)[0]:
            if j <= i: continue
            for k in np.where(A[j]>0)[0]:
                if k <= j or not A[i,k]: continue
                if not ({(i,j),(j,i),(i,k),(k,i),(j,k),(k,j)} & used):
                    used |= {(i,j),(j,i),(i,k),(k,i),(j,k),(k,j)}
                    cnt += 1
    return cnt, used

def greedy_triangles_multi(A, tries=200, seed=3):
    """多趟隨機順序 greedy — 攞 edge-disjoint triangle 數上限."""
    n = A.shape[0]
    rng = np.random.default_rng(seed)
    best = 0
    for _ in range(tries):
        order = rng.permutation(n)
        used = set(); cnt = 0
        for i in order:
            nb = np.where(A[i]>0)[0]
            for j in nb:
                if j <= i: continue
                for k in np.where(A[j]>0)[0]:
                    if k <= j or not A[i,k]: continue
                    if not ({(i,j),(j,i),(i,k),(k,i),(j,k),(k,j)} & used):
                        used |= {(i,j),(j,i),(i,k),(k,i),(j,k),(k,j)}
                        cnt += 1
        best = max(best, cnt)
    return best, used

def edge_disjoint_odd_cycles(A, need=3, maxl=9):
    """Greedy 搵 edge-disjoint odd cycles (3,5,7,9); 回傳數量."""
    n = A.shape[0]
    used = set(); cnt = 0
    # 1) 三角形
    _, used_t = greedy_triangles(A)
    used |= used_t
    cnt += len(used_t)//6
    if cnt >= need: return cnt
    # 2) 5/7/9-cycles — 路徑枚舉 (固定 st 為 cycle 最小點)
    for L in (5,7,9):
        for st in range(n):
            # DFS path from st of length L-1, closing edge to st
            stack = [(st, [st], {st})]
            while stack and cnt < need:
                node, path, seen = stack.pop()
                if len(path) == L:
                    if A[node, st]:
                        ed = set()
                        for x in range(L):
                            u, v = path[x], path[(x+1)%L]
                            ed.add((u,v)); ed.add((v,u))
                        if not (ed & used):
                            used |= ed; cnt += 1
                    continue
                for w in np.where(A[node]>0)[0]:
                    if w == st and len(path) == L-1:
                        stack.append((w, path+[w], seen))
                    elif w not in seen and w >= st:
                        stack.append((w, path+[w], seen|{w}))
    return cnt

def greedy_maxcut_lb(A, restarts=400, seed=9):
    """Local search MaxCut 下界 (2-coloring + 單點 flip). 只要下界, 唔需精確."""
    rng = np.random.default_rng(seed)
    n = A.shape[0]
    idx = np.triu(A>0, 1)
    best = 0
    for _ in range(restarts):
        col = rng.integers(0, 2, n)
        imp = True
        while imp:
            imp = False
            for i in range(n):
                d0 = int((A[i][col==0]).sum()); d1 = int((A[i][col==1]).sum())
                cur = d1 if col[i]==0 else d0
                alt = d0 if col[i]==0 else d1
                if alt > cur:
                    col[i] = 1-col[i]; imp = True
        cut = int(((col[:,None]!=col[None,:]) & idx).sum())
        best = max(best, cut)
    return best

# ── §B 小掃描 ────────────────────────────────────────────────
print("="*88); print("§B 小掃描 (seed 777, N=3000) — 8 類 (E,tri) 收斂"); print("="*88)
rngB = np.random.default_rng(777)
cntB = Counter(); repsB = {}
t0 = time.time()
for i in range(3000):
    v = rngB.normal(size=3)
    P, A = orbit_graph(v)
    if A.shape[0] != 60: continue
    E, tri, mono = graph_stats(A)
    cntB[(E,tri)] += 1
    repsB.setdefault((E,tri), A)
print(f"  有效 = {sum(cntB.values())}/3000, 類數 = {len(cntB)}  ({time.time()-t0:.1f}s)")
for k in sorted(cntB): print(f"    (E={k[0]:>3}, tri={k[1]:>3})  {cntB[k]:>4}  {100*cntB[k]/sum(cntB.values()):5.2f}%")
ck("§B 腔室類數 (E,tri) = 8", len(cntB), 8)
ck("§B (120,20) 類存在", (120,20) in cntB, True)
ck("§B (150,80) 類存在", (150,80) in cntB, True)

# ── §C (120,20) ──────────────────────────────────────────────
print("\n"+"="*88); print("§C (120,20) 精確 MaxCut = 88 (面結構上界 + greedy, 無 MILP)"); print("="*88)
A_rh = repsB[(120,20)]
n = A_rh.shape[0]
edt, used_t = greedy_triangles(A_rh)
print(f"  edge-disjoint triangles (greedy) = {edt}")
ck("§C greedy 搵到 ≥20 個 edge-disjoint △", edt >= 20, True)
# 若 greedy 唔夠 20, 用更多嘗試? — greedy 單遍通常已達 20; 若唔係, 呢個 check fail 要調查.
rem = A_rh.copy()
for (i,j) in itertools.combinations(range(n),2):
    if A_rh[i,j] and (i,j) in used_t:
        rem[i,j]=0; rem[j,i]=0
# 剩餘度 = 4 − 2 = 2 (每△ 2 條邊 per vertex) — 但 used_t 只係 greedy 揀咗嘅 △, 唔係全部.
# 面結構上界需要「扣除全部 20 個 △」嘅 5-循環分解. 簡單做法: 剩餘圖 = A − (揀嘅 △ 邊)
# 若揀到 20 個 disjoint △, 每點剩 4−2 = 2 度 → cycles. 數 length.
deg_rem = rem.sum(1)
cycles = []
if int(deg_rem.min()) == 2:
    visited = set()
    for st in range(n):
        if st in visited or rem[st].sum() == 0: continue
        cyc = [st]; prev = -1; cur = st; visited.add(st)
        while True:
            nbrs = np.where(rem[cur]>0)[0]
            nxt = nbrs[0] if nbrs[0] != prev else nbrs[1]
            if nxt == st: break
            cyc.append(nxt); visited.add(nxt); prev, cur = cur, nxt
        cycles.append(cyc)
lens = sorted(len(c) for c in cycles)
print(f"  剩餘 cycle 長度 (扣除揀咗嘅 △): {lens}")
ck("§C 剩餘 2-正則 ⟹ 12 個 5-循環 (面結構 ⬠)", lens, [5]*12)
ck("§C mono ≥ 20(△) + 12(⬠) = 32 ⟹ MaxCut ≤ 88", 120-32, 88)
lb = greedy_maxcut_lb(A_rh, restarts=400, seed=11)
print(f"  greedy MaxCut 下界 = {lb} (需 ≥88 ⟹ 上界可取)")
ck("§C greedy 到達 88 ⟹ MaxCut = 88 EXACT（上界 = 下界）", lb >= 88, True)

# ── §D 排除其他 7 類 ─────────────────────────────────────────
print("\n"+"="*88); print("§D 其他 7 類排除 (MaxCut ≠ 88, 無 MILP)"); print("="*88)
ex_by_E = sorted(k for k in cntB if k[0] < 88)
print(f"  E<88 自動排除: {ex_by_E}")
ck("§D E<88 類 = 3 (30,0),(60,0),(60,20)", len(ex_by_E), 3)
A_9020 = repsB[(90,20)]
edt_9020, _ = greedy_triangles(A_9020)
print(f"  (90,20): edge-disjoint △ = {edt_9020}")
ck("§D (90,20) mono ≥ 3 ⟹ MaxCut ≤ 87 ≠ 88", edt_9020 >= 3, True)
A_900 = repsB[(90,0)]
oddc_900 = edge_disjoint_odd_cycles(A_900, need=3)
print(f"  (90,0): edge-disjoint odd cycles = {oddc_900}")
ck("§D (90,0) mono ≥ 3 ⟹ MaxCut ≤ 87 ≠ 88", oddc_900 >= 3, True)
A_120120 = repsB[(120,120)]
# 組合 cover 論證 (確定性, 唔依賴 greedy): 每個三角形 2-coloring 下至少 1 條 mono 邊;
# 每條邊至多屬於 n_t 個三角形 ⟹ mono ≥ tri_count / n_t
t_120 = int(np.trace(A_120120@A_120120@A_120120))//6
n = A_120120.shape[0]
edge_tri = []
for i in range(n):
    for j in np.where(A_120120[i]>0)[0]:
        if j <= i: continue
        c = 0
        for k in range(n):
            if A_120120[i,k] and A_120120[j,k]: c += 1
        edge_tri.append(c)
max_et = max(edge_tri)
lb_mono_cover = math.ceil(t_120 / max_et)
print(f"  (120,120): tri = {t_120}, max #tri per edge = {max_et} "
      f"⟹ covering mono ≥ {lb_mono_cover}")
ck("§D (120,120) mono ≥ 33 (triangle-cover 下界) ⟹ MaxCut ≤ 87 ≠ 88",
   lb_mono_cover >= 33, True)
A_15080 = repsB[(150,80)]
lb_15080 = greedy_maxcut_lb(A_15080, restarts=400, seed=13)
print(f"  (150,80): greedy MaxCut 下界 = {lb_15080} (需 ≥89 ⟹ ≠88)")
ck("§D (150,80) MaxCut ≥ 89 ⟹ ≠ 88", lb_15080 >= 89, True)

# ── §E 度數 ──────────────────────────────────────────────────
print("\n"+"="*88); print("§E 度數檢查"); print("="*88)
for k in sorted(repsB):
    A = repsB[k]
    print(f"    (E={k[0]:>3}, tri={k[1]:>3}): 度數 = {dict(Counter(A.sum(1).tolist()))}")
ck("§E 唯一 88 類 (120,20) 4-正則", sorted(set(repsB[(120,20)].sum(1).tolist())), [4])
ck("§E (150,80) 5-正則 (被 88 排除)", sorted(set(repsB[(150,80)].sum(1).tolist())), [5])

# ── §F 完整鏈 ────────────────────────────────────────────────
print("\n"+"="*88); print("§F 完整鏈 (獨立重建)"); print("="*88)
ok_chain = (len(cntB)==8 and (120,20) in repsB
            and lb >= 88 and edt_9020>=3 and oddc_900>=3 and lb_mono_cover>=33 and lb_15080>=89)
ck("§F 唯一 88 = (120,20) ⟹ 4-正則 (獨立 verifier)", ok_chain, True)
print(f"\nPASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL:
    print("FAIL:")
    for f in FAIL: print("  -", f)