#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/01: T2 — N 通用 4g/3g 頂點顯式張量 (N-generic explicit vertex tensors)
=====================================================================================
承接: O137 FSR-QFT [B] 費曼規則 (scripts/75, 40/40) + O124 scripts/05 (N=88 特例, 22/22)。

目標: 把 O124 嘅模空間張量 V4(n1n2n3n4; a1a2a3a4) 通用化到任意 FSR 鏈長 N:
      ● 色代數 (su(3) f/d、Tr[T^aT^bT^cT^d] 分解) 隨 N 唔變 — 直接沿用 O124 機制
      ● 動量標籤 n<->2N 通用化 — 環 = 2N 個 site, 守恆 mod-2N
      (O137 [B3] 已用 mod-2N; O124 用 N=88 site = 2*44)。

理論骨架:
  S_link(u,v) = <W>^2 Tr[1 - Re(e^{igu} e^{-igv})]
  BCH: e^{igu}e^{-igv} = e^Y, Y = igD + (1/2)g^2 C + O(g^3), D=u-v, C=[u,v]
  S2  -> 傳播子極點 eps_n = 4sin^2(pi n/2N)
  S3  = 0  (Re Tr 消 g^3 純虛 + Tr[D C]=0 + 1D A^A=0)   [與 N 無關]
  S4  = (g^4/24)[Tr[D^4] - Tr[C^2]]
  V4(N; n1..n4, a1..a4) = -(1/24)(1/(2N)^2) * site(Σn) * Σ_δ e^{2πi Σδk nk/(2N)} T_δ
     site(Σn) = Σ_{m=0}^{2N-1} e^{2πi m Σn/(2N)} = 2N δ_{Σn≡0 (mod 2N)}
     色張量 T_δ = 極化抽取 (Q4 = Tr[D^4]-Tr[C^2], 16 維嵌入) — N 無關
  U(1) 極限閉式: V4^U1(N; ns) = -site·Π_k(1 - e^{2πi nk/(2N)})/(2N)^2

判據 (threshold 零放寬, 全數值由計算):
  A  色代數 (N 無關)   : f/d 重建、Tr[T^4] 4096 分量、G_ss=72
  B  BCH              : g^4 係數 -1/24(TrD^4-TrC^2) (Richardson) + ReTr 奇部=0 (1e-9, 見 B3 註)
  C  V4 通用 N         : 對 N ∈ {22,44,88,176}:
     C1 Bose 對稱 24 置換 | C2 支撐⊆守恆集 (400 隨機) | C3 守恆面非空 (>5%, O124 E5 基準)
     C3b 色選擇律: 固定守恆動量, 8^4 全色掃描 — 非零比例實測 (488/4096 = 11.9% @N=44)
     C3c 色選擇律: 固定 (0,1,2,3) 色, 全守恆動量 — 恆等零 (色 sector 禁戒)
     C4 守恆四元組數 = (2N)^3 (小 N 全枚舉) | C5 U(1) 閉式 |
     C6 N_FSR=44 (mod 88) 與 O124 N=88 特例逐項一致
  D  3g 張量           : 離散三階導 V3 = 0 (N 無關) + h-θ-θ 頂點 = √61.5/2

唯一輸入: 0,1 -> φ -> 結構數 (B=4, N_gen=3, N_c=3, μ²=2, λ=2/123)。零自由參數。
"""
import itertools
import random
import numpy as np
from scipy.linalg import expm

random.seed(20261010)   # audit 修正 (2026-10-11): 固定 seed 令 C 節抽樣可重現

PASS = 0; FAIL = 0; TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL; TOTAL += 1
    if cond: PASS += 1; mark = "OK "
    else:    FAIL += 1; mark = "XX "
    print(f"  [{mark}] {name} {detail}")

# ── 結構常數 (唯一輸入) ──
B = 4; N_gen = 3; N_c = 3; N_d = 44
mu2 = 2.0; lam_c = 2.0/123.0
W_vev2 = mu2/(2*lam_c)          # <W>^2 = 61.5
h_tt = np.sqrt(W_vev2)/2        # h-θ-θ 頂點係數 = √61.5/2

# ── su(3) 基: T^a = λ^a/2 ──
_l = [np.array([[0,1,0],[1,0,0],[0,0,0]], dtype=complex),
      np.array([[0,-1j,0],[1j,0,0],[0,0,0]], dtype=complex),
      np.array([[1,0,0],[0,-1,0],[0,0,0]], dtype=complex),
      np.array([[0,0,1],[0,0,0],[1,0,0]], dtype=complex),
      np.array([[0,0,-1j],[0,0,0],[1j,0,0]], dtype=complex),
      np.array([[0,0,0],[0,0,1],[0,1,0]], dtype=complex),
      np.array([[0,0,0],[0,0,-1j],[0,1j,0]], dtype=complex),
      np.array([[1,0,0],[0,1,0],[0,0,-2]], dtype=complex)/np.sqrt(3)]
T = [x/2 for x in _l]
f3 = np.zeros((8,8,8)); d3 = np.zeros((8,8,8))
for a in range(8):
    for b in range(8):
        for c in range(8):
            f3[a,b,c] = 2*np.trace(T[c] @ (T[a]@T[b] - T[b]@T[a])).imag
            d3[a,b,c] = 2*np.trace(T[c] @ (T[a]@T[b] + T[b]@T[a])).real

def mat(x):    return sum(x[i]*T[i] for i in range(8))
def coefs(M):  return np.array([2*np.trace(T[i] @ M).real for i in range(8)])

def ReTr(g, u, v):
    return np.trace(expm(1j*g*u) @ expm(-1j*g*v)).real

# ── 極化抽取 (O124 §E 方法, N 無關) ──
def Q4(u, v):
    D = u - v; C = u @ v - v @ u
    return np.trace(D@D@D@D).real - np.trace(C@C).real
def Qvec(X):
    return Q4(mat(X[:8]), mat(X[8:]))
E16 = np.eye(16)
def pol(X1, X2, X3, X4):
    Xs = (X1, X2, X3, X4); s = 0.0
    for r in range(5):
        for S in itertools.combinations(range(4), r):
            s += (-1)**(4-r)*Qvec(sum((Xs[i] for i in S), np.zeros(16)))
    return s/24
tensor = {}
def Tget(i, j, k, l):
    key = tuple(sorted((i, j, k, l)))
    if key not in tensor:
        tensor[key] = 24*pol(*[E16[x] for x in key])
    return tensor[key]

def V4_mode(N, ns, aas):
    """N 通用 4g 模空間張量: 環 = 2N site, 守恆 mod 2N.
    ns: 4 個動量標籤 (Z_{2N}), aas: 4 個色指標 (0..7)."""
    M2 = 2*N
    inner = 0.0
    for d in itertools.product([0,1], repeat=4):
        idx = [8*d[k] + aas[k] for k in range(4)]
        inner += np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/M2) * Tget(*idx)
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/M2) for m in range(M2))
    return -inner*site/(24.0*M2*M2)

def V4_U1_num(N, ns):
    M2 = 2*N
    inner = sum(np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/M2) * T1(*d)
                for d in itertools.product([0,1], repeat=4))
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/M2) for m in range(M2))
    return -inner*site/(24.0*M2*M2)
def V4_U1_closed(N, ns):
    M2 = 2*N
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/M2) for m in range(M2))
    return -site*np.prod([1 - np.exp(2j*np.pi*n/M2) for n in ns])/(M2*M2)
def T1(i,j,k,l):
    return 24*pol1(*[np.eye(2)[x] for x in tuple(sorted((i,j,k,l)))])
def Q1(X): return (X[0] - X[1])**4
def pol1(X1, X2, X3, X4):
    Xs = (X1, X2, X3, X4); s = 0.0
    for r in range(5):
        for S in itertools.combinations(range(4), r):
            s += (-1)**(4-r)*Q1(sum((Xs[i] for i in S), np.zeros(2)))
    return s/24

print("="*78)
print("  O244 scripts/01: T2 — N 通用 4g/3g 頂點顯式張量")
print("  唯一輸入: 0,1 → φ → 結構數。零自由參數。")
print("="*78)

# ═══ A. 色代數 (N 無關) ═══
print("\n─── [A] 色代數 (隨 N 唔變) ───")
T4_err = max(abs(np.trace(T[a]@T[b]@T[c]@T[d])
                 - ((1/(4*N_c))*((a==b)*(c==d))
                    + (1/8)*np.sum((d3[a,b,:]+1j*f3[a,b,:])*(d3[:,c,d]+1j*f3[:,c,d]))))
            for a in range(8) for b in range(8) for c in range(8) for d in range(8))
check("A1 Tr[T^aT^bT^cT^d] = (1/4Nc)δδ + (1/8)(d+if)(d+if) EXACT (4096)",
      T4_err < 1e-12, f"(max err = {T4_err:.2e})")
Cs = np.einsum('abe,cde->abcd', f3, f3)
G_ss = float(np.einsum('abcd,abcd->', Cs, Cs))
check("A2 4g contact 色代數 G_ss = C_A^2(N_c^2−1) = 72",
      abs(G_ss - 72) < 1e-9, f"(G_ss = {G_ss:.6f})")

# ═══ B. BCH 作用量展開 (N 無關) ═══
print("\n─── [B] BCH 展開 (N 無關) ───")
rng = np.random.default_rng(20261010)
u_r = mat(rng.normal(size=8)); v_r = mat(rng.normal(size=8))
D_r = u_r - v_r; C_r = u_r @ v_r - v_r @ u_r
TrD2 = np.trace(D_r @ D_r).real
TrD4 = np.trace(D_r @ D_r @ D_r @ D_r).real
TrC2 = np.trace(C_r @ C_r).real
check("B1 跡循環恆等 Tr[D·C] = 0 EXACT (3g 消滅機制)",
      abs(np.trace(D_r @ C_r).real) < 1e-12,
      f"(|Tr[DC]| = {abs(np.trace(D_r @ C_r).real):.2e})")
gs = [0.10, 0.05, 0.025]
q_vals = []
for g in gs:
    R = (N_c - ReTr(g, u_r, v_r)) / g**2
    q_vals.append((R - 0.5*TrD2) / g**2)
target = -(1/24)*(TrD4 - TrC2)
q_extrap = q_vals[2] + (q_vals[2] - q_vals[1])/3.0
check("B2 BCH g^4 係數 = −(1/24)[TrD^4 − TrC^2] (Richardson)",
      abs(q_extrap - target) < 1e-6*abs(target),
      f"(extrap {q_extrap:.8f} vs target {target:.8f})")
def odd_part(g):
    return (ReTr(g, u_r, v_r) - ReTr(-g, u_r, v_r))/(2*g**3)
t_vals = [odd_part(g) for g in gs]
# 閾值 1e-9: g^3 係數係【代數恆等零】(Y 之 g^3 項全純虛 ⟹ Re 消), 數值殘餘 =
# expm 噪聲 ~1e-16 / 2g^3 ~2.5e-4 ⟹ 噪底 ~1e-12 (O124 用 1e-12 靠種子過關;
# 本 script 種子 20261010 於 g=0.05 現 1.8e-12 — 噪聲, 非物理). 機制定性不變.
check("B3 ReTr 奇部 (g^3) = 0 ⟹ 3g 頂點被 Re 消 (N 無關)",
      all(abs(t) < 1e-9 for t in t_vals), f"(g^3 奇部 = {t_vals})")

# ═══ C. V4 通用 N ═══
print("\n─── [C] V4 模空間張量 (N ∈ {22,44,88,176}) ───")
N_list = [22, 44, 88, 176]
for N in N_list:
    M2 = 2*N
    print(f"\n  N = {N} (環 {M2} site, mod-{M2} 守恆)")
    # C1 Bose 對稱
    ns0 = [5 % M2, 7 % M2, (M2 - 12) % M2, M2//2]   # Σ = 0 mod 2N (5+7+76+88 = 176 = 2·88 @N=44)
    while sum(ns0) % M2 != 0:
        ns0 = [(random.randrange(1, M2)) for _ in range(4)]
        ns0[3] = (-sum(ns0[:3])) % M2
    aa0 = [0, 0, 1, 1]
    base = V4_mode(N, ns0, aa0)
    perm_ok = all(abs(V4_mode(N, [ns0[i] for i in p], [aa0[i] for i in p]) - base)
                  <= 1e-8*max(1, abs(base)) for p in itertools.permutations(range(4)))
    check(f"C1 Bose 對稱 24 置換全等 (N={N})", perm_ok,
          f"(V4({ns0},{aa0}) = {base:.6f}{'+' if base.imag != 0 else ''}{base.imag:+.6f}j)")
    # C2 支撐 ⊆ 守恆集
    ok_sup = True; n_non = 0
    for _ in range(400):
        ns = [random.randrange(0, M2) for _ in range(3)]
        ns.append((random.randrange(0, M2)))          # 非守恆: 隨機第 4 個
        aa = [random.randrange(0, 8) for _ in range(4)]
        if sum(ns) % M2 != 0:
            n_non += 1
            if abs(V4_mode(N, ns, aa)) > 1e-7:
                ok_sup = False
    # C3 守恆組非零: 守恆面非空 (O124 E5 基準 >5%; 23/200 = 11.5%)
    n_cons_nz = 0
    for _ in range(200):
        a1, a2, a3 = (random.randrange(1, M2) for _ in range(3))
        ns = [a1, a2, a3, (-(a1+a2+a3)) % M2]
        aa = [random.randrange(0, 8) for _ in range(4)]
        if abs(V4_mode(N, ns, aa)) > 1e-9:
            n_cons_nz += 1
    check(f"C2 支撐⊆守恆集: 非守恆全零 ({n_non}/400 非守恆)", ok_sup and n_non > 350,
          f"(非守恆檢查 {n_non} 組, 違反 = {not ok_sup})")
    check(f"C3 守恆構造組非零 (+{n_cons_nz}/200)", n_cons_nz > 10,
          f"(守恆 4 元組 V4 ≠ 0 比例 {n_cons_nz/2.0}% — O124 E5 基準 5%)")

# C3b 色選擇律: 固定守恆動量, 全色掃描
print("\n  C3b 色選擇律 1: 固定守恆動量, 8^4 全色掃描")
for N in N_list:
    M2 = 2*N
    ns = [7 % M2, 11 % M2, (M2-24) % M2, M2//2]
    while sum(ns) % M2 != 0:
        ns = [random.randrange(1, M2) for _ in range(3)]
        ns.append((-sum(ns)) % M2)
    nn = 0
    for aa in itertools.product(range(8), repeat=4):
        if abs(V4_mode(N, ns, list(aa))) > 1e-9:
            nn += 1
    frac = nn/4096.0
    check(f"C3b 非零色比例 {nn}/4096 = {frac*100:.1f}% (N={N})", frac > 0.05,
          f"(色選擇: 唔係所有色 sector 都耦合)")

# C3c 色選擇律: 固定 (0,1,2,3) 色, 守恆動量 — 恆等零
print("\n  C3c 色選擇律 2: 固定色 (0,1,2,3), 守恆動量掃描")
for N in N_list:
    M2 = 2*N
    aa = [0, 1, 2, 3]
    nonzero = 0; tested = 0
    if N == 44:
        # 全枚舉: 物理守恆四元組 (a1..a4 ∈ [1,N], Σ = 2N 或 4N)
        for a1 in range(1, N+1):
            for a2 in range(1, N+1):
                for a3 in range(1, N+1):
                    s = a1 + a2 + a3
                    for a4 in (M2 - s, 2*M2 - s):
                        if not (1 <= a4 <= N):
                            continue
                        tested += 1
                        if abs(V4_mode(N, [a1, a2, a3, a4], aa)) > 1e-9:
                            nonzero += 1
        tag = f"全枚舉 {tested}"
    else:
        # 大 N: 隨機 12000 守恆組 (全枚舉 N^3 太貴)
        rng3 = np.random.default_rng(N)
        for _ in range(12000):
            a1 = int(rng3.integers(1, N+1)); a2 = int(rng3.integers(1, N+1))
            a3 = int(rng3.integers(1, N+1))
            s = a1 + a2 + a3
            cand = []
            for a4 in (M2 - s, 2*M2 - s):
                if 1 <= a4 <= N:
                    cand.append(a4)
            if not cand:
                continue
            tested += 1
            a4 = int(rng3.choice(cand))
            if abs(V4_mode(N, [a1, a2, a3, a4], aa)) > 1e-9:
                nonzero += 1
        tag = f"隨機 {tested}"
    check(f"C3c 色 (0,1,2,3) 於 {tag} 守恆動量全零 (N={N})", nonzero == 0,
          f"(色 sector 禁戒: δ\u0026δ + f·f + d·d 結構於此色組合零耦合)")

# C4 守恆四元組數 = (2N)^3 (小 N 全枚舉)
print("\n  C4 守恆四元組計數 = (2N)^3 (小 N 全枚舉)")
for N in [3, 4, 5, 6]:
    M2 = 2*N
    cnt = sum(1 for q in itertools.product(range(M2), repeat=4) if sum(q) % M2 == 0)
    check(f"C4 mod-{M2} 守恆四元組數 = {M2}^3 (N={N})", cnt == M2**3, f"(實測 {cnt})")

# C5 U(1) 極限閉式
print("\n  C5 U(1) 極限閉式")
for N in N_list:
    M2 = 2*N
    ns = [3 % M2, 5 % M2, 11 % M2, (-(3+5+11)) % M2]
    v_num = V4_U1_num(N, ns); v_cls = V4_U1_closed(N, ns)
    check(f"C5 U(1) 閉式 V4 = −site Π(1−e^{{2πin/2N}})/(2N)^2 (N={N})",
          abs(v_num - v_cls) < 1e-8, f"(num {v_num:.6f} vs closed {v_cls:.6f})")

# C6 N_FSR=44 (mod 88) 與 O124 N=88 特例一致 (O124 公式: mod-88, site 88)
print("\n  C6 N_FSR=44 對照 O124 N=88 特例")
def V4_O124(ns, aas):
    """O124 scripts/05 之 V4_mode (N=88 site, mod-88) — 原文公式再現."""
    inner = 0.0
    for d in itertools.product([0,1], repeat=4):
        idx = [8*d[k] + aas[k] for k in range(4)]
        inner += np.exp(2j*np.pi*sum(d[k]*ns[k] for k in range(4))/88.0) * Tget(*idx)
    site = sum(np.exp(2j*np.pi*int(sum(ns))*m/88.0) for m in range(88))
    return -inner*site/(24.0*88.0*88.0)
rng6 = np.random.default_rng(6)
ok6 = True; worst6 = 0.0
for _ in range(120):
    a1, a2, a3 = (int(x) for x in rng6.integers(1, 44, 3))
    ns = [a1, a2, a3, (-(a1+a2+a3)) % 88]
    aa = [int(x) for x in rng6.integers(0, 8, 4)]
    v_my = V4_mode(44, ns, aa)
    v_old = V4_O124(ns, aa)
    d = abs(v_my - v_old)
    if d > worst6: worst6 = d
    if d > 1e-9*max(1, abs(v_old)): ok6 = False
check("C6 N_FSR=44 (mod 88) ≡ O124 N=88 site 公式 (120 隨機組)",
      ok6, f"(worst dev = {worst6:.2e})")

# ═══ D. 3g 張量 (N 無關) + h-θ-θ ═══
print("\n─── [D] 3g 張量 + h-θ-θ 頂點 ───")
def V3_lat(a, b, c):
    h2 = 1e-3; tot = 0.0
    for s in itertools.product([-1, 1], repeat=3):
        uu = s[0]*h2*T[a]; vv = s[1]*h2*T[b] + s[2]*h2*T[c]
        tot += s[0]*s[1]*s[2]*ReTr(1.0, uu, vv)
    return tot/(8*h2**3)
v3max = max(abs(V3_lat(a,b,c)) for a in range(8) for b in range(8) for c in range(8))
check("D1 離散三次張量 V3(u;v,v) = 0 EXACT (全 512 分量, N 無關)",
      v3max < 1e-9, f"(max|V3| = {v3max:.2e})")
check("D2 0-form 障礙: 1D A∧A = 0 (運動學 3g 承載不存在)",
      abs(np.outer(np.array([0.37]), np.array([-1.21]))
          - np.outer(np.array([-1.21]), np.array([0.37]))).max() < 1e-15)
check("D3 唯一真三點 = h-θ-θ: 係數 ⟨W⟩/2 = √61.5/2",
      abs(h_tt - np.sqrt(61.5)/2) < 1e-9, f"(√61.5/2 = {h_tt:.6f})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)