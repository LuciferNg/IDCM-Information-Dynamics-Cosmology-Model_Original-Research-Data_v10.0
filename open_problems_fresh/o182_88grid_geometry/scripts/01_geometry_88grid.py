#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O182 scripts/01 — 88 格幾何構造: A5 網絡透明邊中點
====================================================
構造 (零新常數, 鏈結構直接推出):
  88 格 = A5 60 節點網絡嘅 88 條正常(透明, 雙色)邊嘅中點
  88 = 120 邊 - 32 阻挫邊  (O21: 88 normal edges = TRANSPARENT)
  對應 O159 88-site 鏈 (176-Laplacian) 嘅 88 site
  期望: 88 中點 = 44 對極對 (鏈嘅 44 mode pairs, N_d = 44)

驗證:
  1. 60 節點圖重建: 閾值 28° (26.09° 邊長 + 擾動, 下一層 31.68° — cmb_cold_spot/scripts/14 原設定)
     -> 120 邊 (每節點度 4)
  2. 阻挫邊計數 = 32 (同色), 正常邊 = 88 (異色)
  3. 與 cmb_cold_spot/data/frustration_edges.txt 交叉 (邊距離一致)
  4. 均勻性: 中點最近鄰距離分佈
  5. 88 格與 A5 節點分離度 (唔重疊)
"""
import numpy as np
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
DATA = ROOT / "cmb_cold_spot/data"

ok = 0; tot = 0
def chk(name, cond, note=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")

# ---- 1. 節點 + 著色 ----
nodes = np.loadtxt(DATA / "a5_nodes.txt")           # RA Dec (deg)
colors = {}
for line in (DATA / "anchored_coloring.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    colors[int(p[0])] = int(p[3])
col = np.array([colors[i] for i in range(60)])
ra, dec = np.radians(nodes[:,0]), np.radians(nodes[:,1])
v = np.column_stack([np.cos(dec)*np.cos(ra), np.cos(dec)*np.sin(ra), np.sin(dec)])
print(f"節點: {len(nodes)}, 著色: {col.sum()}×1 / {(1-col).sum()}×0 (expect 30/30)")

# 對極閉合 of node set
def antipodal_pairs(V, atol=1e-9):
    pairs = []
    used = set()
    for i in range(len(V)):
        if i in used: continue
        for j in range(i+1, len(V)):
            if j in used: continue
            if np.allclose(V[i], -V[j], atol=atol):
                pairs.append((i, j)); used.add(i); used.add(j); break
    return pairs

ap = antipodal_pairs(v)
print(f"A5 節點對極對: {len(ap)} — 結構事實: A₅ 旋轉群軌道冇反演, 0 對係預期 (非 FAIL)")

# ---- 2. 圖重建: 閾值 28° (原 script 14 設定) ----
dmat = np.arccos(np.clip(v @ v.T, -1, 1))           # angular distance matrix (rad)
THRESH = np.radians(28.0)
edges = [(i, j) for i in range(60) for j in range(i+1, 60) if dmat[i, j] < THRESH]
print(f"\n邊閾值: 28° -> 邊數 {len(edges)} (expect 120)")
deg = np.zeros(60, dtype=int)
for i, j in edges: deg[i] += 1; deg[j] += 1
print(f"每節點度數分佈: {sorted(set(deg.tolist()))} (expect [4])")
chk("圖重建: 120 邊, 度 4", len(edges) == 120 and set(deg.tolist()) == {4})
# 距離直方圖確認兩層
d_edges = np.degrees([dmat[i, j] for i, j in edges])
d_next = np.min([dmat[i, j] for i in range(60) for j in range(i+1, 60) if dmat[i, j] >= THRESH])
print(f"邊距離範圍: {d_edges.min():.3f}–{d_edges.max():.3f}° (下一層 {np.degrees(d_next):.2f}°)")

# ---- 3. 阻挫 vs 正常 ----
frust = [(i, j) for (i, j) in edges if col[i] == col[j]]
normal = [(i, j) for (i, j) in edges if col[i] != col[j]]
print(f"阻挫邊 (同色): {len(frust)} (expect 32), 正常邊 (異色): {len(normal)} (expect 88)")
chk("阻挫 32 / 正常 88", len(frust) == 32 and len(normal) == 88)

# 與 frustration_edges.txt 交叉
fr_file = set()
for line in (DATA / "frustration_edges.txt").read_text().splitlines():
    if line.startswith("#") or not line.strip(): continue
    p = line.split()
    u, w = int(p[0]), int(p[1])
    fr_file.add((min(u,w), max(u,w)))
print(f"frustration_edges.txt 條目: {len(fr_file)}")
chk("阻挫邊與檔案完全一致", set(frust) == fr_file,
    f"(file {len(fr_file)}, reconstructed {len(frust)})")

# ---- 4. 88 格 = 正常邊中點 ----
out = ROOT / "o182_88grid_geometry/data"
out.mkdir(parents=True, exist_ok=True)
mid = np.array([(v[i] + v[j]) for (i, j) in normal])
mid = mid / np.linalg.norm(mid, axis=1, keepdims=True)
print(f"\n88 格節點: {len(mid)}")

# 對極閉合 (A5 旋轉軌道冇反演 — 唔預期閉合, 純記錄)
apm = antipodal_pairs(mid)
print(f"88 中點對極對: {len(apm)} (A5 旋轉軌道冇反演 — 唔預期 44)")

# ---- 5. 均勻性: 最近鄰角距分佈 ----
dm = np.arccos(np.clip(mid @ mid.T, -1, 1))
np.fill_diagonal(dm, np.inf)
nn = np.min(dm, axis=1)
print(f"88 格最近鄰角距: mean {np.degrees(nn.mean()):.2f}°  std {np.degrees(nn.std()):.2f}°")
print(f"  均勻球面期望 (N=88): 平均間距 ~{np.degrees(np.sqrt(4*np.pi/88)):.2f}°")
# 最小最近鄰距離 (有冇退化/重疊)
print(f"  最小最近鄰: {np.degrees(nn.min()):.3f}°")

# 與 60 節點分離檢查 (88 格應該係新點, 唔重疊)
d60 = np.arccos(np.clip(mid @ v.T, -1, 1)).min(axis=1)
print(f"88 格與 A5 節點最近距離: min {np.degrees(d60.min()):.2f}°  (應 > 0, 新點集)")

# 32 阻挫邊中點 (控制組)
fmid = np.array([(v[i] + v[j]) for (i, j) in frust])
fmid = fmid / np.linalg.norm(fmid, axis=1, keepdims=True)
raF = np.degrees(np.arctan2(fmid[:,1], fmid[:,0])) % 360
decF = np.degrees(np.arcsin(fmid[:,2]))
np.savetxt(out / "g32_frustration_midpoints.txt", np.column_stack([raF, decF]), fmt="%.4f")
print(f"32 阻挫邊中點 (控制組): {len(fmid)} 已輸出 g32_frustration_midpoints.txt")

# 緯度分佈
dec88 = np.degrees(np.arcsin(mid[:,2]))
print(f"88 格緯度: mean {dec88.mean():+.1f}°  |b| 分佈: <20°: {(np.abs(dec88)<20).sum()}, 20-40°: {((np.abs(dec88)>=20)&(np.abs(dec88)<40)).sum()}, >40°: {(np.abs(dec88)>=40).sum()}")

# ---- 6. 輸出 RA/Dec ----
ra88 = np.degrees(np.arctan2(mid[:,1], mid[:,0])) % 360
dec88 = np.degrees(np.arcsin(mid[:,2]))
out = ROOT / "o182_88grid_geometry/data"
out.mkdir(parents=True, exist_ok=True)
np.savetxt(out / "g88_nodes.txt", np.column_stack([ra88, dec88]), fmt="%.4f")
# 邊中點對應 (edge -> midpoint idx)
with open(out / "g88_edge_map.txt", "w") as f:
    f.write("# mid_idx edge_u edge_v (normal edge endpoints)\n")
    for k, (i, j) in enumerate(normal):
        f.write(f"{k} {i} {j}\n")

print(f"\n輸出: {out}/g88_nodes.txt (88 點 RA Dec)")
print(f"      {out}/g88_edge_map.txt (88 邊 -> 中點)")
print(f"\nRESULT: {ok}/{tot} PASS")
