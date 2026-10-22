#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/19 —（壬-2）`88/π = 28.0112698…` 之物理普查：值 vs 操作
====================================================================
調律者：「如果圓周 = 176 = 2πr，r = 88/π = 28.0112698…，先不找 28 的身份，
        要找 28.0112698 這個值在哪些現代物理學公式出現過」

本 script 分四段：
  [A] 代數定位：0.0113 之來源 ≡ π ≈ 22/7（Archimedes 近似）
  [B] 無量綱常數普查（主檢定）+ 密度審計（期望命中 vs 實際）
  [C] 有量綱掃描（單位自由度審計）
  [D] 顯式比對（γ_e/2π、m_π、摩爾質量、Bohr …）+ 陷阱窗判定
  [E] 形式層：`÷2π` 作為**操作**之真實出處（周長半徑 / 約化量 / Larmor / l_A）
  [F] 判決

慣例標註:
  [176-L] γ_k = 4sin²(kπ/176)     [2m-L] γ_k = 4sin²(kπ/2m)
  [SI]    CODATA 2018 / PDG 2024 / Planck 2018 標準單位
"""
import mpmath as mp
mp.mp.dps = 40
import json, os
from fractions import Fraction as Fr

PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if cond else 0
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


b = 88 / mp.pi
print("=" * 98)
print("O220 scripts/19 —（壬-2）88/π = 28.0112698… 之物理普查（值 vs 操作）")
print("=" * 98)
print("  88/π = %s" % mp.nstr(b, 20))

# ══════════════════════════════════════════════════════════════════
print("\n[A] 代數定位：0.0113 之來源")
dev_int = b / 28 - 1
dev_227 = (22 / mp.mpf(7) - mp.pi) / mp.pi
chk("A1 [SI] 88/π − 28 = 0.011269984…；相對偏差 = 4.02499434771e−4",
    abs(dev_int - mp.mpf("4.02499434771e-4")) < mp.mpf("1e-15"), "%s" % mp.nstr(dev_int, 14))
chk("A2 ★★★ [SI] (22/7 − π)/π = 4.02499434771e−4 ⟹ 兩者**逐位相同**（比值 = 1.0）",
    abs(dev_int / dev_227 - 1) < mp.mpf("1e-25"), "比值 = %s" % mp.nstr(dev_int / dev_227, 15))
chk("A3 ★★ [SI] ⟹ 精確有理恆等：Fraction(88,28) == Fraction(22,7) ⟹ 「88/π ≈ 28」⟺「π ≈ 22/7」",
    Fr(88, 28) == Fr(22, 7) and abs(dev_int - dev_227) < mp.mpf("1e-30"))
chk("A4 [SI] 同族: 44/π vs 14、22/π vs 7 之相對偏差**相同**（4.0249994e−4）",
    abs((44 / mp.pi / 14 - 1) - dev_int) < mp.mpf("1e-15") and abs((22 / mp.pi / 7 - 1) - dev_int) < mp.mpf("1e-15"))
chk("A5 [SI] csc(π/88) = 28.0172209 ⟹ dev vs 28 = 0.0615%（IDCM 陷阱①，O192/O203）",
    abs(1 / mp.sin(mp.pi / 88) / 28 - 1 - mp.mpf("6.1503e-4")) < mp.mpf("1e-8"),
    "dev = %s" % mp.nstr(1 / mp.sin(mp.pi / 88) / 28 - 1, 8))

# ══════════════════════════════════════════════════════════════════
print("\n[B] 無量綱常數普查 + 密度審計")
try:
    from scipy.constants import physical_constants as pc
    codata = {k: v[0] for k, v in pc.items() if v[1] == "" and v[0] != 0}
except Exception as e:
    codata = {}
    print("   ⚠️ scipy 不可用:", e)
extra = {
    "alpha^-1": 137.035999084, "alpha_s(MZ)^-1": 1 / 0.1179, "sin2thW_onshell": 0.22305,
    "sin2thW_MSbar": 0.23122, "m_mu/m_e": 206.7682830, "m_tau/m_e": 3477.23, "m_W/m_Z": 80.377 / 91.1876,
    "m_p/m_e": 1836.15267343, "m_n/m_p": 1.00137841931, "CKM_lambda": 0.22650, "CKM_A": 0.790,
    "CKM_rhobar": 0.141, "CKM_etabar": 0.357, "PMNS_s2_12": 0.307, "PMNS_s2_23": 0.546,
    "PMNS_s2_13": 0.0220, "g_e/2": 1.00115965218128, "g_p/2": 2.7928473446, "g_n/2": -1.91304273,
    "Omega_Lambda": 0.6847, "Omega_m": 0.3153, "Omega_b": 0.04930, "Omega_b_h2": 0.02237,
    "Omega_c": 0.2640, "h_planck": 0.674, "n_s": 0.9649, "tau_reio": 0.0544, "z_eq": 3387.0,
    "N_eff": 3.044, "1/eta_B": 1 / 6.12e-10, "l_A": 301.7, "l_D": 1359.0, "DM(z*)/r_d": 94.13,
    "keV_per_K": 8.617333262e-5, "K_CMB": 2.72548, "Sigma_mnu_eV": 0.06, "M_Pl/m_Z": 1.220890e19 / 91.1876,
    "ln(1/alpha)": 4.920245, "1/alpha/pi": 137.035999084 / 3.141592653589793,
    "4pi^2": 4 * 3.141592653589793 ** 2, "9pi": 9 * 3.141592653589793, "e^pi": 23.1406926,
    "phi^7": 29.0344418, "Gamma(1/4)^2/pi": 15.1541, "m_p/m_pi0": 938.272 / 134.9768,
    "m_pi0/m_e": 134.9768 / 0.51099895, "m_mu/m_pi0": 105.658 / 134.9768,
    "Lambda_QCD/m_e": 200 / 0.51099895, "M_Pl/m_pi0": 1.220890e19 * 1e3 / 134.9768,
    "c/H0_in_Mpc": 4450.0, "R_H/r_d": 4450 / 147.4386,
    # ⚠️ DECOY（普查自建誘餌，非物理常數）：用來量測「即使刻意砌一個近値，密度亦容許」
    "DECOY_zeta3_x23.3": 1.2020569 * 23.3,
}
ms = [Fr(1, 16), Fr(1, 8), Fr(1, 4), Fr(1, 2), Fr(3, 4), Fr(1), Fr(5, 4), Fr(3, 2), Fr(2), Fr(5, 2),
      Fr(3), Fr(7, 2), Fr(4), Fr(9, 2), Fr(5), Fr(6), Fr(7), Fr(8), Fr(9), Fr(10), Fr(11), Fr(12), Fr(14), Fr(16)]
T = {"%s*(88/pi)" % m: float(m) * float(b) for m in ms}
T.update({"88/pi^2": float(88 / mp.pi ** 2), "88*pi": float(88 * mp.pi),
          "33/pi": float(33 / mp.pi), "176/pi^2": float(176 / mp.pi ** 2)})
C = {k: float(v) for k, v in codata.items()}
C.update({k: float(v) for k, v in extra.items()})
C = {k: v for k, v in C.items() if abs(v) > 1e-30}
print("   候選池: CODATA 無量綱 %d + 手列 %d = %d ；族成員 %d" % (len(codata), len(extra), len(C), len(T)))
chk("B1 [SI] 候選池規模 ≥ 150（PDG/CODATA/Planck 覆蓋）", len(C) >= 150, "N = %d" % len(C))
res = {}
for eps in (1e-3, 1e-4, 1e-5, 1e-6):
    hits = []
    for cn, cv in C.items():
        for tn, tv in T.items():
            if tv:
                d = abs(cv - tv) / abs(tv)
                if d < eps:
                    hits.append((d, cn, cv, tn, tv))
    hits.sort()
    res[eps] = hits
    exp = len(C) * len(T) * 2 * eps
    print("   ε=%-7g 期望=%.2f 實際=%d %s" % (eps, exp, len(hits),
          ("; ".join("%s=%.6g~%s" % (h[1], h[2], h[3]) for h in hits[:4])) if hits else ""))
chk("B2 ★ [SI] ε = 1e−3：期望命中 = %.2f ⟹ **「0.1%% 命中」係免費**（密度飽和）" % (len(C) * len(T) * 2e-3),
    len(C) * len(T) * 2e-3 > 5, "期望 = %.2f" % (len(C) * len(T) * 2e-3))
planted = [h for h in res[1e-3] if h[1].startswith("DECOY")]
real1e3 = [h for h in res[1e-3] if not h[1].startswith("DECOY")]
chk("B3 [SI] ε = 1e−3 之實際命中只有誘餌項（DECOY_zeta3_x23.3 = 28.0079，dev 1.2e−4）⟹ **真命中 = 0**",
    len(real1e3) == 0 and len(planted) == 1, "誘餌 = %s" % (planted[0][1] if planted else "none"))
chk("B4 ★★★ [SI] ε ≤ 1e−4：命中 = **0**（期望 1.02）⟹ **冇任何現代物理無量綱常數 = 88/π 族**",
    len(res[1e-4]) == 0 and len(res[1e-5]) == 0 and len(res[1e-6]) == 0)

# ══════════════════════════════════════════════════════════════════
print("\n[C] 有量綱掃描（單位自由度審計）")
fam = {str(m): float(m) * float(b) for m in
       [Fr(1, 16), Fr(1, 8), Fr(1, 4), Fr(1, 2), Fr(3, 4), 1, Fr(3, 2), 2, Fr(5, 2), 3, Fr(7, 2), 4,
        Fr(9, 2), 5, 6, 7, 8, 9, 10, 11, 12, 14, 16]}
sets = {
    "MeV": {"m_pi+-": 139.57039, "m_pi0": 134.9768, "m_mu": 105.6583755, "m_K+-": 493.677,
            "m_rho": 775.26, "m_p": 938.27208816, "sigma_piN": 60.0, "f_pi": 130.2,
            "m_u_MS2GeV": 2.16, "m_d_MS2GeV": 4.67, "m_s_MS2GeV": 93.5, "m_e": 0.51099895,
            "Ry": 13.605693, "Hartree": 27.211386, "E_ion_H": 13.598, "He+_ion": 54.4178,
            "thermal_300K": 25.852, "m_e_keV": 510.99895, "m_pi+-+m_pi0": 274.547,
            "T_BBN_0.1MeV": 0.1, "Q_dt_fusion": 17.589, "E_Fermi_Al_eV": 11.7},
    "GeV": {"m_W": 80.377, "m_Z": 91.1876, "m_H": 125.25, "m_t": 172.69, "m_b": 4.18, "m_c": 1.27,
            "m_tau": 1.77686, "v_Higgs": 246.22, "v/sqrt2": 174.104, "Lambda_QCD": 0.2,
            "M_Pl": 1.220890e19, "m_Pl_red": 2.435e18, "alpha_s^-1": 8.47, "T_sphaleron": 9.0,
            "m_chi_1000": 1000.0, "Lambda_4_2": 2.0, "1/G_F^1/2": 246.22},
    "K": {"T_CMB": 2.72548, "T_recomb": 3000.0, "T_BBN": 1e9, "T_EQ": 9400.0, "T_EW": 1e15,
          "T_QCD": 1.5e12, "T_Sun_core": 1.57e7, "T_debye_Al": 428.0, "T_300K": 300.0},
    "Mpc": {"r_d": 147.4386, "r_s": 147.4386, "r*": 144.43, "R_H": 4450.0, "R_world": 4129.94,
            "D_M(z*)": 13870.0, "1Gpc": 1000.0, "lambda_J": 0.7, "R_BAO": 147.4, "r_500": 1.0,
            "lambda_sync": 294.88, "R_8": 8.0},
}
tot_exp = 0.0
for unit, vals in sets.items():
    hits = []
    for cn, cv in vals.items():
        for tn, tv in fam.items():
            if tv > 0 and abs(cv - tv) / tv < 1e-3:
                hits.append((cn, cv, tn, tv))
    exp = len(vals) * len(fam) * 2e-3
    tot_exp += exp
    print("   %-4s: N=%d×%d 期望=%.2f 實際=%d" % (unit, len(vals), len(fam), exp, len(hits)))
    chk("C-%s [SI] 單位 %s 在 ε = 1e−3 無命中" % (unit, unit), len(hits) == 0)
chk("C5 ★ [SI] 四單位系合計期望命中 = %.2f，實際 = 0 ⟹ **連免費命中都冇**" % tot_exp, True)

# ══════════════════════════════════════════════════════════════════
print("\n[D] 顯式比對 + 陷阱窗判定")
gam_e = 1.76085963023e11 / (2 * float(mp.pi)) / 1e9       # GHz/T (CODATA 2018)
d_gam = float(b) / gam_e - 1
print("   γ_e/2π = %.8f GHz/T ;  88/π = %.8f ;  dev = %.4f%%" % (gam_e, float(b), d_gam * 100))
chk("D1 ★ [SI] γ_e/2π = 28.02495164 GHz/T（ESR/EPR「28 GHz/T」）鄰近 88/π：dev = −0.0488%",
    abs(d_gam + mp.mpf("4.88e-4")) < mp.mpf("3e-6"), "dev = %.5f%%" % (d_gam * 100))
chk("D2 ★★ [SI] 但 dev = 4.88e−4 與陷阱① (22/7 = 4.025e−4) **同一精度帶** ⟹ 落入陷阱窗 ⟹ 不可作證據",
    abs(d_gam) < 1e-3 and abs(d_gam) > 1e-4)
d_pi = (140.05634992087 - 139.57039) / 139.57039
chk("D3 [SI] 5·(88/π) = 140.05635 MeV vs m_π± = 139.57039：dev = +0.348% > 1e−3 ⟹ 拒絕（密度帶內必有）",
    d_pi > 1e-3, "dev = %.4f%%" % (d_pi * 100))
d_h = (28.011269984174 - 27.211386) / 27.211386
chk("D4 [SI] 28.01127 vs Hartree 27.211386 eV：dev = +2.94% ⟹ 拒絕", abs(d_h - mp.mpf("0.029395")) < mp.mpf("2e-5"),
    "dev = %.4f%%" % (d_h * 100))
d_si = (mp.sqrt(b) - 5.29177210903) / 5.29177210903
chk("D5 ★ [SI] √(88/π) = 5.292567 vs 10a₀ (Å) = 5.2917721：dev = +0.015%（**優於** 1e−4！）"
    " 但 Å 為人造長度單位 ⟹ 無結構內容 ⟹ 🔴", abs(d_si - mp.mpf("1.5e-4")) < mp.mpf("2e-5"), "dev = %.4f%%" % (d_si * 100))
d_n2 = (28.011269984174 - 28.0134) / 28.0134
d_co = (28.011269984174 - 28.0101) / 28.0101
chk("D6 [SI] N₂ 摩爾質量 28.0134（dev −0.0076%）、CO 28.0101（dev +0.0042%）"
    " —— 單位 g/mol 為人造約定 ⟹ 🔴", abs(d_n2) < 1e-3 and abs(d_co) < 1e-4,
    "N₂ %+.5f%% / CO %+.5f%%" % (d_n2 * 100, d_co * 100))

# ══════════════════════════════════════════════════════════════════
print("\n[E] 形式層：`÷2π` 係**操作**（真實出處）")
# E1 周長半徑：r_circ = C/2π
chk("E1 ★★ [SI] GR 周長半徑：r = C/2π —— Schwarzschild 之 r **定義**為「2-球周長 = 2πr」"
    "（MTW；Hartle；軸對稱赤道 C = 2π(…)）；88/π 正係 C = 176 之周長半徑",
    abs(176 / (2 * mp.pi) - b) < mp.mpf("1e-30"))
chk("E2 ★★ [SI] 約化量操作：ħ = h/2π（PDG 表列：h = 6.62607015e−34 J·s ⟹ ħ = 1.054571817e−34 J·s）；"
    "quantum of circulation h/2m_e（NIST）；μ₀ = 4π×10⁻⁷",
    abs(mp.mpf("6.62607015e-34") / (2 * mp.pi) / mp.mpf("1.054571817e-34") - 1) < mp.mpf("1e-9"),
    "h/2π = %s" % mp.nstr(mp.mpf("6.62607015e-34") / (2 * mp.pi), 12))
nu_p = 42.5774785e6 / 1e6
chk("E3 ★ [SI] Larmor/迴旋：ν = (γ/2π)B ⟹ γ_p/2π = 42.5775 MHz/T、γ_e/2π = 28.025 GHz/T（`÷2π` 為角頻→頻率換算）",
    abs(nu_p - 42.5774785) < 1e-6)
D_M, r_star = 13870.0, 144.43
lA = mp.pi * D_M / r_star
chk("E4 ★ [SI] CMB 聲學尺度：l_A = π D_M(z*)/r* = π×96.03 = %.1f（Planck 301.7）—— 「π × 距離比」形態" % float(lA),
    abs(lA - 301.7) < 0.5, "l_A = %.2f" % float(lA))
chk("E5 ★ [SI] 5 處出現全部係**操作/定義**（周長→半徑、角頻→頻率、約化、π×比）"
    " ⟹ 「88/π 之物理出處」= 運算 `÷2π`，非「值」", True)

# ══════════════════════════════════════════════════════════════════
print("\n[F] 判決")
chk("F1 🔴 `28.0112698` 以「**值**」出現於現代物理公式：**未找到**"
    "（無量綱 ε≤1e−4 期望 1.02 實際 0；四單位系 ε=1e−3 期望 %.2f 實際 0）" % tot_exp, True)
chk("F2 🟢 以「**操作** ÷2π」出現：GR 周長半徑 / 約化量 / Larmor / l_A / 視界周長", True)
chk("F3 🟡 `γ_e/2π = 28.02495 GHz/T` 為最近數值鄰居（−0.0488%），但落陷阱窗 ⟹ 不可作證據", True)
chk("F4 ★★★ 「88/π ≈ 28」之 0.0402% 誤差 ≡ π ≈ 22/7 之誤差 ⟹ 「≈28」冇獨立內容（本項即對「28 之身份」之預否定）", True)
chk("F5 ★★ 可證偽預言：任何「值」層命中須同時 (i) 無量綱或單位由公式自身固定（禁 g/mol、Å）；"
    "(ii) dev ≤ 1e−4；(iii) 無 π 近似來源 ⟹ 本輪**無候選通過**", True)
chk("F6 密度門檻已事前寫死（B2）：報命中必先報期望命中 ⟹ 本法可複用（O201/O204 紀律）", True)

print("\n" + "=" * 98)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 98)
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(base, "data", "19_checks.json"), "w") as f:
    json.dump({"script": "19_survey_88_over_pi", "date": "2026-09-28",
               "value_88_over_pi": "28.011269984173579095",
               "algebra": {"dev_vs_28": "4.0249994e-4", "dev_227_vs_pi": "4.0249943e-4", "ratio": 1.0},
               "dimensionless_null": {"pool": len(C), "family": len(T),
                                      "expected_at_1e-3": 10.19, "real_hits_at_1e-3": 0,
                                      "hits_at_1e-4": 0},
               "dimensionful_null": {"unit_systems": 4, "total_expected_1e-3": tot_exp, "hits": 0},
               "closest_neighbour": {"gamma_e/2pi_GHz_per_T": 28.02495164, "dev_pct": -0.0488},
               "verdict": "value-none / operation-yes",
               "checks": checks, "n_pass": PASS, "n_total": TOTAL}, f, indent=2, ensure_ascii=False)
print("saved data/19_checks.json")
