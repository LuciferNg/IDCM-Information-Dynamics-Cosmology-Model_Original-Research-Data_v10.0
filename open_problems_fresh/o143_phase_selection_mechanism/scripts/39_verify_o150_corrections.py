#!/usr/bin/env python3
"""
O143 #39 — 獨立重算驗證 O150 嘅 6 條修正 (2026-09-21)
=====================================================
規矩: 不信任其他 session 嘅 self-report → 由第一性原理重算。
A. a5_nodes = 冷斑方向喺手性二十面體群 I (order 60) 下嘅軌道?
B. 任何 I-軌道自動係 5-design?
C. 120 個 graph automorphism 中只有 60 個係幾何等距?
D. ℓ=3 佔比: Σcoef² (44.3%, 基依賴) vs ‖Π₃Tz‖²/‖Tz‖² (basis-free)
E. GRF null (物理正確) vs 置換 null → ℓ=3 p 值
F. node9 z-score / rank; |T₉/T₂₀| 病態性
G. 全天空 ℓ=3 軸 vs 節點集 ℓ=3 軸
"""
import numpy as np, math, json, os
import healpy as hp
import networkx as nx
from scipy.special import lpmv
from astropy.coordinates import SkyCoord, Galactic
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
D = f'{ROOT}/cmb_cold_spot/data'
G = f'{ROOT}/o182_88grid_geometry/data'
CACHE = f'{ROOT}/o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits'
R = []
def chk(tag, name, got, want, tol=1e-9):
    try:
        ok = abs(float(got)-float(want)) <= tol if isinstance(want,(int,float)) else (got==want)
    except Exception:
        ok = False
    R.append((tag, name, got, want, ok)); return ok

phi = (1+5**0.5)/2; inv_phi = phi-1
def norm(v): return v/np.linalg.norm(v)
def rot_matrix(axis, ang):
    a = np.asarray(axis,float); a = a/np.linalg.norm(a)
    c,s = math.cos(ang), math.sin(ang)
    K = np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3) + s*K + (1-c)*(K@K)

print("="*100); print("  O143 #39 — 獨立重算驗證 O150 修正"); print("="*100)

# ═══ A. 軌道重建 ═══
print("\n[A] a5_nodes = 冷斑方向 I-軌道? (由 cmb_cold_spot/scripts/09 L45-106 重建)")
cs = SkyCoord(l=209*u.deg, b=-57*u.deg, frame=Galactic).icrs
ra, dec = math.radians(cs.ra.deg), math.radians(cs.dec.deg)
v_cs = np.array([math.cos(dec)*math.cos(ra), math.cos(dec)*math.sin(ra), math.sin(dec)])
verts = []
for sx in (-1,1):
    for sy in (-1,1):
        for sz in (-1,1): verts.append((sx,sy,sz))
for sx in (-1,1):
    for sy in (-1,1):
        verts.append((0, sx*inv_phi, sy*phi)); verts.append((sx*inv_phi, sy*phi, 0)); verts.append((sx*phi, 0, sy*inv_phi))
Vn = np.array([norm(v) for v in verts])
faces = []
for sx in (-1,1):
    for sy in (-1,1):
        faces.append((0, sx, sy*phi)); faces.append((sx, sy*phi, 0)); faces.append((sx*phi, 0, sy))
Fn = np.array([norm(v) for v in faces])
g1 = rot_matrix(Fn[0], 2*math.pi/5); g2 = rot_matrix(Vn[0], 2*math.pi/3)
group = [np.eye(3)]; seen = {tuple(np.round(np.eye(3).flatten(),10))}; q = [np.eye(3)]
while q:
    M = q.pop(0)
    for g in (g1,g2):
        nw = g@M; k = tuple(np.round(nw.flatten(),10))
        if k not in seen: seen.add(k); group.append(nw); q.append(nw)
print(f"    群階 |I| = {len(group)}")
chk('A', '群階 = 60', len(group), 60)
orbit = []
for M in group:
    v = M@v_cs
    if not any(np.allclose(v,o,atol=1e-6) or np.allclose(v,-o,atol=1e-6) for o in orbit): orbit.append(v)
orbit = np.array(orbit)
print(f"    軌道大小 = {len(orbit)}")
chk('A', '軌道大小 = 60', len(orbit), 60)
a5raw = np.loadtxt(f'{D}/a5_nodes.txt')
A5_icrs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                     math.cos(math.radians(d))*math.sin(math.radians(r)), math.sin(math.radians(d))]
                    for r,d in a5raw])
# 逐點最近匹配
dmin = []
for v in A5_icrs:
    dmin.append(max(abs(np.dot(v, o)) for o in orbit))
ang = [math.degrees(math.acos(np.clip(x,-1,1))) for x in dmin]
print(f"    逐點最大匹配角 = {max(ang):.6f}°  (檔案 4 位小數捨入 ⟹ ~0.00005°)")
chk('A', '最大匹配角 < 0.001°', max(ang), 0.000054, 5e-5)
# 邊長兩類?
def dmat(V):
    n=len(V); M=np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            if i!=j: M[i,j]=math.degrees(math.acos(np.clip(np.dot(V[i],V[j]),-1,1)))
    return M
DA5 = dmat(A5_icrs); Do = dmat(orbit)
iu = np.triu_indices(60,1)
# ⚠️ 修正 (09-21): 原用 np.sort(...,axis=1)[:,0] = 對角線 (dmat 對角=0) → 得 0.0。正解: 排除自身, 取邊 (<28°)
ed = DA5[iu]; ed = ed[ed < 28.0]
cls = np.unique(np.round(ed,3))
eo = Do[iu]; eo = eo[eo < 28.0]
print(f"    a5 邊 ({len(ed)} 條) 長度類別: {list(cls)}  計數 {[int((np.round(ed,3)==c).sum()) for c in cls]}")
o_cls = np.unique(np.round(eo,3))
print(f"    orbit 邊 ({len(eo)} 條) 長度類別: {list(o_cls)}  mean {eo.mean():.4f}  散佈 {eo.max()-eo.min():.4f}")
print("    ⟹ 軌道重現 a5_nodes 嘅兩類邊長 (26.0914/26.1664) ⟹ a5_nodes = I·v_cs 直接確認")
print("       精確 rhombicosidodecahedron 係另一構型 (全等長 25.8786, 見 docs/10 §1)")
chk('A', 'a5 邊長類 1 = 26.0914', float(cls[0]), 26.0914, 0.01)
chk('A', 'a5 邊長類 2 = 26.1664', float(cls[-1]), 26.1664, 0.01)
# ⚠️ 修正 (09-21 二輪): 原本誤設 orbit = rhombicosidodecahedron (全等長 25.8786) —
#    orbit = I·v_cs 係「另一構型」, 正確斷言 = 與 a5_nodes 兩類邊長同值
chk('A', 'orbit 邊長類 = a5 (min/max 同值)', max(abs(float(o_cls[0]-cls[0])), abs(float(o_cls[-1]-cls[-1]))), 0.0, 0.01)
chk('A', 'orbit 非全等長 (≠ rhombicosidodecahedron)', float(o_cls[-1]-o_cls[0]) > 0.05, True)

# ═══ B. 5-design 自動性 ═══
print("\n[B] 任何 I-軌道自動係 5-design? (隨機種子)")
def sym_tensor(Vv,p):
    T = np.zeros((3,)*p)
    for v in Vv:
        for idx in np.ndindex((3,)*p):
            pr=1.0
            for dd in idx: pr*=v[dd]
            T[idx]+=pr
    return T/len(Vv)
def iso_tensor(p):
    if p%2==1: return np.zeros((3,)*p)
    def prs(it):
        if not it: yield []; return
        f=it[0]
        for i in range(1,len(it)):
            for pp in prs(it[1:i]+it[i+1:]): yield [(f,it[i])]+pp
    def df(m):
        r=1
        while m>0: r*=m; m-=2
        return r
    T=np.zeros((3,)*p)
    for pr in prs(list(range(p))):
        arr=np.ones((3,)*p)
        for (a,b) in pr:
            sh=[1]*p; sh[a]=3; sh[b]=3
            arr=arr*np.eye(3).reshape(sh)
        T+=arr
    return T/df(p+1)
rng = np.random.default_rng(2026)
devs = {t: [] for t in range(1,7)}
for trial in range(5):
    v0 = norm(rng.normal(size=3))
    orb = []
    for M in group:
        v = M@v0
        if not any(np.allclose(v,o,atol=1e-8) or np.allclose(v,-o,atol=1e-8) for o in orb): orb.append(v)
    orb = np.array(orb)
    if len(orb) != 60: continue
    for t in range(1,7):
        devs[t].append(float(np.abs(sym_tensor(orb,t)-iso_tensor(t)).max()))
for t in range(1,7):
    print(f"    t={t}: 隨機 I-軌道偏差 max = {max(devs[t]):.3e}")
chk('B', 't=1..5 全部 ≤ 1e-12', all(max(devs[t])<=1e-12 for t in range(1,6)), True)
chk('B', 't=6 失敗 (> 1e-6)', max(devs[6])>1e-6, True)
print(f"    ⟹ 5-design 係群軌道自動性質 (唔係 O143 特殊發現)")

# ═══ C. 自同構: 真等距 vs 非真 ═══
print("\n[C] 120 個 graph automorphism 中, 幾多個係幾何等距?")
LB = np.column_stack([SkyCoord(ra=a5raw[:,0]*u.deg, dec=a5raw[:,1]*u.deg, frame='icrs').galactic.l.deg,
                      SkyCoord(ra=a5raw[:,0]*u.deg, dec=a5raw[:,1]*u.deg, frame='icrs').galactic.b.deg])
Vg = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))] for l,b in LB])
A = np.zeros((60,60), bool)
for i in range(60):
    for j in range(i+1,60):
        if math.degrees(math.acos(np.clip(np.dot(Vg[i],Vg[j]),-1,1))) < 28.0: A[i,j]=A[j,i]=True
edges = [(i,j) for i in range(60) for j in range(i+1,60) if A[i,j]]
Gg = nx.Graph(); Gg.add_nodes_from(range(60)); Gg.add_edges_from(edges)
autos = list(nx.algorithms.isomorphism.GraphMatcher(Gg,Gg).isomorphisms_iter())
print(f"    |Aut(G)| = {len(autos)}")
chk('C', '|Aut(G)| = 120', len(autos), 120)
proper = 0; res = []
for m in autos:
    P = Vg[[m[i] for i in range(60)]]           # 目標
    Q = Vg.copy()                                # 源
    H = Q.T @ P
    U_,S_,Vt = np.linalg.svd(H)
    D = np.eye(3); D[2,2] = np.sign(np.linalg.det(U_@Vt))
    Rot = U_@D@Vt
    r = float(np.abs(Q@Rot - P).max())
    res.append(r)
    if r < 1e-5: proper += 1   # ⚠️ 修正 (09-21): 原 1e-6 太嚴 (a5_nodes 4 位小數 ⟹ ~1.7e-6 rad 座標誤差) → 只算得 4
res = np.array(res)
print(f"    幾何等距 (Procrustes 殘餘 < 1e-5) = {proper}")
print(f"    其餘 {len(autos)-proper} 個: 殘餘 min {res[res>1e-5].min():.4f} / 中位 {np.median(res[res>1e-5]):.4f} / max {res[res>1e-5].max():.4f}")
chk('C', '真等距數 = 60', proper, 60)
chk('C', '非等距自動同構數 = 60', len(autos)-proper, 60)
print("    ⚠️ O150 報『非真元素 Gram 殘餘 = 0.177』— 本 O Procrustes 度量得 1.31–1.85,")
print("       另算 Gram-relF = 0.132 / distmat-relF = 0.054 — metric 差異; 定性結論 (60/60) 一致")
# det 分佈
dets = []
for m in autos:
    Q = Vg.copy(); P = Vg[[m[i] for i in range(60)]]
    H = Q.T@P; U_,S_,Vt = np.linalg.svd(H); dets.append(np.sign(np.linalg.det(U_@Vt)))
print(f"    det 分佈: +1 = {dets.count(1.0)}, -1 = {dets.count(-1.0)}")
# 真等距是否構成閉合群? (只取殘餘 < 1e-5 者)
grp = []
for m in autos:
    Q = Vg.copy(); P = Vg[[m[i] for i in range(60)]]
    H = Q.T@P; U_,S_,Vt = np.linalg.svd(H)
    D = np.eye(3); D[2,2] = np.sign(np.linalg.det(U_@Vt)); Rr = U_@D@Vt
    if float(np.abs(Q@Rr - P).max()) < 1e-5: grp.append(Rr)
clos = max(float(np.abs(Rr@R2 - min(grp, key=lambda X: np.abs(X-Rr@R2).max())).max()) for Rr in grp for R2 in grp)
detg = set(int(round(np.linalg.det(Rr))) for Rr in grp)
print(f"    真等距旋轉集: {len(grp)} 個, det 集 = {detg}, 乘法閉合殘餘 = {clos:.2e}")
chk('C', '真等距構成閉合群 (order 60)', len(grp), 60)
chk('C', '乘法閉合 (殘餘 < 1e-5)', clos, 0.0, 1e-5)

# ═══ D. basis-free 佔比 ═══
print("\n[D] ℓ=3 佔比: Σcoef² (基依賴) vs ‖Π₃Tz‖² (basis-free)")
T = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
Tz = T - T.mean()
def real_sph(l,m,v):
    th = np.arccos(np.clip(v[:,2],-1,1)); ph = np.arctan2(v[:,1],v[:,0]); am=abs(m)
    nrm = math.sqrt((2*l+1)/(4*math.pi)*math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am,l,np.cos(th))
    if m==0: return nrm*P
    if m>0: return math.sqrt(2)*nrm*P*np.cos(am*ph)
    return math.sqrt(2)*nrm*P*np.sin(am*ph)
B = {l: np.column_stack([real_sph(l,m,Vg) for m in range(-l,l+1)]) for l in range(7)}
normTz2 = float((Tz**2).sum())
print(f"    ‖Tz‖² = {normTz2:.1f} μK²")
proj2 = {}
for l in range(1,7):
    Bl = B[l]; c, *_ = np.linalg.lstsq(Bl, Tz, rcond=None)
    proj2[l] = float(((Bl@c)**2).sum())
    print(f"    ℓ={l}: ‖ΠTz‖² = {proj2[l]:8.1f} ({100*proj2[l]/normTz2:5.1f}%)   Σcoef² = {float((c**2).sum()):8.1f}")
frac3 = 100*proj2[3]/normTz2
chk('D', 'basis-free ℓ=3 佔比 = 31.8%', frac3, 31.8, 0.15)
G3 = (4*np.pi/60)*(B[3].T@B[3])
chk('D', '‖(4π/60)G₃ − I‖_max = 0.0949', float(np.max(np.abs(G3-np.eye(7)))), 0.0949, 5e-4)

# ═══ E. GRF null ═══
print("\n[E] GRF null (物理正確) vs 置換 null")
if os.path.exists(CACHE):
    m = hp.read_map(CACHE, field=0).astype(np.float64)
    lmax = 96
    cl = hp.anafast(m, lmax=lmax)
    # 驗證 cache 同 temps2 一致
    th = np.radians(90.0-LB[:,1]); ph = np.radians(LB[:,0])
    Tc = hp.get_interp_val(m, th, ph)*1e6
    cc = float(np.corrcoef(Tc, T)[0,1])
    print(f"    cache 驗證: corr(自算, temps2) = {cc:.6f}")
    # 節點方向 (ICRS for synalm 用銀河 theta/phi 一致)
    def l3frac(y):
        c, *_ = np.linalg.lstsq(B[3], y-y.mean(), rcond=None)
        return 100*float(((B[3]@c)**2).sum())/float(((y-y.mean())**2).sum())
    obs = l3frac(T)
    # 置換 null
    rng2 = np.random.default_rng(7)
    perm = np.array([l3frac(rng2.permutation(T)) for _ in range(4000)])
    # GRF null
    np.random.seed(15041)
    grf = []
    for i in range(2000):
        alm = hp.synalm(cl, lmax=lmax, new=True)
        f = hp.alm2map(alm, 2048, verbose=False)
        y = hp.get_interp_val(f, th, ph)*1e6
        grf.append(l3frac(y))
    grf = np.array(grf); perm = np.array(perm)
    print(f"    觀測 ℓ=3 佔比 = {obs:.4f}")
    print(f"    置換 null: {perm.mean():.4f} ± {perm.std():.4f} → p = {(1+(perm>=obs).sum())/(1+len(perm)):.4f}")
    print(f"    GRF   null: {grf.mean():.4f} ± {grf.std():.4f} → p = {(1+(grf>=obs).sum())/(1+len(grf)):.4f}")
    chk('E', 'GRF null p ≈ 0.078', float((1+(grf>=obs).sum())/(1+len(grf))), 0.078, 0.04)
    chk('E', '置換 null p ≈ 0.0045', float((1+(perm>=obs).sum())/(1+len(perm))), 0.0045, 0.006)
    grf_frac = grf
else:
    print("    ⚠️ cache 唔存在"); grf_frac = None

# ═══ F. node9 統計 ═══
print("\n[F] node9 z-score / rank; |T₉/T₂₀| 病態性")
z = (T - T.mean())/T.std(ddof=1)
print(f"    z(node9) = {z[9]:.4f}, rank = {int((z<z[9]).sum())+1}/60")
# ⚠️ 修正 (09-21): z 值依 σ 約定 — ddof=1 → −2.289 / ddof=0 → −2.309 / map σ_all → −2.389 / map σ_masked → −2.579
# O150 報 −2.414 落喺此範圍內 → 檢定改為「約定範圍」而非精確值
chk('F', 'z(node9) ∈ [−2.6, −2.2]', abs(float(z[9])+2.4) < 0.2, True)
chk('F', 'rank(node9) ≤ 5/60', int((z<z[9]).sum())+1 <= 5, True)
print(f"    z(node20) = {z[20]:.4f}, rank = {int((z<z[20]).sum())+1}/60")
chk('F', 'z(node20) = +0.800', float(z[20]), 0.800, 0.01)
print(f"    |T₉/T₂₀| = {abs(T[9]/T[20]):.4f}")
if grf_frac is not None:
    np.random.seed(15042)
    rat = []
    for i in range(2000):
        alm = hp.synalm(cl, lmax=lmax, new=True)
        f = hp.alm2map(alm, 2048, verbose=False)
        y = hp.get_interp_val(f, th, ph)*1e6
        rat.append(abs(y[9]/y[20]) if abs(y[20])>1e-9 else np.nan)
    rat = np.array([x for x in rat if np.isfinite(x)])
    pv = float((1+(rat>=abs(T[9]/T[20])).sum())/(1+len(rat)))
    print(f"    GRF |T₉/T₂₀| null: 中位 {np.median(rat):.3f}; 觀測 3.016 → p = {pv:.4f}")
    chk('F', 'GRF |T9/T20| p ≈ 0.20', pv, 0.203, 0.06)

# ═══ G. 全天空 ℓ=3 軸 ═══
print("\n[G] 全天空 ℓ=3 軸 vs 節點集 ℓ=3 軸")
if os.path.exists(CACHE):
    alm = hp.map2alm(m, lmax=3)
    # ⚠️ 修正 (09-21): 原用 alm3[:4]=0; alm3[4:16]=0 清 ℓ≤2 — lmax=3 時 alm 只有 10 個元素 → 全被清零
    # 正解: 用 hp.Alm.getidx 保留 ℓ=3 (m=0..3)
    alm3 = np.zeros_like(alm)
    for mm in range(4):
        idx3 = hp.Alm.getidx(3, 3, mm); alm3[idx3] = alm[idx3]
    vals = hp.alm2map(alm3, 2048, verbose=False)
    # ℓ=3 分量 = Σ_m a₃m Y₃m(n̂) (加法定理: ∫T₃·P₃(n̂·â)dΩ = (4π/7)·T₃(â)) → 軸 = |分量| 極值方向
    i = int(np.argmax(np.abs(vals)))
    th_i, ph_i = hp.pix2ang(2048, i)
    l_sky = math.degrees(ph_i) % 360; b_sky = math.degrees(np.pi/2 - th_i)
    print(f"    全天空 ℓ=3 軸 = ({l_sky:.1f}°, {b_sky:+.1f}°)")
    chk('G', '全天空 ℓ=3 軸 l ≈ 82.4', l_sky, 82.4, 3.0)
    chk('G', '全天空 ℓ=3 軸 b ≈ +17.2', b_sky, 17.2, 3.0)
    axj = json.load(open(f'{O143}/data/step30_axis_corrected.json'))['axis']
    l0,b0 = axj
    v1 = np.array([math.cos(math.radians(b0))*math.cos(math.radians(l0)),
                   math.cos(math.radians(b0))*math.sin(math.radians(l0)), math.sin(math.radians(b0))])
    v2 = np.array([math.cos(math.radians(b_sky))*math.cos(math.radians(l_sky)),
                   math.cos(math.radians(b_sky))*math.sin(math.radians(l_sky)), math.sin(math.radians(b_sky))])
    angs = math.degrees(math.acos(np.clip(np.dot(v1,v2),-1,1)))
    # ⚠️ 修正 (09-21 二輪): ℓ=3 圖樣 ∝ cos3Θ 對 ±â 等價 (T₃(−â) = −T₃(â)) ⟹ 用軸向角
    ang_ax = min(angs, 180.0-angs)
    print(f"    節點集軸 ({l0:.2f}°, {b0:.2f}°) vs 全天空軸 ({l_sky:.2f}°, {b_sky:+.2f}°) → 夾角 {angs:.1f}° (軸向 {ang_ax:.1f}°)")
    chk('G', '軸向夾角 ≈ 63°', ang_ax, 63.0, 8.0)

npass = sum(1 for r in R if r[4]); nfail = len(R)-npass
print("\n" + "="*100)
print(f"{'':4}{'檢查項':<46}{'實測':>16}{'期望':>14}  結果")
print("-"*100)
for tag,name,got,want,ok in R:
    g = f"{got:.6g}" if isinstance(got,float) else str(got)
    w = f"{want:.6g}" if isinstance(want,float) else str(want)
    print(f"[{tag}] {name:<46}{g:>16}{w:>14}  {'PASS' if ok else 'FAIL'}")
print("-"*100)
print(f"\n總計: {npass}/{len(R)} PASS, {nfail} FAIL")
if nfail:
    print("FAIL:"); [print(f"  [{t}] {n}: got={g} want={w}") for t,n,g,w,ok in R if not ok]
with open(f'{O143}/data/step36_o150_correction_verify.json','w') as f:
    json.dump({'n_pass':npass,'n_total':len(R),
               'checks':[{'tag':t,'name':n,'got':(float(g) if isinstance(g,float) else str(g)),
                          'want':(float(w) if isinstance(w,float) else str(w)),'ok':bool(ok)} for t,n,g,w,ok in R]},
              f, indent=2, ensure_ascii=False)
print(f"\n✅ 已存: data/step36_o150_correction_verify.json")
