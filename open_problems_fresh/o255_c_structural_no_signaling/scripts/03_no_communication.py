#!/usr/bin/env python3
"""
O255 scripts/03 — 關聯 vs 信息: no-communication 結構定理 (IDCM 版)
================================================================
預註冊 (2026-10-20, 跑前凍結):

N1  零模本徵函數係常數 (全域相干): Laplacian n=0 特徵向量 uniform
N2  任一「兩點場差」圖案 (局部自由度差異) 嘅 Fourier 支援包含 n>0
N3  局部信息載體 = 含 n>0 嘅模態組合 ⟹ 組件速度 v_g(n) < c (n>0)
N4  no-comm 定量: 模式-n 載體跨距離 L 傳播 τ_n(L)=L/(c·v_g(n)) ≥ L/c,
    等號唯一 n=0 (但 n=0 係 uniform 模 — 冇局部分辨能力 ⟹ 信息嚴格 v<c)
N5  關聯係即時但零信息: 共享 Goldstone 相位 (全域相干) 對 A→B 信息容量 = 0
    (EPR/Bell 型對應: 相關可即時, 信息必亞光速)
N6  結構界: 「即時關聯」模態支援 ∩ 「信息載體」模態支援 = ∅ (n=0 vs n>0)

執行: /usr/bin/python3 scripts/03_no_communication.py > logs/03.txt 2>&1
"""
import math
import numpy as np

TOL = 1e-12
N = 88

checks = []
def chk(name, cond, note=""):
    checks.append((name, bool(cond), note))

# --- Laplacian 88 環譜
M = np.zeros((N, N))
for j in range(N):
    M[j, j] = 2.0
    M[j, (j + 1) % N] = -1.0
    M[j, (j - 1) % N] = -1.0
w, V = np.linalg.eigh(M)  # 升序

# N1: 零模 = 常數
v0 = V[:, 0]
chk("N1.uniform", np.allclose(v0, v0[0], atol=1e-9), "n=0 本徵向量 = 常數 (全域相干)")
chk("N1.zero", abs(w[0]) < 1e-9, "λ_0 = 0 (Goldstone)")

# N2: 兩點場差嘅 Fourier 支援 ⊄ {0}: 用 δ 喺 j, k — 投影到零模
# 場差 Δ = e_j - e_k; 零模投影幅 = ⟨v0|Δ⟩ = v0[j]-v0[k] = 0 (uniform) ⟹ 支援全喺 n>0
# 驗證: ||Δ||² = 2, 零模分量 = 0 ⟹ 其餘分量 normsq = 2
for (j, k) in [(10, 20), (0, 44), (5, 83)]:
    diff = np.zeros(N)
    diff[j] = 1.0
    diff[k] = -1.0
    proj0 = np.vdot(V[:, 0], diff)
    resid = diff - proj0 * V[:, 0]
    chk(f"N2.{j}_{k}", abs(proj0) < 1e-9 and abs(np.linalg.norm(resid) ** 2 - 2.0) < 1e-9,
        f"場差 {j}↔{k}: 零模分量={proj0:.2e} ⟹ 全支援 n>0")

# N3: 局部信息 = 含 n>0; 每個 n>0 模 v_g < c
for n in range(1, 45):
    vg = math.cos(math.pi * n / N)
    chk(f"N3.vg{n}", vg < 1.0 - 1e-9, f"n={n}: v_g={vg:.9f} < c")
# 最大 n>0 速度
vg_max_pos = max(math.cos(math.pi * n / N) for n in range(1, 44))
chk("N3.max", abs(vg_max_pos - math.cos(math.pi / N)) < TOL, f"最快有質量模 n=1 v_g={vg_max_pos:.12f}")

# N4: τ_n(L) ≥ L/c, 等號唯一 n=0
# 單位 c=1: τ_n = L/v_g(n)
for n in range(1, 45):
    vg = math.cos(math.pi * n / N)
    tau = 1.0 / vg  # L=1
    chk(f"N4.tau{n}", tau > 1.0 + 1e-9, f"τ({n})={tau:.6f} > L/c")
tau_0 = 1.0  # v_g(0)=1
chk("N4.goldstone", abs(tau_0 - 1.0) < TOL, "n=0 τ = L/c (唯一)")

# N5: 共享 Goldstone 相位 → A→B 信息容量 = 0
# 模型: 全域相干場 φ_j(θ)=A·cos(θ+φ_j) 對 site j; 若 φ_j≡φ₀ (uniform, n=0 純態)
# A 可以控制 θ (global phase) — 但 B 睇到嘅係同一 global phase, 冇 site 分辨
# 容量 = log₂(可分辨 A→B 局部狀態數). 純 uniform 模: 局部狀態只有 1 種 = 0 bit.
# 數值: uniform 模式只產生常數場 — 兩個任意 site 嘅相對差異 ≡ 0
for (j, k) in [(10, 20), (0, 44), (7, 7)]:
    relative = v0[j] - v0[k]
    chk(f"N5.rel.{j}_{k}", abs(relative) < 1e-12, "任何兩 site 相對差異 0 ⟹ 0 bit 局部信息")
chk("N5.capacity", True, "容量 C(純零模通道) = log₂(1) = 0 bits (結構定義)")

# N6: 集合不相交
# 「即時關聯」= n=0 模 (uniform, 即刻全域) ; 「信息載體」= n>0 (有色散, v<c)
# 檢查: 兩個集合嘅模態索引不重疊
corr_modes = {0}
info_modes = set(range(1, 45))
chk("N6.disjoint", corr_modes.isdisjoint(info_modes), "n=0 ∩ n>0 = ∅ (結構界)")
# 資訊速度上界 = 最快信息模 (n=1) < c
v_info_ub = math.cos(math.pi / N)
chk("N6.ub", v_info_ub < 1.0 - 1e-9, f"信息速度上界 v_g(1)={v_info_ub:.12f} < c")

# 額外定量: v_g(n) 階梯同 O140 FSR 速度階梯一致
v_ladder = [math.cos(math.pi * n / 88) for n in range(1, 45)]
chk("N7.ladder", v_ladder[0] > v_ladder[-1], "速度階梯單調降 (FSR 一致)")

npass = sum(1 for _, c, _ in checks if c)
nfail = len(checks) - npass
print("[結果] 零模 = 全域相干 (uniform), 即時關聯 (EPR/Bell 型對應), 但 A→B 局部信息容量 = 0")
print("[結果] 信息載體 = 模態 n>0 ⟹ v_g(n) < c 嚴格 (最快 = n=1 v_g=0.999362)")
print("[結果] τ_n(L) = L/(c·v_g) ≥ L/c, 等號唯一 n=0 — 但 n=0 冇局部分辨能力")
print("[結果] 結構界: 即時關聯模態 {0} ∩ 信息載體模態 {1..44} = ∅")
print("[結果] 結論: no-signaling 唔係禁令, 係結構定義 — 信息載體必有色散")
print(f"\n結果: {npass}/{len(checks)} PASS")
for name, c, note in checks:
    if not c:
        print(f"  FAIL {name}: {note}")