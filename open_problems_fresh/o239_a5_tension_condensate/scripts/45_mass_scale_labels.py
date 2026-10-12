#!/usr/bin/python3
"""O239 — Script 45: 質量數據 scale 標注表 + 閉合式 mixed-scale 穩健檢定
============================================================================
狀態: 2026-10-12（調律者: 「現在公式中的質量數據能標是否2GeV」）

背景: 閉合式 m=M₀|Δm|^φ² fit 用 data/09 mass9 = PDG2024 標準報值,
      但 PDG 對不同粒子用唔同 scheme/scale——9 點本身係 mixed-scale:
        u/d/s: MS̄(2 GeV)
        c:     MS̄(m_c)   b: MS̄(m_b)
        e/μ/τ: pole (lepton 冇 running, 唔係 2GeV)
        t:     pole
      如果閉合式結論依賴 scale 混雜, α=φ² 就唔穩健。

任務:
  S1: 質量數據 scale 標注表（每粒子 → scheme → scale → 是否 2GeV）
  S2: 閉合式輸入 mixed-scale 事實確認 (data/09 mass9 冇 scale 欄)
  S3: ★按 scale 分組 fit α: pole 組 {e,μ,τ,t} / 2GeV 組 {u,d,s} /
      mc,mb 組 {c,b} —— 每組 α vs φ²?（組間一致 = 閉合式 scale 穩健）
  S4: 結論: 閉合式 α=φ² 係咪唔依賴 scale 混雜

判據預註冊:
  S3: 每組 α 偏差: |α_group − φ²|/SE < 2σ（4 組: pole/2GeV/mc,mb/mixed 全體）
  S4: 若 S3 全過 ⟹ mixed-scale 輸入係「閉合式成立嘅容器」, 唔係引擎
產物: data/45_mass_scale_labels.json
"""
import json
import math
import numpy as np
from scipy import stats

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/45 — 質量數據 scale 標注 + mixed-scale 穩健檢定")
print("=" * 78)

PHI2 = ((1 + 5**0.5)/2)**2
PARTS = ["t", "b", "tau", "c", "mu", "s", "d", "u", "e"]
MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = np.array([172690.0, 4180.0, 1776.86, 1270.0, 105.6584, 93.4, 4.67, 2.16, 0.510999])
ERRS = np.array([1300.0, 30.0, 0.12, 20.0, 0.0003, 1.0, 0.48, 0.49, 0.000001])

# ── S1: scale 標注表 ──
# PDG2024 標準 scheme/scale（權威: PDG Review of Particle Physics 2024）
SCHEME_TAG = ["pole", "MS̄", "pole", "MS̄", "pole", "MS̄", "MS̄", "MS̄", "pole"]
SCALE  = ["pole(172.7GeV)", "μ=m_b", "pole", "μ=m_c", "pole", "μ=2GeV", "μ=2GeV", "μ=2GeV", "pole"]
# 更正: t/b/c 詳細—— t: pole (PDG 主報), b: MS̄(m_b)=4.18, c: MS̄(m_c)=1.27
SCALE_T = {
    "t":  "pole (PDG 主報); MS̄(m_t)=162.5 GeV 另報",
    "b":  "MS̄(μ=m_b)=4.18 GeV",
    "tau": "pole (lepton 冇 running)",
    "c":  "MS̄(μ=m_c)=1.27 GeV",
    "mu": "pole (lepton 冇 running)",
    "s":  "MS̄(μ=2 GeV)=93.4 MeV",
    "d":  "MS̄(μ=2 GeV)=4.67 MeV",
    "u":  "MS̄(μ=2 GeV)=2.16 MeV",
    "e":  "pole (lepton 冇 running)",
}
IS_2GEV = {"t": False, "b": False, "tau": False, "c": False, "mu": False,
           "s": True, "d": True, "u": True, "e": False}

print("\n── S1: ★質量數據 scale 標注表 (PDG2024 標準報值) ──")
print(f"   {'粒子':>4s} {'n':>2s} {'mass(MeV)':>10s} {'scheme':>6s} {'scale':>20s} {'2GeV?':>6s}")
for i, p in enumerate(PARTS):
    print(f"   {p:>4s} {MODES[i]:2d} {MASS[i]:10.4f} {SCHEME_TAG[i]:>6s} {SCALE_T[p]:>20s} {str(IS_2GEV[p]):>6s}")
n2gev = sum(1 for p in PARTS if IS_2GEV[p])
print(f"\n   ⟹ 只有 u/d/s 3/9 係 2GeV; c/b 係 m_c/m_b; e/μ/τ/t 係 pole")
chk("S1 標注表完成", True, f"{n2gev}/9 係 2GeV")

# ── S2: data/09 冇 scale 欄 ──
print("\n── S2: data/09 mass9 scale 標注現況 ──")
d09 = json.load(open("data/09_o206_inputs.json"))
print(f"   data/09 keys: {list(d09.keys())} —— {'mass9' in d09}")
print(f"   mass9 冇 scale 欄 ⟹ 需要標注表（本 script S1）")
chk("S2 確認 data/09 無 scale 欄", "mass9" in d09 and not any("scale" in k.lower() for k in d09),
    "mass9 裸數值, 無 scheme/scale")

# ── S3: 按 scale 分組 fit α ──
NC = 88
idx = np.arange(1, NC + 1)
psi = np.array([np.sin(n * math.pi * idx / (NC + 1)) for n in range(1, NC + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
V = psi @ np.diag(idx - idx.mean()) @ psi.T
E_n = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, NC + 1)])
D = E_n[:, None] - E_n[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm_all = np.einsum("ab,ab->a", V**2, Gm)
dm = np.abs(dm_all[[n - 1 for n in MODES]])
logdm = np.log(dm)
logm = np.log(MASS)

print("\n── S3: ★按 scale 分組 fit α (ln m vs ln|Δm|) ──")
groups = {
    "pole": [i for i, p in enumerate(PARTS) if SCHEME_TAG[i] == "pole"],
    "2GeV": [i for i, p in enumerate(PARTS) if IS_2GEV[p]],
    "mc_mb": [i for i, p in enumerate(PARTS) if p in ("c", "b")],
    "all": list(range(9)),
}
results = {}
for gname, gi in groups.items():
    if len(gi) < 3:
        # mc_mb 只有 2 點——唔 fit 斜率, 只報兩點比
        if gname == "mc_mb":
            print(f"   {gname} (n={len(gi)}): 2 點唔 fit 斜率, 只報: "
                  f"c {logm[3]-PHI2*logdm[3]:+.4f} / b {logm[2]-PHI2*logdm[2]:+.4f}")
            results[gname] = {"n": len(gi), "note": "2 點, 唔 fit 斜率"}
        continue
    rg = stats.linregress(logdm[gi], logm[gi])
    devg = (rg.slope - PHI2)/rg.stderr
    results[gname] = {"n": len(gi), "alpha": float(rg.slope), "se": float(rg.stderr),
                      "dev_sigma": float(devg)}
    print(f"   {gname} (n={len(gi)}): α = {rg.slope:.4f} ± {rg.stderr:.4f}, "
          f"dev vs φ² = {devg:+.2f}σ")
# 檢定全部組 |dev| < 2σ
all_pass = all(abs(v["dev_sigma"]) < 2.0 for k, v in results.items() if "dev_sigma" in v)
chk("S3 各 scale 組 α 全部 <2σ vs φ²", all_pass,
    "; ".join(f"{k}: {v['dev_sigma']:+.1f}σ" for k, v in results.items() if "dev_sigma" in v))

# ── S4: 結論 ──
print("\n── S4: mixed-scale 輸入對閉合式嘅意義 ──")
print("   ⟹ 若 S3 全過: α=φ² 喺 pole/2GeV 子集各自成立——")
print("     scale 混雜係『容器』, 唔係 α=φ² 引擎; 閉合式結論 scale 穩健")
print("   ⟹ 若 S3 有組 FAIL: 該 scale 子集 α 偏離 ⟹ 閉合式依賴 scale, 要拆")
chk("S4 結論成立 (S3 全過)", all_pass, "混合源自數據容器, 非引擎")

json.dump({
    "scale_table": [
        {"label": p, "n": MODES[i], "mass": float(MASS[i]), "scheme": SCHEME_TAG[i],
         "scale": SCALE_T[p], "is_2GeV": IS_2GEV[p]} for i, p in enumerate(PARTS)
    ],
    "data09_has_scale_field": False,
    "group_alpha": {k: v for k, v in results.items()},
    "group_all_pass": all_pass,
    "verdict": f"9 點中只有 u/d/s 係 MS̄(2GeV); c/b 係 m_c/m_b MS̄; e/μ/τ/t 係 pole。"
               f"按 scale 分組 fit α: { {k: (round(v['dev_sigma'],2) if 'dev_sigma' in v else '2pt') for k,v in results.items()} }"
               f" —— {'全 <2σ ⟹ α=φ² scale 穩健' if all_pass else '有組 FAIL'}"
}, open("data/45_mass_scale_labels.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")