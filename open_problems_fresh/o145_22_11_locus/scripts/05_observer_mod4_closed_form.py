"""
O145 script 05 — 觀察者側 mod-4 類精確閉式: Σγ = 44 ± sec(π/88)
====================================================================
問題 (docs/01 🟡): Σγ(n≡1 mod 4) ≈ 43, Σγ(n≡3 mod 4) ≈ 45 — 「接近但唔精確」

突破: 唔係「接近 43/45」, 而係有精確閉式:

Σ_{n≡1 mod 4} 4sin²(nπ/176) = 44 − sec(π/88)   (n = 1,5,...,85, 22 項)
Σ_{n≡3 mod 4} 4sin²(nπ/176) = 44 + sec(π/88)   (n = 3,7,...,87, 22 項)

推導 (等差角度求和):
  Σ_{k=0}^{N-1} cos(a+kd) = [sin(Nd/2)/sin(d/2)]·cos(a+(N−1)d/2)
  N=22, a=π/88, d=π/22 → sin(π/2)/sin(π/44)·cos(43π/88) = sin(π/88)/sin(π/44)
  Σγ = 4·[22 − Σcos]/2 = 44 − 2·sin(π/88)/sin(π/44) = 44 − 1/cos(π/88)  [sin(2θ)=2sinθcosθ]

即: 觀察者側 mod-4 類以 N_d=44 為中心, 偏移 ±sec(π/88) ≈ ±1.000638
    44 − 1.000638 = 42.999362 (n≡1), 44 + 1.000638 = 45.000638 (n≡3)
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

checks = []
def check(name, cond, detail=""):
    checks.append((name, cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 72)
print("[1] 精確閉式驗證")
print("=" * 72)
g88 = lambda n: 4 * math.sin(math.pi * n / 176) ** 2
s1 = sum(g88(n) for n in range(1, 89, 4))   # n ≡ 1 mod 4: 1,5,...,85
s3 = sum(g88(n) for n in range(3, 89, 4))   # n ≡ 3 mod 4: 3,7,...,87
sec = 1 / math.cos(math.pi / 88)
check("Σγ(n≡1) = 44 − sec(π/88)", abs(s1 - (44 - sec)) < 1e-12, f"({s1:.10f})")
check("Σγ(n≡3) = 44 + sec(π/88)", abs(s3 - (44 + sec)) < 1e-12, f"({s3:.10f})")
check("Σγ(n≡1) 22 項", len(list(range(1, 89, 4))) == 22)
check("Σγ(n≡3) 22 項", len(list(range(3, 89, 4))) == 22)
check("和 = 88 (觀察者預算)", abs(s1 + s3 - 88) < 1e-12)
check("差 = 2sec(π/88)", abs((s3 - s1) - 2 * sec) < 1e-12, f"({s3-s1:.10f} vs {2*sec:.10f})")

print()
print("=" * 72)
print("[2] ★ 結構意義: 44 ± sec(π/88) — 偏移量分解")
print("=" * 72)
print(f"  sec(π/88) = {sec:.10f}")
print(f"  sec(π/88) − 1 = {sec - 1:.10f} (偏移)"
      f" ≈ (π/88)²/2 = {(math.pi/88)**2/2:.10f} (二階展開)")
print(f"  π/88 = {math.pi/88:.10f} — 半格角度 (O74 θ_site = π/44 嘅一半)")
# γ_n Z₂ 對稱: γ_{44-n} = 4−γ_n (44-site) / γ_{88-n} = 4−γ_n (88-site)
# mod-4 類: n≡1 ↔ 88−n≡3, 每對 γ_n+γ_{88−n} = 4
# 22 對 × 4 = 88, 但 n≡1 類攞每對嘅「細 n」(低頻) → 減 sec; n≡3 攞「大 n」→ 加 sec
print("  鏡像對 (n, 88−n): n≡1 ↔ n≡3, 每對 γ 和 = 4")
print("  22 對 × 4 = 88 但唔係均分 44/44 — 因 n≡1 類偏向低頻 (n<44 嗰半)")
print(f"  低頻半 (n≡1, n<44): {sum(g88(n) for n in range(1,45,4)):.6f}")
print(f"  高頻半 (n≡1, n>44): {sum(g88(n) for n in range(45,89,4)):.6f}")

print()
print("=" * 72)
print("[3] 階梯截斷: 88 = 觀察者預算 = 自然截斷")
print("=" * 72)
print("  階梯 {11..88} = 11×{1..8}, 乘數 = 轉移矩陣不變量")
print("  ★ 88 就係觀察者預算 Σγ_odd (88-site) = L₀L₃L₅")
print("  → 階梯頂端 = 觀察者能量預算, 唔係任意數字")
# 88 = Σγ_odd 全部 44 個奇模式加埋 — 即階梯第 8 級 = 觀察者總能量
oddfull = sum(g88(n) for n in range(1, 89, 2))
check("88 = Σγ_odd 全 44 奇模式", abs(oddfull - 88) < 1e-12)
check("88 = L₀L₃L₅ = 2×4×11", L(0) * L(3) * L(5) == 88)
print("  階梯 k=8 → 88: 乘數 8 = L₀L₃ = 2×4 = Z₂×B = 觀察者因子")
check("乘數 8 = L₀L₃ (Z₂×B) = 觀察者因子", L(0) * L(3) == 8)

print()
print("=" * 72)
print("[4] ★★ 22/11 喺觀察者側嘅完整圖")
print("=" * 72)
print("  觀察者側 (88-site odd sector, 44 modes, Σγ=88):")
print("    ├─ mod-4 分層: n≡1 (22 modes) = 44 − sec(π/88)")
print("    │                n≡3 (22 modes) = 44 + sec(π/88)")
print("    └─ Z₂ 對 (n, 88−n): 22 對, 每對 γ 和 = 4")
print("  22 = 對數 = 每 mod-4 類嘅模式數 = 2L₅")
print("  11 = 低頻半 (n≡1, n<44) 嘅對數 = L₅")
lo11 = [n for n in range(1, 45, 4)]  # n≡1 mod4, n<44: 11 個
hi11 = [n for n in range(45, 89, 4)]  # n≡1 mod4, n>44: 11 個
check("低頻 n≡1 半 (n<44): 11 個模式", len(lo11) == 11)
check("高頻 n≡1 半 (n>44): 11 個模式", len(hi11) == 11)
# 低頻半同高頻半嘅 γ 和?
slo = sum(g88(n) for n in lo11); shi = sum(g88(n) for n in hi11)
print(f"  Σγ(低頻 n≡1) = {slo:.6f}, Σγ(高頻 n≡1) = {shi:.6f}, 和 = {slo+shi:.6f}")
check("低頻+高頻 = 44 − sec(π/88)", abs(slo + shi - (44 - sec)) < 1e-12)

print()
print("=" * 72)
tot = sum(1 for _, c in checks if c)
print(f"總計: {tot}/{len(checks)} PASS")
print()
print("結論:")
print("  1. ★ 閉式: Σγ(n≡1 mod 4) = 44 − sec(π/88), Σγ(n≡3) = 44 + sec(π/88)")
print("     → 以 N_d=44 為中心嘅對稱偏移, 唔係「接近 43/45」!")
print("  2. 偏移 sec(π/88) − 1 ≈ (π/88)²/2 (二階展開)")
print("  3. 階梯頂端 88 = 觀察者預算 Σγ_odd = 自然截斷 (乘數 8 = L₀L₃ = Z₂×B)")
print("  4. 觀察者側 22/11: 22 對 = 每類模式數, 11 = 低/高頻半嘅對數")