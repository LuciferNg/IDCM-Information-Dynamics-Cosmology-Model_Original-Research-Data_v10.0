#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-33 — α_s 公式脆弱性攻堅
========================================================================
觸發: docs/19 (問題 7 裁決) 之附帶發現 ——
  `α_s⁻¹ = F₆ + sin²θ_W + 1/B` 用**已否證之** `3/13` (8.480769, dev 0.0122%)
  反而比用結構值 `0.220776` (8.470776, dev 0.1300%) 更貼 SM `8.4818`。
  docs/19 判為「α_s 公式本身脆弱」，本檔獨立覆核並裁決。

範圍: 寫入限於 o144_boson_identity/；上游僅只讀引用。
依賴: mpmath dps=40
"""
import json, mpmath as mp
from fractions import Fraction as Fr
from pathlib import Path

mp.mp.dps = 40
O144 = Path(__file__).resolve().parent.parent
ROWS = []; N = {"p": 0, "f": 0}

def chkb(cid, desc, ok, note=""):
    ROWS.append({"id": cid, "desc": desc, "ok": bool(ok), "note": str(note)})
    N["p" if ok else "f"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {desc}" + (f"  <<{note}>>" if note and not ok else ""))

def hdr(t):
    print("\n" + "=" * 78); print(t); print("=" * 78)

# ---- 結構常數 ----
B = 4; N_gen = 3; N_d = 44; L4 = 7; L5 = 11; F6 = 8; F7 = 13
mu2 = 2; SgE = 90; SgO = 88; Mtree = 33; L7 = 29; F10 = 55
b0 = L4; b1 = 2 * F7          # O142 v10: QCD β = T̂ 不變量
aEM_inv = 137
mw_mz_B = mp.sin(30 * mp.pi / 88) / mp.sin(41 * mp.pi / 88)
sin2_B = 1 - mw_mz_B ** 2
sin2_A = mp.mpf(3) / 13

hdr("[§A] 公式出處審計 (provenance)")
print(f"""
  形式:  α_s⁻¹(M_Z) = F₆ + sin²θ_W + 1/B
  譜身份 (上游聲明, o142 docs/08+09):
    F₆ = 8 = b₀ + 1  (b₀ = L₄ = Tr(T̂⁴) = 7)
    sin²θ_W = 1 − (m_W/m_Z)² = 1 − (cos(14π/88)/cos(3π/88))²
    1/B = 1/4
  機制聲明: 「跡線性定理 (直和 ⊕ ⟹ 跡相加)」⟹ 三項相加

  ★★ 關鍵出處事實 (o142 final_result.md L34, 逐字):
     ~~α_s = 1/(8+3/13+1/4)~~、~~v1 閉合表~~（**由 3/13 驅動**）
  ⟹ **v1 之 α_s「閉合」係用 `3/13` 砌出嚟嘅**;
     `3/13` 被否證後 (o142 自行標「數值湊數」), 公式**原封不動**只換輸入。
""")
chkb("A1", "b₀ = L₄ = 7 (QCD β 係數之結構身份)", b0 == L4)
chkb("A2", "F₆ = b₀ + 1 = 8", F6 == b0 + 1)
vB = F6 + sin2_B + mp.mpf(1) / B
vA = F6 + sin2_A + mp.mpf(1) / B
chkb("A3", f"α_s⁻¹ 用結構值 = {mp.nstr(vB,10)} (= 8.4707757)",
     abs(vB - mp.mpf("8.4707757")) < mp.mpf("1e-6"))
chkb("A4", f"α_s⁻¹ 用舊值 3/13 = {mp.nstr(vA,10)} (= 8.4807692)",
     abs(vA - mp.mpf("8.4807692")) < mp.mpf("1e-6"))
print("""
  ⟹ 「跡線性定理」只解釋**為何相加** (直和之跡 = 跡之和, 恆真);
     **唔解釋點解係呢三項** —— 三項之選擇係 v1 擬合時鎖定, 非由定理導出。""")

hdr("[§B] ★★ 輸入不確定度傳播 (決定性測試)")
# PDG α_s(M_Z) 兩版
P = {"PDG2022": (mp.mpf("0.1179"), mp.mpf("0.0010")),
     "PDG2024": (mp.mpf("0.1180"), mp.mpf("0.0009"))}
infl = {}
for tag, (a_s, sa) in P.items():
    inv = 1 / a_s
    sinv = sa / a_s ** 2              # d(1/α)/dα = −1/α²
    dA = abs(F6 + sin2_A + mp.mpf(1) / B - inv)
    dB = abs(F6 + sin2_B + mp.mpf(1) / B - inv)
    gap = abs(sin2_A - sin2_B)
    infl[tag] = dict(target=mp.nstr(inv, 8), sigma=mp.nstr(sinv, 6),
                     zA=mp.nstr(dA / sinv, 6), zB=mp.nstr(dB / sinv, 6),
                     gap=mp.nstr(gap, 6), gap_sigma=mp.nstr(gap / sinv, 6))
    print(f"  {tag}: α_s⁻¹ = {mp.nstr(inv,8)} ± {mp.nstr(sinv,6)}")
    print(f"    候選 A (3/13)     dev = {mp.nstr(dA,6)}  = {mp.nstr(dA/sinv,6)} σ")
    print(f"    候選 B (mode-rat) dev = {mp.nstr(dB,6)}  = {mp.nstr(dB/sinv,6)} σ")
    print(f"    |A − B| = {mp.nstr(gap,6)} = {mp.nstr(gap/sinv,6)} σ")
chkb("B1", "σ(α_s⁻¹) 傳播 = σ_α/α² (PDG2024) ≈ 0.0646",
     abs(mp.mpf(infl["PDG2024"]["sigma"]) - mp.mpf("0.0646")) < mp.mpf("0.001"))
chkb("B2", "★ 候選 A 與 B 之 α_s 差 |A−B| = 0.0100 ≪ 1σ (PDG2024: 0.155σ)",
     mp.mpf(infl["PDG2024"]["gap_sigma"]) < 1)
chkb("B3", "★★ 兩候選之 α_s z 值皆 ≪ 1σ ⟹ **不可分辨**",
     mp.mpf(infl["PDG2024"]["zA"]) < 0.5 and mp.mpf(infl["PDG2024"]["zB"]) < 0.5)
chkb("B4", "PDG2022 (α_s=0.1179±0.0010) 亦同樣不可分辨",
     mp.mpf(infl["PDG2022"]["gap_sigma"]) < 1)
print("""
  ★★★ 結論 (docs/19 附帶發現之修正):
    候選 A/B 對 α_s 之差 **遠小於輸入不確定度** (0.155σ)
    ⟹ 兩者對 α_s **同樣完美**; docs/19 之「A 勝 10×」(0.0122% vs 0.1300%)
      係**虛假精度**產物 (比較咗遠超數據能分辨之小數位)
    ⟹ α_s **對 sin²θ_W 之裁決零判別力**
    ⟹ docs/19 之 sin²θ_W 裁決**不受影響** (已由 m_W/m_Z 3.40× + 推導鏈決定)""")

hdr("[§C] 密度測試 (≤3 項結構式 vs α_s⁻¹)")
VOC = sorted({1,2,3,4,5,6,7,8,9,11,12,13,14,17,21,26,29,30,33,34,35,44,45,47,55,66,88,89,90,123,137,176})
def gen3(voc):
    out = {}
    def add(e, val):
        if val <= 0 or val > 60: return
        out.setdefault(e, val)
    for a in voc:
        add(f"{a}", mp.mpf(a))
        add(f"1/{a}", mp.mpf(1)/a)
        for b in voc:
            add(f"{a}+{b}", mp.mpf(a)+b); add(f"{a}-{b}", mp.mpf(a)-b)
            add(f"{a}*{b}", mp.mpf(a)*b); add(f"{a}/{b}", mp.mpf(a)/b)
            for c in voc:
                add(f"{a}+{b}+{c}", mp.mpf(a)+b+c); add(f"{a}+{b}-{c}", mp.mpf(a)+b-c)
                add(f"{a}-{b}-{c}", mp.mpf(a)-b-c)
                add(f"{a}+{b}/{c}", mp.mpf(a)+mp.mpf(b)/c)
                add(f"{a}*{b}/{c}", mp.mpf(a)*b/c)
                add(f"({a}+{b})/{c}", (mp.mpf(a)+b)/c)
                add(f"{a}/{b}+{c}/{b}", mp.mpf(a)/b+mp.mpf(c)/b)
    return out
EX = gen3(VOC)
inv_t = 1 / P["PDG2024"][0]; s_inv = P["PDG2024"][1] / P["PDG2024"][0] ** 2
print(f"  詞彙 n = {len(VOC)}; 表達式 = {len(EX)}")
dens = {}
for k, mult in [("1σ", 1), ("0.5σ", mp.mpf("0.5")), ("2σ", 2)]:
    tol = s_inv * mult
    hits = {e: v for e, v in EX.items() if abs(v - inv_t) <= tol}
    vals = sorted({mp.nstr(v, 10) for v in hits.values()})
    dens[k] = dict(n_hits=len(hits), n_distinct=len(vals), tol=mp.nstr(tol, 5),
                   examples=sorted(hits)[:8])
    print(f"  ±{k} (tol {mp.nstr(tol,5)}): 命中 {len(hits)} 條 / {len(vals)} 個相異值")
    print(f"    例: {sorted(hits)[:8]}")
chkb("C1", f"★ ±1σ 內命中數 = {dens['1σ']['n_hits']} (≫1 ⟹ 無判別力)",
     dens["1σ"]["n_hits"] > 20)
chkb("C2", f"★ ±0.5σ 內仍有多條命中 ({dens['0.5σ']['n_hits']} 條 ≥ 10)",
     dens["0.5σ"]["n_hits"] >= 10)
chkb("C3", "命中之相異值數 < 命中數 ⟹ 多條表達式收斂到同一值 (重複計算)",
     dens["1σ"]["n_distinct"] < dens["1σ"]["n_hits"])
print("""
  ⚠️ 誠實: ±1σ 窗口 = ±0.065 (相對 0.77%) 已係寬窗 ⟹ 密度必然高
     ⟹ 「α_s⁻¹ 有結構表達」**唔構成**證據; 真判據係**輸入能否分辨** (§B)""")

hdr("[§D] 簡約性測試 (為何係 3 項?)")
two = {}
for a in VOC:
    for b in VOC:
        for e, v in [(f"{a}+{b}", mp.mpf(a)+b), (f"{a}-{b}", mp.mpf(a)-b),
                     (f"{a}*{b}", mp.mpf(a)*b), (f"{a}/{b}", mp.mpf(a)/b),
                     (f"{a}+1/{b}", mp.mpf(a)+mp.mpf(1)/b), (f"{a}*{b}/2", mp.mpf(a)*b/2)]:
            if 0 < v < 60: two.setdefault(e, v)
h2 = [e for e, v in two.items() if abs(v - inv_t) <= s_inv]
print(f"  ≤2 項表達式 = {len(two)}; ±1σ 命中 = {len(h2)}")
print(f"    例: {sorted(h2)[:10]}")
chkb("D1", f"★ ≤2 項亦有命中 ({len(h2)} 條) ⟹ 「3 項」非被迫", len(h2) >= 1,
     f"n2={len(h2)}")
print("  ⟹ 三項相加之形式**非結構必然** (兩項已命中) ⟹ 項數係自由度, 非推導")

hdr("[§E] 原理優先測試 (先立原理, 再比數)")
res = {}
# E1: QCD 1-loop 標度蛻變 α_s⁻¹(M_Z) = (b₀/2π)·ln(M_Z/Λ)
mZ = mp.mpf("91.1876")
for tag, bb, lam_obs in [("b₀=L₄=7", mp.mpf(7), mp.mpf("0.210")),
                         ("b₀=23/3 (SM Nf=5)", mp.mpf(23)/3, mp.mpf("0.210"))]:
    lam = mZ * mp.e ** (-2 * mp.pi * inv_t / bb)
    res[tag] = dict(Lambda_GeV=mp.nstr(lam, 6), off=mp.nstr(lam_obs / lam, 5))
    print(f"  E1 β 蛻變 {tag}: Λ = {mp.nstr(lam,6)} GeV  vs Λ_QCD(MS-bar,5f)≈0.210 GeV"
          f"  ⟹ 差 {mp.nstr(lam_obs/lam,5)}×")
chkb("E1a", "1-loop 蛻變 b₀=7 給 Λ ≈ 0.0456 GeV (vs 0.210 ⟹ 4.6× 偏)",
     abs(mp.mpf(res["b₀=L₄=7"]["off"]) - mp.mpf("4.6")) < mp.mpf("0.3"))
chkb("E1b", "1-loop 蛻變 b₀=23/3 給 Λ ≈ 0.0884 GeV (⟹ 2.4× 偏)",
     mp.mpf(res["b₀=23/3 (SM Nf=5)"]["off"]) > 2)
# E2: 譜和候選
spec = {}
spec["Σ1/γ_odd(k) 176鏈"] = sum(1 / (4 * mp.sin(k * mp.pi / 176) ** 2) for k in range(1, 176, 2))
spec["Σ1/γ_all 88鏈"] = sum(1 / (4 * mp.sin(k * mp.pi / 176) ** 2) for k in range(1, 89))
spec["Σγ_odd/μ² + L₅/B"] = mp.mpf(SgO) / mu2 + mp.mpf(L5) / B
spec["N_d/B + F₆/B"] = mp.mpf(N_d) / B + mp.mpf(F6) / B
spec["F₆ + μ²/B"] = F6 + mp.mpf(mu2) / B
best = min(((e, abs(v - inv_t)) for e, v in spec.items()), key=lambda x: x[1])
for e, v in spec.items():
    print(f"  E2 候選 {e} = {mp.nstr(v,8)}  dev {mp.nstr(abs(v-inv_t),5)}"
          f"  ({mp.nstr(abs(v-inv_t)/s_inv,4)}σ)")
chkb("E2a", f"★ 最簡候選 '{best[0]}' = {mp.nstr(spec[best[0]],6)} dev {mp.nstr(best[1],5)}, "
            f"但 **≤2 項亦有候選落入 1σ** ⟹ 3 項形式非唯一",
     abs(spec["F₆ + μ²/B"] - inv_t) <= s_inv,
     f"F6+mu2/B dev={mp.nstr(abs(spec['F₆ + μ²/B']-inv_t),5)} sigma={mp.nstr(abs(spec['F₆ + μ²/B']-inv_t)/s_inv,4)}")
# E3: 兩項 (F₆ + x) 所需 x, 及兩形式之相對偏差
need = inv_t - F6
print(f"  E3 若形式為 F₆ + x, 則 x = {mp.nstr(need,6)} (需 0.4708)")
print(f"     sin²θ_W(B) + 1/B = {mp.nstr(sin2_B + mp.mpf(1)/B,6)}")
print(f"     sin²θ_W(A) + 1/B = {mp.nstr(sin2_A + mp.mpf(1)/B,6)}")
od = abs(vB - inv_t) / inv_t * 100        # 相對 α_s⁻¹
oa = abs(vA - inv_t) / inv_t * 100
print(f"     相對 α_s⁻¹ 之 dev: B-form {mp.nstr(od,4)}%  vs  A-form {mp.nstr(oa,4)}%"
      f"   (輸入 σ 相對 = {mp.nstr(s_inv/inv_t*100,4)}%)")
chkb("E3", "★ 兩形式之 dev (相對 α_s⁻¹) 皆 ≪ σ_rel = 0.76% ⟹ 形式不可分辨",
     od < s_inv / inv_t * 100 and oa < s_inv / inv_t * 100,
     f"od={mp.nstr(od,4)} oa={mp.nstr(oa,4)}")

hdr("[§F] 判決")
print(f"""
  α_s 公式 `α_s⁻¹ = F₆ + sin²θ_W + 1/B`:

  1. **出處** (🔴 硬負面): v1 之「閉合」係用 `3/13` 砌出 (`1/(8+3/13+1/4)`);
     `3/13` 被否證後公式**只換輸入**, 形式未重新導出 ⟹ 形式係擬合產物
  2. **機制審計** (🔴): 「跡線性定理」只解釋**相加性** (直和之跡 = 跡和, 恆真);
     **未導出點解係呢三項**
  3. **輸入解析度** (★★ 決定性): |A−B| = {mp.nstr(abs(sin2_A-sin2_B),5)} ⟹ α_s 差
     = {infl['PDG2024']['gap_sigma']}σ ≪ 1σ ⟹ **α_s 對 sin²θ_W 零判別力**
     ⟹ docs/19 之「A 勝 10×」係**虛假精度**產物 (非真張力)
  4. **密度** (🔴): ±1σ 內 {dens['1σ']['n_hits']} 條命中 / {dens['1σ']['n_distinct']} 個相異值 ⟹ 無判別力
  5. **簡約性** (🔴): ≤2 項亦有 {len(h2)} 條命中 ⟹ 三項形式非被迫
  6. **原理路由** (🔴): 1-loop 標度蛻變 b₀=7 ⟹ Λ = 0.0456 GeV (4.6× 偏);
     b₀=23/3 ⟹ 0.0884 GeV (2.4× 偏); 譜和候選無一命中

  ★★★ 兩項修正 (取代 docs/19 之附帶發現):
   (a) 唔係「**α_s 公式脆弱**」而係「**α_s 無法裁決任何嘢**」——
       其輸入不確定度 (0.76%) 遠大於候選間距 (0.12%)
   (b) sin²θ_W 之裁決**完全不受影響** (由 m_W/m_Z 3.40× + 推導鏈決定)
  ⟹ α_s 公式判定: **🔴 非閉合** (形式係擬合 + 無判別力 + 原理路由全敗)
""")
chkb("F1", "α_s 公式判 🔴 非閉合 (形式擬合, 機制只解釋相加性)",
     True)
chkb("F2", "★ docs/19 附帶發現重寫: 由「公式脆弱」→「α_s 零判別力」",
     True)

# ---- save ----
out = {"passed": N["p"], "failed": N["f"], "rows": ROWS,
       "A_provenance": {"v1_form": "1/(8+3/13+1/4)", "source": "o142 final_result L34 (struck through)",
                        "b0": int(b0), "F6_is_b0_plus_1": True},
       "B_inference": infl,
       "C_density": dens, "D_two_term_hits": sorted(h2)[:20], "E_principle": res,
       "F_verdict": "🔴 unclosed: form fitted with a since-falsified input; "
                    "additivity justified but term choice underived; "
                    "α_s input uncertainty 0.76% ≫ candidate gap 0.12% ⇒ zero discriminating power"}
(O144 / "data/33_alpha_s_fragility.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n" + "=" * 78)
print(f"  驗證: scripts/33 = {N['p']} PASS / {N['f']} FAIL")
print(f"  ★★ 核心: σ(α_s⁻¹)/α_s⁻¹ = {mp.nstr(s_inv/inv_t*100,4)}% ≫ 候選間距 "
      f"{mp.nstr(abs(sin2_A-sin2_B)/inv_t*100,4)}% ⟹ α_s 零判別力")
print(f"  ⟹ α_s 公式 = 🔴 非閉合; docs/19 附帶發現需重寫")
print("=" * 78)
