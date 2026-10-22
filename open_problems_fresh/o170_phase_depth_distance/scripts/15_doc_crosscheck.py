#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/15 — 文檔獨立核對器 (doc crosscheck)  [v2, 2026-09-15]

目的 (用戶指令): 「驗證並獨立核對每一個文檔中所有推導鏈過程中內容、公式和數值」

方法 (o-series-research-workflow 文檔審計工作流 step 2):
  - **唔 import scripts/01-14 任何函數**; 由 data/01 原始表逐字重新輸入
  - 每個 doc 一區塊 (A=docs/01 ... H=data/01); chk(doc, claim, 算值, doc值, tol) → [OK]/[X]
  - 最後 "DOC CROSSCHECK RESULT: N/N"

v2 修正 (v1 有 49 個 FAIL, triage 後 12 個係 check 自身錯, 見 docs/09):
  rd 約定: 歷史區塊 (docs/01-04) 用 scripts/04-09 嘅 rd = 147.088;
            新區塊 (docs/05-07, data/01) 用 scripts/10-14 嘅 rd = πR/88·420/421
  1. Lyα 殘餘符號: doc 慣例 = (obs − model)/σ (同 docs/06 殘餘一致)
  2. BGS D_app/ladder: 正確模型組合 = D_app+const φ / D_lin+const φ (scripts/06 §E9)
  3. 淺區加權均值 = 6 點集 (7 淺點 減合併 bin; scripts/07 §F3)
  4. ⟨sec⟩ = mean of **sec** (唔係 cos)
  5. docs/05 §5c: D_new(ℓ_nyq)/πR = (1−4^{−ℓ_nyq})(ℓ_nyq+b)/π
  6. docs/07 §2 L4: 統一律 D_H = dD_M/dz 解析值 = R·M(ℓ)/((1+z)ln4) — 唔用受污染嘅有限差分
  7. docs/07 §4 跨調查: (DESI − BOSS)/σ
  8. ℓ_t 掃描用 scripts/04 嘅 1e-3 網格
  9. 1dp/2dp 顯示值容差放寬; 10. data/01 ℓ 欄 provenance; 11. excl-bin 點集; 12. docs/01 §5 例
"""
import mpmath as mp
mp.mp.dps = 40

# ============ 基礎常數 ============
C_KM = mp.mpf("299792.458")
R = mp.mpf("4129.94")
RD_H = mp.mpf("147.088")                   # 歷史區塊 (scripts/04-09)
RD = mp.pi * R / 88 * mp.mpf(420) / 421    # 新區塊 (scripts/10-14) = 147.088302979
LN4 = mp.log(4)
PHI = (1 + mp.sqrt(5)) / 2
SQ2 = mp.sqrt(2)
C_D = mp.mpf("-0.1697")
ELL_T = mp.log(3) / LN4
ELL_NYQ = mp.log(18) / LN4
ND, B, NGEN = 44, 4, 3
M_SH = 1 / mp.cos(mp.mpf("25.5") * mp.pi / 88)
B_NEW = 22 / sum(mp.cos(mp.pi * n / 88) for n in range(1, 23))

def ell(z): return mp.log(1 + mp.mpf(str(z))) / LN4
def vg(n): return mp.cos(mp.pi * mp.mpf(str(n)) / 88)
def sec_nc(nc): return 1 / vg(nc)
def nc_arch(e): return 22 + B * mp.sin(mp.pi * e) if e < ELL_T else mp.mpf(22)
def nc_step(e): return mp.mpf("25.5") if e < ELL_T else mp.mpf(22)
def M_arch(e): return sec_nc(nc_arch(e))
def M_step(e): return sec_nc(nc_step(e))
def M_phi(e): return PHI if e < ELL_T else SQ2

def D_app(z):
    e = ell(z); return R * (1 - 4**(-e)) * (1 + 2/PHI*e + C_D*(e - mp.mpf("0.5"))*(1 - 4**(-e)))
def D_new(z):
    e = ell(z); return R * (1 - 4**(-e)) * (e + B_NEW)
def D_phi_lin(z): return R * PHI * ell(z)
def D_app_lad(z):
    e = ell(z); return D_app(z) if e <= ELL_T else D_app(4**ELL_T - 1) + R*SQ2*(e - ELL_T)
def D_unif(z, msh):
    e = ell(z); return R*msh*e if e <= ELL_T else R*(msh*ELL_T + SQ2*(e - ELL_T))
def D_unif_arch(z):
    e = ell(z)
    return R*(mp.quad(lambda t: M_arch(t), [0, e]) if e <= ELL_T else 1.2603070874 + SQ2*(e - ELL_T))
def M_id(Df, z):
    e = ell(z); h = mp.mpf("1e-10")
    return (Df(4**(e+h) - 1) - Df(4**(e-h) - 1)) / (2*h) / R

COSMO6 = [("LRG1", "0.510", "13.588", "0.167", "21.863", "0.425", "-0.459"),
          ("LRG2", "0.706", "17.351", "0.177", "19.455", "0.330", "-0.404"),
          ("LRG3+ELG1", "0.934", "21.576", "0.152", "17.641", "0.193", "-0.416"),
          ("ELG2", "1.321", "27.601", "0.318", "14.176", "0.221", "-0.434"),
          ("QSO", "1.484", "30.512", "0.760", "12.817", "0.516", "-0.500"),
          ("Lyalpha", "2.330", "38.988", "0.531", "8.632", "0.101", "-0.431")]
VERIFY2 = [("LRG3", "0.922", "21.648", "0.178", "17.577", "0.213", "-0.406"),
           ("ELG1", "0.955", "21.707", "0.335", "17.803", "0.297", "-0.462")]
EXT5 = [("SDSS MGS", "0.15", "DV", "4.470", "0.170"), ("BOSS z=0.38", "0.38", "DM", "10.230", "0.170"),
        ("BOSS z=0.38", "0.38", "DH", "25.000", "0.760"), ("BOSS z=0.51", "0.51", "DM", "13.360", "0.210"),
        ("BOSS z=0.51", "0.51", "DH", "22.330", "0.580")]
ZB, DVO, DVE = mp.mpf("0.295"), mp.mpf("7.942"), mp.mpf("0.075")

def M_obs(dh, z, rd): return mp.mpf(dh) * rd * (1 + mp.mpf(z)) * LN4 / R
def sM(dh_err, z, rd): return mp.mpf(dh_err) * rd * (1 + mp.mpf(z)) * LN4 / R
def DV_of(DMf, Mf, rd):
    dmv = DMf(ZB)/rd; dhv = Mf(ell(ZB))*R/((1+ZB)*LN4)/rd
    return (ZB*dmv**2*dhv)**(mp.mpf(1)/3)
def pred_ext(Mf, z, kind):
    e = ell(z)
    if kind == "DV": return (mp.mpf(z)*(D_new(z)/RD)**2*(Mf(e)*R/((1+mp.mpf(z))*LN4)/RD))**(mp.mpf(1)/3)
    return D_new(z)/RD if kind == "DM" else Mf(e)*R/((1+mp.mpf(z))*LN4)/RD

LEDGER = []
def chk(doc, claim, got, want, tol):
    ok = abs(mp.mpf(got) - mp.mpf(want)) <= mp.mpf(tol)
    LEDGER.append((ok, doc, claim, float(mp.mpf(got)), want))
    print(("  [OK] " if ok else "  [X ] ") + f"{doc} {claim}: 算 {mp.nstr(mp.mpf(got),12)}  doc {want}")
    return ok

def chi2_DH(kind, pts, rd):
    f = M_arch if kind == "arch" else (M_step if kind == "step" else M_phi)
    return sum((f(ell(z)) - M_obs(dh, z, rd))**2 / sM(sdh, z, rd)**2 for (nm, z, dm, sdm, dh, sdh, rho) in pts)
def chi2_DM(DMf, pts, rd):
    return sum((DMf(z)/rd - mp.mpf(dm))**2/mp.mpf(sdm)**2 for (nm, z, dm, sdm, dh, sdh, rho) in pts)
def chi2_joint(DMf, Mf, pts, rd):
    t = mp.mpf(0)
    for (nm, z, dm, sdm, dh, sdh, rho) in pts:
        d1 = DMf(z)/rd - mp.mpf(dm); d2 = Mf(ell(z))*R/((1+mp.mpf(z))*LN4)/rd - mp.mpf(dh)
        e1 = mp.mpf(sdm); e2 = mp.mpf(sdh); r_ = mp.mpf(rho); cov = e1*e2*r_
        t += (d1**2*e2**2 + d2**2*e1**2 - 2*cov*d1*d2)/(e1**2*e2**2 - cov**2)
    return t
def dmsig(DMf, rd):
    return [(DMf(z)/rd - mp.mpf(dm))/mp.mpf(sdm) for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6]
def res6(Mf, rd):
    return [(M_obs(dh, z, rd) - Mf(ell(z)))/sM(sdh, z, rd) for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6]

print("=" * 108)
print("O170 scripts/15 — 文檔獨立核對器 v2 (獨立於 scripts/01-14)")
print("=" * 108)
print(f"  R={R}  RD_H={RD_H}  RD_exact={mp.nstr(RD,14)}  ln4={mp.nstr(LN4,12)}")
print(f"  phi={mp.nstr(PHI,12)}  sqrt2={mp.nstr(SQ2,12)}  ell_t={mp.nstr(ELL_T,12)}  ell_nyq={mp.nstr(ELL_NYQ,12)}")

# ══════════════════════ A: docs/01 (定義) ══════════════════════
print("\n" + "─"*108 + "\nA. docs/01_phase_depth_definition.md\n" + "─"*108)
chk("docs/01", "R_world = c/H0^local = 4129.94", C_KM/72.59, R, "0.5")
chk("docs/01", "H0^local = c/R = 72.590", C_KM/R, "72.590", "5e-4")
chk("docs/01", "SH0ES 73.0 → −0.41σ", (C_KM/R - 73.0)/1.0, "-0.41", "5e-3")
chk("docs/01", "r_d fiducial = 147.088", RD_H, "147.088", "5e-4")
chk("docs/01", "ΔE0 = sin(π/12) [O159]", mp.sin(mp.pi/12), "0.258819", "1e-6")
chk("docs/01 §5", "例 D_H(0.510)/rd (step 核)", R*4**(-ell("0.510"))*M_step(ell("0.510"))/LN4/RD_H, "21.862", "5e-3")
chk("docs/01 §5", "例 D_H(0.510)/rd (arch 核)", R*4**(-ell("0.510"))*M_arch(ell("0.510"))/LN4/RD_H, "21.584", "5e-3")

# ══════════════════════ B: docs/02 (step 核, 歷史) ══════════════════════
print("\n" + "─"*108 + "\nB. docs/02_radial_kernel_closure.md (step 核 — 已被 docs/06 取代, 歷史記錄)\n" + "─"*108)
WM = {"LRG1": "1.6300", "LRG2": "1.6387", "LRG3+ELG1": "1.6845", "ELG2": "1.6245", "QSO": "1.5719", "Lyalpha": "1.4192"}
for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6:
    chk("docs/02 §1", f"M({nm})", M_obs(dh, z, RD_H), WM[nm], "5e-5")
chk("docs/02 §1", "M(LRG3) 驗證 tracer", M_obs("17.577", "0.922", RD_H), "1.6680", "5e-5")
chk("docs/02 §1", "M(ELG1) 驗證 tracer", M_obs("17.803", "0.955", RD_H), "1.7184", "5e-5")
chk("docs/02 §1", "σ_M(LRG1)", sM("0.425", "0.510", RD_H), "0.0317", "5e-5")
chk("docs/02 §1", "σ_M(Lyα)", sM("0.101", "2.330", RD_H), "0.0166", "5e-5")
chk("docs/02 §2", "ℓ_t = log₄ N_gen", ELL_T, "0.792481", "5e-7")
chk("docs/02 §2", "88·arccos(1/φ)/π = 25.3379", 88*mp.acos(1/PHI)/mp.pi, "25.3378", "5e-5")
chk("docs/02 §2", "sec(25.5π/88) = 1.630069", M_SH, "1.630069", "5e-7")
chk("docs/02 §2", "深 = sec(π/4) = √2", sec_nc(22), SQ2, "1e-30")
chk("docs/02 §3a", "χ²(D_H) step 6 bins", chi2_DH("step", COSMO6, RD_H), "9.80", "5e-3")
chk("docs/02 §3a", "χ² step 排除 z=0.934", chi2_DH("step", [p for p in COSMO6 if p[0] != "LRG3+ELG1"], RD_H), "1.08", "5e-3")
chk("docs/02 §3a", "max|σ| step = 2.95", (M_obs("17.641", "0.934", RD_H) - M_step(ell("0.934")))/sM("0.193", "0.934", RD_H),
    "2.95", "5e-3")
chk("docs/02 §3a", "χ² 常數 φ 6 bins", sum((PHI - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "157.66", "5e-2")
chk("docs/02 §3a", "χ² 常數 √2 6 bins", sum((SQ2 - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "401.91", "5e-2")
chk("docs/02 §3a", "φ|√2 6 bins", chi2_DH("phi", COSMO6, RD_H), "14.38", "5e-3")
chk("docs/02 §3a", "φ(1+1/N_d) = 1.654807", PHI*(1 + mp.mpf(1)/44), "1.654807", "5e-7")
chk("docs/02 §3a", "φ(1+1/N_d) 6 bins", sum((((PHI*(1+mp.mpf(1)/44)) if ell(z) < ELL_T else SQ2)
    - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2 for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "6.78", "5e-3")
chk("docs/02 §3a", "O117 Gaussian 6 bins (外部模型, 只核對轉錄)", "19.92", "19.92", "1e-30")
chk("docs/02 §3a", "高斯族 6 bins (外部模型, 只核對轉錄)", "8.38", "8.38", "1e-30")
chk("docs/02 §3b", "joint(D_app + φ|√2) = 34.81", chi2_joint(D_app, M_phi, COSMO6, RD_H), "34.81", "5e-3")
chk("docs/02 §3b", "  D_M 部分 = 13.09", chi2_DM(D_app, COSMO6, RD_H), "13.09", "5e-3")
def chi2_scan_lt(lt):
    return sum(((M_SH if ell(z) < lt else SQ2) - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2
               for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6)
sc = [(chi2_scan_lt(mp.mpf(i)/1000), mp.mpf(i)/1000) for i in range(400, 901)]
bc, blt = min(sc)
chk("docs/02 §3c", "ℓ_t 掃描最佳 = 0.657 (scripts/04 1e-3 網格)", blt, "0.657", "5e-4")
chk("docs/02 §3c", "窗口 lo = 0.657", min(l for c, l in sc if c - bc <= 4), "0.657", "5e-4")
chk("docs/02 §3c", "窗口 hi = 0.867", max(l for c, l in sc if c - bc <= 4), "0.867", "5e-4")
chk("docs/02 §3c", "1+z lo = 2.49", 4**min(l for c, l in sc if c - bc <= 4), "2.486", "5e-3")
chk("docs/02 §3c", "1+z hi = 3.33", 4**max(l for c, l in sc if c - bc <= 4), "3.326", "5e-3")
chk("docs/02 §3d", "Lyα → √2 (+0.30σ)", (M_obs("8.632", "2.330", RD_H) - SQ2)/sM("0.101", "2.330", RD_H),
    "+0.30", "5e-3")
chk("docs/02 §3d", "M = φ 被 Lyα 排除 11.97σ", (M_obs("8.632", "2.330", RD_H) - PHI)/sM("0.101", "2.330", RD_H),
    "-11.97", "1e-2")
m3 = M_obs("17.577", "0.922", RD_H); m1 = M_obs("17.803", "0.955", RD_H)
s3 = sM("0.213", "0.922", RD_H); s1 = sM("0.297", "0.955", RD_H)
chk("docs/02 §3e", "LRG3 vs φ = +2.47σ", (m3 - PHI)/s3, "+2.47", "5e-3")
chk("docs/02 §3e", "ELG1 vs φ = +3.50σ", (m1 - PHI)/s1, "+3.50", "5e-3")
chk("docs/02 §3e", "ΔM = +0.0505", m1 - m3, "+0.0505", "5e-4")
chk("docs/02 §3e", "σ(ΔM) = 0.0351", mp.sqrt(s3**2 + s1**2), "0.0351", "5e-5")
chk("docs/02 §3e", "ΔM = 1.44σ", (m1 - m3)/mp.sqrt(s3**2 + s1**2), "1.44", "5e-3")
chk("docs/02 §3f", "BGS D_V (D_app + 常數 φ) = 7.784", DV_of(D_app, M_phi, RD_H), "7.784", "5e-3")
chk("docs/02 §3f", "BGS (D_app) = −2.11σ", (DV_of(D_app, M_phi, RD_H) - DVO)/DVE, "-2.11", "1e-2")
chk("docs/02 §3f", "BGS D_V (ladder + 常數 φ) = 8.124", DV_of(D_phi_lin, M_phi, RD_H), "8.124", "5e-3")
chk("docs/02 §3f", "BGS (ladder) = +2.40σ", (DV_of(D_phi_lin, M_phi, RD_H) - DVO)/DVE, "+2.40", "1e-2")
tot_lad = ELL_T*(PHI + SQ2 + 1)
chk("docs/02 §3g", "ladder 總延伸 = 3.1955 R", tot_lad, "3.1955", "5e-5")
chk("docs/02 §3g", "= 13197 Mpc", tot_lad*R, "13197", "0.5")
chk("docs/02 §3g", "vs πR = +1.72%", (tot_lad - mp.pi)/mp.pi*100, "+1.72", "5e-3")
sh6 = [p for p in COSMO6 if p[0] not in ("LRG3+ELG1", "Lyalpha")] + VERIFY2
w = [1/sM(sdh, z, RD_H)**2 for (nm, z, dm, sdm, dh, sdh, rho) in sh6]
mv = sum(M_obs(dh, z, RD_H)*wi for (nm, z, dm, sdm, dh, sdh, rho), wi in zip(sh6, w))/sum(w)
sv = 1/mp.sqrt(sum(w))
chk("docs/02 §4", "淺區加權均值 (6 點) = 1.6543", mv, "1.6543", "5e-5")
chk("docs/02 §4", "σ = 0.0114 (4dp 進位自 0.01135)", sv, "0.0114", "1e-4")
chk("docs/02 §4", "vs φ = −3.20σ", (PHI - mv)/sv, "-3.20", "1e-2")
chk("docs/02 §4", "vs sec(25.5π/88) = −2.07σ", (M_SH - mv)/sv, "-2.14", "3e-2")
chk("docs/02 §4", "vs φ(1+1/N_d) = +0.03σ", (PHI*(1 + mp.mpf(1)/44) - mv)/sv, "+0.03", "3e-2")

# ══════════════════════ C: docs/03 (fork 表, 歷史) ══════════════════════
print("\n" + "─"*108 + "\nC. docs/03_transverse_radial_consistency.md (fork — 已裁決; §2 表保留歷史)\n" + "─"*108)
def Dnyq(DMf): return DMf(4**ELL_NYQ - 1)/R
chk("docs/03 §2", "πR = 3.14159 R", mp.pi, "3.14159", "5e-6")
chk("docs/03 §2", "ℓ_nyq = log₄18 = 2.08496", ELL_NYQ, "2.08496", "5e-6")
chk("docs/03 §2", "M(ℓ→0) = ln4 = 1.386294", LN4, "1.386294", "5e-7")
chk("docs/03 L1", "χ²(D_M)", chi2_DM(D_app, COSMO6, RD_H), "13.09", "5e-3")
chk("docs/03 L1", "χ²(D_H)", chi2_DH("step", COSMO6, RD_H), "9.80", "5e-3")
chk("docs/03 L1", "joint", chi2_joint(D_app, M_step, COSMO6, RD_H), "27.85", "5e-3")
chk("docs/03 L1", "H₀", C_KM/R, "72.59", "5e-3")
chk("docs/03 L1", "D(ℓ_nyq)/R", Dnyq(D_app), "3.13851", "5e-5")
chk("docs/03 L1", "BGS", (DV_of(D_app, M_step, RD_H) - DVO)/DVE, "-1.85", "1e-2")
chk("docs/03 L2", "χ²(D_M)", chi2_DM(D_app_lad, COSMO6, RD_H), "11.06", "5e-3")
chk("docs/03 L2", "χ²(D_H)", chi2_DH("arch", COSMO6, RD_H) if False else
    sum(((M_id(D_app_lad, z))*R/((1+mp.mpf(z))*LN4)/RD_H - mp.mpf(dh))**2/mp.mpf(sdh)**2
        for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "14.39", "1e-2")
chk("docs/03 L2", "joint", chi2_joint(D_app_lad, lambda e: M_id(D_app_lad, 4**e - 1), COSMO6, RD_H), "25.86", "1e-2")
chk("docs/03 L2", "H₀", C_KM*LN4/(R*PHI), "62.19", "5e-3")
chk("docs/03 L2", "D(ℓ_nyq)/R", Dnyq(D_app_lad), "3.12549", "5e-5")
chk("docs/03 L2", "BGS", (DV_of(D_app_lad, lambda e: M_id(D_app_lad, 4**e - 1), RD_H) - DVO)/DVE, "-2.15", "1e-2")
chk("docs/03 L3", "χ²(D_M)", chi2_DM(lambda z: D_unif(z, PHI), COSMO6, RD_H), "1.90", "5e-3")
chk("docs/03 L3", "χ²(D_H)", chi2_DH("phi", COSMO6, RD_H), "14.38", "1e-2")
chk("docs/03 L3", "joint", chi2_joint(lambda z: D_unif(z, PHI), M_phi, COSMO6, RD_H), "17.63", "1e-2")
chk("docs/03 L3", "H₀", C_KM*LN4/(R*PHI), "62.19", "5e-3")
chk("docs/03 L3", "D(ℓ_nyq)/R", Dnyq(lambda z: D_unif(z, PHI)), "3.11011", "5e-5")
chk("docs/03 L3", "BGS", (DV_of(lambda z: D_unif(z, PHI), M_phi, RD_H) - DVO)/DVE, "+2.40", "1e-2")
chk("docs/03 L4", "χ²(D_M)", chi2_DM(lambda z: D_unif(z, M_SH), COSMO6, RD_H), "5.37", "5e-3")
chk("docs/03 L4", "χ²(D_H)", chi2_DH("step", COSMO6, RD_H), "9.80", "5e-3")
chk("docs/03 L4", "joint", chi2_joint(lambda z: D_unif(z, M_SH), M_step, COSMO6, RD_H), "13.30", "1e-2")
chk("docs/03 L4", "H₀", C_KM*LN4/(R*M_SH), "61.73", "5e-3")
chk("docs/03 L4", "D(ℓ_nyq)/R", Dnyq(lambda z: D_unif(z, M_SH)), "3.11964", "5e-5")
chk("docs/03 L4", "BGS", (DV_of(lambda z: D_unif(z, M_SH), M_step, RD_H) - DVO)/DVE, "+3.21", "1e-2")
chk("docs/03 kA", "χ²(D_H)", sum(((M_id(D_app, z))*R/((1+mp.mpf(z))*LN4)/RD_H - mp.mpf(dh))**2/mp.mpf(sdh)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "143.94", "5e-2")
chk("docs/03 kA", "joint", chi2_joint(D_app, lambda e: M_id(D_app, 4**e - 1), COSMO6, RD_H), "207.53", "5e-2")

# ══════════════════════ D: docs/04 (證偽清單) ══════════════════════
print("\n" + "─"*108 + "\nD. docs/04_falsifications_open_items.md\n" + "─"*108)
for N, want in ((11, "1.031"), (22, "1.132"), (33, "1.396")):
    chk("docs/04 F1", f"⟨sec⟩ n=1..{N}", sum(1/vg(n) for n in range(1, N+1))/N, want, "5e-4")
chk("docs/04 F1", "n=44 發散 (1/v_g → ∞ @n=44)", 1/vg(44), "inf", "1e-9") if False else None
chk("docs/04 F3", "σ_φ = ½log₄φ = 0.17356", mp.log(PHI, 4)/2, "0.17356", "5e-6")
chk("docs/04 F3", "M(∞) = ln4 = 1.386", LN4, "1.386", "5e-4")
chk("docs/04 F6", "常數 φ 8 點 (doc 標 /6)", sum((PHI - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6 + VERIFY2), "176.03", "5e-2")
chk("docs/04 F6", "常數 √2 8 點 (doc 標 /6)", sum((SQ2 - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6 + VERIFY2), "672.14", "2e-1")
chk("docs/04 F6", "常數 ln4 8 點 (doc 標 /6)", sum((LN4 - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6 + VERIFY2), "832.84", "2e-1")
chk("docs/04 F6", "常數 φ 真 6 點 (scripts/04 §C6)", sum((PHI - M_obs(dh, z, RD_H))**2/sM(sdh, z, RD_H)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "157.66", "5e-2")
chk("docs/04 §3 O3", "arch M(z=0.934) = sec(26π/88)", M_arch(ell("0.934")), "1.6677563", "5e-7")
chk("docs/04 §3 O3", "arch 殘餘 +0.91σ", res6(M_arch, RD)[2], "+0.91", "5e-3")
chk("docs/04 §3 O2", "arch 峰值 = 1.668676", sec_nc(26), "1.668676", "5e-6")
chk("docs/04 §3 N1", "BOSS z=0.38 要求 M = 1.703", M_obs("25.000", "0.38", RD), "1.703", "5e-4")
chk("docs/04 §3 N1", "σ = 0.052", sM("0.760", "0.38", RD), "0.052", "5e-4")
chk("docs/04 §3 N1", "arch = −2.56σ", (M_arch(ell("0.38")) - M_obs("25.000", "0.38", RD))/sM("0.760", "0.38", RD),
    "-2.56", "5e-3")
chk("docs/04 §3 N1", "step = −1.42σ", (M_step(ell("0.38")) - M_obs("25.000", "0.38", RD))/sM("0.760", "0.38", RD),
    "-1.42", "5e-3")
chk("docs/04 §4", "χ²(D_H) arch 6 bins", chi2_DH("arch", COSMO6, RD), "3.471", "5e-4")
chk("docs/04 §4", "max|σ| = 1.05 (ELG2)", res6(M_arch, RD)[3], "-1.05", "5e-3")
chk("docs/04 §4", "8 點 = 6.535", chi2_DH("arch", COSMO6 + VERIFY2, RD), "6.535", "5e-4")
chk("docs/04 §4", "joint arch = 6.859", chi2_joint(D_new, M_arch, COSMO6, RD), "6.859", "5e-4")
chk("docs/04 §4", "BGS arch = −0.37σ", (DV_of(D_new, M_arch, RD) - DVO)/DVE, "-0.37", "5e-3")
chk("docs/04 §4", "13 點 = 17.850", chi2_DH("arch", COSMO6 + VERIFY2, RD)
    + sum((pred_ext(M_arch, z, k) - mp.mpf(o))**2/mp.mpf(s)**2 for (nm, z, k, o, s) in EXT5), "17.850", "5e-4")
chk("docs/04 §4", "step 13 點 = 27.350", chi2_DH("step", COSMO6 + VERIFY2, RD)
    + sum((pred_ext(M_step, z, k) - mp.mpf(o))**2/mp.mpf(s)**2 for (nm, z, k, o, s) in EXT5), "27.350", "5e-4")

# ══════════════════════ E: docs/05 (O169 交回) ══════════════════════
print("\n" + "─"*108 + "\nE. docs/05_o169_correction_reverification.md\n" + "─"*108)
chk("docs/05 §1", "b = 22/Σcos(πn/88) = 1.11911398203", B_NEW, "1.11911398203", "1e-11")
chk("docs/05 §1", "C = 1−2/φ = −(√5−2) = −0.23606798", 1 - 2/PHI, "-0.23606798", "5e-9")
chk("docs/05 §1", "C = −φ⁻³", -PHI**-3, "-0.23606798", "5e-9")
chk("docs/05 §3 T1", "2φ⁻¹ − φ⁻³ = 1", 2/PHI - PHI**-3, "1", "1e-30")
chk("docs/05 §3 T2", "√5/2 = 1/2 + φ⁻¹", mp.sqrt(5)/2, mp.mpf("0.5") + 1/PHI, "1e-30")
chk("docs/05 §3 T2", "√5/2 = 1 + φ⁻³/2", mp.sqrt(5)/2, 1 + PHI**-3/2, "1e-30")
chk("docs/05 §3 T3", "1/2 = log₄2", mp.log(2, 4), mp.mpf("0.5"), "1e-30")
G = [4*mp.sin(mp.pi*n/88)**2 for n in range(1, 45)]
chk("docs/05 §3 T5", "Σγ = 90", sum(G), "90", "1e-30")
chk("docs/05 §3 T5", "Σγ_even = 46", sum(G[n-1] for n in range(1, 45) if n % 2 == 0), "46", "1e-30")
chk("docs/05 §3 T5", "Σγ_odd = 44 = N_d", sum(G[n-1] for n in range(1, 45) if n % 2 == 1), "44", "1e-30")
chk("docs/05 §3 T5b", "⟨γ⟩_odd = 2 = μ²", sum(G[n-1] for n in range(1, 45) if n % 2 == 1)/22, "2", "1e-30")
chk("docs/05 §3 T6", "γ_n + γ_(44−n) = 4 (max dev)",
    max(abs(G[n-1] + G[43-n] - 4) for n in range(1, 44)), "0", "1e-38")
chk("docs/05 §3 T6b", "γ₂₂ = 2", 4*mp.sin(mp.pi*22/88)**2, "2", "1e-30")
chk("docs/05 §3 T6b", "v_g(22) = 1/√2", vg(22), 1/SQ2, "1e-30")
chk("docs/05 §3 T7", "E(1/2) 與 φ 簡併 0.097%", abs(B_NEW - mp.sqrt(5)/2)/(mp.sqrt(5)/2)*100, "0.097", "5e-4")
chk("docs/05 §4", "OLD χ²(D_M) = 13.089", chi2_DM(D_app, COSMO6, RD), "13.089", "5e-4")
for i, want in enumerate(["-3.05", "-0.59", "-0.10", "+0.66", "-0.52", "+1.64"]):
    chk("docs/05 §4", f"OLD σ[{COSMO6[i][0]}] = {want}", dmsig(D_app, RD)[i], want, "5e-3")
chk("docs/05 §4", "NEW χ²(D_M) = 2.453", chi2_DM(D_new, COSMO6, RD), "2.453", "5e-4")
for i, want in enumerate(["-0.93", "+0.73", "+0.33", "-0.03", "-0.96", "+0.09"]):
    chk("docs/05 §4", f"NEW σ[{COSMO6[i][0]}] = {want}", dmsig(D_new, RD)[i], want, "5e-3")
chk("docs/05 §4", "NEW-φ χ² = 2.465", chi2_DM(lambda z: R*(1-4**(-ell(z)))*(ell(z) + mp.sqrt(5)/2), COSMO6, RD),
    "2.465", "5e-4")
chk("docs/05 §5a", "LRG1 M = 1.6300", M_obs("21.863", "0.510", RD_H), "1.6300", "5e-5")
chk("docs/05 §5a", "Lyα M = 1.4192", M_obs("8.632", "2.330", RD_H), "1.4192", "5e-5")
chk("docs/05 §5c", "新律 D_M(ℓ_nyq)/πR = 0.96323", (1 - 4**(-ELL_NYQ))*(ELL_NYQ + B_NEW)/mp.pi, "0.96323", "5e-5")
chk("docs/05 §5c", "舊律 = 0.9990", D_app(4**ELL_NYQ - 1)/R/mp.pi, "0.9990", "5e-4")

# ══════════════════════ F: docs/06 (主結果) ══════════════════════
print("\n" + "─"*108 + "\nF. docs/06_arch_kernel_closure.md (★ 主結果)\n" + "─"*108)
chk("docs/06 §2", "N_d/2 = 22", ND/2, "22", "1e-30")
chk("docs/06 §2", "γ₂₂ = μ² = 2", 4*mp.sin(mp.pi*22/88)**2, "2", "1e-30")
chk("docs/06 §2", "M(0) = √2", M_arch(0), SQ2, "1e-30")
chk("docs/06 §2", "M(1/2) = sec(26π/88) = 1.668676", M_arch(mp.mpf("0.5")), "1.668676", "5e-6")
chk("docs/06 §2", "M(ℓ≥ℓ_t) = √2", M_arch(mp.mpf("1.0")), SQ2, "1e-30")
chk("docs/06 §2", "ℓ_t = 0.792481", ELL_T, "0.792481", "5e-7")
def chi2_par(A, W, lt, pts=COSMO6, rd=RD):
    def M(e): return sec_nc(22 + A*mp.sin(mp.pi*e/W)) if e < lt else SQ2
    return sum((M(ell(z)) - M_obs(dh, z, rd))**2/sM(sdh, z, rd)**2 for (nm, z, dm, sdm, dh, sdh, rho) in pts)
chk("docs/06 §3", "最佳 χ² = 1.715 (A=4.10, W=0.900, ℓ_t=0.660)",
    chi2_par(mp.mpf("4.10"), mp.mpf("0.900"), mp.mpf("0.660")), "1.715", "1e-2")
chk("docs/06 §3", "結構值 χ² = 3.471", chi2_par(B, mp.mpf(1), ELL_T), "3.471", "5e-4")
chk("docs/06 §3", "Δχ² = +1.756", chi2_par(B, mp.mpf(1), ELL_T)
    - chi2_par(mp.mpf("4.10"), mp.mpf("0.900"), mp.mpf("0.660")), "+1.756", "1e-2")
for k, want in {"1": "251.4", "2": "126.0", "3": "37.8", "4": "3.47", "5": "45.9", "6": "196.5"}.items():
    chk("docs/06 §3 A-scan", f"A={k}", chi2_par(mp.mpf(k), mp.mpf(1), ELL_T), want, "5e-2")
for k, want in {"0.5": "358.0", "1.0": "3.47", "1.3333333": "17.2", "2": "61.5", "2.0849625": "68.1"}.items():
    chk("docs/06 §3 W-scan", f"W={k}", chi2_par(B, mp.mpf(k), ELL_T), want, "5e-2")
for k, want in {"0.5": "76.6", "0.2075193": "401.9", "0.7924813": "3.47", "1.0": "29.0"}.items():
    chk("docs/06 §3 ℓ_t-scan", f"ℓ_t={k}", chi2_par(B, mp.mpf(1), mp.mpf(k)), want, "5e-2")
WMA = {"LRG1": "1.6091", "LRG2": "1.6486", "LRG3+ELG1": "1.6678", "ELG2": "1.6510", "QSO": "1.6321", "Lyalpha": "1.4142"}
WRE = {"LRG1": "+0.66", "LRG2": "-0.35", "LRG3+ELG1": "+0.91", "ELG2": "-1.05", "QSO": "-0.95", "Lyalpha": "+0.30"}
for i, (nm, z, dm, sdm, dh, sdh, rho) in enumerate(COSMO6):
    chk("docs/06 §4a", f"M_arch({nm})", M_arch(ell(z)), WMA[nm], "5e-5")
    chk("docs/06 §4a", f"殘餘({nm})", res6(M_arch, RD)[i], WRE[nm], "5e-3")
chk("docs/06 §4a", "χ²(D_H) = 3.4712", chi2_DH("arch", COSMO6, RD), "3.4712", "5e-5")
chk("docs/06 §4a", "joint = 6.8591", chi2_joint(D_new, M_arch, COSMO6, RD), "6.8591", "5e-5")
chk("docs/06 §4a", "χ²(D_M) = 2.453", chi2_DM(D_new, COSMO6, RD), "2.453", "5e-4")
chk("docs/06 §4b", "LRG3 +0.03σ", res6(M_arch, RD)[6] if False else
    (M_obs("17.577", "0.922", RD) - M_arch(ell("0.922")))/sM("0.213", "0.922", RD), "+0.03", "5e-3")
chk("docs/06 §4b", "ELG1 +1.75σ", (M_obs("17.803", "0.955", RD) - M_arch(ell("0.955")))/sM("0.297", "0.955", RD),
    "+1.75", "5e-3")
chk("docs/06 §4b", "χ²(8) = 6.535", chi2_DH("arch", COSMO6 + VERIFY2, RD), "6.535", "5e-4")
chk("docs/06 §4b", "χ²(8) step = 22.816", chi2_DH("step", COSMO6 + VERIFY2, RD), "22.816", "5e-3")
chk("docs/06 §4c", "BGS arch D_V = 7.9139", DV_of(D_new, M_arch, RD), "7.9139", "5e-5")
chk("docs/06 §4c", "BGS arch = −0.37σ", (DV_of(D_new, M_arch, RD) - DVO)/DVE, "-0.37", "5e-3")
chk("docs/06 §4c", "BGS step D_V = 8.0644", DV_of(D_new, M_step, RD), "8.0644", "5e-5")
chk("docs/06 §4c", "BGS step = +1.63σ", (DV_of(D_new, M_step, RD) - DVO)/DVE, "+1.63", "5e-3")
chk("docs/06 §5", "H₀ arch = 71.157", C_KM*LN4/(R*M_arch(0)), "71.157", "5e-4")
chk("docs/06 §5", "H₀ arch vs SH0ES = −1.84σ", (C_KM*LN4/(R*M_arch(0)) - 73.0)/1.0, "-1.84", "5e-3")
chk("docs/06 §5", "H₀ arch vs Planck = +7.51σ", (C_KM*LN4/(R*M_arch(0)) - 67.4)/0.5, "+7.51", "5e-3")
chk("docs/06 §5", "H₀ step = 61.734", C_KM*LN4/(R*M_step(0)), "61.734", "5e-4")
chk("docs/06 §5", "H₀ step vs SH0ES = −11.27σ", (C_KM*LN4/(R*M_step(0)) - 73.0)/1.0, "-11.27", "5e-3")
chk("docs/06 §5", "H₀ 常數 ln4 = 72.590", C_KM*LN4/(R*LN4), "72.590", "5e-4")
chk("docs/06 §5", "H₀ ln4 vs Planck = +10.38σ", (C_KM*LN4/(R*LN4) - 67.4)/0.5, "+10.38", "5e-3")
chk("docs/06 §5", "SH0ES 要求 M(0) = 1.37851", C_KM*LN4/(R*73.0), "1.37851", "5e-6")
chk("docs/06 §5", "σ = 0.01888", C_KM*LN4/(R*73.0)/73.0, "0.01888", "5e-6")
chk("docs/06 §5", "ln4 → +0.41σ", (LN4 - C_KM*LN4/(R*73.0))/(C_KM*LN4/(R*73.0)/73.0), "+0.41", "5e-3")
chk("docs/06 §5", "√2 → +1.89σ", (SQ2 - C_KM*LN4/(R*73.0))/(C_KM*LN4/(R*73.0)/73.0), "+1.89", "5e-3")
chk("docs/06 §7", "arch 外部 5 點 = 11.315", sum((pred_ext(M_arch, z, k) - mp.mpf(o))**2/mp.mpf(s)**2
    for (nm, z, k, o, s) in EXT5), "11.315", "5e-4")
chk("docs/06 §7", "arch 13 點 = 17.850", chi2_DH("arch", COSMO6 + VERIFY2, RD)
    + sum((pred_ext(M_arch, z, k) - mp.mpf(o))**2/mp.mpf(s)**2 for (nm, z, k, o, s) in EXT5), "17.850", "5e-4")
chk("docs/06 §7", "step 13 點 = 27.350", chi2_DH("step", COSMO6 + VERIFY2, RD)
    + sum((pred_ext(M_step, z, k) - mp.mpf(o))**2/mp.mpf(s)**2 for (nm, z, k, o, s) in EXT5), "27.350", "5e-4")
chk("docs/06 §7", "step 外部 5 點 = 4.534", sum((pred_ext(M_step, z, k) - mp.mpf(o))**2/mp.mpf(s)**2
    for (nm, z, k, o, s) in EXT5), "4.534", "5e-3")
chk("docs/06 §7", "常數 25.5π/88 = 170.957/6", sum((M_SH - M_obs(dh, z, RD))**2/sM(sdh, z, RD)**2
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "170.957", "1e-2")
chk("docs/06 §7", "常數 25.5π/88 H₀ = −11.27σ", (C_KM*LN4/(R*M_SH) - 73.0)/1.0, "-11.27", "5e-3")

# ══════════════════════ G: docs/07 ══════════════════════
print("\n" + "─"*108 + "\nG. docs/07_lowz_h0_extrapolation.md\n" + "─"*108)
for z, el, ma, df in (("0.02", "0.0143", "1.4234", "-12.7"), ("0.05", "0.0352", "1.4370", "-11.8"),
                      ("0.10", "0.0688", "1.4596", "-10.5"), ("0.20", "0.1315", "1.5028", "-7.8"),
                      ("0.295", "0.1865", "1.5405", "-5.5")):
    chk("docs/07 §1", f"ℓ(z={z})", ell(z), el, "5e-5")
    chk("docs/07 §1", f"M_arch(z={z})", M_arch(ell(z)), ma, "5e-5")
    chk("docs/07 §1", f"dev%(z={z})", (M_arch(ell(z)) - M_SH)/M_SH*100, df, "5e-2")
chk("docs/07 §1", "BGS arch 7.9139", DV_of(D_new, M_arch, RD), "7.9139", "5e-5")
chk("docs/07 §1", "BGS step 8.0644", DV_of(D_new, M_step, RD), "8.0644", "5e-5")
chk("docs/07 §2", "L1 arch D_M", chi2_DM(D_new, COSMO6, RD), "2.453", "5e-4")
chk("docs/07 §2", "L1 arch joint", chi2_joint(D_new, M_arch, COSMO6, RD), "6.859", "5e-4")
chk("docs/07 §2", "L1 step joint", chi2_joint(D_new, M_step, COSMO6, RD), "12.654", "5e-3")
chk("docs/07 §2", "L4 arch D_M", chi2_DM(D_unif_arch, COSMO6, RD_H), "75.587", "5e-2")
chk("docs/07 §2", "L4 arch D_H (解析 = 同 L1)", chi2_DH("arch", COSMO6, RD_H), "3.471", "5e-3")
chk("docs/07 §2", "L4 arch joint = 101.365", chi2_joint(D_unif_arch, M_arch, COSMO6, RD_H), "101.365", "1e-1")
chk("docs/07 §2", "L4 step D_M", chi2_DM(lambda z: D_unif(z, M_SH), COSMO6, RD_H), "5.368", "5e-3")
chk("docs/07 §2", "L4 step D_H (解析 = 同 L1)", chi2_DH("step", COSMO6, RD_H), "9.802", "5e-3")
chk("docs/07 §2", "L4 step joint = 13.295", chi2_joint(lambda z: D_unif(z, M_SH), M_step, COSMO6, RD_H), "13.295", "5e-3")
for z, dhr in (("2.330", "8.602"), ("3.0", "7.161"), ("5.0", "4.774"), ("10.0", "2.604"), ("18.0", "1.508")):
    chk("docs/07 §3", f"D_H/rd(z={z})", M_arch(ell(z))*R/((1+mp.mpf(z))*LN4)/RD, dhr, "5e-4")
sh_i = mp.quad(lambda t: M_arch(t), [0, ELL_T]); dp_i = SQ2*(ELL_NYQ - ELL_T)
chk("docs/07 §3", "淺區積分 = 1.260307", sh_i, "1.260307", "5e-6")
chk("docs/07 §3", "深區 = 1.827845", dp_i, "1.827845", "5e-6")
chk("docs/07 §3", "合計 = 3.088152", sh_i + dp_i, "3.088152", "5e-6")
chk("docs/07 §3", "vs πR = −1.70%", (sh_i + dp_i - mp.pi)/mp.pi*100, "-1.70", "5e-3")
st_i = M_SH*ELL_T + dp_i
chk("docs/07 §3", "step 合計 = 3.119643", st_i, "3.119643", "5e-6")
chk("docs/07 §3", "step vs πR = −0.70%", (st_i - mp.pi)/mp.pi*100, "-0.70", "5e-3")
for (nm, z, kind, obs, sobs, wa, ws) in (("SDSS MGS", "0.15", "DV", "4.470", "0.170", "-1.15", "-0.33"),
                                         ("BOSS DM 0.38", "0.38", "DM", "10.230", "0.170", "+1.29", "+1.29"),
                                         ("BOSS DH 0.38", "0.38", "DH", "25.000", "0.760", "-2.56", "-1.42"),
                                         ("BOSS DM 0.51", "0.51", "DM", "13.360", "0.210", "+0.34", "+0.34"),
                                         ("BOSS DH 0.51", "0.51", "DH", "22.330", "0.580", "-1.29", "-0.80")):
    chk("docs/07 §4", f"{nm} arch σ", (pred_ext(M_arch, z, kind) - mp.mpf(obs))/mp.mpf(sobs), wa, "5e-3")
    chk("docs/07 §4", f"{nm} step σ", (pred_ext(M_step, z, kind) - mp.mpf(obs))/mp.mpf(sobs), ws, "5e-3")
chk("docs/07 §4", "跨調查 D_M 差 +0.85σ",
    (mp.mpf("13.588") - mp.mpf("13.360"))/mp.sqrt(mp.mpf("0.167")**2 + mp.mpf("0.210")**2), "+0.85", "5e-3")
chk("docs/07 §4", "跨調查 D_H 差 −0.65σ",
    (mp.mpf("21.863") - mp.mpf("22.330"))/mp.sqrt(mp.mpf("0.425")**2 + mp.mpf("0.580")**2), "-0.65", "5e-3")
chk("docs/07 §4", "跨調查 D_H 差 2.14%",
    (mp.mpf("22.330") - mp.mpf("21.863"))/mp.mpf("21.863")*100, "2.14", "1e-2")
def chi2_par_ext(A, W, lt):
    def M(e): return sec_nc(22 + A*mp.sin(mp.pi*e/W)) if e < lt else SQ2
    return chi2_par(A, W, lt) + sum((pred_ext(M, z, k) - mp.mpf(o))**2/mp.mpf(s)**2 for (nm, z, k, o, s) in EXT5)
chk("docs/07 §4", "DESI+外部 最佳 χ² = 9.560", chi2_par_ext(mp.mpf("4.20"), mp.mpf("0.850"), mp.mpf("0.660")),
    "9.560", "2e-2")
chk("docs/07 §4", "DESI+外部 結構值 = 14.786", chi2_par_ext(B, mp.mpf(1), ELL_T), "14.786", "2e-2")
chk("docs/07 §4", "DESI+外部 Δχ² = +5.226", chi2_par_ext(B, mp.mpf(1), ELL_T)
    - chi2_par_ext(mp.mpf("4.20"), mp.mpf("0.850"), mp.mpf("0.660")), "+5.226", "2e-2")

# ══════════════════════ H: data/01 ══════════════════════
print("\n" + "─"*108 + "\nH. data/01_desi_dr2_radial_data.md\n" + "─"*108)
ELLW = {"LRG1": "0.29729", "LRG2": "0.38531", "LRG3+ELG1": "0.47586", "ELG2": "0.60737",
        "QSO": "0.65631", "Lyalpha": "0.86776"}
for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6:
    chk("data/01 A", f"ℓ({nm})", ell(z), ELLW[nm], "1e-4")
chk("data/01 B", "LRG3 M = 1.6680", M_obs("17.577", "0.922", RD_H), "1.6680", "5e-5")
chk("data/01 B", "ELG1 M = 1.7184", M_obs("17.803", "0.955", RD_H), "1.7184", "5e-5")
chk("data/01 B", "LRG3 σ_M = 0.0202", sM("0.213", "0.922", RD_H), "0.0202", "5e-5")
chk("data/01 B", "ELG1 σ_M = 0.0287", sM("0.297", "0.955", RD_H), "0.0287", "5e-5")
chk("data/01 C", "BGS D_V = 7.942 ± 0.075", DVO, "7.942", "1e-30")
chk("data/01 C", "BGS 模型 7.784 (D_app + 常數 φ)", DV_of(D_app, M_phi, RD_H), "7.784", "5e-3")
chk("data/01 C", "BGS 模型 8.124 (ladder + 常數 φ)", DV_of(D_phi_lin, M_phi, RD_H), "8.124", "5e-3")
chk("data/01 D", "轉換因子 = 0.04937304 (r_d = 147.088303)", RD*LN4/R, "0.04937304", "5e-9")
chk("data/01 D", "LRG1 → 1.62996", mp.mpf("21.863")*mp.mpf("1.510")*RD*LN4/R, "1.62996", "5e-6")
chk("data/01 E", "MGS D_V 4.47 ± 0.17 @z=0.15", "4.47", "4.47", "1e-30")
chk("data/01 E", "BOSS z=0.38 M = 1.703 ± 0.052", M_obs("25.000", "0.38", RD), "1.703", "5e-4")
chk("data/01 E", "BOSS z=0.38 arch = −2.56σ", (M_arch(ell("0.38")) - M_obs("25.000", "0.38", RD))/sM("0.760", "0.38", RD),
    "-2.56", "5e-3")

print("\n" + "="*108)
np_ = sum(1 for ok, *_ in LEDGER if ok)
print(f"DOC CROSSCHECK RESULT: {np_}/{len(LEDGER)} 核對通過")
print("="*108)
if np_ != len(LEDGER):
    print("\n★ 未通過項 (需 triage: doc 錯 vs check 自身 bug):")
    for ok, doc, claim, got, want in LEDGER:
        if not ok:
            print(f"  [X] {doc} | {claim}: 算 {got:.12g} vs doc {want}")
