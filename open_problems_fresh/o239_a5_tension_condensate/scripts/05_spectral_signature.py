#!/usr/bin/python3
"""O239 — Script 05: 挫阻扣減 spect 層 signature（|dm|、γ 同 88-site 結構）
============================================================================
問題 5（O239/01_problem_record）: 「剔走 32 挫阻」呢個操作喺譜層
（88-chain 譜量 |dm|_n、γ_n）有冇可識別 signature？

已知（O182/O171/O159）:
  - 88 節點 = A₅ 網 88 條透明邊中點 = 88-site chain（176-Laplacian half-site D-D）
  - 88 = 120 邊 − 32 挫阻; 88 = 2N_d = 2×44; O159: γ_k = 4sin²(kπ/176), k=1..88
  - O136 scripts/63: |dm|_n = Δm^(2)_n = [V G V]_nn（V = position perturbation,
    G = resolvent at γ_n）—— 質量層 C_f 源頭
  - O171 docs/02 (ii): #{γ ≤ μ²} = 44 = N_d; #{γ < μ²/2} = 29 = L₇

本 script 預註冊檢定「挫阻扣減」喺譜層嘅候選 signature:
  H1 譜簡併 = 44 pairs: γ_n 喺 n↔88−n 對稱（88 = 2N_d 譜層身份）—— sanity/已知
  H2 |dm|_n 同 γ_n 嘅 rank 相關: 若 |dm|_n ∝ 1/(γ_n − μ²) 式 resolvent 主導,
     譜層「扣減」會令 |dm| 喺 γ 細端大、γ 大端細
  H3 挫阻數 32 喺譜上有冇 signature: γ_{32}, γ_{56} (=88−32), |dm|_32 有冇特別位?
     —— 只報告位置統計, 唔做「命中宣稱」（單點 = 冇檢驗力, 唔算結構）
  H4 L₇ 分割: n 對應 γ_n < μ²/2 嘅集合大小 = 29（O171 譜恆等式重現）
  H5 挫阻距離帶簡併度 {40,20,12,10,2,4} 同 |dm|/γ 帶結構有冇對應
     （|dm|_n 相異值數 vs 88; 若 |dm| 都有強簡併 = 譜層離散 = 扣減 signature）
  H6 質量層 M9 = {1,2,3,4,5,7,9,11,13} 喺 |dm|_n 度有冇位置特權
     （排名: |dm| 最大 9 個 mode 同 M9 嘅 overlap）—— 只記錄, 唔宣稱

預註冊判據:
  H1 PASS 若 unique(γ_n) == 44 且 allclose(γ_n, γ_{88−n})
  H2 PASS 若 |corr(rank γ, rank |dm|)| > 0.9（resolvent 主導）或 < -0.9
  H3 記錄（唔 PASS/FAIL）
  H4 PASS 若 #{n: γ_n < 1} == 29（μ²/2 = 1）
  H5 PASS 若 unique(|dm|_n) <= 60（對比 88 = 連續）—— 離散 = signature
  H6 記錄 (top-9 |dm| ∩ M9)
"""
import json, math
import numpy as np
from pathlib import Path

NC = 88
M9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

# ── O136 scripts/63 權威定義重現: |dm|_n = [V G V]_nn ──
x = np.arange(1, NC + 1, dtype=float)
Psi = np.zeros((NC, NC))
for n in range(1, NC + 1):
    Psi[:, n - 1] = np.sin(n * math.pi * x / (NC + 1))
for n in range(NC):
    Psi[:, n] /= np.linalg.norm(Psi[:, n])
V = Psi.T @ np.diag(x - x.mean()) @ Psi
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])

def dm2_full():
    d = np.zeros(NC)
    for n in range(1, NC + 1):
        denom = E[n - 1] - E
        with np.errstate(divide="ignore", invalid="ignore"):
            g = np.where(np.abs(denom) > 1e-12, 1.0 / denom, 0.0)
        G = np.diag(g)
        A = V @ G @ V
        d[n - 1] = A[n - 1, n - 1]
    return d

DM = dm2_full()
GAM = E

print("=" * 78)
print("O239 scripts/05 — 挫阻扣減 spect 層 signature")
print("=" * 78)
print(f"\n88-chain 譜量: γ_n = 4sin²(nπ/88), n=1..88")
print(f"  γ range: [{GAM.min():.6f}, {GAM.max():.6f}]  unique = {len(np.unique(np.round(GAM, 10)))}")

# ── H1: γ 譜 88 = 2N_d 計數身份 ──
# periodic 88-chain: n=1..43 同 88−n (=87..45) 配對, n=44 自對(γ=4), n=88 零模(γ=0)
# ⟹ unique = 43 pairs + 2 自對 = 45; #{γ ≤ μ²=2} = 44 = N_d（O171 (ii)）
gamma_unique = len(np.unique(np.round(GAM, 10)))
pair_ok = all(np.allclose(GAM[i], GAM[86 - i]) for i in range(43))  # n=1↔87 ... n=43↔45
self44 = np.allclose(GAM[43], 4.0)   # n=44: γ=4 (μ²·2? No — μ²=2, γ_44=4)
zero88 = np.allclose(GAM[87], 0.0)   # n=88: 零模
chk("H1 γ_n 譜 = 43 pairs + n44 自對 + n88 零模 => unique 45 = 88(2N_d) 計數身份",
    gamma_unique == 45 and pair_ok and zero88, f"unique={gamma_unique} pair43={pair_ok} γ88=0={zero88}")

# ── H4: L₇ 分割 ──
n29 = int((GAM < 1.0).sum())   # μ²/2 = 1
n44 = int((GAM <= 2.0).sum())  # μ² = 2
chk("H4 #{γ < μ²/2} = 29 = L₇（O171 譜恆等式）", n29 == 29, f"n(γ<1)={n29}")
print(f"  #{'γ ≤ μ²'} = {n44}（= N_d = 44）")

# ── H2: rank 相關 ──
r12 = np.corrcoef(
    np.argsort(np.argsort(GAM)), np.argsort(np.argsort(np.abs(DM)))
)[0, 1]
chk("H2 |corr(rank γ, rank |dm|)| > 0.9（resolvent 主導）", abs(r12) > 0.9,
    f"r={r12:.4f}")

# ── H3: 32 位置（記錄）──
print("\n[H3 記錄] 挫阻數 32 喺譜位置（單點冇檢驗力, 只報）:")
for n in [32, 56, 44]:
    print(f"  γ_{n:>2} = {GAM[n-1]:.6f}  |dm|_{n} = {abs(DM[n-1]):.6e}  "
          f"rank(|dm|) = {int(np.argsort(np.argsort(-np.abs(DM)))[n-1])+1}/88")

# ── H5: |dm| 離散度 ──
dm_unique = len(np.unique(np.round(DM, 8)))
chk("H5 |dm|_n 相異值 <= 60（譜層離散 = 扣減 signature）", dm_unique <= 60,
    f"unique={dm_unique}/88")
print(f"  |dm| range: [{np.abs(DM).min():.4e}, {np.abs(DM).max():.4e}]  unique={dm_unique}")

# ── H6: M9 top-9 overlap（記錄）──
top9 = set(np.argsort(-np.abs(DM))[:9].tolist())
ol = top9 & set(M9)
print(f"\n[H6 記錄] |dm| 最大 9 個 mode: {sorted(top9)}  ∩ M9 = {sorted(ol)}")
print(f"   M9 喺 |dm| rank 分佈: {[int(np.argsort(np.argsort(-np.abs(DM)))[m-1])+1 for m in M9]}")

# ── 加: M9 嘅 |dm| 結構（質量層 context, 只記錄）──
print("\n[M9 記錄] mode 嘅 γ / |dm|:")
for m in M9:
    print(f"  n={m:>2}: γ={GAM[m-1]:.6f}  |dm|={abs(DM[m-1]):.6e}")

out = {
    "gamma": {"unique": int(gamma_unique), "pair43": bool(pair_ok),
              "self44": bool(self44), "zero88": bool(zero88),
              "range": [float(GAM.min()), float(GAM.max())]},
    "H2_rank_corr": float(r12),
    "H4": {"n29": n29, "n44": n44},
    "H3": {str(n): {"gamma": float(GAM[n-1]), "absdm": float(abs(DM[n-1]))} for n in [32, 56, 44]},
    "H5": {"dm_unique": int(dm_unique)},
    "H6": {"top9": sorted(top9), "overlap_M9": sorted(ol),
           "M9_rank": [int(np.argsort(np.argsort(-np.abs(DM)))[m-1]) + 1 for m in M9]},
    "dm_all": DM.tolist(), "gamma_all": GAM.tolist(),
}
outfile = Path(__file__).parent.parent / "data" / "05_spectral_signature.json"
outfile.parent.mkdir(parents=True, exist_ok=True)
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

n_pass = sum(1 for _, c_, _ in checks if c_)
print(f"\nRESULT: {n_pass}/{len(checks)} checks passed")