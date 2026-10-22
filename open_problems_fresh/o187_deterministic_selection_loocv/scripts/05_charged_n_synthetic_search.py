#!/usr/bin/env python3
"""
O187 Script 05 — 帶電 n 規則合成搜索 (Synthetic Search: G1∧G2 模式集 × L1 形式 × P_f 池)
=========================================================================================
路線 A 只試咗 O209 固定 assignment (冪律排序) 落 L1 形式 → 0/8。
本 script 放大: O209 質量無關模式集 S = {1,2,3,4,5,7,9,11,13} (G1∧G2, 零質量輸入)
              × L1 形式 m = M₀γ_n·P_f  ×  P_f 池 {3.6, 15.5, 37, 33, 13, 44}
              × 自由 assignment (9 模式揀 8 畀 8 帶電粒子, t 除外, n 唔重用)

問題:
  Q1 有冇 assignment 令全部 8 粒子 m_pred 入 ±5% 窗?  (blind: 由池×γ 產生, 唔 fit)
  Q2 若冇: 最近嘅 assignment 係咩? 加闊窗到幾多先有第 1 個全解?
  Q3 若冇: 證明「G1∧G2 質量無關模式集 + γ·P_f + 池」嘅零解係結構必然定窗太窄?
  Q4 有: assignment 有冇質量無關規則結構 (即唔係純 fit)?
"""
import math, json, itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"
RES = {}

M0 = 27.900915
S = [1,2,3,4,5,7,9,11,13]           # O209 G1∧G2 模式集 (質量無關)
POOL = [18/5, 44-28.5, 44-7, 44-11, 13.0, 44.0]   # = L6/F5, Nd-Eproj, Nd-L4, Nd-L5, F7, Nd
POOL_LAB = ["L6/F5=3.6","Nd-Eproj=15.5","Nd-L4=37","Nd-L5=33","F7=13","Nd=44"]
MASS = {"e":0.511000,"d":4.67,"u":2.16,"s":93.4,"mu":105.6584,"c":1270.0,
        "tau":1776.86,"b":4180.0}
ORDER = ["e","d","u","s","mu","c","tau","b"]      # 8 帶電粒子 (t 除外)

def gamma(n): return 4*math.sin(n*math.pi/88)**2

# ── Q1/Q2: 對每粒子列可接受 (n, P_f) 組合 (m_pred 入窗) ──
def acceptable(win):
    acc = {}
    for p in ORDER:
        mp = MASS[p]
        lst = []
        for n in S:
            for i, pf in enumerate(POOL):
                m = M0*gamma(n)*pf
                if abs(m-mp)/mp < win:
                    lst.append((n, POOL_LAB[i], m))
        acc[p] = lst
    return acc

for win in [0.001, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30]:
    acc = acceptable(win)
    counts = {p: len(acc[p]) for p in ORDER}
    ncand = sum(counts.values())
    # 有冇（可能嘅）全 assignment: 每粒子至少 1 候選 且 n 可互斥分配
    # 用 bipartite matching 判斷: 8 粒子 9 模式 全部可分配唔同 n
    import itertools as it
    # 簡化: 每粒子候選 n 集
    nsets = [set(x[0] for x in acc[p]) for p in ORDER]
    feasible = None
    # 貪婪後退: 檢查是否存在 8 個唔同 n 嘅選擇 (Hall 條件近似: 排列窮舉太大, 用回溯)
    def backtrack(i, used):
        if i == len(ORDER): return True
        for n in nsets[i]:
            if n not in used:
                if backtrack(i+1, used | {n}): return True
        return False
    ok = backtrack(0, set())
    print(f"窗 {win*100:>5.1f}%: 候選對 = {ncand:>3}  每粒最小 = {min(counts.values()):>2}  可行全分配 = {ok}")
    RES.setdefault("windows", []).append({"win": win, "ncand": ncand,
                                          "counts": counts, "feasible": ok})

# ── 最細窗下有冇全解: 直接睇 2% 窗嘅候選 ──
acc2 = acceptable(0.02)
print("\n±2% 窗候選清單:")
for p in ORDER:
    print(f"  {p:>4} ({MASS[p]:>8.3f}): {acc2[p] if acc2[p] else '—'}")

# ── Q3: 若零解 —「單粒子可表示」覆蓋率 (唔要求全分配) ──
cov2 = {p: len(acc2[p]) for p in ORDER}
print("\n±2% 窗單粒子覆蓋: " + " ".join(f"{p}:{c}" for p, c in cov2.items()))
n_covered = sum(1 for c in cov2.values() if c > 0)
print(f"  覆蓋粒子數/8 = {n_covered}/8")

RES.update({
    "S": S, "pool": POOL, "mass": MASS, "order": ORDER,
    "covered_2pct": cov2, "covered_count": n_covered,
})

# ── Q4 預檢: 若有解, 最近解 (nest) ──
# 最近窗 feasible 嘅位 (已有 windows 掃描) → 記最低 feasible 窗
feas_wins = [w["win"] for w in RES["windows"] if w["feasible"]]
print(f"\n最低可行窗: {min(feas_wins)*100:.1f}%" if feas_wins else "\n所有窗都無可行全分配 (<30%)")

(OUT/"05_charged_n_synthetic_search.json").write_text(
    json.dumps(RES, ensure_ascii=False, indent=2))
print("\n✅ 寫入 data/05_charged_n_synthetic_search.json")