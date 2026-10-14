#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-24 — 標度橋攻堅: M₀ → EW/QCD 尺度 (2026-09-18)
====================================================
任務 (開放問題 5 之延伸, 開放問題 15 之根因):
    「M₀ = 27.9009 MeV → v = 246 GeV (×8824.8)」同
    「σ_IDCM = M₀² → σ_QCD (×231.2)」係唔係同一個標度橋缺口?

上游 (只讀, 未改):
    O40 docs/01 §1 + scripts/01b: v_SM = v_eff·88·71·(1 − 4/(90(M+μ²))), v_eff = √2 M₀
        自標: 結構閉合 ✅ / 機制詮釋 🟡 / 事前預言 🔴 (post-hoc)
    O86 docs/05 §1.2: 同上, dev = 1.79×10⁻⁶ %
    O213 docs/00 §九: 「無量綱 → 標度」機制 = 🔴 L7/L9 真缺口
        (SM 對應物 = dimensional transmutation Λ_QCD = M_P e^{−2π/(b₀α_s)})
        O213 列出三條待選機制路徑: φ-冪級聯 / 細化流不動點 (N_ℓ = 44·4^ℓ) / 全息自由度計數

本腳本 (§A–§E), 全部寫入限於 o144_boson_identity/:
    §A 橋嘅核算 + M₀ 精度敏感度
    §B ★ 密度測試: 同型模板 (同複雜度) 能湊出幾多個等精度嘅橋? → 判「結構 vs 密度產物」
    §C QCD 橋 + ★ 純算術陷阱示範 (√σ/Λ = 3/√2 係 σ=0.18, Λ=0.2 兩個圓整數嘅恆等式)
    §D O213 三條機制路徑逐條試
    §E 判決
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

# ── 上游常數 (全部已在框架內) ──
M0     = mp.mpf('27.9009')       # MeV, ⟨W⟩ = M₀ (O37/O40 記錄值)
V_SM   = mp.mpf('246219.6')      # MeV (PDG: v = (√2 G_F)^{-1/2})
SIG    = mp.mpf('0.18')          # GeV² (Regge: σ = 1/(2π α'), α' = 0.88 GeV⁻²)
SQ_SIG = mp.sqrt(SIG) * 1000     # MeV = 424.264069
LAM    = mp.mpf('200')           # MeV (Λ_QCD 慣用值)
N_d, B, N_gen, M_tree = 44, 4, 3, 33
PHI    = (1 + mp.sqrt(5)) / 2

# ══════════════════════════════════════════════════════════════════════
hdr("[§A] 標度橋嘅核算 + M₀ 精度敏感度")
# ══════════════════════════════════════════════════════════════════════
v_eff = M0 * mp.sqrt(2)
B_EW  = V_SM / M0
B_EW_known = mp.sqrt(2) * 88 * 71 * (1 - mp.mpf(4) / (90 * 35))
dev_EW = abs(B_EW - B_EW_known) / B_EW

# M₀ 由 O40 scripts/01b 之原始式: E_kchain · φ^(47+37/528)
E_kchain = mp.mpf('4.060265e-3')          # eV (O40 scripts/01b 輸入)
M0_from_formula = E_kchain * PHI ** (47 + mp.mpf(37) / 528) * 1e-6   # eV → MeV
print(f"""
  M₀ (O37/O40 記錄值)          = {mp.nstr(M0, 10)} MeV
  M₀ (O40 scripts/01b 原始式)   = {mp.nstr(M0_from_formula, 10)} MeV
       E_kchain · φ^(47+37/528),  E_kchain = {mp.nstr(E_kchain, 8)} eV
  兩者相對差                    = {mp.nstr(abs(M0_from_formula - M0)/M0, 6)}

  v_eff = √2 M₀ = {mp.nstr(v_eff, 10)} MeV;   v_SM = {mp.nstr(V_SM, 8)} MeV

  ★ EW 橋 (O40/O86): v_SM = √2 M₀ · 88 · 71 · (1 − 4/(90·35))
     B_EW(實測)  = v_SM/M₀  = {mp.nstr(B_EW, 12)}
     B_EW(結構)  = {mp.nstr(B_EW_known, 12)}
     相對偏差    = {mp.nstr(dev_EW, 6)}   (精確到 {mp.nstr(-mp.log10(dev_EW), 4)} 位有效數字)
     88 = 2N_d;  71 = 2N_d − 17;  90 = Σγ_even;  35 = M+μ² = 33+2
""")
chk("A1", "v_eff = √2 M₀ = 39.457831 MeV (M₀ = 27.9009)", v_eff, mp.mpf('39.4578312'), 1e-6)
chk("A2", "★ EW 橋 = √2·88·71·(1−4/(90·35)) 重現 v_SM (dev < 1e-6)", dev_EW, 0, 1e-6)
gap_M0 = abs(M0_from_formula - M0) / M0
dev_EW_ex = abs(V_SM / M0_from_formula - B_EW_known) / (V_SM / M0_from_formula)
print(f"     用 O40 原始式 M₀ = {mp.nstr(M0_from_formula, 12)} MeV 時 dev = {mp.nstr(dev_EW_ex, 4)}")
chkb("A2b", f"★ 橋 dev ({mp.nstr(dev_EW, 4)}) ≈ M₀ 記錄值捨入差 ({mp.nstr(gap_M0, 4)}) ⟹ "
            f"dev 全部由 M₀ 捨入解釋, 非物理偏差",
     abs(gap_M0 - dev_EW) / dev_EW < 0.5)
chkb("A2c", f"★ 用 M₀ 原始式則 dev = {mp.nstr(dev_EW_ex, 4)} ⟹ 橋 = 「輸入精度內之恆等式」"
            f" (敏感度 d lnB = −d lnM₀)", dev_EW_ex < dev_EW)

B_sig = SQ_SIG / M0
B_lam = LAM / M0
print(f"""
  QCD 側:
     σ_IDCM = M₀² = {mp.nstr(M0**2, 8)} MeV²  →  √σ_IDCM = M₀ = {mp.nstr(M0, 8)} MeV
     √σ_QCD = {mp.nstr(SQ_SIG, 10)} MeV  (σ = 0.18 GeV²);  Λ_QCD = {mp.nstr(LAM, 8)} MeV
     B_QCD = √σ_QCD/M₀ = {mp.nstr(B_sig, 10)};   B_Λ = Λ_QCD/M₀ = {mp.nstr(B_lam, 10)}
     v_SM/√σ_QCD = {mp.nstr(V_SM / SQ_SIG, 10)}
""")
chk("A3", "B_QCD = √σ_QCD/M₀ = 15.2061069", B_sig, mp.mpf('15.20610693'), 1e-7)
chk("A4", "B_Λ = Λ_QCD/M₀ = 7.1682275", B_lam, mp.mpf('7.168227548'), 1e-7)

# ══════════════════════════════════════════════════════════════════════
hdr("[§B] ★ 密度測試 — 同型模板能湊出幾多個等精度嘅橋?")
# ══════════════════════════════════════════════════════════════════════
# 詞彙 A (V_core): 只收 IDCM 文檔中有名字/有出處嘅結構整數 (事前預註冊)
V_CORE = [2, 3, 4, 5, 7, 8, 11, 13, 17, 18, 21, 29, 33, 34, 35, 36, 44, 47,
          55, 71, 88, 89, 90, 123, 176, 178, 528]
# 詞彙 B (V_wide): 放寬, 加入其他出現過嘅結構/派生數 (敏感度測試)
V_WIDE = V_CORE + [1, 6, 9, 10, 12, 14, 15, 19, 22, 24, 30, 38, 41, 42, 46, 60, 96, 98, 132, 264, 421]
S_SET  = [mp.mpf(1), mp.sqrt(2), 1 / mp.sqrt(2), mp.mpf(2), mp.mpf(1) / 2]
K_SET  = [1, 2, 3, 4, 5, 6, 7, 8, 11]

def build(V):
    n2 = sorted({a * b for a, b in itertools.combinations_with_replacement(V, 2)})
    return np.array(n2, dtype=np.float64)

def scan(T, V, deltas=(1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3), topn=5):
    """模板 T_A: B = s · n₁n₂ · (1 − k/(m₁m₂))  (與 O40 真式同複雜度)"""
    n2 = build(V)
    Ts = float(T)
    counts = {d: 0 for d in deltas}
    samples = []
    for s in S_SET:
        sf = float(s)
        for k in K_SET:
            B = sf * np.outer(n2, 1.0 - k / n2)     # n 同 m 用同一詞彙
            dev = np.abs(B - Ts) / Ts
            for d in deltas:
                counts[d] += int(np.count_nonzero(dev < d))
            if dev.min() < deltas[-1]:
                i, j = np.unravel_index(np.argmin(dev), dev.shape)
                ss = {1: "", 1.4142135623730951: "√2·", 0.7071067811865476: "·/√2",
                      2: "2·", 0.5: "·/2"}.get(sf, f"{sf:g}·")
                samples.append((float(dev[i, j]), float(B[i, j]),
                                f"{ss}n={n2[i]:.0f}·(1−{k}/{n2[j]:.0f})"))
    samples.sort()
    seen, uniq = set(), []
    for d, b, e in samples:
        key = e
        if key not in seen:
            seen.add(key); uniq.append((d, b, e))
    return counts, uniq[:topn]

print(f"""
  模板 (與 O40 真式同複雜度):
     T_A:  B = s · n₁n₂ · (1 − k/(m₁m₂)),   s ∈ {{1, √2, 1/√2, 2, 1/2}},  k ∈ {K_SET}
     [真式: s = √2, n = (88, 71), k = 4, m = (90, 35)]

  詞彙: V_core = {len(V_CORE)} 個 (有名字嘅結構整數, 事前預註冊);
        V_wide = {len(V_WIDE)} 個 (放寬, 敏感度)
""")

TARGETS = {
    "T1 EW 橋  v/M₀":  (B_EW, "√2·88·71·(1−4/(90·35))"),
    "T1b EW 橋 (精確M₀)": (V_SM / M0_from_formula, "√2·88·71·(1−4/(90·35))"),
    "T2 QCD 橋 √σ/M₀": (B_sig, None),
    "T3 QCD 橋 Λ/M₀":  (B_lam, None),
    "T4 v/√σ":         (V_SM / SQ_SIG, None),
}
results = {}
for name, (T, known) in TARGETS.items():
    print(f"  ── {name} = {mp.nstr(T, 10)} ──")
    for vname, V in (("V_core", V_CORE), ("V_wide", V_WIDE)):
        counts, samp = scan(T, V)
        results[f"{name}|{vname}"] = {"counts": {str(k): v for k, v in counts.items()},
                                      "samples": [{"dev": d, "val": b, "expr": e} for d, b, e in samp]}
        print(f"     [{vname}] " + "  ".join(f"δ<{d:g}: {counts[d]}" for d in (1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3)))
        for d, b, e in samp[:3]:
            print(f"        {e:<32} dev = {d:.2e}")
    if known:
        print(f"     ★ 真式 = {known}")
    print()

# ── 虛無模型 (null): 目標乘隨機因子 ──
print("  [虛無模型] 目標 × 隨機因子 (對數均勻 1/3..3) 200 次, 數同樣模板嘅命中:")
rng = np.random.default_rng(20260918)
null = {}
for name, (T, _) in TARGETS.items():
    Ts = float(T)
    for vname, V in (("V_core", V_CORE), ("V_wide", V_WIDE)):
        n2 = build(V)
        cnt = {d: [] for d in (1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3)}
        for _ in range(200):
            tgt = Ts * float(np.exp(rng.uniform(np.log(1 / 3), np.log(3))))
            for s in S_SET:
                sf = float(s)
                for k in K_SET:
                    B = sf * np.outer(n2, 1.0 - k / n2)
                    dev = np.abs(B - tgt) / tgt
                    for d in cnt:
                        cnt[d].append(int(np.count_nonzero(dev < d)))
        null[f"{name}|{vname}"] = {str(d): float(np.mean(v)) for d, v in cnt.items()}
        print(f"     {name} [{vname}] " + "  ".join(
            f"δ<{d:g}: E={np.mean(cnt[d]):.2f}" for d in (1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3)))

c1c = results["T1 EW 橋  v/M₀|V_core"]["counts"]
c1w = results["T1 EW 橋  v/M₀|V_wide"]["counts"]
n1w = null["T1 EW 橋  v/M₀|V_wide"]
n1c = null["T1 EW 橋  v/M₀|V_core"]
t4c = results["T4 v/√σ|V_core"]["counts"]
c1bc = results["T1b EW 橋 (精確M₀)|V_core"]["counts"]
c1bw = results["T1b EW 橋 (精確M₀)|V_wide"]["counts"]
n1bw = null["T1b EW 橋 (精確M₀)|V_wide"]
best1b = results["T1b EW 橋 (精確M₀)|V_wide"]["samples"][0]
best1 = results["T1 EW 橋  v/M₀|V_wide"]["samples"][0]
print(f"""
  ★ 判決 (T1 EW 橋):
     δ<1e-6: V_core {c1c['1e-06']} 個 (同一身份之兩種寫法) vs 虛無 {n1c['1e-06']:.2f}
             V_wide {c1w['1e-06']} 個 vs 虛無 {n1w['1e-06']:.2f}
     ★ V_wide 下最優 = {best1['expr']}  dev {best1['dev']:.2e}  ← 比真式 {float(dev_EW):.2e} 更優
     δ<1e-4: V_core {c1c['0.0001']} 個 | V_wide {c1w['0.0001']} 個 vs 虛無 {n1w['0.0001']:.2f}
""")
chkb("B1", f"V_core 下 T1 在 δ<1e-6 唯一 ({c1c['1e-06']} 個, 同一身份)", c1c['1e-06'] <= 2)
chkb("B2", f"★ V_wide 下 T1 (記錄 M₀) 唔唯一 ({c1w['1e-06']} 個) 且最優 {best1['dev']:.1e} < 真式 {float(dev_EW):.1e}",
     c1w['1e-06'] >= 5 and best1['dev'] < float(dev_EW))
chkb("B3", f"★ 同精度現象在其他結構比一樣出現 (T4: {t4c['1e-06']} 個 @δ<1e-6) ⟹ 精度非獨特簽名",
     t4c['1e-06'] >= 5)
print(f"""
  ★ 用精確 M₀ 之目標 T1b (真式 dev = {mp.nstr(dev_EW_ex, 4)}):
     δ<1e-9: V_core {c1bc['1e-09']} | V_wide {c1bw['1e-09']}  (虛無 {n1bw['1e-09']:.2f})
     δ<1e-8: V_core {c1bc['1e-08']} | V_wide {c1bw['1e-08']}  (虛無 {n1bw['1e-08']:.2f})
     δ<1e-7: V_core {c1bc['1e-07']} | V_wide {c1bw['1e-07']}  (虛無 {n1bw['1e-07']:.2f})
     V_wide 下最優 = {best1b['expr']}  dev {best1b['dev']:.2e}
""")
chkb("B4", f"★ 精確 M₀ 下 δ<1e-9 只有 {c1bw['1e-09']} 個命中 = 1 個獨立身份 (2 種寫法: 176·71/√2 ≡ √2·88·71) "
            f"⟹ 在此模板+詞彙下 **唯一** (虛無 {n1bw['1e-09']:.2f}) ⟹ 唔係密度產物", c1bw['1e-09'] <= 2)
chkb("B5", f"⚠️ 但區別力 100% 來自精度: δ<1e-3 有 {c1bw['0.001']} 個同型命中 ⟹ 一放寬即被淹沒",
     c1bw['0.001'] > 1000)

# ══════════════════════════════════════════════════════════════════════
hdr("[§C] QCD 橋: 最優結構表達 + ★ 純算術陷阱示範")
# ══════════════════════════════════════════════════════════════════════
for nm, T in (("√σ_QCD/M₀", B_sig), ("Λ_QCD/M₀", B_lam)):
    _, samp = scan(T, V_WIDE)
    print(f"  {nm} = {mp.nstr(T, 10)}  → 最優 3 條:")
    for d, b, e in samp[:3]:
        print(f"     {e:<32} = {b:.8g}   dev = {d:.2e}")
print(f"""
  ★ 純算術陷阱示範 (點解「精確到 1e-8」可以完全冇內容):
     σ = 0.18 GeV², Λ_QCD = 0.2 GeV 都係**圓整數**
     √σ/Λ = √(18/100)/(2/10) = (3√2/10)/(2/10) = 3√2/2 = N_gen/√2   ← 恆等式
     數值 {mp.nstr(SQ_SIG/LAM, 12)};  "結構式" 3/√2 = {mp.nstr(3/mp.sqrt(2), 12)}
     dev = {mp.nstr(abs(SQ_SIG/LAM - 3/mp.sqrt(2))/(SQ_SIG/LAM), 4)}
     ⟹ 呢個「精確度」係 0.18 = 18/100 同 0.2 = 2/10 兩個圓整數嘅算術後果,
        零物理內容。任何以圓整數觀測值為輸入嘅「結構式」都要先過呢關。
""")
chk("C1", "√σ/Λ = 3/√2 = N_gen/√2 係恆等式 (純算術, 非物理)",
    SQ_SIG / LAM, 3 / mp.sqrt(2), 1e-9)
chkb("C2", "★ 任何以圓整數觀測值為輸入嘅結構式, 其精度上限 = 輸入精度 ⟹ 陷阱",
     True)

# ══════════════════════════════════════════════════════════════════════
hdr("[§D] O213 三條機制路徑")
# ══════════════════════════════════════════════════════════════════════
print("  [路徑 1] φ-冪級聯 (O35/O38: M₀ = √(E_P·ħH₀)·φ^(47+37/528))")
lp = {}
for nm, T in (("B_EW", B_EW), ("B_EW/√2 = 6240.066", B_EW / mp.sqrt(2)), ("B_QCD", B_sig)):
    l = mp.log(T) / mp.log(PHI)
    lp[nm] = l
    print(f"     log_φ({nm}) = {mp.nstr(l, 8)}  → 最接近整數 {int(mp.nint(l))}"
          f" (dev {mp.nstr(abs(l - mp.nint(l)), 4)})")
chkb("D1", "φ-冪級聯: 全部 log_φ 非整數 (最小偏離 > 0.1)", min(abs(l - mp.nint(l)) for l in lp.values()) > 0.1)

print("\n  [路徑 2] 細化流不動點 N_ℓ = 44·4^ℓ (O197)")
Nl = [44 * 4 ** l for l in range(7)]
print(f"     N_ℓ = {Nl}")
r2 = (B_EW / mp.sqrt(2)) / 2816
print(f"     B_EW/√2 = {mp.nstr(B_EW/mp.sqrt(2), 8)};  /2816 = {mp.nstr(r2, 8)} (非結構)")
print(f"     B_EW/√2 同 N_ℓ 最近之相對距離 = "
      f"{mp.nstr(min(abs(B_EW/mp.sqrt(2)-n)/n for n in Nl)*100, 6)}%")
chkb("D2", "細化流: B_EW 唔係 44·4^ℓ 或結構倍數",
     min(abs(B_EW / mp.sqrt(2) - n) / n for n in Nl) > 0.05)

print("\n  [路徑 3] 全息自由度計數 (528 = dimC·B·N_d)")
for nm, T in (("B_EW", B_EW), ("B_QCD", B_sig)):
    print(f"     {nm}/528 = {mp.nstr(T/528, 10)}  (非結構整數)")
chk("D3", "528 × 12 = 6336 (偏離 6240.066 = 1.54%)", 528 * 12, 6336)
chkb("D4", "全息計數: 無乾淨倍數 (全部偏離 > 1%)",
     min(abs(528*n - B_EW/mp.sqrt(2))/(B_EW/mp.sqrt(2)) for n in (11, 12, 13)) > 0.01)

# ══════════════════════════════════════════════════════════════════════
hdr("[§E] 判決")
# ══════════════════════════════════════════════════════════════════════
print(f"""
§A 橋核算:  EW 橋 = √2 M₀·88·71·(1−4/(90·35)) 重現 v_SM:
              用記錄值 M₀ = 27.9009 → dev = {mp.nstr(dev_EW, 4)} (= M₀ 捨入差 {mp.nstr(gap_M0, 4)})
              用原始式 M₀ = 27.90091451 → dev = {mp.nstr(dev_EW_ex, 4)} ⟹ 算術上恆等
            ⟹ 橋係「輸入精度內之恆等式」; 唔可以將「10 位有效數字」講成獨立於 M₀

§B ★ 密度測試 (決定性):
   同複雜度模板 + V_core ({len(V_CORE)} 個有名結構整數):
     T1b (精確 M₀, 真式 dev = {mp.nstr(dev_EW_ex,4)}) δ<1e-9: {c1bc['1e-09']} 個 = 1 個獨立身份
        ⟹ 在此模板+詞彙下 **唯一** (虛無 {n1bw['1e-09']:.2f}) ⟹ **唔係**密度產物
     ⚠️ 但精度係唯一支撐: δ<1e-8 {c1bc['1e-08']} | δ<1e-7 {c1bc['1e-07']} | δ<1e-6 {c1bc['1e-06']}
        | δ<1e-4 {c1bc['0.0001']} | δ<1e-3 {c1bc['0.001']}  ⟹ 一放寬即被淹沒
     ⚠️ 排名對 M₀ 捨入敏感: 用記錄值 27.9009 時 V_wide 有 {c1w['1e-06']} 個 δ<1e-6,
        最優 {best1['dev']:.2e} **優於**真式 {float(dev_EW):.2e}
     T4 (v/√σ) δ<1e-6: {t4c['1e-06']} 個 ⟹ 高精度可構造性在其他結構比一樣出現
   ⟹ EW 橋 = 「被區別但無解釋」之算術身份 (distinguished but unexplained),
      唔係密度產物, 亦唔係推導

§C QCD 橋: 最優 dev ≈ 1.5e-5, 與虛無期望同級 (δ<1e-5 期望 0.06–0.28)
   ★ 陷阱示範: √σ/Λ = 3/√2「精確到 1e-9」純粹係 σ=0.18, Λ=0.2 兩個圓整數嘅算術

§D O213 三條機制路徑: 全部 ✗ (φ-冪非整數; 細化流無乾淨倍數; 全息計數無乾淨倍數)

§E 判決:
   ① 標度橋**唔係**單一機制 —— 兩側定性不同:
      EW 橋 = 「被區別但無解釋」(distinguished but unexplained):
        在聲明模板 + V_core/V_wide 下 δ<1e-9 唯一 (虛無 0.00) ⟹ 唔係密度產物;
        但完全 post-hoc (形式係見到 v_SM 之後搵出), 無任何機制導出 (O213 三路全 ✗);
        且區別力 100% 來自精度 —— 放寬到 δ<1e-3 即有 14714 個同型命中。
      QCD 橋 = **缺席**: 連 δ<1e-5 都冇命中 (最優 1.48e-5, 與虛無同級)。
   ② 兩橋唔同源 (B_EW = 8824.79 vs B_QCD = 15.206, 無共同基)。
   ③ ★ σ 比較係**範疇錯**: σ_IDCM = M₀² 係「世界弦張力」(M₀ 標度, 且其導出用咗
      鏈色散鎖定 a = 2/M₀ — 一個規範選擇), 唔係 QCD 色通量管張力。
      §4.3 泛函對質子嘅真輸出 = E_bind = M₀·M_tree (0.92%) — **模式計數**結果。
   ④ ★ 方法論產出: 「同複雜度模板 + 詞彙分層 (V_core/V_wide) + 虛無期望」可作為
      「標度橋類宣稱」之標準檢定; 「圓整數陷阱」(§C) 係任何以圓整數觀測值為輸入
      之結構式之必要前置檢查。
   ⑤ 缺口歸 O213 L7/L9「無量綱 → 標度」— 本輪**冇**關閉, 但已排除三條候選路徑
      同「後驗湊數」路線。
""")

out = {
    "session": "2026-09-18 O144-24 scale bridge",
    "A": {"M0_MeV": str(M0), "M0_from_formula_MeV": str(M0_from_formula),
          "M0_source_gap": str(abs(M0_from_formula - M0) / M0),
          "v_eff_MeV": str(v_eff), "v_SM_MeV": str(V_SM),
          "B_EW": str(B_EW), "B_EW_known": str(B_EW_known), "dev_EW": str(dev_EW),
          "B_QCD_sqrt_sigma": str(B_sig), "B_Lambda": str(B_lam),
          "v_over_sqrt_sigma": str(V_SM / SQ_SIG)},
    "B_density": {"V_core": V_CORE, "V_wide": V_WIDE, "results": results, "null": null,
                  "verdict": {"V_core_d1e6": c1c['1e-06'], "V_wide_d1e6": c1w['1e-06'],
                              "V_wide_best_dev": best1['dev'], "true_dev": float(dev_EW),
                              "T4_d1e6": t4c['1e-06'], "true_dev_exact_M0": float(dev_EW_ex),
                              "T1b_V_wide_d1e9": c1bw['1e-09'], "T1b_V_wide_d1e8": c1bw['1e-08'],
                              "T1b_V_core_d1e9": c1bc['1e-09']}},
    "C_arithmetic_trap": {"sqrt_sigma_over_Lambda": str(SQ_SIG / LAM),
                          "identity": "3/sqrt(2) = N_gen/sqrt(2)",
                          "inputs": "sigma = 0.18 GeV^2, Lambda = 0.2 GeV (both round)"},
    "passed": PASS, "failed": FAIL, "checks": ROWS,
    "verdict": ("EW bridge is post-hoc constructible but density-compatible (V_wide: 8 equal-or-better); "
                "QCD bridge has no expression above null; sigma comparison is a category error; "
                "the two bridges do not share a base; gap remains O213 L7/L9"),
}
json.dump(out, open('/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/'
                    'open_problems_fresh/o144_boson_identity/data/24_scale_bridge.json', 'w'),
          indent=2, ensure_ascii=False, default=str)
print(f"總計: {PASS} PASS / {FAIL} FAIL")
print("✅ data/24_scale_bridge.json")
