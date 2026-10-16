#!/usr/bin/env python3
"""
O88 — SU(12) Anomaly Coefficients 計算
========================================
計算 SU(12) 所有相關表示嘅 anomaly coefficient A(R)，
用於搵 anomaly-free 嘅 fermion 表示組合。

Anomaly formula for SU(N):
  A(□) = 1  (fundamental)
  A(□̄) = -1 (anti-fundamental)
  A(adj) = 0
  A(Λ²) = N - 4  (antisymmetric rank-2)
  A(Sym²) = N + 4  (symmetric rank-2)
  A(Λ³) = (N-3)(N-6)/2  (antisymmetric rank-3)
  For tensor product: A(R₁⊗R₂) = dim(R₂)·A(R₁) + dim(R₁)·A(R₂)

★ 後續修正 (2026-10-02, 由 scripts/04_audit_independent.py 獨立審計觸發):
  原 Λ⁴ / Λ⁵ 之封閉式
      A(Λ⁴) = (N-3)(N-6)(N-10)/6          → N=12 得 18   ❌
      A(Λ⁵) = (N-3)(N-6)(N-10)(N-15)/24   → N=12 得 -13.5, 經 `//` 地板除出 -14 ❌
  兩式**不成立**（Λ⁵ 一式更給出非整數，地板除把錯誤隱藏）。
  正解（用權重法 A(R) = Σ_{λ∈R}Σ_i λ_i³ / [(N-1)(N-2)/N] 獨立推導，並與封閉式雙路徑互證）：
      A(Λ^k) = C(N,k) · k(N−k)(N−2k) / [ N(N−1)(N−2) ]
  N=12 正典值：Λ¹..Λ¹¹ = 1, 8, 27, **48**, **42**, 0, −42, −48, −27, −8, −1
  （即記錄之 Λ⁴=18、Λ⁵=−14 兩項有誤；其餘項與本式一致。）
  原文保留（記錄當時認知）；正典全表見 data/04_audit_independent.json。
"""

import json, os, math, itertools

N = 12  # SU(12)

# ============================================================
# 表示維度計算
# ============================================================
def dim_fund(N):
    return N

def dim_antifund(N):
    return N

def dim_adj(N):
    return N**2 - 1

def dim_antisym2(N):
    return N*(N-1)//2

def dim_sym2(N):
    return N*(N+1)//2

def dim_antisym3(N):
    return N*(N-1)*(N-2)//6

def dim_antisym4(N):
    return N*(N-1)*(N-2)*(N-3)//24

def dim_antisym5(N):
    return N*(N-1)*(N-2)*(N-3)*(N-4)//120

# ============================================================
# Anomaly Coefficients (A(R))
# ============================================================
def A_fund(N):
    return 1

def A_antifund(N):
    return -1

def A_adj(N):
    return 0

def A_antisym2(N):
    return N - 4

def A_sym2(N):
    return N + 4

def A_antisym3(N):
    return (N-3)*(N-6)//2

def A_antisymk(N, k):
    """A(Λ^k) = C(N,k)·k(N−k)(N−2k) / [N(N−1)(N−2)]   （權重法推導，精確有理）

    ★ 2026-10-02 修正：取代原 A_antisym4 / A_antisym5 之錯誤封閉式。
    """
    from fractions import Fraction
    num = math.comb(N, k) * k * (N - k) * (N - 2 * k)
    den = N * (N - 1) * (N - 2)
    return Fraction(num, den)

def A_antisym4(N):
    """★ 2026-10-02 修正：原 (N-3)(N-6)(N-10)//6 得 18（錯），正解 48。"""
    return A_antisymk(N, 4)

def A_antisym5(N):
    """★ 2026-10-02 修正：原 (N-3)(N-6)(N-10)(N-15)//24 得 −13.5 → 地板除 −14（錯），正解 42。"""
    return A_antisymk(N, 5)

# ============================================================
# Tensor product anomaly
# ============================================================
def A_tensor(dim_R1, A_R1, dim_R2, A_R2):
    """A(R₁⊗R₂) = dim(R₂)·A(R₁) + dim(R₁)·A(R₂)"""
    return dim_R2 * A_R1 + dim_R1 * A_R2

# ============================================================
# 表示目錄
# ============================================================
reps = {}

# 基本表示
reps['12'] = {'dim': dim_fund(N), 'A': A_fund(N), 'label': '□', 'young': [1]}
reps['12̄'] = {'dim': dim_antifund(N), 'A': A_antifund(N), 'label': '□̄', 'young': [1,1,1,1,1,1,1,1,1,1,1]}
reps['143'] = {'dim': dim_adj(N), 'A': A_adj(N), 'label': 'adj', 'young': [2,1,1,1,1,1,1,1,1,1,1]}
reps['66'] = {'dim': dim_antisym2(N), 'A': A_antisym2(N), 'label': 'Λ²', 'young': [1,1]}
reps['78'] = {'dim': dim_sym2(N), 'A': A_sym2(N), 'label': 'Sym²', 'young': [2]}
reps['220'] = {'dim': dim_antisym3(N), 'A': A_antisym3(N), 'label': 'Λ³', 'young': [1,1,1]}
reps['495'] = {'dim': dim_antisym4(N), 'A': A_antisym4(N), 'label': 'Λ⁴', 'young': [1,1,1,1]}
reps['792'] = {'dim': dim_antisym5(N), 'A': A_antisym5(N), 'label': 'Λ⁵', 'young': [1,1,1,1,1]}

# 注意: Λ⁶(12) = Λ⁶⁻κ(12) 通過對偶 → Λ⁶ = Λ⁶(12) = 924, self-dual for N=12
# 12 choose 6 = 924
# Λ⁶(12) = 924, A(Λ⁶) = 0 (self-dual for even N/2)

dim_antisym6 = dim_antisym3(N) * dim_antisym3(N)  # Hodge dual
# Actually just compute: C(12, 6) = 924
def comb(n, k):
    return math.comb(n, k)
dim_antisym6 = comb(12, 6)
reps['924'] = {'dim': dim_antisym6, 'A': 0, 'label': 'Λ⁶', 'young': [1]*6}
# For SU(N), Λ^k is equivalent to Λ^{N-k}*, so when N=12, Λ^6 is self-dual and has A=0

# 12⊗12̄ = 1 ⊕ 143
# A(12⊗12̄) = dim(12̄)·A(12) + dim(12)·A(12̄) = 12·1 + 12·(-1) = 0
# This checks out: A(1) + A(143) = 0 + 0 = 0 OK

# 12⊗12 = 66 ⊕ 78
# A(12⊗12) = 12·A(12) + 12·A(12) = 12+12 = 24
# A(66) + A(78) = 8 + 16 = 24 ✓

# 12̄⊗12̄ = 66̄ ⊕ 78̄
# A(66̄) = -A(66) = -8, A(78̄) = -A(78) = -16

# ============================================================
# 驗證 tensor product anomaly 加法定則
# ============================================================
print("=" * 72)
print("O88 — SU(12) Anomaly Coefficients")
print("=" * 72)

print(f"\nN = {N} (SU({N}))")
print(f"\n{'表示':>8} | {'維度':>6} | {'A(R)':>6} | {'Young':>12} | {'對偶':>8}")
print("-" * 52)
for name, data in reps.items():
    dual = name + '̄' if '̄' not in name else name.replace('̄', '')
    if name == '924':
        dual = '924 (self-dual)'
    print(f"{name:>8} | {data['dim']:>6} | {data['A']:>+6} | {data['label']:>12} | {dual:>8}")

# ============================================================
# Tensor product decomposition checks
# ============================================================
print("\n\n[V] Tensor Product Anomaly Sum Rules:")
print("-" * 52)

# 12⊗12 = 66⊕78
A_12x12 = A_tensor(12, 1, 12, 1)
check_12x12 = (A_12x12 == reps['66']['A'] + reps['78']['A'])
print(f"  A(12⊗12) = {A_12x12:>+3}; A(66)+A(78) = {reps['66']['A']+reps['78']['A']:>+3} → {'✅' if check_12x12 else '❌'}")

# 12⊗12̄ = 1⊕143
A_12x12bar = A_tensor(12, 1, 12, -1)
check_12x12bar = (A_12x12bar == 0)
print(f"  A(12⊗12̄) = {A_12x12bar:>+3}; A(1)+A(143) = 0 → {'✅' if check_12x12bar else '❌'}")

# 12⊗66 = 12⊕... 
# 12⊗66 = 12 ⊕ 220 ⊕ 572 (standard decomposition)
# A(12⊗66) = dim(12)·A(66) + dim(66)·A(12) = 12·8 + 66·1 = 96+66 = 162
A_12x66 = A_tensor(12, 1, 66, 8)
# Decomposition: 12⊗66 = 12 ⊕ 220 ⊕ 572
# A(12) + A(220) + A(572) should equal 162
# Need A(572) for this check
# 572 = Λ²(12)⊗12 with projection... Actually I need to compute A(572) properly
# 572 appears in 12⊗66 = 12 ⊕ 220 ⊕ 572
# 572 = 12⊗66 - 12 - 220 (dim check: 12*66 = 792, 792-12-220 = 560... hmm)
# Actually 12⊗66 = 12 ⊕ 220 ⊕ 572? Let me double-check
# dim(12) = 12, dim(66) = 66, 12×66 = 792
# 12 + 220 + 572 = 12 + 220 + 572 = 804... doesn't work
# Let me just note what we know

print(f"  A(12⊗66) = {A_12x66:>+4} (dim check: 12×66 = {12*66})")

# 12̄⊗66 = 12̄ ⊕ 220̄ ⊕ 572̄
# A(12̄⊗66) = dim(12̄)·A(66) + dim(66)·A(12̄) = 12·8 + 66·(-1) = 96-66 = 30
A_12barx66 = A_tensor(12, -1, 66, 8)
print(f"  A(12̄⊗66) = {A_12barx66:>+4}")

# ============================================================
# Anomaly-free combinations search
# ============================================================
print("\n\n" + "=" * 72)
print("Anomaly-Free Combination Search")
print("=" * 72)

# We need to find combinations of representations that:
# 1. Sum of A(R) = 0 (anomaly-free)
# 2. Total dimension is at least 48 (3 generations × 16 Weyl fermions)
# 3. Can contain 3×(4,2,1) ⊕ 3×(4̄,1,2) SM content

# Available representations with their (dim, A):
# ★ 2026-10-02 修正（二）：原字典**硬編碼** '495': (495, 55)、'792': (792, 78)，
#   與 reps 表（當時為 18 / −14）及權重法正解（48 / 42）**三者皆唔同**。
#   同一支 script 內同一物理量出現三個唔同值 ⟹ 組合搜尋結果受污染。
#   現改為由 reps 表單一來源導出，並用**顯式共軛表**避免二次共軛產生幽靈鍵（如 '12̄̄'）。
_CONJ = {'12': '12̄', '66': '66̄', '78': '78̄', '220': '220̄',
         '495': '495̄', '792': '792̄'}
avail = {}
for _n, _d in reps.items():
    avail[_n] = (_d['dim'], _d['A'])
for _n, _c in _CONJ.items():
    if _c not in avail and _n in reps:
        avail[_c] = (reps[_n]['dim'], -reps[_n]['A'])

# Strategy: search for combinations with small total dimension
# that are anomaly-free
# 
# Key constraint: 3 generations → 3 × 16 = 48 Weyl fermions
# But SU(12) representations may contain extra vector-like pairs
# that get mass at high scales
#
# Most natural: 3×(12⊕12̄) = 72 dim, anomaly-free
# Contains 3×(4⊕4̄) = 3×8 = 24 states per generation direction
# But we need 16 per generation...

# Let's search more systematically
print("\nSearching minimal anomaly-free combinations...")
print(f"{'組合':>40} | {'總維度':>6} | {'A':>6} | {'≥48?':>6}")
print("-" * 72)

# Simple combinations first
combos = []
for name, (d, a) in avail.items():
    combos.append((f"{name}", d, a))

# Check 12⊕12̄
d12 = 12; a12 = 1
d12b = 12; a12b = -1
if d12 + d12b >= 48:
    print(f"{'12⊕12̄':>40} | {d12+d12b:>6} | {a12+a12b:>+6} | {'✅' if d12+d12b>=48 else '❌':>6}")
else:
    print(f"{'12⊕12̄':>40} | {d12+d12b:>6} | {a12+a12b:>+6} | {'❌':>6}")

# 2×(12⊕12̄) = 48
d2 = 2*(12+12)
a2 = 2*(1-1)
print(f"{'2×(12⊕12̄) = 48':>40} | {d2:>6} | {a2:>+6} | {'✅' if d2>=48 else '❌':>6}")

# 3×(12⊕12̄) = 72
d3 = 3*(12+12)
a3 = 3*(1-1)
print(f"{'3×(12⊕12̄) = 72':>40} | {d3:>6} | {a3:>+6} | {'✅' if d3>=48 else '❌':>6}")

# 12⊕12̄⊕66⊕66̄
d = 12+12+66+66
a = 1-1+8-8
print(f"{'12⊕12̄⊕66⊕66̄':>40} | {d:>6} | {a:>+6} | {'✅' if d>=48 else '❌':>6}")

# 12⊕12̄⊕78⊕78̄
d = 12+12+78+78
a = 1-1+16-16
print(f"{'12⊕12̄⊕78⊕78̄':>40} | {d:>6} | {a:>+6} | {'✅' if d>=48 else '❌':>6}")

# 12⊕12̄⊕66⊕78 = 12+12+66+78 = 168
d = 12+12+66+78
a = 1-1+8+16
print(f"{'12⊕12̄⊕66⊕78':>40} | {d:>6} | {a:>+6} | {'✅' if d>=48 else '❌':>6}")

# 3×12 ⊕ 3×12̄ = 72
d = 3*12 + 3*12
a = 3*1 + 3*(-1)
print(f"{'3×12 ⊕ 3×12̄ = 72':>40} | {d:>6} | {a:>+6} | {'✅' if d>=48 else '❌':>6} {'★最自然':>10}")

# 12⊕66⊕12̄⊕66̄ = 12+66+12+66 = 156
d = 12+66+12+66
a = 1+8-1-8
print(f"{'12⊕66⊕12̄⊕66̄':>40} | {d:>6} | {a:>+6} | {'✅' if d>=48 else '❌':>6}")

# 12⊕66⊕78 = 12+66+78 = 156
d = 12+66+78
a = 1+8+16
# Need A = 0, so need -25 somewhere
# 12⊕66⊕78⊕220̄ = 12+66+78+220 = 376
d = 12+66+78+220
a = 1+8+16-27
print(f"{'12⊕66⊕78⊕220̄':>40} | {d:>6} | {a:>+6} | {'✅' if d>=48 else '❌':>6}")

# 3×12⊕3×66⊕... no, this gets huge
# Let's be systematic: the simplest anomaly-free combinations
# that contain at least 48 Weyl fermions

print("\n\nSystematic search (small combinations):")
print(f"{'#':>3} | {'組合':>40} | {'總維度':>6} | {'A':>6} | {'≥48?':>6}")
print("-" * 72)

rep_names = list(avail.keys())
rep_data = [avail[n] for n in rep_names]
found = 0
results = []

# For small combinations (up to 4 copies of each rep)
for n_copies in range(1, 5):
    for combo in itertools.combinations_with_replacement(range(len(rep_names)), n_copies):
        # Check if this combo is worth analyzing
        total_dim = sum(rep_data[i][0] for i in combo)
        total_A = sum(rep_data[i][1] for i in combo)
        
        if total_A == 0 and total_dim >= 48:
            name = '+'.join(rep_names[i] for i in combo)
            # Count copies
            from collections import Counter
            counts = Counter(rep_names[i] for i in combo)
            name_compact = '+'.join(f"{c}×{n}" if c > 1 else n for n, c in counts.items())
            results.append((total_dim, name_compact, combo))
            found += 1

# Sort by total dimension
results.sort()
for r in results[:15]:
    print(f"{r[0]:>3} | {r[1]:>40} | {r[0]:>6} | {0:>+6} | {'✅':>6}")

print(f"\nFound {found} anomaly-free combinations with dim ≥ 48 (showing top 15 by dim)")

# ============================================================
# 重點: 3×(12⊕12̄) 的 anomaly-free 性質
# ============================================================
print("\n\n" + "=" * 72)
print("★ 推薦: 3×(12⊕12̄) — Anomaly-Free, Dim=72")
print("=" * 72)
print(f"""
  A(3×12 = 36) = 3×A(12) = 3×1 = +3
  A(3×12̄ = 36) = 3×A(12̄) = 3×(-1) = -3
  A(total) = 0 ✓
  
  總維度 = 72 (大於 SM 48 個 Weyl fermions)
  多出 24 個 vector-like 配對 → 高能標度獲得質量

  3×(12⊕12̄) 嘅 IDCM 對應:
    36 = 3×12 = h11 = K_tree + N_gen = 33+3 ✓
    36̄ = 3×12̄ = h11̄ = ...
""")

# ============================================================
# 保存結果
# ============================================================
results_data = {
    'N': N,
    'reps': {name: {'dim': data['dim'],
                      'A': int(data['A']) if getattr(data['A'], 'denominator', 1) == 1
                           else float(data['A'])} for name, data in reps.items()},
    'tensor_product_checks': {
        '12x12_to_66_and_78': {
            'A_12x12': A_12x12,
            'A_66_plus_78': reps['66']['A'] + reps['78']['A'],
            'pass': check_12x12
        },
        '12x12bar_to_1_and_143': {
            'A_12x12bar': A_12x12bar,
            'pass': check_12x12bar
        }
    },
    'recommended_combination': {
        'name': '3×(12⊕12̄)',
        'total_dim': 72,
        'total_A': 0,
        'anomaly_free': True,
        'idcm_connection': '36 = 3×12 = h11 = K_tree + N_gen = 33+3'
    },
    'anomaly_free_combos_found': found,
}

# ★ 2026-10-02 路徑衛生修正：原本硬編碼 ghost tree 路徑，改 __file__-相對
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_path = os.path.join(BASE_DIR, 'data', '01_anomaly_coefficients.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(results_data, f, indent=2)

print(f"\n✅ 結果已保存: data/01_anomaly_coefficients.json")