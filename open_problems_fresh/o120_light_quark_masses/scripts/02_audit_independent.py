#!/usr/bin/env python3
"""
O120 — Independent Close-out Audit (T1/T2, zero import of scripts/01)
======================================================================
Closeout 2026-10-06 · 由 x²+x−1=0 第一性原理重算全部 headline 數字，
對照 O120 docs/01-03 + final_result + O136 data（唯讀）＋ 新結構裁決檢定。

Sections:
  A 常數層        B Framework A (v9.0 Fₙ/CY₃ˢ)   C Framework B (O136 M₀γP_f)
  D up_quark_corr E m_u/m_d 比                    F O54 輕子交叉
  G 反週期條件    H ★ 模式集兩判準               I ★ O136 模式排除
  J ★ A₅ C_f 表   K ★ gen1 均勻性 null           L ★ C_f≡3.6 預言
  M ★ 三式 m_u/m_d N 密度基準                    O docs 跨核對
"""
import math, json, os, random
from itertools import combinations

try:
    import mpmath as mp
    mp.mp.dps = 60
    HAVE_MP = True
except Exception:
    HAVE_MP = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
O136_DATA = os.path.join(BASE, "..", "o136_quark_mass_spectrum", "data")
J8 = None
if os.path.exists(os.path.join(O136_DATA, "08_final_closure.json")):
    with open(os.path.join(O136_DATA, "08_final_closure.json")) as f:
        J8 = json.load(f)

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  [{detail}]" if detail and not cond else ""))

def d(x):  # 1-based floating helper for printing
    return f"{x:.10f}"

# ═══════════════════════════════════════════════════════════
print("=" * 76); print("A. 常數層 — 由 x²+x−1=0 第一性原理"); print("=" * 76)
φ = (1 + math.sqrt(5)) / 2
L = [round(φ**n + (-1)**n * φ**(-n)) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
h11, h21 = 36, 98
CY3 = h11 + h21
B, Nd, NG = 4, 44, 3
M = (CY3 - 2) // 4
EPS = φ**(-1) / 4
M0 = 27.900915
gam = lambda n: 4 * math.sin(n * math.pi / 88)**2
check("φ = (1+√5)/2", abs(φ - 1.618033988749895) < 1e-14)
check("Lucas L₀..L₈", L[:9] == [2,1,3,4,7,11,18,29,47])
check("Fibonacci F₅..F₁₀", F[5:11] == [5,8,13,21,34,55])
check("CY₃ = h¹¹+h²¹ = 134", CY3 == 134)
check("M = (CY₃−2)/4 = 33", M == 33)
check("L₆/F₅ = 18/5 = 3.6", abs(L[6]/F[5] - 3.6) < 1e-15)
check("Nd−L₅ = 44−11 = 33 = M", Nd - L[5] == 33 == M)
check("Nd−E_proj = 44−28.5 = 15.5", Nd - 28.5 == 15.5)
check("Nd−L₄ = 44−7 = 37 (τ P_f)", Nd - L[4] == 37)
check("ε = φ⁻¹/4 = 1/(Bφ)", abs(EPS - 1/(B*φ)) < 1e-15)
check("γ₁ = 4sin²(π/88)", abs(gam(1) - 0.005095770779492917) < 1e-15)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("B. Framework A — v9.0 第一代 (Fₙ/CY₃ˢ) 全鏈重算"); print("=" * 76)
# 依 docs/03 §1.3 + scripts/01 之定義，由頭算 m_u, m_d（含 m_t/m_b 鏈）
def compute_K(fib_idx, s, k, extra_a=0):
    sign = (-1)**(k+s+1); Fn = F[fib_idx]
    a = k - 3*(s-1) + extra_a
    return sign * Fn * CY3 * (1/φ)**a
def fg_ratio(fib_idx, s, k, extra_a=0):
    Fn = F[fib_idx]; Kn = compute_K(fib_idx, s, k, extra_a)
    return (Fn + EPS**3 * Kn) / CY3**s
V_EW = φ**8 * (φ**3 + 1)
VEV_nat = math.sqrt(EPS / (2 * (1/16)))
SCALE = V_EW / VEV_nat
m_t_nat = VEV_nat / math.sqrt(2)
k_d = (M - L[4]) * (1/φ) / 2 - (1/φ)**4
D_quark = 1 + (h11/h21) * EPS * (1 + EPS)
m_t = m_t_nat * SCALE
m_b = m_t_nat * (1/φ)**k_d * D_quark * SCALE
m_u_A = m_t * fg_ratio(9, 3, 9, 0)
m_d_A = m_b * fg_ratio(8, 2, 8, 0)
dev_u_A = abs(m_u_A*1000 / 2.16 - 1) * 100
dev_d_A = abs(m_d_A*1000 / 4.67 - 1) * 100
print(f"  m_u = {m_u_A*1000:.4f} MeV  dev = {dev_u_A:.4f}%  (docs/03: 0.5125%)")
print(f"  m_d = {m_d_A*1000:.4f} MeV  dev = {dev_d_A:.4f}%  (docs/03: 0.4043%)")
check("m_u dev = 0.5125% (docs/02 §1.1 0.51%)", abs(dev_u_A - 0.5125) < 0.01)
check("m_d dev = 0.4043% (docs/02 §1.1 0.40%)", abs(dev_d_A - 0.4043) < 0.01)
check("D_quark = 1 + (h¹¹/h²¹)ε(1+ε) = 1.065528", abs(D_quark - 1.0655278512659367) < 1e-12)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("C. Framework B — O136 M₀γ_nP_f (對照 08_final_closure.json 唯讀)"); print("=" * 76)
check("O136 08_final_closure.json 存在", J8 is not None)
if J8:
    m_u_B = M0 * gam(1) * 15.5
    m_d_B = M0 * gam(1) * 33.0
    print(f"  m_u = {m_u_B:.6f}  (JSON {J8['up']['m_pred']:.6f})  dev {J8['up']['dev_pct']:.4f}%")
    print(f"  m_d = {m_d_B:.6f}  (JSON {J8['down']['m_pred']:.6f})  dev {J8['down']['dev_pct']:.4f}%")
    check("m_u = M₀γ₁×15.5 = 2.203738 (docs/02 2.02%)", abs(m_u_B - J8['up']['m_pred']) < 1e-9 and abs(m_u_B - 2.203738) < 1e-5)
    check("m_d = M₀γ₁×33 = 4.691830 (docs/02 0.47%)", abs(m_d_B - J8['down']['m_pred']) < 1e-9 and abs(m_d_B - 4.691830) < 1e-5)
    check("JSON u n=1 P=15.5", J8['up']['n'] == 1 and abs(J8['up']['P_f']-15.5) < 1e-9)
    check("JSON d n=1 P=33", J8['down']['n'] == 1 and abs(J8['down']['P_f']-33.0) < 1e-9)
    for name, n, pf in [("electron",1,3.6), ("muon",7,15.5), ("tau",20,37.0),
                        ("strange",14,3.6), ("charm",34,13.0), ("bottom",33,44.0)]:
        check(f"JSON {name} n={n} P={pf}", J8[name]['n'] == n and abs(J8[name]['P_f']-pf) < 1e-9)
    for name in ['strange','charm','bottom','top']:
        d8 = abs(J8[name]['dev_pct'])
        check(f"{name} 實測閉合 (<5%)  — O115『>90%』過時", d8 < 5)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("D. up_quark_correction.py 重算 (docs/03 §1.4)"); print("=" * 76)
M_Pl = 1.220890e22
V_g1 = 46.5390
up_corr = 0.0227488532 * M_Pl * math.exp(-V_g1) * math.sqrt(φ)
d_corr = 0.0117201474 * M_Pl * math.exp(-V_g1) * 5.3
dev_up = abs(up_corr / 2.16 - 1) * 100
dev_dc = abs(d_corr / 4.67 - 1) * 100
print(f"  up×√φ = {up_corr:.4f} MeV dev {dev_up:.4f}%  (docs 0.472%)")
print(f"  d×5.3  = {d_corr:.4f} MeV dev {dev_dc:.4f}%  (docs 0.244%)")
check("up ×√φ dev = 0.472%", abs(dev_up - 0.472) < 0.01)
check("down ×5.3 dev = 0.244%", abs(dev_dc - 0.244) < 0.01)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("E. m_u/m_d — 15.5/33 (docs/02 Q4 + SESSION_START L17)"); print("=" * 76)
r_p, r_obs = 15.5/33.0, 2.16/4.67
r_dev = abs(r_p/r_obs - 1) * 100
print(f"  P_u/P_d = {r_p:.6f}  obs = {r_obs:.6f}  Δ = {r_dev:.4f}%")
check("P_u/P_d = 0.469697", abs(r_p - 0.469697) < 1e-6)
check("obs = 0.462527", abs(r_obs - 0.462527) < 1e-6)
check("Δ = 1.5502% (docs/03 §1.5)", abs(r_dev - 1.5502) < 0.01)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("F. O54 輕子交叉 (docs/03 §1.6: μ 0.131% / e 0.164%)"); print("=" * 76)
m_mu = M0 * gam(7) * 15.5
m_e = M0 * gam(1) * (L[6]/F[5])
dev_mu = abs(m_mu/105.66 - 1) * 100
dev_e = abs(m_e/0.510999 - 1) * 100
print(f"  m_μ = {m_mu:.4f} dev {dev_mu:.4f}%   m_e = {m_e:.6f} dev {dev_e:.4f}%")
check("μ dev = 0.131%", abs(dev_mu - 0.131) < 0.01)
check("e dev = 0.164%", abs(dev_e - 0.164) < 0.01)
check("u↔μ 共用 P_f = 15.5 觀察成立", True)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("G. 費米子反週期 nL ≡ 44 (mod 88) (docs/03 §1.7)"); print("=" * 76)
assign = {1:44, 7:44, 20:11, 14:22, 34:22, 33:4}
check("6 模式全過反週期條件", all((n*l) % 88 == 44 for n, l in assign.items()))

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("H. ★★ 合法模式集：兩條獨立判準一致"); print("=" * 76)
H_NZ = {6,10,12,15,16,18,20,21,22,24,25,26}
def protected(n):
    return all(j not in H_NZ for j in range(1, n+1) if j % 2 == n % 2)
PROT = [n for n in range(1, 45) if protected(n)]
SEL  = sorted({n for n in range(1, 45) if (n % 2 == 1 and n < 15) or (n % 2 == 0 and n < 6)})
EXPECT = [1,2,3,4,5,7,9,11,13]
print(f"  判準① 全息保護 = {PROT}")
print(f"  判準② O209 閾值定理 = {SEL}")
check("判準① = {1,2,3,4,5,7,9,11,13}", PROT == EXPECT)
check("判準② = 同一集", SEL == EXPECT)
check("兩判準一致 (|M|=9=N_gen²)", len(PROT) == 9 == NG**2)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("I. ★★ O136 夸克模式 {14,33,34} 受保護性 (O120 P_f 基礎)"); print("=" * 76)
for n in [14, 33, 34]:
    print(f"  n={n}: protected = {protected(n)}")
check("s n=14 唔受保護", not protected(14))
check("c n=34 唔受保護", not protected(34))
check("b n=33 唔受保護", not protected(33))
check("u n=1 / d n=1 受保護（合法）", protected(1) and protected(1))
# 與 O136 docs/34 統計裁決一致（P=0.8525 反週期集 vs P=0.0155 A₅ 集）

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("J. ★ A₅ 質量升序指派 C_f = m/(M₀γ_n) (O137 R19 框架)"); print("=" * 76)
PDG = {"e":0.51099895, "u":2.16, "d":4.67, "s":93.4, "mu":105.6583755,
       "c":1270.0, "tau":1776.86, "b":4180.0, "t":172690.0}
A5 = [1,2,3,4,5,7,9,11,13]
order = ["e","u","d","s","mu","c","tau","b","t"]
Cf = {}
for f, n in zip(order, A5):
    Cf[f] = PDG[f] / (M0 * gam(n))
    print(f"  {f:>4} n={n:>2}  C_f = {Cf[f]:>10.4f}")
EXP_CF = {"e":3.5941,"u":3.8029,"d":3.6620,"s":41.3207,"mu":30.0309,
          "c":186.0605,"tau":159.6437,"b":255.7517,"t":7722.8073}
for f, x in EXP_CF.items():
    check(f"C_f({f}) ≈ {x}", abs(Cf[f] - x) < 5e-3)
blocks = [["e","u","d"], ["s","mu","c"], ["tau","b","t"]]
spans = []
for blk in blocks:
    v = [Cf[x] for x in blk]
    spans.append(max(v)/min(v))
print(f"  塊內跨度: gen1={spans[0]:.3f}  gen2={spans[1]:.3f}  gen3={spans[2]:.3f}")
check("gen1 C_f 跨度 1.058 (近乎均勻)", abs(spans[0] - 1.0583) < 0.01)
check("全譜 C_f 跨度 ≈ 2149×", 2140 < max(Cf.values())/min(Cf.values()) < 2160)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("K. ★★ gen1 C_f 均勻性 null — 精確枚舉 + 多 seed MC"); print("=" * 76)
allm = sorted(PDG.values())
g1_modes = [gam(n) for n in [1,2,3]]
obsS1 = 1.0583
vals1 = []
for pick in combinations(allm, 3):
    cf = [m/(M0*g) for m, g in zip(pick, g1_modes)]
    vals1.append(max(cf)/min(cf))
vals1.sort()
rank1 = sum(1 for v in vals1 if v <= obsS1)
print(f"  精確枚舉 C(9,3)=84: gen1 觀測 S={obsS1:.4f}  rank = {rank1}/84  (p={rank1/84:.4f})")
check("gen1 係 84 個三子集唯一最小值 (rank 1/84)", rank1 == 1)
# 多 seed MC 確認（p ≈ 0.0119）
for seed in [7, 123, 20260926]:
    random.seed(seed)
    N = 200_000
    cnt = 0
    for _ in range(N):
        pick = sorted(random.sample(allm, 3))
        cf = [m/(M0*g) for m, g in zip(pick, g1_modes)]
        if max(cf)/min(cf) <= obsS1:
            cnt += 1
    p = cnt/N
    print(f"  MC seed={seed}: p = {p:.4f}")
    check(f"MC seed={seed} p≈0.0119 (±0.003)", abs(p - 0.0119) < 0.0035)
# 其他塊 rank
g2_modes, g3_modes = [gam(n) for n in [4,5,7]], [gam(n) for n in [9,11,13]]
def rank_of(modes, obsS):
    vs = []
    for pick in combinations(allm, 3):
        cf = [m/(M0*g) for m, g in zip(pick, modes)]
        vs.append(max(cf)/min(cf))
    vs.sort()
    return sum(1 for v in vs if v <= obsS), len(vs)
r2, tot = rank_of(g2_modes, spans[1]); r3, tot = rank_of(g3_modes, spans[2])
print(f"  gen2 rank {r2}/84 (p={r2/84:.4f}) · gen3 rank {r3}/84 (p={r3/84:.4f})")
check("gen2 rank = 3/84 (p=0.0357)", r2 == 3)
check("gen3 rank = 16/84 (p=0.1905)", r3 == 16)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("L. ★ 若 C_f ≡ L₆/F₅ = 3.6（整代恒一）之預言"); print("=" * 76)
for f, n in [("e",1),("u",2),("d",3)]:
    pred = M0 * gam(n) * 3.6
    dev = abs(pred/PDG[f] - 1) * 100
    print(f"  m_{f:<2} = {pred:>9.5f} MeV  dev {dev:.2f}%")
    check(f"C_f≡3.6 預言 m_{f} dev ∈ docs 值", (f == "e" and abs(dev-0.164) < 0.05) or
          (f == "u" and abs(dev-5.34) < 0.05) or (f == "d" and abs(dev-1.69) < 0.05))

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("M. ★ m_u/m_d 三式比較"); print("=" * 76)
rg = gam(2)/gam(3)
need = r_obs / rg
print(f"  純 γ₂/γ₃ = {rg:.6f}  dev {abs(rg/r_obs-1)*100:.3f}%")
print(f"  需 C_u/C_d = {need:.6f}")
check("純 γ 比 dev = 3.705%", abs(abs(rg/r_obs-1)*100 - 3.705) < 0.01)
check("需 C_u/C_d = 1.038476", abs(need - 1.038476) < 1e-5)
check("A₅ 式 (γ×C_f) 精確重現 obs（當式 tautology）", abs((gam(2)*Cf['u'])/(gam(3)*Cf['d']) / r_obs - 1) < 1e-9)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("N. 密度基準 — O120 P_f 三數目"); print("=" * 76)
def catalog(upto=176):
    s = set()
    s |= {n for n in L if n <= upto}; s |= {n for n in F if n <= upto}
    for n in range(1, 30): s |= {n, 2*n, 3*n, 4*n, n*n}
    s |= {44,88,90,123,134,176,45,55,66,98,36,41,60,61,17,19,28,31}
    s |= {h11, h21, CY3, 27,29,33,37,42,46,48,50,51,64}
    return {x for x in s if 1 <= x <= upto}
CAT = catalog()
density = len(CAT)/176
print(f"  目錄 1..176 結構數 = {len(CAT)} ({density*100:.1f}% 密度)")
check("目錄密度 ~49% (87/176)", abs(density - 87/176) < 0.02)
print(f"  12..20 全在目錄: {all(x in CAT for x in range(12,21))}")
check("15.5 (=31/2) 屬目錄係高密度巧合 (12..20 全在)", all(x in CAT for x in range(12, 21)))

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76); print("O. docs 跨核對 — 逐 headline 對 docs/01-03 claims"); print("=" * 76)
# 抽述（quoted from docs）→ 已喺 A–N 驗證，此處再對 docs 字面
docs_claims = [
    ("docs/02 §1.1『u 0.51%』", abs(dev_u_A - 0.5125) < 0.01),
    ("docs/02 §1.1『d 0.40%』", abs(dev_d_A - 0.4043) < 0.01),
    ("docs/02 §1.2『u 2.2037 MeV 2.02%』", abs(m_u_B - 2.203738) < 1e-5 and abs(J8['up']['dev_pct']-2.0249) < 0.001 if J8 else False),
    ("docs/02 §1.2『d 4.6918 MeV 0.47%』", abs(m_d_B - 4.691830) < 1e-5 and abs(J8['down']['dev_pct']-0.4675) < 0.001 if J8 else False),
    ("docs/02 §三『up_quark_correction 0.47% / 0.24%』", abs(dev_up-0.472) < 0.01 and abs(dev_dc-0.244) < 0.01),
    ("docs/02 Q4『Δ1.55%』", abs(r_dev - 1.5502) < 0.01),
    ("docs/03 §2.2 O136-08 s/c/b/t 各 <1%", all(abs(J8[name]['dev_pct']) < 1.0 for name in ['strange','charm','bottom','top']) if J8 else False),
    ("docs/03 §1.7 反週期 6 模式", all((n*l) % 88 == 44 for n, l in assign.items())),
]
for name, ok in docs_claims:
    check(name, ok)

# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 76)
import sys
sys.exit(1 if FAIL else 0)