#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O232 — scripts/06: 銀河系三星齡問題 (Q1/Q3) — 候選星 vs ΛCDM 天花板
====================================================================
Q1: 銀河系係咪「年輕星系」所以星齡唔過？
Q3: 有冇恆星超過 138 億歲（紅矮星/白矮星）？
全部候選 = 文獻引用值 (只引用, 不重推)。天花板 = A_U = 13.787 Gyr (Planck 2018, 外部)。
判據: |age − A_U| / σ ≥ 3 ⟹ 穩健超齡 (會殺 ΛCDM t=0); < 1σ ⟹ 相容。
"""
import json, os
from mpmath import mp, mpf, nstr

mp.dps = 20
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AU = mpf('13.787')          # Planck 2018 (外部)
MAX_PLAUSIBLE = mpf('13.705')  # Banik+2026 操作天花板: A−5σ > 13.705 (t_f=0.1 最小形成延遲)

print("="*88)
print("O232 / 06 — 銀河系三星齡問題: 候選星 vs ΛCDM t=0 天花板 A_U = 13.787 Gyr")
print("="*88)

# (名稱, 類型, 年齡 Gyr, σ Gyr, 文獻)
cands = [
    ("HD 140283 (Methuselah)", "暈次巨星(Subgiant)", 14.46, 0.80, "Bond+2013 HST 視差 (名義值)"),
    ("HD 140283 (現代複審)",   "暈次巨星(Subgiant)", 13.90, 0.70, "VandenBerg+2013 等時線+Gaia 後收窄 (綜合)"),
    ("NGC 6752 WD 冷卻序列",   "球狀星團白矮星",     13.10, 0.40, "Bedin+2022 MNRAS (12.7–13.5 峰值)"),
    ("M4 WD 冷卻序列",         "球狀星團白矮星",     12.10, 0.90, "Hansen+2004"),
    ("NGC 6397 WD 冷卻序列",   "球狀星團白矮星",     11.50, 1.00, "Hansen+2007 (≈11.5–13)"),
    ("BPS CS 22876−32",        "特低金屬主序星",     13.60, 0.60, "Ruchti+2013 (綜合)"),
    ("Banik+2026 A_★ (樣本最老)", "155,600 次巨星 latent max", 13.73, 0.165, "由 (13.73,+0.18/−0.15) 取平均σ"),
]
print(f"\n{'候選':<28s} {'類型':<22s} {'age':>6s} {'±σ':>5s} {'Δ(AU−age)':>10s} {'σ 距離':>7s} 判決")
print("-"*88)
results = []
for name, typ, age, sig, ref in cands:
    d = float(mpf(str(age)) - AU)
    nsig = d/sig
    if abs(nsig) < 1.0:   verdict = "相容 (≤1σ)"
    elif abs(nsig) < 3.0: verdict = "⚠️ 邊緣 (1–3σ)"
    else:                 verdict = "🔴 穩健超齡 (>3σ)"
    results.append({"name": name, "type": typ, "age_Gyr": age, "sigma": sig,
                    "delta_vs_AU": d, "nsig": nsig, "verdict": verdict, "ref": ref})
    print(f"{name:<28s} {typ:<22s} {age:>6.2f} {sig:>5.2f} {d:>+10.3f} {nsig:>+7.2f}  {verdict}")
print("-"*88)
print(f"Banik+2026 操作天花板: A − 5σ > {MAX_PLAUSIBLE} Gyr (t_f = 0.1 Gyr) — 樣本內 228 星被其視為 0.1% 量測偽影")

# ---- 紅矮星 (Q3) ----
print("\n[Q3·紅矮星] 主序壽命 vs 宇宙齡 (零參數事實, 引用恆星演化)")
tMS = {"0.1 M☉": 1.0e4, "0.3 M☉": 1.0e3, "0.5 M☉": 2.0e2, "0.8 M☉": 2.0e1}  # Gyr 量級
for m, t in tMS.items():
    print(f"  M={m}: 主序壽命 ≈ {t:>6.0f} Gyr ≫ 13.787 Gyr ⟹ 宇宙內所有呢類星都『未死』, "
          f"但冇一粒可以 > 13.787 (t=0 令形成時間 ≥ 0)")
print("  ⟹ 紅矮星唔會「超過 138 億歲」: 佢哋係『長命』, 唔係『老過宇宙』")
print("  ⟹ 最老紅矮星 (暈星) 年齡 ≈ 13.5–13.7 Gyr (同最老次巨星同源), 全喺天花板內")

# ---- 判決 ----
print("\n[判決]")
n_robust = sum(1 for r in results if r["verdict"].startswith("🔴"))
print(f"  穩健超齡候選: {n_robust}/{len(results)}")
print(f"  最接近天花板: HD 140283 名義 14.46±0.8 → +0.84σ (2013); 現代複審 13.9±0.7 → +0.16σ")
print("  🟢 Q3 數據側: 冇一粒恆星被穩健證實超過 13.787 Gyr; 全部候選喺誤差帶內相容 ΛCDM t=0")
print("  🟢 Q1 數據側: 銀河暈/球狀星團屬『宇宙最老成員』(13.5–13.7), 唔係『年輕星系』;")
print("     但『恆星 ≤ 宇宙齡』喺 ΛCDM 係普遍約束, 同星系年輕/年老無關")
checks_note = "全部候選 = 文獻引用, 冇新閉合; 零參數 — 判據只有 σ 距離"
print(f"  ⚠️ {checks_note}")
print("="*88); print("RESULT: 0 robust violations / table complete (literature-cited)"); print("="*88)

out = {"script": "06_stellar_age_ceiling_candidates.py",
       "AU_Planck_Gyr": float(AU), "max_plausible_Banik": float(MAX_PLAUSIBLE),
       "candidates": results,
       "red_dwarf_lifetimes_Gyr": tMS,
       "conclusion": "no star robustly exceeds 13.787 Gyr; all consistent within uncertainties",
       "disclaimer": checks_note}
with open(os.path.join(BASE, "data", "06_stellar_age_candidates.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print("data/06_stellar_age_candidates.json written.")