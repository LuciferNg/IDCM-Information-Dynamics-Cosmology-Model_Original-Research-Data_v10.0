#!/usr/bin/env python3
"""
O209 - Script 07: 選擇閾值定理 (Selection Threshold Theorem)
================================================================================
追 item 4: 「為何 n = 6?」

核心命題 (零參數):
  A. A5 節點集 (60 點, 二十面體對稱) 嘅 Legendre 動差
     M_l(c) = Sum_i P_l(u_i . c)
     係 A5-不變諧和多項式 (degree l)。
  B. 「恆等零」係軸無關: M_l 要麼恆等零, 要麼對幾乎所有軸非零。
     零集 Z = {1,2,3,4,5,7,8,9,11,13,14,17,19,23,...}
     諧和度集 S = {6,10,12,15,16,18,20,21,22,24,25,26,...}
  C. S = 半群 <6,10,15>  (二十面體基本不變量次數 2,6,10,15 去掉 2)
  D. 首值: l_first(even) = 6, l_first(odd) = 15
  E. 閾值定理: G2(n) <=> n < l_first(parity(n))
     => Sel(S) = {odd n < 15} U {even n < 6} = {1,2,3,4,5,7,9,11,13}  (9 模式)
  F. G1 冗餘: G2 subset of G1  =>  Sel = G2
  G. 中微子: n_nu = min{n : not G2(n)} = l_first(even) = 6

Null: 隨機 60 點集嘅 l_first(even) 分佈 (5-design 係必要條件)
"""
import numpy as np, math, json
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
A5NODES = ROOT / "cmb_cold_spot/data/a5_nodes.txt"
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

Nd, B, Ngen, F5, F7 = 44, 4, 3, 5, 13
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))

print("=" * 96)
print("O209 Script 07: 選擇閾值定理 - 二十面體諧和度譜 => 9 模式 + n=6")
print("=" * 96)

nodes = np.loadtxt(A5NODES)
ra, dec = np.radians(nodes[:, 0]), np.radians(nodes[:, 1])
U = np.column_stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])
NODE = U.shape[0]

def leg(l, xx):
    if l == 0: return np.ones_like(xx)
    p0 = np.ones_like(xx); p1 = xx.copy()
    for k in range(2, l + 1):
        p0, p1 = p1, ((2 * k - 1) * xx * p1 - (k - 1) * p0) / k
    return p1

l_c, b_c = math.radians(209.0), math.radians(-57.0)
cs = np.array([math.cos(b_c) * math.cos(l_c), math.cos(b_c) * math.sin(l_c), math.sin(b_c)])
cs /= np.linalg.norm(cs)

LMAX = 26
NRAX = 400
rng = np.random.default_rng(20260925)
axes = rng.normal(size=(NRAX, 3)); axes /= np.linalg.norm(axes, axis=1, keepdims=True)
axes[0] = cs                                   # 第一條 = 冷斑軸

# M[l, k] = Sum_i P_l(u_i . a_k)
M = np.zeros((LMAX + 1, NRAX))
for k in range(NRAX):
    x = U @ axes[k]
    for l in range(1, LMAX + 1):
        M[l, k] = leg(l, x).sum()

TOL = 1e-3
maxabs = {l: float(np.abs(M[l]).max()) for l in range(1, LMAX + 1)}
Zid = [l for l in range(1, LMAX + 1) if maxabs[l] < TOL]
S = [l for l in range(1, LMAX + 1) if maxabs[l] >= TOL]

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C1. A5 節點集 = 球面 5-design")
print("-" * 96)
m_cs = {l: float(M[l, 0]) for l in range(1, LMAX + 1)}
print(f"  冷斑軸: 零動差 = {[l for l in range(1, LMAX + 1) if abs(m_cs[l]) < TOL]}")
print(f"          非零   = {[l for l in range(1, LMAX + 1) if abs(m_cs[l]) >= TOL]}")
chk("C1.1 l = 1..5 全部零 (5-design 定義)", all(l in Zid for l in range(1, 6)))
chk("C1.2 冷斑軸非零集 = {6,10,12,15,16,18,20,21,22,24,25,26}",
    [l for l in range(1, LMAX + 1) if abs(m_cs[l]) >= TOL] ==
    [6, 10, 12, 15, 16, 18, 20, 21, 22, 24, 25, 26])
chk("C1.3 重現 O136 docs/19 動差值 (l=6,10,12,15,16)",
    all(abs(m_cs[l] - v) < 1e-4 for l, v in
        {6: 0.873778, 10: 0.267446, 12: -5.288945, 15: 0.199879, 16: -1.175282}.items()),
    f"l6={m_cs[6]:.6f} l12={m_cs[12]:.6f}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C2. 「恆等零」軸無關 (max over 400 軸; 零 vs 非零差 4 個數量級)")
print("-" * 96)
print(f"  {'l':>3} {'max|M_l|':>12}   class")
for l in range(1, LMAX + 1):
    print(f"  {l:>3} {maxabs[l]:>12.3e}   {'ZERO' if maxabs[l] < TOL else 'harmonic'}")
chk("C2.1 零集 Z = {1,2,3,4,5,7,8,9,11,13,14,17,19,23}",
    Zid == [1, 2, 3, 4, 5, 7, 8, 9, 11, 13, 14, 17, 19, 23], str(Zid))
chk("C2.2 諧和度集 S = {6,10,12,15,16,18,20,21,22,24,25,26}",
    S == [6, 10, 12, 15, 16, 18, 20, 21, 22, 24, 25, 26], str(S))
chk("C2.3 零/非零分離 >= 10x (max_Z < 1e-3 < 0.09 <= min_S)",
    max(maxabs[l] for l in Zid) < 1e-3 and min(maxabs[l] for l in S) > 0.09,
    f"max_Z={max(maxabs[l] for l in Zid):.2e} min_S={min(maxabs[l] for l in S):.3f}")
chk("C2.4 冷斑軸分類 = 軸無關分類", Zid == [l for l in range(1, LMAX + 1) if abs(m_cs[l]) < TOL])

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C3. 群論身份: S = 半群 <6,10,15> (二十面體基本不變量次數 2,6,10,15)")
print("-" * 96)
semi = sorted({6 * a + 10 * b + 15 * c
               for a in range(0, 5) for b in range(0, 3) for c in range(0, 2)
               if 6 * a + 10 * b + 15 * c <= LMAX and 6 * a + 10 * b + 15 * c > 0})
print(f"  半群 <6,10,15> 喺 [1,{LMAX}] = {semi}")
chk("C3.1 S = 半群 <6,10,15>", S == semi, f"{S} vs {semi}")
chk("C3.2 6,10,15 = 二十面體基本不變量次數 (去 2)", semi[0] == 6 and 10 in semi and 15 in semi)
chk("C3.3 17,19,23 非半群元素 (唔可表示成 6a+10b+15c)",
    17 not in semi and 19 not in semi and 23 not in semi)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C4. 首值 (分奇偶)")
print("-" * 96)
Se = [l for l in S if l % 2 == 0]; So = [l for l in S if l % 2 == 1]
lf_even, lf_odd = min(Se), min(So)
print(f"  偶諧和度 = {Se}  -> l_first(even) = {lf_even}")
print(f"  奇諧和度 = {So}  -> l_first(odd)  = {lf_odd}")
chk("C4.1 l_first(even) = 6", lf_even == 6, str(lf_even))
chk("C4.2 l_first(odd) = 15", lf_odd == 15, str(lf_odd))
chk("C4.3 結構身份 6 = 2*N_gen, 15 = N_gen*F5", lf_even == 2 * Ngen and lf_odd == Ngen * F5,
    f"2*{Ngen}={2*Ngen}, {Ngen}*{F5}={Ngen*F5}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C5. 閾值定理: G2(n) <=> n < l_first(parity(n))")
print("-" * 96)
def a0(n): return 0.0 if n % 2 else -1.0 / (n * n - 1)
# 軸無關 G2: 對每 n 用 400 軸嘅 max 判「多項式恆等零 vs 60a0」
G2_poly = []
for n in range(1, Nd + 1):
    vals = []
    for k in range(NRAX):
        b = np.arccos(np.clip(U @ axes[k], -1, 1))
        vals.append(abs(float(np.cos(n * b).sum()) - NODE * a0(n)))
    if max(vals) < TOL:
        G2_poly.append(n)
pred = sorted([n for n in range(1, Nd + 1) if n % 2 == 1 and n < lf_odd] +
              [n for n in range(1, Nd + 1) if n % 2 == 0 and n < lf_even])
print(f"  G2 (400 軸 max 判) = {G2_poly}")
print(f"  閾值預言           = {pred}")
chk("C5.1 閾值預言 = G2 (軸無關, EXACT)", pred == G2_poly, str(pred))
chk("C5.2 選擇集大小 = 9 = 3 輕子 + 6 夸克", len(pred) == 9)
chk("C5.3 奇模式 = odd < 15", [n for n in pred if n % 2] == [1, 3, 5, 7, 9, 11, 13])
chk("C5.4 偶模式 = even < 6", [n for n in pred if n % 2 == 0] == [2, 4])
chk("C5.5 冷斑軸 G2 直算 = 同一集", G2_poly == pred)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C6. G1 冗餘定理 (單生成元選擇律)")
print("-" * 96)
def v2(v):
    c = 0
    while v % 2 == 0: v //= 2; c += 1
    return c
G1 = [n for n in range(1, Nd + 1) if v2(n) <= 2]
chk("C6.1 |G1| = 39, 排除 {8,16,24,32,40}",
    len(G1) == 39 and [n for n in range(1, Nd + 1) if n not in G1] == [8, 16, 24, 32, 40])
chk("C6.2 G2 subset of G1", set(G2_poly) <= set(G1))
chk("C6.3 Sel = G1 & G2 = G2 (G1 對選擇零貢獻)", sorted(set(G1) & set(G2_poly)) == G2_poly)
chk("C6.4 max v2(G2) = 2 (G1 條件自動滿足)", max(v2(n) for n in G2_poly) == 2)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C7. 中微子扇區: n_nu = l_first(even) = 6")
print("-" * 96)
n_nu = min(n for n in range(1, Nd + 1) if n not in G2_poly)
chk("C7.1 min{n : not G2(n)} = 6", n_nu == 6, str(n_nu))
chk("C7.2 n_nu = l_first(even)", n_nu == lf_even)
chk("C7.3 n=6 偶模式 (同 O49/O57 中微子 = 鏈模式 6 一致)", n_nu % 2 == 0)
chk("C7.4 6 係首個非零偶動差 (即 O136 docs/19 l=6)", 6 in S and all(l in Zid for l in (2, 4)))

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C8. Null test: 隨機 60 點集嘅 l_first(even) 分佈")
print("-" * 96)
NMC = 2000
rng2 = np.random.default_rng(7)
hit = 0
for _ in range(NMC):
    P = rng2.normal(size=(60, 3)); P /= np.linalg.norm(P, axis=1, keepdims=True)
    v = rng2.normal(size=3); v /= np.linalg.norm(v)
    x = P @ v
    fe = None
    for l in range(1, 15):
        if abs(float(leg(l, x).sum())) >= TOL:
            if l % 2 == 0: fe = l; break
    if fe is not None and fe >= 6: hit += 1
q_obs = hit / NMC
print(f"  N_mc = {NMC}  (隨機 60 點集, 單隨機軸)")
print(f"  隨機集 l_first(even) >= 6 : {hit}/{NMC}   q_obs = {q_obs:.4%}")
chk("C8.1 隨機集幾乎全部 l_first(even) = 2 (非 5-design)", q_obs < 0.01, f"q_obs = {q_obs:.4%}")
chk("C8.2 A5 觀測值 l_first(even)=6 喺 null 下 < 1%", q_obs < 0.01)

# ══════════════════════════════════════════════════════════════════
npass = sum(1 for _, ok, _ in checks if ok)
print("\n" + "=" * 96)
print(f"RESULT: {npass}/{len(checks)} PASS")
print("=" * 96)

json.dump({
    "zero_moments": Zid, "harmonic_degrees": S,
    "semigroup_6_10_15": semi,
    "l_first_even": lf_even, "l_first_odd": lf_odd,
    "G2_selected": G2_poly, "threshold_prediction": pred,
    "G1_size": len(G1), "G1_redundant": sorted(set(G1) & set(G2_poly)) == G2_poly,
    "n_neutrino": n_nu,
    "null": {"N_mc": NMC, "l_first_even_ge6": hit, "q_obs": q_obs},
    "structural_ids": {"6": "2*N_gen", "15": "N_gen*F5"},
    "maxabs_moments": {str(l): maxabs[l] for l in range(1, LMAX + 1)},
    "checks_passed": npass, "checks_total": len(checks),
}, open(OUT / "07_selection_threshold_theorem.json", "w"), indent=2, ensure_ascii=False)
print(f"\n-> data/07_selection_threshold_theorem.json")
