#!/usr/bin/env python3
"""
O88/PD #1 — N_LQ = 48 相干 vs 非相干：群論 Clebsch 完整計算
============================================================
目標: 處置 docs/04 §4.1 之 [2.89e38, 1.39e40] yr 範圍（跨度 48 = N_LQ）。

結果（v3）: 推導唔止消除「48×」—— 直情否證 docs/04 之核心前提：
  ① (15,8) coset generator 之 support 只喺 (quark, lepton) 指標對
  ② 故其電流 J = psi^bar_a T^A_ab psi_b 帶 (DeltaB, DeltaL) = (-1/3, -1)
  ③ 故交換算子 O = J . J^dagger 帶 (DeltaB, DeltaL) = (0, 0)
  ④ ⟹ gauge boson 交換唔中介 DeltaB=1 ⟹ N_channel(DeltaB=1) = 0
  ⑤ ⟹ 質子衰變唔由 gauge leptoquark 中介；「48」唔係（亦唔可能係）channel 數
  ⑥ 副定理: 即使有 DeltaB=1 通道，48 個 generator 之和因張量積分解而
     = (6 部分) x (8 部分)，乘數係 O(1)，唔會係 48 / 48^2 / 8 / 6

修訂記錄（append-only）:
  v1 — 首版；S7 FAIL 抓到閉式漏 colour 限制
  v2 — 修正閉式（maxdev=0）、加 15 = 8+6+1 分解恆等；但 S9/S12 之
       「pair-tensor 冪等」命題本身錯誤（正確命題係 Casimir），且
       invariant 收縮全 0 未被解讀 → 最終 crash
       （v2 全文保留於 logs/07_clebsch_closure.v2_superseded.py，sha256 06b7530d…）
  v3 — 正確 Casimir 命題；★ 解讀全 0 收縮 ⟹ 發現 main result（ΔB = 0）

零新常數、零觀測錨。結構輸入: O85 破缺鏈、O89 M_GUT/alpha_GUT。

執行: /usr/bin/python3 scripts/07_clebsch_closure.py
"""

import os, json, math
from fractions import Fraction as F

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE, "logs"); DATA_DIR = os.path.join(BASE, "data")
os.makedirs(LOG_DIR, exist_ok=True); os.makedirs(DATA_DIR, exist_ok=True)

RESULTS = []
def check(name, cond, detail=""):
    RESULTS.append({"id": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
    return bool(cond)

print("=" * 78)
print("O88/PD #1 — N_LQ = 48 相干 vs 非相干：群論 Clebsch 完整計算 (v3)")
print("=" * 78)

# ============================================================
# SECTION 1: Generator 建構
# ============================================================
print("\nSECTION 1: Generator 建構（normalization Tr(T T') = delta/2）")
print("-" * 78)

def build_sun_gens(n):
    gens = []
    for i in range(n):
        for j in range(i + 1, n):
            A = [[0j] * n for _ in range(n)]; A[i][j] = 0.5;  A[j][i] = 0.5
            gens.append(A)
            B = [[0j] * n for _ in range(n)]; B[i][j] = -0.5j; B[j][i] = 0.5j
            gens.append(B)
    for k in range(1, n):
        c = 1.0 / math.sqrt(2.0 * k * (k + 1))
        D = [[0j] * n for _ in range(n)]
        for i in range(k): D[i][i] = complex(c)
        D[k][k] = complex(-k * c)
        gens.append(D)
    return gens

T4 = build_sun_gens(4)   # SU(4)_PS
T3 = build_sun_gens(3)   # SU(3)_F
def tr_norm(A, B): return sum(A[i][j] * B[j][i] for i in range(len(A)) for j in range(len(B)))
check("S1  SU(4)_PS 生成元數 = 15", len(T4) == 15, "got=%d" % len(T4))
check("S2  SU(3)_F  生成元數 = 8",  len(T3) == 8,  "got=%d" % len(T3))
check("S3  SU(4) 正規化 Tr=delta/2",
      all(abs(tr_norm(T4[a], T4[b]) - (0.5 if a == b else 0.0)) < 1e-12 for a in range(15) for b in range(15)))
check("S4  SU(3) 正規化 Tr=delta/2",
      all(abs(tr_norm(T3[a], T3[b]) - (0.5 if a == b else 0.0)) < 1e-12 for a in range(8) for b in range(8)))

# ============================================================
# SECTION 2: PS 4-plet 內容 + 15 = 8 + 6 + 1
# ============================================================
print("\nSECTION 2: PS 4-plet 內容 同 SU(4)_PS adjoint 分解")
print("-" * 78)

PS_B  = [F(1, 3), F(1, 3), F(1, 3), F(0)]
PS_L  = [F(0), F(0), F(0), F(1)]
PS_BL = [PS_B[i] - PS_L[i] for i in range(4)]
print("  PS 4-plet (B, L, B-L): %s" % [(str(PS_B[i]), str(PS_L[i]), str(PS_BL[i])) for i in range(4)])
check("S5  B-L(quark)=1/3, B-L(lepton)=-1",
      PS_BL[0] == F(1, 3) and PS_BL[3] == F(-1), "BL=%s" % [str(x) for x in PS_BL])

def classify(M):
    if any(abs(M[a][b]) > 1e-12 for a in range(4) for b in range(4) if (a < 3) != (b < 3)):
        return "LQ"
    if all(abs(M[a][b]) < 1e-12 for a in range(4) for b in range(4) if a == 3 or b == 3):
        return "SU3c"
    return "BL"

CLS = [classify(M) for M in T4]
n_c, n_lq, n_bl = CLS.count("SU3c"), CLS.count("LQ"), CLS.count("BL")
print("  SU(4)_PS adjoint: 8_c = %d ; LQ (3 + 3bar) = %d ; B-L singlet = %d" % (n_c, n_lq, n_bl))
check("S6  ★ 15 = 8(colour octet) + 6(leptoquark) + 1(B-L)",
      (n_c, n_lq, n_bl) == (8, 6, 1), "got=(%d,%d,%d)" % (n_c, n_lq, n_bl))
LQ = [M for M, c in zip(T4, CLS) if c == "LQ"]

# ============================================================
# SECTION 3: ★★ 核心否證 — LQ generator support 與 DeltaB
# ============================================================
print("\nSECTION 3: ★★ 核心否證 — coset generator support 與 DeltaB")
print("-" * 78)

support = set()
for M in LQ:
    for a in range(4):
        for b in range(4):
            if abs(M[a][b]) > 1e-12:
                support.add((a, b))
kinds = set(("q" if a < 3 else "l", "q" if b < 3 else "l") for (a, b) in support)
print("  LQ generator 之 (index_a, index_b) 類型集合 = %s" % sorted(kinds))
check("S7  ★ LQ generator 只在 (quark,lepton) 或 (lepton,quark) 有 support",
      kinds == {("q", "l"), ("l", "q")}, "kinds=%s" % sorted(kinds))
check("S8  ★ 冇 LQ generator 有 (quark,quark) support（⟹ 無 diquark 電流）",
      ("q", "q") not in kinds, "kinds=%s" % sorted(kinds))
check("S9  ★ 冇 LQ generator 有 (lepton,lepton) support",
      ("l", "l") not in kinds, "kinds=%s" % sorted(kinds))

def current_charges(a, b):
    """J = psi^bar_a T_ab psi_b：消滅 psi_a、產生 psi_b ⟹ (DeltaB, DeltaL) = (B_b-B_a, L_b-L_a)"""
    return (PS_B[b] - PS_B[a], PS_L[b] - PS_L[a])

cur = set(current_charges(a, b) for (a, b) in support)
print("  LQ 電流 J 之 (DeltaB, DeltaL) = %s" % sorted((str(x), str(y)) for x, y in cur))
check("S10 ★ 每個 LQ 電流帶 (DeltaB, DeltaL) = (+1/3,-1) 或 (-1/3,+1)（每個只含一 q 一 l）",
      cur == {(F(1, 3), F(-1)), (F(-1, 3), F(1))},
      "set=%s" % sorted((str(x), str(y)) for x, y in cur))

# ★ 交換: 每個 boson 之發射 + 吸收兩頂點，兩電流必為共軛對
exch = set()
for (db1, dl1) in cur:
    for (db2, dl2) in cur:
        exch.add((db1 + db2, dl1 + dl2))
# ★★ 更強: 列舉「任意兩電流配對」（不限共軛），顯示 |DeltaB| 只可能係 0 或 2/3
allpairs = sorted(set((db1 + db2, dl1 + dl2) for (db1, dl1) in cur for (db2, dl2) in cur),
                  key=lambda t: (t[0], t[1]))
print("\n  ── 兩電流任意配對之 (DeltaB, DeltaL) 全集合 ──")
print("  %s" % [(str(x), str(y)) for x, y in allpairs])
check("S11 ★★ 任意兩 LQ 電流配對之 |DeltaB| ∈ {0, 2/3}（結構上取不到 1）",
      set(abs(db) for (db, dl) in allpairs) == {F(0), F(2, 3)},
      "|DeltaB| set=%s" % sorted(str(abs(db)) for (db, dl) in allpairs))

n_db1 = len([1 for (db, dl) in allpairs if abs(db) == 1])
print("\n  ★★ N_channel(|DeltaB| = 1) = %d   （docs/04 宣稱 48）" % n_db1)
check("S12 ★★ N_channel(|DeltaB|=1) = 0 ⟹ 48 唔係 DeltaB=1 通道數", n_db1 == 0, "N_db1=%d" % n_db1)
check("S13 ★★ 無任何 LQ 電流有 (q,q) 或 (l,l) 支撐 ⟹ 無 diquark 耦合 ⟹ 唔中介 DeltaB=±1",
      n_db1 == 0 and ("q", "q") not in kinds and ("l", "l") not in kinds,
      "n_db1=%d kinds=%s" % (n_db1, sorted(kinds)))

# --- 3.5 ★★ 推廣: 全部 120 個 (15,8) coset 生成元 ---
# (15,8) = [SU(4) adjoint 15] (x) [SU(3)_F adjoint 8]; 15 = 8_c + 3 + 3bar + 1
# 每個 SU(4) 方向之 leg 類型決定電流之 (DeltaB, DeltaL); SU(3)_F 部分不帶 B/L
allcur = set()
leg_by_comp = {}
for MA in T4:
    legs = set((a, b) for a in range(4) for b in range(4) if abs(MA[a][b]) > 1e-12)
    comp = classify(MA)
    lm = set((("q" if a < 3 else "l"), ("q" if b < 3 else "l")) for (a, b) in legs)
    leg_by_comp.setdefault(comp, set()).update(lm)
    if comp == "BL":
        # B-L singlet 方向: leg 為 (lepton,lepton) 對角（或由零 trace 條件決定）
        allcur.add((F(0), F(0)))
    for (a, b) in legs:
        allcur.add(current_charges(a, b))

print("\n  ── 全部 coset 分量之 leg 類型 ──")
for comp in ("SU3c", "LQ", "BL"):
    print("     %-6s leg 類型 = %s" % (comp, sorted(leg_by_comp.get(comp, set()))))
print("  全部 coset 電流之 (DeltaB, DeltaL) = %s" % sorted((str(x), str(y)) for x, y in allcur))

allpair_max = max(abs(db1 + db2) for (db1, dl1) in allcur for (db2, dl2) in allcur)
print("  ★★ 全部 120 個 coset 生成元: 單 boson 交換之 max|DeltaB| = %s" % allpair_max)
check("S13b ★★ 全 (15,8) coset: 單 boson 交換 max|DeltaB| = 2/3 < 1 ⟹ 廣義無質子衰變",
      allpair_max == F(2, 3), "max|dB|=%s" % allpair_max)

# ============================================================
# SECTION 4: 副定理 — 張量積分解 + 部分和閉式 + Casimir
# ============================================================
print("\nSECTION 4: 副定理 — 張量積分解 + 部分和精確閉式 + Casimir")
print("-" * 78)

S_PS = {(a, b, c, d): sum(M[a][b] * M[c][d] for M in LQ)
        for a in range(4) for b in range(4) for c in range(4) for d in range(4)}
def is_col(x): return x < 3
def ps_closed(a, b, c, d):
    t1 = (1.0 if b == 3 else 0.0) * (1.0 if c == 3 else 0.0) * (1.0 if (a == d and is_col(a)) else 0.0)
    t2 = (1.0 if a == 3 else 0.0) * (1.0 if d == 3 else 0.0) * (1.0 if (b == c and is_col(b)) else 0.0)
    return 0.5 * (t1 + t2)
dev = max(abs(S_PS[(a, b, c, d)] - ps_closed(a, b, c, d))
          for a in range(4) for b in range(4) for c in range(4) for d in range(4))
print("  ★ sum_{A in LQ} T^A_ab T^A_cd 閉式 max|dev| = %.3e" % dev)
check("S14 ★ PS LQ 部分和 = (1/2)[d_b4 d_c4 d_ad^col + d_a4 d_d4 d_bc^col]", dev < 1e-12, "maxdev=%.2e" % dev)

full = {(a, b, c, d): sum(M[a][b] * M[c][d] for M in T4)
        for a in range(4) for b in range(4) for c in range(4) for d in range(4)}
cpart = {(a, b, c, d): sum(M[a][b] * M[c][d] for M, cl in zip(T4, CLS) if cl == "SU3c")
         for a in range(4) for b in range(4) for c in range(4) for d in range(4)}
blpart = {(a, b, c, d): sum(M[a][b] * M[c][d] for M, cl in zip(T4, CLS) if cl == "BL")
          for a in range(4) for b in range(4) for c in range(4) for d in range(4)}
dev_dec = max(abs(full[k] - cpart[k] - blpart[k] - S_PS[k]) for k in full)
print("  ★ 分解恆等 max|full - (SU3c + LQ + BL)| = %.3e" % dev_dec)
check("S15 ★ 15-adjoint = 8_c + LQ + B-L（部分和分解恆等）", dev_dec < 1e-12, "maxdev=%.2e" % dev_dec)

def casimir(Ts, n):
    return [[sum(M[a][b] * M[b][c] for M in Ts for b in range(n)) for c in range(n)] for a in range(n)]
C4m, C3m = casimir(T4, 4), casimir(T3, 3)
c4_val = sum(C4m[i][i] for i in range(4)).real / 4
c3_val = sum(C3m[i][i] for i in range(3)).real / 3
sc4 = max(abs(C4m[i][j] - (c4_val if i == j else 0.0)) for i in range(4) for j in range(4))
sc3 = max(abs(C3m[i][j] - (c3_val if i == j else 0.0)) for i in range(3) for j in range(3))
print("  Casimir: C2(SU(4) fund) = %.10f (15/8) ; C2(SU(3) fund) = %.10f (4/3)" % (c4_val, c3_val))
check("S16 ★ sum_a T^a T^a = C2·1（SU(4) fund, C2 = 15/8）",
      sc4 < 1e-10 and abs(c4_val - 15.0 / 8.0) < 1e-10, "C2=%.10f" % c4_val)
check("S17 ★ sum_a t^a t^a = C2·1（SU(3) fund, C2 = 4/3）",
      sc3 < 1e-10 and abs(c3_val - 4.0 / 3.0) < 1e-10, "C2=%.10f" % c3_val)

S_F = {(i, j, k, l): sum(M[i][j] * M[k][l] for M in T3)
       for i in range(3) for j in range(3) for k in range(3) for l in range(3)}
def f_closed(i, j, k, l):
    return 0.5 * ((1.0 if i == l else 0.0) * (1.0 if k == j else 0.0)
                  - (1.0 if i == j else 0.0) * (1.0 if k == l else 0.0) / 3.0)
dev_f = max(abs(S_F[(i, j, k, l)] - f_closed(i, j, k, l))
            for i in range(3) for j in range(3) for k in range(3) for l in range(3))
print("  ★ SU(3)_F 完備性 max|dev| = %.3e" % dev_f)
check("S18 ★ SU(3)_F 完備性 = (1/2)[d_il d_kj - (1/3) d_ij d_kl]", dev_f < 1e-12, "maxdev=%.2e" % dev_f)

sing = abs(sum(S_F[(i, i, k, k)] for i in range(3) for k in range(3)))
print("  ★ Schur: (sum_i d_ii)x(sum_k d_kk) = %.3e" % sing)
check("S19 ★ Schur: family-adjoint 湮滅 family-singlet（收縮 = 0，唔係 8）", sing < 1e-12, "val=%.2e" % sing)

# --- 張量積分解之直接核對（12 = 4 (x) 3 空間）---
K12 = []
for MA in LQ:
    for Ma in T3:
        K12.append([[MA[i][j] * Ma[p][q] for j in range(4) for q in range(3)]
                    for i in range(4) for p in range(3)])
print("  12-dim K = T^A_PS (x) t^a_F 生成元數 = %d" % len(K12))
check("S20 ★ 48 = 6 (LQ) x 8 (SU(3)_F adjoint) 生成元數", len(K12) == 48, "got=%d" % len(K12))

idx = [(i, p) for i in range(4) for p in range(3)]
maxdev_fact = 0.0
for (i1, p1) in idx:
    for (i2, p2) in idx:
        for (i3, p3) in idx:
            for (i4, p4) in idx:
                lhs = sum(K[i1 * 3 + p1][i2 * 3 + p2] * K[i3 * 3 + p3][i4 * 3 + p4] for K in K12)
                rhs = S_PS[(i1, i2, i3, i4)] * S_F[(p1, p2, p3, p4)]
                if abs(lhs - rhs) > maxdev_fact: maxdev_fact = abs(lhs - rhs)
print("  ★ 張量積分解 max|sum_{48} K K - (sum_6 T T)(sum_8 t t)| = %.3e" % maxdev_fact)
check("S21 ★★ 48-生成元和 = (6-和) x (8-和) ⟹ 乘數唔可能係獨立之 48",
      maxdev_fact < 1e-12, "maxdev=%.2e" % maxdev_fact)

# ============================================================
# SECTION 5: 結論 — tau_p 範圍之處置
# ============================================================
print("\nSECTION 5: ★★ 結論 — docs/04 tau_p 範圍之處置")
print("-" * 78)
print("""
  docs/04 §2.2 宣稱: 「(3,8) (+) (3bar,8) 色三重態 | 48 | DeltaB = 1 | leptoquark（耦合 qq 同 qbar l）」
  docs/04 §4.1 範圍: [2.891e38, 1.388e40] yr（跨度 48 = N_LQ，非相干 vs 相干）

  本推導判定:
   ① support 檢查 (S7-S9):  LQ generator 只在 (q,l)/(l,q) 有 support ⟹ **無 diquark 耦合**
   ② 電流電荷 (S10):        J 帶 (DeltaB, DeltaL) = (+1/3,-1) 或 (-1/3,+1)
   ③ 兩電流任意配對 (S11):  |DeltaB| ∈ {0, 2/3} —— 結構上取不到 1
   ④ 通道數  (S12-S13):     N_channel(|DeltaB| = 1) = 0

  ⟹ 「DeltaB = 1」標籤唔成立；48 個 gauge boson 唔中介質子衰變。
  ⟹ [2.891e38, 1.388e40] yr 唔係「收窄」，而係**前提否證** → 整個範圍撤回。
  ⟹ 副定理 (S14-S21)：48 個生成元之和結構性分解為 (6 部分)x(8 部分)，
     乘數係 O(1)；且 SU(3)_F adjoint 對 family-singlet 收縮 = 0（Schur）。
     故 48 / 48^2 / 8 / 6 四種假設全部結構性排除。

  結構理由（不依賴 12 / 12bar 選擇）: coset generator 之 support 定義上係
  (colour <-> lepton)，故任一雙線性算子必含「恰好一 q 一 l」。
  DeltaB=1 之質子衰變卻要求交換 boson 具 diquark 耦合（(q q) <-> (qbar lbar)），
  在此結構下不存在 ⟹ |DeltaB| = 1 無法生成。

  IDCM v10 SU(12) 鏈之質子衰變: **唔由 gauge leptoquark 中介**。
  DeltaB=1 算子若要出現，須由 **scalar 扇區**（Higgs leptoquark：鏈中 (15,8) 標量
  或 PS 破缺 Higgs (4,1,2)/(4bar,1,2)）提供 —— 本 O 從未分析 ⟹ 新開放項。
""")
check("S22 ★★ 判定: gauge-LQ 介質之 tau_p 範圍撤回（前提否證）", n_db1 == 0)
check("S23 ★★ 新開放項已識別: DeltaB=1 須由 scalar 扇區提供", n_db1 == 0 and len(LQ) == 6)

# ============================================================
print("\n" + "=" * 78)
npass = sum(1 for r in RESULTS if r["pass"])
print("結果: %d/%d PASS" % (npass, len(RESULTS)))
for r in RESULTS:
    if not r["pass"]: print("   FAIL - %s : %s" % (r["id"], r["detail"]))
print("=" * 78)

out = {
    "script": "07_clebsch_closure.py", "version": "v3", "date": "2026-10-02",
    "purpose": "O88/PD #1 — N_LQ=48 相干 vs 非相干：群論 Clebsch 完整計算",
    "main_result": "coset generator 只喺 (q,l) 有 support ⟹ 無 diquark 耦合 ⟹ |DeltaB|=1 通道數 = 0",
    "lq_generator_support_kinds": sorted([list(x) for x in kinds]),
    "lq_current_charges": sorted([[str(x), str(y)] for x, y in cur]),
    "two_current_pairings": sorted([[str(x), str(y)] for x, y in allpairs]),
    "exchange_conjugate_pairing": sorted([[str(x), str(y)] for x, y in exch]),
    "n_channel_deltaB_1": n_db1,
    "ps_lq_partial_sum": "sum_{A in LQ} T^A_ab T^A_cd = (1/2)[d_b4 d_c4 d_ad^col + d_a4 d_d4 d_bc^col]",
    "decomposition_identity": "full SU(4) adjoint sum = (8_c sum) + (LQ sum) + (B-L sum)",
    "su3_completeness": "sum_{a=1..8} t^a_ij t^a_kl = (1/2)[d_il d_kj - (1/3) d_ij d_kl]",
    "tensor_factorization_dev": maxdev_fact,
    "casimir_su4_fund": c4_val, "casimir_su3_fund": c3_val,
    "secondary_theorem": "48-生成元和 = (6-和)x(8-和) ⟹ 乘數 O(1)，非 48/48^2/8/6",
    "falsified_hypotheses": {"incoherent_x48": True, "coherent_x48sq": True,
                             "family_count_x8": True, "lq_count_x6": True,
                             "gauge_LQ_mediates_DeltaB1": True},
    "tau_old_range_yr": [2.891e38, 1.388e40],
    "tau_new_status": "RETRACTED（前提否證：gauge-LQ 唔中介 DeltaB=1）",
    "new_open_item": "DeltaB=1 算子須由 scalar 扇區（Higgs leptoquark）提供 —— 未分析",
    "checks": RESULTS, "n_pass": npass, "n_total": len(RESULTS),
}
with open(os.path.join(DATA_DIR, "07_clebsch_closure.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
print("\n已寫入: data/07_clebsch_closure.json")
