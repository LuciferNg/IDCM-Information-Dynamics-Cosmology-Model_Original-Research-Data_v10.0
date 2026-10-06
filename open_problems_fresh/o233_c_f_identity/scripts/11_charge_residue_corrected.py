#!/usr/bin/env python3
"""
O206 — 第十五輪 scripts/11_: charge-residue 正確表 + 輕子槽成因 + up/down 分析
=========================================================================
承接: 第十四輪 docs/10_ B4 residue 表——⚠️ 發現表有錯誤: ≡3 = {d(3), c(7), b(11)}
中 c 係 up-type（唔係 down-type）——docs/10_ 寫「d,c,b 全 ≡3（3/3, s 例外）」誤導。
本輪一次過（調律者「一次過」）:
  C1 更正 + 正確 charge-residue 完整表（附 q_eff=-1/3/+2/3 標記）
  C2 輕子槽成因: 88-chain mod-4 槽幾何（γ_n 分佈、半週期平移 n+44↔4−γ_n、residue 不變性）
     + O158/O210 mod-4 家族銜接（RAG 已查: O158 45族a奇/47族a偶、O210-T1 k≡±|B−L| mod 4）
     + B=4 分支數解釋「點解有 4 個 ≡1 槽」
  C3 up/down-type residue 分析:
     up-type {u≡2, c≡3, t≡1}: 3 個唔同 residue——H0 概率?
     down-type {d≡3, s≡0, b≡3}: 2/3 ≡3, s≡0 獨特——s anomaly 確認

PRE-REGISTERED: C3 用 H0 = 3 up-type 隨機落 9 mode, P(3 residue 全 distinct/MC 10⁶).
──────────────────────────────────────────────────────────────────────
"""
import math, random, itertools, json, os

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print("  %s %s %s" % ("✅" if cond else "❌", name, detail))

MODES9 = [1,2,3,4,5,7,9,11,13]
# 正確 charge 表（R19 assignment）: (fermion, mode, type, charge)
ASSIGN = [("e",1,"lepton","-1"),("u",2,"quark-up","+2/3"),("d",3,"quark-down","-1/3"),
          ("s",4,"quark-down","-1/3"),("mu",5,"lepton","-1"),("c",7,"quark-up","+2/3"),
          ("tau",9,"lepton","-1"),("b",11,"quark-down","-1/3"),("t",13,"quark-up","+2/3")]

# ══════════════════ C1. 正確 residue 表 ══════════════════
print("=" * 74)
print("C1. 更正: charge-residue 完整表（docs/10_ B4 有誤）")
print("=" * 74)
rows = {}
for f, n, typ, ch in ASSIGN:
    rows.setdefault(n % 4, []).append((f, n, typ, ch))
for r in sorted(rows):
    print("  n ≡ %d (mod 4): %s" % (r, [(f, n, t, c) for f, n, t, c in rows[r]]))
print()
print("  更正重點: ≡3 = {d(down), c(UP), b(down)} —— c 係 up-type!")
print("  down-type {d,s,b}: residues {3,0,3} —— 2/3 ≡3, s 例外(≡0)")
print("  up-type   {u,c,t}: residues {2,3,1} —— 3 個全唔同")
print("  輕子 {e,μ,τ}: residues {1,1,1} —— 全 ≡1 (O14 正結果)")
check("C1: 輕子全 ≡1 (重申 O14)", all(n % 4 == 1 for _, n, t, _ in ASSIGN if t == "lepton"),
      "lepton residues 全 ≡1")

# ══════════════════ C2. 輕子槽成因: 88-chain mod-4 幾何 ══════════════════
print("\n" + "=" * 74)
print("C2. 輕子槽成因: 88-chain mod-4 幾何 + O158/O210 家族銜接")
print("=" * 74)
# γ_n 值 (n=1..13)
gam = lambda n: 4*math.sin(math.pi*n/88)**2
for r in sorted(rows):
    vals = [(n, round(gam(n), 6)) for f, n, t, c in rows[r]]
    print("  ≡%d: γ 值 %s" % (r, vals))
# 半週期平移: γ_(n+44) = 4−γ_n (exact identity), residue 不變 (44 ≡ 0 mod 4)
print("  ★ γ_{n+44} = 4 − γ_n (exact: sin²(x+π/2)=cos²); 44 ≡ 0 mod 4 ⟹ 半週期平移保持 residue")
print("  ⟹ 每 residue 槽喺 88-chain 有 2 個『半週期對』(n, n+44), 4×22 站")
print("  ★ 4 = B (O210: k ≡ ±|B−L| (mod B), B=4 分支數) —— 槽數 = 分支數")
print("  ★ O158 先例: 45族 a奇/47族 a偶 mod-4 方向判準; O148 mod-4 扇區閉式")
print("  ── 呢啲係語境, 唔係新證明: 輕子槽 ≡1 落入 mod-4 家族, 但『點解輕子佔 ≡1 唔係 ≡3』未解")

# ══════════════════ C3. up/down residue 分析 ══════════════════
print("\n" + "=" * 74)
print("C3. up/down-type residue: H0 概率")
print("=" * 74)
up_m = [n % 4 for _, n, t, _ in ASSIGN if t == "quark-up"]      # u,c,t → 2,3,1
dn_m = [n % 4 for _, n, t, _ in ASSIGN if t == "quark-down"]    # d,s,b → 3,0,3
print("  up-type residues:   %s (3 個全唔同)" % sorted(up_m))
print("  down-type residues: %s (2/3 ≡3, s≡0 例外)" % sorted(dn_m))
# H0: 3 個 up-type 隨機落 9 mode（residue counts {1:4, 2:1, 3:3, 0:1}）→ P(3 distinct)
counts = [sum(1 for n in MODES9 if n % 4 == r) for r in (0,1,2,3)]
print("  residue counts in MODES9: {0:%d, 1:%d, 2:%d, 3:%d}" % tuple(counts))
random.seed(20261006)
N = 1_000_000
cnt_distinct = 0
cnt_all_same = 0
for _ in range(N):
    s = [n % 4 for n in random.sample(MODES9, 3)]
    if len(set(s)) == 3: cnt_distinct += 1
    if len(set(s)) == 1: cnt_all_same += 1
p_dist = cnt_distinct / N
p_same = cnt_all_same / N
print("  H0 P(3 residue 全 distinct) = %.4f (MC)" % p_dist)
print("  H0 P(3 residue 全相同)      = %.4f (MC, 對照 down-type 2/3 無此可能)" % p_same)
check("C3a: up-type 3 distinct 唔稀有 (p > 0.05)——唔係 anomaly", p_dist > 0.05,
      "p=%.4f" % p_dist)
# down-type: s≡0 獨特 —— 唯一 ≡0 mode 係 n=4 (s 自己); P(隨機 down-type 有 ≡0) 較低
c0 = counts[0]
p_down_has0 = 1 - math.comb(9 - c0, 3)/math.comb(9, 3)
print("  H0 P(down-type 3 個中含 ≡0 槽) = %.4f (9-mode, 任意 3 位)" % p_down_has0)
check("C3b: down-type 含 ≡0 (s) 唔特別稀有 (p > 0.05)", p_down_has0 > 0.05,
      "p=%.4f" % p_down_has0)

out = {"C1": {"residue_table": {str(r): [[f, n, t, c] for f, n, t, c in v] for r, v in rows.items()}},
       "C2": {"gamma_by_residue": {str(r): [round(gam(n), 6) for f, n, t, c in v] for r, v in rows.items()}},
       "C3": {"up_residues": up_m, "down_residues": dn_m, "p_distinct": p_dist, "p_same": p_same,
              "p_down_has0": p_down_has0}}
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "11_charge_residue_corrected.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n結果: %d PASS / %d FAIL" % (PASS, FAIL))