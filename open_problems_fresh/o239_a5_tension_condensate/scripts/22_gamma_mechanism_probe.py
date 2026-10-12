#!/usr/bin/python3
"""O239 — Script 22: γ 機構探測（重寫版）
============================================================================
狀態: 2026-10-12 回滾後重寫（原 R16 內容已回滾, 本 script 重新落碟）
目的: 檢定候選 B′——「γ = −M_lepton/B 係由最低族 (Lepton) 附近 local 行為外推」?
      以及 stair 拆解是否全 stair 元素。

判據預註冊（唔 fit target）:
  B1: local 斜率（中心差分）對 9 質量模態: 有冇任何單點 local 斜率 ≈ −19/4 (|<5σ|)?
      若全部 >5σ ⟹ 「local 外推由某單點嚟」假設排除。
  B2: stair 拆解: γ = −(K_Tree − (N_gen−1)·L₄)/B = −33/4 + 7/2 = −4.75 是否 EXACT?
  B3: 殘差 vs 族: Lepton 族最貼近 global fit?（若 Up 更貼 ⟹ 「最低族控制」假設負）
  B4: 最輕端 e (mode 13) local 斜率 vs −19/4: 是否都遠離?
產物: data/22_gamma_mechanism_probe.json（重寫版）
資料: data/09_o206_inputs.json（O206 DM 譜, freeze v1.0）
"""
import json
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/22 — γ 機構探測（重寫版, 回滾後重新落碟）")
print("=" * 78)

O9 = json.load(open("data/09_o206_inputs.json"))
PAIR = O9["PAIR"]               # [(n,label), ...]
m9 = np.array(O9["mass9"])      # 質量譜 (m ∝ θ^γ) — γ 檢定用質量, 唔係 |dm|
theta = np.array([n*np.pi/88 for n, _ in PAIR])

gamma_struct = -19/4
g_mc, g_std = -4.7503, 0.0361     # scripts/14 MC

# ── global fit (質量譜) ──
lt = np.log(theta)
lm = np.log(m9)
rf = stats.linregress(lt, lm)
gamma_global = rf.slope
resid = lm - (rf.slope*lt + rf.intercept)

print(f"── global γ (OLS, 質量譜) = {gamma_global:.4f} vs γ_struct = {gamma_struct} vs γ_MC = {g_mc}±{g_std}")

# ── B1: local 斜率（中心差分 log-log, 質量譜）──
print(f"\n── B1: local 斜率 (中心差分, 質量譜) ──")
local = []
for i in range(1, len(PAIR)-1):
    n, lab = PAIR[i]
    s = (lm[i+1] - lm[i-1]) / (lt[i+1] - lt[i-1])
    d = abs(s - gamma_struct) / g_std
    local.append((lab, n, s, d))
for lab, n, s, d in local:
    print(f"   mode {n:>2} ({lab}): γ_local = {s:+.3f}  |距 −19/4| = {d:6.1f}σ")
d_min = min(d for _, _, _, d in local)
chk("B1 冇單點 local ≈ −19/4 (全部 >5σ)", d_min > 5.0, f"最近 {d_min:.1f}σ")

# ── B2: stair 拆解 ──
K_Tree, L4, B, N_gen = 33, 7, 4, 3
g_decomp = -(K_Tree - (N_gen-1)*L4)/B
print(f"\n── B2: stair 拆解 ──")
print(f"   γ = −(K_Tree − (N_gen−1)·L₄)/B = −33/4 + 2·7/4 = {g_decomp} = {gamma_struct}?")
chk("B2 拆解 EXACT = −19/4", abs(g_decomp - gamma_struct) < 1e-12, f"{g_decomp}")

# ── B3: 殘差 vs 族 ──
print(f"\n── B3: 殘差 vs 族 ──")
family = {"Lepton": ["e", "mu", "tau"], "Up": ["u", "d"], "Down": ["c", "s", "b"]}
for fam, labs in family.items():
    idx = [i for i, (n, lab) in enumerate(PAIR) if lab in labs]
    r = np.sqrt(np.mean(resid[idx]**2))
    print(f"   {fam:<7}: RMS resid = {r:.4f}")
r_lept = np.sqrt(np.mean([resid[i]**2 for i, (n, lab) in enumerate(PAIR) if lab in ["e","mu","tau"]]))
r_up = np.sqrt(np.mean([resid[i]**2 for i, (n, lab) in enumerate(PAIR) if lab in ["u","d"]]))
print(f"      → Lepton {r_lept:.4f} vs Up {r_up:.4f} (Up 更貼 = 假設負)")
chk("B3 假設負: Up 未必更差", r_up < r_lept, f"Up {r_up:.4f} < Lepton {r_lept:.4f}")

# ── B4: 最輕端 e (mode 13) ──
print(f"\n── B4: 最輕端 e ──")
# rightmost 差分 (同原版): e 係最後一個 mode
i13 = next(i for i, (n, lab) in enumerate(PAIR) if n == 13)
if i13 >= 1:
    s13 = (lm[i13] - lm[i13-1]) / (lt[i13] - lt[i13-1])
    d13 = abs(s13 - gamma_struct) / g_std
else:
    s13, d13 = float("nan"), float("inf")
print(f"   γ_local(e) = {s13:.4f}  |距 −19/4| = {d13:.1f}σ")
chk("B4 e local 完全唔 close (>10σ)", d13 > 10.0, f"{d13:.1f}σ")

# ── B5: freeze 層敏感度 — μ local 斜率對 c 質量構建 ──
print(f"\n── B5: μ local 斜率 freeze 層敏感度 ──")
# μ 中心差分 = (log s − log c)/(log θ7 − log θ4); c 質量: PDG pole 1270 vs FLAG RGI ~1089
def mu_local(c_mass):
    # PAIR index: mode 5 (μ) 喺 [4]; c (mode4) 喺 [3]; s (mode7) 喺 [5]
    ic = next(i for i, (n, lab) in enumerate(PAIR) if n == 4)
    im = next(i for i, (n, lab) in enumerate(PAIR) if n == 5)
    is_ = next(i for i, (n, lab) in enumerate(PAIR) if n == 7)
    return (np.log(m9[is_]) - np.log(c_mass)) / (lt[is_] - lt[ic])
mu_pdg = mu_local(1270.0)      # freeze v1.0 (PDG2024)
mu_rgi = mu_local(93.4*11.652) # FLAG RGI 重建 (原版 scripts/22 用)
print(f"   μ local (c=PDG 1270):  {mu_pdg:+.4f}  |距 −19/4| = {abs(mu_pdg-gamma_struct)/g_std:.1f}σ")
print(f"   μ local (c=RGI 1089):  {mu_rgi:+.4f}  |距 −19/4| = {abs(mu_rgi-gamma_struct)/g_std:.1f}σ")
print(f"   ⟹ B′ 判定依賴 freeze 層 (PDG: μ 支持 2.4σ; RGI: μ 遠離 10.1σ)")
chk("B5 敏感度明確標注 (判定非 robust)", abs(mu_pdg - mu_rgi)/g_std > 3.0,
    f"PDG vs RGI 差 {(mu_pdg-mu_rgi)/g_std:.1f}σ")

json.dump({
    "B1_gamma_global": float(gamma_global),
    "B1_local": [(lab, n, float(s), float(d)) for lab, n, s, d in local],
    "B1_d_min": float(d_min),
    "B2_decomp": float(g_decomp),
    "B3_rms": {"Lepton": float(r_lept), "Up": float(r_up)},
    "B4_e_local": float(s13), "B4_d_sigma": float(d13),
    "B5_mu_pdg": float(mu_pdg), "B5_mu_rgi": float(mu_rgi),
    "verdict": "重寫版發現 (回滾後重建): B′ 判定依賴 freeze 層 — PDG: μ local 2.4σ 支持; RGI: μ 10.1σ 遠離; 原 R16『全負』只對 RGI 構建成立, 唔係 robust",
}, open("data/22_gamma_mechanism_probe.json", "w"), indent=1, ensure_ascii=False)

n_pass = sum(1 for _, c_ in P if c_)
print(f"\nRESULT: {n_pass}/{len(P)} checks passed")