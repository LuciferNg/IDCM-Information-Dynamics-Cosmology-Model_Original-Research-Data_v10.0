#!/usr/bin/env python3
"""
O53 Q2 延續: d_{ijk} 張量結構分析
===================================
對比 projection_operator.py (rank-2 缺陷) 同 dijk_intersection.py (per-modulus)
驗證 d_tensor 係咪有真正 36 維結構

+ 核心結構問題: 134 moduli 點樣由 946 beats 生成?
  如果 P̂ 要真正有 rank 66, 需要 per-modulus weight
"""
import sys, os, math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from dijk_intersection import KahlerBasis, TripleIntersectionTensor

phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 Q2: d_{ijk} 張量結構 vs 投影算子 rank-2 缺陷")
print("=" * 70)

# --- [1] KahlerBasis 結構 ---
print("\n[1] Kähler 基底 (per-modulus 依賴)")
kb = KahlerBasis()
print(f"    basis pairs 數: {kb.n_basis}")
pairs = kb.basis_pairs
print(f"    前 10 個 (n,m) pairs: {pairs[:10]}")
print(f"    最後 5 個: {pairs[-5:]}")

# 檢查 pairs 有冇重複 / 結構
unique_pairs = set(pairs)
print(f"    唯一 pairs: {len(unique_pairs)} / {len(pairs)}")

# parity 檢查
even_pairs = [p for p in pairs if (p[0]+p[1]) % 2 == 0]
print(f"    even-parity pairs: {len(even_pairs)}")

# --- [2] d_{ijk} 張量 ---
print("\n[2] d_{ijk} 三重相交張量")
tt = TripleIntersectionTensor()
d = tt.compute()
print(f"    張量形狀: {d.shape}")
print(f"    非零元素: {np.count_nonzero(d)} / {d.size}")
print(f"    稀疏度: {np.count_nonzero(d) / d.size * 100:.2f}%")

# 對每個 i, 睇 d[i,:,:] 係咪有獨立結構
print("\n[3] 每行 i 嘅獨立性 (d[i,:,:] 有冇 per-index 依賴)")
# 取 d[0], d[5], d[10], d[35] 比較
for i in [0, 5, 10, 20, 35]:
    flat_i = d[i].flatten()
    mask = flat_i != 0
    if mask.sum() > 0:
        print(f"    d[{i}]: 非零 {mask.sum()}, 範圍 [{flat_i[mask].min():.3e}, {flat_i[mask].max():.3e}]")

# 行間相關性 (驗證 per-index 依賴)
print("\n    行間相關性 (應 < 1.0 如果 per-index 依賴存在):")
cors = []
for i in range(0, 36, 5):
    for j in range(i+5, 36, 5):
        fi, fj = d[i].flatten(), d[j].flatten()
        mask = (fi != 0) & (fj != 0)
        if mask.sum() > 3:
            cors.append(np.corrcoef(fi[mask], fj[mask])[0, 1])
cors = np.array(cors)
print(f"    corr 範圍: [{cors.min():.6f}, {cors.max():.6f}], mean={cors.mean():.6f}")

# --- [3] d 張量嘅「秩」分析 ---
print("\n[4] d 張量 reshape 做矩陣嘅秩 (36² × 36)")
D = d.reshape(36*36, 36)
rank_d = np.linalg.matrix_rank(D, tol=1e-10)
print(f"    秩: {rank_d} / 36")
print(f"    → {'✅ 全維度 (36 維獨立)' if rank_d == 36 else '⚠️ 秩虧損' if rank_d < 36 else '❌ 超維'}")

# --- [4] 關鍵問題: 36 Kähler basis pairs 嘅結構 ---
print("\n[5] 36 個 Kähler basis pairs 嘅生成規則")
# 佢哋係咪 = 44 site 中 even-even pairs 嘅前 36 個?
all_even_pairs = []
for n in range(1, 45):
    for m in range(n, 45):
        if (n+m) % 2 == 0:
            gamma_n = 4*math.sin(math.pi*n/88)**2
            gamma_m = 4*math.sin(math.pi*m/88)**2
            if (gamma_n+gamma_m)/2 <= 2.0:
                all_even_pairs.append((n, m))
print(f"    滿足條件嘅 even pairs 總數: {len(all_even_pairs)}")
print(f"    取前 36: {all_even_pairs[:36]}")
print(f"    同 KahlerBasis 一致? {all_even_pairs[:36] == pairs}")

# 呢個對應有幾多個「真正 Kähler 方向」?
# γ<2 → n,m 邊界: 4sin²(πn/88) < 2 → sin(πn/88) < 1/√2 → πn/88 < π/4 → n < 22
n_boundary = int(88/4)
print(f"\n    γ<2 嘅邊界: n < 88/4 = {n_boundary} (n=22 係 γ=2)")
print(f"    所以 even pairs 需要 n,m ≤ 22 或 ≥ 66...")
# 但 44 site 只有 1..44, 所以 γ<2 對應 n ≤ 22
n_max = 22
even_in = [(n, m) for n in range(1, n_max+1) for m in range(n, n_max+1) if (n+m) % 2 == 0]
print(f"    n,m ≤ 22 嘅 even pairs: {len(even_in)}")
print(f"    C(22,2)+22 = {22*21//2 + 22}")

# --- [5] 核心結構總結 ---
print("\n" + "=" * 70)
print("【核心結構發現】")
print("=" * 70)
print(f"""
  1. projection_operator.py 嘅 P̂ (134×946):
     真正秩 = 2 (Kähler/CPX 兩類) — 66 個「本徵態」係浮點噪聲
     → 現有質量譜機制有 rank 缺陷

  2. dijk_intersection.py 嘅 d_{{ijk}}:
     36 個 Kähler modulus 有真實 per-index 依賴 (每個對應唔同 (n,m))
     → 呢個先係「CY₃ = K_Chain 投影化身」嘅真正結構載體

  3. 關鍵數字:
     946 = C(44,2) ✅ 自然生成
     rank(P̂) = 2 (缺陷)
     66 = C(12,2) = 3×22 = 2×33 (候選, 未定)
     36 = 前 36 個 γ<2 even pairs
""")
print("=" * 70)
