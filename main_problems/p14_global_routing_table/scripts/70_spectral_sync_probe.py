#!/usr/bin/env python3
"""
P14 新方向探針 v2 — 底層譜駐波自發同步 (2026-10-21)
==================================================
Corrected: chain = ring LOCAL coupling (K_Chain 結構), rotating frame, sane dt.

三個命題:
  P1: identical-frequency ring (無阻挫) — 弱耦合 K=1/16 會唔會自發鎖相?
      (定義: 序參數 r = |mean e^{iθ}| 穩定 > 0.9 = 全域同步)
  P2: 加 32 條 β=π 阻挫邊 — 鎖定到固定相位差 pattern (駐波測度)?
  P3: 收斂時間量級 vs 光橫越 R_ring
"""
import numpy as np

N = 88
K = 1/16.0
dt = 0.002
steps = 100000          # 200 時間單位
omega = 0.0             # rotating frame (identical freq 歸零)

def sim(beta_edges, seed=42, K=K, dt=dt, steps=steps):
    """ring local Kuramoto: dθ_i = ω + K Σ_{j∈{i±1}} sin(θ_j−θ_i−β_ij)"""
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, N)
    r_traj = []
    for s in range(steps):
        dtheta = np.zeros(N)
        for i in range(N):
            jr = (i+1) % N
            jl = (i-1) % N
            dtheta[i] = (K*np.sin(theta[jr]-theta[i]-beta_edges[i, jr])
                         + K*np.sin(theta[jl]-theta[i]-beta_edges[i, jl]))
        theta = theta + dt*dtheta
        if s % 500 == 0:
            r_traj.append(np.abs(np.mean(np.exp(1j*theta))))
    return theta, np.array(r_traj)

def report(name, theta, r_traj):
    print(f"\n[{name}]")
    print(f"  首 r: {r_traj[0]:.4f}   尾 r: {r_traj[-1]:.4f}")
    # 駐波測度: 相鄰相位差
    diff = np.diff(np.concatenate([theta, theta[:1]]))
    diff = np.mod(diff + np.pi, 2*np.pi) - np.pi
    f0 = np.mean(np.abs(diff) < 0.05)
    fpi = np.mean(np.abs(np.abs(diff) - np.pi) < 0.05)
    print(f"  相鄰差≈0: {f0:.3f}  差≈π: {fpi:.3f}  (駐波 = 差固定 0/π)")
    if r_traj[-1] > 0.9:
        print(f"  🟢 全域同步鎖相 (r→1)")
    elif (f0 + fpi) > 0.7:
        print(f"  🟢 駐波 pattern 鎖定 (相位差固定 0/π)")
    else:
        print(f"  🟡 混合/未鎖定 — 需要非平衡驅動?")

print("=" * 70)
print("  P14 新方向探針 v2 — ring-local Kuramoto on 88-chain (K=κ=1/16)")
print("=" * 70)

# P1: 無阻挫 ring
beta0 = np.zeros((N, N))
th1, r1 = sim(beta0, seed=42)
report("P1 無阻挫 ring", th1, r1)

# P2: 32 條 β=π 均勻分佈
beta2 = np.zeros((N, N))
edges = [(i, (i+1) % N) for i in range(N)]
for e in range(32):
    i, j = edges[e * 88 // 32]
    beta2[i, j] = np.pi
    beta2[j, i] = np.pi
th2, r2 = sim(beta2, seed=7)
report("P2 32阻挫邊 ring", th2, r2)

# P2b: 強耦合對照 (K=0.8, docs/17 GRT-40 閾值)
th2b, r2b = sim(beta2, seed=7, K=0.8)
report("P2b 強耦合 K=0.8 對照", th2b, r2b)

# P3: 收斂時間
print("\n[P3] 收斂時間量級:")
for label, r in [("無阻挫", r1), ("阻挫 K=κ", r2), ("阻挫 K=0.8", r2b)]:
    it = next((i for i, v in enumerate(r) if v > 0.5), None)
    if it is None:
        print(f"  {label}: r>0.5 未出現 (記錄間距 1.0)")
    else:
        print(f"  {label}: r>0.5 首次 @ {it*500*dt:.1f} 時間單位 (記錄間距 1.0)")
R_ring_yr = 4129.94 * 3.26e6
print(f"  參考: 光穿越 2πR_ring = {2*np.pi*R_ring_yr/1e9:.3e} Gyr (時間單位未定標)")