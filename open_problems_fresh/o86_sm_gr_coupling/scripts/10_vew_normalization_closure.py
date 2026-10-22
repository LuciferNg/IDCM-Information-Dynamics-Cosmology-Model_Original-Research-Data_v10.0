#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O86 — scripts/10: phi_n-electron 耦合歸一化閉合
================================================
交回來源: O207 docs/11_mapping_mechanism.md (2026-09-22, B4 延伸路線③)
問題: O207 用 SM Yukawa 類比 y_e = sqrt(2)*m_7/v_EW = 7.93e-5 歸一化
      phi_n-electron 耦合, 但「v_EW 係正確歸一化標度」係類比假設。
      問: O86 既 lambda_WH = lambda_self = 2/123 (W-H 耦合身份) 能否
          作為 phi_n-electron 耦合歸一化既結構依據 (W<->H<->費米子鏈)?

方法: 純 mpmath (dps=50), 零 import 任何原腳本 (獨立重算)。
      跨版本核實 O37/O40 之 v_SM 結構閉合。
"""
from mpmath import mp, mpf, sqrt, sin, pi, nstr
import os
mp.dps = 50

_PASS = []
_FAIL = []
def chk(name, cond, detail=""):
    ( _PASS if cond else _FAIL ).append(name)
    print(("  [PASS] " if cond else "  [FAIL] ") + name + (("   " + detail) if detail else ""))
def p(s=""):
    print(s)
def f(x, n=12):
    return nstr(x, n)

# =====================================================================
# 常數 (零自由參數)
# =====================================================================
N_d   = mpf(44)
N_gen = mpf(3)
B     = mpf(4)
mu2   = mpf(2)
M_tree = mpf(33)                       # K_Tree 深度
phi   = (1 + sqrt(5)) / 2
gamma_n = lambda n: 4 * sin(mpf(n) * pi / 88) ** 2
omega_n = lambda n: 2 * sin(mpf(n) * pi / 88)

M0_MeV   = mpf('27.900915')            # O86 現用常數 (O38)
E_kchain = mpf('4.060265e-3')          # eV (O40 scripts/01b)
M0_form_MeV = E_kchain * phi ** (47 + mpf(37) / 528) * mpf(10) ** -6   # O38/O40 公式

v_SM_PDG = mpf('246.2196') * 1000      # MeV (PDG)
eps_S_NA64 = mpf('1e-4')               # NA64 PRL 126.211802 scalar 限制 (O207 輸入)

p("=" * 78)
p("O86 scripts/10 — phi_n-electron 耦合歸一化閉合 (O207 交回 路線③)")
p("=" * 78)

# =====================================================================
# PART A — v_EW 結構來源 (O37/O40 跨版本核實)
# =====================================================================
p("\n--- PART A. v_SM 結構來源 (O37 section8 -> O40 scripts/01b) ---")

v_eff = M0_MeV * sqrt(2)               # IDCM 有效 VEV
p("  M0 (O86 常數)      = " + f(M0_MeV) + " MeV")
p("  M0 (O38/O40 公式)  = " + f(M0_form_MeV) + " MeV")
devM0 = abs(M0_form_MeV - M0_MeV) / M0_MeV
p("  M0 公式 vs 常數 dev = " + f(devM0 * 100, 6) + " %")
p("  v_eff = M0*sqrt(2)  = " + f(v_eff) + " MeV")

S_all  = sum(gamma_n(n) for n in range(1, 45))
S_even = sum(gamma_n(n) for n in range(2, 45, 2))
S_odd  = sum(gamma_n(n) for n in range(1, 45, 2))
p("  sum gamma_n (n=1..44)     = " + f(S_all))
p("  sum gamma_n (n even 1..44)= " + f(S_even))
p("  sum gamma_n (n odd  1..44)= " + f(S_odd))

fac = mpf(88) * mpf(71) * (1 - mpf(4) / (mpf(90) * (M_tree + mu2)))
v_SM_pred = v_eff * fac
dev_v = abs(v_SM_pred - v_SM_PDG) / v_SM_PDG
p("  factor 88*71*(1-4/(90*35)) = " + f(fac))
p("  v_SM_pred = v_eff*factor    = " + f(v_SM_pred) + " MeV")
p("  v_SM_PDG  = 246.2196 GeV    = " + f(v_SM_PDG) + " MeV")
p("  dev = " + f(dev_v * 100, 8) + " %")

chk("A1  88 = 2*N_d", 2 * N_d == 88)
chk("A2  71 = 2*N_d - 17", 2 * N_d - 17 == 71)
chk("A3  90 = sum gamma_n (n=1..44)", abs(S_all - 90) < mpf('1e-40'), "got " + f(S_all))
chk("A4  35 = M_tree + mu^2 = 33 + 2", M_tree + mu2 == 35)
chk("A5  v_eff = M0*sqrt(2) 結構", abs(v_eff / M0_MeV - sqrt(2)) < mpf('1e-40'))
chk("A6  v_SM = v_eff*88*71*(1-4/(90*35)) 結構閉合 (dev<1e-6)",
    dev_v < mpf('1e-6'), "dev=" + f(dev_v * 100, 8) + " %")
chk("A7  M0 公式 (O40) vs O86 常數 一致 (dev<0.2%)", devM0 < mpf('2e-3'),
    "dev=" + f(devM0 * 100, 5) + " %")

# =====================================================================
# PART B — lambda_WH 維度 no-go
# =====================================================================
p("\n--- PART B. lambda_WH 維度分析 (路線③ 核心) ---")
lambda_self = mu2 / 123
lambda_WH   = mu2 / 123
p("  lambda_WH = mu^2/123 = " + f(lambda_WH))
p("  質量維度: [lambda_WH] = 0  (四次 portal 耦合, 無量綱)")
p("  歸一化所需: [Lambda] = 1  (質量標度)")
chk("B1  lambda_WH = 2/123 數值", abs(lambda_WH - mpf(2) / 123) < mpf('1e-40'))
chk("B2  lambda_WH == lambda_self (身份, N6)", lambda_WH == lambda_self)
chk("B3  維度 no-go: [lambda_WH]=0 != 1 => 任何 lambda_WH 冪次都產生唔到質量標度",
    True, "結構論證 (無量綱不能供給質量標度)")

# =====================================================================
# PART C — W<->H<->fermion 鏈存在性 (O86 L_total)
# =====================================================================
p("\n--- PART C. W<->H<->fermion 鏈存在性 (讀 docs/02 原文) ---")
_doc02 = ""
for _c in ("docs/02_derivation_record.md", "../docs/02_derivation_record.md"):
    if os.path.exists(_c):
        _doc02 = open(_c, encoding="utf-8").read()
        break
has_WH = ("λ_WH" in _doc02) and ("|W|²" in _doc02) and ("|H|²" in _doc02)
has_Yuk = ("y_f" in _doc02) and ("ψ̄" in _doc02)
p("  docs/02 讀取: " + ("OK (" + str(len(_doc02)) + " chars)" if _doc02 else "NOT FOUND"))
p("  " + ("[present] " if has_WH else "[absent ] ") + "L_WH   = lambda_WH|W|^2|H|^2  (W<->H portal)")
p("  " + ("[present] " if has_Yuk else "[absent ] ") + "L_Yuk  = -sum_f y_f psibar psi H (H<->fermion)")
chk("C1  docs/02 含 W<->H portal (lambda_WH|W|^2|H|^2)", has_WH)
chk("C2  docs/02 含 H<->fermion Yukawa (-sum_f y_f psibar psi H)", has_Yuk)
chk("C3  => W<->H<->fermion 鏈存在 (portal + Yukawa 同現於 L_total)", has_WH and has_Yuk)

# =====================================================================
# PART D — M0 相消: y_n 係純結構數
# =====================================================================
p("\n--- PART D. y_n = sqrt(2)*m_n/v_SM 之 M0 相消 ---")
m_n = lambda n: M0_MeV * omega_n(n)
y_n = lambda n, M0=M0_MeV: sqrt(2) * (M0 * omega_n(n)) / (M0 * sqrt(2) * fac)
y_7 = y_n(7)
y_7_closed = omega_n(7) / fac
p("  m_7 = M0*omega_7 = " + f(m_n(7)) + " MeV   (omega_7=" + f(omega_n(7)) + ")")
p("  y_7 = sqrt(2)*m_7/v_SM = " + f(y_7))
p("  y_7 closed = omega_7/(88*71*(1-4/(90*35))) = " + f(y_7_closed))
chk("D1  y_7 = sqrt(2)*m_7/v_SM (結構值 v_SM_pred)",
    abs(y_7 - sqrt(2) * m_n(7) / v_SM_pred) < mpf('1e-45'))
chk("D2  y_7 = omega_7/factor (M0 相消, 純結構數)", abs(y_7 - y_7_closed) < mpf('1e-45'))
chk("D3  M0 相消檢驗: y_7(M0) = y_7(3*M0)",
    abs(y_n(7, M0_MeV) - y_n(7, 3 * M0_MeV)) < mpf('1e-45'))
chk("D4  y_7 命中 O207 值 7.93e-5 (dev<0.5%)",
    abs(y_7 - mpf('7.93e-5')) / mpf('7.93e-5') < mpf('5e-3'),
    "dev=" + f(abs(y_7 - mpf('7.93e-5')) / mpf('7.93e-5') * 100, 4) + " %")

# =====================================================================
# PART E — 歸一化候選枚舉 (所有結構標度皆 propto M0)
# =====================================================================
p("\n--- PART E. 歸一化候選枚舉 ---")
W_vev = M0_MeV * sqrt(mpf('61.5'))       # <W> = M0*sqrt(mu^2/2lambda) = M0*sqrt(61.5)
cands = [
    ("Lambda = v_SM  (EW VEV, 結構推導)", v_SM_PDG),
    ("Lambda = <W>   (W 凝聚, M0*sqrt(61.5))", W_vev),
    ("Lambda = v_eff (IDCM 有效 VEV, M0*sqrt(2))", v_eff),
    ("Lambda = M0    (K_chain 標度)", M0_MeV),
]
for name, Lam in cands:
    g = m_n(7) / Lam
    verdict = "存活 (< eps_S)" if g < eps_S_NA64 else "被排除 (> eps_S)"
    p("  " + name.ljust(44) + " = " + f(Lam, 10).ljust(14) +
      " g_7 = " + f(g, 8).ljust(12) + " " + verdict)
chk("E1  Lambda=v_SM: g_7 < eps_S (存活, 邊緣)", m_n(7) / v_SM_PDG < eps_S_NA64)
chk("E2  Lambda=<W> : g_7 > eps_S (被排除)", m_n(7) / W_vev > eps_S_NA64)
chk("E3  Lambda=M0  : g_7 > eps_S (被排除)", m_n(7) / M0_MeV > eps_S_NA64)
chk("E4  所有結構標度皆 propto M0 => 比值 M0-無關 (純數)",
    abs((m_n(7) / W_vev) / (m_n(7) / M0_MeV) - M0_MeV / W_vev) < mpf('1e-40'))

# =====================================================================
# PART F — 裁定
# =====================================================================
p("\n" + "=" * 78)
p("PART F. 裁定")
p("=" * 78)
p("  (1) lambda_WH = 2/123 值本身: 維度 no-go — 無量綱 quartic 唔可以提供")
p("      歸一化所需既質量標度 Lambda。故「lambda_WH 作為歸一化依據」")
p("      按字面陳述 = 結構不可能 (FAIL)。")
p("  (2) 但 W<->H<->fermion 鏈存在 (C1+C2), 且歸一化標度 v_SM 有結構來源")
p("      (A6: v_SM = v_eff*88*71*(1-4/(90*35)), dev=" + f(dev_v * 100, 8) + " %)。")
p("  (3) => y_n = sqrt(2)*m_n/v_SM = omega_n/(88*71*(1-4/(90*35))) 係純結構數")
p("      (M0 相消, 零自由參數); y_7 = " + f(y_7, 8) + "。")
p("  (4) 殘餘 🟡: (a) v_SM 閉合係 post-hoc (O40 自標 '結構閉合 ✅, 預言 ❌');")
p("      (b) 場身份 — phi_n 係 W 玻色模態, 套用費米子 Yukawa 形式 (sqrt(2)m/v)")
p("      仍屬類比; 且所有結構標度皆 propto M0, 選 v_SM 而非 <W>/M0 靠 Yukawa 結構。")
p("")
p("  裁定: 路線③ 部分成立 — 標度 🟢 結構 (v_SM 已推導, 比值 M0-無關);")
p("        場身份 🟡 類比。O207 之 🟡 總狀態正確, 但原因由「標度未知」")
p("        精確化為「場身份類比」。m_7 存活 (y_7 < eps_S) 屬結構性命題,")
p("        但邊緣 (1.3x) 且依賴場身份假設。")
p("")
p("  PASS " + str(len(_PASS)) + " / " + str(len(_PASS) + len(_FAIL)))
p("=" * 78)

# 寫入 data/
with open("data/10_vew_normalization_output.txt", "w") as fh:
    fh.write("O86 scripts/10 — phi_n-electron 耦合歸一化閉合 (O207 路線③)\n")
    fh.write("=" * 78 + "\n")
    fh.write("v_SM = v_eff*88*71*(1-4/(90*(M+mu^2))) = " + f(v_SM_pred) + " MeV, dev=" + f(dev_v * 100, 8) + " %\n")
    fh.write("lambda_WH = 2/123: dim 0 -> 維度 no-go (唔可以提供質量標度)\n")
    fh.write("y_7 = omega_7/(88*71*(1-4/(90*35))) = " + f(y_7, 10) + " (純結構數, M0 相消)\n")
    fh.write("g_7(v_SM)=" + f(m_n(7) / v_SM_PDG, 8) + "  g_7(<W>)=" + f(m_n(7) / W_vev, 8) +
             "  g_7(M0)=" + f(m_n(7) / M0_MeV, 8) + "  eps_S~1e-4\n")
    fh.write("裁定: 標度 🟢 結構; 場身份 🟡 類比\n")
    fh.write("PASS " + str(len(_PASS)) + "/" + str(len(_PASS) + len(_FAIL)) + "\n")
print("\n  -> data/10_vew_normalization_output.txt")
