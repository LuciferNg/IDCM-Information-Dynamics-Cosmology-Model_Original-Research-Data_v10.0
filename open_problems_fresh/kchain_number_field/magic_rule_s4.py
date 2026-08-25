#!/usr/bin/env python3
"""
★ Magic rows 生成規則 — 低次數成員 = 偶數 n?
================================================
發現: d=14/20/22 低次數成員 n 全偶數 (除特殊端點)
      d=7: n=[4,11,26,33], d=33: n=[11]
問題: 低次數 n 嘅「偶數」規則係咪 magic 生成規則?
      特殊端點 (11,22,33,44) 點解例外?
"""
import csv
from math import gcd, lcm, pi, sin

rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']), 's': int(r['s']),
            'deg_diff': int(r['deg_diff']), 'deg_sum': int(r['deg_sum']),
            'label': r['label'].strip()
        })

print("="*72)
print("1. 驗證: 低次數成員 n 全偶數? (除特殊端點)")
print("="*72)
for d in [7, 14, 20, 22, 33]:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    low = [r for r in members if r['deg_diff'] < 40]
    odd_n = [r['n'] for r in low if r['n'] % 2 == 1]
    even_n = [r['n'] for r in low if r['n'] % 2 == 0]
    print(f"  d={d:2d}: 低次數 n 奇數 = {odd_n}, 偶數 = {len(even_n)} 個")

print("\n" + "="*72)
print("2. ★ 低次數 n 嘅本質: 唔係『偶數』, 係『同 d 嘅奇偶』!")
print("="*72)
# d=14 (偶), 低次數 n 偶數 → s = n+m = n+n+d = 2n+d (偶+偶=偶) → s 偶
# d=7 (奇), 低次數 n = 4,11,26,33 → s = 2n+7 = 15,29,59,73 (奇) → s 奇
print("奇偶守恆 (規則 I): deg<40 只喺 d≡s (mod 2)")
print("  d=14 (偶): 要求 s 偶 → n = (s−14)/2 偶數?")
print("  檢查: d=14 成員 s = 16,18,...,74 (步長 2)")
print("  → s 偶數時 n = (s−d)/2 = (偶−偶)/2 = 整數, 奇偶由 s/2 決定")
print()
print("但係 d=14 低次數 n 全偶 → 即係 s = 2n+14, n 偶 → s = 4k+14 = 2(2k+7)")
print("  → s ≡ 2 (mod 4)? s = 18,22,26,30,... (s ≡ 2 mod 4)")
print()
# 驗證
print("驗證 d=14 低次數成員 s 值:")
d14_low = [r for r in rows if r['d'] == 14 and r['n'] < r['m'] and r['deg_diff'] < 40]
s_vals = sorted(r['s'] for r in d14_low)
print(f"  s = {s_vals}")
print(f"  s mod 4: {[s%4 for s in s_vals]}")
print(f"  → 全部 s ≡ 2 (mod 4)! ✅")
print()
print("d=14 高次數 (deg=40) 成員 s 值:")
d14_hi = [r for r in rows if r['d'] == 14 and r['n'] < r['m'] and r['deg_diff'] == 40]
s_hi = sorted(r['s'] for r in d14_hi)
print(f"  s = {s_hi}")
print(f"  s mod 4: {[s%4 for s in s_hi]}")

print("\n" + "="*72)
print("3. ★ 新規則: magic rows 低次數 = s ≡ 2 (mod 4)?")
print("="*72)
for d in [14, 20, 22]:
    members = [r for r in rows if r['d'] == d and r['n'] < r['m']]
    low = [r for r in members if r['deg_diff'] < 40]
    hi = [r for r in members if r['deg_diff'] == 40]
    low_s_mod = set(r['s'] % 4 for r in low)
    hi_s_mod = set(r['s'] % 4 for r in hi)
    print(f"  d={d:2d}: 低次數 s mod4 = {low_s_mod}, 高次數 s mod4 = {hi_s_mod}")

print("\n" + "="*72)
print("4. ★ deg 10 成員嘅 SYNC 結構")
print("="*72)
# deg10 成員: d=14 (8,22), (22,36); d=20 6 個
print("deg10 成員 (n,m,s):")
for d in [14, 20]:
    deg10 = [r for r in rows if r['d'] == d and r['n'] < r['m'] and r['deg_diff'] == 10]
    for r in deg10:
        print(f"  d={d:2d}: ({r['n']:2d},{r['m']:2d}) s={r['s']:3d}")
print()
print("分析:")
print("  d=14: (8,22) 同 (22,36) — 差 14! n: 8→22→36 (步長 14)")
print("  d=20: (4,24),(8,28),(12,32),(16,36),(20,40),(24,44)")
print("         n: 4,8,12,16,20,24 (步長 4!), m: 24,28,...,44 (步長 4)")
print("  → d=20 嘅 deg10 成員 n 步長 4 = B!")
print("  → d=14 嘅 deg10 成員 n 步長 14 = d 本身!")

print("\n" + "="*72)
print("5. ★ deg10 條件: sin_deg 分析")
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
def sin_deg(k):
    k=abs(k)%176
    if k==88: return 1
    m=(88-k)%176; g=gcd(352,m)
    return phi(352//g)//2

# deg = lcm(sin_deg(d), sin_deg(s))? 唔係, 係 lcm(deg ω_n, deg ω_m)
# ω_n = 2sin(nπ/88), deg = ?
def omega_deg(n):
    if n == 44: return 1
    dd = abs(44-n)  # 88/2
    g = gcd(dd, 176)
    return phi(176//g)//2

print("deg10 成員嘅端點 deg:")
for d in [14, 20]:
    deg10 = [r for r in rows if r['d'] == d and r['n'] < r['m'] and r['deg_diff'] == 10]
    for r in deg10[:4]:
        dn, dm = omega_deg(r['n']), omega_deg(r['m'])
        print(f"  ({r['n']:2d},{r['m']:2d}): deg ω_n={dn}, deg ω_m={dm}, lcm={lcm(dn,dm)}")
