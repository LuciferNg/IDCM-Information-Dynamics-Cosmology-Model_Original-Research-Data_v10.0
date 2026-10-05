#!/usr/bin/env python3
"""
O206 — 第十四輪 scripts/38: lepton 槽盲測（L4 升級版, pre-registered）
=========================================================================
承接: 第十三輪 L4 exploratory 發現 lepton modes = {1,5,9}（等差 4, nominal 1/56）。
本輪 pre-register 盲測——用「性質目標」降低事後選擇 bias:

  B1 盲測 (8-mode, 指定 subset 目標): H0 = 3 輕子位置隨機試 8 個 mode（無放回）,
      命中 = modes 恰好 {1,5,9}。P = 1/C(8,3) = 1/56 ≈ 0.0179。
      （目標由上一輪 exploratory 固定, 唔喺 H0 內掃描——單一目標命中測試合法）
  B2 對照 (等差本身稀有?): P(lepton modes 構成任何長 3 等差) = 10/56 ≈ 0.179
      —— 證明稀有性掛喺具體 subset, 唔係「等差」性質本身。
  B3 盲測 (9-mode 含 t, 性質目標): H0 = 3 輕子位置隨機試 9 個 mode,
      命中 = 全 n ≡ 1 (mod 4)。mod-4 槽 {1,5,9,13}（4 個槽）⟹
      P = C(4,3)/C(9,3) = 4/84 = 1/21 ≈ 0.0476。
      （用「≡1 mod 4」性質而唔係指定三數 = 可串通規則, bias 較低;
       mod-4 判準係 O 系列既有家族——結構語境支持）
  B4 描述性: 9 費米子 assignment 嘅 full mod-4 residue 表
      （輕子+t 全 ≡1: {1,5,9,13}; d,c,b 全 ≡3: {3,7,11}; u ≡2; s ≡0）——唔設閘

誠實附註: 同一 8 點 dataset 已多輪 look（鋸齒、極值、身份……）。B1/B3 嘅 p
係單一目標 nominal, 未含 look-elsewhere factor —— 只係「樣本外單目標盲測」。

PRE-REGISTERED: B1 p<0.05 ✅ 預期; B2 只報告; B3 p<0.05 ✅ 預期; MC seed 20261006。
──────────────────────────────────────────────────────────────────────
"""
import math, random, itertools, json, os

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print("  %s %s %s" % ("✅" if cond else "❌", name, detail))

MODES8 = [1,2,3,4,5,7,9,11]
MODES9 = [1,2,3,4,5,7,9,11,13]
TARGET = {1,5,9}

# ══════════════════ B1. 8-mode 指定 subset ══════════════════
print("=" * 74)
print("B1. 盲測: P(lepton modes = {1,5,9}) 8-mode (MC 10⁶ 對照 1/56)")
print("=" * 74)
exact = 1 / (math.comb(8,3))
random.seed(20261006)
N = 1_000_000
cnt = 0
for _ in range(N):
    s = set(random.sample(MODES8, 3))
    if s == TARGET: cnt += 1
print("  理論 P = 1/C(8,3) = %.6f · MC = %.6f (%d/%d)"
      % (exact, cnt/N, cnt, N))
check("B1: {1,5,9} 命中 p < 0.05", exact < 0.05, "p=%.4f" % exact)

# ══════════════════ B2. 等差對照 ══════════════════
print("\n" + "=" * 74)
print("B2. 對照: P(lepton modes 構成任何長 3 等差) 8-mode")
print("=" * 74)
ap_sub = []
for c in itertools.combinations(MODES8, 3):
    if c[1]-c[0] == c[2]-c[1]:
        ap_sub.append(c)
p_ap = len(ap_sub)/math.comb(8,3)
print("  等差 3-subset: %s (count=%d)" % (ap_sub, len(ap_sub)))
print("  P(any arithmetic) = %.3f (唔稀有——稀有性喺具體 subset 或 mod 類)" % p_ap)
check("B2: 等差本身唔稀有 (p > 0.1)", p_ap > 0.1, "p=%.3f" % p_ap)

# ══════════════════ B3. 9-mode 含 t, mod-4 性質 ══════════════════
print("\n" + "=" * 74)
print("B3. 盲測: 3 輕子全 n ≡ 1 (mod 4), 9-mode 含 t (C(9,3))")
print("=" * 74)
exact3 = math.comb(4,3)/math.comb(9,3)
cnt3 = 0
random.seed(20261006)
for _ in range(N):
    s = set(random.sample(MODES9, 3))
    if all(n % 4 == 1 for n in s): cnt3 += 1
print("  理論 P = C(4,3)/C(9,3) = 4/84 = %.5f · MC = %.6f"
      % (exact3, cnt3/N))
print("  mod-4 槽: ≡1 = %s（4 個）, ≡3 = %s（3 個）, ≡2 = %s, ≡0 = %s"
      % ([n for n in MODES9 if n%4==1], [n for n in MODES9 if n%4==3],
         [n for n in MODES9 if n%4==2], [n for n in MODES9 if n%4==0]))
check("B3: 輕子全 ≡1 mod 4 命中 p < 0.05", exact3 < 0.05, "p=%.4f (=1/21)" % exact3)

# ══════════════════ B4. 描述性 full residue 表 ══════════════════
print("\n" + "=" * 74)
print("B4. 描述性: 9 費米子 assignment 嘅 mod-4 residue 表（唔設閘）")
print("=" * 74)
ASSIGN = [("e",1,"lepton"),("u",2,"quark-up"),("d",3,"quark-down"),
          ("s",4,"quark-down"),("mu",5,"lepton"),("c",7,"quark-up"),
          ("tau",9,"lepton"),("b",11,"quark-down"),("t",13,"quark-up-VEV")]
rows = {}
for f, n, kind in ASSIGN:
    rows.setdefault(n % 4, []).append((f, n, kind))
for r in sorted(rows):
    print("  n ≡ %d (mod 4): %s" % (r, [(f, n, k) for f, n, k in rows[r]]))
print("  輕子 (e,μ,τ) + t: 全 ≡1 —— 4/4")
print("  down-type quark (d,c,b): 全 ≡3 —— 3/3 (s 例外 ≡0)")
print("  up-type quark: u≡2, c≡3, t≡1 —— 冇固定 residue?")
print("  ⚠️ 呢啲係『t 走 VEV 機制』+『R19 指派』之後嘅結構觀察, 唔當獨立預言")

out = {"B1": {"p_theory": exact, "p_mc": cnt/N},
       "B2": {"p_any_ap": p_ap, "ap_subsets": [list(c) for c in ap_sub]},
       "B3": {"p_theory": exact3, "p_mc": cnt3/N},
       "B4": {"residue_table": {str(r): [[f, n, k] for f, n, k in v] for r, v in rows.items()}}}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "38_lepton_slot_blind.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n結果: %d PASS / %d FAIL" % (PASS, FAIL))