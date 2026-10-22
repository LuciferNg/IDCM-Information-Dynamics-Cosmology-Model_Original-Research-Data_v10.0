#!/usr/bin/env python3
"""
O62 一期 03: F(γ) 精確結構 + 修正項候選審計
============================================
一期 02 發現: F(γ) = 264.0821 (t=γ_n 自然方案)
  F(γ) + 44γ₆ + L₅ = 283.0345 (0.0144%)
  初步檢查: V_obs − F(γ) = 18.9931 ≈ 19.0000 (0.036%)
  19 = 44 − F₈ − B = 44 − 21 − 4 (CPX kernel 缺口補償!)

本腳本:
  1. F(γ) 精確分解 (264.0821 = 6N_d + ?)
  2. ΔV = V_obs − F(γ) 修正候選完整比較
  3. 統計對照: random t / random κ 下 F(t) 分佈 → γ 方案顯著性
  4. 第一性原理鏈評估
"""
import sys, os, math, json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O62 一期 03: F(γ) 精確結構 + 修正候選審計")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 基本量 ============
print("\n[1] 基本量")
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
gamma36 = 4 * np.sin(np.pi * np.arange(1, 37) / 88) ** 2
L = [2, 1]
for i in range(2, 40):
    L.append(L[i-1] + L[i-2])
F_ = [1, 1]
for i in range(2, 40):
    F_.append(F_[i-1] + F_[i-2])

def F(t):
    return np.einsum("ijk,i,j,k", kappa, t, t, t) / 6.0

V_obs = 283.0752
Fg = F(gamma36)
dV = V_obs - Fg
print(f"  F(γ) = {Fg:.10f}")
print(f"  ΔV = V_obs − F(γ) = {dV:.10f}")

# ============ 2. F(γ) 精確分解 ============
print("\n[2] F(γ) 精確分解")
print(f"  F(γ) = {Fg:.12f}")
print(f"  6×44 = {6*44}, F(γ)−264 = {Fg-264:.8f}")
print(f"  F(γ)/44 = {Fg/44:.10f}")
print(f"  F(γ)/6 = {Fg/6:.10f}")

# 高精度: F(γ) 係咪 = 264 + Σ c_n γ_n?
# F(γ) − 264 = 0.08212923
rem = Fg - 264
print(f"\n  剩餘 = F(γ) − 264 = {rem:.10f}")
print(f"  264 = 6×44 = 6N_d")
# γ_n 線性組合拟合
print(f"\n  γ_n 組合搜索:")
gamma44 = 4 * np.sin(np.pi * np.arange(1, 45) / 88) ** 2
best = []
for n in range(1, 45):
    for m in range(n, 45):
        val = gamma44[n-1] + gamma44[m-1]
        err = abs(val - rem)/rem*100
        if err < 2:
            best.append((err, f"γ_{n}+γ_{m}", val))
        val2 = gamma44[n-1] * gamma44[m-1]
        err2 = abs(val2 - rem)/rem*100
        if err2 < 2:
            best.append((err2, f"γ_{n}×γ_{m}", val2))
        val3 = gamma44[n-1] / (m+1)
        err3 = abs(val3 - rem)/rem*100
        if err3 < 2:
            best.append((err3, f"γ_{n}/{m+1}", val3))
best.sort()
for err, name, val in best[:10]:
    print(f"    {name:12s} = {val:.8f} (誤差 {err:.3f}%)")

# ============ 3. ΔV 修正候選完整表 ============
print("\n[3] ΔV = V_obs − F(γ) 修正候選")
g6 = 4*math.sin(6*math.pi/88)**2
g1 = 4*math.sin(math.pi/88)**2
g4 = 4*math.sin(4*math.pi/88)**2
cands = {
    "19 (整數)": 19.0,
    "44−F₈−B = 44−21−4": 44 - 21 - 4,
    "44−25 (CPX gap)": 44 - 25,
    "L₅+F₆ = 11+8": 11 + 8,
    "L₆+1 = 18+1": 18 + 1,
    "44γ₆+L₅": 44*g6 + 11,
    "44γ₆": 44*g6,
    "L₅+F₆+γ₁L₅": 11 + 8 + g1*11,
    "44γ₆+L₅+γ₁L₅": 44*g6 + 11 + g1*11,
    "2L₅−3 = 22−3": 22 - 3,
    "F₈−2 = 21−2": 21 - 2,
    "90/4.737": 90/4.737,
    "Σγ/4.737": 90/4.737,
    "44×γ₆+11.04": 44*g6 + 11.04,
    "B×L₅−25": 4*11 - 25,
    "F₁₀−36 = 55−36": 55 - 36,
}
print(f"  ΔV = {dV:.6f}")
print(f"  {'候選':22s} {'值':>12s} {'誤差%':>10s} {'結構':>6s}")
for name, val in cands.items():
    err = abs(val - dV)/dV*100
    # 結構標記
    if "44−" in name or "整數" in name or "L₅+F₆" in name or "L₆+1" in name:
        struct = "🟢"
    elif "γ₆" in name or "γ₁" in name:
        struct = "🟡"
    else:
        struct = "🔴"
    print(f"  {name:22s} {val:12.6f} {err:9.4f}% {struct}")

# ============ 4. 完整公式比較 ============
print("\n[4] 完整真空能公式比較")
V10 = L[10]*phi + L[9]
formulas = {
    "F(γ)+44−F₈−B": Fg + 44 - 21 - 4,
    "F(γ)+19": Fg + 19,
    "F(γ)+44γ₆+L₅": Fg + 44*g6 + 11,
    "F(γ)+44γ₆+L₅+γ₁L₅": Fg + 44*g6 + 11 + g1*11,
    "V₁₀+44γ₆ (O57)": V10 + 44*g6,
    "F(γ) (無修正)": Fg,
    "F(γ)+L₅": Fg + 11,
}
print(f"  V_obs = {V_obs:.8f}")
print(f"  {'公式':24s} {'值':>12s} {'誤差%':>10s}")
for name, val in formulas.items():
    err = abs(val - V_obs)/V_obs*100
    print(f"  {name:24s} {val:12.6f} {err:9.5f}%")

# ============ 5. 統計對照: random t ============
print("\n[5] 統計對照: random t 下 F(t) 分佈")
rng = np.random.default_rng(42)
# random t 喺 [0, 4] (γ 範圍) 正數
N_trials = 2000
Fs_random = []
for _ in range(N_trials):
    t_rand = rng.uniform(0.005, 4.0, 36)
    Fs_random.append(F(t_rand))
Fs_random = np.array(Fs_random)
# γ 方案 F 嘅 rank
rank_abs = np.sum(Fs_random < Fg) / N_trials  # F(γ) 大過幾多 random?
rank_neg = np.sum(Fs_random < 0) / N_trials
print(f"  random t ∈ U(0.005, 4)³⁶:")
print(f"    F mean = {Fs_random.mean():.2f}, std = {Fs_random.std():.2f}")
print(f"    F range: [{Fs_random.min():.2f}, {Fs_random.max():.2f}]")
print(f"    P(F < F(γ)) = {rank_abs:.4f} (γ 方案嘅百分位)")
print(f"    P(F < 0) = {rank_neg:.4f}")
print(f"    |F| < 100 比例: {np.sum(np.abs(Fs_random) < 100)/N_trials:.4f}")
print(f"    F ∈ [250, 300] 比例: {np.sum((Fs_random > 250) & (Fs_random < 300))/N_trials:.4f}")

# F(γ) 接近 264 = 6N_d 嘅顯著性
print(f"\n  F(γ) = {Fg:.2f} ≈ 264 = 6N_d?")
print(f"    P(|F − 264| < 1) random = {np.sum(np.abs(Fs_random - 264) < 1)/N_trials:.4f}")
print(f"    P(|F − 264| < 10) random = {np.sum(np.abs(Fs_random - 264) < 10)/N_trials:.4f}")

# ============ 6. 統計對照: random κ ============
print("\n[6] 統計對照: random κ 同譜 (保持稀疏度)")
# 生成 random κ: 相同稀疏度 (1341/46656 = 2.9%), 相同值域
kappa_flat = kappa.flatten()
nnz = np.count_nonzero(kappa)
mask = kappa_flat != 0
vals = kappa_flat[mask]
print(f"  真 κ: {nnz} 非零, 值域 [{vals.min():.0f}, {vals.max():.0f}]")
N_trials2 = 200
F_random_kappa = []
for _ in range(N_trials2):
    k_rand = np.zeros_like(kappa_flat)
    idx = rng.choice(len(kappa_flat), nnz, replace=False)
    k_rand[idx] = rng.choice(vals, nnz, replace=True)
    k_rand = k_rand.reshape(kappa.shape)
    Fk = np.einsum("ijk,i,j,k", k_rand, gamma36, gamma36, gamma36) / 6.0
    F_random_kappa.append(Fk)
F_random_kappa = np.array(F_random_kappa)
print(f"  random κ 對稱化? 未對稱 — 粗略對照")
print(f"    F mean = {F_random_kappa.mean():.2f}, std = {F_random_kappa.std():.2f}")
print(f"    F range: [{F_random_kappa.min():.2f}, {F_random_kappa.max():.2f}]")
print(f"    |F(γ)| = {abs(Fg):.2f} 百分位: {np.sum(np.abs(F_random_kappa) < abs(Fg))/N_trials2:.4f}")

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("一期 03 總結:")
print("=" * 72)
print(f"""
  F(γ) 結構:
  - F(γ) = {Fg:.6f} ≈ 264 = 6N_d (剩餘 {Fg-264:.6f})
  - ΔV = {dV:.6f} ≈ 19 (誤差 {abs(dV-19)/dV*100:.3f}%)

  最佳完整公式:
  - F(γ) + 44 − F₈ − B = {Fg+44-21-4:.6f} ({abs(Fg+44-21-4-V_obs)/V_obs*100:.5f}%)
  - F(γ) + 44γ₆ + L₅ = {Fg+44*g6+11:.6f} ({abs(Fg+44*g6+11-V_obs)/V_obs*100:.5f}%)

  統計:
  - random t 下 F(γ) 嘅百分位 = {rank_abs:.4f}
  - F(γ) ≈ 264 = 6N_d 嘅隨機概率 = {np.sum(np.abs(Fs_random - 264) < 10)/N_trials:.4f}
""")
out = {
    "test": "O62 一期 03: F(γ) 結構 + 修正審計",
    "F_gamma": float(Fg), "delta_V": float(dV),
    "F_minus_264": float(Fg - 264),
    "candidates": {k: float(v) for k, v in cands.items()},
    "formulas": {k: float(v) for k, v in formulas.items()},
    "stat_random_t": {"mean": float(Fs_random.mean()), "std": float(Fs_random.std()),
                      "pctile_Fg": float(rank_abs), "p_neg": float(rank_neg),
                      "p_250_300": float(np.sum((Fs_random>250)&(Fs_random<300))/N_trials)},
    "stat_random_kappa": {"mean": float(F_random_kappa.mean()), "std": float(F_random_kappa.std()),
                          "pctile": float(np.sum(np.abs(F_random_kappa) < abs(Fg))/N_trials2)},
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "03_F_gamma_structure.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 一期 03 完成!")
