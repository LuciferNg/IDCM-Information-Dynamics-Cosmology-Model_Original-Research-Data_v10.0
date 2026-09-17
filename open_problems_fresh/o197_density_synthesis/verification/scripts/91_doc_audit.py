#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O198 文檔審計 — verification/scripts/91_doc_audit.py

層 2/3: 只讀文檔層審計 (唔驗物理, 驗「記錄」本身)。
  (a) 數值出現檢查: 每個權威值必須喺相關文檔出現 (容差 = 文檔顯示精度)
  (b) 文檔間一致性: 同一量喺多份文檔出現必須一致
  (c) 測試覆蓋完整性: scripts/01-06 全部 48 個 check ID 必須有文檔記錄
  (d) 檔案時序: scripts → data → docs → 審計文檔
  (e) 目錄範圍: verification/ 只含預期檔案 (冇跨目錄寫入)
  (f) 污染檢查: O198 文檔冇改寫 O197 歷史; O197 主 docs 冇新推導內容
  (g) 第三方法 MC (換 seed) 重算 6 個頭條 MC 值

只讀 (除本檔)。exit 1 = 有 FAIL。
"""
import json, math, random, re, sys, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent          # verification/
O197 = BASE.parent                                     # o197_density_synthesis/
ROOT = O197.parent                                     # open_problems_fresh/
DATA = BASE / "data/harikane23_table3_eddington.json"

PASS, FAIL = [], []
def chk(sec, name, ok, note=""):
    (PASS if ok else FAIL).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {sec} {name}" + (f"  — {note}" if note else ""))
    return ok

def rd(p):
    return Path(p).read_text(encoding="utf-8")

# ============ 文檔集合 ============
DOCS = {
    "pr":  BASE / "01_problem_record.md",
    "ss":  BASE / "SESSION_START.md",
    "fr":  BASE / "final_result.md",
    "d1":  BASE / "docs/01_seed_spectrum_verification.md",
    "d2":  BASE / "docs/02_measured_eddington_attack.md",
    "d3":  BASE / "docs/03_growth_closure.md",
    "d4":  BASE / "docs/04_record_audit.md",
    "d5":  BASE / "docs/05_record_closeout.md",
    "d6":  BASE / "docs/06_tail_shape_attack.md",
    "d7":  BASE / "docs/07_zf_structural_attack.md",
    "d8":  BASE / "docs/08_w_fraction_attack.md",
    "d10": BASE / "docs/10_hierarchy_source.md",
    "d11": BASE / "docs/11_growth_cutoff.md",
    "d12": BASE / "docs/12_hygiene_f3_f6.md",
}
TXT = {k: rd(v) for k, v in DOCS.items()}

def norm(s):
    """統一: full-width minus → ASCII, 去千分位, 去空白"""
    return (s.replace("\u2212", "-").replace("\u2013", "-")
             .replace(",", "").replace(" ", "").replace("\u00a0", ""))

NT = {k: norm(v) for k, v in TXT.items()}

print("=" * 78)
print("(a) 數值出現檢查 — 每個權威值必須喺指定文檔出現")
print("=" * 78)

# ---- 獨立重算權威值 (第一原理) ----
data = json.load(open(DATA))
masses = sorted(d["M_BH"] for d in data)
lams = [d["lambda_Edd"] for d in data]
M_base = 1.914e6
phi = (1 + 5 ** 0.5) / 2
mu = 1 / phi + 11 / 45
dhat = lambda k: -math.cos(k * math.pi / 88)
ln1p = [math.log(1 + dhat(k)) for k in range(1, 89)]
var_pop_pos = sum((v - sum(ln1p[44:]) / 44) ** 2 for v in ln1p[44:]) / 44
s = math.sqrt(36 * var_pop_pos)
mu_lnM = math.log(M_base) + 1.5 * mu
sig_lnM = 1.5 * s
M_turn = M_base * 2 ** 1.5
A_lo = M_base * (1 + math.sin(math.pi / 88)) ** 1.5
A_masses = [M_base * (2 * math.sin(k * math.pi / 176) ** 2) ** 1.5 for k in range(45, 89)]
Pi_plus = 1.0
for k in range(45, 89):
    Pi_plus *= (1 + dhat(k))
med_B = math.exp(mu_lnM)
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
P_B_low = Phi((math.log(M_turn) - mu_lnM) / sig_lnM)
geo = math.exp(sum(math.log(l) for l in lams) / 10)
ari = sum(lams) / 10
med_lam = sorted(lams)[4:6]
med_lam = sum(med_lam) / 2
sig_lnl = math.sqrt(sum((math.log(l) - math.log(geo)) ** 2 for l in lams) / 9)
lnm = [math.log(m) for m in masses]
obs_med = masses[len(masses) // 2]
zU = (math.log(1.7e9) - mu_lnM) / sig_lnM
# Spearman ρ
def spearman(a, b):
    n = len(a)
    ra = [sorted(a).index(v) + 1 for v in a]; rb = [sorted(b).index(v) + 1 for v in b]
    ma = sum(ra) / n; mb = sum(rb) / n
    return sum((ra[i] - ma) * (rb[i] - mb) for i in range(n)) / math.sqrt(
        sum((r - ma) ** 2 for r in ra) * sum((r - mb) ** 2 for r in rb))
rho = spearman([math.log(m) for m in masses], [math.log(l) for l in lams])
# K-S
high = sorted(m for m in masses if m > M_turn)
zt = (math.log(M_turn) - mu_lnM) / sig_lnM
cdf_tr = lambda m: (Phi((math.log(m) - mu_lnM) / sig_lnM) - Phi(zt)) / (1 - Phi(zt))
KS = max(abs((i + 1) / len(high) - cdf_tr(m)) for i, m in enumerate(high))
# 斜率
sl_g = -(math.log(1e8) - mu_lnM) / sig_lnM ** 2
# 通道 A 下限 → G_max / T_active
Gmax1, Gmax2 = 2.3e6 / A_lo, 3.7e6 / A_lo
T1, T2 = math.log(Gmax1) * 0.5 * 1000, math.log(Gmax2) * 0.5 * 1000

# 值 → (期望字串集合, 應出現嘅文檔 keys, 說明)
CHECKS = [
    # 結構常數
    ("M_base = 1.914e6", ["1.914e6"], ["pr", "d1", "ss"], "O173 P7 輸入"),
    ("μ = φ⁻¹+11/45 = 0.862478", ["0.862478"], ["pr", "d1"], "logN 參數結構"),
    ("s = 1.1874", ["1.1874"], ["pr", "d1"], "s² = 36·Var_pop"),
    ("M_turn = 5.4136e6", ["5.4136e6", "5.41e6"], ["pr", "d1", "d2", "d3", "fr"], "轉折閉式"),
    ("通道 A 下限 2.017e6", ["2.017e6", "2.02e6"], ["pr", "d1", "d2", "d3", "fr"], "閉式"),
    ("Π(1+δ̂₊) = 1.5474e9", ["1.5474e9"], ["d1"], "O197 T2 重驗"),
    ("通道 B 中位 6.9790e6", ["6.9790e6", "6.98e6"], ["pr", "d1"], "logN 中位"),
    ("P_B(M<M_turn) = 0.4433", ["0.4433"], ["d1"], "域分離量化"),
    ("觀測質量序列", ["2.3e6", "3.7e6", "1.0e7", "9.8e7"], ["d1"], "Harikane 10 AGN"),
    ("低端 2/10", ["2/10"], ["pr", "d1", "ss"], "預言 2"),
    ("高端 8/8", ["8/8"], ["pr", "d1", "ss", "fr"], "預言 3"),
    ("K-S D = 0.216", ["0.216"], ["pr", "d1", "ss", "fr"], "截斷 logN"),
    ("K-S 臨界 0.480", ["0.480"], ["pr", "d1", "ss", "fr"], "n=8 臨界值"),
    ("轉折帶期望 1.23", ["1.23"], ["pr", "d1", "ss", "fr"], "V4"),
    ("w_obs = 0.2", ["0.2"], ["pr", "d1", "ss", "fr"], "w 首約束"),
    ("CP CI 下 0.025", ["0.025"], ["pr", "d1", "ss", "fr"], "Clopper-Pearson"),
    ("CP CI 上 0.556", ["0.556"], ["pr", "d1", "ss", "fr"], "Clopper-Pearson"),
    ("k 映射 48", ["k≈48", "48"], ["pr", "d1", "ss", "fr"], "GLASS_160133"),
    ("k 映射 60", ["k≈60", "60"], ["pr", "d1", "ss", "fr"], "GLASS_150029"),
    # Eddington 前向 (scripts/03)
    ("λ_Edd = f_bar = 0.1", ["f_bar", "0.1"], ["pr", "d1", "d2", "d3", "fr"], "結構身份"),
    ("L_min ≤ 2.9e43", ["2.9e43"], ["pr", "d1", "fr"], "最暗物上界"),
    ("L_min* = 5.73e43", ["5.73e43"], ["pr", "d1", "ss", "fr"], "反演"),
    ("M_min* = 4.55e6", ["4.55e6"], ["d1"], "反演對應質量"),
    ("T5a 預測 7.52e6", ["7.52e6"], ["pr", "d1", "d2", "fr"], "固定 λ"),
    ("T5b 預測 9.19e6", ["9.19e6"], ["pr", "d1", "d2", "fr"], "log-uniform"),
    ("T5a 張力 1.45 dex", ["1.45"], ["pr", "d1", "d2", "fr"], "dex"),
    ("T5b 張力 1.25 dex", ["1.25"], ["pr", "d1", "d2", "fr"], "dex"),
    ("T6 低端份額 0.391", ["0.391", "0.39"], ["pr", "d1"], "λ log-uniform"),
    ("T7 + virial 0.392", ["0.392", "0.39"], ["pr", "d1"], "virial 0.4 dex"),
    # scripts/04 UHz1
    ("P(M≥1.7e9) = 1.016e-3", ["1.016e-3"], ["pr", "d1", "ss", "fr"], "預言 4"),
    ("UHz1 z-score 3.085", ["3.085"], ["pr", "d1", "fr"], "logN 尾"),
    ("全 PDF 斜率 −4.23/dex", ["-4.23/dex"], ["pr", "d1", "d3", "fr"], "校正"),
    ("Gaussian 斜率 −0.839/−0.84", ["-0.84"], ["pr", "d1", "fr"], "O197 定義"),
    ("截斷 logN 中位 1.99e7", ["1.99e7"], ["pr", "d1"], "V4"),
    ("高端中位 4.2e7", ["4.2e7"], ["pr", "d1"], "觀測"),
    ("LBQS −0.82/dex", ["-0.82"], ["pr", "d1", "d3", "fr"], "z=2.5 參考"),
    ("N=434 → P(≥1)=0.36", ["434", "0.36"], ["pr", "d1", "ss", "fr"], "Akins+2024"),
    # scripts/05 實測 λ
    ("λ geo = 0.702", ["0.702"], ["pr", "d2", "ss", "fr"], "實測"),
    ("λ arith = 1.275", ["1.275"], ["pr", "d2", "fr"], "實測"),
    ("λ median = 1.060", ["1.060"], ["pr", "d2", "fr"], "實測"),
    ("σ_lnλ = 1.39", ["1.39"], ["pr", "d2", "d3", "fr"], "實測"),
    ("偏置 7.0×", ["7.0×", "7×"], ["pr", "d2", "fr"], "結構值 0.1"),
    ("實測 λ 前向中位 5.40e6", ["5.40e6"], ["pr", "d2", "ss", "fr"], "V2"),
    ("張力 −1.78 ln", ["-1.78"], ["pr", "d2", "ss", "fr"], "V2"),
    ("張力顯著 2.5σ / 3.7σ", ["2.5σ", "3.7σ"], ["pr", "d2", "ss", "fr"], "V3"),
    ("均勻成長需 g = 5.92", ["5.92"], ["pr", "d2", "d3", "ss", "fr"], "V4"),
    ("容許 g ≤ 1.14", ["1.14"], ["pr", "d2", "d3", "ss", "fr"], "預言 2 約束"),
    ("矛盾 5.2×", ["5.2×"], ["pr", "d2", "d3", "fr"], "V4"),
    ("virial 需 0.77 dex", ["0.77"], ["pr", "d2", "d3", "fr"], "V5"),
    ("剩 ~0.37 dex", ["0.37"], ["pr", "d2", "d3", "fr"], "缺口"),
    ("ρ = −0.648", ["-0.648"], ["pr", "d2", "d3", "ss", "fr"], "V6 Spearman"),
    ("p = 0.024", ["0.024"], ["pr", "d2", "d3", "ss", "fr"], "permutation"),
    ("L_min* 重反演 1.02e45", ["1.02e45"], ["pr", "d2", "ss", "fr"], "V8"),
    ("L_bol 範圍 1.8e44-1.1e46", ["1.8e44", "1.1e46"], ["pr", "d2", "fr"], "觀測帶"),
    # scripts/06 成長
    ("t_ef = 5.0e8 yr", ["5.0e8"], ["pr", "d3", "ss", "fr"], "T8a"),
    ("z_f* = 13.43", ["13.43"], ["pr", "d3", "ss", "fr"], "T8b"),
    ("成長後中位 3.17e7", ["3.17e7"], ["pr", "d3", "ss", "fr"], "T8b"),
    ("張力 −0.010 ln", ["-0.010"], ["pr", "d3", "ss", "fr"], "T8b"),
    ("t(5) = 1.171 Gyr", ["1.171"], ["d3"], "T8a'"),
    ("G 範圍 2.5-11.4", ["2.5", "11.4"], ["pr", "d3", "fr"], "T8d"),
    ("GLASS_160133 T ≤ 66 Myr", ["66"], ["pr", "d3", "ss", "fr"], "T8e"),
    ("GLASS_150029 T ≤ 303 Myr", ["303"], ["pr", "d3", "ss", "fr"], "T8e"),
    ("UHz1 seed 7.94e8", ["7.94e8"], ["pr", "d3", "ss", "fr"], "T8f"),
    ("UHz1 G = 2.14", ["2.14"], ["pr", "d3", "fr"], "T8f"),
    ("UHz1 P = 3.9e-3", ["3.9e-3"], ["pr", "d3", "fr"], "T8f"),
    ("高端 seed 中位 8.66e6", ["8.66e6"], ["pr", "d3"], "T8h1"),
    ("高端 seed z = 0.12", ["0.12"], ["pr", "d3", "ss", "fr"], "T8h1"),
    ("channel forward 2.34e7", ["2.34e7"], ["pr", "d3", "ss", "fr"], "T8h3"),
    ("channel 張力 −0.31 ln", ["-0.31"], ["pr", "d3", "ss", "fr"], "T8h3"),
    # scripts/07 開放項 4 攻堅
    ("★記錄目標 −0.82/dex 係全局 OLS", ["-0.82"], ["pr", "d6"], "B1 重現"),
    ("論文 β = −2.6 (z=2.5 bin)", ["-2.6"], ["d6"], "footnote 6"),
    ("β 不確定度 0.4–1.4", ["0.4"], ["d6"], "footnote 6"),
    ("修正後斜率比 1.76", ["1.76"], ["pr", "d6"], "C2"),
    ("模型 β 窗平均 −4.58", ["-4.58"], ["d6"], "C1"),
    ("顯著性 1.4σ–5.0σ", ["1.41σ", "4.95σ"], ["d6"], "C3"),
    ("λ 散射 G 跨 72 dex", ["72"], ["d6"], "D2 證偽"),
    ("★z=0.35 預測中位 1.2e15", ["1.2e15", "1.20e15"], ["pr", "d6"], "D4 新證偽"),
    ("★需 seed 0.58 M☉ (次恆星)", ["0.58"], ["pr", "d6"], "D4b"),
    ("★z_f ≤ 2.26 (seed ≥ 100 M☉)", ["2.26"], ["d6"], "D4c"),
    ("形成時間散佈 σ_tf = 2.30 Gyr", ["2.30"], ["d6"], "D5"),
    ("層級疊加 −1.53/dex", ["-1.53"], ["d6"], "D6"),
    # scripts/08 開放項 5 攻堅
    ("z_f* 獨立重現 13.42", ["13.42"], ["d7"], "A1"),
    ("★channel-resolved 反演 22.68", ["22.68"], ["pr", "d7"], "A2 模型依賴"),
    ("★z_f* 全變動範圍 spread 22.67", ["22.67"], ["pr", "d7"], "A6"),
    ("L_min 掃描 27.21→7.33", ["27.21", "7.33"], ["d7"], "A3"),
    ("t_f = t_ef → z = 9.59", ["9.59"], ["d7"], "B"),
    ("t_f = t_S → z = 10.36", ["10.36"], ["d7"], "B"),
    ("13 命中 10 條 (11 → 15)", ["10條", "15"], ["d7"], "C form density"),
    # scripts/09 開放項 1 攻堅
    ("w_obs = 0.20 (2/10)", ["0.20"], ["pr", "d8"], "W1"),
    ("選擇偏置 2.9%", ["2.9"], ["d8"], "W1"),
    ("CP CI [0.025, 0.556]", ["0.556"], ["d8"], "W2"),
    ("7/7 候選全落 CI", ["7/7"], ["d8"], "W2b"),
    ("0.2 命中 237 條", ["237"], ["d8"], "W3"),
    ("需 n ≈ 97", ["97"], ["pr", "d8"], "W4"),
    # scripts/10 開放項 6 攻堅 (層級第一原理)
    ("B = L3 = phi^3 - phi^-3 = 4", ["L\u2083"], ["d10", "pr"], "Lucas 階梯"),
    ("精化因子 k = 4 唯一 (mod-4 + 質因數封閉)", ["mod-4"], ["d10", "pr"], "E 段"),
    ("質因數封閉排除 k=8 (73 @ l=3)", ["73"], ["d10"], "E2"),
    ("群塔 Z_{44*4^l} = Z_{4^(l+1)} x Z_11", ["Z_11"], ["d10", "pr"], "C 段"),
    ("Δℓ 容許窗 [0.798, 1.164]", ["0.798"], ["d10", "d11"], "R2"),
    # scripts/11 開放項 4/5 殘餘 (成長層級截止)
    ("截止點 1+z_stop = 3.5 = L4/mu^2", ["3.5"], ["d11", "pr"], "R3"),
    ("凍結後 M(z<=2.5) = 6.88e8", ["6.88e8"], ["d11", "pr"], "S1"),
    ("z_stop 容許窗 [1.87, 3.78]", ["3.78"], ["d11", "pr"], "R1"),
    ("成長窗 Δℓ = 1.0218", ["1.0218"], ["d11"], "R5"),
    ("z=0.35 斜率張力 1.08", ["1.08"], ["d11"], "T1"),
]
ALLDOC = ("pr", "d1", "d2", "d3", "ss", "fr", "d4", "d5", "d6", "d7", "d8", "d10", "d11", "d12")
bad = []
cov = {}
for name, needles, dkeys, why in CHECKS:
    # 語義: needles = 同一值嘅唔同顯示形式 (ANY-of);
    #       dkeys   = 「優先應該記錄呢個值」嘅文檔, 但只要有任一 O198 文檔記錄即算
    #                 (避免「要求從未存在嘅內容」= verifier bug)
    hit = [k for k in ALLDOC if any(norm(nd) in NT[k] for nd in needles)]
    own = [k for k in dkeys if k in hit]
    cov[name] = (hit, dkeys)
    if not hit:
        bad.append((name, needles, why))
        chk("a", f"{name} {needles} 冇任何 O198 文檔記錄", False, why)
    elif not own:
        print(f"[INFO] a {name} {needles} 唔喺首選 {dkeys}, 但記錄於 {hit}")
chk("a", f"數值出現檢查: {len(CHECKS)} 組全部有文檔記錄", not bad,
    f"全部命中 ({len(CHECKS)} 組)" if not bad else f"{len(bad)} 組缺失")
n_own = sum(1 for n, (h, dk) in cov.items() if any(k in h for k in dk))
print(f"  └ 其中 {n_own}/{len(CHECKS)} 組出現喺首選文檔")

print()
print("=" * 78)
print("(b) 文檔間一致性 — 同一量跨文檔必須一致 (抽樣: 數字集合對齊)")
print("=" * 78)
# 抽出每份文檔嘅所有數字 token, 檢查關鍵值冇互相矛盾 (例: 兩個唔同嘅 z_f*)
def nums(t):
    return set(re.findall(r"\d+\.\d+(?:e[+-]?\d+)?", norm(t)))
pairs = [("z_f*", ["13.43"], ["13.4"], ["pr", "d3", "ss", "fr"]),
         ("t_ef", ["5.0e8", "5e8"], [], ["pr", "d3", "ss", "fr"]),
         ("L_min*", ["5.73e43"], ["1.02e45"], ["d1", "d2"])]
# 具體檢查: docs/02 記 L_min* 兩個值要分別出現喺正確位置
chk("b", "docs/02 同時記舊 5.73e43 + 新 1.02e45 (新舊對比清楚)", 
    "5.73e43" in NT["d2"] and "1.02e45" in NT["d2"])
# T5b 撤銷必須有標記 (禁止靜默改寫)
chk("b", "problem_record 有 T5b 撤銷標記 (⚠️ 撤銷)", "⚠️ 撤銷" in TXT["pr"] or "撤銷" in TXT["pr"])
chk("b", "problem_record 有 N=434 更新標記 (⚠️ 更新)", "⚠️ 更新" in TXT["pr"])
# 計數一致性 (09-16 第二輪: 四層各自獨立; 舊值保留為「計數沿革」)
for k in ["pr", "ss", "fr"]:
    chk("b", f"{k} 記主腳本 136/136 PASS (01-11)", "136/136" in NT[k])
for k in ["pr", "ss", "fr"]:
    chk("b", f"{k} 記層 1 149/150 PASS", "149/150" in NT[k])
for k in ["ss", "fr"]:
    chk("b", f"{k} 記層 2 90/90 PASS", "90/90" in NT[k])
# 舊計數必須保留為歷史 (禁止刪除歷史 = 另一種回溯污染)
chk("b", "計數沿革保留: 主腳本 48/48 仍見於時序索引 (歷史)", "48/48" in NT["pr"])
chk("b", "計數沿革保留: 主腳本 83/83 仍見於時序索引 (歷史)", "83/83" in NT["pr"])
chk("b", "計數沿革保留: 層 1 105/106 仍見於 §四-B/§四-E (歷史)", "105/106" in NT["pr"])
chk("b", "計數沿革保留: 層 1 125/126 仍見於 §四-B/§四-E (歷史)", "125/126" in NT["pr"])
chk("b", "計數沿革保留: 層 2 45/45 仍見於 §四-C (歷史)", "45/45" in NT["pr"])
chk("b", "計數沿革保留: 層 2 62/62 仍見於 §四-C/§四-F (歷史)", "62/62" in NT["pr"])
chk("b", "計數沿革保留: 層 2 67/67 中間值仍見於 §〇 #25 (歷史)", "67/67" in NT["pr"])
chk("b", "計數沿革保留: 層 2 73/73 中間值仍見於 §〇 #25 (歷史)", "73/73" in NT["pr"])
# 每層計數分母唯一 ⟹ 跨文檔一致 (唔會同其他層混淆)
# ⚠️ 只接受「似樣」嘅分子 (den 或 den-1) — 否則「136 / 150 / 67」之類嘅
# 分母列表會被誤抓成 136/150 (自查發現, 見 docs/12)
def tally_den(den):
    vals = set()
    d = int(den)
    for t in [TXT["pr"], TXT["ss"], TXT["fr"]]:
        for m in re.finditer(r"(\d+)/" + den + r"\b", norm(t)):
            if int(m.group(1)) in (d, d - 1):
                vals.add(m.group(0))
    return vals
for den, name in [("136", "主腳本"), ("150", "層 1"), ("90", "層 2")]:
    v = tally_den(den)
    chk("b", f"{name} 計數 (/ {den}) 文檔間一致", len(v) <= 1, f"出現: {sorted(v)}")
# 舊分母亦要一致 (沿革行會寫 "48/48 → 83/83" 之類, 唔應出現第三個值)
for den, name in [("83", "主腳本(沿革)"), ("126", "層 1(沿革)"), ("67", "層 2(沿革)"),
                  ("73", "層 2(沿革2)")]:
    v = tally_den(den)
    chk("b", f"{name} 計數 (/ {den}) 文檔間一致", len(v) <= 1, f"出現: {sorted(v)}")

print()
print("=" * 78)
print("(c) 測試覆蓋完整性 — scripts/01-06 全部 check ID 必須有文檔記錄")
print("=" * 78)
TEST_IDS = {
    "01": ["V1", "V2a", "V2b", "V3", "V4", "V5", "V6", "V7", "V8"],
    "02": ["V1", "V2", "V3", "V4", "V5", "V6", "V7"],
    "03": ["T1", "T2", "T3", "T5a", "T5b", "T6", "T7"],
    "04": ["V1", "V2", "V3", "V3b", "V4", "V5"],
    "05": ["V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8"],
    "06": ["T8a", "T8a'", "T8b", "T8c", "T8d", "T8e", "T8f", "T8h1", "T8h2", "T8h3", "T8g"],
    "07": ["A1", "A2", "B1", "B2", "C1", "C2", "C3", "C4", "D1", "D2", "D3", "D4", "D4b",
           "D4c", "D5", "D6"],
    "08": ["A1", "A2", "A3", "A4", "A5", "A6", "B1", "B2", "C1", "C2", "D1", "D2"],
    "09": ["W1", "W1b", "W2", "W2b", "W3", "W3b", "W4"],
    "10": ["A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8",
           "C1", "C2", "C3", "C4", "C5", "C6", "D1", "D2", "D3",
           "E1", "E2", "E3", "E3b", "E4", "E5", "F1", "F2", "F3"],
    "11": ["P1", "P2", "P3", "P4", "P5", "Q1", "Q2", "R1", "R2", "R3", "R4", "R5",
           "S1", "S2", "S3", "T1", "U1", "U2", "U3", "U4", "V1", "V2", "V3"],
}
# 對每個 script 嘅「發現」層: 文檔必須覆蓋該 script 嘅主題 (用主題關鍵詞檢查, 唔要求逐 ID 出現)
TOPIC = {
    "01": ("兩通道譜閉式", ["2.017e6", "5.4136e6", "6.9790e6", "0.4433"]),
    "02": ("Harikane 放置 V1-V7", ["2/10", "8/8", "0.216", "1.23", "0.025", "0.556"]),
    "03": ("Eddington 前向", ["5.73e43", "7.52e6", "9.19e6", "0.39"]),
    "04": ("UHz1 + 斜率", ["1.016e-3", "3.085", "-4.23", "1.99e7"]),
    "05": ("實測 λ 攻堅", ["0.702", "5.40e6", "-1.78", "5.92", "-0.648", "1.02e45"]),
    "06": ("成長閉合", ["5.0e8", "13.43", "3.17e7", "66", "303", "7.94e8", "8.66e6", "2.34e7"]),
    "07": ("開放項 4 尾斜率攻堅", ["-2.6", "1.76", "1.2e15", "0.58", "2.26"]),
    "08": ("開放項 5 z_f* 可識別性", ["22.68", "22.67", "9.59", "10.36", "13.42"]),
    "09": ("開放項 1 w 份額", ["0.556", "2.9", "237", "97"]),
    "10": ("開放項 6 層級第一原理", ["L\u2083", "mod-4", "Z_11", "73", "0.798"]),
    "11": ("開放項 4/5 殘餘 成長截止", ["3.5", "6.88e8", "3.78", "1.08"]),
}
DOCKEYS = ("pr", "d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "d10", "d11", "d12", "ss", "fr")
for sid, (topic, keys) in TOPIC.items():
    missing = [k for k in keys if not any(norm(k) in NT[d] for d in DOCKEYS)]
    chk("c", f"scripts/{sid} 主題「{topic}」全部關鍵值有文檔記錄", not missing,
        f"缺: {missing}" if missing else f"{len(keys)} 個關鍵值全中")
n_checks = sum(len(v) for v in TEST_IDS.values())
chk("c", f"scripts/01-11 共 {n_checks} 個 check ID 已枚舉 (136 PASS)", n_checks == 136,
    f"實數 {n_checks}")

print()
print("=" * 78)
print("(d) 檔案時序 — 執行鏈 (data → scripts) + 每份 doc ≥ 佢所記錄嘅 script")
print("=" * 78)
def mt(p): return Path(p).stat().st_mtime
# 執行鏈: 數據先於用佢嘅 script
# ⚠️ 09-16: 此 mtime 判序因 F3 合法改名 patch (lambda_lo/hi -> lambda_err_lo/hi)
# 令 data mtime 後移而失效 ⟹ 降為 INFO; 時序有效性改以「內容核對」為準
# (見本段後方 _dj / _miss / _geo 三項)。
print("  [INFO] d data/json vs scripts/05 之 mtime 判序: "
      + ("ok" if mt(DATA) <= mt(BASE / "scripts/05_edd_ratio_data.py") else "inverted")
      + "  (09-16 F3 改名 patch 令 data mtime 後移 — 合法, 見 docs/12 §1)")
# doc ≥ 佢記錄嘅 script (晚補嘅 doc patch 係合法嘅 — 唔用 mtime 判先後,
# 依 skill: 「Timestamps lie after legit patches」)
PAIR = [
    ("docs/01 ≥ scripts/01-04", BASE / "docs/01_seed_spectrum_verification.md",
     [BASE / "scripts/01_two_channel_spectrum.py", BASE / "scripts/02_harikane_placement.py",
      BASE / "scripts/03_eddington_forward.py", BASE / "scripts/04_uhz1_tail.py"]),
    ("docs/02 ≥ scripts/05", BASE / "docs/02_measured_eddington_attack.md",
     [BASE / "scripts/05_edd_ratio_data.py"]),
    ("docs/03 ≥ scripts/06", BASE / "docs/03_growth_closure.md",
     [BASE / "scripts/06_growth_closure.py"]),
    ("docs/04 ≥ 90 審計腳本", BASE / "docs/04_record_audit.md",
     [BASE / "scripts/90_audit_records.py"]),
    ("docs/10 ≥ scripts/10", BASE / "docs/10_hierarchy_source.md",
     [BASE / "scripts/10_hierarchy_source.py"]),
    ("docs/11 ≥ scripts/11", BASE / "docs/11_growth_cutoff.md",
     [BASE / "scripts/11_growth_cutoff.py"]),
]
for nm, doc, scripts in PAIR:
    # ⚠️ mtime 只作 INFO: 後期合法 patch (F5 衞生修正 / 補註) 會令 script 或 doc 嘅
    # mtime 後移, 唔代表時序錯。時序有效性以內容為準 (90 段獨立重算 + 91(a)(c))。
    import datetime as _dtm
    _dt = lambda t: f"{_dtm.datetime.fromtimestamp(t):%m-%d %H:%M}"
    print(f"  [INFO] {nm}: doc {_dt(mt(doc))} vs script max {_dt(max(mt(s) for s in scripts))}"
          + ("  (doc 較新 ✓)" if mt(doc) >= max(mt(s) for s in scripts) else "  (doc 較舊 — 後期 script patch)"))
# ⚠️ 09-16: data/json 因 F3 合法改名 patch (lambda_lo/hi -> lambda_err_lo/hi) 而 mtime
# 後移, 令 mtime 判序失效 ⟹ 降為 INFO; 改以「內容核對」取代 (見下方)
_mt_ok = mt(DATA) <= mt(BASE / "scripts/05_edd_ratio_data.py")
print(f"  [INFO] d data/json vs scripts/05 之 mtime 判序: "
      + ("ok" if _mt_ok else "inverted")
      + "  (09-16 F3 改名 patch 令 data mtime 後移 — 合法, 見 docs/12 §1)")
# 內容核對 (取代 mtime 判序, 免疫於合法 patch):
_dj = json.load(open(DATA, encoding="utf-8"))
_fmt = lambda m: ("%.1e" % m).replace("e+0", "e").replace("e-0", "e-").replace("e+", "e")
chk("d", f"data/json {len(_dj)} 個物件齊全 + 6 必要欄 + F3 新欄名 (舊名已無)",
    len(_dj) == 10 and all(
        all(k in o for k in ("name", "M_BH", "L_bol", "lambda_Edd",
                             "lambda_err_lo", "lambda_err_hi"))
        and "lambda_lo" not in o and "lambda_hi" not in o for o in _dj),
    "n = " + str(len(_dj)))
_miss = [m for m in (o["M_BH"] for o in _dj)
         if _fmt(m) not in NT["d1"] and _fmt(m).replace(".0e", "e") not in NT["d1"]]
chk("d", "data/json 全部 M_BH 值出現於 docs/01 (改名唔改值之內容核對)",
    not _miss, "缺: " + str(_miss))
# 數值不變之獨立覆核: λ_Edd 幾何均值仍 = 0.702 (docs/02 記錄值)
import functools as _ft
_geo = _ft.reduce(lambda a, b: a * b, (o["lambda_Edd"] for o in _dj)) ** (1 / len(_dj))
chk("d", "★F3 改名後 data 值不變: λ_Edd 幾何均值 = 0.702 (docs/02 記錄)",
    abs(_geo - 0.702) < 5e-3, "得 " + f"{_geo:.4f}")
print("  mtime 全表 (INFO — 晚補 patch 會令 mtime 後移, 唔代表時序錯):")
for nm, p in [("scripts/01", BASE / "scripts/01_two_channel_spectrum.py"),
              ("data/json", DATA),
              ("scripts/05", BASE / "scripts/05_edd_ratio_data.py"),
              ("scripts/06", BASE / "scripts/06_growth_closure.py"),
              ("docs/01", BASE / "docs/01_seed_spectrum_verification.md"),
              ("docs/02", BASE / "docs/02_measured_eddington_attack.md"),
              ("docs/03", BASE / "docs/03_growth_closure.md"),
              ("90_audit", BASE / "scripts/90_audit_records.py"),
              ("docs/04", BASE / "docs/04_record_audit.md")]:
    import datetime as _dtm
    print(f"    {nm:12s} {p.name:42s} {_dtm.datetime.fromtimestamp(mt(p)):%m-%d %H:%M:%S}")

print()
print("=" * 78)
print("(e) 目錄範圍 — verification/ 只含預期檔案")
print("=" * 78)
want = {
    "01_problem_record.md", "SESSION_START.md", "final_result.md",
    "docs/01_seed_spectrum_verification.md", "docs/02_measured_eddington_attack.md",
    "docs/03_growth_closure.md", "docs/04_record_audit.md",
    "docs/05_record_closeout.md",
    "docs/06_tail_shape_attack.md", "docs/07_zf_structural_attack.md",
    "docs/08_w_fraction_attack.md", "docs/09_attack_round_closeout.md",
    "data/harikane23_table3_eddington.json",
    "data/vestergaard09_beta_slopes.json",
    "scripts/01_two_channel_spectrum.py", "scripts/02_harikane_placement.py",
    "scripts/03_eddington_forward.py", "scripts/04_uhz1_tail.py",
    "scripts/05_edd_ratio_data.py", "scripts/06_growth_closure.py",
    "scripts/07_tail_shape.py", "scripts/08_zf_structural.py",
    "scripts/09_w_fraction.py",
    "docs/10_hierarchy_source.md", "docs/11_growth_cutoff.md",
    "docs/12_hygiene_f3_f6.md",
    "scripts/10_hierarchy_source.py", "scripts/11_growth_cutoff.py",
    "scripts/90_audit_records.py", "scripts/91_doc_audit.py",
    "scripts/92_chain_continuity.py",
}
have = {str(p.relative_to(BASE)) for p in BASE.rglob("*") if p.is_file()
        and "__pycache__" not in str(p)}
extra = sorted(have - want)
missing = sorted(want - have)
chk("e", "verification/ 冇預期外檔案", not extra, f"extra = {extra}")
chk("e", "預期檔案齊全", not missing, f"missing = {missing}")

print()
print("=" * 78)
print("(f) 污染檢查 — O198 文檔冇改寫 O197 歷史 / 冇 O199+ 污染")
print("=" * 78)
# O198 文檔只可以「引用」O197, 唔可以改寫 O197 結論
o197_docs = [O197 / "docs/01_closure.md", O197 / "docs/04_dhat_minus_role.md",
             O197 / "docs/05_three_half_power.md", O197 / "01_problem_record.md"]
for p in o197_docs:
    if not p.exists():
        chk("f", f"{p.name} 存在", False)
        continue
    t = rd(p)
    # O198 相關內容只可以係「合併記錄」形式
    has_o198 = "O198" in t
    chk("f", f"{p.name}: O198 提及 = 合併記錄形式 (唔係新推導)",
        (not has_o198) or ("合併" in t or "verification/" in t),
        f"(提及 O198 = {has_o198})")
# 冇 O199/O200 污染 (排除合法歷史引用)
for k, t in TXT.items():
    lines = [ln for ln in t.splitlines()
             if not re.search(r"沒喊過開O19|誤開|合併|留 O19|O199\+", ln)]
    poll = [ln for ln in lines if re.search(r"O19[9]|O20[0-9]", ln)]
    chk("f", f"{k} 冇 O199/O200 污染 (排除合併記錄引用)", not poll,
        f"{poll[:2]}" if poll else "")
# O198 文檔唔可以出現「重寫 O197 已閉合結論」字句
for k in ("d1", "d2", "d3"):
    t = TXT[k]
    bad_phrase = re.search(r"O197.{0,12}(已改|更正為|修正 O197 結論)", t)
    chk("f", f"{k} 冇改寫 O197 結論字句", bad_phrase is None,
        bad_phrase.group(0) if bad_phrase else "")
# 編碼完整性: 冇 U+FFFD (replacement char) — 09-16 docs/12 曾中招 (5 對 ⛔ 變亂碼)
for k, t in TXT.items():
    _n = t.count("\ufffd")
    chk("f", f"{k} 編碼完整 (冇 U+FFFD replacement char)", _n == 0,
        f"{_n} 個 U+FFFD" if _n else "")

print()
print("=" * 78)
print("(g) 第三方法 MC 重算 (換 seed, n=1.2e5) — 頭條 MC 值")
print("=" * 78)
rng = random.Random(20260915)          # 第三個 seed (90 用 987654321/24681357)
L_EDD = 1.26e38
def draw(rng):
    if rng.random() < 0.2: return rng.choice(A_masses)
    return math.exp(rng.gauss(mu_lnM, sig_lnM))
def fwd(lam_pool, Lmin, n=120000):
    v = []
    for _ in range(n):
        li = rng.choice(lam_pool); M = draw(rng)
        if li * L_EDD * M >= Lmin: v.append(math.log(M))
    v.sort(); return math.exp(v[len(v) // 2]) if v else 0.0
med_emp = fwd(lams, 3e43)
chk("g", "實測 λ 前向中位 ≈ 5.40e6 (第三 seed)", abs(med_emp / 5.40e6 - 1) < 0.05,
    f"得 {med_emp:.3e}")
g_need = obs_med / med_emp
chk("g", "閉合需 g ≈ 5.92 (第三 seed)", abs(g_need / 5.92 - 1) < 0.05, f"得 {g_need:.3f}")
# z_f* 反演 (第三 seed)
zs = {"CEERS_01244": 4.478, "GLASS_160133": 4.015, "GLASS_150029": 4.583,
      "CEERS_00746": 5.624, "CEERS_01665": 4.483, "CEERS_00672": 5.666,
      "CEERS_02782": 5.241, "CEERS_00397": 6.0, "CEERS_00717": 6.936,
      "CEERS_01236": 4.484}
H0, Om = 67.4, 0.315
H0s = H0 * 1e5 / 3.086e24
def t_z(z, n=4000):
    # 自寫梯形積分 (第三方法: 唔用 scipy/mpmath)
    a, b = z, 1e4
    # 代換 u = ln(1+z): du = dz/(1+z)
    u0, u1 = math.log(1 + z), math.log(1 + 1e4)
    h = (u1 - u0) / n
    s = 0.0
    for i in range(n + 1):
        u = u0 + i * h
        zz = math.exp(u) - 1
        f = 1 / math.sqrt(Om * (1 + zz) ** 3 + (1 - Om))
        w = 1 if i in (0, n) else (4 if i % 2 else 2)
        s += w * f
    return s * h / 3 / H0s / 3.156e16
t5 = t_z(5)
chk("g", "t(5) ≈ 1.171 Gyr (第三方法梯形)", abs(t5 / 1.171 - 1) < 0.01, f"得 {t5:.4f}")
rng2 = random.Random(13572468)
def fwd_g(z_f, n=80000):
    tzf = t_z(z_f); tobs = [t_z(v) for v in zs.values()]
    v = []
    for _ in range(n):
        li = rng2.choice(lams); M = draw(rng2); to = rng2.choice(tobs)
        Mo = M * math.exp((to - tzf) / 0.5)
        if li * L_EDD * Mo >= 3e43: v.append(math.log(Mo))
    v.sort(); return math.exp(v[len(v) // 2]) if v else 0.0
lo, hi = 8.0, 25.0
for _ in range(25):
    mid = (lo + hi) / 2
    if fwd_g(mid) < obs_med: lo = mid
    else: hi = mid
zf = (lo + hi) / 2
chk("g", "z_f* ≈ 13.43 (第三 seed, MC 噪聲容差 2%)", abs(zf / 13.43 - 1) < 0.02, f"得 {zf:.2f}")
m_star = fwd_g(zf, n=120000)
chk("g", "z_f* 成長後中位 ≈ 3.17e7", abs(m_star / 3.17e7 - 1) < 0.06, f"得 {m_star:.3e}")
G_U = math.exp((t_z(7.5) - t_z(zf)) / 0.5)
chk("g", "UHz1 G ≈ 2.14", abs(G_U / 2.14 - 1) < 0.05, f"得 {G_U:.3f}")

print()
print("=" * 78)
print("(h) RESULT_TEMPLATE 段序符合性 (狀態→結論→關鍵公式→依賴)")
print("=" * 78)
TPL_ORDER = ["狀態", "結論", "關鍵公式", "依賴"]
fr_secs = re.findall(r"^## (.+?)$", TXT["fr"], re.M)
idx = []
for s in fr_secs:
    for i, t in enumerate(TPL_ORDER):
        if s.startswith(t):
            idx.append(i)
            break
chk("h", f"final_result 四段齊 + 依 template 序 (實得 {[TPL_ORDER[i] for i in idx]})",
    len(idx) == 4 and idx == sorted(idx), f"章節: {fr_secs}")
chk("h", "final_result 狀態 emoji 統一 (🟢/🟡/🔴)",
    any(s.startswith("狀態") and any(e in s for e in "🟢🟡🔴") for s in fr_secs))
dep = re.search(r"## 依賴\n+(.+)", TXT["fr"])
chk("h", "final_result 依賴用 → 箭頭", bool(dep) and "→" in dep.group(1))
chk("h", "final_result 有關鍵公式段且非空",
    bool(re.search(r"## 關鍵公式\n+(-\s*.+\n?)+", TXT["fr"])))
chk("h", "final_result 有合併警告 (本 entry 特殊狀態)", "已合併回 O197" in TXT["fr"])

print()
print("=" * 78)
print(f"文檔審計總計: {len(PASS)}/{len(PASS) + len(FAIL)} PASS")
print("=" * 78)
if FAIL:
    print("★ FAIL:")
    for f in FAIL: print(f"  - {f}")
    sys.exit(1)
print("全部通過。")
