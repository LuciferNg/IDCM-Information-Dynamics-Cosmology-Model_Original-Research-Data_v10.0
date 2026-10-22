"""
O145 — scripts/10_electroweak_subring.py — 電弱子環閉合 (2026-09-05)
====================================================================
閉合 O145 docs/08 §6 剩餘開放:
  🔴 n=22 全扇區共振嘅可觀測後果 → 電弱對稱破缺子環身份

發現 (由 O142 玻色子質量模式追擊):
  ★★★ W (n=30) 同 Higgs (n=38) 都坐喺 L=22 子環類 (v₂=1)!
  ★★★ m_W/m_Z = sin(30π/88)/sin(41π/88) = L=22/L=44 跨類比
  ★★★ m_H/m_W = sin(38π/88)/sin(19π/88) = L=22/L=44 跨類比
  → n=22 嘅物理標籤 = 電弱對稱破缺子環 (Higgs VEV 錨點 + W/H 質量模式)

物理圖像:
  n=22 本身 = Higgs VEV 錨點 (φ=6 特殊站點, O137 closure §2.3)
  L=22 子環類 (v₂=1, 11 個模式) = 電弱扇區: {W, H} + {s, c} 夸克
  L=44 子環類 (v₂=0) = Z + 第一代費米子
  L=11 子環類 (v₂=2) = τ
"""
import math

def v2(m):
    c = 0
    while m % 2 == 0:
        m //= 2; c += 1
    return c

def Lsub(n):
    v = v2(n)
    return 44 // (2**v) if v < 3 else None

checks = []
def check(name, cond, detail=""):
    checks.append((name, cond))
    print(f"  {'✅' if cond else '❌'} {name} {detail}")

print("=" * 74)
print("[1] ★★★ W/H 玻色子坐喺 L=22 子環類")
print("=" * 74)
L22_modes = [n for n in range(1, 45) if v2(n) == 1]
print(f"  L=22 類 (v₂=1): {L22_modes} (11 個)")
check("W (n=30) ∈ L=22 類", 30 in L22_modes)
check("H (n=38) ∈ L=22 類", 38 in L22_modes)
check("Z (n=41) ∈ L=44 類", Lsub(41) == 44)
check("19 (H/W 分母) ∈ L=44 類", Lsub(19) == 44)

print()
print("=" * 74)
print("[2] ★★★ 電弱質量比 = L=22/L=44 跨類比")
print("=" * 74)
# m_W/m_Z = sin(30π/88)/sin(41π/88): W=L22, Z=L44
r_WZ = math.sin(30*math.pi/88)/math.sin(41*math.pi/88)
# m_H/m_W = sin(38π/88)/sin(19π/88): H=L22, 19=L44
r_HW = math.sin(38*math.pi/88)/math.sin(19*math.pi/88)
print(f"  m_W/m_Z = sin(30π/88)/sin(41π/88) = {r_WZ:.6f}  (L=22/L=44)")
print(f"  m_H/m_W = sin(38π/88)/sin(19π/88) = {r_HW:.6f}  (L=22/L=44)")
check("W/Z 比 = L22/L44 跨類", Lsub(30)==22 and Lsub(41)==44)
check("H/W 比 = L22/L44 跨類", Lsub(38)==22 and Lsub(19)==44)
# PDG 對照
check("m_W/m_Z ≈ 0.8814 (PDG)", abs(r_WZ - 0.881447) < 0.005, f"({r_WZ:.4f} vs 0.8814)")
check("m_H/m_W ≈ 1.5583 (PDG)", abs(r_HW - 1.558282) < 0.005, f"({r_HW:.4f} vs 1.5583)")

print()
print("=" * 74)
print("[3] ★ 費米子 L 類分配 (O143 grid)")
print("=" * 74)
fermions = {'e':1, 'μ':7, 'τ':20, 'u':1, 'd':1, 's':14, 'c':34, 'b':33}
for name, n in fermions.items():
    print(f"  {name:>2} (n={n:2d}): L={Lsub(n)}")
check("s, c ∈ L=22 類 (同 W/H)", Lsub(14)==22 and Lsub(34)==22)
check("e, μ, u, d, b ∈ L=44 類 (同 Z)", all(Lsub(fermions[x])==44 for x in ['e','μ','u','d','b']))
check("τ ∈ L=11 類", Lsub(20)==11)

print()
print("=" * 74)
print("[4] ★★★ 完整物理圖像: 22 = 電弱子環")
print("=" * 74)
print("""  n=22 三重身份 (O145 全 O 閉合):
    1. 譜: γ₂₂ = 2 (Z₂ 自對偶), v_g = 0.7071c
    2. 代數: 22 = 2L₅ = N_d/2 = 階梯第 2 級
    3. 物理 (本 doc): Higgs VEV 錨點 + 電弱子環代表

  L 子環類物理分配:
    L=44 (v₂=0, 22 modes): Z 玻色子 + 第一代費米子 (e,μ,u,d) + b
    L=22 (v₂=1, 11 modes): W 玻色子 + Higgs + s,c 夸克  ← 電弱扇區!
    L=11 (v₂=2, 6 modes):  τ (第三代)
    純玻色子 (v₂≥3, 5 modes): {8,16,24,32,40} (O137)""")

print()
print("=" * 74)
print("[5] 可觀測後果總結")
print("=" * 74)
print("""  1. W/Z 質量比 = sin(L=22 模式)/sin(L=44 模式) — 電弱扇區跨類結構
  2. H/W 質量比 = sin(L=22 模式)/sin(L=44 模式) — Higgs 同屬 L=22
  3. s,c 夸克同 W,H 共享 L=22 子環 — 電弱/第二代夸克共模
  4. τ 孤懸 L=11 — 第三代唯一 L=11 粒子
  5. n=22 全扇區共振 (RRRR) + 電弱子環 → 電弱對稱破缺嘅 2-adic 座標""")

print()
print("=" * 74)
tot = sum(1 for _, c in checks if c)
print(f"總計: {tot}/{len(checks)} PASS")
print()
print("結論:")
print("  1. ★★★ W (n=30) 同 Higgs (n=38) 坐喺 L=22 子環類 — 電弱玻色子共模")
print("  2. ★★★ m_W/m_Z 同 m_H/m_W 全部 = L=22/L=44 跨類比")
print("  3. ★ n=22 物理標籤完整: 譜身份 + 代數身份 + 電弱子環代表")
print("  4. 🔴→🟢: 「全扇區共振可觀測後果」= 電弱對稱破缺子環 (O142 質量比)")