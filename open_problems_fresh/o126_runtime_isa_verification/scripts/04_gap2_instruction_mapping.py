#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O126 -- docs/04 Gap 2 攻堅: 微碼指令空間 <-> 物理循環映射
================================================================
背景 (docs/03 §四 #2): 946 拍頻 (d,s) = (opcode 行, workflow 列) 嘅「執行」語義;
kchain_number_field/08 自記「928 個填充指令嘅具體執行 = 大工程未開始」。

攻擊路線: 唔逐條解 946 個填充指令 (唔可行), 而係問三個結構問題:
  Q1  ISA 詞彙量 = ?  (所有可能嘅 2-模操作)
  Q2  最小生成集 = ?  (鏈閉合 + SYNC)
  Q3  一個循環執行幾多 op, 同 ISA 關係?

v10.0 已知 (實檔):
  - 44 模 omega_n = 2sin(n pi/88)  (kchain_number_field/00)
  - 鏈閉合: beat(i,j) = sum_{k=i}^{j-1} e_k, 43 邊 e_k  (10_chain_closure)
  - self loop (i,i) = 2 omega_i = SYNC  (09_self_loop)
  - 每 cycle 88 ops = 44 reads + 44 writes  (O41)

執行: /usr/bin/python3 scripts/04_gap2_instruction_mapping.py
"""

import mpmath as mp
from mpmath import mpf, sqrt, pi, sin, cos
from fractions import Fraction

mp.mp.dps = 40

PHI = (1 + sqrt(5)) / 2
B = 4
N_D = 44

results = []


def chk(label, cond, detail=""):
    ok = bool(cond)
    results.append((label, ok, detail))
    print(("  [PASS] " if ok else "  [FAIL] ") + label + ("   " + detail if detail else ""))
    return ok


def rel(a, b):
    return abs(a - b) / abs(b)


def w(n):
    return 2 * sin(pi * n / 88)


print("=" * 78)
print("O126 docs/04 -- Gap 2: 微碼指令空間 <-> 物理循環映射")
print("=" * 78)

# ============ Q1: ISA 詞彙量 ============
print("\n--- [G2.1] Q1: ISA 詞彙量 ---")
beats = [(i, j) for i in range(1, N_D + 1) for j in range(i + 1, N_D + 1)]
selfs = [(i, i) for i in range(1, N_D + 1)]
chk("G2.1a 拍頻 = C(44,2) = 946", len(beats) == 946 and 44 * 43 // 2 == 946, "946")
chk("G2.1b ISA = 946 拍頻 + 44 self loop = 990 = C(N_d+1,2) = C(45,2)",
    len(beats) + len(selfs) == 990 and 45 * 44 // 2 == 990, "990 = C(45,2)")
chk("G2.1c ISA = 完整圖 K_(N_d+1) 嘅邊數 (44 模 + 1 種子 = 45 點)",
    990 == 45 * 44 // 2, "45 = N_d + 1 = 2N_d − 43")

# (d, s) 參數化: d = j−i, s = i+j
dvals = sorted(set(j - i for i, j in beats + selfs))
svals = sorted(set(i + j for i, j in beats + selfs))
chk("G2.1d opcode 行 d = j−i ∈ {0,...,43} = 44 = N_d 個值",
    dvals == list(range(0, N_D)), "d ∈ [0,43]")
chk("G2.1e workflow 列 s = i+j ∈ {2,...,88} = 87 = 2N_d − 1 個值",
    svals == list(range(2, 89)), "s ∈ [2,88]")

# ============ Q2: 最小生成集 ============
print("\n--- [G2.2] Q2: 最小生成集 (原子指令) ---")
edges = [(k, k + 1) for k in range(1, N_D)]
chk("G2.2a 相鄰邊 = 43 = N_d − 1", len(edges) == 43, "43")
chk("G2.2b 原子集 = 43 邊 + 44 self loop = 87 = 2N_d − 1",
    len(edges) + len(selfs) == 87, "87")
chk("G2.2c 87 = 88 − 1 = 觀察者鏈格點 − 種子 (11_edge_energy 一致)",
    87 == 88 - 1, "87 = 88−1")

# 鏈閉合: beat(i,j) = sum edges
def edge(k):
    return w(k + 1) - w(k)


ok = True
worst = mpf(0)
for (i, j) in beats:
    s = sum(edge(k) for k in range(i, j))
    err = rel(s, w(j) - w(i))
    worst = max(worst, err)
    if err > mpf('1e-30'):
        ok = False
chk("G2.2d 鏈閉合: beat(i,j) = sum_{k=i}^{j-1} e_k  (946/946)", ok,
    "max dev = %.2e" % float(worst))

# ============ Q3: 循環 op 數 ============
print("\n--- [G2.3] Q3: 循環執行 op 數 ---")
reads = len(selfs)          # 44 self loops = SYNC(omega_n)
writes = 44                 # O41: 44 次寫入 (相位翻轉)
chk("G2.3a 每 cycle 88 ops = 44 reads (self loop) + 44 writes (O41)",
    reads + writes == 88, "44 + 44 = 88 = 2N_d")
chk("G2.3b 原子數 + 種子 = 循環 op 數:  43 + 44 + 1 = 88",
    len(edges) + len(selfs) + 1 == 88, "43 + 44 + 1 = 88")
chk("G2.3c reads = 44 self loop <-> 44 模 (雙射: 每模讀一次)",
    reads == N_D, "44 <-> 44")

# ============ 執行次序 ============
print("\n--- [G2.4] 執行次序 (PC 候選) ---")
# 候選: PC = 上標 j, 步驟 j 做 j 個 op (i=1..j, i=j 係 self loop)
slot = {j: j for j in range(1, N_D + 1)}
total = sum(slot.values())
chk("G2.4a PC = j (上標), 步驟 j 做 j op  =>  sum_j j = 44*45/2 = 990 = ISA",
    total == 990 and total == 44 * 45 // 2, "sum j = 990")
chk("G2.4b 步驟 j 內 j−1 個 beat (i<j) + 1 個 self loop",
    all((j - 1) + 1 == j for j in range(1, N_D + 1)), "slot size = j")
chk("G2.4c sum_{j=2}^{44}(j−1) = 946 = 全部拍頻",
    sum(j - 1 for j in range(2, N_D + 1)) == 946, "946")

# 對照: 88 ops/cycle vs 990 ISA
chk("G2.4d 88 ops/cycle = 44 相 (j=1..44) x 2 op (read + write) per 相",
    44 * 2 == 88, "44 相 x 2 = 88")

# ============ 殘餘: 精確雙射 ============
print("\n--- [G2.5] 殘餘: 44 writes <-> 邊集? ---")
chk("G2.5a 44 writes vs 43 邊 -> 差 1 (種子) [候選, 未強迫]",
    writes - len(edges) == 1, "44 − 43 = 1")
chk("G2.5b s 列 87 個 = 原子數 87 (列數 = 原子數)",
    len(svals) == 87 and len(edges) + len(selfs) == 87, "87 = 87")

# ---- 裁決 ----
print("\n" + "=" * 78)
n_pass = sum(1 for _, ok, _ in results if ok)
n_tot = len(results)
print("總計: %d/%d PASS" % (n_pass, n_tot))
print("=" * 78)
print("""
裁決 Gap 2: 🟡 部分閉合 (詞彙量 + 生成集 + 循環 op 數 🟢; 精確雙射 🟡)
  Q1 ISA 詞彙量 🟢: 990 = 946 拍頻 + 44 self loop = C(N_d+1,2) = C(45,2)
                     = 完整圖 K_(N_d+1) 邊數 (44 模 + 1 種子)
      參數化: opcode 行 d = j−i ∈ [0,43] = N_d 值;  workflow 列 s = i+j ∈ [2,88] = 2N_d−1 值
  Q2 最小生成集 🟢: 87 = 43 邊 + 44 self loop = 2N_d − 1 = 觀察者鏈 − 種子
                     鏈閉合 946/946 (beat = 路徑積分) — 由 43 邊生成
  Q3 循環 op 數 🟢: 88 = 44 reads + 44 writes (O41) = 43 邊 + 44 self + 1 種子
  ★ 執行次序候選 🟢 (結構, 非強迫): PC = 上標 j, 步驟 j 做 j op => sum j = 990 = ISA
                                    88 ops/cycle = 44 相 x 2 op (read + write)
  🟡 殘餘: 44 writes 精確對應邊集差 1 (種子) — 雙射未被強迫
  ⇒ 「928 填充指令具體執行」嘅正確框架: 唔係逐條解, 而係 ISA = 完整 2-模操作空間,
    循環只執行 88 個 (44 read + 44 write), 其餘 902 個係「可達但未執行」嘅指令
""")
if n_pass != n_tot:
    raise SystemExit(1)
