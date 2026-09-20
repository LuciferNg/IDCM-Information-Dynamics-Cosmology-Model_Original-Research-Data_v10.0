#!/usr/bin/env python3
"""
O206 — Script 13: CY₃ 鏡頭 / 變焦效應 vs 映射層缺口 (α)
=========================================================
調律者指示 (2026-09-21):
  「費米子會經過CY3，有鏡頭焦距效應引起的質量變化，
    之前已經把RGE重新解釋為變焦效應」

上游框架 (唯讀):
  O156 docs/07: RGE = 【調焦定律】, 唔係流: θ(N) = atan(sin(7π/N)/sin(6π/N)), N = 焦距參數
                塔 {11,22,33,44,55,88,176} = 量子化焦距 detent
  O156 docs/09: 「鏡頭」就係 CY₃(36,98) 本身; detent 由 h¹¹ encode:
                55 = h¹¹+f_proj, 88 = 2(h¹¹+F₆), 176 = 4(h¹¹+F₆)
  O162 docs/02: 消色差定理 d²γ/dk² = 0 ⟺ k = 44 (中心模 = 自對偶錨 = μ²)
                色差閉式 γ(44+m) = 2 + 2sin(mπ/88) — 【冇 m² 項】= 二階消色差 EXACT
                失焦量 1/Δθ ≈ 469 = L₄·h̄ (h̄ = 67 = CY₃ 平均模數); 88−55 = 33 = K_tree

本 script 檢驗 (全部離散、框架導出, 唔係自由擬合):
  §A ★ 焦距 detent 掃描 — 重建每個 detent 之鏈譜 + 位置算子, 重擬合 m ↔ |Δm|
     N ∈ {33, 44, 55, 60, 88, 176} (O156 之量子化 detent 塔)
     ⟹ 質量梯用邊個 detent? (O156 判「質量比用 88」— 本節獨立檢驗)
  §B 色差檢驗 — O206 殘餘 vs 色差 a_n = 2sin((44−n)π/88) (O162 閉式)
  §C 失焦量檢驗 — O156/O162 之 469 = L₄·h̄ 是否出現喺質量殘餘結構
  §D 鏡頭因子擬合 — m_n = M₀|Δm_n|^α·(1 + c·a_n); c 顯著嗎? (含池子 null 紀律)
  §E 裁決
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from o206_lib import (NC, ND, MU2, A5_MODES, LM, MASS, E_ring44, V_position,
                      logscore, sum_V2_dE)

OUT = Path(__file__).parent.parent / "data"
checks = []


def chk(name, cond, detail=""):
    checks.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))


PAIR = [(1, "t"), (2, "b"), (3, "tau"), (4, "c"), (5, "mu"), (7, "s"), (9, "d"), (11, "u"), (13, "e")]
lm = np.array([math.log(MASS[p]) for _, p in PAIR])


def ols(X, y):
    A = np.column_stack([np.ones(len(y))] + ([X] if X.ndim == 1 else [X[:, i] for i in range(X.shape[1])]))
    b, *_ = np.linalg.lstsq(A, np.asarray(y, float), rcond=None)
    return b, A @ b


def build_detent(N):
    """重建 detent N 之鏈: ψ_n(i) = sin(nπi/(N+1)), X = diag(i−⟨i⟩), E_n = 4sin²(πn/N)"""
    x = np.arange(1, N + 1, dtype=float)
    P = np.zeros((N, N))
    for n in range(1, N + 1):
        P[:, n - 1] = np.sin(n * math.pi * x / (N + 1))
    for n in range(N):
        P[:, n] /= np.linalg.norm(P[:, n])
    V = P.T @ np.diag(x - x.mean()) @ P
    E = np.array([4 * math.sin(n * math.pi / N) ** 2 for n in range(1, N + 1)])
    return V, E


def dm_at(V, E, modes, N):
    out = []
    for n in modes:
        idx = [m for m in range(N) if m != n - 1 and (m - (n - 1)) % 2 == 1]
        dE = E[n - 1] - E[idx]
        if np.min(np.abs(dE)) < 1e-12:
            return None          # 反-parity 簡併 ⟹ |Δm| 發散 (結構上唔可行)
        aV2 = np.abs(V[n - 1, idx]) ** 2
        out.append(abs(float((aV2 / dE).sum())))
    return np.array(out)


print("=" * 100)
print("O206 Script 13: CY₃ 鏡頭 / 變焦效應 vs 映射層缺口 (α)")
print("=" * 100)

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§A ★ 焦距 detent 掃描 (O156 量子化 detent 塔)\n{'─'*100}")
print("""
  對每個 detent N 重建鏈 (ψ/ X / 譜) 再重擬合 ln m = c + α·ln|Δm|
  ⟹ 問: 質量梯住喺邊個焦距? (O156 判「質量比 = chain 觀察量, 焦距 88」)
""")
DETENTS = [22, 33, 44, 55, 60, 88, 176]
IDENT = {22: "2L₅", 33: "K_tree", 44: "N_d", 55: "h¹¹+f_proj", 60: "F₅·B·N_gen",
         88: "2(h¹¹+F₆)", 176: "4(h¹¹+F₆)"}
print(f"  {'detent N':>9} {'CY₃ 身份':>22} {'α':>10} {'RMS':>9} {'vs N=88':>9}")
print("  " + "-" * 64)
res_det = {}
excluded = {}
for N in DETENTS:
    V, E = build_detent(N)
    d = dm_at(V, E, A5_MODES, N)
    if d is None:
        excluded[N] = "γ_n = γ_(N−n) 反-parity 簡併 ⟹ |Δm| 發散 (奇 detent 結構上唔可行)"
        print(f"  {N:>9} {IDENT[N]:>22} {'—':>10} {'發散':>9} {'排除':>9}")
        continue
    b, pred = ols(np.log(d), lm)
    r = float(np.std(lm - pred))
    res_det[N] = {"alpha": float(b[1]), "rms": r}
    if 88 in res_det and N != 88:
        ratio = f"{r/res_det[88]['rms']:.4f}×"
    else:
        ratio = "—"
    print(f"  {N:>9} {IDENT[N]:>22} {b[1]:>10.6f} {r:>9.4f} {ratio:>9}")

best_det = min(res_det.items(), key=lambda kv: kv[1]["rms"])
print(f"\n  ★ 最佳 detent = {best_det[0]} ({IDENT[best_det[0]]}), RMS = {best_det[1]['rms']:.4f}")
print(f"  ★ 結構上排除之 detent: {list(excluded)} — {list(excluded.values())[0] if excluded else '—'}")

# ★ 可辨識性: detent 60 vs 88 之差異顯著嗎? (bootstrap N=2000, 同 α 一樣之檢驗)
rng_d = np.random.default_rng(13)
boot_rms = {N: [] for N in res_det}
dms = {}
for N in res_det:
    Vn, En = build_detent(N)
    dms[N] = dm_at(Vn, En, A5_MODES, N)
for _ in range(2000):
    idx = rng_d.integers(0, 9, 9)
    for N in res_det:
        bb, pp = ols(np.log(dms[N][idx]), lm[idx])
        boot_rms[N].append(float(np.std(lm[idx] - pp)))
sd60 = float(np.std(boot_rms[60]))
sd88 = float(np.std(boot_rms[88]))
d_6088 = abs(res_det[60]["rms"] - res_det[88]["rms"])
sd_diff = math.sqrt(sd60 ** 2 + sd88 ** 2)
z_6088 = d_6088 / sd_diff if sd_diff > 0 else 0.0
print(f"\n  ★ 可辨識性 (detent 60 vs 88):")
print(f"     RMS(60) = {res_det[60]['rms']:.4f} ± {sd60:.4f};  RMS(88) = {res_det[88]['rms']:.4f} ± {sd88:.4f}")
print(f"     |Δ| = {d_6088:.4f} vs σ_diff = {sd_diff:.4f}  ⟹  |Δ|/σ = {z_6088:.4f}")
chk("C1 [detent 掃描] detent 60 與 88 不可辨識 (|ΔRMS|/σ < 2) ⟹ 質量數據唔足以定焦距",
    z_6088 < 2.0,
    f"|Δ|/σ = {z_6088:.4f} ⟹ 最佳 detent 之身份不可辨識 (同 α 一樣)")
chk("C2 [detent 掃描] 無任何 detent 達到閉合門檻 (RMS < 0.05)",
    all(v["rms"] > 0.05 for v in res_det.values()),
    f"最佳 RMS = {best_det[1]['rms']:.4f}")
chk("C3 ★ [奇 detent] 55 與 33 結構上排除 (反-parity 簡併) ⟹ 質量梯必住偶 detent",
    set(excluded) >= {33, 55},
    f"排除 {sorted(excluded)} — 呢個係 sector 分離之【結構理由】(唔係經驗理由)")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§B 色差檢驗 (O162 閉式: γ(44+m) = 2 + 2sin(mπ/88), 冇 m² 項)\n{'─'*100}")
V88, E88 = V_position(), E_ring44()
b88, pred88 = ols(np.log(sum_V2_dE(E88, V88)), lm)
resid = lm - pred88
print(f"\n  基準: α = {b88[1]:.6f}, RMS = {float(np.std(resid)):.4f}")
aberr = np.array([2 * math.sin((44 - n) * math.pi / 88) for n, _ in PAIR])
print(f"\n  {'mode':>5} {'粒子':>6} {'m = 44−n':>9} {'色差 a_n':>10} {'殘餘':>9}")
print("  " + "-" * 44)
for (n, p), a, r in zip(PAIR, aberr, resid):
    print(f"  {n:>5} {p:>6} {44-n:>9} {a:>10.6f} {r:>9.4f}")
r_ab = float(np.corrcoef(aberr, resid)[0, 1])
print(f"\n  corr(色差, 殘餘) = {r_ab:+.4f}")
chk("C3 [色差] 殘餘與色差無顯著相關 (|r| < 0.67 = N=9 之 p<0.05 門檻)",
    abs(r_ab) < 0.67, f"r = {r_ab:+.4f} (需 |r| > 0.67)")

# 消色差點距離
m_dist = np.array([44 - n for n, _ in PAIR], dtype=float)
r_md = float(np.corrcoef(m_dist, resid)[0, 1])
print(f"  corr(|44−n|, 殘餘) = {r_md:+.4f}")
chk("C4 [消色差] 殘餘與「距消色差點 k=44 之距離」無顯著相關",
    abs(r_md) < 0.67, f"r = {r_md:+.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§C 失焦量檢驗 (O156/O162: 1/Δθ = 469 = L₄·h̄, h̄ = 67)\n{'─'*100}")
target = 469.0
print(f"\n  殘餘之特徵量:")
print(f"    殘餘跨度 = {resid.max()-resid.min():.6f}  倍數跨度 = {math.exp(resid.max()-resid.min()):.4f}×")
print(f"    殘餘 std = {float(np.std(resid)):.6f}")
for name, val in [("1/std(殘餘)", 1 / float(np.std(resid))),
                  ("1/跨度", 1 / (resid.max() - resid.min())),
                  ("exp(跨度)", math.exp(resid.max() - resid.min()))]:
    print(f"    {name:>16} = {val:.4f}  (vs 469: Δ {abs(val-469)/469*100:.2f}%)")
d469 = min(abs(1 / float(np.std(resid)) - target), abs(1 / (resid.max() - resid.min()) - target)) / target
chk("C5 [失焦量] 469 = L₄·h̄ 唔出現喺質量殘餘結構 (最小 Δ > 20%)",
    d469 > 0.20, f"最小相對偏差 = {d469*100:.2f}%")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§D 鏡頭因子擬合: m_n = M₀|Δm_n|^α·(1 + c·a_n)\n{'─'*100}")
ldm = np.log(sum_V2_dE(E88, V88))
b_lens, pred_lens = ols(np.column_stack([ldm, aberr]), lm)
rms_lens = float(np.std(lm - pred_lens))
c_lens = float(b_lens[2])
rng = np.random.default_rng(20260921)
boot_c = []
for _ in range(2000):
    idx = rng.integers(0, 9, 9)
    bb, _ = ols(np.column_stack([ldm[idx], aberr[idx]]), lm[idx])
    boot_c.append(bb[2])
sd_c = float(np.std(boot_c))
z_c = abs(c_lens) / sd_c if sd_c > 0 else 0.0
print(f"\n  擬合: c = {c_lens:+.6f} ± {sd_c:.6f}  (bootstrap N=2000);  |c|/σ = {z_c:.4f}")
print(f"  RMS: 無鏡頭因子 {float(np.std(resid)):.4f} → 有 {rms_lens:.4f} (改善 {float(np.std(resid))/rms_lens:.4f}×)")
chk("C6 [鏡頭因子] 色差項唔顯著 (|c|/σ < 2) ⟹ 色差唔解釋殘餘",
    z_c < 2.0, f"|c|/σ = {z_c:.4f}")

# ═══════════════════════════════════════════════════════════════
print(f"\n{'─'*100}\n§E 裁決 (script 13)\n{'─'*100}")
print(f"""
  ① ★ 焦距 detent 掃描: 最佳 detent = {best_det[0]} ({IDENT[best_det[0]]}), RMS = {best_det[1]['rms']:.4f}
     vs detent 88 (O156 判決) RMS = {res_det[88]['rms']:.4f};  |Δ|/σ = {z_6088:.4f}
     ⟹ 60 與 88 【不可辨識】— 質量數據唔足以定焦距 (同 α 一樣之可辨識性問題)
     ⟹ O156 之 sector 判決【既唔被確認亦唔被否證】— 數據無判別力
  ② ★★ 但得一個【結構性】結果: 奇 detent {sorted(excluded)} 結構上排除
     (γ_n = γ_(N−n) 落喺反 parity ⟹ resolvent 分母 = 0 ⟹ |Δm| 發散)
     ⟹ 質量梯【必須】住偶 detent ⟹ 55 (θ₂₃ 之家) 對質量【結構上不可用】
     ⟹ 呢個係 O156 sector 分離 (θ₂₃ 住 55 / 質量住 88) 之【結構理由】, 唔係經驗理由
  ③ 色差 (O162 閉式 a_n = 2sin((44−n)π/88)): corr(殘餘) = {r_ab:+.4f} ⟹ 唔顯著
     距消色差點 |44−n|: corr = {r_md:+.4f} ⟹ 唔顯著
  ④ 失焦量 469 = L₄·h̄ 唔出現喺質量殘餘結構 (最小 Δ {d469*100:.1f}%)
  ⑤ 鏡頭因子 (1 + c·a_n): c = {c_lens:+.6f} ± {sd_c:.6f}, |c|/σ = {z_c:.4f} ⟹ 唔顯著
  ⟹ 裁決: CY₃ 鏡頭/變焦框架【結構上一致】(並提供 sector 分離之結構理由 ②),
     但【唔解釋】O206 之質量殘餘 — 殘餘仍係 N=9 之統計噪聲 (docs/12 曲率檢驗一致)
     ⟹ 「變焦」解釋【焦距選擇 / sector 分離】, 唔係【殘餘】
""")

n_pass = sum(1 for _, ok in checks if ok)
print(f"{'='*100}\nRESULT: {n_pass}/{len(checks)} PASS\n{'='*100}")
for name, ok in checks:
    if not ok:
        print(f"  FAIL: {name}")

with open(OUT / "13_cy3_lens_vs_alpha.json", "w") as f:
    json.dump({
        "detent_scan": {str(k): v for k, v in res_det.items()},
        "detents_excluded_odd": {str(k): v for k, v in excluded.items()},
        "best_detent": best_det[0], "best_detent_rms": best_det[1]["rms"],
        "aberr_corr": r_ab, "achrom_dist_corr": r_md,
        "defocus_469_min_dev_pct": d469 * 100,
        "lens_factor_c": c_lens, "lens_factor_sigma": sd_c, "z_c": z_c,
        "baseline_alpha": float(b88[1]), "baseline_rms": float(np.std(resid)),
        "checks_pass": int(n_pass), "checks_total": len(checks),
    }, f, ensure_ascii=False, indent=2)
print("✅ 寫入 data/13_cy3_lens_vs_alpha.json")
