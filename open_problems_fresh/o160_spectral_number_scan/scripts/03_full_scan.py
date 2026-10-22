#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/03 — ★★★ 88×88×33 排除法全掃描 (R2/R3)

由零開始: 只由譜定義 γ_k = 4sin²(kπ/176), ω_k = 2sin(kπ/176), λ_c = 4sin²(cπ/68)
出發, 枚舉 13 個不變量族, 對照 constant_web.json 排除法過濾:

  Pass 0  全空間枚舉 (numpy 向量化)
  Pass 1  排除: |value − web| ≤ 1e-9·max(1,|web|) → EXACT HIT (閉合網連結)
  Pass 2  obs: |value − obs| ≤ 3σ·obs → OBS HIT (觀測量連結, O158 語境)
  Pass 3  trap: 1e-5~1e-3 窗 → 🟡 候選 (φ-trap, R12)
  Pass 4  novel: 整數/半整數/web-rational/小分母有理 唔喺 web → 🔮 待解釋
  Pass 5  去重: (family, value) 每值一個代表 + 多重度

輸出: data/scan_results.json + data/exact_hits.csv + data/obs_hits.csv
      + data/novel_candidates.csv + data/trap_candidates.csv
"""
import json
import sys
from pathlib import Path

import numpy as np

O160 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(O160))
from tools.registry import get_spectra  # noqa: E402

DATA = O160 / "data"
DATA.mkdir(exist_ok=True)

TOL_WEB = 1e-9       # 閉合網精確容差 (相對)
TOL_NOVEL = 1e-9     # 新數字偵測容差
TRAP_LO, TRAP_HI = 1e-5, 1e-3  # φ-trap 窗


def load_web():
    web = json.loads((DATA / "constant_web.json").read_text())
    targets = []  # (value, name, kind)
    for e in web["integers"] + web["halfints"] + web["rationals"]:
        targets.append((e["value"], e["name"], e.get("frac", "")))
    obs = [(e["value"], e["name"], e.get("err", 0.0)) for e in web["obs"]]
    return targets, obs


def find_hits(X, targets, tol, max_per_target=400):
    """對陣列 X 掃所有 target. 返回 [(target_name, value, idx_list_capped, count)]"""
    hits = []
    for tval, tname, tfrac in targets:
        tol_eff = tol * max(1.0, abs(tval))
        mask = np.abs(X - tval) <= tol_eff
        n = int(mask.sum())
        if n == 0:
            continue
        idxs = np.argwhere(mask)
        hits.append({
            "target": tname, "target_value": tval, "target_frac": tfrac,
            "value": float(X[mask][0]), "count": n,
            "cells": (idxs + 1)[:max_per_target].tolist(),
            "truncated": n > max_per_target,
        })
    return hits


def find_obs_hits(X, obs):
    hits = []
    for tval, tname, err in obs:
        tol_eff = 3.0 * err * abs(tval) if err > 0 else 1e-9 * abs(tval)
        if tol_eff <= 0:
            continue
        mask = np.abs(X - tval) <= tol_eff
        n = int(mask.sum())
        if n == 0:
            continue
        idxs = np.argwhere(mask)
        hits.append({
            "target": tname, "target_value": tval, "value": float(X[mask][0]),
            "rel_dev": float((X[mask][0] - tval) / tval), "count": n,
            "cells": (idxs + 1)[:300].tolist(), "truncated": n > 300,
        })
    return hits


def find_novel(X, web_ints, web_rat_vals, family, dims):
    """新數字偵測: 整數/半整數/web-rational/小分母有理 唔喺 web.
    只喺候選格上做 (mask), 唔全空間掃 rational."""
    novel = []
    # 候選 mask: 近整數 或 近半整數 (排除 0 — 對角退化, 冇結構)
    r = np.round(X)
    cand_int = np.abs(X - r) <= TOL_NOVEL * np.maximum(1.0, np.abs(X))
    r2 = np.round(2 * X) / 2.0
    cand_half = np.abs(X - r2) <= TOL_NOVEL * np.maximum(1.0, np.abs(X))
    cand = (cand_int | cand_half) & (np.abs(X) > 1e-12)
    # web-rational: |X·q − p| ≤ tol·q, p,q ∈ web ints — 只喺候選格做
    if cand.any():
        idxs = np.argwhere(cand)
        for ix in idxs[:4000]:
            v = float(X[tuple(ix)])
            # 近整數
            nint = int(round(v))
            if abs(v - nint) <= TOL_NOVEL * max(1.0, abs(v)) and nint not in web_ints:
                novel.append({"type": "integer", "value": v, "as": nint,
                              "cell": [int(i) + 1 for i in ix]})
                continue
            # 近半整數
            half = round(2 * v) / 2.0
            if abs(v - half) <= TOL_NOVEL * max(1.0, abs(v)) and half not in web_rat_vals:
                novel.append({"type": "half-integer", "value": v, "as": half,
                              "cell": [int(i) + 1 for i in ix]})
                continue
            # web-rational p/q (q ∈ web ints)
            found = False
            for q in web_ints:
                p = int(round(v * q))
                if abs(v - p / q) <= TOL_NOVEL * max(1.0, abs(v)) and (p / q) not in web_rat_vals:
                    novel.append({"type": "web-rational", "value": v, "as": f"{p}/{q}",
                                  "cell": [int(i) + 1 for i in ix]})
                    found = True
                    break
            if found:
                continue
            # 小分母有理 q ≤ 34
            for q in range(2, 35):
                p = int(round(v * q))
                if abs(v - p / q) <= TOL_NOVEL * max(1.0, abs(v)) and (p / q) not in web_rat_vals:
                    novel.append({"type": "rational", "value": v, "as": f"{p}/{q}",
                                  "cell": [int(i) + 1 for i in ix]})
                    break
    return novel


def dedupe(hits):
    """按 (target, 值 12 位) 去重, 保留首個代表."""
    seen = set()
    out = []
    for h in sorted(hits, key=lambda h: (h["target"], -h["count"])):
        key = (h["target"], round(h["value"], 12))
        if key in seen:
            continue
        seen.add(key)
        out.append(h)
    return out


def main():
    S = get_spectra()
    gamma, omega, lam = S["gamma"], S["omega"], S["lam"]
    gamma44, omega44 = S["gamma44"], S["omega44"]
    web = json.loads((DATA / "constant_web.json").read_text())
    targets, obs = load_web()
    web_ints = {e["value"] for e in web["integers"]}
    web_rat_vals = {e["value"] for e in web["integers"] + web["halfints"] + web["rationals"]}

    # ── Pass 0: 全空間枚舉 ──
    G2 = gamma[None, :] / gamma[:, None]          # (88,88) R88
    O2 = omega[None, :] / omega[:, None]          # O88
    B2 = np.abs(omega[None, :] - omega[:, None])  # BEAT
    GTp = gamma[:, None] * lam[None, :]           # (88,33)
    GTd = gamma[:, None] / lam[None, :]
    OTp = omega[:, None] * lam[None, :]
    OTd = omega[:, None] / lam[None, :]
    # FULL (88,88,33)
    Gr = gamma[None, :, None] / gamma[:, None, None]
    Or = omega[None, :, None] / omega[:, None, None]
    B3 = np.abs(omega[None, :, None] - omega[:, None, None])
    L3 = lam[None, None, :]
    F_wr = Or * L3
    F_gr = Gr * L3
    F_gd = Gr / L3
    F_bt = B3 * L3
    G3 = gamma[None, :, None] + gamma[:, None, None] + L3
    G3m = gamma[None, :, None] + gamma[:, None, None] - L3

    families = {
        "R88": G2, "O88": O2, "BEAT": B2,
        "GT_prod": GTp, "GT_div": GTd, "OT_prod": OTp, "OT_div": OTd,
        "FULL_wr": F_wr, "FULL_gr": F_gr, "FULL_gd": F_gd, "FULL_bt": F_bt,
        "SUM_plus": G3, "SUM_minus": G3m,
    }

    results = {}
    all_hits, all_obs, all_novel, all_traps = [], [], [], []
    for fname, X in families.items():
        cells = int(X.size)
        hits = find_hits(X, targets, TOL_WEB)
        obs_hits = find_obs_hits(X, obs)
        # trap 窗 (唔包括 web 命中格)
        trap = []
        for tval, tname, tfrac in targets:
            d = np.abs(X - tval)
            in_win = (d > TRAP_LO * max(1.0, abs(tval))) & (d <= TRAP_HI * max(1.0, abs(tval)))
            n = int(in_win.sum())
            if n:
                trap.append({"target": tname, "count": n,
                             "value": float(X[in_win][0]),
                             "cell": np.argwhere(in_win)[:10].tolist()})
        novel = find_novel(X, web_ints, web_rat_vals, fname, X.shape)
        # 去重 (exact hits 按 target+value)
        hits = dedupe(hits)
        results[fname] = {
            "cells": cells, "exact": len(hits), "exact_raw": sum(h["count"] for h in hits),
            "obs": len(obs_hits), "trap_targets": len(trap), "novel": len(novel),
        }
        all_hits += [dict(h, family=fname) for h in hits]
        all_obs += [dict(h, family=fname) for h in obs_hits]
        all_traps += [dict(t, family=fname) for t in trap]
        all_novel += [dict(n, family=fname) for n in novel]
        print(f"  {fname:10s} cells={cells:9d}  exact={len(hits):4d} "
              f"obs={len(obs_hits):3d} trap_tgt={len(trap):3d} novel={len(novel):4d}")

    # ── 44-chain 次框架 (對照) ──
    G44 = gamma44[None, :] / gamma44[:, None]
    O44 = omega44[None, :] / omega44[:, None]
    B44 = np.abs(omega44[None, :] - omega44[:, None])
    G44T = gamma44[:, None] * lam[None, :]
    O44T = omega44[:, None] * lam[None, :]
    results["_44chain"] = {
        "R44": len(dedupe(find_hits(G44, targets, TOL_WEB))),
        "O44": len(dedupe(find_hits(O44, targets, TOL_WEB))),
        "BEAT44": len(dedupe(find_hits(B44, targets, TOL_WEB))),
        "G44T": len(dedupe(find_hits(G44T, targets, TOL_WEB))),
        "O44T": len(dedupe(find_hits(O44T, targets, TOL_WEB))),
    }
    print("  [44-chain 次框架] R44/O44/BEAT44/G44T/O44T exact:",
          results["_44chain"])

    # ── 存檔 ──
    summary = {"families": results,
               "total_exact": len(all_hits), "total_obs": len(all_obs),
               "total_novel": len(all_novel), "total_trap_targets": len(all_traps)}
    (DATA / "scan_results.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    (DATA / "exact_hits.csv").write_text(
        "family,target,target_value,value,count,cell_a,cell_b,cell_c,truncated\n" +
        "\n".join(
            f"{h['family']},{h['target']},{h['target_value']:.10g},{h['value']:.12g},"
            f"{h['count']},{h['cells'][0][0] if h['cells'] else ''},"
            f"{h['cells'][0][1] if len(h['cells'][0])>1 else ''},"
            f"{h['cells'][0][2] if len(h['cells'][0])>2 else ''},{h['truncated']}"
            for h in all_hits))
    (DATA / "obs_hits.csv").write_text(
        "family,target,target_value,value,rel_dev,count,cell_a,cell_b,cell_c\n" +
        "\n".join(
            f"{h['family']},{h['target']},{h['target_value']:.10g},{h['value']:.12g},"
            f"{h['rel_dev']:.3g},{h['count']},"
            f"{h['cells'][0][0] if h['cells'] else ''},"
            f"{h['cells'][0][1] if len(h['cells'][0])>1 else ''},"
            f"{h['cells'][0][2] if len(h['cells'][0])>2 else ''}"
            for h in all_obs))
    (DATA / "novel_candidates.csv").write_text(
        "family,type,value,as,cell_a,cell_b,cell_c\n" +
        "\n".join(
            f"{n['family']},{n['type']},{n['value']:.12g},{n['as']},"
            f"{n['cell'][0] if len(n['cell'])>0 else ''},"
            f"{n['cell'][1] if len(n['cell'])>1 else ''},"
            f"{n['cell'][2] if len(n['cell'])>2 else ''}"
            for n in all_novel))
    (DATA / "trap_candidates.csv").write_text(
        "family,target,value,count\n" +
        "\n".join(f"{t['family']},{t['target']},{t['value']:.12g},{t['count']}"
                  for t in all_traps[:500]))
    print(f"\n===== 掃描摘要 =====")
    print(f"  exact web hits: {len(all_hits)} distinct (raw {sum(h['count'] for h in all_hits)})")
    print(f"  obs hits:       {len(all_obs)}")
    print(f"  novel:          {len(all_novel)}")
    print(f"  trap targets:   {len(all_traps)}")
    print("RESULT: full scan complete -> data/scan_results.json")


if __name__ == "__main__":
    main()
