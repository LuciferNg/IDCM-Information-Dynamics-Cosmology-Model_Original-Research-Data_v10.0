"""
IDCM v10.0 — 從 44 K_Chain mode 嘅 beat frequency 推導 CKM 角
==============================================================
核心: CKM 角 = beat frequency 比例, 唔係 12D d_tensor 對角化

每個粒子 = 某個 K_Chain mode 嘅 beat frequency 共振
CKM 混合 = 兩個 sector (up/down) 之間嘅 beat ratio 錯位
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
sqrt_φ = math.sqrt(φ)
ε = φ**(-1) / 4
N_d = 44

# 44 個 K_Chain mode 嘅 γ_n 同 ω_n
γ = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, N_d + 1)])
ω = np.sqrt(γ)

print("=" * 80)
print("IDCM v10.0 — 從 44 K_Chain beat frequency 推導 CMK 角 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. 44 個 mode 嘅 Z₃ × Z₅ 分類
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. 44 個 mode 嘅 Z₃ × Z₅ 分類")
print("─" * 80)

# Z₃ = n mod 3, Z₅ = n mod 5
# 每個 (Z₃, Z₅) 組合嘅最小 n
z3z5_modes = {}
for n in range(1, 45):
    z3 = n % 3
    z5 = n % 5
    key = (z3, z5)
    if key not in z3z5_modes:
        z3z5_modes[key] = []
    z3z5_modes[key].append(n)

print(f"  每個 (Z₃, Z₅) 組合嘅 n 值:")
for z3 in range(3):
    for z5 in range(5):
        key = (z3, z5)
        if key in z3z5_modes:
            modes = z3z5_modes[key]
            print(f"    (Z₃={z3}, Z₅={z5}): n = {modes}")

# ══════════════════════════════════════════════════════════════
# 2. 粒子到模式嘅映射
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. 粒子到模式嘅映射")
print("─" * 80)

# 從 12D index 分配:
# 每個粒子對應一個 Z₃ × Z₅ pair
# 從 44 個 mode 中, 每個 (Z₃, Z₅) 揀最匹配嘅 n

# 關鍵: 唔係揀最小 n, 而係揀 γ_n 最接近 mass ratio 嘅 n
# 質量 ∝ f(γ_n) 嘅某種函數

# 試: 質量 ∝ 1/γ_n (低 γ = 重)
# 但 1/γ_1 = 196, 1/γ_44 = 0.25
# 比例 196/0.25 = 784, 唔夠 Top/Electron = 338,083

# 試: 質量 ∝ exp(-φ/γ_n) 或類似
# 即係 V_cycle 指數壓抑

# 直接從 44 個 mode 嘅 γ_n 搵「標準模式」嘅分配
# 每個 generation 有 3 個粒子 (up, down, lep)
# 每個粒子對應一個 (Z₃, Z₅) pair

# 從 12D index 分配 (已知 work):
# Gen3: (0,0)=Top, (0,1)=Bottom, (0,2)=Tau
# Gen2: (1,3)=Charm, (1,4)=Strange, (1,0)=Muon
# Gen1: (2,1)=Up, (2,2)=Down, (2,3)=Electron

# 從 44 個 mode 嘅 (Z₃, Z₅) 分類, 每個粒子有 3 個候選 n:
particle_modes = {
    "Top": z3z5_modes[(0, 0)],     # Z₃=0, Z₅=0 → n=15, 30
    "Bottom": z3z5_modes[(0, 1)],   # Z₃=0, Z₅=1 → n=6, 21, 36
    "Tau": z3z5_modes[(0, 2)],      # Z₃=0, Z₅=2 → n=12, 27, 42
    "Charm": z3z5_modes[(1, 3)],    # Z₃=1, Z₅=3 → n=13, 28, 43
    "Strange": z3z5_modes[(1, 4)],  # Z₃=1, Z₅=4 → n=4, 19, 34
    "Muon": z3z5_modes[(1, 0)],     # Z₃=1, Z₅=0 → n=10, 25, 40
    "Up": z3z5_modes[(2, 1)],       # Z₃=2, Z₅=1 → n=11, 26, 41
    "Down": z3z5_modes[(2, 2)],     # Z₃=2, Z₅=2 → n=2, 17, 32
    "Electron": z3z5_modes[(2, 3)], # Z₃=2, Z₅=3 → n=8, 23, 38
}

# 粒子質量 (PDG)
particle_masses = {
    "Top": 172760, "Bottom": 4180, "Tau": 1776.86,
    "Charm": 1270, "Strange": 93.4, "Muon": 105.658,
    "Up": 2.16, "Down": 4.67, "Electron": 0.511
}

# 每個粒子有 3 個候選 n, 每個 n 有對應嘅 γ_n
# 揀 γ_n 最接近 mass_ratio 嘅 n
# mass_ratio = m_particle / m_Top

print(f"  粒子候選 mode 分析:")
print(f"  {'粒子':>10} | {'m (MeV)':>10} | {'ratio':>10} | {'候選 n':>20} | {'γ_n':>30} | {'最佳 n':>8}")
print("-" * 85)

for particle in ["Top", "Bottom", "Tau", "Charm", "Strange", "Muon", "Up", "Down", "Electron"]:
    mass = particle_masses[particle]
    ratio = mass / particle_masses["Top"]
    candidates = particle_modes[particle]
    γ_candidates = [f"{γ[n-1]:.4f}" for n in candidates]
    
    # 揀最佳 n: 質量 ∝ 1/γ_n 嘅最接近
    best_n = None
    best_err = float('inf')
    for n in candidates:
        # 質量 ∝ exp(-φ/γ_n) 或類似
        # 但簡單啲: 直接比 γ_n 嘅排序
        err = abs(γ[n-1] - ratio * 100)  # 粗略
        if err < best_err:
            best_err = err
            best_n = n
    
    print(f"  {particle:>10} | {mass:>10.4f} | {ratio:>10.6f} | {str(candidates):>20} | {', '.join(γ_candidates):>30} | {best_n:>8}")

# ══════════════════════════════════════════════════════════════
# 3. 用 γ_n 質量公式搵粒子-mode 映射
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. 用 γ_n 質量公式搵粒子-mode 映射")
print("─" * 80)

# 質量公式: m = M_Pl × exp(-V_cycle) × γ_n?
# 或 m = M_0 × γ_n^k?
# 或 m = M_0 × φ^(-k/γ_n)?

# 從已知嘅 beat frequency 分析:
# 之前發現 φ², √2, π 自然出現喺 beat frequency 中
# 即係: 特定 beat = 特定無理數

# 對於 SM 粒子質量比, 之前發現:
# m_u/m_d = 0.23% (來自 beat (30,31))
# m_s/m_d = 0.10% (來自 beat (3,27))
# m_W/m_Z = 0.54% (來自 beat (13,14))
# m_H/m_W = 0.06% (來自 beat (18,20))

# 但呢啲係質量比, 唔係絕對質量
# CKM 角需要從 mode 之間嘅 overlap 推導

# 用 44 個 mode 嘅波函數直接計算 CKM:
# 對於每個 mode n, 波函數 ψ_n(x) = sin(πnx/44)
# 兩個 mode 嘅 overlap: O_{nm} = ∫ψ_n ψ_m dx
# 但呢個 overlap 係正交嘅 (δ_{nm})

# CY₃ 投影引入非正交性:
# 投影後嘅波函數: ψ_n^{(proj)} = P_CY₃ ψ_n
# 投影 operator P_CY₃ 將 44 個 mode 投影到 12 個物理粒子
# 呢個投影就係 12D d_tensor 嘅作用

# 但既然 user 話唔用 d_tensor, 要從 44 個 mode 直接推導
# 可能嘅方法: 用 Z₃ × Z₅ 決定 overlap

# 3 個 generation 嘅 up/down 分配:
# 每個 generation 內, up/down 嘅 Z₅ charge 差 = 1 (Higgs VEV)
# 跨 generation 混合 = Z₅ orbit overlap

# 從 44 個 mode 嘅 Z₃ × Z₅ 分類:
# Gen3 (Z₃=0): 揀 Z₅=0(Top), 1(Bottom), 2(Tau) 嘅最小 n
# Gen2 (Z₃=1): 揀 Z₅=3(Charm), 4(Strange), 0(Muon)
# Gen1 (Z₃=2): 揀 Z₅=1(Up), 2(Down), 3(Electron)

# 但「最小 n」可能唔啱 — 需要考慮 γ_n 嘅大小
# 重粒子應該對應低 γ_n (低頻率)

# 試另一種分配: 按 γ_n 排序 (大 γ_n = 輕粒子)
# 每個 generation 揀 γ_n 最小嘅 n, 但限制 Z₃

print(f"\n  按 γ_n 排序 (最小 γ_n = 最重):")
for z3 in range(3):
    modes_z3 = [(n, γ[n-1]) for n in range(1, 45) if n % 3 == z3]
    modes_z3.sort(key=lambda x: x[1])
    print(f"  Z₃={z3}: {[(n, f'{g:.4f}') for n, g in modes_z3[:5]]}")

# 按 Z₃ 分組, 每個 Z₃ 内 γ_n 最小嘅 3 個 mode 做 3 個粒子
# 但需要分配 up/down/lep 嘅 Z₅

# 從 12D index 分配:
# Z₃=0: Top(Z₅=0), Bottom(Z₅=1), Tau(Z₅=2)
# Z₃=1: Charm(Z₅=3), Strange(Z₅=4), Muon(Z₅=0)
# Z₃=2: Up(Z₅=1), Down(Z₅=2), Electron(Z₅=3)

# 每個 Z₃ 内最小 γ_n 嘅 3 個 mode:
for z3, gen_name in [(0, "Gen3"), (1, "Gen2"), (2, "Gen1")]:
    modes_z3 = [(n, γ[n-1]) for n in range(1, 45) if n % 3 == z3]
    modes_z3.sort(key=lambda x: x[1])
    print(f"\n  {gen_name} (Z₃={z3}): 最小 γ_n 嘅 3 個 mode:")
    for n, g in modes_z3[:3]:
        z5 = n % 5
        print(f"    n={n:2d}, γ={g:.6f}, Z₅={z5}")

# ══════════════════════════════════════════════════════════════
# 4. 從 44 個 mode 嘅 beat frequency 搵 CKM 角公式
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 從 44 個 mode 嘅 beat frequency 搵 CKM 角公式")
print("─" * 80)

# 已知: CKM 角來自不同 mode 之間嘅 beat
# θ₁₂ = Cabibbo angle = 13.04°
# θ₁₂ = arctan(|V_us|/|V_ud|)

# 如果 |V_us| ∝ 某個 beat, |V_ud| ∝ 另一個 beat
# 則 tan(θ₁₂) = beat_us / beat_ud

# 搵 beat ratio 接近 tan(13.04°) = 0.2316 嘅 pair
tan_θ12 = math.tan(math.radians(13.04))
print(f"\n  tan(θ₁₂) = tan(13.04°) = {tan_θ12:.6f}")

# 計算所有 beat ratio
print(f"\n  搵 beat ratio ≈ {tan_θ12:.6f}:")
best_ratio = []
for i in range(44):
    for j in range(i+1, 44):
        beat_ij = abs(ω[i] - ω[j])
        if beat_ij < 1e-10:
            continue
        for k in range(44):
            for l in range(k+1, 44):
                beat_kl = abs(ω[k] - ω[l])
                if beat_kl < 1e-10:
                    continue
                ratio = beat_ij / beat_kl
                if abs(ratio - tan_θ12) < 0.01:
                    best_ratio.append((abs(ratio - tan_θ12), i+1, j+1, k+1, l+1, ratio))

best_ratio.sort(key=lambda x: x[0])
print(f"  {'rank':>4} | {'beat(i,j)':>12} | {'beat(k,l)':>12} | {'ratio':>10} | {'誤差':>10}")
print("-" * 55)
for rank, (err, i, j, k, l, ratio) in enumerate(best_ratio[:10]):
    print(f"  {rank+1:>4} | ({i:2d},{j:2d})={abs(ω[i-1]-ω[j-1]):>8.6f} | ({k:2d},{l:2d})={abs(ω[k-1]-ω[l-1]):>8.6f} | {ratio:>10.6f} | {err:>10.6f}")

# 同樣搵 θ₂₃ 同 θ₁₃
tan_θ23 = math.tan(math.radians(2.38))
tan_θ13 = math.sin(math.radians(0.201))

print(f"\n  tan(θ₂₃) = tan(2.38°) = {tan_θ23:.6f}")
print(f"  sin(θ₁₃) = sin(0.201°) = {tan_θ13:.6f}")

# 特別關注: V_ub = sin(θ₁₃) = 0.00369 = ε³ = φ⁻³/64
# 呢個係已知嘅結構公式!
# 從 44 個 mode 睇, ε³ 對應邊個 beat?
print(f"\n  已知: V_ub = ε³ = φ⁻³/64 = {ε**3:.6f}")
print(f"  搵 beat frequency ≈ {ε**3:.6f}:")

best_beat = []
for i in range(44):
    for j in range(i+1, 44):
        beat = abs(ω[i] - ω[j])
        if abs(beat - ε**3) < 0.001:
            best_beat.append((abs(beat - ε**3), i+1, j+1, beat))

best_beat.sort(key=lambda x: x[0])
for err, i, j, beat in best_beat[:5]:
    print(f"    ({i:2d},{j:2d}): |ω_{i}-ω_{j}| = {beat:.6f} (誤差 {err:.6f})")

# ══════════════════════════════════════════════════════════════
# 5. 用 φ-power 直接從 44 個 mode 構建 CKM
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 用 φ-power 直接從 44 個 mode 構建 CKM")
print("─" * 80)

# 從 beat frequency 分析, CKM 角應該係 φ-power 公式
# 已知:
#   θ₁₂ ≈ 13.58° (從 3×3 submatrix)
#   θ₂₃ ≈ 3.97° (從 6×6+VEV+Z₅)
#   θ₁₃ = arcsin(ε³) = 0.211°
#   δ = 4π/5 = 144°

# 但呢啲係從 12D 數值推導
# 從 44 個 mode 直接推導需要搵出對應嘅 beat

# 用 44 個 mode 嘅 (Z₃, Z₅) 分類構建 CKM:
# 每個 CKM 元素 V_ij = 粒子 i 同粒子 j 嘅 mode overlap
# 粒子 i 對應 mode n_i, 粒子 j 對應 mode n_j
# Overlap = f(γ_{n_i}, γ_{n_j}, Z₃, Z₅)

# 假設: 
# 共享 Z₅ → 最大 overlap (∼1)
# 唔共享 Z₅ → 次級 overlap (∼φ⁻¹)
# 世代距離 → 額外壓抑 (∼φ^{-|Δgen|})

# 從 44 個 mode 嘅 γ_n 構建 overlap matrix
# 用 Z₃ × Z₅ 決定權重, 用 γ_n 修正

# 先確定每個粒子嘅 mode number
# 從 12D index 分配開始:
# 但呢個係從 12D 數值, 唔係從 44 個 mode
# 需要從 44 個 mode 嘅結構搵出正確映射

# 從 44 個 mode 嘅 Z₃ × Z₅, 每個粒子有 3 個候選
# 揀 γ_n 最接近質量排序嘅一個

# 質量排序 (由重到輕): Top > Bottom > Tau > Charm > Strange > Muon > Up > Down > Electron
# γ_n 排序 (由小到大): γ_1 < γ_2 < ... < γ_44

# 所以: 最重粒子 = 最小 γ_n = n=1
# 但 n=1 嘅 Z₃=1, Z₅=1 — 唔係 Top (Z₃=0, Z₅=0)

# 所以粒子唔係直接對應單個 mode, 而係 mode 嘅組合
# 每個粒子 = 多個 mode 嘅疊加

# 呢個就係關鍵: 12 個物理粒子 = 44 個 mode 嘅線性組合
# CY₃ 投影 = 44D → 12D 投影
# 12D d_tensor 就係呢個投影嘅近似

# 但 user 話要從 44 個 mode 直接推導
# 可能係用 44 個 mode 嘅 γ_n 同 Z₃ × Z₅ 直接構建 Yukawa

# 方法: 每個 generation 有 2 個 doublet (up, down)
# 每個 doublet 嘅 2 個 component 共享 Z₃ 但 Z₅ 差 1
# 跨 generation 混合 = Z₅ orbit 連接

# 直接從 44 個 mode 嘅 γ_n 構建 12×12 Yukawa:
# Y_{ij} = Σ_{k=1}^{44} f(γ_k, Z₃_i, Z₃_j, Z₅_i, Z₅_j)
# 其中 f 係某種結構函數

# 但呢個就係 d_tensor 嘅 44D 版本!
# 或者: 用 44 個 mode 嘅 γ_n 直接構建 3×3 CKM

# 3×3 CKM 直接從 44 個 mode 嘅 overlap:
# 每個 up/down 粒子係一個「mode cluster」
# 3 個 up cluster: U₁, U₂, U₃
# 3 個 down cluster: D₁, D₂, D₃
# CKM_ij = <U_i|D_j> (inner product)

# 每個 cluster 係 44D 空間嘅向量
# Cluster 向量由 Z₃ × Z₅ 決定

# 構建 3 個 up cluster (Top, Charm, Up):
# 每個 cluster 係 44 個 mode 嘅線性組合
# 權重由 Z₃ 同 Z₅ 決定

# 對於 generation g (Z₃=g), up-type (Z₅=0):
# U_g = Σ_{n: n%3=g, n%5=0} w_n |n⟩
# 其中 w_n = f(γ_n)

# 同樣對於 down-type (Z₅=1):
# D_g = Σ_{n: n%3=g, n%5=1} w_n |n⟩

# 從 44 個 mode 中, 每個 (Z₃, Z₅) 組合有 3 個 mode (n1, n2, n3)
# 權重: w_n = γ_n / Σγ (normalized)

# 構建 cluster vectors
# 每個 cluster 對應一個 (Z₃, Z₅) pair
# Cluster 向量嘅分量 = 權重 w_n

# 對於每個 (Z₃, Z₅), 有 3 個 mode
# 權重 ∝ γ_n (大 γ = 大權重 = 輕粒子)

print(f"\n  Cluster 向量構建:")
print(f"  每個 (Z₃, Z₅) 組合嘅 mode 同權重:")

clusters = {}
for z3 in range(3):
    for z5 in range(5):
        modes = z3z5_modes.get((z3, z5), [])
        if modes:
            # 權重: γ_n (大 γ = 大權重)
            weights = [γ[n-1] for n in modes]
            total = sum(weights)
            w_norm = [w/total for w in weights]
            clusters[(z3, z5)] = list(zip(modes, w_norm))

# 3 個 up cluster (Z₅=0)
up_clusters = {}
for z3 in range(3):
    key = (z3, 0)
    if key in clusters:
        modes_weights = clusters[key]
        # 構建 44D 向量
        vec = np.zeros(44)
        for n, w in modes_weights:
            vec[n-1] = w
        up_clusters[z3] = vec
        print(f"    Up Gen{z3+1} (Z₃={z3}, Z₅=0): modes={[m for m,w in modes_weights]}, weights={[f'{w:.4f}' for m,w in modes_weights]}")

# 3 個 down cluster (Z₅=1)
down_clusters = {}
for z3 in range(3):
    key = (z3, 1)
    if key in clusters:
        modes_weights = clusters[key]
        vec = np.zeros(44)
        for n, w in modes_weights:
            vec[n-1] = w
        down_clusters[z3] = vec
        print(f"    Down Gen{z3+1} (Z₃={z3}, Z₅=1): modes={[m for m,w in modes_weights]}, weights={[f'{w:.4f}' for m,w in modes_weights]}")

# CKM = <U_i|D_j> (inner product)
V_ckm_cluster = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        if i in up_clusters and j in down_clusters:
            V_ckm_cluster[i, j] = np.dot(up_clusters[i], down_clusters[j])

# 行正規化
for i in range(3):
    row_sum = sum(V_ckm_cluster[i, :])
    if row_sum > 0:
        V_ckm_cluster[i, :] /= row_sum

# PDG 參考
V_PDG = np.array([
    [0.97435, 0.22500, 0.00369],
    [0.22486, 0.97349, 0.04182],
    [0.00857, 0.04110, 0.99912],
])

print(f"\n  CKM (從 44 個 mode cluster):")
for row in V_ckm_cluster:
    print(f"    {[f'{x:.6f}' for x in row]}")

print(f"\n  PDG 參考:")
for row in V_PDG:
    print(f"    {[f'{x:.6f}' for x in row]}")

θ12_c = math.degrees(math.atan2(V_ckm_cluster[0, 1], V_ckm_cluster[0, 0]))
θ23_c = math.degrees(math.atan2(V_ckm_cluster[1, 2], V_ckm_cluster[2, 2]))
θ13_c = math.degrees(math.asin(min(V_ckm_cluster[0, 2], 1.0)))

print(f"\n  {'參數':>10} | {'44-cluster':>12} | {'PDG':>12} | {'偏差':>10}")
print("-" * 50)
print(f"  {'θ₁₂':>10} | {θ12_c:>12.4f}° | {13.04:>12.4f}° | {abs(θ12_c-13.04):>9.4f}°")
print(f"  {'θ₂₃':>10} | {θ23_c:>12.4f}° | {2.38:>12.4f}° | {abs(θ23_c-2.38):>9.4f}°")
print(f"  {'θ₁₃':>10} | {θ13_c:>12.4f}° | {0.201:>12.4f}° | {abs(θ13_c-0.201):>9.4f}°")

# ══════════════════════════════════════════════════════════════
# 6. 儲存結果
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 儲存結果")
print("─" * 80)

lines = []
lines.append("IDCM v10.0 — 從 44 K_Chain mode 推導 CKM")
lines.append("=" * 60)
lines.append("")
lines.append("44 個 mode 嘅 Z₃ × Z₅ 分類:")
for z3 in range(3):
    for z5 in range(5):
        key = (z3, z5)
        if key in z3z5_modes:
            lines.append(f"  (Z₃={z3}, Z₅={z5}): n = {z3z5_modes[key]}")
lines.append("")
lines.append(f"CKM (cluster model):")
for row in V_ckm_cluster:
    lines.append(f"  [{', '.join(f'{x:.6f}' for x in row)}]")
lines.append(f"θ₁₂ = {θ12_c:.4f}°")
lines.append(f"θ₂₃ = {θ23_c:.4f}°")
lines.append(f"θ₁₃ = {θ13_c:.4f}°")

with open("open_problems_fresh/ckm_reconstruction/kchain_44_ckm_results.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存結果 ✅")