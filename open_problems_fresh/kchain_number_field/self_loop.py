#!/usr/bin/env python3
"""
Self Loop 指令分析 — 44×44 全矩陣對角線 (i=i)
================================================
拍頻 = i<j (946 個, 差頻≠0)
Self loop = i=j (44 個, 差頻=0) — master_atlas 標記 "DIAG zero/self"
"""
import csv, math
from math import pi, sin, gcd, lcm

# ===== 讀 master_atlas =====
rows = list(csv.DictReader(open(
    '/home/wsl/Projects/IDCM/IDCM-v10.0/beat_periodic_table/data/master_atlas.csv')))

print("="*72)
print("1. Self Loop (DIAG zero/self) 全部 44 個")
print("="*72)
diag = [r for r in rows if r['n'] == r['m']]
print(f"對角線成員: {len(diag)} (n=m=1..44)")
print(f"{'n':>3} {'sum=2ω_n':>12} {'γ_n=4sin²':>12} {'deg_sum':>8} {'label':>16}")
for r in diag:
    n = int(r['n'])
    w = 2*sin(pi*n/88)
    g = 4*sin(pi*n/88)**2
    print(f"{n:>3} {2*w:>12.8f} {g:>12.8f} {r['deg_sum']:>8} {r['label']:>16}")

# ===== 2. 特殊 self loop =====
print("\n" + "="*72)
print("2. 特殊 self loop 成員")
print("="*72)
print("n=11:  4sin(11π/88) = 4sin(π/8) = 2√(2−√2)   [高對稱]")
print("n=22:  4sin(π/4) = 2√2                          [半節點]")
print("n=33:  4sin(3π/8) = 2√(2+√2)                    [高對稱]")
print("n=44:  4sin(π/2) = 4                            [Nyquist, 有理]")
print()
print("self loop sum = 4sin(nπ/88) = 2ω_n = 2√γ_n")
print("→ self loop 嘅和頻 = 端點能量 γ_n 嘅平方根 × 2")

# ===== 3. degree 分析 =====
print("\n" + "="*72)
print("3. Self loop degree (和頻次數)")
print("="*72)
from collections import Counter
dc = Counter(r['deg_sum'] for r in diag)
print(f"deg_sum 分布: {dict(sorted(dc.items(), key=lambda x:int(x[0])))}")
print()
print("對比: 946 拍頻 (i<j) 用 diff degree")
print("  deg<40 只喺偶區, 但 self loop 有 deg=2,4 等低次數")

# ===== 4. ISA 語義 =====
print("\n" + "="*72)
print("4. Self Loop 嘅 COMMAND/WORKFLOW 語義")
print("="*72)
print("""
  (i,i) 指令:
    d = 0   → 差頻 = 0 = 零操作 (NOP/IDLE?)
    s = 2i  → 和頻 = 2ω_i = 自耦合能量
    → 「對自己運算」= self loop

  ISA 對應:
    Runtime ISA 有 IDL (IDLE) 指令 — 空轉 N ticks
    Boot ISA 有 STORE — 寫返自己?
    SYNC = DUP+ADD — 自己加自己 = 2ω_i = self loop 嘅和頻!
    
  ★ 關鍵: self loop sum = 2ω_i = SYNC(ω_i)
    — 即係 self loop 就係 SYNC 指令作用喺單一模式!
""")

# ===== 5. 驗證: self loop sum = SYNC(ω) = 2ω = DUP+ADD =====
print("="*72)
print("5. 驗證: self loop = SYNC 指令 (DUP+ADD)")
print("="*72)
for n in [1, 2, 11, 22, 33, 44]:
    w = 2*sin(pi*n/88)
    print(f"  n={n:2d}: ω_n={w:.8f}, SYNC(ω_n)=2ω_n={2*w:.8f}, deg_sum={[r['deg_sum'] for r in diag if int(r['n'])==n][0]}")

# ===== 6. 統計: self loop vs 全表 =====
print("\n" + "="*72)
print("6. 統計位置")
print("="*72)
print(f"44×44 = 1936 格")
print(f"  self loop (對角線): 44 格 (2.3%)")
print(f"  差頻拍頻 (i≠j):    1892 格 (97.7%) — 但 946 係唯一 pair (上下三角對稱)")
print(f"  上三角 (i<j):       946 格")
print(f"  下三角 (i>j):       946 格 (CPT 反物質對偶, 負差頻)")
