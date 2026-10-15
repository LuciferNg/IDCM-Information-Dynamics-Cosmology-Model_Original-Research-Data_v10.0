#!/usr/bin/env python3
"""
O168 — 23: η_B 結構形式審計 (修正版 v3: 權威錨 O5-3 判定)
======================================================
v1 (09-11): 錨 η_B = 6.062e-10 (BBN) — 係 O37×P_n 雙重 stale (O169 09-15 判定)
v2 (09-15): 改錨 6.063632e-10 (O169 v10.0 鏈) — 但該鏈用 Ω_b = 19/450,
            O73 O5-1 判定 (09-23) 以 17.6σ/14.5σ 排除 19/450 家族!
v3 (10-15): 權威錨 = η_B(IDCM) = 6.2116e-10 (p1_bbn/O5-3), Planck 6.1163e-10
本版對權威錨重測 (4/5)e⁻²¹ → 誠實裁決 (否定)。
"""
from mpmath import mp, mpf, exp, ln, sqrt, pi
mp.dps = 50

phi = (1 + sqrt(5))/2
B = 4; F5 = 5; N_gen = 3; L4 = 7; F_proj = 17; mu2 = 2

# 權威錨 (p1_bbn/09_summary + O73 O5-1/O5-3, 2026-09-23)
etaB_idcm   = mpf('6.2116e-10')    # IDCM 權威 (Ω_b = 1/20 鏈, +1.558% = 2.32σ)
etaB_planck = mpf('6.1163e-10')    # Planck 對照 (p1_bbn 用)
etaB_fix    = mpf('6.0817e-10')    # Fixsen T (o166 參考)
# 已排除參考 (禁錨, 只列明): 6.0622e-10 (O37×P_n 雙重 stale) / 6.063632e-10 (19/450 族, 17.6σ)

results = []
def check(name, ok, info=""):
    results.append(ok)
    print(f"  [{'OK ' if ok else 'XX '}] {name} — {info}")

print("="*74)
print("  O168 — 23: η_B 結構形式審計 (權威錨 v3)")
print("="*74)

# ── [0] 錨修正歷史 ──
print("\n─── [0] 錨修正歷史 (append-only) ───")
print("  v1 (09-11): η_B = 6.062e-10 — O37×P_n 雙重 stale (O169 判定)")
print("  v2 (09-15 整合): 6.063632e-10 — 但屬 19/450 家族, O5-1 (09-23) 17.6σ 排除!")
print("  v3 (10-15 本版): 權威錨 = 6.2116e-10 (p1_bbn/O5-3) + Planck 6.1163e-10")

# ── [1] 候選 (4/5)e⁻²¹ 對權威錨 ──
print("\n─── [1] 候選 (4/5)e⁻²¹ 對權威錨重測 ───")
cand1 = mpf(4)/5 * exp(-21)
d_idcm   = abs(cand1/etaB_idcm - 1)*100
d_planck = abs(cand1/etaB_planck - 1)*100
d_fix    = abs(cand1/etaB_fix - 1)*100
print(f"  (4/5)·e⁻²¹ = {float(cand1):.6e}")
print(f"  vs η_B(IDCM 權威) = {float(etaB_idcm):.6e} — dev {float(d_idcm):.4f}%  ← 關鍵")
print(f"  vs η_B(Planck)    = {float(etaB_planck):.6e} — dev {float(d_planck):.4f}%")
print(f"  vs η_B(Fixsen)    = {float(etaB_fix):.6e}   — dev {float(d_fix):.4f}%")
check("[1a] 候選對權威錨 dev < 0.1%", d_idcm < 0.1,
      f"dev {float(d_idcm):.4f}% ≈ 2.34% ≫ 0.1%")
check("[1b] 候選對 Planck dev < 0.5%", d_planck < 0.5,
      f"dev {float(d_planck):.4f}% ≈ 0.82% ≫ 0.5%")
print("  ⇒ 初版 0.040% 擊中係 stale 錨假象 (撞正被排除鏈) — 候選否證")

# ── [2] 唯一性掃描對權威錨 ──
print("\n─── [2] 唯一性掃描 (c·e^{−n}) 對權威錨 6.2116e-10 ───")
rats = [("1", mpf(1)), ("1/2", mpf(1)/2), ("2/3", mpf(2)/3), ("3/4", mpf(3)/4),
        ("4/5", mpf(4)/5), ("5/6", mpf(5)/6), ("6/7", mpf(6)/7), ("7/8", mpf(7)/8),
        ("8/9", mpf(8)/9), ("9/10", mpf(9)/10), ("1/4", mpf(1)/4), ("3/5", mpf(3)/5),
        ("5/8", mpf(5)/8), ("13/21", mpf(13)/21), ("19/20", mpf(19)/20),
        ("20/21", mpf(20)/21), ("21/22", mpf(21)/22), ("26/27", mpf(26)/27),
        ("33/34", mpf(33)/34), ("44/45", mpf(44)/45)]
hits = []
for n in range(1, 89):
    for cname, c in rats:
        v = c * exp(-n)
        dd = abs(v/etaB_idcm - 1)*100
        if dd < 0.5:
            hits.append((n, cname, float(dd)))
hits.sort(key=lambda t: t[2])
print(f"  <0.5% 命中: {len(hits)} 個候選:")
for n, cname, d in hits[:8]:
    print(f"    e^−{n}·{cname}: dev {d:.3f}%")
check("[2a] 對權威錨 <0.5% 命中 = 0 (沙漠)", len(hits) == 0, f"{len(hits)} 個")
print("  ⇒ η_B 結構沙漠確認 (權威錨下冇結構形式)")

# ── [3] φ 原生替代對權威錨 ──
print("\n─── [3] φ 原生替代 φ⁻⁴⁴·19/20 對權威錨 ───")
cand2 = phi**(-44) * mpf(19)/20
d2 = abs(cand2/etaB_idcm - 1)*100
print(f"  φ⁻⁴⁴·19/20 = {float(cand2):.6e} — dev {float(d2):.4f}%")
check("[3a] φ 候選對權威錨 dev < 0.5%", d2 < 0.5, f"dev {float(d2):.4f}%")

# ── [4] Ω_b 沙漠修正: 1/20 就係結構形式 (O5-1) ──
print("\n─── [4] Ω_b 沙漠修正 (docs/21-22 舊讀法更正) ───")
print("  舊讀法: Ω_b 沙漠最佳 1/(B·F₅) = 1/20 dev 2.9% vs Planck → 當『無結構形式』")
print("  ★ O5-1 判定 (09-23): Ω_b = 3/60 = 1/20 = N_gen/60 就係權威結構形式!")
print("    (Ω_DM/Ω_b = 16/3, −0.48σ; Ω_b/Ω_m = 3/19, +0.92σ; 19/450 家族 17.6σ 排除)")
print("  ⇒ 2.9% vs Planck = 框架自身 2.32σ 張力 (p1_bbn 🟡), 唔係『冇結構形式』")
check("[4a] Ω_b = 1/(B·F₅) = 1/20 = N_gen/60 (O5-1 權威)",
      mpf(1)/(B*F5) == mpf(N_gen)/60 == mpf(1)/20)

# ── [5] 單冪沙漠 (權威錨) ──
print("\n─── [5] 單冪沙漠 (權威錨) ───")
d_phi44 = abs(phi**(-44)/etaB_idcm - 1)*100
check("[5a] 單冪全 > 1% (沙漠)", d_phi44 > 1.0, f"φ⁻⁴⁴ dev {float(d_phi44):.2f}%")

# ── [6] 後果 ──
print("\n─── [6] 後果 ───")
print("  ❌ η_B = (4/5)e⁻²¹ 候選對權威錨 dev 2.34% — 否證 (非結構形式)")
print("  ✅ Ω_b = 1/20 結構形式已由 O5-1 閉合 (唔係沙漠)")
print("  🟡 η_B 維持無結構形式 (IDCM 值 6.2116e-10 有 2.32σ 邊緣張力, p1_bbn 已知)")
print("  → 絕對尺度缺口: η_B 唔再係候選路徑; 剩 ω_ring 純譜預言")
print("  ★ 教訓: 掃描唯一 + dev<0.1% 仍可係假象 — 因為鎖咗錯錨 (stale 鏈)")
check("[E] η_B 候選否證 (2.34%); Ω_b 已閉合; η_B 維持輸入 🟡",
      d_idcm > 1.0 and len(hits) == 0)

print(f"\n{'='*74}")
print(f"  O168-23 η_B 審計: {sum(results)}/{len(results)} PASS")
print(f"{'='*74}")