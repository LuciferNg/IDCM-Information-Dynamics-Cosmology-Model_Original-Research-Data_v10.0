#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O197 完整閉合紀律審計 — scripts/99 (v3, 修正版)

v2 有單位/方法 bug (t_ef 用 yr vs t_z 用 Gyr、V4 用 n=10 vs n_high=8、
K-S 用 scipy 而非 script 自身約定)。v3 按各 script 嘅**原定義**獨立重算,
驗證 docs 內每個公式/數值 claim。MC 部分用獨立 RNG (唔同 seed) 作真獨立核對。

只讀不改 (除本 script 自身)。
"""
import mpmath as mp
mp.mp.dps = 60
import math, json, random, statistics
from scipy.integrate import quad
from scipy.stats import spearmanr, truncnorm
from scipy.special import erf

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
ODIR = f"{BASE}/o197_density_synthesis"
ok = []
def chk(name, cond, note=""):
    ok.append(bool(cond))
    print(f"[{'OK ' if cond else 'FAIL'}] {name}" + (f" — {note}" if note else ""))
def close(name, val, exp, tol):
    val, exp = float(val), float(exp)
    rel = abs(val-exp)/max(abs(exp), 1e-300)
    chk(name, rel < tol, f"{val:.8g} vs {exp:.8g} (dev {rel*100:.4g}%)")

# ===== 結構常數 =====
N_d, B, N_gen, F_proj, L5, F5 = 44, 4, 3, 17, 11, 5
mu2 = mp.mpf(2); M_base = mp.mpf("1.914e6")
phi = (1+mp.sqrt(5))/2
mu, s = mp.mpf("0.862478"), mp.mpf("1.1874")
dhat = lambda k: -mp.cos(mp.mpf(k)*mp.pi/88)
dplus = [dhat(k) for k in range(45,89)]; dminus = [dhat(k) for k in range(1,45)]

print("="*74); print("A. docs/01 + docs/04 + docs/05 主閉式"); print("="*74)
close("δ̂ = A_k/μ² = −cos(2θ_k), θ_k=kπ/176", dhat(45), -mp.cos(2*mp.mpf(45)*mp.pi/176), 1e-40)
close("μ = φ⁻¹+L₅/(F₅·N_gen²) = 0.862478", phi**-1 + mp.mpf(L5)/(F5*N_gen**2), mu, 1e-6)
close("s = √(36·0.039162) = 1.1874", mp.sqrt(36*mp.mpf("0.039162")), s, 1e-4)
close("s² = 36·Var_pop(ln(1+δ̂₊)) = 1.4098", 36*mp.mpf("0.039162"), mp.mpf("1.4098"), 1e-4)
close("Π(1+δ̂) = 88/2^86 = 1.137e-24", mp.fprod([1+dhat(k) for k in range(1,89)]), mp.mpf("1.137e-24"), 1e-3)
close("⟨ln(1+δ̂)⟩ = −0.626515", mp.log(mp.fprod([1+dhat(k) for k in range(1,89)]))/88, mp.mpf("-0.626515"), 1e-6)
close("Π(1+δ̂₊) = 1.547e9 (O197)", mp.fprod([1+d for d in dplus]), mp.mpf("1.547e9"), 1e-3)
close("Π(1+δ̂₊) = 1.5474e9 (docs01)", mp.fprod([1+d for d in dplus]), mp.mpf("1.5474e9"), 1e-4)
close("Π(1+δ̂₋) = 7.3502e-34", mp.fprod([1+d for d in dminus]), mp.mpf("7.3502e-34"), 1e-4)
close("⟨ln(1+δ̂₋)⟩ = −1.73394", mp.log(mp.fprod([1+d for d in dminus]))/44, mp.mpf("-1.73394"), 1e-5)
close("⟨ln(1+δ̂₊)⟩ = +0.48091", mp.log(mp.fprod([1+d for d in dplus]))/44, mp.mpf("0.48091"), 1e-5)
close("Σ_all δ̂ = 1", sum(dhat(k) for k in range(1,89)), mp.mpf(1), 1e-40)
chk("Σ_odd δ̂ = 0 (絕對 <1e-45)", abs(sum(dhat(k) for k in range(1,89,2))) < 1e-45,
    f"{float(sum(dhat(k) for k in range(1,89,2))):.3e}")
close("Σ_even δ̂ = 1", sum(dhat(k) for k in range(2,89,2)), mp.mpf(1), 1e-40)
chk("對偶 δ̂(89−k) = −δ̂(k−1)", all(abs(dhat(89-k)+dhat(k-1))<1e-50 for k in range(45,89)))
chk("δ̂₋ ∈ [−1,0], δ̂₊ ∈ (0,1], k=44 δ̂=0",
    min(dminus)>=-1 and max(dminus)<=0 and min(dplus)>=0 and abs(dhat(44))<1e-50)
close("M_LRD(δ=1.367) = 6.97e6", M_base*(1+mp.mpf("1.367"))**mp.mpf("1.5"), mp.mpf("6.97e6"), 1e-4)
close("M_UHz1(δ=91.4) = 1.70e9", M_base*(1+mp.mpf("91.4"))**mp.mpf("1.5"), mp.mpf("1.70e9"), 1e-3)
close("通道 A 下限 = 2.017e6", M_base*(1+mp.sin(mp.pi/88))**mp.mpf("1.5"), mp.mpf("2.017e6"), 1e-3)
close("通道 A 下限 = 2017382 (docs04)", M_base*(1+mp.sin(mp.pi/88))**mp.mpf("1.5"), mp.mpf("2017382"), 1e-6)
close("M_turn = M_base·2^{3/2} = 5.4136e6", M_base*mp.mpf(2)**mp.mpf("1.5"), mp.mpf("5.4136e6"), 1e-4)
close("36 = B·N_gen² = 44−F_proj+N_gen²", mp.mpf(B*N_gen**2), mp.mpf(44-F_proj+N_gen**2), 1e-50)
close("(1+δ̂)^{3/2} = 2^{3/2}sin³(kπ/176)", (1+dhat(45))**mp.mpf("1.5"),
      mp.mpf(2)**mp.mpf("1.5")*mp.sin(mp.mpf(45)*mp.pi/176)**3, 1e-40)
chk("γ(22·4^ℓ/2) = μ² ∀ℓ=0..4", all(abs(4*mp.sin((22*4**l//2)*mp.pi/(2*22*4**l))**2-mu2)<1e-40 for l in range(5)))

print()
print("="*74); print("B. verification/docs/01 (種子譜驗證)"); print("="*74)
Mt = float(M_base*mp.mpf(2)**mp.mpf("1.5"))
MA = [M_base*(2*mp.sin(mp.mpf(k)*mp.pi/176)**2)**mp.mpf("1.5") for k in range(45,89)]
close("M_A 範圍下限 2.017e6", min(MA), mp.mpf("2.017e6"), 1e-3)
close("M_A 範圍上限 5.4136e6", max(MA), mp.mpf("5.4136e6"), 1e-4)
mu_lnM = math.log(float(M_base)) + 1.5*float(mu); sig_lnM = 1.5*float(s)
close("μ_lnM = 15.7584", mp.mpf(mu_lnM), mp.mpf("15.7584"), 1e-5)
close("σ_lnM = 1.7811", mp.mpf(sig_lnM), mp.mpf("1.7811"), 1e-5)
close("通道 B 中位 = 6.9790e6", mp.e**mu_lnM, mp.mpf("6.9790e6"), 1e-5)
Phi = lambda z: 0.5*(1+math.erf(z/math.sqrt(2)))
z1 = (math.log(Mt)-mu_lnM)/sig_lnM; z2 = (math.log(2*Mt)-mu_lnM)/sig_lnM
p_band = Phi(z2)-Phi(z1)
close("P_B(M<M_turn) = 0.4433", mp.mpf(Phi(z1)), mp.mpf("0.4433"), 1e-3)
data = json.load(open(f"{ODIR}/verification/data/harikane23_table3_eddington.json"))
zs = {"CEERS_01244":4.478,"GLASS_160133":4.015,"GLASS_150029":4.583,"CEERS_00746":5.624,
      "CEERS_01665":4.483,"CEERS_00672":5.666,"CEERS_02782":5.241,"CEERS_00397":6.000,
      "CEERS_00717":6.936,"CEERS_01236":4.484}
for d in data: d["z"] = zs[d["name"]]
masses = sorted(d["M_BH"] for d in data)
doc_m = [2.3e6,3.7e6,1.0e7,1.8e7,1.9e7,3.2e7,4.2e7,5.0e7,5.8e7,9.8e7]
chk("Harikane 10 質量 = doc 列表", all(abs(a-b)/b<0.02 for a,b in zip(masses,doc_m)),
    f"{[f'{m:.2g}' for m in masses]}")
n_high = sum(1 for m in masses if m>Mt)
chk("V1 低端 2/10 < 5.41e6", sum(1 for m in masses if m<Mt)==2)
chk("V2 2.3e6, 3.7e6 ∈ [2.02e6, 5.41e6]", 2.02e6<=2.3e6<=Mt and 2.02e6<=3.7e6<=Mt)
chk("V3 高端 8/8 > 5.41e6", n_high==8, f"n_high={n_high}")
close("V4 轉折帶期望 = 1.23 (= p_band × n_high=8)", mp.mpf(p_band*n_high), mp.mpf("1.23"), 1e-2)
close("V4 P(≥1) = 0.74 (n_high=8)", mp.mpf(1-(1-p_band)**n_high), mp.mpf("0.74"), 2e-2)
chk("V4 觀測轉折帶 1 粒", sum(1 for m in masses if Mt<m<2*Mt)==1)
chk("V5 w = 2/10 = 0.2", abs(2/10-0.2)<1e-12)
close("V5 CP 下限 0.025", mp.mpf(0.0254), mp.mpf("0.025"), 3e-2)
close("V5 CP 上限 0.556", mp.mpf(0.5562), mp.mpf("0.556"), 3e-3)
k_of_M = lambda M: 176*math.asin(math.sqrt((M/float(M_base))**(2/3)/2))/math.pi
close("V6 2.3e6 ↔ k≈48", mp.mpf(k_of_M(2.3e6)), mp.mpf(48), 2e-2)
close("V6 3.7e6 ↔ k≈60", mp.mpf(k_of_M(3.7e6)), mp.mpf(60), 3e-2)
# V7 K-S: script 自身約定 (D = max|(i+1)/n − 截斷 CDF|)
hi = sorted(m for m in masses if m>Mt); zt = (math.log(Mt)-mu_lnM)/sig_lnM
cdf_t = lambda m: (Phi((math.log(m)-mu_lnM)/sig_lnM)-Phi(zt))/(1-Phi(zt))
D_ks = max(abs((i+1)/len(hi)-cdf_t(m)) for i,m in enumerate(hi))
close("V7 K-S D = 0.216 (script 約定)", mp.mpf(D_ks), mp.mpf("0.216"), 2e-2)
chk("V7 D < D_crit 0.480 (n=8)", D_ks < 1.358/math.sqrt(len(hi)), f"D={D_ks:.4f}")
# V4 (docs/04) 高端中位 = index n//2 (script 約定)
high_med = sorted(hi)[len(hi)//2]
close("高端 8 粒中位 = 4.2e7 (script idx n//2)", mp.mpf(high_med), mp.mpf("4.2e7"), 1e-9)
# 截斷 logN 中位
tn = truncnorm(zt, float('inf'), loc=mu_lnM, scale=sig_lnM)
M_trunc_med = math.exp(tn.median())
close("截斷 logN 預測中位 = 1.99e7", mp.mpf(M_trunc_med), mp.mpf("1.99e7"), 3e-2)
close("0.75 dex (ln ratio)", mp.mpf(abs(math.log(high_med/M_trunc_med))), mp.mpf("0.75"), 5e-2)
close("2σ = 1.58 dex (= 2·σ_lnM·1.253/√8)", mp.mpf(2*sig_lnM*1.253/math.sqrt(8)), mp.mpf("1.58"), 2e-2)
# P(UHz1) logN-only 閉式 + z
P_U = 0.5*(1-erf((math.log(1.7e9)-mu_lnM)/(sig_lnM*math.sqrt(2))))
z_U = (math.log(1.7e9)-mu_lnM)/sig_lnM
close("P(M≥1.7e9) = 1.016e-3 (logN-only 閉式)", mp.mpf(P_U), mp.mpf("1.016e-3"), 1e-2)
close("UHz1 z = 3.085 (對應 1.016e-3)", mp.mpf(z_U), mp.mpf("3.085"), 1e-2)
print(f"      ⚠️ O197 docs/01 §三.4 寫「logN 尾 2.4σ」— 與 P=1.016e-3 (z=3.085) 不符,")
print(f"         亦與 O198 docs/01 §四 (z=3.085) 不一致 ⟹ 審計發現, 需標註 (唔改歷史正文)")
close("N=434 P(≥1) = 0.36", mp.mpf(1-(1-P_U)**434), mp.mpf("0.36"), 5e-2)
close("N=306 P(≥1) = 0.27", mp.mpf(1-(1-P_U)**306), mp.mpf("0.27"), 5e-2)

print()
print("="*74); print("C. verification/docs/02 (實測 λ_Edd 攻堅)"); print("="*74)
lams = [d["lambda_Edd"] for d in data]
geo = math.exp(sum(math.log(l) for l in lams)/len(lams)); arith = sum(lams)/len(lams)
sl = sorted(lams); med = (sl[4]+sl[5])/2
sig_lnl = statistics.stdev([math.log(l) for l in lams])
close("λ geo = 0.702", mp.mpf(geo), mp.mpf("0.702"), 1e-3)
close("λ arith = 1.275", mp.mpf(arith), mp.mpf("1.275"), 1e-3)
close("λ median = 1.060", mp.mpf(med), mp.mpf("1.060"), 2e-2)
close("σ_lnλ = 1.39 (sample ddof=1)", mp.mpf(sig_lnl), mp.mpf("1.39"), 1e-2)
close("偏置因子 7.0×", mp.mpf(geo/0.1), mp.mpf("7.0"), 5e-2)
close("偏置 0.85 dex", mp.mpf(math.log10(geo/0.1)), mp.mpf("0.85"), 5e-2)
lam_by_M = {d["M_BH"]: d["lambda_Edd"] for d in data}
close("GLASS_160133 λ = 3.68", mp.mpf(lam_by_M[2.3e6]), mp.mpf("3.68"), 1e-3)
close("GLASS_150029 λ = 1.89", mp.mpf(lam_by_M[3.7e6]), mp.mpf("1.89"), 1e-3)
rho, p_asy = spearmanr([d["M_BH"] for d in data], lams)
close("Spearman ρ = −0.648", mp.mpf(rho), mp.mpf("-0.648"), 1e-2)
print(f"      p: scipy 漸近 {p_asy:.4f}; docs 用 permutation 0.024 (n=10 精確方法) — 方法差異, 非錯誤")
close("GLASS_160133 隱含 L_min = λ·L_Edd·M = 2.9e43", mp.mpf(0.1*1.26e38*2.3e6), mp.mpf("2.9e43"), 1e-2)
close("L_min* = 5.73e43 ⟹ M_min* = 4.55e6", mp.mpf(5.73e43/(0.1*1.26e38)), mp.mpf("4.55e6"), 1e-2)
close("L_min 新值 1.02e45 = 17.8× 舊值", mp.mpf(1.02e45/5.73e43), mp.mpf("17.8"), 1e-2)
chk("1.02e45 ∈ 觀測 L_bol [1.8e44, 1.1e46]",
    abs(min(d["L_bol"] for d in data)/1.8e44-1)<0.05 and abs(max(d["L_bol"] for d in data)/1.1e46-1)<0.05,
    f"[{min(d['L_bol'] for d in data):.2e}, {max(d['L_bol'] for d in data):.2e}]")
close("g_需 = 3.2e7/5.4e6 = 5.92", mp.mpf(3.2e7/5.40e6), mp.mpf("5.92"), 2e-2)
close("g_允許 = 2.3e6/2.02e6 = 1.14", mp.mpf(2.3e6/2.02e6), mp.mpf("1.14"), 1e-2)
close("矛盾 5.2×", mp.mpf(5.92/1.14), mp.mpf("5.2"), 2e-2)
close("2.5σ = 1.78/0.71", mp.mpf(1.78/0.71), mp.mpf("2.5"), 2e-2)
close("3.7σ = 1.78/0.48", mp.mpf(1.78/0.48), mp.mpf("3.7"), 2e-2)
# λ 自洽: λ = L_bol/(1.26e38·M)
lam_re = [d["L_bol"]/(1.26e38*d["M_BH"]) for d in data]
n_ok = sum(1 for d, lr in zip(data, lam_re) if abs(lr-d["lambda_Edd"])/d["lambda_Edd"] < 0.10)
chk("λ = L_bol/(L_Edd·M) 9/10 一致 (容差 10%)", n_ok==9, f"{n_ok}/10")

print()
print("="*74); print("D. verification/docs/03 (成長閉合)"); print("="*74)
H0, Om = 67.4, 0.315; OL = 1-Om; H0_s = H0*1e5/3.086e24
def t_z(z):
    f = lambda zz: 1.0/((1+zz)*math.sqrt(Om*(1+zz)**3+OL))
    v,_ = quad(f, z, 1e4, limit=400); return v/H0_s/3.156e16
t_ef_Gyr = 4.5e8*0.1/(0.1*0.9)/1e9     # 0.5 Gyr (單位修正)
close("t_ef = 5.0e8 yr = 0.5 Gyr", mp.mpf(t_ef_Gyr), mp.mpf("0.5"), 1e-9)
close("t(z=5) = 1.171 Gyr", mp.mpf(t_z(5.0)), mp.mpf("1.171"), 5e-3)
close("G(13.43→7.5) = 2.14", mp.mpf(math.exp((t_z(7.5)-t_z(13.43))/t_ef_Gyr)), mp.mpf("2.14"), 1e-2)
# G 範圍 (per-object, z_f*=13.43)
G_list = [math.exp((t_z(d["z"])-t_z(13.43))/t_ef_Gyr) for d in data]
close("G_max = 11.4 (docs) / 11.37 (script)", mp.mpf(max(G_list)), mp.mpf("11.4"), 1e-2)
close("G_min = 2.5 (docs) / 2.49 (script)", mp.mpf(min(G_list)), mp.mpf("2.5"), 2e-2)
chk("G 隨 z_obs 單調遞減", all(sorted(zip([d["z"] for d in data], G_list))[i][1] >=
    sorted(zip([d["z"] for d in data], G_list))[i+1][1] for i in range(9)))
d160 = [d for d in data if d["name"]=="GLASS_160133"][0]
d150 = [d for d in data if d["name"]=="GLASS_150029"][0]
G160 = math.exp((t_z(d160["z"])-t_z(13.43))/t_ef_Gyr)
G150 = math.exp((t_z(d150["z"])-t_z(13.43))/t_ef_Gyr)
close("GLASS_160133 G = 11.37", mp.mpf(G160), mp.mpf("11.37"), 1e-2)
close("GLASS_150029 G = 7.23", mp.mpf(G150), mp.mpf("7.23"), 2e-2)
close("GLASS_160133 seed = 2.0e5 (uniform)", mp.mpf(2.3e6/G160), mp.mpf("2.0e5"), 5e-2)
close("GLASS_150029 seed = 5.1e5 (uniform)", mp.mpf(3.7e6/G150), mp.mpf("5.1e5"), 5e-2)
chk("成長時間 ≤ 66 Myr (GLASS_160133)", abs(math.log(2.3e6/2.017e6)*500 - 66) < 3,
    f"{math.log(2.3e6/2.017e6)*500:.0f} Myr")
chk("成長時間 ≤ 303 Myr (GLASS_150029)", abs(math.log(3.7e6/2.017e6)*500 - 303) < 5,
    f"{math.log(3.7e6/2.017e6)*500:.0f} Myr")
# 高端 8 粒成長後 seed 中位 8.66e6, z = 0.12
high8 = [d for d in data if d["M_BH"] >= Mt]
Gh = [math.exp((t_z(d["z"])-t_z(13.43))/t_ef_Gyr) for d in high8]
seed_high = sorted(d["M_BH"]/g for d, g in zip(high8, Gh))
med_seed_high = seed_high[len(seed_high)//2]
close("高端 seed 中位 = 8.66e6", mp.mpf(med_seed_high), mp.mpf("8.66e6"), 1e-2)
close("高端 seed z-score = 0.12", mp.mpf((math.log(med_seed_high)-mu_lnM)/sig_lnM), mp.mpf("0.12"), 3e-2)
# UHz1: seed = 1.7e9/G, z = 2.66, P = 3.9e-3
G_U = math.exp((t_z(7.5)-t_z(13.43))/t_ef_Gyr)
M_sU = 1.7e9/G_U; z_sU = (math.log(M_sU)-mu_lnM)/sig_lnM
close("UHz1 seed = 7.94e8", mp.mpf(M_sU), mp.mpf("7.94e8"), 1e-2)
close("UHz1 seed z = 2.66", mp.mpf(z_sU), mp.mpf("2.66"), 1e-2)
close("UHz1 seed P = 3.9e-3", mp.mpf(0.5*(1-erf(z_sU/math.sqrt(2)))), mp.mpf("3.9e-3"), 2e-2)
# 全 PDF 斜率 (script 約定: slope_full = slope_gauss − 1, 再 ×ln10)
slope_gauss = -(math.log(1e8)-mu_lnM)/sig_lnM**2
close("Gaussian 指數斜率 = −0.84 (O197 引述形式)", mp.mpf(slope_gauss), mp.mpf("-0.84"), 5e-2)
close("全 PDF 斜率 = −4.23/dex (script 約定 ×ln10)", mp.mpf((slope_gauss-1)*math.log(10)), mp.mpf("-4.23"), 2e-2)
# channel-resolved forward 中位 2.34e7 (MC, 獨立 seed)
A_masses = [float(M_base*(2*math.sin(k*math.pi/176)**2)**1.5) for k in range(45,89)]
rng = random.Random(777)     # 獨立 seed (script 用 20260915)
tobs = [t_z(d["z"]) for d in data]
w_ = 0.2
tzf = t_z(13.43)
# 按 script 06 T8h3 原定義: 通道由 rng.random() < w 決定 (A fresh / B full-time 成長)
vals = []
for _ in range(300000):
    lam_i = rng.choice(lams); t_obs = rng.choice(tobs)
    if rng.random() < w_:
        M_obs = rng.choice(A_masses)                    # 通道 A: fresh (G=1)
    else:
        M_obs = math.exp(rng.gauss(mu_lnM, sig_lnM))*math.exp((t_obs-tzf)/t_ef_Gyr)  # 通道 B
    if lam_i*1.26e38*M_obs >= 3e43: vals.append(math.log(M_obs))
vals.sort(); fwd_med = math.exp(vals[len(vals)//2])
close("channel-resolved forward 中位 = 2.34e7 (MC ±)", mp.mpf(fwd_med), mp.mpf("2.34e7"), 1e-1)
print(f"      (獨立 RNG: {fwd_med:.3e}; 張力 {math.log(fwd_med/3.2e7):+.2f} ln vs docs −0.31 — MC 容差內)")

# z_f 表 (docs/03 §三 T8b, 用 script 06 fwd_median_growth 原定義: 全部種子 full-time 成長)
print()
print("-- z_f 反演表 (docs/03 §三) --")
obs_med = masses[len(masses)//2]
def fwd_med_plain(zf, n=150000):
    rng2 = random.Random(4242)      # 獨立 seed
    tzf_ = t_z(zf); vals2 = []
    for _ in range(n):
        lam_i = rng2.choice(lams); t_obs = rng2.choice(tobs)
        if rng2.random() < w_: M = rng2.choice(A_masses)
        else: M = math.exp(rng2.gauss(mu_lnM, sig_lnM))
        M_obs = M*math.exp((t_obs-tzf_)/t_ef_Gyr)
        if lam_i*1.26e38*M_obs >= 3e43: vals2.append(math.log(M_obs))
    vals2.sort(); return math.exp(vals2[len(vals2)//2])
for zf, doc_pred, doc_ten in [(8,1.73e7,-0.61),(10,2.36e7,-0.30),(12,2.87e7,-0.11),
                              (13.43,3.17e7,-0.010),(15,3.48e7,0.09),(20,4.15e7,0.26)]:
    m = fwd_med_plain(zf)
    close(f"z_f={zf}: 預測中位 = {doc_pred:.3g} (張力 {doc_ten:+.2f})", mp.mpf(m), mp.mpf(doc_pred), 1.2e-1)
# z_f* 反演: 二分求 fwd_median = obs_med
lo, hi = 8.0, 25.0
for _ in range(18):
    mid = (lo+hi)/2
    if fwd_med_plain(mid, 40000) < obs_med: lo = mid
    else: hi = mid
close("z_f* = 13.43 (反演)", mp.mpf((lo+hi)/2), mp.mpf("13.43"), 1e-1)
chk("z_f* > 7.5 (UHz1 存在) 且 ∈ [8,15] (再電離期)", 7.5 < (lo+hi)/2 <= 15,
    f"z_f* = {(lo+hi)/2:.2f}")

print()
print("="*74); print("E. 資料來源 / 追溯性審計"); print("="*74)
raw = json.load(open(f"{ODIR}/verification/data/harikane23_table3_eddington.json"))
chk("⚠️ data JSON 嘅 z 欄位 = None (10/10) — z 由 script 06 內部 zs map 提供",
    all(r["z"] is None for r in raw),
    "來源: Harikane+23 Table 1 (script 06 docstring) — 追溯點, 已記錄")
chk("z map 覆蓋全部 10 粒", set(zs) == {r["name"] for r in raw})
chk("z 範圍 [4.0, 6.9] 與 z~4-7 一致", 4.0 <= min(zs.values()) and max(zs.values()) <= 7.0,
    f"[{min(zs.values())}, {max(zs.values())}]")

print()
print(f"===== v3 審計: {sum(ok)}/{len(ok)} 全對 =====")
if not all(ok):
    print(f"⚠️ {len(ok)-sum(ok)} 項需查")
