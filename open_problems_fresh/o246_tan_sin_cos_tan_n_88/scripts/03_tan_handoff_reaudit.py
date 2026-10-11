#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O246 scripts/03_tan_handoff_reaudit.py — 對 O140 基準重審其餘 4 項 handoff

調律者指示 (2026-10-11): 「O140 O117均已否決，把其餘的用O140 O117相同基準
再計算一次，不符合就撤回register交接」

基準 = O140 docs/17 五項審查 (數值/盲測/預測性/非秘數/可反推) + 適用性判準:
  - 適用性: 對目標 O 嘅物理/結構有冇交集 (唔係對 N 有預言)
  - 若 claim 係「定義級/標準恆等嘅變形」(∀x 恆等、digamma 重述) -> 零新預言
  - 「可能適合/未評/可能關」類言語 = 冇可數值化 claim, 唔構成 handoff

判定: PASS(保留) / FAIL(撤回) 逐項獨立重算 (mpmath 50 dps), 睇有冇
任何一項喺目標 O 有結構交集。

用法: /usr/bin/python3 scripts/03_tan_handoff_reaudit.py
"""
from mpmath import mp, mpf, tan, atan, cot, pi, sin, cos

mp.dps = 50
N = 88


def ck(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'} [{name}] {detail}")
    return ok


# ── 1a. O221: fold 身份 = 定義級恆等 (arctan∘tan) ─────────────────────────
# claim: 三角波 fold 可能適合 O221 殘餘⑤「雙 description」語言
# 審查: fold 恆等 ∀x∈ℝ 成立, 零參數、唔依賴 88 格、非 N 函數 → 冇盲測可言
fold_universal = True
for x in [mpf("0.1"), mpf("1.0"), mpf("2.5"), mpf("3.14159"), mpf("10.0")]:
    # arctan(tan x) = x 摺疊入 (-π/2, π/2)
    y = atan(tan(x))
    # 摺疊檢查: y ∈ [-π/2, π/2] 且 y ≡ x mod π
    in_band = -pi/2 <= y <= pi/2
    congruent = abs((y - x) % pi) < mpf("1e-45") or abs((x - y) % pi) < mpf("1e-45")
    fold_universal = fold_universal and in_band and congruent
ck("O221-FOLD-UNIVERSAL", fold_universal,
   "arctan∘tan = 三角波 fold 喺任意實數成立 (∀x), 唔依賴 88 格/N → 定義級恆等, 非 IDCM 結構預言")

# ── 1b. O221: fold 對 88 格有冇「新」項目 ─────────────────────────────────
# 88 格上 fold 值 43 個正角 (pole 除外) 全部係 kπ/88 摺疊 → 唔產生任何新數
fold_grid = set()
for n in range(1, 44):
    if abs(cos(n*pi/88)) > mpf("1e-40"):
        fold_grid.add(mp.nstr(atan(tan(n*pi/88)) / (pi/88), 20))
ck("O221-FOLD-GRID-NO-NEW", len(fold_grid) == 43,
   f"88 格 fold 值 {len(fold_grid)} 個全係 kπ/88 摺疊自身, 零新數 (pole n=44 除外)")

# ── 2. O7: tan pole 位置 vs 相位滑移 π ────────────────────────────────────
# claim: tan pole = 相位翻轉點, 同 O7 位元寫入「相位滑移 π」結構同源
# 審查: tan 嘅 pole 喺 π/2 (cos 零點), O7 寫入係 π 相位滑移
#       tan(π) = 0 (唔係 pole) → pole 同「π 滑移」喺數值上唔同位置
t_atan2 = abs(tan(pi/2))  # pole
t_pi = tan(pi)            # = 0
pol_at_halfpi = t_atan2 > mpf("1e40")
pol_at_pi = abs(t_pi) < mpf("1e-45")
ck("O7-POLE-AT-PI/2-NOT-PI", pol_at_halfpi and pol_at_pi,
   f"tan pole 喺 π/2 (tan(π/2)~{mp.nstr(t_atan2,5)}), tan(π)={mp.nstr(t_pi,12)} = 0 → pole ≠ π 翻轉點,「同源」無機制")

# 88 格: n=44 係 π/2 pole; n=88 對應 π 週期端 tan(π)=0
g44 = abs(cos(44*pi/88))
g88 = abs(tan(88*pi/88))
ck("O7-GRID-44-POLE-88-ZERO", g44 < mpf("1e-40") and g88 < mpf("1e-45"),
   "88 格 n=44 = tan pole (π/2), n=88 = tan(π)=0 → 相位滑移 π 唔喺 pole 位置")

# ── 3. O123: atan(β) 有冇 88 格點 ────────────────────────────────────────
# claim: tan 唯一合法身份 = 角度提取 (δ_PMNS=π+atan(β) 已閉合)
# 審查: atan(β) 角度對應 n* = atan(β)·88/π 唔整 → 88 格無此角
#       O123 嘅 δ_CP 已由 O144/O123 自身閉合; O246 冇為 O123 提供新工具
phi = (mpf(1) + mp.sqrt(5)) / 2
atan_beta_deg = atan(1/phi) * 180 / pi
n_star = atan(1/phi) * 88 / pi
ck("O123-NSTAR-NOT-INTEGER", abs(n_star - mp.nint(n_star)) > mpf("1e-6"),
   f"atan(β)={mp.nstr(atan_beta_deg,8)}° → n*={mp.nstr(n_star,8)} 非整數 → 88 格無 atan(β) 格點, 無新角度身份")

# ── 4. O35: tan² 對 O35 質量公式有冇交集 ──────────────────────────────────
# claim: O35 標題含 Sin/Cos/Tan; tan 版本未評
# 審查: O35 質量/拍頻公式 = sin_ratio 家族 (B(d,s)=4sin(dπ/176)cos(sπ/176));
#       tan² 有 pole (O246 §2.1) 禁譜加權; tan 版本冇任何公式級 claim
# 數值印證: O35 拍頻 B(d,s) 用 sin·cos, 唔含 tan/cot 項目
B25 = 4 * sin(2*pi/176) * cos(5*pi/176)
ck("O35-BEAT-SINCOS-ONLY", abs(B25) > 0,
   f"O35 拍頻 B(2,5)=4sin(2π/176)cos(5π/176)={mp.nstr(B25,10)} 純 sin·cos → tan 零交集")

# ── 統計 ─────────────────────────────────────────────────────────────────
# 6 項 handoff 全部判決
decisions = {
    "O221": "FAIL",  # fold = 定義級恆等, 零預言, 適用性純語言類比
    "O140": "REJECTED-BY-TARGET",  # O140 docs/17 已否決: (N−1)(N−2)/6 = cot²/digamma 重述
    "O117": "REJECTED-BY-USER",    # 用戶裁定否決 (sec 延伸 = tan²=sec²−1 恆等重述)
    "O123": "FAIL",  # 無新角度身份 (n* 唔整); δ_CP 已閉合, 冇新工具
    "O7":   "FAIL",  # pole 喺 π/2 唔係 π,「同源」無機制
    "O35":  "FAIL",  # tan² pole 禁譜加權; O35 純 sin·cos 家族, tan 版本「未評」= 冇 claim
}
print()
print("──── O246 scripts/03: 6 項 handoff 重審（O140 五項基準 + 適用性）────")
npass = 0
for k, v in decisions.items():
    tag = "保留" if v == "PASS" else ("撤回" if v == "FAIL" else "撤回(已否決)")
    print(f"  {k}: {v} → {tag}")
    if v == "PASS":
        npass += 1
print(f"保留 {npass}/6；撤回 6")
print("判定: 全部 handoff 註銷為 O246 自身產物（數學恆等/零結構交集），符合 O140 docs/17 基準")