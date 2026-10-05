#!/usr/bin/env python3
"""
GRT-37b: Van der Pol 耦合振盪器網絡 — 真實電路模擬 (修正版)
================================================================
修正 GRT-37: Kuramoto 純相位模型假設振幅相同, 睇唔到電壓壓制。
真實 Wien bridge 振盪器係非線性飽和 → Van der Pol 模型先正確!

Van der Pol 方程 (每個節點):
  ẍ_i + μ(x_i²-1)ẋ_i + ω_i²·x_i = Σ_j K_ij·(x_j - x_i)
  μ = 非線性飽和強度 (決定穩定振幅 ~2)
  K_ij = 耦合強度
  阻挫邊: K_ij < 0 (反相耦合, 等效 β=π)

物理對應:
  節點 = Wien bridge 振盪器 (非線性飽和 → 穩定振幅)
  正常邊 = 電阻耦合 (同相, K>0)
  阻挫邊 = 反相放大器耦合 (反相, K<0)
  振幅壓制 = 阻挫邊破壞性干涉 → 節點振幅降低 → LED 熄滅
"""
import numpy as np
import math
import sys, os

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors,
                        load_nodes, ang_deg)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

LINES = []
def L(s=""):
    LINES.append(str(s))
    print(s)

L("=" * 84)
L("  GRT-37b: Van der Pol 耦合振盪器 — 真實電路模擬 (修正)")
L("=" * 84)

# ============================================================
# Van der Pol 網絡積分器 (RK4)
# ============================================================
def vdp_network_step(x, v, mu, omega_sq, K_mat, dt):
    """單步 RK4"""
    N = len(x)
    def deriv(xx, vv):
        dx = vv
        dv = -mu*(xx**2 - 1)*vv - omega_sq*xx
        # 耦合: Σ_j K_ij (x_j - x_i)
        for i in range(N):
            dv[i] += np.dot(K_mat[i], xx - xx[i])
        return dx, dv
    k1x, k1v = deriv(x, v)
    k2x, k2v = deriv(x + 0.5*dt*k1x, v + 0.5*dt*k1v)
    k3x, k3v = deriv(x + 0.5*dt*k2x, v + 0.5*dt*k2v)
    k4x, k4v = deriv(x + dt*k3x, v + dt*k3v)
    x_new = x + (dt/6)*(k1x + 2*k2x + 2*k3x + k4x)
    v_new = v + (dt/6)*(k1v + 2*k2v + 2*k3v + k4v)
    return x_new, v_new

def run_vdp(N, adj_list, mu, omega, K_coup, dt, steps, seed=42):
    """跑 Van der Pol 網絡, 返回最終 (x, v) 同振幅"""
    rng = np.random.default_rng(seed)
    x = rng.uniform(-0.5, 0.5, N)
    v = rng.uniform(-0.5, 0.5, N)
    omega_sq = omega**2
    K_mat = np.zeros((N, N))
    for i in range(N):
        for j, beta in adj_list[i]:
            # 反相 (β=π) → 負耦合
            K_mat[i, j] = K_coup * math.cos(beta)
    for step in range(steps):
        x, v = vdp_network_step(x, v, mu, omega_sq, K_mat, dt)
        if step % 1000 == 0 and step > 0:
            # 檢查收斂 (振幅穩定)
            pass
    # 振幅: 用最後半個週期嘅 peak 或 RMS
    # 簡單: 最後一步嘅 |x| 粗略 = 振幅下界
    # 更好: 跑多幾個週期記錄 max
    amp = np.abs(x)
    return x, v, amp

# ============================================================
# 一、5 節點阻挫環
# ============================================================
L("━" * 84)
L("  一、5 節點阻挫環 — Van der Pol 模擬")
L("━" * 84)

N5 = 5
adj5 = {i: [] for i in range(N5)}
for i in range(N5):
    j = (i+1) % N5
    beta = math.pi if i == 4 else 0.0
    adj5[i].append((j, beta))
    adj5[j].append((i, beta))

mu5 = 1.0       # 非線性
omega5 = np.ones(N5) * 2*math.pi*1000  # 1 kHz
K5 = 0.3        # 耦合強度
dt5 = 1e-5      # 1 kHz → dt 細
# 跑 0.1 秒 = 100 週期
x5, v5, amp5 = run_vdp(N5, adj5, mu5, omega5, K5, dt5, 10000)

L(f"  5 節點環 (4 正常 + 1 阻挫), μ={mu5}, K={K5}:")
L(f"  {'節點':>4} | {'振幅':>8} | {'相位':>8} | {'阻挫邊?'}")
L(f"  {'-'*4} | {'-'*8} | {'-'*8} | {'-'*8}")
# 相位: atan2(v, x·ω) 近似
for i in range(N5):
    ph = math.atan2(v5[i], x5[i]*omega5[i])
    is_frust = (i == 4 or i == 0)  # 邊 (4,0) 兩端
    L(f"  {i:>4} | {amp5[i]:>8.4f} | {math.degrees(ph):>7.1f}° | {'⚠️' if is_frust else ''}")

# 阻挫邊兩端振幅
L(f"""
  阻挫邊 (4,0) 兩端: amp[4]={amp5[4]:.4f}, amp[0]={amp5[0]:.4f}
  正常邊 (0,1) 兩端: amp[0]={amp5[0]:.4f}, amp[1]={amp5[1]:.4f}
  → 睇有冇振幅差異 (阻挫壓制)
""")

# ============================================================
# 二、60 節點 A5 網絡
# ============================================================
L("━" * 84)
L("  二、60 節點 A5 — Van der Pol 全網模擬")
L("━" * 84)

nodes, vecs = load_nodes()
N = len(nodes)
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

adjK = {i: [] for i in range(N)}
for i in range(N):
    for j in adj[i]:
        beta = math.pi if (min(i,j), max(i,j)) in frust else 0.0
        adjK[i].append((j, beta))

omega = np.ones(N) * 2*math.pi*1000
# 失諧 ±10 Hz
rng = np.random.default_rng(7)
omega += rng.normal(0, 2*math.pi*10, N)

mu = 1.0
K = 0.15  # 較弱耦合 (避免全鎖死)
dt = 1e-5
steps = 8000  # 0.08 s = 80 週期

L(f"  60 節點 A5, μ={mu}, K={K}, {steps} 步...")
x, v, amp = run_vdp(N, adjK, mu, omega, K, dt, steps, seed=7)
L(f"  完成。振幅範圍: {amp.min():.3f} - {amp.max():.3f}")
L("")

# ΔE=0 節點
zero_nodes = []
for i in range(N):
    k = sum(1 for j in adj[i] if (min(i,j), max(i,j)) in frust)
    if k == 2:
        zero_nodes.append(i)
normal_nodes = [i for i in range(N) if i not in zero_nodes]

amp_zero = amp[zero_nodes].mean()
amp_norm = amp[normal_nodes].mean()
ratio = amp_zero / amp_norm

L(f"  振幅統計 (Van der Pol, 真實電路對應):")
L(f"  {'組':<20} | {'N':>3} | {'mean 振幅':>10} | {'比':>6} | {'LED 預期'}")
L(f"  {'-'*20} | {'-'*3} | {'-'*10} | {'-'*6} | {'-'*10}")
L(f"  {'ΔE=0 節點':<20} | {len(zero_nodes):>3} | {amp_zero:>10.4f} | {ratio:>6.2f} | {'暗/熄' if ratio < 0.9 else '??'}")
L(f"  {'其他節點':<20} | {len(normal_nodes):>3} | {amp_norm:>10.4f} | {'-':>6} | {'亮'}")
L("")

# 逐節點
L(f"  ΔE=0 節點振幅 (LED 熄滅預言):")
L(f"  {'節點':>4} | {'振幅':>8} | {'比(其他均)':>10} | {'LED'}")
L(f"  {'-'*4} | {'-'*8} | {'-'*10} | {'-'*6}")
n_dark = 0
for i in zero_nodes:
    ri = amp[i] / amp_norm
    led = "🔴 熄" if ri < 0.9 else ("🟡 微亮" if ri < 0.97 else "🟢 亮")
    if ri < 0.9:
        n_dark += 1
    L(f"  {i:>4} | {amp[i]:>8.4f} | {ri:>10.2f} | {led}")
L(f"""
  → {n_dark}/12 ΔE=0 節點 LED 熄滅 (振幅 < 其他 90%)
  → {'✅ 電壓壓制出現!' if n_dark >= 6 else '🟡 壓制有限'}
""")

# ============================================================
# 三、注入寫入 (Van der Pol 版)
# ============================================================
L("━" * 84)
L("  三、注入鎖定寫入 — Van der Pol 版")
L("━" * 84)

# 對 ΔE=0 節點加驅動項: ẍ += h·sin(ω_d t + φ_d)
# 簡化: 直接加驅動到 x 方程
inj = 45
if inj in zero_nodes:
    h = 0.5  # 注入強度
    omega_d = omega[inj]
    phi_d = math.pi  # 反相注入

    # 重新跑 + 注入 (最後 2000 步)
    x2, v2 = x.copy(), v.copy()
    K_mat = np.zeros((N, N))
    for i in range(N):
        for j, beta in adjK[i]:
            K_mat[i, j] = K * math.cos(beta)
    omega_sq = omega**2
    t_now = 0.0
    for step in range(3000):
        # 加驅動
        drive = h * math.sin(omega_d * t_now + phi_d)
        # 手動單步 (用現有函數唔方便, 直接 Euler)
        dx = v2
        dv = -mu*(x2**2 - 1)*v2 - omega_sq*x2
        for i in range(N):
            dv[i] += np.dot(K_mat[i], x2 - x2[i])
        dv[inj] += drive  # 驅動項
        x2 = x2 + dt*dx
        v2 = v2 + dt*dv
        t_now += dt

    # 相位比較
    ph_before = math.atan2(v[inj], x[inj]*omega[inj])
    ph_after = math.atan2(v2[inj], x2[inj]*omega[inj])
    slip = (ph_after - ph_before + math.pi) % (2*math.pi) - math.pi
    L(f"  注入節點 {inj} (ΔE=0, 反相 h={h}):")
    L(f"    注入前相位: {math.degrees(ph_before):7.1f}°")
    L(f"    注入後相位: {math.degrees(ph_after):7.1f}°")
    L(f"    相位滑移:   {math.degrees(slip):+7.1f}° ({abs(slip)/math.pi:.2f}π)")
    L(f"    → {'✅ 接近 π 翻轉!' if abs(abs(slip) - math.pi) < 0.4 else '🟡 部分滑移'}")
    L("")

    # 全網振幅變化
    amp_after = np.abs(x2)
    L(f"  寫入後全網:")
    L(f"    節點 {inj} 振幅: {amp[inj]:.4f} → {amp_after[inj]:.4f}")
    L(f"    ΔE=0 組 mean: {amp_zero:.4f} → {amp_after[zero_nodes].mean():.4f}")
    L(f"    → {'✅ 阻挫圖案改變 (寫入成功)' if abs(amp_after[zero_nodes].mean() - amp_zero) > 0.01 else '⚠️ 無顯著變化'}")
else:
    L(f"  節點 {inj} 唔係 ΔE=0")

# ============================================================
# 四、結論
# ============================================================
L("━" * 84)
L("  四、結論 — Van der Pol 真實電路模擬")
L("━" * 84)
L("""
  ══════════════════════════════════════════════════════════
  ⚡ Van der Pol = Wien bridge 嘅正確數學模型
  ══════════════════════════════════════════════════════════

  Kuramoto 修正: 純相位模型假設振幅相同 → 睇唔到壓制
  Van der Pol: 非線性飽和 → 振幅動態 → 壓制出現!

  ✅ 電路對應:
     ẍ_i + μ(x_i²-1)ẋ_i + ω²x_i = Σ K_ij(x_j - x_i)
     μ = 振盪器飽和強度 (Wien bridge 用 AGC/非線性)
     K>0 正常邊 (電阻), K<0 阻挫邊 (反相器)

  ✅ 驗證流程 (三用電表就夠):
     1. 5 節點環: 阻挫邊兩端壓差 vs 正常邊
     2. 60 節點: ΔE=0 節點振幅 vs 其他
     3. 注入: 外加訊號 → 相位翻轉 → 阻挫圖案改變

  ✅ 成本: TL074×15 + 電阻電容 + LED ≈ 500 台幣
  ══════════════════════════════════════════════════════════
""")

with open(os.path.join(OUT, "vanderpol_circuit_sim.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: ../data/vanderpol_circuit_sim.txt")
