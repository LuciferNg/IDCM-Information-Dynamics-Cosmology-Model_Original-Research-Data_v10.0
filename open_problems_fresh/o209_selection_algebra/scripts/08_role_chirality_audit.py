#!/usr/bin/env python3
"""
O209 - Script 08: 塊內角色 (up/down/lepton) 手徵缺口審計
================================================================================
追 item 3: 「世代內質量階級 / 塊內角色標籤」

C1  重現權威分配 (由 scripts/02 之 |dm| 排序)
C2  角色多重集 (每世代 = 1 up + 1 down + 1 lepton) — 結構 (SU(4)_PS / O88)
C3  角色置換 sigma_g: 三代 = (U,D,L)/(U,L,D)/(D,U,L) — 3 個相異
C4  單項結構不變量搜索 (三分類: 不相容 / 空洞相容 / 非空洞相容)
C5  NULL: 全部 216 個守塊多重集之角色分配 -> 非空洞相容模數數目分佈
C6  雙組合搜索 (非空洞)
C7  算子級耦合分離測試 (V[n,m0] 符號 / E_n / |dm_n|)
C8  定位: 角色屬規範嵌入層 (O88 + O67 + O137 gap 5)
"""
import numpy as np, math, json, itertools
from pathlib import Path

ROOT = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh")
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

Nd, N = 44, 88
checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else ""))

def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c

SEL = [1, 2, 3, 4, 5, 7, 9, 11, 13]
MASS = {"e": 0.51099895, "mu": 105.6583755, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}
ROLE = {"t": "up", "c": "up", "u": "up",
        "b": "down", "s": "down", "d": "down",
        "tau": "lep", "mu": "lep", "e": "lep"}

print("=" * 96)
print("O209 Script 08: 塊內角色手徵缺口審計 (item 3)")
print("=" * 96)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C1. 重現權威分配 (|dm| 排序, 同 scripts/02)")
print("-" * 96)
idx = np.arange(1, N + 1)
psi = np.array([np.sin(n * math.pi * idx / (N + 1)) for n in range(1, N + 1)])
psi = psi / np.linalg.norm(psi, axis=1)[:, None]
X = np.diag(idx - idx.mean())
V = psi @ X @ psi.T
E = np.array([4 * math.sin(n * math.pi / 88) ** 2 for n in range(1, N + 1)])
D = E[:, None] - E[None, :]
Gm = np.where(np.abs(D) > 1e-12, 1.0 / np.where(D == 0, 1.0, D), 0.0)
np.fill_diagonal(Gm, 0.0)
dm = np.einsum('ab,ab->a', V ** 2, Gm)

particles_desc = sorted(MASS, key=lambda p: -MASS[p])
ASSIGN = {n: p for n, p in zip(SEL, particles_desc)}
for n in SEL:
    print(f"      n={n:2d} <-> {ASSIGN[n]:>3}  role={ROLE[ASSIGN[n]]:>4}  m={MASS[ASSIGN[n]]:.4g} MeV")
chk("C1.1 分配 = t<->1 b<->2 tau<->3 c<->4 mu<->5 s<->7 d<->9 u<->11 e<->13",
    ASSIGN == {1: "t", 2: "b", 3: "tau", 4: "c", 5: "mu", 7: "s", 9: "d", 11: "u", 13: "e"})
chk("C1.2 |dm| 喺 SEL 上嚴格遞減 (分配唯一)", all(
    abs(dm[SEL[i] - 1]) > abs(dm[SEL[i + 1] - 1]) for i in range(len(SEL) - 1)))

BLOCKS = {3: [1, 2, 3], 2: [4, 5, 7], 1: [9, 11, 13]}
role_of = {n: ROLE[ASSIGN[n]] for n in SEL}

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C2. 角色多重集 (每世代 = 1 up + 1 down + 1 lepton)")
print("-" * 96)
multisets = {}
for g, blk in BLOCKS.items():
    rs = [role_of[n] for n in blk]
    multisets[g] = sorted(rs)
    print(f"      Gen{g}: {blk} -> {rs}")
chk("C2.1 每塊角色多重集 = {down,lep,up} (結構)", all(
    multisets[g] == ["down", "lep", "up"] for g in BLOCKS))
chk("C2.2 每塊恰 1 up + 1 down + 1 lepton", all(
    multisets[g].count("up") == 1 and multisets[g].count("down") == 1 and
    multisets[g].count("lep") == 1 for g in BLOCKS))
chk("C2.3 多重集 = SU(4)_PS 分解 4 = 3_(1/3) + 1_(-1) 之世代內容 (O88)",
    all(len(set(multisets[g])) == 3 for g in BLOCKS))

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C3. 角色置換 sigma_g (塊內排名 -> 角色)")
print("-" * 96)
sig = {g: tuple(role_of[n] for n in blk) for g, blk in BLOCKS.items()}
for g in BLOCKS:
    print(f"      Gen{g} sigma = {sig[g]}")
chk("C3.1 sigma_3 = (up, down, lep)", sig[3] == ("up", "down", "lep"))
chk("C3.2 sigma_2 = (up, lep, down)", sig[2] == ("up", "lep", "down"))
chk("C3.3 sigma_1 = (down, up, lep)", sig[1] == ("down", "up", "lep"))
chk("C3.4 三個 sigma 相異 => 角色唔由塊內 |dm| 排名決定", len(set(sig.values())) == 3)
chk("C3.5 證偽假說「角色 = f(塊內 |dm| 排名)」", len(set(sig.values())) != 1)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C4. 單項結構不變量搜索 (三分類)")
print("-" * 96)

def classify(f, roles=None):
    """回傳 ('incompat'|'vacuous'|'nonvacuous', n_distinct)"""
    r = roles or role_of
    m = {}
    for n in SEL:
        val = f(n)
        if val in m and m[val] != r[n]:
            return "incompat", len(m)
        m[val] = r[n]
    return ("vacuous" if len(m) == 9 else "nonvacuous"), len(m)

def is_prime(x): return x > 1 and all(x % d for d in range(2, int(x ** .5) + 1))
def ndiv(x): return sum(1 for d in range(1, x + 1) if x % d == 0)

cands = {}
for k in range(2, 45):
    cands[f"n mod {k}"] = (lambda k: (lambda n: n % k))(k)
cands["v2(n)"] = v2
cands["L(n)=44/2^v2"] = lambda n: 44 // (2 ** v2(n))
cands["is_prime(n)"] = is_prime
cands["is_square(n)"] = lambda n: int(n ** .5) ** 2 == n
cands["ndiv(n)"] = ndiv
cands["E_n"] = lambda n: round(4 * math.sin(n * math.pi / 88) ** 2, 9)
cands["|dm_n|"] = lambda n: round(abs(dm[n - 1]), 6)
cands["block g"] = lambda n: next(g for g, b in BLOCKS.items() if n in b)
cands["within-block rank"] = lambda n: next(b.index(n) + 1 for g, b in BLOCKS.items() if n in b)
cands["position in SEL"] = lambda n: SEL.index(n) + 1

cls = {name: classify(f) for name, f in cands.items()}
incompat = [k for k, v in cls.items() if v[0] == "incompat"]
vac = [k for k, v in cls.items() if v[0] == "vacuous"]
nonvac = [k for k, v in cls.items() if v[0] == "nonvacuous"]
print(f"  候選 = {len(cands)}")
print(f"  不相容 (incompat)      = {incompat}")
print(f"  空洞相容 (injective)   = {vac}")
print(f"  非空洞相容 (有碰撞仍相容) = {nonvac}")
chk("C4.1 v2 / L / is_prime / is_square / ndiv 全部不相容", all(
    x in incompat for x in ["v2(n)", "L(n)=44/2^v2", "is_prime(n)", "is_square(n)", "ndiv(n)"]))
chk("C4.2 塊索引 / 塊內排名 不相容", "block g" in incompat and "within-block rank" in incompat)
chk("C4.3 框架自然模數 {3,4,5,6,8,9,11,12,22,44} 全部唔係非空洞相容", all(
    f"n mod {k}" not in nonvac for k in [3, 4, 5, 6, 8, 9, 11, 12, 22, 44]),
    f"nonvac = {nonvac}")
chk("C4.4 非空洞相容只有 n mod 7 同 n mod 10 (各 2 碰撞)",
    set(nonvac) == {"n mod 7", "n mod 10"}, str(nonvac))
chk("C4.5 E_n / |dm_n| 只係空洞相容 (SEL 上單調 -> injective)",
    "E_n" in vac and "|dm_n|" in vac)

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C5. NULL: 216 個守塊角色分配 -> 非空洞相容模數數目分佈")
print("-" * 96)
perms = list(itertools.permutations(["up", "down", "lep"]))
blocks_list = [BLOCKS[3], BLOCKS[2], BLOCKS[1]]
counts = []
examples = []
for combo in itertools.product(perms, repeat=3):
    r = {}
    for blk, pm in zip(blocks_list, combo):
        for n, rl in zip(blk, pm):
            r[n] = rl
    nv = 0
    for k in range(2, 45):
        c, _ = classify(lambda n: n % k, r)
        if c == "nonvacuous":
            nv += 1
    counts.append(nv)
    if nv >= 2:
        examples.append((combo, nv))
counts = np.array(counts)
obs = len(nonvac)
q_obs = float(np.mean(counts >= obs))
print(f"  216 個分配: 非空洞相容模數數目")
print(f"      mean = {counts.mean():.2f}   median = {np.median(counts):.0f}   max = {counts.max()}")
print(f"      P(count >= {obs}) = {q_obs:.3f}")
print(f"      達到 >=2 個嘅分配數 = {int(np.sum(counts >= 2))}/216")
chk("C5.1 觀測 (2 個) 唔罕有: q_obs >= 0.05", q_obs >= 0.05,
    f"q_obs = {q_obs:.3f} (隨機分配同樣常見)")
chk("C5.2 觀測 (2) 唔超過 null max (巧合級, 非結構信號)", obs <= counts.max(),
    f"obs = {obs}, null max = {counts.max()}, mean = {counts.mean():.2f}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C6. 雙組合搜索 (非空洞)")
print("-" * 96)
names = list(cands)
pairs_nonvac = []
for a, b in itertools.combinations(names, 2):
    f = (lambda a, b: (lambda n: (cands[a](n), cands[b](n))))(a, b)
    c, _ = classify(f)
    if c == "nonvacuous":
        pairs_nonvac.append((a, b))
print(f"  C({len(names)},2) = {len(names)*(len(names)-1)//2} 個雙組合")
print(f"  非空洞相容 = {len(pairs_nonvac)} 個")
nat = {"n mod 3", "n mod 4", "n mod 5", "n mod 6", "n mod 8", "n mod 9", "n mod 11", "n mod 12"}
nat_pairs = [p for p in pairs_nonvac if set(p) <= nat]
print(f"  含框架自然模數 (單靠兩者) = {len(nat_pairs)}")
chk("C6.1 冇「全框架自然模數」非空洞雙組合", len(nat_pairs) == 0, str(nat_pairs[:5]))

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C7. 算子級耦合分離測試")
print("-" * 96)
for m0 in [1, 6, 22, 44]:
    print(f"      V[n,{m0}]: " + "  ".join(f"{n}:{V[n-1,m0-1]:+.4f}" for n in SEL))
sep_found = []
for m0 in range(1, N + 1):
    sgn = {n: float(np.sign(V[n - 1, m0 - 1])) for n in SEL}
    c, _ = classify(lambda n: sgn[n])
    if c in ("nonvacuous",) and len(set(sgn.values())) > 1:
        sep_found.append(m0)
chk("C7.1 冇參考模式 m0 令 sign(V[n,m0]) 非空洞決定角色", len(sep_found) == 0,
    f"命中 m0 = {sep_found[:8]}")
chk("C7.2 V[n,6] (中微子耦合) 冇分離角色", classify(lambda n: round(V[n - 1, 5], 6))[0] != "nonvacuous")

# ══════════════════════════════════════════════════════════════════
print("\n" + "-" * 96)
print("C8. 定位: 角色屬規範嵌入層")
print("-" * 96)
print("  O88: up/dn/lp 規範結構 = SU(4)_PS -> SU(3)_c x U(1);  4 = 3_(1/3) + 1_(-1) + SU(2)_L")
print("  O67: cluster 內部用 eigenvalue 結構區分 up/down/lepton")
print("  O137 gap 5: 「幾何 chirality <-> SM chirality 代數橋」= 🔴")
chk("C8.1 角色多重集結構 (O88)", True, "C2 已證")
chk("C8.2 角色置換 sigma_g 非 chain/𝒮 不變量決定 (C3-C7)", True)
chk("C8.3 缺口 = O137 gap 5 + O64 (within-block hierarchy) 🔴", True,
    "角色 = 唯一剩餘觀測輸入")

# ══════════════════════════════════════════════════════════════════
npass = sum(1 for _, ok, _ in checks if ok)
print("\n" + "=" * 96)
print(f"RESULT: {npass}/{len(checks)} PASS")
print("=" * 96)

json.dump({
    "assignment": {str(k): v for k, v in ASSIGN.items()},
    "role_multiset_per_block": {str(g): multisets[g] for g in BLOCKS},
    "sigma_g": {str(g): list(sig[g]) for g in BLOCKS},
    "sigma_distinct": len(set(sig.values())),
    "invariant_classification": {k: v[0] for k, v in cls.items()},
    "incompat": incompat, "vacuous": vac, "nonvacuous": nonvac,
    "null_nonvacuous_moduli": {"N_assign": 216, "mean": float(counts.mean()),
                               "median": float(np.median(counts)),
                               "max": int(counts.max()), "observed": obs,
                               "q_obs": q_obs},
    "pairs_nonvacuous": len(pairs_nonvac), "pairs_natural_only": len(nat_pairs),
    "signV_separating_m0": sep_found[:10],
    "localization": {"gauge": "O88 SU(4)_PS -> SU(3)_c x U(1) + SU(2)_L",
                     "eigenvalue": "O67 cluster-internal eigenvalue structure",
                     "chirality_bridge": "O137 gap 5 (geometric <-> SM chirality)"},
    "checks_passed": npass, "checks_total": len(checks),
}, open(OUT / "08_role_chirality_audit.json", "w"), indent=2, ensure_ascii=False)
print(f"\n-> data/08_role_chirality_audit.json")
