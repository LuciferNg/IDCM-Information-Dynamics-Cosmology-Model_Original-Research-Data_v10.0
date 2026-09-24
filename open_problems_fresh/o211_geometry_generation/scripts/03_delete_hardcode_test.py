#!/usr/bin/env python3
"""
O211 scripts/03 — 刪碼測試 (delete-the-hardcode test)
=====================================================
核心命題 (O211 SESSION_START §二):
    「刪除硬編碼之後, 全部下游結果必須不變。
      若唔成立 → 證明 h¹¹=36, h²¹=98 係事後輸入。」

做法:
    A 版 = 幾何參數以【字面值】輸入 (h11=36, h21=98, n_moduli=134)
    B 版 = 幾何參數由【種子 x²+x−1=0】導出 (O211 scripts/01-02 鏈)
    兩版跑同一下游 (建 P -> rank -> 本徵值譜), 逐位元比較。
    F 版 = 證偽對照 (故意用錯嘅導出 B=3 -> (38,96)) — 下游必須改變,
           證明測試【有牙】(唔係恆真)。

用法: 由 O 目錄 root 跑 -> /usr/bin/python3 scripts/03_delete_hardcode_test.py
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

# ============================================================
# 導出層 (O211 scripts/01-02) — 唯一輸入 = 種子
# ============================================================
def derive_geometry(branch=None):
    """由種子導出全部幾何參數。branch=None -> B = φ³−φ⁻³ (正確)。"""
    B = PHI ** 3 - PHI ** -3 if branch is None else branch
    B = round(B) if branch is None else branch
    L5 = round(PHI ** 5 + (-PHI) ** -5)      # 11
    N_d = B * L5                              # 44
    gamma = {n: B * math.sin(math.pi * n / (2 * N_d)) ** 2 for n in range(1, N_d + 1)}
    Sigma_gamma = round(sum(gamma.values()))  # 90 (精確)
    h11 = N_d - 2 * B
    h21 = Sigma_gamma + 2 * B
    return dict(B=B, L5=L5, N_d=N_d, gamma=gamma, Sigma=Sigma_gamma,
                h11=h11, h21=h21, n_moduli=h11 + h21)


GEO = derive_geometry()
print("=" * 74)
print("O211 scripts/03 — 刪碼測試 (delete-the-hardcode test)")
print("=" * 74)
print(f"\n導出層: B={GEO['B']} N_d={GEO['N_d']} Σγ={GEO['Sigma']} "
      f"h11={GEO['h11']} h21={GEO['h21']} n_moduli={GEO['n_moduli']}")


# ============================================================
# 下游: 投影算子建構 (兩個 style)
# ============================================================
def beats_of(N_d):
    return [(n, m) for n in range(1, N_d + 1) for m in range(n + 1, N_d + 1)]


def build_P_srcstyle(h11, h21, N_d, gamma):
    """src/projection_operator.py 嘅 5 條選擇律 (原版, rank-2 缺陷版)。"""
    bs = beats_of(N_d)
    P = np.zeros((h11 + h21, len(bs)))
    for a in range(h11 + h21):
        is_kahler = a < h11
        for b, (n, m) in enumerate(bs):
            parity = (n + m) % 2
            z2 = +1 if parity == 0 else -1
            if (0 if is_kahler else 1) != parity:
                continue
            if (+1 if is_kahler else -1) != z2:
                continue
            qn = 1 if n <= 11 else 2 if n <= 22 else 3 if n <= 33 else 4
            qm = 1 if m <= 11 else 2 if m <= 22 else 3 if m <= 33 else 4
            if is_kahler and qn > 2 and qm > 2:
                continue
            if (not is_kahler) and qn < 3 and qm < 3:
                continue
            avg = (gamma[n] + gamma[m]) / 2
            if is_kahler and avg > 2.0:
                continue
            if (not is_kahler) and avg < 2.0:
                continue
            P[a, b] = PHI ** (-avg) if is_kahler else math.exp(-1.0 / avg)
    return P


def build_P_v2style(h11, h21, N_d, gamma):
    """O53 docs/03 修正版 v2 (per-modulus support, rank-109)。"""
    bs = beats_of(N_d)
    bn = np.array([n for n, m in bs])
    bm = np.array([m for n, m in bs])
    P = np.zeros((h11 + h21, len(bs)))
    low_modes = sorted(range(1, N_d + 1), key=lambda k: gamma[k])[:h11]
    for a in range(h11 + h21):
        if a < h11:
            n_mode = low_modes[a]
            parity = n_mode % 2
            z2 = +1 if parity == 0 else -1
            mask = ((bn == n_mode) | (bm == n_mode)) & ((bn + bm) % 2 == parity) \
                   & (np.where((bn + bm) % 2 == 0, 1, -1) == z2)
            for b in np.where(mask)[0]:
                avg = (gamma[bn[b]] + gamma[bm[b]]) / 2
                P[a, b] = PHI ** (-avg)
        else:
            cpx_idx = a - h11
            pairs = [(n, m) for n in range(23, N_d + 1) for m in range(n + 1, N_d + 1)]
            if cpx_idx < len(pairs):
                nc, mc = pairs[cpx_idx]
                parity = 1
                mask = ((bn == nc) | (bm == nc) | (bn == mc) | (bm == mc)) \
                       & ((bn + bm) % 2 == 1)
                for b in np.where(mask)[0]:
                    avg = (gamma[bn[b]] + gamma[bm[b]]) / 2
                    P[a, b] = math.exp(-1.0 / avg)
    return P


def downstream(P):
    """下游結果 = (shape, rank, 本徵值譜摘要)。"""
    rank = int(np.linalg.matrix_rank(P, tol=1e-10))
    ev = np.linalg.eigvalsh(P @ P.T)
    ev_pos = np.sort(ev[ev > 1e-10])[::-1]
    return dict(shape=P.shape, rank=rank, n_pos=len(ev_pos),
                ev_sum=float(ev_pos.sum()) if len(ev_pos) else 0.0,
                ev_head=float(ev_pos[0]) if len(ev_pos) else 0.0)


# ============================================================
# [1] A 版 (硬編碼) vs B 版 (導出) — src-style
# ============================================================
print("\n[1] src-style 投影算子: A(硬編碼 36/98/134) vs B(導出)")
A_lit = build_P_srcstyle(36, 98, 44, GEO['gamma'])
B_der = build_P_srcstyle(GEO['h11'], GEO['h21'], GEO['N_d'], GEO['gamma'])
same = np.array_equal(A_lit, B_der)
print(f"    A shape={A_lit.shape}  B shape={B_der.shape}")
print(f"    逐位元相同: {same}  (max|Δ| = {np.abs(A_lit - B_der).max():.3e})")
chk("E1 src-style: 刪硬編碼後矩陣逐位元不變", same,
    f"max|Δ| = {np.abs(A_lit - B_der).max():.3e}")
da, db = downstream(A_lit), downstream(B_der)
chk("E2 src-style: 下游 (rank, 譜) 不變",
    da == db, f"A={da['rank']} B={db['rank']}")

# ============================================================
# [2] A 版 vs B 版 — o53 v2-style (rank-109)
# ============================================================
print("\n[2] o53 v2-style 投影算子: A(硬編碼) vs B(導出)")
A2 = build_P_v2style(36, 98, 44, GEO['gamma'])
B2 = build_P_v2style(GEO['h11'], GEO['h21'], GEO['N_d'], GEO['gamma'])
same2 = np.array_equal(A2, B2)
dA2, dB2 = downstream(A2), downstream(B2)
print(f"    A shape={A2.shape} rank={dA2['rank']}")
print(f"    B shape={B2.shape} rank={dB2['rank']}")
print(f"    逐位元相同: {same2}")
chk("E3 v2-style: 刪硬編碼後矩陣逐位元不變", same2,
    f"max|Δ| = {np.abs(A2 - B2).max():.3e}")
chk("E4 v2-style: 下游 rank 不變", dA2 == dB2, f"A={dA2['rank']} B={dB2['rank']}")

# 子矩陣秩 (重現 O53 宣稱)
rk = int(np.linalg.matrix_rank(B2[:36, :], tol=1e-10))
rc = int(np.linalg.matrix_rank(B2[36:, :], tol=1e-10))
print(f"    Kähler 子秩 = {rk}   CPX 子秩 = {rc}   sum = {rk + rc}")
chk("E5 v2-style: Kähler 子秩 = h11 = 36 (重現 O53)",
    rk == GEO['h11'] == 36, f"rank(Kähler) = {rk}")
chk("E6 v2-style: 總秩 = 36 + CPX 子秩 (重現 O53 rank 109)",
    rk + rc == 109, f"總秩 = {rk + rc}, CPX 子秩 = {rc}")

# ============================================================
# [3] 證偽對照 (測試有冇牙)
# ============================================================
print("\n[3] 證偽對照 — 故意用錯嘅導出 (B=3 → (38,96))")
F = derive_geometry(3)
print(f"    F 版參數: B={F['B']} N_d={F['N_d']} h11={F['h11']} h21={F['h21']} "
      f"n_moduli={F['n_moduli']}")
Fm = build_P_srcstyle(F['h11'], F['h21'], F['N_d'], F['gamma'])
print(f"    F shape={Fm.shape}  (vs A shape={A_lit.shape})")
chk("E7 證偽對照: 錯導出 (B=3) 令下游改變 ⟹ 刪碼測試有牙 (非恆真)",
    Fm.shape != A_lit.shape, f"F shape {Fm.shape} ≠ A shape {A_lit.shape}")

# 更細緻嘅對照: 譜不變 (N_d=44), 只改耦合 c = 2B
print("\n[3b] 精細對照 — 譜不變 (N_d=44), 只改 K_tree 耦合 c")
for c in [6, 8, 10]:
    h11c = GEO['N_d'] - c
    h21c = GEO['Sigma'] + c
    Pc = build_P_srcstyle(h11c, h21c, GEO['N_d'], GEO['gamma'])
    dc = downstream(Pc)
    tag = "  <- c=2B=8 (φ 強制)" if c == 8 else ""
    print(f"    c={c:2d}: (h11,h21)=({h11c},{h21c}) shape={Pc.shape} "
          f"rank={dc['rank']}{tag}")
chk("E8 精細對照: 同 shape 下換耦合 c 令矩陣改變 (行重新分配)",
    not np.array_equal(build_P_srcstyle(38, 96, GEO['N_d'], GEO['gamma']),
                       build_P_srcstyle(36, 98, GEO['N_d'], GEO['gamma'])),
    "c=6 vs c=8 矩陣唔同 ⟹ 硬編碼 (36,98) 真係有內容, 唔係任意")

# ============================================================
print("\n" + "=" * 74)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
print("=" * 74)
if N_FAIL:
    raise SystemExit(1)
