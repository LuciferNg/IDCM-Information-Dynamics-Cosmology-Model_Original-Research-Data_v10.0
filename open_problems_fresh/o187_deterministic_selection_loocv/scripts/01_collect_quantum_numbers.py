#!/usr/bin/env python3
"""
O187 Step 1: 量子數數據集 + v₂(n) 2-adic 分析
=============================================
三不原則: 禁止讀取 PDG 質量, 只用量子數 + 拓撲性質。

數據集: 9 費米子 (Q, T₃, g, Color) × (n, P_f) — n/P_f 係 O136 現有值,
但唔准用質量反推, 只係作為「要解釋嘅目標」。

核心問題: 有冇純代數映射 f: (Q,T₃,g,Color) ↦ (n,P_f)?
"""
import numpy as np
import json, os

phi = (1+np.sqrt(5))/2
psi = -1/phi
def L(n): return phi**n + psi**n
def F(n): return (phi**n - psi**n)/np.sqrt(5)

# ── 數據集 (量子數, 無質量) ──
fermions = [
    # name, Q, T3, gen, color, n_existing, Pf_desc
    ('e',  -1,   -0.5, 1, 'singlet', 1,  'L6/F5'),
    ('mu', -1,   -0.5, 2, 'singlet', 7,  'Nd-E_proj'),
    ('tau',-1,   -0.5, 3, 'singlet', 20, 'Nd-L4'),
    ('u',  +2/3, +0.5, 1, 'triplet', 1,  'Nd-E_proj'),
    ('d',  -1/3, -0.5, 1, 'triplet', 1,  'Nd-L5'),
    ('s',  -1/3, -0.5, 2, 'triplet', 14, 'L6/F5'),
    ('c',  +2/3, +0.5, 2, 'triplet', 34, 'F7'),
    ('b',  -1/3, -0.5, 3, 'triplet', 33, 'Nd'),
    ('t',  +2/3, +0.5, 3, 'triplet', 0,  'Higgs VEV'),
]

# ── v₂(n) 2-adic ──
def v2(n):
    if n == 0: return None
    c = 0
    while n % 2 == 0:
        n //= 2; c += 1
    return c

# ── P_f 數值 (O136 定義) ──
Nd = 44
E_proj = 28.5  # ? 待推導
PF_VALUES = {
    'L6/F5': L(6)/F(5),
    'Nd-E_proj': Nd - E_proj,
    'Nd-L4': Nd - L(4),
    'Nd-L5': Nd - L(5),
    'F7': F(7),
    'Nd': Nd,
}

print("="*70)
print(" O187 Step 1: 量子數 × (n, P_f) 數據集")
print("="*70)

print(f"\n── 數據集 ──")
print(f"{'name':<5}{'Q':>7}{'T3':>6}{'g':>3}{'color':<9}{'n':>4}{'v2(n)':>6}  {'P_f desc':<12}{'P_f val':>8}")
for name,Q,T3,g,color,n,pfd in fermions:
    print(f"{name:<5}{Q:>7.2f}{T3:>6.1f}{g:>3}{color:<9}{n:>4}{str(v2(n)):>6}  {pfd:<12}{PF_VALUES.get(pfd,0):>8.3f}")

print(f"""
── 結構觀察 (量子數 → n) ──

1. 輕子 (Q=-1, T3=-½, singlet): n = 1, 7, 20 (g=1,2,3)
2. up-type (Q=+⅔, T3=+½, triplet): n = 1, 34, 0 (g=1,2,3)
3. down-type (Q=-⅓, T3=-½, triplet): n = 1, 14, 33 (g=1,2,3)

→ n 似乎由 (T3, g) 決定, 唔係由 Q:
  T3=-½: n = 1, 7, 20 (輕子) | 1, 14, 33 (down)
  T3=+½: n = 1, 34, 0   (up)
""")

# ── n 嘅 2-adic + Lucas/Fibonacci 分解 ──
print(f"── n 嘅代數分解 ──")
print(f"{'n':>4}{'v2':>4}{'2^v2':>6}{'odd part':>9}{'Lucas?':>10}{'Fib?':>8}{'selected_n?':>12}")
selected = [1,2,3,7,8,10,12,14,15,20,21,26,27,30,33]
for n in [1,7,20,14,34,33]:
    v = v2(n)
    if v is None:
        print(f"{n:>4}{'—':>4}{'—':>6}{'—':>9}{'':>10}{'':>8}{'':>12}")
        continue
    odd = n // (2**v)
    is_L = any(abs(L(i)-n) < 1e-6 for i in range(10))
    is_F = any(abs(F(i)-n) < 1e-6 for i in range(12))
    print(f"{n:>4}{v:>4}{2**v:>6}{odd:>9}{'✓' if is_L else '':>10}{'✓' if is_F else '':>8}{'✓' if n in selected else '':>12}")

# ── 關鍵: n 有冇「先驗」規則? ──
print(f"""
── 先驗規則候選 ──

候選 A: n = f(g, T3) 由世代 + 弱同位旋決定?
  輕子 g=1,2,3 → 1, 7, 20
  down  g=1,2,3 → 1, 14, 33
  up    g=1,2,3 → 1, 34, 0
  → g=1 全部 n=1 (degenerate!)
  → g=2: 輕子 7, down 14, up 34
  → g=3: 輕子 20, down 33, up 0(Higgs)

候選 B: n 由 color × T3 × g 組合?
  n = 1 出現 3 次 (e,u,d 全部 g=1) → g=1 必 n=1?

候選 C: v₂(n) 分類?
  n=1 (v2=0), n=7 (v2=0), n=14 (v2=1), n=20 (v2=2), n=33 (v2=0), n=34 (v2=1)
  → 冇簡單模式
""")

# ── 儲存 ──
data = {
    'fermions': [
        {'name':n,'Q':Q,'T3':T3,'gen':g,'color':c,'n':n_,'v2':v2(n_),'P_f':pfd,'P_f_val':float(PF_VALUES.get(pfd,0))}
        for n,Q,T3,g,c,n_,pfd in fermions
    ],
    'selected_n': selected,
    'PF_values': {k:float(v) for k,v in PF_VALUES.items()},
}
os.makedirs('data', exist_ok=True)
with open('data/01_quantum_numbers.json','w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("saved: data/01_quantum_numbers.json")
