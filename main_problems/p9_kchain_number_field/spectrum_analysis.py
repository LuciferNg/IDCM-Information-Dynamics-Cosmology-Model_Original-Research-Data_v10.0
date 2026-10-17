#!/usr/bin/env python3
"""
拍頻光譜學 — 由 946 個拍頻值外推新模式
========================================
方法: 唔用 (d,s) 座標, 純粹睇 beat 值本身嘅分佈
      搵簇、間隙、比例、同已知常數嘅關係
"""
from math import pi, sin, sqrt, log
from collections import Counter

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

# 全部 946 個拍頻值
bvals = [beat(i,j) for (i,j) in pairs]
bmin, bmax = min(bvals), max(bvals)
print("="*72)
print("1. 拍頻光譜基本統計")
print("="*72)
print(f"拍頻數: {len(bvals)}")
print(f"值範圍: {bmin:.6f} .. {bmax:.6f}")
print(f"中位數: {sorted(bvals)[len(bvals)//2]:.6f}")
print(f"平均:   {sum(bvals)/len(bvals):.6f}")

# 直方圖
bins = 20
bin_w = (bmax-bmin)/bins
hist = [0]*bins
for v in bvals:
    idx = min(int((v-bmin)/bin_w), bins-1)
    hist[idx] += 1
print(f"\n直方圖 (20 bins):")
for i, h in enumerate(hist):
    lo = bmin + i*bin_w
    hi = lo + bin_w
    bar = '█' * (h//5)
    print(f"  [{lo:.4f},{hi:.4f}): {h:3d} {bar}")

print("\n" + "="*72)
print("2. ★ 拍頻值『間隙』分析")
print("="*72)
sorted_b = sorted(bvals)
gaps = [(sorted_b[k+1]-sorted_b[k], k, sorted_b[k], sorted_b[k+1]) 
        for k in range(len(sorted_b)-1)]
gaps.sort(reverse=True)
print("最大 10 個間隙:")
for gap, k, v1, v2 in gaps[:10]:
    print(f"  gap={gap:.6f}  [{v1:.6f} → {v2:.6f}]  (pos {k}/{len(sorted_b)})")

print("\n" + "="*72)
print("3. ★ 拍頻值『簇』分析 (近鄰密度)")
print("="*72)
# 每個拍頻值周圍 0.001 範圍內有幾多個其他拍頻?
eps = 0.001
clusters = []
for idx, v in enumerate(sorted_b):
    # 往前數
    cnt = 1
    j = idx-1
    while j >= 0 and sorted_b[idx] - sorted_b[j] < eps:
        cnt += 1
        j -= 1
    # 往後數
    j = idx+1
    while j < len(sorted_b) and sorted_b[j] - sorted_b[idx] < eps:
        cnt += 1
        j += 1
    if cnt >= 5:  # 至少 5 個近鄰
        clusters.append((v, cnt))
# 去重 (只保留每個簇中心)
print(f"密度≥5 嘅簇 ({len(clusters)} 個):")
seen = set()
for v, cnt in sorted(clusters, key=lambda x: -x[1])[:15]:
    # 聚合
    key = round(v, 3)
    if key not in seen:
        seen.add(key)
        print(f"  中心 ~{v:.4f}: {cnt} 個拍頻喺 ±{eps} 範圍")

print("\n" + "="*72)
print("4. ★ 拍頻值 vs 已知常數 (外推候選)")
print("="*72)
# 已知物理參數拍頻值
phys = {
    (1,18): "m_μ/m_τ", (1,22): "m_s/m_d", (7,20): "n/p",
    (8,22): "c/s", (8,33): "m_c/m_b", (10,24): "u/d",
    (19,33): "t/b", (19,38): "m_H/m_W", (30,41): "m_W/m_Z"
}
phys_vals = {f"{name} ({i},{j})": beat(i,j) for (i,j), name in phys.items()}
print("已知物理拍頻值:")
for name, val in sorted(phys_vals.items(), key=lambda x: x[1]):
    print(f"  {name:30s} = {val:.8f}")

# 找「接近但未用」嘅拍頻值
print("\n候選: 靠近已知物理拍頻嘅『未用』拍頻 (差值 < 0.001):")
for (p_i,p_j), pname in phys.items():
    pv = beat(p_i,p_j)
    for (i,j) in pairs:
        if (i,j) == (p_i,p_j): continue
        bv = beat(i,j)
        diff = abs(bv-pv)
        if diff < 0.0005:
            print(f"  {pname:20s} beat({i:2d},{j:2d})={bv:.6f} 差 {diff:.6f} (近 beat({p_i},{p_j})={pv:.6f})")

print("\n" + "="*72)
print("5. ★ 拍頻比例光譜 (beat/beat = 無理數族)")
print("="*72)
# 檢查: 拍頻之間嘅比例係咪接近簡單有理數?
print("拍頻比接近簡單有理數 (1/2, 2/3, 3/4, 4/5, 5/6, 3/2, 4/3, 5/3, 5/4):")
targets = [(1,2), (2,3), (3,4), (4,5), (5,6), (3,2), (4,3), (5,3), (5,4)]
for (i,j) in pairs[:100]:  # 抽樣
    vi = beat(i,j)
    for (p,q) in targets:
        for (k,l) in pairs:
            if (k,l) <= (i,j): continue
            vk = beat(k,l)
            if abs(vi/vk - p/q) < 0.0001:
                print(f"  beat({i:2d},{j:2d})/beat({k:2d},{l:2d}) = {vi/vk:.6f} ≈ {p}/{q}")