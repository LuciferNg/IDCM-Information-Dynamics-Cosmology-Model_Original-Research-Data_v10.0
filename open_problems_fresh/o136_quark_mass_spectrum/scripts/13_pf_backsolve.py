#!/usr/bin/env python3
"""
O136 — Script 13: 決定性檢驗 — 從質量比反解 P_f 比值
================================================================
邏輯:
  若 m_f = M₀·γ_n·P_f 為真結構, 則對任意兩粒子:
    P_f1/P_f2 = (m_1/m_2) / (γ_n1/γ_n2)
  這給出 P_f 比值的「實驗值」。
  然後檢驗: 這些實驗比值是否 = 字典值比值 (3.6, 15.5, 37, 33, 13, 44)?

  若一致 → 字典 P_f 是真結構
  若不一致 → 字典 P_f 是近似, 需修正

使用方案無關比值 (同扇區):
  夸克-夸克: 全 MS-bar(2 GeV)  → c/s, b/s, b/c, u/d, u/s, d/s
  輕子-輕子: 全 pole mass       → μ/e, τ/e, τ/μ
"""
import math, json
from pathlib import Path
from fractions import Fraction

phi = (1 + math.sqrt(5))/2
L = [int(round(phi**n + (-1)**n * phi**(-n))) for n in range(15)]
F = [0, 1]
for n in range(2, 12): F.append(F[n-1] + F[n-2])
Nd, B = 44, 4
M0 = 27.900915
gamma = lambda n: 4 * math.sin(n * math.pi / 88)**2

print("=" * 84)
print("O136 Script 13: 決定性檢驗 — 從質量比反解 P_f")
print("=" * 84)

# 字典值
dict_Pf = {
    "e":  (1,  Fraction(18,5),  0.510999),
    "mu": (7,  Fraction(31,2),  105.658),
    "tau":(20, Fraction(37,1),  1776.86),
    "u":  (1,  Fraction(31,2),  2.16),
    "d":  (1,  Fraction(33,1),  4.67),
    "s":  (14, Fraction(18,5),  93.0),
    "c":  (34, Fraction(13,1),  1270.0),
    "b":  (33, Fraction(44,1),  4180.0),
}

# ═══ 1. 夸克-夸克比值 (全 MS-bar 2 GeV, t 除外) ═══════
print(f"\n{'─'*84}")
print("1. 夸克-夸克比值反解 (全 MS-bar 2 GeV, 方案一致)")
print(f"{'─'*84}")

q_pairs = [
    ("c/s", "c", "s"),
    ("b/s", "b", "s"),
    ("b/c", "b", "c"),
    ("u/d", "u", "d"),
    ("u/s", "u", "s"),
    ("d/s", "d", "s"),
]

print(f"\n{'比值':>6} {'PDG 比':>12} {'γ 比':>12} {'P_f 比 (實驗)':>14} {'P_f 比 (字典)':>14} {'偏差':>9}")
print("-" * 76)
q_results = {}
for label, p1, p2 in q_pairs:
    n1, pf1, m1 = dict_Pf[p1]
    n2, pf2, m2 = dict_Pf[p2]
    obs = m1/m2
    gratio = gamma(n1)/gamma(n2)
    pf_exp = obs/gratio
    pf_dict = float(pf1)/float(pf2)
    dev = (pf_dict - pf_exp)/pf_exp*100
    q_results[label] = {"obs": obs, "gratio": gratio, "pf_exp": pf_exp, "pf_dict": pf_dict, "dev": dev}
    print(f"{label:>6} {obs:>12.5f} {gratio:>12.5f} {pf_exp:>14.6f} {pf_dict:>14.6f} {dev:>8.3f}%")

# ═══ 2. 輕子-輕子比值 (全 pole mass) ═════════════════
print(f"\n{'─'*84}")
print("2. 輕子-輕子比值反解 (全 pole mass, 方案一致)")
print(f"{'─'*84}")

l_pairs = [("mu/e", "mu", "e"), ("tau/e", "tau", "e"), ("tau/mu", "tau", "mu")]
print(f"\n{'比值':>6} {'PDG 比':>12} {'γ 比':>12} {'P_f 比 (實驗)':>14} {'P_f 比 (字典)':>14} {'偏差':>9}")
print("-" * 76)
l_results = {}
for label, p1, p2 in l_pairs:
    n1, pf1, m1 = dict_Pf[p1]
    n2, pf2, m2 = dict_Pf[p2]
    obs = m1/m2
    gratio = gamma(n1)/gamma(n2)
    pf_exp = obs/gratio
    pf_dict = float(pf1)/float(pf2)
    dev = (pf_dict - pf_exp)/pf_exp*100
    l_results[label] = {"obs": obs, "gratio": gratio, "pf_exp": pf_exp, "pf_dict": pf_dict, "dev": dev}
    print(f"{label:>6} {obs:>12.5f} {gratio:>12.5f} {pf_exp:>14.6f} {pf_dict:>14.6f} {dev:>8.3f}%")

# ═══ 3. 從夸克比值反解絕對 P_f (以 c 為參考) ═════════
print(f"\n{'─'*84}")
print("3. 從夸克比值反解絕對 P_f (以 b 為參考, 用 b/c 同 b/s)")
print(f"{'─'*84}")

# 用 m_b/m_c 和 m_b/m_s 反解 P_f(c), P_f(s), 假設 P_f(b) = 44
n_b, pf_b, m_b = dict_Pf["b"]
print(f"\n假設 P_f(b) = N_d = 44 (待檢驗)")
print(f"\n{'粒子':>5} {'PDG 質量':>12} {'γ_n':>10} {'P_f 反解':>12} {'字典值':>10} {'偏差':>9} {'結構候選':>14}")
print("-" * 78)

pf_solved = {}
for p in ["c", "s", "u", "d", "tau", "mu", "e"]:
    n, pf_dict, m = dict_Pf[p]
    # P_f(p)/P_f(b) = (m_p/m_b)/(γ_n/γ_33)
    ratio = (m/m_b)/(gamma(n)/gamma(n_b))
    pf_solved_p = ratio * 44.0
    pf_solved[p] = pf_solved_p
    dev = (float(pf_dict) - pf_solved_p)/pf_solved_p*100
    print(f"{p:>5} {m:>12.5f} {gamma(n):>10.6f} {pf_solved_p:>12.6f} {float(pf_dict):>10.4f} {dev:>8.3f}%")

print(f"\n★ 若 P_f(b) = 44 正確, 反解值應等於字典值")
print(f"★ 反解偏差 < 0.1% 的粒子 = P_f 字典值正確")

# ═══ 4. 關鍵檢驗: 反解 P_f 是否有結構 ════════════════
print(f"\n{'─'*84}")
print("4. 關鍵檢驗: 反解 P_f 是否為結構數?")
print(f"{'─'*84}")

struct_cands = {
    "L₆/F₅ = 18/5": 18/5,
    "(N_d−F₇)/2 = 31/2": 31/2,
    "N_d−L₄ = 37": 37.0,
    "N_d−L₅ = 33": 33.0,
    "F₇ = 13": 13.0,
    "N_d = 44": 44.0,
    "40/11": 40/11,
    "L₇ = 29": 29.0,
    "L₆ = 18": 18.0,
    "B×F₅ = 20": 20.0,
    "L₅ = 11": 11.0,
    "E_proj = 28.5": 28.5,
}

print(f"\n{'粒子':>5} {'反解 P_f':>12} {'最佳結構匹配':>22} {'值':>10} {'偏差':>9}")
print("-" * 66)
for p, val in pf_solved.items():
    best = min(struct_cands.items(), key=lambda kv: abs(kv[1]-val)/val)
    dev = (best[1]-val)/val*100
    print(f"{p:>5} {val:>12.6f} {best[0]:>22} {best[1]:>10.4f} {dev:>8.3f}%")

# ═══ 5. 結論 ════════════════════════════════════════
print(f"\n{'='*84}")
print("結論")
print(f"{'='*84}")

q_devs = [abs(r["dev"]) for r in q_results.values()]
l_devs = [abs(r["dev"]) for r in l_results.values()]
print(f"""
夸克-夸克 P_f 比偏差: {['%.3f%%' % d for d in q_devs]}
  平均 |偏差| = {sum(q_devs)/len(q_devs):.3f}%
  最大 |偏差| = {max(q_devs):.3f}%

輕子-輕子 P_f 比偏差: {['%.3f%%' % d for d in l_devs]}
  平均 |偏差| = {sum(l_devs)/len(l_devs):.3f}%
  最大 |偏差| = {max(l_devs):.3f}%
""")

# 判斷
if max(q_devs) < 0.5 and max(l_devs) < 0.5:
    print("✅ 字典 P_f 在 0.5% 內一致 → 真結構")
else:
    print("🟡 字典 P_f 有 >0.5% 偏差 → 部分近似")

print(f"""
關鍵發現:
  1. 輕子 P_f 比: μ/e 偏差 {l_results['mu/e']['dev']:.3f}%, τ/e {l_results['tau/e']['dev']:.3f}%
     → 輕子字典 (3.6, 15.5, 37) 高度一致
  2. 夸克 P_f 比: b/c 偏差 {q_results['b/c']['dev']:.3f}% (極佳)
     → b = N_d = 44, c = F₇ = 13 互為驗證
  3. c/s 偏差 {q_results['c/s']['dev']:.3f}% → s 的 P_f 應為 {pf_solved['s']:.4f} 而非 3.6
  4. u/d 偏差 {q_results['u/d']['dev']:.3f}%
""")

# 保存
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "13_pf_backsolve.json", "w") as f:
    json.dump({
        "quark_pairs": q_results,
        "lepton_pairs": l_results,
        "pf_solved": pf_solved,
        "mean_quark_dev": sum(q_devs)/len(q_devs),
        "mean_lepton_dev": sum(l_devs)/len(l_devs),
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/13_pf_backsolve.json")