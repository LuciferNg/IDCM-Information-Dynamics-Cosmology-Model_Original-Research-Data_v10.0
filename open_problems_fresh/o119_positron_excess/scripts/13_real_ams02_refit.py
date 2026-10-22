#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O119 - Script 13: 真實 AMS-02 正電子分數重擬合 (74 點)
====================================================
docs/01 §4 嘅「0 參數閉合 chi2/dof = 1.094」係對 **10 個手打點 + 固定
sigma = 0.005** 算出。本 script 用 CRDB 下載嘅真實 AMS-02 (2011/05-2018/05)
正電子分數 (74 點, 0.57-832 GeV), 誤差 = stat ⊕ syst, 重做擬合。

真實形狀 (Aguilar+2019 PRL 122,041102; arXiv:1511.00052):
  0.5-9 GeV: 隨能量下降 (電荷相關太陽調制)
  9-300 GeV: 上升 (正電子超出, 起點 25.2±1.8 GeV)
  >284 GeV : 急降 (源項指數截斷, E_s = 810+310/-180 GeV)

數據源: data/obs/ams02_positron_fraction.csv (CRDB; Aguilar+ 2021 Phys.Rept.894)
"""
import csv, io, math, os
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS = os.path.join(BASE, "data", "obs")

print("=" * 74)
print("O119 Script 13: 真實 AMS-02 正電子分數重擬合")
print("=" * 74)

E, f, sig = [], [], []
with io.open(os.path.join(OBS, "ams02_positron_fraction.csv"), encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("#") or not line.strip():
            continue
        p = next(csv.reader([line]))
        st = max(float(p[5]), float(p[6])); sy = max(float(p[7]), float(p[8]))
        E.append(float(p[1])); f.append(float(p[4])); sig.append(math.sqrt(st**2 + sy**2))
E = np.array(E); f = np.array(f); sig = np.array(sig)
print(f"  載入 {len(E)} 點, E ∈ [{E.min():.2f}, {E.max():.1f}] GeV")

passed = 0; total = 0
def check(name, cond, detail=""):
    global passed, total
    total += 1
    if cond: passed += 1; print(f"  ✅ {name} {detail}")
    else: print(f"  ❌ {name} {detail}")

# ---------- 1. 真實形狀 ----------
print("\n[1] 真實數據形狀 (三段行為)")
i_lo = int(np.argmin(E)); i_min = int(np.argmin(f)); i_hi = int(np.argmax(E))
i_pk = i_min + int(np.argmax(f[i_min:]))
print(f"  最低能 {E[i_lo]:.2f} GeV: f = {f[i_lo]:.4f}")
print(f"  局部最低 {E[i_min]:.2f} GeV: f = {f[i_min]:.4f}  (太陽調制區谷底)")
print(f"  峰值 {E[i_pk]:.1f} GeV: f = {f[i_pk]:.4f}  (正電子超出)")
print(f"  最高能 {E[i_hi]:.0f} GeV: f = {f[i_hi]:.4f}  (源項截斷後)")
check("谷底喺 < 15 GeV (太陽調制)", E[i_min] < 15, f"({E[i_min]:.1f} GeV)")
check("峰值喺 > 100 GeV (正電子超出)", E[i_pk] > 100, f"({E[i_pk]:.0f} GeV)")
check("峰值後下降 (源項截斷)", f[i_hi] < f[i_pk], f"({f[i_hi]:.3f} < {f[i_pk]:.3f})")

# ---------- 2. O54/O119 模型 vs 真實數據 ----------
f_sec = lambda x: 0.055 * x ** (-0.33) + 0.005
def chi2(model, E, f, sig):
    return float(np.sum(((f - model) / sig) ** 2))

n = len(E)
m_A = f_sec(E) + 0.0400 * E ** 0.2581        # O54 2-param
m_Ap = f_sec(E) + (1/25) * E ** (8/31)       # O119 結構 0-param
m_S = f_sec(E)                               # 純次級

print("\n[2] 對真實 74 點 chi2 (誤差 = stat ⊕ syst)")
print(f"  {'模型':<34}{'chi2':>10}{'dof':>5}{'chi2/dof':>10}")
for nm, m, k in (("O54 2-par fit + f_W", m_A, 2),
                 ("O119 結構 0-par (1/25, 8/31)", m_Ap, 0),
                 ("純次級 (無 W-field)", m_S, 0)):
    c = chi2(m, E, f, sig); print(f"  {nm:<34}{c:>10.1f}{n-k:>5}{c/(n-k):>10.1f}")
check("O119 結構模型 chi2/dof > 100 (完全描述唔到真實數據)",
      chi2(m_Ap, E, f, sig)/n > 100, f"({chi2(m_Ap,E,f,sig)/n:.0f})")

# ---------- 3. 只喺上升區 (10-300 GeV) ----------
print("\n[3] 局限喺上升區 10-300 GeV")
sel = (E >= 10) & (E <= 300)
Es, fs, ss = E[sel], f[sel], sig[sel]
print(f"  選中 {sel.sum()} 點")
for nm, m in (("O54 2-par", f_sec(Es) + 0.0400*Es**0.2581),
              ("O119 結構", f_sec(Es) + (1/25)*Es**(8/31))):
    c = chi2(m, Es, fs, ss); print(f"  {nm:<14} chi2/dof = {c/len(Es):.1f}")

# 自由擬合上升區
x = np.log(Es); y = np.log(fs - f_sec(Es)); w = ((fs - f_sec(Es)) / ss) ** 2
W = w.sum(); swx=(w*x).sum(); swy=(w*y).sum(); swxx=(w*x*x).sum(); swxy=(w*x*y).sum()
det = W*swxx - swx**2
g_hat = (W*swxy - swx*swy)/det; C_hat = math.exp((swxx*swy - swx*swxy)/det)
sig_g = math.sqrt(W/det)
m_B = f_sec(Es) + C_hat * Es ** g_hat
cB = chi2(m_B, Es, fs, ss)
print(f"\n  自由 2-參數 fit (上升區): C = {C_hat:.4f}, gamma = {g_hat:.4f} ± {sig_g:.4f}")
print(f"  chi2/dof = {cB/(len(Es)-2):.2f}")
print(f"  O54 值 gamma = 0.2581 -> 差 {abs(0.2581-g_hat)/sig_g:.1f} sigma")
check("上升區自由 fit 收斂 (chi2/dof < 3)", cB/(len(Es)-2) < 3.0, f"({cB/(len(Es)-2):.2f})")

# ---------- 4. 源項截斷 ----------
print("\n[4] AMS-02 源項截斷 (Aguilar+2019: E_s = 810 GeV, 超出起點 25.2 GeV)")
print("  IDCM W-field 標度: m_deltaW = 13.95 MeV = 1.4e-2 GeV")
print("  源項截斷需要 E_s ~ 810 GeV = 5.8e4 × m_deltaW")
check("IDCM W-field 標度 (MeV) 同源項截斷 (GeV) 差 > 10^4",
      810 / (13.9505e-3) > 1e4, f"(ratio {810/13.9505e-3:.0f})")

print("\n" + "=" * 74)
print("[5] 結論")
print("=" * 74)
print(f"""
  ★ docs/01 §4 嘅 chi2/dof = 1.094 係對 10 個手打點 + 固定 sigma = 0.005 得出。
    用真實 74 點 AMS-02 (真實 stat⊕syst 誤差) 重算:
      O54 2-param : chi2/dof = {chi2(m_A,E,f,sig)/n:.0f}
      O119 結構    : chi2/dof = {chi2(m_Ap,E,f,sig)/n:.0f}
      純次級       : chi2/dof = {chi2(m_S,E,f,sig)/n:.0f}
      自由 2-param (上升區) : chi2/dof = {cB/(len(Es)-2):.2f}
  ★ 真實數據形狀 = 谷底(~9 GeV, 太陽調制) → 峰(~{E[i_pk]:.0f} GeV, 正電子超出)
    → 截斷(>284 GeV, 源項 E_s = 810 GeV)。
  ★ O54/O119 模型 (單調冪律) 冇峰冇截斷 -> 對全譜 chi2/dof ~ 10^3-10^4。
  ★ 更根本: AMS-02 超出需要源項標度 ~810 GeV; IDCM W-field = 13.95 MeV,
    差 ~6e4 倍 -> IDCM W-field 唔可能係 AMS-02 超出嘅源。
""")
print(f"RESULT: {passed}/{total} PASS")

import json
with open(os.path.join(BASE, "data", "13_real_ams02_refit.json"), "w") as fh:
    json.dump({
        "n_points": int(n), "E_range_GeV": [float(E.min()), float(E.max())],
        "min_GeV": float(E[i_min]), "peak_GeV": float(E[i_pk]), "peak_f": float(f[i_pk]),
        "chi2_dof": {"O54_2par": chi2(m_A,E,f,sig)/n, "O119_struct": chi2(m_Ap,E,f,sig)/n,
                     "secondary_only": chi2(m_S,E,f,sig)/n, "free_2par_rise": cB/(len(Es)-2)},
        "free_fit_rise": {"C": C_hat, "gamma": g_hat, "sigma_gamma": sig_g},
        "verdict": "docs/01 chi2=1.09 用 10 假點+固定誤差; 真實 74 點 chi2/dof~10^3-10^4; AMS-02 源標度 810 GeV vs IDCM 13.95 MeV",
    }, fh, indent=1, ensure_ascii=False)
print("✅ data/13_real_ams02_refit.json")
if passed < total: exit(1)
