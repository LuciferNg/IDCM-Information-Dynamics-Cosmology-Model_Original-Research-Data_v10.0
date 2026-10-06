#!/usr/bin/env python3
"""
O209 — Script 03: 唯一分配定理 (窮舉) + sympy 形式化
================================================================================
C1  模式集唯一性 — 窮舉 G2 子集 (N_search = 1)
C2  分配唯一性 — 窮舉 9! = 362880 雙射 (N_search = 1)
C3  全局方案數 = N_modeset x N_assignment = 1  (對照 legacy = 0)
C4  sympy 形式化 — Legendre 展開 / 積分閉式 / 環自同構封閉性
"""
import numpy as np, math, json, itertools, sys
from pathlib import Path
from fractions import Fraction

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
A5NODES = ROOT / "cmb_cold_spot/data/a5_nodes.txt"
OUT = Path(__file__).resolve().parent.parent / "data"
Nd = 44
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))

def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c

MASS = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}

# ── A5 動差 (與 script 01 同源) ──────────────────────────────────
nodes = np.loadtxt(A5NODES)
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
U = np.column_stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])
lc, bc = math.radians(209.0), math.radians(-57.0)
axis = np.array([math.cos(bc) * math.cos(lc), math.cos(bc) * math.sin(lc), math.sin(bc)])
axis /= np.linalg.norm(axis)
x = np.cos(np.arccos(np.clip(U @ axis, -1, 1)))

def leg(l, xx):
    if l == 0: return np.ones_like(xx)
    p0 = np.ones_like(xx); p1 = xx.copy()
    for k in range(2, l + 1):
        p0, p1 = p1, ((2 * k - 1) * xx * p1 - (k - 1) * p0) / k
    return p1

def Tn(n, xx): return np.cos(n * np.arccos(np.clip(xx, -1, 1)))
def a0(n): return 0.0 if n % 2 else -1.0 / (n * n - 1)

def G1(n): return v2(n) <= 2
def G2(n): return abs(float(Tn(n, x).sum()) - 60 * a0(n)) < 1e-3

print("=" * 96)
print("O209 Script 03: 唯一分配定理 (窮舉) + sympy 形式化")
print("=" * 96)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C1. 模式集唯一性 — 窮舉")
print("-" * 96)
g1 = [n for n in range(1, Nd + 1) if G1(n)]
g2 = [n for n in range(1, Nd + 1) if G2(n)]
print(f"  |G1| = {len(g1)}   |G2| = {len(g2)}  G2 = {g2}")
print(f"  C(44,9) = {math.comb(44, 9):,}")
print(f"  C(39,9) = {math.comb(39, 9):,}  (G1-限制下)")

# 窮舉: 所有 9-子集 S ⊂ {1..44} 使「全部元素過 G2」。
# ⚠️ C(44,9) = 7.09e8 不可直接迭代 ⟹ 用組合論證 (exhaustive by combinatorics):
#     G2 係逐模式謂詞 ⟹ 「全部元素過 G2」嘅 9-子集 = 從 G2-通過集取 9 個 = C(|G2|,9)
cnt_g2 = math.comb(len(g2), 9)                        # = C(9,9) = 1
cnt_g1g2 = math.comb(len(set(g2) & set(g1)), 9)       # (G1 ∧ G2) 飽和
print(f"  G2-飽和 9-子集數 = C({len(g2)},9) = {cnt_g2}   (組合論證, 唔需迭代 7e8)")
print(f"  (G1 ∧ G2)-飽和 9-子集數 = {cnt_g1g2}")
# 隨機 sanity check: 抽 200k 個 9-子集, 應該 0 個全部元素過 G2
rng = np.random.default_rng(209)
hits = 0
for _ in range(200_000):
    s = rng.choice(np.arange(1, Nd + 1), size=9, replace=False)
    if all(G2(int(n)) for n in s):
        hits += 1
print(f"  隨機 200k 個 9-子集 -> 全 G2 通過數 = {hits} (期望 0)")
unique_set = tuple(sorted(g2))
print(f"  唯一模式集 = {unique_set}")
chk("C1.1 G2 飽和 9-子集唯一 (C(9,9)=1)", cnt_g2 == 1)
chk("C1.2 隨機 sanity check: 0 個外來子集通過", hits == 0, f"{hits}/200000")
chk("C1.3 唯一模式集 = {1,2,3,4,5,7,9,11,13}", unique_set == (1, 2, 3, 4, 5, 7, 9, 11, 13))
chk("C1.4 G2 ⊂ G1", set(g2) <= set(g1))
chk("C1.5 N_search(modeset) = 1", cnt_g1g2 == 1)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C2. 分配唯一性 — 窮舉 9! 雙射")
print("-" * 96)
SEL = list(unique_set)
N = 88
NC = 88          # ★ 權威定義 (O136 scripts/63): Δm^(2) 掃描全部 88 個模式
idx = np.arange(1, N + 1)
psi = np.array([np.sin(n * math.pi * idx / (N + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
Xm = np.diag(idx - idx.mean())
V = psi @ Xm @ psi.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
# ★ 權威定義 (O136 scripts/63): 1/d 只在 |d| > 1e-12 時取, 否則 0
D = E[:, None] - E[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, Gm)
absdm = np.abs(dm[[n - 1 for n in SEL]])
chk("C2.0 重現 docs/33 |dm_1| = 16862.478721 (NC=88)", abs(absdm[0] - 16862.478721) < 1e-5,
    f"got {absdm[0]:.6f}")

particles = sorted(MASS, key=lambda p: -MASS[p])
logm = np.log(np.array([MASS[p] for p in particles]))
logdm = np.log(absdm)

# 閉式: 對單調無關變量, RMS = std(y)·sqrt(1 - corr(x,y)^2)
# ⟹ 最小化 RMS ⟺ 最大化 |corr| (窮舉 = 最大化相關)
perms = np.array(list(itertools.permutations(range(9))), dtype=np.int8)   # (362880, 9)
X = logdm[perms]                                  # (362880, 9)
Xc = X - X.mean(axis=1, keepdims=True)
Yc = logm - logm.mean()
num = (Xc * Yc).sum(axis=1)
den = np.sqrt((Xc ** 2).sum(axis=1) * (Yc ** 2).sum())
corr = num / den
std_y = float(logm.std())
rms_all = std_y * np.sqrt(np.clip(1 - corr ** 2, 0, None))
imin = int(np.argmin(rms_all))
min_rms = float(rms_all[imin])
n_at_min = int(np.sum(rms_all <= min_rms + 1e-9))
best_perm = tuple(int(v) for v in perms[imin])
mono = tuple(range(9))
mono_rms = std_y * math.sqrt(max(0.0, 1 - float(np.corrcoef(logdm, logm)[0, 1]) ** 2))

print(f"  9! = {len(perms)} 個雙射; 最小 RMS = {min_rms:.6f}")
print(f"  達到最小 (容差 1e-9) 嘅雙射數 = {n_at_min}")
print(f"  最小配對: {[SEL[j] for j in best_perm]} <- {particles}")
print(f"  單調配對 RMS = {mono_rms:.6f}   corr = {np.corrcoef(logdm, logm)[0,1]:.6f}")
chk("C2.1 窮舉 362880 雙射", len(perms) == 362880)
chk("C2.2 最小 RMS 唯一 (N=1)", n_at_min == 1, f"got {n_at_min}")
chk("C2.3 最小 = 單調配對", best_perm == mono, f"{best_perm}")
chk("C2.4 最小配對 = docs/33 最佳配對", [SEL[j] for j in best_perm] == [1, 2, 3, 4, 5, 7, 9, 11, 13],
    "t<->1 b<->2 tau<->3 c<->4 mu<->5 s<->7 d<->9 u<->11 e<->13")
chk("C2.5 分配遵守世代塊 {1,2,3}/{4,5,7}/{9,11,13}",
    sorted([SEL[j] for j in best_perm][:3]) == [1, 2, 3] and
    sorted([SEL[j] for j in best_perm][3:6]) == [4, 5, 7] and
    sorted([SEL[j] for j in best_perm][6:]) == [9, 11, 13])

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C3. 全局方案數 (對照 legacy)")
print("-" * 96)
N_global = cnt_g1g2 * n_at_min
print(f"  N_global = N_modeset x N_assignment = {cnt_g1g2} x {n_at_min} = {N_global}")
chk("C3.1 N_global = 1 (唔係 0 或 ∞)", N_global == 1, f"got {N_global}")

legacy = {
    "O34/O35":   {"mu": 1, "tau": 18, "u": 10, "d": 24, "s": 22, "c": 8, "b": 33, "t": 19},
    "O136/O54":  {"e": 1, "mu": 7, "tau": 20, "s": 14, "c": 34, "b": 33},
    "O120/O137": {"e": 1, "u": 1, "d": 1, "mu": 7, "tau": 20, "s": 14, "c": 34, "b": 33},
}
for nm, m in legacy.items():
    ns = set(m.values())
    n_g1 = sum(1 for n in ns if G1(n)); n_g2 = sum(1 for n in ns if G2(n))
    print(f"  {nm}: |set|={len(ns)}  G1 pass {n_g1}/{len(ns)}  G2 pass {n_g2}/{len(ns)}")
chk("C3.2 O34/O35 帶約束方案數 = 0 (d=24,c=8 違反 G1)",
    sum(1 for n in set(legacy["O34/O35"].values()) if G1(n)) < len(set(legacy["O34/O35"].values())))
chk("C3.3 O136/O54 帶約束方案數 = 0 (模式集 ≠ G2 集)",
    set(legacy["O136/O54"].values()) != set(g2))
chk("C3.4 O120/O137 帶約束方案數 = 0 (模式集 ≠ G2 集)",
    set(legacy["O120/O137"].values()) != set(g2))
chk("C3.5 舊框架 N=0 -> 新代數 N=1 (缺陷已解)",
    N_global == 1 and set(legacy["O136/O54"].values()) != set(g2))

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C4. sympy 形式化")
print("-" * 96)
try:
    import sympy as sp
    xx = sp.symbols('x')
    ok_all = True
    # C4.a Legendre 展開: T_n = Σ_{l≤n, l≡n(2)} c_l P_l
    for n in range(1, 17):
        Tn_expr = sp.chebyshevt(n, xx)
        # 展開成 Legendre
        coeffs = {}
        rem = sp.expand(Tn_expr)
        for l in range(n, -1, -1):
            Pl = sp.legendre(l, xx)
            c = sp.integrate(rem * Pl, (xx, -1, 1)) * sp.Rational(2 * l + 1, 2)
            c = sp.simplify(c)
            if c != 0:
                coeffs[l] = c
                rem = sp.expand(rem - c * Pl)
        par = [l for l in coeffs if l % 2 != n % 2]
        if par: ok_all = False
    chk("C4.a T_n 只含同奇偶 Legendre 分量 (n=1..16)", ok_all,
        "T_n = Σ_{l≡n(2), l≤n} c_l P_l")
    # C4.b 積分閉式 ∫_{-1}^{1} T_n dx = 0 (奇) / 2/(1-n²) (偶)
    ok_int = True
    for n in range(1, 17):
        I = sp.integrate(sp.chebyshevt(n, xx), (xx, -1, 1))
        want = 0 if n % 2 else sp.Rational(2, 1 - n * n)
        if sp.simplify(I - want) != 0: ok_int = False
    chk("C4.b ∫T_n dx = 0 (奇) / 2/(1-n²) (偶)", ok_int)
    # C4.c a0(n) = (1/2)∫T_n = -1/(n²-1) for even n
    ok_a0 = all(sp.simplify(sp.Rational(1, 2) * sp.integrate(sp.chebyshevt(n, xx), (xx, -1, 1))
                            - sp.Rational(-1, n * n - 1)) == 0 for n in range(2, 17, 2))
    chk("C4.c a0(n) = -1/(n²-1) (偶 n)", ok_a0)
    # C4.d 環自同構 (Z/88)^x 保 v2: v2(a·n) = v2(n), a 奇
    ok_v2 = all(v2(a * n) == v2(n) for a in range(1, 88, 2) for n in range(1, 45))
    chk("C4.d v2(a·n) = v2(n) 對全部奇 a (環自同構保 G1)", ok_v2)
    # C4.e 子環長度 L(n)=44/2^v2(n) 對允許模式 ∈ {11,22,44}
    Ls = set(int(Fraction(44, 2 ** v2(n))) for n in g1)
    chk("C4.e L(n) ∈ {11,22,44} (v2=0/1/2 -> 44/22/11)", Ls == {11, 22, 44}, str(sorted(Ls)))
    # C4.f 排除集 = 8|n
    chk("C4.f 排除集 = {8,16,24,32,40} = {n: 8|n}", [n for n in range(1, 45) if not G1(n)] == [8, 16, 24, 32, 40])
    print("  sympy 版本:", sp.__version__)
except ImportError as e:
    chk("C4 sympy 可用", False, str(e))

# ══════════════════════════════════════════════════════════════════
npass = sum(1 for _, ok, _ in checks if ok)
print("\n" + "=" * 96)
print(f"RESULT: {npass}/{len(checks)} PASS")
print("=" * 96)

json.dump({
    "G1": g1, "G2": g2, "selection": SEL,
    "C44_9": math.comb(44, 9), "C39_9": math.comb(39, 9),
    "N_search_modeset": cnt_g1g2,
    "N_search_assignment": n_at_min, "n_perm": len(perms),
    "min_rms": min_rms, "best_perm": list(best_perm),
    "best_pairing": {str(SEL[j]): particles[i] for i, j in enumerate(best_perm)},
    "N_global": N_global,
    "legacy": {k: sorted(set(v.values())) for k, v in legacy.items()},
    "checks_passed": npass, "checks_total": len(checks),
}, open(OUT / "03_uniqueness_theorem.json", "w"), indent=2, ensure_ascii=False)
print(f"\n-> data/03_uniqueness_theorem.json")
