#!/usr/bin/env python3
"""
O38/m0-scale — scripts/24: 式族自由度審計 (Family Freedom Audit)
================================================================
★ 用戶批評 (2026-10-18): 「很多方法都能逼近，數值越大都高自由度，
   例如 (44^33)/(22^11)」⟹ 拆細唔夠 — 任何固定目標, 只要式族夠大
   (基底可無限衍生: 44/22/11/33 全係 88 嘅 divisor), 命中必爆炸。

本 script:
  [A] 實測用戶例 (44^33)/(22^11) — 拆質因數 + log₁₀ + 對 N_O38 嘅真 dev
  [B] ★ 式族密度判準: ρ = N_expr/D_range [式/dex]; 命中期望 E = ρ·tol_dex
      E >> 1 ⟹ 零資訊 (任何目標都中); E << 1 ⟹ 先有資訊
  [C] 三族實測: C1 {44^a/22^b} (用戶例族), C2 對數整數族 (scripts/23),
      C3 半整數乘積族 (scripts/20, 用記錄)
  [D] 式族註冊制 (4 條件) + O38 全部後驗命中證據權重歸零審計
"""
import math, random, time
print("=" * 76)
print("  O38/m0-scale — 式族自由度審計 (scripts/24)")
print("=" * 76)

LOG10_N = 40.25572603          # log₁₀(N_O38 = 1.80188233461e40)
N_O38 = 1.80188233461e40

# ═══ [A] 用戶例實測 ═══
print("\n─── [A] 用戶例: (44^33)/(22^11) ───")
num = 44**33; den = 22**11
val = num/den
# 44 = 2²·11, 22 = 2·11 ⟹ 44^33/22^11 = 2^66·11^33 / 2^11·11^11 = 2^55·11^22
print(f"  44^33/22^11 = {num}/{den} = 2^55·11^22 = {val:.6e}")
ld = math.log10(val)
print(f"  log₁₀ = {ld:.6f}   vs   log₁₀ N_O38 = {LOG10_N:.6f}")
print(f"  量級差 = {LOG10_N - ld:+.4f} dex   ⟹  真 dev = {(val-N_O38)/N_O38*100:+.2f}% (唔算逼近!)")
print("  ⚠️ 呢個例子反而示範: log 尺度『睇落近』(10^39.5 vs 10^40.3), 實際差 83.7%")

# ═══ [B] 式族密度判準 ═══
print("\n─── [B] 式族密度判準 ───")
print("""  定性: 自由度唔係『目標數值大細』嘅函數, 係『式族參數空間』嘅函數。
  定量: ρ = N_expr / D_range  [候選式數目 ÷ 覆蓋範圍 (dex)]
        E  = ρ × tol_dex      [對目標附近嘅命中期望]
  判準: E >> 1 ⟹ 零資訊 (隨機目標幾乎必中);  E << 0.1 ⟹ 有資訊
        E ≈ 0.3 屬『可報但必須連帶報告 E』;  未有 E 記錄嘅命中 = 後驗, 證據權重 0""")

# ═══ [C] 三族實測 ═══
def family_density(fn, tgt, tol, nsam=200, seed=42):
    """fn: expr 生成器 (yield (e_min,e_max) (dex)); 返回 (rho, E, hits, nullrate)"""
    vals = list(fn())
    lo = min(v for _, v in vals); hi = max(v for _, v in vals)
    rho = len(vals)/(hi-lo)
    hits = sum(1 for _, v in vals if abs(v-tgt) < tol)
    E = rho*(2*tol)
    random.seed(seed)
    nh = 0
    for _ in range(nsam):
        t = random.uniform(lo+1, hi-1)
        if any(abs(v-t) < tol for _, v in vals): nh += 1
    return rho, E, hits, nh/nsam

print("\n─── [C1] 用戶例族 {44^a / 22^b}, a,b ∈ [-40,40] ───")
def f44_22():
    for a in range(-40, 41):
        for b in range(-40, 41):
            yield (f"44^{a}/22^{b}", a*math.log10(44) - b*math.log10(22))
values44 = [(n, v) for n, v in f44_22()]
for tol in (0.02, 0.05, 0.1):
    rho, E, hits, nr = family_density(f44_22, LOG10_N, tol)
    near = [(n, v) for n, v in values44 if abs(v-LOG10_N) < tol]
    print(f"  tol={tol:4.2f} dex: ρ = {rho:6.1f}/dex, E = {E:5.2f}, 對 N 命中 = {hits}, null({tol}) = {nr*100:4.1f}%")
    for n, v in sorted(near, key=lambda t: abs(t[1]-LOG10_N))[:3]:
        print(f"      例: {n} → log₁₀ = {v:.6f} (dev {abs(v-LOG10_N):.5f} dex)")
print("  ⟹ 0.02 dex 時 E≈1.1: 每 100 個隨機目標 ~70 個 '命中' — 用戶例族自由度已高")

print("\n─── [C2] scripts/23 對數整數族 (三項 + 窄基底) — 覆蓋缺陷更正 ───")
def f_intlog():
    s1s = [88,137,61.5,123,90,256]; s2s = [88,47,29,33,42]; s3s = [2,3,5,11,18,27]
    for s1 in s1s:
        for e1 in range(-4,5):
            for s2 in s2s:
                for e2 in range(-4,5):
                    for s3 in s3s:
                        for e3 in range(-8,9):
                            yield (f"{e1}ln{s1}+{e2}ln{s2}+{e3}ln{s3}",
                                   e1*math.log(s1)/math.log(10) + e2*math.log(s2)/math.log(10) + e3*math.log(s3)/math.log(10))
st = time.time()
vals = [v for _, v in f_intlog()]
lo, hi = min(vals), max(vals)
rho = len(vals)/(hi-lo)
for tol in (0.005, 0.02):
    E = rho*2*tol
    random.seed(7); nh = 0
    for _ in range(200):
        t = random.uniform(lo+1, hi-1)
        if any(abs(v-t) < tol for v in vals): nh += 1
    print(f"  族覆蓋: [{lo:+.1f}, {hi:+.1f}] dex; 目標 N 喺 {LOG10_N:.1f} dex 超出覆蓋 {LOG10_N-hi:+.1f} dex!")
    print(f"  tol={tol:4.3f} dex: ρ = {rho:5.1f}/dex, E = {E:6.4f}, 域內 null = {nh/2:.1f}%  ({time.time()-st:.0f}s)")
print("""  ⚠️ 更正 (對 scripts/23 [C]): 當日『0 命中 + null 0%』係覆蓋假象 —
  族賣 max ≈ 29.9 dex, 目標 40.26 dex 根本唔喺覆蓋範圍 ⟹ 0 命中係必然,
  null 0% 亦係『目標全部喺族外』造成 — 唔係『族稀疏』嘅有資訊負!
  正確解讀: 三項整數指數族喺自己域內其實好稠密 (E≈43 @0.005 dex) ⟹
  無論命中定 miss, 對目標 N 都係零資訊。用戶批評成立: 式族要覆蓋目標,
  且覆蓋內 E<<1, 負結果先有資訊。""")

print("\n─── [C3] scripts/20 半整數乘積族 ∏ a_i^{k/4} (記錄) ───")
print("""  φ^x (28,140) / 137^k (14,070): 零命中
  乘積族 (2,977,270): 最佳 dev 5.089e−05 (後驗, 唔升格)
  null: @1e−3 → 100%, @1e−4 → 81%, @1e−5 → 24%  ⟹ E >> 1 (零資訊族)
  對比: 同一 dev 5e−5 喺 C2 族 (null 0%) 先有證據力 — E 係唯一判準""")

# ═══ [D] 式族註冊制 + 審計 ═══
print("\n─── [D] 式族註冊制 (門檻) + O38 後驗命中證據權重審計 ───")
print("""  任何『N ≈ 表達式』主張必須附:
  1. 定義: 式族 (基底集 + 指數集 + 組合數) — 可重算
  2. 密度 E: 該族對同量級隨機目標嘅命中期望 (≥200 樣本)
  3. 家族命中數: 同一族喺容差內有幾多個唔同式 (多 = 稠密 = 零資訊)
  4. 機制語義: 基底/指數點解係呢啲數 (譜結構直接生成, 唔可以由 88/44/2 再組合)""")
audits = [
    ("F_e ≈ 55 = F₁₀",            "54.6007", "0.731%",  "未註冊/後驗", "0 (只係 scripts/21 順手掃到)"),
    ("r_7e ≈ 3³ = N_gen³",        "27.0063", "0.023%",  "未註冊/後驗", "0 (同源: m_7/m_e)"),
    ("f_v ≈ 8825 = 5²·353",       "8824.79", "0.0024%", "未註冊/後驗", "0 (v_SM/M₀ 順手掃到)"),
    ("M_Pl/M₀ ≈ 35/8·10²⁰",       "4.3758",  "0.018%",  "未註冊/後驗", "0 (10 進制尾數 density)"),
    ("N 尾數 ≈ 9/5",              "1.80188", "0.10%",   "未註冊/後驗", "0"),
    ("M₀/E_Pl 尾數 ≈ 16/7",       "2.28529", "0.020%",  "未註冊/後驗", "0"),
    ("(44^33)/(22^11) ≈ N 量級",  "10^39.5", "83.7%",   "未註冊/後驗", "0 (量級命中, 唔算逼近)"),
]
print(f"  {'候選':28s} {'值':11s} {'dev':9s} {'註冊':14s} 證據權重")
for name, val, dev, reg, w in audits:
    print(f"  {name:28s} {val:11s} {dev:9s} {reg:14s} {w}")
print("""  ⟹ O38 全部已報『命中』嘅證據權重 = 0 — 冇一個過式族註冊制。
      而 scripts/23 [C] 嘅『0 命中 + null 0%』經 C2 更正 = 覆蓋假象 (目標喺族外)。
      真正狀態: 現有全部式族 = 覆蓋內稠密 (E≈43) 或覆蓋外 (目標唔喺範圍) ⟹
      **冇任何式族能對 N 提供有意義測試** — 正負結果都係零資訊。

─── [E] 判定 ───
  1. ✅ 用戶例確認: (44^33)/(22^11) 對 N 係 83.7% dev (log 差 0.79 dex) — 唔係逼近,
     係『量級命中』示範; 同時證明 44/22/11/33 型基底可無限衍生 (88 嘅 divisor)
  2. ✅ 自由度正確測量 = ρ·tol = E; 大數令 log 尺度『睇落近』, 但拆細 + 式族註冊先係防線
  3. 🔴 所有候選 (包括 3³/8825/35·8×10²⁰/9·5/16·7) 證據權重 = 0 — N 維持 🔴
  4. ⚠️ 更正 scripts/23 [C]: 『對數整數族 0 命中 + null 0% = 有資訊負』係覆蓋假象 —
     族覆蓋 ±28.9 dex, 目標 40.26 dex 喺族外 ⟹ 必然 0 命中; 域內其實 E≈43 稠密
  5. ✅ 正當路徑: 先定義式族 → 確認覆蓋目標 → 計覆蓋內 E → E<<1 先有資格報
     『命中』/『負結果』; 預先註冊式族 + 機制語義先有證據力
  6. ⟹ 方法升級: 式族註冊制 (含覆蓋檢查) 入 skill; 後續所有 N/細數候選一律過閘
""")
print("EXIT 0 — 報告型 (審計輸出; 每族 E 值標明)")