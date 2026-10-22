#!/usr/bin/env python3
"""
O43-D: k↔temperature stratification — corrected leave-one-out
"""
import numpy as np
import os

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
OUT = f"{BASE}/open_problems_fresh/o43_holographic_untested"

# Load node temperatures
T = {}
with open(f"{BASE}/open_problems_fresh/o3_node_temperatures/data/node_temps.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        T[int(p[0])] = float(p[2])

# Load k values from anchored_coloring.txt
k_file = []
with open(f"{BASE}/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt") as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        p = line.split()
        k_file.append(int(p[-1]))

k = np.array(k_file)
T_arr = np.array([T[i] for i in range(60)])

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O43-D: 修正 Leave-one-out 分析")
log("=" * 72)

k0_indices = np.where(k == 0)[0]
k1_indices = np.where(k == 1)[0]
k2_indices = np.where(k == 2)[0]
log(f"k=0 節點: {list(k0_indices)}")
log(f"k=2 節點: {list(k2_indices)}")

# Original mean
m0_orig = np.mean(np.abs(T_arr[k0_indices]))
log(f"\n原始 k=0 mean|T| = {m0_orig:.1f}")

# Correct leave-one-out
log(f"\nLeave-one-out (移除單個 k=0 節點):")
for i in k0_indices:
    mask = np.ones(60, dtype=bool)
    mask[i] = False
    remaining_k0 = k[mask] == 0
    m0_loo = np.mean(np.abs(T_arr[mask][remaining_k0]))
    log(f"   移除 #{i} (T={T_arr[i]:+.1f}): k=0 mean|T| = {m0_loo:.1f} (Δ={m0_loo-m0_orig:+.1f})")

# Leave-one-out for k=2
log(f"\nLeave-one-out (移除單個 k=2 節點):")
m2_orig = np.mean(np.abs(T_arr[k2_indices]))
for i in k2_indices:
    mask = np.ones(60, dtype=bool)
    mask[i] = False
    remaining_k2 = k[mask] == 2
    m2_loo = np.mean(np.abs(T_arr[mask][remaining_k2]))
    log(f"   移除 #{i} (T={T_arr[i]:+.1f}): k=2 mean|T| = {m2_loo:.1f} (Δ={m2_loo-m2_orig:+.1f})")

# Combined sensitivity
log(f"\n組合移除 (極端節點):")
for remove_set in [[0], [53], [0, 53], [9], [0, 9, 53]]:
    mask = np.ones(60, dtype=bool)
    for r in remove_set:
        mask[r] = False
    k_trim = k[mask]
    T_trim = T_arr[mask]
    for kv in [0, 1, 2]:
        mv = np.mean(np.abs(T_trim[k_trim == kv]))
        log(f"   移除 {remove_set}: k={kv} mean|T| = {mv:.1f}")
    # Check ordering
    m0_t = np.mean(np.abs(T_trim[k_trim == 0]))
    m1_t = np.mean(np.abs(T_trim[k_trim == 1]))
    m2_t = np.mean(np.abs(T_trim[k_trim == 2]))
    log(f"   排序 k0>k1>k2? {m0_t > m1_t > m2_t}")

with open(f"{OUT}/data_o43d_v2.txt", "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/data_o43d_v2.txt")