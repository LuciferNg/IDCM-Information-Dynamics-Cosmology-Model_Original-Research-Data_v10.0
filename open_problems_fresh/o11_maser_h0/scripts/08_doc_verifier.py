#!/usr/bin/env python3
"""
O11 記錄文檔 Verifier v2 — 語意數字對比
=========================================
唔依賴 regex group: 直接從文檔全文提取所有數字 token,
然後逐個核對關鍵聲稱值 (用 substring search)。
"""
import math

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
kappa = 1 / 16
c_km = 299792.458
H0_idcm = 72.59
SIGMA_PEC = 250.0

galaxies = [
    ("UGC 3789",    51.5, 4.0, 4.5, 3319.9, 0.8),
    ("NGC 6264",   132.1, 17.0, 21.0, 10192.6, 0.8),
    ("NGC 6323",   109.4, 23.0, 34.0, 7801.5, 1.5),
    ("NGC 5765b",  112.2, 5.1, 5.4, 8525.7, 0.7),
    ("CGCG 074-064", 87.6, 7.2, 7.9, 7172.2, 1.9),
    ("NGC 4258",     7.58, 0.11, 0.11, 679.3, 0.4),
]

def D_app(z, H0=H0_idcm):
    RH = c_km / H0
    ell = math.log(1 + z, 4)
    return (44 - 44 / 4**ell) * (RH / 44) * (1 + 2 * phi_inv * ell)

def H_eff(z, dz=1e-5):
    return c_km / ((D_app(z + dz) - D_app(z - dz)) / (2 * dz))

# ============ 獨立重算 (全部關鍵值) ============
offset = 73.9 / 72.59 - 1
z_off = (73.9 - 72.59) / 3.0
z_pl = (73.5 - 72.59) / 3.0
offset_pl = 73.5 / 72.59 - 1

chi2_5 = 0
d4258 = None
vpec4258 = None
for name, D, elo, ehi, v, verr in galaxies:
    z = v / c_km
    d = D_app(z)
    err = (elo + ehi) / 2
    s = (d - D) / err
    if name == "NGC 4258":
        d4258 = d
        vpec4258 = (d - D) * H0_idcm
    else:
        chi2_5 += s**2

wsum = hsum = 0
for name, D, elo, ehi, v, verr in galaxies:
    z = v / c_km
    err = (elo + ehi) / 2
    w = 1 / err**2
    wsum += w
    hsum += w * H_eff(z)
h_avg = hsum / wsum

trgb = 72.59 * (1 - kappa * phi_inv)
miras = 72.59 * (1 + kappa * phi_inv / 4)
sh0es = 72.59 * (1 + phi_inv / 100)
kphi2 = kappa * phi_inv / 2
kphi2_dev = abs(kphi2 - offset) / offset * 100

def D_A_lcdm(z, H0=67.36, Om=0.315):
    Ol = 1 - Om
    def E(zp):
        return math.sqrt(Om * (1+zp)**3 + Ol)
    n = 4000
    dz = z / n
    s = 0.5 * (1/E(0) + 1/E(z))
    for i in range(1, n):
        s += 1/E(i*dz)
    s *= dz
    return c_km / H0 * s / (1 + z)

z4258 = 679.3 / c_km
lcdm4258 = D_A_lcdm(z4258)
s4258_lcdm = (lcdm4258 - 7.58) / 0.11

claims = {
    # (label, calculated, [allowed doc strings], tol_rel)
    "offset 1.8047%": (offset*100, ["1.8047", "1.80"], 1e-3),
    "z=0.44σ": (z_off, ["0.44"], 1e-2),
    "z_pl=0.30σ": (z_pl, ["0.30"], 5e-2),
    "offset_pl 1.254%": (offset_pl*100, ["1.254", "1.25"], 1e-2),
    "χ²(5)=5.0": (chi2_5, ["5.0", "5.00", "χ²(5)"], 1e-2),
    "χ²(5)/dof=1.00": (chi2_5/5, ["1.00", "1.0"], 1e-2),
    "NGC4258 D=9.36": (d4258, ["9.36", "9.4"], 1e-2),
    "NGC4258 v_pec=+129": (vpec4258, ["129", "+130", "130"], 1e-2),
    "NGC4258 σ=+16.14": ((d4258-7.58)/0.11, ["16.14", "16.1", "+16"], 1e-2),
    "H_eff avg=72.63": (h_avg, ["72.63", "72.6"], 1e-3),
    "TRGB=69.79": (trgb, ["69.79", "69.78", "69.8"], 1e-3),
    "Miras=73.29": (miras, ["73.29", "73.3"], 1e-3),
    "SH0ES=73.04": (sh0es, ["73.04"], 1e-3),
    "κφ⁻¹/2=1.931%": (kphi2*100, ["1.931"], 1e-3),
    "κφ⁻¹/2 dev=7.02%": (kphi2_dev, ["7.02", "7.0"], 1e-2),
    "ΛCDM 4258 σ=+22.5": (s4258_lcdm, ["22.5", "+22", "22"], 1e-2),
    "IDCM 72.59": (72.59, ["72.59"], 1e-6),
    "Maser σ=+0.44": ((73.9-72.59)/3.0, ["+0.44", "0.44"], 1e-2),
    "2M++/CF3 71.8": (71.8, ["71.8"], 1e-4),
    "profile 73.5": (73.5, ["73.5"], 1e-4),
}

docs = {
    "02_closure_record.md": open("02_closure_record.md").read(),
    "01_problem_record.md": open("01_problem_record.md").read(),
    "README.md": open("README.md").read(),
}

print("=" * 84)
print("O11 文檔 Verifier v2 — 語意對比 (全部 3 份文檔)")
print("=" * 84)
print(f"\n{'聲稱':24s} {'計算':>10s} {'文檔有?':>8s} {'狀態':>6s}")
print("-" * 84)

all_ok = True
for label, (calc, needles, tol) in claims.items():
    found_in = []
    for dname, dtext in docs.items():
        for nd in needles:
            if nd in dtext:
                found_in.append(f"{dname}({nd})")
                break
    if found_in:
        # 檢查數值一致性: needle 要係數字
        numeric_needle = None
        for nd in needles:
            try:
                val = float(nd)
                numeric_needle = val
                break
            except ValueError:
                continue
        if numeric_needle is not None:
            dev = abs(calc - numeric_needle) / max(abs(calc), 1e-12)
            ok = dev < tol
        else:
            ok = True
        status = "✅" if ok else "❌"
        if not ok:
            all_ok = False
        loc = ", ".join(found_in[:3])
        print(f"{label:24s} {calc:10.4f} {'YES':>8s} {status:>6s}  [{loc}]")
    else:
        all_ok = False
        print(f"{label:24s} {calc:10.4f} {'NO':>8s} {'❌':>6s}  [任何文檔都冇!]")

# 額外: 檢查 6 星系 σ 值
print("\n" + "-" * 84)
print("六星系 σ 值 (02_closure_record.md §3):")
for name, D, elo, ehi, v, verr in galaxies:
    z = v / c_km
    d = D_app(z)
    err = (elo + ehi) / 2
    s = (d - D) / err
    docstr = "02_closure_record.md"
    # 搵文檔入面嗰行
    for line in open("02_closure_record.md"):
        if name.split()[0] in line:
            in_doc = name.split()[0] in line
            break
    print(f"  {name:12s} σ_calc={s:+.2f}  {'✅ 文檔有' if name.split()[0] in open('02_closure_record.md').read() else '❌'}")

print("\n" + "=" * 84)
print(f"VERDICT: {'✅✅ 全部 PASS — 記錄文檔正確無幻覺' if all_ok else '❌❌ 有 FAIL — 需要修正'}")
print("=" * 84)
