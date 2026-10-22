#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/02 — 三圖 88 格節點溫度提取 (SMICA + Commander + SEVEM)
=====================================================================
管道 (完全複製 O175/O174 原設定):
  read_map -> ordering 驗證 (cross-corr vs SMICA RING 參考)
  -> hp.smoothing (4.17° AND 5.0° FWHM) -> remove_dipole
  -> get_interp_val 節點採樣 (60 A5 + 88 格 + 32 阻挫控制組)
  -> ⟨|δT|⟩/A, A = 134.2 μK

關鍵: Commander 係真 NESTED (O2 教訓) — 必須 reorder 先至平滑;
      SEVEM 宣稱 NESTED 但數據係 RING — cross-corr 自動揀啱。
"""
import numpy as np
import healpy as hp
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = ROOT / "o182_88grid_geometry/data"
OUT.mkdir(parents=True, exist_ok=True)

MAPS = {
    "SMICA":     ROOT / "o175_entropy_theorem/data/planck/COM_CMB_IQU-smica_2048_R3.00_full.fits",
    "Commander": ROOT / "data_gated_unlock/COM_CMB_IQU-commander_2048_R3.00_full.fits",
    "SEVEM":     ROOT / "o42_independent_measurement_A/data/bands/sevem_final.fits",
}

# 節點集
a5 = np.loadtxt(ROOT / "cmb_cold_spot/data/a5_nodes.txt")      # 60
g88 = np.loadtxt(OUT / "g88_nodes.txt")                        # 88
g32 = np.loadtxt(OUT / "g32_frustration_midpoints.txt")        # 32 (控制組)
g120 = np.vstack([g88, g32])                                   # 120 全邊中點
sets = {"A5_60": a5, "G88": g88, "G32frust": g32, "G120_all": g120}
for k, v in sets.items():
    print(f"節點集 {k}: {len(v)}")

# 讀 SMICA 作 RING 參考
print("\n=== ordering 驗證 ===")
sm = hp.read_map(str(MAPS["SMICA"]), field=0, verbose=False).astype(np.float64)
print(f"SMICA: nside={hp.get_nside(sm)}, len={len(sm)}, finite={np.isfinite(sm).mean():.4f}")
sel = np.arange(0, len(sm), 3000)

prepared = {}
for name, path in MAPS.items():
    m = hp.read_map(str(path), field=0, verbose=False).astype(np.float64)
    c0 = np.corrcoef(m[sel], sm[sel])[0, 1]
    mr = hp.reorder(m, n2r=True)
    c1 = np.corrcoef(mr[sel], sm[sel])[0, 1]
    choice = "as-is" if c0 >= c1 else "reorder(n2r)"
    m_final = m if c0 >= c1 else mr
    prepared[name] = m_final
    print(f"  {name:10s}: corr as-is={c0:+.4f}, reorder={c1:+.4f} -> {choice}")

# 平滑 + 提取
SMOOTHS = [4.17, 5.0]
results = {}
for fwhm in SMOOTHS:
    print(f"\n=== 平滑 {fwhm}° ===")
    for name, m in prepared.items():
        ms = hp.smoothing(m, fwhm=np.radians(fwhm), verbose=False)
        ms = hp.remove_dipole(ms, verbose=False)
        sigma_map = np.std(ms) * 1e6
        # masked σ (|b|>20, 乾淨 CMB)
        npix = len(ms)
        theta_all, phi_all = hp.pix2ang(hp.get_nside(ms), np.arange(npix))
        b_all = 90.0 - np.degrees(theta_all)
        gmask = np.abs(b_all) > 20.0
        sigma_masked = np.std(ms[gmask]) * 1e6
        for sname, pts in sets.items():
            theta = np.radians(90.0 - pts[:, 1])
            phi = np.radians(pts[:, 0])
            T = hp.get_interp_val(ms, theta, phi) * 1e6
            key = (fwhm, name, sname)
            results[key] = {"T": T, "sigma_map": sigma_map, "sigma_masked": sigma_masked}
            dT = T - T.mean()
            m1 = np.mean(np.abs(dT)) / 134.2
            print(f"  {fwhm:>4.2f}° {name:10s} {sname:8s}: ⟨|δT|⟩/A = {m1:.5f}  "
                  f"(σ_map={sigma_map:.1f}, σ_masked={sigma_masked:.1f} μK)")

# 儲存節點溫度
import json
for fwhm in SMOOTHS:
    for name in MAPS:
        arr = {sname: results[(fwhm, name, sname)]["T"].tolist() for sname in sets}
        (OUT / f"temps_{name}_{fwhm}deg.json").write_text(json.dumps(arr))
print("\n溫度已存: data/temps_{map}_{fwhm}deg.json")
print("\nRESULT: 提取完成 (ordering 已驗證)")
