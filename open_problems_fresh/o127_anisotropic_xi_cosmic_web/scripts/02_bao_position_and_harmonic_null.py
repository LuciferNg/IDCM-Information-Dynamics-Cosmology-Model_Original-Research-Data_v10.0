#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O127 / scripts/02_bao_position_and_harmonic_null.py
==================================================
P1: (a) IDCM BAO 尺度檢定 (α-dilation fit)  (b) 諧波序列 λ_sync/n null test

P1a: 官方 eBOSS DR16 LRG BAO model ξ0(s/α) 擬合數據 → α; IDCM λ_sync/2 vs fiducial r_d。
P1b: v9.0 聲稱「n=3..20 全部 18/18 S/N>3 檢測」。三項檢定:
     (i)  預言位置解析度 d_med vs bin 寬
     (ii) 殘餘結構 @ 預言位置 vs 位置隨機化 null (10^5)
     (iii) 密度基準入場券 N_search / d_med / q_obs (O208)
"""
import numpy as np, os, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
PASS, FAIL = [], []
def chk(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  [{'PASS' if c else 'FAIL'}] {n}" + (f"  | {d}" if d else ""))

def load_xi(fn):
    rows = []
    with open(os.path.join(RAW, fn)) as f:
        for line in f:
            if line.startswith("#") or not line.strip(): continue
            rows.append([float(x) for x in line.split()])
    return np.array(rows)

D = load_xi("Data_LRGxi_NGCSGC_0.6z1.0_postrecon.txt")
s, xi0, err0, xi2, err2, xi4, err4 = D.T
M = load_xi("Model_BAO_LRGxi_NGCSGC_0.6z1.0_postrecon.txt")
ms, mx0, mx2 = M.T

C_KMS, W_RING = 299792.458, 72.59
R_WORLD = C_KMS / W_RING
BAO_IDCM = (2*np.pi*R_WORLD/88)/2      # 147.439 Mpc 物理
H = W_RING/100.0
RS_FID = 147.78

print("="*78); print("  O127 / 02 — P1: BAO 尺度檢定 + 諧波序列 null test"); print("="*78)

# ---------------------------------------------------------------
print(f"\n[P1a] IDCM BAO 尺度 vs eBOSS DR16 LRG (z=0.698)")
print(f"    IDCM λ_sync/2 = πR_world/88 = {BAO_IDCM:.4f} Mpc (物理, 零參數, h-無關)")
print(f"    eBOSS fiducial r_d = {RS_FID} Mpc   → dev = {(BAO_IDCM/RS_FID-1)*100:+.3f}%  ★主結論")

# ★ h 投影敏感性 (用戶要求: 必須標明用邊個 h; v10.0 由 ω_ring 生成多個尺度投影)
PROJ = [("h_cmb  (CMB 尺度)", 0.674071), ("h_o170 (徑向)", 0.711570),
        ("ω_ring/100", 0.725900), ("h_lad  (徑向/BAO)", 0.731300), ("eBOSS fiducial", 0.676000)]
print(f"\n    ★ h 投影敏感性 (λ_sync/2 落 eBOSS s-軸 [Mpc/h]):")
for nm, hh in PROJ:
    print(f"        {nm:20s} h={hh:.6f} → s = {BAO_IDCM*hh:8.2f} Mpc/h")
print(f"    觀測 BAO 峰喺 s ≈ 100 Mpc/h (r_d^fid×0.676 = {RS_FID*0.676:.2f})")
print(f"    ⟹ h_cmb/0.674 落峰上; ω_ring/100 投影偏 +7% (1.5 bin)")

def chi2_alpha(alpha):
    mi = np.interp(s, ms/alpha, mx0); m2 = np.interp(s, ms/alpha, mx2)
    ok = (s >= ms.min()) & (s <= ms.max())
    d = np.concatenate([(xi0[ok]-mi[ok])/err0[ok], (xi2[ok]-m2[ok])/err2[ok]])
    return float(np.sum(d**2))

alphas = np.linspace(0.85, 1.15, 6001)
chi2s = np.array([chi2_alpha(a) for a in alphas])
a_best = alphas[np.argmin(chi2s)]
print(f"\n    α-dilation fit: α_best = {a_best:.4f}, χ²_min = {chi2s.min():.2f} / {2*((s>=ms.min())&(s<=ms.max())).sum()} dof")
print(f"    → 觀測 BAO 尺度 = {RS_FID*a_best:.2f} Mpc")
chk("IDCM BAO 同 eBOSS r_d 一致 (<0.5%)", abs(BAO_IDCM/RS_FID-1) < 0.005, f"dev={(BAO_IDCM/RS_FID-1)*100:+.3f}%")
chk("α_best ≈ 1", abs(a_best-1) < 0.03, f"α={a_best:.4f}")
chk("IDCM/fid 落入 α_best 1σ 內", abs(BAO_IDCM/RS_FID - a_best) < 0.02,
    f"IDCM/fid={BAO_IDCM/RS_FID:.4f} vs α_best={a_best:.4f}")
chk("★ h_cmb 投影落喺觀測峰 ±1 bin", abs(BAO_IDCM*0.674071 - RS_FID*0.676) < 5.0,
    f"{BAO_IDCM*0.674071:.1f} vs {RS_FID*0.676:.1f} Mpc/h")

# ---------------------------------------------------------------
print(f"\n[P1b] 諧波序列 λ_sync/n (n=2..20) — null test")
pos_hinv = np.array([BAO_IDCM*2/n for n in range(2, 21)]) * H
print(f"    λ_sync/n 換 eBOSS Mpc/h: {np.round(pos_hinv,1)}")
print(f"    (h 投影 = ω_ring/100 = 0.7259; 敏感度: d_med ∝ h ⟹ 0.674 投影 d_med×0.93 仍 <1 bin)")

# (i) 解析度
gaps = np.diff(np.sort(pos_hinv))
d_med = float(np.median(gaps))
n_degen = int((gaps < 5.0).sum()) + 1     # 同一 bin 內嘅位置數
print(f"\n    (i) 位置解析度: d_med = {d_med:.2f} Mpc/h = {d_med/5:.2f} bin (bin 寬 5 Mpc/h)")
print(f"        {len(pos_hinv)} 個位置擠入 {pos_hinv.max()-pos_hinv.min():.0f} Mpc/h 跨度")
print(f"        相鄰 gap < 1 bin 嘅位置數 = {n_degen}/{len(pos_hinv)}")
chk("d_med < 1 bin ⟹ 預言位置不可分辨 (測試零鑑別力)", d_med/5 < 1.0, f"d_med={d_med:.2f} Mpc/h = {d_med/5:.2f} bin")
chk("過半位置互相重疊 (同一 bin)", n_degen > len(pos_hinv)/2, f"{n_degen}/{len(pos_hinv)}")

# (ii) 殘餘結構 — log 空間 broadband, 限制 s>=25 (避開 1-halo 區); 需 xi0>0
mask = (s >= 25.0) & (xi0 > 0)
sm, sx0, se0 = s[mask], xi0[mask], err0[mask]
cf = np.polyfit(np.log(sm), np.log(sx0), 5)
bb = np.exp(np.polyval(cf, np.log(sm)))
res = sx0 - bb
snr = res/se0
print(f"\n    (ii) 殘餘 (s≥25, log-poly5 broadband): {mask.sum()} bins")
print(f"        RMS(res)={res.std():.5f}, RMS(err)={se0.mean():.5f}, mean|S/N|={np.abs(snr).mean():.2f}")

inr = pos_hinv[(pos_hinv >= sm.min()) & (pos_hinv <= sm.max())]
def stat_snr(positions, sarr=sm, snrarr=snr):
    return np.array([np.abs(snrarr[np.argmin(np.abs(sarr-p))]) for p in positions])
obs = stat_snr(inr)
print(f"        預言位置 (s≥25): {len(inr)} 個")
for p, v in zip(inr, obs):
    print(f"          λ_sync/n @ {p:6.1f} Mpc/h : |S/N| = {v:.2f}")

# ★ 分離 n=2 (BAO) vs n≥3 (高階諧波)
inr_n2 = inr[:1]; inr_n3 = inr[1:]
obs_n2 = stat_snr(inr_n2); obs_n3 = stat_snr(inr_n3)

rng = np.random.default_rng(127)
NS = 100000
def null_dist(npos):
    m = np.empty(NS); c = np.empty(NS, dtype=int)
    for k in range(NS):
        v = stat_snr(rng.uniform(sm.min(), sm.max(), npos))
        m[k] = v.mean(); c[k] = (v > 3).sum()
    return m, c
n3m, n3c = null_dist(len(inr_n3))
print(f"\n        n≥3 ({len(inr_n3)} 位置): obs mean|S/N| = {obs_n3.mean():.2f}, #>3 = {(obs_n3>3).sum()}")
print(f"          null: mean = {n3m.mean():.2f} ± {n3m.std():.2f}, #>3 = {n3c.mean():.2f}")
p_n3_mean = float((n3m >= obs_n3.mean()).mean()); p_n3_cnt = float((n3c >= (obs_n3>3).sum()).mean())
print(f"          → P(mean ≥ obs) = {p_n3_mean:.3f}, P(#>3 ≥ obs) = {p_n3_cnt:.3f}")
print(f"\n        n=2 (BAO) 單獨: |S/N| = {obs_n2[0]:.2f}  ← 呢個係真 BAO 特徵 (見 P1a)")

chk("★ n≥3 高階諧波: mean|S/N| 唔超越隨機 null (零檢測)", p_n3_mean > 0.05,
    f"obs={obs_n3.mean():.2f} vs null={n3m.mean():.2f}±{n3m.std():.2f}, P={p_n3_mean:.3f}")
chk("★ n≥3 高階諧波: #>3 唔超越隨機 null", p_n3_cnt > 0.05,
    f"obs={(obs_n3>3).sum()}/{len(inr_n3)}, null mean={n3c.mean():.2f}, P={p_n3_cnt:.3f}")
chk("殘餘超額集中喺 n=2 (BAO), 唔係諧波序列", obs_n2[0] > obs_n3.mean(),
    f"n=2 |S/N|={obs_n2[0]:.2f} > n≥3 mean={obs_n3.mean():.2f}")

# (iii) 密度基準入場券
N_search = int(mask.sum()); q_obs = float((obs > 3).sum())
print(f"\n    (iii) 密度基準入場券 (O208): N_search={N_search}, d_med={d_med:.2f} Mpc/h "
      f"({d_med/5:.2f} bin), q_obs={q_obs}")
chk("密度基準入場券齊全 (N_search/d_med/q_obs)", N_search > 0 and d_med > 0, "已報")

# 對照: 只用 n=2 (BAO) 單一位置 — 唯一有鑑別力嘅檢定
i2 = np.argmin(np.abs(s - pos_hinv[0]))
print(f"\n    [對照] 只用 n=2 (BAO): λ_sync/2 = {pos_hinv[0]:.1f} Mpc/h, s_bin={s[i2]:.1f}, "
      f"ξ0={xi0[i2]:.5f}±{err0[i2]:.5f}, S/N={xi0[i2]/err0[i2]:.2f}")
print(f"        官方 BAO model 局部峰 (80..130 Mpc/h) = "
      f"{ms[np.argmax(np.where((ms>80)&(ms<130), mx0, -1e9))]:.1f} Mpc/h")
chk("n=2 BAO 位置喺數據範圍內 (推翻 v9.0「範圍外」)", pos_hinv[0] < s.max(), f"{pos_hinv[0]:.1f} < {s.max():.1f}")

out = dict(bao_idcm=BAO_IDCM, rs_fid=RS_FID, dev=float(BAO_IDCM/RS_FID-1), alpha_best=float(a_best),
           d_med=d_med, n_degen=n_degen, n_pos=len(pos_hinv),
           obs_n2_snr=float(obs_n2[0]), obs_n3_mean_snr=float(obs_n3.mean()),
           null_n3_mean=float(n3m.mean()), null_n3_std=float(n3m.std()),
           p_n3_mean=p_n3_mean, p_n3_cnt=p_n3_cnt, N_search=N_search, q_obs=q_obs)
with open(os.path.join(BASE, "data", "02_results.json"), "w") as f:
    json.dump(out, f, indent=2)

print("\n" + "="*78)
print(f"  RESULT: {len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("  FAILED: " + ", ".join(FAIL))
print("="*78)
