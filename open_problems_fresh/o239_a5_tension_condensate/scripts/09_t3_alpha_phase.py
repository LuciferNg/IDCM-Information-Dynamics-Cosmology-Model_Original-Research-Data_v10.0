#!/usr/bin/python3
"""O239 — Script 09: T3 α = 相位冪? （局部 α 結構檢定）
============================================================================
策略 T3（docs/04 §三 + 攻堅策略 T3）: O206 已證 α=2.633254 喺任何常數池
不可辨識（607 池 P=0.4175, 兩錨盲測 α∈[2.58,3.05] 浮動）。⟹ 新問題唔係
「α=邊個常數」而係「**α 係咪相位投影嘅冪**」——即 α 唔係常數而係局部
函數 α(θ): d(ln m)/d(ln|Δm|) 對 θ 有冇結構?

材料（全部 prior-proved, data/09_o206_inputs.json）:
  9 模態 A5_MODES=[1,2,3,4,5,7,9,11,13], θ_n = nπ/88
  dm9 = |Δm_n|（O206 兩項式）, mass9 = m_n（10¹⁰yr 樣本商定 9 費米子）
  E_ring44: E_n = 4sin²(nπ/88)（= γ_n O136 權威）

預註冊判據（跑前凍結）:
  K1 冪律形式: ln|dm| vs ln θ 之 R²（如果 Δm 喺相位空間有冪律結構）
  K2 質量-相位: ln m vs ln θ 之 R²（質量對相位係咪冪律）
  K3 一致性: (質-相斜率)/(dm-相斜率) ≡ α?  偏差如何
  K4 ★局部 α_n: 9 點排序後嘅 8 個間隔 α_i = Δln m/Δln|dm|,
     對應平均 θ —— α_i 係常數（→ α 係普通冪）定係 θ 函數（→ α(θ) 相位冪）?
     判據: Spearman(α_i, θ_i) 顯著?
  K5 相位候選樣本外（兩錨凍結）: 用 (1,13) 兩錨凍結每個候選函數
     {m∝|dm|^α_fixed, m∝弦長=2sin(θ/2), m∝cotθ, m∝cscθ, m∝θ^p} 之一常數,
     預測其餘 7 點 RMS（對數空間）; 相位函數若 < 固定 α 全擬合 RMS → 相位路線可取
"""
import json, math
import numpy as np
from scipy import stats

OUT = json.load(open("data/09_o206_inputs.json", encoding="utf-8"))
PAIR = OUT["PAIR"]
dm9 = np.array(OUT["dm9"]); mass9 = np.array(OUT["mass9"])
N_MODES = [n for n, _ in PAIR]
theta9 = np.array([n*np.pi/88 for n, _ in PAIR])   # θ_n, 相位空間 88-gon

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/09 — T3: α = 相位冪? 局部 α 結構檢定")
print("=" * 78)

ldm = np.log(dm9)
lm = np.log(mass9)
lt = np.log(theta9)

# ── K1: ln|dm| vs ln θ ──
print("\n── K1: ln|dm| vs ln θ（|Δm| 喺相位空間嘅冪律結構）──")
slope_dm, ic_dm, r_dm, p_dm, se_dm = stats.linregress(lt, ldm)
print(f"   R² = {r_dm**2:.6f}   slope = {slope_dm:.4f}   p = {p_dm:.4e}")
chk("K1 |Δm| 對 θ 之冪律 R² > 0.9（結構存在）", r_dm**2 > 0.9,
    f"R²={r_dm**2:.4f}")

# ── K2: ln m vs ln θ ──
print("\n── K2: ln m vs ln θ（質量對相位冪律）──")
slope_m, ic_m, r_m, p_m, se_m = stats.linregress(lt, lm)
print(f"   R² = {r_m**2:.6f}   slope = {slope_m:.4f}   p = {p_m:.4e}")
chk("K2 質量對 θ 之冪律 R² > 0.9", r_m**2 > 0.9, f"R²={r_m**2:.4f}")

# ── K3: 一致性 α = slope_m/slope_dm ──
print("\n── K3: 一致性 α = slope_m / slope_dm ──")
alpha_pred = slope_m / slope_dm
alpha_obs = 2.633254
print(f"   slope_m/slope_dm = {slope_m:.4f}/{slope_dm:.4f} = {alpha_pred:.6f}")
print(f"   O206 α 全擬合 = {alpha_obs}")
dev = abs(alpha_pred - alpha_obs)/alpha_obs
chk("K3 相位冪推 α 同 O206 全擬合 α 偏差 < 5%", dev < 0.05,
    f"dev={dev*100:.2f}%")

# ── K4: 局部 α ──
print("\n── K4: 局部 α_i = Δln m / Δln|dm|（8 間隔）──")
# 排序按 θ（＝按 n，PAIR 已升序: 1,2,3,4,5,7,9,11,13）
alphas = []
ths_mid = []
for i in range(len(dm9)-1):
    da = (lm[i+1]-lm[i])/(ldm[i+1]-ldm[i])
    alphas.append(da)
    ths_mid.append(0.5*(theta9[i]+theta9[i+1]))
alphas = np.array(alphas); ths_mid = np.array(ths_mid)
print("   α_i:", ", ".join(f"{a:.3f}" for a in alphas))
print(f"   mean α_i = {alphas.mean():.4f}  std = {alphas.std():.4f}  (O206 α = {alpha_obs})")
rho, pval = stats.spearmanr(alphas, ths_mid)
print(f"   Spearman(α_i, θ_i) = {rho:.4f}  p = {pval:.4f}")
# 常數性判據: 局部 α 嘅變異係咪大到難當常數?
cv = alphas.std()/abs(alphas.mean())
chk("K4a 局部 α 有 θ 結構（Spearman |ρ|>0.7）", abs(rho) > 0.7,
    f"ρ={rho:.3f}")
chk("K4b 局部 α 唔係平穩常數（CV>15% 則 α(θ) 非固定）", cv > 0.15,
    f"CV={cv*100:.1f}%")

# ── K5: 相位候選樣本外兩錨（凍結 (1,13)）──
print("\n── K5: 相位函數候選兩錨樣本外（錨 = t + e）──")
i1, i13 = 0, 8
def oos_rms(fn_cand):
    """fn_cand(theta, A, B) -> m; 用錨 (1,13) 定 (A,B)（對數空間兩點插值），預測其餘 7 點 RMS"""
    t1, t13 = theta9[i1], theta9[i13]
    m1, m13 = mass9[i1], mass9[i13]
    # 對數空間線性: ln m = A + B·g(θ)
    g1, g13 = fn_cand(t1), fn_cand(t13)
    B = (math.log(m13)-math.log(m1))/(g13-g1)
    A = math.log(m1) - B*g1
    errs = []
    for i in range(len(mass9)):
        if i in (i1, i13): continue
        pred = math.exp(A + B*fn_cand(theta9[i]))
        errs.append((math.log(mass9[i])-math.log(pred))**2)
    return math.sqrt(sum(errs)/len(errs))

candidates = {
    "固定α冪律 m∝|dm|^α(α=2.6333)": lambda t: alpha_obs*math.log(OUT["dm9"][0])/1,  # 唔用（非相位）
    "相位冪 m∝θ^p":                lambda t: math.log(t),
    "弦長 m∝2sin(θ/2)":            lambda t: math.log(2*math.sin(t/2)),
    "γ m∝cscθ":                    lambda t: math.log(1/math.sin(t)),
    "動量 m∝cotθ":                 lambda t: math.log(1/math.tan(t)),
    "γ² m∝csc²θ":                  lambda t: 2*math.log(1/math.sin(t)),
    "弦² m∝4sin²(θ/2)=γ_n":        lambda t: math.log(4*math.sin(t/2)**2),
}
del candidates["固定α冪律 m∝|dm|^α(α=2.6333)"]
results = {}
for name, fn in candidates.items():
    rms = oos_rms(fn)
    results[name] = rms
    print(f"   {name:<24} 兩錨 OOS RMS(ln) = {rms:.4f}")
best = min(results, key=results.get)
print(f"   ⟹ 最佳: {best}  RMS = {results[best]:.4f}")
# 基準: 固定 α 全擬合殘餘（O206 → RMS 0.5872 ln 單位典型）
chk("K5 最佳相位候選 OOS RMS < 固定α全擬合典型殘餘（~0.6）",
    results[best] < 0.6, f"best={results[best]:.4f}")

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")

import os
json.dump({
    "k1_R2": r_dm**2, "k1_slope": slope_dm,
    "k2_R2": r_m**2, "k2_slope": slope_m,
    "k3_alpha_pred": alpha_pred, "k3_alpha_obs": alpha_obs, "k3_dev": dev,
    "k4_alphas": list(alphas), "k4_rho": rho, "k4_pval": pval, "k4_cv": cv,
    "k5_oos": results, "k5_best": best,
    "verdict": "T3: α 恆等數封死(O206); 局部α結構檢定中",
}, open("data/09_t3_alpha_phase.json", "w"), indent=1, ensure_ascii=False)
print("saved data/09_t3_alpha_phase.json")