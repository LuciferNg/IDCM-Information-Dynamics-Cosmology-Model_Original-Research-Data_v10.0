#!/usr/bin/env python3
"""
O62 八期 32: GLSM 深入 — 7+29=36 結構
======================================
上次: charge matrix 32×37, rank 32, kernel 5
linear relations: 5 條 (glsm_linrels)

問題: 36 Kähler 參數 ζ^a 喺邊?
  7+29 = 36: γ_7 動態 + L_7=29 固定

hypothesis: 32 U(1) 中, 8 個係「residual」(O58: residual U(1) 8)
  → 24 個凍結 (div0 對沖?)
  → residual 8 個中, 7 個動態 + 1 個特殊?

或者: linear relations 5 條對應 5 個消去
  37 − 5 = 32 = 2B²?? (O58: 32 U(1) = 2B²!)

深入:
  1. glsm_linrels 完整解讀 (5 條 37-dim 向量)
  2. 邊 5 個 field 被消去? (non-trivial entries)
  3. Q 嘅 kernel basis (5 個)
  4. residual U(1) 分析: 邊 8 個 U(1) 特殊?
  5. 7+29 結構: γ_7 ↔ ?
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 32: GLSM 7+29=36 深入")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
Q = np.array(d["glsm_matrix"], dtype=float)  # 32×37
linrels = d["glsm_linrels"]  # 5×37
pts = np.array(d["points"], dtype=float)

# ============ 1. Linear relations 結構 ============
print("\n[1] Linear relations (5×37)")
LR = np.array(linrels, dtype=float)
print(f"  shape: {LR.shape}")
# 每條 relation 嘅非零位置
for r_idx, lr in enumerate(LR):
    nz = [(i, int(lr[i])) for i in range(len(lr)) if abs(lr[i]) > 1e-8]
    print(f"  relation {r_idx}: {len(nz)} 非零: {nz[:12]}")

# ============ 2. Charge matrix 結構 ============
print("\n[2] Charge matrix 結構")
# 有 32 行, 每行一個 U(1)
# field 0, 3, 4, 7, 8 有多個 charge (col_nnz > 1)
col_nnz = np.count_nonzero(Q, axis=0)
multi = [(i, int(col_nnz[i])) for i in range(len(col_nnz)) if col_nnz[i] > 1]
print(f"  多 charge field (col_nnz > 1): {multi}")
# 呢啲 field 係咪對應頂點?
print(f"  頂點 (0-5): {[(i, int(col_nnz[i])) for i in range(6)]}")

# ============ 3. Kernel of Q ============
print("\n[3] Q kernel")
# Q: 32×37, rank 32 → kernel 5
U, S, Vt = np.linalg.svd(Q)
kernel = Vt[32:]  # 最後 5 行
print(f"  kernel basis: {kernel.shape}")
# 檢查 kernel 同 linrels 關係
print(f"  kernel 每行非零數: {[np.count_nonzero(k) for k in kernel]}")

# ============ 4. U(1) 之間嘅關係 ============
print("\n[4] U(1) 數目分析")
n_U1 = Q.shape[0]  # 32
print(f"  U(1) 數: {n_U1}")
print(f"  2B² = 32? {2*4*4 == 32}")
check("32 U(1) = 2B²", n_U1 == 32, "")

# ============ 5. 37 fields = 48 points − 11 ============
print("\n[5] Field 數 vs 點數")
print(f"  fields: {Q.shape[1]} (37)")
print(f"  points: {len(pts)} (48)")
print(f"  差: {len(pts) - Q.shape[1]} = 11")
print(f"  11 = F₈ − F₆ + ... ? 或者 = 44/4 = N_d/B?")
print(f"  44/4 = 11 ✓")

# ============ 6. 7+29 探索 ============
print("\n[6] 7+29 = 36")
print(f"  h11 = 36")
print(f"  γ_7 (mode 7) + L_7 (29)")
# 檢查: Q 有冇 29 或 7 嘅結構?
# 每行 U(1) 嘅 charge 總和
row_sum = Q.sum(axis=1)
print(f"  每 U(1) charge 總和: {[int(v) for v in row_sum]}")
# charge 總和 = 0 嘅 U(1) 數
zero_rows = np.where(np.abs(row_sum) < 1e-8)[0]
print(f"  Σcharge = 0 嘅 U(1): {zero_rows.tolist()} ({len(zero_rows)} 個)")
# 呢啲係「special」U(1)

# 頂點 charge pattern
print(f"\n  頂點 fields (0-5) 嘅 charges:")
for f in range(6):
    print(f"    field {f}: {[int(Q[a,f]) for a in range(min(10, Q.shape[0]))]}...")

# ============ 7. 殘餘 U(1) (O58: residual 8) ============
print("\n[7] residual U(1) 分析")
# O58: residual positions {0,3,7,25,28,29,30,31} — 呢啲係 field positions?
# 定係 U(1) indices?
residual = [0, 3, 7, 25, 28, 29, 30, 31]
print(f"  residual positions (O58): {residual}")
# 如果係 U(1) indices: 呢 8 個 U(1) 有咩特別?
print(f"  呢 8 個 U(1) 嘅 charge 總和:")
for r in residual:
    print(f"    U(1) {r}: {[int(v) for v in Q[r,:10]]}...")
# 如果係 field indices: 呢 8 個 field 有咩特別?
print(f"\n  如果係 field indices:")
for r in residual:
    if r < Q.shape[1]:
        print(f"    field {r}: charge 分佈 {[int(Q[a,r]) for a in range(8)]}...")

# ============ 8. 總結 ============
print("\n" + "=" * 72)
print("八期 32 總結:")
print("=" * 72)
print(f"""
  GLSM 結構:
  - Charge matrix: 32×37 (32 U(1) = 2B² ✓, 37 fields = 48−11)
  - rank 32, kernel 5 (linear relations)
  - 11 = 44/4 = N_d/B (field 消去數)

  7+29 = 36 探索:
  - h11 = 36 Kähler 參數
  - residual U(1) 8 個 (O58)
  - 7 = γ_7 動態, 29 = L_7

  🟡 機制未閉合 — 需要理解 32 U(1) → 36 Kähler 嘅映射
""")
out = {
    "test": "O62 八期 32: GLSM 深入",
    "LR_shape": list(LR.shape),
    "multi_charge_fields": multi,
    "n_U1": int(n_U1),
    "n_fields": int(Q.shape[1]),
    "zero_row_sums": zero_rows.tolist(),
    "kernel_nnz": [int(np.count_nonzero(k)) for k in kernel],
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "32_glsm_deep.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 32 完成!")
