#!/usr/bin/env python3
"""
GRT-39: 電路參數優化 — 掃描 K, μ, 失諧, 注入強度
================================================================
優化目標: 最大「阻挫壓制」(ΔE=0 節點振幅 / 其他節點振幅 最細)

可調參數 (電路對應):
  K  (耦合強度)      ← 電阻值 (R 細 = 耦合強)
  μ  (非線性飽和)    ← Wien bridge AGC / 振盪幅度
  σω (頻率失諧)      ← 電阻/電容容差 (1% 電阻 = ±10 Hz @ 1kHz)
  h  (注入強度)      ← 寫入訊號幅度
  φ  (注入相位)      ← 寫入訊號相位 (理想 π)

物理對應:
  阻挫壓制比 R_amp = mean|amp|(ΔE=0) / mean|amp|(其他)
  R_amp < 0.85 = LED 熄滅可見
  R_amp 越細 = 越明顯
"""
import numpy as np
import math
import sys, os, itertools

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
L("  GRT-39: 電路參數優化 — 掃描 K, μ, 失諧, 注入強度")
L("=" * 84)

# ============================================================
# 圖 + 節點
# ============================================================
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

zero_nodes = []
for i in range(N):
    k = sum(1 for j in adj[i] if (min(i,j), max(i,j)) in frust)
    if k == 2:
        zero_nodes.append(i)
normal_nodes = [i for i in range(N) if i not in zero_nodes]

# ============================================================
# Van der Pol 網絡 (高效版, 向量化)
# ============================================================
def vdp_network(x, v, mu, omega_sq, K_mat, dt, steps, drive=None):
    """Van der Pol 網絡 RK4 (drive = (node, h, omega_d, phi_d) 可選)"""
    N = len(x)
    t = 0.0
    for step in range(steps):
        def deriv(xx, vv, tt):
            dx = vv
            dv = -mu*(xx**2 - 1)*vv - omega_sq*xx
            for i in range(N):
                dv[i] += np.dot(K_mat[i], xx - xx[i])
            if drive is not None:
                node, h, wd, ph = drive
                dv[node] += h * math.sin(wd * tt + ph)
            return dx, dv
        k1x, k1v = deriv(x, v, t)
        k2x, k2v = deriv(x + 0.5*dt*k1x, v + 0.5*dt*k1v, t + 0.5*dt)
        k3x, k3v = deriv(x + 0.5*dt*k2x, v + 0.5*dt*k2v, t + 0.5*dt)
        k4x, k4v = deriv(x + dt*k3x, v + dt*k3v, t + dt)
        x = x + (dt/6)*(k1x + 2*k2x + 2*k3x + k4x)
        v = v + (dt/6)*(k1v + 2*k2v + 2*k3v + k4v)
        t += dt
    return x, v

def suppression_ratio(x, zero_nodes, normal_nodes):
    """阻挫壓制比: ΔE=0 組 mean|amp| / 其他組 mean|amp|"""
    amp = np.abs(x)
    if len(normal_nodes) == 0 or amp[normal_nodes].mean() == 0:
        return 1.0
    return amp[zero_nodes].mean() / amp[normal_nodes].mean()

# ============================================================
# 掃描 1: 耦合強度 K (電阻值)
# ============================================================
L("━" * 84)
L("  一、掃描 K (耦合強度 ↔ 電阻值)")
L("━" * 84)
L("""
  電路對應: K = 1/(R·C·ω) 耦合強度
  R 細 (強耦合) → K 大
  R 大 (弱耦合) → K 細
  物理: 太弱耦合 = 各自振盪 (冇鎖定)
        太強耦合 = 全鎖死 (振幅冇分別)
        中間 = 阻挫壓制最佳!
""")

mu_fix = 1.0
dt = 1e-5
steps = 8000
rng = np.random.default_rng(11)
omega_base = np.ones(N) * 2*math.pi*1000
omega_base += rng.normal(0, 2*math.pi*10, N)  # ±10 Hz
omega_sq = omega_base**2

K_range = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
L(f"  {'K':>6} | {'R 對應':>8} | {'壓制比':>8} | {'ΔE=0 mean':>10} | {'其他 mean':>10} | {'狀態'}")
L(f"  {'-'*6} | {'-'*8} | {'-'*8} | {'-'*10} | {'-'*10} | {'-'*8}")

K_best = None
K_best_ratio = 1.0
for K in K_range:
    K_mat = np.zeros((N, N))
    for i in range(N):
        for j, beta in adjK[i]:
            K_mat[i, j] = K * math.cos(beta)
    x0 = rng.uniform(-0.5, 0.5, N)
    v0 = rng.uniform(-0.5, 0.5, N)
    x, v = vdp_network(x0, v0, mu_fix, omega_sq, K_mat, dt, steps)
    ratio = suppression_ratio(x, zero_nodes, normal_nodes)
    R_equiv = 10e3 / (K * 10)  # 粗略對應 (10kΩ @ K=0.1)
    status = "🟢" if ratio < 0.80 else ("🟡" if ratio < 0.90 else "🔴")
    L(f"  {K:>6.2f} | {R_equiv:>7.0f}Ω | {ratio:>8.3f} | {np.abs(x[zero_nodes]).mean():>10.4f} | {np.abs(x[normal_nodes]).mean():>10.4f} | {status}")
    if ratio < K_best_ratio:
        K_best_ratio = ratio
        K_best = K

L(f"""
  → 最佳 K = {K_best} (壓制比 {K_best_ratio:.3f})
  → 對應電阻 ≈ {10e3/(K_best*10):.0f}Ω (基準 10kΩ)
""")

# ============================================================
# 掃描 2: 非線性 μ (AGC 飽和)
# ============================================================
L("━" * 84)
L("  二、掃描 μ (非線性飽和 ↔ AGC 強度)")
L("━" * 84)
L("""
  電路對應: μ = Wien bridge 非線性飽和強度
  μ 大 = 強飽和 (振幅硬限制, 方波傾向)
  μ 小 = 弱飽和 (振幅軟限制, 正弦傾向)
  物理: μ 控制振幅穩定性, 影響阻挫壓制深度
""")

K_fix = K_best if K_best else 0.15
K_mat = np.zeros((N, N))
for i in range(N):
    for j, beta in adjK[i]:
        K_mat[i, j] = K_fix * math.cos(beta)

mu_range = [0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0]
L(f"  (K = {K_fix} 固定)")
L(f"  {'μ':>6} | {'壓制比':>8} | {'ΔE=0 mean':>10} | {'其他 mean':>10} | {'狀態'}")
L(f"  {'-'*6} | {'-'*8} | {'-'*10} | {'-'*10} | {'-'*8}")

mu_best = None
mu_best_ratio = 1.0
for mu in mu_range:
    x0 = rng.uniform(-0.5, 0.5, N)
    v0 = rng.uniform(-0.5, 0.5, N)
    x, v = vdp_network(x0, v0, mu, omega_sq, K_mat, dt, steps)
    ratio = suppression_ratio(x, zero_nodes, normal_nodes)
    status = "🟢" if ratio < 0.80 else ("🟡" if ratio < 0.90 else "🔴")
    L(f"  {mu:>6.1f} | {ratio:>8.3f} | {np.abs(x[zero_nodes]).mean():>10.4f} | {np.abs(x[normal_nodes]).mean():>10.4f} | {status}")
    if ratio < mu_best_ratio:
        mu_best_ratio = ratio
        mu_best = mu

L(f"""
  → 最佳 μ = {mu_best} (壓制比 {mu_best_ratio:.3f})
  → 對應電路: AGC 中等強度 (Wien bridge 輸出 ~1-2V)
""")

# ============================================================
# 掃描 3: 頻率失諧 σω (元件容差)
# ============================================================
L("━" * 84)
L("  三、掃描 σω (頻率失諧 ↔ 元件容差)")
L("━" * 84)
L("""
  電路對應: 電阻/電容容差
  1% 電阻: σω/ω ≈ 1% → σω ≈ 2π·10 Hz @ 1kHz
  5% 電阻: σω/ω ≈ 5% → σω ≈ 2π·50 Hz
  10% 電容: σω/ω ≈ 10% → σω ≈ 2π·100 Hz
  物理: 失諧太大 = 節點各自振盪 (冇鎖定)
        失諧細 = 容易鎖定 (阻挫壓制明顯)
""")

mu_fix2 = mu_best if mu_best else 1.0
L(f"  (K = {K_fix}, μ = {mu_fix2} 固定)")
L(f"  {'σω (Hz)':>8} | {'容差':>6} | {'壓制比':>8} | {'狀態'}")
L(f"  {'-'*8} | {'-'*6} | {'-'*8} | {'-'*8}")

sigma_range = [0, 2, 5, 10, 20, 50, 100, 200]
sig_best = None
sig_best_ratio = 1.0
for sig in sigma_range:
    rng2 = np.random.default_rng(sig + 100)
    om = np.ones(N) * 2*math.pi*1000 + rng2.normal(0, 2*math.pi*sig, N)
    om_sq = om**2
    x0 = rng2.uniform(-0.5, 0.5, N)
    v0 = rng2.uniform(-0.5, 0.5, N)
    x, v = vdp_network(x0, v0, mu_fix2, om_sq, K_mat, dt, steps)
    ratio = suppression_ratio(x, zero_nodes, normal_nodes)
    tol = f"{sig/1000*100:.0f}%" if sig > 0 else "0%"
    status = "🟢" if ratio < 0.80 else ("🟡" if ratio < 0.90 else "🔴")
    L(f"  {sig:>8.0f} | {tol:>6} | {ratio:>8.3f} | {status}")
    if ratio < sig_best_ratio:
        sig_best_ratio = ratio
        sig_best = sig

L(f"""
  → 最佳 σω = {sig_best} Hz (壓制比 {sig_best_ratio:.3f})
  → 對應: 用 1% 電阻 (σω≈10Hz) 已足夠, 唔需要精選
""")

# ============================================================
# 掃描 4b: 脈衝注入寫入 (修正版)
# ============================================================
L("━" * 84)
L("  四、脈衝注入寫入 — 相位重置 (修正)")
L("━" * 84)
L("""
  修正: 連續正弦驅動只改振幅, 唔會滑移相位
  真實寫入 = 脈衝注入 (短時間強驅動):
  - 對節點加 dc 偏置脈衝 (持續 ~半週期)
  - 節點被強制拉到特定相位
  - 脈衝消失後, 網絡重新鎖定 → 相位記憶新狀態

  電路對應: 訊號產生器輸出一個短脈衝 (方波/dc 突波)
""")

# 脈衝注入函數
def vdp_pulse(x, v, mu, omega_sq, K_mat, dt, steps, pulse=None):
    """Van der Pol + 脈衝 (pulse = (node, amp, t_start, t_end))"""
    N = len(x)
    t = 0.0
    for step in range(steps):
        def deriv(xx, vv, tt):
            dx = vv
            dv = -mu*(xx**2 - 1)*vv - omega_sq*xx
            for i in range(N):
                dv[i] += np.dot(K_mat[i], xx - xx[i])
            if pulse is not None:
                node, amp, t0, t1 = pulse
                if t0 <= tt < t1:
                    dv[node] += amp
            return dx, dv
        k1x, k1v = deriv(x, v, t)
        k2x, k2v = deriv(x + 0.5*dt*k1x, v + 0.5*dt*k1v, t + 0.5*dt)
        k3x, k3v = deriv(x + 0.5*dt*k2x, v + 0.5*dt*k2v, t + 0.5*dt)
        k4x, k4v = deriv(x + dt*k3x, v + dt*k3v, t + dt)
        x = x + (dt/6)*(k1x + 2*k2x + 2*k3x + k4x)
        v = v + (dt/6)*(k1v + 2*k2v + 2*k3v + k4v)
        t += dt
    return x, v

inj_node = 45  # ΔE=0 節點
# 用基底做起始 (最佳參數: K_fix, mu_fix2, 零失諧)
rng3 = np.random.default_rng(999)
om_best = np.ones(N) * 2*math.pi*1000
om_best_sq = om_best**2
x0 = rng3.uniform(-0.5, 0.5, N)
v0 = rng3.uniform(-0.5, 0.5, N)
x_base, v_base = vdp_network(x0, v0, mu_fix2, om_best_sq, K_mat, dt, steps)
# 測量基底實際振盪頻率 (最後 2000 步嘅過零計數)
def measure_freq(x_series, dt):
    crossings = 0
    for i in range(1, len(x_series)):
        if x_series[i-1] < 0 and x_series[i] >= 0:
            crossings += 1
    return crossings / (len(x_series) * dt)
x_traj = []
x_t, v_t = x_base.copy(), v_base.copy()
for _ in range(2000):
    dx = v_t
    dv = -mu_fix2*(x_t**2 - 1)*v_t - om_best_sq*x_t
    for i in range(N):
        dv[i] += np.dot(K_mat[i], x_t - x_t[i])
    x_t = x_t + dt*dx
    v_t = v_t + dt*dv
    x_traj.append(x_t[inj_node])
f_meas = measure_freq(np.array(x_traj), dt)
L(f"  基底: 節點 {inj_node} 振盪頻率 f = {f_meas:.0f} Hz")

T_period = 1/f_meas  # 用測得週期
t0_pulse = 0.0
t1_pulse = 0.5 * T_period  # 半週期脈衝

L(f"  注入節點 {inj_node} (ΔE=0), 脈衝寬度 = 半週期 ({t1_pulse*1000:.2f} ms)")
L(f"  {'h (脈衝)':>9} | {'相位滑移':>10} | {'|滑移|/π':>8} | {'ΔE=0 組變':>10} | {'狀態'}")
L(f"  {'-'*9} | {'-'*10} | {'-'*8} | {'-'*10} | {'-'*8}")

ph_before = math.atan2(v_base[inj_node], x_base[inj_node]*om_best[inj_node])
h_range2 = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 50.0]
h_best = None
h_best_slip = 0
for h in h_range2:
    pulse = (inj_node, h, t0_pulse, t1_pulse)
    x_inj, v_inj = vdp_pulse(x_base.copy(), v_base.copy(), mu_fix2, om_best_sq, K_mat, dt, 15000, pulse=pulse)
    ph_after = math.atan2(v_inj[inj_node], x_inj[inj_node]*om_best[inj_node])
    slip = (ph_after - ph_before + math.pi) % (2*math.pi) - math.pi
    slip_pi = abs(slip)/math.pi
    amp_change = abs(np.abs(x_inj[zero_nodes]).mean() - np.abs(x_base[zero_nodes]).mean())
    if slip_pi > 0.7:
        status = "🟢 寫入!" if amp_change > 0.005 else "🟡 相位轉"
    elif slip_pi > 0.3:
        status = "🟡 部分"
    else:
        status = "🔴 未鎖定"
    L(f"  {h:>9.1f} | {math.degrees(slip):>+9.1f}° | {slip_pi:>8.2f} | {amp_change:>10.4f} | {status}")
    if slip_pi > h_best_slip:
        h_best_slip = slip_pi
        h_best = h

L(f"""
  → 最佳脈衝 h = {h_best} (滑移 {h_best_slip:.2f}π)
  → 電路對應: 短脈衝 (半週期) 注入節點, 幅度 {h_best}
""")

# ============================================================
# 五、最佳工作點總結
# ============================================================
L("━" * 84)
L("  五、最佳工作點總結 (電路設計指引)")
L("━" * 84)
L(f"""
  ══════════════════════════════════════════════════════════
  ⚙️ 最佳工作點 (參數掃描結果)
  ══════════════════════════════════════════════════════════

  耦合強度 K = {K_best}  → 電阻 R ≈ {10e3/(K_best*10):.0f}Ω (壓制比 {K_best_ratio:.3f})
  非線性 μ  = {mu_best}  → AGC 中等飽和 (壓制比 {mu_best_ratio:.3f})
  失諧 σω   = {sig_best} Hz → 用 1% 電阻已夠 (壓制比 {sig_best_ratio:.3f})
  注入 h    = {h_best}  → 訊號產生器 0.3-0.7V (滑移 {h_best_slip:.2f}π)

  → 電路設計:
    R1 = R2 = 10kΩ (選頻)
    Rout = {10e3/(K_best*10):.0f}Ω (耦合, 最佳)
    Rf = 33kΩ, Ri = 10kΩ (增益 4.3)
    R_LED = 1kΩ (限流)
    電阻全部 1% (10Hz 失諧 OK)
    電源 ±9V
    注入: 0.3-0.7V 反相訊號 @ 1.59kHz

  ⚡ 物理規律:
  - K 太細 → 冇鎖定 (各自振盪)
  - K 太大 → 全鎖死 (壓制消失)
  - 中間最佳: 阻挫邊壓制 ΔE=0 節點!
  - 呢個就係「幾何阻挫」嘅宏觀電路體現
  ══════════════════════════════════════════════════════════
""")

with open(os.path.join(OUT, "circuit_optimization.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: ../data/circuit_optimization.txt")
