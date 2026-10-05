#!/usr/bin/env python3
"""
O136 — Script 50: 驗證 Gemini 提案「質量 = 觀察的代價 m ∝ 1/|⟨O|n⟩|²」
================================================================================
Gemini 提案要點:
  (1) 質量 = 資訊從系統跨越邊界到觀察者嘅能量代價 (關係量子力學)
  (2) 巨大跨度 (3.4e5×) 來自【機率連乘】P = Π p_i (穿透 k 層網絡)
  (3) 不規則形狀來自【模式與觀察者基準點之拓撲投影角度】
  (4) 具體處方: 定義 |O⟩ = A₅ Node 0 (冷斑 ICRS) 或 Lucas 基準態
      m(n) ∝ 1/|⟨O|n⟩|²
  (5) 唔需要新常數

本 script 逐項驗證。已有結果對照:
  * 乘積型可達任意範圍 → docs/27 §一 🟢 (Gemini 第 (2) 點正確)
  * 位置算子 = 精確 Z₂-奇耦合 → docs/25 🟢
  * 二階自能 RMS 0.5873 (最佳, 未閉合) → docs/25
  * 純冪律不可能 (α 跨度 42.6×) → docs/26
"""
import numpy as np, math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
PHI = (1+math.sqrt(5))/2
ND = 44; M9 = [1,2,3,4,5,7,9,11,13]
MASS = {"e":0.510999,"mu":105.6584,"tau":1776.86,
        "u":2.16,"d":4.67,"s":93.4,"c":1270.0,"b":4180.0,"t":172690.0}
SP = sorted(MASS, key=lambda p: MASS[p])
LM = np.array([math.log(MASS[p]) for p in SP])

A5F = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt")
A5 = []
for ln in A5F.read_text().strip().splitlines():
    a = ln.split()
    if len(a) >= 2: A5.append((float(a[0]), float(a[1])))
v = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
               math.cos(math.radians(d))*math.sin(math.radians(r)),
               math.sin(math.radians(d))] for r,d in A5])

print("=" * 96)
print("O136 Script 50: 驗證 Gemini 提案 (質量 = 觀察的代價)")
print("=" * 96)

# ═══ 1. ★ 9 個模式與 Node 0 嘅幾何距離 (用戶直接提問) ═══
print(f"\n{'─'*96}\n1. ★ A₅ Node 0 與其餘節點之幾何距離 (用戶提問)\n{'─'*96}")
n0 = v[0]
beta = np.arccos(np.clip(v @ n0, -1, 1))          # 弧度
bd = np.degrees(beta)
print(f"  Node 0 (冷斑) = {A5[0]}")
print(f"  β_i 分佈: min = {bd[1:].min():.4f}°, max = {bd.max():.4f}°, 中位 = {np.median(bd[1:]):.4f}°")
u = np.unique(np.round(bd, 6))
print(f"  相異 β 值 ({len(u)} 個): {[round(x,3) for x in u[:12]]}{' ...' if len(u)>12 else ''}")
# 最近/最遠
i_min = int(np.argsort(bd[1:])[0]) + 1
i_max = int(np.argmax(bd))
print(f"  最近節點: #{i_min} β = {bd[i_min]:.4f}°   最遠: #{i_max} β = {bd[i_max]:.4f}°")

print(f"\n  ★ 關鍵: Node 0 自身 β₀ = 0 ⟹ c_{{0,n}} = cos²(n·0/2) = 1 對所有 n")
print(f"  ⟹ 以 Node 0 為 |O⟩ 之 ⟨O|n⟩ ≡ 1 (退化) ⟹ m(n) ∝ 1/1 = 常數 🔴")

# ═══ 2. 模式 n 在 A₅ 上嘅「座標 / 相角」 ═══
print(f"\n{'─'*96}\n2. 9 個模式在 A₅ 上嘅投影結構\n{'─'*96}")
C = {}
for n in M9:
    c = np.cos(n*beta/2)**2
    C[n] = c
print(f"\n{'n':>3} {'Σ_i c':>9} {'max c':>8} {'argmax β':>10} {'⟨c⟩/max':>9} {'有效節點數':>11}")
print("-" * 56)
for n in M9:
    c = C[n]
    s = float(c.sum())
    mx = float(c.max()); am = float(bd[int(np.argmax(c))])
    neff = float((c.sum()**2)/np.sum(c**2))
    print(f"{n:>3} {s:>9.4f} {mx:>8.4f} {am:>10.4f} {s/60/mx:>9.4f} {neff:>11.3f}")
print("\n  ★ Σ_i c_{i,n} 只有 2 個值: 30 (奇 n ≤ 14) / 20 (偶 n ≤ 4)")
print(f"  ⟹ 無法分辨 9 個質量 🔴")

# ═══ 3. 逐個 |O⟩ 定義測試 m ∝ 1/|⟨O|n⟩|² ═══
print(f"\n{'─'*96}\n3. ★ 測試 m(n) ∝ 1/|⟨O|n⟩|² — 逐個 |O⟩ 定義\n{'─'*96}")

# 鏈模式 (D-D 44 site)
Nc = 44
xx = np.arange(1, Nc+1, dtype=float)
Psi = np.zeros((Nc, Nc))
for n in range(1, Nc+1):
    Psi[:, n-1] = np.sin(n*math.pi*xx/(Nc+1))
for n in range(Nc):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])

def rms_best(vals):
    v = np.abs(np.array(vals))
    if np.any(v <= 1e-300): return None
    X = np.log(v); best = (9e9, None, None)
    for perm in itertools.permutations(range(9)):
        Xp = X[list(perm)]
        A = np.vstack([np.ones(9), Xp]).T
        c, *_ = np.linalg.lstsq(A, LM, rcond=None)
        r = float(np.sqrt(np.mean((A@c-LM)**2)))
        if r < best[0]: best = (r, perm, float(c[1]))
    return best

cands = {}
# (a) |O⟩ = Node 0 (A₅) → ⟨O|n⟩ = c_{0,n} = 1
cands["(a) |O⟩=A₅ Node 0"] = [C[n][0] for n in M9]
# (b) |O⟩ = A₅ 均勻 (Σ c_{i,n}/60)
cands["(b) |O⟩=A₅ 均勻"] = [float(C[n].sum()/60) for n in M9]
# (c) |O⟩ = 最遠節點
i_far = int(np.argmax(bd))
cands["(c) |O⟩=A₅ 最遠節點"] = [float(C[n][i_far]) for n in M9]
# (d) |O⟩ = 世界扇區 (偶模式)
cands["(d) |O⟩=世界扇區"] = [1.0 if n % 2 == 0 else 0.0 for n in M9]
# (e) |O⟩ = 鏈基態 (n=1)
cands["(e) |O⟩=鏈基態 n=1"] = [abs(float(np.dot(Psi[:, n-1], Psi[:, 0]))) for n in M9]
# (f) |O⟩ = 鏈上 Node 0 對應格點 (site 1)
cands["(f) |O⟩=鏈 site 1"] = [abs(float(Psi[0, n-1])) for n in M9]
# (g) |O⟩ = 鏈上中央格點
cands["(g) |O⟩=鏈中央"] = [abs(float(Psi[Nc//2, n-1])) for n in M9]
# (h) 投影「代價」= 1/Σ_i c (資訊熵式)
cands["(h) 1/Σ_i c_{i,n}"] = [1.0/float(C[n].sum()) for n in M9]
# (i) 有效節點數之倒數
cands["(i) 1/N_eff"] = [float(np.sum(C[n]**2))/(C[n].sum()**2) for n in M9]
# (j) A₅ 投影之 Shannon 熵
cands["(j) A₅ 投影熵"] = []
for n in M9:
    p = C[n]/C[n].sum()
    cands["(j) A₅ 投影熵"].append(float(-np.sum(p*np.log(p+1e-300))))

print(f"\n{'|O⟩ 定義':>22} {'最佳 RMS':>10} {'α':>9} {'m 範圍':>12} {'判定':>8}")
print("-" * 68)
for name, vals in cands.items():
    vv = np.abs(np.array(vals))
    rng = (vv.max()/vv.min()) if vv.min() > 1e-300 else float('inf')
    if vv.min() <= 1e-300 or len(set(np.round(vv, 12))) < 3:
        print(f"{name:>22} {'退化/常數':>10} {'—':>9} {rng:>12.3g} {'🔴 不可用':>8}")
        continue
    b = rms_best(vals)
    if b is None: continue
    rms, perm, a = b
    ps = " ".join(f"{SP[i][0]}:{M9[perm[i]]}" for i in range(9))
    flag = '🟢' if rms < 0.3 else ('🟡' if rms < 0.8 else '🔴')
    print(f"{name:>22} {rms:>10.4f} {a:>9.4f} {rng:>12.3g} {flag:>8}")

print(f"\n★ 對照: |Δm| 二階自能 0.5873 | sin 0.8028 | 累積乘積 0.7106 | 上限 3.8588")
print(f"★ 所需 m 範圍 = {max(MASS.values())/min(MASS.values()):.3e}")

# ═══ 4. 機率連乘 (Gemini 第 (2) 點) ═══
print(f"\n{'─'*96}\n4. ★ 機率連乘 P = Π p_i (Gemini 第 (2) 點)\n{'─'*96}")
print(f"  已有結果 (docs/23, 27):")
print(f"    逐節點連乘 Σln cos² → RMS 2.1529; 路徑積分 sumM2 → 0.9482")
print(f"    累積乘積 Π_{{k≤n}} sin(kπ/88) → 0.7106 (最佳乘積)")
print(f"    Gap 本徵向量範圍 2.175e5× (對), 但 RMS 1.1765")
print(f"  ⟹ 🟢 Gemini 第 (2) 點【部分正確】: 乘積型確實給出正確【範圍】(docs/27 §一 已證)")
print(f"  ⟹ 🔴 但【形狀】未解決: 最佳乘積 RMS 0.7106 ≫ 閉合所需 <0.05")

# ═══ 5. 「唔需要新常數」檢驗 ═══
print(f"\n{'─'*96}\n5. ★ 「唔需要新常數」檢驗\n{'─'*96}")
print(f"  m(n) ∝ 1/|⟨O|n⟩|² 係【無量綱】嘅比值 → 必須乘一個量綱標度 M")
print(f"  已知: 二階自能擬合標度 C = 5.387e−05 MeV vs M₀ = 27.900915 MeV (差 5.2e5×)")
print(f"  已試: M₀ = 27.900915 MeV (O34, E_kchain × φ^{{47+37/528}})")
print(f"  ⟹ 🔴 Gemini 第 (5) 點【唔成立】: 需要量綱標度, 而現有標度唔匹配")

# ═══ 6. 保存 ═══
res = {}
for name, vals in cands.items():
    vv = np.abs(np.array(vals))
    if vv.min() <= 1e-300 or len(set(np.round(vv, 12))) < 3:
        res[name] = {"degenerate": True}; continue
    b = rms_best(vals)
    res[name] = {"rms": b[0], "alpha": b[2],
                 "pairing": {SP[i]: M9[b[1][i]] for i in range(9)},
                 "range": float(vv.max()/vv.min())}
with open(OUT/"50_gemini_proposal_verify.json", "w") as f:
    json.dump({
        "node0_geometry": {"beta_min_deg": float(bd[1:].min()), "beta_max_deg": float(bd.max()),
                           "beta_median_deg": float(np.median(bd[1:])),
                           "distinct_beta_count": int(len(u)),
                           "key_finding": "Node 0 自身 β₀=0 ⟹ c_{0,n}=1 ∀n (退化)"},
        "observer_definitions": res,
        "product_idea": {"status": "range OK (docs/27 §一), shape NOT solved",
                         "best_product_rms": 0.7106},
        "new_constants": {"verdict": "需要量綱標度; C=5.387e-5 MeV vs M₀=27.900915 MeV 差 5.2e5×"},
        "reference": {"2nd_order": 0.5873, "sin": 0.8028, "upper": float(LM.std())},
    }, f, ensure_ascii=False, indent=2)
print(f"\n✅ 寫入 data/50_gemini_proposal_verify.json")