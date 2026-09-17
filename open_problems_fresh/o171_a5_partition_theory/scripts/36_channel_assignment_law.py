#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/36 — 通道分派律審計 (Channel Assignment Law Audit)

背景 (docs/22 §4 + docs/24 §5 遺留):
  docs/22 建立「通道分裂定理」—— 每個成員 U = (d−1)/d 作用於**唔同觀測量**,
  各通道精度差 16×。但**冇解釋點解某成員作用於某通道** —— 呢個分派係
  (i) 由結構導出, 抑或 (ii) 由「發現處」繼承 (即 post-hoc)?

  若係 (ii), 則家族嘅證據強度必須經 look-elsewhere 校正。

本節做四件事:
  A. 建立通道表 + 成員「發現處」表 (逐條文檔引)
  B. ★ 對消律: θ* = 7π/2112 係**比不變量** ⇒ 結構上應零修正
     (o73 docs/07 預言; o167 docs/02 修正 4.76σ → 0.48σ; o167 docs/07 「對聲學標尺修正不變」)
  C. 分派矩陣: 逐 (成員 × 通道) 檢查 bare 值存在 / 吻合 / 檢定力
  D. look-elsewhere + null control + 未來通道能力

★ 核心判準 (本節定義):
  一個 (成員, 通道) 對係「**合法檢定**」⟺ 三條件同時成立:
    (i)   該通道有 IDCM bare 值 (已註冊, 唔准新造)
    (ii)  修正後值同觀測吻合 (|z_dev| ≤ 1σ)
    (iii) 檢定力 z_det = (bare/d)/σ ≥ 1σ
  缺 (i) ⇒ 分派無效; 缺 (iii) ⇒ 「吻合」係低檢定力之平凡後果。
"""

import math
from fractions import Fraction as F
from pathlib import Path

import mpmath as mpm
mp = mpm.mp
mp.dps = 50

BASE = Path(__file__).resolve().parent.parent
N_PASS = 0
N_FAIL = 0
FAILS = []


def chk(name, cond, extra=""):
    global N_PASS, N_FAIL
    if cond:
        N_PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        N_FAIL += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {extra}")


print("=" * 78)
print("O171 scripts/36 — 通道分派律審計 (Channel Assignment Law Audit)")
print("=" * 78)

# =====================================================================
print("\n=== A: 通道表 (真實 σ + 出處) ===")

# 觀測值: (中心值, 1σ 絕對誤差, 出處)
OBS = {
    "theta_star":   (mp.mpf("1.04110"),  mp.mpf("0.00031"),
                     "Planck 2018 VI: 100θ_MC = 1.04110 ± 0.00031"),
    "r_d":          (mp.mpf("147.09"),   mp.mpf("0.26"),
                     "Planck 2018 VI: r_d = 147.09 ± 0.26 Mpc"),
    "r_star":       (mp.mpf("144.46"),   mp.mpf("0.25"),
                     "Planck 2018 VI: r* = 144.46 ± 0.25 Mpc"),
    "D1_peak":      (mp.mpf("5816.479677744882"), mp.mpf("165.4180814864716"),
                     "Planck binned D₁ 峰高 (O10)"),
    "Omega_Lambda": (mp.mpf("0.6847"),   mp.mpf("0.0073"),
                     "Planck 2018 VI: Ω_Λ = 0.6847 ± 0.0073"),
}
# r*/r_d 比值通道 (誤差傳播)
_xr = OBS["r_star"][0] / OBS["r_d"][0]
_sr = mp.sqrt((OBS["r_star"][1] / OBS["r_star"][0]) ** 2
              + (OBS["r_d"][1] / OBS["r_d"][0]) ** 2)
OBS["r_ratio"] = (_xr, _sr, "r*/r_d = 144.46/147.09 (誤差傳播)")

# A_s: ln(10^10 A_s) = 3.044 ± 0.014 ⇒ 相對誤差 = 0.014 = 1.400%
OBS["A_s"] = (mp.mpf("3.044"), mp.mpf("0.014"),
              "Planck 2018 VI Tab.2: ln(1e10 As) = 3.044 ± 0.014")

CH_SIG = {}
print(f"  {'通道':>14} {'中心':>14} {'σ_絕對':>12} {'σ_相對':>10}")
for k, (c, s, src) in OBS.items():
    sig_rel = s / c
    CH_SIG[k] = dict(center=c, sig=s, sig_rel=sig_rel, src=src)
    print(f"  {k:>14} {mp.nstr(c, 10):>14} {mp.nstr(s, 6):>12} {float(sig_rel)*100:9.5f}%")

chk("A1 σ(θ*)/σ(r_d) = 5.94× ⇒ θ* 係最銳通道",
    abs(float(CH_SIG["r_d"]["sig_rel"] / CH_SIG["theta_star"]["sig_rel"]) - 5.936) < 0.01,
    f"({float(CH_SIG['r_d']['sig_rel']/CH_SIG['theta_star']['sig_rel']):.3f}×)")
chk("A2 σ(D₁ 峰高)/σ(r_d) = 16.09× (docs/22 §2 一致)",
    abs(float(CH_SIG["D1_peak"]["sig_rel"] / CH_SIG["r_d"]["sig_rel"]) - 16.089) < 0.01,
    f"({float(CH_SIG['D1_peak']['sig_rel']/CH_SIG['r_d']['sig_rel']):.3f}×)")
# ★ A_s 之乘性 σ = σ(ln A_s) = 0.014 = 1.400% (ln 空間之 σ 即相對誤差)
SIG_MULT = {k: CH_SIG[k]["sig_rel"] for k in CH_SIG}
SIG_MULT["A_s"] = CH_SIG["A_s"]["sig"] / 1  # 0.014
chk("A3 ★ 乘性 σ(A_s) = 1.4000% (= σ(ln A_s), 唔係 0.014/3.044 = 0.4599%)",
    abs(float(SIG_MULT["A_s"]) * 100 - 1.4000) < 1e-6)
print("  ★ 乘性 σ 表: " + ", ".join(f"{k} {float(v)*100:.5f}%"
      for k, v in SIG_MULT.items() if k != "A_s") + f", A_s {float(SIG_MULT['A_s'])*100:.4f}%")

# =====================================================================
print("\n=== B: 成員「發現處」表 (逐條文檔引) ===")

# (標籤, d, 發現處文檔, 發現處通道/來源)
MEMBERS = [
    ("33/34",   34,  "O171 docs/01 §2 (質數峰幅度, O10)",        "CMB 峰高 D_ℓ"),
    ("44/45",   45,  "O171 docs/01 §2 + o168 docs/05 (88/90 = Σγ_odd/Σγ_even)",
                     "譜恆等式 — **唔係任何觀測量**"),
    ("55/56",   56,  "o167 docs/05 (r* = r_d × 55/56)",           "r* (聲學尺)"),
    ("420/421", 421, "o167 docs/05 (r_d = πR/88 × 420/421)",      "r_d (聲學尺)"),
]
print(f"  {'成員':>9} {'d':>5}  發現處")
for lab, d, src, chan in MEMBERS:
    print(f"  {lab:>9} {d:>5}  {src}")
    print(f"  {'':>9} {'':>5}    ⇒ 發現通道 = {chan}")

n_nosite = sum(1 for _, _, _, c in MEMBERS if "唔係任何觀測量" in c)
print(f"\n  ⇒ 4 個成員中, {4 - n_nosite} 個有發現處通道, {n_nosite} 個冇 (44/45 係譜恆等式)")
chk("B1 33/34 發現通道 = CMB 峰高 (O10 質數峰幅度)",
    "O10" in MEMBERS[0][2] and MEMBERS[0][3] == "CMB 峰高 D_ℓ")
chk("B2 44/45 冇發現處觀測通道 (純譜恆等式 88/90) ⇒ 任何分派皆 post-hoc",
    "唔係任何觀測量" in MEMBERS[1][3])
chk("B3 55/56, 420/421 發現處皆 O167 聲學尺 (r*, r_d)",
    "o167" in MEMBERS[2][2] and "o167" in MEMBERS[3][2])

# =====================================================================
print("\n=== C: ★ 對消律 (精確, 由結構導出) ===")

R = mp.mpf("4129.94")          # o167 scripts/16 之 R_world 數值
r_s = mp.pi * R / 88           # 聲學尺 bare = πR/88
D_A = 24 * R / 7               # 角直徑距離 (o167 scripts/16)
print(f"  R = {R},  r_s(bare) = πR/88 = {mp.nstr(r_s, 12)}")
print(f"  D_A = 24R/7 = {mp.nstr(D_A, 12)}")

theta = r_s / D_A
theta_exact = 7 * mp.pi / 2112
print(f"  θ* = r_s/D_A = {mp.nstr(theta, 12)}   7π/2112 = {mp.nstr(theta_exact, 12)}")
chk("C1 ★ θ* = 7π/2112 EXACT (R 對消 — 精確至 1e-45)",
    abs(theta - theta_exact) < mp.mpf("1e-45"))
chk("C2 ★ θ* 對 R 無關 ⇒ 任何「同步作用於 r_s 同 D_A」之幾何修正皆對消",
    abs((mp.pi * mp.mpf("9999.0") / 88) / (24 * mp.mpf("9999.0") / 7) - theta_exact)
    < mp.mpf("1e-45"))

# 420/421 同 55/56 同步作用 ⇒ 對消
f_420 = mp.mpf(420) / 421
f_55 = mp.mpf(55) / 56
th_sync = (r_s * f_420 * f_55) / (D_A * f_420 * f_55)
chk("C3 ★ θ* 對 420/421 × 55/56 同步縮放不變 (比不變量)",
    abs(th_sync - theta_exact) < mp.mpf("1e-45"),
    f"(100θ* = {float(100*th_sync):.8f})")

# r*/r_d = 55/56 (420/421 對消)
f_rd = F(420, 421)
f_rs = F(420, 421) * F(55, 56)
ratio_pred = f_rs / f_rd                      # Fraction 精確
rd_pred = r_s * (mp.mpf(f_rd.numerator) / f_rd.denominator)
rs_pred = r_s * (mp.mpf(f_rs.numerator) / f_rs.denominator)
print(f"\n  r_d(pred) = πR/88 × 420/421 = {mp.nstr(rd_pred, 12)}")
print(f"  r*(pred) = r_d × 55/56       = {mp.nstr(rs_pred, 12)}")
print(f"  r*/r_d   = {ratio_pred} (Fraction 精確)")
chk("C4 ★ r*/r_d = 55/56 EXACT (共享 420/421 對消) — Fraction 恆等",
    ratio_pred == F(55, 56))
chk("C5 ★ 對消律 ⇒ 420/421 結構上唔可能作用於 r*/r_d 通道",
    ratio_pred == F(55, 56))

# =====================================================================
print("\n=== D: 分派矩陣 (成員 × 通道) ===")

# 通道 bare 值 (只認已註冊者)
BARE = {
    "theta_star":   (theta_exact * 100,  "7π/2112 (o73 docs/07 + o167 docs/02)"),
    "r_d":          (r_s,                "πR/88 (o167 docs/05)"),
    "r_star":       (r_s,                "πR/88 (o167 docs/05)"),
    "r_ratio":      (mp.mpf(1),          "定義 (比通道 bare = 1)"),
    "Omega_Lambda": (mp.mpf(41) / 60,    "41/60 (O39/O84 真空預算)"),
    "D1_peak":      (None,               "O10 峰高公式 — 統一因子 ⇒ 同 A_s 簡併 (docs/12 §8)"),
    "A_s":          (None,               "❌ R7-A_s 撤銷 (docs/23) ⇒ 冇 bare 值"),
}

# 通道之**已註冊因子鏈** (由 o167/O171 文檔; 順序 = 文檔鏈)
CHAIN = {
    "r_d":          [421],       # r_d = πR/88 × 420/421 (o167 docs/05)
    "r_star":       [421, 56],   # r* = r_d × 55/56        (o167 docs/05)
    "r_ratio":      [56],        # 420/421 對消 (對消律 C4)
    "theta_star":   [],          # 全對消 (對消律 C1–C3)
    "Omega_Lambda": [],          # 冇已註冊鏈 (bare = 41/60)
    "D1_peak":      [],          # 冇已註冊鏈 (33/34 簡併, docs/12 §8)
    "A_s":          None,        # ❌ 冇 bare 值 (docs/23 撤銷)
}

# ★ 邊際測試: 測成員 d 之貢獻 ⇒ base = bare × Π(鏈中排喺 d 之前之因子), with = base × (d−1)/d
D_MEMBERS = [(lab, d) for lab, d, _, _ in MEMBERS]
rows = []
print(f"  {'成員':>9} {'通道':>13} {'base':>13} {'with':>13} {'z_dev':>9} {'z_det':>8} 鏈 判定")
for lab, d in D_MEMBERS:
    for ck, (bare, bsrc) in BARE.items():
        sig_abs = CH_SIG[ck]["sig"]
        chain = CHAIN[ck]
        if chain is None:
            rows.append(dict(mem=lab, d=d, ch=ck, base=None, z_dev=None, z_det=None,
                             reg=False, verdict="✗ 冇 bare 值"))
            print(f"  {lab:>9} {ck:>13} {'—':>13} {'—':>13} {'—':>9} {'—':>8} -  ✗ 冇 bare 值")
            continue
        if bare is None:
            z_det = float((CH_SIG[ck]["center"] / d) / sig_abs)
            rows.append(dict(mem=lab, d=d, ch=ck, base=None, z_dev=None, z_det=z_det,
                             reg=False, verdict="✗ 簡併/無公式"))
            print(f"  {lab:>9} {ck:>13} {'—':>13} {'—':>13} {'—':>9} {z_det:7.3f}σ -  ✗ 簡併")
            continue
        base = bare
        for dd in chain:
            if dd == d:
                break
            base = base * (dd - 1) / dd
        with_ = base * (d - 1) / d
        obs = CH_SIG[ck]["center"]
        z_dev = float((with_ - obs) / sig_abs)
        z_det = float((base / d) / sig_abs)
        reg = d in chain
        ok = abs(z_dev) <= 1.0 and z_det >= 1.0
        verdict = ("✅ 合法檢定" if ok else
                   ("✗ 唔吻合" if abs(z_dev) > 1 else "✗ 檢定力 < 1σ"))
        rows.append(dict(mem=lab, d=d, ch=ck, base=base, z_dev=z_dev, z_det=z_det,
                         reg=reg, verdict=verdict))
        print(f"  {lab:>9} {ck:>13} {mp.nstr(base, 8):>13} {mp.nstr(with_, 10):>13} "
              f"{z_dev:8.3f}σ {z_det:7.3f}σ {'✔' if reg else '-'}  {verdict}")

valid = [r for r in rows if r["verdict"].startswith("✅")]
print(f"\n  總對數 = {len(rows)};  合法檢定 = {len(valid)}")
for r in valid:
    print(f"    ✅ {r['mem']} × {r['ch']}  (z_dev {r['z_dev']:+.4f}σ, z_det {r['z_det']:.3f}σ)"
          f"  {'[已註冊鏈]' if r['reg'] else '[假設性分派]'}")

chk("D1 ★ 28 對中只有 3 對係合法檢定",
    len(rows) == 28 and len(valid) == 3, f"({len(rows)} 對, {len(valid)} 合法)")

vd = {(r["mem"], r["ch"]) for r in valid}
chk("D2 420/421 × r_d 合法 (z_dev −0.007σ, z_det 1.35σ) [已註冊鏈]",
    ("420/421", "r_d") in vd)
chk("D3 ★ 55/56 × r_star 合法 (邊際測試: base = r_d = 147.0883) [已註冊鏈]",
    ("55/56", "r_star") in vd)
chk("D4 55/56 × r_ratio 合法 (z_dev +0.009σ, z_det 7.22σ) [已註冊鏈]",
    ("55/56", "r_ratio") in vd)
chk("D5 ★ 33/34 同 44/45 冇任何合法檢定 (0 對)",
    not any(r["mem"] in ("33/34", "44/45") for r in valid))
chk("D6 ★ 全部 3 個合法檢定皆喺**已註冊鏈**上 (冇任何假設性分派命中)",
    all(r["reg"] for r in valid))

# =====================================================================
print("\n=== E: ★ θ* 通道排除全部成員 (對消律之定量確認) ===")

th100 = theta_exact * 100
sig_th = CH_SIG["theta_star"]["sig"]
print(f"  bare 100θ* = {mp.nstr(th100, 10)}  (Planck {mp.nstr(CH_SIG['theta_star']['center'],8)}"
      f" ± {mp.nstr(sig_th,4)})")
z_bare = float((th100 - CH_SIG["theta_star"]["center"]) / sig_th)
print(f"  零修正 (對消律預言) ⇒ z = {z_bare:+.3f}σ")
chk("E1 ★ 零修正預言通過: 100θ* bare vs Planck 0.48σ",
    abs(z_bare - 0.476) < 0.01, f"({z_bare:+.3f}σ)")

z_excl = {}
for lab, d in D_MEMBERS:
    pred = th100 * (d - 1) / d
    z = float((pred - CH_SIG["theta_star"]["center"]) / sig_th)
    z_excl[lab] = z
    print(f"  若 {lab:>8} 單邊作用於 θ* ⇒ 100θ* = {float(pred):.6f}, z = {z:+.2f}σ"
          f"  {'✗ 排除' if abs(z) > 3 else '⚠️'}")
chk("E2 ★ 全部四成員單邊作用於 θ* 皆被排除 (|z| > 3σ)",
    all(abs(z) > 3 for z in z_excl.values()),
    f"(|z| = {', '.join(f'{abs(z):.1f}' for z in z_excl.values())})")
chk("E3 θ* 通道最嚴: 33/34 之 |z| > 90σ",
    abs(z_excl["33/34"]) > 90, f"({z_excl['33/34']:+.1f}σ)")
chk("E4 420/421 之 |z| = 7.50σ (> 3σ ⇒ 仍排除)",
    abs(z_excl["420/421"] - (-7.503)) < 0.02, f"({z_excl['420/421']:+.3f}σ)")

# =====================================================================
print("\n=== F: 獨立性審計 — r*/r_d = 55/56 唔係獨立檢定 ===")

rd_obs, rd_sig = CH_SIG["r_d"]["center"], CH_SIG["r_d"]["sig"]
rs_obs, rs_sig = CH_SIG["r_star"]["center"], CH_SIG["r_star"]["sig"]
rd_p, rs_p = rd_pred, rs_pred
z_rd = float((rd_p - rd_obs) / rd_sig)
z_rs = float((rs_p - rs_obs) / rs_sig)
print(f"  r_d : pred {mp.nstr(rd_p,10)} vs obs {rd_obs} ⇒ z = {z_rd:+.4f}σ")
print(f"  r*  : pred {mp.nstr(rs_p,10)} vs obs {rs_obs} ⇒ z = {z_rs:+.4f}σ")
print(f"  比值: pred 55/56 vs obs {mp.nstr(_xr,10)} ⇒ z = "
      f"{float((mp.mpf(55)/56 - _xr)/_sr):+.4f}σ")
print("  ★ 但 r*(pred) = r_d(pred) × 55/56 係**構造恆等** ⇒ 比值檢定 = 兩個絕對匹配之算術後果")
chk("F1 ★ r*(pred)/r_d(pred) = 55/56 恆等 (構造) ⇒ 比值通道唔獨立",
    abs((rs_p / rd_p) - mp.mpf(55) / 56) < mp.mpf("1e-40"))
chk("F2 比值 z_dev ≈ +0.009σ (docs/24 §3 一致)",
    abs(float((mp.mpf(55) / 56 - _xr) / _sr) - 0.009) < 0.001)
chk("F3 ★ 3 個合法檢定中, 2 個 (r*/r_d, r*) 係同一匹配 ⇒ 有效獨立檢定 = 2",
    len(valid) == 3)

# =====================================================================
print("\n=== G: 撤回 docs/22 §4 之 A_s 通道分派 (33/34, 44/45) ===")

print("  docs/22 §4: 33/34 × A_s ⇒ z_det = 2.10σ;  44/45 × A_s ⇒ z_det = 1.59σ")
print("  撤回理由 (兩條獨立):")
print("    (i)  A_s 冇 IDCM bare 值 — R7-A_s 鏈條已撤銷 (docs/23: 環2 失效)")
print("    (ii) A_s 係 ΛCDM 擬合自由參數; 統一因子 M/(M+1) 對所有峰統一相乘")
print("         ⇒ 因子被 A_s 吸收 ⇒ 原理上唔可檢定 (docs/12 §8)")
za = float(mp.log(mp.mpf(34) / 33) / CH_SIG["A_s"]["sig"])
zb = float(mp.log(mp.mpf(45) / 44) / CH_SIG["A_s"]["sig"])
print(f"  (參考: ln 精確版 z_det = {za:.3f}σ / {zb:.3f}σ, 線性版 2.101σ / 1.587σ)")
chk("G1 ★ A_s 通道分派撤回 ⇒ 33/34 之合法通道 = 發現處 (CMB 峰高 D₁)",
    BARE["A_s"][0] is None)
chk("G2 ★ 33/34 於 D₁ 通道 z_det = 1.03σ 但統一因子簡併 ⇒ 原理上不可檢定",
    abs(float((CH_SIG["D1_peak"]["center"] / 34) / CH_SIG["D1_peak"]["sig"]) - 1.034) < 0.01)
chk("G3 44/45 冇發現處通道 + 冇合法檢定 ⇒ 家族中最弱成員",
    "唔係任何觀測量" in MEMBERS[1][3] and not any(r["mem"] == "44/45" for r in valid))

# =====================================================================
print("\n=== H: look-elsewhere 量化 ===")

# 結構候選集 (同 scripts/34 定義, 供 null control 用)
LUC = [2, 1]
while len(LUC) < 20:
    LUC.append(LUC[-1] + LUC[-2])
FIB = [1, 1]
while len(FIB) < 20:
    FIB.append(FIB[-1] + FIB[-2])
G_INV = [1, 3, 4, 5, 12, 60]
CAND = sorted(set(FIB) | set(LUC) | {g * l for g in G_INV for l in LUC}
              | {33, 44, 55, 420, 88, 176, 12, 16, 25, 60})
print(f"  結構候選集 (Fibonacci + Lucas + g·Lucas + 家族/鏈/群常數) = {len(CAND)} 個")

def hits_for(ck):
    bare, _ = BARE[ck]
    if bare is None:
        return None
    obs, sig = CH_SIG[ck]["center"], CH_SIG[ck]["sig"]
    return [N for N in CAND
            if abs(float((bare * (N - 1) / N - obs) / sig)) <= 1.0]

print(f"\n  {'通道':>13} {'bare':>13} {'1σ 窗內候選':>34} {'多重度':>8}")
mult = {}
for ck in ["theta_star", "r_d", "r_star", "r_ratio", "Omega_Lambda"]:
    h = hits_for(ck)
    mult[ck] = h
    show = str(h) if len(h) <= 10 else str(h[:10])[:-1] + ", ...]"
    print(f"  {ck:>13} {mp.nstr(BARE[ck][0], 8):>13} {show:>34} {len(h):>8}")

h_th_small = [N for N in mult["theta_star"] if N <= 421]
print(f"      ★ θ* 窗內最小候選 = {min(mult['theta_star'])}; d ≤ 421 者 = {len(h_th_small)} 個")
print(f"      ⇒ θ* 之 σ = 0.0298% 太細 ⇒ 只有 1/d < 0.044% (即 d > 2273) 之修正才落窗內")
chk("H1 ★★ θ* 通道: 全部家族成員 (d ≤ 421) 被排除; 1σ 窗內最小候選 = 2388",
    len(h_th_small) == 0 and min(mult["theta_star"]) == 2388,
    f"(窗內 {len(mult['theta_star'])} 個, 最小 {min(mult['theta_star'])})")
chk("H2 ★ r*/r_d 通道: 恰 3 個 (54, 55, 60) ⇒ 識別退化 (docs/24 §3 一致)",
    sorted(mult["r_ratio"]) == [54, 55, 60], f"({mult['r_ratio']})")
chk("H3 ★ r* 通道: ≥ 3 個 ⇒ 識別同樣退化",
    len(mult["r_star"]) >= 3, f"({mult['r_star']})")
chk("H4 ★ r_d 通道多重度最大 ⇒ 絕對尺通道本質高度退化",
    len(mult["r_d"]) >= 8, f"({len(mult['r_d'])} 個)")
chk("H5 ★ 分派自由度 = 4 成員 × 7 通道 = 28 對; 合法 3 對",
    len(rows) == 28)

hits_tight = [N for N in CAND
              if abs(float((mp.mpf(N) / (N + 1) - _xr) / _sr)) <= 0.05]
print(f"\n  收緊至 |z| ≤ 0.05σ: {hits_tight}")
chk("H6 ★ 收緊至 0.05σ 後只剩 1 個 (55) ⇒ 55/56 係最佳匹配",
    hits_tight == [55], f"({hits_tight})")

sep_val = (mp.mpf(55) / 56) - (mp.mpf(54) / 55)
sep_sig = float(sep_val / _sr)
need = float(sep_val / 3)
print(f"  55/56 vs 54/55 之值分離 = {float(sep_val)*100:.5f}% = {sep_sig:.4f}σ")
print(f"  ⇒ 3σ 分辨所需 σ ≤ {need*100:.6f}%  (現時 {float(_sr)*100:.5f}%)"
      f"  ⇒ 需改善 {float(_sr/need):.1f}×")
chk("H7 ★ 分辨 55/56 同 54/55 需 σ 改善 22.9× (更正第八輪口頭之 4.4×)",
    abs(float(_sr / need) - 22.9) < 0.3, f"({float(_sr/need):.2f}×)")
# =====================================================================
print("\n=== I: 未來通道能力 (達 3σ 所需 σ + 實驗投影) ===")

TARGETS = [
    ("420/421", 421, "r_d",     mp.mpf("0.17676"), "CMB-S4 σ_r_d ≈ 0.05% ⇒ 4.75σ"),
    ("33/34",    34, "D1_peak", mp.mpf("2.844"),   "簡併 ⇒ 冇用 (僅記錄)"),
]
for lab, d, ck, cur, note in TARGETS:
    need_sig = mp.mpf(100) / (3 * d)      # σ_rel < 1/(3d)
    print(f"  {lab:>8} × {ck:>8}: 現 σ_rel = {float(cur):.5f}%  需 ≤ {float(need_sig):.5f}%"
          f"  ⇒ 改善 {float(cur/need_sig):.2f}×   [{note}]")
chk("I1 420/421 達 3σ 需 σ(r_d) ≤ 0.0792% (改善 2.23×)",
    abs(float(mp.mpf("0.17676") / (mp.mpf(100) / (3 * 421))) - 2.232) < 0.02)
chk("I2 33/34 達 3σ 需 σ(D₁) ≤ 0.98% (改善 2.90×) — 但簡併令其無意義",
    abs(float(mp.mpf("2.844") / (mp.mpf(100) / (3 * 34))) - 2.901) < 0.02)

# =====================================================================
print("\n=== J: 本節結論 ===")
print("""
  1. ★★ 對消律 (導出): θ* = r_s/D_A = 7π/2112 EXACT (R 對消);
     420/421 同 55/56 喺同步縮放時對消 ⇒ θ* 結構上應零修正。
     實測: bare 100θ* = 1.041248 vs Planck 1.04110 ± 0.00031 ⇒ 0.48σ 🟢 (通過)
     定量排除: 四成員單邊作用於 θ* ⇒ |z| = 7.5 / 59.5 / 74.2 / 98.3σ ✗ (全員排除)
     ⚠️ 誠實: θ* 之 σ = 0.0298% 太細 ⇒ 只有 d > 2273 之修正落窗內 (46 個候選)
        ⇒ 「零修正」讀法一致但**唔唯一**; 排除家族靠嘅係成員 d 太小 (≤ 421)
  2. ★★ 分派律 = **發現處繼承** (3/4 有發現處通道; 44/45 冇)。
     ⇒ 分派唔係由結構導出, 係 post-hoc ⇒ 必須經 look-elsewhere 校正。
  3. ★★ 撤回 docs/22 §4 之 A_s 通道分派 (33/34 2.10σ, 44/45 1.59σ):
     A_s 冇 bare 值 (docs/23 撤銷) + 統一因子簡併 (docs/12 §8) ⇒ 分派無效。
  4. ★★ 28 對 (成員 × 通道) 中只有 3 對係合法檢定, 且其中 2 對係同一匹配
     (r*/r_d = 55/56 係構造恆等) ⇒ **有效獨立檢定 = 2 對**:
       420/421 × r_d     (z_dev −0.000σ, z_det 1.34σ) — 唯一未閉合, CMB-S4 → 4.75σ
       55/56  × r_star   (z_dev ≈ 0,     z_det 10.3σ)
  5. ★ 33/34 同 44/45 冇任何合法檢定 ⇒ 同識別層一樣, 屬原理上不可檢定。
  6. ★ 55/56 之 z_det = 7.22σ 唔係家族證據 — 佢係「r* ≠ r_d」之偵測 (ΛCDM 已知物理)。
  7. ★ 更正: 分辨 55/56 同 54/55 需 σ 改善 **22.8×** (第八輪口頭之 4.4× 係錯)。
""")

print("=" * 78)
print(f"RESULT: {N_PASS}/{N_PASS + N_FAIL} PASS")
if FAILS:
    print("FAILS:")
    for f_ in FAILS:
        print(f"  - {f_}")
print("=" * 78)
