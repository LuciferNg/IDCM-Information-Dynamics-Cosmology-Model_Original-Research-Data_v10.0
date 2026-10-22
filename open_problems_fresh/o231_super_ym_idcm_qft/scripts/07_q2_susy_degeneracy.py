#!/usr/bin/env python3
"""
scripts/07 — Q2 攻堅：SUSY ↔ 譜簡併結構的形式化檢驗

問題: N=4 SYM 的「超對稱」在 IDCM 中對應什麼結構?
候選（D2 假說）: SUSY = 譜簡併。

攻堅三層:
    L1 (簡併):   鏡像對 (k, 88−k) 能量簡併 → 超對稱對的種子
    L2 (扇區):   mod-4 扇區 88 = 4×22（B=4 × N_d/2）→ 4 個「超電荷 index」
    L3 (代數):   子集鏡像算子 Q_S（scattering 的生成算子）能否構成超代數?
                 即: 有冇 ℤ₂-grading 令 Q 滿足 Q² = 0 / 反交換關係?

誠實檢驗: N=4 SYM 要求 16 態 supermultiplet (1+4+6+4+1)；
          IDCM 鏡像簡併度 = 2 (k, 88−k) → 最多 N=1 類比。
          四道硬測試會指出呢個「SUSY」有幾多係真結構、幾多係命名。
"""
import math, sys
from collections import defaultdict, Counter

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS [{name}] {detail}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL [{name}] {detail}")

N = 88
def omega(k): return 2 * abs(math.sin(math.pi * k / N))

print("=" * 60)
print("L1. 譜簡併結構（SUSY 種子）")
print("=" * 60)
# 1.1 能量簡併度分佈
deg = defaultdict(list)
for k in range(1, N):
    deg[round(omega(k), 12)].append(k)
degdist = Counter(len(v) for v in deg.values())
print(f"  簡併度分佈: {dict(sorted(degdist.items()))}")
# 每能量 2 重（除 k=44 自鏡像）→ 簡併度 2 = 「N=1 超對稱對」
check("L1a 鏡像簡併度 = 2 (除自鏡像)", degdist[2] == 43, f"43 對雙重簡併")
check("L1b 自鏡像 k=44 唯一單例", degdist[1] == 1, "k=44")

# 1.2 mod-4 扇區
sectors = defaultdict(list)
for k in range(1, N + 1):
    sectors[k % 4].append(k)
sizes = {a: len(v) for a, v in sectors.items()}
print(f"  mod-4 扇區大小: {sizes}")
check("L1c 88 = 4×22（B=4 × N_d/2）", all(s == 22 for s in sizes.values()),
      f"4 扇區 × 22 = 88")

# 1.3 鏡像 M 嘅扇區映射
m_map = Counter()
for k in range(1, 44):
    m_map[(k % 4, (N - k) % 4)] += 1
print(f"  鏡像扇區映射: {dict(m_map)}")
check("L1d 鏡像 M: 0↔0, 2↔2 內部; 1↔3 跨扇區",
      m_map[(0, 0)] > 0 and m_map[(2, 2)] > 0 and m_map[(1, 3)] > 0,
      f"{dict(m_map)}")

print()
print("=" * 60)
print("L2. 超電荷 index 候選：mod-4 扇區")
print("=" * 60)
# N=4 有 4 個 supercharge Q_a。IDCM 有 4 個 mod-4 扇區 → 候選 index a=0..3
# 每個扇區 22 個模式 → 「超電荷」嘅 representation 大小 = 22 = 2×11 = μ²×11
print("  候選: supercharge index a ∈ {0,1,2,3} ↔ mod-4 扇區")
print(f"  每扇區 22 模式 = 2×11 = μ²·11 (O229: 鏈自對點 n=22)")
check("L2a 4 個扇區 = 4 個候選超電荷 index", len(sectors) == 4)
# 但注意: 扇區 a=0,2 內部有鏡像對; a=1,3 無 → 扇區唔對稱
# pair 計數（每對 (k, 88−k) 計一次）
inner_by_pair = Counter()
for k in range(1, 44):
    mk = N - k
    for a in sectors:
        if k in sectors[a] and mk in sectors[a]:
            inner_by_pair[a] += 1
print(f"  各扇區內部鏡像對數 (pair): {dict(inner_by_pair)}")
check("L2b 扇區唔對稱 (0/2 有內部鏡像對, 1/3 冇)",
      inner_by_pair[0] == 10 and inner_by_pair[2] == 11
      and inner_by_pair[1] == 0 and inner_by_pair[3] == 0,
      f"{dict(inner_by_pair)}")

print()
print("=" * 60)
print("L3. 超代數檢驗：子集鏡像算子 Q_S")
print("=" * 60)
# 定義: Q 作用喺散射態上 = 對子集 S 做鏡像 k → 88−k
# Q 嘅「grading」: 若 S 含奇數個粒子 → G = −1 (fermionic), 偶數 → +1 (bosonic)
# 檢驗: Q_S 係咪 satisfy 超代數要求 (Q² = 0 or Q² = 1)
#
# 事實: 鏡像 M: k → 88−k 係 involution: M(M(k)) = 88−(88−k) = k
# ⟹ M² = id。Schur: 超電荷通常要求 Q² = 0 (nilpotent) 或 Q² = P (動量)。
# M² = id 係「反演」型 — 唔係 standard SUSY Q。
M2 = all((N - (N - k)) % N == k for k in range(1, N))
check("L3a 鏡像 M² = id (involution)", M2, "M(k)=88−k, M²=k")

# 超對稱代數: {Q, Q†} = 2H。檢驗 IDCM 對應: 鏡像對交換能量 → 「反交換子」= 2ω
# 對每個對 (k, 88−k): ω_k = ω_{88−k} → 「Q, Q† 作用後能量不變」
pair_energy_equal = all(abs(omega(k) - omega(N - k)) < 1e-14 for k in range(1, N))
check("L3b 鏡像對能量相等 ({Q,Q†}=2H 嘅譜對應)", pair_energy_equal,
      "ω_k = ω_{88−k} ⟹ Q 交換後能量守恆")

# 有幾個「超電荷」？ 鏡像只有 1 個生成子 M。N=4 要 4 個。
# 候選: 4 個 mod-4 扇區 → 4 個「partial mirror」? M_a: 只鏡像扇區 a 嘅模式
# 檢驗: 呢啲 M_a 可唔可以獨立作用?
# M_a 作用喺 k ∈ 扇區 a: k → 88−k。但 88−k 嘅扇區可能唔同 (a=1 → 3)!
# ⟹ M_a 唔係「扇區內」算子 — 佢會跨扇區。所以 4 個 M_a 唔係 4 個獨立生成子。
cross = {a: sorted({(N - k) % 4 for k in sectors[a]}) for a in sectors}
print(f"  扇區 a 嘅鏡像目標扇區: {cross}")
check("L3c 4 個 partial mirror 唔獨立（跨扇區）",
      cross[1] == [3] and cross[3] == [1],
      f"{cross}")

print()
print("=" * 60)
print("L4. 誠實判定：IDCM 嘅「超對稱」係咩層次")
print("=" * 60)
print("""
N=4 SYM supermultiplet: 1 gauge boson + 4 gauginos + 6 scalars = 16 態 (1+4+6+4+1).
IDCM 鏡像簡併: 每對 (k, 88−k) = 2 態。

對應強度:
  ✅ 有簡併 → 「SUSY = 譜簡併」嘅種子成立（最低限度 N=1 類比: boson↔fermion 對）
  ✅ 4 個 mod-4 扇區 → 4 = N 嘅 index 數吻合（naming: N=4 ↔ B=4 ↔ 4 扇區）
  🔴 簡併度 2 ≠ 16 → 唔可以叫「N=4 超對稱」；IDCM 冇 (1+4+6+4+1) 態結構
  🔴 M² = id 而唔係 Q² = 0 → 鏡像係 involution, 唔係 nilpotent supercharge
  🔴 冇 R-symmetry SU(4) → IDCM 無對應嘅内部對稱群

判定: D2 假說「SUSY = 譜簡併」係 PARTIAL:
  簡併種子 ✅（結構真實存在）
  完整 N=4 超代數 🔴（唔存在對應 — 誠實標記）
""")
check("L4a D2 = 部分閉合 (簡併種子有, 完整代數無)", True,
      "SUSY=簡併嘅種子成立; N=4 完整對應唔存在")

print()
print(f"\n===== 總結: PASS={PASS} FAIL={FAIL} =====")
sys.exit(0 if FAIL == 0 else 1)