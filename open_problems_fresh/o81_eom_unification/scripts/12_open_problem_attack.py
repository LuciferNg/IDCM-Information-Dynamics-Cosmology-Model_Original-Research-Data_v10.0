#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O81 — Script 12 (v2): 開放問題攻堅 — E_J 結構強制性 + 阻挫 32 來源
=====================================================================
攻堅 O81 §八:
  🟡 #1  E_J = 2⟨W⟩² 之結構強制性
  🟡 #4  α_ij (阻挫) 之獨立結構來源

v2 修正 (2026-09-20):
  - 面枚舉改用**旋轉系統 (rotation system)** — v1 之「全部 5-環」誤算 72
  - 撤回 v1 之「λ_max = 2d」假設 (實測 λ_max = 4 + φ² = 6.618, 非 8)
  - 保留並強化 v1 之 MaxCut 結果 (獨立確認 32)
"""
import os, math, itertools
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)

LINES = []
PASS = 0
FAIL = 0
NEG = 0
def L(s=""):
    LINES.append(str(s)); print(s)
def CHECK(desc, cond, details=""):
    global PASS, FAIL
    if cond: PASS += 1; L(f"  ✅ {desc}")
    else:    FAIL += 1; L(f"  ❌ {desc}")
    if details: L(f"     {details}")
def NEGATIVE(desc, note):
    global NEG
    NEG += 1
    L(f"  ⚠️  [否定結果] {desc}")
    L(f"     {note}")

L("=" * 88)
L("  O81 — Script 12 (v2): E_J 結構強制性 + 阻挫 32 來源")
L("=" * 88)
L("  建立日期: 2026-09-20   (v2: 修正面枚舉 + 撤回錯誤譜假設)")
L("")

# ============================================================
# 0. 權威參數
# ============================================================
N_d = 44
mu2 = 2.0
lam = 2 / 123
W2 = mu2 / (2 * lam)
W0 = math.sqrt(W2)
J_eff = W2
phi = (1 + math.sqrt(5)) / 2

# ============================================================
# 一、A5 圖建構 + 旋轉系統面枚舉
# ============================================================
L("━" * 88)
L("  一、A5 圖 (Rhombicosidodecahedron) — 建構 + 真面枚舉")
L("━" * 88)
L("")

def even_perms(v):
    a, b, c = v
    return [(a, b, c), (b, c, a), (c, a, b)]

verts = set()
base = []
for s1 in (1, -1):
    for s2 in (1, -1):
        for s3 in (1, -1):
            base.append((s1 * 1, s2 * 1, s3 * phi ** 3))
            base.append((s1 * phi ** 2, s2 * phi, s3 * 2 * phi))
for s1 in (1, -1):
    for s2 in (1, -1):
        base.append((s1 * (2 + phi), 0.0, s2 * phi ** 2))
        base.append((0.0, s1 * phi ** 2, s2 * (2 + phi)))
        base.append((s1 * phi ** 2, s2 * (2 + phi), 0.0))

for v in base:
    for p in even_perms(v):
        verts.add(tuple(round(x, 9) for x in p))

V = np.array(sorted(verts), dtype=float)
nV = len(V)
edges = []
for i in range(nV):
    for j in range(i + 1, nV):
        if abs(np.linalg.norm(V[i] - V[j]) - 2.0) < 1e-6:
            edges.append((i, j))
nE = len(edges)
adj = {i: [] for i in range(nV)}
for i, j in edges:
    adj[i].append(j); adj[j].append(i)

L(f"  V = {nV}, E = {nE}, 度 = {sorted(set(len(adj[i]) for i in range(nV)))}")
CHECK("V = 60", nV == 60, f"{nV}")
CHECK("E = 120", nE == 120, f"{nE}")
CHECK("4-正則", all(len(adj[i]) == 4 for i in range(nV)))
CHECK("E/V = 2 = d/2", abs(nE / nV - 2.0) < 1e-12, f"{nE/nV}")
L("")

# 旋轉系統: 每頂點鄰居按繞外法線之角度排序
normals = V / np.linalg.norm(V, axis=1, keepdims=True)
cyclic = {}
for v in range(nV):
    n = normals[v]
    # 建構切平面基底
    tmp = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(n, tmp)) > 0.9:
        tmp = np.array([1.0, 0.0, 0.0])
    e1 = np.cross(n, tmp); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    nbrs = adj[v]
    angs = []
    for w in nbrs:
        d = V[w] - V[v]
        d = d - np.dot(d, n) * n
        angs.append((math.atan2(np.dot(d, e2), np.dot(d, e1)), w))
    angs.sort()
    cyclic[v] = [w for _, w in angs]

# 面: 有向邊 (v->w) 之 next = (w -> x), x = cyclic[w] 中 v 之後一個
def next_edge(v, w):
    c = cyclic[w]
    idx = c.index(v)
    return (w, c[(idx + 1) % len(c)])

faces = []
visited = set()
for i, j in edges:
    for start in [(i, j), (j, i)]:
        if start in visited:
            continue
        face = []
        cur = start
        while cur not in visited:
            visited.add(cur)
            face.append(cur[0])
            cur = next_edge(*cur)
        if face:
            faces.append(face)

face_len = {}
for f in faces:
    face_len[len(f)] = face_len.get(len(f), 0) + 1

L(f"  面總數 F = {len(faces)}")
L(f"  面按邊數: {dict(sorted(face_len.items()))}")
CHECK("F = 62", len(faces) == 62, f"{len(faces)}")
CHECK("20 個三角形 (3-環)", face_len.get(3, 0) == 20, f"{face_len.get(3,0)}")
CHECK("30 個正方形 (4-環)", face_len.get(4, 0) == 30, f"{face_len.get(4,0)}")
CHECK("12 個五邊形 (5-環)", face_len.get(5, 0) == 12, f"{face_len.get(5,0)}")
CHECK("歐拉 χ = V − E + F = 2", nV - nE + len(faces) == 2, f"{nV-nE+len(faces)}")
L("")

odd_faces = [f for f in faces if len(f) % 2 == 1]
even_faces = [f for f in faces if len(f) % 2 == 0]
L(f"  奇面數 = {len(odd_faces)} (20△ + 12⬠ = 32)   偶面數 = {len(even_faces)} (30□)")
CHECK("奇面數 = 32", len(odd_faces) == 32, f"{len(odd_faces)}")

# 奇面之間是否共邊
def face_edges(f):
    return set(tuple(sorted((f[k], f[(k + 1) % len(f)]))) for k in range(len(f)))
odd_edge_count = {}
for f in odd_faces:
    for e in face_edges(f):
        odd_edge_count[e] = odd_edge_count.get(e, 0) + 1
shared = [e for e, c in odd_edge_count.items() if c > 1]
L(f"  奇面共邊數 (被 ≥2 個奇面共用) = {len(shared)}")
L(f"  僅屬 1 個奇面之邊數 = {sum(1 for c in odd_edge_count.values() if c == 1)}")
CHECK("奇面之間無共邊 (每邊最多屬 1 奇面)", len(shared) == 0, f"共邊 {len(shared)}")
L("")

# ============================================================
# 二、★ 路線 B: 32 阻挫邊 — 下界 + 可達 (獨立推導)
# ============================================================
L("━" * 88)
L("  二、★ #4 阻挫 32 之獨立推導 — 奇面下界 + 可達性")
L("━" * 88)
L("")

L("""
  設定: 頂點 ±1 二色化 s_i ∈ {+1,−1}; 「阻挫邊」= 同色邊 (α_ij = π)

  ─── 下界 (奇面論證, 嚴格) ───
  沿任何面 C 走一圈, 顏色改變次數必為偶數 (回到起點顏色):
    #(變色) = |C| − #(同色) ≡ 0 (mod 2)
  |C| 奇 ⟹ #(同色) 奇 ⟹ #(同色) ≥ 1
  ⟹ #阻挫邊 ≥ #奇面 = 32

  ─── 可達 (構造性) ───
  奇面之間無共邊 (已證: 0 條共邊)
  ⟹ 若每奇面恰好 1 條同色邊, 且偶面 0 條, 則總數 = 32 (無重複計數)
""")

# MaxCut 求解
def cut_size(s):
    return sum(1 for i, j in edges if s[i] != s[j])

rng = np.random.default_rng(20260920)
best_s, best_cut = None, -1
for trial in range(600):
    s = rng.choice([-1, 1], size=nV)
    improved = True
    while improved:
        improved = False
        for v in range(nV):
            cur = sum(1 for w in adj[v] if s[v] != s[w])
            s[v] *= -1
            new = sum(1 for w in adj[v] if s[v] != s[w])
            if new > cur: improved = True
            else: s[v] *= -1
    c = cut_size(s)
    if c > best_cut:
        best_cut, best_s = c, s.copy()

frust = set(tuple(sorted((i, j))) for i, j in edges if best_s[i] == best_s[j])
L(f"  最佳 cut = {best_cut} / {nE}  ⟹ 最少同色 (阻挫) 邊 = {nE - best_cut}")
CHECK("MaxCut = 88 ⟹ 最少阻挫邊 = 32 (下界飽和)", nE - best_cut == 32,
      f"cut={best_cut}, 阻挫={nE-best_cut}")
CHECK("該著色之阻挫邊數 = 32", len(frust) == 32, f"{len(frust)}")
L("")

per_odd = []
for f in odd_faces:
    fe = face_edges(f)
    per_odd.append(sum(1 for e in fe if e in frust))
L(f"  每個奇面之阻挫邊數: 分佈 = {sorted(set(per_odd))}, min={min(per_odd)}, max={max(per_odd)}")
CHECK("每個奇面恰好 1 條阻挫邊", all(x == 1 for x in per_odd),
      f"min={min(per_odd)}, max={max(per_odd)}")

per_even = []
for f in even_faces:
    fe = face_edges(f)
    per_even.append(sum(1 for e in fe if e in frust))
L(f"  每個偶面之阻挫邊數: 分佈 = {sorted(set(per_even))}, min={min(per_even)}, max={max(per_even)}")
CHECK("每個偶面 0 或 2 條阻挫邊 (偶性)", all(x % 2 == 0 for x in per_even),
      f"分佈 {sorted(set(per_even))}")
L("")

# 一對一對應: 阻挫邊 ↔ 奇面
mapping = {}
for idx, f in enumerate(odd_faces):
    fe = [e for e in face_edges(f) if e in frust]
    mapping[idx] = fe[0]
CHECK("32 阻挫邊 ↔ 32 奇面 一對一 (無兩奇面共用同一阻挫邊)",
      len(set(mapping.values())) == 32, f"唯一阻挫邊 {len(set(mapping.values()))}")
L("")
L("  ★★ 結論 (#4): 32 = 20△ + 12⬠ 之奇面數, 由 (i) 奇環顏色奇偶下界 +")
L("      (ii) 奇面無共邊之可達性 共同鎖定 — 獨立於冷斑觀測。")
L("")

# ============================================================
# 三、★ #1 E_J 結構強制性 — 候選路線逐一檢驗
# ============================================================
L("━" * 88)
L("  三、★ #1 E_J = 2⟨W⟩² 之結構強制性 — 候選路線逐一檢驗")
L("━" * 88)
L("")

A = np.zeros((nV, nV))
for i, j in edges:
    A[i, j] = A[j, i] = 1.0
Lap = np.diag(np.array([len(adj[i]) for i in range(nV)], dtype=float)) - A
evals = np.sort(np.linalg.eigvalsh(Lap))
lam_max, lam_mean = evals[-1], evals.sum() / nV

L(f"  A5 Laplacian 譜: λ_max = {lam_max:.10f}, ⟨λ⟩ = {lam_mean:.10f}, λ_max/⟨λ⟩ = {lam_max/lam_mean:.10f}")
L(f"  λ_max 精確形式: 4 + φ² = {4 + phi**2:.10f}  (φ² = {phi**2:.10f})")
CHECK("λ_max = 4 + φ²", abs(lam_max - (4 + phi ** 2)) < 1e-9, f"實算 {lam_max:.10f}")
L("")

L("  ── 路線 1: 均分原理 (on-site 剛度 = bond 剛度) ──")
L(f"     每頂點 on-site 剛度 = E_J/2;  每頂點 bond 剛度 = (E/V)·J_eff = {nE/nV:.4f}·J_eff")
L(f"     均分 ⟹ E_J/2 = (E/V)·J_eff ⟹ E_J = 2·(E/V)·J_eff = {2*nE/nV:.1f}·J_eff = {2*(nE/nV)*J_eff:.4f}")
L(f"     ⚠️ 給 4J_eff = 246, 目標 2J_eff = 123 → 差 2 倍")
NEGATIVE("均分原理給 E_J = 4J_eff, 非 2J_eff", "2 倍差無法以正規化消除 → 路線否定")
L("")

L("  ── 路線 2: Laplacian 譜端點/均值比 ──")
L(f"     λ_max/⟨λ⟩ = {lam_max/lam_mean:.10f} ≠ 2")
L(f"     (v1 假設 λ_max = 2d = 8 係錯 — 只有二分圖/完全圖成立; A5 圖 λ_max = 4 + φ² = 6.618)")
NEGATIVE("譜端點/均值比 = 1.6545 ≠ 2", "v1 之 λ_max = 2d 假設錯誤, 路線否定")
L("")

L("  ── 路線 3: E/V = d/2 = 2 (邊頂比) ──")
L(f"     E/V = {nE/nV:.10f} = d/2 = B/2 = 2  ✅ (4-正則恆等: 2E = V·d)")
L(f"     E_J/J_eff = 2 = E/V ⟹ E_J = 2J_eff = {2*J_eff:.4f}  ✅ 符合目標")
L(f"     物理讀法: 每個頂點分擔 d/2 = 2 條邊 ⟹ on-site 尺度 = 2 × bond 尺度")
CHECK("E_J/J_eff = E/V = d/2 = B/2 = 2 (4-正則結構恆等)", abs(nE / nV - 2.0) < 1e-12,
      f"E/V = {nE/nV}")
L("")

L("  ── 路線 4: E_J 之 SSB 等價形式 (核對恆等, 非新推導) ──")
forms = [
    ("E_J = 2⟨W⟩²", 2 * W2),
    ("E_J = μ²/λ", mu2 / lam),
    ("E_J = μ²⟨W⟩² (μ²=2)", mu2 * W2),
    ("E_J = 2|V_min|", 2 * abs(-mu2 ** 2 / (4 * lam))),
    ("E_J = μ⁴/(2λ)", mu2 ** 2 / (2 * lam)),
]
for name, val in forms:
    L(f"     {name:26s} = {val:.6f}  {'✅' if abs(val-123)<1e-9 else '❌'}")
CHECK("五種等價形式皆 = 123 (L₁₀)", all(abs(v - 123) < 1e-9 for _, v in forms))
L("")

L("  ── 路線 5: 阻挫能量比 (檢查係否給 2) ──")
cands = [
    ("E/V = d/2", nE / nV),
    ("(E − 2·F_fr)/V", (nE - 2 * 32) / nV),
    ("F_fr/16 = 32/B²", 32 / 16),
    ("(V − F_fr)/14", (nV - 32) / 14),
    ("F_even/V × ...", len(even_faces) / nV),
    ("λ_max/⟨λ⟩", lam_max / lam_mean),
    ("V/(V−F_fr)", nV / (nV - 32)),
    ("E/(E−F_fr)", nE / (nE - 32)),
]
for name, val in cands:
    mark = "★" if abs(val - 2.0) < 1e-9 else " "
    L(f"   {mark} {name:22s} = {val:.10f}")
L("")
L("  ★ 命中 2 之候選分兩類:")
L("     (i)  無額外常數: E/V = d/2 = 2  ← 4-正則邊頂比, 純圖量")
L("     (ii) 需引入額外數: F_fr/16 = 32/B², (V−F_fr)/14 = 28/a  (a = 14, O171)")
L("          → 分母 16 同 14 係外加, 屬事後湊數 (numerology), 不構成結構律")
L("  ★ 唯一無額外常數而命中 2 者 = E/V = d/2 = B/2")
CHECK("E_J/J_eff 之無額外常數結構命中 = E/V = B/2", abs(nE / nV - 2.0) < 1e-12)
L("")

# ============================================================
# 四、E_J/J_eff = B/2 之進一步檢驗 (盲測思路)
# ============================================================
L("━" * 88)
L("  四、E_J/J_eff = B/2 之可證偽檢驗")
L("━" * 88)
L("")

L("""
  ★ 若 E_J/J_eff = B/2 係結構律 (而非 A5 專屬巧合), 則對**任何 B-正則圖**皆應成立。
  但 B = 4 係 A5 圖度數 — 兩者係同一事實之兩面 (2E = V·d)。

  ─── 可證偽檢驗 (設計) ───
  檢驗 1: 其他 4-正則圖 (立方體 Q3 之線圖, 或 K5) — E/V = 2 皆成立
          → 律「E/J = d/2」對所有 d-正則圖成立 = 圖論恆等, 非 A5 特殊性
  檢驗 2: 若模擬用其他正則度 d 之圖, E_J/J_eff 應 = d/2
          → 可對 cold-spot 模擬做敏感度測試 (需另開工作, 本輪不執行)
""")

# 檢驗 1: 其他 d-正則圖
def reg_check(name, Vn, En, d):
    return (name, Vn, En, d, En / Vn, abs(En / Vn - d / 2) < 1e-12)

tests = [
    reg_check("立方體 Q3 (d=3)", 8, 12, 3),
    reg_check("K5 (d=4)", 5, 10, 4),
    reg_check("K3,3 (d=3)", 6, 9, 3),
    reg_check("Octahedron (d=4)", 6, 12, 4),
    reg_check("A5 rhombicosidodecahedron (d=4)", 60, 120, 4),
]
L(f"  {'圖':34s} | {'V':>4} | {'E':>4} | {'d':>2} | {'E/V':>6} | {'= d/2?':>7}")
L(f"  {'-'*34} | {'-'*4} | {'-'*4} | {'-'*2} | {'-'*6} | {'-'*7}")
for name, Vn, En, d, ratio, ok in tests:
    L(f"  {name:34s} | {Vn:>4} | {En:>4} | {d:>2} | {ratio:>6.3f} | {'✅' if ok else '❌':>7}")
CHECK("E/V = d/2 對所有 d-正則圖成立 (圖論恆等)", all(t[5] for t in tests))
L("")
L("  ⚠️ 誠實標記: E/V = d/2 係**圖論恆等**, 唔係 A5 特殊性。")
L("     故「E_J/J_eff = E/V」之內容 = 「on-site 尺度 = 邊頂比 × bond 尺度」,")
L("     仍需物理機制說明為何係邊頂比。**未達 structural necessity。**")
L("")

# ============================================================
# 五、總結
# ============================================================
L("━" * 88)
L("  五、總結")
L("━" * 88)
L("")
L(f"""
  ┌──────────────────────────────────────────────────────────────────────┐
  │  🟢 #4 α_ij 阻挫來源 — 已獨立推導 (本輪完成)                       │
  │     下界: 每奇面 ≥ 1 同色邊 (奇環顏色奇偶) ⟹ ≥ 32                  │
  │     可達: 奇面無共邊 (0 條) ⟹ 每奇面恰好 1 條 ⟹ 恰好 32           │
  │     獨立確認: MaxCut = {best_cut} ⟹ 最少阻挫 = {nE-best_cut}                        │
  │     面結構: F = 62 = 20△ + 30□ + 12⬠, χ = 2                        │
  │     32 阻挫邊 ↔ 32 奇面 一對一 (無重複)                            │
  │                                                                    │
  │  🟡 #1 E_J 結構強制性 — 部分進展 + 兩個否定結果                     │
  │     ✅ 新結構恆等: E_J/J_eff = E/V = d/2 = B/2 = 2 (4-正則)        │
  │     ⚠️ 否定: 均分原理 (on-site 剛度 = bond 剛度) 給 4J_eff ≠ 2J_eff │
  │     ⚠️ 否定: λ_max/⟨λ⟩ = 4+φ²/4 = 1.6545 ≠ 2 (v1 假設 λ_max=2d 錯) │
  │     ⚠️ E/V = d/2 係圖論恆等, 非 A5 特殊 → 物理機制仍缺              │
  │     🟡 狀態維持: 候選 (與模擬一致 + 結構恆等), 未達 structural       │
  │        necessity                                                     │
  └──────────────────────────────────────────────────────────────────────┘
""")
L(f"  通過: {PASS}/{PASS+FAIL}  ✅")
L(f"  失敗: {FAIL}/{PASS+FAIL}  ❌")
L(f"  否定結果 (誠實記錄): {NEG}")

with open(os.path.join(OUT, "12_open_problem_attack.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(LINES) + "\n")
print(f"\n✅ 已寫入: {OUT}/12_open_problem_attack.txt")
print(f"📊 {PASS}/{PASS+FAIL} PASS, {FAIL} FAIL, {NEG} 否定結果")
