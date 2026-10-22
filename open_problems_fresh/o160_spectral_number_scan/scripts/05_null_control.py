#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/05 — null-control: 背景命中率 (R5)

對每個 family:
  - 解析期望: E = Σ_targets N_cells × 2·tol_eff / range (tol 1e-9 相對)
  - Monte Carlo: 隨機 target 均勻分布喺 family 值域, 重複 200 次,
    計平均背景命中 → 與實際命中比較 (p = P(背景 ≥ 實際))
  - obs 目標: 對每個 obs target 計 3σ 窗內期望密度 vs 實際 count
    (重點: m_W/m_Z O88 count=1 vs E≈0.01 → p≈0.01 唯一結構命中;
     m_τ/m_b O88 count=47 vs E≈60 → 密度背景)

輸出: data/null_control.json
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

O160 = Path(__file__).resolve().parent.parent
DATA = O160 / "data"
sys.path.insert(0, str(O160))
from tools.registry import get_spectra  # noqa: E402


def build_families(S, stride=2):
    gamma, omega, lam = S["gamma"], S["omega"], S["lam"]
    g, o = gamma[::stride], omega[::stride]  # 降採樣 (background 密度估計用)
    l = lam[::stride]
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
    targets = [e["value"] for e in web["integers"] + web["halfints"] + web["rationals"]]
    N_TGT = len(targets)
    # 實際 exact hits per family (raw counts, from scan_results.json)
    scan = json.loads((DATA / "scan_results.json").read_text())

    print("=== 解析期望 vs 實際 (web 精確命中, tol=1e-9) ===")
    fams = build_families(S, stride=2)  # 44×44×17 ≈ 33K cells — MC 可行
    scale = {  # 由 stride 採樣還原到全空間 cell 數
        "R88": 4, "O88": 4, "BEAT": 4,
        "GT_prod": 6, "GT_div": 6, "OT_prod": 6, "OT_div": 6,
        "FULL_wr": 24, "FULL_gr": 24, "FULL_gd": 24, "FULL_bt": 24,
        "SUM_plus": 24, "SUM_minus": 24,
    }
    out = {}
    for fam, X in fams.items():
        N = X.size
        rng = float(X.max() - X.min())
        if rng <= 0:
            continue
        # 解析期望 (全空間)
        E_analytic = sum(N * scale[fam] * 2e-9 * max(1.0, t) / rng for t in targets)
        # MC: 200 trials, 每個 trial 抽 N_TGT 個隨機 target
        rngobj = np.random.default_rng(42)
        mc_hits = []
        for _ in range(200):
            rt = rngobj.uniform(X.min(), X.max(), N_TGT)
            h = 0
            for t in rt:
                tol = 1e-9 * max(1.0, abs(t))
                h += int((np.abs(X - t) <= tol).sum())
            mc_hits.append(h * scale[fam])
        mc_mean = float(np.mean(mc_hits))
        actual = scan["families"][fam]["exact_raw"]
        # p = P(MC ≥ actual) (Poisson 近似 / 經驗)
        p_val = float(np.mean([h >= actual for h in mc_hits]))
        out[fam] = {"E_analytic": E_analytic, "MC_mean": mc_mean,
                    "MC_std": float(np.std(mc_hits)), "actual_raw": actual,
                    "p_geq_actual": p_val}
        print(f"  {fam:10s} E_analytic={E_analytic:8.4f} MC_mean={mc_mean:8.4f} "
              f"actual={actual:6d} p(≥actual)={p_val:.4f}")

    print("\n=== OBS 目標密度 vs 實際 (3σ 窗) ===")
    obs_out = {}
    obs_rows = list(csv.DictReader(open(DATA / "obs_hits.csv")))
    # 重建全空間 families (stride=1, 只需 88 鏈 × 33)
    Sf = get_spectra()
    gamma, omega, lam = Sf["gamma"], Sf["omega"], Sf["lam"]
    full = {
        "R88": gamma[None, :] / gamma[:, None],
        "O88": omega[None, :] / omega[:, None],
        "BEAT": np.abs(omega[None, :] - omega[:, None]),
        "GT_prod": gamma[:, None] * lam[None, :],
        "GT_div": gamma[:, None] / lam[None, :],
        "OT_prod": omega[:, None] * lam[None, :],
        "OT_div": omega[:, None] / lam[None, :],
        "FULL_wr": (omega[None, :, None] / omega[:, None, None]) * lam[None, None, :],
        "FULL_gr": (gamma[None, :, None] / gamma[:, None, None]) * lam[None, None, :],
        "FULL_gd": (gamma[None, :, None] / gamma[:, None, None]) / lam[None, None, :],
        "FULL_bt": np.abs(omega[None, :, None] - omega[:, None, None]) * lam[None, None, :],
        "SUM_plus": gamma[None, :, None] + gamma[:, None, None] + lam[None, None, :],
        "SUM_minus": gamma[None, :, None] + gamma[:, None, None] - lam[None, None, :],
    }
    # per (target, family) 期望
    obs_web = {e["name"]: (e["value"], e["err"]) for e in web["obs"]}
    from collections import defaultdict
    actual_map = defaultdict(int)
    for r in obs_rows:
        actual_map[(r["target"], r["family"])] += int(r["count"])
    for tname, (tval, err) in obs_web.items():
        tol_eff = 3.0 * err * abs(tval) if err > 0 else 1e-9 * abs(tval)
        line = []
        for fam, X in full.items():
            N = X.size
            rng = max(float(X.max() - X.min()), 1e-12)
            E = N * 2 * tol_eff / rng
            a = actual_map.get((tname, fam), 0)
            sig = a / max(E, 1e-12)
            if a > 0 or sig > 3:
                line.append(f"{fam}:{a}/{E:.1f}({sig:.1f}×)")
        if line:
            print(f"  {tname:10s}  " + "  ".join(line))
            obs_out[tname] = line

    (DATA / "null_control.json").write_text(json.dumps(
        {"web": out, "obs": obs_out}, indent=2, ensure_ascii=False))
    print("\nRESULT: null control complete -> data/null_control.json")


if __name__ == "__main__":
    main()
