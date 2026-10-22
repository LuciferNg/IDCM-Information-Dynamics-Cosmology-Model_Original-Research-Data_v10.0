#!/usr/bin/env python3
"""
O187 Route A — 兩語言對齊裁定 (Authoritative, 整合 Part 1-3)
=============================================================
裁定問題: γ·P_f 語言 (L1/O136-O187) vs |Δm|^α 語言 (L2/O209) 係咪同一物兩種參數化?

L1: m = M0·γ_n·P_f,  M0 = 27.900915 MeV,  n ∈ {1,7,14,20,33,34},  P_f ∈ 結構池
L2: m = M0'·|Δm|^α,  M0' = e^(−13.5071) MeV,  n ∈ {1,2,3,4,5,7,9,11,13},  α ≈ 2.6333

判定基準 (預註冊):
  (i)   L2 n-set 落 L1 形式: C_f = m/(M0·γ_n) 應落入 L1 P_f 池 (±2%)
  (ii)  P_f_implied = (M0'/M0)·|Δm|^α/γ_n 應落入 L1 P_f 池 (±2%)
  (iii) L1 語言 fit 品質 vs L2 (RMS ln-space)

由原始定義獨立重算: V_nm = ⟨n|x|m⟩, ψ_n(i)=sin(nπi/89), N=88, 歸一化
E_n = 4sin²(nπ/88); |Δm_n| = Σ_{m≠n} |V_nm|²/|E_n−E_m| (退化→0)
"""
import numpy as np, math, json
from pathlib import Path

NC = 88
M0_L1 = 27.900915
M0_L2 = math.exp(-13.5071)
TOL = 0.02

OUT = Path(__file__).parent.parent / "data"
RES = {}

# ── 原始構建 ──
x = np.arange(1, NC+1, dtype=float)
Psi = np.zeros((NC, NC))
for n in range(1, NC+1):
    Psi[:, n-1] = np.sin(n*math.pi*x/(NC+1))
for n in range(NC):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4*math.sin(n*math.pi/88)**2 for n in range(1, NC+1)])

def dm2(n):
    d = E[n-1] - E
    with np.errstate(divide='ignore', invalid='ignore'):
        g = np.where(np.abs(d) > 1e-12, 1.0/d, 0.0)
    return float(np.sum(V[n-1, :]**2 * g))

DM = {n: abs(dm2(n)) for n in range(1, NC+1)}
def gamma(n): return 4*math.sin(n*math.pi/88)**2

# sanity (O209 docs 值)
assert abs(DM[1] - 16862.478721) < 1e-4, DM[1]
assert abs(DM[13] - 152.535542) < 1e-4, DM[13]
RES["sanity_dm"] = {"dm1": DM[1], "dm13": DM[13]}

MASS = {"e":0.511000,"u":2.16,"d":4.67,"s":93.4,"mu":105.6584,"c":1270.0,
        "tau":1776.86,"b":4180.0,"t":172690.0}
L1_N = {"e":1,"mu":7,"tau":20,"u":1,"d":1,"s":14,"c":34,"b":33}
L1_PF = {"e":3.6,"mu":15.5,"tau":37.0,"u":15.5,"d":33.0,"s":3.6,"c":13.0,"b":44.0}
L2_N = {"t":1,"b":2,"tau":3,"c":4,"mu":5,"s":7,"d":9,"u":11,"e":13}
POOL = np.array([18/5, 44-28.5, 44-7, 44-11, 13.0, 44.0])
POOL_LAB = ["L6/F5=3.6","Nd−Eproj=15.5","Nd−L4=37","Nd−L5=33","F7=13","Nd=44"]

rows = []
r1 = []
for p in ["e","u","d","s","mu","c","tau","b"]:
    mp = MASS[p]
    n1, pf = L1_N[p], L1_PF[p]
    m1 = M0_L1*gamma(n1)*pf
    r1.append(math.log(m1/mp))
    # (i) L2 n-set 落 L1 形式
    n2 = L2_N[p]
    cf = mp/(M0_L1*gamma(n2))
    dmin = float(np.abs(cf-POOL).min())
    # (ii) P_f_implied
    imp = (M0_L2/M0_L1)*DM[n2]**(79/30)/gamma(n2)
    rows.append({"p": p, "m_pdg": mp, "L1_n": n1, "L1_Pf": pf, "L1_m": m1,
                 "L1_dev_pct": (m1-mp)/mp*100,
                 "L2_n": n2, "Cf_m_M0L1_gamma": cf, "pool_dist_min": dmin,
                 "Pf_implied": imp})
    print(f"{p:>4} n1={n1:>3} Pf={pf:>5.1f} m1={m1:>10.4f} (dev {(m1-mp)/mp*100:+6.2f}%) | "
          f"L2n={n2:>3} Cf={cf:>9.4f} 池dist={dmin:>8.4f} | P_imp={imp:>10.4f}")

# L1 fit 品質
rms1 = float(np.sqrt(np.mean(np.array(r1)**2)))
# L2 fit 品質 (9 點, α 擬合)
lv = np.array([math.log(MASS[p]) for p in ["e","u","d","s","mu","c","tau","b","t"]])
ld = np.array([math.log(DM[L2_N[p]]) for p in ["e","u","d","s","mu","c","tau","b","t"]])
c2 = float(np.corrcoef(ld, lv)[0,1])
alpha_fit = float(np.polyfit(ld, lv, 1)[0])
resid = lv - (alpha_fit*ld + np.polyfit(ld, lv, 1)[1])
rms2 = float(np.sqrt(np.mean(resid**2)))

RES.update({
  "L1_rms_log": rms1, "L2_corr": c2, "L2_alpha_fit": alpha_fit, "L2_rms_log": rms2,
  "ratio_L1overL2": rms1/rms2,
  "rows": rows,
})
print(f"\nL1 RMS(ln) = {rms1:.4f}   L2 RMS(ln, fit α={alpha_fit:.4f}) = {rms2:.4f}   L1/L2 = {rms1/rms2:.2f}×")
print(f"L1 語言 fit 比 L2 好 {rms2/rms1:.0f}× — L1 後驗搜索產物, L2 質量排序產物")

# 命中統計 (i)(ii)
n_hit_i = sum(1 for r in rows if r["pool_dist_min"] < TOL*44)  # 44 唔啱, 用 |池|*TOL
n_hit_i = sum(1 for r in rows if r["pool_dist_min"] < TOL*44)
n_hit_ii = sum(1 for r in rows if min(abs(r["Pf_implied"]-POOL)) < TOL*44)
# 正確: 相對距離
n_hit_i = sum(1 for r in rows if min(abs(r["Cf_m_M0L1_gamma"]-POOL)/POOL) < TOL)
n_hit_ii = sum(1 for r in rows if min(abs(r["Pf_implied"]-POOL)/POOL) < TOL)
RES["hit_count_i"] = n_hit_i
RES["hit_count_ii"] = n_hit_ii
print(f"\n裁定 (i) L2 n-set 落 L1 池命中: {n_hit_i}/8")
print(f"裁定 (ii) P_f_implied 落 L1 池命中: {n_hit_ii}/8")
print(f"⟹ 兩語言 {'可以對齊' if n_hit_i >= 7 and n_hit_ii >= 7 else '唔可以對齊'} — "
      f"{'｜同一物兩種參數化' if n_hit_i>=7 and n_hit_ii>=7 else '｜語言分歧係真'}")

(OUT/"03_language_alignment.json").write_text(
    json.dumps(RES, ensure_ascii=False, indent=2))
print(f"\n✅ 寫入 data/03_language_alignment.json")
