#!/usr/bin/env python3
"""
盲測批量 v2: 30 條隨機拍頻 COMMAND/WORKFLOW 全面統計
+ 深度分析 magic 行成員
"""
import random, json, math
from math import pi, sin
from collections import Counter

Nd = 44
w = lambda n: 2*sin(pi*n/88)
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123}
L_inv = {v:k for k,v in L.items()}
magic_rows = {7:"m7", 14:"GEN", 20:"T(s->d)", 22:"half-node", 33:"K_tree"}
phys_labels = {
    (10,24): "u/d", (8,22): "c/s", (19,33): "t/b",
    (8,33): "m_c/m_b", (1,22): "m_s/m_d", (30,41): "m_W/m_Z",
    (19,38): "m_H/m_W", (1,18): "m_mu/m_tau", (7,20): "n/p",
}

pairs = [(i,j) for i in range(1,Nd) for j in range(i+1,Nd+1)]
random.seed(20260826)  # 新 seed, 新一批
drawn = random.sample(pairs, 30)

def classify(i, j):
    d = j - i; s = j + i
    beat = abs(w(j) - w(i))
    info = {"pair": (i,j), "d": d, "s": s, "beat": round(beat, 8),
            "s-d": s-d, "s+d": s+d}
    info["d_role"] = magic_rows.get(d, f"L{L_inv[d]}" if d in L_inv else f"plain({d})")
    info["s_role"] = "M-pipe" if s==33 else ("N_d" if s==44 else (f"L{L_inv[s]}" if s in L_inv else f"plain({s})"))
    info["phys"] = phys_labels.get((min(i,j),max(i,j)))
    info["workflow"] = []
    if d == 7: info["workflow"].append("m7-anchor")
    if d == 14: info["workflow"].append("GEN")
    if d == 20: info["workflow"].append("T(s->d)")
    if d == 22: info["workflow"].append("half-node")
    if d == 33: info["workflow"].append("K_tree")
    if s == 33: info["workflow"].append("M-pipeline")
    if s == 44: info["workflow"].append("N_d-domain")
    if not info["workflow"]: info["workflow"] = ["一般填充"]
    if i == 2 or j == 2: info["sync"] = True
    else: info["sync"] = False
    return info

results = [classify(i,j) for i,j in drawn]
# 輸出簡潔表
print(f"{'pair':>8} {'d':>3} {'s':>3} {'beat':>10} {'d_role':>12} {'s_role':>10} {'workflow':>16} {'phys':>10} {'sync':>5}")
for r in results:
    print(f"({r['pair'][0]:>2},{r['pair'][1]:>2}) {r['d']:>3} {r['s']:>3} {r['beat']:>10.6f} "
          f"{r['d_role']:>12} {r['s_role']:>10} {','.join(r['workflow']):>16} {str(r['phys']):>10} {r['sync']}")

# 統計
print("\n=== 統計 ===")
dc = Counter(r["d_role"].split("(")[0] for r in results)
print("d_role 分布:", dict(dc))
wf = Counter(wf for r in results for wf in r["workflow"])
print("workflow 分布:", dict(wf))
phys_n = sum(1 for r in results if r["phys"])
print(f"物理參數命中: {phys_n}/30")
magic_n = sum(1 for r in results if r["workflow"] != ["一般填充"])
print(f"magic workflow 命中: {magic_n}/30")
sync_n = sum(1 for r in results if r["sync"])
print(f"SYNC 家族: {sync_n}/30")
