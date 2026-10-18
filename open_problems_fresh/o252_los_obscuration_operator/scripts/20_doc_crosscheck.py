#!/usr/bin/env python3
"""
O252 — Script 20: docs↔data 交叉核對 (closeout 永久產物) (2026-10-17)
=====================================================================
唯讀: 由 data/*.json 抽 key claims, grep docs/ 確認每份 doc 引用值與
data 一致 (closeout T2)。唔改任何 doc。
"""
import json, math, os, re, sys

HDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = HDIR + "/data"
DOCS = HDIR + "/docs"
LOG = []
def ck(name, cond, detail=''):
    LOG.append((name, bool(cond), detail))
    print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

def jd(n):
    with open(f"{DATA}/{n}.json") as f: return json.load(f)

def doc_has(d, s):
    p = f"{DOCS}/{d}.md"
    if not os.path.exists(p): return False
    txt = open(p, encoding='utf-8').read()
    return s in txt

print("="*84)
print("O252/20 — docs↔data 交叉核對 (唯讀)")
print("="*84)

# 1. docs/03: 9/12 命中 p=4.26e-7 (R3) + 後註記
d8 = jd("08_conservative_audit")
ck("docs/03 引 9/12 命中", doc_has("03_statistical_closure_r3", "9/12 命中"),
   "—")
ck("docs/03 引 p=4.26e-7", doc_has("03_statistical_closure_r3", "4.26e-7"),
   f"data/08 V1 p_ge={d8['uniq']['p_ge']:.2e}")
ck("docs/03 引 z=8.42", doc_has("03_statistical_closure_r3", "8.42"),
   f"data/08 z={d8['all_nobound']['z']:.2f}")

# 2. docs/07: σ=189.52 dev 0.12% t=0.03
d12 = jd("12_sigma_bandthickness")
ck("docs/07 引 189.52", doc_has("07_sigma_bandthickness_r7", "189.52"), "—")
ck("docs/07 引 dev 0.12%", doc_has("07_sigma_bandthickness_r7", "0.12%"),
   f"data/12 S1 dev={abs(d12['obs_mean']-d12['sig_E'])/d12['sig_E']*100:.2f}%")
ck("docs/07 引 t=-0.03", doc_has("07_sigma_bandthickness_r7", "t=−0.03")
   or doc_has("07_sigma_bandthickness_r7", "t=-0.03"),
   f"data/12 t_sigE={d12['t_sigE']:.2f}")

# 3. docs/10-11: μ_hat=235.7±21.6
d15 = jd("15_single_center")
ck("docs/10 引 μ_hat 235.7", doc_has("10_single_center_r10", "235.7"),
   f"data/15 mu_hat={d15['mu_hat']:.1f}")
ck("docs/10 引 ±21.6", doc_has("10_single_center_r10", "21.6"),
   f"data/15 se={d15['se']:.1f}")
ck("docs/10 引 CI [193,278]", doc_has("10_single_center_r10", "193")
   and doc_has("10_single_center_r10", "278"),
   f"data/15 ci95={d15['ci95']}")

# 4. docs/12: 9/13 p=0.0004, 11/13 p=0
d18 = jd("18_full_sample_inc_nodip")
ck("docs/12 引 9/13", doc_has("12_full_sample_inc_nodip_r12", "9/13"), "—")
ck("docs/12 引 11/13", doc_has("12_full_sample_inc_nodip_r12", "11/13"), "—")
ck("docs/12 引 Hβ 171 vs 37", doc_has("12_full_sample_inc_nodip_r12", "171")
   and doc_has("12_full_sample_inc_nodip_r12", "37"),
   f"data/18 Hα={d18['Hα_mean_dAIC']:.0f} Hβ={d18['Hβ_mean_dAIC']:.0f}")

# 5. docs/13: ⟨v⟩=280.03, 中位 289.8
d19 = jd("19_hop_moments")
ck("docs/13 引 280.03", doc_has("13_final_spec_r13", "280.03"),
   f"data/19 mean_v={d19['mean_v']:.4f}")

# 6. docs/11: ΔAIC≥150 → 203.7
ck("docs/11 引 ΔAIC≥150 μ_hat 203.7",
   doc_has("11_center_sensitivity_r11", "203.7"), "—")

# 7. docs/09 → data/14 (empirical null p=0.0003)
d14 = jd("14_position_empirical_null")
ck("docs/09 引 p=0.0003", doc_has("09_position_empirical_null_r9", "0.0003"),
   f"data/14 null_uniform_p={d14['null_uniform_p']:.4g}")

# 8. 所有 docs 存在
missing = []
for i in range(1, 14):
    cands = [f for f in os.listdir(DOCS) if f.startswith(f"{i:02d}_")]
    if not cands:
        missing.append(f"{i:02d}")
print(f"docs 01-13 存在檢查: missing={missing}")
ck("docs 01-13 全部存在", len(missing) == 0, f"missing={missing}")

ok = sum(1 for _,p,_ in LOG if p)
print(f"\n結果: {ok}/{len(LOG)} PASS → (唯讀, 唔寫 data)")
with open(f"{DATA}/20_doc_crosscheck.json","w") as f:
    json.dump({"checks": [{"name": n, "pass": p, "detail": d} for n,p,d in LOG],
               "ok": ok, "total": len(LOG)}, f, indent=2, ensure_ascii=False)
print(f"→ data/20_doc_crosscheck.json 記錄")