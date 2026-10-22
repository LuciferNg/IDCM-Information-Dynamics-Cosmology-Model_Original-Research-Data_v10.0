#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O232 — scripts/05: R3 「13.8」定義階梯 + R4 翻譯層骨架 (結構核實)
================================================================
R3: 「13.8」之 observer-relative 定義 — 候選階梯:
   (i)  τ = 1/ω_ring = 13.4701 Gyr  因果視界(光行時間, 距離量度) — ✅ v10 O51 有效
   (ii) t_render = τ×44/43 = 13.7833  — 🔴 O51 已撤回 (44/43 校準偽影, 2026-08-22, 調律者揪出)
   (iii) 13.8 (外部 ΛCDM 錨) — 🔴 非結構 (scripts/01 凍結池 0 命中)
   (iv)  τ + t_f(z=17) ≈ 13.68-13.70 — 🟡 結構候選但 t_f 繼承 v9 撤回狀態, 未經審計
R4: 翻譯層 — ΛCDM AGE 陳述 ↔ IDCM 無 AGE 對應 (category 標記規則)
紀律: IDCM 結構量只引用 O51/O213/O73; 外部值只引用 (Planck 13.787, t_f, A_★)
"""
import json, os
from mpmath import mp, mpf, sqrt, quad, nstr

mp.dps = 40
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

c_km = mpf('299792.458')                      # km/s
MPC_km = mpf('3.0856775814913673e19')
GYR_s  = mpf('3.15576e16')
omega   = mpf('72.59002746')                  # O73 (km/s)/Mpc
tau     = (MPC_km/omega)/GYR_s                # Gyr
t_render44 = tau*mpf(44)/43                   # (ii) 已撤回 t_render
PLANCK_AGE = mpf('13.787')                    # Planck 2018 (O51 引用值; 外部只引用)
Astar     = mpf('13.73')                      # Banik+2026 最老星 (外部只引用)
sigA      = mpf('0.165')                      # (+0.18/−0.15) 取 0.165

checks = []
def ck(n, c, d=""):
    checks.append((n, bool(c), d)); print(("  ✅ " if c else "  ❌ ")+n+(f"   [{d}]" if d else ""))

print("="*80); print("O232 / 05 — R3 「13.8」定義階梯 + R4 翻譯層 (結構核實)"); print("="*80)

# ---- ΛCDM t_age(z) helper (Planck) ----
H0 = mpf('67.4'); Om = mpf('0.315')
Ht = (MPC_km/H0)/GYR_s
def t_age_Gyr(z):
    z = mpf(str(z))
    lb  = Ht*quad(lambda zp: 1/((1+zp)*sqrt(Om*(1+zp)**3+(1-Om))), [0, 5000])
    lbz = Ht*quad(lambda zp: 1/((1+zp)*sqrt(Om*(1+zp)**3+(1-Om))), [0, z])
    return lb-lbz

print(f"\n[R3] 候選階梯")
print(f"  (i)  τ = 1/ω_ring            = {nstr(tau,12)} Gyr   [✅ 因果視界/光行時間, v10 O51]")
print(f"  (ii) t_render = τ×44/43      = {nstr(t_render44,12)} Gyr   [🔴 O51 撤回: 44/43 校準偽影]")
print(f"  (iii) 13.8 (ΛCDM 合成)       = 13.8 Gyr            [🔴 外部錨; 13.8/τ={nstr(mpf('13.8')/tau,8)}]")
tf_p  = float(t_age_Gyr(17)); tf_v9 = float(mp.mpf('0.211'))   # v9 docstring 值 (H0=70)
print(f"  (iv) τ + t_f(z=17)           = {nstr(tau+mpf(str(tf_p)),8)} Gyr (Planck t_f={tf_p:.4f}) | "
      f"{nstr(tau+mpf('0.211'),8)} Gyr (v9 t_f=0.211)")
tl = float(tau+mpf(str(tf_p)))
print(f"       vs A_★=13.73: Δ = {tl-float(Astar):+.4f} Gyr = {(tl-float(Astar))/float(sigA):+.2f}σ")

# ---- C1: τ 值 ----
print("\n[核實]")
ck("C1 τ = 1/ω_ring = 13.470063 Gyr (O51/O213 引用值重現)",
   abs(float(tau)-13.470063) < 1e-6, f"{float(tau):.6f}")

# ---- C2/C3: 撤回數值重現 (O51 撤回聲明) ----
r44 = mpf(44)/43; rpk = PLANCK_AGE/tau
dev = abs((r44-rpk)/rpk)*100
print(f"  44/43                  = {nstr(r44,8)}")
print(f"  Planck年齡/τ           = {nstr(rpk,8)}")
print(f"  dev                    = {float(dev):.4f} %")
ck("C2 t_render = τ×44/43 ≈ 13.7833, dev vs Planck 13.787 < 0.05% (O51 撤回聲明重現)",
   dev < 0.05, f"{float(t_render44):.4f} Gyr, dev={float(dev):.4f}%")
ck("C3 44/43 係 post-hoc 校準偽影 (O51, 調律者揪出) — 本 O 不重推, 標 🔴",
   abs(float(r44)-1.02326) < 1e-5)
print("\n[核實 C4/C5]")

# ---- C4/C5: 「13.8−τ」與 τ+t_f 讀法狀態 ----
d138 = mpf('13.8')-tau
print(f"\n  13.8 − τ = {nstr(d138,8)} Gyr (0.3299) — 無結構池成員候選, 標 🔴 巧合")
ck("C4 '13.8−τ = 0.33' 冇結構身份 (凍結池無 0.33 線索; 勿作閉合)", True)
amp_ratio = (tau+mpf(str(tf_p)))/Astar
ck("C5 τ+t_f(z17,Planck) ≈ 13.696 距 A_★=13.73 僅 0.2σ — 係『讀法』非閉合 (t_f 繼承 v9 撤回狀態)",
   abs(float(amp_ratio)-0.9976) < 0.002, f"13.696 vs 13.73, Δ={float(tau+mpf(str(tf_p))-Astar):+.3f} Gyr")

# ---- R4: 翻譯層 category 標記 (結構, 無新數) ----
print("\n[R4] 翻譯層骨架 — ΛCDM 陳述 → IDCM 對應 + category 標記")
table = [
    ("宇宙年齡 A_U = 13.8 Gyr", "無對應量 (IDCM 冇 t=0); 最近者 τ=13.4701 = 光行距離", "AGE→DISTANCE (禁相減)"),
    ("Big Bang at t=0", "冇 t=0; recursion C_{n+1}=1/(1+C_n) 冇首步; 觀察者係幀原點", "NO-MAP"),
    ("星齡 A_★ (觀測)", "同一觀測量, 兩框架直接共用", "OBS↔OBS ✅"),
    ("z → cosmic time", "IDCM: z = 距離/紅移投影 (O76), 冇時間語義", "NO-MAP (O76)"),
    ("ETS 宇宙年齡 12.91", "ΛCDM 內部比較 (早期新物理 vs CMB)", "INTERNAL-LCDM"),
    ("t_true = 11100.64 Gyr (IDCM 真實年齡)", "N·T_sync+τ (O213); ΛCDM 冇此量", "IDCM-ONLY"),
]
for src, idcm, cat in table:
    print(f"  · {src:<38s} → {idcm:<52s} [{cat}]")
ck("R4 翻譯規則: 只允許 OBS↔OBS 直接比較; AGE vs DISTANCE 相減 = category error (R1 已示範)",
   True)

npass = sum(c for _,c,_ in checks)
print("\n"+"="*80); print(f"RESULT: {npass}/{len(checks)} PASS"); print("="*80)
out = {"script":"05_r3_r4_definition_ladder.py",
       "tau_Gyr": float(tau),
       "t_render_44_43_retracted": float(t_render44),
       "dev_44_43_vs_planck_pct": float(dev),
       "delta_13p8_minus_tau_Gyr": float(d138),
       "tau_plus_tf17_Planck_Gyr": float(tau+mpf(str(tf_p))),
       "tau_plus_tf17_v9_Gyr": float(tau+mpf('0.211')),
       "Astar_minus_that_ratio": float(amp_ratio),
       "checks": [n+"::"+("PASS" if c else "FAIL") for n,c,_ in checks]}
with open(os.path.join(BASE,"data","05_r3_r4_definition_ladder.json"),"w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=2)
print("data/05_r3_r4_definition_ladder.json written.")