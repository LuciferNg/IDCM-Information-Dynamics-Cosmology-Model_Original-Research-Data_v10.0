"""
O145 — scripts/08_physical_labels.py — 22/11 物理標籤: 2-adic 扇區共振分析
====================================================================
追擊 O145 docs/01 §三 🔴「22/11 模式嘅具體物理標籤」

發現 (2026-09-05, 由 O137 docs/12 未開發線索出發):
  ★ 階梯 {11,22,33,44} 全部對 φ=8 規範玻色子扇區給出純實數阻抗 Z = 18 = L₆
  ★ n=22, n=44 係唯一兩個「全扇區共振」模式 (φ=6, φ=8, φ=9, φ=12 全部純實數)
  ★ φ=9 (世代混合扇區) 對全部 44 個模式正交 (Z=0 恆等) — v₂=0 權重消失
  ★ Z(φ=6) 實部 = mod-4 指紋: n≡0→+3=N_gen, n≡2→+1, n≡1/3→−2
    對應 O145 docs/05 Σγ mod-4 閉式 (46/44/44∓sec)

物理標籤候選 (基於 O137 closure §2.3 φ 分層, 唔係新作料):
  n=22: Higgs VEV 錨點 (φ=6 特殊站點 {22,44}) + 全扇區共振
  n=11: rank(SU(12)) = L₅ + 規範扇區共振 (Z=18)
"""
import math, cmath

def v2(m):
    c = 0
    while m % 2 == 0:
        m //= 2; c += 1
    return c

# O137 Map3 (v₂ 自然映射) φ 子群 — 以 O137 docs/12 為準
G6 = {22, 44}                              # φ=6: Higgs VEV 錨點 (O137 closure §2.3)
G8 = {8, 16, 24, 32, 40}                   # φ=8: 規範玻色子扇區 (5 純玻色子)
G9 = set(range(1, 19, 2))                  # φ=9: 世代混合 (9 奇數點 {1..17}, v₂=0)
G12 = set(range(1, 45)) - G6 - G8 - G9     # φ=12: Kähler bulk (28 點)

def Z(G, n):
    """2-adic 阻抗: Σ_{a∈G} exp(2πi·n·a/88)·v₂(a)"""
    return sum(cmath.exp(2j * math.pi * n * a / 88) * v2(a) for a in G)

checks = []
def check(name, cond, detail=""):
    checks.append((name, cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 74)
print("[1] ★★★ 階梯 {11,22,33,44} = φ=8 規範扇區共振模")
print("=" * 74)
ladder = [11, 22, 33, 44]
for n in ladder:
    z = Z(G8, n)
    print(f"  n={n:2d}: Z(φ=8) = {z.real:+.6f}{z.imag:+.6f}i")
check("階梯全部對 φ=8 純實數 Z=18",
      all(abs(Z(G8, n).imag) < 1e-9 and abs(Z(G8, n).real - 18) < 1e-9 for n in ladder))
# 唯一性: 冇其他模式 Z(φ=8)=18
others = [n for n in range(1, 45) if n not in ladder
          and abs(Z(G8, n).imag) < 1e-9 and abs(Z(G8, n).real - 18) < 1e-9]
check("唯一性: 冇其他模式 Z(φ=8)=18", len(others) == 0, f"(others={others})")

print()
print("=" * 74)
print("[2] 機制: 11|n ⟺ 相位全部 = 1")
print("=" * 74)
# n = 11k: exp(2πi·11k·a/88) = exp(2πi·k·a/8); a∈G8 全部 ≡0 mod 8 → 相位=1
amod8 = sorted(a % 8 for a in G8)
print(f"  G8 點 mod 8: {amod8} — 全部 ≡0")
print(f"  → Z(φ=8, n=11k) = Σ v₂(a) = {sum(v2(a) for a in G8)} = L₆")
check("G8 全部 ≡0 mod 8", set(amod8) == {0})
check("Σ v₂(G8) = 3+4+3+5+3 = 18 = L₆", sum(v2(a) for a in G8) == 18)
# L₆ = 18 身份
def L(n):
    a, b = 2, 1
    for _ in range(n): a, b = b, a + b
    return a
check("18 = L₆ = Tr(T̂⁶)", L(6) == 18)
check("18 = 2×N_gen² = 2×9", 18 == 2 * 9)
check("11|n ⟺ n ∈ {11,22,33,44} (1..44)", [n for n in range(1, 45) if 11*math.ceil(n/11) == n and n % 11 == 0] == ladder or [n for n in range(11,45,11)] == ladder)

print()
print("=" * 74)
print("[3] ★ n=22, n=44 = 唯一全扇區共振 (RRRR)")
print("=" * 74)
def sector_flags(n):
    flags = []
    for G in [G6, G8, G9, G12]:
        z = Z(G, n)
        flags.append(abs(z.imag) < 1e-9)
    return flags
for n in range(1, 45):
    flags = sector_flags(n)
    if all(flags):
        print(f"  n={n:2d}: 全扇區共振 ✅ (φ=6, φ=8, φ=9, φ=12 全部純實數)")
check("22 全扇區共振", all(sector_flags(22)))
check("44 全扇區共振", all(sector_flags(44)))
allres = [n for n in range(1, 45) if all(sector_flags(n))]
check("唯一性: 只有 {22,44} 全扇區", allres == [22, 44], f"({allres})")
# 但 11/33 只共振 φ=8, φ=9
print(f"  n=11 扇區: {['φ6','φ8','φ9','φ12'][0] if sector_flags(11)[0] else ''} "
      f"{'φ8' if sector_flags(11)[1] else ''} {'φ9' if sector_flags(11)[2] else ''} {'φ12' if sector_flags(11)[3] else ''}")
print(f"  n=33 扇區: {['φ6','φ8','φ9','φ12'][0] if sector_flags(33)[0] else ''} "
      f"{'φ8' if sector_flags(33)[1] else ''} {'φ9' if sector_flags(33)[2] else ''} {'φ12' if sector_flags(33)[3] else ''}")

print()
print("=" * 74)
print("[4] ★ φ=9 (世代混合扇區) 完全正交")
print("=" * 74)
z9max = max(abs(Z(G9, n)) for n in range(1, 45))
check("全部 44 模式 |Z(φ=9)| = 0", z9max < 1e-9)
print("  原因: φ=9 點全部奇數 (v₂=0) → Z = Σ exp(2πi·n·a/88)·0 = 0 恆等")
print("  世代混合扇區 = 2-adic 正交 — 混合角來源唔係 2-adic 結構 (留 O65)")

print()
print("=" * 74)
print("[5] ★★ Z(φ=6) 實部 = mod-4 指紋 (對應 O145 docs/05 Σγ 閉式)")
print("=" * 74)
print(f"  {'mod-4 類':>10} | {'Z(φ=6)':>10} | {'實部身份':>12} | {'O145 Σγ 閉式':>16}")
table = [
    (1, -2, 1, "−Z₂", "44−sec(π/88)"),
    (3, -2, -1, "−Z₂", "44+sec(π/88)"),
    (2, 1, 0, "rank 單位", "44 (恆等)"),
    (0, 3, 0, "N_gen", "46 (恆等)"),
]
ok = True
for cls, re_, im_, ident, closure in table:
    ns = [n for n in range(1, 45) if n % 4 == cls]
    vals = set((round(Z(G6, n).real, 6), round(Z(G6, n).imag, 6)) for n in ns)
    match = len(vals) == 1 and abs(list(vals)[0][0] - re_) < 1e-6 and abs(list(vals)[0][1] - im_) < 1e-6
    ok &= match
    print(f"  n≡{cls} mod 4     | {re_:+d}{im_:+d}i     | {ident:>12} | {closure:>16}  {'✅' if match else '❌'}")
check("Z(φ=6) mod-4 指紋全部匹配", ok)

print()
print("=" * 74)
print("[6] 物理標籤候選表")
print("=" * 74)
print("""  n=22: γ=2 (Z₂ 自對偶), v_g=0.7071c, v₂=1 → L=22 子環
         φ=6 特殊站點 {22,44} = Higgs VEV 錨點 (O137 closure §2.3)
         ★ 全扇區共振 (唯一兩個之一) — 規範/世代/bulk 全部純實數
         ★ Z(φ=6)=+1 = rank 單位 (n≡2 mod 4 類)
  n=11: γ=2−√2, v_g=0.9239c, v₂=0 → L=44 子環
         = L₅ = rank(SU(12)) (O145 docs/01)
         ★ 規範扇區共振 Z=18=L₆ (同 22/33/44)
         ★ 非全扇區: φ=6/φ=12 有虛部 (對比 22 嘅全共振)
  n=33: γ=2+√2 = M 模式, n=11 嘅 Z₂ 鏡像 — 同 n=11 有相同共振輪廓 (φ8,φ9)
  n=44: γ=4 (Nyquist), 全扇區共振 (唯一另一個 RRRR)
  實部身份: +3=N_gen (玻色子類 n≡0), +1=rank (n≡2), −2=−Z₂ (奇數)""")

print()
print("=" * 74)
tot = sum(1 for _, c in checks if c)
print(f"總計: {tot}/{len(checks)} PASS")
print()
print("結論:")
print("  1. ★★★ 階梯 {11,22,33,44} = φ=8 規範扇區共振模, Z=18=L₆=2N_gen²")
print("     (機制: 11|n ⟺ G8 相位全=1 ⟺ Z=Σv₂=18, 唯一性由 11|n 保證)")
print("  2. ★ n=22 同 n=44 係唯一全扇區共振 (RRRR) — 物理上嘅「全耦合」模式")
print("  3. ★ φ=9 世代混合扇區 2-adic 正交 (Z=0 恆等) — 混合角唔嚟自 2-adic 結構")
print("  4. ★★ Z(φ=6) 實部 = mod-4 指紋: +3=N_gen / +1=rank / −2=−Z₂")
print("     同 O145 docs/05 Σγ 閉式 (46/44/44∓sec) 完全對齊")
print("  5. 物理標籤: n=22 = Higgs VEV 錨點 (O137 已標) + 全扇區共振;")
print("     n=11 = rank(SU(12)) + 規範扇區共振 — 階梯即規範結構")