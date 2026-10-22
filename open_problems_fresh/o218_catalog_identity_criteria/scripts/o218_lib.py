# -*- coding: utf-8 -*-
"""
O218 — 目錄身份判準 (Catalog Identity Criteria)
統一可執行判準引擎 (Unified Executable Criterion Engine)  o218_lib.py

=======================================================================
本模組 = O218 核心交付物。合成 (引用、不重驗) 以下五套已分散規則:
  O200  docs/01  三分類: 代數恆等式 / 預言殘差 / 池子匹配
  O201  docs/03,07,23  語言層判準 6 步 + 常數掃描陷阱 (24 條)
  O204  references/structural-null-test-protocol.md  結構 null test 五步協議
  O208  docs/01  密度基準三件套 (N_search / N_mc / d_obs / d_med / q_obs)
  O148/O151  陷阱窗律 (1e-5, 1e-3) + tautology 判別三步
=======================================================================

設計原則 (對應 SESSION_START 六、鐵律):
  ① 判準必須可執行 (禁「靠經驗判斷」)
  ② 池必須自動閉包 (禁手選 — O204 實錄: 手選會漏候選自身成分 15 = N_d − L₇)
  ③ 禁對截斷值做有理重建
  ④ 出唔到就誠實標 🔴
  ⑤ 零外部寫入 (本模組純函數, 唔開任何檔案)

判準輸出 = (class, gates, density, 判級 code)
"""

import re
import random
import sympy as sp

# =====================================================================
# 第一節 — 原子註冊表 (Atom Registry)
# =====================================================================
# 每個原子 = (value, 名稱元組, 框架標籤, 出處)
# 框架標籤: "IDCM" = IDCM 結構數 (可作目錄身份)
#           "EXTERNAL" = 外部框架數 (SM/MSSM/QCD content、觀測擬合值) — 不可作目錄身份
#
# ⚠️ 出處綁定: 每個原子必須有 IDCM 已閉合 O 嘅出處; 冇出處 = 非法葉 (G1 FAIL)

ATOM_TABLE = [
    # --- K_chain 譜層 ---
    (2,   ("mu2", "gamma_22"),        "IDCM", "O159: μ² = E−O = γ⁽⁸⁸⁾₄₄/2 = γ⁽⁸⁸⁾₂₂ = 2 (88-L); 176-L γ⁽¹⁷⁶⁾₄₄ = 2; 三鏈統一 γ⁽ᴺ⁾_{N/4}"),
    (4,   ("B", "L_3", "gamma_max"),  "IDCM", "B = L₃ = φ³−φ⁻³ = 2μ² ⟸ Binet ψ=−1/φ (★O229 ① 筆誤更正 2026-10-03); γ⁽⁸⁸⁾₄₄ = 4 (88-L, 端點模)"),
    (44,  ("N_d", "Sigma_gamma_odd"), "IDCM", "O95: N_d = 44; O169 B1: Σγ⁽⁸⁸⁾_odd = N_d EXACT (88-L)"),
    (46,  ("Sigma_gamma_even",),      "IDCM", "O169 B1: Σγ⁽⁸⁸⁾_even = 46 = N_d + μ² (88-L)"),
    (88,  ("N_site", "two_N_d"),      "IDCM", "O159/O175: 88-site = 2N_d"),
    (90,  ("Sigma_gamma",),           "IDCM", "O211: Σγ⁽⁸⁸⁾ = B(N_d+1)/2 = 90 EXACT (88-L); 176-L Σγ⁽¹⁷⁶⁾ = 178 = 2F₁₁ (O220 戊)"),
    (176, ("N_laplacian", "two_N"),   "IDCM", "O159: 176-Laplacian half-set k=1..88"),
    (18,  ("L_6",),                   "IDCM", "Lucas 階梯 L₆ = 18"),
    # --- Lucas / Fibonacci / 階梯 ---
    (3,   ("N_gen",),                 "IDCM", "O211: N_gen = 3 = B−1"),
    (5,   ("F_5",),                   "IDCM", "Fibonacci F₅ = 5"),
    (7,   ("L_4", "TrT4"),            "IDCM", "O124: L₄ = 7 = Tr(T̂⁴) = b₀; Lucas"),
    (8,   ("F_6",),                   "IDCM", "F₆ = 8 = N_c²−1 (color)"),
    (11,  ("L_5",),                   "IDCM", "O145: L₅ = 11 = rank(SU(12))"),
    (13,  ("F_7",),                   "IDCM", "F₇ = 13 = b₁/2"),
    (21,  ("F_8",),                   "IDCM", "F₈ = 21 = K(0)"),
    (26,  ("b_1",),                   "IDCM", "O124: b₁ = 2F₇ = 26"),
    (29,  ("L_7",),                   "IDCM", "O171: L₇ = a+b = 29"),
    (33,  ("K_tree", "M_depth"),      "IDCM", "O83: K_tree = 33 = 3·11 = N_gen·L₅"),
    (34,  ("F_9",),                   "IDCM", "F₉ = 34"),
    (47,  ("L_8",),                   "IDCM", "Lucas L₈ = 47"),
    (55,  ("F_10",),                  "IDCM", "O156: F₁₀ = 55 = θ₂₃ sector"),
    (76,  ("L_9",),                   "IDCM", "Lucas L₉ = 76"),
    (89,  ("F_11",),                  "IDCM", "F₁₁ = 89 = K(0)+N_gen·Δα⁻¹"),
    (123, ("L_10", "E_J"),            "IDCM", "O124/O81: L₁₀ = Tr(T̂¹⁰) = E_J = Σγ⁽⁸⁸⁾+K_tree = 123"),
    (144, ("F_12",),                  "IDCM", "F₁₂ = 144"),
    # --- CY₃ / 幾何 ---
    (36,  ("h11",),                   "IDCM", "O211: h¹¹ = N_d − 2B = 36 (零輸入導出)"),
    (98,  ("h21",),                   "IDCM", "O211: h²¹ = Σγ⁽⁸⁸⁾ + 2B = 98"),
    (134, ("CY3_chi_abs", "TrG"),     "IDCM", "O211: h¹¹+h²¹ = Tr G = N_d+Σγ⁽⁸⁸⁾ = 134"),
    (137, ("alpha_inv_0",),           "IDCM", "O124: α⁻¹(0) = C(B²,2)+B²+1 = 137"),
    (946, ("C_Nd_2",),                "IDCM", "O213: 946 = C(N_d,2) EXACT"),
    (990, ("C_Nd1_2",),               "IDCM", "O126: 990 = C(N_d+1,2)"),
    # --- 預算 / 份額 ---
    (60,  ("N_budget", "kappa_inv_plus_Nd"), "IDCM", "O215: 60 = Σγ⁽⁸⁸⁾_odd + γ⁽⁸⁸⁾_max² = N_d + B² (88-L)"),
    (41,  ("Omega_Lambda_num",),      "IDCM", "O215: Ω_Λ = 41/60"),
    (19,  ("Omega_m_num",),           "IDCM", "O215: Ω_m = 19/60"),
    (16,  ("Omega_dm_num",),          "IDCM", "O214: Ω_dm = 16/60"),
    (28,  ("E_proj_num",),            "IDCM", "O215: Ω_m = 28.5/90 ⟹ 分子 28.5"),
]

# 譜層實數原子 (非整數): 只可作表達式因子, 唔可作整數掃描原子
REAL_ATOM_TABLE = [
    ("phi",       sp.GoldenRatio,        "IDCM", "T̂ 譜 {φ, −1/φ} (O213 docs/02)"),
    ("sqrt5",     sp.sqrt(5),            "IDCM", "Q(√5) 數域元素"),
    ("c_ln2",     sp.log(2),             "IDCM", "Landauer 常數 (O151 docs/03)"),
    ("c_pi",      sp.pi,                 "IDCM", "相位模 (O201 §0c)"),
    ("b_spec",    sp.Float("1.119113982034844", 30), "IDCM",
     "O213 R3: b_spec = 1/⟨v_g⟩_{1..22}, 閉式 22sin(π/176)/(sin(π/8)cos(23π/176))"),
]

# 外部框架常數 (EXTERNAL): 可作「目標」, 唔可作 IDCM 目錄身份之葉
EXTERNAL_TABLE = [
    ("b1_SM",      sp.Rational(41, 10),  "EXTERNAL", "SM GUT-norm b₁ = (4/3)ΣY²_f+(1/3)ΣY²_h = 41/10 (O151 docs/12)"),
    ("b1_MSSM",    sp.Rational(33, 5),   "EXTERNAL", "MSSM GUT-norm b₁ = 33/5 (O151 docs/12)"),
    ("mdot_2pct",  sp.Rational(1, 50),   "EXTERNAL", "TDE 觀測臨界率 0.02 (O199 docs/02)"),
    ("one_third",  sp.Rational(1, 3),    "EXTERNAL", "SM 超荷歸一化 (4/3) 家族"),
]

# =====================================================================
# 第二節 — 池自動閉包 (O204 protocol 步驟 1)
# =====================================================================

CLOSURE_CAP = 400          # O204 protocol: 上限 400
CLOSURE_OPS = ("+", "-")   # O204 protocol: 只閉合於 |a−b| 與 a+b


def base_atoms():
    """回傳 base 集 (整數原子值) + provenance。禁手選 — 由 ATOM_TABLE 直接生成。"""
    out = {}
    for v, names, fw, src in ATOM_TABLE:
        out.setdefault(v, {"names": set(), "framework": fw, "source": set()})
        out[v]["names"] |= set(names)
        out[v]["source"].add(src)
    return out


def closure_pool(cap=CLOSURE_CAP, atoms=None):
    """
    P = 自動閉包 (禁手選)。
      P = base ∪ {|a−b| ≤ cap} ∪ {a+b ≤ cap}
    O204 實錄: 手選池會漏候選自身成分 (漏 15 = N_d−L₇) ⟹ 結論全錯。
    """
    if atoms is None:
        atoms = base_atoms()
    base = set(atoms.keys())
    P = set(base)
    frontier = sorted(base)
    changed = True
    while changed:
        changed = False
        cur = sorted(P)
        for a in cur:
            for b in cur:
                d = abs(a - b)
                s = a + b
                if 1 <= d <= cap and d not in P:
                    P.add(d); changed = True
                if 1 <= s <= cap and s not in P:
                    P.add(s); changed = True
        if len(frontier) == len(P):
            break
    return P


def representations(n, pool):
    """n 在池內之 a+b 無序表示 (a,b ∈ pool, a ≤ b)。"""
    reps = []
    for a in sorted(pool):
        b = n - a
        if b in pool and a <= b:
            reps.append((a, b))
    return reps


# =====================================================================
# 第三節 — 葉審計 (G1 語法合法 / G2 出處)
# =====================================================================

LEAF_STATUS = {
    "REGISTERED":      "已註冊原子 (有 O 出處)",
    "DEPTH1":          "深度 1 衍生 (∃ a+b : a,b ∈ 已註冊原子)",
    "CLOSURE_TRIVIAL": "閉包可達 (已證退化 — 對 [1,cap] 零信息)",
    "BARELITERAL":     "裸整數 (唔在閉包內) — 非法葉",
    "FITTED":          "擬合常數 (非註冊實數) — 非法葉",
    "EXTERNAL":        "外部框架常數 (SM/MSSM/觀測擬合值)",
    "REAL":            "已註冊譜層實數 (φ, √5, π, ln2)",
}


def registered_values():
    """回傳已註冊整數原子之值集合。"""
    return {v for v, _, _, _ in ATOM_TABLE}


def closure_degeneracy(pool, cap=CLOSURE_CAP):
    """
    ★ 閉包退化檢定 (本 O 新結果):
    base 含 3 與 4 (gcd = 1) ⟹ |3−4| = 1 ∈ P ⟹ P ⊇ [1, cap]。
    一旦閉包包含 1, {+,−} 閉包就係完整整數區間 ⟹「n ∈ P」對 n ≤ cap 恆真
    ⟹ 閉包可達性**零信息** (O201 §4「結構整數集係下界」/ §19「整數目標 null = 1.000」之形式化)。
    回傳 dict: 區間覆蓋率 / 是否退化 / 最小正元素。
    """
    pos = sorted(x for x in pool if 1 <= x <= cap)
    covered = set(pos)
    frac = len(covered & set(range(1, cap + 1))) / cap
    return {
        "cap": cap,
        "min_positive": min(pos) if pos else None,
        "interval_coverage": frac,
        "degenerate": frac == 1.0,
        "n_le_cap": len(covered),
    }


def depth1_reps(n, reg_vals=None):
    """
    深度 1 表示: n = a + b, a,b ∈ 已註冊原子集 (a ≤ b)。
    ★ 只有深度 1 (用已註冊原子) 之表示數才有目錄意義 —
    閉包池內嘅表示數係目錄大小函數, 唔係 n 嘅性質 (本 O 新結果)。
    """
    if reg_vals is None:
        reg_vals = registered_values()
    return [(a, n - a) for a in sorted(reg_vals) if (n - a) in reg_vals and a <= n - a]


def registered_names():
    """回傳 名稱 → (value, framework, source) 之註冊映射。"""
    reg = {}
    for v, names, fw, src in ATOM_TABLE:
        for nm in names:
            reg[nm] = (sp.Integer(v), fw, src)
    for nm, val, fw, src in REAL_ATOM_TABLE:
        reg[nm] = (val, fw, src)
    for nm, val, fw, src in EXTERNAL_TABLE:
        reg[nm] = (val, fw, src)
    return reg


def subs_registered(expr):
    """把已註冊名稱代入其數值, 令表達式可數值求值。"""
    reg = registered_names()
    sub = {}
    for nm, (val, _fw, _src) in reg.items():
        sub[sp.Symbol(nm)] = val
    return sp.sympify(expr).subs(sub)


def symbol_names(expr):
    """表達式內嘅符號名集合。"""
    return {s.name for s in sp.sympify(expr).free_symbols}


def audit_symbol_names(expr, allow_symbols=()):
    """
    G2 出處審計 (名稱層): 每個符號名必須已註冊 (有 O 出處),
    或喺 claim 明示之 scaffolding 符號 (e.g. T1 共有量自由符號)。
    回傳 (unknown_names, allowed_used)
    """
    reg = registered_names()
    allow = set(allow_symbols)
    names = symbol_names(expr)
    unknown = sorted(n for n in names if n not in reg and n not in allow)
    return unknown, sorted(n for n in names if n in allow)


def audit_leaves(names, pool):
    """
    葉審計。輸入 = 表達式用嘅符號名集合。
    回傳 = {name: status}, 並標出非法葉。
    """
    reg = registered_names()
    out = {}
    for nm in sorted(names):
        if nm in reg:
            val, fw, src = reg[nm]
            out[nm] = ("EXTERNAL" if fw == "EXTERNAL"
                       else ("REAL" if not val.is_Integer else "REGISTERED"))
        else:
            out[nm] = "UNKNOWN"
    return out


def audit_numeric_literals(expr, pool=None, reg_vals=None):
    """
    掃表達式內嘅數值字面值。
      - 已註冊整數原子            → REGISTERED
      - 深度 1 (∃ a+b 由註冊原子) → DEPTH1 (合法衍生葉, 需報表示數)
      - ∈ 自動閉包 P 但非深度 1   → CLOSURE_TRIVIAL (合法但零信息 — 見 closure_degeneracy)
      - ∉ P                       → BARELITERAL (非法)
      - 非整數有理/浮點 (未註冊)   → FITTED (非法)
    """
    if reg_vals is None:
        reg_vals = registered_values()
    if pool is None:
        pool = closure_pool()
    real_vals = {sp.nsimplify(v) for _, v, _, _ in REAL_ATOM_TABLE}

    def _legit_int(v):
        """0/1 (單位元) 或已註冊 或 深度 1 可達 ⟹ 合法 (符號唔帶結構信息)。"""
        w = abs(int(v))
        return w in (0, 1) or w in reg_vals or bool(depth1_reps(w, reg_vals))

    findings = []
    for node in sp.preorder_traversal(expr):
        if node.is_Integer:
            v = int(node)
            w = abs(v)            # 符號唔帶結構信息 (冪次 −1 / 負號)
            if w in (0, 1):
                findings.append((v, "UNIT"))       # 算術單位元 (零信息, 一律合法)
            elif w in reg_vals:
                findings.append((v, "REGISTERED"))
            elif depth1_reps(w, reg_vals):
                findings.append((v, "DEPTH1"))
            elif w in pool:
                findings.append((v, "CLOSURE_TRIVIAL"))
            else:
                findings.append((v, "BARELITERAL"))
        elif node.is_Rational:
            # 有理字面值: 分子分母逐個審 (整數字面值會自動化為 Rational)
            p_, q_ = int(node.p), int(node.q)
            if _legit_int(p_) and _legit_int(q_):
                findings.append((node, "RATIO"))
            else:
                findings.append((node, "FITTED"))
        elif node.is_Float:
            findings.append((node, "FITTED"))
        elif node.is_Number and node not in real_vals:
            findings.append((node, "EXOTIC"))
    return findings


# =====================================================================
# 第四節 — 結構內容三測 (T1 重言式 / T2 跨框架巧合 / T3 自由乘數)
# =====================================================================

def t1_tautology(lhs, rhs, shared_symbol):
    """
    T1 重言式 (O151 docs/12 判別三步):
    「共有量」若係外部固有數 (唔係 IDCM 推導), 而等式對佢**恆等** ⟹ 重言式。
    測試: 把共有量換成自由符號, **其餘**已註冊名代入數值, 再檢查 sympy 化簡 = 0
    (若等式對共有量任何值都成立 ⟹ 該「推導」冇用過佢嘅任何結構內容 ⟹ 重言式)。
    """
    sv = shared_symbol if isinstance(shared_symbol, sp.Symbol) \
        else sp.Symbol(str(shared_symbol))
    reg = registered_names()
    sub = {sp.Symbol(nm): val for nm, (val, _f, _s) in reg.items() if sp.Symbol(nm) != sv}
    s = sp.Symbol("_s_free", positive=True)
    try:
        Ls = sp.sympify(lhs).subs(sub).subs({sv: s})
        Rs = sp.sympify(rhs).subs(sub).subs({sv: s})
        d = sp.simplify(Ls - Rs)
    except Exception:
        return False, None
    return (d == 0), d


def t2_cross_framework_coincidence(lhs_names, rhs_names, mechanism=None,
                                   target_kind="pool_match"):
    """
    T2 跨框架巧合:
      dev = 0 (精確) 但兩邊**無共同推導來源**, 且一邊係**另一個理論嘅導出常數**
      (SM/MSSM content、ΛCDM 擬合值) ⟹ 數值巧合, 唔係目錄身份
      (O151 b₁×30=123; MSSM 33 = N_gen×L₅)。
    ⚠️ 不適用於 prediction / prediction_residual —
      「IDCM 預言 對 觀測」係合法檢定 (O208 例外 4), 唔屬巧合判;
      該類由 G0(σ 預算) / G4(陷阱窗) / T5(兩級) / G5(Farey 密度) 處理。
    """
    if mechanism:
        return False, "有機制證據"
    if target_kind in ("prediction", "prediction_residual"):
        return False, "預言/觀測對比類 (O208 例外 4) — 唔屬跨框架巧合判"
    reg = registered_names()
    lf = {reg[n][1] for n in lhs_names if n in reg}
    rf = {reg[n][1] for n in rhs_names if n in reg}
    has_ext = ("EXTERNAL" in lf) or ("EXTERNAL" in rf)
    if not has_ext:
        return False, "兩邊皆 IDCM (無外部框架成分)"
    if lf & rf:
        return False, "兩邊共享框架"
    return True, "跨框架 (IDCM ↔ EXTERNAL) 且無共同推導來源"


def t3_free_multiplier(target, base_reach_max, base_reach_min, expr):
    """
    T3 自由乘數 / 可達性 (density ref §8):
    目標值超出「base 原子自身可達範圍」⟹ 係自由乘數供給該值, 基礎比值只係裝飾。
    """
    tv = float(target)
    if tv > float(base_reach_max) * 1.0000001 or tv < float(base_reach_min) * 0.9999999:
        return True, f"目標 {tv:.6g} 超出 base 可達範圍 [{float(base_reach_min):.4g}, {float(base_reach_max):.4g}]"
    return False, "目標在 base 可達範圍內"


# =====================================================================
# 第五節 — 非唯一表示裁決 (U 測)
# =====================================================================

def nonuniqueness(n, pool):
    """
    目錄表示非唯一性。輸入整數 n → 回傳 (R_unordered, reps)。
    R ≥ 2 ⟹ 目錄表示非唯一 ⟹ 「n 屬 IDCM 目錄」唔構成獨立證據 (O137 docs/36 §8.5)。
    """
    reps = representations(n, pool)
    return len(reps), reps


# =====================================================================
# 第六節 — 陷阱窗 (G4) 與數域 (G6)
# =====================================================================

TRAP_LO, TRAP_HI = 1e-5, 1e-3     # O148/O151 陷阱窗


def trap_window(dev, target_precision=None):
    """
    陷阱窗律 (O148/O151) + O201 §2 前置條件:
    只在「目標精度優於窗寬」時才綁定。
    回傳 (in_trap, reason)
    """
    if target_precision is not None and target_precision >= (TRAP_HI - TRAP_LO):
        return False, (f"目標精度 {target_precision:.3g} ≳ 窗寬 ⟹ 窗律 n/a (O201 §2)")
    inwin = (TRAP_LO < abs(dev) < TRAP_HI)
    return inwin, ("dev 落陷阱窗 (1e-5,1e-3) ⟹ φ 陷阱/巧合" if inwin
                   else f"dev = {abs(dev):.3g} 喺窗外")


def field_separation(m1, m2):
    """
    G6 數域分離: Q(ζ_m1) ∩ Q(ζ_m2) = Q(ζ_gcd(m1,m2))。
    gcd = 1 ⟹ 交集 = Q ⟹ 兩個代數數「結構上唔可能」係同一個 (O201 §11)。
    """
    from math import gcd
    g = gcd(m1, m2)
    return (g == 1), g


# =====================================================================
# 第六節補 — 精確證書 (Exact Certificate) 與 K_chain 譜工具
# =====================================================================

def certify_exact_symbolic(lhs, rhs):
    """
    符號恆等式證書: 先代入已註冊名之數值, 再 sympy 化簡 (lhs − rhs)。
    ⚠️ 必須用 trigsimp — 純 simplify 對 4sin²(πn/88)+4sin²(π(44−n)/88) 唔會歸零。
    """
    try:
        d = subs_registered(lhs) - subs_registered(rhs)
        for f in (sp.expand_trig, sp.trigsimp, sp.simplify, sp.expand_trig, sp.trigsimp):
            d = f(d)
        return (d == 0), d
    except Exception:
        return False, None


def certify_exact_numeric(lhs_val, rhs_val, dps=60, tol=1e-45):
    """數值精確證書: mpmath dps 位下 |lhs − rhs| < tol。"""
    import mpmath as mp
    with mp.workdps(dps):
        a, b = mp.mpf(lhs_val), mp.mpf(rhs_val)
        d = abs(a - b)
        return bool(d < tol), d


def gamma_n(n, dps=60):
    """γ_n = 4sin²(πn/88) — K_chain 譜 (O124/O130 慣例)。"""
    import mpmath as mp
    with mp.workdps(dps):
        return 4 * mp.sin(mp.pi * n / 88) ** 2


def sum_gamma(lo=1, hi=44, dps=60):
    """Σ_{n=lo}^{hi} γ_n (精確 mpmath)。"""
    import mpmath as mp
    with mp.workdps(dps):
        return mp.fsum([gamma_n(n, dps) for n in range(lo, hi + 1)])


def sum_gamma_odd(n_max=43, dps=60):
    """
    Σ_{奇 n ≤ n_max} γ_n — O169 B1: = N_d = 44 EXACT (n_max = 43 時 22 項)。
    ★ 別名: == sum_gamma(n_max-1, n_max) 純屬巧合 (γ_n + γ_{44−n} = B), 唔可混用。
    """
    import mpmath as mp
    with mp.workdps(dps):
        return mp.fsum([gamma_n(n, dps) for n in range(1, n_max + 1, 2)])


def sum_gamma_even(n_max=44, dps=60):
    """Σ_{偶 n ≤ n_max} γ_n — = 46 = N_d + μ² EXACT (n_max = 44 時 22 項)。"""
    import mpmath as mp
    with mp.workdps(dps):
        return mp.fsum([gamma_n(n, dps) for n in range(2, n_max + 1, 2)])


# =====================================================================
# 第六節之二 — ★ γ 歸一化分離 (本 O 新結果: 同一符號兩個鏈)
# =====================================================================
#
# 全庫 γ 有 **兩個並存歸一化**, 同一字面恆等式在兩鏈真假相反:
#   88  鏈: γ⁽⁸⁸⁾_n = 4sin²(πn/88),  n = 1..44   (O169 docs/02, O211 docs/01)
#           Σγ = 90 = B(N_d+1)/2;  Σγ_odd = 44 = N_d;  Σγ_even = 46
#           γ⁽⁸⁸⁾_22 = 2 = μ²;  γ⁽⁸⁸⁾_44 = 4 = B
#           配對 (n, 44−n):  γ_n + γ_{44−n} = 4 = B  ∀n (含端點 γ_0 := 0)
#   176 鏈: γ⁽¹⁷⁶⁾_k = 4sin²(πk/176), k = 1..88  (O124 scripts/13 A1-A3)
#           γ⁽¹⁷⁶⁾_44 = 2 = μ²
#           配對 (44−j, 44+j): γ_{44−j} + γ_{44+j} = 4 = B  ∀j (含 j=0)
#           ⚠️ 錯配對 (n, 44−n) 下 **≠** 4 (最近 dev ≈ 2.07) — O124 A3 負結果
#
# 關係: γ⁽⁸⁸⁾_n = γ⁽¹⁷⁶⁾_{2n} (88 鏈 = 176 鏈之偶模子集)
#
# ⟹ O163 docs/07 之無標籤寫法「B = 4 = γ_n + γ_{44−n}」:
#     喺 88 鏈 **真** (本檔可執行驗證 ✓), 喺 176 鏈 **假** (O124 A3 ✓)。
#     O124 A3 之負結果係 **鏈條件性** 嘅, 唔係絕對 no-go。
# ⟹ 判準鐵律: **譜符號必須帶鏈標籤** (γ⁽⁸⁸⁾ / γ⁽¹⁷⁶⁾), 否則同一字串真假相反。

GAMMA_CHAIN = {
    "44": {
        "N": 44, "half": 22,
        "form": "4*sin(pi*n/44)**2",
        "range": (1, 22),
        "source": "O220 docs/25 §5 (44-L); 本 O 補入 (2026-10-03)",
        "sum": 46, "odd": 22, "even": 24,
        "pairing": "(n, 22-n)", "pair_half": 22, "pair_sum": 4,
        "g_11": 2, "g_22": 4,
        "mod8": False,          # 44 = 4·11 ⟹ 無 45°/135° 整數站 ⟹ ±μ 家族不可用
    },
    "88": {
        "N": 88, "half": 44,
        "form": "4*sin(pi*n/88)**2",
        "range": (1, 44),
        "source": "o169 docs/02 §B1; o211 docs/01 C7",
        "sum": 90, "odd": 44, "even": 46,
        "pairing": "(n, 44-n)", "pair_half": 44, "pair_sum": 4,
        "g_22": 2, "g_44": 4,
        "mod8": True,           # 88 = 8·11 ⟹ 45°/135° 立於 k = 11/33 ✓
    },
    "176": {
        "N": 176, "half": 88,
        "form": "4*sin(pi*k/176)**2",
        "range": (1, 88),
        "source": "o124 scripts/13 (A1-A3); o163 docs/07 源頭標籤",
        "sum": 178, "even_sum": 90, "odd_sum": 88,
        "pairing": "(44-j, 44+j)", "pair_half": 44, "pair_sum": 4,
        "g_44": 2, "g_88": 4,
        "mod8": True,           # 176 = 16·11 ✓
    },
}


def gamma_chain(n, chain="88", dps=60):
    """γ 譜值 (必須指明鏈: "44" | "88" | "176")。無標籤 = ValueError (禁)。"""
    if chain not in GAMMA_CHAIN:
        raise ValueError(f"未知鏈 {chain!r} — 必須係 '44' | '88' | '176'")
    import mpmath as mp
    with mp.workdps(dps):
        return 4 * mp.sin(mp.pi * n / GAMMA_CHAIN[chain]["N"]) ** 2


def chain_pairing_check(chain="88", dps=60):
    """
    §自動判定一條鏈之配對恆等式 (唔靠人手寫死):
      "88"  → max_n |γ_n + γ_{44−n} − 4|          (n = 1..44, γ_0 := 0)
      "176" → max_j |γ_{44−j} + γ_{44+j} − 4|     (j = 0..43)
    回傳 dict: {chain, tested, max_dev, is_identity}
    """
    info = GAMMA_CHAIN[chain]
    h = info["pair_half"]
    devs = []
    if chain in ("44", "88"):
        for n in range(1, h + 1):
            a = gamma_chain(n, chain, dps)
            b = 0 if n == h else gamma_chain(h - n, chain, dps)
            devs.append(abs(float(a + b - 4)))
    else:
        for j in range(0, h):
            a = gamma_chain(h - j, "176", dps)
            b = gamma_chain(h + j, "176", dps)
            devs.append(abs(float(a + b - 4)))
    mx = max(devs) if devs else None
    return {"chain": chain, "pairing": info["pairing"], "tested": len(devs),
            "max_dev": mx, "is_identity": (mx is not None and mx < 1e-30)}


def wrong_pairing_check(chain="176", dps=60):
    """對比: 用另一條鏈之配對規則測試本鏈 — 應為負結果 (O124 A3)。"""
    devs = []
    for n in range(1, 44):
        a = gamma_chain(n, chain, dps)
        b = gamma_chain(44 - n, chain, dps)
        devs.append(abs(float(a + b - 4)))
    mx = min(devs) if devs else None     # 最近接之偏差 (證明「冇任何 n」)
    return {"chain": chain, "pairing": "(n, 44-n) 錯配對",
            "min_dev": mx, "no_solution": (mx is not None and mx > 1e-6)}


# =====================================================================
# 第七節 — 密度基準 (O208 三件套)
# =====================================================================

def build_candidate_space(pool, cap_val=1000, products=True, quotients=True):
    """
    由池自動生成候選值空間 (禁手選)。回傳 (values_set, 構成報告)。
    """
    vals = set(pool)
    comp = {"atoms": len(pool)}
    n_add = 0
    for a in pool:
        for b in pool:
            if 1 <= abs(a - b) <= cap_val:
                vals.add(abs(a - b)); n_add += 1
            if a + b <= cap_val:
                vals.add(a + b); n_add += 1
    comp["pairwise_sum_diff"] = n_add
    n_prod = 0
    if products:
        for a in pool:
            for b in pool:
                if 1 <= a * b <= cap_val:
                    vals.add(a * b); n_prod += 1
    comp["pairwise_product"] = n_prod
    n_quot = 0
    if quotients:
        for a in pool:
            for b in pool:
                if b != 0 and a <= cap_val * b:
                    vals.add(sp.Rational(a, b)); n_quot += 1
    comp["pairwise_quotient"] = n_quot
    return vals, comp


def density_baseline(target, candidates, n_mc=100000, seed=20260928,
                     local_window=0.10, d_obs=None):
    """
    O208 密度基準三件套。
      N_search = |candidates|
      d_med    = 隨機目標 (局部窗 ±local_window) 之最佳匹配偏差中位數
      q_obs    = P(隨機目標最佳偏差 ≤ d_obs)
    回傳 dict (含 N_mc / seed 以便重現)。
    ★ 實現: 候選預排序 + bisect ⟹ 每樣本 O(log N), 唔用 O(N) 掃描。
    """
    import bisect
    import statistics
    t = float(target)
    if t <= 0:
        return {"error": "target ≤ 0"}
    cands = sorted(float(c) for c in candidates if float(c) > 0)
    if not cands:
        return {"error": "no positive candidates"}
    lo, hi = t * (1 - local_window), t * (1 + local_window)
    rng = random.Random(seed)

    def best_dev(x):
        i = bisect.bisect_left(cands, x)
        best = float("inf")
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(cands):
                best = min(best, abs(cands[j] / x - 1.0))
        return best

    devs = [best_dev(rng.uniform(lo, hi)) for _ in range(n_mc)]
    d_med = statistics.median(devs)
    out = {
        "N_search": len(cands),
        "N_mc": n_mc,
        "seed": seed,
        "local_window": local_window,
        "d_med": d_med,
        "d_med_mean": statistics.fmean(devs),
        "d_med_p01": _pct(devs, 0.01),
        "d_med_p05": _pct(devs, 0.05),
    }
    if d_obs is not None:
        q = sum(1 for d in devs if d <= d_obs) / len(devs)
        out["d_obs"] = d_obs
        out["q_obs"] = q
        out["grade"] = ("🟢" if q <= 0.01 else ("🟡" if q <= 0.05 else "🔴"))
    return out


def _pct(xs, p):
    xs = sorted(xs)
    k = max(0, min(len(xs) - 1, int(round(p * (len(xs) - 1)))))
    return xs[k]


def farey_density(target, tol_rel, q_max):
    """
    ★ Farey 密度論證 — 「符號庫爆炸」之形式化 (本 O 新結果)。

    由結構池 {a} (a ≤ A) 可造之有理表達式, 其值域 ⊆ {p/q : q ≤ q_max}。
    分母 ≤ q_max 之有理數喺長度 L 之區間內之數目 ≈ L·(3/π²)·q_max²。
    窗寬 L = 2·tol_rel·T  ⟹  N_search ≈ (3/π²)·q_max²·2·tol_rel·T。

    N_search ≫ 1 ⟹ 任何目標值都可由低分母表達式「命中」⟹ 零判別力
    (O136 符號庫爆炸之定量根源; O201 §19 整數目標 null = 1.000 之推廣)。

    形式與 q_max:
      單因子  a               → q_max = A
      商      a/b             → q_max = A
      乘積     a·b            → q_max = A²
      商積    (a/b)·(c/d)     → q_max = A²
      和差     a/b ± c/d      → q_max = A²
    """
    L_win = 2.0 * tol_rel * abs(float(target))
    n_est = L_win * (3.0 / (3.141592653589793 ** 2)) * (q_max ** 2)
    return {
        "N_search_farey": n_est,
        "window_width": L_win,
        "q_max": q_max,
        "note": f"Farey: N ≈ (3/π²)·q_max²·2·tol·T = {n_est:.4g}",
        "discriminating": (n_est < 1.0),
    }


def q_max_for_form(form, A):
    """由形式名 + 池上限 A 得 q_max (見 farey_density 文檔)。"""
    if form in ("single", "quotient"):
        return A
    if form in ("product", "quotient_product", "sum_quotients"):
        return A * A
    raise ValueError(f"未知形式: {form}")


# =====================================================================
# 第八節 — 統一判準 (Unified Criterion)
# =====================================================================

CLAIM_CLASSES = ("identity", "prediction_residual", "pool_match")

# 判級 code
V = {
    "FALSE":       ("🔴", "等式不成立 (dev 超容差) — G0"),
    "ILLEGAL":     ("🔴", "非法葉 (裸數/未註冊) — G1/G2 FAIL"),
    "FITTED":      ("🔴", "含擬合常數 — G3 FAIL"),
    "TAUTOLOGY":   ("🔴", "重言式 — T1 (等式對共有量恆等)"),
    "COINCIDENCE": ("🔴", "跨框架數值巧合 — T2 (無共同推導來源)"),
    "MULTIPLIER":  ("🔴", "自由乘數供值 — T3 (目標不可達)"),
    "NONUNIQUE":   ("🔴", "目錄表示非唯一 — U (R ≥ 2)"),
    "TRAP":        ("🔴", "落陷阱窗 (1e-5,1e-3) — G4"),
    "DENSITY":     ("🔴", "密度效應 (q_obs > 5%) — G5"),
    "FIELD":       ("🔴", "數域分離 — G6"),
    "WEAK_DENSITY":("🟡", "密度邊緣 (1% < q_obs ≤ 5%) — G5"),
    "FORMAL_OK":   ("🟡", "形式合格, 缺機制證據 — 需 null<1e-4 或推導"),
    "IDENTITY_OK": ("🟢", "代數恆等式 (N_search = 1, 唔受密度檢定) — O200 ①"),
    "MATCH_OK":    ("🟢", "池子匹配超越密度 (q_obs ≤ 1%, R = 1, 無 T 標記)"),
}


def criterion(name, lhs, rhs, target_kind, pool,
              lhs_names=(), rhs_names=(),
              shared_symbol=None, shared_concrete=None,
              mechanism=None, target_precision=None, tol_rel=1e-9,
              d_obs=None, density=None, nonunique_target=None,
              field_pair=None, external_reach=None, exact_cert=None,
              leading_dev=None, allow_symbols=()):
    """
    統一可執行判準 — 輸入 (候選表達式, 目標, 容差) → 輸出 (class, gates, 判級)。

    參數
      lhs, rhs            : sympy 可解析字串 (用註冊原子名; 唔可以有裸數自由值)
      target_kind         : identity | prediction_residual | pool_match (O200 三分類)
      shared_symbol       : T1 用 — 兩邊共有之「外部固有量」符號名
      exact_cert          : identity 類必需 — ("symbolic", diff) 或 ("numeric", diff)
      target_precision    : 目標自身精度 (相對); 用於 O201 §2 窗律前置條件
      d_obs               : 觀測/匹配偏差 (相對); 有值就報 q_obs
      density             : 由 density_baseline() 得嘅 dict
      nonunique_target    : 目錄身份類 — 該整數之表示數 R
      field_pair          : (m1, m2) 數域 pair (G6)
      external_reach      : (min, max) base 可達範圍 (T3)

    回傳 dict: {name, class, gates:{...}, density:{...}, verdict, 判級}
    """
    gates = {}
    notes = []
    L, R = sp.sympify(lhs), sp.sympify(rhs)
    if not lhs_names:
        lhs_names = tuple(symbol_names(L))
    if not rhs_names:
        rhs_names = tuple(symbol_names(R))

    # --- 第 1 步 葉審計 (G1/G2) ---
    unk_l, _ = audit_symbol_names(L, allow_symbols)
    unk_r, _ = audit_symbol_names(R, allow_symbols)
    unknown = sorted(set(unk_l) | set(unk_r))
    lits = audit_numeric_literals(L, pool) + audit_numeric_literals(R, pool)
    # CLOSURE_TRIVIAL 亦屬非法葉: 由閉包退化定理 (docs/03 §二), 落喺 [1,cap] 之
    # 任意整數都 ∈ P ⟹ 「∈ P」零信息 ⟹ 該葉無結構身份 (O201 ①: 葉必須有結構來源)。
    bad = [x for x in lits if x[1] in ("BARELITERAL", "EXOTIC", "CLOSURE_TRIVIAL")]
    derived = sorted({x[0] for x in lits if x[1] == "DEPTH1"})
    trivial = sorted({x[0] for x in lits if x[1] == "CLOSURE_TRIVIAL"})
    gates["G1_G2_leaf_audit"] = ("PASS" if (not bad and not unknown) else "FAIL")
    if bad:
        notes.append(f"非法葉 (數值): {bad[:6]}")
    if any(x[1] == "CLOSURE_TRIVIAL" for x in bad):
        notes.append("⚠️ 閉包退化葉: 由閉包退化定理任意整數 n ≤ cap 都合格 ⟹ 零信息")
    if unknown:
        notes.append(f"未註冊符號 (無出處): {unknown}")
    if derived:
        notes.append(f"深度 1 衍生葉 (需報表示數): {derived}")
    if trivial:
        notes.append(f"⚠️ 閉包退化葉 (零信息): {trivial}")

    # --- 第 2 步 自由參數 (G3) ---
    fitted = [x for x in lits if x[1] == "FITTED"]
    gates["G3_zero_free_param"] = ("PASS" if not fitted else "FAIL")
    if fitted:
        notes.append(f"擬合常數: {sorted({str(x[0]) for x in fitted})}")

    # --- 精確證書 (先算, G0/G5 都要用) ---
    cert_ok, cert_kind = False, None
    if exact_cert is not None:
        cert_kind = exact_cert[0] if isinstance(exact_cert, (tuple, list)) else None
        try:
            cert_ok = (exact_cert[1] == 0) or (abs(float(exact_cert[1])) < 1e-45)
        except Exception:
            cert_ok = False

    # --- 第 0 步 等式真偽 (G0) — 先驗等式本身成唔成立 ---
    #   identity 類: tol = 1e-9 (EXACT 級); observational 類: 用 target_precision
    #   符號恆等式 (symbolic cert) ⟹ G0 自動 PASS, dev = 0
    tol_use = tol_rel if target_precision is None else max(tol_rel, target_precision)
    if cert_ok and cert_kind == "symbolic":
        dev = 0.0
        gates["G0_equality_holds"] = "PASS"
        notes.append("符號恆等式 (sympy 化簡差 = 0) ⟹ 對所有變量成立")
    else:
        if d_obs is not None:
            dev = abs(d_obs)
        else:
            try:
                vL, vR = sp.N(subs_registered(L), 30), sp.N(subs_registered(R), 30)
                dev = abs(float((vL - vR) / vR)) if vR != 0 else None
            except Exception:
                dev = None
        gates["G0_equality_holds"] = ("PASS" if (dev is not None and dev <= tol_use) else "FAIL")
        if gates["G0_equality_holds"] == "FAIL" and cert_ok and cert_kind == "numeric":
            # 精確數值證書 (mpmath 60 位) 已證 lhs = rhs ⟹ 取代代數代換失敗之 dev
            try:
                dev = abs(float(exact_cert[1]))
            except Exception:
                dev = 0.0
            gates["G0_equality_holds"] = "PASS"
            notes.append("數值精確證書 (mpmath 60 位, |差| < 1e-45) 確立等式")
    if gates["G0_equality_holds"] == "FAIL":
        notes.append("等式不成立: dev = {} > tol = {:g}".format(
            "n/a" if dev is None else f"{dev:.4g}", tol_use))

    # --- 第 3 步 結構內容三測 ---
    if shared_symbol is not None:
        taut, d = t1_tautology(L, R, sp.Symbol(shared_symbol))
    else:
        taut, d = False, None
    gates["T1_tautology"] = ("FAIL" if taut else "PASS")

    coin, coinreason = t2_cross_framework_coincidence(
        lhs_names, rhs_names, mechanism=mechanism, target_kind=target_kind)
    gates["T2_cross_framework"] = ("FAIL" if coin else "PASS")
    notes.append(f"T2: {coinreason}")

    mult = False
    if external_reach is not None:
        mult, mreason = t3_free_multiplier(R, external_reach[1], external_reach[0], R)
        notes.append(f"T3: {mreason}")
    gates["T3_free_multiplier"] = ("FAIL" if mult else "PASS")

    # --- 第 3b 步 兩級測試 (O204 步驟 2) ---
    #   leading_dev = 框架強逼主體值 vs 目標之偏差 (未加乘性修正前)
    #   若主體偏差 ≫ 目標精度, 而全式 dev ≈ 0 ⟹ 匹配由乘性修正承載 ⟹ 🔴 自由乘數
    t5 = False
    if leading_dev is not None:
        ref = target_precision if target_precision is not None else tol_rel
        if abs(leading_dev) > max(5.0 * ref, 1e-3) and (dev is not None and dev <= tol_rel):
            t5 = True
            notes.append(f"T5 兩級測試: 主體偏差 {abs(leading_dev):.4g} ≫ 目標精度 "
                         f"{ref:.3g}, 全式 {dev:.3g} ⟹ 乘性修正承載匹配")
        else:
            notes.append(f"T5 兩級測試: 主體偏差 {abs(leading_dev):.4g}")
    gates["T5_two_level"] = ("FAIL" if t5 else ("PASS" if leading_dev is not None else "N/A"))

    # --- 第 4 步 非唯一表示 (U) ---
    Rcount = nonunique_target
    gates["U_nonunique"] = ("FAIL" if (Rcount is not None and Rcount >= 2) else "PASS")

    # --- 第 5 步 精度 vs 陷阱窗 (G4) ---
    if target_kind == "identity" and dev == 0:
        gates["G4_trap_window"] = "N/A (EXACT)"
    else:
        intrap, treason = trap_window(dev if dev is not None else 0.0, target_precision)
        gates["G4_trap_window"] = ("FAIL" if intrap else "PASS")
        notes.append(f"G4: {treason}")

    # --- 第 6 步 密度基準 (G5) ---
    gates["G5_exact_cert"] = ("PASS" if cert_ok else "MISSING")
    dens = dict(density or {})
    if (target_kind in ("prediction", "prediction_residual")
            and target_precision is not None and dev is not None
            and dev <= target_precision):
        dens.setdefault("N_search", 1)
        dens["note"] = ("觀測量測量誤差內 (|obs−pred| ≤ σ_obs) ⟹ 報 σ 替代分位數 "
                        "(O208 例外 2)")
        dens["dev_in_sigma"] = (dev / target_precision if target_precision else None)
        gates["G5_density"] = "PASS (σ 內, O208 例外 2)"
    elif target_kind == "identity" and cert_ok:
        dens.setdefault("N_search", 1)
        dens["note"] = "純代數恆等式 ⟹ N_search = 1, 唔受密度檢定 (O208 例外/O200 ①)"
        gates["G5_density"] = "PASS (N_search=1)"
    elif density is not None:
        q = dens.get("q_obs")
        Nf = dens.get("N_search_farey")
        if q is not None:
            if q <= 0.01:
                gates["G5_density"] = "PASS"
            elif q <= 0.05:
                gates["G5_density"] = "WEAK"
            else:
                gates["G5_density"] = "FAIL"
        elif Nf is not None:
            if Nf < 1.0:
                gates["G5_density"] = "PASS"
            elif Nf < 10.0:
                gates["G5_density"] = "WEAK"
            else:
                gates["G5_density"] = "FAIL"
            notes.append(f"G5 Farey: N_search = {Nf:.4g} "
                         + ("(< 1 ⟹ 有判別力)" if Nf < 1 else "(≫ 1 ⟹ 零判別力)"))
        else:
            gates["G5_density"] = "INCOMPLETE"
            notes.append("G5: 密度基準缺 q_obs / N_search_farey ⟹ 未閉合 (O208)")
    else:
        gates["G5_density"] = "MISSING"
        notes.append("G5: 冇密度基準 ⟹ 未閉合 (O208)")

    # --- 第 7 步 數域 (G6) ---
    if field_pair is not None:
        sep, g = field_separation(*field_pair)
        gates["G6_field"] = ("FAIL" if sep else "PASS")
        notes.append(f"G6: gcd({field_pair[0]},{field_pair[1]}) = {g} ⟹ "
                     + ("交集 = Q (結構上唔可能相等)" if sep else "交集非 Q"))
    else:
        gates["G6_field"] = "N/A"

    # --- 判級 (決策樹) ---
    code = _decide(target_kind, gates, dev, dens)
    emoji, desc = V[code]
    return {
        "name": name, "class": target_kind, "gates": gates,
        "dev": dev, "density": dens, "verdict": code,
        "emoji": emoji, "desc": desc, "notes": notes,
        "derived_leaves": derived, "closure_trivial_leaves": trivial,
        "exact_certified": cert_ok,
    }


def _decide(target_kind, gates, dev, dens):
    g = gates
    # ★ 審計次序 (O201 6 步): 語法合法性 (①) → 零自由參數 (③) → 等式真偽 (數值)
    if g["G1_G2_leaf_audit"] == "FAIL":
        return "ILLEGAL"
    if g["G3_zero_free_param"] == "FAIL":
        return "FITTED"
    if g.get("G0_equality_holds") == "FAIL":
        return "FALSE"
    if g["T1_tautology"] == "FAIL":
        return "TAUTOLOGY"
    if g["T2_cross_framework"] == "FAIL":
        return "COINCIDENCE"
    if g["T3_free_multiplier"] == "FAIL":
        return "MULTIPLIER"
    if g.get("T5_two_level") == "FAIL":
        return "MULTIPLIER"
    if g["G6_field"] == "FAIL":
        return "FIELD"
    if g["U_nonunique"] == "FAIL":
        return "NONUNIQUE"
    if g["G4_trap_window"] == "FAIL":
        return "TRAP"
    if target_kind == "identity" and g["G5_density"].startswith("PASS"):
        return "IDENTITY_OK"
    if g["G5_density"] == "FAIL":
        return "DENSITY"
    if g["G5_density"] == "WEAK":
        return "WEAK_DENSITY"
    if g["G5_density"].startswith("PASS"):
        if g.get("T1_tautology") == "PASS" and g.get("T2_cross_framework") == "PASS":
            return "MATCH_OK"
        return "FORMAL_OK"
    return "FORMAL_OK"


# =====================================================================
# 第九節 — 輸出工具
# =====================================================================

def fmt_result(res, indent="  "):
    lines = [f"{indent}[{res['emoji']}] {res['name']}",
             f"{indent}    class = {res['class']}   dev = "
             + (f"{res['dev']:.4g}" if res.get("dev") is not None else "n/a")]
    for k, v in res["gates"].items():
        lines.append(f"{indent}    {k:22s} {v}")
    d = res.get("density") or {}
    if d.get("N_search") is not None:
        lines.append(f"{indent}    密度基準: N_search={d['N_search']} "
                     f"N_mc={d.get('N_mc','-')} seed={d.get('seed','-')} "
                     f"d_obs={d.get('d_obs','-')} d_med={d.get('d_med','-')} "
                     f"q_obs={d.get('q_obs','-')}")
    lines.append(f"{indent}    → 判級 {res['verdict']}: {res['desc']}")
    return "\n".join(lines)


if __name__ == "__main__":
    P = closure_pool()
    print("O218 o218_lib self-test")
    print(f"  |P| = {len(P)}")
    print(f"  P ∋ 15 (O204 實錄: 手選洩漏 {15 < 44}); 15 in P = {15 in P}")
    print(f"  base atoms = {sorted(base_atoms().keys())}")
    print(f"  reps(47) unordered = {nonuniqueness(47, P)[0]}")


# =====================================================================
# 第十節 — 入站交接 (2026-10-03): 索引身份 / sector 標籤 / 端點鎖群論
# =====================================================================
# register 交接清單 (owner = O218; 見 o218/docs/08_inbound_handoffs.md):
#   O229 ① 2026-10-02  Binet 筆誤「φ³+φ⁻³ = L₃」→ 本 O 已更正為 φ³−φ⁻³ (第一節)
#   O229 ② 2026-10-02  原子索引身份: R(2) = {(L,0),(F,3)} ⟹「μ² = F₃」唔唯一
#   O229 ③ 2026-10-03 (用戶指派) R5-A: 端點鎖 137 = C(B²,2) + B² + 1 之二值判定
#   O220 ④ 2026-10-02  sector 標籤: 報 44/88/176 家族必標 sector
# 本節一律精確 (int / Fraction / sympy), 浮點只出現於顯示。

# ---- 10.1 索引實現集 R(v) = {(seq, idx) : seq[idx] = v} (O229 docs/09 §1) ----

def lucas(n):
    """L₀ = 2, L₁ = 1, Lₙ = Lₙ₋₁ + Lₙ₋₂。"""
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fib(n):
    """F₀ = 0, F₁ = 1。"""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def index_implementation_set(v, n_max=20, families=("L", "F")):
    """
    R(v) = {(seq, idx) : seq[idx] = v} — O229 docs/09 §1 之機械實現。
    回傳 list[(seq, idx)] 已排序。
    """
    out = []
    for seq in families:
        f = lucas if seq == "L" else fib
        for i in range(n_max + 1):
            if f(i) == v:
                out.append((seq, i))
    return sorted(out)


def index_identity_verdict(v, n_max=20):
    """
    原子索引身份裁決 (O218 準則):
      |R(v)| = 1 ⟹ 索引強制 (可宣稱「= L_n」/「= F_n」)
      |R(v)| ≥ 2 ⟹ 索引非唯一 ⟹ 唔可宣稱; 必須改用產生途徑身份
                    (算子 / 鏈站: 見 chain_index_identity)
    """
    R = index_implementation_set(v, n_max)
    forced = len(R) == 1
    return {"value": v, "impl": R, "count": len(R), "index_forced": forced,
            "verdict": "INDEX_FORCED" if forced else "INDEX_AMBIGUOUS",
            "rule": "|R|=1 ⟹ 可宣稱索引; |R|≥2 ⟹ 索引唔可宣稱, 改用算子/鏈身份"}


def chain_index_identity(v):
    """
    產生途徑身份: v 作為 γ⁽ᴺ⁾ 之站值出現在哪條鏈之哪一站。
      v = μ² = 2 ⟹ 每條鏈之 N/4 站;  v = B = 4 ⟹ 每條鏈之 N/2 站。
    回傳 {chain: index} (全部精確核實 < 1e-40)。
    """
    out = {}
    for ch, info in GAMMA_CHAIN.items():
        N = info["N"]
        cand = {2: N // 4, 4: N // 2}.get(v)
        if cand is None or cand < 1:
            continue
        if abs(float(gamma_chain(cand, ch)) - v) < 1e-40:
            out[ch] = cand
    return out


# ---- 10.2 sector 判別 (O220 交接 ④) ----
# 準則 (O220 final_result (壬)): 身份屬「計數/鏈長/索引和/γ 和」⟹ 家族間隔 = μ² = 2;
#                               身份屬「γ 譜值/平方量」      ⟹ 家族間隔 = μ = √2。
# ⟹ 報 44/88/176 家族必標 sector, 否則歧義。

SECTOR_RULE = {
    "counting": {
        "spacing": "mu2 = 2",
        "family_form": "N -/+ mu2",
        "families": {"44": (42, 44, 46), "88": (86, 88, 90), "176": (174, 176, 178)},
        "examples": "鏈長、索引和、γ 和 (部分和 = N ± 2)",
        "source": "O220 final_result (壬); O211 (90 = Σγ⁽⁸⁸⁾); O220 docs/25 (§5)",
    },
    "spectral": {
        "spacing": "mu = sqrt(2)",
        "family_form": "mu2 -/+ mu",
        "families": {"88": (11, 22, 33), "176": (22, 44, 66), "44": None},
        "values_sympy": "{2 - sqrt(2), 2, 2 + sqrt(2)}",
        "examples": "γ 譜值、平方量; 需 N ≡ 0 mod 8 (2-adic 門檻: 44 = 4·11 唔夠)",
        "source": "O220 final_result (壬); O220 docs/25 §5",
    },
}


def classify_sector(values, tol=1e-9):
    """由家族間隔判定 sector: ≈ √2 ⟹ spectral; ≈ 2 ⟹ counting; 其餘 ⟹ 未定。"""
    import math
    vals = sorted(float(x) for x in values)
    if len(vals) < 2:
        return {"sector": None, "reason": "單點無間隔"}
    gaps = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
    gm = sum(gaps) / len(gaps)
    if abs(gm - math.sqrt(2)) < tol * 10:
        return {"sector": "spectral", "spacing": gm, "target": math.sqrt(2)}
    if abs(gm - 2.0) < tol * 10:
        return {"sector": "counting", "spacing": gm, "target": 2.0}
    return {"sector": None, "spacing": gm, "reason": "間隔既非 √2 亦非 2"}


def sector_of_value(v):
    """
    44 / 88 / 176 之 sector 歧義表: 同一整數在兩個 sector 有唔同意義。
    報告時必須聲明 sector (O220 交接 ④)。
    """
    table = {
        44: {"counting": "N_d (鏈長; 88-L 之半鏈) ; Σγ⁽⁸⁸⁾_odd = 44",
             "spectral": "γ⁽⁸⁸⁾₄₄ = 4 = B (88-L 端點/模) ; γ⁽¹⁷⁶⁾₄₄ = 2 = μ² (176-L 中心站)"},
        88: {"counting": "N_site = 2N_d (站數; 鏈長) ; 88 = {86,88,90} 之中項",
             "spectral": "γ⁽¹⁷⁶⁾₈₈ = 4 = B (176-L 端點) ; γ⁽⁸⁸⁾ 之索引上界"},
        176: {"counting": "4N_d = N_laplacian 半集上界 ; {174,176,178} 之中項",
              "spectral": "176-L 之鏈長 ⟹ 全部 176-L 譜值之歸一化分母"},
    }
    return {"value": v, "readings": table.get(v), "ambiguous": True}


def require_sector_tag(value, sector):
    """報告 44/88/176 家族時必須聲明 sector; 未聲明/錯標 ⟹ raise (禁歧義報告)。"""
    if value not in (44, 88, 176):
        return True
    if sector not in ("counting", "spectral"):
        raise ValueError(f"{value} 之報告缺 sector 標籤 (必須 'counting' | 'spectral')")
    return True


# ---- 10.3 端點鎖群論 (O229 ③ / R5-A) ----

def fixed_point_pigeonhole(G_order, n_points):
    """
    定理 (O218 R5-A): 設有限群 G (|G| = G_order) 作用於 n_points 點。
      傳遞 ⟺ n_points | G_order。若 G_order > n_points − 1 且唔傳遞 (軌道數 k ≥ 2),
      則 Σ_{g≠1} fix(g) = G_order·k − n_points ≥ 2·G_order − n_points > G_order − 1
      ⟹ (若所有 g≠1 皆 fix ≤ 1 則 Σ ≤ G_order − 1) 矛盾
      ⟹ **∃ g ≠ 1 固定 ≥ 2 點**。
    對 (120, 16): 2·120 − 16 = 224 > 119 ⟹ 必然存在 fix ≥ 2 之元素。
    """
    transitive_possible = (n_points % G_order == 0)
    k_min = 1 if transitive_possible else 2
    total_min = G_order * k_min - n_points
    bound_le_one = G_order - 1
    return {"G_order": G_order, "n_points": n_points,
            "transitive_possible": transitive_possible,
            "k_min": k_min, "sum_fix_min": total_min,
            "sum_fix_if_all_le_one": bound_le_one,
            "forced_double_fixpoint": total_min > bound_le_one}


def pair_action_free_possible(G_order, n_points):
    """Pairs(n_points) 之作用可否自由? (自由 ⟸ 所有 g≠1 固定 ≤ 1 點。)"""
    r = fixed_point_pigeonhole(G_order, n_points)
    return {**r, "free_on_pairs_possible": not r["forced_double_fixpoint"],
            "reason": ("C(fix(g),2) ≥ 1 ⟹ Pairs 有非平凡穩定子 ⟹ 非自由"
                       if r["forced_double_fixpoint"] else "可能")}


def equivariant_pair_bijection_possible(G_order, n_points):
    """
    Pairs(n_points) →（|G| = G_order 之正則 G-set）等變雙射存在 ⟺ Pairs 作用自由且傳遞。
    正則 = 自由 + 傳遞 ⟹ 任一條件失敗即唔存在。
    """
    r = pair_action_free_possible(G_order, n_points)
    card_ok = (n_points * (n_points - 1) // 2) == G_order
    ok = card_ok and r["free_on_pairs_possible"]
    return {"card_match": card_ok, "free": r["free_on_pairs_possible"],
            "exists": ok, "reason": r["reason"]}


def partitions_into_divisors(n, d, min_parts=2):
    """n 之分解 (每塊整除 d) — O229 docs/30 之「16 之 34 種非傳遞分解」。"""
    out = []
    def rec(rem, mx, acc):
        if rem == 0:
            if len(acc) >= min_parts:
                out.append(tuple(acc))
            return
        for s in range(min(rem, mx), 0, -1):
            if d % s == 0:
                rec(rem - s, s, acc + [s])
    rec(n, n, [])
    return sorted(out)


def pair_count_of_partition(parts):
    """分解之內部對數 (同塊) + 跨塊對數 = C(n,2) 恆等。"""
    from math import comb
    inside = sum(comb(p, 2) for p in parts)
    cross = sum(parts[i] * parts[j] for i in range(len(parts)) for j in range(i + 1, len(parts)))
    return inside, cross, inside + cross


def pair_count_partition_invariant(n):
    """∀ 分解 n = Σ nᵢ: Σ C(nᵢ,2) + Σ_{i<j} nᵢnⱼ = C(n,2) EXACT (配對計數對分裂穩健)。"""
    from math import comb
    bad = []
    for parts in partitions_into_divisors(n, n) if False else _all_partitions(n):
        i_, c_, t_ = pair_count_of_partition(parts)
        if t_ != comb(n, 2):
            bad.append((parts, t_))
    return {"n": n, "checked": len(_all_partitions(n)), "bad": bad}


def _all_partitions(n, maxpart=None):
    maxpart = maxpart or n
    if n == 0:
        return [()]
    out = []
    for k in range(min(n, maxpart), 0, -1):
        for rest in _all_partitions(n - k, k):
            out.append((k,) + rest)
    return out


def endpoint_lock_anatomy(B=4):
    """137 = C(B²,2) + B² + 1 之解剖 + dim Sym(B²) 對照讀法。"""
    from math import comb
    B2 = B * B
    c = comb(B2, 2)
    return {"B": B, "B2": B2, "C(B2,2)": c, "B2+1": B2 + 1, "total": c + B2 + 1,
            "dim_Sym": B2 * (B2 + 1) // 2, "dim_Sym_plus_1": B2 * (B2 + 1) // 2 + 1}
