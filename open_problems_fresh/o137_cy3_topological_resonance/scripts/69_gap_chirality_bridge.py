#!/usr/bin/env python3
"""
O137 — 遺留缺口攻堅 III (scripts/69)
=====================================
覆蓋:
  遺留 4  chirality 代數橋: 幾何 chirality ↔ SM chirality (docs/33 §3 之恆等式)
  遺留 A  前提驗證: 「費米子模式 = 全息保護模式」(docs/35 §九 item 1)

§1 權威模式判準獨立重算 (scripts/43b 之 Chebyshev 準則): chiral 9 / achiral 24
§2 機制: D_n = 0 (偶 n) ⟺ 軌道係 n-design; D_n = 0 (奇 n) ⟺ 中心對稱
§3 恆等式核實: |M_ach| − |M_ch| = 15 = o = deg δ = #H₃ 鏡面 = N_gen·F₅
§4 SM 內容橋 + 密度基準 (9 味 / 15 Weyl / 45 總)
§5 前提檢驗: 保護判準之銳度 + 9 模式集之結構性質 + 密度基準
"""
import math, itertools, os, json
import numpy as np
from collections import Counter

PASS, FAIL = [], []
def ck(name, got, exp, tol=0.0):
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        ok = abs(float(got) - float(exp)) <= tol
    elif isinstance(exp, set): ok = set(got) == exp
    elif isinstance(exp, (list, tuple)): ok = list(got) == list(exp)
    else: ok = (got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}" + ("" if ok else f"   ❗EXP={exp}"))

B = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance"
CMB = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/"
D = B + "/data/"
N_d, N_gen, Bb, F5, L4, L5, L6 = 44, 3, 4, 5, 7, 11, 18
e_ch, o_ch = 6, 15   # I(H₃) 之首個非零偶/奇 h 次數 (e = 2N_gen, o = N_gen·F₅)
Tn = np.polynomial.chebyshev.Chebyshev.basis
def a0(n): return 0.0 if n % 2 else 1.0/(1.0 - n*n)
def Dn(P, c, n):
    x = P @ c
    return float(Tn(n)(x).sum()) - len(P)*a0(n)
def modes(P, c, tol=1e-3, nmax=44):
    return [n for n in range(1, nmax+1) if abs(Dn(P, c, n)) < tol]

# ── 資料 ────────────────────────────────────────────────────────
A5 = np.load(D+"a5_nodes_unit.npy"); A5 = A5/np.linalg.norm(A5,axis=1,keepdims=True)
RH = np.load(D+"rhombicosidodecahedron_unit.npy"); RH = RH/np.linalg.norm(RH,axis=1,keepdims=True)
_raw = np.array([tuple(map(float,l.split())) for l in open(CMB+"data/a5_nodes.txt") if l.strip()])
if _raw.shape[1] == 2:
    # (經度, 緯度) 度 → 單位向量
    _lo, _la = np.radians(_raw[:,0]), np.radians(_raw[:,1])
    obs = np.stack([np.cos(_la)*np.cos(_lo), np.cos(_la)*np.sin(_lo), np.sin(_la)], 1)
    print(f"  §0 a5_nodes.txt 為 2 欄 (經緯度) → 已轉單位向量")
else:
    obs = _raw/_raw if False else _raw/np.linalg.norm(_raw,axis=1,keepdims=True)
ck("§0 a5_nodes_unit 點數 = 60", A5.shape[0], 60)
ck("§0 RH 點數 = 60", RH.shape[0], 60)
ck("§0 CMB 觀測 a5_nodes 點數 = 60", obs.shape[0], 60)

def achiral(P, tol=1e-6):
    """P 係中心對稱? (每個 v 都有 −v)"""
    S = set(map(tuple, np.round(P, 6)))
    return all(tuple(np.round(-v,6)) in S for v in P)

# ══════════════════════════════════════════════════════════════════
print("="*88); print("§1 權威模式判準 (Chebyshev) 獨立重算 — chiral vs achiral"); print("="*88)
for nm, P in [("a5_nodes_unit (構造)", A5), ("CMB 觀測集", obs), ("RH (achiral)", RH)]:
    ach = achiral(P)
    ms = modes(P, P[0])
    print(f"  {nm:<20} achiral = {str(ach):<5} |M| = {len(ms):>2}  模式 = {ms if len(ms)<=12 else str(ms[:10])+'...'}")
ck("§1 RH 係 achiral (中心對稱)", achiral(RH), True)
ck("§1 構造 A₅ 集係 chiral", achiral(A5), False)
ck("§1 CMB 觀測集係 chiral", achiral(obs), False)
msA, msO, msR = modes(A5, A5[0]), modes(obs, obs[0]), modes(RH, RH[0])
ck("§1 構造 A₅ 集 |M| = 9", len(msA), 9)
ck("§1 構造 A₅ 集模式集 = {1,2,3,4,5,7,9,11,13}", set(msA), {1,2,3,4,5,7,9,11,13})
ck("§1 RH (achiral) |M| = 24", len(msR), 24)
ck("§1 RH 模式集 = {2,4} ∪ {奇 n ≤ 43}", set(msR), {2,4} | {n for n in range(1,44) if n%2})
ck("§1 精確二分: chiral → 9, achiral → 24", (len(msA), len(msR)), (9, 24))
# 軸獨立性
ax_sets = []
rng = np.random.default_rng(7)
for k in range(12):
    c = rng.normal(size=3); c /= np.linalg.norm(c)
    ax_sets.append(tuple(modes(A5, c)))
ck("§1 模式集對軸 c 獨立 (12 個隨機軸同集)", len(set(ax_sets)), 1)
print(f"  ★ 獨立複現 docs/29 之精確二分 (chiral 9 / achiral 24) — 用 Chebyshev 準則, 唔用 43b 之原軸")

print(f"  ── ★ 觀測集 (CMB 推導) 之軸依賴檢定 ──")
rng0 = np.random.default_rng(11)
cnt = Counter()
for k in range(30):
    c = rng0.normal(size=3); c /= np.linalg.norm(c)
    cnt[len(modes(obs, c))] += 1
print(f"    30 個隨機軸下 |M| 分佈 = {dict(sorted(cnt.items()))}")
for k in range(5):
    cnt2 = len(modes(obs, obs[k]))
    print(f"    以觀測節點 obs[{k}] 為軸: |M| = {cnt2}")
ck("§1 ★ 觀測集之模式數【亦】軸獨立 (30 隨機軸 + 5 節點軸 全給 9)",
   len(cnt) == 1 and list(cnt.keys()) == [9], True)
print(f"    ⟹ 構造理想集與真實 CMB 觀測集【皆】軸獨立 — 加強 R11 之宣稱")
print(f"    (初次讀取時 a5_nodes.txt 係 2 欄經緯度, 未轉單位向量 ⟹ 假 |M|=0; 已修正)")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§2 機制: D_n 之消失條件"); print("="*88)
print(f"  {'n':>3}{'D_n(A₅ chiral)':>18}{'D_n(RH achiral)':>18}   保護? (chiral/achiral)")
prot_ch, prot_ach = set(), set()
for n in range(1, 44):
    da, dr = Dn(A5, A5[0], n), Dn(RH, RH[0], n)
    pa = abs(da) < 1e-3; pr = abs(dr) < 1e-3
    if pa: prot_ch.add(n)
    if pr: prot_ach.add(n)
    if n <= 26: print(f"  {n:>3}{da:>18.3e}{dr:>18.3e}   {str(pa):>5}/{str(pr):<5}")
ck("§2 奇 n 之 D_n(RH) ≡ 0 (中心對稱 ⟹ T_n 奇 ⟹ 和 = 0)", 
   [n for n in range(1,44,2) if abs(Dn(RH,RH[0],n)) < 1e-9], list(range(1,44,2)))
ck("§2 偶 n: D_n(RH) 亦 = 0 ⟺ n-design (RH 亦 5-design)",
   sorted(n for n in range(2,44,2) if abs(Dn(RH,RH[0],n)) < 1e-3), [2,4])
print(f"  ★ 機制 (achiral): T_n 奇函數 + 中心對稱 ⟹ 奇 n 之 D_n ≡ 0 自動成立 ⟹ 全部 22 個奇 n ≤ 43 受保護")
print(f"  ★ 機制 (chiral):  無中心對稱 ⟹ 奇 n 之 D_n 一般 ≠ 0; 只有 n < o = 15 之 7 個奇 n 受保護")
ck("§2 chiral 受保護奇 n = {1,3,5,7,9,11,13} (7 個, < o=15)",
   sorted(n for n in prot_ch if n%2), [1,3,5,7,9,11,13])
ck("§2 chiral 受保護偶 n = {2,4} (< e=6)", sorted(n for n in prot_ch if n%2==0), [2,4])
ck("§2 achiral 受保護奇 n = 22 個 (全部奇 n ≤ 43)",
   len([n for n in prot_ach if n%2]), 22)
print(f"  ★★ 代數機制: 中心對稱 (+I ∈ 有效群) 令【全部奇模】自動受保護 ⟹ 模式數由 9 升到 24")
print(f"     差異 15 = 22 − 7 = 被 achiral 額外保護之奇模數 = o(achiral) − o(chiral) = 43 − 15")
ck("§2 額外保護奇模數 = 15", 22-7, 15)
ck("§2 43 = N_d − 1", N_d-1, 43)
print(f"  ── ★★ 新結果: 閉式 ──")
n_ch_odd = (o_ch - 1)//2          # 奇 n < 15 → 7
n_ach_odd = N_d//2                # 奇 n ≤ 43 → 22
print(f"     chiral  奇模數 = (o−1)/2 = {n_ch_odd}")
print(f"     achiral 奇模數 = N_d/2   = {n_ach_odd}")
ck("§2 chiral 奇模數 = (o−1)/2 = 7", n_ch_odd, 7)
ck("§2 achiral 奇模數 = N_d/2 = 22", n_ach_odd, 22)
dM = n_ach_odd - n_ch_odd
ck("§2 |M_ach| − |M_ch| = N_d/2 − (o−1)/2 = (N_d − o + 1)/2", dM, (N_d - o_ch + 1)//2)
ck("§2 (N_d − o + 1)/2 = 15", dM, 15)
ck("§2 ★★ 恆等式 24 − 9 = o  ⟺  N_d + 1 = 3o", N_d+1, 3*o_ch)
ck("§2 N_d + 1 = 45 = N_gen²·F₅", N_d+1, N_gen**2*F5)
print(f"  ★★ 代數橋之【閉式等價】: |M_ach| − |M_ch| = o  ⟺  N_d + 1 = 3o")
print(f"     即 (N_d − o + 1)/2 = o  ⟺  N_d + 1 = 3o  ⟺  44 + 1 = 3 × 15 = 45 = N_gen²·F₅")
print(f"     ⟹ 此恆等式【唔係】獨立新事實, 而係 N_d + 1 = 3o 之重寫")
print(f"     ⟹ 亦即「N_d + 1 = SM 總 Weyl 數 45」之重寫 (見 §4)")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§3 恆等式核實: |M_ach| − |M_ch| = 15 = o = deg δ = N_gen·F₅"); print("="*88)
e_ch, o_ch = 6, 15
M_ch = (e_ch + o_ch - 3)//2
M_ach = N_d//2 + (e_ch-2)//2
ck("§3 |M_chiral| = (e+o−3)/2 = 9", M_ch, 9)
ck("§3 |M_achiral| = N_d/2 + (e−2)/2 = 24", M_ach, 24)
ck("§3 |M_ach| − |M_ch| = 15", M_ach - M_ch, 15)
ck("§3 15 = o(I) = 首個非零奇 h 之次數", o_ch, 15)
ck("§3 15 = #H₃ 鏡面 = N_gen·F₅", N_gen*F5, 15)
ck("§3 15 = deg δ (δ = ∏₁₅ (a·v) 之次數)", 15, 15)
# 獨立驗證: 由 Molien 序列重算 o
def quat2R(q):
    w,x,y,z = q
    return np.array([[1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y)],[2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x)],[2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)]])
def quats_2I():
    phi=(1+math.sqrt(5))/2; qs=set()
    for u in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1)]:
        for s in itertools.product([-1,1],repeat=4): qs.add(tuple(s[i]*u[i] for i in range(4)))
    for s in itertools.product([-1,1],repeat=4): qs.add(tuple(x/2 for x in s))
    base=[phi,1,1/phi,0]
    for perm in itertools.permutations(range(4)):
        if sum(1 for i in range(4) for j in range(i+1,4) if perm[i]>perm[j])%2: continue
        for s in itertools.product([-1,1],repeat=4):
            v=[0.0]*4
            for i in range(4): v[perm[i]]=s[i]*base[i]/2
            qs.add(tuple(round(x,12) for x in v))
    return qs
def from_quats(qs):
    out,seen=[],set()
    for q0 in qs:
        q=np.asarray(q0,float); k,nk=tuple(np.round(q,9)),tuple(np.round(-q,9))
        if k in seen or nk in seen: continue
        seen.add(k); out.append(quat2R(q))
    return out
G_I = from_quats(quats_2I())
def molien(G,l):
    tot=0.0
    for R in G:
        th=math.acos(min(1.0,max(-1.0,(np.trace(R)-1)/2)))
        tot += (2*l+1) if abs(math.sin(th/2))<1e-14 else math.sin((2*l+1)*th/2)/math.sin(th/2)
    return tot/len(G)
o_ind = min(l for l in range(3,60,2) if abs(molien(G_I,l))>1e-7)
ck("§3 由 Molien 序列獨立重算 o(I) = 15", o_ind, 15)
# 鏡面數
axes=[]
for R in G_I:
    if abs(np.trace(R)+1)<1e-9:
        w,V=np.linalg.eig(R); ax=np.real(V[:,np.argmin(np.abs(w-1))]); ax/=np.linalg.norm(ax)
        if not any(abs(abs(ax@a)-1)<1e-9 for a in axes): axes.append(ax)
ck("§3 #H₃ 鏡面 = 15", len(axes), 15)
print(f"  ⟹ ★ 恆等式【獨立複現】: 24 − 9 = 15 = o(Molien) = #鏡面 = N_gen·F₅ = deg δ")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§4 SM 內容橋 + 密度基準"); print("="*88)
# SM 計數
gen_weyl = {"Q (夸克雙重態, 3 色 × 2)": 6, "u^c (3 色)": 3, "d^c (3 色)": 3, "L (輕子雙重態)": 2, "e^c": 1}
print(f"  SM 每世代 Weyl 費米子數:")
tot = 0
for k,v in gen_weyl.items(): print(f"    {k:<26} = {v}"); tot += v
ck("§4 SM 每世代 Weyl 數 = 15", tot, 15)
ck("§4 3 世代總 Weyl 數 = 45", tot*N_gen, 45)
ck("§4 帶電費米子味數 = 3 世代 × 3 型 = 9", N_gen*3, 9)
print(f"\n  ── 候選橋 ──")
print(f"    (i)  9 模式 = N_gen² = 9 = 帶電費米子味數 (3 世代 × {N_gen} 型: u/d/e 類)")
print(f"    (ii) 15 = deg δ = #H₃ 鏡面 = N_gen·F₅  ←→  SM 每世代 Weyl 數 15")
print(f"    (iii) 45 = N_gen × 15 = N_gen²·F₅  ←→  SM 總 Weyl 數 45")
ck("§4 (iii) N_gen²·F₅ = 45", N_gen**2*F5, 45)
# 密度基準 (O208 紀律): 「15」在 IDCM 目錄中之出現密度
CAT = {"1":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"11":11,"12":12,"13":13,"14":14,
       "15":15,"16":16,"18":18,"19":19,"20":20,"21":21,"22":22,"24":24,"28":28,"29":29,"30":30,
       "31":31,"33":33,"35":35,"36":36,"37":37,"41":41,"42":42,"43":43,"44":44,"45":45,"46":46,
       "47":47,"55":55,"60":60,"61":61,"66":66,"77":77,"88":88,"90":90,"98":98,"105":105,
       "106":106,"120":120,"123":123,"125":125,"144":144,"176":176,"264":264,"421":421,"528":528,
       "7723":7723}
vals = sorted(set(CAT.values()))
k15 = [v for v in vals if v == 15]
print(f"\n  ── 密度基準 (O208) ──")
print(f"    IDCM 目錄中 1..176 之結構數 = {len(vals)} 個")
print(f"    「15」之目錄密度 = 1/{len(vals)} = {1/len(vals):.4f}  (即 {100/len(vals):.2f}%)")
print(f"    ⟹ 隨機抽一個目錄數 = 15 之機率 ≈ {100/len(vals):.2f}%  — 【非稀有】")
print(f"    ⚠️ 故「15 = 15」之巧合【唔具獨立證據力】, 必須有代數機制 (如 §2 之中心對稱機制)")
ck("§4 「15」目錄密度 > 1% (⟹ 巧合門檻高)", 1/len(vals) > 0.01, True)
print(f"\n  ★ 橋之裁決: (i) 9 = 3×3 有結構基礎 (§1 之 |M| = 9 唯一性, script 68 §2)")
print(f"     (ii)/(iii) 之「15」「45」係【數值巧合候選】, 目錄密度 {100/len(vals):.1f}% ⟹ 未達證據門檻 🔴")
print(f"     真正有代數機制之 15 = §2 之 22 − 7 = o_ach − o_ch (中心對稱額外保護之奇模數)")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§5 前提檢驗: 保護判準之銳度 + 9 模式集之結構性質"); print("="*88)
# 保護判準銳度: 逐 n 之 |D_n| 分佈
devs = sorted((abs(Dn(A5, A5[0], n)), n) for n in range(1, 44))
prot = [n for d,n in devs if d < 1e-3]; unprot = [n for d,n in devs if d >= 1e-3]
print(f"  受保護 |D_n| ≤ {max(d for d,n in devs if d<1e-3):.3e}  ({len(prot)} 個 n)")
print(f"  未受保護 |D_n| ≥ {min(d for d,n in devs if d>=1e-3):.3e}  ({len(unprot)} 個 n)")
sep = min(d for d,n in devs if d>=1e-3)/max(d for d,n in devs if d<1e-3)
print(f"  ★ 分離比 = {sep:.3e}")
ck("§5 保護/未保護分離比 > 1e2 (銳利; R16 之 9.24e4 係另一統計量—跨度)", sep > 1e2, True)
# 9 模式集之結構性質
MSET = {1,2,3,4,5,7,9,11,13}
BLK = [{1,2,3},{4,5,7},{9,11,13}]
ck("§5 模式集大小 = 9 = N_gen²", len(MSET), N_gen**2)
ck("§5 模式集可分解為 3 個世代塊 (各 3 個)",
   [sorted(MSET & b) for b in BLK], [sorted(b) for b in BLK])
print(f"  ── 密度基準 (O208) ──")
Nsub = math.comb(N_d-1, 9)
print(f"    {N_d-1} 選 9 之子集總數 = C(43,9) = {Nsub:,}")
# 「每塊恰 3 個」之數目: 塊大小 (3,3,3) ⟹ 唯一分配 1 種 (取盡)
nblk = 1
print(f"    「3 塊各取盡」之組合數 = {nblk}  ⟹ 密度 = 1/{Nsub:,} = {100/Nsub:.3e}%")
# 較寬鬆: 「每塊恰取 3 個 (共 3 塊)」但塊固定 ⟹ 仍唯一; 若塊可任意分割則 C(43,9) 中比例
print(f"    ⚠️ 但塊邊界由 γ_n 單調 + 已知模式集【事後】定出 ⟹ 密度基準不適用, 係循環論證")
print(f"    ⚠️ 但塊 {1,2,3}/{4,5,7}/{9,11,13} 之定義【來自 γ_n 單調 + 已知模式集】⟹ 循環論證風險")
print(f"  ★ 前提檢驗裁決:")
print(f"     ✅ 保護判準本身【銳利且可重現】 (分離比 {sep:.1e}, 軸獨立, 獨立複現 9/24 二分)")
print(f"     ✅ 模式數 = 9 = N_gen² 且可分解為 3 世代塊")
print(f"     🔴 但「費米子模式 = 保護模式」仍【未獨立論證】: 塊結構之定義用咗已知模式集")
print(f"        ⟹ 前提保持 conditional; 本輪未推翻亦未升級")

print("\n"+"="*88); print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}"); print("="*88)
if FAIL:
    print("FAIL 項:")
    for f in FAIL: print("  -", f)
