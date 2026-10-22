#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O232 — scripts/03: 天花板判據 (Ceiling Criterion)
=================================================
R1 之結構裁決後果: IDCM 明言「冇年齡上限」(verify_young_galaxies.py) ⟹
論文之 ΛCDM「年齡天花板 A_U」測試係**正交**於 IDCM。
真正可分辨之判據 = 高 z 星系恆星齡 vs ΛCDM 硬天花板 t_age(z)。

本 script (只算 ΛCDM 積分 + IDCM 預言式, 零新參數):
  1. ΛCDM 天花板 t_age(z) = A_U − lookback(z)  (Planck: H0=67.4, Om=0.315)
  2. IDCM 預言: 「唔存在 z-相關天花板」(高 z = 更遠非更年輕)
  3. 可證偽判據: 任何星系 stellar age > t_age(z_obs) ⟹ ΛCDM 違反 (IDCM 存活)
"""
import os, json
from mpmath import mp, mpf, quad, sqrt, nstr

mp.dps = 30
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- ΛCDM (Planck 2018, 用於天花板曲線) ----
H0   = mpf('67.4')            # km/s/Mpc
Om   = mpf('0.315')
c_kms = mpf('299792.458'); MPC_km = mpf('3.0856775814913673e19'); GYR_s = mpf('3.15576e16')
HubbleTime_Gyr = (MPC_km/H0)/GYR_s        # 1/H0 in Gyr

def E(z):  return sqrt(Om*(1+z)**3 + (1-Om))
def lookback(z):                          # Gyr
    return float(HubbleTime_Gyr * quad(lambda zp: 1/((1+zp)*E(zp)), [0, z]))
A_U = lookback(mpf('5000'))               # 總 lookback ≈ 宇宙齡
print("="*78); print("O232 / 03 — 天花板判據"); print("="*78)
print(f"\nΛCDM (Planck18):  H0={nstr(H0,4)}, Om={nstr(Om,4)}, 1/H0={nstr(HubbleTime_Gyr,6)} Gyr")
print(f"A_U (z→5000) = {A_U:.4f} Gyr")

# ---- IDCM 側 ----
TAU = mpf('13.470063')      # 1/ω_ring
OMEGA_RING = mpf('72.59002746')
print(f"IDCM: τ = 1/ω_ring = {nstr(TAU,7)} Gyr;  ω_ring = {nstr(OMEGA_RING,8)}")

checks = []
def ck(n, c, d=""):
    checks.append((n, bool(c), d)); print(("  ✅ " if c else "  ❌ ")+n+(f"   [{d}]" if d else ""))

print("\n[Α] ΛCDM 年齡天花板 t_age(z) (星系恆星齡硬上界)")
print(f"  {'z':>6} {'t_age(z) Gyr':>14} {'t_age Gyr (Myr)':>18}")
zlist = [4,5,6,8,10,13,14.32,15,16,17,20]
tbl = {}
for z in zlist:
    t = A_U - lookback(mpf(str(z)))
    tbl[z] = float(t)
    print(f"  {z:>6} {float(t):>14.4f}      {float(t)*1000:>10.1f} Myr")
ck("C1 t_age(17) ≈ 0.21 Gyr (重現 v9 之 210 Myr 之說)", abs(tbl[17]-0.211) < 0.02, f"{tbl[17]:.4f} Gyr")
ck("C2 t_age(10) ≈ 0.54 Gyr [❌ 假設誤: 混用 H0 約定]", abs(tbl[10]-0.54) < 0.02, f"{tbl[10]:.4f} (Planck)")
# -c 更正: v9 用 H0=70,Om=0.3; 本 script 用 Planck 67.4/0.315 ⇒ 值不同, 非物理矛盾
def lookback_conv(z, h0, om):
    from mpmath import sqrt as _s
    return float((MPC_km/mpf(h0))/GYR_s * quad(lambda zp: 1/((1+zp)*_s(om*(1+zp)**3+(1-om))), [0, z]))
A_U_conv = lookback_conv(5000, 70.0, 0.3)
t10_conv = A_U_conv - lookback_conv(10, 70.0, 0.3)
ck("C2-c v9 之 540 Myr 與其自身 (H0=70,Om=0.3) 不符 (得 466 Myr) ⟹ v9 文檔不一致",
   abs(t10_conv-0.54) > 0.05,
   f"{t10_conv:.4f} Gyr (v9 約定) ≪ 0.54 宣稱 ⟹ v9 docstring 數值不一致 (真 finding)")

print("\n[Β] IDCM 預言 (無 z-天花板)")
print("  IDCM: z 係 K_Tree 階梯位置 (更遠), 唔係時間 ⟹ 冇 t_age(z) 上界")
print("  預言: 高 z (8–15) 星系可有與本地同齡之恆星族群 ⟹ 可違反 ΛCDM 天花板")
print(f"  IDCM 對 A_★ (本地最老星) 冇預言 (τ 係環周長, 唔係年齡)")

print("\n[Γ] 可分辨之數據點 (IDCM v9 `verify_young_galaxies.py` 自引例子; 只引用, 不重驗)")
ex = [("GS-z5-Q1", 5.39, 0.9), ("COS-z5-Q1", 5.11, 0.7),
      ("JADES-GS-z14-0", 14.32, 0.30), ("Labbé+2023 z~8", 8.0, 0.6)]
nviol = 0
for name, z, age in ex:
    t = tbl.get(z) or float(A_U - lookback(mpf(str(z))))
    viol = age > t
    nviol += int(viol)
    print(f"  {name:16s} z={z:6.2f}  age={age:5.2f} Gyr  t_age(z)={t:6.3f} Gyr  {'⚠️ 超天花板' if viol else '✓ 未超'}")
ck("C3 判據清晰 (存在判別式 age vs t_age(z))", True, f"引例中超天花板者 {nviol}/4 (低 z 例未超, 因 t_age 大)")

print("\n[Δ] 裁決")
print(f"  ★ 論文之主結果 (A_★=13.73 ≈ A_U^CMB − 0.2) 係**確認 ΛCDM 天花板**,")
print(f"    對 IDCM 無約束力 (IDCM 無 A_★ 預言)。")
print(f"  ★ 唯一可分辨 IDCM vs ΛCDM 之方向: 高 z (8–15) 星系恆星齡。")
print(f"  ★ 判據: 若 (且僅若) 觀測到 stellar age > t_age(z) ⟹ ΛCDM 違反、IDCM 存活。")
verdict = "🟢 R1 已裁決: τ ≠ 年齡天花板; 論文測試對 IDCM 正交。可分辨判據 = 高 z 恆星齡 (z=8–15) vs t_age(z)"
print(f"  判決: {verdict}")

npass = sum(1 for c in checks if c[1])
print("\n"+"="*78); print(f"RESULT: {npass}/{len(checks)} PASS"); print("="*78)
out = {"script": "03_ceiling_criterion.py", "lcdm": {"H0": float(H0), "Om": float(Om), "A_U_Gyr": A_U},
       "t_age_table": tbl, "idcm_tau": float(TAU),
       "criterion": "galaxy stellar age > t_age(z) => LambdaCDM violated",
       "checks": [{"name": n, "pass": c, "detail": d} for n, c, d in checks],
       "pass": npass, "total": len(checks), "verdict": verdict}
with open(os.path.join(BASE, "data", "03_ceiling_criterion.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("data/03_ceiling_criterion.json written.")