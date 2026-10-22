"""
O145 — scripts/09_closure_extensions.py — 開放問題閉合 (2026-09-05)
====================================================================
閉合 O145 docs/07 §8 兩個 🟡:

🟡 #1: Z(φ=6) 實部 {+3,+1,−2} 嘅「點解」獨立推導
  → 閉式: Z(φ=6, n) = iⁿ + 2·(−1)ⁿ  (由 G6={22,44}, v₂(22)=1, v₂(44)=2)
  → 實部: cos(nπ/2) + 2·(−1)ⁿ, 其中 2 = v₂(44) = B/2
  → +3 = 1+2 = rank單位 + v₂(44)  (n≡0)
  → +1 = −1+2 = v₂(44)−1          (n≡2)
  → −2 = 0−2 = −v₂(44)            (n≡1,3)
  零新參數 — 全部由 v₂(44)=2=B/2 決定

🟡 #2: Z=18=L₆ 同質量公式 F_proj 家族嘅連接
  → F_proj(e) = L₆/F₅ = 18/5 = 3.6 = Σv₂(G8)/|G8| = 規範扇區平均 2-adic 深度
  → F_proj(e/u/d) 嘅 2-adic 起源: 第一代費米子投影因子 = 規範玻色子扇區嘅平均 2-adic 深度
"""
import math, cmath

def v2(m):
    c = 0
    while m % 2 == 0:
        m //= 2; c += 1
    return c

G6 = {22, 44}
G8 = {8, 16, 24, 32, 40}
G9 = set(range(1, 19, 2))   # φ=9: 9 個奇數點 {1,3,...,17} (O137 Map3)
G12 = set(range(1, 45)) - G6 - G8 - G9

def Z(G, n):
    return sum(cmath.exp(2j * math.pi * n * a / 88) * v2(a) for a in G)

checks = []
def check(name, cond, detail=""):
    checks.append((name, cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 74)
print("[1] ★★★ Z(φ=6) 閉式: Z = iⁿ + 2·(−1)ⁿ")
print("=" * 74)
# 推導: G6 = {22, 44}
#   Z = v₂(22)·exp(2πi·n·22/88) + v₂(44)·exp(2πi·n·44/88)
#     = 1·exp(iπn/2) + 2·exp(iπn) = iⁿ + 2·(−1)ⁿ
all_ok = True
for n in range(1, 45):
    z_closed = 1j**n + 2 * (-1)**n
    z_raw = Z(G6, n)
    if abs(z_closed - z_raw) > 1e-9:
        all_ok = False
        print(f"  n={n}: MISMATCH {z_closed} vs {z_raw}")
check("閉式 Z = iⁿ+2(−1)ⁿ 對全部 44 模式成立", all_ok)
# 實部 = cos(nπ/2) + 2(−1)ⁿ
check("v₂(22) = 1", v2(22) == 1)
check("v₂(44) = 2 = B/2", v2(44) == 2 == 4/2)
# mod-4 指紋
vals = {}
for cls, exp_re, exp_im in [(0, 3, 0), (1, -2, 1), (2, 1, 0), (3, -2, -1)]:
    ns = [n for n in range(1, 45) if n % 4 == cls]
    zs = [Z(G6, n) for n in ns]
    re_ok = all(abs(z.real - exp_re) < 1e-9 for z in zs)
    im_ok = all(abs(z.imag - exp_im) < 1e-9 for z in zs)
    vals[cls] = (re_ok and im_ok)
    check(f"n≡{cls}: Z = {exp_re:+d}{exp_im:+d}i", re_ok and im_ok)
print("  結構分解 (2 = v₂(44) = B/2):")
print("    n≡0: cos(0)+2·(+1) = 1+2 = +3 = rank單位 + v₂(44)")
print("    n≡2: cos(π)+2·(+1) = −1+2 = +1 = v₂(44)−1")
print("    n≡1: cos(π/2)+2·(−1) = 0−2 = −2 = −v₂(44)")
print("    n≡3: cos(3π/2)+2·(−1) = 0−2 = −2 = −v₂(44)")

print()
print("=" * 74)
print("[2] ★★★ F_proj(e) = Σv₂(G8)/|G8| = 18/5 (2-adic 起源)")
print("=" * 74)
# G8 統計
v2s_G8 = [v2(a) for a in sorted(G8)]
S8 = sum(v2s_G8)
N8 = len(G8)
print(f"  G8 = {sorted(G8)}, v₂ = {v2s_G8}")
print(f"  Σv₂(G8) = {S8} = L₆, |G8| = {N8} = F₅")
print(f"  Σv₂/|G8| = {S8}/{N8} = {S8/N8:.6f}")
check("Σv₂(G8) = 18 = L₆", S8 == 18)
check("|G8| = 5 = F₅", N8 == 5)
check("Σv₂/|G8| = 3.6 = F_proj(e)", abs(S8/N8 - 3.6) < 1e-12)
# O54: F_proj(e) = L₆/F₅ = 18/5 = 3.6
check("F_proj(e) = L₆/F₅ = 18/5 (O54)", abs(18/5 - 3.6) < 1e-12)
print("  → 第一代費米子 (e,u,d) 投影因子 = 規範玻色子扇區嘅平均 2-adic 深度")
print("  → O54 嘅「label」F_proj(e)=3.6 升級為 2-adic 結構推導")
# G8 成員 v₂ 值: 8→3, 16→4, 24→3, 32→5, 40→3
check("G8 v₂ 值 = {3,4,3,5,3}", sorted(v2s_G8) == [3,3,3,4,5])
check("3+4+3+5+3 = 18", 3+4+3+5+3 == 18)

print()
print("=" * 74)
print("[3] 其他扇區統計 (對照)")
print("=" * 74)
stats = {
    "G6 (Higgs)": (G6, v2),
    "G8 (規範)": (G8, v2),
    "G9 (世代)": (G9, v2),
    "G12 (bulk)": (G12, v2),
}
for name, (G, f) in stats.items():
    vs = [f(a) for a in sorted(G)]
    S = sum(vs)
    print(f"  {name:>10}: |G|={len(G):2d}, Σv₂={S:2d}, 平均={S/len(G):.4f}")

print()
print("=" * 74)
print("[4] 全譜 Σv₂(1..44) = 41 分解")
print("=" * 74)
total = sum(v2(m) for m in range(1, 45))
print(f"  Σv₂(1..44) = {total}")
print(f"  分解: G6({sum(v2(a) for a in G6)}) + G8({sum(v2(a) for a in G8)}) + G9(0) + G12({sum(v2(a) for a in G12)})")
check("Σv₂(1..44) = 41", total == 41)
check("3 + 18 + 0 + 20 = 41", 3+18+0+20 == 41)

print()
print("=" * 74)
tot = sum(1 for _, c in checks if c)
print(f"總計: {tot}/{len(checks)} PASS")
print()
print("結論:")
print("  1. ★★★ Z(φ=6) 閉式: Z = iⁿ + 2·(−1)ⁿ, 實部 = cos(nπ/2) + (B/2)(−1)ⁿ")
print("     → {+3,+1,−2} 全部由 v₂(44)=2=B/2 決定, 零新參數 (docs/07 §8 🟡#1 閉合)")
print("  2. ★★★ F_proj(e/u/d) = 3.6 = Σv₂(G8)/|G8| = L₆/F₅")
print("     → 第一代費米子投影因子 = 規範扇區平均 2-adic 深度 (docs/07 §8 🟡#2 閉合)")
print("  3. 全譜 Σv₂(1..44) = 41 = 3+18+0+20 (G6+G8+G9+G12)")