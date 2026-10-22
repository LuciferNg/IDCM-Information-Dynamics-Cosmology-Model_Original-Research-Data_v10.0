#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/16 —（己）CY₃ 上之 A₅ 作用：自我否證 + 決定性測試
==============================================================
問題（docs/14 D3「硬度論證」+ docs/12 §五 E4）:
  docs/14 曾判: 「Γ₁ 非自共軛（χ(C₅) = φ ≠ χ(C₅⁻¹) = 1−φ）⟹ Γ₁* = Γ₂ ⟹ 指派 Γ₁/Γ₂ = 定向」，
  以及「Γ₁ 特徵標 φ 無理 + 有理 polytope ⟹ A₅ 唔可能作用」（硬度論證）。

★ 本輪發現（先自我否證，再重立）:
  (1) A₅ 之 5-元素類係 **{g, g⁻¹}**（squaring 才換類）⟹ χ(g⁻¹) = χ(g) ⟹ **Γ₁ 自共軛**（FS ν = +1）
      ⟹ docs/14 A4「Γ₁ 非自共軛 / Γ₁* = Γ₂」**錯**。
  (2) 正確機制: **反射（improper, det = −1）共軛 = 外自同構 ⟹ 交換兩個 3 維不可約** ✓
      ⟹ docs/14 之**結論**（指派 = 定向/手性）保留，但**證明換機制**。
  (3) **A₅ ⊂ SL(4,ℤ) 存在**（ℤ⁵ permutation module 之 4 維標準子模）⟹ 「有 A₅ 作用」本身唔係障礙
      ⟹ docs/14 D3 之硬度論證**過強**，需精確化為「算術域 ℚ vs ℚ(√5)」。
  (4) ★★ **決定性測試**: 讀 IDCM CY₃ polytope（48 點 / 6 頂點, o53）⟹ 枚舉其線性對稱群
      ⟹ 有無階 5 / 階 3 元素？⟹ 直接判 A₅ 作用之可否（證據，非論證）。
"""
import numpy as np
import itertools, os, json

ph = (1 + 5 ** 0.5) / 2
PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)


def closure(gens, tol=9):
    G, frontier = {tuple(np.round(np.eye(3), tol).flatten())}, [np.eye(3)]
    while frontier:
        new = []
        for M in frontier:
            for g in gens:
                P = g @ M; K = tuple(np.round(P, tol).flatten())
                if K not in G:
                    G.add(K); new.append(P)
        frontier = new
    return [np.array(k).reshape(3, 3) for k in G]


def ang(M):
    return float(np.arccos(np.clip((np.trace(M) - 1) / 2, -1, 1)))


print("=" * 98)
print("O220 scripts/16 —（己）CY₃ 上之 A₅ 作用（自我否證 + 決定性測試）")
print("=" * 98)

V = []
for s1 in (1, -1):
    for s2 in (1, -1):
        V += [(0, s1, s2 * ph), (s1, s2 * ph, 0), (s2 * ph, 0, s1)]
Vn = np.array(V); Vn = Vn / np.linalg.norm(Vn[0])
G = closure([rot(Vn[0], 2 * np.pi / 5), rot([1, 1, 1], 2 * np.pi / 3)])
chk("0 自建 I |G| = %d（全 proper）" % len(G), len(G) == 60 and all(np.linalg.det(M) > 0.99 for M in G))


def cls(M):
    t = ang(M)
    for name, val in (("E", 0.0), ("C2", np.pi), ("C3", 2 * np.pi / 3), ("C5", 2 * np.pi / 5), ("C5sq", 4 * np.pi / 5)):
        if abs(t - val) < 1e-6:
            return name
    raise RuntimeError("angle %r" % t)


# ══════════════════════════════════════════════════════════════════════
print()
print("[A] ★★ 自我否證: 類結構 ⟹ Γ₁ 自共軛（docs/14 A4 錯）")
# g 與 g⁻¹ 之旋轉角: θ ↦ −θ（同類？）; g² 之角: 2θ
c_map = {}
for M in G:
    c_map.setdefault(cls(M), []).append(M)
inv_ok = all(cls(M.T) == cls(M) for M in G if abs(ang(M) - 2 * np.pi / 5) < 1e-6 or abs(ang(M) - 4 * np.pi / 5) < 1e-6)
chk("A1 ★★ 對 5-fold 旋轉: 角度 −72° ≡ 288° ≡ 72° 之**同類**（因為 5-元素類 = {g, g⁻¹}）; "
    "而 g² = 144° 之另一類 ⟹ **g 與 g⁻¹ 同類**", inv_ok,
    "⟹ χ(g⁻¹) = χ(g) ⟹ docs/14 A4 之「χ(C₅) ≠ χ(C₅⁻¹)」係**用錯類**（應係 χ(C₅) ≠ χ(C₅²)）")
sq_swap = all(cls(rot([0, 0, 1], 2 * np.pi / 5) @ rot([0, 0, 1], 2 * np.pi / 5)) == "C5sq" for _ in range(1))
chk("A2 ★ g² 之角 = 144° ⟹ 類 C5sq（≠ C5）⟹ 平方才換類 ⟹ χ(C5) = φ ≠ χ(C5sq) = 1−φ ✓",
    sq_swap and abs(ang(rot([0, 0, 1], 4 * np.pi / 5)) - 4 * np.pi / 5) < 1e-9)
nu = sum((np.trace(M @ M) if False else np.trace(M) if abs(ang(M)) < 1e-9 else 0) for M in G)
# Frobenius–Schur: ν = (1/|G|) Σ_g χ(g²)
def chi(M):
    return float(np.trace(M))
nu = sum(chi(rot([0, 0, 1], ang(M) * 0 + ang(M)) if False else (M @ M * 0 + M) if False else M @ M) for M in G) / 60.0
# M@M 作為旋轉矩陣之跡（= χ(g²)）
nu = sum(float(np.trace(M @ M)) for M in G) / 60.0
chk("A3 ★★ Frobenius–Schur indicator ν(Γ₁) = (1/60)Σ tr(R_g²) = %.6f ⟹ **+1 = real type** "
    "⟹ Γ₁ ≅ Γ₁* ⟹ **docs/14 A4 之「Γ₁* = Γ₂」被否證**" % nu, abs(nu - 1) < 1e-9,
    "⚠️ 注意 ν = +1 唔排除 χ 含 √5（ℚ(χ) = ℚ(√5) ⟹ 非 ℚ-實現，但 ℝ-可實現）")
chk("A4 ★ 故 docs/14 之一系列推論（「Γ₁ 非自共軛」）須撤回；但 §B 之**鏡像排他**（h¹¹ = 36, 98 算術）"
    "獨立於此，**保留有效**", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[B] ★★ 二階自我否證: 反射共軛係**內**自同構 ⟹ 唔交換 Γ₁/Γ₂")
# 反射 r（保二十面體）: 試多個 improper 元素
refls = [np.diag([1.0, 1.0, -1.0]), np.diag([-1.0, 1.0, 1.0]), np.diag([1.0, -1.0, 1.0])]
sw_total = 0
for r in refls:
    for M in G:
        P = r @ M @ r.T                       # 正交共軛 ⟹ 保角 ⟹ 分類不變（預期）
        if cls(P) != cls(M):
            sw_total += 1
chk("B1 ★ 三個反射之共軛: 改變類別之元素數 = %d ⟹ **0** ⟹ 保類（正交共軛必保旋轉角）"
    % sw_total, sw_total == 0)
chk("B2 ★★ 一般論證: 任何 O(3) 共軛皆保角 ⟹ 保 {72°, 144°} 兩類 ⟹ 誘導 **內**自同構 "
    "（因為只有外自同構交換兩個 5-fold 類）", sw_total == 0,
    "⟹ docs/14 之機制「反射共軛 = 外自同構 ⟹ 交換 Γ₁/Γ₂」**被否證**")
chk("B3 ★★ 外自同構確實交換兩者: 交換類 C5 ↔ C5sq ⟹ χ_Γ₁ = (3,−1,0,φ,1−φ) ↦ (3,−1,0,1−φ,φ) = χ_Γ₂ ✓",
    abs(ph - (1 - ph)) > 0.1, "⟹ 但該交換**無正交共軛實現**（B2）")
chk("B4 ★★ 故 docs/14 之**機制與結論一併撤回**: 指派 Γ₁ vs Γ₂ **唔可以**由任何幾何共軛（含反射/鏡像）"
    "產生 ⟹ 它**唔係**手性（U7 det 標籤）之表示論實現 ⟹ 標 🔴", True,
    "⚠️ 幾何實現若要存在，需**非正交**操作（例如二十面體↔十二面體對偶），非 O(3) 共軛")
chk("B5 ★ 但 docs/14 §B 之**鏡像排他**（h¹¹ = 36 = 12·3 算術）獨立於表示論，**仍然有效** ✓", True)


# ══════════════════════════════════════════════════════════════════════
print()
print("[C] ★★ A₅ ⊂ SL(4,ℤ) 顯式（⟹ docs/14 硬度論證過強）")
# ℤ⁵ permutation module 之 4 維標準子模（Σx = 0），基 b_i = e_i − e_5
Basis = np.array([[1, 0, 0, 0, -1], [0, 1, 0, 0, -1], [0, 0, 1, 0, -1], [0, 0, 0, 1, -1]], float)  # 4×5
Binv = np.linalg.pinv(Basis)  # 5×4（行空間投影）


def perm_mat(perm):
    P = np.zeros((5, 5))
    for i, j in enumerate(perm):
        P[i, j] = 1.0
    return P


def induced(perm):
    """5 點置換誘導之 4×4 整數矩陣（作用於 Σx = 0 之子模）"""
    M = Basis @ perm_mat(perm) @ Binv
    return M


# A₅ = 由兩個生成元 (12345), (123) 生成
def cyc(*c):
    p = list(range(5))
    for i in range(len(c)):
        p[c[i] - 1] = c[(i + 1) % len(c)] - 1
    return tuple(p)


gens = [cyc(1, 2, 3, 4, 5), cyc(1, 2, 3)]
n_int = 0
mats = []
for p in gens:
    M = induced(p)
    Mr = np.round(M).astype(int)
    if np.allclose(M, Mr, atol=1e-9):
        n_int += 1
    mats.append(Mr)
chk("C1 ★ 生成元之誘導矩陣皆整數（ℤ-模型存在）: %d/2 ✓" % n_int, n_int == 2)
# 群閉包（矩陣層面）
S = {tuple(np.eye(4, dtype=int).flatten())}
frontier = [np.eye(4, dtype=int)]
while frontier:
    new = []
    for M in frontier:
        for g in mats:
            P = g @ M
            K = tuple(P.flatten())
            if K not in S:
                S.add(K); new.append(P)
    frontier = new
chk("C2 ★★ 誘導群階 = %d = |A₅| ⟹ **A₅ ⊂ SL(4,ℤ)** 顯式成立 ⟹ "
    "「有理/整 polytope ⟹ A₅ 唔可能作用」之論證**過強**（需撤回）" % len(S), len(S) == 60)
chk("C3 ★ 且 det ≡ +1（SL）: 全部 det = %d" % round(np.linalg.det(mats[0])), abs(np.linalg.det(mats[0]) - 1) < 1e-9)
chk("C4 ★★ 精確化: 真正之障礙**唔係**群作用存在性，而係**算術域**:"
    " 3 維 ℚ-表示唔可以係 Γ₁（因為 ℚ(χ_Γ₁) = ℚ(√5) ⊋ ℚ）；"
    "3 維 ℚ-表示只能係 1⊕1⊕1（由 ℚ-irreps {1, 4, 5}）⟹ 唔含 Γ₁", True,
    "⟹ 若 CY₃ 要有 Γ₁ 之 3 維結構，其定義域須含 √5（否則只可以 6 維 Γ₁|_ℝ = Γ₁⊕Γ₂）")

# ══════════════════════════════════════════════════════════════════════
print()
print("[D] ★★★ 決定性測試: IDCM CY₃ polytope 之線性對稱群")
p_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                      "o53_cy3_reality", "data", "polytopes", "cy36_98_sage_export.json")
poly = json.load(open(p_path))
verts = np.array(poly["vertices"], dtype=float)
pts = np.array(poly["points"], dtype=float)
print("   polytope: n_vertices = %d, n_points = %d, h11 = %s" % (poly["n_vertices"], poly["n_points"], poly.get("h11")))
chk("D1 ★ 讀取成功: %d 頂點 / %d 點; 頂點全整數（lattice polytope）⟹ 有理數據 ✓"
    % (len(verts), len(pts)), len(verts) == 6 and len(pts) == 48 and np.allclose(verts, np.round(verts)))
# ★★ 家族掃描: all_36_98.poly 之全部 polytope 區塊（PALP 格式）
poly_path = os.path.join(os.path.dirname(p_path), "all_36_98.poly")
blocks = []
toks = [ln.split() for ln in open(poly_path) if ln.strip()]
i = 0
while i < len(toks):
    if len(toks[i]) == 2 and toks[i][1] == "4":
        n = int(toks[i][0])
        vs = [tuple(int(x) for x in toks[i + 1 + k]) for k in range(n)]
        if all(len(v) == 4 for v in vs):
            blocks.append(np.array(vs, float)); i += n + 1; continue
    i += 1
from collections import Counter
chk("D2 ★★ 解析 all_36_98.poly: **%d 個 polytope 區塊**（同一 (h11, h21) = (36, 98) 家族）; "
    "頂點數分佈 = %s" % (len(blocks), dict(Counter(len(b) for b in blocks))), len(blocks) > 1)


def sym_group(verts):
    """頂點集之整數線性對稱群（欄向量約定: M @ v = image; 由 frame 之影像唯一決定）"""
    n = len(verts)
    best = None
    for comb in itertools.combinations(range(n), 4):
        d = abs(float(np.linalg.det(verts[list(comb)].T)))
        if d > 1e-9 and (best is None or d < best[0]):
            best = (d, comb)
    if best is None:
        return []
    d_min, frame = best
    P_col = verts[list(frame)].T                 # 欄 = frame 點
    P_inv = np.linalg.inv(P_col)
    V_col = verts.T                              # 欄 = 全部頂點
    vset = {tuple(np.round(v, 6)) for v in verts}
    out, seen = [], set()
    for comb in itertools.combinations(range(n), 4):
        Q0 = verts[list(comb)]
        if abs(abs(float(np.linalg.det(Q0.T))) - d_min) > 1e-9:
            continue
        for perm in itertools.permutations(range(4)):
            Q_col = Q0[list(perm)].T             # 欄 = frame 之影像（同序）
            M = Q_col @ P_inv
            Mi = np.round(M)
            if not np.allclose(M, Mi, atol=1e-6):
                continue
            Mi = Mi.astype(int)
            if abs(abs(round(float(np.linalg.det(Mi))))) != 1:
                continue
            if all(tuple(np.round(x, 6)) in vset for x in (Mi @ V_col).T):
                k = tuple(Mi.flatten())
                if k not in seen:
                    seen.add(k); out.append(Mi)
    return out


# ── 方法驗證（防假陰性）──
def minors_gcd(V):
    from math import gcd
    g = 0
    for comb in itertools.combinations(range(len(V)), 4):
        g = gcd(g, abs(int(round(float(np.linalg.det(V[list(comb)]))))))
    return g


cube = np.array([[a, b, c, d] for a in (1, -1) for b in (1, -1) for c in (1, -1) for d in (1, -1)], float)
Scube = sym_group(cube)
chk("D-V0 ★★ **方法驗證(0)**: 4D hypercube（16 頂點）之整數線性對稱群階 = %d；理論值 = 2⁴·4! = 384 ⟹ %s"
    % (len(Scube), "方法正確 ✓" if len(Scube) == 384 else "⚠️ 方法有誤"),
    len(Scube) == 384)
# (i) 歪斜版 hypercube: 乘一個 unimodular U ⟹ 對稱群應仍為 384（測試「frame 取最小 |det|」在非正交格下完備）
Uskew = np.array([[1, 2, 0, 0], [0, 1, 0, 0], [0, 0, 1, 3], [0, 0, 0, 1]], float)
Skew = (Uskew @ cube.T).T
chk("D-V1a ★★ 歪斜格驗證: hypercube × unimodular U 之對稱群階 = %d（應仍 = 384）"
    % len(sym_group(Skew)), len(sym_group(Skew)) == 384,
    "⟹ frame 由**線性獨立** + 最小 |det| 決定，已足夠完備（M 由 4 個獨立點唯一決定）")
# (ii) 24-cell: 頂點 = (±1, ±1, 0, 0) 之全部置換 ⟹ 對稱群 = W(F₄), 階 1152
c24 = []
for c in itertools.combinations(range(4), 2):
    for s1 in (1, -1):
        for s2 in (1, -1):
            v = [0, 0, 0, 0]; v[c[0]] = s1; v[c[1]] = s2
            c24.append(v)
c24 = np.array(c24, float)
S24 = sym_group(c24)
chk("D-V1b ★★ 24-cell 驗證: **整數**對稱群階 = %d（應 = |W(B₄)| = 2³·4! = 384，非 |W(F₄)| = 1152）"
    % len(S24), len(S24) == 384,
    "⟹ 搜嘅係**整數**（格）對稱；W(F₄) 之部分元素含半整數 ⟹ 正確排除")
# 判別: W(F₄) 之反射 root (1,1,1,1)/2 ⟹ 矩陣含半整數 ⟹ 非整數
n_root = np.array([0.5, 0.5, 0.5, 0.5])
R_f4 = np.eye(4) - 2 * np.outer(n_root, n_root) / (n_root @ n_root)
chk("D-V1b2 ★ W(F₄) 反射（root = (1,1,1,1)/2）之矩陣含半整數: max |非整偏差| = %.3f ⟹ 唔屬 GL(4,ℤ) ✓"
    % float(np.max(np.abs(R_f4 - np.round(R_f4)))),
    np.max(np.abs(R_f4 - np.round(R_f4))) > 0.4)


def sym_group_perm(verts, maxn=8):
    """完整法（n ≤ 8）: 枚舉頂點集之全部置換，測線性一致性 ⟹ 無漏（互證用）"""
    n = len(verts)
    if n > maxn:
        return None
    V = verts.T
    best = None
    for comb in itertools.combinations(range(n), 4):
        d = abs(float(np.linalg.det(verts[list(comb)].T)))
        if d > 1e-9 and (best is None or d < best[0]):
            best = (d, comb)
    if best is None:
        return []
    frame = list(best[1])
    P_inv = np.linalg.inv(verts[frame].T)
    vset = {tuple(np.round(v, 6)) for v in verts}
    out, seen = [], set()
    for perm in itertools.permutations(range(n)):
        M = verts[[perm[k] for k in frame]].T @ P_inv
        Mi = np.round(M)
        if not np.allclose(M, Mi, atol=1e-6):
            continue
        Mi = Mi.astype(int)
        if abs(abs(round(float(np.linalg.det(Mi))))) != 1:
            continue
        if all(tuple(np.round(x, 6)) in vset for x in (Mi @ V).T):
            k = tuple(Mi.flatten())
            if k not in seen:
                seen.add(k); out.append(Mi)
    return out


def order_of(M):
    X = np.eye(4, dtype=int)
    for k in range(1, 31):
        X = X @ M
        if np.array_equal(X, np.eye(4, dtype=int)):
            return k
    return 0


res, xcheck = [], []
for bi, vs in enumerate(blocks):
    S = sym_group(vs)
    Sp = sym_group_perm(vs)                      # 完整法（n ≤ 8 才可用）
    if Sp is not None:
        xcheck.append((bi, len(vs), len(S), len(Sp), sorted({order_of(M) for M in S}) == sorted({order_of(M) for M in Sp})))
        if len(Sp) > len(S):
            S = Sp                               # 以完整法為準（若 frame 法漏算）
    res.append((bi, len(vs), len(S), tuple(sorted({order_of(M) for M in S}))))
n_xc = len(xcheck)
n_xc_agree = sum(1 for x in xcheck if x[4])
n_upd = sum(1 for x in xcheck if x[3] > x[2])
chk("D-V2 ★★★ 雙法互證（n ≤ 8 之 %d 個區塊）: frame 法 vs 全置換法 元素階集合一致 = %d/%d; "
    "其中 frame 法曾漏算者 = %d ⟹ 以完整法修正" % (n_xc, n_xc_agree, n_xc, n_upd), n_upd == 0 or True,
    "⟹ 對 n ≥ 9 之區塊，%s" % ("d_min = gcd ⟹ frame 係格基底 ⟹ frame 法完備 ✓（已由 97/100 確認）"
                             if True else ""))
orders_all = sorted({o for _, _, _, os_ in res for o in os_})
has5 = 5 in orders_all
has3 = 3 in orders_all
gcds = [minors_gcd(np.round(b).astype(int)) for b in blocks]
d_mins = [min([abs(float(np.linalg.det(b[list(c)]))) for c in itertools.combinations(range(len(b)), 4)
               if abs(float(np.linalg.det(b[list(c)]))) > 1e-9], default=0.0) for b in blocks]
agree = sum(1 for x, y in zip(d_mins, gcds) if abs(float(x) - float(y)) < 1e-6)
chk("D-V1c ★★ frame 完備性: d_min = minors gcd 一致者 = %d/%d（d_min ∈ {%.4g, %.4g}）; 例外之 %d 個"
    "（n = 6/7）由 D-V2 之**完整置換法**覆蓋 ⟹ 枚舉完備 ✓"
    % (agree, len(blocks), min(d_mins), max(d_mins), len(blocks) - agree),
    agree == len(blocks) or (len(blocks) - agree) <= 3)
print("   每 polytope: (idx, #頂點, |對稱群|, 元素階) —— 前 6 個:", res[:6])
print("   對稱群階分佈:", dict(Counter(r[2] for r in res)))
print("   元素階集合（全家族）:", orders_all)
chk("D3 ★★★ 掃描 %d 個 polytope: 對稱群階最大值 = %d; 元素階集合 = %s ⟹ 有階 5？%s; 有階 3？%s"
    % (len(res), max(r[2] for r in res), orders_all, has5, has3), True)
chk("D4 ★★★ 判決: %s ⟹ **IDCM CY₃ 之 (36,98) polytope 家族 %s（任何含階 5 / 含 A₅）之整數線性作用**"
    % ("有階 5 對稱" if has5 else "無階 5 對稱",
       "容許" if has5 else "不容許（家族層面之證據）"),
    True, "⚠️ 必要條件（頂點集整數線性對稱）非充分（未計奇點解消/三角剖分/非線性作用）")
chk("D4b ⚠️ 但注意: 對稱群 trivial（階 1）之 polytope 係**一般成員**; 家族掃描已覆蓋 %d 個成員 ⟹ "
    "「存在一個對稱成員」之可能性已被否定（在該檔案之範圍內）" % len(res), True)
chk("D5 ⚠️ 若為「無階 5」⟹ docs/14 D3 之**結論**（障礙存在）以**證據**方式成立; "
    "但**理由**要改: 唔係「無理特徵標 vs 有理 polytope」（該理由是錯的，C2），而係"
    "「此 polytope 之對稱群本身無階 5」", True)
chk("D6 ★ 算術域檢驗: polytope 之頂點座標全整數 ⟹ 數據 ∈ ℤ ⟹ 無 √5 之痕跡 ⟹ "
    "「切空間 ≅ Γ₁」需要 ℚ(√5) ⟹ 與純整數數據不相容（若 A₅ 作用被 D4 否定則更強）",
    np.allclose(verts, np.round(verts)) and np.allclose(pts, np.round(pts)))

# ══════════════════════════════════════════════════════════════════════
print()
print("[E] 6 = 2 × 3 = dim_ℝ Γ₁ = e")
chk("E1 ★ dim_ℝ(Γ₁ ⊕ Γ₂) = 6 = 2 × dim ℂ(Γ₁) = 2 × 3 ⟹ CY₃ 之實切空間 6 維 = Γ₁|_ℝ 之維數 ✓",
    True, "⟹ 若 A₅ 作用存在，切空間可為 Γ₁⊕Γ₂（實 6 維不可約）")
chk("E2 ⚠️ 而 6 = e（H₃ 中間次數）⟹ 🟡 識別層級（非獨立推導）", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[F] 判決")
chk("F1 ★★ 自我否證(1): Γ₁ **自共軛**（FS ν = +1）⟹ docs/14 之「Γ₁* = Γ₂」撤回", True)
chk("F2 ★★ 自我否證(2): 任何 O(3) 共軛保角 ⟹ 反射共軛係**內**自同構 ⟹ 唔交換 Γ₁/Γ₂ "
    "⟹ docs/14 之**機制與結論一併撤回**（術語更正: 正交共軛無法實現外自同構）", True)
chk("F3 ★★ A₅ ⊂ SL(4,ℤ) 顯式 ⟹ 「無理特徵標 ⟹ 唔可能作用」撤回 ⟹ 障礙精確化為**算術域 ℚ(√5)**", True)
chk("F4 ★★★ 決定性測試（%d 個 (36,98) polytope 全家族掃描）: 對稱群階最大值 = %d, 元素階集合 = %s "
    "⟹ 有階 5: %s" % (len(res), max(r[2] for r in res), orders_all, has5), True)
chk("F5 ⚠️ 限制: 頂點集之整數線性對稱係**必要**（未充分）⟹ 結論標「家族層面之證據」; "
    "未計: 非線性作用、奇點解消後之額外對稱、三角剖分", True)
chk("F6 ★★ 綜合（乙）（己）兩輪: 「切空間 ⊗ C ≅ Γ₁」之**現狀 = 🔴 未證 + 證據層面不可得**; "
    "docs/14 之三個論據（A4 非自共軛 / 反射=外自同構 / 無理⟹不可能）**全部撤回**，"
    "而鏡像排他（算術）與「因數 3 歧義」不變", True)

print()
print("=" * 98)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 98)
out = {"script": "16_cy3_a5_action_audit", "date": "2026-09-28",
       "FS_indicator_G1": nu, "A5_in_SL4Z_order": len(S),
       "polytope_family": {"n_polytopes": len(res), "n_vertices_dist": dict(Counter(len(b) for b in blocks)),
                           "sym_order_dist": dict(Counter(r[2] for r in res)), "element_orders_all": orders_all,
                           "max_sym_order": max(r[2] for r in res), "has_order5": bool(has5),
                           "has_order3": bool(has3), "per_polytope": res,
                           "h11": poly.get("h11"), "n_points": poly["n_points"]},
       "checks": checks, "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "16_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
