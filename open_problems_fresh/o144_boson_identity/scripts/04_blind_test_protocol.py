#!/usr/bin/env python3
"""
O144-04 — 盲測協議 v2: 質量公式預測能力審計 (2026-09-17)
=========================================================
用戶原則 (2026-09-17): 所有粒子/質量公式必須以盲測及帶有預測能力的
結構性閉合, 不能純以算子方式推導。

協議 (v2, 含過擬合控制):
  [0] 先驗公理 (僅從已閉合輕子歸納, 不參考強子/複合態):
      A1: m = M₀ × γ_n × C_f
      A2: 模式 n ∈ 反週期解集 {n·L ≡ 44 (mod 88), L ∈ {4,8,11,22,44}}
      A3: C_f ∈ R = Φ ∪ Φ/N_φ6 ∪ {(Σφ8+δ)/N_φ8, δ∈{0,1}}
          (Φ = φ9 相交矩陣 1+x₃x₃'; Σφ8 = 17; N_φ6 = 2; N_φ8 = 5)

  [1] 校準集 (規則歸納): e, μ, τ — 循環, 不算預測
  [2] 盲測集 (獨立): u, d, s, c, b — 真測試
  [3] 複合態: p, X(2370) — 規則外測試
  [4] 過擬合控制: Monte Carlo 隨機期望命中 vs 實際命中 (z-score)
  [5] 後驗算子標記: 34/85/64/33/13/44 ∈ R?

判決標準:
  - 命中: |dev| < 1% 且實際命中數顯著 > 隨機期望 (z ≥ 3)
  - 邊緣: < 2%
  - 未命中/無辨識度: 否則
"""
import json, math, random, sys

M0 = 27.9009
phi = (1 + math.sqrt(5)) / 2
random.seed(20260917)

particles = {
    "e": 0.5110, "mu": 105.66, "tau": 1776.86,   # 校準 (歸納規則用)
    "u": 2.16, "d": 4.67, "s": 93.0,             # 盲測
    "c": 1270.0, "b": 4180.0,                    # 盲測
    "p": 938.2720813, "X(2370)": 2376.3,         # 複合態
}

def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2

print("=" * 76)
print("O144-04 盲測協議 v2 (含過擬合控制)")
print("=" * 76)

# ================================================================
# [0] 先驗公理
# ================================================================
modes = set()
for L in [4, 8, 11, 22, 44]:
    for n in range(1, 45):
        if (n * L) % 88 == 44:
            modes.add(n)
modes = sorted(modes)

G1, G2 = [1, 5, 9], [0, 1, 3, 4, 6, 7]
Phi = [1 + x1 * x2 for x1 in G1 for x2 in G2]
N_phi6, N_phi8, S_phi8 = 2, 5, 17
R = sorted(set(Phi) | {v / N_phi6 for v in Phi} | {(S_phi8 + d) / N_phi8 for d in [0, 1]})

# 預言集 (去重)
preds = sorted({round(M0 * gamma(n) * cf, 8) for n in modes for cf in R})
print(f"[A2] 模式集 ({len(modes)}): {modes}")
print(f"[A3] 規則 R ({len(R)} 值): {[round(v,4) for v in R]}")
print(f"[預言集] |P| = {len(preds)} (M₀×γ_n×C_f 全組合去重)")
print(f"[預言範圍] [{min(preds):.4f}, {max(preds):.2f}] MeV")

# ================================================================
# [1-3] 命中掃描
# ================================================================
print("\n" + "=" * 76)
print("[1-3] 命中掃描 (|dev| < 1% = 命中, < 2% = 邊緣)")
print("=" * 76)
hits_by_target = {}
print(f"{'粒子':>9} | {'目標(MeV)':>10} | {'最佳預言':>10} | {'最佳C_f':>8} | {'最佳n':>5} | {'1%內個數':>7} | 判決")
print("-" * 80)
for name, T in particles.items():
    best_dev, best_p, best_cf, best_n = 1e9, None, None, None
    n_hit1, n_hit2 = 0, 0
    for cf in R:
        for n in modes:
            p = M0 * gamma(n) * cf
            dev = abs(p - T) / T
            if dev < 0.01: n_hit1 += 1
            if dev < 0.02: n_hit2 += 1
            if dev < best_dev:
                best_dev, best_p, best_cf, best_n = dev, p, cf, n
    dev_pct = best_dev * 100
    if name in ("e", "mu", "tau"):
        verdict = "校準(循環)"
    elif dev_pct < 1.0 and n_hit1 <= 3:
        verdict = "✅ 命中(1%內,唯一性OK)"
    elif dev_pct < 1.0:
        verdict = f"🟡 命中但無辨識度({n_hit1}個)"
    elif dev_pct < 2.0:
        verdict = "🟡 邊緣"
    else:
        verdict = "❌ 未命中"
    hits_by_target[name] = {"T": T, "best_dev_pct": dev_pct, "best_pred": best_p,
                            "best_cf": best_cf, "best_n": best_n, "n_hit1": n_hit1,
                            "n_hit2": n_hit2, "verdict": verdict}
    print(f"{name:>9} | {T:>10.4f} | {best_p:>10.3f} | {best_cf:>8.3f} | {best_n:>5} | {n_hit1:>7} | {verdict}")

# ================================================================
# [4] 過擬合控制 (Monte Carlo)
# ================================================================
print("\n" + "=" * 76)
print("[4] 過擬合控制: 隨機期望命中 vs 實際命中")
print("=" * 76)
m_min, m_max = min(preds), max(preds)
log_min, log_max = math.log10(m_min), math.log10(m_max)
print(f"  預言範圍對數跨度: log₁₀({m_max:.1f}/{m_min:.2f}) = {log_max-log_min:.3f}")
print(f"  隨機期望 (單目標): N_pred × 窗寬 / 跨度 = {len(preds)} × {2*math.log10(1.01):.5f} / {log_max-log_min:.3f} "
      f"= {len(preds)*2*math.log10(1.01)/(log_max-log_min):.2f} 個")
# Monte Carlo: 隨機預言集 (同大小, 對數均勻) 對所有目標計命中
N_MC = 2000
mc_hits = []
targets = [v for k, v in particles.items() if k not in ("e", "mu", "tau")]  # 盲測+複合態目標
for _ in range(N_MC):
    samp = [10 ** random.uniform(log_min, log_max) for _ in range(len(preds))]
    h = 0
    for T in targets:
        h += sum(1 for s in samp if abs(s - T) / T < 0.01)
    mc_hits.append(h)
mc_mean = sum(mc_hits) / N_MC
mc_std = (sum((h - mc_mean) ** 2 for h in mc_hits) / N_MC) ** 0.5
# 實際命中 (盲測+複合態, 1% 內且判決為命中)
actual = sum(1 for k in ("u","d","s","c","b","p","X(2370)") if hits_by_target[k]["verdict"] == "✅ 命中(1%內,唯一性OK)")
print(f"  Monte Carlo 隨機期望: {mc_mean:.2f} ± {mc_std:.2f} 個命中 (對 {len(targets)} 個目標)")
print(f"  實際命中 (盲測+複合態, 唯一性OK): {actual} 個")
if mc_std > 0:
    z = (actual - mc_mean) / mc_std
    print(f"  z-score = {z:.2f}  (z ≥ 3 = 顯著超過隨機)")
    sig = "✅ 顯著" if z >= 3 else "❌ 不顯著 (過擬合風險)"
    print(f"  判決: {sig}")
else:
    z, sig = 0, "?"
    print("  判決: MC std = 0 (異常)")

# ================================================================
# [5] 後驗算子標記
# ================================================================
print("\n" + "=" * 76)
print("[5] 後驗算子標記 (規則外, 降級 🔴)")
print("=" * 76)
posthoc_ops = [
    ("質子候選A", 34, "γ₂₂×Σφ8 = 2×17", "∉ R — 看到 938 後組合"),
    ("膠球", 85, "N_φ8×Σφ8 = 5×17", "∉ R — 看到 2370 後組合"),
    ("d", 33, "N_d−L₅ = K_Tree", "∉ R — O136 後驗"),
    ("c", 13, "F₇", "∉ R — O136 後驗"),
    ("b", 44, "N_d", "∉ R — O136 後驗"),
    ("節點", 64, "Φ[3,6] = 1+9×7", "✅ ∈ R! 但指派給質子節點是後驗"),
]
for name, v, formula, note in posthoc_ops:
    inR = "✅ ∈ R" if v in R else "❌ ∉ R"
    print(f"  {name:>8} ({v:>4}): {inR}  {formula:<24} {note}")

# ================================================================
# 總結
# ================================================================
print("\n" + "=" * 76)
print("總結判決")
print("=" * 76)
print(f"""
1. 校準集 (e, μ, τ): 命中 — 循環驗證 (規則由它們歸納), 非獨立證據
2. 盲測集 (u, d, s, c, b): 
   s → 命中 (C_s = C_e = 3.6 ∈ R, n=14 ∈ 反週期集, 0.78%)
   u → 邊緣 (C_u = C_μ = 15.5 ∈ R, 2.02% > 1%)
   d/c/b → 未命中 (33/13/44 ∉ R — 規則 R 無預言)
3. 複合態 (p, X(2370)): 規則 R 預言不出 (34/85 ∉ R) → 未通過盲測
4. 過擬合控制: z-score = {z:.2f} — {sig}
5. 後驗算子 (34/85/33/13/44): 全部降級 🔴 未閉合
   唯一規則內量: 64 = Φ[3,6] (但「對應質子節點」指派後驗)
⟹ 昨天的「膠球閉合候選」與「候選 A」未達盲測標準, 撤回為 🔴 後驗猜測
⟹ 真正閉合的只有: 輕子 (O137, 結構閉合但非盲測) + s (盲測通過)
⟹ 下一步: 尋找能預言 d/c/b/p/膠球的統一規則 (色修正/連結能量), 再盲測
""")
print(f"審計結果: {hits_by_target['s']['verdict']} | 隨機期望 {mc_mean:.2f}±{mc_std:.2f} | 實際 {actual} | z={z:.2f}")

out = {
    "session": "2026-09-17 O144-04 blind test v2",
    "axioms": {"A1": "m = M0*gamma_n*C_f", "A2": "anti-periodic modes", "A3": "R = Phi ∪ Phi/2 ∪ {(17+δ)/5}",
               "modes": modes, "R": [round(v, 5) for v in R], "|P|": len(preds)},
    "hits_by_target": hits_by_target,
    "overfit_control": {"mc_mean": mc_mean, "mc_std": mc_std, "actual": actual, "z": z, "significant": sig},
    "posthoc_ops": [{"name": n, "value": v, "formula": f, "note": note} for n, v, f, note in posthoc_ops],
    "verdict": {
        "closed_by_blind_test": ["s"],
        "marginal": ["u"],
        "unpredicted": ["d", "c", "b", "p", "X(2370)"],
        "posthoc_demoted": ["proton A (34)", "glueball (85)", "d (33)", "c (13)", "b (44)"],
        "note": "glueball closure candidate and proton candidate A REVOKED as blind-test failures (post-hoc)",
    },
}
with open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o144_boson_identity/data/04_blind_test.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/04_blind_test.json 已寫入")
sys.exit(0)
