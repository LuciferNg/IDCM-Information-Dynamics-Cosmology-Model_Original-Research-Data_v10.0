#!/usr/bin/python3
"""O239 — Script 47: e/ν 質量通道檢定 —— 投影 vs 激發（二通道互斥檢驗）
============================================================================
狀態: 2026-10-12（調律者: 「等等，e是否和v是否都是激發態而非投影」）

背景: IDCM 有兩套質量公式結構:
  ν (O49):     m₀ = (γ₆·v)²/M_comp × φ^(1/8)  —— 有 VEV v=246 GeV,
               seesaw 型「激發態」(場被 VEV 激發)
  e (O239):    m_e = M₀|Δm|^φ²  (α=φ² 固化, scripts/46)
  e (O54):     m_e = M₀·γ₁·(L₆/F₅)  —— 冇 v, 純譜投影

問題: e 同 ν 係咪同一通道? 定係「投影通道」(9 PAIR) 同「激發通道」(ν)
      兩套獨立機制?

任務:
  T1: ★e 用 ν 式: 全 88 mode γ_n 掃, 睇 M_req=(γ_n·v)²/m_e 有冇
      命中結構能標 (M_comp=3.933e13, M_Pl=1.221e19, M_GUT~2e16,
      901e12 等)? (閘: 命中 = |log10 距| < 0.1)
  T2: ★ν 用投影式: m_ν = M₀|Δm|^φ² (O239 1 參數, M₀=0.033331 MeV),
      睇要嘅 |Δm| 有冇落入譜域 [152, 16862]? (閘: 落入 = 同一通道可能)
  T3: 結構判讀: 若 T1/T2 都無命中 ⟹ 兩通道互斥, e≠ν 同一機制

產物: data/47_excitation_vs_projection.json
"""
import json
import math
import numpy as np

print("=" * 78)
print("O239 scripts/47 — e/ν 質量通道: 投影 vs 激發")
print("=" * 78)

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

PHI = (1 + 5**0.5)/2
PHI2 = PHI**2
NC = 88
v = 246.2196  # v_SM = 246.2196 GeV (O241)
m_e_GeV = 0.51099895e-3
M0_MeV = 0.033331  # O239 1 參數 (MeV)

# 結構能標池（★唔可以包含由 m_e 自己推出嘅量——池子陷阱!）
M_comp = 1.220910e19 / (2*36*98*44)  # O49: M_Pl/(2·h11·h21·Nd)
targets = {
    "M_comp(O49)": M_comp,   # 3.93e13
    "M_Pl": 1.220910e19,
    "M_GUT~2e16": 2e16,
}
print(f"  v = {v} GeV, m_e = {m_e_GeV*1e3} MeV")
print(f"  M_comp(O49) = {M_comp:.4e} GeV")
print(f"  閘: |log10(M_req/目標)| < 0.1 (≈26% 內)")

# ── T1: e 用 ν 式, 全 88 mode 掃 M_req ──
print("\n── T1: e 用激發式 m=(γ_n·v)²/M_req, 全 88 mode 掃 M_req ──")
best = None
for n in range(1, NC+1):
    gn = 4*math.sin(n*math.pi/NC)**2
    M_req = (gn*v)**2 / m_e_GeV
    for tname, tval in targets.items():
        d = abs(math.log10(M_req/tval))
        if best is None or d < best[0]:
            best = (d, n, gn, M_req, tname, tval)
d, n, gn, M_req, tname, tval = best
print(f"   γ_n 最大 = {4*math.sin(44*math.pi/88)**2:.4f} (n=44), "
      f"M_req_max = {(4*v)**2/m_e_GeV:.3e} GeV")
print(f"   M_req 範圍: {min((gn_*v)**2/m_e_GeV for gn_ in [4*math.sin(k*math.pi/NC)**2 for k in range(1,NC+1)]):.3e} – {(4*v)**2/m_e_GeV:.3e} GeV")
print(f"   最近命中: n={n} γ={gn:.4f} M_req={M_req:.3e} vs {tname}={tval:.3e} "
      f"|Δlog10|={d:.3f}")
hit_t1 = d < 0.1
# ★閘: T1 PASS = 冇命中 (e 唔可能係激發式同結構能標掛鉤)
chk("T1 e 用激發式冇命中結構能標(互斥)", not hit_t1,
    f"|Δlog10|={d:.3f} 閘<0.1 先算命中; 冇命中=通道互斥")

# ── T2: ν 用投影式, 睇要嘅 |Δm| ──
print("\n── T2: ν 用投影式 m_ν = M₀·|Δm|^φ², 要嘅 |Δm| ──")
m_nu_eV = 0.053479  # O49: m_0' = 0.053479 eV (ν₃)
print(f"   ν₃ mass = {m_nu_eV} eV = {m_nu_eV*1e-6} MeV")
lndm_needed = math.log(m_nu_eV*1e-6 / M0_MeV) / PHI2
dm_needed = math.exp(lndm_needed)
print(f"   |Δm| 要求 = M₀^(1)… |Δm| = exp(ln(m_ν/M₀)/φ²) = {dm_needed:.6e}")
print(f"   譜域 |Δm| ∈ [152.5, 16862.5] (data/09 dm9 範圍)")
in_domain = 152.5 <= dm_needed <= 16862.5
# ★閘: T2 PASS = 冇落入 (ν 唔可能係 9 點投影通道)
chk("T2 ν 用投影式唔落入譜域(互斥)", not in_domain,
    f"|Δm|={dm_needed:.3e} 譜域[152.5, 16863]; 唔落入=通道互斥")

# ── T3: 判讀 ──
print("\n── T3: 二通道互斥判定 ──")
print(f"   T1 (e 激發式命中結構能標): {hit_t1}")
print(f"   T2 (ν 投影式落入譜域):     {in_domain}")
print("   ⟹ 若兩者皆否: 投影通道 (9 PAIR 帶電費米子) 同激發通道 (ν)")
print("     兩套獨立機制——e 唔會係 ν 式激發, ν 唔會係 9 點投影")
verdict = "二通道互斥: e=投影/ν=激發 (兩套機制)"
if hit_t1 or in_domain:
    verdict = "⚠️ 有交叉! 要查"
print(f"   判定: {verdict}")

json.dump({
    "verdict": verdict,
    "T1": {"best_n": int(n), "best_gamma": float(gn), "M_req": float(M_req),
           "target": tname, "target_val": float(tval), "dlog10": float(d),
           "hit": bool(hit_t1), "M_req_range": [float(min((4*math.sin(k*math.pi/88)**2*v)**2/m_e_GeV for k in range(1,89))), float((4*v)**2/m_e_GeV)]},
    "T2": {"nu_mass_eV": m_nu_eV, "dm_needed": float(dm_needed),
           "spectrum_domain": [152.5, 16862.5], "in_domain": bool(in_domain)},
    "M_comp_O49": M_comp, "v_SM": v,
}, open("data/47_excitation_vs_projection.json", "w"), indent=1, ensure_ascii=False)

print(f"\n判定: {sum(1 for _, c in P if c)}/{len(P)} PASS")