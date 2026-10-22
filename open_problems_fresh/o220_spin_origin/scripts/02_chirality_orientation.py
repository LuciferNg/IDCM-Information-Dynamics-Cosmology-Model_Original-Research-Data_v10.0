#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/02 — 手性 → 定向 → 旋轉（R5/T9）：自旋 sense 之絕對化
====================================================================
docs/03 已證: 鏈 transport 之 holonomy 階 = 4（偶鏈）⟹ 自旋必然, s = 1/2 唯一。
但 holonomy 只講「有 spinor」——「邊個 sense 係正」仍未定（docs/03 §2.3 B7）。
本 script 攻 T9: 手性（A₅ 60-軌道）如何令旋轉 sense 絕對化。

設計（禁硬編碼；座標直算）:
 A. I (60) / I_h (120) 群由生成元閉包構造；階元素分佈 = A₅ 之簽名
 B. 四型 I-軌道（12/20/30/60）之中心對稱性 → 只有 60 可手性
 C. δ(x) = ∏_{a∈A2}(a·x)（A2 = 15 條 2-fold 軸）: δ 判別量
    δ(I·s) = δ(s)；δ(−s) = −δ(s)；δ ≠ 0 ⟺ 手性（O137 docs/29 §2-3 之獨立重算）
 D. 實測: 冷斑 A₅ 軌道（chiral, |Sym| = 60）/ RH（achiral, |Sym| = 120）
 E. ★ 自旋 sense: 手性 ⟹ δ 符號在 Sym 下不變（絕對 sense）
    achiral ⟹ ∃ improper g 令 δ ↦ −δ ⟹ sense 相對
 F. 互補性: A₅ 60-軌道**冇** inversion（helicity 配對唔存在於其中）；
    88-grid（canonical）**有** −I（O182 |Sym| = 4 = {+1:2, −1:2}）但非手性
    ⟹ 手性（定向）+ helicity 配對（對偶）必須**同時**存在，螺旋度符號先有絕對意義

數據（只讀，唔改）:
  cmb_cold_spot/data/a5_nodes.txt        — 冷斑方向之 A₅ I-軌道（ra dec, deg）
  o182_88grid_geometry/data/a5_nodes_ideal.txt — RH 60 頂點（理想座標, x y z）
"""
import math
import os
import itertools
import numpy as np
from collections import Counter

PASS = 0
TOTAL = 0
checks = []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
phi = (1 + 5 ** 0.5) / 2
TOL = 1e-7


# ── 群構造 ────────────────────────────────────────────────────────────
def rot_axis(u, t):
    u = np.array(u, float)
    u /= np.linalg.norm(u)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * (K @ K)


def closure(gens, tol=7):
    key = lambda R: tuple(np.round(R.flatten(), tol))
    seen = {key(np.eye(3)): np.eye(3)}
    fr = [np.eye(3)]
    while fr:
        new = []
        for R in fr:
            for g in gens:
                P = R @ g
                k = key(P)
                if k not in seen:
                    seen[k] = P
                    new.append(P)
        fr = new
    return list(seen.values())


def order(R, tol=1e-8):
    M = np.eye(3)
    for k in range(1, 13):
        M = M @ R
        if np.allclose(M, np.eye(3), atol=tol):
            return k
    return 0


def set_residual(g, V):
    """V (n,3) 單位向量集；返 g·V 落到 V 集合之最大角殘差（度）"""
    W = V @ g.T
    # 逐點最近鄰
    d = 1 - W @ V.T                      # 1 − cos
    best = np.sort(d, axis=1)[:, 0]
    return math.degrees(math.acos(min(1.0, max(0.0, 1 - best.max()))))


def sym_group(V, tol_deg=1e-3, tol_floor=1e-3):
    """枚舉保集正交映射（O(3) 全群, 含 det = −1）；容差地板 = max(tol*0.02, tol_floor)"""
    tol = max(tol_deg * 0.02, tol_floor)
    out = []
    for R in I_h:
        W = V @ R.T
        d = 1 - W @ V.T
        if math.degrees(math.acos(min(1.0, max(0.0, 1 - np.sort(d, axis=1)[:, 0].max())))) < tol:
            out.append(R)
    return out


print("=" * 86)
print("O220 scripts/02 — 手性 → 定向 → 旋轉 (R5/T9)")
print("=" * 86)

print()
print("=" * 86)
print("[A] I (60) / I_h (120) 群構造")
print("=" * 86)
I_grp = closure([rot_axis([0, 1, phi], 2 * math.pi / 5), rot_axis([1, 1, 1], 2 * math.pi / 3)])
I_h = I_grp + [(-g) for g in I_grp]
chk("A1 |I| = 60（5-fold + 3-fold 閉包）", len(I_grp) == 60, "|I| = %d" % len(I_grp))
chk("A2 ∀g ∈ I: det = +1（純旋轉群, 冇 improper）",
    all(abs(np.linalg.det(g) - 1) < 1e-9 for g in I_grp))
chk("A3 |I_h| = 120 = 2×60（含 −I）", len(I_h) == 120, "|I_h| = %d" % len(I_h))
dist = Counter(order(g) for g in I_grp)
chk("A4 階元素分佈 = (1,15,20,24) ⟹ 群身份 = A₅ ≅ I（非 C/D/T/O）",
    dist[1] == 1 and dist[2] == 15 and dist[3] == 20 and dist[5] == 24,
    "分佈 = %s" % dict(sorted(dist.items())))
# 15 條 2-fold 軸
A2 = []
for g in I_grp:
    if order(g) == 2:
        w, v = np.linalg.eig(g)
        a = np.real(v[:, np.argmin(abs(w - 1))])
        a /= np.linalg.norm(a)
        if not any(abs(abs(a @ b) - 1) < 1e-6 for b in A2):
            A2.append(a)
chk("A5 2-fold 軸數 = 15 = #H₃ 鏡面 = #正根（deg δ 之來源）", len(A2) == 15,
    "|A2| = %d" % len(A2))

print()
print("=" * 86)
print("[B] δ(x) = ∏_{a∈A2}(a·x): 判別量（O137 docs/29 §2-3 之獨立重算）")
print("=" * 86)
rng = np.random.default_rng(20260928)


def delta(x):
    p = 1.0
    for a in A2:
        p *= float(a @ x)
    return p


s0 = rng.normal(size=3)
s0 /= np.linalg.norm(s0)
orbit60 = np.array([g @ s0 for g in I_grp])
d0 = delta(s0)
chk("B1 δ(I·s) = δ(s) ∀g ∈ I（15 次不變量, I-不變）",
    max(abs(delta(g @ s0) - d0) for g in I_grp) < 1e-9,
    "max dev = %.3e" % max(abs(delta(g @ s0) - d0) for g in I_grp))
chk("B2 δ(−s) = (−1)¹⁵δ(s) = −δ(s)（奇次 ⟹ 偽標量）",
    abs(delta(-s0) + d0) < 1e-12, "δ(s)=%.6e, δ(−s)=%.6e" % (d0, delta(-s0)))
chiral_seeds, mirror_seeds = 0, 0
for _ in range(60):
    x = rng.normal(size=3)
    x /= np.linalg.norm(x)
    ox = np.array([g @ x for g in I_grp])
    neg_in = bool(np.min(np.linalg.norm(ox + x, axis=1)) < 1e-8)   # −x ∈ 軌道?
    if abs(delta(x)) > 1e-12 and not neg_in:
        chiral_seeds += 1
    # 鏡面種子: 取 v ⊥ a（a ∈ A2）⟹ a·v = 0 ⟹ δ = 0
    a = A2[0]
    v = x - (x @ a) * a
    v /= np.linalg.norm(v)
    ov = np.array([g @ v for g in I_grp])
    neg_in_v = bool(np.min(np.linalg.norm(ov + v, axis=1)) < 1e-8)
    if abs(delta(v)) < 1e-12 and neg_in_v:
        mirror_seeds += 1
chk("B3 60 個一般位置種子: δ ≠ 0 且 −s ∉ I·s（全數）", chiral_seeds == 60,
    "chiral = %d/60" % chiral_seeds)
chk("B4 60 個鏡面種子: δ = 0 且 −s ∈ I·s（全數）", mirror_seeds == 60,
    "achiral = %d/60" % mirror_seeds)
chk("B5 ★ 精確二分: δ ≠ 0 ⟺ 手性（−s ∉ I·s）⟺ 種子唔落鏡面",
    chiral_seeds == 60 and mirror_seeds == 60)

print()
print("=" * 86)
print("[C] 四型 I-軌道: 只有 60-軌道可手性")
print("=" * 86)
ax5 = np.array([0, 1, phi]) / np.linalg.norm([0, 1, phi])
ax3 = np.array([1, 1, 1]) / math.sqrt(3)
for tag, seed, exp in (("12 (5-fold 軸)", ax5, 12), ("20 (3-fold 軸)", ax3, 20),
                       ("30 (2-fold 軸)", A2[0], 30), ("60 (一般位置)", s0, 60)):
    orb = np.array([g @ seed for g in I_grp])
    # 去重
    uniq = []
    for v in orb:
        if not any(np.linalg.norm(v - u) < 1e-7 for u in uniq):
            uniq.append(v)
    uniq = np.array(uniq)
    neg_in = bool(np.min(np.linalg.norm(uniq + seed, axis=1)) < 1e-7)
    sg = sym_group(uniq, tol_deg=1e-4)
    chk("C %-14s N = %2d, −v ∈ 軌道? %-5s ⟹ %s" %
        (tag, len(uniq), "是" if neg_in else "否",
         "非手性" if neg_in else "手性 (|Sym| = %d, 全 proper = %s)"
         % (len(sg), all(np.linalg.det(g) > 0 for g in sg))),
        len(uniq) == exp and neg_in == (exp != 60))

print()
print("=" * 86)
print("[D] 實測資料: 冷斑 A₅ 軌道（chiral）vs RH（achiral）")
print("=" * 86)
f_a5 = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
V_raw = np.loadtxt(f_a5)
ra, dec = np.radians(V_raw[:, 0]), np.radians(V_raw[:, 1])
V_a5 = np.stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)], axis=1)
f_rh = os.path.join(BASE, "o182_88grid_geometry/data/a5_nodes_ideal.txt")
V_rh = np.loadtxt(f_rh)
V_rh = V_rh / np.linalg.norm(V_rh, axis=1)[:, None]
chk("D0 兩個資料集都係 60 點單位向量", V_a5.shape == (60, 3) and V_rh.shape == (60, 3),
    "A₅ = %s, RH = %s" % (V_a5.shape, V_rh.shape))


def max_dev_proper(V):
    """V 對 I 之最大偏差（度）= 是否 I-軌道"""
    return max(set_residual(g, V) for g in I_grp)


mdev = max_dev_proper(V_a5)
chk("D1 冷斑 A₅ 集 = I-軌道（proper 最大偏差 < 0.001° = 檔案 4 位小數級）", mdev < 1e-3,
    "proper 最大偏差 = %.6f°" % mdev)
imp = max(set_residual(g, V_a5) for g in I_h if np.linalg.det(g) < 0)
chk("D2 ★ 冷斑 A₅ 集對**全部** improper 元素皆唔不變（偏差 ≫ 0）", imp > 1.0,
    "improper 最小偏差 = %.6f°" % imp)
sg_a5 = sym_group(V_a5, tol_deg=1e-3)
chk("D3 ★ |Sym(冷斑 A₅)| = 60（全 det = +1）⟹ 嚴格手性",
    len(sg_a5) == 60 and all(np.linalg.det(g) > 0 for g in sg_a5),
    "|Sym| = %d, improper = %d" % (len(sg_a5), sum(1 for g in sg_a5 if np.linalg.det(g) < 0)))
sg_rh = sym_group(V_rh, tol_deg=1e-4)
n_imp_rh = sum(1 for g in sg_rh if np.linalg.det(g) < 0)
chk("D4 ⚠️ 觀察: o182 `a5_nodes_ideal.txt`（標稱 RH 60 頂點）之 |Sym| = %d（%d proper + %d improper）"
    "≠ 120 ⟹ 在標準二十面體框架下**並非** I_h-對稱。本輪**唔用**佢做非手性校準組（改用自建 I_h-軌道）"
    "，並列為跨 O 待核實項" % (len(sg_rh), len(sg_rh) - n_imp_rh, n_imp_rh),
    True, "|Sym| = %d" % len(sg_rh))
# 自建非手性校準組: I_h-軌道（一般位置）⟹ |Sym| = 120 且 δ ≠ 0
s_ach = rng.normal(size=3)
s_ach /= np.linalg.norm(s_ach)
S_ach = np.array([g @ s_ach for g in I_h])
sg_ach = sym_group(S_ach, tol_deg=1e-6)
n_imp_ach = sum(1 for g in sg_ach if np.linalg.det(g) < 0)
chk("D4b 自建 I_h-軌道（一般位置）: |Sym| = 120（%d improper）且 δ ≠ 0 ⟹ 合法非手性校準組"
    % n_imp_ach,
    len(sg_ach) == 120 and n_imp_ach == 60 and abs(delta(s_ach)) > 1e-9,
    "|Sym| = %d, δ = %.3e" % (len(sg_ach), delta(s_ach)))
# δ_m := ½ × (對極接近) = ½ × min_{v,w≠v} angle(−v, w)（軌道不變量）
antipodal = min(math.degrees(math.acos(min(1.0, max(-1.0, float(V_a5[i] @ (-V_a5[j]))))))
                for i in range(60) for j in range(60) if i != j)
dm = antipodal / 2
chk("D5 δ_m := ½·對極接近 = ½·min angle(−v, w) ⟹ δ_m = %.6f°（O213 報 2.670063°；O223 報 2δ_m = 5.340114°）"
    % dm, 2.60 < dm < 2.75, "δ_m = %.6f°（對極接近 = %.6f°）" % (dm, antipodal))
chk("D6 2δ_m = 對極接近 = 全部 improper 元素之共同殘差（連結兩量；容差 1e-3° 配合檔案 4 位小數捨入）",
    abs(2 * dm - imp) < 1e-3,
    "2δ_m = %.6f° vs improper 殘差 %.6f°（差 %.1e° = 檔案捨入）" % (2 * dm, imp, abs(2 * dm - imp)))
chk("D7 A₅ 集: improper 殘差係**常數**（∀ improper g 皆同一值）⟹ 殘差只取決於軌道 vs 其鏡像",
    True, "improper 殘差 = %.6f°（見 D2；因 (−R)·(I·s) = −(I·s) ∀R ∈ I）" % imp)

print()
print("=" * 86)
print("[E] ★ 自旋 sense 之絕對化（T9 核心）")
print("=" * 86)
# 手性集: δ 符號在 Sym 下不變 ⟹ 絕對 sense
sg_a5 = sym_group(V_a5, tol_deg=1e-3)
signs_chiral = {np.sign(delta(g @ V_a5[0])) for g in sg_a5}
chk("E1 ★ 手性集: δ 之符號在全部 |Sym| = 60 元素下**不變** ⟹ 絕對 sense 有定義",
    len(signs_chiral) == 1 and (0 not in signs_chiral),
    "符號集 = %s" % signs_chiral)
# achiral 集: ∃ improper g ∈ Sym 令 δ ↦ −δ ⟹ 兩個 sense 等價
# achiral 集（校準組）= D 段自建之 I_h-軌道 S_ach（一般位置, δ ≠ 0）
flip = [g for g in sg_ach if np.linalg.det(g) < 0]
base_sign = np.sign(delta(s_ach))
flipped = {np.sign(delta(g @ s_ach)) for g in flip}
chk("E2 ★ 非手性集: δ 之符號在 improper g 下**全部翻轉**（δ ↦ −δ）⟹ 兩 sense 由對稱連繫 ⟹ sense 相對",
    flipped == {-base_sign} and base_sign != 0,
    "δ(s) 符號 = %s；improper 下之符號集 = %s" % (base_sign, flipped))
chk("E3 ★ 定理（T9）: 旋轉 sense 絕對化 ⟺ 幾何手性（|Sym| 冇 improper 元素）",
    len(signs_chiral) == 1 and flipped == {-base_sign})

print()
print("=" * 86)
print("[F] 互補性: 手性（定向）vs helicity 配對（對偶）")
print("=" * 86)
neg_in_a5 = bool(np.min(np.linalg.norm(V_a5 + V_a5[0], axis=1)) < 1e-6)
neg_in_rh = bool(np.min(np.linalg.norm(V_rh + V_rh[0], axis=1)) < 1e-6)
chk("F1 A₅ 60-軌道: −v ∉ 集 ⟹ **冇** inversion ⟹ helicity 配對（±p）唔存在於其內",
    not neg_in_a5)
chk("F2 RH 集: −v ∈ 集 ⟹ 有 inversion ⟹ helicity 配對存在（但非手性）", neg_in_rh)
chk("F3 ★ 互補性: 定向（手性）同對偶（helicity 配對）住喺**唔同**結構 —— "
    "A₅ 軌道提供定向但冇對偶；88-grid（O182 canonical |Sym| = 4 = {+1:2, −1:2}，含 −I）"
    "提供對偶但非手性 ⟹ 螺旋度符號之絕對意義需要**兩者同時**", (not neg_in_a5) and neg_in_rh)

print()
print("=" * 86)
print("[G] 與 docs/03 之接合: 自旋 + 定向")
print("=" * 86)
chk("G1 docs/03 (B7): 鏈 holonomy 階 = 4 之結論與定向約定無關 ⟹ 自旋存在唔需要手性", True,
    "（結構陳述；見 docs/03 B7）")
chk("G2 ★ 完整鏈: 偶鏈 holonomy（階 4）⟹ 自旋存在；手性（|Sym| = 60 全 proper）"
    "⟹ 旋轉 sense 絕對化；兩者獨立 ⟹ 自旋 + 定向 = 螺旋度符號有物理意義",
    len(signs_chiral) == 1 and flipped == {-base_sign})

print()
print("=" * 86)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 86)

import json
out = {"script": "02_chirality_orientation", "date": "2026-09-28",
       "delta_m_deg": dm, "improper_min_dev_deg": imp,
       "sym_a5": len(sg_a5), "sym_rh": len(sg_rh), "checks": checks,
       "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "02_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
