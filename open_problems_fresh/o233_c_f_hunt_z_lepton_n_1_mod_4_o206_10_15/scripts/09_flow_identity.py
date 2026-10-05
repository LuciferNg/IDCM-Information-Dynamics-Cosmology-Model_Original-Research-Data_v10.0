#!/usr/bin/env python3
"""
O206 — 第十三輪 scripts/09_: even/odd 兩流身份（quark/lepton 分層 + 塊層 + u/d 二重結構）
=========================================================================
承接: 第十二輪 (docs/08) 後剩餘——even/odd 兩流算子身份 {u,s,c,b} vs {e,d,μ,τ}。
「繼續」⟹ 本輪三問題 + 一 exploratory:

  L1 quark/lepton 分層 null: 8 質量升序 rank, 3 輕子 (e,μ,τ) 全落 odd rank?
      H0: 3 輕子隨機佔 8 個 rank ⟹ P = C(4,3)/C(8,3) = 4/56 = 1/14 ≈ 0.0714。
      補充: 5 quark 只能佔 4 even 位 ⟹ 「4/5 quark even」係分層極限；
      實測達極限 ── 但 P(全輕子奇位) 唔達 0.05 ⟹ 誠實邊緣。
  L2 塊層 even/odd 比: 每塊 even-rank 幾何中位 / odd-rank 幾何中位
      (確認「even 優勢」嘅塊結構——唔 pre-register 為 PASS, 只報告)
  L3 u/d 二重結構: (a) rank 身份喺 PDG 範圍內零變 (b) C_f 序 (鋸齒) 敏感 23%
      ⟹ 「身份 vs 振幅」兩層分離
  L4 exploratory: lepton modes = {1,5,9}（等差 4）——🎯 事件後觀察, 唔係
      pre-registered, 唔入 PASS count; 只列明 P(指定 3-subset)=1/56 同盲測設計。

PRE-REGISTERED: L1 判據 p ≤ 0.05 (FAIL 預期); L3 判據 rank 身份零變。
──────────────────────────────────────────────────────────────────────
"""
import math, itertools, random, json, os

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print("  %s %s %s" % ("✅" if cond else "❌", name, detail))

M0 = 27.900915
gam = lambda n: 4 * math.sin(math.pi * n / 88)**2
MASS = {"e":0.51099895,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
ORDER = ["e","u","d","s","mu","c","tau","b"]
MODES = [1,2,3,4,5,7,9,11]
LEP = {"e","mu","tau"}                    # 3 輕子
BLOCK_G = {"e":0,"u":0,"d":0, "s":1,"mu":1,"c":1, "tau":2,"b":2}

def lnCf(m, n): return math.log(m / (M0 * gam(n)))

# ══════════════════ L1. quark/lepton 分層 null ══════════════════
print("=" * 74)
print("L1. quark/lepton 分層: 3 輕子全落 odd rank?")
print("=" * 74)
ranks = range(1, 9)
odd_ranks = {1, 3, 5, 7}
# comb: 8 揀 3 輕子位置, 全 odd 嘅組數
cnt_total = sum(1 for c in itertools.combinations(ranks, 3))
cnt_allodd = sum(1 for c in itertools.combinations(ranks, 3)
                 if all(r in odd_ranks for r in c))
p1 = cnt_allodd / cnt_total
print("  P(3 輕子全落 odd rank) = %d/%d = %.4f (1/14=0.0714)" % (cnt_allodd, cnt_total, p1))
print("  實測: e→rank1(odd) μ→rank5(odd) τ→rank7(odd) = 全 odd ✓")
print("  附註: 5 quark 只有 4 even 位 ⟹ 『4/5 quark even』係分層極限, 實測達極限")
check("L1: 全輕子奇位 p ≤ 0.05 (誠實預期 FAIL)", p1 <= 0.05, "p=%.4f (邊緣)" % p1)

# ══════════════════ L2. 塊層 even/odd 比 ══════════════════
print("\n" + "=" * 74)
print("L2. 每塊 even-rank 幾何中位 / odd-rank 幾何中位")
print("=" * 74)
cf = {f: math.exp(lnCf(MASS[f], MODES[i])) for i, f in enumerate(ORDER)}
for g in range(3):
    blk = [f for f in ORDER if BLOCK_G[f] == g]
    ev = [cf[f] for f in blk if (ORDER.index(f)+1) % 2 == 0]
    od = [cf[f] for f in blk if (ORDER.index(f)+1) % 2 != 0]
    g_ev = math.exp(sum(math.log(e) for e in ev)/len(ev)) if ev else None
    g_od = math.exp(sum(math.log(o) for o in od)/len(od)) if od else None
    ratio = g_ev/g_od if (g_ev and g_od) else float('nan')
    print("  gen%d %-10s  even=%s geo=%.3f | odd=%s geo=%.3f | ratio=%.4f"
          % (g+1, blk,
             [f for f in blk if (ORDER.index(f)+1) % 2 == 0], g_ev or 0,
             [f for f in blk if (ORDER.index(f)+1) % 2 != 0], g_od or 0, ratio))

# ══════════════════ L3. u/d 二重結構 ══════════════════
print("\n" + "=" * 74)
print("L3. u/d scheme: 身份 vs 振幅 (rank 零變 vs C_f 序 23% 敏感)")
print("=" * 74)
random.seed(20261006)
N = 1_000_000
keep_rank = keep_alt = 0
for _ in range(N):
    u = random.uniform(1.8, 3.5); d = random.uniform(4.5, 5.3)
    ms = {"e":0.51099895,"u":u,"d":d,"s":93.4,"mu":105.6583755,
          "c":1270.0,"tau":1776.86,"b":4180.0}
    # rank 身份: 排序後奇偶構造 (lepton 全 odd rank?)
    order = sorted(ORDER, key=lambda f: ms[f])
    if all((order.index(f)+1) % 2 == 1 for f in LEP):
        keep_rank += 1
    # 鋸齒 (C_f 序交替)
    ys = [lnCf(ms[f], MODES[i]) for i, f in enumerate(ORDER)]
    dirs = [ys[i+1] > ys[i] for i in range(7)]
    if all(dirs[i] != dirs[i+1] for i in range(6)):
        keep_alt += 1
print("  rank 身份 (lepton 全 odd) 保持率: %.4f" % (keep_rank/N))
print("  C_f 鋸齒 (交替) 保持率:           %.4f" % (keep_alt/N))
check("L3a: rank 身份對 u/d 零變 (保持率=1)", keep_rank == N, "%.4f" % (keep_rank/N))
check("L3b: 鋸齒保持率 < 1 (振幅敏感, ≈0.77)", abs(keep_alt/N - 0.7740) < 0.01,
      "p=%.4f" % (keep_alt/N))

# ══════════════════ L4. exploratory: lepton modes ══════════════════
print("\n" + "=" * 74)
print("L4. [EXPLORATORY 非 pre-registered] lepton modes = {1,5,9} (等差 4)")
print("=" * 74)
lepton_modes = sorted(MODES[i] for i, f in enumerate(ORDER) if f in LEP)
print("  lepton 對應 mode: %s" % lepton_modes)
is_ap = len(set(lepton_modes[1]-lepton_modes[0] for _ in [0])) == 1
# 真正等差: 檢查公差一致
deltas = [lepton_modes[i+1]-lepton_modes[i] for i in range(2)]
print("  公差: %s ⟹ 等差4? %s" % (deltas, deltas[0] == deltas[1] == 4))
print("  P(指定 3-subset) = 1/C(8,3) = 1/56 ≈ 0.018 — 🎯 事件後觀察, 唔當 PASS")
print("  盲測設計 (下一輪 pre-register): H0 = quark/lepton 兩種 label 隨機",
      "刷新 8! 次, 命中『lepton modes 等差4』+『全奇位』聯合頻率")

out = {"L1": {"p_lepton_all_odd": p1, "cnt_allodd": cnt_allodd, "cnt_total": cnt_total},
       "L2": {"block_ratios": {}},
       "L3": {"rank_keep": keep_rank/N, "alt_keep": keep_alt/N},
       "L4": {"lepton_modes": lepton_modes, "deltas": deltas, "p_nominal": 1/56}}
for g in range(3):
    blk = [f for f in ORDER if BLOCK_G[f] == g]
    ev = [cf[f] for f in blk if (ORDER.index(f)+1) % 2 == 0]
    od = [cf[f] for f in blk if (ORDER.index(f)+1) % 2 != 0]
    g_ev = math.exp(sum(math.log(e) for e in ev)/len(ev))
    g_od = math.exp(sum(math.log(o) for o in od)/len(od))
    out["L2"]["block_ratios"]["gen%d" % (g+1)] = g_ev/g_od
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "09_flow_identity.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n結果: %d PASS / %d FAIL (L4 exploratory 唔計)" % (PASS, FAIL))