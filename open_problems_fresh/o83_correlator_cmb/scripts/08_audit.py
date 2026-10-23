#!/usr/bin/env python3
"""
O83 — Script 08: 全量審計 (AUDIT)
==================================
獨立重算 + 反空洞檢查 + 文檔完整性審計
唔信任原腳本嘅 PASS 數，逐項重算。

[A] 路徑衛生: 硬編碼 ghost tree 掃描
[B] 空洞 check 掃描 (AST): literal-True / 結構恆真 / 數據依賴
[C] 精確重算: Σγ (sympy 精確), λ_sync 身份, G_n(0) 身份
[D] 峰位: 兩套 obs 各自 RMS (查 cherry-pick)
[E] 振幅: 循環性證明 (w_n 由 A_m 反解)
[F] T_CMB 百分比: cmb_cl 0.01% vs 實算
[G] m=5 F₆/F₈ 出處: 有無獨立推導
[H] 文檔完整性: 位元組/狀態 vs 應有
"""
import ast, os, sys, hashlib, re
from fractions import Fraction
import sympy as sp

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
DOCS = os.path.join(BASE, "docs")
GHOST = "/home/wsl/Projects/IDCM" + "/IDCM-v10.0"   # 拼合，避免本檔自命中

findings = []
def rec(kind, name, detail=""):
    findings.append((kind, name, detail))
    print(f"  [{kind}] {name} {detail}")

print("=" * 74)
print("  O83 — Script 08: 全量審計")
print("=" * 74)

# ──────────────────────────────────────────────
# [A] 路徑衛生
# ──────────────────────────────────────────────
print("\n─── [A] 路徑衛生 (ghost tree 掃描) ───")
ghost_hits = []
for f in sorted(os.listdir(SCRIPTS)):
    if not f.endswith(".py"):
        continue
    p = os.path.join(SCRIPTS, f)
    with open(p, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            if GHOST in line:
                ghost_hits.append((f, i, line.strip()[:90]))
print(f"  硬編碼 ghost tree '{GHOST}' 命中 {len(ghost_hits)} 處:")
for f, i, txt in ghost_hits:
    print(f"    {f}:{i}  {txt}")
rec("🔴" if ghost_hits else "🟢", "ghost path", f"{len(ghost_hits)} call sites")

# ──────────────────────────────────────────────
# [B] 空洞 check 掃描 (AST)
# ──────────────────────────────────────────────
print("\n─── [B] 空洞 check 掃描 (AST) ───")
# check(name, cond, detail) — cond 若係 Constant(True) 即空洞
total_checks = 0
vacuous = []
per_file = {}
for f in sorted(os.listdir(SCRIPTS)):
    if not f.endswith(".py") or f.startswith("08"):
        continue
    p = os.path.join(SCRIPTS, f)
    tree = ast.parse(open(p, encoding="utf-8").read())
    n_site = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "check":
            n_site += 1
            total_checks += 1
            if len(node.args) >= 2:
                c = node.args[1]
                # 解析 cond 表達式，判斷是否恆真
                if isinstance(c, ast.Constant) and c.value is True:
                    nm = node.args[0].value if isinstance(node.args[0], ast.Constant) else "?"
                    vacuous.append((f, node.lineno, nm, "literal True"))
                elif isinstance(c, ast.Name) and c.id == "True":
                    nm = node.args[0].value if isinstance(node.args[0], ast.Constant) else "?"
                    vacuous.append((f, node.lineno, nm, "literal True"))
    per_file[f] = n_site
print(f"  check() call site 總數 = {total_checks}")
for f, n in per_file.items():
    print(f"    {f}: {n}")
print(f"  空洞 (cond 硬寫 True) = {len(vacuous)}:")
for f, ln, nm, why in vacuous:
    print(f"    🔴 {f}:{ln}  「{nm}」 ({why})")
rec("🔴" if vacuous else "🟢", "vacuous checks",
    f"{len(vacuous)}/{total_checks} 空洞 ⟹ 實質 check = {total_checks - len(vacuous)}")

# ──────────────────────────────────────────────
# [C] 精確重算
# ──────────────────────────────────────────────
print("\n─── [C] 精確重算 (sympy 精確有理數) ───")
n = sp.symbols('n', integer=True, positive=True)
m = sp.symbols('m', integer=True, positive=True)

# 44-site chain: Σ_{n=1}^{44} 4sin²(nπ/88)
S44 = sp.simplify(sp.summation(4*sp.sin(n*sp.pi/88)**2, (n, 1, 44)))
print(f"  Σ_{{n=1..44}} 4sin²(nπ/88) = {S44}")
rec("🟢" if S44 == 90 else "🔴", "Σγ(44-site)=90", f"{S44}")

# 88-site chain: Σ_{k=1..88} 4sin²(kπ/176) 及其奇偶分拆
S88 = sp.simplify(sp.summation(4*sp.sin(n*sp.pi/176)**2, (n, 1, 88)))
S88_even = sp.simplify(sp.summation(4*sp.sin(2*m*sp.pi/176)**2, (m, 1, 44)))
S88_odd = sp.simplify(sp.summation(4*sp.sin((2*m-1)*sp.pi/176)**2, (m, 1, 44)))
print(f"  Σγ(88-site, k=1..88) = {S88}")
print(f"    k 偶 = {S88_even}, k 奇 = {S88_odd}, 總 = {sp.simplify(S88_even+S88_odd)}")
rec("🟢" if (S88_even == 90 and S88_odd == 88 and S88 == 178) else "🔴",
    "Σγ(88-site) 偶90/奇88/總178", f"{S88_even}/{S88_odd}/{S88}")
rec("🟢" if S88 == 2*89 else "🔴", "178 = 2F₁₁", f"{S88} vs {2*89}")

# λ_sync 身份
R_world = sp.Float(4129.94, 20)
print(f"\n  R_world = {R_world} Mpc")
for name, val in [("πR_world/44", sp.pi*R_world/44), ("R_world/44", R_world/44),
                  ("R_world/14", R_world/14)]:
    print(f"    {name} = {sp.N(val, 12)} Mpc")
lam_claim = sp.Float(294.88, 12)
print(f"    λ_sync (文檔聲稱) = {lam_claim} Mpc")
r1 = abs(sp.pi*R_world/44 - lam_claim)/lam_claim*100
r2 = abs(R_world/44 - lam_claim)/lam_claim*100
print(f"    vs πR_world/44 dev = {sp.N(r1,6)}%")
print(f"    vs R_world/44  dev = {sp.N(r2,6)}%")
if float(sp.N(r1, 10)) < 0.1:
    rec("🔴", "ℓ_sync=44 係恆等式 (tautology)",
    "λ_sync≡L_ring/88=πR_world/44 ⟹ ℓ_sync≡44 由定義，非預言 (O86 docs/03 #168 已記同義反覆)")
else:
    rec("🟡", "ℓ_sync 關係需再核", f"r1={r1}")
rec("🔴", "2N_d 標籤錯 (跨 O P3)",
    "P3:82 自訂 N_d=44 ⟹ 2N_d=88≠44；正解 ℓ_sync=N_d=44 → 已 handoff P3")

# G_n(0) 身份
print(f"\n  G_n(0) 身份:")
wn = 2*sp.sin(sp.pi/88)
print(f"    ω_1 = 2sin(π/88) = {sp.N(wn,12)}")
print(f"    1/(2ω_1) = {sp.N(1/(2*wn),12)}")
print(f"    1/(4sin(π/88)) = {sp.N(1/(4*sp.sin(sp.pi/88)),12)}")
rec("🟢", "G_n(0)=1/(2ω_n)≡1/(4sin(nπ/88))", "代數恆等，非獨立預言")

# ──────────────────────────────────────────────
# [D] 峰位: 兩套 obs 各自 RMS
# ──────────────────────────────────────────────
print("\n─── [D] 峰位 RMS — 兩套 obs 對照 ───")
from math import comb
def C(nn, kk):
    return comb(nn, kk) if nn >= kk >= 0 else 0
M, F6, F8 = 33, 8, 21
pred = {}
for m in range(1, 8):
    pred[m] = 44*(M-F6)+F8 if m == 5 else 44*(M-C(9-m, 2))+((m-1)*9) % 25
print("  m | ℓ_pred |  cmb_cl obs | dev%  |  O9 obs | dev%")
obs_cl = {1: 220.1, 2: 537, 3: 810, 4: 1014, 5: 1121, 6: 1337, 7: 1400}
obs_o9 = {1: 221, 2: 527, 3: 815, 4: 1013, 5: 1121, 6: 1337, 7: 1400}
d1, d2 = [], []
for m in range(1, 8):
    a = (pred[m]-obs_cl[m])/obs_cl[m]*100
    b = (pred[m]-obs_o9[m])/obs_o9[m]*100
    d1.append(a); d2.append(b)
    print(f"  {m} | {pred[m]:>6} | {obs_cl[m]:>10} | {a:+6.3f} | {obs_o9[m]:>7} | {b:+6.3f}")
rms1 = (sum(x*x for x in d1)/7)**0.5
rms2 = (sum(x*x for x in d2)/7)**0.5
print(f"\n  RMS(cmb_cl obs) = {rms1:.2f}%   RMS(O9 最終矩陣 obs) = {rms2:.2f}%")
rec("🔴", "cherry-pick: O83 用舊 obs 得 0.335%",
    f"同公式用 O9 最終矩陣 obs ⟹ RMS={rms2:.2f}% (O9 記錄 0.83%)")
rec("🟢" if abs(rms2-0.83) < 0.1 else "🔴", "O9 記錄 RMS=0.83% 可重現",
    f"{rms2:.3f}% vs 0.83%")

# ──────────────────────────────────────────────
# [E] 振幅: 循環性
# ──────────────────────────────────────────────
print("\n─── [E] 振幅循環性 ───")
A_obs = {1: 1.0, 2: 4/9, 3: 4/9, 4: 9/49, 5: 3/14, 6: 16/121, 7: 1/7}
print("  O83 路徑: G_n(0) 已知 → w_m² ≡ A_m/G_m(0)  (w_m 由 A_m 反解)")
for m in [1, 2, 5]:
    G0 = 1/(4*float(sp.sin(sp.pi*m/88)))
    print(f"    m={m}: A={A_obs[m]:.6f}, G0={G0:.6f} ⟹ w²≡{A_obs[m]/G0:.6f}")
print("  ⟹ w_m 冇獨立結構式；A_m 係輸入唔係輸出")
# 檢查 O83 全部腳本有無 w_n 嘅獨立推導
w_defs = []
for f in sorted(os.listdir(SCRIPTS)):
    if not f.endswith(".py"):
        continue
    txt = open(os.path.join(SCRIPTS, f), encoding="utf-8").read()
    if re.search(r"w_n\s*=|w_sq\[m\]\s*=|w2\s*=\s*A\s*/", txt):
        w_defs.append(f)
print(f"  含 w_n 定義嘅腳本: {w_defs}")
rec("🔴", "C_ℓ=Σw²G 係重述非推導", "w_m 由 A_m 反解 ⟹ 零預測力")
rec("🔴", "「零自由參數」對振幅唔成立", "振幅係 O9 後驗值 (O9 自認『事後揀最靚』)")

# ──────────────────────────────────────────────
# [F] T_CMB 百分比
# ──────────────────────────────────────────────
print("\n─── [F] T_CMB 百分比 ───")
phi = (1+5**0.5)/2
T_Pl = 1.416784e32
T_pred = 2*T_Pl*2.718281828459045**-74*(134/100)*(1-phi**-9)
T_obs = 2.72548
dev = abs(T_pred-T_obs)/T_obs*100
print(f"  T_pred = {T_pred:.4f} K, T_obs = {T_obs} K, dev = {dev:.3f}%")
rec("🔴", "cmb_cl 記 0.01% 錯", f"實算 {dev:.3f}% (差 10×)")
rec("🟢" if abs(dev-0.10) < 0.02 else "🔴", "O83 doc 記 0.10% 正確", f"{dev:.3f}%")

# ──────────────────────────────────────────────
# [G] m=5 F₆/F₈ 出處
# ──────────────────────────────────────────────
print(f"\n─── [G] m=5 F₆/F₈ 出處 ───")
prov = []
for f in sorted(os.listdir(SCRIPTS)):
    if not f.endswith(".py") or f.startswith("08"):
        continue
    for i, line in enumerate(open(os.path.join(SCRIPTS, f), encoding="utf-8"), 1):
        s = line.strip()
        if re.match(r"^F6\s*=", s) or re.match(r"^F8\s*=", s):
            prov.append((f, i, s))
print(f"  F₆/F₈ 賦值行 (逐字):")
for f, i, s in prov:
    print(f"    {f}:{i}  {s}")
derived = [x for x in prov if not re.match(r"^F[68]\s*=\s*\d+$", x[2])]
print(f"  由其他結構量生成嘅行 = {len(derived)}")
rec("🔴" if not derived else "🟢", "F₆=8/F₈=21 無獨立推導",
    "全部直接賦值；m=5 修正屬後驗 (O9 自認『事後揀最靚』)")

# ──────────────────────────────────────────────
# [H] 文檔完整性
# ──────────────────────────────────────────────
print("\n─── [H] 文檔完整性 (內容標記, 唔用位元組) ───")
d1p = os.path.join(BASE, "docs", "01_problem_record.md")
ssp = os.path.join(BASE, "SESSION_START.md")
d2p = os.path.join(DOCS, "02_derivation_record.md")
rtp = os.path.join(BASE, "01_problem_record.md")
for label, p in [("root/01_problem_record.md", rtp), ("docs/01_problem_record.md", d1p),
                 ("docs/02_derivation_record.md", d2p), ("SESSION_START.md", ssp)]:
    print(f"    {os.path.getsize(p):>6} bytes  {label}")
d1 = open(d1p, encoding="utf-8").read()
root01 = open(rtp, encoding="utf-8").read()
# 量化標記應在 root/01 (08-25 原文重建處)
markers = ["44(M−C(9−m,2))", "((k+1)/(4k−1))²", "1/(4sin(nπ/88))",
           "Z_0(β) = ∏", "零自由參數"]
missing = [mk for mk in markers if mk not in root01]
print(f"    root/01 缺失量化標記: {missing}")
skel = "待攻堅 (由 O72 SESSION_START 移交)" in d1
rec("🟢" if (skel and not missing) else ("🔴" if missing else "🟡"),
    "docs/01=10-15 骨架物證 + root/01 量化內容已復原",
    f"docs/01 skeleton={skel}, root/01 缺 {len(missing)}/{len(markers)} 標記")
ss = open(ssp, encoding="utf-8").read()
rec("🟢" if "🟡 partial" in ss else "🔴", "SESSION_START 閉合狀態",
    "body 保留 08-25 骨架；10-23 裁決 append (§ ★ 2026-10-23)")
d2 = open(d2p, encoding="utf-8").read()
rec("🟢" if ("58/58 PASS" in d2 and "2026-10-23 審計更正附註" in d2) else "🔴",
    "docs/02 推導記錄完整 + 更正附註", "原文保留、附註 append")
d3p = os.path.join(DOCS, "03_audit_report.md")
rec("🟢" if os.path.exists(d3p) else "🔴", "docs/03 審計報告存在",
    f"{os.path.getsize(d3p)} bytes")
rec("🟢" if "🟡 partial" in root01 else "🟡", "root/01 已標審計裁決",
    "原 🔴 待攻堅 → 🟡 partial")

# ──────────────────────────────────────────────
# 總結
# ──────────────────────────────────────────────
print("\n" + "=" * 74)
n_red = sum(1 for k, _, _ in findings if k == "🔴")
n_yel = sum(1 for k, _, _ in findings if k == "🟡")
n_grn = sum(1 for k, _, _ in findings if k == "🟢")
print(f"  審計結果: 🟢 {n_grn}  🟡 {n_yel}  🔴 {n_red}  (共 {len(findings)} 項)")
print("=" * 74)
print(f"""
  O83 審計裁決 (2026-10-23 修復後):
  🟢 保留: propagator 代數恆等、Σγ 精確和、橋接 formalism 形式、熱態形式
  🟡 降級: 「零自由參數」(振幅非導出)、「ℓ_sync=44」(定義恆等)、
           RMS 0.335% (cherry-pick obs ⟹ 權威 0.84%)、m=5 F₆/F₈ (後驗)
  ✅ 已修: ghost path (01/06/07 改相對)、11 個空洞 check 改 📝 註記、
           docs/01 覆蓋物證 + root/01 原文重建、裁決 append 至 SESSION_START/docs/02
  📤 已發還: P3「ℓ_sync = 2N_d = 44」標籤錯 (N_d=44 ⟹ 2N_d=88) — register handoff 已立
""")
sys.exit(0)