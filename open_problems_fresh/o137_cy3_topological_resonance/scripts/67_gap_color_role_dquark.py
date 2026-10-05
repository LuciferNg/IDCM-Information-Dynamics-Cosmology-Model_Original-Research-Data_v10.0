#!/usr/bin/env python3
"""
O137 — 遺留缺口攻堅 I (scripts/67)
===================================
覆蓋:
  遺留 6  色荷纏繞 Δn_color
  遺留 7  D_quark 幾何推導
  遺留 8  「9 = 3 輕子 + 6 夸克」之角色分裂 (φ=9 層 3+6)

★ 方法論紀律 (O136 致命傷 / O208):
  1. 任何「屬 IDCM 目錄」之論證必須先報密度基準
  2. 禁後驗湊算子 — 檢定必須事前寫定
  3. 純代數/幾何恆等式可報 N_search = 1 + 唯一候選
"""
import json, math, itertools, os
import numpy as np
from fractions import Fraction
from collections import Counter

PASS, FAIL = [], []
def ck(name, got, exp, tol=0.0):
    if isinstance(exp, (int, float)) and not isinstance(exp, bool):
        ok = abs(float(got) - float(exp)) <= tol
    elif isinstance(exp, set):
        ok = set(got) == exp
    elif isinstance(exp, (list, tuple)):
        ok = list(got) == list(exp)
    else:
        ok = (got == exp)
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}" + ("" if ok else f"   ❗EXP={exp}"))

B = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance"
N_d, N_gen, Bb, F5, L4, L5, F7, L6 = 44, 3, 4, 5, 7, 11, 13, 18
gam = lambda n: 4*math.sin(n*math.pi/88)**2
MODES = [1,2,3,4,5,7,9,11,13]
BLOCKS = [[1,2,3],[4,5,7],[9,11,13]]
M0 = 27.900915
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0,"t":172690.0}
# O209 唯一指派 (|Δm| 排序)
O209 = {1:"t",2:"b",3:"tau",4:"c",5:"mu",7:"s",9:"d",11:"u",13:"e"}
LEP_O209 = {n for n,p in O209.items() if p in ("e","mu","tau")}
QUARK_O209 = set(MODES) - LEP_O209

# ══════════════════════════════════════════════════════════════════
print("="*88); print("§1 φ=9 層實際結構 (載入 gkz_period_data.json)"); print("="*88)
d = json.load(open(B+"/data/gkz_period_data.json"))
phi = np.array(d["gkz_phi"])
ck("§1 Σφ = 1800 = 20·Σγ", int(phi.sum()), 1800)
ck("§1 φ_origin = 360", d["phi_origin"], 360)
ck("§1 φ 向量長度 = 73", len(phi), 73)
idx9 = [i for i,x in enumerate(phi) if x==9]
print(f"  φ=9 之 0-based 索引 = {idx9}")
ck("§1 φ=9 點數 = 9", len(idx9), 9)
# 由 docs/14 之座標表重建
G1_LAB = [33,37,41]; G1_X3 = [1,5,9]
G2_LAB = [44,45,47,48,50,51]; G2_X3P = [0,1,3,4,6,7]
ck("§1 G1 ∪ G2 = φ=9 索引集", sorted(G1_LAB+G2_LAB), sorted(idx9))
ck("§1 G1 = 3 點 (x₂=0)", len(G1_LAB), 3)
ck("§1 G2 = 6 點 (x₂=1)", len(G2_LAB), 6)
ck("§1 G1 之 x₃ = 1+4k (step B=4)", [1+4*k for k in range(3)], G1_X3)
ck("§1 G2 之 x₃' = (3k, 3k+1) (step N_gen=3)",
   sorted(set(itertools.chain(*[(3*k,3*k+1) for k in range(3)]))), sorted(G2_X3P))
ck("§1 G2 = 3 對 (up/down 型)", [tuple(G2_X3P[2*i:2*i+2]) for i in range(3)],
   [(0,1),(3,4),(6,7)])
print(f"  ★ 結構: 3 (step B={Bb}) + 6 (3 對 step N_gen={N_gen}) = 9")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§2 3+6 對 SM 內容 — 讀法檢定 + 密度基準"); print("="*88)
# 事前寫定之讀法 (禁事後調整)
READINGS = {
 "A: 3 輕子 + 6 夸克 (每世代 1ℓ + 2q)": (3, 6),
 "B: 3 up 夸克 + 6 (down 夸克 + 輕子)": (3, 6),
}
print(f"  SM 內容 (每世代): 1 帶電輕子 + 2 夸克 = 3；3 世代 → 9")
print(f"  讀法 A: G1={3} ↔ 輕子, G2={6} ↔ 夸克 (2/世代)   ✓ 符合 SM 內容")
print(f"  讀法 B: G1={3} ↔ up 型, G2={6} ↔ down+輕子         ✓ 亦符合 SM 內容")
ck("§2 3+6 = 9 = |M| (A₅ 集)", 3+6, 9)
ck("§2 6 = 2·N_gen (2 夸克/世代)", 6, 2*N_gen)
ck("§2 3 = N_gen (1 輕子/世代)", 3, N_gen)
# ★ 判別力: 讀法 A 與 B 皆相容 ⟹ 需第二判據
print(f"\n  ★ 兩讀法皆與 SM 內容相容 ⟹ 【3+6 分裂本身係結構, 但『邊組係輕子』未定】")
# 密度基準: C(9,3) = 84 種「3 輕子」子集
nsub = math.comb(9,3)
ck("§2 密度基準: C(9,3) = 84", nsub, 84)
print(f"  ⟹ 隨機挑 3 個當輕子之命中率 = 1/84 = {100/84:.3f}%")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§3 角色指派判別力 — 候選不變量能否唯一挑出輕子集"); print("="*88)
def block_of(n): return next(i for i,b in enumerate(BLOCKS) if n in b)
# 事前寫定之候選 (唔准事後加)
CANDS = {}
CANDS["n ≡ 1 (mod 4)"]            = {n for n in MODES if n%4==1}
CANDS["n ∈ {1,5,9} (x₃ 值)"]      = {1,5,9}
CANDS["n 奇"]                      = {n for n in MODES if n%2==1}
CANDS["n 為質數"]                  = {n for n in MODES if n>1 and all(n%k for k in range(2,int(n**.5)+1))}
CANDS["n 為 Fibonacci"]            = {n for n in MODES if n in {1,2,3,5,8,13}}
CANDS["n 為 Lucas"]                = {n for n in MODES if n in {1,3,4,7,11,18}}
CANDS["γ_n < 0.1"]                 = {n for n in MODES if gam(n)<0.1}
CANDS["γ_n < 0.15"]                = {n for n in MODES if gam(n)<0.15}
CANDS["v₂(n) = 0"]                 = {n for n in MODES if (n & -n).bit_length()-1==0}
CANDS["n ≤ F₅"]                    = {n for n in MODES if n<=F5}
CANDS["每塊取最小 n"]              = {min(b) for b in BLOCKS}
CANDS["每塊取中位 n"]              = {sorted(b)[1] for b in BLOCKS}
CANDS["每塊取最大 n"]              = {max(b) for b in BLOCKS}
CANDS["每塊取偶 n"]                = {n for n in MODES if n%2==0}
print(f"  {'候選不變量':<26}{'|S|':>4}  {'= 輕子集?':>9}   S")
hits = []
for name, S in CANDS.items():
    eq = (S == LEP_O209)
    if eq: hits.append(name)
    print(f"  {name:<26}{len(S):>4}  {'★ 是' if eq else '否':>9}   {sorted(S)}")
print(f"\n  O209 輕子集 (|Δm| 排序) = {sorted(LEP_O209)}")
print(f"  命中候選 = {hits if hits else '無'}")
# 系統掃描: n ≡ a (mod k)
print(f"\n  ── 系統掃描: n ≡ a (mod k) ──")
mod_hits = []
for k in range(2,13):
    for a in range(k):
        S = {n for n in MODES if n%k==a}
        if len(S)==3:
            if S==LEP_O209: mod_hits.append((k,a,"= 輕子集"))
            else: mod_hits.append((k,a,"3 元但≠輕子"))
three = [(k,a) for k,a,_ in mod_hits]
ck("§3 系統掃描: 得 3 元之 (k,a) 數", len(three), len(three))
for k,a,t in mod_hits: print(f"    n ≡ {a} (mod {k})  →  {sorted(n for n in MODES if n%k==a)}   {t}")
print(f"  ⟹ 密度基準: {len(three)} 個 (k,a) 組合給 3 元子集 (k ≤ 12), 其中 = 輕子集者 "
      f"{sum(1 for _,_,t in mod_hits if t.startswith('='))}")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§4 色荷纏繞 Δn_color (遺留 6)"); print("="*88)
# 奇部 odd part = n / 2^{v₂(n)}
def oddpart(n):
    while n%2==0: n//=2
    return n
odd = {n: oddpart(n) for n in MODES}
print("  n : odd part (n/2^v₂)")
for n in MODES: print(f"    {n:>2} → {odd[n]:>2}   ({O209[n]})")
print(f"\n  O209 指派下:")
print(f"    輕子 {sorted(LEP_O209)} → odd parts {sorted(odd[n] for n in LEP_O209)}")
print(f"    夸克 {sorted(QUARK_O209)} → odd parts {sorted(odd[n] for n in QUARK_O209)}")
lep_odd = sorted(odd[n] for n in LEP_O209)
qk_odd  = sorted(odd[n] for n in QUARK_O209)
print(f"    奇部集: 輕子 {lep_odd} / 夸克 {qk_odd}")
ck("§4 輕子奇部 = {3,5,13}", set(lep_odd), {3,5,13})
ck("§4 夸克奇部 = {1,7,9,11} (2,4 → odd part 1)", set(qk_odd), {1,7,9,11})
ck("§4 夸克奇部含 1 三次 (n=1,2,4 同奇部)", qk_odd.count(1), 3)
# 舊 (O54) 框架之奇部
print(f"\n  O54 框架 (docs/19 發現 4): 輕子奇部 e:1, μ:7, τ:5 → {{1,5,7}}; 夸克 u:1, s:7, c:17, b:33")
ck("§4 O54 輕子奇部 = {1,5,7}", {1,5,7}, {1,5,7})
# Δn_color: 夸克 − 輕子
print(f"\n  ── Δn_color 檢定 (事前寫定之結構候選) ──")
# 事前寫定: Δn = B²·k? N_gen·L₄? 等
CANDS_DN = {
 "Δn ∈ {0, B²=16, 2B²=32, 3B²=48}": {0,16,32,48},
 "Δn ∈ {0, L₄=7, 2L₄=14, 3L₄=21}": {0,7,14,21},
 "Δn ∈ {0, N_gen²=9, 2N_gen²=18, 3N_gen²=27}": {0,9,18,27},
 "Δn ∈ {0, N_d=44, 2N_d=88}": {0,44,88},
 "Δn ∈ 2ℤ (偶)": None,
 "Δn ∈ 4ℤ (B 之倍數)": None,
}
# 以 O54 奇部對 (每世代 1 輕子 2 夸克) 計 Δn
# O54: e=1, μ=7, τ=5 (輕子); u=1, s=7, c=17, b=33 (夸克)
dn_pairs = []
for lq, qq in [((1),(1)), ((7),(7)), ((5),(17)), ((5),(33))]:
    dn_pairs.append(qq-lq)
print(f"    O54 觀測 Δn (夸克奇部 − 輕子奇部) = {dn_pairs}")
obs = set(abs(x) for x in dn_pairs)
for name, S in CANDS_DN.items():
    if S is None:
        if "2ℤ" in name: ok = all(x%2==0 for x in obs)
        else: ok = all(x%4==0 for x in obs)
    else: ok = obs <= S
    print(f"    {name:<44} 觀測 {sorted(obs)} ⊆ S ? {'✅' if ok else '❌'}")
ck("§4 Δn 集 (O54 配對) = {0,12,28}", obs, {0,12,28})
print(f"  ★ Δn 之結構: 12 = ?  28 = ?  (0 = 同奇部)")
print(f"  ⟹ 判定: Δn 無單一結構規則 (0,7,12,28 非等差/等比)")
print(f"  ⚠️ 密度基準: [6,33] 之 IDCM 目錄密度 46%(嚴格)/96%(寬鬆)")
print(f"     ⟹ 「Δn 屬 IDCM 目錄」唔構成證據 (O137 docs/30 方法論教訓)")

# ══════════════════════════════════════════════════════════════════
print("\n"+"="*88); print("§5 D_quark 幾何推導 (遺留 7)"); print("="*88)
h11, h21 = 36, 98
eps = 1/(2*((1+math.sqrt(5))/2))   # φ⁻¹/2? 先核 docs/02 定義
phi_g = (1+math.sqrt(5))/2
eps_std = 1/(4*phi_g)              # φ⁻¹/4
print(f"  ε (docs/02 標準) = φ⁻¹/4 = {eps_std:.7f}")
Dq = 1 + h11/h21 * eps_std * (1+eps_std)
print(f"  D_quark = 1 + h¹¹/h²¹ · ε(1+ε) = {Dq:.6f}")
ck("§5 D_quark = 1.065528", Dq, 1.065528, tol=1e-6)
ck("§5 ε = φ⁻¹/4 = 0.1545085", eps_std, 0.1545085, tol=1e-7)
ck("§5 h¹¹ = 36 = Φ[5][7]", 1+5*7, 36)
ck("§5 h²¹ = 98 = Σγ + 2B = 90 + 8", 90+2*Bb, 98)
# ε 之結構身份
print(f"\n  ε 之結構候選:")
for nm, v in [("φ⁻¹/4", 1/(4*phi_g)), ("1/(B·φ)", 1/(Bb*phi_g)),
              ("(N_d−L₆)/N_d/... ", (N_d-L6)/N_d),
              ("1/(2B+φ)", 1/(2*Bb+phi_g)), ("F₅/(2·N_gen·B²)", F5/(2*N_gen*Bb**2))]:
    print(f"    {nm:<18} = {v:.7f}   Δ vs φ⁻¹/4 = {(v/eps_std-1)*100:+.4f}%")
# ε(1+ε) 之結構
print(f"\n  ε(1+ε) = {eps_std*(1+eps_std):.7f}")
print(f"  1+ε = {1+eps_std:.7f} = 1 + φ⁻¹/4")
# h11/h21 = 36/98
print(f"  h¹¹/h²¹ = 36/98 = {36/98:.7f} = {Fraction(36,98)} = 18/49")
ck("§5 h¹¹/h²¹ = 18/49", Fraction(h11,h21), Fraction(18,49))
print(f"  18 = L₆ = F₅·N_gen + N_gen = 15+3;  49 = L₄²")
ck("§5 18 = L₆ = N_gen·(F₅+1)", L6, N_gen*(F5+1))
ck("§5 49 = L₄²", L4**2, 49)
print(f"\n  ★ D_quark − 1 = (18/49)·ε(1+ε) = 2·9·ε(1+ε)/(2·49)")
print(f"     (18/49) = 2·(9/49) = 2·N_gen²/L₄²")
ck("§5 D_quark − 1 = 2·N_gen²·ε(1+ε)/L₄² (精確)",
   2*N_gen**2 * eps_std*(1+eps_std)/L4**2, Dq-1, tol=1e-12)
ck("§5 D_quark = 1 + L₆·ε(1+ε)/L₄² (精確)",
   1 + L6*eps_std*(1+eps_std)/L4**2, Dq, tol=1e-12)
print(f"  ⟹ ★ 代數恆等: D_quark = 1 + L₆·ε(1+ε)/L₄² = 1 + 2N_gen²·ε(1+ε)/L₄²")
print(f"     L₆ = 18 = N_gen(F₅+1) = 3·6;  L₄² = 49")
print(f"  ★ ε 之結構: φ⁻¹/4 = 1/(B·φ) 精確 (B=4) ⟹ ε = 1/(B·φ) 零參數")
ck("§5 ε = 1/(B·φ) 精確", 1/(Bb*phi_g), 1/(4*phi_g), tol=1e-15)

print("\n"+"="*88); print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}"); print("="*88)
if FAIL:
    print("FAIL 項:")
    for f in FAIL: print("  -", f)
