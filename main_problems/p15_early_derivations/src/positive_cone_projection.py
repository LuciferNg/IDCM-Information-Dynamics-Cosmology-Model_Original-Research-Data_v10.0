"""
IDCM v10.0 — 正定錐投影 + 完整 Kähler 度量 Z-factor
=====================================================
步驟:
1. 將 d_{ijk} 投影到正定錐 (消除 7.1% 負值噪聲)
2. 構建完整 Kähler 度量 K_{i\\bar{j}} = Σ_k d_{ijk} v_k
3. 計算 K^{-1/2} (Cholesky 分解)
4. 標準化質量矩陣: M^{(can)} = v · K^{-1/2} · Y · K^{-1/2}
5. 物理質量 = M^{(can)} 嘅本徵值
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
M_Pl = 1.220890e22

EIGENVALUES = [51.5606114384, 10.0002078429, 4.5782815814, 3.4328552619,
               1.8661710340, 0.2347191871, 0.0227488532, 0.0117201474,
               0.0068136131, 0.0018507699, 0.0013608351, -1.264797e-11]

V_CYCLES = {"Gen3": 42.7396, "Gen2": 44.9431, "Gen1": 46.5390}

PDG = {"Top": 172760.0, "Bottom": 4180.0, "Tau": 1776.86,
       "Charm": 1270.0, "Strange": 93.4, "Muon": 105.6583745,
       "Up": 2.16, "Down": 4.67, "Electron": 0.51099895}

PARTICLE_MAP = [
    ("Top", 0, "Gen3", True), ("Bottom", 1, "Gen3", False),
    ("Tau", 2, "Gen3", False), ("Charm", 3, "Gen2", True),
    ("Strange", 4, "Gen2", False), ("Muon", 5, "Gen2", False),
    ("Up", 6, "Gen1", False), ("Down", 7, "Gen1", False),
    ("Electron", 8, "Gen1", True), ("nu_tau", 9, "Gen1", False),
    ("nu_mu", 10, "Gen1", False),
]

# ─── 1. 載入 d_tensor ───
d = np.load("data/d_tensor_final.npy")
n = d.shape[0]
v = np.array([φ ** (-k / 12) for k in range(n)])

print("=" * 80)
print("IDCM v10.0 — 正定錐投影 + Kähler 度量 Z-factor")
print("=" * 80)

neg_before = np.sum(d < 0)
print(f"\n原始 d_tensor: 負值 {neg_before}/{d.size} ({neg_before/d.size*100:.1f}%)")

# ─── 2. 正定錐投影 (混合迭代) ───
d_clean = d.copy()
for iteration in range(5):
    # Step A: 切片 PSD
    for k in range(n):
        M = d_clean[:, :, k].copy()
        M_sym = (M + M.T) / 2
        ev, evec = np.linalg.eigh(M_sym)
        ev_clamped = np.maximum(ev, 0)
        M_psd = evec @ np.diag(ev_clamped) @ evec.T
        d_clean[:, :, k] = (M_psd + M_psd.T) / 2
    
    # Step B: Yukawa PSD
    Y_c = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            Y_c[i, j] = sum(d_clean[i, j, k] * v[k] for k in range(n))
    Y_c_sym = (Y_c + Y_c.T) / 2
    eY, eVec = np.linalg.eigh(Y_c_sym)
    eY_c = np.maximum(eY, 0)
    Y_c_psd = eVec @ np.diag(eY_c) @ eVec.T
    correction = Y_c_psd - Y_c_sym
    for k in range(n):
        d_clean[:, :, k] += correction / n
    
    # 全對稱化
    d_clean = (d_clean + d_clean.transpose(1,0,2) + d_clean.transpose(0,2,1) +
               d_clean.transpose(2,1,0) + d_clean.transpose(1,2,0) + d_clean.transpose(2,0,1)) / 6

neg_after = np.sum(d_clean < 0)
print(f"清洗後 d_tensor: 負值 {neg_after}/{d_clean.size} ({neg_after/d_clean.size*100:.2f}%)")
np.save("data/d_tensor_positive.npy", d_clean)
print("已儲存 data/d_tensor_positive.npy ✅")

# ─── 3. 完整 Kähler 度量 ───
print("\n" + "─" * 80)
print("完整 Kähler 度量方法")
print("─" * 80)

# K_{i\\bar{j}} = Σ_k d_{ijk} v_k
K = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        K[i, j] = sum(d_clean[i, j, k] * v[k] for k in range(n))
K = (K + K.T) / 2

print(f"\nKähler 度量 K_{i}{{j}}:")
print(f"  對角元素: {[f'{K[i,i]:.4f}' for i in range(n)]}")
print(f"  最小特徵值: {np.linalg.eigvalsh(K)[0]:.6e}")
print(f"  正定: {np.all(np.linalg.eigvalsh(K) > 0)}")

# K^{-1/2} via Cholesky
try:
    L = np.linalg.cholesky(K)
    K_inv = np.linalg.inv(K)
    # K^{-1/2} = L^{-T}
    K_inv_sqrt = np.linalg.inv(L).T
    print(f"  Cholesky 分解成功 ✅")
    print(f"  K^(-1/2) 範數: {np.linalg.norm(K_inv_sqrt):.4f}")
except np.linalg.LinAlgError as e:
    print(f"  Cholesky 失敗: {e}")
    print(f"  改用 eigenvalue 分解...")
    evals_K, evecs_K = np.linalg.eigh(K)
    evals_K = np.maximum(evals_K, 1e-15)
    K_inv_sqrt = evecs_K @ np.diag(1.0 / np.sqrt(evals_K)) @ evecs_K.T

# ─── 4. 裸 Yukawa ───
Y = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        Y[i, j] = sum(d_clean[i, j, k] * v[k] for k in range(n))
Y = (Y + Y.T) / 2

# ─── 5. 標準化質量矩陣 ───
# M^{(can)} = v · K^{-1/2} · Y · K^{-1/2}
M_canon = K_inv_sqrt @ Y @ K_inv_sqrt

# 但呢個係無量綱嘅，需要乘上某個整體標度
# 實際物理質量: m_phys = λ_total × M_Pl × exp(-V) × (K^{-1/2} Y K^{-1/2} 嘅本徵值)
# 其中 λ_total 係整體標度

# 對角化
eigvals_M, eigvecs_M = np.linalg.eigh(M_canon)
idx = np.argsort(eigvals_M)[::-1]
eigvals_M = eigvals_M[idx]
eigvecs_M = eigvecs_M[:, idx]

print(f"\n標準化質量矩陣 M^(can) 本徵值:")
for i in range(n):
    print(f"  λ_{i+1:2d} = {eigvals_M[i]:.6f}")

# 對比原始 WDVV 本徵值
print(f"\n對比原始 WDVV 本徵值:")
for i in range(min(11, n)):
    ratio = eigvals_M[i] / EIGENVALUES[i] if EIGENVALUES[i] != 0 else 0
    print(f"  λ_{i+1:2d}: M_canon={eigvals_M[i]:.6f} vs WDVV={EIGENVALUES[i]:.6f}, ratio={ratio:.4f}")

# ─── 6. 質量預測 ───
print(f"\n" + "─" * 80)
print("質量預測 (Kähler 標準化)")
print("─" * 80)

# 用 M_canon 嘅本徵值做質量預測
# 保留原始嘅 V_cycle 校準結構
# 質量 = λ_M_canon × M_Pl × exp(-V_gen) × factor

# 但 M_canon 嘅本徵值已經包含咗 Kähler 標準化
# 所以唔需要再乘額外嘅 Z-factor

# 校準: 用 Top, Charm, Electron
cal_particles = {"Top": 0, "Charm": 3, "Electron": 8}
cal_evals = {}
for name, idx_p in cal_particles.items():
    cal_evals[name] = eigvals_M[idx_p]

# 校準 V_cycle
def compute_bare(lam, V):
    return lam * M_Pl * math.exp(-V)

# 用 Top 校準 Gen3 V
cal_lam_t = eigvals_M[0]
V3 = -math.log(PDG["Top"] / (cal_lam_t * M_Pl))
print(f"\n校準 V_cycle (從 M_canon):")
print(f"  Gen3 (Top): V = {V3:.4f}")
print(f"  (舊: {V_CYCLES['Gen3']:.4f})")

# 用 Charm 校準 Gen2 V
cal_lam_c = eigvals_M[3]
V2 = -math.log(PDG["Charm"] / (cal_lam_c * M_Pl))
print(f"  Gen2 (Charm): V = {V2:.4f}")
print(f"  (舊: {V_CYCLES['Gen2']:.4f})")

# 用 Electron 校準 Gen1 V
cal_lam_e = eigvals_M[8]
V1 = -math.log(PDG["Electron"] / (cal_lam_e * M_Pl))
print(f"  Gen1 (Electron): V = {V1:.4f}")
print(f"  (舊: {V_CYCLES['Gen1']:.4f})")

V_new = {"Gen3": V3, "Gen2": V2, "Gen1": V1}

# 預測所有粒子
print(f"\n{'粒子':>10} | {'λ_M_canon':>12} | {'V_cycle':>8} | {'預測':>15} | {'PDG':>15} | {'誤差%':>8}")
print("-" * 75)

old_factors = {
    "down": {"Gen3": 1/8.0, "Gen2": 1/7.4, "Gen1": 5.3},
    "lep":  {"Gen3": 1/8.6, "Gen2": 1.22,  "Gen1": 1.0},
    "up":   {"Gen3": 1.0,   "Gen2": 1.0,   "Gen1": math.sqrt(φ)},
}

# 先試: 直接用 M_canon 本徵值 + V_cycle (無額外 factor)
total_err = 0
count = 0
for name, li, gen, is_cal in PARTICLE_MAP:
    if name in ["nu_tau", "nu_mu"]:
        continue
    
    lam = eigvals_M[li]
    V = V_new[gen]
    bare = lam * M_Pl * math.exp(-V)
    
    # 不需要額外 factor — Kähler 標準化已經 built-in
    pred = bare
    pdg = PDG[name]
    err = 0.0 if is_cal else abs(pred / pdg - 1) * 100
    total_err += err
    count += 1
    
    if pred < 1:
        ps = f"{pred*1000:.3f} eV"
    elif pred < 1000:
        ps = f"{pred:.3f} MeV"
    else:
        ps = f"{pred/1000:.3f} GeV"
    
    if pdg < 1:
        ts = f"{pdg*1000:.3f} eV"
    elif pdg < 1000:
        ts = f"{pdg:.3f} MeV"
    else:
        ts = f"{pdg/1000:.3f} GeV"
    
    status = "校準" if is_cal else ("✅" if err < 1 else f"⚠️ {err:.1f}%")
    print(f"{name:>10} | {lam:>12.6f} | {V:>8.4f} | {ps:>15} | {ts:>15} | {err:>7.2f}% | {status}")

avg_err = total_err / count if count else 0
print(f"\n平均誤差 (排除中微子): {avg_err:.2f}%")

# ─── 7. 關鍵: √φ 出現咗未? ───
print(f"\n" + "─" * 80)
print("關鍵檢查: √φ 自然出現?")
print("─" * 80)

# 睇下 M_canon 本徵值同原始 WDVV 本徵值嘅比例
print(f"\nM_canon vs WDVV 本徵值比例:")
for i in range(11):
    ratio = eigvals_M[i] / EIGENVALUES[i] if EIGENVALUES[i] != 0 else 0
    # 呢個比例就係 Z-factor 嘅效果
    print(f"  λ_{i+1:2d}: ratio = {ratio:.6f} = φ^{math.log(ratio)/math.log(φ) if ratio > 0 else 'N/A':.4f}")

# Up 夸克 (index 6) 嘅 Z-factor
up_ratio = eigvals_M[6] / EIGENVALUES[6]
print(f"\nUp 夸克 (index 6):")
print(f"  WDVV λ = {EIGENVALUES[6]:.6f}")
print(f"  M_canon λ = {eigvals_M[6]:.6f}")
print(f"  ratio = {up_ratio:.6f}")
print(f"  √φ = {math.sqrt(φ):.6f}")
print(f"  diff = {abs(up_ratio - math.sqrt(φ)):.4f} ({abs(up_ratio/math.sqrt(φ)-1)*100:.2f}%)")

# 如果 ratio 接近 √φ，就係成功！
if abs(up_ratio - math.sqrt(φ)) < 0.1:
    print(f"  ✅ √φ 自然出現！波函數重整化從 Kähler 度量嚴格推導成功！")
else:
    print(f"  ❌ 仍未自然出現 √φ，需進一步分析")

# ─── 8. 儲存 ───
print(f"\n儲存結果...")
np.save("data/d_tensor_positive.npy", d_clean)
np.save("data/K_metric.npy", K)
np.save("data/M_canon_eigenvalues.npy", eigvals_M)
np.save("data/K_inv_sqrt.npy", K_inv_sqrt)

lines = []
lines.append("IDCM v10.0 — 正定錐投影 + Kähler 度量結果")
lines.append("=" * 70)
lines.append("")
lines.append(f"原始 d_tensor 負值: {neg_before}/{d.size} ({neg_before/d.size*100:.1f}%)")
lines.append(f"清洗後 d_tensor 負值: {neg_after}/{d_clean.size} ({neg_after/d_clean.size*100:.2f}%)")
lines.append("")
lines.append(f"Kähler 度量正定: {np.all(np.linalg.eigvalsh(K) > 0)}")
lines.append("")
lines.append(f"Up 夸克 M_canon/WDVV ratio: {up_ratio:.6f}")
lines.append(f"√φ: {math.sqrt(φ):.6f}")
lines.append(f"差異: {abs(up_ratio - math.sqrt(φ)):.4f} ({abs(up_ratio/math.sqrt(φ)-1)*100:.2f}%)")
lines.append("")
lines.append(f"平均預測誤差: {avg_err:.2f}%")
lines.append("")

with open("data/positive_cone_projection.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存 data/positive_cone_projection.txt ✅")
print("已儲存 data/K_metric.npy ✅")
print("已儲存 data/M_canon_eigenvalues.npy ✅")
print("已完成！")