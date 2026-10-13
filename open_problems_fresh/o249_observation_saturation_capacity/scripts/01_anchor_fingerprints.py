#!/usr/bin/env python3
"""
O249 — Script 01: 飽和錨點指紋 (Saturation Anchor Fingerprints)
================================================================
IDCM 側結構指紋表 — Q2/Q3 盲測設計嘅「目標統計」.
全部由 O151 已閉合公式重現 (scripts/08 + docs/07 + docs/11), 零新自由度.

預註冊判據 (跑前凍結, threshold 零放寬):
  F0  P_mn = |4 sin(dπ/176) cos(sπ/176)| = 2|sin(k_a θ) − sin(k_b θ)|, θ=π/88 (beat = sin 差)  maxdev < 1e-12
  F1  SVD 有效秩 (σ > 1e-6·σ₁) = 22 = N_d/2 = Z₂ 軌道數
  F2  BA 全信道容量 C_beat = 0.43381827 bits (重現 O151, 1e-5)
  F3  最優輸入支撐 = {3,18,26,41} = {N_gen, L₆, N_d−N_gen, N_d−L₆}; 對內概率對稱 (1e-4)
  F4  row Z₂ 退化 row(m) = row(44−m): max|Δ| < 1e-15
  F5  ★ Z₂ 鏡像對信道信息為空: I(X∈{m,44−m}; Y) = 0 < 1e-12  ∀m  (飽和嘅結構核心)
  F6  ★ 飽和曲線: 貪婪最優 k-row 容量 C(S_k), k=1..22
       預期: C(S₁)=0, C(S₂)=C_beat, k≥2 平台 → max|C(S_k)−C_beat| < 1e-4 (ΔI 相對 I(2) < 1e-4)
  F7  容量階梯: C_obs = Σγ_odd = 88 (dev=0); {88,132,264,528} = N_d×{2,3,6,12}; 528 = C(33,2) = B²·33
  F8  兩點信道 {row3,row18} I = 0.43381827 (1e-6 重現, O151 docs/11)

禁區 (O206 docs/19): 唔會引入 K_tree 譜 λ_k 做「第二拍頻」; 微觀飽和載體 = Z₂ 簡併 + 容量共享.
"""
import math
import json

N_d = 44
results = []
details = {}

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)
    return cond

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

def sin_diff_form(ka, kb):
    """2|sin(k_a θ) − sin(k_b θ)|, θ = π/88 — 未歸一化 (應等於 |4 sin(dπ/176) cos(sπ/176)|)"""
    th = math.pi / 88
    return abs(2 * (math.sin(ka * th) - math.sin(kb * th)))

def ba_channel(P, rows, tol=1e-13, max_iter=40000):
    """Blahut-Arimoto capacity of sub-channel restricted to input rows (0-based list)."""
    ni = len(rows)
    if ni == 0:
        return 0.0
    no = len(P[0])
    p = [1.0 / ni] * ni
    Cp = -1.0
    C = 0.0
    for _ in range(max_iter):
        q = [sum(p[x] * P[rows[x]][y] for x in range(ni)) for y in range(no)]
        phi = []
        for x in range(ni):
            s = 0.0
            for y in range(no):
                r = p[x] * P[rows[x]][y] / q[y] if q[y] > 0 else 0.0
                s += P[rows[x]][y] * (math.log(r) if r > 0 else 0.0)
            phi.append(math.exp(s))
        Z = sum(phi)
        pn = [phi[x] / Z for x in range(ni)]
        C = math.log(Z)
        if abs(C - Cp) < tol:
            return C
        Cp = C
        p = pn
    return C

def uniform_mi(P, rows):
    """Mutual information with input uniform over `rows` (0-based)."""
    no = len(P[0])
    HY = 0.0
    HXY = 0.0
    k = len(rows)
    for y in range(no):
        q = sum(P[r][y] for r in rows) / k
        if q > 0:
            HY -= q * math.log2(q)
        for r in rows:
            if P[r][y] > 0:
                HXY -= P[r][y] * math.log2(P[r][y]) / k
    return HY - HXY

def mutual_info_pair(P, m):
    """I(X∈{r,44−r}, uniform; Y) for 0-based m ↔ 1-based r=m+1, mirror 0-based index 42−m.
    期望 0: 兩 row 逐元素相等 ⟹ Y 分佈同一個, I(X;Y)=H(Y)−H(Y|X)=0."""
    r0 = P[m]
    r1 = P[42 - m]
    no = len(P[0])
    HY = 0.0
    HXY = 0.0
    for y in range(no):
        q = 0.5 * r0[y] + 0.5 * r1[y]
        if q > 0:
            HY -= q * math.log2(q)
        for r in (r0[y], r1[y]):
            if r > 0:
                HXY -= 0.5 * r * math.log2(r)
    return HY - HXY

print("=" * 74)
print("  O249 S01: 飽和錨點指紋 (Saturation Anchor Fingerprints)")
print("=" * 74)

P = build_P()

# ---------------- F0: beat = sin 差形式 ----------------
print("\n--- F0: P_mn = 2|sin(k_a θ) − sin(k_b θ)| (beat 形式) ---")
maxdev0 = 0.0
for m in range(1, N_d + 1):
    ka = 2 * m
    for n in range(1, N_d + 1):
        kb = 2 * n - 1
        d = abs(ka - kb); s = ka + kb
        lhs = abs(4 * math.sin(d * math.pi / 176) * math.cos(s * math.pi / 176))
        rhs = sin_diff_form(ka, kb)
        # compare unnormalized weights
        maxdev0 = max(maxdev0, abs(lhs - rhs))
print(f"  max |4sin·cos − 2|sinA−sinB|| = {maxdev0:.3e}")
check("F0: beat = sin 差 (2|sinA−sinB|), maxdev < 1e-12", maxdev0 < 1e-12, f"maxdev={maxdev0:.2e}")
details["F0_sin_diff_maxdev"] = maxdev0

# ---------------- F1: SVD 有效秩 ----------------
print("\n--- F1: SVD 有效秩 (σ > 1e-6 σ₁) ---")
import numpy as np
A = np.array(P)
_, s, _ = np.linalg.svd(A)
eff_rank = int(np.sum(s > 1e-6 * s[0]))
print(f"  sigma_1 = {s[0]:.8f}, 有效秩 = {eff_rank} (期望 22)")
check("F1: 有效秩 = 22 = N_d/2", eff_rank == 22, f"rank={eff_rank}")
details["SVD_eff_rank"] = eff_rank
details["SVD_top8"] = [round(float(x), 6) for x in s[:8]]

# ---------------- F2: BA 全信道容量 ----------------
print("\n--- F2: BA 全信道容量 C_beat ---")
C_full = ba_channel(P, list(range(N_d))) / math.log(2)
print(f"  C_beat = {C_full:.8f} bits")
check("F2: C_beat = 0.43381827 重現 (1e-5)", abs(C_full - 0.43381827) < 1e-5, f"C={C_full:.8f}")
details["C_beat_full"] = C_full

# ---------------- F3: 最優輸入 = Z₂ 對 ----------------
print("\n--- F3: BA 最優輸入支撐 ---")
p = [1.0 / N_d] * N_d
Cp = -1.0
for _ in range(40000):
    q = [sum(p[x] * P[x][y] for x in range(N_d)) for y in range(N_d)]
    phi = []
    for x in range(N_d):
        s = 0.0
        for y in range(N_d):
            r = p[x] * P[x][y] / q[y] if q[y] > 0 else 0.0
            s += P[x][y] * (math.log(r) if r > 0 else 0.0)
        phi.append(math.exp(s))
    Z = sum(phi)
    pn = [phi[x] / Z for x in range(N_d)]
    C = math.log(Z)
    if abs(C - Cp) < 1e-13:
        break
    Cp, p = C, pn
nz = sorted([i + 1 for i, pi in enumerate(p) if pi > 1e-4])
print(f"  非零輸入模: {nz}")
check("F3: 最優輸入 = {3,18,26,41}", nz == [3, 18, 26, 41], f"{nz}")
p3, p41 = p[2], p[40]
p18, p26 = p[17], p[25]
check("F3: Z₂ 對內概率對稱 (p3=p41, p18=p26, 1e-4)",
      abs(p3 - p41) < 1e-4 and abs(p18 - p26) < 1e-4,
      f"|Δ3|={abs(p3-p41):.1e}, |Δ18|={abs(p18-p26):.1e}")
details["optimal_support"] = nz
details["p3_p41"] = [float(p3), float(p41)]
details["p18_p26"] = [float(p18), float(p26)]

# ---------------- F4: row Z₂ 退化 ----------------
print("\n--- F4: row(r) = row(44−r) (1-based, r=1..43) ---")
# 配對 = O151 scripts/13 正典 (P[m-1] vs P[43-m]): 0-based m vs 42−m.
# row 44 (Nyquist, γ₄₄=4=B) 冇 Z₂ 伙伴 — 向量 distinct 但信息近零 (F6 平台).
maxdev4 = 0.0
for m in range(43):
    d = max(abs(P[m][n] - P[42 - m][n]) for n in range(N_d))
    maxdev4 = max(maxdev4, d)
print(f"  max|Δ| = {maxdev4:.3e}")
check("F4: row Z₂ 退化 (r vs 44−r) max|Δ| < 1e-15", maxdev4 < 1e-15, f"maxdev={maxdev4:.2e}")
details["Z2_row_maxdev"] = maxdev4

# ---------------- F5: Z₂ 鏡像對信息為空 ----------------
print("\n--- F5: I(X∈{r,44−r}; Y) — 鏡像對信息 (期望 0) ---")
mi_max = 0.0
for m in range(21):
    mi = mutual_info_pair(P, m)
    mi_max = max(mi_max, mi)
print(f"  max I(mirror pair) = {mi_max:.3e} bits")
check("F5: 鏡像對信息為空 < 1e-12 bits (∀r=1..21)", mi_max < 1e-12, f"max={mi_max:.2e}")
details["mirror_pair_max_MI"] = mi_max

# ---------------- F6: 飽和曲線 (貪婪最優 k-row 容量) ----------------
print("\n--- F6: 飽和曲線 C(S_k) — 貪婪最優 k-row (選取: uniform-MI, 曲線: BA) ---")
# 預註冊: 貪婪選取準則 = uniform-MI (廉價); 最終曲線值 = BA 容量 (同 F2 一致).
# k=1 時 1-row 信道容量 = 0 (H(X)=0), uniform-MI 全 tie — 預註冊 tie-break: row 3 (N_gen).
S = []
curve = []
prev_C = 0.0
for k in range(1, N_d + 1):
    cand = [r for r in range(N_d) if r not in S]
    if k == 1:
        best = 2  # tie-break 預註冊: row 3 = N_gen
    else:
        best = max(cand, key=lambda r: uniform_mi(P, S + [r]))
    S.append(best)
    c = ba_channel(P, S) / math.log(2)
    curve.append((k, best + 1, c))
    if k <= 22:
        print(f"  k={k:2d}: row {best+1:2d} -> C = {c:.8f} bits (Δ = {c-prev_C:+.2e})")
    prev_C = c
C_S2 = curve[1][2]
plateau_dev = max(abs(c - C_full) for _, _, c in curve[2:])
print(f"  C(S₂) = {C_S2:.8f}, |C(k≥2) − C_beat| max = {plateau_dev:.3e}")
check("F6a: C(S₁) = 0 (單 row 冇信息)", curve[0][2] == 0.0)
check("F6b: 飽和平台: k≥2 全部 |C − C_beat| < 1e-4", plateau_dev < 1e-4, f"maxdev={plateau_dev:.2e}")
check("F6c: 兩點信道 C(S₂) ≈ C_beat (1e-4)", abs(C_S2 - C_full) < 1e-4, f"|Δ|={abs(C_S2-C_full):.2e}")
details["saturation_curve"] = [{"k": k, "row": r, "C_bits": c} for k, r, c in curve]
details["plateau_maxdev"] = plateau_dev

# ---------------- F7: 容量階梯 ----------------
print("\n--- F7: 容量階梯 ---")
gamma_odd = [4 * math.sin(math.pi * (2 * n - 1) / 176) ** 2 for n in range(1, N_d + 1)]
C_obs = sum(gamma_odd)
ladder = [N_d * m for m in (2, 3, 6, 12)]
comb = 33 * 32 // 2
print(f"  C_obs = Σγ_odd = {C_obs:.10f} (期望 88)")
print(f"  階梯 {ladder} (期望 [88,132,264,528]); C(33,2) = {comb}")
check("F7a: C_obs = 88 = Σγ_odd (dev=0)", abs(C_obs - 88) < 1e-9, f"{C_obs:.8f}")
check("F7b: 階梯 = N_d×{2,3,6,12}", ladder == [88, 132, 264, 528])
check("F7c: 528 = C(33,2) = B²·33", comb == 528 and 16 * 33 == 528)
details["C_obs"] = C_obs
details["ladder"] = ladder

# ---------------- F8: 兩點信道 {row3, row18} ----------------
print("\n--- F8: 兩點信道 {row3,row18} (1-based) ---")
I2 = ba_channel(P, [2, 17]) / math.log(2)
print(f"  I(row3, row18) = {I2:.8f} bits (期望 0.43381827)")
check("F8: I(row3,row18) = 0.43381827 (1e-6)", abs(I2 - 0.43381827) < 1e-6, f"{I2:.8f}")
details["two_point_I"] = I2

print("\n" + "=" * 74)
print(f"  S01 總計: {sum(results)}/{len(results)} PASS")
print("=" * 74)

with open("data/01_anchor_fingerprints.json", "w") as f:
    json.dump({"checks": [bool(r) for r in results],
               "total": sum(results), "n": len(results),
               "details": details}, f, indent=1, ensure_ascii=False)

sys_exit = 0 if all(results) else 1
raise SystemExit(sys_exit)