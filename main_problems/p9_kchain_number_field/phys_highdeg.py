#!/usr/bin/env python3
"""
開放問題 #2: 物理參數點解坐高次數行?
========================================
觀察: 6/9 物理格坐 gcd=1 (deg40) 行
      3 個低次數: c/s (deg10), u/d (deg20), m_c/m_b (deg20)
問題: 物理參數嘅「行選擇」有冇結構規則?
      高次數行 = 最大代數複雜度 → 編碼最大信息?
"""
import csv
from math import gcd

rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']),
                     's': int(r['s']), 'deg_diff': int(r['deg_diff']),
                     'label': r['label'].strip()})
pairs = [r for r in rows if r['n'] < r['m']]

phys = [(r['n'], r['m'], r['d'], r['s'], r['deg_diff'], r['label']) 
        for r in pairs if r['label'] and not r['label'].startswith('Row')]

print("="*72)
print("1. 物理參數嘅行 deg 同端點 deg")
print("="*72)
def phi(n):
    r=n; p=2
    while p*p<=n:
        if n%p==0:
            while n%p==0: n//=p
            r-=r//p
        p+=1
    if n>1: r-=r//n
    return r
def omega_deg(n):
    if n==44: return 1
    dd=abs(44-n); g=gcd(dd,176)
    return phi(176//g)//2

for n,m,d,s,deg,lbl in phys:
    dn, dm = omega_deg(n), omega_deg(m)
    dg = gcd(abs(44-d),176)
    print(f"  {lbl:25s} ({n:2d},{m:2d}) d={d:2d} (deg ω_d={omega_deg(d):2d}, gcd={dg:2d}) "
          f"端點 deg: ω_{n}={dn}, ω_{m}={dm}, lcm={deg}")

print("\n" + "="*72)
print("2. ★ 物理參數嘅『端點 deg 選擇』")
print("="*72)
print("""
  物理參數 = 9 格, 分佈:
  
  # 高次數 (deg40): 端點包含奇數非 11/33
  m_μ/m_τ  (1,18):  ω_1=40, ω_18=20  → lcm=40
  m_s/m_d  (1,22):  ω_1=40, ω_22=2   → lcm=40
  n/p      (7,20):  ω_7=40, ω_20=5   → lcm=40  (但有 label!)
  m_H/m_W (19,38):  ω_19=40, ω_38=20 → lcm=40
  m_W/m_Z (30,41):  ω_30=20, ω_41=40 → lcm=40
  t/b     (19,33):  ω_19=40, ω_33=4  → lcm=40
  
  # 低次數 (<40): 端點全低次數
  c/s      (8,22):  ω_8=10, ω_22=2   → lcm=10
  u/d     (10,24):  ω_10=20, ω_24=10 → lcm=20
  m_c/m_b (8,33):   ω_8=10, ω_33=4   → lcm=20
""")

print("\n" + "="*72)
print("3. ★ 觀察: 物理參數嘅端點組合")
print("="*72)
print("""
  高次數 (deg40) 嘅 6 個:
    全部包含至少一個 deg40 端點 (奇數非 11/33)
    m_μ/τ: ω_1=40   m_s/d: ω_1=40   n/p: ω_7=40
    m_H/W: ω_19=40  m_W/Z: ω_41=40  t/b: ω_19=40
  
  低次數 (deg<40) 嘅 3 個:
    全部端點都低次數
    c/s: ω_8=10, ω_22=2
    u/d: ω_10=20, ω_24=10
    m_c/b: ω_8=10, ω_33=4
    
  ★ 規則: 物理參數 = 一高一低端點組合?
    唔係: m_μ/τ (1,18) 係 40+20
    係: 高次數物理參數必定包含【奇數非 11/33】端點
        低次數物理參數全部端點喺低次數集
""")

print("\n" + "="*72)
print("4. 端點 deg 40 嘅分佈 (奇數非 11/33)")
print("="*72)
deg40 = [n for n in range(1,45) if omega_deg(n) == 40]
print(f"deg40 端點: {deg40} ({len(deg40)} 個)")
print(f"呢 20 個端點出現喺 {len([p for p in phys if omega_deg(p[0])==40 or omega_deg(p[1])==40])}/{len(phys)} 物理格")

print("\n" + "="*72)
print("5. ★ 結論: 物理參數偏好高次數行嘅原因")
print("="*72)
print("""
  ★ 誠實回答: 冇單一規則解釋「點解物理參數坐高次數行」
  
  部分原因:
  a) 高次數 (=40) 端點有 20 個, 係最大端點類別
     → 純組合概率: 隨機揀兩端點, 包含 deg40 概率 = 1-C(24,2)/C(44,2) = 1-276/946 = 70.8%
     → 6/9 = 66.7%, 接近期望值!
  
  b) 低次數物理參數 (c/s, u/d, m_c/b) 全部係 quark 相關
     → 3 quark 坐 d=14 (GEN 行), 天生低次數
     → 唔係「選擇低次數」, 而係「GEN 行係低次數」
  
  c) 物理參數嘅「行」由 O 系列公式決定, 唔係由 deg 選擇
     → deg 係結果唔係原因
""")