#!/usr/bin/env python3
"""
O131 — 04: λ_sync 諧波階梯 相位折疊疊加檢定 (保留項 — 繼續推)
==============================================================
背景 (見 docs/02, docs/04):
  v9.0 `stacking_toolbox` 嘅獨有內容 (局部阻抗模型) 已廢; 但「疊加」作為**檢定工具**
  仍然有用 — 因為 IDCM 嘅 λ_sync 諧波階梯 (k_n = 2πn/λ_sync) 係**零參數**預言,
  可以用相位折疊 (phase folding) 把 BOSS/eBOSS 嘅 wiggle 信號疊加, 得出一個
  單一嘅、帶 MC null + look-elsewhere 校正嘅顯著度 — 呢個係 O31 逐點匹配做唔到嘅。

本 script 做三件事:
  A. 單位換算釘死 (h/Mpc ↔ h⁻¹Mpc) — 用 c/H₀ = 2998 h⁻¹Mpc 錨, 核 v9/o31/o133 嘅換算方向
  B. BOSS DR12 P(k) wiggle 相位折疊 + α-scan + MC null (相位 null + 置換 null)
  C. eBOSS DR16 ξ(s) 峰/零點加權差 + 連續移位 null

⚠️ 誠實原則: 結果唔顯著就報唔顯著; 唔為咗「閉合」而調 α 或窗。
"""

import math, os, json
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
SEED = 20260927
rng = np.random.default_rng(SEED)

PASS, FAIL = 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; mark = "✅"
    else:    FAIL += 1; mark = "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))

print("=" * 84)
print("  O131/04 — λ_sync 諧波階梯 相位折疊疊加檢定")
print("=" * 84)

# ================================================================
# A. 單位換算釘死
# ================================================================
C_KMS = 299792.458
OMEGA_RING = 72.59                 # (km/s)/Mpc  [O73]
H_IDCM = OMEGA_RING / 100          # 0.7259 (IDCM 慣例值)
H_BOSS = 0.676                     # BOSS DR12 fiducial h (Ross 2016 / o133 已用)
R_WORLD_MPC = C_KMS / OMEGA_RING   # 4129.94 Mpc (physical)
LAM_SYNC_MPC = math.pi * R_WORLD_MPC / 44      # 294.877 Mpc (physical) [O73/O171]
R_D_MPC = LAM_SYNC_MPC / 2                     # 147.439 Mpc (physical) [O127/O171]

print("\n─── A. 單位換算 (h/Mpc ↔ h⁻¹Mpc) ───")
print(f"  R_world = {R_WORLD_MPC:.4f} Mpc (physical);  λ_sync = {LAM_SYNC_MPC:.4f} Mpc;  r_d = {R_D_MPC:.4f} Mpc")
# 錨: c/H₀ = (c/100h) Mpc = (c/100) h⁻¹Mpc (h 無關, 標準 ~3000)
cH0_hinv = C_KMS / 100.0
print(f"  錨: c/H₀ = {C_KMS/(100*H_IDCM):.2f}/h Mpc = {cH0_hinv:.2f} h⁻¹Mpc (h 無關, 標準 ~3000)")
check("A1 c/H₀ = 2998 h⁻¹Mpc (換算錨, h 無關)", abs(cH0_hinv - 2997.92) < 0.5, f"{cH0_hinv:.2f}")

def mpc_to_hinv(x_mpc, h): return x_mpc * h      # 乘 h  ← 正確
def mpc_to_hinv_wrong(x_mpc, h): return x_mpc / h  # 除 h  ← v9/o31/o133 用

lam_hinv_correct = mpc_to_hinv(LAM_SYNC_MPC, H_BOSS)      # 199.34
lam_hinv_v9 = mpc_to_hinv_wrong(LAM_SYNC_MPC, H_IDCM)     # 406.22
lam_hinv_o133 = mpc_to_hinv_wrong(LAM_SYNC_MPC, H_BOSS)   # 436.21
print(f"  λ_sync [h⁻¹Mpc]: 正確 = {lam_hinv_correct:.2f} (×h, h={H_BOSS})")
print(f"                   v9.0 = {lam_hinv_v9:.2f} (÷h, h={H_IDCM});  o133 = {lam_hinv_o133:.2f} (÷h, h={H_BOSS})")
ratio = lam_hinv_o133 / lam_hinv_correct
check("A2 v9/o31/o133 用「÷h」而非「×h」⟹ 偏差 = 1/h²",
      abs(ratio - 1/H_BOSS**2) < 1e-9, f"o133/正確 = {ratio:.4f} = 1/h² (h={H_BOSS})")
# 交叉驗證: r_d 應該等於觀測 BAO 尺度 ~100 h⁻¹Mpc
r_d_hinv = mpc_to_hinv(R_D_MPC, H_BOSS)
print(f"  ★ 交叉驗證: r_d = λ_sync/2 = {r_d_hinv:.2f} h⁻¹Mpc (乘 h) vs 觀測 BAO ~100 h⁻¹Mpc")
check("A3 r_d (乘 h) ≈ 100 h⁻¹Mpc = 觀測 BAO 尺度 ⟹ 「乘 h」係正確方向", abs(r_d_hinv - 99.7) < 2.0,
      f"{r_d_hinv:.2f} h⁻¹Mpc")
r_d_wrong = mpc_to_hinv_wrong(R_D_MPC, H_BOSS)
check("A3b r_d (除 h) = 218 h⁻¹Mpc ≠ 觀測 ⟹ 「除 h」錯", abs(r_d_wrong - 218) < 3, f"{r_d_wrong:.2f} h⁻¹Mpc")

DK_CORRECT = 2 * math.pi / lam_hinv_correct     # 0.031520 h/Mpc
DK_V9 = 2 * math.pi / lam_hinv_o133             # 0.014403 h/Mpc
print(f"  Δk (階梯週期): 正確 = {DK_CORRECT:.6f} h/Mpc;  v9/o133 用 = {DK_V9:.6f} h/Mpc (差 {DK_V9/DK_CORRECT:.3f}×)")

# ================================================================
# B. BOSS DR12 P(k) wiggle 相位折疊
# ================================================================
print("\n─── B. BOSS DR12 P(k) wiggle 相位折疊 + α-scan + MC null ───")
kb, Wb = [], []
with open(os.path.join(DATA, "boss_dr12_bao_wiggles.txt")) as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        p = line.split()
        kb.append(float(p[0])); Wb.append(float(p[3]))
kb = np.array(kb); Wb = np.array(Wb)
N = len(kb)
print(f"  數據: {N} 點, k ∈ [{kb[0]:.5f}, {kb[-1]:.5f}] h/Mpc;  σ_W(估計) = {Wb.std():.4f}")
check("B0 BOSS wiggle 數據載入", N >= 80, f"{N} 點")

# α-scan: 週期 = α × Δk_correct... 定義 λ_eff = α·λ_sync → Δk = 2π/(α·λ)
# A(α) = <W cos(k·λ_sync/α)> ; P(α) = A² + B²
alphas = np.linspace(0.40, 2.60, 881)
def fold_power(alphas, k, W, lam=lam_hinv_correct):
    ph = np.outer(k * lam, 1.0 / alphas)          # (N, Na)
    A = (W @ np.cos(ph)) / len(k)
    B = (W @ np.sin(ph)) / len(k)
    return A, B, A**2 + B**2
A1, B1, P1 = fold_power(alphas, kb, Wb)
i_best = int(np.argmax(P1))
alpha_best = float(alphas[i_best]); P_best = float(P1[i_best])
A_at_1 = float(np.interp(1.0, alphas, A1)); P_at_1 = float(np.interp(1.0, alphas, P1))
# h 慣例敏感度: 若用 IDCM 慣例 h=0.7259 → λ = 214.05 h⁻¹Mpc → α = 199.34/214.05
alpha_h_idcm = lam_hinv_correct / mpc_to_hinv(LAM_SYNC_MPC, H_IDCM)
print(f"  α-scan [0.40, 2.60] (881 點): α_best = {alpha_best:.4f}, P_best = {P_best:.3e}")
print(f"  α = 1 (IDCM 零參數預言, h_fid=0.676): A = {A_at_1:+.5f}, P = {P_at_1:.3e}")
print(f"  α = {alpha_h_idcm:.4f} (若用 IDCM h=0.7259): P = {float(np.interp(alpha_h_idcm, alphas, P1)):.3e}")
print(f"  α = {DK_V9/DK_CORRECT:.4f} (v9/o133 舊換算): P = {float(np.interp(DK_V9/DK_CORRECT, alphas, P1)):.3e}")

# --- Null A: 相位平移 (ladder phase origin) ---
NSHIFT = 200_000
shifts = rng.random(NSHIFT)
# A(δ) = <W cos(k λ + 2πδ)>, δ uniform → 等價於隨機相位
# 用複數: Z(δ) = <W exp(i k λ)> · exp(i 2π δ) → |Z| 同 δ 無關!
# ⟹ 相位平移 null 對「固定 α」嘅 |Z| 無效 (|Z| 平移不變)。故用**置換 null** 為主。
print("\n  ⚠️ 相位平移 null 對 |Z| 係恆等 (|Z| 平移不變) ⟹ 必須用置換 null")
# --- Null B: 置換 W 跨 k (破壞任何週期相干性, 保留 k 分佈) ---
NPERM = 200_000
# 向量化: 每次置換 = 隨機排列 W, 計 max_α P(α)
Pmax_null = np.empty(NPERM)
chunk = 10_000
cosmat = np.cos(np.outer(kb * lam_hinv_correct, 1.0/alphas))   # (N, Na)
sinmat = np.sin(np.outer(kb * lam_hinv_correct, 1.0/alphas))
for s in range(0, NPERM, chunk):
    m = min(chunk, NPERM - s)
    idx = np.argsort(rng.random((m, N)), axis=1)      # (m, N) 隨機排列
    Wp = Wb[idx]                                      # (m, N)
    A = Wp @ cosmat / N
    B = Wp @ sinmat / N
    Pmax_null[s:s+m] = (A**2 + B**2).max(axis=1)
Pmax_null.sort()
p_global = float(np.searchsorted(Pmax_null, P_best) / NPERM)
p_global = 1.0 - p_global
# ★ 對多個 α (含各版本用過嘅 λ_sync 換算) 各做固定-α 置換 null
alpha_o31 = lam_hinv_correct / 406.1
ALPHA_CANDIDATES = {
    "α=1.0000 (正確, h=0.676)": 1.0,
    "α=%.4f (正確, h=0.7259)" % alpha_h_idcm: alpha_h_idcm,
    "α=%.4f (o31 406.1)" % alpha_o31: alpha_o31,
    "α=%.4f (v9/o133 舊)" % (DK_V9/DK_CORRECT): DK_V9/DK_CORRECT,
}
b_rows = {}
for name, a in ALPHA_CANDIDATES.items():
    j = int(np.argmin(np.abs(alphas - a)))
    P_obs_a = float(P1[j])
    Pn = np.empty(NPERM)
    for s in range(0, NPERM, chunk):
        m = min(chunk, NPERM - s)
        idx = np.argsort(rng.random((m, N)), axis=1)
        Wp = Wb[idx]
        A = Wp @ cosmat[:, [j]] / N
        B = Wp @ sinmat[:, [j]] / N
        Pn[s:s+m] = (A**2 + B**2).ravel()
    Pn.sort()
    pv = 1.0 - float(np.searchsorted(Pn, P_obs_a) / NPERM)
    b_rows[name] = {"alpha": a, "P_obs": P_obs_a, "p": pv, "null_med": float(np.median(Pn))}

# 保留 α=1 為主要報告
p_alpha1 = b_rows["α=1.0000 (正確, h=0.676)"]["p"]

print(f"  ── 置換 null ({NPERM} 樣本, seed={SEED}) ──")
for name, r in b_rows.items():
    print(f"     {name:<28} P_obs = {r['P_obs']:.3e};  null 中位 = {r['null_med']:.3e};  p = {r['p']:.4f}")
print(f"     全 α 掃描 (look-elsewhere): P_best = {P_best:.3e};  null max 中位 = {np.median(Pmax_null):.3e};  p = {p_global:.4f}")
# ★ check 驗「計算有效性」(null 校正正確), 物理 verdict 另列 (見總結表)
P_null_expect = Wb.var() / (2 * N)
check("B1 null 校正正確 (null 中位 P ≈ σ_W²/2N, 差 <2×)",
      abs(b_rows["α=1.0000 (正確, h=0.676)"]["null_med"]/P_null_expect - 1) < 1.0,
      f"null {b_rows['α=1.0000 (正確, h=0.676)']['null_med']:.2e} vs 期望 {P_null_expect:.2e}")
check("B2 p 值由 ≥2e5 置換樣本計算且 ∈ [0,1]",
      all(0.0 <= r["p"] <= 1.0 for r in b_rows.values()) and (0.0 <= p_global <= 1.0) and NPERM >= 200_000,
      "; ".join(f"{k.split()[0]} p={r['p']:.3f}" for k, r in b_rows.items()))

# ================================================================
# C. eBOSS DR16 ξ(s) 峰/零點加權差
# ================================================================
print("\n─── C. eBOSS DR16 ξ(s) 峰 (λ_sync/n) vs 零點 (λ_sync/(n+0.5)) 加權差 ───")
se, xe, ee = [], [], []
with open(os.path.join(DATA, "eboss_dr16_lrg_xi.txt")) as f:
    for line in f:
        if line.startswith('#') or not line.strip(): continue
        p = line.split()
        se.append(float(p[0])); xe.append(float(p[1])); ee.append(float(p[2]))
se = np.array(se); xe = np.array(xe); ee = np.array(ee)
print(f"  數據: {len(se)} 點, s ∈ [{se[0]:.1f}, {se[-1]:.1f}] h⁻¹Mpc")

# broadband removal: 標準 ξ = a + b/s + c/s² 擬合 (BAO 分析慣例), 加權
def broadband_resid(s, xi, err):
    X = np.vstack([np.ones_like(s), 1.0/s, 1.0/s**2]).T
    Wm = np.diag(1.0/err**2)
    beta = np.linalg.solve(X.T @ Wm @ X, X.T @ Wm @ xi)
    return xi - X @ beta
xr = broadband_resid(se, xe, ee)
print(f"  去 broadband (a + b/s + c/s², 加權) 後殘餘 RMS = {xr.std():.4f}")

def peak_null_diff(s, xr, err, lam, delta=0.0, nmax=30):
    """峰 at λ/(n+δ) vs 零點 at λ/(n+δ+0.5), 反變異數加權差"""
    n = np.arange(1, nmax+1, dtype=float)
    pn = lam / (n + delta); qn = lam / (n + delta + 0.5)
    def wi(pos):
        m = (pos >= s[0]) & (pos <= s[-1])
        if not m.any(): return 0.0, 0.0
        x = np.interp(pos[m], s, xr); e = np.interp(pos[m], s, err)
        w = 1.0/e**2
        return float(np.sum(w*x)/np.sum(w)), float(np.sqrt(1.0/np.sum(w)))
    mp, ep = wi(pn); mq, eq = wi(qn)
    return mp - mq, math.hypot(ep, eq)

# ★ 向量化 null (s 係 5.0 h⁻¹Mpc 規則柵格 ⟹ 手動線性插值)
DS = se[1] - se[0]
def interp_vec(pos):
    """pos: (M,) → (M,) 線性插值 (規則柵格)"""
    t = (pos - se[0]) / DS
    i0 = np.clip(np.floor(t).astype(int), 0, len(se) - 2)
    fr = t - i0
    return xr[i0]*(1-fr) + xr[i0+1]*fr, ee[i0]*(1-fr) + ee[i0+1]*fr

def diff_vec(lam, deltas, nmax=30):
    """del: (Nd,) → D: (Nd,)"""
    n = np.arange(1, nmax+1, dtype=float)
    pn = lam / (n[None, :] + deltas[:, None])            # (Nd, nmax)
    qn = lam / (n[None, :] + deltas[:, None] + 0.5)
    out = np.empty(len(deltas))
    for tag, pos in (("p", pn), ("q", qn)):
        m = (pos >= se[0]) & (pos <= se[-1])
        posc = np.where(m, pos, se[0])
        x, e = interp_vec(posc.ravel())
        x = x.reshape(pos.shape); e = e.reshape(pos.shape)
        w = np.where(m, 1.0/e**2, 0.0)
        num = np.sum(w*x, axis=1); den = np.sum(w, axis=1)
        out = num/den if tag == "p" else out - num/den
    return out

D_obs, D_err = peak_null_diff(se, xr, ee, lam_hinv_correct)
print(f"  λ_sync = {lam_hinv_correct:.2f} h⁻¹Mpc (×h 正確, h=0.676);  Δ = ⟨ξ⟩_峰 − ⟨ξ⟩_零 = {D_obs:+.5f} ± {D_err:.5f}"
      f"  ({D_obs/D_err:+.2f}σ)")

# null: 連續移位 δ ∈ [0,1)  (對每個候選 λ 各做一次)
NS = 200_000
deltas = rng.random(NS)
Dnull = np.sort(diff_vec(lam_hinv_correct, deltas))
p_D = 1.0 - float(np.searchsorted(Dnull, D_obs)/NS)
print(f"  ── 連續移位 null (δ~U(0,1), {NS} 樣本): null 中位 = {np.median(Dnull):+.5f}, "
      f"95% 界 = {Dnull[int(0.95*NS)]:+.5f};  p = {p_D:.4f}")
# ★ C1 驗「null 有效性」: null 分佈寬度應 ≈ 解析傳播誤差 (唔假設中位 = 0 —
#    峰/零點兩個位置集覆蓋唔同 s 區間, 殘餘有整體趨勢 ⟹ 中位可以偏移, 故用分佈而唔係置中檢定)
check("C1 null 有效 (null 標準差 ≈ 解析傳播誤差 D_err, 差 <2×)",
      abs(Dnull.std()/D_err - 1) < 1.0, f"null std = {Dnull.std():.5f} vs D_err = {D_err:.5f}")

# ★★ C2: 對所有「跨 O 用過嘅 λ_sync 值」逐一檢定 (含 o31 自己嘅 406.1) — 決定性測試
print("\n  ── C2. 各版本 λ_sync 值逐一檢定 (峰/零點差 + 連續移位 null) ──")
LAM_CANDIDATES = {
    "199.34 (正確, ×h, h=0.676)": lam_hinv_correct,
    "214.05 (正確, ×h, h=0.7259)": mpc_to_hinv(LAM_SYNC_MPC, H_IDCM),
    "406.10 (o31 硬編)": 406.1,
    "436.21 (o133 ÷h, h=0.676)": lam_hinv_o133,
}
c2_rows = {}
for name, lam in LAM_CANDIDATES.items():
    Do, De = peak_null_diff(se, xr, ee, lam)
    Dn = np.sort(diff_vec(lam, deltas))
    pv = 1.0 - float(np.searchsorted(Dn, Do)/NS)
    c2_rows[name] = {"lam": lam, "D": Do, "err": De, "sigma": Do/De, "p": pv}
    print(f"     {name:<30} λ={lam:7.2f}  Δ = {Do:+.5f} ± {De:.5f}  ({Do/De:+5.2f}σ)  p = {pv:.4f}")
check("C2 所有候選 λ 嘅檢定完成 (4 個)",
      len(c2_rows) == 4 and all(0.0 <= r["p"] <= 1.0 for r in c2_rows.values()),
      "; ".join(f"{k.split()[0]} p={v['p']:.3f}" for k, v in c2_rows.items()))

# ★★ C3: λ-profile 掃描 — 睇 406.1 係唔係特別 (look-elsewhere 診斷)
print("\n  ── C3. λ-profile (Δ/σ vs λ, 100→600 h⁻¹Mpc) ──")
lam_grid = np.linspace(100.0, 600.0, 26)
prof = []
for L in lam_grid:
    Do, De = peak_null_diff(se, xr, ee, L)
    prof.append(Do/De)
prof = np.array(prof)
i_pk = int(np.argmax(prof))
print(f"     全局最佳: λ = {lam_grid[i_pk]:.1f} h⁻¹Mpc → Δ/σ = {prof[i_pk]:+.2f}")
print(f"     λ=199.34 (r_d 錨定) → {prof[np.argmin(np.abs(lam_grid-199.34))]:+.2f}σ;  "
      f"λ=406.10 (o31) → {prof[np.argmin(np.abs(lam_grid-406.1))]:+.2f}σ;  "
      f"λ=436.21 (o133) → {prof[np.argmin(np.abs(lam_grid-436.21))]:+.2f}σ")
prof_str = " ".join(f"{L:.0f}:{s:+.1f}" for L, s in zip(lam_grid, prof))
print(f"     profile: {prof_str}")
check("C3 λ-profile 完成 (26 點, 全部 |Δ/σ| < 5)",
      len(prof) == 26 and np.all(np.abs(prof) < 5.0), f"max |Δ/σ| = {np.abs(prof).max():.2f}")

# ★★ C4: λ-scan look-elsewhere 校正 (null 校準) — 折疊工具嘅核心價值
def sigma_of_lambda(lam, nmax=30):
    n = np.arange(1, nmax+1, dtype=float)
    def s1(pos):
        m = (pos >= se[0]) & (pos <= se[-1])
        if not m.any(): return np.inf
        e = np.interp(pos[m], se, ee)
        return float(np.sum(1.0/e**2))
    return math.sqrt(1.0/s1(lam/n) + 1.0/s1(lam/(n+0.5)))

NS4 = 20_000
deltas4 = rng.random(NS4)
sig_lam = np.array([sigma_of_lambda(L) for L in lam_grid])
obs_max = float(np.abs(prof).max())
null_max = np.empty(NS4)
CH = 2_000
for s in range(0, NS4, CH):
    m = min(CH, NS4 - s)
    Dm = np.empty((m, len(lam_grid)))
    for j, L in enumerate(lam_grid):
        Dm[:, j] = diff_vec(L, deltas4[s:s+m]) / sig_lam[j]
    null_max[s:s+m] = np.abs(Dm).max(axis=1)
null_max.sort()
p_scan = 1.0 - float(np.searchsorted(null_max, obs_max) / NS4)
print(f"\n  ── C4. λ-scan look-elsewhere (null 校準, {NS4} 樣本, {len(lam_grid)} λ) ──")
print(f"     觀測 max_λ |Δ/σ| = {obs_max:.2f} (λ = {lam_grid[i_pk]:.1f})")
print(f"     null max_λ |Δ/σ| 中位 = {np.median(null_max):.2f}, 95% 界 = {null_max[int(0.95*NS4)]:.2f}")
print(f"     ⟹ p_scan (已含 look-elsewhere) = {p_scan:.4f}")
check("C4 λ-scan look-elsewhere 校正完成 (p ∈ [0,1])",
      0.0 <= p_scan <= 1.0, f"p_scan = {p_scan:.4f}")

# ── 物理 VERDICT (唔入 PASS 計數; 假說被證偽 = 發現) ──
print("\n  ── 物理 VERDICT (假說檢定) ──")
verdict = []
for name, r in b_rows.items():
    verdict.append((f"B: BOSS 折疊 {name.split()[0]}", f"p = {r['p']:.4f}",
                    "🔴 不顯著" if r["p"] >= 0.05 else "🟢 顯著"))
verdict.append(("B: α-scan best (α=%.3f)" % alpha_best, f"p = {p_global:.4f}",
                "🔴 不顯著" if p_global >= 0.05 else "🟢 顯著"))
for name, r in c2_rows.items():
    verdict.append((f"C: eBOSS {name.split()[0]}", f"{r['sigma']:+.2f}σ, p = {r['p']:.4f}",
                    "🔴 不顯著" if r["p"] >= 0.05 else "🟢 顯著"))
verdict.append(("C: λ-scan look-elsewhere", f"max |Δ/σ| = {obs_max:.2f}, p_scan = {p_scan:.4f}",
                "🔴 不顯著" if p_scan >= 0.05 else "🟢 顯著"))
for name, val, v in verdict:
    print(f"     {v:<10} {name:<34} {val}")

# ================================================================
# 總結
# ================================================================
print("\n" + "=" * 84)
print("  總結 (誠實評級)")
print("=" * 84)
print(f"  A. 單位: v9/o31/o133 用「÷h」⟹ λ_sync 偏 {ratio:.3f}× (1/h²); 正確 λ_sync = {lam_hinv_correct:.2f} h⁻¹Mpc")
print(f"     ⟹ 之前 k-space 階梯預言 (Δk ≈ 0.0144–0.0155 h/Mpc) 週期錯 ~2.05×")
print(f"  B. BOSS P(k) 折疊: 4 個 α 候選全部不顯著 (p = " +
      ", ".join(f"{r['p']:.3f}" for r in b_rows.values()) + f"); α-scan best α = {alpha_best:.3f}, p = {p_global:.4f}")
print(f"  C. eBOSS ξ(s) 峰/零點: 4 個 λ 候選全部不顯著 (p = " +
      ", ".join(f"{r['p']:.3f}" for r in c2_rows.values()) + ")")
print(f"  ★ 決定性: 即使改用 o31 自己嘅 λ_sync = 406.1 h⁻¹Mpc，eBOSS 檢定 p = {c2_rows['406.10 (o31 硬編)']['p']:.4f}，BOSS p = {b_rows['α=%.4f (o31 406.1)' % alpha_o31]['p']:.4f}")

out = {
    "seed": SEED, "n_perm": NPERM, "n_shift": NS,
    "units": {"lam_sync_mpc": LAM_SYNC_MPC, "r_d_mpc": R_D_MPC,
              "lam_sync_hinv_correct": lam_hinv_correct, "h_boss": H_BOSS,
              "lam_sync_hinv_v9": lam_hinv_v9, "lam_sync_hinv_o133": lam_hinv_o133,
              "lam_sync_hinv_o31": 406.1,
              "dk_correct": DK_CORRECT, "dk_v9": DK_V9, "ratio_o133_over_correct": ratio},
    "BOSS_fold": {"alpha_best": alpha_best, "P_best": P_best, "A_at_alpha1": A_at_1,
                  "P_at_alpha1": P_at_1, "p_alpha1": p_alpha1, "p_global": p_global,
                  "null_med_maxalpha": float(np.median(Pmax_null)),
                  "by_alpha": b_rows},
    "eBOSS_peaknull": {"D_obs": D_obs, "D_err": D_err, "sigma": D_obs/D_err, "p": p_D,
                       "null_med": float(np.median(Dnull)), "by_lambda": c2_rows,
                       "lambda_profile": {"grid": lam_grid.tolist(), "delta_over_sigma": prof.tolist(),
                                          "best_lambda": float(lam_grid[i_pk]), "best_sigma": float(prof[i_pk])},
                       "lambda_scan_lookelsewhere": {"obs_max_abs_sigma": obs_max, "p_scan": p_scan,
                                                      "n_null": NS4, "n_lambda": len(lam_grid),
                                                      "null_med": float(np.median(null_max)),
                                                      "null_95": float(null_max[int(0.95*NS4)])}},
    "RESULT": f"{PASS}/{PASS+FAIL} PASS",
}
with open(os.path.join(DATA, "04_ladder_fold_results.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n  RESULT: {PASS}/{PASS+FAIL} PASS")
print(f"  寫入 data/04_ladder_fold_results.json")
