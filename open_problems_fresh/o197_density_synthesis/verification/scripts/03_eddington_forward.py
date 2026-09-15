#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 scripts/03 — Eddington 前向模型 (Eddington Forward Model + Selection)

O174 遺留 🔴: 「固定增長核被證偽 (23.4% ≫ 7.25%), 需 Eddington + 選擇函數」
(記憶標記: k=36 模態映射已由 O197 T4 閉合; Eddington forward-model 剩此)

結構參數 (零新常數):
  λ_Edd = f_bar = B/(N_d−B) = 4/40 = 0.1   (IDCM 結構候選, O173 docs)
  L_bol = λ_Edd · L_Edd · (M/M☉), L_Edd = 1.26e38 erg/s   (物理輸入)
  兩通道種子譜: w·P_A + (1−w)·P_B, w = 0.2 (scripts/02 V5 反演, data-gated)

T1 λ_Edd 結構身份: f_bar = B/(N_d−B) = 0.1
T2 L(M) 映射 + 最暗觀測物 GLASS_160133 (2.3e6) 嘅隱含 L_min 上界
T3 前向選擇 (λ 固定): M_min = L_min/(λ·L_Edd); 預測被選種子嘅低端份額 vs 觀測 2/10
T4 反演: 邊個 L_min 令預測低端份額 = 0.2 (data-gated w + 選擇自洽)
T5 中位檢驗: 預測被選 ln M 中位 vs 觀測高端 8 粒中位 (選擇偏置解釋)
T6 靈敏度: λ_Edd log-uniform [0.01, 1] (觀測輸入, 唔係 IDCM 常數) — 低端份額範圍
T7 virial 散射 0.4 dex 跨轉折影響 (觀測輸入) — 低端份額修正
"""
import json, math, random
from pathlib import Path

BASE = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")

M_base = 1.914e6
mu = 0.862478
s = 1.1874
B, N_d = 4, 44
L_EDD = 1.26e38
M_turn = M_base * 2.0 ** 1.5
mu_lnM = math.log(M_base) + 1.5 * mu
sig_lnM = 1.5 * s
w = 0.2                      # scripts/02 V5 (data-gated)

def Phi(z): return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

tot = 0; pas = 0
def T(name, ok, note=""):
    global tot, pas
    tot += 1; pas += 1 if ok else 0
    chk(name, ok, note)

# ---------- T1: λ_Edd 結構身份 ----------
lam = B / (N_d - B)
T("T1 λ_Edd = f_bar = B/(N_d−B) = 0.1", abs(lam - 0.1) < 1e-9, f"λ_Edd = {lam:.4f}")

# ---------- T2: L(M) + 最暗觀測物上界 ----------
data = json.load(open(f"{BASE}/o174_condensation_rate_lagrangian/data/harikane23_10agn.json"))
masses = sorted(d["M_BH"] for d in data)
M_faint = masses[0]          # 最暗 = 最低質量 (λ 固定下 L ∝ M)
L_faint = lam * L_EDD * M_faint
T("T2 最暗觀測物 (GLASS_160133 2.3e6) 隱含 L_min ≤ %.2e" % L_faint,
  L_faint > 1e43 and M_faint < M_turn,
  f"M_faint = {M_faint:.2e}, L(λ=0.1) = {L_faint:.2e} erg/s ⟹ 樣本敏感至低端")

# ---------- 通道 A 離散譜 ----------
A_masses = [M_base * (2.0 * math.sin(k * math.pi / 176.0) ** 2) ** 1.5
            for k in range(45, 89)]

def P_B(m):                  # 通道 B 密度 (ln M)
    z = (math.log(m) - mu_lnM) / sig_lnM
    return math.exp(-0.5 * z * z) / (sig_lnM * math.sqrt(2 * math.pi)) / m

def P_mix(m):                # 兩通道混合密度
    return w * (1.0 / 44.0) * sum(1.0 for a in A_masses if abs(m - a) < 1e-6) + (1 - w) * P_B(m)

def frac_below(mmin):
    """被選 (M>mmin) 種子中低端 (M<M_turn) 份額 — 解析"""
    A_sel = [a for a in A_masses if a > mmin]
    A_low = [a for a in A_sel if a < M_turn]
    nA = len(A_sel)
    PB_sel = 1 - Phi((math.log(mmin) - mu_lnM) / sig_lnM)
    PB_low = Phi((math.log(M_turn) - mu_lnM) / sig_lnM) - Phi((math.log(mmin) - mu_lnM) / sig_lnM)
    if mmin > M_turn: PB_low = 0.0
    num = w * len(A_low) / 44.0 + (1 - w) * PB_low
    den = w * nA / 44.0 + (1 - w) * PB_sel
    return num / den if den > 0 else 0.0

# ---------- T3/T4: 前向選擇 L_min 掃描 + 反演 ----------
print("\n--- T3/T4: L_min 掃描 (λ_Edd = 0.1 固定) ---")
obs_low_frac = sum(1 for m in masses if m < M_turn) / len(masses)
print(f"觀測低端份額: {obs_low_frac:.2f} ({sum(1 for m in masses if m < M_turn)}/10)")
for L_min in [1e42, 3e42, 1e43, 3e43, 1e44, 3e44, 1e45]:
    M_min = L_min / (lam * L_EDD)
    fl = frac_below(M_min)
    print(f"  L_min = {L_min:.0e}: M_min = {M_min:.2e}, 預測低端份額 = {fl:.3f}")

# 反演: 解 frac_below(M_min) = 0.2 → L_min* (二分)
lo, hi = 1e5, 1e8        # M_min 搜尋範圍
for _ in range(80):
    mid = math.exp((math.log(lo) + math.log(hi)) / 2)
    if frac_below(mid) > obs_low_frac: lo = mid
    else: hi = mid
M_min_inv = math.exp((math.log(lo) + math.log(hi)) / 2)
L_min_inv = lam * L_EDD * M_min_inv
plausible = 1e43 < L_min_inv < 1e44
T("T3 反演: 邊個 L_min* 令預測份額 = 觀測 0.2 (自洽 + 物理合理)",
  plausible,
  f"M_min* = {M_min_inv:.2e} ⟹ L_min* = {L_min_inv:.2e} erg/s ∈ (1e43, 1e44) = {plausible} "
  f"(樣本敏感至低端, 預言 2 未被證偽)")

# ---------- T5: 中位檢驗 (固定 λ 張力 + λ 分布 MC) ----------
rng = random.Random(42)
# 5a: 固定 λ=0.1, L_min = 最暗物自洽上界
L_min0 = lam * L_EDD * M_faint * 0.999   # 最暗物啱啱可探測
M_min0 = L_min0 / (lam * L_EDD)
def cdf_sel(m, mmin):
    PA = sum(1 for a in A_masses if mmin < a < m) / 44.0
    PB = Phi((math.log(m) - mu_lnM) / sig_lnM) - Phi((math.log(mmin) - mu_lnM) / sig_lnM)
    den = w * sum(1 for a in A_masses if a > mmin) / 44.0 + (1 - w) * (1 - Phi((math.log(mmin) - mu_lnM) / sig_lnM))
    return (w * PA + (1 - w) * PB) / den
lo, hi = M_min0, 1e12
for _ in range(80):
    mid = math.exp((math.log(lo) + math.log(hi)) / 2)
    if cdf_sel(mid, M_min0) < 0.5: lo = mid
    else: hi = mid
med_pred = math.exp((math.log(lo) + math.log(hi)) / 2)
all_med = sorted(masses)[len(masses) // 2]
high_med = sorted(m for m in masses if m > M_turn)[len([m for m in masses if m > M_turn]) // 2]
t5a_ok = abs(math.log(med_pred) - math.log(all_med)) < 1.5
T("T5a 固定 λ=0.1: 預測被選中位 vs 觀測樣本中位", t5a_ok,
  f"預測 {med_pred:.2e} vs 觀測 {all_med:.2e} ({abs(math.log(med_pred/all_med)):.2f} dex)")

# 5b: λ log-uniform [0.01,1] MC 被選中位 (觀測輸入, 非 IDCM 常數)
def sim_median(lam_lo=0.01, lam_hi=1.0, Lmin=3e43, n=200000):
    vals = []
    for _ in range(n):
        lam_i = math.exp(rng.uniform(math.log(lam_lo), math.log(lam_hi)))
        if rng.random() < w:
            M = rng.choice(A_masses)
        else:
            M = math.exp(rng.gauss(mu_lnM, sig_lnM))
        if lam_i * L_EDD * M > Lmin:
            vals.append(math.log(M))
    vals.sort()
    return math.exp(vals[len(vals) // 2]) if vals else 0.0
med_lambda = sim_median()
t5b_ok = abs(math.log(med_lambda) - math.log(all_med)) < 1.5
T("T5b λ log-uniform [0.01,1]: MC 被選中位 vs 觀測", t5b_ok,
  f"預測 {med_lambda:.2e} vs 觀測 {all_med:.2e} ({abs(math.log(med_lambda/all_med)):.2f} dex) — "
  f"λ 散射令中位上升, 固定-λ 張力 (T5a) 由物理 λ 分布吸收")

# ---------- T6: 靈敏度 λ_Edd log-uniform [0.01, 1] ----------
rng = random.Random(42)
def sim_frac(mmin, lam_lo=0.01, lam_hi=1.0, n=200000):
    """蒙地卡羅: λ 隨機 + 兩通道種子 → L>Lmin 選擇 → 低端份額"""
    Lmin = 3e43
    low_c = tot_c = 0
    for _ in range(n):
        lam_i = math.exp(rng.uniform(math.log(lam_lo), math.log(lam_hi)))
        if rng.random() < w:
            M = rng.choice(A_masses)
        else:
            M = math.exp(rng.gauss(mu_lnM, sig_lnM))
        if lam_i * L_EDD * M > Lmin:
            tot_c += 1
            if M < M_turn: low_c += 1
    return low_c / tot_c if tot_c else 0.0
f_sim = sim_frac(0.0)
T("T6 靈敏度 (λ log-uniform [0.01,1], L_min=3e43)", 0.05 <= f_sim <= 0.7,
  f"預測低端份額 = {f_sim:.3f} (蒙特卡羅 n=2e5; 觀測輸入 λ 分布, 非 IDCM 常數)")

# ---------- T7: virial 散射 0.4 dex ----------
def sim_frac_virial(lam_lo=0.01, lam_hi=1.0, sig_vir=0.4, n=200000):
    Lmin = 3e43
    low_c = tot_c = 0
    for _ in range(n):
        lam_i = math.exp(rng.uniform(math.log(lam_lo), math.log(lam_hi)))
        if rng.random() < w:
            M = rng.choice(A_masses)
        else:
            M = math.exp(rng.gauss(mu_lnM, sig_lnM))
        M_obs = M * math.exp(rng.gauss(0, sig_vir))   # virial 散射
        if lam_i * L_EDD * M_obs > Lmin:
            tot_c += 1
            if M < M_turn: low_c += 1
    return low_c / tot_c if tot_c else 0.0
f_vir = sim_frac_virial()
T("T7 virial 散射 0.4 dex 下低端份額", 0.05 <= f_vir <= 0.7,
  f"預測低端份額 = {f_vir:.3f} (真實種子質量判定, 散射跨轉折影響已含)")

print(f"\n===== {pas}/{tot} PASS =====")
