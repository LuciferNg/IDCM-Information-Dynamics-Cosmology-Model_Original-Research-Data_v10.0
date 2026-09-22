#!/usr/bin/env python3
"""
O136 — Script 34: 質量標度檢驗 — A₅ 選出的 9 模式 vs 觀測質量
================================================================
A₅ 動差準則選出 9 模式: {1, 2, 3, 4, 5, 7, 9, 11, 13}
= 3 輕子 + 6 夸克 (數量匹配)

本 script 檢驗:
  1. 純 sin 比能否重現觀測質量比?
  2. m = M₀·sin(nπ/88) 的 M₀_eff 分佈
  3. 所有 9! 配對中最佳者
  4. 需要幾大的額外因子?
"""
import math, json, itertools
from pathlib import Path

Nd, B_, dimC = 44, 4, 3
phi = (1 + math.sqrt(5))/2
lnphi = math.log(phi)

# 觀測質量 (MeV) — PDG
mass = {
    "e": 0.510999, "mu": 105.6584, "tau": 1776.86,
    "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0,
}
M0 = 27.900915

A5_MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
def sn(n): return math.sin(n*math.pi/88)

print("=" * 96)
print("O136 Script 34: 質量標度檢驗 — A₅ 選出的 9 模式")
print("=" * 96)

# ═══ 1. 模式譜 ═══════════════════════════════════════
print(f"\n{'─'*96}")
print("1. A₅ 選出模式的 sin 譜")
print(f"{'─'*96}")

print(f"\n{'n':>3} {'sin(nπ/88)':>12} {'比 (n=1)':>10} {'L':>5} {'q':>4} {'M₀·sin (MeV)':>14}")
print("-" * 56)
for n in A5_MODES:
    L = Nd // math.gcd(n, Nd); q = n // math.gcd(n, Nd)
    print(f"{n:>3} {sn(n):>12.6f} {sn(n)/sn(1):>10.4f} {L:>5} {q:>4} {M0*sn(n):>14.4f}")

print(f"\n★ 譜範圍: {M0*sn(1):.4f} – {M0*sn(13):.4f} MeV (比 {sn(13)/sn(1):.3f}×)")
print(f"★ 觀測範圍: {min(mass.values()):.3f} – {max(mass.values()):.1f} MeV (比 {max(mass.values())/min(mass.values()):.0f}×)")
print(f"→ 🔴 譜範圍 {sn(13)/sn(1):.2f}× 遠細於觀測 {max(mass.values())/min(mass.values()):.0f}×")

# ═══ 2. ★ 關鍵檢驗: 純 sin 比 vs 觀測質量比 ═════════
print(f"\n{'─'*96}")
print("2. ★ 關鍵檢驗: 9 模式的純 sin 比 vs 觀測質量比")
print(f"{'─'*96}")

# 觀測質量比 (所有帶電費米子對)
particles = ["e","mu","tau","u","d","s","c","b","t"]
obs_ratios = {}
for a, b in itertools.combinations(particles, 2):
    obs_ratios[(a,b)] = mass[a]/mass[b]

# 9 模式的 sin 比
mode_ratios = {}
for i, j in itertools.combinations(A5_MODES, 2):
    mode_ratios[(i,j)] = sn(i)/sn(j)

print(f"\n觀測質量比數: {len(obs_ratios)}")
print(f"模式 sin 比數: {len(mode_ratios)}")

# 對每個觀測比, 找最佳模式比
print(f"\n{'─'*96}")
print("每個觀測比的最佳 9-模式匹配")
print(f"{'─'*96}")
print(f"\n{'觀測比':>10} {'值':>12} {'最佳模式對':>12} {'sin比':>10} {'偏差%':>10}")
print("-" * 60)
best_devs = []
for (a,b), t in sorted(obs_ratios.items(), key=lambda x: -x[1]):
    bd, bm = 1e9, None
    for (i,j), r in mode_ratios.items():
        d = abs(r/t - 1)
        if d < bd: bd, bm = d, (i,j,r)
    best_devs.append(bd*100)
    print(f"{a+'/'+b:>10} {t:>12.6f} {f'({bm[0]},{bm[1]})':>12} {bm[2]:>10.6f} {bd*100:>+10.4f}")

print(f"\n★ 最佳匹配偏差: 中位數 {sorted(best_devs)[len(best_devs)//2]:.3f}%, 最小 {min(best_devs):.3f}%")
print(f"★ 對照: O136 舊框架的最佳比 = 0.015%; 一般要求 < 0.5%")
print(f"→ {'🟢 可重現' if min(best_devs) < 0.5 else '🔴 唔能重現觀測質量比'}")

# ═══ 3. ★ M₀_eff 分佈 ════════════════════════════════
print(f"\n{'─'*96}")
print("3. ★ 若 m = M₀_eff·sin(nπ/88), 反解 M₀_eff")
print(f"{'─'*96}")

print(f"\n{'粒子':>6} {'質量 (MeV)':>12} {'模式 n':>8} {'M₀_eff (MeV)':>14} {'M₀_eff/M₀':>12}")
print("-" * 58)
# 按質量排序配對
sorted_p = sorted(particles, key=lambda p: mass[p])
for p, n in zip(sorted_p, A5_MODES):
    meff = mass[p]/sn(n)
    print(f"{p:>6} {mass[p]:>12.4f} {n:>8} {meff:>14.4f} {meff/M0:>12.2f}")

print(f"\n★ M₀_eff 跨度: {mass[sorted_p[0]]/sn(A5_MODES[0]):.3f} – {mass[sorted_p[-1]]/sn(A5_MODES[-1]):.1f} MeV")
print(f"★ 比 = {(mass[sorted_p[-1]]/sn(A5_MODES[-1]))/(mass[sorted_p[0]]/sn(A5_MODES[0])):.0f}×")
print(f"→ 🔴 需要 M₀_eff 變化 {((mass[sorted_p[-1]]/sn(A5_MODES[-1]))/(mass[sorted_p[0]]/sn(A5_MODES[0]))):.0f} 倍")

# ═══ 4. ★ 全配對搜索 (需要什麼額外因子?) ════════════
print(f"\n{'─'*96}")
print("4. ★ 全配對搜索: 哪個配對令 φ-power 最結構?")
print(f"{'─'*96}")

# 檢驗: 存在配對使 m_p = M₀ sin(n) φ^{k_p}, k_p 為結構數?
results = []
for perm in itertools.permutations(A5_MODES):
    ks = [math.log(mass[p]/(M0*sn(n)))/lnphi for p, n in zip(sorted_p, perm)]
    # 度量: 與最近結構數的距離
    score = 0
    for k in ks:
        # 結構數候選: 半整數, 整數, n/2, n
        cands = [round(k*2)/2, round(k), round(k*2)/2]
        score += min(abs(k-c) for c in cands)
    results.append((score, perm, ks))

results.sort(key=lambda x: x[0])
print(f"\n搜索空間: 9! = {math.factorial(9)} 配對")
print(f"\n最佳 5 個配對 (按 φ-指數接近半整數/整數):")
print(f"\n{'#':>3} {'score':>8} {'配對 (模式→粒子)':>40} {'φ-指數':>40}")
print("-" * 96)
for i, (sc, perm, ks) in enumerate(results[:5]):
    pair_str = " ".join(f"{p}:{n}" for p, n in zip(sorted_p, perm))
    k_str = " ".join(f"{k:.2f}" for k in ks)
    print(f"{i:>3} {sc:>8.3f} {pair_str:>40} {k_str:>40}")

print(f"\n★ 最佳 score = {results[0][0]:.3f} (平均每粒子 {results[0][0]/9:.4f})")
print(f"→ {'🟢 存在結構配對' if results[0][0]/9 < 0.05 else '🔴 無結構配對 (φ-指數唔接近整數/半整數)'}")

# ═══ 5. 判決 ════════════════════════════════════════
print(f"\n{'─'*96}")
print("5. 判決")
print(f"{'─'*96}")

print(f"""
A₅ 選擇律的成就:
  ✅ 9 個模式 = 3 輕子 + 6 夸克 (數量精確匹配)
  ✅ 完全質量無關 (只用 A₅ 幾何動差結構)

A₅ 選擇律的失敗:
  🔴 純 sin 比最佳偏差 {min(best_devs):.3f}% (O136 舊框架 0.015%)
  🔴 譜範圍只有 {sn(13)/sn(1):.2f}×, 觀測需 {max(mass.values())/min(mass.values()):.0f}×
  🔴 M₀_eff 需變化 {((mass[sorted_p[-1]]/sn(A5_MODES[-1]))/(mass[sorted_p[0]]/sn(A5_MODES[0]))):.0f} 倍

★ 結論: A₅ 選擇律給出正確的【模式數】但唔給出【質量標度】
  → 模式選擇與質量標度確實係兩個獨立環節
  → 且 A₅ 選出的模式集與觀測質量比【不相容】
""")

# ═══ 6. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
with open(data_dir / "34_mass_scale_test.json", "w") as f:
    json.dump({
        "a5_modes": A5_MODES,
        "mass_ordered_particles": sorted_p,
        "spectrum_range_ratio": sn(13)/sn(1),
        "observed_range_ratio": max(mass.values())/min(mass.values()),
        "best_mode_match_dev_pct": min(best_devs),
        "median_best_dev_pct": sorted(best_devs)[len(best_devs)//2],
        "best_pairing": {"perm": list(results[0][1]), "ks": results[0][2], "score": results[0][0]},
        "verdict": "A₅ 選擇律給出正確模式數 (9) 但唔給出質量標度; 模式集與觀測質量比不相容",
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/34_mass_scale_test.json")