#!/usr/bin/env python3
"""
O53 方向②: (36,98) 100 實例 block 譜統計測試
=================================================
問題: 1/3 本徵值結構 (J* 下 Block 0 有 1/3) 係咪 (36,98) 家族普適?

方法: 每個實例用 tip J (合法 Kähler) 做 Y = κ·J
      檢查 block 譜有冇 1/3 格點結構
      再用「隨機 J」做對照
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")

print("=" * 70)
print("O53: 100 實例 block 譜統計")
print("=" * 70)

from cytools import Polytope
from cytools.config import enable_experimental_features
enable_experimental_features()

# 解析 all_36_98.poly
polytopes = []
with open(os.path.join(BASE, 'all_36_98.poly')) as f:
    lines = [l.strip() for l in f if l.strip()]
i = 0
while i < len(lines):
    parts = lines[i].split()
    if len(parts) == 2 and parts[0].isdigit():
        n = int(parts[0])
        verts = []
        for j in range(n):
            verts.append([int(x) for x in lines[i+1+j].split()])
        polytopes.append(np.array(verts))
        i += 1 + n
    else:
        i += 1

print(f"總共 {len(polytopes)} 個實例")

# 對每個實例: 計算 κ (32×32 via tip), 檢查 1/3 本徵值
blocks = [(0,12), (12,24), (24,32)]
results = []
n_tested = 0

for k in range(min(30, len(polytopes))):
    p = Polytope(polytopes[k])
    try:
        tri = p.triangulate()
        cy = tri.get_cy()
        tip = cy.toric_kahler_cone().tip_of_stretched_cone(1)
        Kt = np.array(cy.compute_kappa_matrix(tip))  # 32×32
        
        # Block 0 (0:12)
        B0 = Kt[0:12, 0:12]
        ev0 = np.linalg.eigvalsh(B0)
        
        # 檢查 1/3 格點
        near13 = sum(1 for e in ev0 if abs(e - round(e*3)/3) < 0.05)
        has_13 = any(abs(e - 1/3) < 0.05 for e in ev0)
        
        # 全譜 1/3 統計
        ev_all = np.linalg.eigvalsh(Kt)
        near_all = sum(1 for e in ev_all if abs(e - round(e*3)/3) < 0.05)
        
        results.append((k, len(polytopes[k]), near13, has_13, near_all))
        print(f"  [{k}] {len(polytopes[k])}v: Block0 近1/3 = {near13}/12, 有1/3 = {has_13}, 全譜 = {near_all}/32")
        n_tested += 1
    except Exception as e:
        print(f"  [{k}] FAIL: {str(e)[:60]}")
    if n_tested >= 20:
        break

print(f"\n結果 ({len(results)} 個):")
if results:
    has = [r[3] for r in results]
    print(f"  有 1/3 本徵值: {sum(has)}/{len(has)} = {sum(has)/len(has)*100:.0f}%")
    near = [r[2] for r in results]
    print(f"  Block0 近1/3 數量: mean = {np.mean(near):.1f}/12")
    near_all = [r[4] for r in results]
    print(f"  全譜近1/3: mean = {np.mean(near_all):.1f}/32")

# 隨機對照: 隨機 32×32 矩陣嘅 1/3 命中率
print(f"\n[對照] 隨機 32×32 矩陣 (symmetric):")
rng = np.random.default_rng(5)
rand_near = []
for _ in range(100):
    M = rng.normal(0, 10, (32, 32))
    M = (M + M.T) / 2
    ev = np.linalg.eigvalsh(M)
    rand_near.append(sum(1 for e in ev if abs(e - round(e*3)/3) < 0.05))
rand_near = np.array(rand_near)
print(f"  隨機近1/3: mean = {rand_near.mean():.1f}/32 ({rand_near.mean()/32*100:.1f}%)")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)