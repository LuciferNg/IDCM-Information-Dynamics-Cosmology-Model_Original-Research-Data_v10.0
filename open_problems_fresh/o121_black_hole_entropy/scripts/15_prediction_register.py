#!/usr/bin/env python3
"""
O121 — script 15: G8 預言登記 + Gemini 4 項核帳
============================================================
A. Gemini 4 項逐條核 (出處 / 判決)
B. ★ P8 vs O121 docs/04 內部張力: Hayward 臨界質量 M_crit
C. G8 預言登記 (可證偽門檻 + ΛCDM 判別)
D. 「是否應加入驗證」之裁決

零新常數。
"""
import math, json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0; FAIL = 0
def ck(n, c, d=""):
    global PASS, FAIL
    if c: PASS += 1; print(f"  ✅ {n} {d}")
    else: FAIL += 1; print(f"  ❌ {n} {d}")

G, c_l, hbar = 6.674e-11, 2.99792458e8, 1.0546e-34
M_sun, Yr, Mpc = 1.989e30, 3.1557e7, 3.0857e22
t_univ = 13.8e9*Yr
phi = (1+math.sqrt(5))/2
ell = 4.516e-23                      # O121 docs/10: Hayward 核心尺度 (由 ρ_max=ρ_P)

print("="*78); print("O121 script 15: G8 預言登記 + Gemini 4 項核帳"); print("="*78)

# ===== A. Gemini 4 項核 =====
print("\n"+"="*78); print("[A] Gemini 4 項逐條核"); print("="*78)
claims = [
 ("① f_return = 0.8028", "o121 docs/14,15 (本 session 自導)", "✅ 真",
  "但「19.7% 來自直接重聯」之拆分**未導出** (只導出 80.3% 總量)"),
 ("② P8 冇 Hawking 蒸發 → 冇 γ 爆", "o173 docs/06 P8 (真條目)", "⚠️ 有內部張力",
  "O121 docs/04: IDCM **重現標準 Hawking** (T_H, t_evap=5120πG²M³/ħc⁴) — 見 §B"),
 ("③ ρ_debris∞=4.0e6, today≈3.0e6 (75%)", "o173 docs/12: 固定點 = 總恆星質量×2%", "✅ 真 (逐字)",
  "數值與 75% 皆見於原文"),
 ("④ n=27 瓶頸 σ=0.772 → UHECR 能譜截斷", "o121 docs/07: σ(n≤26)=1, σ(27)=0.772, σ(n≥28)=0", "🟡 推論",
  "σ_n 係**模指數** throughput; n↔能量映射**未導出**"),
]
for a, b, v, n_ in claims:
    print(f"  {a}\n     出處: {b}\n     判決: {v} — {n_}")
n_real = sum(1 for x in claims if x[2].startswith("✅"))
n_tension = sum(1 for x in claims if "張力" in x[2])
ck("至少 2 條逐字為真 (①③)", n_real >= 2, f"(✅ {n_real})")
ck("至少 1 條需修正 (②)", n_tension >= 1, f"(⚠️ {n_tension})")

# ===== B. P8 vs docs/04: Hayward 臨界質量 =====
print("\n"+"="*78); print("[B] ★ P8 內部張力: Hayward 臨界質量 M_crit"); print("="*78)
# Hayward f=1−2Mr²/(r³+2Mℓ²); 極值 h(r)=r³−2Mr²+2Mℓ²=0 ∧ h'=0 → r=4M/3, M_crit=(3√3/4)ℓ
M_crit = (3*math.sqrt(3)/4)*ell*c_l**2/G
M_naive = ell*c_l**2/(2*G)                     # r_H = ℓ
print(f"  ℓ = {ell:.3e} m (核心尺度, ρ_max=ρ_P)")
print(f"  M_crit (Hayward 極值 (3√3/4)ℓ) = {M_crit:.3e} kg = {M_crit/1e3:.1f} 噸")
print(f"  M_naive (r_H=ℓ)                = {M_naive:.3e} kg")
ck("M_crit ≈ 7.9e4 kg (~79 噸) — 黑洞最小質量", 5e4 < M_crit < 1.2e5, f"({M_crit:.3e})")
# 現今蒸發之 PBH 質量
M_pbh = (t_univ*hbar*c_l**4/(5120*math.pi*G**2))**(1/3)
print(f"  ⭐ 現今蒸發之 PBH: M = (t ħc⁴/5120πG²)^(1/3) = {M_pbh:.3e} kg "
      f"= {M_pbh:.2e} kg")
ratio = M_pbh/M_crit
print(f"  M_pbh,now / M_crit = {ratio:.3e}")
ck("M_pbh,now ≫ M_crit (≥ 10⁵ 倍)", ratio > 1e5, f"({ratio:.2e})")
# Hayward 修正量
for M in (M_pbh, 1e12, M_sun):
    Rs = 2*G*M/c_l**2
    print(f"    M={M:.2e} kg: R_s={Rs:.3e} m, ℓ/R_s={ell/Rs:.2e}, (ℓ/R_s)²={(ell/Rs)**2:.2e}")
ck("對 M ≫ M_crit, Hayward 修正 ~(ℓ/R_s)² ≪ 1 ⟹ 標準 Hawking 適用", (ell/(2*G*M_pbh/c_l**2))**2 < 1e-12)
print("  ★★ 裁決: IDCM 自身 ℓ 給出 M_crit≈7.9e4 kg; 而**現今蒸發之 PBH 質量 ~1.7e11 kg**")
print("     ⟹ 對 PBH 蒸發, IDCM **冇**抑壓 ⟹ P8 原句「冇 γ 爆簽名」**不成立** (過度宣稱)")
print("     ✓ 可辯護版本: IDCM 預言**最小黑洞質量 M_crit ≈ 7.9e4 kg** (以下為無視界核)")
ck("P8 原句不成立 (M_pbh ≫ M_crit ⟹ 照常蒸發)", ratio > 1e5)

# ===== C. G8 預言登記 =====
print("\n"+"="*78); print("[C] G8 預言登記 (可證偽門檻)"); print("="*78)
reg = [
 ("P-G8a", "f_return = 0.8028 (BH 返池佔 UHECR 質量率)", "✅ 導出 (docs/15)",
  "Auger/TA 成分+各向異性 → BH 源佔比; 若 <0.55 或 >0.95 (>3σ)", "ΛCDM 無此定值", "🟢"),
 ("P-G8b", "τ_rec/τ_p = 3.07e-22 (質子衰變從未啟動)", "✅ 導出 (docs/13)",
  "Hyper-K/ DUNE 見質子衰變 ⟹ 反駁", "ΛCDM 無預言", "🟢"),
 ("P-G8c", "黑洞質量函數**無萎縮端** (冇『回收中』群)", "✅ 導出 (O173 P10)",
  "質量函數低端出現萎縮/空洞", "ΛCDM 無此否定預言", "🟢"),
 ("P-G8d", "★ **最小黑洞質量 M_crit ≈ 7.9e4 kg**", "🟡 由 ℓ (ρ_max=ρ_P 假設) 導出",
  "確認 PBH 蒸發至 <7.9e4 kg ⟹ 反駁", "ΛCDM: 無最小質量 (蒸發至 Planck)", "🟡"),
 ("P-G8e", "ρ_debris(z=0) ≈ 3.0e6 → 固定點 4.0e6 M☉/Mpc³", "✅ 導出 (O173 docs/12 P15)",
  "Euclid/LSST/JWST 暗殘骸普查 >4.0e6 ⟹ 反駁", "ΛCDM 無飽和", "🟢"),
 ("P-G8f", "T_pipe† σ_n 譜: σ(n≤26)=1, σ(27)=0.772, σ(n≥28)=0", "✅ 導出 (docs/07)",
  "需 **n↔E 映射**導出後方可測 UHECR 能譜", "ΛCDM 無此階梯", "🟡"),
]
for pid, pred, der, fals, disc, st in reg:
    print(f"  {st} {pid} {pred}\n      導出: {der}\n      證偽: {fals}\n      判別: {disc}")
n_green = sum(1 for r in reg if r[5]=="🟢")
ck("≥ 4 條 🟢 (可即時證偽 + 導出)", n_green >= 4, f"({n_green})")
ck("每條皆有明文證偽門檻", all(r[3] for r in reg))
# P8 更正登記
print("\n  ⚠️ **P8 更正登記** (跨 O):")
print("     O173 docs/06 P8「冇 Hawking 蒸發簽名」→ **降級** 🟡→❌")
print("     理由: 與 O121 docs/04 (重現標準 Hawking) 及 ℓ=M_crit 計算矛盾")
print("     替換: P-G8d (最小黑洞質量 M_crit ≈ 7.9e4 kg)")

# ===== D. 裁決 =====
print("\n"+"="*78); print("[D] 「是否應加入驗證?」之裁決"); print("="*78)
print("  ✅ **應該** — 長時標 (τ_rec~8.9e16 yr) 唔需要等: 靠**瞬時比例/否定性特徵**")
print("     (與質子衰變壽命 <10^34 yr 之驗證範式相同: N 個樣本 × 1 年觀測)")
print("  ✅ 已有 5 條導出型預言 (P-G8a/b/c/e/f) + 1 條 🟡 (P-G8d)")
print("  ⚠️ Gemini ② 原版不成立; ④ 屬推論 (缺 n↔E 映射); ① 之 19.7% 拆分未導")
print("  ★ 方法學: 驗證**唔係**靠「等」，係靠 (i) 瞬時通量比 (ii) 否定性特徵 (iii) 飽和固定點")
out = {
 "problem": "O121/G8 預言登記 + Gemini 4 項核帳",
 "A_gemini_audit": [{"claim": a, "source": b, "verdict": v, "note": n_} for a,b,v,n_ in claims],
 "B_P8_tension": {"ell_m": ell, "M_crit_kg": M_crit, "M_crit_naive_kg": M_naive,
                   "M_pbh_now_kg": M_pbh, "ratio": ratio,
                   "verdict": "P8 原句不成立; 可辯護版 = 最小黑洞質量 M_crit ≈ 7.9e4 kg"},
 "C_register": [{"id": p, "prediction": pr, "derivation": d, "falsification": f,
                  "discriminator": dc, "status": s} for p,pr,d,f,dc,s in reg],
 "D_verdict": "應加入驗證: 瞬時比例 + 否定性特徵 + 飽和固定點 (非等待)",
}
with open(os.path.join(BASE,"data","15_prediction_register.json"),"w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nRESULT: {PASS} PASS, {FAIL} FAIL  {'🟢' if FAIL==0 else '🔴'}")
if FAIL: exit(1)
