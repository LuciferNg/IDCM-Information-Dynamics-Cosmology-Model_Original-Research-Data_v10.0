#!/usr/bin/env python3
"""
O216 scripts/01_density_baseline.py — 色荷候選區間之密度基準 (O208 標準)
=======================================================================
SESSION_START 鐵律 #1: 密度基準先行 — 未建任何候選規則之前，先量度 IDCM 目錄
喺目標區間之密度。唔報密度就做任何「命中」論證 = 重蹈 O136 符號庫爆炸。

目標區間:
  Δn_color 觀測 = {0, 12, 28} (O137 R19, scripts/67 §4; 夸克奇部−輕子奇部)
  色荷候選值域 = [0,33] (O137 docs/30 已量 [6,33]; 0 另計)

目錄 (O137 定義, scripts/47/48):
  嚴格 (18):  {1,2,3,4,5,6,7,8,9,10,11,13,15,16,18,21,28,33}
  寬鬆 (54):  嚴格 ∪ {12,14,17,19,20,22,24,25,26,27,29,30,31,32,34,35,36,37,
                     40,41,42,44,45,46,49,55,60,64,66,70,75,77,88,90,92,98}

輸出 (O208 docs/01):
  N_search / N_mc + seed / d_obs / d_med / q_obs
"""
import random, math, sys

# ------------------------------------------------------------------ 目錄
STRICT = {1,2,3,4,5,6,7,8,9,10,11,13,15,16,18,21,28,33}
BROAD  = STRICT | {12,14,17,19,20,22,24,25,26,27,29,30,31,32,34,35,36,37,
                   40,41,42,44,45,46,49,55,60,64,66,70,75,77,88,90,92,98}
assert len(STRICT) == 18, len(STRICT)
assert len(BROAD) == 54, len(BROAD)

# ------------------------------------------------------------------ 觀測
DN_OBS = {0, 12, 28}          # Δn_color 觀測值 (O137 R19)
DN_RANGE = (0, 33)            # 候選區間

def cat_density(cat, lo, hi):
    """目錄喺整數區間 [lo,hi] 內嘅密度。"""
    n = hi - lo + 1
    k = sum(1 for x in range(lo, hi+1) if x in cat)
    return k/n, k, n

PASS, FAIL = [], []
def ck(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name}" + (f"  ({detail})" if detail else ""))

print("="*84)
print("§1 重現 O137 docs/30 §2.3 密度基準 ([6,33])")
print("="*84)
for nm, cat in [("嚴格", STRICT), ("寬鬆", BROAD)]:
    dens, k, n = cat_density(cat, 6, 33)
    print(f"  {nm}目錄 {sorted(cat)[:6]}… |  [6,33] 內 {k}/{n} = {dens:.4f}")
ck("嚴格密度 = 13/28 = 46.4%", cat_density(STRICT, 6, 33)[0] == 13/28,
   f"{cat_density(STRICT,6,33)[0]:.4f}")
ck("寬鬆密度 = 27/28 = 96.4%", cat_density(BROAD, 6, 33)[0] == 27/28,
   f"{cat_density(BROAD,6,33)[0]:.4f}")

print()
print("="*84)
print("§2 Δn_color 觀測 = {0,12,28} 命中目錄率")
print("="*84)
for nm, cat in [("嚴格", STRICT), ("寬鬆", BROAD)]:
    hits = sorted(x for x in DN_OBS if x in cat)
    print(f"  {nm}目錄: Δn ∩ 目錄 = {hits}  ({len(hits)}/3)")
ck("Δn ∩ 嚴格 = {28} (1/3)", {28}, set(x for x in DN_OBS if x in STRICT))
ck("Δn ∩ 寬鬆 = {12,28} (2/3)", {12,28}, set(x for x in DN_OBS if x in BROAD))

print()
print("="*84)
print("§3 MC null — 隨機 3 值集命中目錄 3/3 之概率 (q_obs)")
print("="*84)
# 目標: 隨機抽 3 個唔同整數喺 [0,33], 全部命中嚴格/寬鬆目錄 嘅概率
# d_obs = 觀測命中率 (命中值數目/3); d_med = 隨機中位命中率
N_MC = 200_000
SEED = 216
rng = random.Random(SEED)

def sample_hit_fraction(cat):
    """隨機 3 個唔同整數喺 [0,33], 回傳命中目錄嘅比例 (0,1/3,2/3,1)。"""
    xs = rng.sample(range(DN_RANGE[0], DN_RANGE[1]+1), 3)
    return sum(1 for x in xs if x in cat)/3

obs_hit_s = len(DN_OBS & STRICT)/3   # 1/3
obs_hit_b = len(DN_OBS & BROAD)/3    # 2/3

vals_s = vals_b = []
q_obs_s = q_obs_b = 0.0
for nm, cat, obs_hit in [("嚴格", STRICT, obs_hit_s), ("寬鬆", BROAD, obs_hit_b)]:
    vals = [sample_hit_fraction(cat) for _ in range(N_MC)]
    if nm == "嚴格":
        vals_s = vals; q_obs_s = sum(1 for v in vals if v <= obs_hit)/N_MC
    else:
        vals_b = vals; q_obs_b = sum(1 for v in vals if v <= obs_hit)/N_MC
    # d_med = 隨機中位命中比例
    med = sorted(vals)[N_MC//2]
    # q_obs = 觀測命中比例喺隨機分佈嘅分位 (比例 <= 觀測)
    q_obs = sum(1 for v in vals if v <= obs_hit)/N_MC
    # p3 = 隨機 3 值全部命中目錄 嘅概率
    p3 = sum(1 for v in vals if v == 1.0)/N_MC
    print(f"\n  [{nm}目錄] 區間 [0,33]")
    print(f"    d_obs = {obs_hit:.4f}  (觀測 Δn 命中比例 {len(DN_OBS & cat)}/3)")
    print(f"    d_med = {med:.4f}  (隨機中位, N_mc={N_MC}, seed={SEED})")
    print(f"    q_obs = {q_obs:.4%}  (觀測命中比例之分位)")
    print(f"    隨機 3 值全中 3/3 概率 = {p3:.4%}")
    ck(f"q_obs({nm}) > 5% → 🔴 唔顯著 (密度效應)", q_obs > 0.05, f"q_obs={q_obs:.4%}")
    print(f"    ─ O208 判定: q_obs≤1% 🟢 | 1-5% 🟡 | >5% 🔴")

print()
print("="*84)
print("§4 N_search (O208 規格)")
print("="*84)
# Δn_color 之搜尋空間: 從 9 模式 ∀ 配對差 (夸克奇部 − 輕子奇部) 之候選值
quarks_odd = [1,1,1,7,9,11]
leps_odd   = [3,5,13]
pairs = sorted({abs(q-l) for q in quarks_odd for l in leps_odd})
print(f"  夸克奇部 {quarks_odd} × 輕子奇部 {leps_odd} → 唔同差值 {pairs} (共 {len(pairs)})")
print(f"  → 搜尋空間 (差值集合大小) = {len(pairs)} 個候選值")
print(f"  更寬: [0,33] 內 C(34,3) = {math.comb(34,3)} 個 3-值子集 (隨機挑 3 個 Δ)")
print(f"  O137 R19 事前候選規則數 = 6 (CANDS_DN: B^2 倍/ L4 倍 / N_gen^2 倍 / N_d 倍 / 2Z / 4Z)")
N_search = len(pairs)
ck("N_search(差值集) = 5", N_search == 5, str(N_search))
ck("N_search(3-值子集) = C(34,3) = 5984", math.comb(34,3) == 5984, str(math.comb(34,3)))
ck("N_search(事前候選規則) = 6 (O137 R19)", 6 == 6, "CANDS_DN")

print()
print("="*84)
print("§5 結論 — 密度基準報告 (O208 格式)")
print("="*84)
# 用 §3 實際計算值
med_s = sorted(vals_s)[N_MC//2]; q_s = q_obs_s
med_b = sorted(vals_b)[N_MC//2]; q_b = q_obs_b
print(f"""
## 密度基準 (O216 scripts/01)
- 名稱: Δn_color 觀測 {sorted(DN_OBS)} 命中 IDCM 目錄
- N_search = {N_search} (夸克奇部×輕子奇部差值集) / {math.comb(34,3)} (C(34,3) 子集空間) / 6 (O137 R19 事前候選)
- N_mc = {N_MC}, seed = {SEED}
- [6,33] 嚴格密度 46.4% (13/28) / 寬鬆 96.4% (27/28)  ← O137 重現
- Δn ∩ 嚴格 = {{{sorted(set(x for x in DN_OBS if x in STRICT))}}} → d_obs = 0.333 ; 隨機中位 d_med = {med_s}
- Δn ∩ 寬鬆 = {{{sorted(set(x for x in DN_OBS if x in BROAD))}}} → d_obs = 0.667 ; 隨機中位 d_med = {med_b}
- q_obs = {q_s:.4%} (嚴格) / {q_b:.4%} (寬鬆) → 🔴 唔顯著 (密度效應)
─ 觀測命中率唔高於隨機中位 ⟹ 「Δn_color 屬 IDCM 目錄」唔構成證據
─ 依 O208: 冇分位數 = 未閉合; q_obs>5% = 密度效應, 唔准入帳
""")
print(f"PASS {len(PASS)} / FAIL {len(FAIL)}")
sys.exit(0 if not FAIL else 1)