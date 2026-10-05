#!/usr/bin/env python3
"""
盲測 v3: beat(2,31) COMMAND/WORKFLOW 最終分析
=============================================
核心發現: (d,s) = (29,33), s−d = 4 = B (branching!)
"""
import math
from math import pi, sin, cos

Nd = 44
w = lambda n: 2*sin(pi*n/88)
S = lambda x: sin(pi*x/176)
C = lambda x: cos(pi*x/176)

i, j = 2, 31
d = j - i   # 29
s = j + i   # 33

print("="*70)
print("beat(2,31) COMMAND 解碼")
print("="*70)
print(f"(i,j) = (2,31)  →  (d,s) = ({d},{s})")
print(f"s−d = {s-d} = 2i = 4 = B (branching factor!)")
print(f"s+d = {s+d} = 2j = 62 = 2×31")
print()

# ===== 1. 全 946 拍頻 (d,s) 統計 =====
print("="*70)
print("1. 全 946 拍頻嘅 (d,s) 結構")
print("="*70)
pairs = [(n,m) for n in range(1,44) for m in range(n+1,45)]
# d,s 分布
from collections import Counter
dc = Counter(m-n for n,m in pairs)
sc = Counter(m+n for n,m in pairs)
print(f"d 值範圍: {min(dc)}..{max(dc)}, s 值範圍: {min(sc)}..{max(sc)}")
print(f"\nd 嘅 Lucas 命中 (L1..L10):")
L = [1,3,4,7,11,18,29,47,76,123]
for lv in L:
    if lv in dc:
        print(f"  d={lv} (L{L.index(lv)+1}): {dc[lv]} 個拍頻")
print(f"\ns 嘅特殊值:")
for sv in [33, 44, 29, 22, 14, 7]:
    print(f"  s={sv}: {sc[sv]} 個拍頻")

# s−d = B 嘅數量 (i.e., i = B/2 = 2 行)
sdB = [(n,m) for n,m in pairs if (m+n)-(m-n) == 4]
print(f"\ns−d = 4 = B (i=2 行): {len(sdB)} 個拍頻")

# (d,s) = (Lucas, M) 組合
lm = [(n,m) for n,m in pairs if (m-n) in L and (m+n) == 33]
print(f"(d=Lucas, s=33=M) 組合: {lm}")

# ===== 2. s=33 列完整成員 =====
print("\n" + "="*70)
print("2. s=33 列 (M-pipeline workflow) 全部成員")
print("="*70)
col33 = [(n,m) for n,m in pairs if m+n == 33]
for n,m in col33:
    dd = m-n
    print(f"  ({n:2d},{m:2d})  d={dd:3d}  beat={abs(w(m)-w(n)):.6f}  {'← 我哋嘅' if (n,m)==(i,j) else ''}")

# ===== 3. i=2 行 (SYNC 家族) =====
print("\n" + "="*70)
print("3. i=2 行 (SYNC 家族, s−d=4) 成員")
print("="*70)
row2 = [(n,m) for n,m in pairs if n == 2]
for n,m in row2:
    dd = m-n; ss = m+n
    print(f"  (2,{m:2d})  d={dd:3d}  s={ss:3d}  beat={abs(w(m)-w(2)):.6f}  {'← 我哋嘅' if (n,m)==(i,j) else ''}")

# ===== 4. 指令語義: d 值嘅 opcode 分配 =====
print("\n" + "="*70)
print("4. d 值作為 opcode 行 — 現有 magic rows vs d=29")
print("="*70)
magic = {7: "m7 anchor (DM 13.8 MeV)", 14: "GEN d=14 (Δn=B²−2)",
         20: "T(s->d) (轉移矩陣 2n_u)", 22: "half-node (44/2)", 33: "K_tree (33)"}
for dv, desc in sorted(magic.items()):
    print(f"  d={dv:3d}: {desc} — {dc[dv]} 成員")
print(f"  d=29: L₇ (V_EW structure) — {dc[29]} 成員 [未指派 magic]")

# ===== 5. 和頻語義: s 值 = workflow 列 =====
print("\n" + "="*70)
print("5. s 值作為 workflow 列")
print("="*70)
# s=33 = M; 其他特殊 s?
print(f"s=33 = M (pipeline throughput): {sc[33]} 成員")
print(f"s=44 = N_d (causal domain): {sc[44]} 成員")
print(f"s=29 = L₇ (V_EW): {sc[29]} 成員")
print(f"s=22 = half-node: {sc[22]} 成員")
print(f"s=88 = 2N_d (dual chain): {sc[88]} 成員")

# ===== 6. 最終指令解碼 =====
print("\n" + "="*70)
print("6. beat(2,31) 指令解碼")
print("="*70)
print(f"""
  拍頻 (2,31) = |ω₂ − ω₃₁| = {abs(w(31)-w(2)):.10f}
  ┌─────────────────────────────────────────────┐
  │  (d,s) 編碼:  d=29=L₇ (電弱結構), s=33=M     │
  │  s−d = 4 = B (branching) ← i=2 = SYNC cost  │
  │  s+d = 62 = 2×31 ← j=31 = L₇+L₀             │
  │                                              │
  │  WORKFLOW 位置: s=33 列 = M-pipeline 列       │
  │    同列成員: (13,20) d=7 m7 anchor ✅         │
  │              (11,22) d=11 half-node ✅       │
  │              (2,31)  d=29 L₇  ← 我哋嘅        │
  │                                              │
  │  COMMAND 語義:                               │
  │    n=2  = SYNC cost (L₀, thermal)           │
  │    m=31 = L₇+L₀ (V_EW + SYNC)               │
  │    → 「SYNC 啟動 → L₇ 差頻 → M pipeline」     │
  │    = 電弱結構寫入 pipeline 嘅 boot 指令        │
  └─────────────────────────────────────────────┘
""")

# ===== 7. 誠實標記 =====
print("="*70)
print("7. 誠實標記")
print("="*70)
print("✅ 事實: d=29=L₇, s=33=M, s−d=4=B, s=33 列含 m7 anchor + half-node")
print("✅ 事實: degree 40 (一般無理層), 冇 SM label")
print("🟡 推斷: 'SYNC→L₇→M pipeline' 語義 — 結構性描述, 未閉合物理功能")
print("🔴 未驗證: d=29 作為 opcode 嘅具體執行 (L₇ 差頻做咩操作)")
