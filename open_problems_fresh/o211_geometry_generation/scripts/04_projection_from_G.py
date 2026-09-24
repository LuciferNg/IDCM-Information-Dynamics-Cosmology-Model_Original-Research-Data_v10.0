#!/usr/bin/env python3
"""
O211 scripts/04 — 投影算子 P 由 G 導出 (R4)
==========================================
目標: 由生成算子 G 嘅譜數據導出 P, 取代人手設定嘅 134×946。
關鍵: 秩結構 (rank) 由【支撐模式】決定, 唔由權重決定 (O53 docs/03 教訓:
      「行縮放唔會改變秩」) ⟹ 導出支撐 = 導出秩結構。

本 script 誠實測試:
  (a) Kähler 行指標集 = {n : 對偶(n) = N_d − n ≥ 2B} = {1..36} (由 G 導出, 零硬編碼)
  (b) 秩對【CPX 建構選擇】嘅敏感度 — 109 係結構值定建構偽影?
  (c) 候選 25 = #{γ_n < 5/2} 嘅機制檢查

用法: 由 O 目錄 root 跑 -> /usr/bin/python3 scripts/04_projection_from_G.py
"""
import math
import numpy as np

N_PASS = 0
N_FAIL = 0


def chk(label, cond, detail=""):
    global N_PASS, N_FAIL
    ok = bool(cond)
    if ok:
        N_PASS += 1
        mark = "PASS"
    else:
        N_FAIL += 1
        mark = "FAIL"
    print(f"  [{mark}] {label}" + (f"   -- {detail}" if detail else ""))


PHI = (1 + math.sqrt(5)) / 2
B = round(PHI ** 3 - PHI ** -3)
L5 = round(PHI ** 5 + (-PHI) ** -5)
N_d = B * L5
GAMMA = {n: B * math.sin(math.pi * n / (2 * N_d)) ** 2 for n in range(1, N_d + 1)}
SIGMA = round(sum(GAMMA.values()))
H11 = N_d - 2 * B
H21 = SIGMA + 2 * B

print("=" * 74)
print("O211 scripts/04 — 投影算子 P 由 G 導出")
print("=" * 74)
print(f"\nG 導出: B={B} N_d={N_d} Σγ={SIGMA} h11={H11} h21={H21} 134={H11 + H21}")

BEATS = [(n, m) for n in range(1, N_d + 1) for m in range(n + 1, N_d + 1)]
BN = np.array([n for n, m in BEATS])
BM = np.array([m for n, m in BEATS])
PAR = (BN + BM) % 2
print(f"beat 空間: {len(BEATS)} = C({N_d},2) = Λ²(R^{N_d})   "
      f"even {int((PAR == 0).sum())} / odd {int((PAR == 1).sum())}")

# ============================================================
# [1] Kähler 行指標集 — 由 G 導出 (零硬編碼)
# ============================================================
print("\n[1] Kähler 行指標集 — 由 G 嘅 Z₂ 對偶導出")
active = [n for n in range(1, N_d + 1) if (N_d - n) >= 2 * B]
print(f"    規則: 保留 n  iff  對偶(n) = N_d − n ≥ 2B = {2 * B}")
print(f"    active set = {active[0]}..{active[-1]}  (|active| = {len(active)})")
chk("F1 Kähler 行指標集 = {n : N_d−n ≥ 2B} = {1..36}, |set| = h11",
    active == list(range(1, 37)) and len(active) == H11,
    f"|active| = {len(active)} = h11 = {H11}")
chk("F2 規則零硬編碼 (2B 同 N_d 都由種子導出)",
    (N_d, 2 * B) == (44, 8), f"N_d={N_d}, 2B={2 * B}")

# ============================================================
# [2] 建 P (Kähler 行由 G;  CPX 行 = 高能帶 pair)
# ============================================================
def build_P(active_modes, cpx_pairs, weights=True):
    P = np.zeros((H11 + H21, len(BEATS)))
    for a, n_mode in enumerate(active_modes):
        par = n_mode % 2
        z2 = +1 if par == 0 else -1
        mask = ((BN == n_mode) | (BM == n_mode)) & (PAR == par) \
               & (np.where(PAR == 0, 1, -1) == z2)
        for b in np.where(mask)[0]:
            avg = (GAMMA[BN[b]] + GAMMA[BM[b]]) / 2
            P[a, b] = PHI ** (-avg) if weights else 1.0
    for i, (nc, mc) in enumerate(cpx_pairs):
        if i >= H21:
            break
        mask = ((BN == nc) | (BM == nc) | (BN == mc) | (BM == mc)) & (PAR == 1)
        for b in np.where(mask)[0]:
            avg = (GAMMA[BN[b]] + GAMMA[BM[b]]) / 2
            P[H11 + i, b] = math.exp(-1.0 / avg) if weights else 1.0
    return P


def rank_of(P):
    return int(np.linalg.matrix_rank(P, tol=1e-10))


# CPX pair 池候選
pool_23 = [(n, m) for n in range(23, N_d + 1) for m in range(n + 1, N_d + 1)]
pool_energy = sorted(((n, m) for n, m in BEATS
                      if (GAMMA[n] + GAMMA[m]) / 2 > 2.0),
                     key=lambda t: (GAMMA[t[0]] + GAMMA[t[1]]))
pool_all = sorted(BEATS, key=lambda t: (GAMMA[t[0]] + GAMMA[t[1]]), reverse=True)

print(f"\n    CPX 池大小: 23..44 pairs = {len(pool_23)}, 高能(avg γ>2) = {len(pool_energy)}, "
      f"全排序 = {len(pool_all)}")

results = {}
for name, pool in [("O53 v2 (23..44 前 98)", pool_23),
                   ("G-natural (高能排序前 98)", pool_energy),
                   ("G-natural (全排序最高 98)", pool_all)]:
    P = build_P(active, pool)
    r = rank_of(P)
    rk = rank_of(P[:H11, :])
    rc = rank_of(P[H11:, :])
    results[name] = (r, rk, rc)
    print(f"    {name:28s}: rank={r:3d}  (Kähler {rk}, CPX {rc})")

r_53 = results["O53 v2 (23..44 前 98)"][0]
chk("F3 O53 v2 建構重現 rank = 109 (獨立重算, 唔信 sibling 數字)",
    r_53 == 109, f"rank = {r_53}")
chk("F4 Kähler 子秩 = 36 = h11 (全部建構一致)",
    all(v[1] == 36 for v in results.values()),
    f"Kähler 子秩 = {[v[1] for v in results.values()]}")

# ============================================================
# [3] 秩對建構嘅敏感度 (誠實)
# ============================================================
print("\n[3] 秩對 CPX 建構嘅敏感度 (誠實評級)")
ranks = sorted(set(v[0] for v in results.values()))
print(f"    三種 G-相容建構嘅總秩: {ranks}")
print(f"    ⟹ rank 109 {'係' if len(ranks) == 1 else '唔係'} 建構無關嘅結構值")
chk("F5 誠實標記: rank 109 係【建構相關】(CPX 池選擇改變秩) ⟹ R4 標 🟡",
    len(ranks) > 1, f"觀察到秩 = {ranks}")

# ============================================================
# [4] 候選 25 = #{γ_n < 5/2} 機制檢查
# ============================================================
print("\n[4] CPX 秩缺口 25 嘅機制候選")
c25 = [n for n in range(1, N_d + 1) if GAMMA[n] < 2.5]
print(f"    #{'γ_n < 5/2':>12} = {len(c25)}  (n = 1..{max(c25)})")
print(f"    CPX 秩缺口 (O53) = 98 − 73 = 25")
print(f"    ⚠️ 臨界值 5/2 冇獨立導出 ⟹ 標 🔴 候選, 唔宣稱機制")
chk("F6 候選記錄: #{γ<5/2} = 25 (數值命中, 但閾值 5/2 未導出)",
    len(c25) == 25, "🔴 候選 — 需機制, 見 docs/05")

# 鄰域敏感度: 閾值微擾
for t in [2.4, 2.45, 2.5, 2.55, 2.6]:
    print(f"      #{'γ<'+str(t):>9} = {sum(1 for n in range(1, N_d + 1) if GAMMA[n] < t)}")

# ============================================================
print("\n" + "=" * 74)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
print("=" * 74)
if N_FAIL:
    raise SystemExit(1)
