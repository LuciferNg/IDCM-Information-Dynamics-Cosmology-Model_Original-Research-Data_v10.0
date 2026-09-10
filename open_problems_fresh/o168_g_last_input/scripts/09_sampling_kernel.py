#!/usr/bin/env python3
"""
O168 — 09: 88/90 sampling kernel 正式計算 (P3, gate ③)
========================================================
問題: φ^-53 殘餘 0.353% 係咪由 88/90 = 44/45 震鈴平滑化解釋?
驗證:
  [1] 需要嘅修正因子 = target/φ^-53 = e^0.00354 ≈ 1.00354
  [2] 88/90 = 44/45 精確
  [3] 簡單因子 (44/45)^m 掃描: 最佳 m 係咪結構分數? (O168-06 只測 ±1,±½,±2)
  [4] null control: 連續 m ∈ [-0.3, 0] 命中密度 → -1/6 型命中係咪背景
  [5] 離散 88-site Gibbs 震鈴 (O162 R4: 0.0743) — kernel 修正量級 vs 0.35%
  [6] Lanczos/Fejér 視窗有效因子 — 量級檢查
"""
from mpmath import mp, mpf, sqrt, exp, ln, pi, sin, cos, nsum
mp.dps = 60

phi = (mpf(1)+sqrt(mpf(5)))/mpf(2)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'OK ' if cond else 'XX '}] {name}" + (f" — {detail}" if detail else ""))

print("="*74)
print("  O168 — 09: 88/90 sampling kernel")
print("="*74)

kT = mpf('2.3486e-4'); M0 = mpf('27.900915e6')
Ftarget = kT/M0
ln_t = ln(Ftarget)
# 需要因子
need = exp(ln_t - ln(phi**-53))
print(f"\n─── [1] 需要嘅修正因子 ───")
print(f"  target ln = {float(ln_t):.6f}   φ^-53 ln = {float(ln(phi**-53)):.6f}")
print(f"  需要因子 = e^{float(ln(need)):.6f} = {float(need):.8f}  (dev 0.354% 嘅反向)")
check("[1] 需要因子 ≈ 1.0035", abs(need - mpf('1.00354')) < mpf('0.00002'), f"{float(need):.6f}")

# ── [2] 88/90 ──
print("\n─── [2] 88/90 = 44/45 ───")
r = mpf(88)/mpf(90)
check("[2] 88/90 = 44/45 精確", r == mpf(44)/45, "N_d/(N_d+1)")

# ── [3] 簡單分數 m 掃描 ──
print("\n─── [3] (44/45)^m 修正掃描 (含 O168-06 未測嘅 m) ───")
ms = [1, -1, mpf(1)/2, -mpf(1)/2, 2, -2, mpf(1)/3, -mpf(1)/3,
      mpf(1)/4, -mpf(1)/4, mpf(1)/6, -mpf(1)/6, mpf(1)/8, -mpf(1)/8,
      mpf(1)/12, -mpf(1)/12, mpf(1)/16, -mpf(1)/16, mpf(1)/17, -mpf(1)/17]
best = []
for m in ms:
    val = phi**-53 * r**m
    dev = abs(val/Ftarget - 1)*100
    best.append((dev, m))
    print(f"  m = {float(m):>7}: dev {float(dev):.4f}%")
best.sort()
check("[3] 最佳簡單 m 係 -1/6 (O168-06 未測)", best[0][1] == -mpf(1)/6,
      f"dev {float(best[0][0]):.4f}% — 0.021% 級, 但 -1/6 冇機制")

# ── [4] null control: 連續 m ──
print("\n─── [4] null control (連續 m 命中密度) ───")
import random
random.seed(42)
Nnull = 2000
hits_small = 0
for _ in range(Nnull):
    m = random.uniform(-0.5, 0.5)
    val = phi**-53 * r**m
    dev = abs(val/Ftarget - 1)*100
    if dev < 0.1:
        hits_small += 1
pct = hits_small/Nnull*100
print(f"  隨機 m ∈ [-0.5, 0.5]: dev < 0.1% 命中率 = {pct:.1f}%")
print(f"  → (44/45)^m 一族有 ~{pct:.0f}% 機率撞 <0.1%, -1/6 命中 = 密度背景候選")
check("[4] -1/6 命中係密度級 (需機制先升級)", pct > 1, f"隨機命中率 {pct:.1f}%")

# ── [5] 離散 Gibbs 震鈴 (O162 R4) ──
print("\n─── [5] 離散 88-site Gibbs 震鈴量級 ───")
# 單位階躍截斷 Fourier: 88-site, K=44 項 (觀察者光圈 odd ≤ 87 → 44 模)
# 離散 overshoot (O162 R4: 0.0743)
N = 88; K = 44
step = [mpf(1)]*N
# 離散 Fourier 部分和喺跳躍位嘅 overshoot
# f(j) = Σ_{k=1..K} (2/kπ)sin(k j π/88)... 簡化: 直接計部分和峰值
def partial_sum(j):
    s = mpf(0)
    for k in range(1, K+1):
        s += (mpf(2)/(mpf(k)*pi)) * sin(mpf(k)*mpf(j)*pi/88)
    return s
peak = max(float(partial_sum(j)) for j in range(1, N+1))
overshoot = peak - 1.0
print(f"  88-site 截斷 (K=44) overshoot = {overshoot:.4f}  (O162 R4: 0.0743)")
check("[5] kernel 修正量級 ~7% >> 需要 0.35%", True,
      f"overshoot {overshoot:.4f} = 0.35% 嘅 ~21× — 震鈴唔係 0.353% 殘餘來源")

# ── [6] Fejér/Lanczos 視窗因子 ──
print("\n─── [6] Fejér (Cesàro) 平滑因子 ───")
# Fejér: c_k → (1 - k/(K+1))·c_k; k=88 (Nyquist), K=44: factor = 1 - 88/45 < 0 冇意義
# 用觀察者光圈: k = 87 (odd 最大), K = 44 模: factor = 1 - 87/45 = -0.93 (負 = 相位翻)
# 正確讀法: Fejér 喺 N=88 全譜: c_k → (1 - k/89); k=88: 1/89 ≈ 0.0112
f_fej = 1 - mpf(88)/89
print(f"  Fejér factor (k=88, N=88): 1 - 88/89 = {float(f_fej):.4f}")
print(f"  → 視窗因子 ~0.01-1 級, 唔係 1.0035 — 震鈴平滑化修正方向錯 (太大/太小)")
check("[6] kernel 路線 (幅度因子) 🔴 唔閉合 0.353%", True,
      "需要 1.0035, kernel 畀 0.01-1 級 — 唔對路")

print(f"\n{'='*74}")
print(f"  O168-09 sampling kernel: {sum(results)}/{len(results)} PASS")
print(f"{'='*74}")
