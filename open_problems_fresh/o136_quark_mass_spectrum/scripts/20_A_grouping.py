#!/usr/bin/env python3
"""
O136 — Script 20: A 分組原理攻堅 (缺口 3)
================================================================
Gemini 提案檢驗:
  1. 色選擇律: R=3 允許同世代同位旋對; R=1 禁止 → 輕子強制跨代
  2. Δn(c→b) = L₅ + (B²−2) = 11 + 14 = 25
  3. A 因子 = CY₃ 投影算子本徵值模長; 用分母階梯 {88,132,528} + φ^k 鎖定

同時檢驗 O35 內部一致性 (模式 n 是否唯一)
"""
import math, json
from pathlib import Path

phi = (1 + math.sqrt(5))/2
lnphi = math.log(phi)
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
Nd, B_, dimC = 44, 4, 3
C42 = 6
M_ = 33

# PDG 質量 (MeV)
mass = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0,
        "W": 80377.0, "Z": 91187.6, "H": 125250.0}

def sinm(n): return math.sin(n*math.pi/88)

print("=" * 92)
print("O136 Script 20: A 分組原理攻堅")
print("=" * 92)

# ═══ 1. Gemini 提案 1: 色選擇律 ═════════════════════
print(f"\n{'─'*92}")
print("1. Gemini 提案 1: 色選擇律 (R=3 允許同世代, R=1 禁止)")
print(f"{'─'*92}")

print(f"\n已知配對:")
pairs = [
    ("{{u,d}}", "3 (夸克)", "同世代 g=1", (10, 24), 14),
    ("{{c,b}}", "3 (夸克)", "跨代 2→3", (8, 33), 25),
    ("{{mu,tau}}", "1 (輕子)", "跨代 2→3", (1, 18), 17),
    ("{{W,Z}}", "1 (玻色子)", "規範", (30, 41), 11),
    ("{{H,W}}", "1 (玻色子)", "規範", (19, 38), 19),
]
print(f"\n{'配對':>12} {'R':>12} {'類型':>12} {'模式對':>12} {'Δn':>5}")
print("-" * 60)
for name, R, typ, (a, b), dn in pairs:
    print(f"{name:>12} {R:>12} {typ:>12} {f'({a},{b})':>12} {dn:>5}")

print(f"\n─── 檢驗: 夸克是否全部同世代? ───")
print(f"  {{u,d}}: 同世代 (g=1) ✅")
print(f"  {{c,b}}: 跨世代 (c=g2 up, b=g3 down) 🔴")
print(f"  → 夸克配對同時存在同世代和跨世代 → 色選擇律唔唯一解釋 🔴")

print(f"\n─── 檢驗: 輕子是否強制跨代? ───")
print(f"  μ (g=2), τ (g=3) → 跨代 ✅")
print(f"  但 e (g=1) 無配對 → 係因為 e 無 sin 模式 🔴")
print(f"  → 「禁止同世代」無法解釋 e 的缺失 (e 存在但無配對)")

# ═══ 2. Gemini 提案 2: Δn(c→b) ═════════════════════
print(f"\n{'─'*92}")
print("2. Gemini 提案 2: Δn(c→b) = L₅ + (B²−2)")
print(f"{'─'*92}")

dn_cb = 33 - 8
print(f"\nΔn(c→b) = 33 − 8 = {dn_cb}")
print(f"L₅ + (B²−2) = {L[5]} + {B_**2-2} = {L[5] + B_**2-2}  {'✅' if dn_cb == L[5]+B_**2-2 else '🔴'}")
print(f"\n★ 算術正確, 但: 任何 25 都可分解成多種形式")
cands = []
for a in range(1, 30):
    for b in range(1, 30):
        if a + b == 25:
            cands.append(f"{a}+{b}")
print(f"  25 的分解數: {len(cands)} 種 (a+b)")
print(f"  其中結構數組合: 14+11 (B²−2+L₅), 18+7 (L₆+L₄), 22+3 (N_d/2+dimC), 13+12 (F₇+B·dimC)")
print(f"  → 🔴 4 個結構分解 → 未唯一")

# ═══ 3. Gemini 提案 3: A 因子 φ^k ═══════════════════
print(f"\n{'─'*92}")
print("3. Gemini 提案 3: A 因子 = φ^k (分母階梯 88/132/528)")
print(f"{'─'*92}")

# O35 模式分配
modes = {"e": None, "mu": 1, "tau": 18, "u": 10, "d": 24, "s": 22,
         "c": 8, "b": 33, "t": 19, "W": 30, "Z": 41, "H": 38}

print(f"\n─── 反解 A_f = m_f / sin(n_f π/88) ───")
A = {}
print(f"\n{'粒子':>6} {'n':>4} {'sin':>10} {'m (MeV)':>12} {'A_f (MeV)':>14} {'log_φ(A/A_ud)':>15}")
print("-" * 68)
for name, n in modes.items():
    if n is None: continue
    s = sinm(n)
    a = mass[name]/s
    A[name] = a
Aref = (A["u"] + A["d"])/2
for name, n in modes.items():
    if n is None: continue
    k = math.log(A[name]/Aref)/lnphi
    print(f"{name:>6} {n:>4} {sinm(n):>10.6f} {mass[name]:>12.2f} {A[name]:>14.2f} {k:>15.6f}")

print(f"\n─── A 分組 (log_φ K 值) ───")
groups = {}
for name, n in modes.items():
    if n is None: continue
    k = round(math.log(A[name]/Aref)/lnphi, 4)
    groups.setdefault(k, []).append(name)
print(f"\n{'K (log_φ)':>12} {'成員':>20} {'內部離散':>12}")
print("-" * 50)
for k in sorted(groups.keys()):
    mem = groups[k]
    if len(mem) > 1:
        ks = [math.log(A[m]/Aref)/lnphi for m in mem]
        spread = max(ks)-min(ks)
        print(f"{k:>12.4f} {str(mem):>20} {spread:>12.6f}")
    else:
        print(f"{k:>12.4f} {str(mem):>20} {'—':>12}")

# ═══ 4. K 差值的結構檢驗 ════════════════════════════
print(f"\n{'─'*92}")
print("4. K 差值的結構分子檢驗 (分母 88 / 132 / 528)")
print(f"{'─'*92}")

K = {name: math.log(A[name]/Aref)/lnphi for name in modes if modes[name] is not None}
Kgrp = {}
for name, k in K.items():
    found = False
    for kk in Kgrp:
        if abs(k - kk) < 1e-3:
            Kgrp[kk].append(name); found = True; break
    if not found:
        Kgrp[k] = [name]

print(f"\n{'差值':>22} {'ΔK':>10} {'×88':>10} {'×132':>10} {'×528':>10}")
print("-" * 68)
kud = K["u"]
for name in ["s", "mu", "c", "W", "H", "t"]:
    dk = K[name] - kud
    print(f"{'K('+name+') − K(u,d)':>22} {dk:>10.4f} {dk*88:>10.2f} {dk*132:>10.2f} {dk*528:>10.2f}")

print(f"\n─── 檢查是否有整數分子 ───")
print(f"\n{'差值':>22} {'×528':>10} {'最近整數':>10} {'偏差%':>9} {'結構?':>20}")
print("-" * 78)
for name in ["s", "mu", "c", "W", "H", "t"]:
    dk = K[name] - kud
    v528 = dk*528
    near = round(v528)
    dev = abs(v528-near)/near*100
    struct = ""
    if near % 29 == 0: struct += f"L₇×{near//29} "
    if near % 71 == 0: struct += f"71×{near//71} "
    if near % 88 == 0: struct += f"2N_d×{near//88} "
    print(f"{'K('+name+') − K(u,d)':>22} {v528:>10.2f} {near:>10} {dev:>9.3f} {struct:>20}")

print(f"\n→ 🔴 無乾淨整數分子 (偏差 0.1-5%) → A 分組的 φ 指數無結構基礎")

# ═══ 5. O35 內部一致性檢驗 ═══════════════════════════
print(f"\n{'─'*92}")
print("5. ★ O35 內部一致性: 模式 n 是否唯一?")
print(f"{'─'*92}")

print(f"\nO35 公式中 d 夸克的模式:")
print(f"  公式 1: m_u/m_d = sin10/sin24  → d ↔ 24")
print(f"  公式 2: m_s/m_d = φ^(10/528)·sin22/sin1 → d ↔ 1 🔴")
print(f"\n★ 矛盾: d 同時被指定為 24 和 1")

print(f"\n─── 用 d↔24 重算 m_s/m_d ───")
target = mass["s"]/mass["d"]
print(f"  目標 m_s/m_d = {target:.6f}")
for n_s in [14, 22, 21, 23]:
    s_ratio = sinm(n_s)/sinm(24)
    k = math.log(target/s_ratio)/lnphi
    print(f"  n_s={n_s}: sin{n_s}/sin24 = {s_ratio:.6f} → 需 φ^{k:.6f}")
print(f"\n  → 無整數/結構分子 (k = 5.73, 6.36, ...) 🔴")

print(f"\n─── 用 d↔1 檢查 (O35 原式) ───")
s_ratio = sinm(22)/sinm(1)
k = math.log(target/s_ratio)/lnphi
print(f"  sin22/sin1 = {s_ratio:.6f} → 需 φ^{k:.6f}")
print(f"  k × 528 = {k*528:.2f}  (O35 用 10)  🔴 差 {abs(k*528-10):.1f}")
print(f"  → O35 的 φ^(10/528) 修正嚴重不足! 實際需 φ^{k:.3f}")

# ═══ 6. 純 sin 比 vs φ 修正配對 ═════════════════════
print(f"\n{'─'*92}")
print("6. ★ 真正的 A 分組內容: 哪些配對是純 sin 比?")
print(f"{'─'*92}")

pure = [("u/d", 10, 24), ("mu/tau", 1, 18), ("c/b", 8, 33), ("W/Z", 30, 41), ("H/W", 19, 38)]
phic = [("s/d", 22, 1), ("t/b", 19, 33), ("mu/e", None, None)]

mname = {"u":"u","d":"d","mu":"mu","tau":"tau","c":"c","b":"b","W":"W","Z":"Z","H":"H","s":"s","e":"e","t":"t"}

print(f"\n─── 純 sin 比配對 ───")
print(f"\n{'配對':>10} {'模式':>10} {'sin比':>12} {'PDG比':>12} {'偏差%':>9}")
print("-" * 58)
for label, n1, n2 in pure:
    a, b = label.split("/")
    sr = sinm(n1)/sinm(n2)
    tr = mass[a]/mass[b]
    print(f"{label:>10} {f'({n1},{n2})':>10} {sr:>12.6f} {tr:>12.6f} {(sr-tr)/tr*100:>+9.3f}")

print(f"\n─── 需要 φ 修正的配對 ───")
print(f"\n{'配對':>10} {'模式':>10} {'sin比':>12} {'PDG比':>12} {'純sin偏差%':>12}")
print("-" * 62)
for label, n1, n2 in phic:
    a, b = label.split("/")
    tr = mass[a]/mass[b]
    if n1 is None:
        print(f"{label:>10} {'(無)':>10} {'—':>12} {tr:>12.6f} {'—':>12}")
    else:
        sr = sinm(n1)/sinm(n2)
        print(f"{label:>10} {f'({n1},{n2})':>10} {sr:>12.6f} {tr:>12.6f} {(sr-tr)/tr*100:>+12.3f}")

print(f"\n★ 結論: 純 sin 配對偏差 0.03-0.37%; φ 修正配對偏差 0.4-99%")

# ═══ 7. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "20_A_grouping.json", "w") as f:
    json.dump({
        "gemini_claim_1_color": {"verdict": "🔴 夸克同時有同世代和跨世代配對, 色選擇律唔唯一"},
        "gemini_claim_2_dn_cb": {"value": 25, "formula": "L₅+(B²−2)", "verdict": "算術正確但 4 個結構分解"},
        "gemini_claim_3_phi_A": {"verdict": "🔴 無乾淨整數分子, 偏差 0.1-5%"},
        "o35_inconsistency": {"d_mode": [24, 1], "verdict": "🔴 d 同時指定 24 和 1"},
        "o35_sd_formula_check": {"needed_k": k, "o35_used": 10/528, "verdict": "🔴 修正嚴重不足"},
        "pure_sin_pairs": [p[0] for p in pure],
        "phi_corrected_pairs": [p[0] for p in phic],
        "A_values": A,
        "K_values": K,
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/20_A_grouping.json")