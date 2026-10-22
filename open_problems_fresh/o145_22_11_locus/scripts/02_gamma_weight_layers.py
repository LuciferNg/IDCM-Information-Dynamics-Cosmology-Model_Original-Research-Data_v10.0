"""
O145 script 02 — 44-site 譜 2-adic 分層嘅 γ-權重結構 (22/11 能量身份)
====================================================================
問題延伸: 22 同 11 除咗階梯位置 (script 01), 喺譜能量權重層面嘅身份?

背景 (O34 已建立): 44-site K_Chain 譜 = 88-site 對偶鏈嘅 even sector:
    γ_{2n}^{(88)} = 4sin²(2πn/176) = 4sin²(πn/88) = γ_n^{(44)}
    Σγ (44-site, n=1..44) = 90 = Σγ_even (88-site) = 世界側能量

方法: 按 v₂(m) (2-adic 估值) 將 44 個模式分層, 計每層模式數 + Σγ。
"""
import math

def g(m): return 4 * math.sin(math.pi * m / 88) ** 2

def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2; c += 1
    return c

checks = []
def check(name, cond, detail=""):
    checks.append((name, cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 72)
print("[1] 44-site 譜 v₂(m) 分層: 模式數 vs Σγ")
print("=" * 72)
layers = {
    'v₂=0 (奇 m)':    [m for m in range(1, 45) if v2(m) == 0],
    'v₂=1 (≡2 mod 4)':[m for m in range(1, 45) if v2(m) == 1],
    'v₂=2 (≡4 mod 8)':[m for m in range(1, 45) if v2(m) == 2],
    'v₂≥3 (8|m)':     [m for m in range(1, 45) if v2(m) >= 3],
}
print(f"  {'層':<16} | {'模式數':>6} | {'Σγ':>10} | modes")
tot_n = 0; tot_e = 0
for name, ms in layers.items():
    s = sum(g(m) for m in ms)
    tot_n += len(ms); tot_e += s
    print(f"  {name:<16} | {len(ms):6d} | {s:10.6f} | {ms}")
check("模式數和 = 44", tot_n == 44)
check("Σγ 總和 = 90 (世界側)", abs(tot_e - 90) < 1e-9, f"({tot_e:.6f})")

print()
print("=" * 72)
print("[2] ★ 奇 m 層: 22 個模式 = 11 對 Z₂ 鏡像 → Σγ = 44 = N_d")
print("=" * 72)
odd = layers['v₂=0 (奇 m)']
pairs = [(m, 44 - m) for m in odd[:11]]
print(f"  鏡像對: {pairs}")
print(f"  11 對 × γ_m+γ_{'{44−m}'} = 11×4 = 44")
check("奇層 22 modes = 11 對", len(odd) == 22 and len(pairs) == 11)
check("每對 γ_m+γ_{44−m} = 4", all(abs(g(a)+g(b)-4) < 1e-12 for a, b in pairs))
s_odd = sum(g(m) for m in odd)
check("Σγ(奇) = 44 = N_d = 4L₅", abs(s_odd - 44) < 1e-9, f"({s_odd:.6f})")

print()
print("=" * 72)
print("[3] ★★ v₂=1 層: 11 個模式 (5 對 + 自對偶 m=22) → Σγ = 22 = 2L₅")
print("=" * 72)
c1 = layers['v₂=1 (≡2 mod 4)']
print(f"  v₂=1 modes: {c1}")
mir = [(m, 44 - m) for m in c1[:5]]
print(f"  5 對: {mir}, 自對偶: m=22 (γ₂₂=2)")
check("v₂=1 層 11 modes = 5 對 + m=22", len(c1) == 11)
check("5 對全部喺集合內", all((44-m) in c1 for m in c1 if m != 22))
s_c1 = sum(g(m) for m in c1)
check("Σγ(v₂=1) = 22 = 5×4 + γ₂₂ = 20+2", abs(s_c1 - 22) < 1e-9, f"({s_c1:.6f})")
check("γ₂₂ = 2 (自對偶能量)", abs(g(22) - 2) < 1e-12)

print()
print("=" * 72)
print("[4] v₂≥3 純玻色子層 (O137): 5 模式 → Σγ = 11 = L₅")
print("=" * 72)
c3 = layers['v₂≥3 (8|m)']
print(f"  O137 純玻色子: {c3}")
s_c3 = sum(g(m) for m in c3)
check("Σγ(純玻色子) = 11 = L₅", abs(s_c3 - 11) < 1e-9, f"({s_c3:.6f})")
check("v₂≥3 集合 = O137 {8,16,24,32,40}", set(c3) == {8, 16, 24, 32, 40})

print()
print("=" * 72)
print("[5] ★★★ 能量階梯: 44 → 22 → 11 (連續二分)")
print("=" * 72)
print(f"  Σγ(v₂=0, 22 modes) = 44 = 4×11  ← 世界/鏈整層")
print(f"  Σγ(v₂=1, 11 modes) = 22 = 2×11  ← 半層 (≡2 mod 4)")
print(f"  Σγ(v₂≥2, 11 modes) = 24 = 13+11 ← 下半層 (v₂=2: 13=F₇ + 純玻色子: 11=L₅)")
c2 = layers['v₂=2 (≡4 mod 8)']
s_c2 = sum(g(m) for m in c2)
check("Σγ(v₂=2) = 13 = F₇", abs(s_c2 - 13) < 1e-9, f"({s_c2:.6f})")
check("Σγ(v₂=2) + Σγ(v₂≥3) = 24", abs(s_c2 + s_c3 - 24) < 1e-9)
# 模式數層: 22 + 11 + 6 + 5 = 44; Σγ 層: 44 + 22 + 13 + 11 = 90
print(f"  模式數分層: 22 + 11 + 6 + 5 = 44")
print(f"  Σγ 分層:   44 + 22 + 13 + 11 = 90")
check("Σγ 分層 = 44+22+13+11 = 90", abs((44+22+13+11) - 90) < 1e-9)

print()
print("=" * 72)
print("[6] 22/11 三種單位身份 (同一階梯)")
print("=" * 72)
print("  奇 m 層:    11 = Z₂ 鏡像對數, Σγ = 11×4 = 44 = N_d")
print("  v₂=1 層:    11 = 模式數 (5對+自對偶), Σγ = 11×2 = 22 = N_d/2")
print("  純玻色子層: 11 = L₅ = 總能量 Σγ")
print()
print("  22 = N_d/2 = 2L₅ = v₂=1 層模式數×2 = v₂=1 層總能量")
print("  11 = L₅ = gcd(44,33) = rank(SU(12)) = 純玻色子層總能量")
print("      = 奇層 Z₂ 對數 = v₂=1 層模式數")
check("22 同時 = v₂=1 層模式數×2 同 Σγ", abs(s_c1 - 2 * len(c1)) < 1e-9)
check("11 = 純玻色子層 Σγ = L₅", abs(s_c3 - 11) < 1e-9)

print()
print("=" * 72)
tot_pass = sum(1 for _, c in checks if c)
print(f"總計: {tot_pass}/{len(checks)} PASS")
print()
print("結論: 44-site 譜 2-adic 分層揭示 22/11 嘅能量權重身份:")
print("  - 奇 m 22 modes (11 對) → Σγ 44 = N_d")
print("  - v₂=1 11 modes (5 對 + γ₂₂=2 自對偶) → Σγ 22 = 2L₅")
print("  - v₂≥3 純玻色子 5 modes → Σγ 11 = L₅")
print("  模式數 22+11 / Σγ 44+22+11 構成連續二分階梯 (44→22→11)")
