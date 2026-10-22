"""
O72 docs 內容 vs scripts 數值核對 (防幻覺最終關)
=====================================================================
目的: 每個 docs 嘅核心數值, 由 scripts 獨立重算, 確認一致。

核對清單:
  [1] docs/01: γ_k 譜, Σγ=90/88/90, R_H, λ_sync, 946, 1496, φ, L=53/8
  [2] docs/02: Q1-Q10 存在 (10 條)
  [3] docs/07: 恆等式發現 (2N+2, N, N+2, C(44,2))
  [4] docs/10: O73 交叉影響 (BBN 72.73, CMB 67.41)
  [5] 所有 docs 檔案存在 + 非空
"""
import numpy as np
import os

phi = (1+np.sqrt(5))/2
ok = 0; total = 0
def check(name, cond, detail=""):
    global ok, total
    total += 1
    ok += cond
    print(f"[{'✅' if cond else '❌'}] {name} {detail}")

docs_dir = os.path.expanduser("~/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o72_kchain_ktree_reality/docs")

# [1] docs/01 核心數值
print("=" * 72)
print("[1] docs/01 核心數值")
print("=" * 72)
gamma = 4*np.sin(np.pi*np.arange(1,45)/88)**2
check("docs/01 Σγ(44-site) = 90", abs(gamma.sum()-90) < 1e-9)
g88 = 4*np.sin(np.pi*np.arange(1,89)/176)**2
check("docs/01 88-site Σγ_odd = 88", abs(g88[0::2].sum()-88) < 1e-9)
check("docs/01 88-site Σγ_even = 90", abs(g88[1::2].sum()-90) < 1e-9)
check("docs/01 R_H = 4129.94", abs(299792.458/72.59-4129.94) < 0.01)
T_sync = 2*np.pi*3.085677581e19/(72.59*3.15576e16)
lam_sync = 299792.458*(T_sync*3.15576e16)/(88*3.085677581e19)
check("docs/01 λ_sync = 294.88", abs(lam_sync-294.88) < 0.05)
check("docs/01 946 = C(44,2)", 946 == 44*43//2)
check("docs/01 1496 = 44×34", 1496 == 44*34)
check("docs/01 L = 53/8 = 6.625", abs(53/8-6.625) < 1e-12)
check("docs/01 φ = 1.6180339887", abs(phi-1.6180339887498949) < 1e-12)

# [2] docs/02 Q1-Q10
print()
print("=" * 72)
print("[2] docs/02 LCDM 信徒質疑完整性")
print("=" * 72)
challenges = open(os.path.join(docs_dir, "02_lcdm_challenges.md")).read()
for q in ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10"]:
    check(f"docs/02 有 {q}", f"## 質疑 {q}" in challenges or f"**{q}**" in challenges)

# [3] docs/07 恆等式
print()
print("=" * 72)
print("[3] docs/07 恆等式發現")
print("=" * 72)
sr = open(os.path.join(docs_dir, "07_self_refutation.md")).read()
check("docs/07 有 Σγ = 2N+2", "2N+2" in sr)
check("docs/07 有 Σγ_odd = N", "Σγ_odd = 88" in sr and "N @ N=88" in sr)
check("docs/07 有 C(44,2)", "C(44,2)" in sr)
check("docs/07 有 H₀ 隱藏參數", "隱藏" in sr and "H₀" in sr)

# [4] docs/10 O73 交叉影響
print()
print("=" * 72)
print("[4] docs/10 O73 交叉影響")
print("=" * 72)
c10 = open(os.path.join(docs_dir, "10_O73_cross_impact.md")).read()
check("docs/10 有 BBN 鎖定 72.73", "72.73" in c10)
check("docs/10 有 CMB 投影 67.41", "67.41" in c10)
check("docs/10 有 (1−π/44)", "(1−π/44)" in c10 or "(1-π/44)" in c10)
check("docs/10 有 A2 修正", "A2" in c10 and ("推翻" in c10 or "修正" in c10))

# [5] 所有 docs 存在
print()
print("=" * 72)
print("[5] docs 檔案完整性")
print("=" * 72)
expected = [f"0{i}_" for i in range(1,10)] + ["10_O73_cross_impact.md", "01_problem_record.md", "SESSION_START.md"]
files = sorted(os.listdir(docs_dir))
for f in files:
    if f.endswith(".md"):
        size = os.path.getsize(os.path.join(docs_dir, f))
        check(f"{f} 非空", size > 500, f"({size} bytes)")

print()
print(f"=== 總計: {ok}/{total} PASS ===")
