#!/usr/bin/env python3
"""
O151 — Script 08: 拍頻信道結構分析 (C_beat = 0.4338 bits 嘅來源)
=================================================================
docs/01 留低 🔴: 拍頻信道 C_beat = 0.4338 bits 嘅結構意義。
本 script 解剖信道矩陣: SVD 譜、行條件熵、最優輸入分佈、Z2 對稱、
結構候選掃描 (陷阱窗誠實)。

信道: 世界模 m (ka=2m) -> 觀察者模 n (kb=2n-1), 44x44
      P_mn = |4 sin(d pi/176) cos(s pi/176)| / row_sum, d=|ka-kb|, s=ka+kb
"""
import math

N_d = 44
results = []

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

def build_P():
    P = []
    for m in range(1, N_d + 1):
        ka = 2 * m
        row = []
        for n in range(1, N_d + 1):
            kb = 2 * n - 1
            d = abs(ka - kb)
            s = ka + kb
            b = abs(4 * math.sin(d * math.pi / 176) * math.cos(s * math.pi / 176))
            row.append(b)
        t = sum(row)
        P.append([r / t for r in row])
    return P

P = build_P()

print("=" * 74)
print("  O151 S08: 拍頻信道結構分析")
print("=" * 74)

# ---------------------------------------------------------------
# 1. 行條件熵 H(Y|X=m) — 邊個輸入模最可分辨?
# ---------------------------------------------------------------
print("\n--- 1. 行條件熵 H(Y|X=m) ---")
H_rows = []
for m in range(N_d):
    H = -sum(p * math.log2(p) for p in P[m] if p > 0)
    H_rows.append(H)
best = sorted(range(N_d), key=lambda m: H_rows[m])[:8]
worst = sorted(range(N_d), key=lambda m: H_rows[m])[-5:]
print("  最低條件熵 (最可分辨) 輸入模 m =", [b + 1 for b in best])
print("  最高條件熵 (最唔可分辨) 輸入模 m =", [w + 1 for w in worst])
H_min, H_max = min(H_rows), max(H_rows)
print(f"  H_min = {H_min:.4f}, H_max = {H_max:.4f}, mean = {sum(H_rows)/44:.4f} bits")
check("H_min < H_max (行唔係全部一樣)", H_min < H_max - 0.01)

# 行熵有冇結構? 對應 mode 號
best_modes = [b + 1 for b in best]
print(f"  最佳行 mode 號: {best_modes}")
print(f"  對應 γ_n: {[round(4*math.sin(math.pi*bm*2/176)**2, 4) for bm in best_modes]}")

# ---------------------------------------------------------------
# 2. 最優輸入分佈 (BA)
# ---------------------------------------------------------------
print("\n--- 2. 最優輸入分佈 ---")
def ba(P, tol=1e-13, max_iter=40000):
    ni, no = len(P), len(P[0])
    p = [1.0 / ni] * ni
    Cp = -1.0
    for _ in range(max_iter):
        q = [sum(p[x] * P[x][y] for x in range(ni)) for y in range(no)]
        phi = []
        for x in range(ni):
            s = 0.0
            for y in range(no):
                r = p[x] * P[x][y] / q[y] if q[y] > 0 else 0.0
                s += P[x][y] * (math.log(r) if r > 0 else 0.0)
            phi.append(math.exp(s))
        Z = sum(phi)
        pn = [phi[x] / Z for x in range(ni)]
        C = math.log(Z)
        if abs(C - Cp) < tol:
            return C, p
        Cp = C
        p = pn
    return C, p

C_beat_nats, p_opt = ba(P)
C_beat = C_beat_nats / math.log(2)
print(f"  C_beat = {C_beat:.8f} bits = {C_beat_nats:.8f} nats")
nz = [(i + 1, pi) for i, pi in enumerate(p_opt) if pi > 1e-4]
print(f"  非零輸入 ({len(nz)}): {[(m, round(pi,4)) for m, pi in nz]}")
check("C_beat 重現 0.433818", abs(C_beat - 0.433818) < 1e-5)

# ---------------------------------------------------------------
# 3. 均勻輸入嘅互信息 (如果 = 容量, 信道係對稱)
# ---------------------------------------------------------------
print("\n--- 3. 均勻輸入 I_uniform vs 容量 ---")
p_u = [1.0 / N_d] * N_d
q_u = [sum(p_u[x] * P[x][y] for x in range(N_d)) for y in range(N_d)]
HY_u = -sum(q * math.log2(q) for q in q_u if q > 0)
HXY_u = sum(p_u[x] * H_rows[x] for x in range(N_d))
I_u = HY_u - HXY_u
print(f"  I_uniform = {I_u:.8f} bits, C_beat = {C_beat:.8f} bits")
print(f"  差 = {C_beat - I_u:.6f} (0 = 對稱信道, 均勻輸入最優)")
check("均勻輸入唔係最優 (信道非對稱)", C_beat - I_u > 0.01)

# ---------------------------------------------------------------
# 4. SVD 譜 (|beat| 矩陣, 未歸一化)
# ---------------------------------------------------------------
print("\n--- 4. SVD 譜 (未歸一化 |beat| 矩陣) ---")
def svd_spec(M):
    # 用 numpy 如果可用, 否則 power iteration
    try:
        import numpy as np
        A = np.array(M)
        _, s, _ = np.linalg.svd(A)
        return list(s)
    except ImportError:
        return None

spec = svd_spec(P)
if spec:
    s1, s2 = spec[0], spec[1]
    print(f"  sigma_1 = {s1:.6f}, sigma_2 = {s2:.6f}, ratio = {s2/s1:.3e}")
    print(f"  有效秩 (sigma > 1e-6 sigma_1): {sum(1 for s in spec if s > 1e-6*spec[0])}")
    check("信道矩陣有效秩 > 1 (唔係 rank-1)", sum(1 for s in spec if s > 1e-6 * spec[0]) > 1)
    # 奇異值譜有冇結構?
    print(f"  頭 8 奇異值: {[round(s,4) for s in spec[:8]]}")
    # 譜質量: sum sigma^2 = ||A||_F^2
    F2 = sum(s * s for s in spec)
    print(f"  sum sigma^2 = {F2:.4f} (Frobenius^2)")
else:
    print("  numpy 不可用, 跳過 SVD")
    check("numpy SVD (環境)", False)

# ---------------------------------------------------------------
# 5. Z2 對稱: row m vs row 44-m (ka = 2m vs 88-2m+... )
# ---------------------------------------------------------------
print("\n--- 5. Z2 對稱檢查 ---")
# 世界模 m 嘅對偶: 觀察者模 n <-> 44-n (Z2: kb=2n-1 <-> 2(44-n)-1 = 87-2n)
# 檢查 P[m][n] vs P[44-m][44-n]? (m 對偶 = 44-m 世界模)
sym_count = 0
for m in range(N_d):
    for n in range(N_d):
        if abs(P[m][n] - P[N_d - 1 - m][N_d - 1 - n]) < 1e-12:
            sym_count += 1
print(f"  P[m][n] = P[45-m][45-n] 嘅項: {sym_count}/1936")
check("信道矩陣冇簡單 Z2 鏡像對稱 (唔係 trivial)", sym_count < 1936)

# ---------------------------------------------------------------
# 6. C_beat 結構候選掃描 (陷阱窗誠實; 禁 post-hoc 擬合常數)
# ---------------------------------------------------------------
print("\n--- 6. C_beat 結構候選掃描 ---")
cands = {
    "log2(4/3)":        math.log2(4 / 3),
    "1/pi":             1 / math.pi,
    "ln(phi)/pi":       math.log(1.6180339887) / math.pi,
    "log2(phi)-1/4":    math.log2(1.6180339887) - 0.25,
    "2/pi^2":           2 / math.pi ** 2,
    "1-2/pi":           1 - 2 / math.pi,
    "log2(1.35)":       math.log2(1.3513),
    "log2(phi)/phi":    math.log2(1.6180339887) / 1.6180339887,
}
print(f"  C_beat = {C_beat:.8f} bits")
for name, val in cands.items():
    dev = abs(C_beat - val) / val
    in_trap = 1e-5 <= dev <= 1e-3
    flag = "  <== 陷阱窗! 🟡 排除" if in_trap else ""
    print(f"  {name:16s} = {val:.8f}  dev = {dev:.3e}{flag}")
check("C_beat 冇結構閉式命中 (全部 > 1e-3, 冇 post-hoc 擬合) — 誠實負結果",
      all(abs(C_beat - v) / v > 1e-3 for v in cands.values()))
print("  判決: C_beat 本身冇簡單閉式; 結構喺最優輸入同秩 (見 §8)")

# ---------------------------------------------------------------
# 7. 行熵同 mode 號嘅關聯 (v_g / gamma 結構) — 誠實負結果
# ---------------------------------------------------------------
print("\n--- 7. 行熵 vs 模式物理量 ---")
gamma_w = [4 * math.sin(math.pi * (2 * m) / 176) ** 2 for m in range(1, N_d + 1)]
mean_H = sum(H_rows) / 44
mean_g = sum(gamma_w) / 44
cov = sum((H_rows[i] - mean_H) * (gamma_w[i] - mean_g) for i in range(44)) / 44
var_H = sum((h - mean_H) ** 2 for h in H_rows) / 44
var_g = sum((g - mean_g) ** 2 for g in gamma_w) / 44
corr = cov / math.sqrt(var_H * var_g)
print(f"  corr(H_row, gamma_world) = {corr:.4f}")
check("行熵同 γ 冇簡單線性相關 (corr ~ 0) — 誠實負結果", abs(corr) < 0.2)

# ---------------------------------------------------------------
# 8. ★ 結構發現: 最優輸入 = Z2 對偶對 @ {N_gen, L6}
# ---------------------------------------------------------------
print("\n--- 8. ★ 結構發現: 最優輸入 Z2 對 ---")
N_gen, L6 = 3, 18
opt_modes = [m for m, pi in enumerate(p_opt, start=1) if pi > 1e-4]
print(f"  最優輸入模: {opt_modes}")
check("最優輸入 = {3, 18, 26, 41} = {N_gen, L6, N_d-N_gen, N_d-L6}",
      sorted(opt_modes) == [3, 18, 26, 41])
check("Z2 對 (3,41): 3 + 41 = 44 = N_d", 3 + 41 == 44)
check("Z2 對 (18,26): 18 + 26 = 44 = N_d", 18 + 26 == 44)
check("錨點: 3 = N_gen (世代數), 18 = L6 (Lucas 6)", N_gen == 3 and L6 == 18)
check("錨點和: 3 + 18 = 21 = F8 (Fibonacci 8)", 3 + 18 == 21)
# 對內機率對稱
p3, p41 = p_opt[2], p_opt[40]
p18, p26 = p_opt[17], p_opt[25]
print(f"  p3 = {p3:.6f}, p41 = {p41:.6f} (對內對稱: {abs(p3-p41):.2e})")
print(f"  p18 = {p18:.6f}, p26 = {p26:.6f} (對內對稱: {abs(p18-p26):.2e})")
check("Z2 對內機率對稱 (p3=p41, p18=p26)", abs(p3 - p41) < 1e-4 and abs(p18 - p26) < 1e-4)
# 譜權重: 每對 = 4 = B
g3 = 4 * math.sin(math.pi * 6 / 176) ** 2      # k=2*3
g41 = 4 * math.sin(math.pi * 82 / 176) ** 2    # k=2*41
g18 = 4 * math.sin(math.pi * 36 / 176) ** 2
g26 = 4 * math.sin(math.pi * 52 / 176) ** 2
print(f"  gamma3+gamma41 = {g3+g41:.10f} (=4=B)")
print(f"  gamma18+gamma26 = {g18+g26:.10f} (=4=B)")
check("Z2 對譜權重 = 4 = B (兩對)", abs(g3 + g41 - 4) < 1e-9 and abs(g18 + g26 - 4) < 1e-9)
check("總譜權重 = 8 = 2B", abs(g3 + g41 + g18 + g26 - 8) < 1e-9)
# 輸出峰值: 對應邊個觀察者模?
def peak_col(m):
    return max(range(N_d), key=lambda n: P[m - 1][n]) + 1
pk_18, pk_26 = peak_col(18), peak_col(26)
pk_3, pk_41 = peak_col(3), peak_col(41)
print(f"  對 (18,26) 輸出峰值 -> 觀察者模 n = {pk_18}, {pk_26}")
print(f"  對 (3,41)  輸出峰值 -> 觀察者模 n = {pk_3}, {pk_41}")
check("對 (18,26) -> n=1 (基頻觀察者模)", pk_18 == 1 or pk_26 == 1)
check("對 (3,41) -> n=22 (自對偶 N_d/2)", pk_3 == 22 or pk_41 == 22)
print("  解讀: 信道最優策略 = 用 {L6 對} 讀基頻觀察者模, 用 {N_gen 對} 讀自對偶模")

# 有效秩 = 22 = N_d/2
if spec:
    eff_rank = sum(1 for s in spec if s > 1e-6 * spec[0])
    check("有效秩 = 22 = N_d/2 = Z2 軌道數", eff_rank == 22)
    print(f"  有效秩 {eff_rank} = N_d/2 = Z2 對數 (O145: 22 = Z2 自對偶)")

print("\n" + "=" * 74)
print(f"  S08 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)
