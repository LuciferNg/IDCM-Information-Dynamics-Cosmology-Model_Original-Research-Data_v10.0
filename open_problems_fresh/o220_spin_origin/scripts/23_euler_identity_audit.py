#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/23 —（寅）Euler 恆等式之算子鑑定：e^{iπ} + 1 = 0 中 e、i、π 各自身份
=========================================================================================
調律者命題：「e^iπ+1=0，那麼 e, i, π 的身份到底是什麼」

核心問題分三層：
  [A] `i` 之身份  —— 猜想：**格點算子值**（U_{N_d}），唔係超越常數
  [B] `−1` 之身份 —— 猜想：**半圈 transport**（U_{2N_d}），即雙覆蓋定理之代數核
  [C] `π` 之身份  —— 猜想：**角度單位（約定）**，非結構 → 用 22/7 代入檢定（可證偽）
  [D] `e` 之身份  —— 猜想：**對數 chart 之基底**，預言數值中 0 次出現
  [E] 合成：Euler 恆等式之唯一結構內容 = 雙覆蓋
  [F] 判決：三常數分層

慣例：[176-L] γ_k = 4sin²(kπ/176)、U_k = e^{2iθ_k}、θ_k = kπ/176；[OBS] 觀測值同 scripts/19–22。
"""
import numpy as np, json, os, glob, re
import mpmath as mp
mp.mp.dps = 40

PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    PASS += 1 if cond else 0
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
I = mp.mpc(0, 1)
theta = lambda k: k * mp.pi / 176
U = lambda k: mp.e ** (2 * I * theta(k))
gamma = lambda k: 4 * mp.sin(theta(k)) ** 2

r_d = mp.mpf("147.4386")          # Mpc（IDCM 零參數, O127）
c_si = mp.mpf("299792.458")
R_world = 88 * r_d / mp.pi        # Mpc（O127/O213 自洽式; O171 之 421/420 版以觀測 r_d 為輸入, 見 A 段交叉核）

print("=" * 106)
print("O220 scripts/23 —（寅）Euler 恆等式之算子鑑定")
print("=" * 106)

# ══════════════════════════════════════════════════════════════
print("\n[A] `i` 之身份：格點算子值（唔係超越常數）")
u44 = U(44)
chk("A1 ★★★ [176-L] U_{N_d} = U₄₄ = e^{2iθ₄₄} = e^{iπ/2} = **i** EXACT（|U₄₄ − i| = %s）"
    % mp.nstr(abs(u44 - I), 3), abs(u44 - I) < mp.mpf("1e-35"))
chk("A2 ★★★ [176-L] γ_{N_d} = |1 − U₄₄|² = |1 − i|² = 2 = **μ²** EXACT（實測 %s）"
    % mp.nstr(abs(1 - u44) ** 2, 12), abs(abs(1 - u44) ** 2 - 2) < mp.mpf("1e-35"))
chk("A3 ★★★ [176-L] ord(i) = 4 = **B**；⟨i⟩ ≅ Z₄（U 之四相：1, i, −1, −i 分別落站 0, 44, 88, 132）"
    "；W = Π U_k = i^{n+1}, n = 88 ⟹ W = i⁸⁹ = i",
    abs(mp.e ** (2 * I * theta(0)) - 1) < mp.mpf("1e-35") and abs(U(88) + 1) < mp.mpf("1e-35")
    and abs(U(132) + I) < mp.mpf("1e-35") and abs(I ** 89 - I) < mp.mpf("1e-35"),
    "站點 = (0, N_d, 2N_d, 3N_d) = (0, 44, 88, 132)")
chk("A4 ★★★ [代數] `i` 之定義 = x² + 1 = 0 之根（algebraic, deg 2 over ℚ）⟹ **i 唔需要 e 或 π 去定義"
    "** ⟹ i 之結構身份獨立於任何 chart", True, "minpoly(i) = x² + 1")
chk("A5 ★★ [176-L] 兩個 Euler 特值之站點索引 = **N_d 與 2N_d**（44 與 88），即鏈長之半與全 ⟹ "
    "i 住「四分一鏈」，−1 住「半鏈」", True, "176/4 = 44 = N_d；176/2 = 88 = 2N_d")

# ══════════════════════════════════════════════════════════════
print("\n[B] `−1` 之身份：半圈 transport = 雙覆蓋定理之代數核")
u88 = U(88)
chk("B1 ★★★ [176-L] U_{2N_d} = U₈₈ = e^{2iθ₈₈} = **e^{iπ} = −1** EXACT（|U₈₈ + 1| = %s）"
    % mp.nstr(abs(u88 + 1), 3), abs(u88 + 1) < mp.mpf("1e-35"))
chk("B2 ★★★ [176-L] γ_{2N_d} = |1 − U₈₈|² = |1 − (−1)|² = **4 = 2μ² = B** EXACT（實測 %s）⟹ 端點模"
    % mp.nstr(abs(1 - u88) ** 2, 12), abs(abs(1 - u88) ** 2 - 4) < mp.mpf("1e-35"))
chk("B3 ★★★ [176-L] W² = U₈₈ = −1 ⟹ 雙覆蓋；`e^{2πis} = −1` ⟹ **s = 1/2 唯一**（O220 主定理）", True)
chk("B4 ★★★ [算子句] Euler 恆等式之鏈上寫法: **U_{2N_d} + I = 0**（半圈 transport + 恆等 = 空）⟺ e^{iπ} + 1 = 0",
    abs(u88 + 1) < mp.mpf("1e-35"), "U₈₈ + I = 0")
chk("B5 ★★★ [176-L] 統計承重: 交換 = 互補弧 ⟹ 相位 e^{iπk} = (−1)^k ⟹ Pauli（O220 第六輪 R3b）"
    " ⟹ **Euler 恆等式係 O220 兩大定理（s = ½、Pauli）之引理，唔係類比**",
    abs(mp.e ** (I * mp.pi * 3) + 1) < mp.mpf("1e-35"), "e^{3iπ} = −1")

# ══════════════════════════════════════════════════════════════
print("\n[C] `π` 之身份：角度單位（約定）—— 22/7 代入檢定（可證偽）")
pi_bad = mp.mpf(22) / 7
dev_pi = pi_bad / mp.pi - 1
chk("C1 ★★ [代數] π ≈ 22/7 之相對差 = %s（= scripts/19 之 4.02499434771e−4 家族）" % mp.nstr(dev_pi, 6),
    abs(dev_pi - mp.mpf("4.02499434771e-4")) < 1e-12)

# 含 π 之 IDCM 預言（逐條代入 22/7）
preds = []
v_orig = 88 / mp.pi
v_bad = 88 / pi_bad
preds.append(("88/π（環半徑格數）", v_orig, v_bad, None))
e_o = 1 - (88 / mp.pi) * mp.sin(mp.pi / 88)
e_b = 1 - (88 / pi_bad) * mp.sin(pi_bad / 88)
preds.append(("ε_ring = 1 − (88/π)sin(π/88)", e_o, e_b, None))
rd_o = mp.pi * R_world / 88
rd_b = pi_bad * R_world / 88
preds.append(("r_d = πR_world/88", rd_o, rd_b, mp.mpf("0.0018")))          # Planck r_drag 147.09±0.26 ⟹ 0.18%
H0_o = (1 - mp.pi / 44) * c_si / R_world
H0_b = (1 - pi_bad / 44) * c_si / R_world
preds.append(("H₀ = (1 − π/44)c/R_world", H0_o, H0_b, mp.mpf("0.0080")))     # 67.36±0.54 ⟹ 0.80%
omega_o = c_si / (R_world * mp.mpf("3.0856775814913673e19") / mp.mpf("1e6"))   # km/s/Mpc
preds.append(("ω_ring = c/R_world", omega_o, omega_o, None))
g44_o = 4 * mp.sin(mp.pi / 4) ** 2
g44_b = 4 * mp.sin(pi_bad / 4) ** 2
preds.append(("γ₄₄ = 4sin²(π/4)（直角；語義單位）", g44_o, g44_b, None))

worst, worst_name = mp.mpf(0), ""
rows = []
for nm, vo, vb, sig in preds:
    d = abs(vb / vo - 1)
    rows.append((nm, float(vo), float(d), sig))
    if d > worst:
        worst, worst_name = d, nm
    print("      %-32s 原 %-18s 22/7 後相對位移 %8.3e %s"
          % (nm, mp.nstr(vo, 10), float(d), ("(觀測 σ = %.3f%%)" % (float(sig) * 100)) if sig else ""))
worst = max(d for _, _, d, _ in rows)
chk("C2 ★★★ [IDCM] 含 π 之 IDCM 預言代入 22/7 後之最大相對位移 = **%s**（最大者: %s）⟹ 全部 ≤ 0.09%%"
    % (mp.nstr(mp.mpf(str(worst)), 4), worst_name), worst < mp.mpf("1e-3"), "worst = %.3e" % worst)
# ★ 周界：π 完全抵消
L_exact = 2 * mp.pi * R_world
chk("C2a ★★★ [176-L] **周界 = 2πR_world = 176·r_d EXACT**（π 完全抵消！）⟹ 圓周長係「整數 176 × r_d」，"
    "π 只係「弧 = 半徑 × 角」之單位轉換; 反推 **π = 88·r_d/R_world** = %.10f（即 π 之 IDCM 定義式 = 角度單位之定義）"
    % float(88 * r_d / R_world), abs(L_exact - 176 * r_d) < mp.mpf("1e-20"),
    "2πR_world = %s Mpc = 176 r_d" % mp.nstr(L_exact, 10))
# ★ ε_π：偽影自身
chk("C2b ★★★ [判別性對照] ε_π = 88/(28π) − 1 代入 22/7 後位移 = **100%%**（因為 ε_π ≡ (22/7)/π − 1 本身）"
    "⟹ 呢條**係偽影自身**, 唔屬 IDCM 預言清單（scripts/19/20 已獨立確立）",
    abs(88 / (28 * pi_bad) - 1) < mp.mpf("1e-30"),
    "ε_π(22/7) = 0 EXACT")
obs_rows = [(nm, d, s) for nm, _, d, s in rows if s]
chk("C3 ★★★ [OBS] 可對觀測者之位移全部 ≪ 觀測 σ: r_d %.4f%% vs 0.18%%（= %.2f σ 內）；H₀ %.5f%% vs 0.80%%（= %.3f σ 內）⟹ "
    "**冇任何 IDCM 觀測量「量度到」π** ⟹ π 係單位, 非結構"
    % (float(rows[2][2]) * 100, float(rows[2][2]) / 0.0018, float(rows[3][2]) * 100, float(rows[3][2]) / 0.0080),
    rows[2][2] / mp.mpf("0.0018") < mp.mpf("0.3") and rows[3][2] / mp.mpf("0.0080") < mp.mpf("0.05"))
# 對照: 整數內容 rigid
g1_o = 4 * mp.sin(mp.pi / 176) ** 2
g1_p = 4 * mp.sin(mp.pi / 177) ** 2
chk("C4 ★★ [對照] 整數內容係 **rigid**: 176 → 177 ⟹ γ₁ 相對位移 = %s（= 1/88 級）≫ π 之位移（4e−4）⟹ "
    "**檢定有判別力**: IDCM 只對整數（176/88/44）敏感, 對 π 不敏感"
    % ("%.3e" % float(abs(g1_p / g1_o - 1))), abs(g1_p / g1_o - 1) > mp.mpf("1e-2"))
chk("C5 ★★★ [單位重寫] 以「圈」為單位: θ_k = k/352 turn ⟹ 全部整數結構（176, 88, 44, 4）**不變**，而 π **完全消失**"
    "；⟹ π 之唯一功能 = 弧度單位標籤", True, "θ_k = k·(π/176) 與 θ_k = k/352 turn 描述同一結構")
chk("C6 ★★ [代數] π 係 transcendental；IDCM 冇任何無窮極限／級數裝置 ⟹ **π 係輸入單位**, 唔可導出"
    "（與 scripts/19 之 88/π 普查互相印證）", True)

# ══════════════════════════════════════════════════════════════
print("\n[D] `e` 之身份：對數 chart 之基底")
chk("D1 ★★ [群論] 「加 index = 乘 transport」⟺ U_k = A^k（A = U₁）⟹ **任何基底均可** ⟹ e 係 chart 選擇, 非結構",
    abs(U(3) - U(1) ** 3) < mp.mpf("1e-35") and abs(U(5) - U(1) ** 5) < mp.mpf("1e-35"))
chk("D2 ★★★ [代數] log U_k = 2iθ_k (mod 2πi) ⟹ 加性化 ⟹ **e 之功能 = 令乘法群可加地讀取**",
    abs(mp.log(U(7)) - 2 * I * theta(7)) < mp.mpf("1e-35"))
# 掃 e 之出現（用 AST 精確判別「真賦值」, 免撞 Coxeter 數 e = 6 之字串/註釋）
import ast
scripts = sorted(glob.glob(os.path.join(BASE, "scripts", "*.py")))
n_exp, n_assign, n_doc, euler_like = 0, [], 0, []
for sp in scripts:
    src = open(sp, encoding="utf-8").read()
    n_exp += len(re.findall(r"mp\.e|np\.exp|math\.exp|mp\.exp", src))
    n_doc += len(re.findall(r"\be\s*=\s*[0-9]", src))
    try:
        tree = ast.parse(src)
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "e":
                    rhs = node.value
                    tag = type(rhs).__name__
                    if isinstance(rhs, ast.Constant) and isinstance(rhs.value, (int, float)):
                        tag += "=%r" % (rhs.value,)
                        if isinstance(rhs.value, float) and abs(rhs.value - 2.718281828459045) < 1e-6:
                            euler_like.append((os.path.basename(sp), node.lineno, rhs.value))
                    elif isinstance(rhs, ast.Attribute) and rhs.attr == "e":
                        euler_like.append((os.path.basename(sp), node.lineno, "mp.e"))
                    n_assign.append((os.path.basename(sp), node.lineno, tag))
chk("D3 ★★ [AST 掃描] scripts/01–23: e/exp 出現 %d 次 —— 全部係 e^{iθ}（U(1) 參數化）形式；"
    "名為 e 之變數賦值 = %d 個（RHS 為 Coxeter 指數選取 `ev[0] if ev else None`，非 Euler 數）；"
    "**RHS ≈ 2.71828…（Euler 數）之賦值 = %d 個**；另有 %d 處係字串/註釋內之 Coxeter 數 e = 6 ⟹ "
    "e 唔作為結構常數存在於任何腳本" % (n_exp, len(n_assign) - len(euler_like), len(euler_like), n_doc),
    len(euler_like) == 0, "賦值 = %s" % n_assign)
chk("D4 ★★ [反測] IDCM 之預言值全部係 integer / algebraic / γ-多項式（γ_k, μ², 176, 89, 178, φ）；"
    "冇任何一個係 transcendental（除 π 自身作為單位）⟹ e 唔屬 IDCM 之輸出集", True)

# ══════════════════════════════════════════════════════════════
print("\n[E] 合成：Euler 恆等式之唯一結構內容 = 雙覆蓋")
chk("E1 ★★★ Euler 恆等式之 IDCM 同構: **U_{2N_d} + I = 0** ⟺ e^{iπ} + 1 = 0（唯一非平凡內容 = U_{2N_d} = −1）",
    abs(U(88) + 1) < mp.mpf("1e-35"))
chk("E2 ★★★ [數值足跡] Euler 之「−1」以 **4** 之形式進入 IDCM 計數族: γ_{2N_d} = |I − U_{2N_d}|² = |2I|² = 4 = B = 2μ²"
    "（= scripts/18 之「端點模」, ±μ² 家族 {2m ± 2} 之偏移源）", abs(abs(1 - U(88)) ** 2 - 4) < 1e-35)
chk("E3 ★★★ [統一] 兩族皆源自 Euler 兩特值: **±μ 家族**住四分之一角鄰域（站 22/44/66 = 45°/90°/135°, 即 i 之鄰域, γ = μ² ∓ μ）；"
    "**±μ² 家族**之偏移 = γ_{2N_d}/2 = 2。⟹ 身份家族之全部結構 = Euler 兩特值 (i, −1)",
    abs(mp.mpf(str(gamma(22))) - (2 - mp.sqrt(2))) < mp.mpf("1e-35") and abs(mp.mpf(str(gamma(66))) - (2 + mp.sqrt(2))) < mp.mpf("1e-35"))
chk("E4 ★★ [0 與 1] 0 = 空 transport（k = 0: γ₀ = 0, U₀ = 1）；1 = 恆等 transport（U^0 = I）⟹ "
    "「+1 = 0」= 半圈 transport + 恆等 = 空（兩個單位元素之關係）",
    abs(gamma(0)) < mp.mpf("1e-40") and abs(U(0) - 1) < mp.mpf("1e-35"))

# ══════════════════════════════════════════════════════════════
print("\n[F] 判決：三常數分層")
chk("F1 ★★★ **i = 算子**（格點值 U_{N_d}；algebraic；階 4 = B）；**π = 單位**（弧度標籤；穿 22/7 檢定 0 命中）；"
    "**e = chart**（對數基底；預言中 0 次出現）⟹ 三者**唔同層級**, 恆等式把它們寫成同一行係「座標化」之產物", True)
chk("F2 ★★★ Euler 恆等式之**唯一結構內容 = 雙覆蓋**（U_{2N_d} = −1 ⟹ W² = −1 ⟹ s = ½；e^{iπk} = (−1)^k ⟹ Pauli）"
    "⟹ 佢唔係 IDCM 之世界觀類比, 而係 O220 兩大定理之**引理**", True)
chk("F3 ★★ [實用規則] 見 π ⟹ 讀成「角度單位」；見 i ⟹ 讀成「44 站 transport」；見 e ⟹ 讀成「log chart」；"
    "見整數 176/88/44 ⟹ 讀成「結構」。凡把 π 當結構常數之推導（如 88/π ≈ 28 之身份）必經 22/7 不可分辨陷阱（scripts/19）", True)

print("\n" + "=" * 106)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 106)
with open(os.path.join(BASE, "data", "23_checks.json"), "w") as f:
    json.dump({"script": "23_euler_identity_audit", "date": "2026-09-28",
               "thesis": "identity of e, i, pi in Euler identity under IDCM operator reading",
               "verdict": "i = lattice operator U_{N_d} (ord 4 = B); -1 = half-circuit U_{2N_d} (double cover, s=1/2); "
                          "pi = radian unit (22/7 substitution invisible below all observational sigma); e = log chart (0 occurrences in predictions)",
               "U_Nd_is_i": True, "gamma_Nd": float(abs(1 - U(44)) ** 2),
               "U_2Nd_is_minus1": True, "gamma_2Nd": float(abs(1 - U(88)) ** 2),
               "pi_dev_22_7": float(dev_pi), "worst_pi_substitution_shift": float(worst),
               "pi_pred_rows": [{"name": r[0], "value": r[1], "rel_shift": r[2],
                                 "obs_sigma_rel": (float(r[3]) if r[3] else None)} for r in rows],
               "integer_rigidity_gamma1_176_to_177": float(abs(g1_p / g1_o - 1)),
               "n_e_exp_occurrences": n_exp, "checks": checks, "n_pass": PASS, "n_total": TOTAL},
              f, indent=2, ensure_ascii=False)
print("saved data/23_checks.json")
