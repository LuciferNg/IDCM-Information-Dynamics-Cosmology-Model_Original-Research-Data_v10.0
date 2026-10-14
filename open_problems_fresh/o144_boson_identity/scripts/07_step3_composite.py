#!/usr/bin/env python3
"""
O144-07 — 順序攻堅 Step 3: 複合態連結能量公理 (2026-09-17)
===========================================================
目標: 質子/膠球 = 複合態 (非節點模式 m = M₀×γ_n×C_f)。
先驗公理候選: 連結能量 = 玻色子扇區 (φ8) 結構量的自相交。

候選算子集 L (全部 φ-group 語言, 零新常數):
  X ∈ {Φ 值} ∪ {N_φ8 × Φ 值} ∪ {Σφ8 × Φ 值} ∪ {N_φ8×Σφ8} ∪ {Σφ8²} ∪ {N_φ8²}
  (Φ 值 16 個, N_φ8=5, Σφ8=17)

預言:
  膠球 (純連結凝聚, 無節點): m_g = M₀ × X
  質子 (3 節點 + 連結):       m_p = M₀ × (γ₁×64 + X')  — 或直接 M₀ × X

判決: MC 顯著性 — 算子空間 ~50, 目標 2 個, 期望隨機命中多少?
      85 = N_φ8×Σφ8 命中膠球是否顯著?
"""
import json, math, random, sys

M0 = 27.9009
phi = (1 + math.sqrt(5)) / 2
random.seed(20260917)
def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'

G1, G2 = [1, 5, 9], [0, 1, 3, 4, 6, 7]
Phi = sorted({1 + x1 * x2 for x1 in G1 for x2 in G2})
S_phi8, N_phi8, N_phi6, N_phi12 = 17, 5, 2, 28
Nd, B, Ngen = 44, 4, 3

targets = {"p": 938.2720813, "X(2370)": 2376.3}

# 連結能量算子集 (φ-group 語言)
L_ops = set()
for v in Phi:
    L_ops.add(v)                    # Φ 值
    L_ops.add(N_phi8 * v)           # N_φ8 × Φ
    L_ops.add(S_phi8 * v)           # Σφ8 × Φ
L_ops.update({N_phi8 * S_phi8, S_phi8 ** 2, N_phi8 ** 2, N_phi12, N_phi12 + S_phi8})
L_ops = sorted(L_ops)
# 也含 γ 模式因子版本 (φ6 Nyquist γ₂₂=2, 全鏈 γ₄₄=4)
L_ops2 = sorted(set(L_ops) | {2 * v for v in L_ops} | {4 * v for v in L_ops})

print("=" * 76)
print("O144-07 Step 3: 複合態連結能量公理")
print("=" * 76)
print(f"  算子集 L ({len(L_ops)} 值, 無 γ 因子): {L_ops}")
print(f"  算子集 L' ({len(L_ops2)} 值, 含 γ₂₂/γ₄₄ 因子): 前幾個 {L_ops2[:10]}...")

for tag, ops in [("L (純 φ-group)", L_ops), ("L' (含 γ 因子)", L_ops2)]:
    print(f"\n[{tag}] 預言 m = M₀ × X")
    print(f"{'X':>6} | {'m_pred (MeV)':>12} | 目標")
    print("-" * 40)
    hits = {}
    for X in ops:
        m = M0 * X
        mark = ""
        for tname, T in targets.items():
            if abs(m - T) / T < 0.02:
                mark += f" ← {tname} ({abs(m-T)/T*100:.2f}%)"
                hits.setdefault(tname, []).append((X, m))
        if mark:
            print(f"{X:>6} | {m:>12.3f} |{mark}")
    if not hits:
        print("  (無 2% 內命中)")

    # MC 顯著性: 隨機 |L| 個算子, 對 2 目標的 1% 命中期望
    m_lo, m_hi = M0 * min(ops), M0 * max(ops)
    log_span = math.log10(m_hi / m_lo)
    N_MC = 2000
    mc = []
    for _ in range(N_MC):
        samp = [10 ** random.uniform(math.log10(m_lo), math.log10(m_hi)) for _ in range(len(ops))]
        c = sum(1 for T in targets.values() if any(abs(s - T) / T < 0.01 for s in samp))
        mc.append(c)
    mean = sum(mc) / N_MC
    std = (sum((x - mean) ** 2 for x in mc) / N_MC) ** 0.5
    actual = sum(1 for t in targets if any(abs(M0 * X - targets[t]) / targets[t] < 0.01 for X in ops))
    z = (actual - mean) / std if std > 0 else 0
    print(f"  MC: 隨機期望 {mean:.2f}±{std:.2f} 命中; 實際 {actual}; z = {z:.2f} "
          f"{'✅' if z >= 3 else '❌'}")

print("\n" + "=" * 76)
print("[判決]")
print("=" * 76)
print(f"""
1. 算子空間 |L| = {len(L_ops)}, |L'| = {len(L_ops2)} — 對 2 個目標, 隨機期望已 ~1 個命中
2. 85 = N_φ8×Σφ8 命中 X(2370) (0.20-1.8% 視目標值) — 但 L 中另有 N_φ8×Φ 值等
   大量候選, 命中不唯一且不顯著
3. 「質子 = γ₁×64 + X'」需要額外公理 (節點 64 = Φ[3,6] 的指派 + X' 的選擇) —
   兩步都是後驗
⟹ 判決: ❌ 連結能量算子空間太大, 無先驗唯一性; 85 是後驗挑選
   同源比 5/2 = N_φ8/γ₂₂ 有結構形式, 但 2.5327/2.5 = 1.3% 差 + 無先驗理由
⟹ Step 3 判決: ❌ 複合態連結能量公理不存在 (現有語言內)
""")

out = {
    "session": "2026-09-17 O144-07 Step3",
    "L_ops": L_ops,
    "L_ops_with_gamma": L_ops2,
    "hits_85": {"N_phi8*S_phi8": N_phi8 * S_phi8, "pred_MeV": M0 * N_phi8 * S_phi8,
                "target": "X(2370)", "dev_pct": abs(M0 * N_phi8 * S_phi8 - 2376.3) / 2376.3 * 100},
    "verdict": "link-energy operator space too large, no prior uniqueness; 85 post-hoc",
}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/07_step3_composite.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/07_step3_composite.json 已寫入")
sys.exit(0)
