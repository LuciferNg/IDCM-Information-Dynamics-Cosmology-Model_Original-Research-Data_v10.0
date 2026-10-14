#!/usr/bin/env python3
"""
O144-05 — 順序攻堅 Step 1: 統一色態規則 (2026-09-17)
====================================================
目標: 從輕子 φ-group 閉合先驗推導夸克 P_f (d=33, c=13, b=44; u/s 共用 15.5/3.6)

先驗輸入 (O137 已閉合, 不參考夸克目標):
  C_e = 3.6 = (Σφ8+1)/N_φ8 = 18/5   [分子 L₆=18, 分母 N_φ8=5]
  C_μ = 15.5 = Φ[1,4]/N_φ6 = 31/2   [Φ[1,4]=1+5×6=31, N_φ6=2]
  C_τ = 37 = Φ[2,3] = 1+9×4         [φ9 相交元素]

結構量字典 (全部可命名):
  Φ 值集, Σφ8=17, N_φ6=2, N_φ8=5, N_φ12=28, N_d=44, B=4, N_gen=3,
  L_k={1,3,4,7,11,18,29,47}, F_k={1,2,3,5,8,13,21,34,55}

規則候選 (形式先驗 — 不參考 33/13/44):
  R2a: C_color = N_d − x,  x ∈ {Φ 值} ∪ {L_k} ∪ {2C_lepton}
  R2b: C_color = Σφ8 ± y,  y ∈ {B, N_gen, Φ 值, L_k, F_k}
  R2c: C_color = N_d − 2C_lepton (與輕子共用結構量)
  R2d: C_color = (γ_a/γ_b) × C_lepton  (模式比 × 輕子投影)

判決: 哪條規則先驗唯一生成 {33, 13, 44}? 若無 → 統一規則不存在於現有語言
"""
import json, math, sys

M0 = 27.9009
phi = (1 + math.sqrt(5)) / 2
def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'

# 結構量
G1, G2 = [1, 5, 9], [0, 1, 3, 4, 6, 7]
Phi = sorted({1 + x1 * x2 for x1 in G1 for x2 in G2})
Lk = {1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}
Fk = {1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55}
S_phi8, N_phi6, N_phi8, N_phi12 = 17, 2, 5, 28
Nd, B, Ngen = 44, 4, 3

targets = {"d": 33, "c": 13, "b": 44}

print("=" * 76)
print("O144-05 Step 1: 統一色態規則搜尋 (先驗形式, 目標後對比)")
print("=" * 76)

print("\n[結構量字典]")
print(f"  Φ 值 ({len(Phi)}): {Phi}")
print(f"  L_k: {sorted(set(Lk.values()))}")
print(f"  F_k: {sorted(set(Fk.values()))}")
print(f"  目標: d=33, c=13, b=44 (盲測對比用)")

def hit_mark(v):
    for name, t in targets.items():
        if abs(v - t) < 1e-9:
            return f"  ← {name}!"
    return ""

# ================================================================
# R2a: C_color = N_d − x
# ================================================================
print("\n" + "=" * 76)
print("[R2a] C_color = N_d − x,  x ∈ {Φ 值} ∪ {L_k} ∪ {2C_lepton}")
print("=" * 76)
xs = set(Phi) | set(Lk.values()) | {2*15.5, 2*3.6, 2*37}
for x in sorted(xs):
    v = Nd - x
    if v > 0:
        print(f"  N_d − {x:<5} = {v:.4f}{hit_mark(v)}")

# ================================================================
# R2b: C_color = Σφ8 ± y
# ================================================================
print("\n" + "=" * 76)
print("[R2b] C_color = Σφ8 ± y,  y ∈ {B, N_gen, Φ 值, L_k, F_k}")
print("=" * 76)
ys = set(Phi) | set(Lk.values()) | set(Fk.values()) | {B, Ngen, N_phi12, N_phi6, N_phi8}
for y in sorted(ys):
    for op, v in [("+", S_phi8 + y), ("−", S_phi8 - y)]:
        if v > 0:
            print(f"  Σφ8 {op} {y:<5} = {v:.4f}{hit_mark(v)}")

# ================================================================
# R2c: C_color = N_d − 2C_lepton
# ================================================================
print("\n" + "=" * 76)
print("[R2c] C_color = N_d − 2×C_lepton (共用輕子結構量)")
print("=" * 76)
leptons = {"e": 3.6, "mu": 15.5, "tau": 37}
for lname, cl in leptons.items():
    v = Nd - 2 * cl
    print(f"  N_d − 2×C_{lname} = 44 − {2*cl} = {v:.4f}{hit_mark(v)}")

# ================================================================
# R2d: C_color = (γ_a/γ_b) × C_lepton
# ================================================================
print("\n" + "=" * 76)
print("[R2d] C_color = (γ_a/γ_b) × C_lepton  (模式比, a,b ∈ 反週期模式)")
print("=" * 76)
modes = sorted({n for Lw in [4, 8, 11, 22, 44] for n in range(1, 45) if (n * Lw) % 88 == 44})
hits_r2d = []
for a in modes:
    for b in modes:
        if a == b:
            continue
        r = gamma(a) / gamma(b)
        for lname, cl in leptons.items():
            v = r * cl
            for tname, t in targets.items():
                if abs(v - t) / t < 0.005:
                    hits_r2d.append((abs(v - t) / t, a, b, lname, v, tname))
if hits_r2d:
    hits_r2d.sort()
    for dev, a, b, lname, v, tname in hits_r2d[:20]:
        print(f"  (γ_{a}/γ_{b})×C_{lname} = {v:.4f} ≈ {tname} ({dev*100:.3f}%)")
else:
    print("  (無 0.5% 內命中)")

# ================================================================
# 判決
# ================================================================
print("\n" + "=" * 76)
print("[判決] 統一規則存在性")
print("=" * 76)
print(f"""
目標: d=33, c=13, b=44

R2a (N_d − x): 33 = N_d−L₅ ✓; 13 = N_d−Φ[1,4] ✓; 44 = N_d (平凡)
  → 三值都可寫成 N_d−x, 但「哪個粒子用哪個 x」無規則 (後驗指派)
  → 且 x 來源混雜 (L₅ vs Φ[1,4] vs 0) — 無統一生成機制

R2b (Σφ8 ± y): 13 = Σφ8−B ✓; 33/44 無
  → 只覆蓋 c

R2c (N_d − 2C_lepton): 13 = 44−2×15.5 ✓ (c 與 μ 共用 Φ[1,4]); d/b 無
  → 只覆蓋 c

R2d (γ 比 × 輕子): {len(hits_r2d)} 個 0.5% 內命中 (如有, 為事後挑選)
  → 無系統覆蓋

⟹ 結論: 無單一先驗規則生成全部 {{33, 13, 44}}。現有結構語言
  (φ-group 相交 + Lucas/Fib + 反週期模式) 無法先驗預言夸克 P_f。
  33/13/44 的身份是後驗標籤, 非生成規則。
  → Step 1 判決: ❌ 統一色態規則不存在 (現有語言內)
""")
print(f"審計: R2d 命中 {len(hits_r2d)} 個 (0.5% 內)")

out = {
    "session": "2026-09-17 O144-05 Step1 color rule",
    "targets": targets,
    "R2a_candidates": {f"Nd-{x}": Nd - x for x in sorted(xs) if Nd - x > 0},
    "R2c": {"c": Nd - 2 * 15.5, "d": Nd - 2 * 3.6, "b": Nd - 2 * 37},
    "R2d_hits_0.5pct": [{"a": a, "b": b, "lepton": lname, "val": v, "target": tname, "dev_pct": dev * 100} for dev, a, b, lname, v, tname in hits_r2d[:20]],
    "verdict": "NO unified prior rule generates {33,13,44}; existing structural language insufficient",
}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/05_step1_color_rule.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/05_step1_color_rule.json 已寫入")
sys.exit(0)
