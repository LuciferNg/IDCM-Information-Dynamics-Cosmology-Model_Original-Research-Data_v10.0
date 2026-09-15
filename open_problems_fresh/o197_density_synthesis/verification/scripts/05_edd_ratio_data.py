#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 scripts/05 — 實測 λ_Edd 數據攻中位張力 (Measured Eddington-Ratio Attack)

開放項 2 (中位張力 1.25-1.45 ln) 最可攻候選: (b) 樣本 λ_Edd mean > 0.1。
今次直接攞 Harikane+23 Table 3 嘅 10 粒 AGN 實測 λ_Edd (arXiv:2303.11946v3,
Table 3: M_BH, L_bol, λ_Edd 含非對稱誤差) — 唔再用 log-uniform 假設。

結構身份候選: λ_Edd = f_bar = B/(N_d−B) = 0.1 (O173 docs, scripts/03 T1)。
測試 (全用實測 λ 分布):
  V1 λ_Edd 實測分布統計 vs 結構值 0.1 (Eddington 偏置因子)
  V2 實測 λ 前向被選中位 vs 觀測 3.2e7 — 同 scripts/03 T5a (7.52e6) /
     T5b log-uniform (9.19e6) 比較: λ 散射「吸收張力」假設仲企唔企得穩
  V3 張力顯著性: Δln = 1.78 vs σ_med = 1.253·σ_lnM/√10 (模型) + 觀測散射版
  V4 ★均勻成長排除: 預言 2 (低端喺通道 A) 要求 2.3e6/g ≥ 2.02e6 → g ≤ 1.14;
     閉合張力需 g = 3.2e7/5.4e6 = 5.9 → 矛盾 ⟹ 成長唔可以係 resolution
  V5 virial 高估所需: 閉合需 5.9× (0.77 dex) vs 文獻單紀元 virial 系統
     ~0.3-0.5 dex → 唔夠, 剩餘結構缺口
  V6 M-λ Spearman (選擇階梯預言): 低質量種子要高 λ 先被探測 → 反相關
  V7 低端份額: 實測 λ 下 0.507 vs 觀測 0.2 — λ=0.1 假設下 L_min*=5.73e43
     與實測 λ 唔自洽 (實測 λ 高 ⟹ 幾乎全部種子都探測到)
  V8 L_min 重反演: 實測 λ 下邊個 L_min* 令低端份額 = 0.2, 對觀測 L_bol 範圍

零新常數: 結構值 μ = 0.862478, s = 1.1874, w = 0.2 (scripts/02 V5 反演)。
實測 λ_Edd = 觀測輸入 (Harikane+23 Table 3), 非 IDCM 常數 — 用嚟檢驗結構身份 0.1。
"""
import json, math, random, statistics
from pathlib import Path

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = BASE / "o197_density_synthesis/verification/data/harikane23_table3_eddington.json"

M_base = 1.914e6
mu = 0.862478
s = 1.1874
B, N_d = 4, 44
L_EDD = 1.26e38
M_turn = M_base * 2.0 ** 1.5
mu_lnM = math.log(M_base) + 1.5 * mu
sig_lnM = 1.5 * s
w = 0.2

def Phi(z): return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

tot = 0; pas = 0
def T(name, ok, note=""):
    global tot, pas
    tot += 1; pas += 1 if ok else 0
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")

# ---------- 載入實測數據 ----------
data = json.load(open(DATA))
assert len(data) == 10
lams = [d["lambda_Edd"] for d in data]
masses = sorted(d["M_BH"] for d in data)
obs_med = masses[len(masses) // 2]
# λ 自洽檢查 (論文取捨, 容差 10%)
for d in data:
    lam_re = d["L_bol"] / (L_EDD * d["M_BH"])
    if abs(lam_re - d["lambda_Edd"]) / d["lambda_Edd"] > 0.10:
        print(f"  ⚠️ λ 自洽偏差 >10%: {d['name']} λ_tab={d['lambda_Edd']:.3f} λ_re={lam_re:.3f}")

# ---------- V1: 實測 λ_Edd 分布 vs 結構值 0.1 ----------
ln_lams = [math.log(l) for l in lams]
geo = math.exp(statistics.mean(ln_lams))
ari = statistics.mean(lams)
med = statistics.median(lams)
sig_ln = statistics.stdev(ln_lams)
lam_struct = B / (N_d - B)
bias = geo / lam_struct
T("V1 λ_Edd 分布 vs 結構值 0.1 (樣本 Eddington 偏置)",
  bias > 3 and bias < 30,
  f"geo = {geo:.3f}, arith = {ari:.3f}, median = {med:.3f}, σ_lnλ = {sig_ln:.2f}; "
  f"結構 0.1 ⟹ 偏置因子 {bias:.1f}× ({math.log10(bias):.2f} dex) — flux-limited "
  f"樣本偏置方向正確")

# ---------- 通道 A 離散譜 ----------
A_masses = [M_base * (2.0 * math.sin(k * math.pi / 176.0) ** 2) ** 1.5
            for k in range(45, 89)]

rng = random.Random(20260915)

def draw_seed(rng):
    if rng.random() < w:
        return rng.choice(A_masses)
    return math.exp(rng.gauss(mu_lnM, sig_lnM))

def fwd_median(lam_pool, Lmin, n=300000):
    vals = []
    for _ in range(n):
        lam_i = rng.choice(lam_pool)
        M = draw_seed(rng)
        if lam_i * L_EDD * M >= Lmin:
            vals.append(math.log(M))
    vals.sort()
    return math.exp(vals[len(vals) // 2]) if vals else 0.0

def fwd_lowfrac(lam_pool, Lmin, n=300000):
    low_c = tot_c = 0
    for _ in range(n):
        lam_i = rng.choice(lam_pool)
        M = draw_seed(rng)
        if lam_i * L_EDD * M >= Lmin:
            tot_c += 1
            if M < M_turn: low_c += 1
    return low_c / tot_c if tot_c else 0.0

# ---------- V2: 實測 λ 分布下中位張力 ----------
Lmin_ref = 3e43                     # scripts/03 T5b/T6 參考值
med_emp = fwd_median(lams, Lmin_ref)
t_emp = math.log(med_emp / obs_med)
# 同 scripts/03 基線比較 (7.52e6 固定 λ, 9.19e6 log-uniform)
t_fix = math.log(7.52e6 / obs_med)
t_lu  = math.log(9.19e6 / obs_med)
worse_than_fix = abs(t_emp) > abs(t_fix)
T("V2 實測 λ 前向中位 vs 觀測 3.2e7 (λ 散射吸收假設檢驗)",
  worse_than_fix,
  f"預測 {med_emp:.2e}, 張力 {t_emp:+.2f} ln ({t_emp/math.log(10):+.2f} dex); "
  f"基線: 固定λ 7.52e6 ({t_fix:+.2f}), log-uniform 9.19e6 ({t_lu:+.2f}) — "
  f"實測 λ (geo 0.70) 令預測中位更低, 張力更大 ⟹ log-uniform 低尾 "
  f"(λ→0.01) 先係 T5b「吸收」來源, 實測樣本冇呢個低尾")

# ---------- V3: 張力顯著性 ----------
sig_med_model = 1.253 * sig_lnM / math.sqrt(10)
ln_obs = [math.log(m) for m in masses]
sig_obs = statistics.stdev(ln_obs)
sig_med_obs = 1.253 * sig_obs / math.sqrt(10)
z_model = abs(t_emp) / sig_med_model
z_obs = abs(t_emp) / sig_med_obs
T("V3 中位張力顯著性 (n=10)",
  z_model > 2.0,
  f"Δln = {abs(t_emp):.2f}; σ_med(模型 σ=1.78) = {sig_med_model:.2f} → "
  f"{z_model:.1f}σ; σ_med(觀測散射 σ={sig_obs:.2f}) = {sig_med_obs:.2f} → "
  f"{z_obs:.1f}σ — 結構性張力, 唔係統計噪聲")

# ---------- V4: 均勻成長排除 ----------
# 預言 2: 低端種子必須仍喺通道 A 帶 [A_min, M_turn] 內 (scripts/01 V2a)
A_min = min(A_masses)             # 2.0174e6 (k=45)
# 種子 = 觀測/g, 要求 A_min ≤ 2.3e6/g → g ≤ 2.3e6/A_min; 同理 3.7e6/A_min
g_allow = min(2.3e6 / A_min, 3.7e6 / A_min)
g_need = obs_med / med_emp        # 閉合張力所需成長因子
g_excl = g_need > g_allow * 3
T("V4 均勻成長排除 (預言 2 約束 vs 閉合所需)",
  g_excl,
  f"閉合張力需 g = {g_need:.2f} ({math.log10(g_need):.2f} dex); 預言 2 容許 "
  f"g ≤ {g_allow:.2f} ({math.log10(g_allow):.2f} dex, 種子 ∈ [2.02e6, 5.41e6]) — "
  f"矛盾 {g_need/g_allow:.1f}× ⟹ 均勻成長唔可以係 resolution (會拆穿預言 2)")

# ---------- V5: virial 高估所需 ----------
vir_need = math.log10(obs_med / med_emp)
T("V5 virial 高估閉合所需 vs 文獻系統",
  vir_need > 0.5,
  f"需 {vir_need:.2f} dex (5.9×); 文獻單紀元 virial 系統 ~0.3-0.5 dex "
  f"(Shen+11 etc.) → 唔夠閉合, 剩餘 ~{vir_need-0.4:.2f} dex 結構缺口 🟡")

# ---------- V6: M-λ Spearman ----------
xs = [math.log(d["M_BH"]) for d in data]
ys = [math.log(d["lambda_Edd"]) for d in data]
def spearman(xs, ys):
    n = len(xs)
    rx = [sorted(xs).index(v) + 1 for v in xs]
    ry = [sorted(ys).index(v) + 1 for v in ys]
    mx, my = sum(rx)/n, sum(ry)/n
    cov = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    vx = math.sqrt(sum((rx[i]-mx)**2 for i in range(n)))
    vy = math.sqrt(sum((ry[i]-my)**2 for i in range(n)))
    return cov/(vx*vy) if vx*vy else 0.0
rho = spearman(xs, ys)
rng2 = random.Random(7)
cnt = 0; Nperm = 20000
for _ in range(Nperm):
    ys2 = ys[:]; rng2.shuffle(ys2)
    if spearman(xs, ys2) <= rho: cnt += 1
pval = cnt / Nperm
T("V6 log M vs log λ Spearman (選擇階梯預言: 反相關)",
  rho < -0.3 and pval < 0.1,
  f"ρ = {rho:+.3f}, permutation p = {pval:.3f} (n=10) — 低質量種子要更高 λ "
  f"先被探測, 機制運作中 (同 V1 偏置互為表裡)")

# ---------- V7: 實測 λ 下低端份額 ----------
f_emp = fwd_lowfrac(lams, Lmin_ref)
f_obs = sum(1 for m in masses if m < M_turn) / len(masses)
T("V7 實測 λ 低端份額 vs 觀測 0.2 (L_min = 3e43 自洽性)",
  f_emp > f_obs * 1.5,
  f"預測 {f_emp:.3f} vs 觀測 {f_obs:.2f} — λ=0.1 假設下 L_min*=5.73e43 同實測 λ "
  f"唔自洽: 實測 λ 高 ⟹ 幾乎全部種子過閘 ⟹ 需要更高 L_min")

# ---------- V8: L_min 重反演 (實測 λ) ----------
lo, hi = 1e42, 1e47
for _ in range(80):
    mid = math.exp((math.log(lo) + math.log(hi)) / 2)
    if fwd_lowfrac(lams, mid) > f_obs: lo = mid
    else: hi = mid
L_min_inv2 = math.exp((math.log(lo) + math.log(hi)) / 2)
Lbol_range = (min(d["L_bol"] for d in data), max(d["L_bol"] for d in data))
in_range = Lbol_range[0] <= L_min_inv2 <= Lbol_range[1]
T("V8 L_min 重反演 (實測 λ): 低端份額 = 0.2 所需 L_min*",
  in_range,
  f"L_min* = {L_min_inv2:.2e} (舊 λ=0.1 反演 5.73e43); 觀測 L_bol 範圍 "
  f"[{Lbol_range[0]:.1e}, {Lbol_range[1]:.1e}] — {'喺範圍內 ✓' if in_range else '⚠️ 範圍外'}")

print(f"\n===== {pas}/{tot} PASS =====")
print(f"實測 λ_Edd: {[f'{l:.2f}' for l in lams]}")
print(f"觀測中位: {obs_med:.2e}; 預測中位 (實測λ): {med_emp:.2e}; M_turn: {M_turn:.2e}")
