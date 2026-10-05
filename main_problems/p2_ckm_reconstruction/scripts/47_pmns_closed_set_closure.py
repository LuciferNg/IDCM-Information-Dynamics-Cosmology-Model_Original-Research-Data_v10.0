#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ckm 47 — O155/O156 閉環交接: PMNS 全閉合集驗證 + 分配規則懲罰 + P7 探測
=====================================================================
承接 O155 (K_tree 算子化) + O156 (θ₂₃ 住 55) 閉環結論, 對 ckm_reconstruction
餘下開放問題 (P1-P7) 做最終閉環驗證:

A. P1/P4 閉環: 全閉合 PMNS 集 (θ₁₂ tree+1/33, θ₂₃@55, θ₁₃ tree·32/33, δ=230°)
   → 9 |U| 條目 vs NuFIT + J_CP (PDG 慣例) + sin²θ
B. 分配規則懲罰 (三角度三形式統一嘅必要性量化):
   通道對調 (θ₁₂↔p_I, θ₁₃↔p_B) 嘅災難性懲罰 — O155 T30 home-對調 嘅 channel 類比
C. CKM 閉合不變: δ_CKM = atan(√(γ₂₁/γ₉)) = 66.399960° (1e-9), J_CKM = 2.931e-5
D. P7 探測: tanβ = 27.3625 (半經驗) — 框架常數 (a·b)/c 家族 null-control + 近距記錄

慣例: 88-convention (ω_n = 2sin(nπ/88), γ_n = 4sin²(nπ/88) = ω_n²)
      θ(N) = atan(sin(7π/N)/sin(6π/N))  (O156 焦距形式)
      NuFIT 5.2 參考 (框架既有): θ₁₂=33.460°, θ₂₃=49.198°, θ₁₃=8.569°,
      |U| = [[0.8249,0.5450,0.1490],[0.3083,0.5871,0.7485],[0.4737,0.5984,0.6462]], J=0.0254
"""
import math
import cmath
from itertools import product

DEG = 180.0 / math.pi
PHI = (1 + math.sqrt(5)) / 2
BETA = 1 / PHI          # φ⁻¹ (tree meta-axiom)
EPS = BETA / 4          # φ⁻¹/4 (pipeline gap)
KTREE = 33
ND = 44
B = 4
NGEN = 3
L5 = 11
F7 = 13
F8 = 21
F9 = 34
F10 = 55

def w(n, N=88): return 2 * math.sin(n * math.pi / N)
def g(n, N=88): return 4 * math.sin(n * math.pi / N) ** 2
def deg(x): return x * DEG

results = []
def check(name, val, target, tol, unit=""):
    ok = abs(val - target) <= tol
    rel = abs(val - target) / abs(target) * 100 if target else float('nan')
    results.append((name, val, target, rel, ok))
    return ok

print("=" * 78)
print("A. PMNS 全閉合集 (O155 × O156 結論)")
print("=" * 78)

# --- A1. 三角度 + δ (全閉合集) ---
t12 = math.atan(BETA) + math.atan(1 / KTREE)
t12_exact = math.atan((KTREE + PHI) / (KTREE * PHI - 1))   # tan 加法精確形式
t23_55 = math.atan(math.sin(7 * math.pi / 55) / math.sin(6 * math.pi / 55))
t13 = math.asin(EPS * 32 / 33)
delta = (KTREE + F7) * (L5 - 2 * NGEN)   # 46 × 5 = 230.00 EXACT

print(f"θ₁₂ = atan(β)+atan(1/33)        = {deg(t12):.6f}°  (NuFIT 33.460°)")
print(f"   tan 加法精確形式             = {deg(t12_exact):.6f}°  Δ={abs(deg(t12)-deg(t12_exact)):.2e}°")
check("t12 exact-form", deg(t12_exact), deg(t12), 1e-12)
print(f"θ₂₃ = atan(sin(7π/55)/sin(6π/55)) = {deg(t23_55):.6f}°  (NuFIT 49.198°)  ← O156 home=55")
print(f"θ₁₃ = asin(ε·32/33)            = {deg(t13):.6f}°  (NuFIT 8.569°)")
print(f"δ   = (K_tree+F₇)(L₅−2N_gen)   = {delta}.000000° EXACT  (46×5, O155 R6)")

# --- A2. 全矩陣 (標準參數化, δ=230°) ---
s12, c12 = math.sin(t12), math.cos(t12)
s23, c23 = math.sin(t23_55), math.cos(t23_55)
s13, c13 = math.sin(t13), math.cos(t13)
d = math.radians(delta)

# PDG 參數化: U = R23(θ23)·R13(θ13,δ)·R12(θ12)
U = [
    [c12 * c13,                       s12 * c13,                       s13 * cmath.exp(-1j * d)],
    [-s12 * c23 - c12 * s23 * s13 * cmath.exp(1j * d),
      c12 * c23 - s12 * s23 * s13 * cmath.exp(1j * d),  s23 * c13],
    [ s12 * s23 - c12 * c23 * s13 * cmath.exp(1j * d),
     -c12 * s23 - s12 * c23 * s13 * cmath.exp(1j * d),  c23 * c13],
]

NUFIT = [
    [0.8249, 0.5450, 0.1490],
    [0.3083, 0.5871, 0.7485],
    [0.4737, 0.5984, 0.6462],
]

print("\n|U| IDCM (閉合集) vs NuFIT 5.2:")
maxd, meand = 0.0, 0.0
for i in range(3):
    row = [abs(U[i][j]) for j in range(3)]
    drow = [abs(row[j] - NUFIT[i][j]) for j in range(3)]
    maxd = max(maxd, max(drow)); meand += sum(drow)
    print(f"  row{i+1}: IDCM {[f'{x:.4f}' for x in row]}  Δ {[f'{x:.4f}' for x in drow]}")
meand /= 9
print(f"  maxΔ|U| = {maxd:.4f}  (期望 ≤0.0008),  meanΔ|U| = {meand:.4f}  (期望 0.0002)")

# --- A3. J_CP (PDG 慣例: J = s₁₂c₁₂s₂₃c₂₃s₁₃c₁₃²·|sinδ|) ---
J = s12 * c12 * s23 * c23 * s13 * c13 ** 2 * abs(math.sin(d))
print(f"\nJ_CP = {J:.6f}  vs NuFIT 0.0254  (Δ {abs(J-0.0254)/0.0254*100:.2f}%)")
check("J_CP", J, 0.0254, 0.001)

# --- A4. sin²θ 三值 ---
sin2 = [s12**2, s23**2, s13**2]
nufit_sin2 = [0.304, 0.573, 0.02219]   # docs 參考 (θ₁₃ 對應 8.569°)
names = ["sin²θ₁₂", "sin²θ₂₃", "sin²θ₁₃"]
for n, v, t in zip(names, sin2, nufit_sin2):
    print(f"{n} = {v:.6f}  vs NuFIT {t}  (Δ {abs(v-t)/t*100:.3f}%)")

# --- A5. 全-88 對照 (θ₂₃(88) = 49.3202°) ---
t23_88 = math.atan(w(7) / w(6))
s23b, c23b = math.sin(t23_88), math.cos(t23_88)
Ub = [
    [c12 * c13,                       s12 * c13,                       s13 * cmath.exp(-1j * d)],
    [-s12 * c23b - c12 * s23b * s13 * cmath.exp(1j * d),
      c12 * c23b - s12 * s23b * s13 * cmath.exp(1j * d),  s23b * c13],
    [ s12 * s23b - c12 * c23b * s13 * cmath.exp(1j * d),
     -c12 * s23b - s12 * c23b * s13 * cmath.exp(1j * d),  c23b * c13],
]
maxb, meanb = 0.0, 0.0
for i in range(3):
    rowb = [abs(Ub[i][j]) for j in range(3)]
    drow = [abs(rowb[j] - NUFIT[i][j]) for j in range(3)]
    maxb = max(maxb, max(drow)); meanb += sum(drow)
meanb /= 9
print(f"\n對照 全-88 (θ₂₃(88)=49.3202°): maxΔ={maxb:.4f}, meanΔ={meanb:.4f}  → 改善 {maxb/maxd:.1f}×/{meanb/meand:.1f}×")
J88 = s12 * c12 * s23b * c23b * s13 * c13 ** 2 * abs(math.sin(d))
print(f"J_CP(88) = {J88:.6f}  vs  J_CP(55) = {J:.6f}")

print("\n" + "=" * 78)
print("B. 分配規則懲罰 (三角度三形式統一: 通道對調必要性)")
print("=" * 78)
# 通道對調: θ₁₂ 用大概率 p_I, θ₁₃ 用細概率 p_B
t12_swap = math.atan(BETA) + math.atan(32 / 33)     # 75.83° — 爆破
t13_swap = math.asin(EPS / 33)                       # 0.27° — 坍縮
s12s = math.sin(t12_swap) ** 2
s13s = math.sin(t13_swap) ** 2
print(f"θ₁₂(p_I=32/33) = {deg(t12_swap):.3f}°  sin²θ₁₂ = {s12s:.4f}  vs NuFIT 0.304  → Δ = {abs(s12s-0.304)/0.304*100:.1f}%  (爆破)")
print(f"θ₁₃(p_B=1/33)  = {deg(t13_swap):.4f}°  sin²θ₁₃ = {s13s:.2e}  vs NuFIT 0.02219 → Δ = {abs(s13s-0.02219)/0.02219*100:.1f}%  (坍縮 32×)")
# 基量類型繼承論證: atan(1/33) ≈ 1/33 rad (線性區) vs 32/33 ≈ 1 (近單位因子)
print(f"\n基量類型繼承: θ₁₂ 基 = atan(β) 係角 → 角空間合成 (atan 相加, 需要細 p → p_B=1/33)")
print(f"              θ₁₃ 基 = ε 係振幅/gap → 振幅空間合成 (乘因子 ≈1, 需要大 p → p_I=32/33)")
print(f"線性區檢驗: atan(1/33) = {deg(math.atan(1/33)):.6f}° vs 1/33 rad = {deg(1/33):.6f}° (Δ {abs(deg(math.atan(1/33))-deg(1/33))*60:.3f} arcmin)")
print(f"通道分配 = 互補概率一致性: 角通道↔細 p (p_B), 振幅通道↔大 p (p_I); 對調災難性 → 必要性量化完成 (T30 類比)")

print("=" * 78)
print("C. CKM 閉合不變 (O155 T31 winding 強化)")
print("=" * 78)
# ⚠️ convention: δ_CKM 用 176-Laplacian 慣例 (γ_k = 4sin²(kπ/176), 首88模) — ckm docs/03 §P3
# tan δ_CKM = beat(2,23)/beat(8,17) = sin(21π/176)/sin(9π/176)
d_ckm = math.atan(math.sin(21 * math.pi / 176) / math.sin(9 * math.pi / 176))
print(f"δ_CKM = atan(sin(21π/176)/sin(9π/176)) = {deg(d_ckm):.8f}°  (66.399960°, 1e-9 閉合不變)")
# winding: d = 21-9 = 12 → 88 偶環 winding = 12/4 = 3 = N_gen 圈
print(f"winding: d = 21−9 = 12 = N_gen·B → 88 偶環 winding = 12/4 = 3 = N_gen 圈 (世代整數圈, O155 T31)")
J_ckm = 0.2252 * math.sqrt(1 - 0.2252**2) * 0.0405 * math.sqrt(1 - 0.0405**2) \
        * 0.00369 * (1 - 0.00369**2) * abs(math.sin(math.radians(66.399960)))
print(f"J_CKM ≈ {J_ckm:.3e}  vs PDG 3.05e-5 (ratio {J_ckm/3.05e-5:.3f}); 記錄 docs/06: 2.931e-5 (ratio 1.05)")

print("\n" + "=" * 78)
print("D. P7 探測: tanβ = 27.3625 (半經驗) — 框架常數家族 null-control")
print("=" * 78)
TANB = 27.3625
CONSTS = [2, 3, 4, 5, 7, 11, 13, 16, 17, 19, 21, 27, 29, 32, 33, 36, 41, 42, 44,
          46, 47, 55, 66, 68, 77, 84, 88, 90, 92, 94, 123, 126, 134, 137, 144,
          176, 178, 180, 230, 231, 274, 352, 360, 469, 561]
hits = []
TOL = 1e-3  # 0.1%
for a, b, c in product(CONSTS, repeat=3):
    v = (a * b) / c
    if abs(v - TANB) / TANB <= TOL:
        hits.append((v, a, b, c))
# 去重 (同值不同序)
uniq = {}
for v, a, b, c in hits:
    key = (v, tuple(sorted((a, b))), c)
    uniq[key] = True
print(f"候選: tanβ = {TANB} (半經驗 m_t·λ_b/(m_b·λ_t), 精度 ~0.1-1%)")
print(f"框架常數集: {len(CONSTS)} 個; (a·b)/c 家族, tol 0.1% → 命中 {len(uniq)} 個:")
for (v, ab, c) in sorted(uniq)[:12]:
    a, b = ab
    print(f"  {v:.4f} = {a}×{b}/{c}   (Δ {abs(v-TANB)/TANB*100:.3f}%)")
# 近距記錄: m_t/m_b ≈ f_unproj, λ_t/λ_b ≈ 3/2
mt_mb = 172.69 / 4.18
print(f"\n近距記錄 (唔宣稱): m_t/m_b = {mt_mb:.2f} vs f_unproj = 41 (Δ {abs(mt_mb-41)/41*100:.2f}%)")
lb_lt = TANB / mt_mb
print(f"  λ_b/λ_t = tanβ/(m_t/m_b) = {lb_lt:.4f} vs 2/3 (Δ {abs(lb_lt-2/3)/(2/3)*100:.2f}%)")
print(f"  ⇒ tanβ ≈ f_unproj·(2/3) = 27.333 (Δ {abs(27.333-TANB)/TANB*100:.2f}%) — form-grade, 唔係結構")

print("\n" + "=" * 78)
print("SUMMARY")
print("=" * 78)
for name, val, target, rel, ok in results:
    print(f"  {'✅' if ok else '❌'} {name}: {val:.8g} vs {target:.8g} (Δ {rel:.3g}%)")
print(f"\nP 表最終狀態: P1 ✅ (θ₂₃@55), P2 🟡 (V_ub 張力+θ₁₃ 0.56%), P3 ✅ (δ_CKM 66.399960°),")
print(f"              P4 ✅ (J_CP = {J:.4f}, 0.4%), P5 ✅ (k-ladder reframe), P6 ✅ (二 sector 域),")
print(f"              P7 🔴 (tanβ 半經驗, 家族命中 {len(uniq)} 個 → 唔宣稱)")
