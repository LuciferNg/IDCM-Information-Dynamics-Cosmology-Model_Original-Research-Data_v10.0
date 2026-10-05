#!/usr/bin/env python3
"""
方向評估: magic rows 喺邊集嘅切分角色 + 最終方向建議
=====================================================
問題: magic d 值 (7,14,20,22,33) 喺邊集有冇特別「切分」角色?
      即係: 由 k=1 到 k=d 嘅邊和, 有冇產生物理拍頻?
"""
from math import pi, sin
from collections import Counter

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))
e = [w(k+1)-w(k) for k in range(1,N)]
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

phys = {(10,24):"u/d", (8,22):"c/s", (19,33):"t/b", (8,33):"m_c/m_b",
        (1,22):"m_s/m_d", (30,41):"m_W/m_Z", (19,38):"m_H/m_W",
        (1,18):"m_mu/m_tau", (7,20):"n/p"}
phys_pairs = set(phys.keys())

print("="*72)
print("1. 邊集切分: 每條 magic d 值對應嘅邊和")
print("="*72)
magic = {7:"m7", 14:"GEN", 20:"T(s->d)", 22:"half", 33:"K_tree"}
for d in sorted(magic):
    # 由 k=1 到 k=d 嘅邊和 = beat(1, d+1)
    s = sum(e[:d])
    b = beat(1, d+1)
    print(f"  d={d:2d} ({magic[d]:8s}): 邊和 beat(1,{d+1}) = {s:.8f}")
    # 呢個係咪物理拍頻?
    phys_hit = [name for (i,j),name in phys.items() if (1,d+1)==(i,j) or (1,d+1)==(j,i)]
    print(f"      → beat(1,{d+1}) 物理身份: {phys_hit if phys_hit else '無'}")

print("\n" + "="*72)
print("2. 邊集切分: 每條 magic d 值對應嘅『物理拍頻數』")
print("="*72)
# 喺 d=7 行 (邊距 7), 有幾多物理?
for d in sorted(magic):
    members = [(i,j) for (i,j) in pairs if j-i == d]
    hits = [(i,j) for (i,j) in members if (i,j) in phys_pairs]
    print(f"  d={d:2d} ({magic[d]:8s}): {len(hits)} 個物理 {hits}")

print("\n" + "="*72)
print("3. ★ 最有力嘅下一步方向")
print("="*72)
print(f"""
  候選方向評估:

  1. 【微碼執行語義】(最有力)
     - 方向 A 已證: 13244/13244 路徑閉合
     - 拍頻 = 保守勢差 → workflow = path-independent
     - 下一步: 43 條邊做「基本操作」, 組合規則 = ?
     - 問題: 邊嘅「物理功能」係咩? 相鄰勢差 = ?

  2. 【magic rows 嘅生成規則】
     - 7,14,20,22,33 冇明顯 Lucas/Fib 生成
     - 但 14 = 2×7, 22 = 2×11 — SYNC 關係!
     - 下一步: 檢查 7→14→22→33 係咪「SYNC 鏈」
     - 問題: 20 點解插入? 

  3. 【世界/觀察者/邊集三鏈嘅執行】
     - 90/88/84 已閉合
     - 下一步: 84 核心嘅「執行」角色
     - 問題: 21 對 = ?

  4. 【物理參數嘅邊集位置】
     - 所有物理拍頻 = 邊嘅連續和 (平凡)
     - 但: 物理拍頻嘅「邊界」有冇特殊?
     - 例如: u/d = (10,24) = 邊 10..23
""")

print("="*72)
print("4. 物理拍頻嘅『邊界位置』分析")
print("="*72)
# 每個物理拍頻 (i,j) 對應邊 i..j-1
# 檢查: 起點 i 同終點 j 有冇 pattern?
starts = [i for (i,j) in phys_pairs]
ends = [j for (i,j) in phys_pairs]
print(f"物理拍頻起點 i: {sorted(starts)}")
print(f"物理拍頻終點 j: {sorted(ends)}")
print(f"起點 Lucas? {[i for i in sorted(starts) if i in [1,2,3,4,7,11,18,29]]}")
print(f"終點 Lucas? {[j for j in sorted(ends) if j in [1,2,3,4,7,11,18,29]]}")
print()
# d 值
ds = [j-i for (i,j) in phys_pairs]
print(f"物理 d 值: {sorted(ds)}")
print(f"d 值 Lucas? {[d for d in sorted(ds) if d in [1,2,3,4,7,11,18,29]]}")
print(f"  → {sorted(set(ds))}")
