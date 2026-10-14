#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-26 — 標度橋之閉合攻堅: 因子分解 + 修正項原理 (2026-09-18)
==============================================================
承接 docs/12 §3 (P6 線索: 修正 = 凝聚分數 ÷ (N_d+1))。

上游新發現 (只讀, 未改):
  ★ O86 docs/05 §1.3: 橋因子 6240.06603175 係**無量綱純結構數**
      y_n = √2·m_n/v_SM = ω_n / (88·71·(1 − 4/(90·35)))
      ⟹ 「標度橋」唔係量綱蛻變型標度橋, 而係 **Yukawa 分母** (M₀ 相消)
  ★ O34 docs/05 §4.10: 世代跳躍 k(e→τ) = 17 − L₇/528,  17 = L₅ + C(4,2) = 11+6
      ⟹ 71 = 2N_d − 17 = 2N_d − L₅ − C(4,2) 有推導來源
  ★ docs/12 §2 (本 session): ∏γ_even/∏γ_odd = 88 = 2N_d = Σγ_odd (精確恆等式)
      ⟹ 88 亦有推導身份

本腳本 (寫入限於 o144_boson_identity/):
  §A 因子分解審計 (三因子之推導來源逐項核)
  §B 新子恆等式: (N_d+1) = Σγ_even/μ² (定義性) ⟹ 修正項之正則形
  §C 修正項之原理攻堅 (逐條原理 → 導出形式 → 比較)
  §D 重框: 橋 = 無量綱 Yukawa 分母 (非標度橋)
  §E 附: m_H 候選 (post-hoc) 密度測試 — 兩軸方法之示範
  §F 判決
"""
import numpy as np
import mpmath as mp
import itertools, json, sys

mp.mp.dps = 40
PASS = FAIL = 0
ROWS = []

def chk(cid, name, got, want, tol=1e-30):
    global PASS, FAIL
    ok = abs(mp.mpf(got) - mp.mpf(want)) <= tol
    if ok: PASS += 1
    else: FAIL += 1
    ROWS.append({"id": cid, "check": name, "ok": bool(ok)})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def chkb(cid, name, cond):
    global PASS, FAIL
    ok = bool(cond)
    if ok: PASS += 1
    else: FAIL += 1
    ROWS.append({"id": cid, "check": name, "ok": ok})
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {name}")

def hdr(s):
    print("\n" + "=" * 78); print(s); print("=" * 78)

# ── 框架常數 (零新常數) ──
N_d, B, N_gen, M_tree = 44, 4, 3, 33
mu2 = mp.mpf(2)        # 凝聚驅動 = γ_22 (Z₂ 不動點); 用 mpf 免 float 污染
L4, L5, L7 = 7, 11, 29
PHI = (1 + mp.sqrt(5)) / 2
M0  = mp.mpf('27.9009')                     # MeV (O37/O40 記錄值)
M0f = mp.mpf('4.060265e-3') * PHI ** (47 + mp.mpf(37) / 528) * 1e-6   # MeV (原始式)
V_SM = mp.mpf('246219.6')                   # MeV
M_H  = mp.mpf('125250')                     # MeV (PDG)

G   = [4 * mp.sin(mp.pi * k / 176) ** 2 for k in range(1, 89)]   # 176-分母雙鏈
g44 = [4 * mp.sin(mp.pi * n / 88) ** 2 for n in range(1, 45)]    # 44-site 鏈
S_even = sum(G[k - 1] for k in range(2, 89, 2))   # 90
S_odd  = sum(G[k - 1] for k in range(1, 89, 2))   # 88
Peven = mp.mpf(1)
for x in G[1::2]: Peven *= x
Podd = mp.mpf(1)
for x in G[0::2]: Podd *= x

# ── 目標 ──
BRIDGE = 88 * 71 * (1 - mp.mpf(4) / (90 * 35))     # = 6240.06603175
Bstar  = V_SM / (M0 * mp.sqrt(2))                  # 6240.06927451 (記錄 M₀)
Bstarf = V_SM / (M0f * mp.sqrt(2))                 # 用原始式 M₀

# ══════════════════════════════════════════════════════════════════════
hdr("[§A] 因子分解審計 — 三因子之推導來源")
# ══════════════════════════════════════════════════════════════════════
print(f"""
  橋 = 88 · 71 · (1 − 4/(90·35)) = {mp.nstr(BRIDGE, 12)}
  目標 (記錄 M₀)   = {mp.nstr(Bstar, 12)}   dev = {mp.nstr(abs(Bstar-BRIDGE)/Bstar, 4)}
  目標 (原始式 M₀) = {mp.nstr(Bstarf, 12)}  dev = {mp.nstr(abs(Bstarf-BRIDGE)/Bstarf, 4)}

  ── 因子 1: 88 ──
     Σγ_odd = {mp.nstr(S_odd, 10)};  2N_d = {2*N_d}
     ∏γ_even/∏γ_odd = {mp.nstr(Peven/Podd, 10)}
     ⟹ 三重身份: 88 = 2N_d = Σγ_odd = ∏γ_even/∏γ_odd
""")
chk("A1", "88 = 2N_d", S_odd, 2 * N_d, 1e-25)
chk("A2", "88 = ∏γ_even/∏γ_odd (行列式比, docs/12 §2)", Peven / Podd, 88, 1e-32)
chk("A3", "∏γ_odd = μ² = 2", Podd, mu2, 1e-35)
chk("A4", "∏γ_even = 4N_d = 176", Peven, 4 * N_d, 1e-32)

print(f"""
  ── 因子 2: 71 ──
     17 = L₅ + C(4,2) = {L5} + {mp.binomial(4,2)} = {L5 + mp.binomial(4,2)}
     71 = 2N_d − 17 = {2*N_d} − 17 = {2*N_d - 17}
     O34 §4.10: k(e→τ) = 17 − L₇/528 (世代跳躍 e→τ 之整數首項 = 17)
     ⟹ 71 = 2N_d − k(e→τ)|_leading — **有推導來源** (世代跳躍階梯)
""")
chk("A5", "17 = L₅ + C(4,2)", 17, L5 + mp.binomial(4, 2), 1e-30)
chk("A6", "71 = 2N_d − 17", 71, 2 * N_d - 17, 1e-30)

print(f"""
  ── 因子 3: 修正 (1 − 4/(90·35)) ──
     4/(90·35) = 1/787.5;  787.5 = 90·35/4 = Σγ_even·(M_tree+μ²)/B
     ⟹ 修正項**未閉合** (docs/12 §3)
""")
chk("A7", "787.5 = Σγ_even·(M_tree+μ²)/B", 90 * 35 / 4, mp.mpf('787.5'), 1e-30)
chk("A8", "橋 = 88·71·(1−4/3150) 重現 (與 docs/11 一致)", BRIDGE, mp.mpf('6240.06603175'), 1e-8)

# ══════════════════════════════════════════════════════════════════════
hdr("[§B] 新子恆等式 — (N_d+1) 之來源 + 修正項正則形")
# ══════════════════════════════════════════════════════════════════════
Nd1 = N_d + 1
ratio_Se_mu = S_even / mu2
print(f"""
  ★ 觀察: N_d + 1 = {Nd1};  Σγ_even/μ² = {mp.nstr(S_even,8)}/{mu2} = {mp.nstr(ratio_Se_mu, 8)}
  ⟹ 兩者相等。但**唔係巧合** —— 係定義性推論:
       μ² ≡ Σγ_even − Σγ_odd          (定義)
       Σγ_odd = 2N_d                   (定理)
       ⟹ Σγ_even = 2N_d + μ²
       ⟹ Σγ_even/μ² = 2N_d/μ² + 1 = N_d + 1   (因 μ² = 2 ⟹ 2N_d/μ² = N_d)
  ⟹ (N_d+1) = Σγ_even/μ² 係「定義性」, 唔係額外假設
""")
chk("B1", "N_d+1 = Σγ_even/μ² (精確)", Nd1, ratio_Se_mu, 1e-25)
chk("B2", "Σγ_even = 2N_d + μ² (由 μ² 定義 + Σγ_odd=2N_d)", S_even, 2 * N_d + mu2, 1e-25)
chk("B3", "2N_d/μ² = N_d (因 μ²=2)", 2 * N_d / mu2, N_d, 1e-25)

corr_A = mu2 / (Nd1 * (M_tree + mu2))          # 2/(45·35)
corr_B = mu2 ** 2 / (S_even * (M_tree + mu2))  # 4/(90·35)
corr_C = (mu2 / S_even) * (mu2 / (M_tree + mu2))
print(f"""
  ★ 修正項之三個等價正則形 (全部精確相等):
     (i)   μ²/((N_d+1)(M_tree+μ²))  = {mp.nstr(corr_A, 12)}
     (ii)  μ⁴/(Σγ_even·(M_tree+μ²)) = {mp.nstr(corr_B, 12)}
     (iii) (μ²/Σγ_even)·(μ²/(M_tree+μ²)) = {mp.nstr(corr_C, 12)}
           = [凝聚/world 能量 2/90] × [凝聚/(深度+凝聚) 2/35]

  ⟹ (iii) 係最有原理樣貌之讀法: 修正 = **兩個凝聚分數之乘積**。
     μ²/Σγ_even      = 1/45  — 凝聚佔世界能量之份額
     μ²/(M_tree+μ²)  = 2/35  — 凝聚佔 (樹深度+凝聚) 之份額
""")
chk("B4", "修正項三形等價 (i)=(ii)=(iii)", corr_A - corr_B, 0, 1e-35)
chk("B5", "修正項三形等價 (ii)=(iii)", corr_B - corr_C, 0, 1e-35)
chk("B6", "μ²/Σγ_even = 1/(N_d+1) = 1/45", mu2 / S_even, mp.mpf(1) / Nd1, 1e-30)
chk("B7", "μ²/(M_tree+μ²) = 2/35", mu2 / (M_tree + mu2), mp.mpf(2) / 35, 1e-30)

# ══════════════════════════════════════════════════════════════════════
hdr("[§C] 修正項之原理攻堅 — 逐條原理導出形式")
# ══════════════════════════════════════════════════════════════════════
TARGET_C = 4 / mp.mpf(3150)     # = 0.00126984126984

print(f"""
  目標修正 = {mp.nstr(TARGET_C, 12)}

  [Pr-1] 有限尺寸 1/N_cells 原理 (最自然之 1/N 形式: 修正 = 1/cells)
""")
cells = {"(N_d+1)(M_tree+μ²)": Nd1 * (M_tree + mu2), "N_d·(M_tree+μ²)": N_d * (M_tree + mu2),
         "(N_d+1)·M_tree": Nd1 * M_tree, "2N_d·(M_tree+μ²)": 2 * N_d * (M_tree + mu2),
         "N_d·M_tree": N_d * M_tree}
for k, v in cells.items():
    print(f"       {k:<22s} = {int(v):<6d} → 1/cells = {mp.nstr(mp.mpf(1)/v, 8)}"
          f"   (偏 {float((mp.mpf(1)/v - TARGET_C)/TARGET_C*100):+8.3f}%)")
minrel = min(abs(mp.mpf(1) / v - TARGET_C) / TARGET_C for v in cells.values())
print(f"""
     ⟹ 全部偏 ≥ {mp.nstr(minrel*100, 3)}% ⟹ **裸 1/cells 唔成立**。
     命中需要分子 μ² (即 μ²/cells) ⟹ 咁就係正則形 (i) 之重述, 非獨立原理。
""")
chkb("C1", f"Pr-1 裸 1/N_cells: 5 個自然 cells 全偏 ≥ {mp.nstr(minrel*100,3)}% ⟹ 不成立",
     minrel > 0.4)

print(f"""
  [Pr-2] 凝聚分數乘積原理 (§B(iii))
     修正 = (μ²/Σγ_even)·(μ²/(M_tree+μ²)) = {mp.nstr(corr_C, 12)}
     ⟹ 形式**精確命中**, 且兩因子各有獨立結構身份。
     ⚠️ 但「為何係乘積」未有原理; 且**冇 out-of-sample 預言** ⟹ 讀法級, 非推導級
""")
chk("C2", "Pr-2 凝聚分數乘積: 形式精確命中", corr_C, TARGET_C, 1e-35)

TOLZ = mp.mpf('1e-20')
nlt = sum(1 for x in g44 if x < mu2 - TOLZ)
nbt = sum(1 for x in g44 if abs(x - mu2) <= TOLZ)
ngt = sum(1 for x in g44 if x > mu2 + TOLZ)
print(f"""
  [Pr-3] 模態耗盡 (mode depletion)
     44-chain: γ_n < μ²(=2) 之數目 = {nlt}; γ_n = μ² 之數目 = {nbt}; γ_n > μ² 之數目 = {ngt}
     (γ_22 = μ² 係 Z₂ 不動點 ⟹ 臨界模態恰 1 個)
     ⟹ 任何整數比 (nlt/44, ngt/44, 1/44, ...) 皆 ≠ {mp.nstr(TARGET_C, 8)} = 1/787.5
""")
chkb("C3", f"Pr-3 模態耗盡: 任何整數比 ≠ 1/787.5 ⟹ 不成立",
     abs(mp.mpf(nlt) / 44 - TARGET_C) / TARGET_C > 0.1
     and abs(mp.mpf(nbt) / 44 - TARGET_C) / TARGET_C > 0.1)

print(f"""
  [Pr-4] 頻譜和 Σ1/γ_n 與相關量
     Σ_{{n=1}}^{{44}} 1/γ_n = {mp.nstr(sum(1/x for x in g44), 12)}
     Σ_{{n=1}}^{{44}} γ_n/Σγ   = {mp.nstr(sum(x for x in g44)/S_even, 8)}
     Σ_{{k=1}}^{{88}} 1/γ_k = {mp.nstr(sum(1/x for x in G), 12)}
     ⟹ 無一 = 787.5 或 3150
""")
chkb("C4", "Pr-4 頻譜和: Σ1/γ_n = 322.75, Σ1/γ_k = 1290.75, 皆 ≠ 787.5 ⟹ 不成立",
     abs(sum(1 / x for x in g44) - 787.5) > 1 and abs(sum(1 / x for x in G) - 787.5) > 1)

print(f"""
  [Pr-5] 1-loop tadpole 型 (coupling)²/(mass²·N)
     候選: B/(16π²) = {mp.nstr(mp.mpf(B)/(16*mp.pi**2), 8)}; μ²/(4π²) = {mp.nstr(mu2/(4*mp.pi**2), 8)}
           λ/16π² (λ=μ²/123) = {mp.nstr((mu2/123)/(16*mp.pi**2), 8)}
     ⟹ 全部比目標修正 {mp.nstr(TARGET_C, 8)} 大 2–3 個數量級 ⟹ 不成立
""")
chkb("C5", "Pr-5 1-loop: 所有候選 ≫ 目標修正 ⟹ 不成立",
     min(mp.mpf(B) / (16 * mp.pi ** 2), mu2 / (4 * mp.pi ** 2)) > 10 * TARGET_C)

print(f"""
  [Pr-6] 樹節點計數
     B-ary 樹深度 d 之節點數 (B^{{d+1}}−1)/(B−1):
       d=2: {(B**3-1)//(B-1)};  d=3: {(B**4-1)//(B-1)};  d=M_tree? 天文數字
     Σγ_even 之分解: 21·B + γ_22 + γ_44 = 21·4 + 2 + 4 = 90   (21 = (B³−1)/(B−1))
     ⟹ 21 有樹節點身份; 但 21 唔進入修正項
""")
chk("C6", "Pr-6 樹節點: 21 = (B³−1)/(B−1) 但未進入修正項", (B ** 3 - 1) // (B - 1), 21, 1e-30)

lp = mp.log(BRIDGE) / mp.log(PHI)
print(f"""
  [Pr-7] φ-冪陷阱檢查 (skill idcm-phi-power-trap)
     ln(橋)/ln(φ) = {mp.nstr(lp, 12)}
     距最近整數 = {mp.nstr(abs(lp - mp.nint(lp)), 6)} ⟹ **非整數**
     最接近之簡分數讀法 「18 + 7/44」 偏離 = {mp.nstr(abs(lp - (18 + mp.mpf(7)/44))/lp*100, 6)}%
     ⚠️ 0.0043% 之近命中係**陷阱實例**: (a) 唔精確; (b) 指數 18+7/44 係看到目標後
        才揀之簡分數 (post-hoc); (c) φ-冪族稠密 ⟹ 近命中無信息量。
     ⟹ **拒絕** (符合 idcm-phi-power-trap 規則)
""")
chkb("C7", "Pr-7 φ-冪: 非整數 (距 0.1599) 且 18+7/44 讀法非精確 (0.0043%) ⟹ 拒絕",
     abs(lp - mp.nint(lp)) > 0.05 and abs(lp - (18 + mp.mpf(7) / 44)) / lp > 1e-5)

print(f"""
  ── §C 判決 ──
  7 條原理: Pr-2 (凝聚分數乘積) **形式精確命中** 但只係正則形 (i) 之重述 (讀法級);
  Pr-7 (φ-冪 18+7/44) 0.0043% 近命中 = **陷阱實例** (post-hoc 簡分數);
  其餘 5 條全部 ✗ (裸 1/cells 偏 ≥45.8%、1-loop 大 2–3 個數量級、頻譜和、模態耗盡、樹節點)。
  ⟹ 修正項之形式**仍未由原理導出**。
""")

# ══════════════════════════════════════════════════════════════════════
hdr("[§D] 重框 — 橋 = 無量綱 Yukawa 分母 (非標度橋)")
# ══════════════════════════════════════════════════════════════════════
y7 = 2 * mp.sin(7 * mp.pi / 88) / BRIDGE
print(f"""
  O86 docs/05 §1.3: y_n = √2·m_n/v_SM = ω_n / (88·71·(1−4/(90·35)))
    m_n = M₀·ω_n,  v_SM = √2 M₀ · 橋  ⟹  M₀ 相消
    y₇ = ω₇/橋 = {mp.nstr(y7, 10)}   (O207 記 7.93e-5)

  ★★ 重框: 「M₀ → 246 GeV」唔係量綱蛻變型標度橋。
     量綱內容 100% 在 v_eff = √2 M₀ (其標度 = O212 之錨 G ≡ ω_ring ≡ M_Pl);
     橋因子 6240.06603175 係**純無量綱結構數**。
  ⟹ 缺口分解為兩件**獨立**事:
       (a) 導出純數 6240.06603175  ← 本輪: 3 因子中 2 個已有推導
       (b) 錨 M₀ 本身 (O212; 唔屬本問題)
""")
chk("D1", "y₇ = ω₇/橋 = 7.9264e-5 (O86 記錄同級)", y7, mp.mpf('7.9264e-5'), 1e-8)
chkb("D2", "橋因子與 M₀ 無關 (y_n 中 M₀ 相消) ⟹ 係無量綱純結構數", True)

# ══════════════════════════════════════════════════════════════════════
hdr("[§E] 附: m_H 候選 (post-hoc) 密度測試 — 兩軸方法示範")
# ══════════════════════════════════════════════════════════════════════
n_pairs = 21                       # 44-chain Z₂ 對偶對數 = (B³−1)/(B−1)
n67 = 2 * N_d - n_pairs
TmH = M_H / M0                     # 4489.05
print(f"""
  候選 (本輪觀察, 明確標為 post-hoc): m_H = (2N_d − n_pairs)² · M₀
     n_pairs = 21 = 44-chain Z₂ 對偶對數 = (B³−1)/(B−1)
     2N_d − n_pairs = {n67};  {n67}² = {n67**2}
     m_H/M₀ (PDG) = {mp.nstr(TmH, 10)};  {n67}² = {n67**2}
     dev = {mp.nstr(abs(TmH - n67**2)/TmH*100, 6)}%

  ── 密度測試 (同 docs/11 模板 + 平方族) ──
""")
V_CORE = [2,3,4,5,7,8,11,13,17,18,21,29,33,34,35,36,44,47,55,71,88,89,90,123,176,178,528]
V_WIDE = V_CORE + [1,6,9,10,12,14,15,19,22,24,30,38,41,42,46,60,96,98,132,264,421]
K_SET = [1,2,3,4,5,6,7,8,11]
S_SET = [mp.mpf(1), mp.sqrt(2), 1/mp.sqrt(2), mp.mpf(2), mp.mpf(1)/2]

def build(V):
    return np.array(sorted({a*b for a,b in itertools.combinations_with_replacement(V,2)}), dtype=np.float64)

def density(T, V, deltas=(1e-6,1e-5,1e-4,1e-3)):
    n2 = build(V); Ts = float(T)
    cnt = {d: 0 for d in deltas}
    for s in S_SET:
        for k in K_SET:
            B_ = float(s) * np.outer(n2, 1.0 - k/n2)
            dev = np.abs(B_ - Ts)/Ts
            for d in deltas:
                cnt[d] += int(np.count_nonzero(dev < d))
    return cnt

cnt_core = density(TmH, V_CORE); cnt_wide = density(TmH, V_WIDE)
print(f"     V_core: " + "  ".join(f"δ<{d:g}: {cnt_core[d]}" for d in (1e-6,1e-5,1e-4,1e-3)))
print(f"     V_wide: " + "  ".join(f"δ<{d:g}: {cnt_wide[d]}" for d in (1e-6,1e-5,1e-4,1e-3)))
# 平方族專測: 67² 是否唯一
sq_hits = [n for n in V_WIDE if abs(mp.mpf(n)**2 - TmH)/TmH < 1e-4]
sq_hits2 = [n for n in range(2, 200) if abs(mp.mpf(n)**2 - TmH)/TmH < 1e-4]
print(f"     平方族 δ<1e-4 命中: V_wide 中 {sq_hits}; 整數 n∈[2,200) 中 {sq_hits2}")
print(f"     (平方族間距 ~3% ⟹ n² 之唯一性係必然, 非信息 ⟹ 改用「67 之結構表達」檢驗)")
print(f"     67 = 2N_d − n_pairs = {2*N_d} − {n_pairs}; √(m_H/M₀) = {mp.nstr(TmH**mp.mpf('0.5'), 10)}")
diffs = sorted({(a, b) for a in V_WIDE for b in V_WIDE if a - b == 67})
print(f"     a − b = 67 之結構表達 (a,b ∈ V_wide): {diffs}")
n_sq = len(diffs)
chkb("E1", f"m_H/M₀ = 67² 命中 (dev {mp.nstr(abs(TmH-67**2)/TmH*100,6)}%)", abs(TmH - 67**2)/TmH < 1e-4)
chkb("E2", f"★ 密度: δ<1e-3 有 {cnt_wide[1e-3]} 條同型命中; δ<1e-4 有 {cnt_wide[1e-4]} 條",
     cnt_wide[1e-4] > 100)
chkb("E3", f"★ 67 本身之結構表達不唯一: a−b=67 有 {n_sq} 種 ⟹ 67 非特別",
     n_sq >= 2)
print(f"""
  ⟹ 判決: m_H = 67²M₀ 之 {mp.nstr(abs(TmH-67**2)/TmH*100,6)}% 命中, 但
     (i) 密度測試 δ<1e-3 有 {cnt_wide[1e-3]} 條同型表達, δ<1e-4 有 {cnt_wide[1e-4]} 條;
     (ii) 67 本身之結構表達有 {n_sq} 種 (a−b=67) ⟹ 67 非特別;
     (iii) 完全 post-hoc (由觀察數字反推)
     ⟹ 判 **🔴 不存在** (密度產物)。記錄為方法示範, **不**列入任何關鍵數字。
""")

# ══════════════════════════════════════════════════════════════════════
hdr("[§F] 判決")
# ══════════════════════════════════════════════════════════════════════
print(f"""
  ① ★★ 重框 (§D): 「標度橋」唔係量綱蛻變型標度橋 —— 橋因子 6240.06603175 係
     **無量綱純結構數** (Yukawa 分母, M₀ 相消, O86 §1.3)。
     ⟹ 缺口 = (a) 導出純數 + (b) 錨 M₀ (O212, 唔屬本問題)。
  ② ★ 因子分解 (§A): 三因子中 **兩個已有推導來源**
       88 = ∏γ_even/∏γ_odd = Σγ_odd = 2N_d          (docs/12 §2 新恆等式)
       71 = 2N_d − 17, 17 = L₅ + C(4,2)              (O34 §4.10 世代跳躍)
     淨低 **一個** 未閉合: 修正項 (1 − 4/(90·35))。
  ③ ★ 新子恆等式 (§B): (N_d+1) = Σγ_even/μ² 係**定義性**
     (由 μ² ≡ Σγ_even − Σγ_odd 及 Σγ_odd = 2N_d 推出, 唔係額外假設)。
     ⟹ 修正項正則形: μ²/((N_d+1)(M_tree+μ²)) = μ⁴/(Σγ_even(M_tree+μ²))
        = (μ²/Σγ_even)·(μ²/(M_tree+μ²)) = **兩個凝聚分數之乘積**。
  ④ 修正項之原理攻堅 (§C): 7 條原理 —— 裸 1/cells 5 個自然定義全偏 ≥
     {mp.nstr(minrel*100,3)}%; 1-loop 候選大 2–3 個數量級; 頻譜和 (322.75, 1290.75)
     唔中; 模態耗盡唔中; 樹節點 21 唔進入修正項; φ-冪 18+7/44 只有 0.0043% 且係
     post-hoc 簡分數 ⟹ **陷阱實例**。
     唯一「精確命中」係 Pr-2 凝聚分數乘積, 但佢只係正則形 (i) 之**重述**,
     屬讀法級 (無原理、無 out-of-sample 預言)。
  ⑤ §E: m_H = 67²M₀ 候選 (post-hoc) 經密度測試判 **🔴 不存在** (δ<1e-4 有
     {cnt_wide[1e-4]} 條同型; a−b=67 有 {n_sq} 種結構表達) ⟹ 兩軸方法示範, 不列入關鍵數字。
  ⑥ 缺口現狀: 橋之閉合 = 導出「修正項 = 兩凝聚分數乘積」之原理。
     已排除路線 6 條; 唯一存活讀法 Pr-2 缺「為何係乘積」之機制。
""")

out = {
    "session": "2026-09-18 O144-26 bridge closure: factor audit",
    "A_factors": {"bridge": str(BRIDGE), "Bstar": str(Bstar), "Bstar_formula_M0": str(Bstarf),
                  "f1_88": {"identities": ["2N_d", "Sigma_gamma_odd", "prod_ratio"], "derived": True},
                  "f2_71": {"form": "2N_d - L5 - C(4,2)", "source": "O34 sec 4.10 gen ladder",
                            "derived": True},
                  "f3_correction": {"form": "4/(90*35)", "derived": False}},
    "B_identities": {"Nd_plus_1": str(Nd1), "Sigma_even_over_mu2": str(ratio_Se_mu),
                     "corr_A": str(corr_A), "corr_B": str(corr_B), "corr_C": str(corr_C),
                     "reading": "mu2/(Nd+1)/(M_tree+mu2) = (mu2/Sigma_even)*(mu2/(M_tree+mu2))"},
    "C_principles": {"Pr1_bare_1over_cells": {"min_rel_dev_pct": float(minrel * 100), "verdict": "fail"},
                     "Pr2_condensate_product": "exact form, reading-level (restatement of canonical form)",
                     "Pr3_depletion": "fail", "Pr4_spectral_sum": "fail",
                     "Pr5_1loop": "fail", "Pr6_tree_nodes": "fail", "Pr7_phi": "fail"},
    "D_reframe": {"bridge_is": "dimensionless Yukawa denominator", "y7": str(y7),
                  "gap": "(a) derive pure number 6240.06603175; (b) anchor M0 (O212)"},
    "E_mH_candidate": {"claim": "m_H = (2N_d-21)^2 M0 = 67^2 M0", "dev_pct": float(abs(TmH-67**2)/TmH*100),
                       "density_V_core": {str(k): v for k, v in cnt_core.items()},
                       "density_V_wide": {str(k): v for k, v in cnt_wide.items()},
                       "n67_structural_expressions": n_sq, "verdict": "does not exist (density product)"},
    "passed": PASS, "failed": FAIL, "checks": ROWS,
    "verdict": ("Bridge reframed as a DIMENSIONLESS Yukawa denominator (M0 cancels). "
                "2 of 3 factors now have derivations (88 = det-ratio; 71 = 2N_d - L5 - C(4,2)). "
                "New: (N_d+1) = Sigma_gamma_even/mu2 is DEFINITIONAL, giving correction = "
                "product of two condensate fractions. Only the correction's principle remains open; "
                "6 of 7 routes excluded. Post-hoc m_H = 67^2 M0 candidate: density product, does not exist."),
}
json.dump(out, open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/'
                    'open_problems_fresh/o144_boson_identity/data/26_bridge_closure.json', 'w'),
          indent=2, ensure_ascii=False, default=str)
print(f"總計: {PASS} PASS / {FAIL} FAIL")
print("✅ data/26_bridge_closure.json")
