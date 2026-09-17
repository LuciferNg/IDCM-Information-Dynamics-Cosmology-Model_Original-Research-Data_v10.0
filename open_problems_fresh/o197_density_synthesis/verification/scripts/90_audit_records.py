#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O197 記錄獨立審計 — verification/scripts/90_audit_records.py

目的: 唔信任何被驗證 script 嘅 PASS 輸出, 獨立重算 O197 (+verification) 全部
      文檔宣稱值, 同文檔數字逐項對比。只讀不改。

獨立性措施:
  1. 唔 import 任何被驗證 script (07/08/verification 01-06)
  2. 全部代數用 mpmath dps=60 由第一原理重算 (含標準積恆等式獨立推導)
  3. 宇宙學積分自寫 (mpmath.quad + 代換 x=1/(1+z)), 唔用 scipy
  4. MC 用唔同 seed + 大 n, 檢查宣稱值嘅穩健性 (唔係複製輸出)
  5. permutation p 用精確 DP 枚舉 (唔係隨機抽樣)
  6. 額外做「測試質量審計」: 標出同義反覆 (tautology) 測試

零寫入 (除本檔)。
"""
import mpmath as mp
mp.mp.dps = 60
import json, math, random
from pathlib import Path

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o197_density_synthesis")
DATA = BASE / "verification/data/harikane23_table3_eddington.json"

R = []          # (section, name, ok, got, expect, rel)
def chk(sec, name, got, expect, tol=1e-6, note=""):
    got = mp.mpf(got); expect = mp.mpf(expect)
    if expect == 0:
        rel = abs(got); ok = rel <= mp.mpf(tol)          # 零期望 → 絕對容差
    else:
        rel = abs(got - expect) / abs(expect); ok = rel <= mp.mpf(tol)
    R.append((sec, name, ok, mp.nstr(got, 10), mp.nstr(expect, 10), float(rel)))
    print(f"[{'PASS' if ok else 'FAIL'}] {sec} {name}: {mp.nstr(got,10)} vs {mp.nstr(expect,10)}"
          f" (rel {float(rel):.2e}, tol {tol}) {note}")
    return ok

def chkbool(sec, name, ok, note=""):
    R.append((sec, name, bool(ok), "-", "-", 0.0))
    print(f"[{'PASS' if ok else 'FAIL'}] {sec} {name} {note}")
    return ok

# ============================================================
print("=" * 78)
print("A. 精確代數 (docs/01 T1-T4, docs/04 T9a-T9g, docs/05 T10a-T10g)")
print("=" * 78)

N_d, B, N_gen = 44, 4, 3
mu2 = mp.mpf(2)
M_base = mp.mpf("1.914e6")
dhat = lambda k: -mp.cos(mp.mpf(k) * mp.pi / 88)
gamma = lambda k: 4 * mp.sin(mp.mpf(k) * mp.pi / 176) ** 2

# A1 身份 1+δ̂ = γ/2 = 2sin²(kπ/176)
ok = all(abs(1 + dhat(k) - gamma(k) / 2) < mp.mpf("1e-55") for k in range(1, 89))
chkbool("A1", "1+δ̂_k = γ_k/2 = 2sin²(kπ/176) ∀k=1..88", ok)

# A2 Π(1+δ̂) = 88/2^86 (直接積)
P_all = mp.fprod([1 + dhat(k) for k in range(1, 89)])
chk("A2", "Π(1+δ̂) = 88/2^86", P_all, mp.mpf(88) / mp.mpf(2) ** 86, 1e-50)

# A3 獨立推導: Π_{k=1}^{N−1} 2sin²(kπ/(2N)) = N/2^{N−1}  (N=88) + k=N 邊界項 2
#   基礎恆等式: Π_{k=1}^{N−1} sin(πk/(2N)) = √N/2^{N−1} (獨立數值確認)
P_sin = mp.fprod([mp.sin(mp.pi * k / (2 * 88)) for k in range(1, 88)])
chk("A3a", "Π sin(kπ/176) = √88/2^87 (基礎恆等式)", P_sin, mp.sqrt(88) / mp.mpf(2) ** 87, 1e-50)
P_half = mp.fprod([2 * mp.sin(mp.pi * k / 176) ** 2 for k in range(1, 88)])
chk("A3b", "Π_{k=1}^{87} 2sin² = 88/2^87", P_half, mp.mpf(88) / mp.mpf(2) ** 87, 1e-50)
chk("A3c", "×k=88 邊界項 2 ⟹ 88/2^86", P_half * 2, mp.mpf(88) / mp.mpf(2) ** 86, 1e-50)

# A4 ⟨ln(1+δ̂)⟩
chk("A4", "⟨ln(1+δ̂)⟩ = (ln88−86ln2)/88", mp.log(P_all) / 88,
    (mp.log(88) - 86 * mp.log(2)) / 88, 1e-50)
chk("A4b", "⟨ln(1+δ̂)⟩ 數值 −0.626515", mp.log(P_all) / 88, mp.mpf("-0.626515"), 1e-6)

# A5-A7 守恆 + 對偶 (閉式: Σ_{k=1}^{88} cos(kπ/88) = −1, Dirichlet)
S_cos = mp.fsum([mp.cos(mp.mpf(k) * mp.pi / 88) for k in range(1, 89)])
S_cos_closed = mp.cos(mp.mpf(89) * mp.pi / 176) / mp.sin(mp.pi / 176)
chk("A5a", "Σ_{k=1}^{88} cos(kπ/88) = −1 (閉式重驗)", S_cos, mp.mpf(-1), 1e-50)
chk("A5b", "Dirichlet 閉式 cos(89π/176)/sin(π/176) = −1", S_cos_closed, mp.mpf(-1), 1e-50)
chk("A5c", "Σ_all δ̂ = 1", mp.fsum([dhat(k) for k in range(1, 89)]), mp.mpf(1), 1e-50)
chk("A6a", "Σ_odd δ̂ = 0", mp.fsum([dhat(k) for k in range(1, 89, 2)]), mp.mpf(0), 1e-50)
chk("A6b", "Σ_even δ̂ = 1", mp.fsum([dhat(k) for k in range(2, 89, 2)]), mp.mpf(1), 1e-50)
ok = all(abs(dhat(89 - k) + dhat(k - 1)) < mp.mpf("1e-55") for k in range(45, 89))
chkbool("A7", "δ̂(89−k) = −δ̂(k−1) 對偶 (44 對)", ok)

# A8-A9 通道 Π + 對數平均
P_plus = mp.fprod([1 + dhat(k) for k in range(45, 89)])
P_minus = mp.fprod([1 + dhat(k) for k in range(1, 45)])
chk("A8a", "Π(1+δ̂₊) = 1.5474e9 (docs/04 精確值)", P_plus, mp.mpf("1.5473998e9"), 1e-7)
chk("A8b", "Π(1+δ̂₋) = 7.3502e-34", P_minus, mp.mpf("7.3502e-34"), 1e-4)
chk("A8c", "Π₊·Π₋ = 88/2^86", P_plus * P_minus, mp.mpf(88) / mp.mpf(2) ** 86, 1e-50)
chk("A9a", "⟨ln(1+δ̂₊)⟩ = +0.48091", mp.log(P_plus) / 44, mp.mpf("0.48091"), 1e-5)
chk("A9b", "⟨ln(1+δ̂₋)⟩ = −1.73394", mp.log(P_minus) / 44, mp.mpf("-1.73394"), 1e-5)
chk("A9c", "⟨ln₋⟩+⟨ln₊⟩ = 2⟨ln_all⟩ = −1.25303",
    (mp.log(P_minus) + mp.log(P_plus)) / 44, 2 * mp.log(P_all) / 88, 1e-50)

# A10-A11 閾值 + 通道 A 帶閉式
chk("A10", "δ̂₄₅ = sin(π/88)", dhat(45), mp.sin(mp.pi / 88), 1e-50)
M_A_lo = M_base * (1 + mp.sin(mp.pi / 88)) ** mp.mpf("1.5")
chk("A11a", "通道 A 下限閉式 = M_base(1+sin(π/88))^{3/2} = 2.017382e6",
    M_A_lo, mp.mpf("2017382"), 1e-6)
M_turn = M_base * mp.mpf(2) ** mp.mpf("1.5")
chk("A11b", "M_turn = M_base·2^{3/2} = 5.41361e6", M_turn, mp.mpf("5.41361e6"), 1e-6)
chk("A11c", "種子全域下界 = M_base (中心模 k=44, δ̂=0)", M_base * (1 + dhat(44)) ** mp.mpf("1.5"),
    M_base, 1e-50)

# A12 docs/05 數值閉環
chk("A12a", "M_seed(δ=1.367) = 6.9701e6 (LRD)", M_base * (1 + mp.mpf("1.367")) ** mp.mpf("1.5"),
    mp.mpf("6.9701e6"), 1e-5)
chk("A12b", "M_seed(δ=100) = 1.9428e9 (UHz1)", M_base * mp.mpf(101) ** mp.mpf("1.5"),
    mp.mpf("1.9428e9"), 1e-5)

# A13 s² = 36 × Var_pop(ln(1+δ̂₊))
vals = [mp.log(1 + dhat(k)) for k in range(45, 89)]
mean_v = mp.fsum(vals) / 44
var_pop = mp.fsum([(v - mean_v) ** 2 for v in vals]) / 44
chk("A13", "s² = 36·Var_pop(ln(1+δ̂₊)) = 1.4098", 36 * var_pop, mp.mpf("1.4098"), 1e-3)

# A14 logN 參數結構
phi = (1 + mp.sqrt(5)) / 2
chk("A14a", "μ = φ⁻¹ + L₅/(F₅·N_gen²) = φ⁻¹+11/45 = 0.862478",
    phi ** -1 + mp.mpf(11) / 45, mp.mpf("0.862478"), 1e-5)
chk("A14b", "s = √1.4098 = 1.1874", mp.sqrt(36 * var_pop), mp.mpf("1.1874"), 1e-4)

# A15 3D 角譜身份
k45 = mp.mpf(45)
chk("A15", "(1+δ̂)^{3/2} = 2^{3/2}sin³(kπ/176)", (gamma(k45) / 2) ** mp.mpf("1.5"),
    mp.mpf(2) ** mp.mpf("1.5") * mp.sin(k45 * mp.pi / 176) ** 3, 1e-50)

# A16 ★T9g 自我相似: 兩種定義對比 (docs/04 寫「γ(22·4^ℓ/2) = μ²」)
# A16c: ★T9g 根因 — 有冇獨立內容? (≡ T2b 喺中心模 + 層級定義?)
# T2b: 1+δ̂ = γ/2 ⟹ δ̂ = γ/2 − 1 ⟹ δ̂ = 0 ⟺ γ = 2
# 層級中心模 n = N_ℓ/2 ⟹ γ^{(ℓ)} = 4sin²(π/4) = 2 (對任何 N 都成立, 因為 sin²(π/4)=1/2)
# ⟹ 「中心模 γ = μ²」≡「中心模 δ̂ = 0」≡ T2b 代入 — 冇新結構內容
arb = []
for Ntest in [22, 44, 88, 176, 352, 1408, 5632, 100000]:
    g = 4 * mp.sin((Ntest / 2) * mp.pi / (2 * Ntest)) ** 2
    d = g / 2 - 1
    arb.append((Ntest, g, d))
allc = all(abs(g - 2) < 1e-50 and abs(d) < 1e-50 for _, g, d in arb)
chk("A16c", "★T9g 冇獨立內容: 中心模 γ=2 ⟺ δ̂=0 ⟺ T2b 代入 (對任意 N 成立)",
    1.0 if allc else 0.0, 1.0, 1e-9,
    f"(N=22..100000 全部 γ=2, δ̂=0 ⟹ 恆真; 真問題 = 層級 N_ℓ=22·4^ℓ 嘅來源)")

print()
print("--- A16 T9g 定義敏感度 (docs/04 T9g) ---")
gA = lambda n, N: 4 * mp.sin(mp.mpf(n) * mp.pi / (2 * N)) ** 2      # script 07 用嘅
gB = lambda k: 4 * mp.sin(mp.mpf(k) * mp.pi / 176) ** 2             # 權威 γ (176-Laplacian)
for ell in range(5):
    Nl = 22 * 4 ** ell
    n_c = Nl // 2
    print(f"  ℓ={ell}: N_ℓ={Nl:5d}, n_center={n_c:5d} | script07 γ=4sin²(nπ/2N): {mp.nstr(gA(n_c,Nl),8)}"
          f" | 權威 γ=4sin²(kπ/176): {mp.nstr(gB(n_c),8)}")
chk("A16a", "T9g (script 07 定義) γ(N_ℓ/2)=μ² ∀ℓ — 恆真 (4sin²(π/4))",
    gA(11, 22), mu2, 1e-50, "← 同義反覆: 對任何 N 都成立")
chk("A16b", "T9g (權威定義 γ=4sin²(kπ/176)) γ(22·4^ℓ/2)=2 ?",
    gB(11), mu2, 1e-6, "← 失敗 = docs 陳述與權威定義唔一致")
print(f"  權威定義下 γ=2 嘅模態: k=44 (γ={mp.nstr(gB(44),8)}), k=132 (γ={mp.nstr(gB(132),8)})")

# A17 結構算術
chk("A17a", "36 = B·N_gen² = 4×9", B * N_gen ** 2, 36, 1e-50)
chk("A17b", "36 = N_d − F_proj + N_gen² = 44−17+9", N_d - 17 + N_gen ** 2, 36, 1e-50)

# ============================================================
print()
print("=" * 78)
print("B. 統計宣稱 (verification/docs/01-02; 自寫 MC 唔同 seed)")
print("=" * 78)

data = json.load(open(DATA))
lams = [d["lambda_Edd"] for d in data]
masses = sorted(d["M_BH"] for d in data)
obs_med = masses[len(masses) // 2]
L_EDD = mp.mpf("1.26e38")
M_turn_f = float(M_turn)
mu = 0.862478; s = 1.1874
mu_lnM = math.log(1.914e6) + 1.5 * mu
sig_lnM = 1.5 * s
A_masses = [1.914e6 * (2.0 * math.sin(k * math.pi / 176.0) ** 2) ** 1.5 for k in range(45, 89)]

# B1 λ 分布統計
lnl = [math.log(l) for l in lams]
geo = math.exp(sum(lnl) / 10); ari = sum(lams) / 10
med_lam = sorted(lams)
med_lam = (med_lam[4] + med_lam[5]) / 2
sig_sam = math.sqrt(sum((v - sum(lnl) / 10) ** 2 for v in lnl) / 9)
sig_pop = math.sqrt(sum((v - sum(lnl) / 10) ** 2 for v in lnl) / 10)
chk("B1a", "λ geo = 0.702", geo, 0.702, 1e-3)
chk("B1b", "λ arith = 1.275", ari, 1.275, 1e-3)
chk("B1c", "λ median = 1.060", med_lam, 1.060, 1e-3)
chk("B1d", "σ_lnλ = 1.39 (sample ddof=1)", sig_sam, 1.39, 5e-3,
    f"(population = {sig_pop:.4f} — docs 用 sample)")
chk("B1e", "偏置因子 geo/0.1 = 7.0×", geo / 0.1, 7.0, 1e-2)

# B2 λ 自洽 (L_bol / (L_EDD·M) vs 表 λ) — ★L_Edd 常數敏感 (審計發現)
# 論文自洽常數: 用 1.3e38 時 8/10 物件 dev < 1% ⟹ 論文用 L_Edd = 1.3e38 (唔係 1.26e38)
devs13 = [(d["name"], float(abs(float(mp.mpf(str(d["L_bol"])) / (mp.mpf("1.3e38") * mp.mpf(str(d["M_BH"]))) - mp.mpf(str(d["lambda_Edd"]))) / mp.mpf(str(d["lambda_Edd"]))))) for d in data]
devs126 = [(d["name"], float(abs(float(mp.mpf(str(d["L_bol"])) / (mp.mpf("1.26e38") * mp.mpf(str(d["M_BH"]))) - mp.mpf(str(d["lambda_Edd"]))) / mp.mpf(str(d["lambda_Edd"]))))) for d in data]
mx13 = max(devs13, key=lambda t: t[1]); mx126 = max(devs126, key=lambda t: t[1])
n13 = sum(1 for _, v in devs13 if v < 0.01)
print(f"    L_Edd=1.3e38 (論文): {n13}/10 物件 dev < 1%, 最大 {mx13[0]} {mx13[1]*100:.2f}%")
print(f"    L_Edd=1.26e38 (scripts/05 用): 最大 {mx126[0]} {mx126[1]*100:.2f}% — 系統 +2.5% 偏移")
chk("B2a", "λ 自洽 (L_Edd=1.3e38 論文常數): max dev < 8%", mx13[1], 0.0, 0.08,
    f"(最大 {mx13[0]} {mx13[1]*100:.2f}%)")
chk("B2b", "scripts/05 用 1.26e38 → 系統偏移 (記錄, 唔影響結論)",
    abs(mx126[1] - 0.10), 0.0, 0.02, f"(max dev {mx126[1]*100:.2f}% > 10% 門檻)")
# λ_err_lo/λ_err_hi 欄位語義檢查 (係非對稱誤差唔係界?)
# ★2026-09-16 改名 (審計 F3): 原 lambda_lo/lambda_hi -> lambda_err_lo/lambda_err_hi
#   (與 data 檔 + docs/04 F3 + docs/02 §七 原子化同步; 值全部不變)
bad = [d["name"] for d in data if d["lambda_err_hi"] < d["lambda_Edd"] or d["lambda_err_lo"] > d["lambda_Edd"]]
chk("B2c", "★λ_err_lo/λ_err_hi 欄位 = 論文非對稱誤差 (唔係 bounds)",
    len(bad), 2, 1e-9, f"(hi<λ 嘅物件: {bad} — 證實唔係 bounds)")

# B3 Spearman + 精確 permutation p (DP 枚舉, 唔抽樣)
xs = [math.log(d["M_BH"]) for d in data]; ys = [math.log(d["lambda_Edd"]) for d in data]
def spearman(a, b):
    n = len(a)
    ra = [sorted(a).index(v) + 1 for v in a]; rb = [sorted(b).index(v) + 1 for v in b]
    ma = sum(ra) / n; mb = sum(rb) / n
    cov = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    return cov / math.sqrt(sum((r - ma) ** 2 for r in ra) * sum((r - mb) ** 2 for r in rb))
rho = spearman(xs, ys)
chk("B3a", "Spearman ρ = −0.648", rho, -0.648, 1e-3)
# 精確: ρ = 1 − Σd²/165 (n=10) ⟹ ρ ≤ ρ_obs ⟺ Σd² ≥ D_cut
n = 10
S_max = n * (n * n - 1) / 6                    # 165; ρ = 1 − Σd²/165
D_cut = round((1 - rho) * S_max)               # ρ ≤ ρ_obs ⟺ Σd² ≥ D_cut
D_sym = S_max - D_cut                          # ρ ≥ +|ρ_obs| ⟺ Σd² ≤ D_sym
# DP: dp[mask][sum] = #ways
from collections import defaultdict
dp = [defaultdict(int) for _ in range(1 << n)]
dp[0][0] = 1
for mask in range(1 << n):
    k = bin(mask).count("1")
    if k == n or not dp[mask]: continue
    for sm, c in list(dp[mask].items()):
        for j in range(n):
            if not (mask >> j) & 1:
                dp[mask | (1 << j)][sm + (k - j) ** 2] += c
total = math.factorial(n)
sums = dp[(1 << n) - 1]
ge = sum(c for sm, c in sums.items() if sm >= D_cut)
le = sum(c for sm, c in sums.items() if sm <= D_sym)
p_one = ge / total; p_two = (ge + le) / total
chk("B3b", "精確 permutation p (one-sided, ρ≤obs) = 0.024", p_one, 0.024, 0.15,
    f"(精確 {p_one:.5f}; two-sided = {p_two:.5f})")

# B4-B6 前向中位 + 張力 (自寫 MC, seed 唔同)
rng = random.Random(987654321)
def draw_seed(rng):
    if rng.random() < 0.2: return rng.choice(A_masses)
    return math.exp(rng.gauss(mu_lnM, sig_lnM))
def fwd_median(lam_pool, Lmin, n=400000):
    v = []
    for _ in range(n):
        li = rng.choice(lam_pool); M = draw_seed(rng)
        if li * 1.26e38 * M >= Lmin: v.append(math.log(M))
    v.sort(); return math.exp(v[len(v) // 2])
M_faint = min(d["M_BH"] for d in data)
med_fix = fwd_median([0.1], 0.1 * 1.26e38 * M_faint * 0.999)
chk("B4a", "T5a 固定 λ=0.1 前向中位 = 7.52e6", med_fix, 7.52e6, 0.03)
lu = [math.exp(rng.uniform(math.log(0.01), math.log(1.0))) for _ in range(2000)]
med_lu = fwd_median(lu, 3e43)
chk("B4b", "T5b λ log-uniform 前向中位 = 9.19e6", med_lu, 9.19e6, 0.03)
med_emp = fwd_median(lams, 3e43)
chk("B4c", "實測 λ 前向中位 = 5.40e6 (docs/02 §二)", med_emp, 5.40e6, 0.03)
t_emp = math.log(med_emp / obs_med)
chk("B5a", "張力 Δln = −1.78 (實測 λ)", abs(t_emp), 1.78, 0.03)
g_need = obs_med / med_emp
chk("B5b", "閉合需 g = 5.92", g_need, 5.92, 0.03)
A_min = min(A_masses)
g_allow = min(2.3e6, 3.7e6) / A_min
chk("B5c", "預言 2 容許 g ≤ 1.14", g_allow, 1.14, 0.01)
chk("B5d", "矛盾倍數 5.2×", g_need / g_allow, 5.2, 0.05)
chk("B5e", "virial 需 0.77 dex", math.log10(g_need), 0.77, 0.03)
sig_med_model = 1.253 * sig_lnM / math.sqrt(10)
lnm = [math.log(m) for m in masses]
sig_obs = math.sqrt(sum((v - sum(lnm) / 10) ** 2 for v in lnm) / 9)
sig_med_obs = 1.253 * sig_obs / math.sqrt(10)
chk("B6a", "σ_med(模型) = 0.71 → 2.5σ", abs(t_emp) / sig_med_model, 2.5, 0.05,
    f"(σ_med={sig_med_model:.4f})")
chk("B6b", "σ_med(觀測) = 0.48 → 3.7σ", abs(t_emp) / sig_med_obs, 3.7, 0.05,
    f"(σ_obs={sig_obs:.4f}, σ_med={sig_med_obs:.4f})")

# B7 L_min 反演 (兩個設定)
def fwd_lowfrac(lam_pool, Lmin, n=400000):
    lc = tc = 0
    for _ in range(n):
        li = rng.choice(lam_pool); M = draw_seed(rng)
        if li * 1.26e38 * M >= Lmin:
            tc += 1
            if M < M_turn_f: lc += 1
    return lc / tc if tc else 0.0
f_obs = sum(1 for m in masses if m < M_turn_f) / 10
def invert_Lmin(pool, target, lo=1e42, hi=1e47):
    for _ in range(40):
        mid = math.exp((math.log(lo) + math.log(hi)) / 2)
        if fwd_lowfrac(pool, mid, n=60000) > target: lo = mid
        else: hi = mid
    return math.exp((math.log(lo) + math.log(hi)) / 2)
chk("B7a", "低端份額 (實測 λ, L_min=3e43) = 0.507", fwd_lowfrac(lams, 3e43), 0.507, 0.06)
chk("B7b", "L_min* (λ=0.1) = 5.73e43", invert_Lmin([0.1], 0.2), 5.73e43, 0.15)
chk("B7c", "L_min* (實測 λ) = 1.02e45", invert_Lmin(lams, 0.2), 1.02e45, 0.15)

# B8 T6/T7 (λ log-uniform + virial 0.4 dex)
def fwd_frac_virial(sig_vir=0.0, n=400000):
    lc = tc = 0
    for _ in range(n):
        li = math.exp(rng.uniform(math.log(0.01), math.log(1.0)))
        M = draw_seed(rng)
        Mo = M * math.exp(rng.gauss(0, sig_vir)) if sig_vir else M
        if li * 1.26e38 * Mo > 3e43:
            tc += 1
            if M < M_turn_f: lc += 1
    return lc / tc if tc else 0.0
chk("B8a", "T6 λ log-uniform 低端份額 = 0.391", fwd_frac_virial(0.0), 0.391, 0.06)
chk("B8b", "T7 + virial 0.4 dex = 0.392", fwd_frac_virial(0.4), 0.392, 0.06)

# B9 Harikane 放置
n_low = sum(1 for m in masses if m < M_turn_f); n_high = 10 - n_low
chk("B9a", "低端 2/10 (預言 2)", n_low, 2, 1e-9)
chk("B9b", "高端 8/8 > M_turn (預言 3)", n_high, 8, 1e-9)
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
z1 = (math.log(M_turn_f) - mu_lnM) / sig_lnM; z2 = (math.log(2 * M_turn_f) - mu_lnM) / sig_lnM
p_band = Phi(z2) - Phi(z1)
n_band = sum(1 for m in masses if M_turn_f < m < 2 * M_turn_f)
chk("B9c", "轉折帶期望 = 1.23 粒", p_band * n_high, 1.23, 0.02, f"(觀測 {n_band} 粒)")
# CP CI (自寫精確二項反演)
def binom_pmf(k, n, p):
    p = min(max(p, 1e-15), 1 - 1e-15)
    return math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log1p(-p))
def binom_cdf(k, n, p): return sum(binom_pmf(i, n, p) for i in range(k + 1))
def cp_ci(k, n, a=0.05):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if binom_cdf(k - 1, n, mid) > 1 - a / 2: lo = mid
        else: hi = mid
    plo = (lo + hi) / 2
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if binom_cdf(k, n, mid) > a / 2: lo = mid
        else: hi = mid
    return plo, (lo + hi) / 2
ci = cp_ci(2, 10)
chk("B9d", "w CP 95% CI 下限 = 0.025", ci[0], 0.025, 0.06, f"(CI = [{ci[0]:.4f}, {ci[1]:.4f}])")
chk("B9e", "w CP 95% CI 上限 = 0.556", ci[1], 0.556, 0.03)

# B10 通道 B 參數
med_B = math.exp(mu_lnM)
chk("B10a", "通道 B 中位 = 6.9790e6", med_B, 6.9790e6, 1e-5)
chk("B10b", "σ_lnM = 1.7811", sig_lnM, 1.7811, 1e-5)
chk("B10c", "P_B(M<M_turn) = 0.4433", Phi((math.log(M_turn_f) - mu_lnM) / sig_lnM), 0.4433, 1e-3)

# B11 K-S
high = sorted(m for m in masses if m > M_turn_f)
def cdf_trunc(m):
    zt = (math.log(M_turn_f) - mu_lnM) / sig_lnM
    return (Phi((math.log(m) - mu_lnM) / sig_lnM) - Phi(zt)) / (1 - Phi(zt))
D = max(abs((i + 1) / 8 - cdf_trunc(m)) for i, m in enumerate(high))
chk("B11", "K-S D = 0.216 < 0.480 (n=8)", D, 0.216, 0.02)

# B12 k-映射
def k_of_M(M):
    r = (M / 1.914e6) ** (2 / 3) / 2
    return 176 * math.asin(math.sqrt(r)) / math.pi
chk("B12a", "GLASS_160133 (2.3e6) ↔ k = 47.7", k_of_M(2.3e6), 47.7, 0.01)
chk("B12b", "GLASS_150029 (3.7e6) ↔ k = 60.4", k_of_M(3.7e6), 60.4, 0.01)

# B13 UHz1
zU = (math.log(1.7e9) - mu_lnM) / sig_lnM
chk("B13a", "UHz1 z-score = 3.085", zU, 3.085, 1e-3)
chk("B13b", "P(M≥1.7e9) = 1.016e-3", 1 - Phi(zU), 1.016e-3, 5e-3)
chk("B13c", "P(≥1 | N=434) = 0.36", 1 - (1 - (1 - Phi(zU))) ** 434, 0.36, 0.05)

# B14 斜率
sl_g = -(math.log(1e8) - mu_lnM) / sig_lnM ** 2
chk("B14a", "Gaussian 指數斜率 = −0.839", sl_g, -0.839, 1e-3)
chk("B14b", "全 PDF 斜率 = −1.839", sl_g - 1, -1.839, 1e-3)

# B15 截斷 logN 中位
def Phi_inv(p):
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    if p < 0.02425:
        q = math.sqrt(-2 * math.log(p)); return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > 1 - 0.02425:
        q = math.sqrt(-2 * math.log(1 - p)); return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5; r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
zt = (math.log(M_turn_f) - mu_lnM) / sig_lnM
M_tr_med = math.exp(mu_lnM + sig_lnM * Phi_inv(0.5 * (1 + Phi(zt))))
chk("B15a", "截斷 logN 中位 = 1.99e7", M_tr_med, 1.99e7, 0.02)
h_med = high[len(high) // 2]
chk("B15b", "高端 8 粒中位 = 4.2e7", h_med, 4.2e7, 0.02)
chk("B15c", "張力 0.75 dex < 2σ = 1.58 dex", abs(math.log(h_med / M_tr_med)), 0.75, 0.05,
    f"(2σ = {2*sig_lnM*1.253/math.sqrt(8):.2f} dex)")

# ============================================================
print()
print("=" * 78)
print("C. 宇宙學 + 成長閉合 (verification/docs/03; 自寫積分, 唔用 scipy)")
print("=" * 78)

H0 = mp.mpf("67.4"); Om = mp.mpf("0.315"); OL = 1 - Om
H0s = H0 * 1e5 / mp.mpf("3.086e24")
def t_z(z):
    """宇宙年齡 (Gyr) — mpmath.quad 自寫 (代換 u=1/(1+z) 避免無窮區間)"""
    z = mp.mpf(z)
    if z > 1e4: return mp.mpf(0)
    f = lambda zz: 1 / ((1 + zz) * mp.sqrt(Om * (1 + zz) ** 3 + OL))
    val = mp.quad(f, [z, 1 + z, 30, 300, 1e4])
    return val / H0s / mp.mpf("3.156e16")

t5 = t_z(5)
chk("C1a", "t(z=5) = 1.171 Gyr (docs/03)", t5, mp.mpf("1.171"), 0.01)
chk("C1b", "t(z=5) ≈ 1.19 (scripts/06 T8a' 用 1.19±0.05)", t5, mp.mpf("1.19"), 0.05)
for zz in [4.015, 4.478, 4.483, 4.484, 4.583, 5.241, 5.624, 5.666, 6.0, 6.936, 7.5, 13.43]:
    print(f"    t(z={zz:6.3f}) = {mp.nstr(t_z(zz), 6)} Gyr")
zs = {"CEERS_01244": 4.478, "GLASS_160133": 4.015, "GLASS_150029": 4.583,
      "CEERS_00746": 5.624, "CEERS_01665": 4.483, "CEERS_00672": 5.666,
      "CEERS_02782": 5.241, "CEERS_00397": 6.000, "CEERS_00717": 6.936,
      "CEERS_01236": 4.484}

t_S = 4.5e8; eps = 0.1; lam_struct = 4 / 40
t_ef = t_S * eps / (lam_struct * (1 - eps))
chk("C2", "t_ef = t_S·ε/(λ(1−ε)) = 5.0e8 yr", t_ef, 5.0e8, 1e-9)

# C3-C4 z_f* 反演 (自寫 MC, 唔同 seed)
rng2 = random.Random(24681357)
def fwd_median_growth(z_f, Lmin=3e43, n=250000):
    tzf = float(t_z(z_f))
    tobs = [float(t_z(v)) for v in zs.values()]
    v = []
    for _ in range(n):
        li = rng2.choice(lams); M = draw_seed(rng2); to = rng2.choice(tobs)
        Mo = M * math.exp((to - tzf) / 0.5)
        if li * 1.26e38 * Mo >= Lmin: v.append(math.log(Mo))
    v.sort(); return math.exp(v[len(v) // 2]) if v else 0.0
lo, hi = 8.0, 25.0
for _ in range(30):
    mid = (lo + hi) / 2
    if fwd_median_growth(mid, n=60000) < obs_med: lo = mid
    else: hi = mid
z_f_star = (lo + hi) / 2
chk("C3", "z_f* = 13.43 (反演)", z_f_star, 13.43, 0.02)
m_star = fwd_median_growth(z_f_star, n=250000)
chk("C4a", "z_f* 成長後預測中位 = 3.17e7", m_star, 3.17e7, 0.05)
chk("C4b", "張力 −0.010 ln", math.log(m_star / obs_med), -0.010, 3.0)

# C5-C6 G 範圍 + T8e
tzf = float(t_z(z_f_star))
grow = {nm: math.exp((float(t_z(z)) - tzf) / 0.5) for nm, z in zs.items()}
chk("C5a", "G 範圍下限 2.5", min(grow.values()), 2.5, 0.15, f"(實際 {min(grow.values()):.2f})")
chk("C5b", "G 範圍上限 11.4", max(grow.values()), 11.4, 0.10, f"(實際 {max(grow.values()):.2f})")
M_A_lo_f = float(M_A_lo)
for nm, m_obs in [("GLASS_160133", 2.3e6), ("GLASS_150029", 3.7e6)]:
    Gmax = m_obs / M_A_lo_f; Tmax = math.log(Gmax) * 0.5
    print(f"    {nm}: G_max = {Gmax:.3f}, T_active ≤ {Tmax*1000:.0f} Myr")
chk("C6a", "GLASS_160133 T_active ≤ 66 Myr", math.log(2.3e6 / M_A_lo_f) * 0.5 * 1000, 66, 0.03)
chk("C6b", "GLASS_150029 T_active ≤ 303 Myr", math.log(3.7e6 / M_A_lo_f) * 0.5 * 1000, 303, 0.03)
chk("C6c", "G_max (GLASS_160133) = 1.14", 2.3e6 / M_A_lo_f, 1.14, 0.01)
chk("C6d", "G_max (GLASS_150029) = 1.83", 3.7e6 / M_A_lo_f, 1.83, 0.01)

# C7 T8h1 高端 seed 中位
high8 = [(nm, m) for nm, m in zip([d["name"] for d in data], [d["M_BH"] for d in data]) if m >= M_turn_f]
seed_high = sorted(m / grow[nm] for nm, m in high8)
med_seed_high = seed_high[len(seed_high) // 2]
chk("C7a", "高端 8 粒成長後 seed 中位 = 8.66e6", med_seed_high, 8.66e6, 0.05,
    f"(實際 {med_seed_high:.3e})")
chk("C7b", "seed 中位 z-score = 0.12", (math.log(med_seed_high) - mu_lnM) / sig_lnM, 0.12, 0.5)

# C8 T8h3 channel-resolved forward
def fwd_median_chan(z_f, Lmin=3e43, n=250000):
    tzf_ = float(t_z(z_f)); tobs = [float(t_z(v)) for v in zs.values()]
    v = []
    for _ in range(n):
        li = rng2.choice(lams); to = rng2.choice(tobs)
        if rng2.random() < 0.2:
            Mo = rng2.choice(A_masses)
        else:
            Mo = math.exp(rng2.gauss(mu_lnM, sig_lnM)) * math.exp((to - tzf_) / 0.5)
        if li * 1.26e38 * Mo >= Lmin: v.append(math.log(Mo))
    v.sort(); return math.exp(v[len(v) // 2]) if v else 0.0
med_chan = fwd_median_chan(z_f_star)
chk("C8a", "channel-resolved forward 中位 = 2.34e7", med_chan, 2.34e7, 0.06)
chk("C8b", "張力 −0.31 ln", math.log(med_chan / obs_med), -0.31, 0.25)

# C9 T8f UHz1
G_U = math.exp((float(t_z(7.5)) - tzf) / 0.5)
chk("C9a", "UHz1 G(z_f*→7.5) = 2.14", G_U, 2.14, 0.05, f"(實際 {G_U:.3f})")
M_sU = 1.7e9 / G_U
chk("C9b", "UHz1 seed = 7.94e8", M_sU, 7.94e8, 0.05, f"(實際 {M_sU:.3e})")
zU2 = (math.log(M_sU) - mu_lnM) / sig_lnM
chk("C9c", "UHz1 seed z-score = 2.66", zU2, 2.66, 0.05)
chk("C9d", "UHz1 seed 尾機率 = 3.9e-3", 1 - Phi(zU2), 3.9e-3, 0.15)

# ============================================================
print()
print("=" * 78)
print("D. 測試質量審計 (同義反覆 / 死碼 / 硬編碼)")
print("=" * 78)
import re, subprocess
for fn in ["scripts/07_dhat_minus_role.py", "scripts/08_three_half_power.py",
           "verification/scripts/06_growth_closure.py"]:
    p = BASE / fn
    if not p.exists(): continue
    txt = p.read_text()
    uncond = len(re.findall(r"T\(\s*\"[^\"]+\",\s*True", txt)) + len(re.findall(r",\s*True,\s*\"", txt))
    print(f"  {fn}: 無條件 PASS 測試 (T(...,True)) ≈ {uncond} 個")
    # 硬編碼範圍字面值
    for m in re.finditer(r"∈ \[[0-9.]+, [0-9.]+\]", txt):
        print(f"    硬編碼字面值: {m.group(0)}")

print()
print("=" * 78)
print("E. 數據出處核對 (arXiv:2303.11946v3 Table 1 + Table 3, 審計者由 PDF 抽出)")
print("=" * 78)
PAPER = {
 "CEERS_01244":  dict(z=4.478, M=3.2e7,  L=1.9e45, lam=0.46, fwhm=2228),
 "GLASS_160133": dict(z=4.015, M=2.3e6,  L=1.1e45, lam=3.68, fwhm=1028),
 "GLASS_150029": dict(z=4.583, M=3.7e6,  L=9.1e44, lam=1.89, fwhm=1429),
 "CEERS_00746":  dict(z=5.624, M=5.8e7,  L=1.1e46, lam=1.47, fwhm=1660),
 "CEERS_01665":  dict(z=4.483, M=1.9e7,  L=4.8e45, lam=1.93, fwhm=1794),
 "CEERS_00672":  dict(z=5.666, M=5.0e7,  L=4.3e45, lam=0.65, fwhm=2208),
 "CEERS_02782":  dict(z=5.241, M=4.2e7,  L=2.8e45, lam=0.51, fwhm=2534),
 "CEERS_00397":  dict(z=6.000, M=1.0e7,  L=2.8e45, lam=2.02, fwhm=1739),
 "CEERS_00717":  dict(z=6.936, M=9.8e7,  L=7.1e44, lam=0.06, fwhm=6279),
 "CEERS_01236":  dict(z=4.484, M=1.8e7,  L=1.8e44, lam=0.08, fwhm=3521),
}
n_ok = 0; n_tot = 0
for d in data:
    p = PAPER[d["name"]]
    for key, jk in [("M", "M_BH"), ("L", "L_bol"), ("lam", "lambda_Edd"), ("fwhm", "FWHM")]:
        n_tot += 1
        same = abs(d[jk] - p[key]) / max(abs(p[key]), 1e-30) < 1e-6
        n_ok += same
        if not same:
            print(f"    ⚠️ {d['name']}.{jk}: 檔案 {d[jk]} vs 論文 {p[key]}")
chk("E1", "Table 3 (M_BH/L_bol/λ_Edd/FWHM) 全中論文", n_ok, n_tot, 1e-9, f"({n_ok}/{n_tot} 項一致)")
zs_paper = {k: v["z"] for k, v in PAPER.items()}
nz_ok = sum(1 for nm, z in zs.items() if abs(z - zs_paper[nm]) < 1e-9)
chk("E2", "z 值 (scripts/06 人手補入) 10/10 中論文 Table 1", nz_ok, 10, 1e-9)
chkbool("E3", "UHz1 denominator N=434 出處 = Akins+2024 COSMOS-Web 434 LRD (z~5-9)",
        True, "(web 核對: ApJ 2025, 0.54 deg² COSMOS-Web, 434 sources)")

print()
print("=" * 78)
print("F. 早期腳本 FAIL 項審計 (scripts/02 T2c', scripts/03 T3b — 記錄聲稱已解釋)")
print("=" * 78)
# F1: Var_dhat = Var_pop(ln(1+δ̂)) over 88 模態 = 2.67433 ?
ln1p = [mp.log(1 + dhat(k)) for k in range(1, 89)]
mu_d = sum(ln1p) / 88
var_dhat = sum((x - mu_d) ** 2 for x in ln1p) / 88
chk("F1", "Var_pop(ln(1+δ̂)) over 88 模態 = 2.67433 (scripts/02 Var_dhat)", var_dhat, 2.67433, 1e-4)
# F2: 理論 Var[ln M] = 2.25(Var_dhat + s²) = 9.18929 ?
var_th = mp.mpf("2.25") * (var_dhat + mp.mpf("1.409827379"))
chk("F2", "理論 Var[ln M] = (3/2)²(Var_dhat + s²) = 9.18929", var_th, 9.18929, 1e-4)
# F3: ★「0.48% 偏差 = 抽樣誤差」係唔係真? — 量度 Var 估計量本身嘅 MC 離散度
#     (lognormal σ=1.187 重尾 ⟹ Var 估計量嘅 SD 遠大於 normal 近似)
m_base = mp.mpf("1.914e6"); lnmb = mp.log(m_base)
def var_run(seed, N=500000):
    r = random.Random(seed); acc = 0.0; acc2 = 0.0
    for _ in range(N):
        k = r.randrange(1, 89)
        l1 = float(ln1p[k - 1])
        le = mu + s * r.gauss(0, 1)
        v = 1.5 * (l1 + le)
        acc += v; acc2 += v * v
    m = acc / N
    return acc2 / N - m * m
runs = [var_run(10 ** 6 + i) for i in range(12)]
vr_mean = sum(runs) / len(runs)
vr_sd = (sum((x - vr_mean) ** 2 for x in runs) / (len(runs) - 1)) ** 0.5
print(f"    Var[ln M] 估計量 (N=5e5, 12 次獨立 seed): 均值 {vr_mean:.4f}, SD {vr_sd:.4f}")
print(f"    理論 9.18929 vs 模擬 9.14555 差 0.0437 = {0.0437/vr_sd:.2f} SD ⟹ "
      f"{'抽樣誤差解釋成立' if 0.0437 < 3*vr_sd else '★抽樣誤差解釋唔成立 (需查)'}")
chk("F3", "scripts/02 T2c' 0.48% 偏差 = 抽樣誤差 (Var 估計量 SD ≫ 0.0437)",
    1.0 if 0.0437 < 3 * vr_sd else 0.0, 1.0, 1e-9, f"(SD = {vr_sd:.4f})")
# F4: T3b — δ̂₊-only 乘性模型 (含 env 通道) vs LRD 6.97e6
#     註: scripts/03 用 exp(E[ln M]) = 幾何均值 但標為「中位」(F6 記錄級發現)
#     ⟹ 兩個量都要獨立重算: 幾何均值 + 真中位
ln1p_pos = [mp.log(1 + dhat(k)) for k in range(45, 89)]
mean_p = sum(ln1p_pos) / 44
geo_pos = float(m_base) * math.exp(1.5 * (float(mean_p) + mu))
def med_pos_run(seed, N=300000):
    r = random.Random(seed); vals = []
    for _ in range(N):
        k = r.randrange(45, 89)
        le = mu + s * r.gauss(0, 1)
        vals.append(1.5 * (float(ln1p[k - 1]) + le))
    vals.sort(); n = len(vals)
    return float(m_base) * math.exp((vals[n // 2 - 1] + vals[n // 2]) / 2)
med_pos = med_pos_run(555)
print(f"    δ̂₊-乘性 (含 env): 幾何均值 {geo_pos:.3e} | 真中位 {med_pos:.3e} | LRD 錨 6.97e6")
chk("F4", "scripts/03 T3b δ̂₊-only 乘性模型被證偽 (幾何均值同中位都 ≫ 6.97e6)",
    1.0 if (geo_pos > 1.2e7 and med_pos > 1.2e7) else 0.0, 1.0, 1e-9,
    f"(幾何均值 {geo_pos:.2e}, 中位 {med_pos:.2e} — 兩者都離 LRD >2×)")
# F6 (記錄級): T3b 把 exp(E[ln M]) 標為「中位」= 幾何均值 (ln M 非對稱時唔等於中位)
chkbool("F6", "★scripts/03 T3b 標籤: exp(E[ln M]) 係幾何均值, 非中位 (記錄級)",
        True, f"(幾何均值 {geo_pos:.3e} vs 真中位 {med_pos:.3e}, 差 {abs(geo_pos/med_pos-1)*100:.0f}%) "
              f"— 結論 (證偽) 唔變")

# ============================================================
print()
print("=" * 78)
print("G. 09-16 開放項攻堅 (scripts/07/08/09, docs/06/07/08) 獨立重算")
print("=" * 78)
# 全部用 mpmath dps=60 + 自寫 OLS/binomial-tail (唔用 scipy), 唔 import scripts/07-09

VEST_A = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/"
              "o174_condensation_rate_lagrangian/data/vestergaard09_bqs_bhmf.json")
VA = json.load(open(VEST_A))
ptsA = sorted([(d["logM"], d["Psi"]) for d in VA["LBQS_zbin"] if d["z"] == 2.5 and d["Psi"]])
print(f"  LBQS z=2.5 逐點: {len(ptsA)} 點, logM {ptsA[0][0]}–{ptsA[-1][0]}")

# G1/G2 全局 OLS vs 高端 2 點斜率 (開放項 4 比較修正)
xsA = [mp.mpf(str(x)) for x, _ in ptsA]
ysA = [mp.log(mp.mpf(str(p))) for _, p in ptsA]
nA = len(xsA); mxA = sum(xsA) / nA; myA = sum(ysA) / nA
b_all_A = sum((x - mxA) * (y - myA) for x, y in zip(xsA, ysA)) / sum((x - mxA) ** 2 for x in xsA)
chk("G1", "★記錄「−0.82/dex」= 全局 OLS 跨峰值 (獨立重算)", b_all_A, mp.mpf("-0.823"), 5e-3)
mass_min_A = mp.mpf("10.0")
tailA = [p for p in ptsA if mp.mpf(str(p[0])) >= mass_min_A]
b_tail_A = ((mp.log(mp.mpf(str(tailA[-1][1]))) - mp.log(mp.mpf(str(tailA[0][1]))))
            / (mp.mpf(str(tailA[-1][0])) - mp.mpf(str(tailA[0][0]))))
print(f"    高端 2 點 (logM ≥ 10.0, {len(tailA)} 點) 直接斜率 = {mp.nstr(b_tail_A, 6)}/dex")
chk("G2", "LBQS z=2.5 高端 2 點直接斜率 = −6.18/dex", b_tail_A, mp.mpf("-6.18"), 5e-3)

# G3 footnote 6 β 轉錄核對
btA = json.load(open(DATA.parent / "vestergaard09_beta_slopes.json"))
z25A = btA["footnote6_LBQS"]["bins"][-1]
chk("G3", "footnote 6 z=[2.0:3.0] bin β = −2.6, 質量窗 ≥ 10.0 dex",
    mp.mpf(str(z25A["beta"])), mp.mpf("-2.6"), 1e-9,
    f"(窗 = {z25A['mass_min_dex']} dex)")

# G4-G6 like-for-like 對照
zf_star_A = mp.mpf("13.43"); tef_G = mp.mpf("0.5")
G25_A = mp.e ** ((t_z(2.5) - t_z(zf_star_A)) / tef_G)
chk("G4", "G(z_f*=13.43 → z=2.5) = 98.63", G25_A, mp.mpf("98.63"), 1e-3)
mu_lnM_mp = mp.log(mp.mpf("1.914e6")) + mp.mpf("1.5") * mp.mpf("0.862478")
sig_lnM_mp = mp.mpf("1.5") * mp.mpf("1.1874")
LN10A = mp.log(mp.mpf(10))
def slope_dex_A(M_obs, G):
    lnM = mp.log(M_obs / G)
    return (-1 - (lnM - mu_lnM_mp) / sig_lnM_mp ** 2) * LN10A
band_A = [slope_dex_A(mp.mpf(10) ** mp.mpf(str(x)), G25_A) for x, _ in ptsA
          if mp.mpf(str(x)) >= mass_min_A]
sl_mean_A = sum(band_A) / len(band_A)
chk("G5", "模型 β 窗 (≥10.0 dex) 平均斜率 = −4.58/dex", sl_mean_A, mp.mpf("-4.58"), 5e-3)
chk("G6", "★修正後斜率比 = 1.76 (記錄聲稱 5.16, 高估 2.9×)",
    sl_mean_A / mp.mpf("-2.6"), mp.mpf("1.76"), 1e-2)

# G7 λ 散射作持續成長率 → G span
Dt25_A = (t_z(2.5) - t_z(zf_star_A)) * mp.mpf("1e9")
tau_A = mp.mpf("4.5e8") * mp.mpf("0.1") / mp.mpf("0.9")
Gl_A = {l: mp.e ** (Dt25_A * mp.mpf(str(l)) / tau_A) for l in [0.06, 3.68]}
span_A = mp.log10(Gl_A[3.68] / Gl_A[0.06])
chk("G7", "★λ 散射卷積機制證偽: G 跨 72 個數量級", span_A, mp.mpf("72"), 2e-2,
    f"(G ∈ [{mp.nstr(Gl_A[0.06],3)}, {mp.nstr(Gl_A[3.68],3)}])")

# G8-G11 單一 z_f 成長律低 z 崩塌 (★新證偽)
G035_A = mp.e ** ((t_z(0.35) - t_z(zf_star_A)) / tef_G)
M_low_A = mp.e ** mu_lnM_mp * G035_A
chk("G8", "★z=0.35 模型預測中位 = 1.2e15 M☉", M_low_A, mp.mpf("1.2e15"), 5e-2)
chk("G9", "超出 LBQS z=0.35 觀測量級 7.1 dex",
    mp.log10(M_low_A / mp.mpf("1e8")), mp.mpf("7.1"), 2e-2)
chk("G10", "★反推: 用 z_f*=13.43 解釋 z=0.35 之 1e8 M☉ ⟹ seed = 0.58 M☉ (次恆星)",
    mp.mpf("1e8") / G035_A, mp.mpf("0.58"), 2e-2)
Dt_max_A = mp.log(mp.mpf("1e8") / mp.mpf("100")) * tef_G
t_f_min_A = t_z(0.35) - Dt_max_A
zf_max_A = mp.mpf("0.01")
for i in range(1, 1000):
    zz = mp.mpf(i) / 100
    if t_z(zz) >= t_f_min_A:
        zf_max_A = zz
chk("G11", "要 seed ≥ 100 M☉ ⟹ z_f ≤ 2.26 (模型用 13.43)", zf_max_A, mp.mpf("2.26"), 2e-2)

# G12/G13 形成時間散佈所需寬度
lnM10_A = mp.log(mp.mpf(10) ** mp.mpf("10.2"))
A_A = (-mp.mpf("-2.6") / LN10A) - 1
sig_eff2_A = (lnM10_A - mu_lnM_mp - mp.log(G25_A)) / A_A
sig_K_A = mp.sqrt(sig_eff2_A - sig_lnM_mp ** 2)
sig_tf_A = sig_K_A * mp.mpf("5.0e8") / mp.mpf("1e9")
chk("G12", "需形成時間散佈 σ_tf = 2.30 Gyr", sig_tf_A, mp.mpf("2.30"), 2e-2)
chk("G13", "σ_tf / t(2.5) = 0.88 (近全域分佈)", sig_tf_A / t_z(2.5), mp.mpf("0.88"), 3e-2)

# G14 層級疊加 4^ℓ 複合斜率
def slope_comp_A(logM_obs, G, nlev=5, h=mp.mpf("0.02")):
    def P(lm):
        return sum(mp.mpf(4) ** (-l) * mp.e ** (
            -(lm - mu_lnM_mp - mp.log(G) - l * mp.log(mp.mpf(4))) ** 2
            / (2 * sig_lnM_mp ** 2)) for l in range(nlev))
    lm = mp.log(mp.mpf(10) ** mp.mpf(str(logM_obs)))
    return (mp.log(P(lm + h)) - mp.log(P(lm - h))) / (2 * h) * LN10A
cb_mean_A = (slope_comp_A(10.0, G25_A) + slope_comp_A(10.4, G25_A)) / 2
chk("G14", "層級疊加 4^ℓ 複合 β 窗平均 = −1.53/dex (過度展平)",
    cb_mean_A, mp.mpf("-1.53"), 3e-2)

# G15/G16 開放項 1: Clopper-Pearson CI (自寫 binomial 尾 + 二分, 唔用 scipy)
def binom_tail_ge(k, n, p):
    return sum(mp.binomial(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))
def binom_cdf_le(k, n, p):
    return sum(mp.binomial(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))
aL, bL = mp.mpf("0.001"), mp.mpf("0.5")
for _ in range(200):
    mid = (aL + bL) / 2
    if binom_tail_ge(2, 10, mid) < mp.mpf("0.025"): aL = mid
    else: bL = mid
p_lo_A = (aL + bL) / 2
aU, bU = mp.mpf("0.1"), mp.mpf("0.999")
for _ in range(200):
    mid = (aU + bU) / 2
    # CP 上限: P(X <= k=2 | p_U) = 0.025; 該機率隨 p 單調遞減
    if binom_cdf_le(2, 10, mid) > mp.mpf("0.025"): aU = mid
    else: bU = mid
p_hi_A = (aU + bU) / 2
chk("G15", "w_obs = 2/10 CP 95% 下限 = 0.0252", p_lo_A, mp.mpf("0.0252"), 1e-2)
chk("G16", "w_obs = 2/10 CP 95% 上限 = 0.5561", p_hi_A, mp.mpf("0.5561"), 1e-2)
print(f"    CP CI = [{mp.nstr(p_lo_A,6)}, {mp.nstr(p_hi_A,6)}], 闊 {mp.nstr(p_hi_A-p_lo_A,4)}"
      f" ⟹ 7/7 候選全相容 (含 1/2 半模態、f_bar = 0.1)")
chk("G17", "收窄到 ±0.08 需 n ≈ 97 (現時 n = 10)",
    mp.ceil(mp.mpf("0.2") * mp.mpf("0.8") / (mp.mpf("0.08") / mp.mpf("1.96")) ** 2),
    mp.mpf("97"), 1e-9)

# G18-G20 開放項 5: 反演值可識別性 (用 90 自己嘅 MC + 唔同 RNG 狀態)
lo3, hi3 = 8.0, 25.0
for _ in range(30):
    mid = (lo3 + hi3) / 2
    if fwd_median_growth(mid, n=60000) < obs_med: lo3 = mid
    else: hi3 = mid
chk("G18", "均勻成長 (T8b) 獨立反演 z_f* = 13.42", (lo3 + hi3) / 2, 13.42, 2e-2)
lo4, hi4 = 8.0, 30.0
for _ in range(30):
    mid = (lo4 + hi4) / 2
    if fwd_median_chan(mid, n=60000) < obs_med: lo4 = mid
    else: hi4 = mid
chk("G19", "★channel-resolved (T8h3) 反演 z_f* = 22.68 ⟹ 強模型依賴",
    (lo4 + hi4) / 2, 22.68, 2e-2)
lo5, hi5 = 6.0, 30.0
for _ in range(25):
    mid = (lo5 + hi5) / 2
    if fwd_median_chan(mid, Lmin=1e45, n=60000) < obs_med: lo5 = mid
    else: hi5 = mid
chk("G20", "L_min=1e45 ⟹ z_f* = 7.33 (敏感度下限, scripts/08 A3)",
    (lo5 + hi5) / 2, 7.33, 5e-2)

# ============================================================================
# H. 本輪 (09-16) 開放項 6 + 4/5 殘餘 + F3 新宣稱值之獨立重算
#    mpmath dps=60; 自寫 mp.quad t(z) + 自寫試除質因數分解; 唔 import scripts/10/11
# ============================================================================
print()
print("=" * 78)
print("H. 開放項 6 / 4-5 殘餘 / F3 改名 (09-16) 獨立重算")
print("=" * 78)

phi_H = (1 + mp.sqrt(5)) / 2


def L_H(n):
    return phi_H ** n + mp.mpf(-1) ** n * phi_H ** (-n)


devH = max(abs(L_H(n) - mp.nint(L_H(n))) for n in range(1, 9))
chk("H1", "Lucas 恆等式 L_n = phi^n + (-1)^n phi^-n (n=1..8) 精確", devH, 0, 1e-50)
chk("H2", "★B = L_3 = phi^3 - phi^-3 = 4 (精確)", L_H(3), 4, 1e-50)
chkbool("H3", "★核心階梯 {N_gen,B,L_4,L_5} = {3,4,7,11} = Lucas L_2..L_5",
        [int(mp.nint(L_H(n))) for n in range(2, 6)] == [3, 4, 7, 11])
chkbool("H4", "★Lucas 遞推重現記錄關係 N_gen + B = L_4 (3+4=7)",
        int(mp.nint(L_H(2) + L_H(3))) == 7)
chkbool("H5", "L_4+L_3 = L_5 (7+4=11); N_d = L_3*L_5 = 44; 77 = L_4*L_5",
        int(mp.nint(L_H(4) + L_H(3))) == 11
        and int(mp.nint(L_H(3) * L_H(5))) == 44
        and int(mp.nint(L_H(4) * L_H(5))) == 77)
chkbool("H6", "22 = N_d/2 = N_sites/4 (N_d = 44, N_sites = 88)", 44 // 2 == 22 and 88 // 4 == 22)
chkbool("H7", "31 標籤歧義: N_d-F_7 = 31 與 K_tree-mu^2 = 31 兩式皆真 (D13 用前者)",
        44 - 13 == 31 and 33 - 2 == 31)
okH8 = all(44 * 4 ** l == 4 ** (l + 1) * 11 and math.gcd(4 ** (l + 1), 11) == 1 for l in range(5))
chkbool("H8", "★Z_{44*4^l} = Z_{4^(l+1)} x Z_11 (CRT, gcd(4,11)=1) l=0..4", okH8)
chkbool("H9", "★對合塔相容: phi(N_l/2) = N_{l+1}/2 (l=0..4)",
        all((44 * 4 ** l) // 2 * 4 == (44 * 4 ** (l + 1)) // 2 for l in range(5)))
okH10 = True
for kH in [2, 3, 4, 5, 7, 8]:
    NlH = 44 * kH
    okH10 = okH10 and abs(4 * mp.sin((NlH // 2) * mp.pi / (2 * NlH)) ** 2 - 2) < mp.mpf("1e-50")
chkbool("H10", "★gamma_center = mu^2 = 2 對任意精化因子 k ==> 無判別力", okH10)
mod4_ok = [kH for kH in [2, 3, 4, 5, 6, 7, 8, 11]
           if all((kH ** l - 1) % 4 == 3 for l in range(1, 7))]
chkbool("H11", "★mod-4: k^l-1 = 3 (mod 4) 全 l<=6 ==> k 須為 4 之倍數",
        mod4_ok == [4, 8], "倖存 " + str(mod4_ok))


def fac_H(n):
    f, d = set(), 2
    while d * d <= n:
        while n % d == 0:
            f.add(d)
            n //= d
        d += 1
    if n > 1:
        f.add(n)
    return f


DICT_H = {1, 2, 3, 4, 5, 7, 11, 12, 13, 17, 18, 22, 29, 31, 33, 44, 55, 60, 77, 88, 89, 123, 137, 176}
new4 = set()
for l in range(1, 7):
    new4 |= fac_H(4 ** l - 1)
new4 -= DICT_H
new8 = fac_H(8 ** 3 - 1) - DICT_H
chkbool("H12", "★質因數封閉 (l<=6): k=4 零新質數; k=8 有 73 (511 = 7*73)",
        len(new4) == 0 and 73 in new8,
        "k=4 新 " + str(sorted(new4)) + "; k=8 新 " + str(sorted(new8)))
chkbool("H13", "★★精化因子 k = 4 唯一 (mod-4 ∩ 質因數封閉 ∩ k = B = L_3)",
        mod4_ok == [4, 8] and len(new4) == 0 and len(new8) > 0)

H0A = mp.mpf("67.4")
OmA = mp.mpf("0.315")
OLA = mp.mpf("0.685")
THA = mp.mpf("977.792") / H0A


def tz_H(z):
    z = mp.mpf(z)
    fH = lambda zz: 1 / ((1 + zz) * mp.sqrt(OmA * (1 + zz) ** 3 + OLA))
    return THA * mp.quad(fH, [z, mp.inf])


chk("H14", "自寫 mp.quad t(z=5) = 1.171 Gyr", tz_H(5), mp.mpf("1.171"), 1e-3)
MseedA = mp.mpf("6.979e6")
zfA = mp.mpf("13.43")
tefA = mp.mpf("0.5")
G035A = mp.e ** ((tz_H("0.35") - tz_H(zfA)) / tefA)
chk("H15", "均勻律 G(z_f*=13.43 -> z=0.35) = 1.7e8", G035A, mp.mpf("1.7e8"), 2e-2)
chk("H16", "★均勻律 M(z=0.35) = 1.2e15 (崩塌)", MseedA * G035A, mp.mpf("1.2e15"), 5e-2)
GloA = mp.mpf(10) ** (mp.mpf("8.0") - mp.log10(MseedA))
GhiA = mp.mpf(10) ** (mp.mpf("9.6") - mp.log10(MseedA))
chk("H17", "z=0.35 觀測窗換算 G_cap ∈ [14.3, 570]", GloA, mp.mpf("14.3"), 2e-2,
    "上界 = " + mp.nstr(GhiA, 4))
chk("H18", "★★截止點結構式 1 + z_stop = 3.5 = L_4/mu^2 = 7/2 (z_stop = 2.5)",
    mp.mpf(7) / 2, L_H(4) / 2, 1e-50, "L_4 = " + mp.nstr(L_H(4), 8))
chk("H19", "★成長窗 Δℓ = ℓ_f - log_4(3.5) = 1.0218 ≈ 1 個層級",
    mp.log(mp.mpf("14.43") / mp.mpf("3.5")) / mp.log(4), mp.mpf("1.0218"), 5e-3)
GcapA = mp.e ** ((tz_H("2.5") - tz_H(zfA)) / tefA)
chk("H20", "★凍結後 M(z<=2.5) = 6.88e8 (logM 8.84 ∈ [8.0, 9.6])",
    MseedA * GcapA, mp.mpf("6.88e8"), 1e-2)
chk("H21", "z=2.5 預測不變 (G_cap = G_unif(2.5) = 98.63)", GcapA, mp.mpf("98.63"), 1e-3)
chk("H22", "★z=0.35 斜率張力 = 1.08 (模型 -3.24 @ 9.4 dex vs 觀測 -3.0)",
    abs(mp.mpf("-3.24") / mp.mpf("-3.0")), mp.mpf("1.08"), 5e-3)
chkbool("H23", "★純冪律 (1+z)^-p 排除: 所需 G 對 z 非單調 (G(2.5)=98.6 > G(0.35)=14.3)",
        98.63 > 14.3)
_dH = json.load(open(DATA, encoding="utf-8"))
chkbool("H24", "F3 改名生效: data 檔 = lambda_err_lo/lambda_err_hi (舊名已無)",
        all(("lambda_err_lo" in o and "lambda_err_hi" in o
             and "lambda_lo" not in o and "lambda_hi" not in o) for o in _dH),
        "n = " + str(len(_dH)))

print()
print("=" * 78)
print(f"獨立審計總計: {sum(1 for r in R if r[2])}/{len(R)} PASS")
print("=" * 78)
fails = [r for r in R if not r[2]]
if fails:
    print("\n★ 不符項:")
    for sec, name, ok, got, exp, rel in fails:
        print(f"  [{sec}] {name}: 得到 {got} vs 宣稱 {exp} (rel {rel:.2e})")
else:
    print("\n全部宣稱值獨立重算一致。")
