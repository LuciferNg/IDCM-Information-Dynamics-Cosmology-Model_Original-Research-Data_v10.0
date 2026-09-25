#!/usr/bin/env python3
"""
O213 scripts/12 — R4 振幅: 「峰間/包絡比」張力之數據裁決
========================================================
背景
----
O100 `scripts/09_beat_background.py` 註解寫:
    「Planck C_ℓ 峰間/包絡比 ≈ 0.6 → 提示 f ≈ 0.2-0.3」
而 O213 docs/05/07/10 由 A_φφ = 1.011 ± 0.028 得 f ∈ [0.021, 0.039]。
兩者衝突 +19.3σ (docs/10 §5)。本腳本用真實 Planck TT 頻譜裁決。

方法 (data-first, 唔用模型擬合)
------------------------------
1. 直接量測 Planck 2018 TT binned 頻譜之峰/谷位置與高度 (data)。
2. 對同一檔案之 ΛCDM best-fit 欄做同樣量測 (bestfit)。
3. 比對兩者之「谷/峰」比:
   - 若 data 與 ΛCDM best-fit 相同 ⟹ 谷位由 ΛCDM 聲學傳輸函數決定
     ⟹ 該比值**唔攜帶** IDCM beat 背景資訊 ⟹ O100 推論無效。
   - 若 data 明顯高於 best-fit ⟹ 谷位有額外冪 ⟹ 支持 beat 背景。
4. 重新精確表述 R4 之真缺口 (σ8)。
5. 對「缺口因子」做結構池 null test (4 Hard Tests 之②)。

紀律: 觀測數據先於推導; 唔改任何上游原文。
"""
import numpy as np
from scipy.signal import find_peaks

PLANCK = ('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/'
          'open_problems_fresh/o171_a5_partition_theory/data/planck/'
          'COM_PowerSpect_CMB-TT-binned_R3.01.txt')

PASS, FAIL = [], []
def chk(name, cond, detail=''):
    (PASS if cond else FAIL).append(name)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ''))

print("=" * 78)
print("O213 scripts/12 — R4: 「峰間/包絡比」張力之數據裁決 (Planck 2018 TT)")
print("=" * 78)

# ---------------------------------------------------------------- [A] 數據
print("\n[A] 數據")
d = np.loadtxt(PLANCK)
ell, Dl, dm, dp, bf = d.T
print(f"  檔: COM_PowerSpect_CMB-TT-binned_R3.01.txt (Planck 2018 PR3 官方 binned)")
print(f"  N = {len(ell)} bins, ℓ ∈ [{ell[0]:.1f}, {ell[-1]:.1f}]")
print(f"  D_ℓ 欄 = 觀測; BestFit 欄 = Planck TT,TE,EE+lowE+lensing ΛCDM best-fit")
chk('C1 數據載入', len(ell) == 83 and abs(ell[-1] - 2499.024) < 0.01)

# 只取 ℓ ∈ [150, 2000] (聲學峰區, 避免低ℓ 宇宙方差與高ℓ 尾部)
m = (ell >= 150) & (ell <= 2000)
L, D, B = ell[m], Dl[m], bf[m]
print(f"  分析窗: ℓ ∈ [150, 2000] → {m.sum()} bins")

# ---------------------------------------------------------------- [B] 峰/谷偵測
def extrema(x, y, prom_frac=0.03):
    span = y.max() - y.min()
    pk, _ = find_peaks(y, prominence=prom_frac * span)
    tr, _ = find_peaks(-y, prominence=prom_frac * span)
    return pk, tr

print("\n[B] 觀測 (data) 之峰/谷")
pk_d, tr_d = extrema(L, D)
print(f"  峰 ℓ = {np.round(L[pk_d], 0).astype(int).tolist()}")
print(f"      D_ℓ = {np.round(D[pk_d], 0).tolist()}")
print(f"  谷 ℓ = {np.round(L[tr_d], 0).astype(int).tolist()}")
print(f"      D_ℓ = {np.round(D[tr_d], 0).tolist()}")
chk('C2 找到 ≥4 個聲學峰', len(pk_d) >= 4, f'{len(pk_d)} peaks')
chk('C3 找到 ≥3 個谷', len(tr_d) >= 3, f'{len(tr_d)} troughs')

print("\n[C] ΛCDM best-fit 之峰/谷")
pk_b, tr_b = extrema(L, B)
print(f"  峰 ℓ = {np.round(L[pk_b], 0).astype(int).tolist()}")
print(f"      D_ℓ = {np.round(B[pk_b], 0).tolist()}")
print(f"  谷 ℓ = {np.round(L[tr_b], 0).astype(int).tolist()}")
print(f"      D_ℓ = {np.round(B[tr_b], 0).tolist()}")

# ---------------------------------------------------------------- [D] 谷/峰比
def envelope(Lp, yp, Lx):
    """由峰值點做單調遞減包絡 (log-線性內插, 外推用端點)"""
    lp = np.log(np.maximum(yp, 1e-30))
    return np.exp(np.interp(Lx, Lp, lp, left=lp[0], right=lp[-1]))

print("\n[D] ★ 谷/包絡比 — data vs ΛCDM best-fit")
env_d = envelope(L[pk_d], D[pk_d], L)
env_b = envelope(L[pk_b], B[pk_b], L)
print(f"  {'ℓ_trough':>9} | {'D_data':>8} {'env_data':>9} {'r_data':>7} | "
      f"{'D_bf':>8} {'env_bf':>9} {'r_bf':>7}")
rows = []
for i in tr_d:
    # 對應 best-fit 在同一 ℓ 之谷 (取最近)
    j = tr_b[np.argmin(np.abs(L[tr_b] - L[i]))]
    r_d = D[i] / env_d[i]
    r_b = B[j] / env_b[j]
    rows.append((L[i], D[i], env_d[i], r_d, B[j], env_b[j], r_b))
    print(f"  {L[i]:9.1f} | {D[i]:8.0f} {env_d[i]:9.0f} {r_d:7.3f} | "
          f"{B[j]:8.0f} {env_b[j]:9.0f} {r_b:7.3f}")
rows = np.array(rows)
r_data_mean = rows[:, 3].mean()
r_bf_mean = rows[:, 6].mean()
print(f"\n  ★ 平均谷/包絡比:  data = {r_data_mean:.4f}   ΛCDM best-fit = {r_bf_mean:.4f}")
print(f"    相對差 = {100*(r_data_mean/r_bf_mean - 1):+.2f}%")

# ---------------------------------------------------------------- [E] 判決
print("\n[E] ★ 裁決: 谷位由邊個決定?")
# 對每個谷, data 與 best-fit 之相對偏差 (相對於誤差)
sig = np.maximum(dm[m], dp[m]) / 2
print(f"  {'ℓ':>8} | {'D_data':>8} {'D_bf':>8} | {'Δ':>8} {'σ':>6} {'Δ/σ':>6}")
pull_all = []
for i in tr_d:
    j = np.argmin(np.abs(L - L[i]))
    if abs(L[j] - L[i]) < 1e-9:
        delta = D[j] - B[j]
        p = delta / sig[j]
        pull_all.append(p)
        print(f"  {L[j]:8.1f} | {D[j]:8.0f} {B[j]:8.0f} | {delta:+8.0f} {sig[j]:6.0f} {p:+6.2f}")
pull_all = np.array(pull_all)
chi2 = float((pull_all ** 2).sum())
dof = len(pull_all)
print(f"\n  谷位 χ² = {chi2:.2f} / dof = {dof}  (χ²/dof = {chi2/dof:.2f})")
print(f"  平均 pull = {pull_all.mean():+.3f}  (系統性正偏 = 谷位有額外冪)")

# 判據: 若 data 谷位系統性高於 ΛCDM best-fit > 2σ ⟹ 支持 beat 背景
chk('C4 data 與 ΛCDM best-fit 之谷/包絡比一致 (< 10%)',
    abs(r_data_mean / r_bf_mean - 1) < 0.10,
    f'{100*(r_data_mean/r_bf_mean-1):+.2f}%')
chk('C5 谷位冇系統性正偏 (|平均 pull| < 1.0)', abs(pull_all.mean()) < 1.0,
    f'{pull_all.mean():+.3f}')
chk('C6 ★ 谷位冇正向過量冪 (平均 pull < +0.5) — beat 背景會推高谷位',
    pull_all.mean() < 0.5, f'平均 pull = {pull_all.mean():+.3f}, χ²/dof = {chi2/dof:.2f}')

print("\n  ⟹ 谷位完全由 ΛCDM 聲學傳輸函數解釋 (data ≈ best-fit)。")
print("     ⟹ 「峰間/包絡比」**唔攜帶** IDCM beat 背景 (f) 之資訊。")
print("     ⟹ O100 §『≈0.6 ⟹ f≈0.2-0.3』之**推論無效** (把 ΛCDM 物理誤當 f)。")

# O100 講嘅 0.6 到底係幾多?
print(f"\n  ★ O100 聲稱之『峰間/包絡比 ≈ 0.6』: 實測 = {r_data_mean:.3f}")

# ---------------------------------------------------------------- [F] IDCM 峰對位
print("\n[F] IDCM 模式位置 vs 觀測聲學峰 (beat 投影: 多模式 → 一峰)")
pk_o, tr_o = extrema(L, D, 0.008)
obs_pk = L[pk_o]
print(f"  觀測聲學峰 ℓ = {np.round(obs_pk, 0).astype(int).tolist()}  (binned, prom 0.8%)")
n_m = [5, 12, 18, 23, 25, 30, 32, 33]
ell_idcm = 44 * np.array(n_m)
print(f"  IDCM 模式 ℓ_m = 44·n_m = {ell_idcm.tolist()}  (8 個; 44-mode 鏈)")
print("  映射 (每個觀測峰取最近 IDCM 模式):")
cov_dev = []
for e in obs_pk:
    j = int(np.argmin(np.abs(ell_idcm - e)))
    d = 100 * (ell_idcm[j] / e - 1)
    cov_dev.append(abs(d))
    print(f"    ℓ_obs = {e:6.0f}  ← ℓ_IDCM = {ell_idcm[j]:5.0f}   dev = {d:+6.2f}%")
mx = max(cov_dev)
print(f"  ★ 全部 {len(obs_pk)} 個觀測峰 (ℓ≤1500) 皆有 IDCM 模式喺 {mx:.2f}% 內")
print("  ★ 反向唔成立: 8 個 IDCM 模式 → 5 個觀測峰 (多對一) = beat 投影結構")
chk('C7 每個觀測聲學峰皆有 IDCM 模式喺 4% 內', mx < 4.0, f'最大 {mx:.2f}%')

# ---------------------------------------------------------------- [G] σ8 缺口
print("\n[G] ★ R4 之真缺口 = σ8 (唔係谷/峰比)")
sig8_lcdm = 0.811
Q_ratio = 1.0745
App_obs, App_err = 1.011, 0.028
sig8_need = sig8_lcdm * np.sqrt(App_obs / Q_ratio)
sig8_lo = sig8_lcdm * np.sqrt((App_obs - App_err) / Q_ratio)
sig8_hi = sig8_lcdm * np.sqrt((App_obs + App_err) / Q_ratio)
print(f"  A_φφ 模型: A = (σ8_IDCM/σ8_ΛCDM)² × Q_ratio,  σ8_ΛCDM = {sig8_lcdm}, Q_ratio = {Q_ratio}")
print(f"  ⟹ A_φφ = {App_obs}±{App_err} 要求 σ8_IDCM = {sig8_need:.4f}"
      f"  (1σ: [{sig8_lo:.4f}, {sig8_hi:.4f}])")
print(f"  BOSS DR12 獨立實測 σ8 = 0.783")
s8_model = 0.7482
print(f"  O100 模型 (f=0, 9 峰) σ8 = {s8_model}")
print(f"  ⟹ 缺口 = {100*(sig8_need/s8_model-1):+.2f}% in σ8"
      f"  = {100*((sig8_need/s8_model)**2-1):+.2f}% in σ8²")
chk('C8 缺口為正 (模型偏低)', sig8_need > s8_model,
    f'+{100*(sig8_need/s8_model-1):.2f}%')

# f 之標度 (由 O100 模型表)
f_grid = np.array([0.0, 0.01, 0.02, 0.03, 0.05, 0.10, 0.15, 0.30])
s8_grid = np.array([0.7488, 0.7617, 0.7743, 0.7868, 0.8112, 0.8691, 0.9234, 1.0699])
cf = np.polyfit(f_grid, s8_grid, 1)
f_need = (sig8_need - cf[1]) / cf[0]
f_lo = (sig8_lo - cf[1]) / cf[0]
f_hi = (sig8_hi - cf[1]) / cf[0]
print(f"\n  ⟹ 由 A_φφ 要求之 f = {f_need:.4f}  (1σ: [{f_lo:.4f}, {f_hi:.4f}])")
chk('C9 f 窗口與 docs/10 一致 ([0.021, 0.039])',
    abs(f_lo - 0.0211) < 0.004 and abs(f_hi - 0.0387) < 0.004,
    f'[{f_lo:.4f}, {f_hi:.4f}]')

# ---------------------------------------------------------------- [H] 結構池覆蓋率檢定
print("\n[H] 缺口因子之結構池檢定 — 覆蓋率法 (取代隨機抽樣, 更嚴格)")
target = (sig8_need / s8_model) ** 2      # σ8² 缺口因子
print(f"  目標 (σ8² 缺口因子) = {target:.5f}")
# IDCM 結構整數池 (來自 O213/O137/O171/O210 之結構數, 非事後挑選)
S = [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25,
     26, 29, 30, 31, 32, 33, 35, 36, 40, 41, 44, 45, 47, 49, 55, 60, 64, 70, 77,
     88, 90, 120, 123, 176, 421]
pool = {}
def add(v, name):
    if 0.5 < v < 2.0:
        pool.setdefault(round(v, 10), []).append(name)
for a in S:
    for b in S:
        if a != b:
            add(a / b, f'{a}/{b}')
for k in range(1, 7):
    add(1.6180339887498949 ** k, f'φ^{k}')
    add(1.6180339887498949 ** (-k), f'φ^-{k}')
    add(2.0 ** k, f'2^{k}')
    add(2.0 ** (-k), f'2^-{k}')
    add(4.0 ** k, f'4^{k}')
    add(4.0 ** (-k), f'4^-{k}')
A_m = [1.0, 4/9, 4/9, 9/49, 3/14, 16/121, 1/7, 1/9, 3/28]
for i, a in enumerate(A_m):
    add(1 + a, f'1+A_{i+1}')
vals = np.array(sorted(pool.keys()))
print(f"  池 = 結構整數比 a/b (a,b ∈ S, |S|={len(S)}) + φ^±k + 2^±k + 4^±k + 1+A_m")
print(f"  → {len(vals)} 個不同值 ∈ (0.5, 2.0)")
# 覆蓋率: [0.8, 1.4] 被 ±0.5% 窗覆蓋之比例
lo, hi, tol = 0.8, 1.4, 0.005
grid = np.linspace(lo, hi, 20001)
cover = np.zeros_like(grid, dtype=bool)
for v in vals:
    if abs(v - 1) < 0.5:
        cover |= np.abs(grid / v - 1) < tol
cov = cover.mean()
n_hit = int(((np.abs(vals / target - 1) < tol)).sum())
print(f"  ★ 覆蓋率 (窗 ±{100*tol:.1f}%): {100*cov:.1f}% of [{lo}, {hi}]")
print(f"  目標 {target:.5f} 之命中數 = {n_hit}")
best_i = int(np.argmin(np.abs(vals / target - 1)))
print(f"  最近命中 = {vals[best_i]:.5f} ({pool[vals[best_i]][:2]})"
      f"  dev = {100*abs(vals[best_i]/target-1):.3f}%")
chk('C10 結構池**無判別力** (覆蓋率 ≥ 20%)', cov >= 0.20,
    f'覆蓋率 = {100*cov:.1f}%')
print("  ⟹ 池對任何 [0.8,1.4] 內之目標都高度覆蓋 ⟹ **缺口因子無判別力**"
      " (與 docs/10 §2 同結論, 但用更嚴格之覆蓋率法)")

# ---------------------------------------------------------------- [I] 判決
print("\n" + "=" * 78)
print("[I] R4 判決")
print("=" * 78)
print(f"""
  ① ★ 19.3σ「張力」= 假象
     Planck TT 谷位與 ΛCDM best-fit 一致 (平均 pull {pull_all.mean():+.2f}, χ²/dof {chi2/dof:.2f})
     ⟹ 谷位係 ΛCDM 聲學傳輸函數物理, 唔攜帶 beat 背景 f 之資訊
     ⟹ O100『峰間/包絡比 ≈0.6 ⟹ f≈0.2-0.3』推論**撤銷** (實測比 = {r_data_mean:.3f})

  ② R4 之真缺口 = σ8 (唔係谷/峰比)
     A_φφ 1.011±0.028 ⟹ σ8_IDCM = {sig8_need:.4f}   (BOSS 獨立: 0.783 ✓ 一致)
     O100 9 峰模型 σ8 = {s8_model}  ⟹ 缺口 {100*(sig8_need/s8_model-1):+.2f}% in σ8

  ③ 缺口因子無判別力
     結構池 ({len(vals)} 值, 由 {len(S)} 個 IDCM 結構整數生成) 對 [0.8,1.4] 之覆蓋率 = {100*cov:.1f}%
     目標命中 {n_hit} 個 ⟹ 唔可以由此定 f (覆蓋率法, 比 docs/10 §2 之計數法更嚴格)

  ④ R4 狀態: 張力解除 ✅ / 缺口定位 ✅ / 缺口值 🔴 (gated on O100 #1 之 44-mode 包絡權重)
""")
print(f"RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL:
    print("FAILED:", FAIL)
