"""
O72 攻堅 12: 44 唯一性深度測試 — 喺「IDCM 閉合網絡」入面 44 係咪特殊?
=====================================================================
O72 A3 質疑: 「44 = L₃×L₅ 指數未證唯一」

要證明 44 特殊, 需要: 44 喺「所有 N-ring 嘅閉合網絡」入面係唯一/特殊。
要反證 (質疑成立), 需要: 其他 N 都有類似網絡。

閉合網絡 (IDCM 依賴嘅數字):
  Σγ(N-site) = 2N+2
  88-site: Σγ_odd = N, Σγ_even = N+2
  946 = C(44,2)
  87 原子 = 43+44
  178 = 2×89 (F₁₁)
  264 = 3×88
  1496 = 44×34

測試:
  T1: 44 嘅因數分解 (2²×11) 喺 Lucas 數入面係咪唯一積?
  T2: 其他「自然」N 有冇同等豐富嘅結構?
  T3: 44 系數字 (44, 88, 90, 178, 946, 264, 1496) 有冇共同「特殊標記」?
  T4: 如果換 N=40 或 N=48, 邊啲閉合死?
"""
import numpy as np

phi = (1+np.sqrt(5))/2
lucas = {n: round(phi**n + (-phi)**(-n)) for n in range(1, 13)}

print("=" * 72)
print("T1: 44 = L₃×L₅ 喺 Lucas 積入面嘅唯一性")
print("=" * 72)
# 所有 Lucas 對積 (L_a × L_b, a≤b, a,b ∈ 1..12)
products = {}
for a in range(1, 13):
    for b in range(a, 13):
        p = lucas[a] * lucas[b]
        products.setdefault(p, []).append((a, b))
# 有冇其他 N 都有 Lucas 積分解? 特別係「多重分解」
print("  Lucas 積多重分解 (同一 N 有多於一個 L_a×L_b):")
multi = {p: v for p, v in products.items() if len(v) > 1}
for p, v in sorted(multi.items())[:15]:
    print(f"    {p} = " + " = ".join(f"L{a}×L{b}" for a, b in v))
print(f"  總共 {len(multi)} 個多重分解")
print()
print("  44 = L₃×L₅ (4×11) — 唯一分解?")
print(f"    products[44] = {products.get(44, [])}")
print(f"    → 44 只有 L₃×L₅ 一個 Lucas 分解 ✅ (唯一)")
print(f"    → 但唯一性只係「Lucas 積」層面, 唔係「自然數」層面")
print(f"    → 44 = 2²×11 本身: 2² = 4 = L₃, 11 = L₅ — 巧合? 定結構?")

print()
print("=" * 72)
print("T2: 其他 N 嘅結構豐富度")
print("=" * 72)
def richness(N):
    """計算 N-ring 嘅「IDCM 風格」結構數"""
    score = 0
    notes = []
    # 1. Σγ = 2N+2
    S = 2*N+2
    # 2. 88-site 版: Σγ_odd = N (N 偶數), Σγ_even = N+2
    # 3. 拍頻 = C(N,2) — 對應 946 嘅 C(44,2)
    beats = N*(N-1)//2
    # 4. 87 原子 = 43+44 — 對應 (N/2-1)+(N/2)? 88-site: 43+44
    # 5. 178 = 2F₁₁ — 對應 2×(N/2+45)?
    return beats

print("  N 嘅拍頻數 C(N,2) (對應 946):")
for N in [40, 42, 44, 46, 48, 88]:
    print(f"    N={N:2d}: C({N},2) = {N*(N-1)//2}")

print()
print("=" * 72)
print("T3: 44 系數字共同標記?")
print("=" * 72)
nums = {"44": 44, "88": 88, "90": 90, "178": 178, "946": 946, "264": 264, "1496": 1496}
for name, n in nums.items():
    facs = []
    d = 2
    m = n
    while d*d <= m:
        while m % d == 0:
            facs.append(d)
            m //= d
        d += 1
    if m > 1:
        facs.append(m)
    print(f"  {name} = {n} = {'×'.join(map(str, facs))}")
print("""
  44 = 2²×11
  88 = 2³×11
  90 = 2×3²×5
  178 = 2×89
  946 = 2×11×43
  264 = 2³×3×11
  1496 = 2³×11×17
  → 44/88/946/264/1496 全部有 11 因子! (90, 178 冇)
  → 11 = L₅ — 44 系數字好多都有 11 因子
  → 但呢個係因為 44 = 4×11, 下游全部 ×2/×3/×22 — 平凡!
""")

print()
print("=" * 72)
print("T4: 換 N=40 或 N=48, 邊啲閉合死?")
print("=" * 72)
def closure_network(N):
    g = 4*np.sin(np.pi*np.arange(1, N+1)/(2*N))**2
    S = g.sum()
    beats = N*(N-1)//2
    twoN = 2*N
    return S, beats, twoN

for N in [40, 44, 48]:
    S, beats, twoN = closure_network(N)
    print(f"  N={N:2d}: Σγ={S:.1f}, C(N,2)={beats}, 2N={twoN}")
print("""
  對比 IDCM 需求:
    Σγ = 90 (N=44 先有)
    946 = C(44,2) (N=44 先有)
    88 = 2×44 (N=44 先有)
    264 = 3×88 (N=44 先有)
  → 如果 N=40: Σγ=82, C(40,2)=780, 2N=80 — 全部唔同
  → 如果 N=48: Σγ=98, C(48,2)=1128, 2N=96 — 全部唔同
  → IDCM 閉合網絡係「44 專用」— 換 N 全死!
  → 但呢個「專用」唔係「唯一性證明」— 係「閉合網絡係 fit 44 出嚟」
  → 關鍵區分:
     🟢 如果 44 有獨立來源 (O51: 0,1→φ→L₃×L₅) → 閉合網絡係預言
     🔴 如果 44 係 fit (揀 44 令網絡最靚) → 閉合網絡係 post-hoc
""")

print()
print("=" * 72)
print("總結: 44 唯一性")
print("=" * 72)
print("""
  🟢 44 = L₃×L₅ 係唯一 Lucas 積分解 (products[44] 單一)
  🟢 44 系閉合網絡 (90/88/946/264/1496) 係 44 專用 — 換 N 全死
  🟡 但「專用」唔等於「必然」:
     44 = L₃×L₅ 有來源 (O51), 但指數 3,5 未證唯一
     點解係 L₃×L₅ 而唔係 L₂×L₇ (=87) 或 L₄×L₂ (=21)?
  🔴 真正嘅 44 唯一性證明需要:
     0,1 → φ → (某結構) → 指數 3,5 被強制
     → 呢個未存在

  結論: 44 有 Lucas 來源 (🟢) + 閉合網絡專用 (🟢),
        但指數選擇未證唯一 (🔴) — A3 質疑仍然成立
""")
