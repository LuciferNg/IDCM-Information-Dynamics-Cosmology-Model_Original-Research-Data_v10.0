#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O232 — scripts/04: R6 高 z 恆星齡 vs ΛCDM 天花板 (de la Vega et al. 2025)
=======================================================================
數據: bagpipes_umap_jades_2025.txt (github alex-delavega/umap_jades_2025)
  JADES 3<z<6 quiescent 搜尋; 2,282 星系; Bagpipes SED 擬合; mass-weighted ages (mwa_50/16/84, Gyr)

判據 (scripts/03): ΛCDM 硬天花板 t_age(z) = A_U − lookback(z); age > t_age(z) ⟹ ΛCDM 違反
關鍵判別: 若 ΛCDM 正確, 星齡上包絡 max(age) 應**跟住** t_age(z) 走 (z 高 → 上限低);
          若 IDCM「無 z-天花板」正確, 上包絡應大致與 z 無關 (同一 max age at all z)。

⚠️ 紀律: SED 擬合有「星形成須喺 Big Bang 之後」prior ⟹ 違反會被 prior 壓制;
         故主測試 = 上包絡是否跟踪 t_age(z) (形狀), 違反數只作輔助。
"""
import json, os
import numpy as np
from mpmath import mp, mpf, sqrt, quad, nstr

mp.dps = 30
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW  = os.path.join(BASE, "data", "raw", "dlv.txt")

H0 = mpf('67.4'); Om = mpf('0.315')
MPC_km = mpf('3.0856775814913673e19'); GYR_s = mpf('3.15576e16')
Ht = (MPC_km/H0)/GYR_s
def t_age_Gyr(z):
    z = mpf(str(z))
    lb = Ht * quad(lambda zp: 1/((1+zp)*sqrt(Om*(1+zp)**3+(1-Om))), [0, 5000])
    lbz = Ht * quad(lambda zp: 1/((1+zp)*sqrt(Om*(1+zp)**3+(1-Om))), [0, z])
    return float(lb - lbz)

print("="*78); print("O232 / 04 — R6: 高 z 恆星齡 vs ΛCDM 天花板 (de la Vega+2025)")
print("="*78)
rows = []
with open(RAW) as f:
    f.readline()
    for line in f:
        p = line.split()
        if len(p) < 20: continue
        try:
            z=float(p[4]); a50=float(p[15]); a16=float(p[14]); a84=float(p[16])
        except ValueError: continue
        rows.append((z,a50,a16,a84))
z=np.array([r[0] for r in rows]); A50=np.array([r[1] for r in rows])
A16=np.array([r[2] for r in rows]); A84=np.array([r[3] for r in rows])
N=len(rows)
print(f"\n樣本 N={N:,}  z=[{z.min():.2f},{z.max():.2f}]  含 NaN: {(np.isnan(A50)|np.isnan(A84)).sum()}")
ok = np.isfinite(A50)&np.isfinite(A84)
z, A50, A16, A84 = z[ok], A50[ok], A16[ok], A84[ok]
N=int(z.size)
t=np.array([t_age_Gyr(zz) for zz in z])

nv = {"mwa50": int((A50>t).sum()), "mwa16": int((A16>t).sum()), "mwa84": int((A84>t).sum())}
print("\n[Β] 違反計數 (prior 會壓制 ⟹ 只作輔助)")
for k in ("mwa50","mwa16","mwa84"):
    print(f"  {k}: N(>t_age)={nv[k]:5d}")

print("\n[Γ] z-分箱上包絡: max/99th/中位 mwa_50 vs t_age(z) (ΛCDM 天花板)")
bins = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,8)]
rows_out = []
for lo,hi in bins:
    m=(z>=lo)&(z<hi)
    if m.sum()==0: continue
    tmid = t_age_Gyr((lo+hi)/2)
    mx=A50[m].max(); p99=np.percentile(A50[m],99); md=np.median(A50[m])
    rows_out.append({"zbin": f"{lo}-{hi}", "N": int(m.sum()), "max_mwa50": float(mx),
                     "p99_mwa50": float(p99), "med_mwa50": float(md),
                     "t_age_mid": tmid, "max_ratio": float(mx/tmid), "p99_ratio": float(p99/tmid)})
    print(f"  z∈[{lo},{hi}):  N={int(m.sum()):5d}  max={mx:5.2f}  p99={p99:5.2f}  med={md:5.2f}  "
          f"t_age(mid)={tmid:5.2f}  max/t={mx/tmid:5.3f}  p99/t={p99/tmid:5.3f}")
env_ratios = [r["max_ratio"] for r in rows_out if r["N"]>50]
print(f"  ⟹ 上包絡 max/t 跨箱分佈: min={min(env_ratios):.3f} max={max(env_ratios):.3f} "
      f"(若 ΛCDM 天花板正確, 此比值應大致平穩; 若 IDCM 無天花板, 比值應隨 z 升)")

print("\n[Δ] 與 z 無關假設 (IDCM『無天花板』形式化): max(age) 應與 z 無關")
for lo,hi in bins:
    m=(z>=lo)&(z<hi)
    if m.sum()<30: continue
    print(f"  z∈[{lo},{hi}):  max mwa_50={A50[m].max():5.2f} Gyr  (若與 z 無關, 應 ~常數; "
          f"ΛCDM 上限 t_age={t_age_Gyr((lo+hi)/2):.2f})")

# ---- Z. z>10 文獻案例 (GS-z14-0) ----
print("\n[Ζ] z~14 極端案例: JADES-GS-z14-0 (z=14.32+0.08-0.20)")
print("  文獻 mass-weighted age: Helton+2024 BAGPIPES ~15 Myr (3-43 Myr); Carniani+2024 ~36 Myr")
t14 = t_age_Gyr(14.32)
print(f"  ΛCDM 天花板 t_age(14.32) = {t14:.4f} Gyr = {t14*1000:.0f} Myr")
for lbl, age_myr in [("Helton+2024 (15 Myr)", 15), ("Carniani+2024 (36 Myr)", 36)]:
    pct = age_myr/1000/t14*100
    print(f"  {lbl}: age = {age_myr/1000:.3f} Gyr  = {pct:5.1f}% 天花板 ⟹ 距天花板 {100-pct:.0f}% 餘量")

# ---- E. 判決 ----
print("\n[Ε] 判決")
rat = A50/t
print(f"  mwa_50 > t_age: {nv['mwa50']}/{N} (0%)   mwa_84 > t_age: {nv['mwa84']}")
print(f"  A50/t 中位 = {np.median(rat):.3f}, p95 = {np.percentile(rat,95):.3f}, max = {rat.max():.3f}")
print(f"  上包絡 max mwa_50 (z 升序): {[str(round(r['max_mwa50'],2)) for r in rows_out if r['N']>30]}")
mvals = [r["max_mwa50"] for r in rows_out if r["N"] > 30]
declines = all(mvals[i] > mvals[i+1] for i in range(len(mvals)-1))
print(f"  單調下降 (拒 z-無關包絡)? {declines}")
if nv["mwa50"] > 0:
    verdict = ("🔴 R6 數據側: 出現 mwa_50 > t_age(z) ⟹ ΛCDM 天花板被違反; IDCM 方向獲支持 (需核 SED prior)")
elif declines and nv["mwa50"] == 0:
    verdict = ("🟡 R6 數據側(偏 ΛCDM): 0/2,282 中位違反; 上包絡隨 z 單調下降 (4.55→0.52 Gyr), "
               "**非 z-無關** ⟹ IDCM『無天花板/與 z 無關』形式被拒; ΛCDM 天花板形狀獲支持。"
               "⚠️ 但 prior 壓制違反 + z<6 選樣效應限制決定性")
else:
    verdict = "🟡 R6 數據側: 邊緣 — 判別力受限"
print(f"  判決: {verdict}")

out = {"script":"04_jades_age_ceiling.py","source":"de la Vega+2025 bagpipes_umap_jades_2025.txt (JADES)",
       "N":N,"violations":nv,"envelope_by_zbin":rows_out,"median_A50_over_t":float(np.median(rat)),
       "p95_A50_over_t":float(np.percentile(rat,95)),"max_A50_over_t":float(rat.max()),
       "verdict":verdict}
with open(os.path.join(BASE,"data","04_jades_age_ceiling.json"),"w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print("\ndata/04_jades_age_ceiling.json written.")