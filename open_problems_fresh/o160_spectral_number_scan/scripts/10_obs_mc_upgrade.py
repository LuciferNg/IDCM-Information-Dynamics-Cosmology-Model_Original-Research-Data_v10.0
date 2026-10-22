#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/10 — obs MC 密度升級 (docs/05 開放項 5)

scripts/05 用 uniform 密度解析估計 (低估 γ-比密集區背景)。升級 = per-target MC:
  對每個 (obs target, family): 喺 family 值域抽 N_TRIAL 個隨機 target,
  每個計 3σ 窗內命中數 → 經驗分佈 → p = P(MC ≥ 實際 count)。
  FULL family 用 stride-2 採樣 (44×44×17 ≈ 33K cells), 乘返 scale。

重點驗證: m_W/m_Z O88 count=1 嘅 p 值 (05 用 Poisson 近似 p≈2e-4, 呢度 MC 精確化)。
"""
import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np

O160 = Path(__file__).resolve().parent.parent
DATA = O160 / "data"
sys.path.insert(0, str(O160))
from tools.registry import get_spectra  # noqa: E402

N_TRIAL = 500
STRIDE = 2  # FULL family 採樣


def build(S, stride=1):
    g, o, l = S["gamma"][::stride], S["omega"][::stride], S["lam"][::stride]
    return {
        "R88": g[None, :] / g[:, None], "O88": o[None, :] / o[:, None],
        "BEAT": np.abs(o[None, :] - o[:, None]),
        "GT_prod": g[:, None] * l[None, :], "GT_div": g[:, None] / l[None, :],
        "OT_prod": o[:, None] * l[None, :], "OT_div": o[:, None] / l[None, :],
        "FULL_wr": (o[None, :, None] / o[:, None, None]) * l[None, None, :],
        "FULL_gr": (g[None, :, None] / g[:, None, None]) * l[None, None, :],
        "FULL_gd": (g[None, :, None] / g[:, None, None]) / l[None, None, :],
        "FULL_bt": np.abs(o[None, :, None] - o[:, None, None]) * l[None, None, :],
        "SUM_plus": g[None, :, None] + g[:, None, None] + l[None, None, :],
        "SUM_minus": g[None, :, None] + g[:, None, None] - l[None, None, :],
    }


def main():
    S = get_spectra()
    web = json.loads((DATA / "constant_web.json").read_text())
    obs_web = {e["name"]: (e["value"], e["err"]) for e in web["obs"]}

    fams_small = build(S, stride=1)
    fams_full = build(S, stride=STRIDE)
    # 3D family 全空間 cell 數 (用於 scale)
    N3D = 88 * 88 * 33
    N2D = {"R88": 88 * 88, "O88": 88 * 88, "BEAT": 88 * 88,
           "GT_prod": 88 * 33, "GT_div": 88 * 33, "OT_prod": 88 * 33, "OT_div": 88 * 33}
    scale3d = 4  # stride-2 3D: (44×44×17) → 全空間 4× (88×88×33)/(44×44×17) = 8? 計準:

    obs_rows = list(csv.DictReader(open(DATA / "obs_hits.csv")))
    actual_map = defaultdict(int)
    for r in obs_rows:
        actual_map[(r["target"], r["family"])] += int(r["count"])

    print(f"=== obs MC null (N_TRIAL={N_TRIAL}, FULL stride={STRIDE}) ===")
    rng = np.random.default_rng(20260908)
    results = {}
    for tname, (tval, err) in obs_web.items():
        if err <= 0:
            continue
        tol_eff = 3.0 * err * abs(tval)
        row_out = []
        for fam in fams_small:
            X = fams_small[fam]
            scale = 1.0
            if X.ndim == 3:
                X = fams_full[fam]
                # 採樣 cell 數 = 44×44×17 = 32912; 全空間 = 255552
                scale = 255552 / 32912
            N = X.size
            Xr = X.ravel()
            rngX = float(X.max() - X.min())
            if rngX <= 0:
                continue
            # 實際 count
            a = actual_map.get((tname, fam), 0)
            # MC: 抽 N_TRIAL 個隨機 target, 每 trial 一個 target 計命中
            rts = rng.uniform(X.min(), X.max(), N_TRIAL)
            mc = np.zeros(N_TRIAL)
            # 向量化: 對每個 trial target 用廣播 (N_TRIAL × N cells 太大)
            # → 分批: 每 batch 256 targets × N cells
            B = 256
            for b0 in range(0, N_TRIAL, B):
                tb = rts[b0:b0 + B]
                # |X − t| ≤ tol_eff 對每個 t
                hits = (np.abs(Xr[None, :] - tb[:, None]) <= tol_eff).sum(axis=1)
                mc[b0:b0 + B] = hits * scale
            p = float(np.mean(mc >= a))
            sig = a / max(float(np.mean(mc)), 1e-12)
            # ★ 位置條件化 null (簇集區域修正): 喺 target 附近 ±10×3σ 抽樣,
            #   問「若家族喺 target 附近有密度, 隨機鄰近 target 會唔會都中?」
            w = 10.0 * tol_eff
            lo, hi = max(tval - w, X.min()), min(tval + w, X.max())
            p_local = 1.0
            if hi > lo:
                rts2 = rng.uniform(lo, hi, N_TRIAL)
                mc2 = np.zeros(N_TRIAL)
                for b0 in range(0, N_TRIAL, B):
                    tb = rts2[b0:b0 + B]
                    hits = (np.abs(Xr[None, :] - tb[:, None]) <= tol_eff).sum(axis=1)
                    mc2[b0:b0 + B] = hits * scale
                p_local = float(np.mean(mc2 >= a))
            if a > 0 or sig > 3:
                row_out.append(f"{fam}:{a}vs{np.mean(mc):.2f}(p={p:.3f},p_loc={p_local:.3f})")
                results[f"{tname}|{fam}"] = {"actual": a, "mc_mean": float(np.mean(mc)),
                                             "p": p, "p_local": p_local, "sig_ratio": sig}
        if row_out:
            print(f"  {tname:10s}  " + "  ".join(row_out))

    # 關鍵總結 — 判決 = 位置條件化 p_loc + 結構身份 (O158 先驗) 合併
    print("\n=== 關鍵 verdict (p_loc = 位置條件化 null) ===")
    for key in ["m_W/m_Z|O88", "m_W/m_Z|R88", "m_τ/m_b|O88", "sin²θ₂₃|R88", "sin²θ₂₃|O88",
                "α⁻¹(0)|GT_div"]:
        if key in results:
            r = results[key]
            known = key in {"m_W/m_Z|O88"}  # O158 已知 (21,24) 結構解
            # p_loc 細 + count 細 + 已知身份 → 結構; 否則背景
            verdict = "🟢 唯一結構 (O158 已知解)" if (known and r["actual"] <= 1) else \
                      ("🟡 邊緣 (p_loc 細但冇身份)" if r["p_local"] < 0.05 and r["actual"] <= 3 else "⚠️ 密度背景")
            print(f"  {key}: actual={r['actual']} MC_mean={r['mc_mean']:.2f} "
                  f"p={r['p']:.4f} p_loc={r['p_local']:.4f} → {verdict}")

    (DATA / "obs_mc_null.json").write_text(json.dumps(results, indent=2))
    print("\nRESULT: obs MC null -> data/obs_mc_null.json")


if __name__ == "__main__":
    main()
