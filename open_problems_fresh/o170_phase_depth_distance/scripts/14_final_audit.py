#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/14 — 最終獨立審計 (independent audit)

目的: 用**獨立代碼路徑**重推 scripts/10-13 嘅頭條數字, 逐項對照 docs/05-07 所寫嘅值。
唔重用 scripts/10-13 嘅任何函數或變數 — 全部由 data/01 嘅原始表重新輸入。

獨立點:
  1. M 轉換式由 data/01 §D 重新實作
  2. 橫向律 D_M 由 raw 表反推形式並重算 (scripts/10 冇明寫, 本腳本由殘餘反推驗證)
  3. 2D χ² 用顯式協方差矩陣求逆 (np-free, 手寫 2x2 逆)
  4. H0 用解析 z→0 斜率 (唔用數值差分)
  5. 積分用 mpmath quad (唔用 sum)
"""
import mpmath as mp

mp.mp.dps = 40

C_KMS = 299792.458
H0_SH0ES, s_SH0ES = 73.0, 1.0
H0_PLANCK, s_PLANCK = 67.4, 0.5
R_WORLD = mp.mpf("4129.94")          # Mpc = c/H0_SH0ES (O167)
RD = mp.pi * R_WORLD / 88 * mp.mpf(420) / 421
LN4 = mp.log(4)
PHI = (1 + mp.sqrt(5)) / 2

def ell_of(z):
    return mp.log(1 + mp.mpf(z)) / LN4

def vg(n):
    return mp.cos(mp.pi * n / 88)

def sec_of_nc(nc):
    return 1 / vg(nc)

# --- 橫向律 (O169): D_M/rd = (R/rd)*(1-4^-ell)*(ell + b),  b = 1/<v_g>_{1..22} ---
B_SHIFT = 22 / sum(vg(n) for n in range(1, 23))

def DM_pred(ell):
    return (R_WORLD / RD) * (1 - mp.power(4, -ell)) * (ell + B_SHIFT)

# --- 徑向核 ---
ELL_T = mp.log(3) / LN4
def nc_arch(ell):
    return 22 + 4 * mp.sin(mp.pi * ell) if ell < ELL_T else mp.mpf(22)
def nc_step(ell):
    return mp.mpf("25.5") if ell < ELL_T else mp.mpf(22)

def M_of(ell, nc_f):
    return sec_of_nc(nc_f(ell))

def DH_pred(ell, nc_f):
    return (R_WORLD / RD) * (mp.power(4, -ell) / LN4) * M_of(ell, nc_f)

def Mobs(dh_rd, z):
    return mp.mpf(dh_rd) * RD * (1 + mp.mpf(z)) * LN4 / R_WORLD

def sM_of(sdh, z):
    """D_H/r_d 誤差 -> M 空間誤差 (同 Mobs 用同一轉換因子)。"""
    return mp.mpf(sdh) * RD * (1 + mp.mpf(z)) * LN4 / R_WORLD

# --- 數據 (逐字由 data/01 抄入, 獨立於 scripts/10-13) ---
COSMO6 = [
    ("LRG1",       "0.510", "13.588", "0.167", "21.863", "0.425", "-0.459"),
    ("LRG2",       "0.706", "17.351", "0.177", "19.455", "0.330", "-0.404"),
    ("LRG3+ELG1",  "0.934", "21.576", "0.152", "17.641", "0.193", "-0.416"),
    ("ELG2",       "1.321", "27.601", "0.318", "14.176", "0.221", "-0.434"),
    ("QSO",        "1.484", "30.512", "0.760", "12.817", "0.516", "-0.500"),
    ("Lyalpha",    "2.330", "38.988", "0.531",  "8.632", "0.101", "-0.431"),
]
VERIFY2 = [
    ("LRG3", "0.922", "21.648", "0.178", "17.577", "0.213", "-0.406"),
    ("ELG1", "0.955", "21.707", "0.335", "17.803", "0.297", "-0.462"),
]
BGS = ("BGS", "0.295", "7.942", "0.075")
EXT = [
    ("SDSS MGS z=0.15 DV", "0.150", "DV", "4.470", "0.170"),
    ("BOSS z=0.38 DM",     "0.380", "DM", "10.230", "0.170"),
    ("BOSS z=0.38 DH",     "0.380", "DH", "25.000", "0.760"),
    ("BOSS z=0.51 DM",     "0.510", "DM", "13.360", "0.210"),
    ("BOSS z=0.51 DH",     "0.510", "DH", "22.330", "0.580"),
]

LEDGER = []
def chk(name, got, want, tol):
    ok = abs(mp.mpf(got) - mp.mpf(want)) <= mp.mpf(tol)
    LEDGER.append((ok, name, float(got), float(want), float(tol)))
    print(("  [PASS] " if ok else "  [FAIL] ") + f"{name}: got {mp.nstr(mp.mpf(got), 12)}  want {want}  (tol {tol})")
    return ok

def joint_chi2(nc_f):
    """2D χ² (D_M, D_H) 用顯式 2x2 協方差 (含 ρ)。"""
    tot = mp.mpf(0)
    for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6:
        e = ell_of(z)
        a = (DM_pred(e) - mp.mpf(dm)) / mp.mpf(sdm)
        b = (DH_pred(e, nc_f) - mp.mpf(dh)) / mp.mpf(sdh)
        r = mp.mpf(rho)
        tot += (a * a + b * b - 2 * r * a * b) / (1 - r * r)
    return tot

print("=" * 100)
print("O170 scripts/14 — 最終獨立審計 (independent code path)")
print("=" * 100)
print(f"R_world = {mp.nstr(R_WORLD, 10)} Mpc   r_d = piR/88*420/421 = {mp.nstr(RD, 12)} Mpc")
print(f"b = 1/<v_g>_{{1..22}} = {mp.nstr(B_SHIFT, 12)}   ell_t = log4(3) = {mp.nstr(ELL_T, 10)}")

print("\n--- A: 常數與結構恆等式 ---")
chk("sqrt2 = sec(pi/4)", 1 / vg(22), mp.sqrt(2), "1e-38")
chk("M(0) arch = sqrt2", M_of(0, nc_arch), mp.sqrt(2), "1e-38")
chk("M peak = sec(26pi/88)", sec_of_nc(26), "1.6686756", "1e-6")
chk("peak at ell = 1/2", M_of(mp.mpf("0.5"), nc_arch), sec_of_nc(26), "1e-38")
chk("M deep (ell>ell_t) = sqrt2", M_of(mp.mpf("1.0"), nc_arch), mp.sqrt(2), "1e-38")
chk("C = 1-2phi^-1 = -phi^-3", 1 - 2 / PHI, -PHI ** -3, "1e-38")

print("\n--- B: M(ell) 表 (由 raw D_H/rd 重算, 對照 data/01 §A) ---")
WANT_M = {"LRG1": "1.6300", "LRG2": "1.6387", "LRG3+ELG1": "1.6845",
          "ELG2": "1.6245", "QSO": "1.5719", "Lyalpha": "1.4192"}
for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6:
    m = Mobs(dh, z)
    print(f"  {nm:10s} z={z}  ell={mp.nstr(ell_of(z),6)}  M = {mp.nstr(m, 8)}")
    chk(f"M_obs({nm})", m, WANT_M[nm], "5e-5")
chk("Lyalpha M -> sqrt2 (0.30 sigma)", (Mobs("8.632", "2.330") - mp.sqrt(2)) / mp.mpf("0.0166"),
    "0.30", "0.01")

print("\n--- C: 橫向律 D_M 逐項 (對照 scripts/10 §T3 NEW) ---")
WANT_DM_SIG = {"LRG1": "-0.93", "LRG2": "+0.73", "LRG3+ELG1": "+0.33",
               "ELG2": "-0.03", "QSO": "-0.96", "Lyalpha": "+0.09"}
for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6:
    s = (DM_pred(ell_of(z)) - mp.mpf(dm)) / mp.mpf(sdm)
    print(f"  {nm:10s} D_M/rd pred = {mp.nstr(DM_pred(ell_of(z)),8)}  obs = {dm} +- {sdm}  -> {mp.nstr(s,5)} sigma")
    chk(f"D_M sigma({nm})", s, WANT_DM_SIG[nm], "0.02")

print("\n--- D: 徑向 χ² 與 2D 聯合 χ² ---")
c6_arch = sum(((M_of(ell_of(z), nc_arch) - Mobs(dh, z)) / sM_of(sdh, z)) ** 2
              for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6)
c6_step = sum(((M_of(ell_of(z), nc_step) - Mobs(dh, z)) / sM_of(sdh, z)) ** 2
              for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6)
print(f"  chi2(D_H x6) arch = {mp.nstr(c6_arch, 10)}    step = {mp.nstr(c6_step, 10)}")
chk("chi2(D_H x6) arch", c6_arch, "3.4712", "0.001")
chk("chi2(D_H x6) step", c6_step, "9.802", "0.01")
jc = joint_chi2(nc_arch)
print(f"  chi2(joint, 2x2 cov incl rho) arch = {mp.nstr(jc, 10)}")
chk("chi2 joint arch", jc, "6.8591", "0.001")
chk("chi2(D_M x6) NEW transverse", sum(((DM_pred(ell_of(z)) - mp.mpf(dm)) / mp.mpf(sdm)) ** 2
                                       for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6), "2.453", "0.005")

print("\n--- E: 8 點 (含驗證 tracer) ---")
c8 = c6_arch + sum(((M_of(ell_of(z), nc_arch) - Mobs(dh, z)) / sM_of(sdh, z)) ** 2
                   for (nm, z, dm, sdm, dh, sdh, rho) in VERIFY2)
print(f"  chi2(8) arch = {mp.nstr(c8, 10)}")
chk("chi2(8) arch", c8, "6.535", "0.002")
for (nm, z, dm, sdm, dh, sdh, rho) in VERIFY2:
    s = (M_of(ell_of(z), nc_arch) - Mobs(dh, z)) / sM_of(sdh, z)
    print(f"  {nm} z={z}  M_obs={mp.nstr(Mobs(dh,z),7)}  M_arch={mp.nstr(M_of(ell_of(z),nc_arch),7)}  {mp.nstr(s,5)} sigma")

print("\n--- F: BGS D_V (最低 ell 獨立點) ---")
zb = mp.mpf(BGS[1]); e = ell_of(zb)
DMb = DM_pred(e); DHb = DH_pred(e, nc_arch)
DV = (zb * DMb * DMb * DHb) ** (mp.mpf(1) / 3)
s = (DV - mp.mpf(BGS[2])) / mp.mpf(BGS[3])
print(f"  z={BGS[1]}  ell={mp.nstr(e,6)}  D_M/rd={mp.nstr(DMb,7)}  D_H/rd={mp.nstr(DHb,7)}")
print(f"  D_V/rd = {mp.nstr(DV,7)}  obs = 7.942 +- 0.075  -> {mp.nstr(s,5)} sigma")
chk("BGS D_V pred", DV, "7.9139", "0.001")
chk("BGS sigma", s, "-0.37", "0.01")

print("\n--- G: 13 點合計 ---")
c_ext = mp.mpf(0)
for (nm, z, kind, obs, sobs) in EXT:
    e = ell_of(z)
    if kind == "DV":
        m = ((mp.mpf(z) * DM_pred(e) ** 2 * DH_pred(e, nc_arch)) ** (mp.mpf(1) / 3))
    elif kind == "DM":
        m = DM_pred(e)
    else:
        m = DH_pred(e, nc_arch)
    s = (m - mp.mpf(obs)) / mp.mpf(sobs)
    c_ext += s * s
    print(f"  {nm:20s} pred = {mp.nstr(m,7)}  obs = {obs} +- {sobs}  -> {mp.nstr(s,5)} sigma")
tot13 = c8 + c_ext
print(f"  外部 5 點 chi2 = {mp.nstr(c_ext,8)}   |   13 點 chi2 = {mp.nstr(tot13,8)}  ({mp.nstr(tot13/13,5)}/dof)")
chk("external 5 chi2", c_ext, "11.315", "0.01")
chk("13-point chi2", tot13, "17.850", "0.01")
chk("13-point chi2/dof", tot13 / 13, "1.373", "0.001")

print("\n--- H: H0 由解析 z->0 斜率 ---")
# D_H(z) = R*4^-ell*M(ell)/ln4, ell = ln(1+z)/ln4
# H(z) = c/D_H'(z); D_H'(0) = R*M(0)/(ln4) * d(4^-ell)/dz|0 = R*M(0)/ln4 * (-ln4) = -R*M(0)
# => H0 = c/(R*M(0)) ... 註: 徑向律嘅 dℓ/dz 因子在 z=0 給出 4^-0/ln4 = 1/ln4
for lbl, nc_f in (("arch", nc_arch), ("step", nc_step)):
    M0 = M_of(0, nc_f)
    h0 = C_KMS / (R_WORLD * M0) * LN4 / LN4   # = c/(R*M0) with ln4/ln4 bookkeeping
    h0b = C_KMS * LN4 / (R_WORLD * M0)
    print(f"  {lbl:5s} M(0) = {mp.nstr(M0,10)}  -> H0 = c*ln4/(R*M0) = {mp.nstr(h0b,8)} km/s/Mpc")
    print(f"        vs SH0ES 73.0+-1.0 -> {mp.nstr((h0b-H0_SH0ES)/s_SH0ES,5)} sigma ; "
          f"vs Planck 67.4+-0.5 -> {mp.nstr((h0b-H0_PLANCK)/s_PLANCK,5)} sigma")
chk("H0 arch", C_KMS * LN4 / (R_WORLD * M_of(0, nc_arch)), "71.157", "0.001")
chk("H0 step", C_KMS * LN4 / (R_WORLD * M_of(0, nc_step)), "61.734", "0.001")
M0_req = C_KMS * LN4 / (R_WORLD * H0_SH0ES)
print(f"  SH0ES 要求 M(0) = {mp.nstr(M0_req, 8)}")
chk("SH0ES-required M(0)", M0_req, "1.37851", "1e-5")

print("\n--- I: 大 ell 外推 + piR ---")
# ⚠️ 核喺 ell_t 有跳躍 -> mp.quad 跨跳躍會失準, 必須分段精確積分。
#    ∫_0^ell_t arch + √2*(ell_nyq - ell_t)
ELL_NYQ = mp.log(18) / LN4
I_arch = mp.quad(lambda t: M_of(t, nc_arch), [0, ELL_T]) + mp.sqrt(2) * (ELL_NYQ - ELL_T)
I_step = mp.quad(lambda t: M_of(t, nc_step), [0, ELL_T]) + mp.sqrt(2) * (ELL_NYQ - ELL_T)
shallow = mp.quad(lambda t: M_of(t, nc_arch), [0, ELL_T])
deep = mp.sqrt(2) * (ELL_NYQ - ELL_T)
print(f"  ell_nyq = log4(18) = {mp.nstr(ELL_NYQ,10)}   piR = {mp.nstr(mp.pi*R_WORLD,10)} Mpc")
print(f"  integral arch = {mp.nstr(I_arch,10)} R = {mp.nstr(I_arch*R_WORLD,10)} Mpc  vs piR = {mp.nstr(mp.pi,8)} R -> "
      f"{mp.nstr((I_arch/mp.pi-1)*100,5)}%")
print(f"  arch 分段: 淺 {mp.nstr(shallow,8)} + 深 {mp.nstr(deep,8)} = {mp.nstr(shallow+deep,8)}")
chk("integral arch", I_arch, "3.0881516", "1e-6")
chk("integral step", I_step, "3.1196434", "1e-6")
chk("shallow segment", shallow, "1.2603071", "1e-6")
chk("deep segment", deep, "1.8278445", "1e-6")

print("\n--- J: 自由擬合最佳點 (獨立粗網格, 確認結構值落入 Delta_chi2<=4) ---")
def chi2_DH(nc_f):
    return sum(((M_of(ell_of(z), nc_f) - Mobs(dh, z)) / sM_of(sdh, z)) ** 2
               for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6)

def kern(A, W, Lt):
    return lambda t: (sec_of_nc(22 + A * mp.sin(mp.pi * t / W)) if t < Lt else mp.sqrt(2))

def chi2_param(A, W, Lt):
    f = kern(A, W, Lt)
    return sum(((f(ell_of(z)) - Mobs(dh, z)) / sM_of(sdh, z)) ** 2
               for (nm, z, dm, sdm, dh, sdh, rho) in COSMO6)

best = ((None, None, None), mp.inf)
for iA in range(30, 51):
    A = mp.mpf(iA) / 10
    for iW in range(5, 26):
        W = mp.mpf(iW) / 20
        for iL in range(40, 141, 5):
            Lt = mp.mpf(iL) / 100
            c = chi2_param(A, W, Lt)
            if c < best[1]:
                best = ((A, W, Lt), c)
(A, W, Lt), cb = best
struct = chi2_DH(nc_arch)
print(f"  粗網格最佳: A={mp.nstr(A,4)} W={mp.nstr(W,4)} ell_t={mp.nstr(Lt,4)} chi2={mp.nstr(cb,6)}")
print(f"  結構值 (A=4, W=1, ell_t=log4 3) chi2 = {mp.nstr(struct,6)}  (Delta = {mp.nstr(struct-cb,5)})")
# 結構值逐個單獨掃 (其他兩個固定結構值), 確認係尖銳極小
print("  一維掃描 (固定其他兩個 = 結構值):")
for lbl, vals, mk in (
    ("A  (W=1, lt=log4 3)", ["1", "2", "3", "4", "5", "6"], lambda v: chi2_param(mp.mpf(v), 1, ELL_T)),
    ("W  (A=4, lt=log4 3)", ["0.5", "1", "1.3333333", "2", "2.0849625"],
     lambda v: chi2_param(4, mp.mpf(v), ELL_T)),
    ("lt (A=4, W=1)", ["0.5", "0.2075193", "0.7924813", "1"], lambda v: chi2_param(4, 1, mp.mpf(v))),
):
    print(f"    {lbl}: " + "  ".join(f"{v}->{mp.nstr(mk(v),6)}" for v in vals))
chk("best-fit A near 4", A, "4.1", "0.3")
chk("best-fit W near 1", W, "0.9", "0.3")
chk("chi2 structural (A=4,W=1,lt=log4 3)", struct, "3.4712", "0.001")
chk("Delta_chi2 structural", struct - cb, "1.76", "0.6")

print("\n" + "=" * 100)
npass = sum(1 for ok, *_ in LEDGER if ok)
print(f"審計結果: {npass}/{len(LEDGER)} PASS")
for ok, name, got, want, tol in LEDGER:
    if not ok:
        print(f"  [FAIL] {name}: got {got}  want {want}  (tol {tol})")
print("=" * 100)
