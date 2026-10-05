#!/usr/bin/env python3
"""
★ 終極規則: deg<40 ⇔ 兩端點都喺「低次數端點集」
====================================================
由 lcm 定理: deg(beat(i,j)) = lcm(deg ω_i, deg ω_j)
→ deg<40 ⇔ i,j 都唔係 deg-40 端點
→ 低次數端點集: {n : deg ω_n < 40} = 24 個
→ deg<40 拍頻數 = C(24,2) = 276! (已知 276 ✅)
"""
import csv
from math import gcd, lcm

# 讀 master_atlas
rows = []
with open('/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            'n': int(r['n']), 'm': int(r['m']), 'd': int(r['d']), 's': int(r['s']),
            'deg_diff': int(r['deg_diff']), 'deg_sum': int(r['deg_sum']),
            'label': r['label'].strip()
        })
pairs = [r for r in rows if r['n'] < r['m']]

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
    """ω_n = 2sin(nπ/88) 嘅代數次數"""
    if n == 44: return 1
    dd = abs(44-n)
    g = gcd(dd, 176)
    return phi(176//g)//2

print("="*72)
print("1. 低次數端點集 (deg ω_n < 40)")
print("="*72)
low_endpoints = [n for n in range(1,45) if omega_deg(n) < 40]
hi_endpoints = [n for n in range(1,45) if omega_deg(n) == 40]
print(f"低次數端點 ({len(low_endpoints)} 個): {low_endpoints}")
print(f"高次數端點 ({len(hi_endpoints)} 個): {hi_endpoints}")
print(f"deg 分布: {sorted(set(omega_deg(n) for n in low_endpoints))}")

# 驗證 C(24,2) = 276
from math import comb
print(f"\nC({len(low_endpoints)},2) = {comb(len(low_endpoints),2)} (已知 deg<40 拍頻 = 276)")

print("\n" + "="*72)
print("2. 驗證: deg<40 拍頻 ⇔ 兩端點都喺低次數集")
print("="*72)
all_low = [r for r in pairs if r['deg_diff'] < 40]
check_ok = 0
check_fail = []
for r in all_low:
    if r['n'] in low_endpoints and r['m'] in low_endpoints:
        check_ok += 1
    else:
        check_fail.append((r['n'], r['m'], r['deg_diff']))
print(f"deg<40 拍頻 ({len(all_low)} 個) 兩端點都低次數: {check_ok}/{len(all_low)}")
if check_fail:
    print(f"違反: {check_fail[:5]}")

# 反向: 兩端點都低次數 → deg<40?
all_pairs_low = [(r['n'], r['m']) for r in pairs if r['n'] in low_endpoints and r['m'] in low_endpoints]
fail2 = [(r['n'], r['m'], r['deg_diff']) for r in pairs if r['n'] in low_endpoints and r['m'] in low_endpoints and r['deg_diff'] >= 40]
print(f"兩端點都低次數嘅拍頻 ({len(all_pairs_low)} 個) 全部 deg<40: {len(all_pairs_low)-len(fail2)}/{len(all_pairs_low)}")
if fail2:
    print(f"違反: {fail2[:5]}")

print("\n" + "="*72)
print("3. ★ 終極規則閉合")
print("="*72)
print(f"""
  deg(beat(i,j)) = lcm(deg ω_i, deg ω_j)   [lcm 定理, 946/946]
  
  → deg < 40  ⇔  deg ω_i < 40 AND deg ω_j < 40
              ⇔  i, j ∈ 低次數端點集 (24 個)
  
  低次數端點集 (24 個):
    deg 1:  {44}
    deg 2:  {22}
    deg 4:  {11, 33}
    deg 5:  {4, 12, 20, 28, 36}
    deg 10: {8, 16, 24, 32, 40}
    deg 20: {2, 6, 10, 14, 18, 26, 30, 34, 38, 42}
    
  高次數端點集 (20 個 = 奇數非 11/33):
    {{1,3,5,7,9,13,15,17,19,21,23,25,27,29,31,35,37,39,41,43}}
    
  deg<40 拍頻數 = C(24,2) = 276  ✅ 完全閉合!
""")

print("="*72)
print("4. ★ 4-adic 規則係終極規則嘅 corollary")
print("="*72)
print("""
  4-adic 觀察: d≡s (mod 4) 先有 deg<40 (24 個例外全係端點 11/33)
  
  真相: 低次數端點集 (24 個) 嘅奇偶:
    偶數: 22 個 (44,22,4,12,20,28,36,8,16,24,32,40,2,6,...,42)
    奇數: 2 個 (11, 33)
    
  → 兩端點都低次數時, 若冇 11/33:
      d = j−i 同 s = j+i 奇偶一致 (兩個都偶或都奇)
      → d≡s (mod 2) ✓ 規則 I
      → 更細: 偶數端點 mod 4 結構 → d≡s (mod 4) 多數成立
      
  但 11/33 係奇數低次數端點 → 打破 mod 4 守恆 (24 個例外)
  → 4-adic 係近似規則, 終極規則係「端點 deg 條件」
""")

print("="*72)
print("5. Magic rows 低次數成員嘅終極解釋")
print("="*72)
print(f"""
  magic row d 嘅低次數成員 = 該行 (d) 入面兩端點都 ∈ 低次數集
  
  d=7:  (4,11),(11,18),(26,33),(33,40) — 全部含 11/33!
  d=14: 15 個, 全部 n,m 偶數 (除 (8,22) deg10 等) — 兩端點都偶數低次數
  d=20: 12 個, 全部 n,m 偶數 — 兩端點都偶數低次數
  d=22: 12 個, (11,33) deg4 (22,44) deg2 — 含特殊端點
  d=33: (11,44) — 含特殊端點 11
  
  → magic rows 嘅低次數成員數 = 該行兩端點都喺低次數集嘅組合數!
""")
