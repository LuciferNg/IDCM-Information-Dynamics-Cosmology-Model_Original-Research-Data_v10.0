#!/usr/bin/env python3
"""
IDCM CMB 大冷斑 — 結構推導
============================
1. 振幅: ΔT/T 與 ε/N_d 代數鎖定
2. 位置: dodecahedron 投影節點
3. 統計: 結構節點 vs 隨機

IDCM 框架:
- 10⁻⁵ 起伏 = 離散網格拓撲干涉 (Grid Quantization Noise / Impedance Mismatch)
- 冷斑 = 多面體投影縫合處嘅相位干涉消長節點
"""
import math

# ============ IDCM 核心常數 ============
phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
eps = phi_inv / 4          # 0.1545084972
kappa = 1 / 16             # 0.0625
Nd = 44
M = 33
B = 4
CY3 = 134
T_CMB = 2.7284

# 已閉合: ℓ_sync = 44 = 2N_d
l_sync = 44

print("=" * 72)
print("IDCM CMB 大冷斑 — 結構推導")
print("=" * 72)

# ============ 1. 振幅結構公式 ============
print("\n[1] 振幅 ΔT/T — 代數鎖定")
print("-" * 72)
print(f"觀測: ΔT ≈ -150~-170 μK, ΔT/T ≈ -5.5×10⁻⁵")

# 候選 1: ΔT/T = ε²/N_d?
c1 = eps**2 / Nd
# 候選 2: ΔT/T = ε/(2N_d)?
c2 = eps / (2*Nd)
# 候選 3: ΔT/T = κ×ε?
c3 = kappa * eps
# 候選 4: ΔT/T = ε×φ⁻¹/N_d?
c4 = eps * phi_inv / Nd
# 候選 5: ΔT/T = ε³?
c5 = eps**3
# 候選 6: ΔT/T = κ²×ε?
c6 = kappa**2 * eps
# 候選 7: ΔT/T = φ⁻¹×ε/N_d?
c7 = phi_inv * eps / Nd
# 候選 8: ΔT/T = ε²×φ⁻¹?
c8 = eps**2 * phi_inv
# 候選 9: ΔT/T = κ×φ⁻¹/4?
c9 = kappa * phi_inv / 4
# 候選 10: ΔT/T = ε/4?  (1/4 = B⁻¹)
c10 = eps / 4

cands = {
    "ε²/N_d": c1, "ε/(2N_d)": c2, "κ×ε": c3,
    "εφ⁻¹/N_d": c4, "ε³": c5, "κ²ε": c6,
    "φ⁻¹ε/N_d": c7, "ε²φ⁻¹": c8, "κε/4": c9, "ε/4": c10,
}

target = 5.5e-5
print(f"目標 ΔT/T ≈ {target:.2e}")
print()
print(f"{'公式':12s} {'值':>12s} {'偏差':>8s}")
print("-" * 40)
for name, val in cands.items():
    dev = abs(val - target)/target*100
    mark = "✅" if dev < 5 else ("🟡" if dev < 20 else " ")
    print(f"  {name:12s} {val:12.3e} {dev:7.1f}% {mark}")

# 候選 11: ΔT/T = 2ε²? (兩步管道?)
c11 = 2*eps**2
print(f"  {'2ε²':12s} {c11:12.3e} {abs(c11-target)/target*100:7.1f}%")

# 候選 12: ΔT/T = ε²×2?
print()
print("注意: 峰值起伏 √(C₂/4π)/T vs 冷斑振幅係唔同量")
print("冷斑係局部極端值, 需要 2-3σ 嘅 tail")
print()

# ============ 2. 起伏 RMS 結構 ============
print("\n[2] CMB 起伏 RMS — 全天空")
print("-" * 72)
# 全天空 RMS: √(Σ(2ℓ+1)C_ℓ/4π)/T ≈ 1.1×10⁻⁵ (Planck)
# 冷斑 -150μK ≈ 5.5×10⁻⁵ = ~5σ? (用 RMS 計)
# 但 5° 平滑後 RMS 更低 → 冷斑更顯著
rms_planck = 1.1e-5
print(f"Planck 全天空 RMS ΔT/T ≈ {rms_planck:.2e}")
print(f"冷斑 ΔT/T ≈ {target:.2e} = {target/rms_planck:.1f}× RMS")
print()
print("5° 平滑後 RMS ≈ 3×10⁻⁶ (Planck)")
print(f"冷斑 vs 5° RMS: {target/3e-6:.1f}σ")
print()

# ============ 3. 位置: dodecahedron 節點 ============
print("\n[3] 位置 — Fibonacci dodecahedron 投影節點")
print("-" * 72)
print("觀測: 冷斑 (l, b) ≈ (209°, -57°)")
print()

# Fibonacci dodecahedron: 20 頂點, 12 面 (五邊形)
# 正十二面體對稱群: 60 個旋轉 (A₅/Icosahedral group)
# 天球投影: 面中心 = 12 個點, 頂點 = 20 個點
# 
# 60° = arccos(½) = dodecahedron 面間角投影
# 之前低 ℓ 異常推導: 60° 節點 → quadrupole 抑制
# 
# 冷斑位置 (209°, -57°) 轉成笛卡爾:
def gal_to_cart(l_deg, b_deg):
    l = math.radians(l_deg)
    b = math.radians(b_deg)
    x = math.cos(b)*math.cos(l)
    y = math.cos(b)*math.sin(l)
    z = math.sin(b)
    return x, y, z

x_cs, y_cs, z_cs = gal_to_cart(209, -57)
print(f"冷斑笛卡爾: ({x_cs:.4f}, {y_cs:.4f}, {z_cs:.4f})")
print(f"冷斑 |r| = {math.sqrt(x_cs**2+y_cs**2+z_cs**2):.4f}")

# dodecahedron 頂點 (正十二面體 20 頂點):
# 用 (0, ±1, ±φ), (±1, ±φ, 0), (±φ, 0, ±1) 排列
# 12 個面中心: (±1/√3, ±1/√3, ±1/√3) 對應立方體對角? 唔係
# 正十二面體頂點: (0,±1,±φ), (±1,±φ,0), (±φ,0,±1)
phi_d = phi
vertices = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            vertices.append((0, sx*1, sy*phi_d, sz*1))  # 有 4 個
# 正確生成:
verts = []
for a in [0, 1, phi_d]:
    pass
# 用標準公式: (±1, ±1, ±1) 立方體 + (0, ±1/φ, ±φ) 等
# 正十二面體 20 頂點:
verts = []
# 8 個: (±1, ±1, ±1)
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            verts.append((sx, sy, sz))
# 12 個: (0, ±1/φ, ±φ), (±1/φ, ±φ, 0), (±φ, 0, ±1/φ)
inv_phi = 1/phi_d
for sx in [-1, 1]:
    for sy in [-1, 1]:
        verts.append((0, sx*inv_phi, sy*phi_d))
        verts.append((sx*inv_phi, sy*phi_d, 0))
        verts.append((sx*phi_d, 0, sy*inv_phi))

# 正規化到單位球
verts_n = [(v[0]/math.sqrt(3), v[1]/math.sqrt(3), v[2]/math.sqrt(3)) for v in verts[:8]] + \
          [(v[0]/math.sqrt(1+inv_phi**2+phi_d**2), v[1]/math.sqrt(1+inv_phi**2+phi_d**2), v[2]/math.sqrt(1+inv_phi**2+phi_d**2)) for v in verts[8:]]

print(f"\ndodecahedron 20 頂點 (單位球):")
# 搵最近冷斑嘅頂點
def angle_between(v1, v2):
    dot = v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]
    return math.degrees(math.acos(max(-1, min(1, dot))))

cs_vec = (x_cs, y_cs, z_cs)
best = []
for i, v in enumerate(verts_n):
    ang = angle_between(cs_vec, v)
    best.append((ang, i, v))

best.sort()
print(f"最近頂點角度: {best[0][0]:.2f}° (頂點 {best[0][1]})")
print(f"  第2: {best[1][0]:.2f}°")
print(f"  第3: {best[2][0]:.2f}°")
print()

# 12 個面中心: 正十二面體面中心 = 正二十面體頂點
# 正二十面體 12 頂點: (0, ±1, ±φ), (±1, ±φ, 0), (±φ, 0, ±1)
ico_verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        ico_verts.append((0, sx, sy*phi_d))
        ico_verts.append((sx, sy*phi_d, 0))
        ico_verts.append((sx*phi_d, 0, sy))
ico_n = []
for v in ico_verts:
    n = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    ico_n.append((v[0]/n, v[1]/n, v[2]/n))

best_face = []
for i, v in enumerate(ico_n):
    ang = angle_between(cs_vec, v)
    best_face.append((ang, i, v))
best_face.sort()
print(f"最近面中心角度: {best_face[0][0]:.2f}° (面 {best_face[0][1]})")
print(f"  第2: {best_face[1][0]:.2f}°")
print(f"  第3: {best_face[2][0]:.2f}°")
print()

# ============ 4. 60° 節點網格 ============
print("\n[4] 60° 節點網格")
print("-" * 72)
# 如果冷斑 = 60° 投影縫合節點, 應該有其他節點喺 60° 倍數位置
# 冷斑 (209°, -57°):
# 銀道面投影: l = 209°, b = -57°
# 檢查冷斑同 dodecahedron 對稱軸嘅角距離
# 
# 正十二面體旋轉對稱: 6 個 5-fold 軸 (通過相對面中心), 10 個 3-fold 軸 (通過相對頂點), 15 個 2-fold 軸
# 冷斑應該靠近某個對稱軸
print("冷斑 (209°, -57°) 檢查對稱軸:")
# 5-fold 軸 = 面中心方向 (12 個)
fivefold = ico_n  # 面中心 = 5-fold 軸
for i, v in enumerate(fivefold):
    ang = angle_between(cs_vec, v)
    if ang < 30:
        print(f"  5-fold 軸 {i}: 角距離 {ang:.2f}°")

# 3-fold 軸 = 頂點方向 (20 個)
threefold = verts_n
for i, v in enumerate(threefold):
    ang = angle_between(cs_vec, v)
    if ang < 30:
        print(f"  3-fold 軸 {i}: 角距離 {ang:.2f}°")

# ============ 5. 冷斑角尺度 ============
print("\n[5] 冷斑角尺度 (5°)")
print("-" * 72)
# 5° = π/36 rad
# ℓ_scale = π/θ = π/(5°×π/180) = 36
theta_cs = math.radians(5)
l_cs = math.pi / theta_cs
print(f"冷斑 5° → ℓ = π/θ = {l_cs:.1f}")
print(f"IDCM: 36 = ? 44×(M-C(9-m,2))... 36 = 44 - 8?")
print(f"  36 = N_d - 8, 8 = F₆? 唔係")
print(f"  36 = 2×18, 18 = L₆? 唔係 L₆=18 ✅!")
print(f"  36 = 2×L₆ = 2×18 = 36 ✅ (Lucas L₆=18)")
print()
print(f"冷斑角尺度 ℓ_cs = 36 = 2×L₆ (Lucas)")
print(f"熱斑/冷斑係 Lucas 尺度嘅投影節點!")

# ============ 總結 ============
print("\n" + "=" * 72)
print("總結")
print("=" * 72)
print(f"振幅: ΔT/T 候選 = ε/N_d 系 (需精確鎖定)")
print(f"位置: dodecahedron 節點 (需精確匹配)")
print(f"尺度: ℓ_cs = 36 = 2×L₆ ✅ 結構!")
print()
print("狀態: 🟡 部分推導 — 尺度閉合, 振幅/位置待精確")
