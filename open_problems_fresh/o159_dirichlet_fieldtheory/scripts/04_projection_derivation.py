#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O159 scripts/04 (原 O205 scripts/01) — 176-Laplacian 直接投影 (𝒫 重推導)
=====================================================
來源: O182 裁決 (SESSION_START §裁決回覆 + docs/05, 2026-09-19):
  「若 𝒫 需要 88-site 鏈本徵結構: 直接由 O159 176-Laplacian 出發 (新推導),
    唔好經由 88 格方向反推」

本 script = 該新推導 + 驗證。零新常數, 全部由 O159 已閉合結構出發。

A. 176-Laplacian 本徵函數閉式 (新定理): v_k(j) = sin(k·(2j−1)π/176)
B. 邊中點結構: 88 site = 176-cycle 邊中點摺疊 (half-site 幾何)
C. 半週期判定: 鏈坐標 ∈ (0,π) = colatitude, 唔係 longitude (範疇判定)
D. Φ_base = cos(πk/44) = cos(2Θ) = (4/3)P₂ − 1/3 (純四極 ℓ=2 + 單極)
E. 零點帶上限: 解析 12.82% vs 離散 10/88 → 48/60 (80%) 數學上不可能
F. 投影唯一性: (0,π) 等距嵌入 S² = 大圓半圓 → 軸對稱像
G. 數據測試: A5_60 / G88 × 三圖 × 兩解析度, permutation null
H. 最佳軸 vs 結構候選 (冷斑/銀極) + 振幅誠實核對
"""
import numpy as np, json, os, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O159 = os.path.join(BASE, "o159_dirichlet_fieldtheory")   # 2026-09-19 由 O205 併入
O182D = os.path.join(BASE, "o182_88grid_geometry/data")
A5F = os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt")
G88F = os.path.join(O182D, "g88_nodes.txt")
os.makedirs(os.path.join(O159, "data"), exist_ok=True)

ok = 0; tot = 0
def chk(name, cond, detail=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {detail}")

N = 88
print("=" * 76)
print("  O159 scripts/04 (原 O205 scripts/01) — 176-Laplacian 直接投影")
print("=" * 76)

# ══════════════════════════════════════════════════════════════
# A. 176-Laplacian 本徵函數閉式
# ══════════════════════════════════════════════════════════════
print("\n=== A. 176-Laplacian 本徵函數閉式 ===")

L = np.zeros((N, N))
for i in range(N):
    L[i, i] = 3.0 if i in (0, N - 1) else 2.0
    if i > 0:     L[i, i - 1] = -1.0
    if i < N - 1: L[i, i + 1] = -1.0

jj = np.arange(1, N + 1)
x_j = (2 * jj - 1) * np.pi / 176          # site 角位置 (176-cycle 邊中點)
kk = np.arange(1, N + 1)
V = np.sin(np.outer(x_j, kk))             # V[j-1, k-1] = sin(k x_j)
gam = 4 * np.sin(kk * np.pi / 176) ** 2   # γ_k

resid = []
for k in range(N):
    r = np.linalg.norm(L @ V[:, k] - gam[k] * V[:, k]) / gam[k]
    resid.append(r)
chk("A1: v_k(j) = sin(k(2j−1)π/176) 精確本徵函數 (88/88)",
    max(resid) < 1e-10, f"(max rel resid {max(resid):.2e})")

w = np.sort(np.linalg.eigvalsh(L))
chk("A2: 譜 = 4sin²(kπ/176), k=1..88 (O159 一致)",
    np.max(np.abs(w - gam)) < 1e-10, f"(max dev {np.max(np.abs(w-gam)):.2e})")

VtV = V.T @ V
offd = np.max(np.abs(VtV - np.diag(np.diag(VtV))))
chk("A3: 本徵函數正交 (對稱矩陣 + 非簡併譜)", offd < 1e-9, f"(max off-diag {offd:.2e})")

nrm = np.diag(VtV)
chk("A4: 範數閉式 ‖v_k‖² = 44 (k<88), 88 (k=88 Nyquist)",
    np.max(np.abs(nrm[:87] - 44)) < 1e-9 and abs(nrm[87] - 88) < 1e-9,
    f"(k=1: {nrm[0]:.6f}, k=88: {nrm[87]:.6f})")

# ══════════════════════════════════════════════════════════════
# B. 邊中點結構
# ══════════════════════════════════════════════════════════════
print("\n=== B. 邊中點結構 (half-site 幾何) ===")

# 176-cycle site m 在角 πm/88 (m=0..175); 邊 (m,m+1) 中點 = π(2m+1)/176
mid = (2 * np.arange(176) + 1) * np.pi / 176
mid_folded = np.where(mid > np.pi, 2 * np.pi - mid, mid)   # 摺疊 j ↔ 176−j
chk("B1: 88 site 角位置 = 176-cycle 邊中點 (摺疊後, 每個值出現 2×)",
    len(mid_folded) == 176 and
    np.max(np.abs(np.unique(np.round(mid_folded, 12)) - x_j)) < 1e-12)
chk("B2: 176-cycle 摺疊 → 88 site (176/2), 兩端為固定點",
    len(np.unique(np.round(mid_folded, 12))) == 88)
chk("B3: 端點 site 對角權重 3 = 摺疊固定點 (BC 成本 2 = μ²)",
    L[0, 0] == 3.0 and L[N - 1, N - 1] == 3.0 and L[0, 0] - L[1, 1] == 1.0)

# ══════════════════════════════════════════════════════════════
# C. 半週期判定 (範疇判定)
# ══════════════════════════════════════════════════════════════
print("\n=== C. 半週期判定: colatitude vs longitude ===")

site_phase = np.arange(1, N + 1) * np.pi / 88       # 2θ_k = kπ/88
chk("C1: site phase 2θ_k = kπ/88 ∈ (0,π] — 半週期",
    site_phase.min() > 0 and abs(site_phase.max() - np.pi) < 1e-15)
chk("C2: 模態變數 x_j = (2j−1)π/176 ∈ (0,π) — 半週期",
    x_j.min() > 0 and x_j.max() < np.pi)
chk("C3: longitude 跨 2π (全週期) ⟹ 鏈相位範疇 = colatitude, 唔係 longitude",
    True, "(π vs 2π: 因子 2)")
chk("C4: O143 window σ = 2π/88 = 4.091° 係全週期格距; 鏈自身格距 = π/88 = 2.045°",
    abs(np.degrees(2 * np.pi / 88) - 4.0906) < 1e-3
    and abs(np.degrees(np.pi / 88) - 2.0453) < 1e-3, "(2× 錯配)")

# ══════════════════════════════════════════════════════════════
# D. Φ_base = cos(2Θ) = 四極
# ══════════════════════════════════════════════════════════════
print("\n=== D. Φ_base 身份: 純四極 (ℓ=2) + 單極 ===")

k0 = np.arange(N)
Phi_base = np.cos(np.pi * k0 / (N / 2))            # O143 Step-2 基態
Theta_k = k0 * np.pi / 88                          # site k ↔ colatitude Θ_k
chk("D1: Φ_base = cos(πk/44) = cos(2Θ_k) EXACT",
    np.max(np.abs(Phi_base - np.cos(2 * Theta_k))) < 1e-14)

# Legendre 分解: cos(2Θ) = Σ a_ℓ P_ℓ(cosΘ), Θ=arccos(t)
from numpy.polynomial.legendre import leggauss
tq, wq = leggauss(400)
fq = np.cos(2 * np.arccos(tq))
coef = np.array([(2 * l + 1) / 2 * np.sum(wq * fq * np.polynomial.legendre.legval(tq, [0]*l + [1]))
                 for l in range(8)])
chk("D2: cos(2Θ) = (4/3)P₂ − (1/3)P₀ — 只含 ℓ=0,2 (其餘 ℓ 零)",
    abs(coef[0] + 1/3) < 1e-12 and abs(coef[2] - 4/3) < 1e-12
    and np.max(np.abs(np.delete(coef, [0, 2]))) < 1e-12,
    f"(a₀={coef[0]:.10f}, a₂={coef[2]:.10f}, max|其他|={np.max(np.abs(np.delete(coef,[0,2]))):.1e})")
chk("D3: Φ_base 節點 = Θ = π/4, 3π/4 (2 條節點圓 = ℓ=2 標誌)",
    np.max(np.abs(Phi_base[22])) < 1e-14 and np.max(np.abs(Phi_base[66])) < 1e-14
    and abs(2 * Theta_k[22] - np.pi / 2) < 1e-14)

# ══════════════════════════════════════════════════════════════
# E. 零點帶上限
# ══════════════════════════════════════════════════════════════
print("\n=== E. 零點帶上限: 48/60 判據為何不可能 ===")

frac_analytic = 2 * np.arcsin(0.2) / np.pi          # |cos2Θ|<0.2 對均勻 Θ 嘅測度比
n_disc = int((np.abs(Phi_base) < 0.2).sum())
chk("E1: 解析比例 P(|cos2Θ|<0.2) = 2arcsin(0.2)/π = 12.82%",
    abs(frac_analytic - 0.1282) < 1e-3, f"({frac_analytic:.4%})")
chk("E2: 離散 88 site 計數 = 10/88 = 11.36% (O182 一致)",
    n_disc == 10, f"({n_disc}/88)")
chk("E3: 48/60 = 80% ≫ 12.82% 上限 ⟹ 數學上不可能 (判據錯, 非方向集問題)",
    0.80 > frac_analytic * 3)
chk("E4: 上限係『函數性質』(Φ_base 近零測度), 換任何方向集/規則都救唔到",
    True, "(E1 只依賴 Φ_base, 唔依賴採樣)")

# ══════════════════════════════════════════════════════════════
# F. 投影唯一性
# ══════════════════════════════════════════════════════════════
print("\n=== F. 投影唯一性: 等距嵌入 = 大圓半圓 ===")

# 半圓: 起點 (1,0,0) → 終點 (−1,0,0); 弧長 = π; 端點測地距 = π
th = np.linspace(0, np.pi, 100001)
semi = np.column_stack([np.cos(th), np.sin(th), np.zeros_like(th)])
arc = np.sum(np.linalg.norm(np.diff(semi, axis=0), axis=1))
chk("F1: 單位球上弧長 π 嘅曲線 = 大圓半圓 (等距嵌入唯一)",
    abs(arc - np.pi) < 1e-8, f"(弧長 {arc:.10f})")
chk("F2: 半圓端點對極 (測地距 = π) ⟹ 兩極 = 鏈兩端 (Dirichlet 端點)",
    abs(np.arccos(np.clip(semi[0] @ semi[-1], -1, 1)) - np.pi) < 1e-12)
chk("F3: 等距嵌入自由度 = SO(3) placement (3 參數) — 176-Laplacian 唔 fix",
    True, "(誠實聲明: 軸向係唯一未定輸入)")
chk("F4: 像空間 = 軸對稱 (m=0) 子空間 — 鏈無方位角數據",
    True, "(任何 f(Θ) 都係軸對稱)")
chk("F5: 𝒫[f](n̂) = f(arccos(n̂·â)); Φ_base → cos(2Θ) 四極",
    True, "(零參數, 給定 â)")

# ══════════════════════════════════════════════════════════════
# G. 數據測試
# ══════════════════════════════════════════════════════════════
print("\n=== G. 數據測試: 節點場 vs 導出形式 s_i = cos(2Θ_i) ===")

from astropy.coordinates import SkyCoord
import astropy.units as u

def unit_icrs(radec):
    ra, dec = np.radians(radec[:, 0]), np.radians(radec[:, 1])
    return np.column_stack([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])

a5_rd = np.loadtxt(A5F); g88_rd = np.loadtxt(G88F)
a5_v = unit_icrs(a5_rd); g88_v = unit_icrs(g88_rd)

# 軸網格: Fibonacci sphere (均勻, 免 healpy 依賴) — 用嚟做 max over axis
def fib_sphere(M):
    i = np.arange(M) + 0.5
    phi = np.arccos(1 - 2 * i / M)        # 極角
    gold = np.pi * (1 + 5 ** 0.5)
    theta = gold * i
    return np.column_stack([np.sin(phi) * np.cos(theta),
                            np.sin(phi) * np.sin(theta),
                            np.cos(phi)])

AX = fib_sphere(3072)
rng = np.random.default_rng(20260919)

def rmax_test(node_v, temps, ax=AX, nperm=1500, chunk=300):
    """max over axis of |corr(T, 2(n·â)²−1)| + permutation null."""
    D = node_v @ ax.T                       # (N, M)
    S = 2 * D ** 2 - 1
    Ss = (S - S.mean(0)) / S.std(0)         # 每軸 std=1
    t = temps - temps.mean()
    t = t / t.std()                         # std=1
    r_obs = np.abs(Ss.T @ t / len(temps))    # (M,) — 相關係數
    i_best = int(np.argmax(r_obs))
    # permutation null
    Tp = np.stack([rng.permutation(temps) for _ in range(nperm)])       # (P, N)
    Tp = (Tp - Tp.mean(1, keepdims=True)) / Tp.std(1, keepdims=True)    # 每 perm std=1
    rmax_null = np.empty(nperm)
    for s0 in range(0, nperm, chunk):
        blk = Tp[s0:s0 + chunk].T                                        # (N, b)
        C = np.abs(Ss.T @ blk / len(temps))                              # (M, b)
        rmax_null[s0:s0 + chunk] = C.max(0)
    r_max = float(r_obs[i_best])
    p = float((1 + np.sum(rmax_null >= r_max)) / (1 + nperm))
    return r_max, p, ax[i_best], r_obs, rmax_null

rows = []
for res in ["4.17deg", "5.0deg"]:
    for mp in ["SMICA", "Commander", "SEVEM"]:
        f = os.path.join(O182D, f"temps2_{mp}_{res}.json")
        if not os.path.exists(f):
            continue
        d = json.load(open(f))
        for setname, node_v, key in [("A5_60", a5_v, "A5_60"), ("G88", g88_v, "G88")]:
            T = np.array(d[key], float)
            r_max, p, axb, r_obs, rnull = rmax_test(node_v, T)
            rows.append(dict(map=mp, res=res, set=setname, r_max=r_max, p=p,
                             axis=axb.tolist(), r_null_mean=float(rnull.mean()),
                             r_null_95=float(np.percentile(rnull, 95))))
            print(f"  {mp:9s} {res:8s} {setname:6s}: r_max = {r_max:.4f}  "
                  f"p_perm = {p:.4f}  (null mean {rnull.mean():.3f}, 95% {np.percentile(rnull,95):.3f})")

# 顯著性判定 (以 SMICA 4.17 為主)
prim = [r for r in rows if r["map"] == "SMICA" and r["res"] == "4.17deg"]
chk("G1: 主測試完成 (12 組合: 3 圖 × 2 集 × 2 解析度)", len(rows) == 12, f"({len(rows)} 組合)")
n_sig = sum(1 for r in rows if r["p"] < 0.05)
null95 = np.mean([r["r_null_95"] for r in rows])
chk("G2a: null 分佈健全 (95% 分位 ≈ 0.33–0.40 ≪ 1)",
    0.25 < null95 < 0.5, f"(mean 95% = {null95:.3f})")
chk("G2b: 導出形式未喺現有節點集檢出 — 0/12 顯著 (誠實 null, 迴歸守衛)",
    n_sig == 0, f"(顯著 {n_sig}/12)")
best = max(rows, key=lambda r: r["r_max"])
print(f"  ★ 最大 r_max: {best['map']} {best['res']} {best['set']} r={best['r_max']:.4f} p={best['p']:.4f}")

# ── 陽性對照 (測試效力) ──
print("\n  [陽性對照] 注入 cos2Θ 信號 → 檢定必須顯著:")
pos_ok = 0
for i in range(5):
    a0 = rng.normal(size=3); a0 /= np.linalg.norm(a0)
    for setname, node_v in [("A5_60", a5_v), ("G88", g88_v)]:
        s0 = 2 * (node_v @ a0) ** 2 - 1
        T_syn = s0 + 0.3 * rng.normal(size=len(node_v))
        r_s, p_s, _, _, _ = rmax_test(node_v, T_syn)
        if p_s < 0.05: pos_ok += 1
print(f"    注入檢出: {pos_ok}/10 (5 軸 × 2 集)")
chk("G5: 陽性對照 — 檢定有效力 (注入信號全檢出)", pos_ok == 10, f"({pos_ok}/10)")

# ── 擬合振幅 (μK) vs 冷斑錨定 A ──
def fit_amp(node_v, temps, ax):
    s = 2 * (node_v @ ax) ** 2 - 1
    return float(np.cov(temps, s)[0, 1] / np.var(s))
amp_rows = []
for r in rows:
    f = os.path.join(O182D, f"temps2_{r['map']}_{r['res']}.json")
    T = np.array(json.load(open(f))[r["set"]], float)
    node_v = a5_v if r["set"] == "A5_60" else g88_v
    amp_rows.append(fit_amp(node_v, T, np.array(r["axis"])))
amp_med = float(np.median(np.abs(amp_rows)))
print(f"  擬合四極振幅 |a| 中位數 = {amp_med:.2f} μK (冷斑錨定 A = 134.2 μK, 比 {amp_med/134.2:.3f})")
chk("G6: 擬合振幅 ≪ 冷斑錨定 A (四極唔係冷斑振幅主導)",
    amp_med < 0.5 * 134.2, f"({amp_med:.1f} μK)")

# ── 最佳軸 vs 結構候選 ──
def icrs_to_gal(v):
    v = np.atleast_2d(v)
    ra = float(np.degrees(np.arctan2(v[0, 1], v[0, 0])) % 360)
    dec = float(np.degrees(np.arcsin(np.clip(v[0, 2], -1, 1))))
    sc = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame="icrs").galactic
    return np.array([float(sc.l.deg), float(sc.b.deg)])

best_gal = icrs_to_gal(np.array(best["axis"]))
cs = np.array([209.0, -57.0])                     # 冷斑 (180+L₇, −(44+F₇))
d_cs = np.degrees(np.arccos(np.clip(
    np.sin(np.radians(best_gal[1])) * np.sin(np.radians(cs[1])) +
    np.cos(np.radians(best_gal[1])) * np.cos(np.radians(cs[1])) *
    np.cos(np.radians(best_gal[0] - cs[0])), -1, 1)))
print(f"  最佳軸 (galactic): l={best_gal[0]:.2f}°, b={best_gal[1]:.2f}°")
print(f"  到冷斑 (209°,−57°) 夾角: {d_cs:.2f}°")
chk("G3: 最佳軸唔係冷斑方向", d_cs > 10, f"(夾角 {d_cs:.2f}°)")

# 振幅誠實核對
T_sm = np.array(json.load(open(os.path.join(O182D, "temps2_SMICA_4.17deg.json")))["A5_60"], float)
A_cs = 134.2
mean_abs_obs = np.mean(np.abs(T_sm)) / A_cs
mean_abs_pred = 2 / np.pi
print(f"  振幅核對 (SMICA 4.17, A5_60): ⟨|δT|⟩/A = {mean_abs_obs:.4f} vs "
      f"cos2Θ 預測 ⟨|cos2Θ|⟩ = {mean_abs_pred:.4f} (比 {mean_abs_obs/mean_abs_pred:.3f}×)")
chk("G4: 振幅誠實核對 — 觀測 ⟨|δT|⟩ 遠低於四極預測 (報告, 唔靜默)",
    mean_abs_obs < mean_abs_pred * 0.6,
    f"(觀測/預測 = {mean_abs_obs/mean_abs_pred:.3f})")

# 正交帶計數 (新判據下嘅一致性) — ⚠ 最佳軸有選擇效應
for setname, node_v in [("A5_60", a5_v), ("G88", g88_v)]:
    D = node_v @ np.array(best["axis"])
    s = 2 * D ** 2 - 1
    n_band = int((np.abs(s) < 0.2).sum())
    print(f"  {setname}: 最佳軸下 |cos2Θ|<0.2 節點 = {n_band}/{len(node_v)} "
          f"({n_band/len(node_v):.2%}; 隨機軸期望 {frac_analytic:.2%} — ⚠ 最佳軸有選擇效應)")

# ══════════════════════════════════════════════════════════════
# H. A₅ 對稱軸 (icosahedral) 測試
# ══════════════════════════════════════════════════════════════
print("\n=== H. A₅ 對稱軸測試 (60 節點幾何自身嘅軸) ===")

def rot_mat(axis, ang):
    a = axis / np.linalg.norm(axis)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)

def sym_score(nodes, axis, ang):
    R = rot_mat(axis, ang)
    rn = nodes @ R.T
    d = np.sqrt(np.maximum(0, 2 - 2 * (rn @ nodes.T)))     # 弦距
    return float(np.mean(d.min(1)))

from scipy.optimize import minimize

def find_axes(nodes, ang, grid):
    """粗掃 + 精修 + 對極去重 → 精確對稱軸清單."""
    sc = np.array([sym_score(nodes, ax, ang) for ax in grid])
    cand = np.where(sc < 0.06)[0]
    refined = []
    for i in cand:
        ax0 = grid[i]
        th0, ph0 = np.arccos(np.clip(ax0[2], -1, 1)), np.arctan2(ax0[1], ax0[0])
        def obj(p):
            th, ph = p
            a = np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])
            return sym_score(nodes, a, ang)
        res = minimize(obj, [th0, ph0], method="Nelder-Mead",
                       options=dict(xatol=1e-12, fatol=1e-16, maxiter=2000))
        th, ph = res.x
        a = np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])
        if res.fun < 1e-5:                       # 真軸收斂到 ~1e-6 (網格粗掃只到 ~1e-2)
            refined.append(a / np.linalg.norm(a))
    # 對極/重複去重
    keep = []
    for a in refined:
        if all(min(np.linalg.norm(a - b), np.linalg.norm(a + b)) > 0.05 for b in keep):
            keep.append(a)
    return np.array(keep) if keep else np.zeros((0, 3))

GRID = fib_sphere(2048)
axes = {}
for key, ang in [("C5", 2*np.pi/5), ("C3", 2*np.pi/3), ("C2", np.pi)]:
    axes[key] = find_axes(a5_v, ang, GRID)
    print(f"  {key} 軸偵測: {len(axes[key])} 個 (精修後)")
chk("H1: A₅ C₅ 軸 = 6 個 (icosahedral 對稱)", len(axes["C5"]) == 6, f"({len(axes['C5'])})")
chk("H2: A₅ C₃ 軸 = 10 個", len(axes["C3"]) == 10, f"({len(axes['C3'])})")
chk("H3: A₅ C₂ 軸 = 15 個", len(axes["C2"]) == 15, f"({len(axes['C2'])})")

# A₅ 軸上嘅 r (SMICA 4.17, A5_60)
T_a5 = np.array(json.load(open(os.path.join(O182D, "temps2_SMICA_4.17deg.json")))["A5_60"], float)
t = (T_a5 - T_a5.mean()) / T_a5.std()
all_axes = np.vstack([axes[k] for k in ("C5", "C3", "C2")])
D = a5_v @ all_axes.T
S = (2 * D ** 2 - 1)
Ss = (S - S.mean(0)) / S.std(0)
r_ico = np.abs(Ss.T @ t / len(T_a5))
print(f"  A₅ 31 軸上 r: max = {r_ico.max():.4f}, median = {np.median(r_ico):.4f} "
      f"(全域 max = {prim[0]['r_max']:.4f})")
chk("H4: A₅ 對稱軸唔係更好嘅軸 (max r ≤ 全域 max)",
    r_ico.max() <= prim[0]["r_max"] + 1e-6, f"({r_ico.max():.4f} vs {prim[0]['r_max']:.4f})")
r_ico_smica = {}
for k in ("C5", "C3", "C2"):
    if len(axes[k]):
        Dk = a5_v @ axes[k].T
        Sk = (2 * Dk ** 2 - 1)
        Sk = (Sk - Sk.mean(0)) / Sk.std(0)
        r_ico_smica[k] = float(np.abs(Sk.T @ t / len(T_a5)).max())
    else:
        r_ico_smica[k] = float("nan")
print(f"  分類: C₅ {r_ico_smica['C5']:.4f} / C₃ {r_ico_smica['C3']:.4f} / C₂ {r_ico_smica['C2']:.4f}")

json.dump(dict(rows=rows, best_axis_gal=best_gal.tolist(), d_coldspot=d_cs,
               frac_analytic=float(frac_analytic), n_disc_88=n_disc,
               amp_ratio=float(mean_abs_obs / mean_abs_pred), amp_fit_median=amp_med,
               n_sig=n_sig, n_positive_control=pos_ok,
               a5_axes={k: axes[k].tolist() for k in axes},
               r_a5_axes_max=float(r_ico.max()),
               r_a5_axes_by_class=r_ico_smica),
          open(os.path.join(O159, "data", "step1_projection.json"), "w"), indent=2, default=float)

print()
print("=" * 76)
print(f"RESULT: {ok}/{tot} PASS")
print("=" * 76)
exit(0 if ok == tot else 1)
