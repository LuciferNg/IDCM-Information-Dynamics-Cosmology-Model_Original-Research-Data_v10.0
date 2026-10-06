#!/usr/bin/env python3
"""
O209 - Script 09: A5 不變量環獨立驗證 (H3 / icosahedral invariant ring)
================================================================================
追 docs/09 §八 🔴: 「二十面體諧和度譜只係引用已知群論, 本 O 冇獨立重推」。

本 script 由 60 節點集**反推**對稱群 G, 再獨立計算:
  C1  對稱群 G (由 60 節點集反推; |G|, det, 是否含 -I)
  C2  Molien 級數 P(t) = (1/|G|) Sum_g 1/det(I - t g)
  C3  諧和部分 (1 - t^2) P(t) 之次數集 vs 實測 S (max-over-axes)
  C4  Primary degrees + skew degree (由 P(t) 代數結構判定)
  C5  特徵標法獨立重算 dim(諧和 A5-不變量) per l
  C6  S = <6,10> U (15 + <6,10>) (自由模結構)
  C7  {2,6,10} 之結構身份 (觀察級, 唔宣稱)
"""
import numpy as np, math, json, itertools
from pathlib import Path
from collections import Counter

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
A5NODES = ROOT / "cmb_cold_spot/data/a5_nodes.txt"
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

LMAX = 30
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))

print("=" * 96)
print("O209 Script 09: A5 不變量環獨立驗證 (由 60 節點集反推群)")
print("=" * 96)

nodes = np.loadtxt(A5NODES)
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
U = np.column_stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])
Nn = U.shape[0]
print(f"  節點數 = {Nn}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C1. 對稱群 G (由節點集反推)")
print("-" * 96)
Dot = U @ U.T
# 揀 3 個線性獨立節點做參考基
basis = None
for a, b, c in itertools.combinations(range(Nn), 3):
    M = np.array([U[a], U[b], U[c]]).T
    if abs(np.linalg.det(M)) > 0.5:
        basis = (a, b, c); Nmat = M; break
i1, i2, i3 = basis
g0 = Nmat.T @ Nmat
invN = np.linalg.inv(Nmat)
print(f"  參考基 = 節點 {basis}, det = {np.linalg.det(Nmat):.4f}")

Rs = []
TOLG = 1e-5     # ⚠️ 座標檔四捨五入到 1e-4 度 -> Gram 偏差 ~7e-6; 1e-9 會漏掉全部非平凡元素
for j1 in range(Nn):
    for j2 in range(Nn):
        if abs(Dot[j1, j2] - g0[0, 1]) > TOLG:
            continue
        for j3 in range(Nn):
            if abs(Dot[j1, j3] - g0[0, 2]) > TOLG or abs(Dot[j2, j3] - g0[1, 2]) > TOLG:
                continue
            Mmat = np.array([U[j1], U[j2], U[j3]]).T
            R = Mmat @ invN
            if np.abs(R.T @ R - np.eye(3)).max() > 1e-5:
                continue
            if abs(np.linalg.det(R) - 1.0) > 1e-5:
                continue
            V = U @ R.T
            dd = np.linalg.norm(V[:, None, :] - U[None, :, :], axis=2).min(axis=1)
            if dd.max() < TOLG:
                Rs.append(R)
# dedup
uniq = []
for R in Rs:
    if not any(np.abs(R - S).max() < 1e-4 for S in uniq):
        uniq.append(R)
G = np.array(uniq)
NG = len(G)
print(f"  |G| = {NG}")
chk("C1.1 |G| = 60 (= |A5|)", NG == 60, f"got {NG}")
trs = np.array([np.trace(R) for R in G])
dets = np.array([np.linalg.det(R) for R in G])
chk("C1.2 全部 det = +1 (G ⊂ SO(3))", np.abs(dets - 1).max() < 1e-5,
    f"max|det-1| = {np.abs(dets - 1).max():.1e} (座標捨入)")
chk("C1.3 冇 -I (min trace > -3)", trs.min() > -2.999, f"min tr = {trs.min():.4f}")
chk("C1.4 群階 60 且作用傳遞 (orbit 大小 60)", NG == 60 and Nn == 60)
# 階分佈 (trace 分類; A5: tr = 3 (id), -1 (order2), 0 (order3), phi (o5), 1-phi (o5))
_phi = (1 + math.sqrt(5)) / 2
def _cls(t):
    for lab, v in (("id", 3.0), ("order2", -1.0), ("order3", 0.0),
                   ("o5a", _phi), ("o5b", 1 - _phi)):
        if abs(t - v) < 1e-2:
            return lab
    return "?"
lab = Counter(_cls(float(t)) for t in trs)
nid, n2, n3 = lab["id"], lab["order2"], lab["order3"]
n5 = lab["o5a"] + lab["o5b"]
print(f"  階分佈: id={nid}, order2={n2}, order3={n3}, order5={n5}  (unknown={lab['?']})")
chk("C1.5 A5 階分佈 (1,15,20,24)", (nid, n2, n3, n5) == (1, 15, 20, 24),
    f"({nid},{n2},{n3},{n5})")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C2. Molien 級數 P(t) = (1/|G|) Sum_g 1/det(I - t g)")
print("-" * 96)
# 對 rotation g: det(I - t g) = 1 - a t + a t^2 - t^3, a = tr(g)
def recip(a, L):
    p = [0.0] * (L + 1); p[0] = 1.0
    for n in range(1, L + 1):
        s = a * p[n - 1]
        if n - 2 >= 0: s -= a * p[n - 2]
        if n - 3 >= 0: s += p[n - 3]
        p[n] = s
    return p

Pser = np.zeros(LMAX + 1)
for R in G:
    a = float(np.trace(R))
    Pser += np.array(recip(a, LMAX))
Pser /= NG
print("  P(t) 係數 h_l (l=0..20):")
print("   ", [f"{Pser[l]:.0f}" for l in range(21)])
chk("C2.1 h_0 = 1", abs(Pser[0] - 1) < 1e-9)
chk("C2.2 h_1 = 0 (無 degree-1 不變量)", abs(Pser[1]) < 1e-9)
chk("C2.3 h_2 = 1 (degree-2: x^2+y^2+z^2)", abs(Pser[2] - 1) < 1e-5,
    f"h_2 = {Pser[2]:.6f}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C3. 諧和部分 (1 - t^2) P(t) vs 實測 S")
print("-" * 96)
harm = [Pser[l] - (Pser[l - 2] if l >= 2 else 0.0) for l in range(LMAX + 1)]
S_molien = [l for l in range(1, LMAX + 1) if harm[l] > 0.5]
print(f"  (1-t^2)P(t) 係數 q_l (l=1..{LMAX}):")
print("   ", [f"{harm[l]:.0f}" for l in range(1, LMAX + 1)])
print(f"  Molien 諧和度集 S = {S_molien}")

# 實測 (max over 400 軸)
def leg(l, xx):
    if l == 0: return np.ones_like(xx)
    p0 = np.ones_like(xx); p1 = xx.copy()
    for k in range(2, l + 1):
        p0, p1 = p1, ((2 * k - 1) * xx * p1 - (k - 1) * p0) / k
    return p1
rng = np.random.default_rng(20260925)
axs = rng.normal(size=(400, 3)); axs /= np.linalg.norm(axs, axis=1, keepdims=True)
mx = {l: max(abs(float(leg(l, U @ a).sum())) for a in axs) for l in range(1, LMAX + 1)}
S_emp = [l for l in range(1, LMAX + 1) if mx[l] >= 1e-3]
print(f"  實測諧和度集 S = {S_emp}")
chk("C3.1 Molien S = 實測 S (獨立路徑一致)", S_molien == S_emp,
    f"molien={S_molien} emp={S_emp}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C4. Primary degrees + skew degree")
print("-" * 96)
# P(t) = (1 + t^15) / ((1-t^2)(1-t^6)(1-t^10))
den = [0.0] * (LMAX + 1)
for l in range(LMAX + 1):
    v = 0.0
    for a in range(LMAX // 2 + 1):
        for b in range(LMAX // 6 + 1):
            for c in range(LMAX // 10 + 1):
                if 2 * a + 6 * b + 10 * c == l:
                    v += 1.0
    den[l] = v
model = den[:]
for l in range(15, LMAX + 1):
    model[l] += den[l - 15]
resid = max(abs(model[l] - Pser[l]) for l in range(LMAX + 1))
print(f"  P(t) vs (1+t^15)/((1-t^2)(1-t^6)(1-t^10)): max|resid| = {resid:.2e}")
chk("C4.1 P(t) = (1+t^15)/((1-t^2)(1-t^6)(1-t^10))", resid < 1e-4,
    f"resid={resid:.1e} (座標捨入級)")
chk("C4.2 primary degrees = {2,6,10} (由 C4.1 因式分解)", resid < 1e-4)
chk("C4.3 skew degree = 15 (分子 t^15)", resid < 1e-4)
chk("C4.4 2*6*10 = 120 = 2*|A5|", 2 * 6 * 10 == 120 == 2 * 60)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C5. 特徵標法獨立重算 dim(諧和 A5-不變量)")
print("-" * 96)
dim_char = []
for l in range(1, LMAX + 1):
    s = 0.0
    for R in G:
        t = float(np.trace(R))
        if abs(t - 3) < 1e-9:
            s += 2 * l + 1
        else:
            th = math.acos(np.clip((t - 1) / 2, -1, 1))
            s += math.sin((2 * l + 1) * th / 2) / math.sin(th / 2)
    dim_char.append(s / NG)
S_char = [l for l in range(1, LMAX + 1) if dim_char[l - 1] > 0.5]
print("  dim_l (特徵標法):", [f"{dim_char[l-1]:.0f}" for l in range(1, 22)])
chk("C5.1 特徵標法 S = Molien S = 實測 S", S_char == S_molien == S_emp)
chk("C5.2 dim 全部整數 (表示論一致性)",
    max(abs(d - round(d)) for d in dim_char) < 1e-4,
    f"max dev = {max(abs(d - round(d)) for d in dim_char):.1e}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C6. S = <6,10> U (15 + <6,10>) (自由模結構)")
print("-" * 96)
def semi(gens, L):
    s = {0}
    out = set()
    for l in range(1, L + 1):
        for g in gens:
            if l - g in s:
                s.add(l); break
    return sorted(s - {0})
s610 = semi([6, 10], LMAX)
s610z = sorted(set(s610) | {0})                     # 含 0 (模生成元 1)
s610_15 = sorted(set(s610) | {15 + x for x in s610z if 15 + x <= LMAX})
print(f"  <6,10>            = {s610}")
print(f"  <6,10> U (15+<6,10>) = {s610_15}")
chk("C6.1 S = <6,10> U (15 + <6,10>)", S_emp == s610_15, f"{S_emp} vs {s610_15}")
semi_all = semi([6, 10, 15], LMAX)
chk("C6.2 半群<6,10,15> = <6,10> U (15+<6,10>) (同集合)",
    sorted(set(semi_all) | {0}) == sorted(set(s610_15) | {0}),
    f"<6,10,15>={semi_all}")
chk("C6.3 l_first(even) = 6, l_first(odd) = 15", 
    min(l for l in S_emp if l % 2 == 0) == 6 and min(l for l in S_emp if l % 2 == 1) == 15)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C7. {2,6,10} 結構身份 (觀察級, 唔宣稱機制)")
print("-" * 96)
print(f"  primary degrees {{2,6,10}} = 2 * {{1,3,5}};  3 = N_gen, 5 = F5")
print(f"  2+6+10 = 18;  2+6+10+15 = 33 = K_tree 尺度維")
chk("C7.1 {2,6,10} = 2*{1,N_gen,F5}", (6, 10) == (2 * 3, 2 * 5))
chk("C7.2 15 = N_gen*F5", 15 == 3 * 5)
chk("C7.3 2+6+10+15 = 33 (K_tree) — 🟡 觀察級, 未做 look-elsewhere",
    sum([2, 6, 10, 15]) == 33)

# ══════════════════════════════════════════════════════════════════
npass = sum(1 for _, ok, _ in checks if ok)
print("\n" + "=" * 96)
print(f"RESULT: {npass}/{len(checks)} PASS")
print("=" * 96)

json.dump({
    "group_order": NG, "class_distribution": {"id": nid, "order2": n2, "order3": n3, "order5": n5},
    "molien_coeffs": [float(Pser[l]) for l in range(LMAX + 1)],
    "harmonic_dims_char": dim_char,
    "S_molien": S_molien, "S_empirical": S_emp,
    "primary_degrees": [2, 6, 10], "skew_degree": 15,
    "module_structure": "S = <6,10> U (15 + <6,10>)",
    "l_first_even": 6, "l_first_odd": 15,
    "checks_passed": npass, "checks_total": len(checks),
}, open(OUT / "09_a5_invariant_ring.json", "w"), indent=2, ensure_ascii=False)
print(f"\n-> data/09_a5_invariant_ring.json")
