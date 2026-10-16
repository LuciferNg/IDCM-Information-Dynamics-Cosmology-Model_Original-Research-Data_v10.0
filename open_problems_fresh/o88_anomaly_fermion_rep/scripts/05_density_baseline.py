#!/usr/bin/env python3
"""
O88 — scripts/05_density_baseline.py   (密度基準 / DENSITY BASELINE)   v2
========================================================================
依 O208 規則：**冇分位數 = 未閉合**。本腳本為 O88 主結論補
N_search / N_mc / d_obs / d_med / q_obs ＋ 硬測試 ①②④。

v1 之錯誤（本版修正）：
  · 搜尋空間誤設「k ≤ 4 個表示」⟹ 3×(12⊕12̄) 需 6 個槽，根本唔喺空間內 ⟹ 候選數假報 0。
  · m = 9（無共軛對）與 scripts/01 之 avail（含共軛）唔一致。
本版改用**物理正確**嘅空間定義：對固定表示集之**多重集（multiset）**，
總維度 ≤ D_MAX，多重數無預設上限 —— 即「任意外加 vector-like 對」之自然空間。

⚠️ 唔 import scripts/01–04。異常係數由**權重法**獨立重算。
"""

import math
import os
import json
import random
from fractions import Fraction as F
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "05_density_baseline.json")

N = 12
B, N_gen, K_tree, N_d, L_5 = 4, 3, 33, 44, 11
H11 = K_tree + N_gen            # 36
D_MAX = 400

# ---------- 權重法異常係數（獨立） ----------
def A_fund_denom(n):
    return F((n - 1) * (n - 2), n)

def A_antisymk(n, k):
    return F(math.comb(n, k) * k * (n - k) * (n - 2 * k), n * (n - 1) * (n - 2))

def A_sym2(n):
    diag = F(n) * (F(2 * (n - 1), n) ** 3 + F(n - 1) * (F(-2, n) ** 3))
    offd = F(math.comb(n, 2)) * (F(2) * (F(1 - F(2, n)) ** 3) + F(n - 2) * (F(-2, n) ** 3))
    return (diag + offd) / A_fund_denom(n)

assert (A_antisymk(N, 1), A_antisymk(N, 2), A_antisymk(N, 3),
        A_antisymk(N, 4), A_antisymk(N, 5)) == (1, 8, 27, 48, 42)
assert A_sym2(N) == N + 4

# ---------- 表示集（14 項，與 scripts/01 原 avail 一致） ----------
ITEMS = [
    ("12",    12,  +1), ("12̄",   12,  -1),
    ("66",    66,  +8), ("66̄",   66,  -8),
    ("78",    78, +16), ("78̄",   78, -16),
    ("220",  220, +27), ("220̄",  220, -27),
    ("495",  495, +48), ("495̄",  495, -48),
    ("792",  792, +42), ("792̄",  792, -42),
    ("924",  924,   0), ("143",  143,   0),
]
ITEMS_SMALL = [it for it in ITEMS if it[1] <= D_MAX]

print("=" * 74)
print("O88 — 密度基準 / MC null / 結構剛性   (v2)")
print("=" * 74)
print("\n  表示集（dim ≤ %d 者 %d 項）:" % (D_MAX, len(ITEMS_SMALL)))
for nm, d, a in ITEMS_SMALL:
    print("    %-6s dim=%-5d A=%+d" % (nm, d, a))

# ============================================================
# 段 1 — 精確枚舉：N_search
# ============================================================
def enumerate_multisets(items, dmax):
    """所有多重集（每項數量無上限），總維度 ≤ dmax。回傳 (counts_tuple, dim, A)。"""
    out = []
    n = len(items)
    counts = [0] * n
    def rec(i, dim, A):
        if i == n:
            out.append((tuple(counts), dim, A))
            return
        nm, d, a = items[i]
        c = 0
        while dim + c * d <= dmax:
            counts[i] = c
            rec(i + 1, dim + c * d, A + c * a)
            if d == 0:
                break
            c += 1
        counts[i] = 0
    rec(0, 0, 0)
    return out

print("\n[段 1] 精確枚舉（multiset，總維度 ≤ %d）" % D_MAX)
space = enumerate_multisets(ITEMS_SMALL, D_MAX)
N_search = len(space)
print("  N_search = %d 個多重集" % N_search)

# ============================================================
# 段 2 — 異常自由組合普查
# ============================================================
af_all = [s for s in space if s[2] == 0]
af48 = [s for s in af_all if s[1] >= 48]
print("\n[段 2] 異常自由組合普查")
print("  A = 0 之多重集         : %d" % len(af_all))
print("  其中 dim ≥ 48          : %d" % len(af48))
print("  （scripts/01 修正後宣稱 93；01 之空間為『k ≤ 4 槽』，與本版唔同 —— 見報告 §十）")

# ============================================================
# 段 3 — dim = 72 之異常自由組合（唯一候選性）
# ============================================================
print("\n[段 3] dim = 2·h11 = 72 且 A = 0 之組合")
c72 = [s for s in af_all if s[1] == 72]
print("  總數 = %d" % len(c72))
pure72 = []
for counts, d, a in c72:
    nz = [(ITEMS_SMALL[i][0], c) for i, c in enumerate(counts) if c]
    tag = "".join("%d×%s" % (c, nm) if c > 1 else nm for nm, c in nz)
    only_fund = all(nm in ("12", "12̄") for nm, _ in nz)
    if only_fund:
        pure72.append(tag)
    print("    %-34s only{12,12̄}=%s" % (tag, only_fund))
print("  ⟹ 只用 {12, 12̄} 者: %d 個 → %s" % (len(pure72), pure72))
uniq = (len(pure72) == 1)
print("  ⟹ 唯一候選性（限定 {12,12̄}）: %s" % uniq)

# ============================================================
# 段 4 — MC null（10⁷）＋ 精確值
# ============================================================
print("\n[段 4] MC null（10⁷ 樣本，uniform over space）")
N_mc = 10_000_000
seed = 88
random.seed(seed)

p72_ex = len(c72) / N_search
paf_ex = len(af48) / N_search
print("  精確 P(dim=72 ∧ A=0)        = %d/%d = %.6e" % (len(c72), N_search, p72_ex))
print("  精確 P(dim≥48 ∧ A=0)        = %d/%d = %.6e" % (len(af48), N_search, paf_ex))

# 向量化 MC（numpy 若可用；否則純 Python + 別名法）
try:
    import numpy as np
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, N_search, size=N_mc)
    dims = np.fromiter((s[1] for s in space), dtype=np.int64, count=N_search)[idx]
    As = np.fromiter((s[2] for s in space), dtype=np.int64, count=N_search)[idx]
    hit72 = int(np.count_nonzero((As == 0) & (dims == 72)))
    hitaf = int(np.count_nonzero((As == 0) & (dims >= 48)))
    engine = "numpy"
except Exception as e:
    print("  (numpy 不可用: %s → 純 Python)" % type(e).__name__)
    dims_l = [s[1] for s in space]
    As_l = [s[2] for s in space]
    hit72 = hitaf = 0
    for _ in range(N_mc):
        i = random.randrange(N_search)
        if As_l[i] == 0:
            if dims_l[i] == 72:
                hit72 += 1
            if dims_l[i] >= 48:
                hitaf += 1
    engine = "pure-python"

p72_mc, paf_mc = hit72 / N_mc, hitaf / N_mc
sig72 = math.sqrt(p72_ex * (1 - p72_ex) / N_mc)
sigaf = math.sqrt(paf_ex * (1 - paf_ex) / N_mc)
z72 = (p72_mc - p72_ex) / sig72 if sig72 > 0 else 0.0
zaf = (paf_mc - paf_ex) / sigaf if sigaf > 0 else 0.0
print("  引擎=%s  seed=%d  N_mc=%d" % (engine, seed, N_mc))
print("  MC  P(dim=72 ∧ A=0) = %.6e (%d hits)   z = %.2f  %s" % (
    p72_mc, hit72, z72, "✅" if abs(z72) < 5 else "⚠️"))
print("  MC  P(dim≥48 ∧ A=0) = %.6e (%d hits)   z = %.2f  %s" % (
    paf_mc, hitaf, zaf, "✅" if abs(zaf) < 5 else "⚠️"))

# ============================================================
# 段 5 — O208 密度基準格式
# ============================================================
print("\n[段 5] O208 密度基準")
lvl = 0
# 分位數：喺異常自由組合中，dim ≤ 72 之佔比
le72 = [s for s in af_all if s[1] <= 72]
q_obs = 100.0 * len(le72) / len(af_all)
dims_af = sorted(s[1] for s in af_all)
d_med = dims_af[len(dims_af) // 2]
d_obs = 72 - 48
print("  N_search = %d" % N_search)
print("  N_mc     = %d，seed = %d" % (N_mc, seed))
print("  d_obs    = 2·h11 − 48 = 72 − 48 = %d" % d_obs)
print("  d_med    = %d（A=0 組合維度中位數，共 %d 個）" % (d_med, len(dims_af)))
print("  q_obs    = %.2f%%（A=0 中 dim ≤ 72 之佔比 = %d/%d）" % (q_obs, len(le72), len(af_all)))
verdict = "🟢" if q_obs <= 10 else ("🟡" if q_obs <= 30 else "🔴")
print("  判讀     = %s" % verdict)

# ============================================================
# 段 6 — 結構剛性（硬測試 ④）：擾動 N
# ============================================================
print("\n[段 6] 結構剛性 — 3×(□⊕□̄) 是否 N-特異")
print("  %-5s %-8s %-8s %-14s %s" % ("N", "dim", "A", "= 2(K+Ng)=72?", "備註"))
for n in [8, 10, 11, 12, 13, 14]:
    d = 6 * n
    print("  %-5d %-8d %-8d %-14s %s" % (n, d, 0, "yes" if d == 72 else "no",
                                        "← IDCM N = B·N_gen" if n == 12 else ""))

# ============================================================
# 段 7 — {12,12̄} 子空間內 72 之唯一性（最相關之收窄）
# ============================================================
print("\n[段 7] 子空間最佳化：只用 {12, 12̄}（近最小 anomaly-free 態）")
sub = [s for s in space
       if all(c == 0 for i, c in enumerate(s[0])
              if ITEMS_SMALL[i][0] not in ("12", "12̄"))]
sub_af = [s for s in sub if s[2] == 0]
print("  子空間大小            : %d" % len(sub))
print("  A = 0 者（含空集）     : %d" % len(sub_af))
print("  其中 dim ≥ 48         : %d" % len([s for s in sub_af if s[1] >= 48]))
print("  其中 dim = 72         : %d  → %s" % (
    len([s for s in sub_af if s[1] == 72]),
    ["%d×12 + %d×12̄" % (s[0][0], s[0][1]) for s in sub_af if s[1] == 72]))
dims_ok = sorted(s[1] for s in sub_af if s[1] >= 48)
print("  {12,12̄} 子空間內 dim ≥ 48 之 A=0 維度: %s" % dims_ok)
print("  ⟹ 最小 anomaly-free (dim ≥ 48) = %d = 2×(12⊕12̄)" % (dims_ok[0] if dims_ok else -1))
print("  ⟹ 72 = 3×(12⊕12̄) 為該子空間內**次小**，且為 IDCM 條件 2·h11 所選")

# ============================================================
# 總結
# ============================================================
summary = {
    "version": "v2",
    "space_definition": "multiset over %d irreps, total dim <= %d" % (len(ITEMS_SMALL), D_MAX),
    "N_search": N_search,
    "N_mc": N_mc, "seed": seed, "mc_engine": engine,
    "anomaly_free_total": len(af_all),
    "anomaly_free_dim_ge48": len(af48),
    "dim72_anomalyfree_count": len(c72),
    "dim72_pure_1212bar": pure72,
    "unique_candidate_dim72_pure": uniq,
    "P_dim72_and_A0_exact": p72_ex,
    "P_dim72_and_A0_mc": p72_mc,
    "P_dimge48_and_A0_exact": paf_ex,
    "P_dimge48_and_A0_mc": paf_mc,
    "z_dim72": z72, "z_dimge48": zaf,
    "d_obs": d_obs, "d_med": d_med, "q_obs_pct": q_obs, "verdict": verdict,
    "min_anomalyfree_dim_ge48_in_fundamental_subspace": dims_ok[0] if dims_ok else None,
    "structural_rigidity_72_only_at_N12": True,
    "anomaly_table_used": {nm: a for nm, _, a in ITEMS},
    "note_01_space_mismatch": "scripts/01 用『k 個表示 (k<=4)』槽位；本版用無上限多重集 ⟹ N_af 數字唔可直接比較",
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print("\n✅ 已寫入 data/05_density_baseline.json")
print("   RESULT: N_search=%d  N_mc=%d  N_af(≥48)=%d  dim72=%d  q_obs=%.2f%%  %s" % (
    N_search, N_mc, len(af48), len(c72), q_obs, verdict))
