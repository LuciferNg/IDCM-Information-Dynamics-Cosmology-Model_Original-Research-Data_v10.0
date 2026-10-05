#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 49 — P7 (tanβ) 攻堅: 結構候選 + 家族密度 null-control
==========================================================
tanβ = 27.3625 (半經驗: m_t·λ_b/(m_b·λ_t), 記錄 P7)
交點數路線已死 (O50: d_tensor vs κ_ijk r<0.1)。測試結構候選:
  H1  v_d = N_gen² = 9 GeV, v = 246.22 (SM) → tanβ = √(v²−v_d²)/v_d
  H2  v = 2L₁₀ = 246 GeV (Lucas VEV) → tanβ = √(4L₁₀²−N_gen⁴)/N_gen²
  H3  tanβ = F₈·43/K_tree = 21×43/33 = 27.3636 (0.0042%)
  H4  λ_t/λ_b = 41/27 (f_unproj/N_gen³) → tanβ = (m_t/m_b)/(41/27)
  H5  λ_t/λ_b = 3/2 檢查
null: (a·b)/c + a/(b·c) 家族, 擴展常數集 (含 43, 45, 83), 0.1%/0.01%/0.005% 窗
"""
import math
import itertools

TANB = 27.3625  # 半經驗 (m_t·λ_b/(m_b·λ_t), 記錄 P7)
PASS = 0
FAIL = 0

def chk(name, val, target, tol, unit=""):
    global PASS, FAIL
    ok = abs(val - target) <= tol * max(1.0, abs(target))
    if ok:
        PASS += 1
        print(f"  [✔] {name} = {val:.6f} {unit} (dev {(val-target)/target*100:+.4f}%)")
    else:
        FAIL += 1
        print(f"  [✘] {name} = {val:.6f} {unit} (dev {(val-target)/target*100:+.4f}%)")

print("=" * 72)
print("H0. 框架質量比 (O64): m_t = M₀·γ₄₄·37·42, m_b = M₀·γ₁₆·37·√12")
print("=" * 72)
M0 = 27.900915  # MeV
g44 = 4 * math.sin(44*math.pi/88)**2   # γ₄₄ (88-convention) = 4
g16 = 4 * math.sin(16*math.pi/88)**2   # γ₁₆
mt = M0 * g44 * 37 * 42
mb = M0 * g16 * 37 * math.sqrt(12)
print(f"  m_t = {mt:.1f} MeV = {mt/1000:.3f} GeV  (O64: 173.4 GeV)")
print(f"  m_b = {mb:.1f} MeV  (O64: 4181 MeV)")
rt = mt / mb
print(f"  m_t/m_b = {rt:.4f}  (f_unproj = 41 → dev {(rt-41)/41*100:+.2f}%; 41.5 = 83/2 → dev {(rt-41.5)/41.5*100:+.3f}%)")
lam_ratio = rt / TANB  # λ_t/λ_b
print(f"  ⇒ λ_t/λ_b = (m_t/m_b)/tanβ = {lam_ratio:.5f}")
print(f"     vs 3/2 = 1.5: dev {(lam_ratio-1.5)/1.5*100:+.2f}%")
print(f"     vs 41/27 = 1.51852: dev {(lam_ratio-41/27)/(41/27)*100:+.3f}%")
print(f"     λ_b/λ_t = {1/lam_ratio:.5f} vs tanθ₁₂(tree) = 0.660711: dev {(1/lam_ratio-0.660711)/0.660711*100:+.3f}%")

print()
print("=" * 72)
print("H1/H2. v_d = N_gen² = 9 GeV 假說 (V = 246.22 SM / 246 = 2L₁₀ Lucas)")
print("=" * 72)
v_sm = 246.22
v_luc = 246.0
t1 = math.sqrt(v_sm**2 - 9**2) / 9
t2 = math.sqrt(v_luc**2 - 9**2) / 9
print(f"  H1: tanβ = √(246.22²−9²)/9 = {t1:.4f}  (dev {(t1-TANB)/TANB*100:+.4f}%)")
print(f"  H2: tanβ = √(246²−9²)/9    = {t2:.4f}  (dev {(t2-TANB)/TANB*100:+.4f}%)")
chk("H1 (v=246.22, v_d=9)", t1, TANB, 1e-3)    # 0.086% < 0.1%?
chk("H2 (v=246, v_d=9)", t2, TANB, 1e-3)       # 0.17% > 0.1%?

print()
print("=" * 72)
print("H3. tanβ = F₈·43/K_tree = 21×43/33 = 27.3636?")
print("=" * 72)
h3 = 21 * 43 / 33
print(f"  tanβ = 21×43/33 = {h3:.6f}  (dev {(h3-TANB)/TANB*100:+.5f}%)")
chk("H3 (21·43/33)", h3, TANB, 5e-5)           # 0.0042% < 0.005%?
# 43 = 邊界模式 (O155 T20: 邊界對 (43,45)); 21 = F₈ = C(L₄,2); 33 = K_tree

print()
print("=" * 72)
print("H4/H5. λ_t/λ_b 候選")
print("=" * 72)
h4 = rt / (41/27)
print(f"  H4: tanβ = (m_t/m_b)/(41/27) = {h4:.4f}  (dev {(h4-TANB)/TANB*100:+.3f}%)")
h5 = rt / 1.5
print(f"  H5: tanβ = (m_t/m_b)/(3/2)   = {h5:.4f}  (dev {(h5-TANB)/TANB*100:+.3f}%)")

print()
print("=" * 72)
print("NULL. 家族密度: (a·b)/c + a/(b·c), 擴展常數集, 三級容差窗")
print("=" * 72)
# 擴展常數集 (O152 核心 + 邊界模式 43/45 + 83 = 2×41+1 + 27 = N_gen³ 等)
CONSTS = [2,3,4,5,7,11,13,16,17,19,21,25,27,29,31,32,33,34,36,37,40,41,42,43,44,45,46,47,55,60,66,77,83,88,90,123,134,137,144,176,178,180,230,246,360]
CONSTS = sorted(set(CONSTS))
print(f"  常數集 ({len(CONSTS)} 個): {CONSTS}")

def scan_family(tol):
    """(a·b)/c 同 a/(b·c) 家族, |val−tanβ| ≤ tol·tanβ, 返回 hits (去重後)"""
    hits = []
    seen = set()
    for a, b, c in itertools.product(CONSTS, repeat=3):
        # (a·b)/c
        v1 = a * b / c
        if abs(v1 - TANB) <= tol * TANB and (a, b, c) not in seen:
            hits.append((a*b, c, "·/", v1))
            seen.add((a, b, c))
        # a/(b·c)
        v2 = a / (b * c)
        if abs(v2 - TANB) <= tol * TANB and ("r", a, b, c) not in seen:
            hits.append((a, b*c, "/·", v2))
            seen.add(("r", a, b, c))
    return hits

for tol in (1e-3, 1e-4, 5e-5):
    hits = scan_family(tol)
    print(f"  tol {tol*100:.2f}% → {len(hits)} hits")
    for h in hits[:8]:
        print(f"    {h[0]}{h[2]}{h[1]} = {h[3]:.6f}  (dev {(h[3]-TANB)/TANB*100:+.4f}%)")

# 特別: 21·43/33 喺家族內? (係 — a·b/c 形式)
print()
print(f"  21×43/33 = {21*43/33:.6f} — 家族形式 (a·b)/c 成員; 0.0042% 命中, 但家族密度見上")
print(f"  66×17/41 = {66*17/41:.6f} (0.012%); 90×40/… 等 — script/47 已見 11+ hits @0.1%")

print()
print("=" * 72)
print("裁決輔助: tanβ 目標自身精度 (半經驗)")
print("=" * 72)
print("  tanβ = 27.3625 由 m_t·λ_b/(m_b·λ_t) — m_t/m_b 有 ~0.5-1% 不確定度")
print("  ⇒ tanβ 自身不確定度 ~0.5-1% (±0.14-0.27) — 任何 <0.1% 命中都喺目標精度內")
print("  H1 (0.086%) 同 H3 (0.004%) 都喺精度內 — 但機制先係判準, 精度唔夠")

print()
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
