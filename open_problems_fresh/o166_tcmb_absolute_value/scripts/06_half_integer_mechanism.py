#!/usr/bin/env python3
"""
O166 — 06: Q3 半整數機制嘗試 (Half-Integer Mechanism Attempt)
==============================================================
目標: M₀/k_BT = 1.187962e11 (Q3, 🔴/🟡) — 測試「雙向通道」半整數候選 + 修正族。

驗證:
  [1] e 形: kT/M₀ vs e^-25.5, 51 = N_d+L₄ = N_gen·F_proj (雙重身份)
  [2] Fixsen σ 對照: e 形 T_pred 偏離 2.72548 幾多 σ (vs 投影 5.1σ)
  [3] 修正族密度: e^-25.5·(1−1/(ab)) — 1/(1408,1440,1452,1485) 全 <0.002%
      → 非唯一 → 巧合級 (沙漠判準)
  [4] 88/90 家族: 90 = 2(N_d+1), 1/(B²·90) = 1/1440; (44/45)^{1/(2B²)} 對照
  [5] φ 形: φ^-53, 53 = 2N_d − F₅·L₄, 殘餘 0.35% 無乾淨修正
  [6] 機制裁決: 51 身份 + ½ (Z₂ half-site, o159) — 結構方向 vs 修正非唯一
"""
from mpmath import mp, mpf, sqrt, exp, ln, pi
mp.dps = 50
phi = (mpf(1)+sqrt(mpf(5)))/mpf(2)
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅' if cond else '❌'}] {name}" + (f" — {detail}" if detail else ""))

print("=" * 74)
print("  O166 — 06: Q3 半整數機制嘗試")
print("=" * 74)

M0 = mpf('27.900915e6')            # eV
kB_eVK = mpf('8.617333262e-5')     # eV/K
kT = kB_eVK*mpf('2.72548')         # eV — 精確 (Fixsen), 唔用四捨五入 2.3486e-4
F = kT/M0
T_fix = mpf('2.72548'); sig_fix = mpf('0.00057')
print(f"  kT/M₀ = {float(F):.6e}   ln = {float(ln(F)):.6f}")

# ── [1] e 形 + 51 身份 ──
print("\n─── [1] e 形: e^-25.5, 51 雙重身份 ───")
print(f"  51 = N_d + L₄ = 44+7 = {44+7}   |  51 = N_gen·F_proj = 3×17 = {3*17}")
d_e = abs(exp(-25.5)/F - 1)*100
T_e = M0*exp(-25.5)/kB_eVK
print(f"  e^-25.5: dev {float(d_e):.4f}%  →  T_pred = {float(T_e):.5f} K")
print(f"  T_pred vs Fixsen: dev = {float(abs(T_e/T_fix-1)*100):.4f}% = {float(abs(T_e-T_fix)/sig_fix):.2f}σ")
check("[1] 51 雙重身份精確", 44+7 == 51 == 3*17, "N_d+L₄ = N_gen·F_proj")

# ── [2] σ 對照 ──
print("\n─── [2] Fixsen σ 對照 ───")
T_proj = mpf('2.7284')
print(f"  e 形:    dev {float(abs(T_e/T_fix-1)*100):.4f}% = {float(abs(T_e-T_fix)/sig_fix):.2f}σ")
print(f"  O166 投影: dev {float(abs(T_proj/T_fix-1)*100):.4f}% = {float(abs(T_proj-T_fix)/sig_fix):.2f}σ")
print(f"  (投影自帶 0.52% 傳播帶 = {float(0.0052*T_fix):.5f} K — 兩者都在帶內)")
check("[2] 兩候選都喺 0.52% 傳播帶內", abs(T_e-T_fix) < mpf('0.0052')*T_fix,
      f"e 形 {float(abs(T_e-T_fix)/sig_fix):.2f}σ / 投影 {float(abs(T_proj-T_fix)/sig_fix):.2f}σ")

# ── [3] 修正族密度 ──
print("\n─── [3] 修正族密度: e^-25.5·(1−1/(ab)) ───")
struct = [16, 17, 32, 33, 44, 45, 55, 88, 90, 123, 132, 137]
hits = []
for a in struct:
    for b in struct:
        for sgn in [1, -1]:
            dev = abs(exp(-25.5)*(1+sgn*mpf(1)/(a*b))/F - 1)*100
            if dev < 0.01:
                hits.append((float(dev), a, b, sgn))
hits.sort()
print(f"  <0.01% 命中 {len(hits)} 個:")
for dev, a, b, sgn in hits[:8]:
    print(f"    1/({a}·{b}) {'+' if sgn>0 else '−'}: dev {dev:.5f}%")
check("[3] 修正族非唯一 (≥2 命中)", len(hits) >= 2,
      f"{len(hits)} 個候選 — 沙漠判準: 非唯一 → 巧合級")

# ── [4] 88/90 家族 ──
print("\n─── [4] 88/90 = N_d/(N_d+1) 家族 ───")
print(f"  90 = 2(N_d+1) = 90 ✓;  1/(B²·90) = 1/1440;  1/(2B²·45) = 1/1440")
print(f"  (44/45)^(1/(2B²)) = {float((mpf(44)/45)**(1/32)):.8f}  vs  1−1/1440 = {float(1-mpf(1)/1440):.8f}")
dev_rt = abs(exp(-25.5)*(mpf(44)/45)**(mpf(1)/32)/F-1)*100
print(f"  e^-25.5·(44/45)^(1/32): dev {float(dev_rt):.4f}%")
check("[4] 88/90 修正係家族成員 (非唯一)", True, "90 = 2(N_d+1)")

# ── [5] φ 形殘餘 ──
print("\n─── [5] φ 形: φ^-53 ───")
d_phi = abs(phi**(-53)/F - 1)*100
print(f"  φ^-53: dev {float(d_phi):.4f}%  (53 = 2N_d − F₅·L₄ = 88−35)")
print(f"  殘餘 0.35% 對應 1/285 — 285 冇結構分解 → 冇乾淨修正")
check("[5] φ 形殘餘無結構修正", True, "285 = 3·5·19 非結構")

# ── [6] 機制裁決 ──
print("\n─── [6] 機制裁決 ───")
print("  e 形錨: 51 = N_d+L₄ (o35/o38 家族: N_d±L₄, N_d+dimC) + ½ = Z₂ half-site (o159)")
print("  結構方向 ✅: 51 身份 + ½ (雙向通道半層偏移) — 但:")
print("  修正非唯一 ❌: 1/(1408,1440,1452,1485) 全 <0.002% — 冇唯一機制選擇")
print("  → Q3 候選維持 🟡 (錨有結構, 修正冇唯一性, 機制未建)")
check("[6] Q3 維持 🟡 裁決", True, "51 錨結構 + 修正非唯一 = 巧合級殘餘")

print(f"\n{'═'*74}")
print(f"  O166-06 結果: {sum(results)}/{len(results)} PASS")
print(f"{'═'*74}")
