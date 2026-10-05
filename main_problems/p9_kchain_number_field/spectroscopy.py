#!/usr/bin/env python3
"""
指令空間譜學 (Instruction Space Spectroscopy)
=============================================
946 拍頻嘅 (d,s,degree) 完整地圖 — microcode 挖掘第一步
目標:
  1. 43 條 d 行嘅代數次數分布 → 搵高對稱行 (低次數 = 高優先級?)
  2. magic rows (7,14,20,22,33) 有冇特殊次數特徵?
  3. d,s 奇偶性 × degree 關聯 → 指令語法規則?
  4. 物理參數喺次數地圖嘅位置
"""
from math import gcd, lcm, pi, sin
from collections import Counter, defaultdict

# ===== degree 函數 (master_atlas 方法) =====
def phi(n):
    r = n; p = 2
    while p*p <= n:
        if n % p == 0:
            while n % p == 0: n //= p
            r -= r // p
        p += 1
    if n > 1: r -= r // n
    return r

def sin_deg(k):
    k = abs(k) % 176
    if k == 88: return 1
    m = (88 - k) % 176
    g = gcd(352, m)
    return phi(352 // g) // 2

def beat_degree(d, s):
    k1 = abs(d+s) % 352; k2 = abs(d-s) % 352
    return lcm(sin_deg(k1), sin_deg(k2))

pairs = [(i,j) for i in range(1,44) for j in range(i+1,45)]
assert len(pairs) == 946

data = []
for (i,j) in pairs:
    d = j-i; s = j+i
    data.append((i,j,d,s,beat_degree(d,s)))

magic = {7:"m7", 14:"GEN", 20:"T(s->d)", 22:"half", 33:"K_tree"}
phys = {
    (10,24): "u/d", (8,22): "c/s", (19,33): "t/b",
    (8,33): "m_c/m_b", (1,22): "m_s/m_d", (30,41): "m_W/m_Z",
    (19,38): "m_H/m_W", (1,18): "m_mu/m_tau", (7,20): "n/p",
}

print("="*72)
print("1. 43 條 d 行嘅次數分布 (★=magic row)")
print("="*72)
d_rows = defaultdict(list)
for (i,j,d,s,deg) in data:
    d_rows[d].append(deg)
for d in sorted(d_rows):
    c = Counter(d_rows[d])
    degs_str = ",".join(f"{k}×{v}" for k,v in sorted(c.items()))
    star = " ★" if d in magic else ""
    print(f"  d={d:2d}: {len(d_rows[d]):2d}成員  [{degs_str}]{star}")

print("\n" + "="*72)
print("2. 次數層統計 (全 946)")
print("="*72)
all_deg = Counter(deg for (_,_,_,_,deg) in data)
for k in sorted(all_deg):
    print(f"  degree {k:2d}: {all_deg[k]:3d} 拍頻 ({all_deg[k]/9.46:.1f}%)")

print("\n" + "="*72)
print("3. d,s 奇偶性 × degree 關聯")
print("="*72)
for dp in ['奇','偶']:
    for sp in ['奇','偶']:
        sub = [deg for (i,j,d,s,deg) in data
               if (d%2==1)==(dp=='奇') and (s%2==1)==(sp=='奇')]
        c = Counter(sub)
        print(f"  d{dp} s{sp}: {len(sub):3d} 成員  deg分布 {dict(sorted(c.items()))}")

print("\n" + "="*72)
print("4. magic rows 次數特徵 vs 全表")
print("="*72)
for d in sorted(magic):
    c = Counter(d_rows[d])
    print(f"  d={d:2d} ({magic[d]:8s}): {dict(sorted(c.items()))}")
print("\n  全表次數分布: ", dict(sorted(all_deg.items())))

print("\n" + "="*72)
print("5. 物理參數喺次數地圖嘅位置")
print("="*72)
for (i,j),name in phys.items():
    d = j-i; s = j+i
    deg = beat_degree(d,s)
    dpar = "偶" if d%2==0 else "奇"
    spar = "偶" if s%2==0 else "奇"
    print(f"  {name:10s} ({i:2d},{j:2d}) d={d:2d}({dpar}) s={s:3d}({spar}) deg={deg}")

print("\n" + "="*72)
print("6. d 行次數一致性: 每條行內部 deg 有幾多種?")
print("="*72)
uniq = {d: len(set(d_rows[d])) for d in d_rows}
for d in sorted(uniq):
    star = " ★" if d in magic else ""
    if uniq[d] <= 2:
        print(f"  d={d:2d}: {uniq[d]} 種次數  [{','.join(str(x) for x in sorted(set(d_rows[d])))}]{star}")
