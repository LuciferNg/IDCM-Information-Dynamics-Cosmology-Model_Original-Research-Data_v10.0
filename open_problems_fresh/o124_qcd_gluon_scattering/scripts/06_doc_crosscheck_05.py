#!/usr/bin/env python3
"""
O124 — Script 06: docs/05 文檔核對 (由零重算, 唔 import scripts/01–05)
======================================================================
獨立重算 docs/05_gluon_vertices.md 每個數值 claim。全部由 0,1 → φ → 結構數。
"""
import itertools
import ast
import numpy as np

PASS = FAIL = TOTAL = 0
def chk(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    ok = bool(cond)
    if ok: PASS += 1
    else:  FAIL += 1
    print(f"  {'✅' if ok else '❌'} {name} {detail}")

N = 88
PHI = (1 + 5**0.5)/2
print("=" * 78)
print("  O124 Script 06: docs/05 文檔核對 (零重算)")
print("=" * 78)

# ── [1] §B 譜 ───────────────────────────────────────────────────────
print("\n─── [1] docs/05 §2 二次項譜 ───")
lam = np.array([4*np.sin(np.pi*n/N)**2 for n in range(N)])
lam_alt = np.array([abs(np.exp(2j*np.pi*n/N) - 1)**2 for n in range(N)])
chk("B1 λ_n = 4sin²(πn/88) = |e^{2πin/88}−1|²", np.max(np.abs(lam - lam_alt)) < 1e-12)
chk("B2 λ₀ = 0", abs(lam[0]) < 1e-14, f"(λ₀ = {lam[0]:.1e})")
chk("B3 Σλ(0..87) = 176 = 4N_d", abs(lam.sum() - 176) < 1e-9, f"({lam.sum():.4f})")
chk("B3 Σλ(1..44) = 90 = Σγ", abs(lam[1:45].sum() - 90) < 1e-9, f"({lam[1:45].sum():.4f})")

# ── [2] §A BCH ──────────────────────────────────────────────────────
print("\n─── [2] docs/05 §1 BCH 展開 ───")
_l = [np.array([[0,1,0],[1,0,0],[0,0,0]], dtype=complex),
      np.array([[0,-1j,0],[1j,0,0],[0,0,0]], dtype=complex),
      np.array([[1,0,0],[0,-1,0],[0,0,0]], dtype=complex),
      np.array([[0,0,1],[0,0,0],[1,0,0]], dtype=complex),
      np.array([[0,0,-1j],[0,0,0],[1j,0,0]], dtype=complex),
      np.array([[0,0,0],[0,0,1],[0,1,0]], dtype=complex),
      np.array([[0,0,0],[0,0,-1j],[0,1j,0]], dtype=complex),
      np.array([[1,0,0],[0,1,0],[0,0,-2]], dtype=complex)/np.sqrt(3)]
T = [x/2 for x in _l]
def mat(x): return sum(x[i]*T[i] for i in range(8))
rng = np.random.default_rng(20260926)
u_r = mat(rng.standard_normal(8)); v_r = mat(rng.standard_normal(8))
D = u_r - v_r; C = u_r@v_r - v_r@u_r
TrD2 = np.trace(D@D).real; TrD4 = np.trace(D@D@D@D).real; TrC2 = np.trace(C@C).real
def ReTr(g, u, v):
    from scipy.linalg import expm
    return np.trace(expm(1j*g*u) @ expm(-1j*g*v)).real
tgt = -(1/24)*(TrD4 - TrC2)
qs = [((3 - ReTr(g, u_r, v_r))/g**2 - 0.5*TrD2)/g**2 for g in (0.1, 0.05, 0.025)]
qex = qs[2] + (qs[2]-qs[1])/3
chk("A1 Richardson → −(1/24)[Tr D⁴ − Tr C²]",
    abs(qex - tgt) < 1e-6*abs(tgt), f"(Richardson {qex:.9f} vs {tgt:.9f})")
chk("A2 殘餘 ∝ g² (比值 → 4)", abs((qs[0]-tgt)/(qs[1]-tgt) - 4) < 0.05,
    f"(比值 {(qs[0]-tgt)/(qs[1]-tgt):.3f})")
chk("A3 三次項奇部 = 0",
    max(abs((ReTr(g, u_r, v_r) - ReTr(-g, u_r, v_r))/(2*g**3)) for g in (0.1, 0.05, 0.025)) < 1e-12)
chk("A4 |Tr[DC]| < 1e−12", abs(np.trace(D@C)) < 1e-12, f"({abs(np.trace(D@C)):.1e})")
X = mat(rng.standard_normal(8))
chk("A5 Tr[θ[θ,X]] = 0", abs(np.trace(u_r @ (u_r@X - X@u_r))) < 1e-12)

# ── [3] §C 3g = 0 ───────────────────────────────────────────────────
print("\n─── [3] docs/05 §3 三次項 = 0 定理 ───")
ks = rng.standard_normal(3)
chk("C1 Σ(k_a−k_b) = 0 (1D 塌縮)", abs((ks[0]-ks[1])+(ks[1]-ks[2])+(ks[2]-ks[0])) < 1e-14)
A1m = rng.standard_normal((1,1)); B1m = rng.standard_normal((1,1))
chk("C2 A∧B = A⊗B − B⊗A = 0 (1×1)", np.max(np.abs(A1m@B1m - B1m@A1m)) < 1e-15)
def ReTr1(u, v):
    from scipy.linalg import expm
    return np.trace(expm(1j*u) @ expm(-1j*v)).real
h = 1e-3
v3max = 0.0
for a in range(8):
    for b in range(8):
        for c in range(8):
            tot = sum(s[0]*s[1]*s[2]*ReTr1(s[0]*h*T[a], s[1]*h*T[b]+s[2]*h*T[c])
                      for s in itertools.product([-1,1], repeat=3))
            v3max = max(v3max, abs(tot/(8*h**3)))
chk("C3 離散三次張量 V₃ = 0 (真空, 全 512 分量)", v3max < 1e-9, f"(max|V₃| = {v3max:.2e})")
f3 = np.zeros((8,8,8))
for a in range(8):
    for b in range(8):
        for c in range(8):
            f3[a,b,c] = 2*np.trace(T[c] @ (T[a]@T[b] - T[b]@T[a])).imag
chk("C4 f^{012} = 1 存在（但頂點 = 0）", abs(f3[0,1,2] - 1) < 1e-12, f"(f[0,1,2] = {f3[0,1,2]:.4f})")

# ── [4] §D 4g 色張量 ────────────────────────────────────────────────
print("\n─── [4] docs/05 §4 四次項色張量 ───")
lhs = np.trace(C@C).real
rhs = 2*np.trace(u_r@v_r@u_r@v_r).real - 2*np.trace(u_r@u_r@v_r@v_r).real
chk("D1 Tr[[u,v]²] = 2Tr[uvuv] − 2Tr[u²v²]", abs(lhs-rhs) < 1e-11, f"(lhs = {lhs:.8f})")
uc = np.array([2*np.trace(T[i]@u_r).real for i in range(8)])
vc = np.array([2*np.trace(T[i]@v_r).real for i in range(8)])
ff = -0.5*np.einsum('abc,dec,a,b,d,e->', f3, f3, uc, vc, uc, vc)
chk("D2 Tr[[u,v]²] = −½ f^{abc}f^{ade} u^a v^b u^d v^e", abs(lhs-ff) < 1e-11, f"(f·f = {ff:.8f})")
d3 = np.zeros((8,8,8))
for a in range(8):
    for b in range(8):
        for c in range(8):
            d3[a,b,c] = 2*np.trace(T[c] @ (T[a]@T[b] + T[b]@T[a])).real
e3 = 0.0
for a in range(8):
    for b in range(8):
        for c in range(8):
            for d in range(8):
                exact = np.trace(T[a]@T[b]@T[c]@T[d])
                pred = (1/(4*3))*((a==b)*(c==d)) + (1/8)*(d3[a,b,:]+1j*f3[a,b,:]) @ (d3[:,c,d]+1j*f3[:,c,d])
                e3 = max(e3, abs(exact-pred))
chk("D3 Tr[TᵃTᵇTᶜTᵈ] 分解 (4096 分量)", e3 < 1e-14, f"(max err = {e3:.2e})")
e4 = 0.0
for a in range(8):
    for b in range(8):
        for c in range(8):
            for d in range(8):
                exact = np.trace(T[a]@T[b]@T[c]@T[d]).real
                pred = (1/(4*3))*((a==b)*(c==d)) + (1/8)*d3[a,b,:]@d3[:,c,d] - (1/8)*f3[a,b,:]@f3[:,c,d]
                e4 = max(e4, abs(exact-pred))
chk("D4 實部 = δδ + d·d + f·f (4096 分量)", e4 < 1e-14, f"(max err = {e4:.2e})")

# ── [5] §E 模空間 V₄ ────────────────────────────────────────────────
print("\n─── [5] docs/05 §5 模空間 V₄ ───")
def Q4(u, v):
    DD = u - v; CC = u@v - v@u
    return np.trace(DD@DD@DD@DD).real - np.trace(CC@CC).real
def Qvec(X): return Q4(mat(X[:8]), mat(X[8:]))
E16 = np.eye(16)
def pol(Xs):
    s = 0.0
    for r in range(5):
        for S in itertools.combinations(range(4), r):
            s += (-1)**(4-r)*Qvec(sum((Xs[i] for i in S), np.zeros(16)))
    return s/24
tc = {}
def Tget(i, j, k, l):
    key = tuple(sorted((i,j,k,l)))
    if key not in tc: tc[key] = 24*pol([E16[x] for x in key])
    return tc[key]
Xu = np.concatenate([uc, vc])
rec = sum(Tget(i,j,k,l)*Xu[i]*Xu[j]*Xu[k]*Xu[l] for i in range(16) for j in range(16)
          for k in range(16) for l in range(16))/24
chk("E1 極化張量重建 Q(u,v)", abs(rec - Q4(u_r, v_r)) < 1e-9*max(1, abs(Q4(u_r,v_r))),
    f"({rec:.8f} vs {Q4(u_r,v_r):.8f})")
def V4m(ns, aas):
    inner = sum(np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/N)*Tget(*[8*d[k]+aas[k] for k in range(4)])
                for d in itertools.product([0,1], repeat=4))
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/N) for m in range(N))
    return -inner*site/(24*N*N)
ns0 = [5,7,11,65]; aa0 = [0,0,1,1]
base = V4m(ns0, aa0)
chk("E2 V₄ Bose 對稱 (24 置換全等)",
    all(abs(V4m([ns0[i] for i in p], [aa0[i] for i in p]) - base) <= 1e-9*max(1, abs(base))
        for p in itertools.permutations(range(4))), f"(V₄ = {base:.6f})")
def Q1(X): return (X[0] - X[1])**4
def pol1(Xs):
    s = 0.0
    for r in range(5):
        for S in itertools.combinations(range(4), r):
            s += (-1)**(4-r)*Q1(sum((Xs[i] for i in S), np.zeros(2)))
    return s/24
def T1(i,j,k,l):
    return 24*pol1([np.eye(2)[x] for x in tuple(sorted((i,j,k,l)))])
def V4U1(ns):
    inner = sum(np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/N)*T1(*d)
                for d in itertools.product([0,1], repeat=4))
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/N) for m in range(N))
    return -inner*site/(24*N*N)
def V4U1c(ns):
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/N) for m in range(N))
    return -site*np.prod([1 - np.exp(2j*np.pi*n/N) for n in ns])/(N*N)
chk("E3 U(1) 閉式 −(1/88)δΠ(1−e^{2πin/88})", abs(V4U1(ns0) - V4U1c(ns0)) < 1e-8,
    f"({V4U1(ns0):.6f} vs {V4U1c(ns0):.6f})")
cnt = sum(1 for q in itertools.product(range(6), repeat=4) if sum(q) % 6 == 0)
chk("E4 守恆四元組數 = N³ (N=6 全枚舉)", cnt == 216, f"({cnt} = 6³)")
rng2 = np.random.default_rng(7)
ok_sup = True; n_noncons = 0; n_cons_nz = 0
for _ in range(2000):
    ns = list(rng2.integers(0,88,4)); aa = list(rng2.integers(0,8,4))
    v = V4m(ns, aa)
    if int(sum(ns)) % 88 == 0: n_cons_nz += (abs(v) > 1e-9)
    else:
        n_noncons += 1
        if abs(v) > 1e-9: ok_sup = False
for _ in range(2000):
    a1,a2,a3 = (int(x) for x in rng2.integers(0,88,3))
    if abs(V4m([a1,a2,a3,(-(a1+a2+a3)) % 88], list(rng2.integers(0,8,4)))) > 1e-9: n_cons_nz += 1
chk("E5 支撐 ⊆ 守恆集 + 守恆集非空", ok_sup and n_noncons > 1900 and n_cons_nz > 100,
    f"(非守恆 {n_noncons}/2000 全零; 守恆非零 {n_cons_nz})")

# ── [6] §F h-θ-θ ────────────────────────────────────────────────────
print("\n─── [6] docs/05 §6 三點頂點 ───")
mu2 = 2.0; lam_c = 2.0/123
W2 = mu2/(2*lam_c)
chk("F1 h-θ-θ 係數 = ⟨W⟩/2 = √61.5/2", abs(np.sqrt(W2)/2 - 3.921097) < 1e-5, f"({np.sqrt(W2)/2:.6f})")
chk("F3 4θ 係數 = −⟨W⟩²/24 = −2.5625", abs(-W2/24 + 2.5625) < 1e-9, f"({-W2/24:.6f})")
Gss = np.einsum('abcd,abcd->', np.einsum('abe,cde->abcd', f3, f3), np.einsum('abe,cde->abcd', f3, f3))
chk("F4 G_ss = C_A²(N_c²−1) = 72", abs(Gss - 72) < 1e-9, f"(G_ss = {Gss:.4f})")

# ── [7] §G + 誠實表 ─────────────────────────────────────────────────
print("\n─── [7] docs/05 §7/§8 修正 + 誠實表 ───")
src = open("scripts/02_discrete_qcd.py", encoding="utf-8").read()
tree = ast.parse(src)
vac = []
for node in ast.walk(tree):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "check"
            and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and node.args[1].value is True):
        vac.append(node.args[0].value if isinstance(node.args[0], ast.Constant) else "?")
c_has = all(any(t in v for v in vac) for t in ("C6","C7","C8"))
chk("G1 scripts/02 空洞檢查含 C6/C7/C8", len(vac) >= 6 and c_has, f"({len(vac)} 個)")
doc = open("docs/05_gluon_vertices.md", encoding="utf-8").read()
tbl = doc.split("## 8. 誠實標記總表")[1].split("## 9.")[0]
rows = [l for l in tbl.splitlines() if l.startswith("|") and "🟢" in l or l.startswith("|") and "🟡" in l
        or l.startswith("|") and "🔴" in l]
chk("誠實表 10 行", len(rows) == 10, f"({len(rows)} 行)")
chk("誠實表 🟢 = 7", sum(1 for r in rows if "🟢" in r) == 7, f"({sum(1 for r in rows if '🟢' in r)})")
chk("誠實表 🟡 = 1", sum(1 for r in rows if "🟡" in r) == 1)
chk("誠實表 🔴 = 2", sum(1 for r in rows if "🔴" in r) == 2)
idx = doc.split("## 9. 推導時序索引（本檔）")[1]
chk("時序索引 T0–T7 (8 項)", all(f"**T{i}**" in idx for i in range(8)))
chk("docs/05 無壓縮標記", "HERMES-CONTEXT-COMPRESSION" not in doc and "omitted here" not in doc)

print("\n" + "=" * 78)
print(f"  結果: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"  結論: {'✅ docs/05 全部數值 claim 核對通過' if FAIL == 0 else '❌ 有核對失敗'}")
print("=" * 78)
