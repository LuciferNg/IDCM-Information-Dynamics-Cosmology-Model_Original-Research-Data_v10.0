"""
O145 script 03 — 階梯延伸 {55,66} + 88/90 預算嘅轉移矩陣分解
================================================================
追擊發現:
1. O145 階梯 {11,22,33,44} = L₅×{1,2,3,4} 可延伸至 {55,66} = L₅×{5,6}
   - 55 = Λ²(11) = C(11,2) = F₁₀ = F₅·L₅ (SU(11) 正根數)
   - 66 = Λ²(12) = C(12,2) = L₀L₂L₅ = 11+55 (O101 已建立: 66=Λ²(12)=11⊕55)
2. 觀察者/世界預算嘅轉移矩陣分解:
   - 88 = Σγ_odd (觀察者) = L₀L₃L₅ = 2×4×11
   - 90 = Σγ_even (世界) = 66+24 = L₀L₂L₅ + L₀L₃L₂ = L₀L₂(L₅+L₃)
   - 24 = 2×12 = 2×B×N_gen = L₀L₃L₂
3. 觀察者側 (88-site odd sector): 44 modes = 22 對 Z₂ 鏡像, 按 mod 4 分 11+11
"""
import math

def Tpow(n):
    a, b, c, d = 1, 0, 0, 1
    base = ((1, 1), (1, 0))
    for _ in range(n):
        a, b, c, d = (a*base[0][0] + b*base[1][0],
                      a*base[0][1] + b*base[1][1],
                      c*base[0][0] + d*base[1][0],
                      c*base[0][1] + d*base[1][1])
    return a, b, c, d

def L(n): return round(Tpow(n)[0] + Tpow(n)[3])
def F(n): return round(Tpow(n)[1])

g88 = lambda n: 4 * math.sin(math.pi * n / 176) ** 2

checks = []
def check(name, cond, detail=""):
    checks.append((name, cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 72)
print("[1] ★ 階梯延伸: {11,22,33,44,55,66} = L₅×{1..6}")
print("=" * 72)
ladder = {11: 'L₅', 22: 'L₀L₅', 33: 'L₂L₅', 44: 'L₃L₅', 55: 'F₅L₅', 66: 'L₀L₂L₅'}
for v, dec in ladder.items():
    ok = {'11': L(5), '22': L(0)*L(5), '33': L(2)*L(5), '44': L(3)*L(5),
          '55': F(5)*L(5), '66': L(0)*L(2)*L(5)}[str(v)] == v
    check(f"{v} = {dec}", ok)
check("55 = C(11,2) = Λ²(11) = F₁₀", math.comb(11, 2) == 55 and F(10) == 55)
check("66 = C(12,2) = Λ²(12) = positive roots of SU(12)", math.comb(12, 2) == 66)
check("66 = 11 + 55 (rank + Λ²(11), O101)", 11 + 55 == 66)
check("55 = positive roots of SU(11) = 11×10/2", 11 * 10 // 2 == 55)

print()
print("=" * 72)
print("[2] ★★ 88/90 預算嘅轉移矩陣分解")
print("=" * 72)
odd88 = sum(g88(n) for n in range(1, 89) if n % 2 == 1)
even88 = sum(g88(n) for n in range(1, 89) if n % 2 == 0)
check("Σγ_odd (88-site) = 88 (觀察者)", abs(odd88 - 88) < 1e-9, f"({odd88:.6f})")
check("Σγ_even (88-site) = 90 (世界)", abs(even88 - 90) < 1e-9, f"({even88:.6f})")
check("88 = L₀L₃L₅ = 2×4×11", L(0) * L(3) * L(5) == 88)
check("24 = L₀L₃L₂ = 2×4×3", L(0) * L(3) * L(2) == 24)
check("90 = L₀L₂L₅ + L₀L₃L₂ = 66 + 24", L(0)*L(2)*L(5) + L(0)*L(3)*L(2) == 90)
check("90 = L₀L₂(L₅+L₃) = 2×3×(11+4)", L(0) * L(2) * (L(5) + L(3)) == 90)
check("178 = 88+90 = 2F₁₁, F₁₁ = 89", 88 + 90 == 2 * F(11) and F(11) == 89)

print()
print("=" * 72)
print("[3] 觀察者側 (88-site odd sector) 22/11 結構")
print("=" * 72)
odd = [n for n in range(1, 89) if n % 2 == 1]
pairs = [(n, 88 - n) for n in odd if n < 88 - n]
check("奇 sector 44 modes = 22 對 Z₂ 鏡像", len(odd) == 44 and len(pairs) == 22)
check("每對 γ_n+γ_{88−n} = 4 → Σ = 22×4 = 88", all(abs(g88(a)+g88(b)-4) < 1e-12 for a, b in pairs))
c1 = [n for n in odd if n % 4 == 1]
c3 = [n for n in odd if n % 4 == 3]
check("n≡1 mod4: 22 modes, n≡3 mod4: 22 modes (11+11 對)", len(c1) == 22 and len(c3) == 22)
lo_pairs = [(n, 88-n) for n in c1 if n < 44]
check("n≡1(低) ↔ n≡3(高): 11 對", len(lo_pairs) == 11)
s1 = sum(g88(n) for n in c1); s3 = sum(g88(n) for n in c3)
print(f"  Σγ(n≡1) = {s1:.4f}, Σγ(n≡3) = {s3:.4f}, 和 = {s1+s3:.4f} (=88)")
check("Σγ(n≡1)+Σγ(n≡3) = 88", abs(s1 + s3 - 88) < 1e-9)

print()
print("=" * 72)
print("[4] 世界側 (44-site = even sector) 嘅 66/24 分層 (docs/02 回顧)")
print("=" * 72)
def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2; c += 1
    return c
A = [m for m in range(1, 45) if v2(m) <= 1]
B = [m for m in range(1, 45) if v2(m) >= 2]
sA = sum(4 * math.sin(math.pi * m / 88) ** 2 for m in A)
sB = sum(4 * math.sin(math.pi * m / 88) ** 2 for m in B)
check("v₂≤1 (33 modes=M): Σγ = 66 = Λ²(12)", abs(sA - 66) < 1e-9, f"({sA:.6f})")
check("v₂≥2 (11 modes=L₅): Σγ = 24 = L₀L₃L₂", abs(sB - 24) < 1e-9, f"({sB:.6f})")
print("  90 = 66 + 24 = Λ²(12) + L₀L₃L₂ = 世界側完整分解")

print()
print("=" * 72)
print("[5] 階梯乘數生成機制: {1,2,3,4,5,6}")
print("=" * 72)
print("  乘數 | 結構數 | 身份")
print("  1    | 11    | rank(SU(12)) = L₅")
print("  2    | 22    | Z₂ 因子 (88/44) = L₀")
print("  3    | 33    | N_gen (世代) = L₂")
print("  4    | 44    | B (K_Tree branching) = L₃")
print("  5    | 55    | F₅ (Fibonacci) = (𝑇̂⁵)₁₂")
print("  6    | 66    | 2×N_gen (O106) = L₀L₂")
check("乘數全部 = 轉移矩陣不變量: L₀L₁L₂L₃ + F₅", L(0) == 2 and L(1) == 1 and L(2) == 3 and L(3) == 4 and F(5) == 5)
check("階梯和: 11+22+33+44+55+66 = 231 = 3×77 = 3L₄L₅", sum([11,22,33,44,55,66]) == 3 * L(4) * L(5))
print(f"  階梯和 = {11+22+33+44+55+66} = 231 = 3×77 = 3L₄L₅ (O106 77=L₄L₅!)")

print()
print("=" * 72)
tot = sum(1 for _, c in checks if c)
print(f"總計: {tot}/{len(checks)} PASS")
print()
print("結論:")
print("  1. 階梯延伸: {11,22,33,44,55,66} = L₅×{1..6}, 66 = 11+55 = Λ²(12) (O101)")
print("  2. 55 = Λ²(11) = F₁₀ = F₅L₅ (SU(11) 正根數)")
print("  3. 觀察者預算 88 = L₀L₃L₅, 世界預算 90 = L₀L₂(L₅+L₃) = 66+24")
print("  4. 觀察者側: 44 modes = 22 對 = 11+11 (mod-4 類)")
print("  5. 乘數 {1,2,3,4,5,6} = {L₁,L₀,L₂,L₃,F₅,L₀L₂} 全轉移矩陣不變量")
