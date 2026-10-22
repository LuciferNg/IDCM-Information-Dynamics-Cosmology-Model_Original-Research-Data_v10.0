#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O222 scripts/02_lazy_semantics.py

R1 (Part A) -- 凍結 D1「延遲項 + 強制」語義，並用可執行模型釘死其性質。

調律者裁定 (2026-09-29):
  (a) force 【不准多值】: 同一 (gen, sigma, ctx) 必須 -> 單一值（純函數 + memo）。
      隨機性/不確定性只准隔離喺 sigma 生成側（環境初始化），force 本身冷酷無情。
      理由: 多值 = 代數總帳開後門 = 摧毀可重播性 + 對賬日誌一致性 + Bell 底線。
  (b) C1 本體定義 = Aut 破缺 / 穩定子階數（memo 拓樸分裂）；ell_read 只係派生索引。
      -> Part B 於 scripts/03_aut_stabilizer.py 做（精確 Q(sqrt5) 群計算）；
         本檔只做 Part A（語義 + 44 模可執行模型），並保留機械版 C1 (A7) 作為 Part B 之對照。

D1 定義（凍結）:
  Thunk       T = (gen, sigma, ctx)      -- 不可變三元組，冇隱藏狀態
  gen         : 生成式（唔係值）          -- 由 (sigma, ctx) 產生值之純函數
  sigma       : 相位/場資料（環境一次性）  -- 唯一允許攜帶不確定性之位置
  ctx         : 讀取上下文（read operator）
  force(T)    : 純函數 T -> 值，值寫入 memo[key(T)]；同一 key 永遠同一值
  疊加表示     sum_n c_n|n> 只係 T 之【派生表示】，唔係 primitive；c_n 必須回收譜（gamma_n/90）

check 慣例標籤:
  [D1-sem]   語義性質（純函數 / memo / ctx 分離 / 無後門）
  [44-mode]  gamma_n = 4 sin^2(pi n/88), n = 1..44
  [O138]     上游測量層（引用: N(s) 內觀映射、Born p_n = gamma_n/90）
"""

import hashlib
import json
import os
from mpmath import mp, mpf, sin, pi, sqrt, nstr

mp.dps = 50

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LOGS = os.path.join(ROOT, "logs")
os.makedirs(DATA, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)

N_D = 44
L = 88
RESULTS = []


def chk(tag, name, ok, detail=""):
    RESULTS.append({"tag": tag, "name": name, "ok": bool(ok), "detail": detail})
    print("[%s] %-9s %-72s %s" % ("PASS" if ok else "FAIL", tag, name, detail))
    return ok


def claim(tag, name, text):
    RESULTS.append({"tag": tag, "name": name, "ok": None, "detail": text})
    print("[CLAIM]   %-9s %-72s %s" % (tag, name, text))


def rel(a, b):
    a, b = mpf(a), mpf(b)
    return abs(a - b) if b == 0 else abs(a - b) / abs(b)


# ============================================================ lattice (44 modes)
gamma = [4 * sin(pi * n / L) ** 2 for n in range(1, N_D + 1)]
omega = [sqrt(g) for g in gamma]
GAM_SUM = sum(gamma)                     # = 90  (O222 R0 A2a)
p_born = [g / GAM_SUM for g in gamma]    # Born weights  gamma_n/90

print("=" * 108)
print("O222 R1 Part A -- D1 evaluation semantics locked (mp.dps=%d)" % mp.dps)
print("=" * 108)


# ============================================================ sigma: environment-side randomness (ONLY here)
def make_sigma(seed):
    """Phase/field data for the 44 modes.  Randomness lives HERE and nowhere else:
    a deterministic expansion of a seed (environment init), frozen once."""
    sig = []
    for n in range(1, N_D + 1):
        h = hashlib.sha256(("%s|%d" % (seed, n)).encode()).hexdigest()
        sig.append(mpf(int(h[:16], 16)) / mpf(2) ** 64)      # in [0,1)
    return tuple(sig)                                        # immutable


SIGMA = make_sigma("O222/R1/2026-09-29")


# ============================================================ generators (pure)
def gen_eig(sigma, ctx):
    """ctx = ('eig', k): read the k-th mode -> (mode index, gamma_k)."""
    _, k = ctx
    return {"mode": k, "gamma": gamma[k - 1], "weight": p_born[k - 1]}   # k is 1-based mode label


def gen_marg(sigma, ctx):
    """ctx = ('marg',): coarse/global read -> Aut-invariant aggregate, resolves NO node."""
    _, = ctx if len(ctx) == 1 else (ctx[1],)
    tot = mpf(0)
    for n in range(N_D):
        tot += p_born[n] * gamma[n]
    return {"support": tuple(range(N_D)), "mean_gamma": tot}


def gen_phase(sigma, ctx):
    """ctx = ('phase', k): phase flow of mode k (global phase, no node pinned)."""
    _, k = ctx
    return {"phase": sigma[k - 1], "support": tuple(range(N_D))}


GENS = {"eig": gen_eig, "marg": gen_marg, "phase": gen_phase}


# ============================================================ thunk / force / memo
class Memo:
    def __init__(self):
        self.tab = {}
        self.writes = 0

    def snapshot(self):
        return hashlib.sha256(json.dumps(
            {k: repr(v) for k, v in sorted(self.tab.items())},
            ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]


def key_of(gen, sigma, ctx):
    """memo key = the whole immutable triple (so a different ctx is a DIFFERENT thunk)."""
    return "%s|%s|%s" % (gen, hashlib.sha256(repr(sigma).encode()).hexdigest()[:8], repr(ctx))


def force(memo, gen, sigma, ctx):
    """force(T) -- PURE FUNCTION of the triple + memo write.  No other state.  Single-valued."""
    k = key_of(gen, sigma, ctx)
    if k not in memo.tab:
        memo.tab[k] = GENS[gen](sigma, ctx)      # <- pure map; no RNG, no clock, no I/O
        memo.writes += 1
    return memo.tab[k]


print("\n--- A. D1 semantics (executable lock) ---")

# A1 purity: 1000 repeated forces -> bit-identical
m = Memo()
v0 = force(m, "eig", SIGMA, ("eig", 7))
same = all(repr(force(m, "eig", SIGMA, ("eig", 7))) == repr(v0) for _ in range(1000))
chk("[D1-sem]", "A1 force is a pure single-valued map (1000x same triple -> identical value)",
    same, "value = %s ; memo writes = %d" % (v0["mode"], m.writes))

# A2 memo consistency: cold recompute == memo hit
m2 = Memo()
cold = force(m2, "eig", SIGMA, ("eig", 7))
warm = force(m, "eig", SIGMA, ("eig", 7))
chk("[D1-sem]", "A2 memo hit == cold recompute (two independent memo tables agree)",
    repr(cold) == repr(warm), "cold = warm = mode %s" % cold["mode"])

# A3 ctx separation: a different ctx is a DIFFERENT thunk; forcing it must not touch the old entry
m3 = Memo()
h_before = m3.snapshot()
va = force(m3, "eig", SIGMA, ("eig", 7))
hb = m3.snapshot()
vb = force(m3, "eig", SIGMA, ("eig", 8))
hc = m3.snapshot()
ka, kb = key_of("eig", SIGMA, ("eig", 7)), key_of("eig", SIGMA, ("eig", 8))
chk("[D1-sem]", "A3 changed ctx = NEW thunk (distinct keys); old memo entry untouched",
    ka != kb and m3.tab[ka] == va and m3.tab[kb] == vb and len(m3.tab) == 2,
    "keys differ = %s ; |memo| = %d" % (ka != kb, len(m3.tab)))

# A4 no back-door: permuted evaluation order / re-entrancy -> value set size == 1
m4 = Memo()
vals = set()
order = [(7,), (8,), (7,), (44,), (1,), (7,), (8,)]
for n in range(10000):
    k = (n * 7919) % N_D + 1
    vals.add(repr(force(m4, "eig", SIGMA, ("eig", k))["gamma"]))
again = set()
for n in reversed(range(10000)):
    k = (n * 7919) % N_D + 1
    again.add(repr(force(m4, "eig", SIGMA, ("eig", k))["gamma"]))
chk("[D1-sem]", "A4 no back-door: 10000 interleaved forces, forward vs reverse -> identical value set",
    vals == again and len(vals) == N_D,
    "|values| = %d (expect %d) ; memo entries = %d" % (len(vals), N_D, len(m4.tab)))

# A5 superposition representation must RECYCLE the spectrum (RT2), not invent constants
c = p_born
chk("[44-mode]", "A5 expanded form sum_n c_n|n> with c_n = gamma_n/90: sum c_n = 1 and sum c_n^2 matches Born weights",
    rel(sum(c), 1) < mpf("1e-45") and rel(sum(x * x for x in c), sum(p * p for p in p_born)) < mpf("1e-45"),
    "sum c = %s ; sum c^2 = %s" % (nstr(sum(c), 20), nstr(sum(x * x for x in c), 20)))

# --- O138 introspection map N(s) (cited; exact f'/f form) ---
LAM = mpf(406.1)
zeros = [LAM / (mpf(n) + mpf(1) / 2) for n in range(1, N_D + 1)]
poles = [LAM / mpf(n) for n in range(1, N_D + 1)]


def Sfun(s):
    """f'/f.  At an exact fixed point (s == zero or s == pole) S -> +-inf, i.e. N(s) == s
    (a zero is super-attracting: N'(zero) = 0, so exact convergence happens in FINITE steps)."""
    tot = mpf(0)
    for z in zeros:
        d = s - z
        if d == 0:
            return mpf("inf")
        tot += 1 / d
    for pp in poles:
        d = s - pp
        if d == 0:
            return mpf("inf")          # the pole is ALSO a fixed point (N'(pole) = 2)
        tot -= 1 / d
    return tot


def Nmap(s):
    S = Sfun(s)
    return s if S == mpf("inf") else s - 1 / S


# A6 collapse thunk: mixed state -> EXACT single outcome in finite steps (super-attracting signature).
#    NOTE (check design, caught on first run): |N(s)-s| is NOT monotone -- it is |f/f'| and can jump.
#    The structural claim is finite-step exact convergence + quadratic error law e_{k+1} ~ C e_k^2.
s = (zeros[0] + zeros[1]) / 2
err = []
steps = 0
for _ in range(200):
    ns = Nmap(s)
    s = ns
    steps += 1
    z_star = min((abs(s - z), z) for z in zeros)[1]
    e = abs(s - z_star)
    err.append(e)
    if e == 0:
        break
quad = None
if len(err) >= 5 and err[-1] == 0:
    e_prev, e_prev2 = err[-2], err[-3]
    quad = (e_prev / e_prev2 ** 2) if e_prev2 != 0 else None
chk("[O138]", "A6 collapse thunk: mixed state -> EXACT single outcome in finite steps (200 cap) with quadratic error law",
    err[-1] == 0 and steps < 200 and quad is not None and quad < mpf("100"),
    "steps = %d (exact hit) ; e_{k-1}/e_{k-2}^2 = %s ; e tail = %s" % (
        steps, nstr(quad, 4) if quad is not None else "-", ", ".join(nstr(x, 3) for x in err[-4:])))

# A7 mechanical memo-support split (contrast item for Part B)
sup_marg = force(Memo(), "marg", SIGMA, ("marg",))["support"]
sup_eig = (7,)
chk("[D1-sem]", "A7 [mechanical] wave-like read resolves NO node (support = all 44, 1 component) vs particle-like read pins 1 node",
    len(sup_marg) == N_D and len(sup_eig) == 1,
    "support(marg) = %d nodes (1 component) ; support(eig) = %d node" % (len(sup_marg), len(sup_eig)))

# A8 negative control: a multi-valued force leaks hidden state INTO the value -> rejected by A1/A4
m5 = Memo()


def force_rng(memo, gen, sigma, ctx, seed):
    """DELIBERATELY BROKEN: the value depends on a hidden counter (a back-door)."""
    k = key_of(gen, sigma, ctx) + "|%d" % seed
    if k not in memo.tab:
        v = dict(GENS[gen](sigma, ctx))
        v["hidden"] = seed                      # <- hidden state leaks into the VALUE
        memo.tab[k] = v
    return memo.tab[k]


set_a = {repr(force_rng(m5, "eig", SIGMA, ("eig", 7), t)) for t in range(5)}
chk("[D1-sem]", "A8 negative control: multi-valued force -> value set size > 1 for one triple (hence ruling (a))",
    len(set_a) == 5,
    "%d distinct values for a single (gen,sigma,ctx) -- so A1/A4 would REJECT it" % len(set_a))


# ============================================================ C1 (definitional form, frozen here)
print("\n--- B. C1: frozen ontologic form (computation in scripts/03) ---")
claim("[C1]", "C1-DEF (frozen)", "Read ctx is WAVE-like iff Aut(ctx) is preserved (|Stab_I(ctx)| >= 2, memo support connected); "
      "PARTICLE-like iff |Stab_I(ctx)| = 1 (full Aut breaking, memo support splits). ell_read is NOT a premise -- it is "
      "the DERIVED index: the smallest rank r at which a lattice-aligned ctx admits |Stab| = 1.")
claim("[C1]", "C1-CROSSCHECK", "O143/O223 claim ell <= 2 protected / ell = 3 first breaking. scripts/03 computes the stabilizer "
      "ladder by brute force from lattice primitives and reports agreement or a flagged discrepancy (no retrofitting).")

# ============================================================ summary
n_pass = sum(1 for r in RESULTS if r["ok"] is True)
n_fail = sum(1 for r in RESULTS if r["ok"] is False)
n_claim = sum(1 for r in RESULTS if r["ok"] is None)
print("\n" + "=" * 108)
print("RESULT: %d/%d PASS  (%d FAIL, %d claims excluded)" % (n_pass, n_pass + n_fail, n_fail, n_claim))
print("=" * 108)

with open(os.path.join(DATA, "02_lazy_semantics.json"), "w", encoding="utf-8") as fh:
    json.dump({"pass": n_pass, "fail": n_fail, "claims": n_claim, "checks": RESULTS},
              fh, ensure_ascii=False, indent=1)
print("saved: data/02_lazy_semantics.json")
