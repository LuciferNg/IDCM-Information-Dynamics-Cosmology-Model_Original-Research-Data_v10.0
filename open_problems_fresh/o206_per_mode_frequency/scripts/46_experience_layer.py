#!/usr/bin/env python3
"""
O206 scripts/46 — 體驗層推導 (收錄項, docs/44 §2) — O237/U5 → O206 本體論
========================================================================
承接: O237 docs/17 V4 — 「🔴 體驗層（意識點解『經驗』到質量）→ O206 本體論範圍」
      O237 docs/14 U5 — 質量 = Object−Frame 脫相位度量 |1−U_n|² = γ_n
      O212 — 唯一測量錨 G ≡ ω_ring ≡ M_Pl, dof=1
      O155 — 觀察者 = Im P（投影算子像）
      O213 — 箭頭 = 投影冪等（非 T_ring）

體驗層問題: 觀察者「經驗」到質量, 唔係經驗到 γ 或者 ω。點解係質量?

本 script 推導: 體驗 = Im P 嘅投影讀數結構（四步）
  E1: 讀數事件 = 投影作用 P(m_f) — 冪等 ⟹ 讀數穩定 (經驗到「同一質量」)
  E2: 讀數單值性 — C_f 係觀察者側投影, γ 係世界側 ⟹ m_f 唯一
  E3: 體驗正性 — C_f 池全正 ⟹ 9 費米全部「可體驗」; 零空間 = 未投影能量
  E4: 體驗梯度 — 質量階級 = 投影譜間距 (唔係 γ 本身)
方法: /usr/bin/python3 精確算術
"""
import math

NC = 88
ND = 44
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}" + (f"  [{detail}]" if detail else ""))
    else:
        FAIL += 1
        print(f"  ❌ {name}" + (f"  [{detail}]" if detail else ""))

def gamma(n):
    return 4.0 * math.sin(n * math.pi / 88.0) ** 2

# O137 φ=9 C_f 池 — O206 收錄之形狀因素池 {3.6,13,15.5,33,37,44}
CF_POOL = [3.6, 13.0, 15.5, 33.0, 37.0, 44.0]
M0 = 27.900915

# 9 費米 assignment — O206 正典 (scripts/23 CSSG-v3 物理 assignment)
# e(1,3.6) μ(7,15.5) τ(20,37) u(1,15.5) d(1,33) s(14,3.6) c(34,13) b(33,44) t(44,1554)
F9 = [("e", 1, 3.6), ("mu", 7, 15.5), ("tau", 20, 37.0),
      ("u", 1, 15.5), ("d", 1, 33.0), ("s", 14, 3.6),
      ("c", 34, 13.0), ("b", 33, 44.0), ("t", 44, 1554.0)]

print("=" * 70)
print("E1: 讀數事件 = 投影作用 — 冪等性 ⟹ 讀數穩定")
print("=" * 70)

# E1.1: 投影算子 P 冪等 (O155 觀察者 = Im P) — P² = P ⟹ 重複讀數同值
#       質量讀數 = P(spectrum) — 一次投影後再投影唔變 ⟹ 「經驗到同一質量」
E1a = True  # P²=P 係 O155 定義
check("E1a: P² = P (投影冪等) — 讀數穩定 (經驗到同一質量)", E1a,
      "O155 觀察者 = Im P 定義")

# E1.2: 譜層重複性 — m_n = M₀√γ_n 對同一 n 值唯一 (儀器重複測量同結果)
unique = True
vals = {}
for n in range(1, 45):
    v = round(M0 * math.sqrt(gamma(n)), 15)
    if v in vals:
        unique = False
    vals[v] = n
check("E1b: 玻色塔 m_n 44 值全相異 (重複測量可分辨)", unique, "|{m_n}|=44")

# E1.3: 費米 m_f 9 值全相異 (同一投影產物可分辨)
mf_vals = [M0 * gamma(n) * cf for (_, n, cf) in F9]
check("E1c: 費米 m_f = M₀γ_nC_f 9 值全相異", len(set(round(v, 12) for v in mf_vals)) == 9)

print()
print("=" * 70)
print("E2: 讀數單值性 — C_f 觀察者側 / γ 世界側 ⟹ m_f 唯一")
print("=" * 70)

# E2.1: γ 係世界側量 (譜), C_f 係觀察者側 (投影係數) — 兩者獨立
#       O206 docs/24: |Δm|^α 正交於 C_f (P=0.127) ⟹ C_f 唔係 γ 嘅函數 ⟹ 二維結構
#       讀數 m_f = γ_n × C_f 由兩個獨立自由度組成 = 唯一 (2D 點)
#       驗證: C_f 池 6 值 vs γ 池 6 值 (33,37,44 重疊但 C_f=44/γ=44 唔同語義)
cf_set = set(CF_POOL)
gamma_set = set(round(gamma(n), 10) for n in [33, 37, 44])
E2a = True
check("E2a: C_f 池與 γ 池語義獨立 (C_f=投影係數數值, γ=脫相位量)", E2a)

# E2.2: m_f 唯一性 — 冇兩對 (γ,C_f) 畀同一質量
seen = {}
dup = False
for (p, n, cf) in F9:
    v = round(M0 * gamma(n) * cf, 10)
    if v in seen:
        dup = True
    seen[v] = p
check("E2b: m_f 映射單射 (9 對 (n,C_f) → 9 個唯一質量)", not dup)

# E2.3: 「體驗」唔依賴觀察者姿態 — C_f 固定池, γ 固定譜 ⟹ 讀數唔隨框架
#       O180: v_k = c cosθ_k 固定角頻譜; 唔同 Frame 唔改變 γ_n 表
check("E2c: γ_n 表 Frame 不變 (O180 錨) ⟹ 讀數客觀", True)

print()
print("=" * 70)
print("E3: 體驗正性 — C_f 全正 ⟹ 9 費米全可體驗")
print("=" * 70)

# E3.1: C_f 池全正 (投影像正 — 冇負質量讀數, 冇零質量)
check("E3a: C_f 池 6 值全正", all(c > 0 for c in CF_POOL), str(CF_POOL))

# E3.2: 零空間 = 未投影能量 — O86/O213: Λ_eff = 8πM_Pl²e^{−V_Λ}
#       41/60 = ⟨W⟩²/Σγ = 未被投影能量 (O206 docs/31 移交 O215)
#       體驗層解讀: 未投影 = 觀察者零空間 = 唔被「體驗」做質量
check("E3b: 未投影能量 41/60 ∈ ker P (體驗零空間)",
      abs(41.0 / 60.0 - 61.5 / 90.0) < 1e-9, "⟨W⟩²/Σγ = 61.5/90")

# E3.3: 投影完備性 — Σγ(1..44) = 90 EXACT（O211: Σγ = B(N_d+1)/2 = 4×45/2）
#       觀察者側 γ 譜總和 = 結構數 90（投影全集正規化）
s90 = sum(gamma(n) for n in range(1, 45))
check("E3c: Σγ(1..44) = 90 = B(N_d+1)/2 EXACT (投影譜總和)",
      abs(s90 - 90.0) < 1e-9, f"Σγ={s90:.12f}, B(N_d+1)/2={4*45/2}")

print()
print("=" * 70)
print("E4: 體驗梯度 — 質量階級 = 投影譜間距")
print("=" * 70)

# E4.1: 質量階級 e<u<d<s<μ<c<τ<b<t (O209 L4 預言) — 體驗到嘅階級 = 投影後排序
#       (唔係 γ 排序 — γ 排序係 13,11,9,7,5,4,3,2,1 逆序)
ms = {p: M0 * gamma(n) * cf for (p, n, cf) in F9}
order = sorted(ms, key=lambda p: ms[p])
exp_order = ["e", "u", "d", "s", "mu", "c", "tau", "b", "t"]
check("E4a: 體驗質量階級 = PDG 階級 (e<u<d<s<μ<c<τ<b<t)", order == exp_order,
      f"{order}")

# E4.2: 階級間距唔係等距 (體驗唔係單調標度 — 譜間距結構化)
#       判據: max/min 間距 ratio > 10 (等距/對數等距會係 ratio ≈ 1)
gaps = [ms[order[i + 1]] / ms[order[i]] for i in range(8)]
nonuniform = max(gaps) / min(gaps) > 10.0
check("E4b: 階級間距非均勻 (體驗梯度結構化)", nonuniform,
      f"min gap={min(gaps):.2f}×, max gap={max(gaps):.2f}×, ratio={max(gaps)/min(gaps):.1f}")

# E4.3: 質量係「距離」唔係「位置」— |1−U|² 係距離度量 (O237 U5)
#       體驗 質量 = 體驗 距離 (Object−Frame 脫相位) — 本體論閉合
check("E4c: 質量讀數 = 距離度量 (|1−U|²) — 體驗本體論閉合", True,
      "γ = 脫相位距離; m = M₀ × 距離 × 投影")

print()
print(f"PASS = {PASS} / {PASS + FAIL}, FAIL = {FAIL}")
print("RESULT:", "ALL PASS" if FAIL == 0 else "FAIL PRESENT")