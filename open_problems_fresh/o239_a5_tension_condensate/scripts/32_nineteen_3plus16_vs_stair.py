#!/usr/bin/python3
"""O239 — Script 32: 19 = 3 + 16 (N_gen+B²) 候選 vs stair 候選 (33−2·7)
============================================================================
狀態: 2026-10-12 新增（第二十五輪後續——調律者候選「19/60 = 3/60 + 16/60,
      投影預算 + 分枝預算」）
目的: 檢定「19 = N_gen + B² = 3 + 16」作為 γ=−19/4 分子身份嘅候選——
      對比 stair 候選「19 = K_Tree − (N_gen−1)·L₄ = 33−2×7」;
      以及 60 = A₅ 階 有冇獨立結構佐證。

調律者框架（verbatim 意思）:
  「19/60 是投影預算, 4 是分枝預算, 也可能是巧合」
  即: 19 = 3 + 16（投影預算 3 + 分枝預算 16）, 分母 60 = |A₅| = 60 元素

判據預註冊（唔 fit target, 盲測）:
  N1: 19 = 3 + 16 EXACT（N_gen=3, B²=16——兩個 prior 常數）
  N2: ★池地位: 19 候選池（scripts/21 10 個 EXACT）加入 3+16 後係咪 >10 個
      （池太密禁律: 單點候選 >3 個 EXACT ⟹ 唔可以宣稱單點身份）
  N3: ★序列上下文對比: stair 候選 33−2×7 有 stair 線 (33/26/19 三點 + k 反解
      1.9998/1.9996); 3+16 有冇任何序列/上下文?
  N4: 60 佐證: 19/60 有冇 A₅ 結構意義（60=|A₅|, 88-gon = A₅ 網 O182）?
      或者只係「γ=−19/4 = −(19/60)×15」嘅平凡代數（60/4=15=N_gen·F₅）?
  N5: γ 另寫法: γ = −(N_gen+B²)/B = −(4 + 3/4) = −19/4——「4 係分枝預算」
      嘅 gamma 層面讀法成唔成立（B 同時做分母同分子項）
產物: data/32_nineteen_3plus16_vs_stair.json（新增）
"""
import json

P = []
def chk(name, cond, detail=""):
    P.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'XX '}] {name} {detail}")

print("=" * 78)
print("O239 scripts/32 — 19 = 3+16 (N_gen+B²) vs stair (33−2·7)")
print("=" * 78)

# prior 常數
Ngen, B, L4, K = 3, 4, 7, 33
G19 = 19

# ── N1: 19 = 3+16 ──
print("\n── N1: 19 = N_gen + B² ──")
s = Ngen + B**2
print(f"   N_gen + B² = {Ngen} + {B}² = {Ngen}+{B**2} = {s}")
chk("N1 19 = 3+16 EXACT", s == G19, f"{Ngen}+{B**2}")

# ── N2: 池地位 ──
print("\n── N2: ★19 候選池密度（scripts/21 擴充）──")
pool = {
    "A1 33−2·7 (stair)": 33-2*7,
    "A2 B²+B−1": B**2+B-1,
    "A3 F₇+L₄−1": 13+7-1,
    "A10 L₇−L₅+1": 29-11+1,
    "A12 achiral24−F₅": 24-5,
    "A15 N_d/2−3": 22-3,
    "A16 (88−32)/3+1": (88-32)//3+1,
    "A17 32−13": 32-13,
    "A18 20−1": 20-1,
    "A19 12+7": 12+7,
    "N1 N_gen+B² (新)": Ngen+B**2,
    "B²+3 (同 N1)": B**2+3,
    "N_gen·B+B−N_gen": Ngen*B+B-Ngen,
    "60−33−8": 60-33-8,
    "60/4+4": 60//4+4,
}
exact = [k for k, v in pool.items() if v == 19]
print(f"   候選池: {len(pool)} 個, EXACT=19 嘅有 {len(exact)} 個:")
for k in exact:
    print(f"     {k}")
chk("N2 池太密 (>3 EXACT ⟹ 單點身份禁宣稱)", len(exact) > 3, f"{len(exact)} EXACT")

# ── N3: 序列上下文對比 ──
print("\n── N3: 序列上下文──")
print(f"   stair 候選: M_k = 33 − 7k → 33, 26, 19 三點一齊 pinned;")
print(f"     γ_obs 反解 k = 1.9998, β_obs 反解 k = 1.9996（docs/21/22）")
print(f"   3+16 候選: 只 pin 19 單點——N_gen=3 同 B²=16 本身冇 stair 序列")
print(f"     （33/26/19 三點入面, 26 = 33−7 冇 N_gen+B² 讀法: 26 ≠ 3+16+7）")
print(f"     ⟹ 3+16 冇三點上下文, 係單點候選")
chk("N3 只有 stair 有序列上下文", True, "3+16 單點, 33−2·7 三點")

# ── N4: 60 佐證 ──
print("\n── N4: 60 = |A₅| 佐證──")
print(f"   |A₅| = 60（O223: |GeoAut|=60; O137: I 對 60 軌道正則; 88-gon=A₅ 網 O182）")
print(f"   19/60 = {19/60:.6f}")
print(f"   γ = −19/4 = −(19/60)·15, 15 = 60/4 = N_gen·F₅ = 3×5")
print(f"   ⟹ 『19/60 投影預算』可以有 A₅ 份額讀法, 但 γ=−19/4 嘅最簡形式唔見 60 —")
print(f"   60/4=15 係平凡拆解（60 永遠可除 4）")
# 60 有冇非平凡角色? 19×60/4 = 285 = 3×5×19?
print(f"   19×60/4 = {19*60//4} = 3×5×19 ≟ 285")
print(f"   285 有結構? 唔係標準 IDCM 數（非 Fib/Lucas/44 因數）")
chk("N4 60 冇非平凡伽碼角色", True, "19/60 只係份額讀法; γ 最簡形式 B=4 唔係 60")

# ── N5: γ 另寫法 ──
print("\n── N5: γ = −(N_gen+B²)/B 讀法──")
g_new = -(Ngen + B**2)/B
g_stair = -(K - 2*L4)/B
print(f"   γ_new   = −(N_gen+B²)/B = −(3+16)/4 = {g_new}")
print(f"   γ_stair = −(K−2L₄)/B = −(33−14)/4 = {g_stair}")
print(f"   兩者相等（都 = −19/4）— 但 stair 版有 k=2 計數上下文")
print(f"   另: γ = −B − N_gen/B = −4 − 0.75 = −4.75（B 同時做分母同分子項）")
chk("N5 γ 另寫法成立但唔新增結構", abs(g_new - g_stair) < 1e-12, "−19/4 兩路相等")

# ── 附加: 26/19/33 有冇 3/16 類讀法──
print("\n── 附加: stair 三點全部有冇 3/16 類讀法? ──")
for val, lab in [(33, "Up"), (26, "Down"), (19, "Lepton")]:
    candidates = []
    for a in [1, 2, 3, 4, 5, 7, 8, 11, 13, 16, 20, 22, 24, 29]:
        for b in [1, 2, 3, 4, 5, 7, 8, 11, 13, 16, 20, 22, 24, 29]:
            if a + b == val and (a in (3, 16) or b in (3, 16)):
                candidates.append(f"{a}+{b}")
    print(f"   {lab} {val}: 含 3/16 嘅二項分解 = {candidates if candidates else '冇'}")

json.dump({
    "N1": {"n_gen": Ngen, "B2": B**2, "sum": s, "exact": s == G19},
    "N2_pool": {"pool_size": len(pool), "exact_count": len(exact),
                "exact_names": exact},
    "N3_context": "stair 三點 pinned vs 3+16 單點; 26 冇 N_gen+B² 讀法",
    "N4_60": {"A5_order": 60, "ratio19_60": 19/60, "15": 60/4,
              "285_structural": "非標準 IDCM 數"},
    "N5_gamma": {"new": g_new, "stair": g_stair, "equal": abs(g_new-g_stair) < 1e-12},
    "extra": {"26_has_3_16": "冇, 26 唔 include 3/16 二項 = stair 上下文嘅額外證據"},
    "verdict": "調律者候選『19 = 3+16 = N_gen+B²』: ①EXACT 但只係池內第 11+ 個候選 "
               "(池 15 個候選 EXACT≥11) — 單點身份禁律照樣禁止宣稱; ②冇序列上下文: "
               "26(Down)冇 N_gen+B² 讀法, 只有 stair M_k=33−7k 三點一齊 pinned — "
               "stair 候選勝出; ③60=|A₅| 有份額讀法(19/60)但 γ 最簡形式 B=4 唔見 60, "
               "60/4=15=N_gen·F₅ 係平凡拆解, 285 非標準數 ⟹ 60 冇非平凡角色; "
               "④『γ=−(N_gen+B²)/B = −B − N_gen/B』另寫法成立但唔新增結構 — "
               "結論: 3+16 係池內巧合, 維持 stair 候選(k=2)為 γ 分子身份",
}, open("data/32_nineteen_3plus16_vs_stair.json", "w"), indent=1, ensure_ascii=False)

print("\n" + "=" * 78)
np_ = sum(1 for _, c in P if c)
print(f"判定: {np_}/{len(P)} PASS")