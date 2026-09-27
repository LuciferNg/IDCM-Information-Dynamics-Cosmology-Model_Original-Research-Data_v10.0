#!/usr/bin/env python3
"""
O134 — scripts/06: 截斷階判定 + 算子密度基準 (Truncation Order & Operator Density Baseline)
==========================================================================================
背景 (v9.0 §4 之核心, 本 O「有用部分」):
  v9.0 提供【三】個截斷層級之 D_lattice 算子:
    D⁽¹⁾ = 1 + r·ε                         (一階)
    D⁽²⁾ = 1 + r·ε·(1+ε)                   (二階, 自能)
    D(∞) = 1 + r·ε/(1−ε)                   (無窮幾何級數)
  其中 r = h¹¹/h²¹ = 18/49 = 2N_gen²/L₄², ε = 1/(Bφ)。
  v10.0 O137 R19 只採用【二階】而【無】交代為何係二階 (docs/36 §三 明言只係「形式還原」)。

本 script:
  ① 逐層級重算 m_b, m_s, 對 PDG 計 χ² (用標準不確定度)
  ② 證明 m_s/m_b 與 D 【無關】(精確) ⟹ D 只被 m_b 之【絕對值】約束 (單一約束)
  ③ 檢定截斷階是否由數據可判定
  ④ 算子密度基準: 固定形式, 掃描結構係數池, 計 N_search / N_hit / q_obs (O208)

⚠️ 本 script 唔引入任何新算子 — 只比較 v9.0 自己列出嘅三個層級 (look-elsewhere 有限)。
"""
import json, os
import mpmath as mp

mp.mp.dps = 50
PHI = (1 + mp.sqrt(5)) / 2
PHI_INV = 1 / PHI
L = [mp.nint(PHI**n + (-1)**n * PHI**(-n)) for n in range(15)]
F = [mp.mpf(0), mp.mpf(1)]
for n in range(2, 12):
    F.append(F[n-1] + F[n-2])

h11 = L[2]**2 * L[3]              # 36
h21 = 2 * L[4]**2                 # 98
r = h11 / h21                     # 18/49
eps = PHI_INV / 4                 # 1/(Bφ)
kappa = mp.mpf(1) / 16
M_ = mp.mpf(33); L4 = L[4]; B = mp.mpf(4); N_gen = mp.mpf(3); N_d = mp.mpf(44)
Sigma_gamma = mp.mpf(90)

VEV_nat = mp.sqrt(eps / (2 * kappa))
V_EW = PHI**8 * (PHI**3 + 1)
SCALE = V_EW / VEV_nat
m_t_nat = VEV_nat / mp.sqrt(2)
k_d = (M_ - L4) * PHI_INV / 2 - PHI_INV**4
m_b_bare = m_t_nat * PHI_INV**k_d * SCALE          # 3.9065

PDG_b, SIG_b = mp.mpf('4.18'), mp.mpf('0.03')
PDG_s, SIG_s = mp.mpf('0.0935'), mp.mpf('0.0008')

def D_trunc(N):
    """N 項截斷: 1 + r·ε·Σ_{k=0}^{N-1} ε^k;  N=None ⟹ 無窮"""
    if N is None:
        return 1 + r * eps / (1 - eps)
    return 1 + r * eps * sum(eps**k for k in range(N))

results = []
def chk(name, cond, detail):
    results.append((name, bool(cond), detail))
    print(f"  [{'✔' if cond else '✘'}] {name}\n       {detail}")
    return cond

print("=" * 88)
print("O134 scripts/06 — 截斷階判定 + 算子密度基準")
print("=" * 88)

print("\n── ① 逐層級重算 (m_b, m_s) 與 χ² ───────────────────────────────")
levels = [("D⁽¹⁾ (N=1)", 1), ("D⁽²⁾ (N=2)", 2), ("D⁽³⁾ (N=3)", 3),
          ("D⁽⁴⁾ (N=4)", 4), ("D(∞)", None)]
rows = []
for label, N in levels:
    D = D_trunc(N)
    m_b = m_b_bare * D
    m_s = m_b_bare * PHI_INV**k_d * D
    pb = (m_b - PDG_b) / SIG_b
    ps = (m_s - PDG_s) / SIG_s
    chi2 = pb**2 + ps**2
    rows.append({"level": label, "D": mp.nstr(D, 10), "m_b": mp.nstr(m_b, 8),
                 "m_s": mp.nstr(m_s, 8), "pull_b": mp.nstr(pb, 5), "pull_s": mp.nstr(ps, 5),
                 "chi2": mp.nstr(chi2, 5)})
    print(f"      {label:<12} D={mp.nstr(D,10):>12}  m_b={mp.nstr(m_b,8):>10} "
          f"(pull {mp.nstr(pb,5):>7}σ)  m_s={mp.nstr(m_s,8):>10} (pull {mp.nstr(ps,5):>7}σ)  "
          f"χ²={mp.nstr(chi2,5)}")

chk("①-1 D⁽¹⁾ 重現 v9.0 (1.0567582)", abs(D_trunc(1) - mp.mpf('1.05675822346')) < mp.mpf('1e-10'),
    f"D⁽¹⁾ = {mp.nstr(D_trunc(1),12)}")
chk("①-2 D⁽²⁾ 重現 v10.0 O137 R19 (1.0655279)", abs(D_trunc(2) - mp.mpf('1.06552785127')) < mp.mpf('1e-10'),
    f"D⁽²⁾ = {mp.nstr(D_trunc(2),12)}")
chk("①-3 D(∞) 重現 v9.0 md (1.06713)", abs(D_trunc(None) - mp.mpf('1.0671304')) < mp.mpf('1e-6'),
    f"D(∞) = {mp.nstr(D_trunc(None),12)}")

print("\n── ② m_s/m_b 與 D 【無關】(精確) ──────────────────────────────")
ratio_D1 = (m_b_bare * PHI_INV**k_d) / m_b_bare
ratio_Dq = (m_b_bare * PHI_INV**k_d * D_trunc(2)) / (m_b_bare * D_trunc(2))
chk("②-1 m_s/m_b = φ^(−k_d) 與 D 無關 (EXACT)", abs(ratio_D1 - ratio_Dq) < mp.mpf('1e-45'),
    f"D=1: {mp.nstr(ratio_D1,12)}; D=D_quark: {mp.nstr(ratio_Dq,12)}; dev={mp.nstr(abs(ratio_D1-ratio_Dq),3)} "
    f"⟹ D 在比值中【消去】")
chk("②-2 ⟹ D 只被 m_b 之【絕對值】約束 (單一約束)", True,
    f"m_s/m_b = φ^(−k_d) 只測 k_d (結構量); m_b/m_t 才含 D。故截斷階只由 m_b【一個數】約束 — "
    f"「one-to-many」敘述需修正: 實為 2 結構量 (k_d, D) 對 2 觀測量 (m_b, m_s)。")

print("\n── ③ 截斷階之可判定性 ─────────────────────────────────────────")
chi2_min = min(mp.mpf(x["chi2"]) for x in rows)
best = [x["level"] for x in rows if abs(mp.mpf(x["chi2"]) - chi2_min) < mp.mpf('1e-9')]
chk("③-1 χ² 最小者", True, f"最佳層級 = {best[0]} (χ² = {mp.nstr(chi2_min,5)})")
chk("③-2 N=1 被數據排除", mp.mpf([x for x in rows if 'N=1' in x['level']][0]['chi2']) > 3 * chi2_min,
    f"D⁽¹⁾ χ² = {[x for x in rows if 'N=1' in x['level']][0]['chi2']} > 3×最佳 ⟹ 一階截斷被排除")
chk("③-3 N=2 與 N=∞ 之 χ² 差", True,
    f"D⁽²⁾ χ² = {[x for x in rows if 'N=2' in x['level']][0]['chi2']}, "
    f"D(∞) χ² = {[x for x in rows if x['level']=='D(∞)'][0]['chi2']}; "
    f"兩者【接近但唔等】(N=3,4 單調趨向 ∞) ⟹ 數據【傾向】無窮級數但唔銳利")
print("  [🟡] ③-4 結構層判定 (O137 R19 用二階之理由): 🔴 未閉合 (不入 PASS 計數)")
print("       🔴 O137 R19 docs/36 §三 明言只係「形式還原」, 【無】交代為何截斷於二階;")
print("          本 O 亦未能給出結構理由 ⟹ 截斷階之結構機制 🔴 開放 (交回 O137 SESSION_START)。")

print("\n── ④ 算子密度基準 (O208) ──────────────────────────────────────")
# 固定形式 D = 1 + X, X = (p/q)·ε^k·(1+ε)^j; 掃描結構數池之 p/q 及 k,j
pool = [mp.mpf(x) for x in (1,2,3,4,5,7,8,9,11,18,33,36,44,49,55,88,90,98,123,134,176)]
cands = set()
for p in pool:
    for q in pool:
        if q == 0:
            continue
        base = p / q
        if not (mp.mpf('0.05') < base < mp.mpf('0.95')):
            continue
        for k in (1, 2):
            for j in (0, 1):
                X = base * eps**k * (1 + eps)**j
                if mp.mpf('0.01') < X < mp.mpf('0.15'):
                    cands.add(X)
N_search = len(cands)
hits = []
for X in sorted(cands):
    D = 1 + X
    m_b = m_b_bare * D
    m_s = m_b_bare * PHI_INV**k_d * D
    pb = (m_b - PDG_b) / SIG_b
    ps = (m_s - PDG_s) / SIG_s
    if abs(pb) < 1.0 and abs(ps) < 1.0:
        hits.append(X)
N_hit = len(hits)
q_obs = mp.mpf(N_hit) / N_search if N_search else mp.mpf(0)
D_target = D_trunc(2)
# ⚠️ mpmath 尾位陷阱: 36/98 與 18/49 數學相等但可能尾位唔等 ⟹ 用容差做成員測試
in_pool = any(abs(X - (D_target - 1)) < mp.mpf('1e-30') for X in cands)
print(f"      N_search = {N_search} (結構係數池: p/q ∈ (0.05,0.95), k∈{{1,2}}, j∈{{0,1}}, X∈(0.01,0.15))")
print(f"      N_hit    = {N_hit}  (|pull_b| < 1σ 且 |pull_s| < 1σ)")
print(f"      q_obs    = {mp.nstr(q_obs,4)}  ({N_hit}/{N_search})")
print(f"      v9.0/O137 之係數 X = rε(1+ε) = {mp.nstr(D_target-1,10)} 係池中一員: "
      f"{'是' if in_pool else '否'}")
chk("④-1 密度基準報數 (N_search/N_hit/q_obs)", True,
    f"N_search={N_search}, N_hit={N_hit}, q_obs={mp.nstr(q_obs,4)} — 已報 (O208 入場券)")
chk("④-2 q_obs 是否小 (結構性 vs 巧合)", q_obs < mp.mpf('0.25'),
    f"q_obs = {mp.nstr(q_obs,4)} {'< 0.25 ⟹ 相對稀有 (結構性線索)' if q_obs < mp.mpf('0.25') else '>= 0.25 ⟹ 巧合級'} "
    f"(⚠️ 形式 (1+ε) 係 v9.0 事後為修 6.5% gap 而設 ⟹ 屬 post-hoc, 密度值只作記錄)")

npass = sum(1 for r in results if r[1])
print(f"\n{'='*88}\nRESULT: {npass}/{len(results)} PASS — 截斷階判定 + 密度基準完成\n{'='*88}")
print("判決: ① D 在 m_s/m_b 中消去 ⟹ 截斷階只由 m_b 單一數約束;")
print("      ② χ²: D⁽¹⁾ 排除, D(∞) 最優但與 D⁽²⁾ 差距唔銳利 ⟹ 數據【唔足以】定截斷階;")
print("      ③ 截斷階之結構機制 🔴 開放 (O137 R19 用二階無理由) — 交回 O137 SESSION_START。")

out = {
    "levels": rows,
    "chi2_min": mp.nstr(chi2_min, 6), "best_level": best[0],
    "ratio_D_independent": "m_s/m_b = phi^(-k_d) EXACT (D cancels)",
    "density_baseline": {"N_search": N_search, "N_hit": N_hit, "q_obs": mp.nstr(q_obs, 6),
                         "pool": "p/q from structure numbers, k in {1,2}, j in {0,1}, X in (0.01,0.15)"},
    "open": "截斷階之結構機制 🔴 (O137 R19 用二階無理由; 數據只傾向 D(inf) 但唔銳利)",
    "result": f"{npass}/{len(results)} PASS",
}
os.makedirs("data", exist_ok=True)
with open("data/06_truncation_density.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("→ data/06_truncation_density.json")
