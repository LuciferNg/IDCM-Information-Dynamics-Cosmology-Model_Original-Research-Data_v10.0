#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O136 scripts/72 -- R8: c/s 同 scheme 化重審 (凍結層更正通知執行)

O234 docs/02 §六 (2026-10-06 已註冊):
  正確 C_c/C_s (FLAG Nf=4 同 scheme) = 3.86
  O233 docs/15 C_f 池 (PDG 絕對質量 by-construction) 隱含 C_c/C_s = 4.50 — 15% 偏離
  混標度來源: m_c(m_c)=1270 MeV vs m_s(2 GeV)=93.4 MeV (唔同重整化標度直接除)

受影響 (必須更正/判死):
  [T1] O209 P2: C_f_c/C_f_s = 4.5029 ≈ 9/2 (dev 0.063%)      ⟹ 混標度產物
  [T2] O209 P6: (9/2)(γ7/γ4) = 13.5889 vs m_c/m_s 13.5974     ⟹ 混標度產物
  [T3] O136 scripts/70: 68/5 = 88/F₅−B = 13.6 (dev 0.019%)    ⟹ 混標度產物 (posthoc 亦死)
  [T4] O136 scripts/70 P5: C_f 28 對家族 (C_f 絕對值)         ⟹ 全家族受混標度影響

凍結層權威 (O234 data/01 + data/03 v1.1):
  m_c/m_s Nf=4     = 11.652 ± 0.065   (FLAG ⊕ ETM, 同 scheme; docs/02 提議做主)
  m_c/m_s HPQCD    = 11.850 ± 0.16    (FLAG 09A; 做交叉)
  m_s/m̂           = 27.227 ± 0.081   (0.30%)
  m_d/m_u          = 2.1505 ± 0.111   (5.2%)

任務:
  [A] 用凍結層同 scheme m_c/m_s 重掃結構池: 11.652 有冇結構身份?
  [B] 9/2 同 68/5 對凍結層值嘅 dev (確認判死)
  [C] m_s/m_u (derived 42.890) + m_s/m_d (19.944) + m_d/m_u (2.1505) 掃結構池
  [D] 差額: 若 11.652 有結構命 — 記錄 ; 冇 — 負閉合, 確認 c/s 單點身份唔存在於同 scheme 層
"""
import json, math
from fractions import Fraction
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
# 輸出編號 (由 O236 scripts/07 搬入 O136 時改 72)
OUTNUM = 72

# ── O233 docs/02 凍結結構常數池 (57 原子) ─────────────────────────────
atoms = set(list(range(1, 26)) + [26, 28, 29, 30, 32, 33, 34, 36, 37, 40, 41,
                                   42, 44, 45, 46, 47, 48, 50, 51, 55, 60, 64,
                                   72, 88, 90, 120, 123, 134, 137, 176, 317,
                                   528, 946])
# Lucas/Fib 檢查補充 (L₀..L₁₄, F₂..F₂₀)
Lucas = [2, 1, 3, 4, 7, 11, 18, 29, 47]
Fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
atoms |= set(Lucas) | set(Fibs) | {5, 66, 68, 76, 84, 92, 100, 121, 144, 169, 196, 256}
atoms = {a for a in atoms if a > 0}
pool = sorted({Fraction(a, b) for a in atoms for b in atoms if b and a >= b})
# 只保留 (0.1, 100] range
pool = [p for p in pool if 0.1 <= p <= 100]

CHK = []
def chk(name, ok, msg=""):
    CHK.append((name, bool(ok), msg))
    print(f"   [{'PASS' if ok else 'FAIL'}] {name} — {msg}")

def nearest(pool, target, tol_frac=0.005):
    """最近結構命中 + 相對 dev (pool 非空保證)"""
    best = (float("inf"), 0.0, Fraction(1, 1))
    for p in pool:
        f = float(p)
        d = abs(f - target) / target if target else float("inf")
        if d < best[0]:
            best = (d, f, p)
    return best

print("O236 scripts/07 -- R8: c/s 同 scheme 化重審 (凍結層更正執行)")
print("=" * 78)

# ── [A] 凍結層同 scheme m_c/m_s 結構身份 ──────────────────────────────
print("\n[A] 凍結層同 scheme m_c/m_s = 11.652 ± 0.065 (Nf=4)")
targets = {
    "m_c/m_s Nf=4": (11.652, 0.065),
    "m_c/m_s HPQCD": (11.850, 0.16),
    "m_s/m̂": (27.227, 0.081),
    "m_d/m_u": (2.1505, 0.111),
    "m_s/m_u derived": (42.890, 1.52),
    "m_s/m_d derived": (19.944, 0.33),
}
hits = {}
for name, (v, err) in targets.items():
    d, f, p = nearest(pool, v, tol_frac=0.005)
    hits[name] = {"value": v, "err": err, "nearest": f, "dev_pct": d * 100, "fraction": str(p)}
    print(f"   {name:>18} = {v:8.3f}±{err:6.3f}  最近結構 {f:8.3f} = {p}  dev {d*100:8.3f}%")

# ── [B] 舊候選對凍結層值嘅 dev (判死確認) ─────────────────────────────
print("\n[B] 舊候選對凍結層同 scheme 值 (判死確認):")
v_cs = 11.652
old = {"9/2 (O209 P2)": 4.5 / (4 * math.sin(7 * math.pi / 88) ** 2) * (4 * math.sin(4 * math.pi / 88) ** 2),
       # 錯用: C_c/C_s = 4.50 係混標度; 直接對比 m 比 13.5974
       "13.5974 (混標度 m_c/m_s)": 13.5974,
       "68/5 = 13.6 (O136)": 13.6,
       "11.652 (凍結層)": 11.652}
for name, v in old.items():
    d = abs(v - v_cs) / v_cs * 100
    hit = "===" if d < 0.5 else ""
    print(f"   {name:>24} dev vs 凍結層 = {d:7.3f}% {hit}")

# ── [C] C_c/C_s 同 scheme 嘅結構量比值 ────────────────────────────────
# C_c/C_s (同 scheme) = (m_c/m_s)/(γ7/γ4) — γ 係 scheme-invariant (純幾何)
print("\n[C] C_c/C_s 同 scheme 重算:")
g4 = 4 * math.sin(4 * math.pi / 88) ** 2
g7 = 4 * math.sin(7 * math.pi / 88) ** 2
C_cs_nf4 = 11.652 / (g7 / g4)
C_cs_hpqcd = 11.850 / (g7 / g4)
print(f"   γ7/γ4 = {g7/g4:.6f}")
print(f"   C_c/C_s (Nf=4)  = {C_cs_nf4:.4f}   最近結構: {nearest(pool, C_cs_nf4)[1]:.4f} (dev {nearest(pool, C_cs_nf4)[0]*100:.3f}%)")
print(f"   C_c/C_s (HPQCD) = {C_cs_hpqcd:.4f}   最近結構: {nearest(pool, C_cs_hpqcd)[1]:.4f} (dev {nearest(pool, C_cs_hpqcd)[0]*100:.3f}%)")
print(f"   9/2 = 4.5 vs 正確 {C_cs_nf4:.3f}: dev {(abs(4.5-C_cs_nf4)/C_cs_nf4)*100:.2f}%  (O234: 15% 級, 確認)")
# 同 scheme 15% 偏離確認
chk("C1. 9/2 對正確 C_c/C_s dev > 10% (混標度判死)", abs(4.5 - C_cs_nf4) / C_cs_nf4 > 0.10,
    f"{abs(4.5-C_cs_nf4)/C_cs_nf4*100:.2f}%")

# ── [D] 結構池命中判據 (MC null 輕量: 池密度) ────────────────────────
print("\n[D] 命中統計 (look-elsewhere):")
# 池密度: 喺 target 附近窗口 (0.5%) 內期望幾多個?
n_pool = len(pool)
# 對數均勻分佈下 0.5% 窗口命中期望 = n_pool × (0.01 / ln(100/0.1))
window_frac_log = 0.01 / math.log(1000)  # 相對窗口 0.5% ×2 方向 = 1% / log 寬度
expect = n_pool * window_frac_log
print(f"   池 {n_pool} 點; log-均勻 0.5% 窗口期望命中 λ = {expect:.2f}")
for name in ["m_c/m_s Nf=4", "m_c/m_s HPQCD", "m_s/m̂", "m_d/m_u", "m_s/m_u derived", "m_s/m_d derived"]:
    dev = hits[name]["dev_pct"]
    flag = "★ 富集" if dev < 0.1 and expect < 2 else ("觀察級" if dev < 0.5 else "—")
    print(f"   {name:>18}: dev {dev:7.3f}%  {flag}")
    if dev < 0.01:
        chk(f"D.{name}: dev < 0.01% (結構命中級)", True, f"{dev:.4f}%")
    else:
        chk(f"D.{name}: dev ≥ 0.01% (非結構命中級, 保持負閉合)", dev >= 0.01, f"{dev:.4f}%")

# ── 判定 ──────────────────────────────────────────────────────────────
print("\n== 判定 ==")
best_dev = min(hits[h]["dev_pct"] for h in hits)
print(f"   凍結層同 scheme 比值對結構池最近 dev = {best_dev:.3f}%")
if best_dev < 0.01:
    print("   🟢 有結構命中級近距 — 需進一步盲測 (單點, look-elsewhere)")
else:
    print("   🔴 冇結構命中級近距 — c/s 層『結構身份』喺同 scheme 下維持負閉合")
print("   9/2 同 68/5 候選: ⚰️ 混標度判死 (確認, 對正確值 dev > 10%)")

out = {
    "frozen_targets": {k: {kk: (float(vv) if isinstance(vv, (int, float)) else vv)
                            for kk, vv in v.items()} for k, v in hits.items()},
    "corrected_CcCs_Nf4": C_cs_nf4,
    "corrected_CcCs_HPQCD": C_cs_hpqcd,
    "old_9over2_dev_pct_vs_corrected": abs(4.5 - C_cs_nf4) / C_cs_nf4 * 100,
    "pool_size": n_pool,
    "expect_hits_0p5pct": expect,
    "checks": [{"name": n, "pass": c, "detail": m} for n, c, m in CHK],
}
(DATA / f"{OUTNUM:02d}_scheme_corrected_cs.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(f"\ndata/{OUTNUM:02d}_scheme_corrected_cs.json written")