#!/usr/bin/env python3
"""
O62 八期 28: Toric 三重相交公式 — 從 cone 體積推導 κ
=====================================================
第一性原理 (Fulton): 
  κ_ijk = Σ_{σ ∈ maximal cones} [i,j,k ∈ σ] · vol(σ 由 v_i,v_j,v_k 生成)
  有向體積 (oriented volume) 求和

對 CY₃ toric variety (4D polytope, 3D cones):
  三重相交數 D_i·D_j·D_k = Σ_σ ε(σ) · det(v_i, v_j, v_k) / det(basis)

推導:
  1. 由 simplices 構建 maximal cones (3D, 4 射線)
  2. 對每個 triple (i,j,k): κ_ijk = Σ_{cone ⊇ {i,j,k}} ±det
  3. 比較同真實 κ: 完美匹配?
  4. 554 消去: κ=0 ⇔ 正負 det 完全對消

呢個先係真正嘅「第一性原理消去定理」:
  co-simplex 但 κ=0 (554) = 所有包含佢嘅 cone 體積對消
"""
import sys, os, math, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 28: Toric 三重相交公式")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"], dtype=float)  # 48×4
simplices = d["simplices"]
kappa36 = np.array(json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))["kappa"])[:36,:36,:36]

# ============ 1. Maximal cones (3D, 4 rays) ============
print("\n[1] Maximal cones")
cones = []
for s in simplices:
    for f in combinations(s, 4):
        cones.append(tuple(sorted(f)))
# 去重
cones = list(set(cones))
print(f"  maximal cones: {len(cones)}")

# 每個 cone 嘅體積基準: det(v_f1, v_f2, v_f3, v_f4) / 4!
# 對 3D cone: 揀 3 條射線 → 3×3 子行列式

# ============ 2. Toric κ 公式 ============
print("\n[2] Toric κ 計算")
# κ_ijk = Σ_{cone ∋ {i,j,k}} det(v_i, v_j, v_k, ·) 嘅正規化
# 正確公式 (4D polytope, 3D cone):
#   D_i·D_j·D_k = Σ_{σ} [i,j,k ⊆ σ] · (1/|det(v_σ1,v_σ2,v_σ3,v_σ4)|) · |det(v_i,v_j,v_k,w_σ)|
# 但更簡單: 用頂點做基準
# 標準做法: 揀任意 4 條線性獨立射線做 basis (例如頭 4 條),
# 每個 cone 由 3 條射線生成 (4 條射線中選 3 條線性獨立)

# 用頂點 (index 0-5) 做基準: 6 個頂點中揀 4 個線性獨立
# 直接做法: det 4×4 矩陣 (v_i, v_j, v_k, w) — w 係 cone 嘅第 4 條射線
# κ_ijk = Σ_{cone=(i,j,k,w)} det(v_i,v_j,v_k,w)  (需要正確 normalization)

# 先試: 對每個 cone (4 射線), 每個 triple 子集:
# det(v_a, v_b, v_c) 3×3 唔得 — 要 4D
# 用: κ_ijk = Σ_cone sign·|det4(v_i,v_j,v_k,v_l)| / |det4(v_a,v_b,v_c,v_d)|
# 其中 (v_a,v_b,v_c,v_d) 係 cone 嘅 4 條射線 (含 i,j,k 其中 3 條 + 第 4 條 l)

kappa_toric = np.zeros((36,36,36))
for c in cones:
    # cone 有 4 條射線
    rays = list(c)
    # 對 cone 內每個 triple 子集 (i,j,k 從 4 條射線選 3)
    for t in combinations(rays, 3):
        i, j, k = t
        if i >= 36 or j >= 36 or k >= 36:
            continue
        # 第 4 條射線
        l = [r for r in rays if r not in t][0]
        # det4(v_i, v_j, v_k, v_l)
        M = np.array([pts[i], pts[j], pts[k], pts[l]])
        det = np.linalg.det(M)
        # 有向貢獻 (唔取絕對值 — 有向體積!)
        kappa_toric[i,j,k] += det
        kappa_toric[i,k,j] += det
        kappa_toric[j,i,k] += det
        kappa_toric[j,k,i] += det
        kappa_toric[k,i,j] += det
        kappa_toric[k,j,i] += det

print(f"  κ_toric 非零: {np.count_nonzero(kappa_toric)}")

# ============ 3. 比較 ============
print("\n[3] κ_toric vs κ_real")
# 全同對角
match_diag = 0
for i in range(36):
    if abs(kappa_toric[i,i,i] - kappa36[i,i,i]) < 1e-6:
        match_diag += 1
print(f"  對角匹配: {match_diag}/36")
# 顯示頭幾個
print(f"  κ_real diag: {[kappa36[i,i,i] for i in range(8)]}")
print(f"  κ_toric diag: {[round(kappa_toric[i,i,i],1) for i in range(8)]}")

# 全體匹配率
tol = 1e-6
n_match = 0
n_total = 0
for i in range(36):
    for j in range(36):
        for k in range(36):
            n_total += 1
            if abs(kappa_toric[i,j,k] - kappa36[i,j,k]) < tol:
                n_match += 1
print(f"  全體匹配: {n_match}/{n_total} ({n_match/n_total*100:.2f}%)")
check("對角匹配 (κ_iii)", match_diag >= 30, f"({match_diag}/36)")

# ============ 4. 正規化 ============
print("\n[4] 正規化修正")
# 如果 det 有常數比例因子, 計 ratio
# 對非零對角: ratio = κ_real/κ_toric
ratios = []
for i in range(36):
    if abs(kappa_toric[i,i,i]) > 1e-8 and abs(kappa36[i,i,i]) > 1e-8:
        ratios.append(kappa36[i,i,i] / kappa_toric[i,i,i])
if ratios:
    r0 = ratios[0]
    print(f"  ratio[0] = {r0:.6f}")
    print(f"  ratios spread: min {min(ratios):.6f}, max {max(ratios):.6f}")
    check("比例一致?", max(abs(r/r0 - 1) for r in ratios) < 0.01, 
          f"(spread {max(abs(r/r0 - 1) for r in ratios)*100:.2f}%)")

# ============ 5. 554 消去 ============
print("\n[5] 554 消去 (有向對消)")
# 用校正後 κ_toric 檢查 co-simplex 中 κ=0
if ratios:
    scale = np.mean(ratios)
else:
    scale = 1.0
kappa_toric_scaled = kappa_toric * scale

# co-simplex (i≤j≤k)
cosimp = set()
for s in simplices:
    lst = sorted(v for v in s if v < 36)
    for i in range(len(lst)):
        for j in range(i, len(lst)):
            for k in range(j, len(lst)):
                cosimp.add((lst[i], lst[j], lst[k]))

# κ_toric 非零分佈
t_nnz = sum(1 for (i,j,k) in cosimp if abs(kappa_toric_scaled[i,j,k]) > 1e-6)
t_zero = len(cosimp) - t_nnz
print(f"  co-simplex κ_toric: 非零 {t_nnz}, 零 {t_zero}")
check("κ_toric 非零 = 350?", t_nnz == 350, f"({t_nnz})")
check("κ_toric 零 = 554?", t_zero == 554, f"({t_zero})")

# 一致率
agree = sum(1 for (i,j,k) in cosimp 
            if (abs(kappa_toric_scaled[i,j,k]) > 1e-6) == (abs(kappa36[i,j,k]) > 1e-6))
print(f"  零/非零一致: {agree}/{len(cosimp)}")
check("toric 公式完全重現零結構?", agree == len(cosimp), f"({agree}/{len(cosimp)})")

# ============ 6. 結論 ============
print("\n" + "=" * 72)
print("八期 28 總結:")
print("=" * 72)
if agree == len(cosimp):
    print("""
  ★★★ Toric 三重相交公式完整驗證!
  κ_ijk = Σ_cone ±det(v_i, v_j, v_k, v_l)   (cone 包含 i,j,k)

  → 904 co-simplex 中:
     350 非零 = 有向體積唔對消
     554 零   = 有向體積完全對消 (Σ±det = 0)

  → 554 消去定理 (第一性原理):
     κ_ijk = 0 ⇔ Σ_{cone} ±det = 0 (有向對消)
     唔係 SR 直接強制, 而係 toric 體積嘅代數對消!
""")
else:
    print(f"""
  ⚠️ Toric 公式未完全匹配 (一致率 {agree}/{len(cosimp)})
  需要檢查 normalization / cone 方向
""")
out = {
    "test": "O62 八期 28: Toric κ",
    "n_cones": len(cones),
    "kappa_toric_nnz": int(np.count_nonzero(kappa_toric)),
    "match_diag": match_diag,
    "n_match": n_match, "n_total": n_total,
    "scale": float(scale) if ratios else None,
    "t_nnz": t_nnz, "t_zero": t_zero,
    "agree": agree,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "28_toric_kappa.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 28 完成!")
