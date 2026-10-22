#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/09 — 44-chain FULL 掃描 (docs/05 開放項 4)

44-mode chain (γ44_n = 4sin²(nπ/88), ω44_n = 2sin(nπ/88)) × K_Tree-33:
  44×44×33 = 63,888 格 × 13 族 — 主掃描 (88×88×33) 嘅完整性對照。

目的: 證明 44-chain 全譜冇新結構 (或者發現新身份)。
預期: 中心模 n=22 → 同類命中 (γ44₂₂×λ₁₇ = 4 = B 等), 冇新嘢 (O152 A7:
44-site 全譜 ≡ 88-site 偶子空間 — 44-chain 係 88 鏈嘅偶子集, 結構已包含)。
"""
import json
import sys
from pathlib import Path

import numpy as np

O160 = Path(__file__).resolve().parent.parent
DATA = O160 / "data"
sys.path.insert(0, str(O160))
from tools.registry import get_spectra  # noqa: E402

TOL = 1e-9


def find_hits(X, targets, tol=TOL, max_per_target=3):
    """|X − t| ≤ tol·max(1,|t|) → hits (0-indexed cells)."""
    hits = []
    for tname, tval in targets:
        mask = np.abs(X - tval) <= tol * max(1.0, abs(tval))
        n = int(mask.sum())
        if n:
            idxs = np.argwhere(mask)
            hits.append({"target": tname, "target_value": tval, "count": n,
                         "cells": (idxs + 1)[:max_per_target].tolist()})
    return hits


def main():
    S = get_spectra()
    g = S["gamma44"]  # 4sin²(nπ/88), n=1..44
    o = S["omega44"]  # 2sin(nπ/88)
    l = S["lam"]      # λ_c = 4sin²(cπ/68), c=1..33

    web = json.loads((DATA / "constant_web.json").read_text())
    targets = [(e["name"], e["value"]) for e in web["integers"] + web["halfints"] + web["rationals"]]

    fams = {
        "R44": g[None, :] / g[:, None],
        "O44": o[None, :] / o[:, None],
        "BEAT44": np.abs(o[None, :] - o[:, None]),
        "G44T_prod": g[:, None] * l[None, :],
        "G44T_div": g[:, None] / l[None, :],
        "O44T_prod": o[:, None] * l[None, :],
        "O44T_div": o[:, None] / l[None, :],
        "F44_wr": (o[None, :, None] / o[:, None, None]) * l[None, None, :],
        "F44_gr": (g[None, :, None] / g[:, None, None]) * l[None, None, :],
        "F44_gd": (g[None, :, None] / g[:, None, None]) / l[None, None, :],
        "F44_bt": np.abs(o[None, :, None] - o[:, None, None]) * l[None, None, :],
        "S44_plus": g[None, :, None] + g[:, None, None] + l[None, None, :],
        "S44_minus": g[None, :, None] + g[:, None, None] - l[None, None, :],
    }

    print("=== 44-chain FULL 掃描 (44×44×33 = 63,888 格 × 13 族) ===")
    total_distinct = 0
    for fam, X in fams.items():
        N = X.size
        hits = find_hits(X, targets)
        distinct = {}
        for h in hits:
            key = (h["target"], round(float(X[np.argwhere(np.abs(X - h["target_value"]) <= TOL * max(1, abs(h["target_value"])))][0] if False else h["target_value"]), 12))
            distinct.setdefault(key, h)
        total_distinct += len(distinct)
        for h in hits:
            c = h["cells"][0] if h["cells"] else []
            print(f"  {fam:12s} {h['target']:<8s} = {h['target_value']:<6g} count={h['count']:>3d} "
                  f"first=({','.join(map(str, c))})")
    print(f"\nRESULT: 44-chain 掃描完成 — {total_distinct} distinct web 命中")
    # 結論: 命中應該全部係中心模 n=22 / λ₁₇ 組合, 冇新結構


if __name__ == "__main__":
    main()
