#!/usr/bin/env python3
"""
O206 — 第十輪 scripts/30: C_f 生成器 Hunt（pre-registered pool + 密度 null）
=============================================================================
承接: scripts/29 裁決後，C_f 生成器問題精確化:
  m_f = M₀·γ_n·C_f, n ∈ A₅ 合法集 {1,2,3,4,5,7,9,11}, t 歸 VEV 機制
  目標 = 8 個 C_f 值 (重框跨度 71.2×, Φ 目錄 0/8 命中)

標準（O137 方法論鐵律 + O120 closeout 紀律）:
  ① 池 = pre-registered 結構算子族（零新常數, 禁 φ-power fitting, 禁後驗加數入池）
  ② 池定義喺執行前凍結 (sha256) — 輸出含 pool_hash
  ③ 每個目標報: 最佳池命中 + dev + q_obs(池密度窗內命中數)
  ④ 聯合 null: log-uniform 隨機 8 目標 × 10⁵ → 命中數分布 → p 值
  ⑤ 證據門檻: dev < 1e-3 ∧ 聯合 MC p < 0.05；否則誠實負結果
──────────────────────────────────────────────────────────────────────
POOL 定義（pre-registered，只此一次）:
  S = 結構常數集（全部 corpus 已有身份）:
      {L₀..L₁₄, F₂..F₂₀, B=4, B²=16, B³=64, B⁴=256, N_gen=3, N_d=44, M=33,
       CY₃=134, h11=36, h21=98, μ²=2, L₆=18, F₅=5, K_tree=33, 88, 176, 946,
       123, 137, 90(Σγ), 46(Σγ_even), 45(Σγ_odd), 60, 42, 37, 44, 41, 33,
       47, 48, 50, 51 (φ9 索引), 26(2F₇), 22(N_d/2), 17(F_proj), 8, 40}
       ⟹ 去重後正整數。
  形式族 (值域 [0.1, 1e4]):
    F1  s/c                         (s,c ∈ S)
    F2  (s1±s2)/c                   (s1,s2,c ∈ S; 正分母)
    F3  γ_i/γ_j  (i,j ∈ 1..44, i≠j) (弦比, 投影類)
    F4  Φ 目錄 18 值 = 1+x₃x₃'      (x₃∈{1,5,9}, x₃'∈{0,1,3,4,6,7})
  γ-比 ∈ ℚ(sin(π/88)) — 60 dps 計算。
  ⚠️ 禁區: 唔加 TARGET 鄰近值入池; 唔准事後改池。
"""
import math, json, os, hashlib, random, sys
import mpmath as mp
mp.mp.dps = 60

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1
    else: FAIL += 1
    print(f"  {'✅' if cond else '❌'} {name}" + (f"  [{detail}]" if detail and not cond else ""))

random.seed(20261006)
HEX = "0123456789abcdef"
def frac_simple(x, tol=2e-3, bmax=200):
    """最簡有理候選（報告用）: 最小分母 b 內第一個命中。"""
    for b in range(1, bmax + 1):
        a = round(float(x) * b)
        if a <= 0: continue
        if abs(a/b - float(x)) <= tol * max(1.0, abs(float(x))):
            return (a, b)
    return None

MPZ = mp.mpf
def mp_sinpi_ratio(a, b):
    return mp.sin(mp.pi * a / b)

# ── 目標（t 除外；8 個）────────────────────────────────────────────
M0 = 27.900915
gam = lambda n: 4 * mp.sin(mp.pi * n / 88)**2
PDG = {"e":0.51099895, "u":2.16, "d":4.67, "s":93.4, "mu":105.6583755,
       "c":1270.0, "tau":1776.86, "b":4180.0}
A5_N = {"e":1, "u":2, "d":3, "s":4, "mu":5, "c":7, "tau":9, "b":11}
Cf = {f: mp.mpf(PDG[f]) / (mp.mpf(M0) * gam(A5_N[f])) for f in PDG}
TARGETS = {f: Cf[f] for f in PDG}
print("TARGETS (8):")
for f, v in TARGETS.items():
    print(f"  {f:>4} = {mp.nstr(v, 12)}")

# ── S 集合（pre-registered）────────────────────────────────────────
L = [round(mp.mpf(2)) ]
a, b_ = 2, 1
L = [2, 1]
for k in range(2, 15):
    L.append(L[-1] + L[-2])
F = [0, 1]
for k in range(2, 21):
    F.append(F[k-1] + F[k-2])
S = set(L) | set(F[2:]) | {4, 16, 64, 256, 3, 44, 33, 134, 36, 98, 2, 18, 5,
                           88, 176, 946, 123, 137, 90, 46, 45, 60, 42, 37, 41,
                           47, 48, 50, 51, 26, 22, 17, 8, 40}
S = {int(s) for s in S if 1 <= s <= 10**6}
S_sorted = sorted(S)
print(f"\nS = {len(S_sorted)} 個結構常數: {S_sorted}")

# ── 池建構 ─────────────────────────────────────────────────────────
pool_vals = set(); pool_forms = {}
def add(v, label):
    if 0.1 <= v <= 1e4:
        key = mp.nstr(v, 12)
        pool_vals.add(key)
        pool_forms.setdefault(key, []).append(label)

for s in S:
    add(mp.mpf(s), f"S:{s}")
for c in S:
    for s in S:
        add(mp.mpf(s)/mp.mpf(c), f"{s}/{c}")
for c in S:
    for s1 in S:
        for s2 in S:
            add((mp.mpf(s1)+mp.mpf(s2))/mp.mpf(c), f"({s1}+{s2})/{c}")
            if s1 > s2:
                add((mp.mpf(s1)-mp.mpf(s2))/mp.mpf(c), f"({s1}-{s2})/{c}")
# γ 比 (44×43/2 pairs)
for i in range(1, 45):
    gi = gam(i)
    for j in range(i+1, 45):
        add(gi/gam(j), f"γ{i}/γ{j}")
        add(gam(j)/gi, f"γ{j}/γ{i}")
# Φ 目錄
for x3 in (1, 5, 9):
    for x3p in (0, 1, 3, 4, 6, 7):
        add(mp.mpf(1 + x3*x3p), f"Φ:{1+x3*x3p}")

POOL = sorted((mp.mpf(k) for k in pool_vals), key=lambda x: float(mp.log(x)))
POOL_HASH = hashlib.sha256((",".join(sorted(pool_vals))).encode()).hexdigest()[:16]
print(f"\nPOOL = {len(POOL)} 值 (0.1–1e4)，pool_hash = {POOL_HASH}")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "30_pool_frozen.json"), "w") as f:
    json.dump({"pool_size": len(POOL), "pool_hash": POOL_HASH,
               "pool_excerpt": [mp.nstr(v, 8) for v in POOL[:20]]}, f)

# ── 逐目標命中 ─────────────────────────────────────────────────────
print("\n" + "=" * 78); print("逐目標: 最佳池命中 (dev 窗 {1e-2, 1e-3, 1e-4})"); print("=" * 78)
def pool_hits(tgt, delta):
    lo, hi = tgt/(1+delta), tgt*(1+delta)
    import bisect
    i0 = bisect.bisect_left(POOL, lo)
    i1 = bisect.bisect_right(POOL, hi)
    return POOL[i0:i1]

summary = {}
for f, t in TARGETS.items():
    hi = pool_hits(t, 1e-2)
    best = min(hi, key=lambda v: abs(float(mp.log(v/t)))) if hi else None
    dev = float(abs(mp.log(best/t))) if best else float("inf")
    n3, n4 = len(pool_hits(t, 1e-3)), len(pool_hits(t, 1e-4))
    summary[f] = {"best": mp.nstr(best, 10) if best else None,
                  "dev": dev, "hits_1e-3": n3, "hits_1e-4": n4,
                  "frac": frac_simple(t)}
    if best:
        forms = pool_forms[mp.nstr(best, 12)] if mp.nstr(best,12) in pool_forms else ["?"]
        print(f"  {f:>4} C_f={mp.nstr(t,8):>10}  最佳={mp.nstr(best,10):>10}  dev={dev:.2e}  "
              f"(1e-3:{n3}, 1e-4:{n4})  {forms[0][:46]}")
    else:
        print(f"  {f:>4} C_f={mp.nstr(t,8):>10}  1% 窗無命中")

# ── 聯合 null MC ───────────────────────────────────────────────────
print("\n" + "=" * 78); print("聯合 null: log-uniform 8 目標 × 10⁵"); print("=" * 78)
LOGLO, LOGHI = math.log(3.5), math.log(260.0)
def rand_pool_count_hits(delta):
    cnt = 0
    for _ in range(len(TARGETS)):
        t = mp.mpf(math.exp(random.uniform(LOGLO, LOGHI)))
        cnt += len(pool_hits(t, delta))
    return cnt
for delta, label in [(1e-3, "1e-3"), (1e-4, "1e-4")]:
    obs = sum(summary[f]["hits_1e-3" if label == "1e-3" else "hits_1e-4"] for f in TARGETS)
    N = 100_000
    hits = [rand_pool_count_hits(delta) for _ in range(N)]
    p = sum(1 for h in hits if h >= obs) / N
    med = sorted(hits)[N//2]
    print(f"  δ={label}: 觀測命中總數 = {obs} | MC 中位 = {med} | P(≥obs) = {p:.4f}")
    check(f"δ={label} 聯合 MC p < 0.05", p < 0.05, f"p={p:.4f}")
    summary[f"joint_{label}"] = {"obs": obs, "mc_median": med, "p": p}

# ── 有理數候選報表（報告用，非證據）───────────────────────────────
print("\n" + "=" * 78); print("有理數候選（對照 CI: C_e=18/5 已 pre-registered）"); print("=" * 78)
for f in ["e","mu","s","c","tau","b","u","d"]:
    v = TARGETS[f]; fr = frac_simple(v)
    if fr:
        a, b_ = fr
        print(f"  {f:>4}: {mp.nstr(v,8)} ≈ {a}/{b_}  (dev {abs(a/b_ - float(v))/float(v)*100:.3f}%)")
    else:
        print(f"  {f:>4}: {mp.nstr(v,8)} — 無 ≤0.2% 有理數候選")

print("\n" + "=" * 78)
print(f"結果: {PASS} PASS / {FAIL} FAIL" + "（聯合 null 決定證據）")
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data",
                       "30_cf_hunt.json"), "w") as f:
    json.dump({k: (str(v) if isinstance(v, mp.mpf) else v) for k, v in summary.items()}, f,
              ensure_ascii=False, indent=1, default=str)
sys.exit(1 if FAIL else 0)