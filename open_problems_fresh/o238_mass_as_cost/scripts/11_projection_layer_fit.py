#!/usr/bin/python3
"""O238 — Script 11: 分測量通道投影 fit (調律者投影框架初步檢定)

調律者指示: 質量 = 按測量而投影 (lazy evaluation). 9 個 freeze 質量點
唔係同一層: e/μ 實驗直量, τ/t 衰變運動學, u/d/s/c/b lattice 理論投影.

本 script:
  P1 通道分組 fit: G3(lattice 5點) fit α, C vs G全(9點) — 同通道內係咪 close?
  P2 跨通道預言: 用 G3 fit 預言 G1/G2 (e,μ,τ,t) — log 偏差 pattern
  P3 對照: γ·P_f 乘積形式 (O206 CSG v2 先例) vs 純冪律, 同一 9 點
  P4 投影身份: |dm| (位置算子自能家族, O136) 嘅二次投影檢查
"""
import numpy as np, math, json

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

N = 88
idxx = np.arange(1, N + 1)
psii = np.array([np.sin(n * math.pi * idxx / (N + 1)) for n in range(1, N + 1)])
psii = psii / np.linalg.norm(psii, axis=1)[:, None]
Xm = np.diag(idxx - idxx.mean())
V = psii @ Xm @ psii.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = E[:, None] - E[None, :]
G = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(G, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, G)
admn = np.abs(dm)
gam = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])

SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
names9 = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
M0 = 27.900915
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2

# freeze v2 (S2) 質量集 (docs/04: scheme 正確 b/c=4.586)
MS2 = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
       "u": 93.4/42.890, "d": 93.4/42.890*2.1505, "s": 93.4,
       "c": 93.4*11.652, "b": 93.4*11.652*4.586, "t": 172690.0}

# 測量通道分組 (投影譜系 docs/06 §二)
G_FREE = ["e", "mu"]        # 自由粒子實驗直量
G_COLL = ["tau", "t"]       # 高能碰撞衰變運動學
G_LAT  = ["u", "d", "s", "c", "b"]  # lattice 理論投影
G_ALL  = names9

def fit_alpha(parts):
    idx = [names9.index(p) for p in parts]
    logm = np.log([MS2[p] for p in parts])
    logd = np.log([admn[SEL9[i]-1] for i in idx])
    A = np.vstack([np.ones(len(parts)), logd]).T
    c, *_ = np.linalg.lstsq(A, logm, rcond=None)
    res = logm - A @ c
    rms = math.sqrt((res**2).mean())
    return c[1], c[0], rms, logd

print("═══ P1. 通道分組 fit ═══")
a_all, b_all, rms_all, _ = fit_alpha(G_ALL)
a_lat, b_lat, rms_lat, logd_lat = fit_alpha(G_LAT)
print(f"  G全 (9點, 混合投影): α={a_all:.6f} RMS={rms_all:.6f}")
print(f"  G3  (5點, lattice):  α={a_lat:.6f} RMS={rms_lat:.6f}")
print(f"  α dev: {abs(a_lat-PHI2):.4f} (φ² {PHI2:.6f}) — {'φ² 內' if abs(a_lat-PHI2)/0.2 < 1 else '偏離'}")
print(f"  G3 RMS vs G全 RMS: {rms_lat/rms_all:.3f}× (同通道較細 ⟹ 混合投影係殘差來源)")
chk("P1.1 G3(lattice) 同通道內 RMS 顯著細過混合 9 點", rms_lat < 0.6*rms_all,
    f"G3 RMS={rms_lat:.4f} vs GAll RMS={rms_all:.4f} ratio={rms_lat/rms_all:.3f}")

print("\n═══ P2. 跨通道預言 (G3 fit → G1/G2) ═══")
print("  用 G3 (lattice) fit 嘅 (α, C) 預言自由粒子 + 碰撞通道:")
for grp, parts in [("G1 自由粒子", G_FREE), ("G2 碰撞", G_COLL)]:
    for p in parts:
        i = names9.index(p)
        pred = math.exp(b_lat + a_lat * math.log(admn[SEL9[i]-1]))
        ldev = math.log(pred / MS2[p])
        print(f"    {p:4s}: pred={pred:10.4f} MeV  obs={MS2[p]:10.4f}  log偏差={ldev:+.4f}")

print("\n═══ P3. γ·P_f 乘積形式 vs 純冪律 (O206 CSG v2 先例) ═══")
# CSG v2: m = M0·γ_n·P_f. 若 P_f = C·|dm|^{φ²-?} ... 先做簡單: log m = a + α·log(γ·|dm|^q)?
# 兩參數 fit: log m = a + q·log γ + p·log|dm|
logm = np.log([MS2[p] for p in names9])
logd = np.log([admn[n-1] for n in SEL9])
logg = np.log([gam[n-1] for n in SEL9])
X3 = np.vstack([np.ones(9), logg, logd]).T
c3, *_ = np.linalg.lstsq(X3, logm, rcond=None)
r3 = logm - X3 @ c3
rms3 = math.sqrt((r3**2).mean())
print(f"  log m = a + q·logγ + p·log|dm|:  q={c3[1]:+.4f} p={c3[2]:+.4f} RMS={rms3:.6f}")
print(f"  純冪律 (α=φ² 固定) RMS = 0.5456; 三項 RMS = {rms3:.6f} ⟹ Δ={0.5456-rms3:+.4f}")
X2 = np.vstack([np.ones(9), logg]).T
c2, *_ = np.linalg.lstsq(X2, logm, rcond=None)
r2 = logm - X2 @ c2
rms2 = math.sqrt((r2**2).mean())
print(f"  純 γ (log m = a + αγ·logγ): αγ={c2[1]:+.4f} RMS={rms2:.6f}")

print("\n═══ P4. |dm| 投影身份 — 二次投影檢查 ═══")
# |dm| 係位置算子自能家族(O136): 佢本身可能已經係投影產物.
# 檢查: log|dm| 對 log γ 嘅關係 — |dm| 係咪 γ 嘅函數?
cc = np.corrcoef(logd, logg)[0,1]
print(f"  corr(log|dm|, log γ) = {cc:+.4f}")
# |dm| vs γ 冪律 fit
Xg = np.vstack([np.ones(9), logg]).T
cg, *_ = np.linalg.lstsq(Xg, logd, rcond=None)
rg = logd - Xg @ cg
rms_g = math.sqrt((rg**2).mean())
print(f"  log|dm| = a' + p'·logγ:  p'={cg[1]:+.4f} RMS={rms_g:.4f} (log 域)")

out = {"alpha_all": float(a_all), "rms_all": float(rms_all),
       "alpha_lat": float(a_lat), "rms_lat": float(rms_lat),
       "corr_dm_gamma": float(cc)}
with open("data/11_projection_layer.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")