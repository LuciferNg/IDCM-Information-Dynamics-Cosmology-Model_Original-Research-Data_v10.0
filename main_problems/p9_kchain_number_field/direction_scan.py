#!/usr/bin/env python3
"""
方向可行性快速掃描
==================
方向 A: 路徑閉合 — beat(i,j)+beat(j,k)=beat(i,k) 有幾多成立?
         → 即係「workflow = 保守場」? 指令序列總效果由首尾決定?
方向 B: magic rows 生成規則 — 7,14,20,22,33 有冇生成鏈?
"""
from math import pi, sin
from collections import Counter

N = 44
w = lambda n: 2*sin(pi*n/88)
beat = lambda i,j: abs(w(j)-w(i))
pairs = [(i,j) for i in range(1,N) for j in range(i+1,N+1)]

print("="*72)
print("方向 A: 路徑閉合 — workflow 係咪保守場?")
print("="*72)
# 對任意 i<j<k: beat(i,j)+beat(j,k) = beat(i,k)?
triples = [(i,j,k) for i in range(1,N-1) for j in range(i+1,N) for k in range(j+1,N+1)]
print(f"triple 數: {len(triples)} = C(44,3)")
viol = []
for (i,j,k) in triples:
    lhs = beat(i,j) + beat(j,k)
    rhs = beat(i,k)
    if abs(lhs-rhs) > 1e-12:
        viol.append((i,j,k))
print(f"路徑閉合: {len(triples)-len(viol)}/{len(triples)} {'✅ 全部成立!' if not viol else viol[:5]}")
print()
print("含義: beat(i,j)+beat(j,k)=beat(i,k) ∀i<j<k")
print("  → 拍頻係『保守勢差』— 任何執行序列嘅總效果 = 首尾端點勢差")
print("  → workflow = 路徑無關 (path-independent)")
print("  → 微碼 = 保守計算 (conservative computation)")
print()
# 有符號版本: beat(i,j) = ω_j − ω_i, 所以加減混合都得
print("有符號版本 (任意次序):")
print("  beat(i,j) − beat(i,k) = beat(k,j)?")
test = []
for (i,j,k) in triples:
    if abs(beat(i,j) - beat(i,k) - beat(k,j)) > 1e-12:
        test.append((i,j,k))
print(f"  {len(triples)-len(test)}/{len(triples)} 成立 {'✅' if not test else ''}")

print("\n" + "="*72)
print("方向 B: magic rows 生成規則")
print("="*72)
magic = [7, 14, 20, 22, 33]
print(f"magic rows: {magic}")
print()
print("Lucas/Fib 分解:")
L = {0:2,1:1,2:3,3:4,4:7,5:11,6:18,7:29}
F = {6:8,7:13,8:21,9:34}
for m in magic:
    comps = []
    for k,v in L.items():
        if v == m: comps.append(f"L{k}")
    for k,v in F.items():
        if v == m: comps.append(f"F{k}")
    print(f"  {m:2d}: {comps}")
print()
print("magic 之間關係:")
print(f"  14 = 2×7 = SYNC(L₄)")
print(f"  22 = 2×11 = SYNC(L₅)")
print(f"  33 = 3×11 = 3×L₅")
print(f"  20 = ? 22−2 = SYNC(L₅)−SYNC")
print(f"  7  = L₄")
print()
print("差分:")
dm = [magic[k+1]-magic[k] for k in range(4)]
print(f"  差分: {dm} = [7, 6, 2, 11]")
print(f"  7 = L₄, 6 = 2×3, 2 = L₀, 11 = L₅")
print(f"  差分和: {sum(dm)} = 26")

print("\n" + "="*72)
print("方向 C: 88 同 44 嘅『差』結構")
print("="*72)
# 44-site vs 88-site: 44 = N_d, 88 = 2N_d
# 87 = 88−1 已經挖到
# 仲有咩 gap?
print(f"88 − 44 = 44 (對偶)")
print(f"88 − 84 = 4 = γ_88 = B")
print(f"90 − 88 = 2 = γ_44")
print(f"87 − 84 = 3")
print(f"87 − 44 = 43 (邊數!)")
print(f"44 − 43 = 1 (種子)")
print()
print("★ 43 (邊) 同 44 (self loop) 差 1 = 種子")
print("★ 90 (世界) 同 88 (觀察者) 差 2 = γ_44")
print("★ 84 (核心) 同 88 差 4 = γ_88")

print("\n" + "="*72)
print("方向 D: 43 條邊嘅『執行』結構 — 邊做咩?")
print("="*72)
# 43 條邊 e_k = ω_{k+1} − ω_k
# 每條邊嘅「角色」= 由端點決定
# 檢查: 邊有冇 cluster (奇偶, 對稱位置)
e = [w(k+1)-w(k) for k in range(1,N)]
print(f"邊長範圍: {e[-1]:.8f} .. {e[0]:.8f}")
print(f"邊長中位: {sorted(e)[len(e)//2]:.8f}")
print(f"前半 (k=1..21) 和: {sum(e[:21]):.8f}")
print(f"後半 (k=22..43) 和: {sum(e[21:]):.8f}")
print(f"前半/總: {sum(e[:21])/sum(e):.6f}")
print(f"後半/總: {sum(e[21:])/sum(e):.6f}")
print(f"→ 前半 (細 n) 佔 {sum(e[:21])/sum(e)*100:.1f}% 能量 — 唔對稱!")
