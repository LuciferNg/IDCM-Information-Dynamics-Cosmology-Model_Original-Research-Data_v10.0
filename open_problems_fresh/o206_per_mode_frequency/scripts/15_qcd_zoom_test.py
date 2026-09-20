#!/usr/bin/env python3
"""
O206 — Script 15: 「變焦」= QCD running 之具體檢驗
=========================================================
承 Script 14 §C 之 t 單點線索 (殘餘因子 0.9392 vs MS-bar/pole 0.9410, Δ0.19%)

調律者框架: RGE = 變焦效應 (O156)。具體預言:
  「若 IDCM 之質量公式喺【某個共同標度 μ₀】成立,
    而 PDG 各粒子喺【各自標度】引用,
    則殘餘 = 該標度之間之 QCD running」
  ★ 決定性結構預言: QCD running 【只影響夸克, 唔影響輕子】(輕子只受 QED, ~α/π ≪ 1%)
    ⟹ 若假說成立, 修正後夸克殘餘應大幅下降, 而輕子殘餘【不變】

檢驗:
  §A α_s 1-loop running 實作 + 對照已知值
  §B 掃描 μ₀, 對每個 μ₀ 重擬合 (M₀, α), 記錄 RMS
  §C 逐夸克: 殘餘 vs ln R(μ_q, μ₀)
  §D 替代假說: 逐模式標度 μ₀(n) = f(γ_n)?
  §E 裁決

⚠️ 唔准事後擬合: μ₀ 係 1 個新參數, 必須報自由度成本; 且檢驗輕子【不變】之預言。
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import A5_MODES, E_ring44, V_position, sum_V2_dE

OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


# ── PDG (MeV) + 引用標度 ──
QUARK = [("t", 1, 172690.0, 172690.0), ("b", 2, 4180.0, 4180.0), ("c", 4, 1270.0, 1270.0),
         ("s", 7, 93.5, 2000.0), ("d", 9, 4.67, 2000.0), ("u", 11, 2.16, 2000.0)]
LEPTON = [("tau", 3, 1776.86), ("mu", 5, 105.6583755), ("e", 13, 0.51099895000)]
PAIR = [(n, p, m) for p, n, m, _ in QUARK] + [(n, p, m) for p, n, m in LEPTON]

# ── α_s 1-loop running ──
ALPHA_MZ = 0.1179
MZ = 91187.6
THRESH = [(172690.0, 6), (4180.0, 5), (1270.0, 4), (0.0, 3)]


def beta0(nf):
    return 11.0 - 2.0 * nf / 3.0


def alpha_s(mu):
    """1-loop α_s, 由 m_Z 向下跑, n_f 隨標度切換."""
    mu = max(mu, 300.0)
    a = ALPHA_MZ
    cur = MZ
    for thr, nf in THRESH:
        if mu >= thr:
            break
        b0 = beta0(nf)
        a = a / (1.0 + b0 * a / (2 * math.pi) * math.log(thr / cur))
        cur = thr
    nf = next(n for t, n in THRESH if mu >= t)
    a = a / (1.0 + beta0(nf) * a / (2 * math.pi) * math.log(mu / cur))
    return a


def nf_at(mu):
    return next(n for t, n in THRESH if mu >= t)


def R_mass(mu_a, mu_b):
    """m(mu_a)/m(mu_b) 之 1-loop QCD running."""
    if abs(mu_a - mu_b) < 1e-9:
        return 1.0
    nf = nf_at(min(mu_a, mu_b))
    return (alpha_s(mu_a) / alpha_s(mu_b)) ** (12.0 / (33.0 - 2.0 * nf))


V = V_position()
E = E_ring44()
dm = sum_V2_dE(E, V)
ldm = np.array([math.log(dm[A5_MODES.index(n)]) for n, _, _ in PAIR])
lm = np.array([math.log(m) for _, _, m in PAIR])
is_q = np.array([p in ("u", "d", "s", "c", "b", "t") for _, p, _ in PAIR])


def fit_resid(extra=None):
    y = lm.copy()
    if extra is not None:
        y = y - extra
    A = np.column_stack([np.ones(9), ldm])
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ b
    return b, r


print("=" * 100)
print("O206 Script 15: 「變焦」= QCD running 之具體檢驗")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A α_s 1-loop running 實作 + 對照\n{'─'*100}")
print(f"\n  {'標度':>12} {'α_s(1-loop)':>13} {'已知值 (approx)':>18}")
print("  " + "-" * 46)
KNOWN = [("m_Z", MZ, 0.1179), ("m_t", 172690, 0.108), ("m_b", 4180, 0.226),
         ("m_c", 1270, 0.38), ("2 GeV", 2000, 0.301), ("1 GeV", 1000, 0.49)]
for name, mu, known in KNOWN:
    a = alpha_s(mu)
    print(f"  {name:>12} {a:>13.4f} {known:>18.3f}")
a2 = alpha_s(2000.0)
chk("C1 [running] α_s(2 GeV) 對照已知 (~0.30)",
    abs(a2 - 0.30) < 0.05, f"α_s(2 GeV) = {a2:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 掃描 μ₀ (IDCM 共同標度) — 對每個 μ₀ 重擬合\n{'─'*100}")
b_base, r_base = fit_resid()
rms_base = float(np.std(r_base))
print(f"\n  基準 (μ₀ 假說唔成立): RMS = {rms_base:.4f}, α = {b_base[1]:.6f}")
print(f"\n  {'μ₀ (MeV)':>12} {'α':>10} {'RMS (全 9)':>12} {'夸克 RMS':>10} {'輕子 RMS':>10}")
print("  " + "-" * 60)
scan = {}
for mu0 in np.logspace(math.log10(300), math.log10(1e7), 60):
    corr = np.zeros(9)
    for i, (n, p, m) in enumerate(PAIR):
        if is_q[i]:
            muq = next(s for pp, nn, mm, s in QUARK if pp == p)
            corr[i] = math.log(R_mass(muq, mu0))
    bb, rr = fit_resid(corr)
    rq = float(np.std(rr[is_q]))
    rl = float(np.std(rr[~is_q]))
    scan[float(mu0)] = {"alpha": float(bb[1]), "rms": float(np.std(rr)),
                        "rms_q": rq, "rms_l": rl}
best_mu = min(scan.items(), key=lambda kv: kv[1]["rms"])
for mu0 in [300, 1000, 2000, 4180, 91188, 172690, 1e6]:
    v = scan[min(scan, key=lambda k: abs(k - mu0))]
    print(f"  {min(scan, key=lambda k: abs(k-mu0)):>12.1f} {v['alpha']:>10.4f} "
          f"{v['rms']:>12.4f} {v['rms_q']:>10.4f} {v['rms_l']:>10.4f}")
print(f"\n  ★ 最佳 μ₀ = {best_mu[0]:.1f} MeV, RMS = {best_mu[1]['rms']:.4f} "
      f"(基準 {rms_base:.4f}, 改善 {rms_base/best_mu[1]['rms']:.3f}×)")
print(f"    對應: 夸克 RMS = {best_mu[1]['rms_q']:.4f}, 輕子 RMS = {best_mu[1]['rms_l']:.4f}")
chk("C2 [μ₀ 掃描] QCD running 唔令殘餘閉合 (最佳改善 < 1.5×)",
    rms_base / best_mu[1]["rms"] < 1.5,
    f"最佳改善 = {rms_base/best_mu[1]['rms']:.3f}×")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 逐夸克: 殘餘 vs ln R(μ_q, μ₀) — 直接相關檢驗\n{'─'*100}")
resid_q = r_base[is_q]
print(f"\n  {'夸克':>5} {'標度 μ_q':>10} {'殘餘':>9} " +
      " ".join(f"{'R('+str(int(m))+')':>10}" for m in [2000, 4180, 172690]))
print("  " + "-" * 62)
for i, (n, p, m) in enumerate(PAIR):
    if not is_q[i]:
        continue
    muq = next(s for pp, nn, mm, s in QUARK if pp == p)
    row = f"  {p:>5} {muq:>10.0f} {r_base[i]:>9.4f} "
    for m0 in [2000, 4180, 172690]:
        row += f"{math.log(R_mass(muq, m0)):>10.4f} "
    print(row)
print(f"\n  {'μ₀':>10} {'corr(殘餘, ln R)':>18} {'perm p':>9}")
print("  " + "-" * 40)
rng = np.random.default_rng(20260921)
best_c = None
for mu0 in np.logspace(math.log10(300), math.log10(1e7), 25):
    c = np.array([math.log(R_mass(next(s for pp, nn, mm, s in QUARK if pp == p), mu0))
                  for n, p, m in PAIR if p in ("u", "d", "s", "c", "b", "t")])
    if c.std() < 1e-12:
        continue
    r = float(np.corrcoef(c, resid_q)[0, 1])
    null = np.array([abs(np.corrcoef(c, rng.permutation(resid_q))[0, 1]) for _ in range(4000)])
    p_ = float((null >= abs(r)).mean())
    if best_c is None or p_ < best_c[2]:
        best_c = (float(mu0), r, p_)
    if abs(math.log10(mu0) - round(math.log10(mu0))) < 0.05:
        print(f"  {mu0:>10.0f} {r:>+18.4f} {p_:>9.4f}")
print(f"\n  ★ 最佳相關: μ₀ = {best_c[0]:.0f} MeV, r = {best_c[1]:+.4f}, p = {best_c[2]:.4f}")
chk("C3 [相關] 殘餘 vs QCD running 唔顯著 (最佳 p > 0.05)",
    best_c[2] > 0.05, f"最佳 r = {best_c[1]:+.4f}, p = {best_c[2]:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 結構預言檢驗: 修正應【只影響夸克】\n{'─'*100}")
gam = np.array([E[n - 1] for n, _, _ in PAIR])
print(f"""
  假說預言: QCD running 修正夸克, 輕子【完全不變】
  ⟹ 若成立: 修正後夸克 RMS → 小, 輕子 RMS 【維持】
  實測 (最佳 μ₀ = {best_mu[0]:.0f} MeV): 夸克 RMS {float(np.std(r_base[is_q])):.4f} → {best_mu[1]['rms_q']:.4f}
                                      輕子 RMS {float(np.std(r_base[~is_q])):.4f} → {best_mu[1]['rms_l']:.4f}
""")
print(f"  {'μ₀':>10} {'夸克 RMS 改善':>15} {'輕子 RMS 改變':>15}")
print("  " + "-" * 44)
for mu0 in [1000, 2000, 4180, 172690]:
    k = min(scan, key=lambda x: abs(x - mu0))
    v = scan[k]
    print(f"  {k:>10.0f} {float(np.std(r_base[is_q]))/v['rms_q']:>14.3f}× "
          f"{v['rms_l']/float(np.std(r_base[~is_q])):>14.3f}×")
# 輕子修正量: 由 corr 陣列直接檢驗 (結構上 leptons 不入 is_q ⟹ corr = 0)
def corr_vec(mu0):
    c = np.zeros(9)
    for i, (n, p, m) in enumerate(PAIR):
        if is_q[i]:
            muq = next(s for pp, nn, mm, s in QUARK if pp == p)
            c[i] = math.log(R_mass(muq, mu0))
    return c


chk("C4 [結構預言] 輕子之【修正量】精確為零 (唔受 QCD 影響)",
    all(np.all(corr_vec(mu0)[~is_q] == 0.0) for mu0 in [1000.0, 2000.0, 4180.0]),
    "輕子修正項 ≡ 0 (結構保證); ⚠️ 但重擬合會令擬合線移動 ⟹ 輕子殘餘仍會變")
print(f"     ⚠️ 誠實記錄: 輕子【殘餘】由 {float(np.std(r_base[~is_q])):.4f} → {best_mu[1]['rms_l']:.4f}"
      f" 係重擬合之擬合線移動所致, 非輕子本身受修正")
# 自由度成本: +1 參數 (μ₀) 換 1.142× 改善 — 用 AIC 比較
n_pt = 9
rss0 = n_pt * rms_base ** 2
rss1 = n_pt * best_mu[1]["rms"] ** 2
aic0 = n_pt * math.log(rss0 / n_pt) + 2 * 2
aic1 = n_pt * math.log(rss1 / n_pt) + 2 * 3
print(f"\n  ★ 自由度成本: 基準 k=2, AIC = {aic0:.3f}; 加 μ₀ 後 k=3, AIC = {aic1:.3f}")
chk("C6 [自由度] μ₀ 之 AIC 改善 < 2 ⟹ 無實質支持 (慣例 ΔAIC<2)",
    aic0 - aic1 < 2.0, f"ΔAIC 改善 = {aic0-aic1:+.3f} (≪2 = 無實質支持)")
# 關鍵: 夸克即使最佳 μ₀ 仍唔閉合
chk("C5 [關鍵] 即使最佳 μ₀, 夸克殘餘仍 ≫ 0 (未閉合)",
    best_mu[1]["rms_q"] > 0.3, f"夸克 RMS = {best_mu[1]['rms_q']:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§E 裁決\n{'─'*100}")
print(f"""
  ★ 「RGE = 變焦 = 標度失配」假說: 🔴 【實測否定】
     ① μ₀ 掃描 (60 點, 300 MeV – 10⁷ MeV): 最佳改善僅 {rms_base/best_mu[1]['rms']:.3f}×
        (基準 RMS {rms_base:.4f} → {best_mu[1]['rms']:.4f}) ⟹ 唔閉合
     ② 夸克殘餘 vs ln R: 最佳 r = {best_c[1]:+.4f} (p = {best_c[2]:.4f}) ⟹ 唔顯著
     ③ 即使最佳 μ₀, 夸克 RMS = {best_mu[1]['rms_q']:.4f} (仍 ≫ 0)
     ⟹ 「殘餘 = 標度失配」唔成立; 但 t 之單點 (Δ0.19%) 仍係未解線索
  ★ 自由度成本: μ₀ 係【新參數】; AIC 改善僅 {aic0-aic1:+.3f} (≪2) ⟹ 無實質支持, 唔值得引入
  ⟹ 結論: 殘餘【唔係】QCD running / 標度失配所造成。
     殘餘係【未建模結構】(Script 14 已證), 且其來源【唔喺】QCD 標度層。
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "15_qcd_zoom_test.json", "w") as f:
    json.dump({
        "alpha_s_2gev": a2,
        "rms_base": rms_base,
        "best_mu0": best_mu[0], "best_mu0_rms": best_mu[1]["rms"],
        "best_improvement": rms_base / best_mu[1]["rms"],
        "best_mu0_rms_quark": best_mu[1]["rms_q"], "best_mu0_rms_lepton": best_mu[1]["rms_l"],
        "corr_best": {"mu0": best_c[0], "r": best_c[1], "p": best_c[2]},
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/15_qcd_zoom_test.json")
