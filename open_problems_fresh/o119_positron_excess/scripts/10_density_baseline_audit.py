#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O119 - Script 10: 密度基準審計 (density-baseline / look-elsewhere audit)
=====================================================================
本輪 (2026-09-26) 針對 docs/01 §4 嘅「零參數結構閉合」
    f_W(E) = (1/F5^2)·E^(F6/(Nd-F7)) = (1/25)·E^(8/31)
做 O208 標準要求嘅密度基準審計 (verification-architecture-standards §2):

  任何數值匹配閉合聲稱必須報 (1) N_search  (2) d_med (MC>=1e5, 附 seed)
  (3) q_obs 分位數 — 判定 <=1% -> 綠 / 1-5% -> 黃 / >5% -> 紅。

docs/01 從未報過呢三項 —— 本 script 補做, 並同時做:
  (a) 加權 MLE 重擬合 + sigma_gamma (可辨識性)
  (b) Delta-chi^2 F-test (「0 參數好過 2 參數」聲稱)
  (c) 池敏感度 (三個池: 本 script 標準池 / O119 script04 池 / 最小池)

第一性原理: 全部候選式由結構數池 (唔含目標值) 生成, 唔 import 其他 script。
"""
import json
import math
import numpy as np

print("=" * 74)
print("O119 Script 10: 密度基準審計 (look-elsewhere) — C=1/25, gamma=8/31, p_CR=2.7")
print("=" * 74)

# ---------------- 結構數池 (pre-registered) ----------------
POOL_CANON = {
    "N_d": 44, "B": 4, "N_gen": 3, "mu2": 2, "M": 33, "F_proj": 17,
    "F3": 2, "F4": 3, "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34, "F10": 55,
    "L3": 4, "L4": 7, "L5": 11, "L6": 18, "L7": 29, "L8": 47,
    "Sgamma": 90, "h11": 36, "h21": 98, "N88": 88, "N176": 176,
    "C44_2": 946, "dimC528": 528, "F11x2": 178, "M2_66": 66, "L4L5_77": 77,
    "gam7": 4 * math.sin(7 * math.pi / 88) ** 2,
    "gam20": 4 * math.sin(20 * math.pi / 88) ** 2,
    "om22": 2 * math.sin(22 * math.pi / 88),
    "Sgamma_odd": 44,
}
# ⚠️ 刻意唔放入 "8" (F6) 同 "31" (N_d-F7) 以外嘅組合數 —— 8 已在池 (F6),
#    31 唔直接放入池, 令 8/31 只能由 a/(b-c) 形式 (F6/(N_d-F7)) 生成,
#    避免「池內已含聲稱式」嘅循環。
POOL_O119 = {  # O119 script 04 用嘅池 (原樣重現)
    "N_d": 44, "B": 4, "F3": 2, "F4": 3, "F5": 5, "F6": 8, "F7": 13, "F8": 21,
    "L3": 4, "L4": 7, "L5": 11, "L6": 18, "L7": 29, "L8": 47, "M": 33, "mu2": 2,
    "F_proj": 17, "N_gen": 3, "90": 90, "88": 88, "178": 178, "36": 36, "98": 98,
    "66": 66, "48": 48, "946": 946, "1496": 1496,
    "gamma7": 4 * math.sin(7 * math.pi / 88) ** 2,
    "gamma20": 4 * math.sin(20 * math.pi / 88) ** 2,
    "omega22": 2 * math.sin(22 * math.pi / 88),
}
POOL_MIN = {"N_d": 44, "B": 4, "F5": 5, "F6": 8, "F7": 13, "L5": 11,
            "L6": 18, "L7": 29, "N_gen": 3, "mu2": 2, "Sgamma": 90, "N88": 88}


def build_exprs(pool):
    keys = list(pool)
    vals = [pool[k] for k in keys]
    n = len(keys)
    out = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            a, b = vals[i], vals[j]
            out.append((f"{keys[i]}/{keys[j]}", a / b))
            for k in range(n):
                if k in (i, j):
                    continue
                c = vals[k]
                out.append((f"({keys[i]}+{keys[j]})/{keys[k]}", (a + b) / c))
                out.append((f"({keys[i]}-{keys[j]})/{keys[k]}", (a - b) / c))
                out.append((f"{keys[i]}/({keys[j]}+{keys[k]})", a / (b + c)))
                if abs(b - c) > 1e-12:
                    out.append((f"{keys[i]}/({keys[j]}-{keys[k]})", a / (b - c)))
    return [(l, v) for l, v in out if v > 0 and math.isfinite(v)]


def baseline(pool, target, cand, lo, hi, N=200000, seed=20260926):
    """回傳 (N_search, dev_obs, d_med, q_obs, n_hits, top5).

    dev_obs = |cand/target - 1| = 聲稱候選本身嘅偏差 (唔係池內最接近者)。
    q_obs   = P(隨機目標被池內任一式命中至 <= dev_obs) — look-elsewhere p 值。
    """
    E = build_exprs(pool)
    V = np.array(sorted(v for _, v in E))
    dev_obs = abs(cand / target - 1)
    rng = np.random.default_rng(seed)
    ts = np.exp(rng.uniform(math.log(lo), math.log(hi), N))
    idx = np.searchsorted(V, ts)
    dv = np.full(N, np.inf)
    m = idx < len(V)
    dv[m] = np.minimum(dv[m], np.abs(V[idx[m]] / ts[m] - 1))
    m = idx > 0
    dv[m] = np.minimum(dv[m], np.abs(V[idx[m] - 1] / ts[m] - 1))
    d_med = float(np.median(dv))
    q_obs = float(np.mean(dv <= dev_obs))
    hits = int(np.sum(np.abs(V / target - 1) <= dev_obs))
    # 池內最接近 target 嘅 5 個 (唯一值)
    order = np.argsort(np.abs(V / target - 1))
    top, seen = [], set()
    for k in order:
        v = V[k]
        if round(v, 12) in seen:
            continue
        seen.add(round(v, 12))
        lab = next(l for l, vv in E if vv == v)
        top.append((float(abs(v / target - 1)), lab, float(v)))
        if len(top) >= 5:
            break
    return len(V), dev_obs, d_med, q_obs, hits, top


def grade(q):
    return "🟢 顯著 (可辨識)" if q <= 0.01 else ("🟡 候選" if q <= 0.05 else "🔴 唔顯著 (巧合級)")


passed = 0
total = 0


def check(name, cond, detail=""):
    global passed, total
    total += 1
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        print(f"  ❌ {name} {detail}")


# ---------------- 1. 加權 MLE 重擬合 ----------------
print("\n[1] 加權 MLE 重擬合 (sigma_f = 0.005 為權重) + 可辨識性")
E_data = np.array([10.0, 16.0, 25.0, 40.0, 65.0, 100.0, 160.0, 250.0, 400.0, 500.0])
f_data = np.array([0.100, 0.110, 0.115, 0.125, 0.138, 0.155, 0.170, 0.185, 0.195, 0.200])
sig_f = 0.005
f_sec = 0.055 * E_data ** (-0.33) + 0.005
f_W = f_data - f_sec
x, y = np.log(E_data), np.log(f_W)
w = (f_W / sig_f) ** 2
W = w.sum(); swx = (w * x).sum(); swy = (w * y).sum()
swxx = (w * x * x).sum(); swxy = (w * x * y).sum()
det = W * swxx - swx ** 2
gamma_hat = (W * swxy - swx * swy) / det
lnC_hat = (swxx * swy - swx * swxy) / det
C_hat = math.exp(lnC_hat)
sig_gamma = math.sqrt(W / det)
sig_lnC = math.sqrt(swxx / det)
print(f"  weighted MLE:  gamma = {gamma_hat:.6f} +- {sig_gamma:.6f}  ({sig_gamma/gamma_hat*100:.2f}%)")
print(f"                 C     = {C_hat:.6f} +- {C_hat*sig_lnC:.6f}")
print(f"  O54 無權重 fit gamma = 0.258122 (docs/01 引用值)")
print(f"  8/31  = 0.258065  -> 同 weighted MLE 差 {abs(8/31-gamma_hat)/sig_gamma:.2f} sigma")
print(f"  1/25  = 0.040000  -> 同 weighted MLE 差 {abs(1/25-C_hat)/(C_hat*sig_lnC):.2f} sigma")
check("gamma 1-sigma 帶 > 1% (觀測對指數弱約束)",
      sig_gamma / gamma_hat > 0.01, f"({sig_gamma/gamma_hat*100:.2f}%)")
check("8/31 落喺 weighted MLE 1.5 sigma 內 (唔可辨識)",
      abs(8 / 31 - gamma_hat) / sig_gamma < 1.5,
      f"({abs(8/31-gamma_hat)/sig_gamma:.2f} sigma)")

# ---------------- 2. Delta-chi^2 F-test ----------------
print("\n[2] Δχ² 檢定: 「0 參數好過 2 參數」聲稱")
chi2_s = float(np.sum(((f_data - (f_sec + (1 / 25) * E_data ** (8 / 31))) / sig_f) ** 2))
chi2_f = float(np.sum(((f_data - (f_sec + C_hat * E_data ** gamma_hat)) / sig_f) ** 2))
dchi = chi2_s - chi2_f
p_dchi = math.exp(-dchi / 2.0)  # chi^2_2 tail = exp(-d/2)
print(f"  chi2(0 參數結構) = {chi2_s:.4f} (dof 10)")
print(f"  chi2(2 參數自由) = {chi2_f:.4f} (dof 8)")
print(f"  Delta-chi2 = {dchi:.4f} (2 額外參數) -> p = {p_dchi:.4f}")
check("2 參數 fit 冇顯著改善 (p > 0.05) ⟹ 數據唔約束指數", p_dchi > 0.05, f"(p={p_dchi:.3f})")

# ---------------- 3. 密度基準 (look-elsewhere) ----------------
print("\n[3] 密度基準 (canonical pool, MC N=2e5, seed=20260926)")
print(f"  {'目標':<26}{'值':>10}{'dev_obs':>10}{'d_med':>9}{'q_obs':>8}{'hits':>6}  判定")
results = {}
targets = [
    ("gamma_fit (O54 fit)", 0.25812150940979006, 8 / 31, 0.02, 5.0),
    ("C_fit (O54 fit)", 0.040032822093017055, 1 / 25, 0.02, 5.0),
    ("p_CR = 2.7 (178/66)", 2.7, 178 / 66, 1.0, 6.0),
    ("f_sec exponent 0.33", 0.33, 1 / 3, 0.05, 3.0),
]
for name, tgt, cand, lo, hi in targets:
    nS, dev_obs, d_med, q_obs, hits, top = baseline(POOL_CANON, tgt, cand, lo, hi)
    results[name] = dict(target=tgt, candidate=cand, N_search=nS, dev_obs=dev_obs,
                         d_med=d_med, q_obs=q_obs, n_hits=hits,
                         top5=[(round(d, 6), l, round(v, 6)) for d, l, v in top])
    print(f"  {name:<26}{tgt:>10.5f}{dev_obs*100:>9.4f}%{d_med*100:>8.4f}%{q_obs:>8.3f}{hits:>6}  {grade(q_obs)}")

print("\n  最接近 gamma_fit 嘅 5 個結構式 (canonical pool):")
for d, l, v in results["gamma_fit (O54 fit)"]["top5"]:
    print(f"    dev {d*100:>7.4f}%   {l} = {v:.6f}")
print("  最接近 C_fit 嘅 5 個結構式:")
for d, l, v in results["C_fit (O54 fit)"]["top5"]:
    print(f"    dev {d*100:>7.4f}%   {l} = {v:.6f}")

q_g = results["gamma_fit (O54 fit)"]["q_obs"]
q_C = results["C_fit (O54 fit)"]["q_obs"]
q_p = results["p_CR = 2.7 (178/66)"]["q_obs"]
check("gamma = 8/31 唔可辨識 (q_obs > 5%)", q_g > 0.05, f"(q={q_g:.3f})")
check("C = 1/25 唔可辨識 (q_obs > 5%)", q_C > 0.05, f"(q={q_C:.3f})")
check("p_CR = 2.7 冇唯一結構 (q_obs > 5%)", q_p > 0.05, f"(q={q_p:.3f})")
q_s = results["f_sec exponent 0.33"]["q_obs"]
check("f_sec 指數 0.33 亦唔可辨識 (docs/01 已標 fit 參數, 此處確認)", q_s > 0.05, f"(q={q_s:.3f})")

# ---------------- 4. 池敏感度 ----------------
print("\n[4] 池敏感度 (同一目標 gamma_fit, 三個池)")
pool_res = {}
for pname, P in (("canonical (34)", POOL_CANON), ("O119 script04 (26)", POOL_O119), ("minimal (12)", POOL_MIN)):
    nS, dev_obs, d_med, q_obs, hits, top = baseline(P, 0.25812150940979006, 8 / 31, 0.02, 5.0)
    pool_res[pname] = dict(N_search=nS, dev_obs=dev_obs, d_med=d_med, q_obs=q_obs, n_hits=hits)
    print(f"  {pname:<22} N_search={nS:>7}  d_med={d_med*100:.4f}%  q_obs={q_obs:.3f}  hits={hits}  {grade(q_obs)}")
check("三個池全部都 q_obs > 5% (結論池無關)",
      all(v["q_obs"] > 0.05 for v in pool_res.values()),
      f"(min q = {min(v['q_obs'] for v in pool_res.values()):.3f})")

# ---------------- 5. 結論 ----------------
print("\n" + "=" * 74)
print("[5] 結論 (O208 密度基準)")
print("=" * 74)
print(f"""
  ★ docs/01 §4 聲稱 f_W = (1/25)·E^(8/31) 係「零參數結構閉合, chi2/dof=1.094」。
    本審計補做 O208 要求嘅密度基準:

    gamma = 8/31 : N_search = {results['gamma_fit (O54 fit)']['N_search']},
                   d_med = {results['gamma_fit (O54 fit)']['d_med']*100:.4f}%,
                   q_obs = {q_g:.3f}  -> {grade(q_g)}
       ⚠️ 隨機目標嘅中位命中 (d_med) 比 8/31 嘅偏差更細 ⟹ 8/31 唔係特別好嘅命中。
    C = 1/25     : q_obs = {q_C:.3f}  -> {grade(q_C)}
    p_CR = 2.7   : q_obs = {q_p:.3f}  -> {grade(q_p)}

  ★ 判定: 「零參數結構閉合」唔成立 —— 候選密度太高 (N_search ~ 1.1e5),
    任何目標值都會被隨機命中到 ~0.01% 級。docs/01 §4 應由 ✅ 降為 🔴
    (結構識別 = 後驗揀最靚, 唔係結構強迫)。

  ★ 仍成立嘅結構內容 (唔受本審計影響):
    - 運動學窗口 (只出 e+e-) — 見 script 12 強化版
    - 產生率譜指數 2 (gamma_n = omega_n^2 恆等)
    - 衰變寬度 Gamma(W->ee) (O37 Lagrangian 層)
    - 指數透明性 (見 script 11) — 反而解釋咗「點解 gamma 唔可能係結構」
""")
print(f"RESULT: {passed}/{total} PASS")

with open("data/10_density_baseline_audit.json", "w") as f:
    json.dump({
        "weighted_MLE": {"gamma": gamma_hat, "sigma_gamma": sig_gamma,
                         "C": C_hat, "sigma_C": C_hat * sig_lnC},
        "eight31_sigma_from_MLE": abs(8 / 31 - gamma_hat) / sig_gamma,
        "chi2_0par": chi2_s, "chi2_2par": chi2_f, "delta_chi2": dchi, "p_delta": p_dchi,
        "density_baseline": results,
        "pool_sensitivity": pool_res,
        "verdict": "gamma=8/31 及 C=1/25 唔可辨識 (q_obs>5%) -> 由 ✅ 降 🔴; p_CR=2.7 亦 🔴",
    }, f, indent=1, ensure_ascii=False)
print("✅ data/10_density_baseline_audit.json")
if passed < total:
    exit(1)
