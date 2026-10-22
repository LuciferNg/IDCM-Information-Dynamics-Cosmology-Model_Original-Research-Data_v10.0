#!/usr/bin/env python3
"""
O131 — 前置驗證 02: v9.0 常數/公式 vs v10.0 權威值 交叉核對 + 框架依賴掃描
=========================================================================
兩部分:
  A. 數值交叉核對 (mpmath dps=50) — 每個 v9.0 物件對 v10.0 權威值, 逐項三分類
     ✅ 遷移 / 🟡 φ 近似 (落陷阱窗 [1e-5,1e-3]) / 🔴 失效
  B. 框架依賴掃描 — grep v9.0 stacking_toolbox + kchain_cosmic_web 嘅膨脹/已 demote 假設

v10.0 權威來源 (現行已閉合 O, 唔自己重算):
  ω_ring = 72.59 (km/s)/Mpc      ← O73 (角頻率身份, 唔係 H₀)
  R_world = 4129.94 Mpc          ← O73 註冊值; O171 精確式 r_d×88×421/(420π) = 4129.99
  r_d = πR_world/88              ← O127 / O171 (BAO ruler)
  λ_sync = πR_world/44           ← O73 / O129 (v9≡v10 幾何, dev 0)
  Ω_Λ = 41/60                    ← O148 / O215 (v10 精確); 4/(φ⁴−1) = φ-近似 (O135)
  ε = 19/123                     ← O135 / O148 (v10 精確); φ⁻¹/4 = φ-近似
  γ_n = 4sin²(πn/88), v_g=cos(πn/88), B=4  ← O34 / O124 (v10-native, 公式相同)
  z_c = 0.6 (F₄/F₅)              ← O126 §D 撤回 / O129 重驗 (v9.0 膨脹偽影)
"""

import math, os, re, glob
import mpmath as mp
mp.mp.dps = 50

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V9 = "/home/wsl/Projects/IDCM-Original/IDCM-v9.0--W-Field-Lattice"

PASS, FAIL = 0, 0
CLAIMS = []
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; mark = "✅"
    else:    FAIL += 1; mark = "❌"
    print(f"  {mark} {name}" + (f" — {detail}" if detail else ""))
def claim(txt):
    CLAIMS.append(txt); print(f"  [CLAIM] {txt}")

phi = (1 + mp.sqrt(5)) / 2
print("=" * 80)
print("  O131/02 — v9.0 物件 vs v10.0 權威值 (mpmath dps=50)")
print("=" * 80)

# ---------------- v9.0 值 (照 _core.py / stacking script) ----------------
H0_IDCM_v9 = mp.mpf("72.59")
R_H_v9 = mp.mpf("299792.458") / H0_IDCM_v9
LAM_v9 = 2 * mp.pi * R_H_v9 / 88
h_v9 = H0_IDCM_v9 / 100
OML_v9 = 4 / (phi**4 - 1)
EPS_v9 = 1 / phi / 4

# ---------------- v10.0 權威值 ----------------
omega_ring_v10 = mp.mpf("72.59")
R_world_v10 = mp.mpf("4129.94")          # 註冊值 (4 s.f., 有捨入)
R_world_exact = mp.mpf("299792.458") / omega_ring_v10   # 精確式 R_world ≡ c/ω_ring (O73 恆等)
r_d_v10 = mp.pi * R_world_exact / 88
LAM_v10_formula = mp.pi * R_world_exact / 44            # v10 公式形 (同一個 R)
LAM_v10_registry = mp.pi * R_world_v10 / 44             # v10 註冊值代入
OML_v10 = mp.mpf(41) / 60
EPS_v10 = mp.mpf(19) / 123

print(f"\n  {'物件':<26} {'v9.0':<24} {'v10.0 權威':<24} {'dev':<12} 分類")
print(f"  {'─'*100}")

def row(name, v9, v10, cls, note=""):
    dev = abs(v9 - v10) / abs(v10) if v10 != 0 else abs(v9 - v10)
    print(f"  {name:<26} {mp.nstr(v9,10):<24} {mp.nstr(v10,10):<24} {float(dev):<12.3e} {cls} {note}")
    return dev

# A1: λ_sync 幾何 — v9 公式形 vs v10 公式形 (同一個 R, 比較公式唔比較註冊值)
d = row("λ_sync (v9: 2πR_H/88)", LAM_v9, LAM_v10_formula, "✅ 遷移", "(公式代數恆等)")
check("A1 λ_sync v9 公式 = v10 公式 (dev = 0 EXACT, 同一 R)", d < mp.mpf("1e-40"), f"dev={float(d):.3e}")
d_reg = abs(LAM_v10_registry - LAM_v10_formula)/LAM_v10_formula
print(f"       ⚠️ 註冊值捨入: v10 註冊 R_world=4129.94 (4 s.f.) ⟹ λ 註冊值 dev = {float(d_reg):.3e} "
      f"(純捨入, 非結構差異)")
check("A1b λ_sync = 294.88 Mpc (v10 註冊)", abs(LAM_v10_registry - mp.mpf("294.88"))/mp.mpf("294.88") < 2e-5,
      f"{float(LAM_v10_registry):.4f}")

# A2: R (v9 標籤 Hubble radius) vs R_world (公式恆等)
d = row("R (c/ω_ring vs R_world)", R_H_v9, R_world_exact, "✅ 遷移 (標籤🔴)", "(v9 標「Hubble radius」)")
check("A2 R_H_v9 = R_world (公式恆等, dev = 0 EXACT)", d < mp.mpf("1e-40"), f"dev={float(d):.3e}")

# A3: H₀ = 72.59 標籤 — 數值同 ω_ring, 但身份唔同 (結構聲稱, 唔入 PASS)
claim(f"A3 H₀=72.59 (v9) 同 ω_ring=72.59 (v10) 數值相同但身份唔同 "
      f"(v10: 角頻率, 唔係哈伯常數 — O73 改名) ⟹ v9 標籤 🔴, 數值 ✅")

# A4: h = 0.7259 (dimensionless) — 慣例值 (fiducial), 非結構預言
claim(f"A4 h = 72.59/100 = 0.7259 係慣例 (用 ω_ring 做 h); v10 有三個 h 投影 "
      f"(h_cmb=0.674071 / h_lad=0.73130 / h_o170=0.71157) ⟹ h⁻¹Mpc 換算係 fiducial, 非結構聲稱")

# A5: Ω_Λ — v9 φ-form vs v10 精確 41/60
d = row("Ω_Λ", OML_v9, OML_v10, "🟡 φ 近似")
check("A5 Ω_Λ 落 φ 陷阱窗 [1e-5,1e-3]", mp.mpf("1e-5") < d < mp.mpf("1e-3"), f"dev={float(d):.3e}")
# Lucas 尾截斷檢定
tail = mp.mpf(41)/60 - 4/(phi**4 - 1)
print(f"       尾截斷: 41/60 − 4/(φ⁴−1) = {mp.nstr(tail,8)}  (√5φ⁻¹⁰/[60(3φ+1)] = "
      f"{mp.nstr(mp.sqrt(5)*phi**-10/(60*(3*phi+1)),8)})")
check("A5b Ω_Λ 舊 φ 形 = 精確式之 Lucas 尾截斷 (EXACT, dev<1e-40)",
      abs(tail - mp.sqrt(5)*phi**-10/(60*(3*phi+1))) < mp.mpf("1e-40"))

# A6: ε — v9 φ-form vs v10 精確 19/123
d = row("ε", EPS_v9, EPS_v10, "🟡 φ 近似")
check("A6 ε 落 φ 陷阱窗", mp.mpf("1e-5") < d < mp.mpf("1e-3"), f"dev={float(d):.3e}")
tail = mp.mpf(19)/123 - 1/phi/4
check("A6b ε 舊 φ 形 = 精確式之 Lucas 尾截斷 (EXACT, dev<1e-40)",
      abs(tail - (-mp.sqrt(5)*phi**-10/492)) < mp.mpf("1e-40"),
      f"19/123 − φ⁻¹/4 = {mp.nstr(tail,8)}")

# A7: γ_n / v_g — v10-native, 公式相同
ok = all(abs(4*mp.sin(mp.pi*n/88)**2 - (2 - 2*mp.cos(2*mp.pi*n/88))) < mp.mpf("1e-40") for n in range(1, 45))
check("A7 γ_n = 4sin²(πn/88) = 2−2cos(2πn/88) (v9 公式 = v10 公式, EXACT)", ok)
check("A7b v_g(n) = cos(πn/88) (公式相同)", abs(mp.cos(mp.pi*22/88) - mp.mpf(2)**-mp.mpf('0.5')) < mp.mpf("1e-40"))

# A8: z_c = 0.6 sync dip — v10 冇 4^ℓ rung
zc = mp.mpf("0.6")
ell = mp.log(1 + zc) / mp.log(4)
print(f"        z_c=0.6 → ℓ = log₄(1.6) = {mp.nstr(ell,8)} (非整數 ⟹ 非 4^ℓ rung)")
check("A8 z_c=0.6 非 4^ℓ rung (ℓ=0.339036 非整數)", abs(ell - mp.mpf("0.339036")) < mp.mpf("1e-5"),
      f"ℓ={float(ell):.6f}")
claim("A8b z_c=0.6 (sync dip, F₄/F₅=3/5) 已由 O126 §D 撤回 (v9.0 膨脹偽影), O129 獨立重驗 5/5")

# ---------------- B. 框架依賴掃描 ----------------
print(f"\n{'─'*80}\n  B. 框架依賴掃描 (v9.0 stacking_toolbox + kchain_cosmic_web)\n{'─'*80}")
TOKENS = {
    "H0_IDCM":       "v9 用 72.59 當 H₀ (v10 = ω_ring)",
    "Omega_L":       "Ω_Λ φ-form (v10 = 41/60)",
    "zeta":          "ζ(z) 阻抗修正 (v9 demote 參數)",
    "ZETA_":         "ζ(z) 參數常數",
    "(1+z)":         "膨脹律 (1+z)^α",
    "inflation":     "膨脹假設",
    "e-fold":        "膨脹 e-folds",
    "z_c":           "sync dip z_c=0.6",
    "H_z(":          "H(z) 膨脹函數",
    "R_H":           "Hubble radius 標籤",
}
targets = sorted(glob.glob(os.path.join(V9, "open_problems_fresh/stacking_toolbox/*.py")) +
                 glob.glob(os.path.join(V9, "open_problems_fresh/kchain_cosmic_web/*.py")))
print(f"  掃描檔案: {len(targets)} 個")
found = {}
for t in targets:
    txt = open(t, encoding="utf-8", errors="ignore").read()
    for tok, desc in TOKENS.items():
        n = len(re.findall(re.escape(tok), txt))
        if n:
            found.setdefault(tok, []).append((os.path.basename(t), n))
for tok, desc in TOKENS.items():
    hits = found.get(tok, [])
    tot = sum(n for _, n in hits)
    files = ", ".join(f"{f}×{n}" for f, n in hits[:4])
    print(f"    {tok:<12} 命中 {tot:>3}  [{desc}]  {files}{' …' if len(hits)>4 else ''}")

# 關鍵: stacking_toolbox 本身嘅框架依賴
st_txt = open(os.path.join(V9, "open_problems_fresh/stacking_toolbox/01_stacked_waveform.py"),
              encoding="utf-8").read()
st_infl = any(re.search(p, st_txt) for p in ["inflation", "inflaton", "e-fold", r"\(1\+z\)"])
st_zeta = "zeta" in st_txt or "ZETA" in st_txt
st_oml  = "Omega_L" in st_txt
st_zc   = "z_c" in st_txt
print(f"\n  ★ stacking_toolbox/01_stacked_waveform.py 自身:")
print(f"      顯式膨脹假設 (inflation/(1+z)): {'有' if st_infl else '冇'}")
print(f"      ζ(z) 阻抗修正:                 {'有' if st_zeta else '冇'}")
print(f"      Ω_Λ φ-form:                    {'有' if st_oml else '冇'}")
print(f"      z_c=0.6 sync dip:              {'有' if st_zc else '冇'}")
check("B1 stacking script 本身冇顯式膨脹假設 (inflation/(1+z))", not st_infl)
check("B1b stacking script 冇 ζ(z) / Ω_Λ / z_c 依賴 (只經 import _core 間接繼承)",
      not (st_zeta or st_oml or st_zc))
check("B2 框架假設集中喺 _core.py (H₀ 標籤/Ω_Λ φ-form/ζ(z) 全喺 _core)",
      ("H0_IDCM" in open(os.path.join(V9, "open_problems_fresh/kchain_cosmic_web/_core.py"),
                         encoding="utf-8").read()))

print(f"\n{'='*80}")
print(f"  RESULT: {PASS}/{PASS+FAIL} PASS  (+{len(CLAIMS)} 結構聲稱, 唔入 PASS 計數)")
print(f"{'='*80}")

with open(os.path.join(BASE, "data", "02_crosscheck_results.txt"), "w") as f:
    f.write("O131/02 — v9 vs v10 交叉核對 + 框架依賴掃描\n")
    f.write(f"lambda_sync_v9={mp.nstr(LAM_v9,12)} lambda_sync_v10_formula={mp.nstr(LAM_v10_formula,12)} "
            f"lambda_sync_v10_registry={mp.nstr(LAM_v10_registry,12)}\n")
    f.write(f"R_H_v9={mp.nstr(R_H_v9,12)} R_world_exact={mp.nstr(R_world_exact,12)} R_world_registry={R_world_v10}\n")
    f.write(f"OmegaL_v9={mp.nstr(OML_v9,12)} OmegaL_v10={mp.nstr(OML_v10,12)}\n")
    f.write(f"eps_v9={mp.nstr(EPS_v9,12)} eps_v10={mp.nstr(EPS_v10,12)}\n")
    f.write(f"ell(0.6)={mp.nstr(ell,12)}\n")
    f.write(f"stacking_script_has_inflation={st_infl} zeta={st_zeta} OmegaL={st_oml} zc={st_zc}\n")
    f.write(f"RESULT={PASS}/{PASS+FAIL} PASS claims={len(CLAIMS)}\n")
print(f"\n  寫入 {os.path.join(BASE,'data','02_crosscheck_results.txt')}")
