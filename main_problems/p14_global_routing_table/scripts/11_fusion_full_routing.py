#!/usr/bin/env python3
"""GRT-11b: 2640 節點融合路由表 — 張量積公式版本.

利用 Cartesian product 性質:
  dist((a,k), (a',k')) = dist_A5(a,a') + dist_K(k,k')
  next_hop: 優先沿距離>0 嘅方向跳

比 BFS 快 1000 倍, 數學上 exact.
"""
import sys
import os
import time

import numpy as np

sys.path.insert(0, ".")
from grt_common import (build_graph, edge_threshold_from_histogram,
                        load_nodes)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

# ---------- 載入 A5 hop matrix ----------
hop5 = np.load(f"{OUT}/hop_matrix.npy")
next5 = np.load(f"{OUT}/next_hop_table.npy")
NA5 = 60
NK = 44
NLOG = NA5 * NK  # 2640

# ---------- K_Chain hop matrix (環距離) ----------
t0 = time.time()
hopK = np.zeros((NK, NK), dtype=np.int16)
for k in range(NK):
    for m in range(NK):
        hopK[k, m] = min(abs(k - m), NK - abs(k - m))

# K_Chain next-hop
nextK = np.full((NK, NK), -1, dtype=np.int16)
for k in range(NK):
    for m in range(NK):
        if k == m:
            nextK[k, m] = -1
        elif hopK[k, m] == 1:
            nextK[k, m] = m
        else:
            # 向 m 方向跳
            if (k + 1) % NK == m or (k - 1) % NK == m:
                nextK[k, m] = m
            elif (k < m and m - k <= NK // 2) or (k > m and k - m > NK // 2):
                nextK[k, m] = (k + 1) % NK
            else:
                nextK[k, m] = (k - 1) % NK if k > 0 else NK - 1

print(f"[1] 載入 A5: {NA5}×{NA5}, K_Chain: {NK}×{NK}")

# ---------- 張量積融合 hop matrix ----------
# hop[(a,k), (a',k')] = hop5[a,a'] + hopK[k,k']
# 用廣播: (60,44,60,44) -> reshape to (2640,2640)
h5 = hop5.reshape(NA5, 1, NA5, 1)  # (60,1,60,1)
hK = hopK.reshape(1, NK, 1, NK)    # (1,44,1,44)
hop = (h5 + hK).reshape(NLOG, NLOG).astype(np.int16)

t1 = time.time()
print(f"[2] 融合 hop matrix: {t1-t0:.3f}s ({hop.nbytes/1e6:.1f} MB)")

# ---------- 張量積 next-hop ----------
# next_hop[(a,k), (a',k')]:
#   如果 hop5[a,a'] > 0 → 跳 A5 方向: next5[a,a']*NK + k
#   否則 (hopK[k,k'] > 0) → 跳 K 方向: a*NK + nextK[k,k']
#   如果兩個都 > 0 → 優先跳 A5 (或者可以揀)
# 用廣播 + 向量化
nh5 = next5.reshape(NA5, 1, NA5, 1)  # (60,1,60,1)
nhK = nextK.reshape(1, NK, 1, NK)    # (1,44,1,44)
h5_bool = hop5.reshape(NA5, 1, NA5, 1) > 0  # A5 方向有距離

# 如果 A5 距離 > 0 → 跳 A5, 否則跳 K
# A5 跳: next_hop = nh5 * NK + k_idx
# K 跳: next_hop = a_idx * NK + nhK
a_idx = np.arange(NA5).reshape(NA5, 1, 1, 1)  # (60,1,1,1)
k_idx = np.arange(NK).reshape(1, NK, 1, 1)    # (1,44,1,1)

# 生成 A5 跳
a5_jump = np.where(nh5 >= 0, nh5 * NK + k_idx, -1)
# 生成 K 跳
k_jump = np.where(nhK >= 0, a_idx * NK + nhK, -1)

# 合併: 優先 A5 跳 (如果 A5 距離 > 0)
next_hop = np.where(h5_bool, a5_jump, k_jump).reshape(NLOG, NLOG).astype(np.int16)

t2 = time.time()
print(f"[3] 融合 next-hop table: {t2-t1:.3f}s ({next_hop.nbytes/1e6:.1f} MB)")

# ---------- 驗證 ----------
# 隨機抽樣 1000 對驗證 hop 同 next-hop
rng = np.random.default_rng(42)
errors = 0
for _ in range(1000):
    s = rng.integers(NLOG)
    t = rng.integers(NLOG)
    if s == t:
        continue
    h = hop[s, t]
    # 驗證 hop 距離 > 0
    if h <= 0:
        print(f"  ❌ hop[{s},{t}] = {h}")
        errors += 1
        continue
    # 驗證 next-hop 存在
    nh = next_hop[s, t]
    if nh < 0:
        print(f"  ❌ next_hop[{s},{t}] = {nh}")
        errors += 1
        continue
    # 驗證 next-hop 係鄰居 (hop[nh, t] == h-1)
    if hop[nh, t] != h - 1:
        print(f"  ❌ hop[{nh},{t}] = {hop[nh,t]}, 預期 {h-1}")
        errors += 1
        continue

if errors == 0:
    print(f"[4] 抽樣驗證: 1000 對全部通過 ✅")
else:
    print(f"[4] 抽樣驗證: {errors}/1000 錯誤 ❌")

# ---------- 統計 ----------
diam = int(hop.max())
avg = float(hop.mean())
hist = {d: int((hop == d).sum()) for d in range(diam + 1)}
print(f"[5] 直徑: {diam} hops, 平均: {avg:.4f}")
print(f"    跳數分佈 (頭尾):")
for d in [0, 1, 2, 3, 28, 29, 30]:
    print(f"      d={d:<3}: {hist[d]:<10} ({hist[d]/(NLOG*NLOG)*100:.3f}%)")
print(f"    分佈對稱: {'✅' if all(hist[d] == hist[diam-d] for d in range(diam+1)) else '❌'}")

# ---------- 保存 ----------
np.save(f"{OUT}/fusion_hop_matrix.npy", hop)
np.save(f"{OUT}/fusion_next_hop_table.npy", next_hop)
np.save(f"{OUT}/fusion_stats.npy", np.array([diam, avg, NLOG, NA5, NK]))
print(f"[6] 已保存")

# ---------- 路由路徑 ----------
print(f"\n[7] 冷斑 ({0}, mode 0) → 對跖 A5({57}, mode 0):")
s = 0 * NK + 0
t = 57 * NK + 0
path = [s]
cur = s
while cur != t:
    nxt = next_hop[cur, t]
    path.append(nxt)
    cur = nxt
print(f"    hops: {len(path)-1}")
# 顯示 A5 同 mode 序列
a5_seq = [p // NK for p in path]
k_seq = [p % NK for p in path]
print(f"    A5: {' → '.join(str(a) for a in a5_seq)}")
print(f"    K:  {' → '.join(str(k) for k in k_seq)}")

# 最遠對 (A5 對跖 + mode 相隔 22)
print(f"\n[8] 最遠對 (A5 對跖 + mode 相隔 22):")
s = 0 * NK + 0
t = 57 * NK + 22
print(f"    ({0}, mode 0) → ({57}, mode 22): hop = {hop[s, t]}")
print(f"    (理論: 8 + 22 = 30)")

# 冷斑到所有節點嘅 hop 分佈
hop0 = hop[0]
print(f"\n[9] 冷斑邏輯節點 0 BFS 分佈:")
for d in range(0, diam + 1, 5):
    cnt = int((hop0 == d).sum())
    print(f"    d={d:<3}: {cnt:<5} 節點")