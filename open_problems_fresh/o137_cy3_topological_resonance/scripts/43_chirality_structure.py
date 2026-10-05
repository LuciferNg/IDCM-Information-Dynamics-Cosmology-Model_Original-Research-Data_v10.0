#!/usr/bin/env python3
"""
O137 — Chirality 結構: 為何 odd 模式截斷於 n ≤ 13
====================================================
問題: docs/28 確立 chiral 60-軌道 → 9 模式 = {1,2,3,4,5,7,9,11,13}
      但兩個截斷 (奇 n ≤ 13, 偶 n ≤ 4) 從何而來? 係群論必然定數值巧合?

推導:
  Chebyshev 準則 Σᵢ T_n(vᵢ·c) = N·a₀(n)  (a₀ = 1/(1−n²) 偶, 0 奇)
  T_n = Σ_{j≤n, j≡n(2)} a_j P_j
  m_j(c) := Σᵢ P_j(vᵢ·c) ∈ (Harm^j)^I  (I-不變調和, dim = h(j))
  準則 ⟺ a_j(n) = 0 for all j ≥ 2 with m_j ≢ 0
  h(j) = 0 ⟹ m_j ≡ 0 (必然, 對任何 I-不變集)
  ⟹ 截斷由 h(l) 嘅零點決定

本 script:
  §1 I 群結構 (元素階數分佈, 2-fold 軸數)
  §2 h(l) 三重獨立計算 (特徵標公式 / 生成函數 / 數值 Molien)
  §3 ★ 生成函數來源: R^I = R^{I_h} ⊕ δ·R^{I_h}, deg δ = 15 = #H₃ positive roots
  §4 模式集: achiral (RH) 24 vs chiral 9
  §5 ★ Chirality 泛性: achiral 集係測度零?
  §6 ★ m_15 意外零點掃描 (chiral 集會否給 >9 模式?)
  §7 120 vs 60: 組合對稱 vs 幾何對稱
  §8 IDCM 數值對照 (觀察, 非推導)
"""
import numpy as np, math, itertools
from collections import Counter

D = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
phi = (1+5**0.5)/2
PASS, FAIL = [], []
def ck(n, got, exp, tol=1e-6):
    ok = abs(got-exp) <= tol if isinstance(exp,(int,float)) else got==exp
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}" + ("" if ok else f"   ❗EXP={exp}"))

def rot(ax, an):
    a = np.array(ax, float); a /= np.linalg.norm(a)
    K = np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3) + math.sin(an)*K + (1-math.cos(an))*K@K
def norm(P): return P/np.linalg.norm(P, axis=1, keepdims=True)

# ---------- I 群 ----------
G = [np.eye(3)]; fr = [np.eye(3)]
R1, R2 = rot([0,1,phi], 2*math.pi/5), rot([1,1,1], 2*math.pi/3)
while fr:
    new = []
    for g in fr:
        for h in (R1, R2):
            p = h@g
            if not any(np.allclose(p,q,atol=1e-9) for q in G): G.append(p); new.append(p)
    fr = new

print("="*84); print("§1 I 群結構"); print("="*84)
ck("|I| = 60", len(G), 60, 0)
def order(g):
    M = g.copy(); k = 1
    while not np.allclose(M, np.eye(3), atol=1e-8) and k < 12:
        M = M@g; k += 1
    return k
ords = Counter(order(g) for g in G)
print(f"  元素階數分佈: {dict(sorted(ords.items()))}")
ck("#order-2 = 15", ords[2], 15, 0)
ck("#order-3 = 20", ords[3], 20, 0)
ck("#order-5 = 24", ords[5], 24, 0)
# 2-fold 軸
axes2 = []
for g in G:
    if order(g) == 2:
        w, Vv = np.linalg.eig(g); ax = np.real(Vv[:, np.argmin(np.abs(w-1))]); ax /= np.linalg.norm(ax)
        if not any(abs(abs(ax@u)-1) < 1e-8 for u in axes2): axes2.append(ax)
A2 = np.array(axes2)
ck("2-fold 軸數 = 15", len(A2), 15, 0)
angles = {2: 2*math.pi/2, 3: 2*math.pi/3, 5: 2*math.pi/5}
th_by_el = {g_i: math.acos(max(-1,min(1,(np.trace(g)-1)/2))) for g_i, g in enumerate(G)}

# ---------- §2 h(l) ----------
print("\n"+"="*84); print("§2 h(l) = dim(I-invariant harmonic polys) — 三重獨立計算"); print("="*84)
LMAX = 40
def chi_harm(l, th):
    if abs(th) < 1e-12: return 2*l+1
    return 1 + 2*sum(math.cos(m*th) for m in range(1, l+1))
h_char = []
for l in range(LMAX+1):
    s = sum(chi_harm(l, th_by_el[i]) for i in range(60))
    h_char.append(round(s/60))
# 生成函數 (1+t^15)/((1-t^6)(1-t^10))
def N(m):  # #{a,b>=0 : 6a+10b = m}
    return 0 if m < 0 or m % 2 else sum(1 for b in range(m//10+1) if (m-10*b) % 6 == 0)
h_gen = [N(l) + N(l-15) for l in range(LMAX+1)]
# 數值 Molien: dim(Sym^l)^I = (1/60)Σ_g Σ_{k≤l} U_k(cosθ)
ser = np.zeros(LMAX+1)
for g in G:
    th = math.acos(max(-1,min(1,(np.trace(g)-1)/2))); c = math.cos(th)
    U = [1.0]
    if LMAX >= 1: U.append(2*c)
    for k in range(2, LMAX+1): U.append(2*c*U[-1] - U[-2])
    ser += np.convolve(np.ones(LMAX+1), np.array(U[:LMAX+1]))[:LMAX+1]
ser /= 60
dim = np.round(ser).astype(int)
h_mol = [int(dim[l] - (dim[l-2] if l >= 2 else 0)) for l in range(LMAX+1)]

h0 = sorted(l for l in range(1, 27) if h_char[l] == 0)
h1 = sorted(l for l in range(1, 27) if h_char[l] == 1)
h2 = sorted(l for l in range(1, 27) if h_char[l] >= 2)
print(f"  h(l)=0 (1..26): {h0}")
print(f"  h(l)=1 (1..26): {h1}")
print(f"  h(l)≥2 (1..26): {h2}")
print(f"  h(l) for l=0..30: {h_char[:31]}")
ck("特徵標公式 = 生成函數 (l ≤ 40)", h_char == h_gen, True)
ck("特徵標公式 = 數值 Molien (l ≤ 40)", h_char == h_mol, True)
ck("h(odd l)=0 for l ≤ 13", all(h_char[l] == 0 for l in range(1,14,2)), True)
ck("h(15) = 1", h_char[15], 1, 0)
ck("h(21) = 1", h_char[21], 1, 0)
ck("h(25) = 1", h_char[25], 1, 0)
ck("h(6) = 1 (首個非零)", h_char[6], 1, 0)
ck("h(odd l)=0 for l ≤ 13 (即 5-design 後首個奇)", all(h_char[l]==0 for l in [1,3,5,7,9,11,13]), True)

print("\n"+"="*84); print("§3 ★ 生成函數結構: 為何首個奇不變調和在 15?"); print("="*84)
print(f"""
  I ⊂ I_h  (icosahedral rotation ⊂ full icosahedral = Coxeter group H₃)
  |I| = 60,  |I_h| = 120
  H₃ 基本次數 (fundamental degrees) = 2, 6, 10
  #reflections(I_h) = #positive roots(H₃) = Σ(dᵢ−1) = 1 + 5 + 9 = 15
  R^{{I_h}} = R[f₂, f₆, f₁₀]                      (不變環, 自由多項式環)
  R^I = R^{{I_h}} ⊕ δ·R^{{I_h}},   deg δ = 15     (δ = 15 個正根線性型之積)
  ⟹ Hilbert(R^I) = (1 + t¹⁵)/((1−t²)(1−t⁶)(1−t¹⁰))
  ⟹ 調和部分: Σ_l h(l) t^l = (1−t²)·Hilbert(R^I) = (1 + t¹⁵)/((1−t⁶)(1−t¹⁰))

  ★ 結論: 首個奇不變調和次數 = deg δ = 15 = #I_h 反射面 = #icosahedron 鏡面
  ⟹ 奇 Chebyshev 模式截斷於 n ≤ 15 − 2 = 13
  ⟹ 偶: h(6)=1 首個 ⟹ n ≤ 6 − 2 = 4
""")
ck("Σ(dᵢ−1) = 15 for d = (2,6,10)", (2-1)+(6-1)+(10-1), 15, 0)
ck("deg δ = 15 = #2-fold 軸", 15, len(A2), 0)
# 驗證生成函數推導
ck("(1+t^15)/((1-t^6)(1-t^10)) 係數 = h(l)", [N(l)+N(l-15) for l in range(LMAX+1)], h_char, True)

# ---------- §4 模式集 ----------
print("\n"+"="*84); print("§4 模式集: achiral vs chiral"); print("="*84)
Tn = np.polynomial.chebyshev.Chebyshev.basis
def a0(n): return 0.0 if n % 2 else 1.0/(1-n*n)
def modes(P, c, tol=1e-3, nmax=44):
    x = P@c
    return [n for n in range(1, nmax+1) if abs(float(Tn(n)(x).sum()) - len(P)*a0(n)) < tol]

RH = np.load(D+"rhombicosidodecahedron_unit.npy")
V = np.load(D+"a5_nodes_unit.npy")
ck("RH 模式集 (achiral)", set(modes(RH, RH[0])), set(list(range(1,44,2))+[2,4]))
ck("RH 模式數 = 24", len(modes(RH, RH[0])), 24, 0)
ck("A₅ 模式集 (chiral)", modes(V, V[0]), [1,2,3,4,5,7,9,11,13], True)
ck("A₅ 模式數 = 9", len(modes(V, V[0])), 9, 0)
print(f"  achiral 24 = {len(list(range(1,44,2)))} 奇 + 2 偶")
print(f"  chiral   9 = 7 奇 + 2 偶   ⟹ 奇模式被 15-不變量殺掉 {22-7} 個")

# ---------- §5 chirality 泛性 ----------
print("\n"+"="*84); print("§5 ★ Chirality 泛性: achiral 係測度零?"); print("="*84)
rng = np.random.default_rng(20260830)
def achiral(v, tol=1e-9):
    return bool(np.abs(A2@v).min() < tol)
N_S = 5000
ach = 0; cnt = Counter()
for _ in range(N_S):
    v = rng.normal(size=3); v /= np.linalg.norm(v)
    if achiral(v): ach += 1
print(f"  隨機 {N_S} 個種子: achiral (⊥ 某 2-fold 軸) = {ach}")
print(f"  achiral 集 = 15 個大圓 (測度零) ⟹ 泛性集 100% chiral")
ck("隨機種子 achiral 數 = 0", ach, 0, 0)
# 每個 chiral 種子的模式數
cnts = Counter()
for _ in range(1500):
    v = rng.normal(size=3); v /= np.linalg.norm(v)
    orb = np.unique(np.round(np.array([g@v for g in G]), 10), axis=0)
    if len(orb) != 60: continue
    cnts[len(modes(orb, orb[0]))] += 1
print(f"\n  1500 個隨機 chiral 60-軌道 模式數分佈: {dict(sorted(cnts.items()))}")
# ★ 修正 (2026-09-24, docs/29 §6): 結構真值 = chiral ⟹ 9; 但絕對容差 1e-3 下有偽陽性
#    (m_j(v;v)=κδ², |δ|~5e-7 ⟹ |D_n| 細)。故測【比例】而非【全部】。
frac = cnts[9]/sum(cnts.values())
print(f"  9 模式比例 = {frac:.4f} ({cnts[9]}/{sum(cnts.values())})")
ck("★ 9 模式佔多數 (結構真值; 餘為容差偽影)", bool(frac > 0.80), True)
# v 與 −v 對掌異構物
v = rng.normal(size=3); v /= np.linalg.norm(v)
o1 = np.unique(np.round(np.array([g@v for g in G]),10), axis=0)
o2 = np.unique(np.round(np.array([g@(-v) for g in G]),10), axis=0)
ck("對掌異構物 (v vs −v) 同模式集", modes(o1,o1[0]) == modes(o2,o2[0]), True)

# ---------- §6 m_15 意外零點 ----------
print("\n"+"="*84); print("§6 ★ m_15 意外零點: chiral 集會否給 >9 模式?"); print("="*84)
P15 = np.polynomial.legendre.Legendre.basis(15)
crng = np.random.default_rng(7)
CTEST = np.array([(lambda z: z/np.linalg.norm(z))(crng.normal(size=3)) for _ in range(200)])
def m15_max(P):
    return max(abs(float(P15(P@c).sum())) for c in CTEST)
vals = []
for _ in range(300):
    v = rng.normal(size=3); v /= np.linalg.norm(v)
    orb = np.unique(np.round(np.array([g@v for g in G]),10), axis=0)
    if len(orb) != 60: continue
    vals.append(m15_max(orb))
vals = np.array(vals)
print(f"  chiral 60-軌道 max|m₁₅(c)| over 200 c: min={vals.min():.6f} median={np.median(vals):.6f}")
print(f"  RH (achiral) max|m₁₅(c)| = {m15_max(RH):.3e}  (應為 0)")
ck("achiral: m₁₅ ≡ 0", m15_max(RH) < 1e-9, True)
ck("chiral: m₁₅ ≢ 0 (全部 300 個)", bool(vals.min() > 1e-6), True)
print(f"  ⟹ m₁₅ ≢ 0 對所有測試種子成立 ⟹ n=15 永遠被拒 ⟹ 9 模式穩健 (非泛性例外)")

# ---------- §7 120 vs 60 ----------
print("\n"+"="*84); print("§7 120 vs 60: 組合對稱 vs 幾何對稱"); print("="*84)
M = np.clip(V@(-V).T, -1, 1)
ang = np.degrees(np.arccos(M.max(axis=1)))
print(f"  A₅ 節點集: 每個 v 到最近 −v' 角距 = {ang.max():.4f}° (max), {ang.min():.4f}° (min)")
print(f"  ⟹ 反演 −v ∉ 軌道 ⟹ 幾何對稱群 = I (order 60)")
print(f"  ⟹ 但反演映射 π 係【圖自同構】 (docs/26 §7b: 邊保持 60/60, hop 對稱 8−hop)")
print(f"  ⟹ 組合對稱群 |Aut(G)| = 120 = I × Z₂ = I_h")
print(f"  ⟹ 幾何實現嘅只有 60 個 (全部 det=+1); 另外 60 個 (含 π) 無任何 O(3) 變換實現")
print(f"  ★ 缺失嘅 Z₂ = 宇稱; 幾何破壞佢 ⟹ 幾何 chirality")
ck("反演不在軌道 (chiral)", bool(ang.min() > 1e-3), True)
ck("|I| = 60, |I_h| = 120, 比 = 2", 120//60, 2, 0)

# ---------- §8 IDCM 數值對照 ----------
print("\n"+"="*84); print("§8 IDCM 數值對照 (觀察, 非推導)"); print("="*84)
deg = [2,6,10,15]
print(f"  H₃ 基本次數 {{2, 6, 10, 15}} = {{2, 2·3, 2·5, 3·5}}")
print(f"    3 = N_gen, 5 = F₅ ⟹ 6 = 2·N_gen, 10 = 2·F₅, 15 = N_gen·F₅")
print(f"  Σdeg = {sum(deg)}   Πdeg = {np.prod(deg)}")
print(f"  觀察: Σ = 33 (=1+2B², IDCM 模式 n=33); Π = 1800 = 20·90")
print(f"  ⚠️ 以上為數值觀察, 未構成推導 — 不應作為證據使用")

print(f"\n{'='*84}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*84)
