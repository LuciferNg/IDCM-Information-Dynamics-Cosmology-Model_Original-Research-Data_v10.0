#!/usr/bin/env python3
"""
重驗 — 偏振 / GRB 色散 / 盲測預測 (對應 p12_uhecrs/records/03_uhecrs_record.md §7, data/*.json)
==============================================================================
路線 1-4 框架嘅數值部分重算。
"""
import math, os, json, sys
from scipy.stats import binom, norm

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.dirname(HERE)
SIB = os.path.dirname(CS)
UHE = os.path.join(SIB, 'p12_uhecrs', 'data')

phi = (1+5**0.5)/2
inv_phi = 1/phi
eps = inv_phi/4
kappa = 1/16
h = 6.62607015e-34; c = 2.99792458e8; L_P = 1.616255e-35
eV_J = 1.602176634e-19; GeV_J = 1.602176634e-10

rows = []
def chk(label, got, claim, tol, fmt="{:.6e}"):
    dev = abs(got/claim - 1) if claim else abs(got)
    ok = dev <= tol
    rows.append((label, fmt.format(got), fmt.format(claim), dev, ok))
    return ok

print("=" * 80)
print("重驗 — 偏振 / GRB / 盲測")
print("=" * 80)

# ---------- 偏振 α 候選 ----------
print("\n[偏振] α 候選 (rad):")
pol = json.load(open(os.path.join(UHE, 'polarization_parity.json')))
ac = pol['alpha_candidates_rad']
print(f"  ε = {eps:.9f}")
print(f"  ε⁵ = {eps**5:.6e}")
chk("ε⁵/8 (RMS)", eps**5/8, pol['rms_cold_spot'], 1e-6)
chk("ε⁵·32/60", eps**5*32/60, ac['eps5_32_60'], 1e-6)
chk("ε⁵/4", eps**5/4, ac['eps5_4'], 1e-6)
chk("κ·ε³", kappa*eps**3, ac['kappa_eps3'], 1e-6)
print(f"  ε⁵/8={eps**5/8:.4e}  ε⁵·32/60={eps**5*32/60:.4e}  ε⁵/4={eps**5/4:.4e}  κε³={kappa*eps**3:.4e}")

# ---------- GRB 色散 ----------
print("\n[GRB 色散]:")
grb = json.load(open(os.path.join(UHE, 'grb_dispersion.json')))
lam_min = L_P * phi**44
E_gzk_eV = h*c/lam_min/eV_J
chk("λ_min", lam_min, grb['lambda_min'], 1e-9)
chk("E_GZK (GeV)", E_gzk_eV/1e9, grb['E_gzk_GeV'], 1e-6)
print(f"  λ_min={lam_min:.4e} m;  E_GZK={E_gzk_eV/1e9:.4e} GeV")
print(f"  方向依賴色散: 效應 {grb['dispersion']['n1_dt_090510_s']:.2e} s ≫ 觀測限 {grb['dispersion']['obs_limit_s']} s → 現有數據測唔到 ✅")

# ---------- 盲測預測功效 ----------
print("\n[盲測預測功效]: 假設真實命中率 0.75, null p0=0.314")
blind = json.load(open(os.path.join(UHE, 'augerprime_blind_prediction.json')))
p0 = 0.314
def z_single(N, rate=0.75, p0=p0):
    """單比例: z = (p1−p0)/√(p0(1−p0)/N)"""
    return (rate-p0)/math.sqrt(p0*(1-p0)/N)
def z_two(N, rate=0.75, p0=p0):
    """雙比例(唔 pool): z = (p1−p0)/√(p1(1−p1)/N + p0(1−p0)/N)"""
    return (rate-p0)/math.sqrt(rate*(1-rate)/N + p0*(1-p0)/N)
print(f"  {'N':>4}{'單比例':>10}{'雙比例':>10}   文檔")
for N, doc in [(20, "3.1σ"), (50, "5.2σ")]:
    print(f"  {N:>4}{z_single(N):>9.2f}σ{z_two(N):>9.2f}σ   {doc}")
z20, z50 = z_two(20), z_two(50)
# 一致性檢查: 任何固定 p0 嘅 z 形式, z(50)/z(20) 必 = √2.5
ratio_required = math.sqrt(50/20)
ratio_doc = 5.2/3.1
print(f"  一致性: 文檔 z(50)/z(20) = {ratio_doc:.3f};  任何固定 p0 公式必 = √2.5 = {ratio_required:.3f}")
print(f"  → 文檔功效表 ({ratio_doc:.2f} vs {ratio_required:.2f}) 唔自洽 — 不可由所報輸入重現 🟡")
ok_pw = abs(ratio_doc - ratio_required) < 0.03
rows.append(("盲測功效自洽性", f"{ratio_doc:.3f}", f"√2.5={ratio_required:.3f}", abs(ratio_doc-ratio_required), ok_pw))
rows.append(("盲測 N=20 (雙比例)", f"{z20:.2f}σ", "3.1σ", abs(z20-3.1), abs(z20-3.1)<0.15))
rows.append(("盲測 N=50 (雙比例)", f"{z50:.2f}σ", "5.2σ", abs(z50-5.2), abs(z50-5.2)<0.15))

# ---------- LSS 框架 ----------
print("\n[LSS 框架]: 定性預測 (H1-H4), 無可重算數值 → 框架就緒")

# ============ 表 ============
print("\n" + "=" * 80)
print(f"{'量':<26}{'重算':>16}{'文檔':>16}{'dev':>11}{'':>4}")
print("-" * 80)
allok = True
for label, got, claim, dev, ok in rows:
    allok &= ok
    print(f"{label:<26}{got:>16}{claim:>16}{dev:>11.2e}  {'✅' if ok else '❌'}")
print("-" * 80)
print(f"結果: {sum(1 for *_,o in rows if o)}/{len(rows)} {'通過 ✅' if allok else '有 FAIL ❌'}")
out = os.path.join(CS, 'data', 'reverify_predictions.json')
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"alpha": ac, "rms": pol['rms_cold_spot'], "z20": z20, "z50": z50, "all_pass": bool(allok)},
          open(out, 'w'), indent=2)
print(f"已存 {out}")
sys.exit(0 if allok else 1)
