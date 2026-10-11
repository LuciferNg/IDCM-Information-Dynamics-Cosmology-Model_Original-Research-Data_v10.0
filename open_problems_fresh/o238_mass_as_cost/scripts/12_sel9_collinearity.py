#!/usr/bin/python3
"""O238 — Script 12: SEL9 共線性檢定 — mode 選擇 = projection (調律者框架)

發現 (scripts/11 P4 follow-up): corr(log|dm|, log γ) 全譜 88 點 = −0.300 (弱),
但 9 個粒子 mode = −0.996 (完美共線) ⟹ 共線係「選擇效應」唔係 |dm| 本質.

調律者框架: 質量 = 按測量而投影; 唔測量 = 粗粒化連續.
⟹ 選邊個 mode (粒子 assignment) 本身已經係投影操作 (P_f selection, O206 CSG v2).

本 script:
  P1 共線性檢定: 全譜 vs SEL9 嘅 corr / R² (log-log)
  P2 re-parameterization: m=C·|dm|^{φ²} 等價於 γ 冪律 (單自由度) — 指數一覽
  P3 CSG v2 對照: γ 指數 +1 (M₀·γ·P_f) vs O238 γ 指數 −2.40 — 衝突量化
  P4 SEL9 喺 (log|dm|, log γ) 平面: 有冇其他 mode 都落喺同一軌跡 (選擇係咪唯一)
"""
import numpy as np, math, json, itertools

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
PHI = (1 + math.sqrt(5)) / 2
PHI2 = PHI ** 2
logd = np.log(admn)
logg = np.log(gam)

print("═══ P1. 共線性檢定 ═══")
cc_all = np.corrcoef(logd, logg)[0,1]
mask = np.zeros(N, bool); mask[np.array(SEL9)-1] = True
cc_sel = np.corrcoef(logd[mask], logg[mask])[0,1]
r2_all = cc_all**2; r2_sel = cc_sel**2
print(f"  全譜 88 點: corr = {cc_all:+.4f}  R² = {r2_all:.4f}")
print(f"  SEL9 9 點:  corr = {cc_sel:+.4f}  R² = {r2_sel:.6f}")
chk("P1.1 全譜弱相關 (|dm| 本質唔共線 γ)", abs(cc_all) < 0.5, f"corr={cc_all:+.4f}")
chk("P1.2 SEL9 強共線 (選擇投影效應)", cc_sel**2 > 0.95, f"R²={r2_sel:.6f}")

print("\n═══ P2. re-parameterization: m=C·|dm|^{φ²} ↔ γ 冪律 ═══")
# log m = a + φ² log|dm|; 9 點 log|dm| ≈ b + s·logγ (s=−0.918)
A = np.vstack([np.ones(9), logg[mask]]).T
c, *_ = np.linalg.lstsq(A, logd[mask], rcond=None)
s = c[1]
print(f"  9 點: log|dm| = {c[0]:.4f} + ({s:.4f})·log γ")
print(f"  ⟹ m = C·|dm|^{{φ²}} ≈ C'·γ^{{{PHI2*s:.4f}}}  (γ 指數 = φ²×s = {PHI2*s:.4f})")
gamma_idx = PHI2 * s
chk("P2.1 O238 fit 等價 γ 冪律 (指數 < 0, 反比)", gamma_idx < 0, f"γ指數={gamma_idx:.4f}")

print("\n═══ P3. CSG v2 對照 ═══")
# CSG v2 (O206 docs/22): m = M0·γ_n·P_f → log m = log M0 + log γ + log P_f → γ 指數 +1
print("  CSG v2:  m = M₀·γ_n·P_f           → γ 指數 = +1 (質量 ∝ γ)")
print(f"  O238:    m = C·|dm|^{{φ²}} (SEL9)    → γ 指數 = {gamma_idx:+.4f} (質量 ∝ γ^{{{gamma_idx:.3f}}})")
print("  ⟹ 兩者 γ 指數相反 → 模式分配衝突 (O206-OPEN-4) 定量化")
chk("P3.1 γ 指數衝突坐實 (+1 vs 負)", (1 - gamma_idx) > 1.5,
    f"+1 − ({gamma_idx:.3f}) = {1-gamma_idx:.3f}")

print("\n═══ P4. SEL9 選擇唯一性 — 有冇其他 9 點 mode 組合都共線 ═══")
# 在 full 88 譜, log|dm| vs log γ 非線性. 隨機抽 9 點, R² 分佈?
rng = np.random.default_rng(20261011)
r2s = []
for _ in range(20000):
    pick = rng.choice(N, 9, replace=False)
    ld = logd[pick]; lg = logg[pick]
    # 迴歸 R²
    A_ = np.vstack([np.ones(9), lg]).T
    c_, *_ = np.linalg.lstsq(A_, ld, rcond=None)
    r = ld - A_ @ c_
    ss_res = (r**2).sum(); ss_tot = ((ld-ld.mean())**2).sum()
    r2s.append(1 - ss_res/ss_tot)
r2s = np.array(r2s)
above = (r2s >= r2_sel).mean()
print(f"  隨機 9 點 R² 分佈: mean={r2s.mean():.4f}  max={r2s.max():.4f}  p(R²≥{r2_sel:.4f})={above:.6f}")
chk("P4.1 SEL9 共線顯著異常 (隨機 9 點幾乎冇咁共線)", above < 0.01,
    f"p={above:.6f}")

out = {"cc_all": float(cc_all), "cc_sel": float(cc_sel),
       "r2_sel": float(r2_sel), "gamma_index_equiv": float(gamma_idx),
       "random9_p": float(above)}
with open("data/12_sel9_collinearity.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)

print(f"\nRESULT: {sum(1 for _, c_, _ in checks if c_)}/{len(checks)} checks passed")
for nm, c_, dt in checks:
    print(f"  [{'OK' if c_ else 'XX'}] {nm} — {dt}")