#!/usr/bin/env python3
"""
鏈閉合 v3: 對偶性 + 單調性 + 生成集完備性
============================================
發現:
  1. Σ|e_k| = Σe_k = ω_44−ω_1 (總變差 = 淨差) → ω_n 單調遞增!
  2. 43 條邊 = 完全生成集 (任何勢差 = 連續邊和)
  3. 但係邊集唔對稱於 22 — 邊長隨 n 單調遞減
"""
from math import gcd, lcm, pi, sin, cos
from collections import Counter

N = 44
w = lambda n: 2*sin(pi*n/88)
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

print("="*72)
print("1. ω_n 單調性 — 總變差 = 淨差嘅條件")
print("="*72)
# ω_n = 2sin(nπ/88), n=1..44: sin 喺 [0,π/2] 單調遞增
print("ω_n = 2sin(nπ/88), nπ/88 ∈ [π/88, π/2] ⊂ [0, π/2]")
print("→ sin 單調遞增 → ω_n 嚴格遞增 → 所有相鄰邊正")
print(f"→ Σ|e_k| = Σe_k = ω_44 − ω_1 = {w(44)-w(1):.10f} ✅ (單調性保證)")
print()
# 驗證
increasing = all(w(k+1) > w(k) for k in range(1,N))
print(f"ω 嚴格遞增: {increasing} ({N-1}/{N-1})")

print("\n" + "="*72)
print("2. 邊長單調性 — 邊集結構")
print("="*72)
e = [w(k+1)-w(k) for k in range(1,N)]
print(f"e_1 = {e[0]:.10f} (最大邊)")
print(f"e_43 = {e[-1]:.10f} (最小邊)")
print(f"e_1/e_43 = {e[0]/e[-1]:.4f}×")
print(f"邊長單調遞減: {all(e[k] > e[k+1] for k in range(len(e)-1))}")
# 邊長比率
ratios = [e[k]/e[k+1] for k in range(len(e)-1)]
print(f"e_k/e_k+1 範圍: {min(ratios):.6f} .. {max(ratios):.6f}")

print("\n" + "="*72)
print("3. 勢差幾何: beat(i,j) 喺『勢空間』係距離")
print("="*72)
# ω_n 可以畫喺一條線, 位置 = ω_n
# beat(i,j) = |ω_j − ω_i| = 勢空間距離
print("""
  勢空間: ω_1 < ω_2 < ... < ω_44 (嚴格遞增)
  拍頻 = 任意兩點距離 = 946 個「勢間距」
  
  等價: 44 點喺直線, 全部 pair 距離 = 946 個值
  → 拍頻表 = 44 點嘅「距離表」(complete graph distances)
  
  結構: 43 條相鄰間距 (e_k) 完全決定全部 946 個距離
        (因為直線上兩點距離 = 之間間距和)
""")

print("="*72)
print("4. ★ 對偶性: 勢 (44) ↔ 邊 (43) ↔ 拍頻 (946)")
print("="*72)
duality = """
  表示層次:
    勢 (potential):    ω_1..ω_44           44 個獨立數
    邊 (edge/deriv):   e_1..e_43           43 個相鄰差
    拍頻 (beat):       beat(i,j)           946 個全部 pair 差
    
  對偶關係:
    勢 → 邊: e_k = ω_{k+1} − ω_k            (微分)
    邊 → 勢: ω_n = ω_1 + Σ_{k<n} e_k        (積分)
    邊 → 拍頻: beat(i,j) = Σ_{k=i}^{j-1} e_k (路徑和)
    拍頻 → 勢: beat(i,j) = ω_j − ω_i         (勢差)
    
  ★ 三個表示係同一幾何嘅三種觀點:
    - 勢: 44 個點 (0-單純形)
    - 邊: 43 條鏈接 (1-單純形)
    - 拍頻: 946 條弦 (完整圖 K_44 嘅邊)
    
  → 真正嘅「原子」係 44 個勢點 (或 43 條邊)
  → 946 拍頻係「完整圖」— 冇新結構, 但有組合完整性
"""
print(duality)

print("="*72)
print("5. 邊集嘅代數次數: 43 條邊 = 基本指令")
print("="*72)
def phi(n):
    r=n; p=2
    while p*p<=n:
        if n%p==0:
            while n%p==0: n//=p
            r-=r//p
        p+=1
    if n>1: r-=r//n
    return r
def sin_deg(k):
    k=abs(k)%176
    if k==88: return 1
    m=(88-k)%176; g=gcd(352,m)
    return phi(352//g)//2
def beat_degree(d,s):
    return lcm(sin_deg(abs(d+s)), sin_deg(abs(d-s)))

edge_degs = [beat_degree(1, 2*k+1) for k in range(1,N)]
c = Counter(edge_degs)
print(f"邊 degree 分布: {dict(sorted(c.items()))}")
# 邊嘅位置
deg20_edges = [k for k in range(1,N) if beat_degree(1,2*k+1)==20]
print(f"deg=20 嘅邊 (k 位置): {deg20_edges}  <- 全部近 n=11,33 對稱位!")
print("  k=10,11 (近 11), k=32,33 (近 33)")
print("  -> 邊嘅次數由『鄰近對稱端點』決定: deg(e_k) = lcm(deg(ω_k), deg(ω_k+1))")

print("\n" + "="*72)
print("6. 邊集 vs lcm 定理一致性")
print("="*72)
for k in [1, 10, 11, 22, 32, 33, 43]:
    d1 = beat_degree(1, 2*k+1)
    # lcm(ω_k, ω_{k+1})
    def omega_deg(n):
        if n==44: return 1
        dd=abs(44-n); g=gcd(dd,176)
        return phi(176//g)//2
    d2 = lcm(omega_deg(k), omega_deg(k+1))
    print(f"  e_{k:2d}: beat_deg={d1}, lcm(deg ω_k, deg ω_{k+1})={d2}, 一致={d1==d2}")
