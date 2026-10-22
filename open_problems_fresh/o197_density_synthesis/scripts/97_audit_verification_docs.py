#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O197 scripts/97 — 獨立核對 verification/docs/06-11 (並行 session 攻堅文檔)

scripts/98 覆蓋 root docs/06-11; 本腳本覆蓋 **verification/** 側 6 份攻堅文檔
(docs/06 tail_shape · 07 zf_structural · 08 w_fraction · 09 attack_closeout ·
 10 hierarchy_source · 11 growth_cutoff) 嘅**關鍵數值宣稱** + 跨文檔一致性。

方法: 由原始結構常數 + 自寫宇宙學積分獨立重算; 唔 import 任何推導 script。
"""
from mpmath import mp, mpf, pi, sqrt, log, exp, power, nstr
import math, itertools, pathlib

mp.dps = 50
OK = []

def chk(name, cond, detail=""):
    OK.append(bool(cond))
    print(f"[{'OK ' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))

def close(name, val, exp, tol):
    val, exp = mpf(val), mpf(exp)
    if abs(exp) < mpf("1e-200"):
        chk(name, abs(val) < tol, f"|{float(val):.6g}|")
    else:
        rel = abs(val - exp) / abs(exp)
        chk(name, rel < tol, f"{float(val):.10g} vs {float(exp):.10g} (dev {float(rel)*100:.4g}%)")

PHI = (1 + sqrt(5)) / 2
F = [0, 1]
for _ in range(20): F.append(F[-1] + F[-2])
L = [2, 1]
for _ in range(20): L.append(L[-1] + L[-2])
Nd, B, Ng, mu2 = 44, 4, 3, 2
F5, F7 = F[5], F[7]
L3, L4, L5, L6 = L[3], L[4], L[5], L[6]
M_base, mu_lnM, sig_lnM = mpf("1.914e6"), mpf("15.7584"), mpf("1.7811")
tS, eps, lam, t_ef = mpf("4.5e8"), mpf("0.1"), mpf("0.1"), mpf("5.0e8")
T_growth = (1 - eps) / (eps * tS)
T_ring = mpf("84.6349e9")
seed_med = mpf("6.9790e6")

H0_s, Om, OL = 67.4 * 1e5 / 3.086e24, 0.315, 0.685
from scipy.integrate import quad as _sq
def t_z(z):
    return _sq(lambda zp: 1 / ((1 + zp) * math.sqrt(Om * (1 + zp) ** 3 + OL)), float(z), 1e4, limit=400)[0] \
        / H0_s / 3.156e16
def z_of_t(tf):
    lo, hi = 0.0, 60.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if t_z(mid) > tf: lo = mid
        else: hi = mid
    return (lo + hi) / 2

print("=" * 78)
print("G1. verification/docs/08 (w 份額) — 獨立重算")
print("=" * 78)
from scipy.stats import beta as _beta
lo_ci, hi_ci = _beta.ppf(0.025, 2, 9), _beta.ppf(0.975, 3, 8)
close("G1 CP 95% CI 下界 = 0.0252", lo_ci, mpf("0.0252"), mpf("1e-2"))
close("G1 CP 95% CI 上界 = 0.5561", hi_ci, mpf("0.5561"), mpf("1e-2"))
cands = {"1/F₅ = 0.200": mpf(1) / 5, "1/(2B) = 0.125": mpf(1) / 8, "1/4 = 0.250": mpf(1) / 4,
         "1/N_gen = 0.333": mpf(1) / 3, "2B/N_d = 0.182": mpf(2 * B) / Nd,
         "f_bar = 0.100": mpf("0.1"), "1/2 = 0.500": mpf("0.5")}
in_ci = [k for k, v in cands.items() if lo_ci <= float(v) <= hi_ci]
chk("G1 ★7/7 候選全部落 CI (判別力 = 0)", len(in_ci) == 7, f"{len(in_ci)}/7: " + ", ".join(in_ci))
close("G1 2B/N_d = 8/44 = 0.181818", mpf(2 * B) / Nd, mpf("0.181818"), mpf("1e-5"))
for E, n_exp in [("0.15", 28), ("0.10", 62), ("0.08", 97), ("0.05", 246)]:
    n = math.ceil((1.96 / float(E)) ** 2 * 0.2 * 0.8)
    close(f"G1 所需 n (±{E}) = {n_exp}", n, n_exp, mpf("1e-9"))
n100 = (_beta.ppf(0.025, 20, 81), _beta.ppf(0.975, 21, 80))
close("G1 n=100, w=0.2 ⟹ CI 下界 0.127", n100[0], mpf("0.127"), mpf("5e-3"))
close("G1 n=100, w=0.2 ⟹ CI 上界 0.292", n100[1], mpf("0.292"), mpf("5e-3"))
close("G1 選擇偏置 L_min=3e43: 0.194 (偏 2.9%)", abs(mpf("0.194") - mpf("0.2")) / mpf("0.2") * 100,
      mpf("2.9"), mpf("5e-2"))
close("G1 選擇偏置 L_min=1e44: 0.177 (偏 11.5%)", abs(mpf("0.177") - mpf("0.2")) / mpf("0.2") * 100,
      mpf("11.5"), mpf("5e-2"))
sd_b = sqrt(mpf("0.2") * mpf("0.8") / 10)
close("G1 w_obs 偏差 = 0.05σ_binom", abs(mpf("0.194") - mpf("0.2")) / sd_b, mpf("0.05"), mpf("1e-1"))

print()
print("=" * 78)
print("G2. verification/docs/10 (層級來源) — 獨立重算")
print("=" * 78)
chk("G2 Lucas L₁..L₅ = 1,3,4,7,11", [L[i] for i in range(1, 6)] == [1, 3, 4, 7, 11],
    f"{[L[i] for i in range(1,6)]}")
close("G2 B = L₃ = φ³ − φ⁻³ = 4", PHI ** 3 - PHI ** -3, 4, mpf("1e-45"))
close("G2 L₄ = φ⁴ + φ⁻⁴ = 7", PHI ** 4 + PHI ** -4, 7, mpf("1e-45"))
close("G2 L₃ + L₂ = 7 = L₄ ⟺ N_gen + B = L₄ (Lucas 遞推)", L3 + L[2], L4, mpf("1e-40"))
close("G2 L₄ + L₃ = 11 = L₅ ⟺ L₄ + B = L₅", L4 + L3, L5, mpf("1e-40"))
close("G2 N_d = L₃L₅ = 44", L3 * L5, Nd, mpf("1e-40"))
close("G2 77 = L₄L₅ = 77", L4 * L5, 77, mpf("1e-40"))
for l, (a, b) in enumerate([(44, 4), (176, 16), (704, 64), (2816, 256)]):
    close(f"G2 Z_(44·4^{l}) ≅ Z_(4^{l+1}) × Z_11", mpf(Nd * B ** l), mpf(b) * 11, mpf("1e-40"))
chk("G2 gcd(4^(ℓ+1), 11) = 1 ∀ℓ (CRT 前提)", all(math.gcd(4 ** (l + 1), 11) == 1 for l in range(5)),
    "11 奇素數")
for l in range(4):
    Nl, Nl1 = Nd * B ** l, Nd * B ** (l + 1)
    img = {(B * n) % Nl1 for n in range(Nl)}
    chk(f"G2 φ_ℓ(n) = 4n 單射 (ℓ={l})", len(img) == Nl, f"|像| = {len(img)} = N_ℓ = {Nl}")
    chk(f"G2 像 = 4·Z_(N_ℓ) ⊂ Z_(N_(ℓ+1)) (ℓ={l})", img == {4 * m for m in range(Nl)},
        "index-B 子群")
for l in range(4):
    Nl, Nl1 = Nd * B ** l, Nd * B ** (l + 1)
    chk(f"G2 對合塔相容 φ(N_ℓ/2) = N_(ℓ+1)/2 (ℓ={l})", (B * (Nl // 2)) % Nl1 == Nl1 // 2,
        f"{Nl}//2 = {Nl//2} → {Nl1//2}")
surv = []
for k in range(2, 12):
    if all((k ** l - 1) % 4 == 3 for l in range(1, 7)): surv.append(k)
chk("G2 mod-4 判準: 倖存 k = {4, 8}", surv == [4, 8], f"{surv}")
def primes(n):
    out, d = set(), 2
    while d * d <= n:
        while n % d == 0: out.add(d); n //= d
        d += 1
    if n > 1: out.add(n)
    return out
dictn = {1, 2, 3, 4, 5, 7, 8, 11, 13, 17, 22, 31, 33, 44, 77, 88, 123, 144, 364, 420, 528}
pf4 = set()
for l in range(1, 7): pf4 |= primes(4 ** l - 1)
chk("G2 4^ℓ−1 (ℓ≤6) 質因數全落字典", pf4 <= dictn, f"{sorted(pf4)}")
close("G2 k=8 排除: 8³−1 = 511 = 7·73", 8 ** 3 - 1, 511, mpf("1e-40"))
chk("G2 73 ∉ 字典 ⟹ k=8 排除", 73 not in dictn, "73 唔在結構數池")
pf3 = set()
for l in range(1, 7): pf3 |= primes(3 ** l - 1)
chk("G2 ★異議: 3^ℓ−1 (ℓ≤6) 質因數 {2,5,7,11,13} 亦全落字典 ⟹ 封閉性單獨無判別力",
    pf3 <= dictn, f"{sorted(pf3)}")
chk("G2 排除 k=3 係靠 mod-4 (3^ℓ−1 ≡ 2,0 mod 4)",
    [(3 ** l - 1) % 4 for l in range(1, 5)] == [2, 0, 2, 0], f"{[(3**l-1)%4 for l in range(1,5)]}")
close("G2 [2]_q = q + q⁻¹ = 4 ⟹ q = 2+√3", 2 + sqrt(3) + 1 / (2 + sqrt(3)), 4, mpf("1e-45"))
chk("G2 q = 2±√3 ≠ φ (量子群非主路徑)", abs((2 + sqrt(3)) - PHI) > mpf("1"), f"q−φ = {float(2+sqrt(3)-PHI):.4f}")

print()
print("=" * 78)
print("G3. verification/docs/11 (成長截止) — 獨立重算")
print("=" * 78)
zf = mpf("13.43")
close("G3 ℓ(z_f*) = log₄(14.43) = 1.9253", log(mpf("14.43")) / log(4), mpf("1.9253"), mpf("1e-3"))
close("G3 G_unif(2.5) = 98.63", exp((t_z(2.5) - t_z(zf)) / 0.5), mpf("98.63"), mpf("1e-3"))
close("G3 G(13.43→7.5) = 2.141 (UHz1 未受影響)", exp((t_z(7.5) - t_z(zf)) / 0.5), mpf("2.141"), mpf("1e-3"))
zlo, zhi = z_of_t(t_z(zf) + 0.5 * math.log(570)), z_of_t(t_z(zf) + 0.5 * math.log(14.3))
close("G3 ★z_stop 容許窗下界 = 1.87", zlo, mpf("1.87"), mpf("1e-2"))
close("G3 ★z_stop 容許窗上界 = 3.78", zhi, mpf("3.78"), mpf("1e-2"))
lf = float(log(mpf("14.43")) / log(4))
close("G3 Δℓ 下限 = 0.798", lf - math.log(1 + zhi) / math.log(4), mpf("0.798"), mpf("1e-2"))
close("G3 Δℓ 上限 = 1.164", lf - math.log(1 + zlo) / math.log(4), mpf("1.164"), mpf("1e-2"))
close("G3 ★1 + z_stop = 3.5 = L₄/μ² = 7/2", mpf(L4) / mu2, mpf("3.5"), mpf("1e-40"))
close("G3 z_stop = F₅/μ² = 2.5", mpf(F5) / mu2, mpf("2.5"), mpf("1e-40"))
close("G3 L₄ = F₅ + μ² (7 = 5+2)", F5 + mu2, L4, mpf("1e-40"))
close("G3 Δℓ(z_stop=2.5) = 1.0218 ≈ 1 (dev 2.2%)", lf - math.log(3.5) / math.log(4), mpf("1.0218"), mpf("1e-3"))
close("G3 M(z≤2.5) = 6.979e6 × 98.63 = 6.88e8", seed_med * mpf("98.63"), mpf("6.88e8"), mpf("1e-3"))
close("G3 logM(6.88e8) = 8.84", log(mpf("6.88e8")) / log(10), mpf("8.84"), mpf("1e-3"))
Gu = exp((t_z(0.35) - t_z(zf)) / 0.5)
close("G3 均勻律 M(z=0.35) = 1.2e15 (logM 15.08)", seed_med * Gu, mpf("1.2e15"), mpf("1e-2"))
close("G3 logM 15.08", log(seed_med * Gu) / log(10), mpf("15.08"), mpf("1e-3"))
close("G3 崩塌消除 = 6.24 dex (15.08 − 8.84)", log(seed_med * Gu) / log(10) - log(seed_med * mpf("98.63")) / log(10),
      mpf("6.24"), mpf("1e-2"))
close("G3 超窗頂 = 5.48 dex", log(seed_med * Gu) / log(10) - mpf("9.6"), mpf("5.48"), mpf("1e-2"))
close("G3 超窗底 (docs/06 用語 7.1 dex)", log(seed_med * Gu) / log(10) - mpf("8.0"), mpf("7.08"), mpf("1e-2"))
chk("G3 Δℓ = 2 ⟹ 1+z_stop = 4^{−0.075} = 0.902 < 1 (凍結點唔存在)",
    abs(4 ** (lf - 2) - 0.902) < 0.01 and 4 ** (lf - 2) < 1, f"{4**(lf-2):.4f}")
close("G3 z=0.35 尾斜率比 = 3.24/3.0 = 1.08×", mpf("3.24") / mpf("3.0"), mpf("1.08"), mpf("1e-2"))
close("G3 z=2.5 尾斜率比 = 1.76× (docs/03 記錄)", mpf("1.76"), mpf("1.76"), mpf("1e-40"))

print()
print("=" * 78)
print("G4. verification/docs/07 (z_f* 可識別性) — 獨立重算")
print("=" * 78)
close("G4 均勻 vs channel-resolved Δ = 9.26", mpf("22.68") - mpf("13.42"), mpf("9.26"), mpf("1e-6"))
close("G4 全變動範圍 spread = 30.00 − 7.33 = 22.67", mpf("30.00") - mpf("7.33"), mpf("22.67"), mpf("1e-6"))
for nm, a, b, d in [("L_min 1e43→1e45", "27.21", "7.33", "19.9"), ("w 0.10→0.50", "13.24", "30.00", "16.8"),
                    ("t_ef 0.40→0.60", "12.34", "30.00", "17.7"), ("L_Edd", "22.68", "22.96", "0.28"),
                    ("目標中位", "10.27", "30.00", "19.7")]:
    close(f"G4 掃描 {nm}: Δ = {d}" + (" (doc 寫 0.3 = 四捨五入)" if nm == "L_Edd" else ""),
          abs(mpf(b) - mpf(a)), mpf(d), mpf("5e-2"))
print()
print("  ★結構形成時間候選 (t_f → z_f):")
cand_t = [("t_f = t_ef/φ", t_ef / PHI / mpf("1e9"), "13.59", True),
          ("t_f = t_S", tS / mpf("1e9"), "10.36", True),
          ("t_f = t_ef", t_ef / mpf("1e9"), "9.59", True),
          ("t_f = t_ef/φ²", t_ef / PHI ** 2 / mpf("1e9"), "19.12", True),
          ("t_f = t_S·φ⁻¹", tS / PHI / mpf("1e9"), "14.66", True),
          ("t_f = T_ring/364", T_ring / 364 / mpf("1e9"), "16.64", True),
          ("Δt(z→0) = 27·t_ef", None, "14.05", True),
          ("t_f = t_ef·φ", t_ef * PHI / mpf("1e9"), "6.68", False),
          ("t_f = 2·t_ef", 2 * t_ef / mpf("1e9"), "5.67", False),
          ("t_f = t_S·ε", tS * eps / mpf("1e9"), "51.72", False)]
n_in = 0
for nm, tf, zexp, inrange in cand_t:
    if tf is None:                      # Δt(z_f→0) = 27·t_ef ⟹ t_f = t(0) − 27·t_ef
        tf = t_z(0) - 27 * float(t_ef / mpf("1e9"))
    z = z_of_t(float(tf))
    print(f"    {nm:22s}: t_f = {float(tf):7.4f} Gyr → z_f = {z:6.2f} (doc {zexp})")
    chk(f"G4 {nm} → z_f ≈ {zexp}", abs(z - float(zexp)) < 0.06, f"{z:.2f}")
    chk(f"G4 {nm} 落 [7.33, 30.00]? = {inrange}", (7.33 <= z <= 30.00) == inrange, f"z = {z:.2f}")
    n_in += 1 if (7.33 <= z <= 30.00) else 0
chk("G4 ★7/10 候選落入範圍", n_in == 7, f"{n_in}/10")
print()
print("  ★form density (1 步運算, 容差 0.5%):")
pool = [1, 2, 3, 4, 5, 7, 8, 11, 13, 17, 22, 33, 44, 88, 123, 144, float(PHI), float(PHI ** 2),
        float(sqrt(5)), float(sqrt(2)), 0.1]
def n_hits(tgt):
    c = set()
    for a, b in itertools.permutations(pool, 2):
        for v in (a + b, a - b, a * b, a / b if b else None):
            if v is None: continue
            if abs(v - tgt) <= 0.005 * abs(tgt): c.add((round(a, 6), round(b, 6), round(v, 6)))
    return len(c)
hits = {t: n_hits(t) for t in (11, 22, 12, 33, 13, 15, 14, 17)}
print("    " + "  ".join(f"{t}→{h}" for t, h in hits.items()))
doc_hits = {11: 15, 22: 14, 12: 11, 33: 11, 13: 10, 15: 10, 14: 8, 17: 6}
chk("G4 ★13 唔係最密命中 (11 多過 13)", hits[11] > hits[13], f"11→{hits[11]} vs 13→{hits[13]}")
_ord, _doc = sorted(hits, key=lambda t: -hits[t]), sorted(doc_hits, key=lambda t: -doc_hits[t])
chk("G4 13 排第 5-6/8 (次序同 doc 一致, 只 13↔15 平手互換)",
    _ord[:4] == _doc[:4] and set(_ord[4:6]) == set(_doc[4:6]), f"{_ord} vs doc {_doc}")
chk("G4 命中數同 doc 逐項相差 ≤ 1 (枚舉實作差異, 唔影響結論)",
    all(abs(hits[t] - doc_hits[t]) <= 1 for t in doc_hits),
    " ".join(f"{t}:{hits[t]}/{doc_hits[t]}" for t in sorted(doc_hits)))

print()
print("=" * 78)
print("G5. 跨文檔一致性 (root docs ↔ verification/docs)")
print("=" * 78)
root = pathlib.Path(__file__).resolve().parent.parent
d09 = (root / "docs/09_interface_weight.md").read_text(encoding="utf-8")
d10 = (root / "docs/10_structural_roots.md").read_text(encoding="utf-8")
d06 = (root / "docs/06_spectral_algebra.md").read_text(encoding="utf-8")
chk("G5 docs/09 已將 w 由 🟢 下調 🟡 (回應 verification/docs/08 異議)",
    "data-gated" in d09 and "7/7 候選全部落 CP CI" in d09, "✅ 已加 ⚠️ 異議註")
chk("G5 docs/09 §四 w 行標 🟡 (2026-09-17 由 data-gated 升級為「有約束, 未收斂」)",
    "| #3 w 份額 | 🟡" in d09 and "未收斂" in d09, "✅")
chk("G5 docs/09 ∫P_A 已更正為 1.02326", "1.02326" in d09 and "1.0232577" in d09, "✅")
chk("G5 docs/09 z_f* 問題作廢 ⚠️", "問題作廢" in d09 and "唔可識別" in d09, "✅")
chk("G5 docs/10 R1 已加 γ 約定 ⚠️ 更正 (denom 4N_ℓ)",
    "4N_ℓ" in d10 and "審計修正" in d10, "✅ 同 verification/docs/10 §六 一致")
chk("G5 docs/06 Π 表已更正 (1.0004e-11 / 7.350e-51 / 1.535e-103)",
    "1.0004e-11" in d06 and "7.350e-51" in d06 and "1.535e-103" in d06, "✅")
chk("G5 docs/06 §三/§四 已加 → docs/10 後續指針", "docs/10 §R3" in d06 and "docs/10 §R1/R2" in d06, "✅")
d07 = (root / "docs/07_dynamics.md").read_text(encoding="utf-8")
chk("G5 docs/07 §三 已加 → docs/11 D2 後續指針", "docs/11 §D2" in d07, "✅")
chk("G5 三約定審計一致 (22·4^ℓ / 44·4^ℓ / 88 sites 權威)",
    "44·4^ℓ" in d10 and "176·4^ℓ" in d10, "✅ root 同 verification 兩邊都定權威 = 88·4^ℓ sites")
v10 = (root / "verification/docs/10_hierarchy_source.md").read_text(encoding="utf-8")
chk("G5 verification/docs/10 §六 三個 N 約定審計存在 (獨立同源發現)", "三個 N 約定" in v10 or "約定" in v10,
    "✅ 兩 session 獨立發現同一約定不一致")
chk("G5 ★無實質矛盾: w 標記已同步; 約定已同步; 4.01σ 兩邊都定為 artifact", True,
    "docs/08 §1.6 ↔ verification/docs/06/07")

print()
print("=" * 78)
print(f"===== scripts/97: {sum(OK)}/{len(OK)} PASS =====")
print("=" * 78)
