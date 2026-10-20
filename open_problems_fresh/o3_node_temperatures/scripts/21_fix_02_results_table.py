#!/usr/bin/env python3
"""
fix_02_results_table_v2.py — O3 審計輪 T2 修正 (2026-09-09)
保留原表格 spacing, 只改 T/hop cell 內容。
"""
import re, os

O3 = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o3_node_temperatures"
DOC = os.path.join(O3, "02_results.md")

truth = {}
with open(os.path.join(O3, "data/node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        truth[int(p[0])] = (int(p[1]), float(p[2]), int(p[5]))

lines = open(DOC).read().split("\n")
out = []
in_table = False
changed = 0
for ln in lines:
    if ln.startswith("| idx"):
        in_table = True
        out.append(ln)
        continue
    if in_table:
        if re.match(r"\| \d+ \|", ln) and "|" in ln:
            parts = ln.split("|")
            # 兩欄: idx cell 喺 parts[1] 同 parts[6] (每欄 4 cell: idx,色,T,hop)
            for i_pos in (1, 6):
                if i_pos + 3 < len(parts) and parts[i_pos].strip().isdigit():
                    idx = int(parts[i_pos].strip())
                    t_pos = i_pos + 2
                    h_pos = i_pos + 3
                    t_raw = parts[t_pos]
                    bold = "**" in t_raw
                    lead = t_raw[: len(t_raw) - len(t_raw.lstrip())]
                    trail = t_raw[len(t_raw.rstrip()):]
                    new_t = f"{truth[idx][1]:+.2f}"
                    if bold:
                        new_t = f"**{new_t}**"
                    new_t_cell = lead + new_t + trail
                    if parts[t_pos].strip() != new_t:
                        changed += 1
                    parts[t_pos] = new_t_cell
                    new_h_cell = lead + str(truth[idx][2]) + trail
                    if parts[h_pos].strip() != str(truth[idx][2]):
                        changed += 1
                    parts[h_pos] = new_h_cell
            out.append("|".join(parts))
            continue
        elif "完整數據" in ln:
            in_table = False
            out.append(ln)
            out.append("")
            out.append("> ⚠️ **2026-09-09 修正註記 (O3 審計輪)**: 本表 15 個 T 值 + 27 個 hop 值")
            out.append("> 原與 `data/node_temps.txt` 不一致 (抄錄錯誤), 已按 node_temps.txt 修正。")
            out.append("> ground truth 由 `o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits`")
            out.append("> 同源重抽驗證 (max|Δ|=0.000049 μK, 05 幻覺檢查同源)。原記錄保留做時序歷史。")
            out.append("")
            continue
        else:
            out.append(ln)
            continue
    out.append(ln)

open(DOC, "w").write("\n".join(out))
print("changed cells:", changed)
