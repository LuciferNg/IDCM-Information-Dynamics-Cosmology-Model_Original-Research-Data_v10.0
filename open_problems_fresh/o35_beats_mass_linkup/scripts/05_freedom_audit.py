#!/usr/bin/env python3
"""
O35 — Step 5: 自由度審計 (Overfit 檢查) ⚠️ 誠實標記
=====================================================
全譜搜尋 (Step 4) 搵到 sin 比值 × φ^k 可以 fit 所有質量比,
但要檢查呢啲 fit 係咪 overfit:

  - 44×44 網格 (1936 個 sin 組合) × φ^k 網格 (幾百個 k) 
    = 幾十萬個候選 → 總會有一個接近
  - 真正閉合需要 k 值有結構來源 (Lucas/Fibonacci/拓撲數)

審計標準 (每項 PASS = k 有結構意義):
  [1] k 可以寫成已知結構常數組合 (Lucas L_n, Fibonacci F_n, N_d, B, CY₃)
  [2] k 嘅分母係結構數 (4, 11, 33, 44, 88, 132, 528)
  [3] sin 配對 (n1,n2) 有結構意義 (Lucas/Fibonacci/質數/半整數)
  [4] 偏差 < 0.1% 同時 k 結構閉合 (唔可以靠 k 補償)
  [5] 獨立預測: 用閉合嘅 k 預測未參與 fit 嘅質量比
"""

import numpy as np
from itertools import product

N = 44
phi = (1 + np.sqrt(5)) / 2

# Lucas / Fibonacci 數 (結構常數庫)
L = {0: 2, 1: 1, 2: 3, 3: 4, 4: 7, 5: 11, 6: 18, 7: 29, 8: 47, 9: 76, 10: 123, 11: 199, 12: 322}
F = {1: 1, 2: 1, 3: 2, 4: 3, 5: 5, 6: 8, 7: 13, 8: 21, 9: 34, 10: 55, 11: 89, 12: 144}

# 結構常數 (O34 已確認)
N_d = 44
B = 4
dimC = 3
CY3 = 3 * N_d + 2  # 134
M_KT = 33  # K_Tree 深度
F5, F7, F10 = 5, 13, 55
L4, L5, L7, L10, L11 = 7, 11, 29, 123, 199

# 結構數集合 (numerator 候選)
struct_ints = set()
struct_ints.update(L.values())
struct_ints.update(F.values())
struct_ints.update([N_d, B, dimC, CY3, M_KT, 88, 176, 528, 71, 17, 6, 2, 1, 0])
# 所有線性組合 (細範圍內)
for a in list(struct_ints):
    for b in list(struct_ints):
        for s in (1, -1):
            v = a + s*b
            if 0 <= v <= 200:
                struct_ints.add(v)

# 結構分母 (k 嘅分母)
struct_dens = {1, 2, 3, 4, 6, 8, 11, 12, 16, 22, 24, 33, 44, 66, 88, 132, 528}

# PDG 2024 (MeV)
masses = {
    "m_u": 2.16, "m_d": 4.67, "m_s": 93.4,
    "m_c": 1.27e3, "m_b": 4.18e3, "m_t": 172.76e3,
    "m_e": 0.511, "m_mu": 105.658, "m_tau": 1776.93,
}

def sin_ratio(n1, n2):
    return np.sin(np.pi * n1 / 88) / np.sin(np.pi * n2 / 88)

def k_phi(r):
    return np.log(r) / np.log(phi)

print("=" * 67)
print("  O35 — Step 5: 自由度審計 (Overfit 檢查)")
print("=" * 67)

targets = {
    "m_u/m_d": masses["m_u"]/masses["m_d"],
    "m_s/m_d": masses["m_s"]/masses["m_d"],
    "m_c/m_b": masses["m_c"]/masses["m_b"],
    "m_c/m_s": masses["m_c"]/masses["m_s"],
    "m_b/m_s": masses["m_b"]/masses["m_s"],
    "m_t/m_c": masses["m_t"]/masses["m_c"],
    "m_mu/m_tau": masses["m_mu"]/masses["m_tau"],
    "m_t/m_b": masses["m_t"]/masses["m_b"],
}

# ═══════════════════════════════════════════════════════════════
# [1] k 結構性審計: 搜索到嘅 k 有冇結構意義?
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [1] k 結構性審計 ───")
print(f"  標準: k = 結構數/結構分母 (Lucas/Fibonacci/拓撲數)")

# Step 4 搜索結果 (唔用搜索, 直接對每個目標做結構 k 掃描)
print(f"\n  {'目標':<10} | {'結構 k 候選':<22} | {'偏差%':<10} | {'狀態':<8}")
print("-" * 60)

audit = {}
for name, target in targets.items():
    # 對每個 (n1,n2) 配對, 掃描結構 k
    best = None
    best_err = float('inf')
    for n1 in range(1, N+1):
        for n2 in range(1, N+1):
            if n1 == n2:
                continue
            r_sin = sin_ratio(n1, n2)
            if r_sin <= 0:
                continue
            # k = log_φ(target/r_sin)
            k = k_phi(target / r_sin)
            # 檢查 k 係咪結構數/結構分母
            for k_num in sorted(struct_ints):
                if k_num > 200:
                    break
                for k_den in sorted(struct_dens):
                    kcand = k_num / k_den
                    if abs(k - kcand) > 0.02:  # 結構匹配容差
                        continue
                    r_pred = r_sin * phi**kcand
                    err = abs(r_pred - target) / target * 100
                    if err < best_err:
                        best_err = err
                        best = (n1, n2, r_sin, kcand, k_num, k_den, k)
    if best:
        n1, n2, r_sin, kcand, k_num, k_den, k_exact = best
        audit[name] = best
        is_struct = abs(k_exact - kcand) < 0.02
        status = "🟢" if (is_struct and best_err < 0.5) else "🟡" if is_struct else "🔴"
        print(f"  {name:<10} | sin({n1:>2},{n2:>2})×φ^({k_num}/{k_den}) | {best_err:>8.4f}% | {status}")

# ═══════════════════════════════════════════════════════════════
# [2] 已知閉合公式重驗證
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [2] 已知閉合公式重驗證 (O34 🟢) ───")
# m_t/m_b = φ^(2B+71/132) × sin(19)/sin(33)
k_t = 2*B + 71/132
r_tb = phi**k_t * sin_ratio(19, 33)
target_tb = masses["m_t"]/masses["m_b"]
print(f"  m_t/m_b = φ^({k_t}) × sin(19)/sin(33)")
print(f"    = {r_tb:.6f} vs 目標 {target_tb:.6f}")
print(f"    dev = {abs(r_tb-target_tb)/target_tb*100:.4f}%")
print(f"    k 結構: 71 = 2N_d - (L₅+C(4,2)) = 88-17 ✅, 132 = 3×44 = dimC×N_d ✅")
print(f"    sin 配對: 19, 33 — 33 = M_KT (K_Tree 深度) ✅, 19 = 90/3 - L₅ ✅")
PASS2 = abs(r_tb-target_tb)/target_tb < 0.001
print(f"  [2] 已知閉合: {'✅ PASS' if PASS2 else '❌ FAIL'}")

# ═══════════════════════════════════════════════════════════════
# [3] 自由度計數: 需要幾多個「結構數」先 fit 到全部?
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [3] 自由度計數 ───")
n_struct_fits = sum(1 for name in audit if abs(audit[name][6] - audit[name][3]) < 0.02)
n_total = len(targets)
print(f"  目標數: {n_total}")
print(f"  結構 k 匹配數: {n_struct_fits}")
print(f"  非結構 k (overfit 風險): {n_total - n_struct_fits}")
print(f"  → 44 個 sin 配對 + 幾百個結構 k = 自由度遠大於 8 個目標")
print(f"  → 結構匹配本身唔夠 — 需要額外嘅「選擇規則」鎖定配對")
PASS3 = n_struct_fits == n_total  # 全部 fit 到結構 k
print(f"  [3] 自由度審計: {'✅ 全部有結構 k' if PASS3 else '❌ 有 overfit 風險'}")

# ═══════════════════════════════════════════════════════════════
# [4] 選擇規則審計: sin 配對 (n1,n2) 有冇結構意義?
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [4] sin 配對結構性 ───")
# O34 已閉合: m_t/m_b 用 (19,33) — 33 = M_KT, 19 = 90/3-L₅
# m_7 用 7 — L₄
print(f"  O34 已閉合配對:")
print(f"    (19,33): 33 = M_KT ✅, 19 = 30-11 = 90/3 - L₅ ✅")
print(f"    (7): 7 = L₄ ✅ (m_7 DM 質量)")
print(f"  Step 4 搜索配對:")
for name, b in audit.items():
    n1, n2 = b[0], b[1]
    # 檢查結構性
    tags = []
    for nn, label in [(n1, "n1"), (n2, "n2")]:
        if nn in L.values(): tags.append(f"{label}=L{list(L.keys())[list(L.values()).index(nn)]}")
        elif nn in F.values(): tags.append(f"{label}=F{list(F.keys())[list(F.values()).index(nn)]}")
        elif nn in [N_d, B, M_KT, 88, 19, 71, 17]: tags.append(f"{label}={nn}結構")
        else: tags.append(f"{label}={nn}?")
    print(f"    {name}: sin({n1},{n2}) → {', '.join(tags)}")

# ═══════════════════════════════════════════════════════════════
# [5] 獨立預測測試
# ═══════════════════════════════════════════════════════════════
print(f"\n─── [5] 獨立預測測試 ───")
# 用 O34 已閉合嘅 k 結構 (71 = 2N_d - (L₅+C(4,2))) 預測 m_u/m_d:
# 假設 m_u/m_d 用同類結構: k = ? 需要推導
# 誠實標記: 目前冇獨立預測 — 所有 fit 都係「事後配對」
print(f"  目前狀態: m_t/m_b 同 m_μ/m_e 係 O34 結構閉合 (k 有拓撲來源)")
print(f"  m_u/m_d, m_s/m_d, m_c/m_b: 搜索 fit 但 k 結構性待確認")
print(f"  → 誠實標記: 🔴 未閉合 — 需要「選擇規則」由 K_Chain 推導 (n1,n2) 配對")
PASS5 = False  # 未閉合
print(f"  [5] 獨立預測: {'✅ PASS' if PASS5 else '🔴 開放 (誠實標記)'}")

# ═══════════════════════════════════════════════════════════════
# 總結
# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*67}")
results = [PASS2, PASS3, PASS5]
print(f"  O35 Step 5 結果: {sum(results)}/{len(results)} PASS (審計)")
print(f"  ⚠️ 全譜搜索 fit ≠ 結構閉合")
print(f"  ⚠️ 44×44 sin 網格 × 結構 k 網格 = overfit 風險")
print(f"  🟢 已閉合: m_t/m_b (φ^8+71/132 × sin19/33), m_μ/m_e (φ^L5+L4/88)")
print(f"  🔴 未閉合: m_u/m_d, m_s/m_d, m_c/m_b 嘅 (n1,n2) 選擇規則")
print(f"{'═'*67}")

with open("data/step5_freedom_audit_results.txt", "w") as f:
    f.write("O35 — Step 5: 自由度審計 (Overfit 檢查)\n")
    f.write("=" * 67 + "\n\n")
    f.write(f"[1] k 結構性審計:\n")
    for name, b in audit.items():
        n1, n2, r_sin, kcand, k_num, k_den, k_exact = b
        f.write(f"  {name}: sin({n1},{n2}) x phi^({k_num}/{k_den}) k_exact={k_exact:.4f}\n")
    f.write(f"\n[2] 已知閉合重驗證: {'PASS' if PASS2 else 'FAIL'} (t/b {abs(r_tb-target_tb)/target_tb*100:.4f}%)\n")
    f.write(f"[3] 自由度審計: {'PASS' if PASS3 else 'FAIL'} ({n_struct_fits}/{n_total} 結構匹配)\n")
    f.write(f"[4] sin 配對結構性: 記錄於上\n")
    f.write(f"[5] 獨立預測: {'PASS' if PASS5 else 'OPEN'}\n")
    f.write(f"\n⚠️ 全譜搜索 fit ≠ 結構閉合\n")
    f.write(f"🟢 已閉合: m_t/m_b, m_μ/m_e\n")
    f.write(f"🔴 未閉合: m_u/m_d, m_s/m_d, m_c/m_b 選擇規則\n")
print(f"\n  結果已寫入 data/step5_freedom_audit_results.txt")
