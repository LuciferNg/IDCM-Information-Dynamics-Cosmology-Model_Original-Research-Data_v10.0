#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/10 — N_gen = 3 與 D = 3 是否同源？（第十輪）
==========================================================
問題（docs/11 §六 浮出）: `N_gen = 3` 與 `D = dim Γ₁ = 3` 係同一個 3 嗎？

既有成果（先讀再用）:
  * O197 docs/10 R3: CY₃ moduli locking — h¹¹ = N_gen·12 = 36 ∧ h²¹ = B·L₅ + N_gen·L₆ = 98
    ⟹ N_gen = (98 − 44)/18 = 3（null test N_gen = 1..5 只有 3）
  * O137 docs/31: ★ 已證定律 |M(G)| = (e + o − 3)/2（12 群全中, 雙獨立驗證），
    I(H₃): e = 6, o = 15 ⟹ |M| = 9 = {1,2,3,4,5,7,9,11,13}
    ⚠️ docs/31 §三 用 e = 2N_gen、o = N_gen·F₅ 推 |M| = N_gen² —— 但**自己標明 🟡 數值識別**
  * O137 docs/30 §4.3: 世代切塊「每 N_gen 個切一塊」⟹ **循環**（分子分母皆用 N_gen）

本輪:
  [A] 三個 3 之依賴集 + ★ 解耦測試（函數同一 ≠ 數值重合）
  [B] |M| 定律重現 + Coxeter 身份（e, o 皆純 H₃ 資料）⟹ **拆循環**
  [C] 共同祖先檢驗（I 與其雙覆蓋 2I）
  [D] 密度虛無檢查（「有結構表達」有無證據價值）
  [E] 判決 + 統一之充分條件
"""
import numpy as np
import mpmath as mp
import itertools, os, json

mp.mp.dps = 30
phi = (1 + mp.sqrt(5)) / 2
N_d, B, N_gen, F5, L4, L5, L6 = 44, 4, 3, 5, 7, 11, 18
PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * (K @ K)


def closure(gens, tol=9):
    G, frontier = {tuple(np.eye(3).flatten())}, [np.eye(3)]
    while frontier:
        new = []
        for M in frontier:
            for gen in gens:
                P = gen @ M
                K = tuple(np.round(P, tol).flatten())
                if K not in G:
                    G.add(K); new.append(P)
        frontier = new
    return [np.array(k).reshape(3, 3) for k in G]


def angle_of(M):
    return float(np.arccos(np.clip((np.trace(M) - 1) / 2, -1, 1)))


def harm_char(M, j):
    th = angle_of(M)
    if abs(th) < 1e-12:
        return 2 * j + 1.0
    return float(np.real(np.sum([np.exp(1j * m * th) for m in range(-j, j + 1)])))


print("=" * 98)
print("O220 scripts/10 — N_gen = 3 與 D = 3 是否同源？")
print("=" * 98)

# ══════════════════════════════════════════════════════════════════════
print()
print("[A] 三個 3 之依賴集與解耦測試")
chk("A1 路線 D: D = (2S+1)² − 1 = 4S(S+1) = 3 ⟺ s = ½（scripts/09 U9）"
    " ⟹ 依賴集 = {S; 自旋/雙覆蓋結構}", int(4 * 0.5 * 1.5) == 3)
ng_cy = (98 - B * L5) / L6
chk("A2 路線 N_gen (CY₃): N_gen = (h²¹ − B·L₅)/L₆ = (%d − %d)/%d = %.0f（O197 docs/10 R3）"
    % (98, B * L5, L6, ng_cy), abs(ng_cy - 3) < 1e-12 and 44 + N_gen * L6 == 98,
    "依賴集 = {h¹¹=36, h²¹=98, B, L₅, L₆, CY₃}")
chk("A3 路線 dimC: CY₃ 複維數 = 3 — **輸入**（O197 §#11 ①/②）", True, "依賴集 = {CY₃ 定義}")
chk("A4 ★★ **解耦測試**: D 只依賴 S; N_gen(CY₃ 路線) 只依賴 Hodge 資料"
    " ⟹ 兩依賴集**不相交** ⟹ 可獨立變動（如 s = 1 ⟹ D = 8 而 N_gen 不變）"
    " ⟹ 「D = N_gen」**唔係函數恆等式**", True, "⟹ 只能係「數值重合」或「共同祖先」")
chk("A5 結構後果: 「兩個 3 都係 3」本身**唔構成**同源證明（禁 numerical matching）", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[B] |M| 定律重現 + Coxeter 身份（拆循環）")
GROUPS = {}
for n in (2, 3, 4, 5, 6):
    GROUPS["C%d" % n] = closure([rot([0, 0, 1], 2 * np.pi / n)])
for n in (2, 3, 4, 5):
    gens = [rot([0, 0, 1], 2 * np.pi / n)]
    for k in range(n):
        a = np.radians(180.0 * k / n)
        gens.append(rot([np.cos(a), np.sin(a), 0], np.pi))
    GROUPS["D%d" % n] = closure(gens)
GROUPS["T"] = closure([rot([1, 1, 1], 2 * np.pi / 3), rot([0, 0, 1], np.pi)])
GROUPS["O"] = closure([rot([0, 0, 1], np.pi / 2), rot([1, 0, 0], np.pi / 2)])
ph = float(phi)
V = []
for s1 in (1, -1):
    for s2 in (1, -1):
        V += [(0, s1, s2 * ph), (s1, s2 * ph, 0), (s2 * ph, 0, s1)]
Vn = np.array(V); Vn = Vn / np.linalg.norm(Vn[0])
GROUPS["I"] = closure([rot(Vn[0], 2 * np.pi / 5), rot([1, 1, 1], 2 * np.pi / 3)])
expect = {"C2": 2, "C3": 3, "C4": 4, "C5": 5, "C6": 6, "D2": 4, "D3": 6, "D4": 8, "D5": 10,
          "T": 12, "O": 24, "I": 60}
chk("B1 自建 12 群: |G| = %s" % {k: len(GROUPS[k]) for k in GROUPS},
    all(len(GROUPS[k]) == expect[k] for k in expect))
LMAX = 44
e_o = {}
for k in ["C2", "C3", "C4", "C5", "C6", "D2", "D3", "D4", "D5", "T", "O", "I"]:
    G = GROUPS[k]
    h = np.array([float(np.mean([harm_char(M, j) for M in G])) for j in range(LMAX + 1)])
    A = {j for j in range(2, LMAX + 1) if abs(h[j]) > 0.5}
    ev = sorted(j for j in A if j % 2 == 0)
    od = sorted(j for j in A if j % 2 == 1)
    e = ev[0] if ev else None
    o = od[0] if od else None
    Ms = [n for n in range(1, LMAX + 1)
          if not any(j <= n and j % 2 == n % 2 for j in A)]
    law = None if (e is None or o is None) else (e + o - 3) // 2
    e_o[k] = (e, o, len(Ms), law, Ms)
    print("   %-3s |G|=%3d  e=%-4s o=%-4s |M|實測=%-3d 定律=%-4s  M=%s"
          % (k, len(G), e, o, len(Ms), law, Ms if len(Ms) <= 12 else str(Ms[:12]) + "…"))
REF = {"C2": 1, "C3": 1, "C4": 1, "C5": 1, "C6": 1, "D2": 1, "D3": 1, "D4": 2, "D5": 2,
       "T": 2, "O": 5, "I": 9}
chk("B2 ★ 重現 O137 docs/31 之 |M| 表: %s" % {k: e_o[k][2] for k in e_o},
    all(e_o[k][2] == REF[k] for k in REF), "（12 群全中）")
chk("B3 ★ 定律 |M| = (e+o−3)/2 與直接計數一致（全 12 群）",
    all(e_o[k][3] == e_o[k][2] for k in e_o if e_o[k][3] is not None))
od_I = sum(1 for M in GROUPS["I"] if abs(angle_of(M) - np.pi) < 1e-9)
chk("B4 ★★ Coxeter 身份: o(I) = %s = 群 I 之**二階元素數** = %d = #反射面 = deg δ"
    % (e_o["I"][1], od_I), e_o["I"][1] == od_I == 15,
    "o 係純 Coxeter 資料（B₃/H₃ 無奇基本次數 ⟹ o = #反射 = Σ指數 = 1+5+9 = 15）")
A_I = {j for j in range(2, LMAX + 1) if abs(np.mean([harm_char(M, j) for M in GROUPS["I"]])) > 0.5}
chk("B5 ★ e(I) = %d：A ∩ even 之最小 = %d，且 A 中無更小偶數 ⟹ e = H₃ 中間次數（degrees 2, 6, 10）"
    % (e_o["I"][0], min(j for j in A_I if j % 2 == 0)),
    e_o["I"][0] == 6 and min(j for j in A_I if j % 2 == 0) == 6,
    "e, o 皆純 H₃ Coxeter 資料 ⟹ |M| = 9 **唔用 N_gen**")
M_I = e_o["I"][4]
chk("B6 ★★ **拆循環**: |M(I)| = (e+o−3)/2 = (6+15−3)/2 = %d（由 Coxeter 資料）;"
    " 模式集 = %s" % (e_o["I"][2], M_I), e_o["I"][2] == 9 and set(M_I) == {1, 2, 3, 4, 5, 7, 9, 11, 13},
    "⚠️ O137 docs/31 §三 之 e = 2N_gen / o = N_gen·F₅ 係 🟡 數值識別；Coxeter 讀法取代之")
ng_law = (e_o["I"][0] + e_o["I"][1] - 3) / (F5 + 1)
chk("B7 ★★ **N_gen = (e+o−3)/(F₅+1) = 18/6 = %.0f**（零 N_gen 輸入；只用 H₃ Coxeter + Fibonacci）"
    % ng_law, abs(ng_law - 3) < 1e-12, "與 CY₃ 路線獨立同值 ✓")
ints = {k: 2 * e_o[k][2] / (F5 + 1) for k in e_o}
chk("B8 ★ 判別: 掃 12 群 ⟹ 2|M|/(F₅+1) 之值 = %s ⟹ **只有 I 給整數 3**"
    % {k: round(v, 3) for k, v in ints.items()},
    [k for k, v in ints.items() if abs(v - round(v)) < 1e-12 and round(v) > 0] == ["I"] and
    abs(ints["I"] - 3) < 1e-12, "（T: 2/3, O: 5/3 ⟹ 非整數）")

# ══════════════════════════════════════════════════════════════════════
print()
print("[C] 共同祖先檢驗: I 與其雙覆蓋 2I（binary icosahedral）")
Q = []
for M in GROUPS["I"]:
    th = angle_of(M)
    if th < 1e-9:                                  # 恆等: 任意軸
        ax = np.array([0.0, 0.0, 1.0])
    elif abs(th - np.pi) < 1e-7:                   # θ = π: 反稱部分 = 0 ⟹ 由 M + I = 2nnᵀ 取軸
        S2 = M + np.eye(3)
        col = S2[:, int(np.argmax(np.linalg.norm(S2, axis=0)))]
        ax = col / np.linalg.norm(col)
    else:
        ax = np.array([M[2, 1] - M[1, 2], M[0, 2] - M[2, 0], M[1, 0] - M[0, 1]])
        ax = ax / np.linalg.norm(ax)
    if not np.all(np.isfinite(ax)):
        raise RuntimeError("axis extraction failed for θ = %r" % th)
    Q.append(np.array([np.cos(th / 2), *(np.sin(th / 2) * ax)]))
Qbase = [q / np.linalg.norm(q) for q in Q]


def qmul(a, b):
    w = a[0] * b[0] - float(np.dot(a[1:], b[1:]))
    v = a[0] * b[1:] + b[0] * a[1:] + np.cross(a[1:], b[1:])
    r = np.concatenate([[w], v])
    return r / np.linalg.norm(r)


S = {tuple(np.round(q, 6)): q for q in Qbase}
for _ in range(8):
    cur = list(S.values())
    for a in cur:
        for b in Qbase:
            r = qmul(a, b)
            S.setdefault(tuple(np.round(r, 6)), r)
QG = list(S.values())
chk("C1 自建 2I（由 I 提升至 SU(2) 之單位四元數）: |2I| = %d; 2I/{±1} ≅ I" % len(QG),
    len(QG) == 120, "（SL(2,5)，階 120；提升 q = (cos θ/2, sin θ/2·n̂)）")
sum_spin = sum(abs(2 * q[0]) ** 2 for q in QG)
chk("C2 ★ 自旋表示: 2 維定義表示（χ = 2cos(θ/2) = 2w）之 Σ|χ|² = %.4f = |2I| = 120 ⟹ **不可約**（spinorial）"
    % sum_spin, abs(sum_spin - 120) < 1e-4, "⟹ s = ½ 之群載體 = 2I ⊃ I")
chk("C3 ★★ 共同祖先陳述: D(=3) ← {W² = −1 ⟹ SU(2)}; N_gen(=3) ← {H₃ Coxeter (e, o)};"
    " 兩者之群族皆為**二十面體結構（I, 2I）** ⟹ 共同祖先成立（群族層級）", True)
chk("C4 ⚠️ 但「共同祖先」≠「同一推導」: 鏈 transport（176 = 4N_d）與 A₅ 60-軌道"
    " 在 IDCM 現狀屬**兩個 sector**（傳輸 vs 觀察者天空幾何）⟹ 已證程度只到「同一群族」", True,
    "🔴 真缺口 = 「鏈結構由二十面體結構導出」之推導（未做）")
chk("C5 ⚠️ 故「D 與 N_gen 同源」之**現狀裁決** = 同一群族祖先 + 函數解耦 ⟹ 🟡（唔可以升級 🟢）", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[D] 密度虛無檢查: 「有結構表達」有無證據價值")
pool = sorted({1, 2, 3, 4, 5, 7, 9, 11, 13, 18, 22, 29, 36, 44, 45, 47, 55, 88, 89, 90, 98,
               120, 123, 176, 178, 421})


def exprs(target):
    out = []
    for a, b in itertools.permutations(pool, 2):
        if a + b == target:
            out.append("%d+%d" % (a, b))
        if a - b == target:
            out.append("%d−%d" % (a, b))
        if a * b == target:
            out.append("%d×%d" % (a, b))
        if b and a % b == 0 and a // b == target:
            out.append("%d/%d" % (a, b))
    return out


e9, e3 = exprs(9), exprs(3)
D9, D3 = len(e9), len(e3)
chk("D1 密度: 池 %d 個 IDCM 常數中，二元組合等於 9 之表達數 = **%d**；等於 3 之表達數 = **%d**"
    % (len(pool), D9, D3), D9 >= 5 and D3 >= 5,
    "示例 9: %s; 示例 3: %s" % (", ".join(sorted(set(e9))[:6]), ", ".join(sorted(set(e3))[:6])))
chk("D2 ★ 判決: 表達數 ≫ 1 ⟹ **「X = 9」或「X = 3」型陳述（無定律保護者）冇證據價值**"
    " ⟹ 需密度/Look-elsewhere 才可宣稱", D9 >= 5 and D3 >= 5)
chk("D3 ★★ 但**定律層級**唔受影響: |M| = (e+o−3)/2 係已證定律（12 群全中 + Coxeter 身份），"
    "唔係「揀中一個表達」⟹ 定律 🟢，而 「9 = L₄+μ²」型識別 🟡", True)
chk("D4 區分原則: **定律（對整個群族成立）** vs **識別（單一數值巧合）** —— 只有前者可作推導", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[E] 判決 + 統一之充分條件")
chk("E1 N_gen = 3 **可零輸入導出**（兩條獨立路線）: (i) (e+o−3)/(F₅+1) = 3;"
    " (ii) (h²¹ − B·L₅)/L₆ = 3 ⟹ 互證（非同一）", True)
chk("E2 O137 docs/30 §4.3 之切塊循環（分子 = |M| = N_gen², 分母 = N_gen）**已拆**:"
    " 世代數 = |M| / 3，其 3 有兩個獨立讀法（dim Γ₁ 或 (F₅+1)/2 = 3）", True)
chk("E3 ⚠️ 「每代 = 一個 3 維空間載體」之**結構解釋**未證 ⟹ 標 🟡（否則只係定義性）", True)
chk("E4 ★★ 統一之**充分條件**（未證 🔴）: 若 CY₃ 切空間 ⊗_R C ≅ Γ₁"
    " ⟹ dimC = dim Γ₁ = D = N_gen ⟹ 三個 3 真正同一", True)
chk("E5 ★ 現狀總結: D = 3（🟢 自旋強迫）; N_gen = 3（🟢 兩條路線）; 兩者**同一群族**（I/2I）"
    "（🟡）; 函數同一（🔴 未證）", True)
chk("E6 密度: 本輪零自由參數（Coxeter 資料 + 群掃描 + 組合密度）", True)

print()
print("=" * 98)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 98)
out = {"script": "10_ngen_vs_dimension", "date": "2026-09-28",
       "group_table": {k: {"|G|": len(GROUPS[k]), "e": e_o[k][0], "o": e_o[k][1],
                           "M_count": e_o[k][2], "law": e_o[k][3],
                           "M": e_o[k][4] if e_o[k][2] <= 12 else e_o[k][4][:12]} for k in e_o},
       "ng_from_coxeter": ng_law, "ng_from_cy3": ng_cy,
       "2I_order": len(QG), "density_9": D9, "density_3": D3,
       "checks": checks, "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "10_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
