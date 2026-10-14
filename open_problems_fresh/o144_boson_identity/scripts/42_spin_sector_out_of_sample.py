#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144-42 — 樣本外自旋扇區: decuplet (J=3/2) + 向量介子 (J=1) 盲測
==================================================================
問題: scripts/40/41 已證 R_h 非 quark-multiset 函數 (η/η′/Λ 同 nodes 三 R_h)
⟹ 連結層必含態量子數。本輪第一次用**樣本外**數據做自旋項檢驗:
decuplet 重子 (Δ, Σ*, Ξ*, Ω) 同向量介子 (ρ, K*, D*, B*, φ, ηc, ηb...) 從來
冇入過 O238/O144 任何 fit — 完美 blind set (預註冊, 零 tune)。

★ 預註冊 (跑前凍結):
  [P1] 節點方案: 主 = NB (m_Q(1S): c=J/ψ/2=1548.45, b=ϒ/2=4730.15, 經 scripts/41
       正性審計; 輕味 u,d,s = O238 anchors); 對照 = NA (c=1088.297)
  [P2] R_h = (M_obs − Σnodes)/M₀ (M₀=27.90091451); **樣本外 = decuplet 4 +
       向量/偽純量介子 7 = 11 態** (ρ,φ,K*,D*,B*,ηc,ηb 全部 PDG 2024 標準值)
  [P3] 自旋項檢驗 (單一預註冊候選, 唔准 tune):
       H1: decuplet-octet 等味分裂 (S=3/2 vs 1/2 對) = F₈/2·M₀ = 10.5 M₀
           (F₈=21, O137 結構常數; 對應 S(S+1) 差 3/2 單位 × 7 = 21/2)
       P3A: 每對偏差 |ΔR − 10.5| ≤ 1σ*3 (σ* = 0.1 M₀, PDG ±1 MeV + node 誤差)
       P3B: 符號: 全部 decuplet R_h > octet 對應 R_h (自旋項正)
  [P4] 向量-偽純量分裂 (ρ−π, K*−K, D*−D0, B*−B0, φ−η, J/ψ−ηc, ϒ−ηb):
       只記錄單調性 (跨味 sector 減細) — 現象層, 唔係算子; 若單調 7/7 記 ✅
  [P5] 判決: H1 PASS ⟹ 自旋項 = F₈/2·M₀ (零參數閉合, 需進一步樣本外); FAIL ⟹
       誠實負 + 記錄 decuplet/vector R_h 表 (下階段假說種子, 禁砌算子)

輸出: data/42_spin_sector_out_of_sample.json
"""
import json

M0 = 27.90091451
NA = {"u": 93.4 / 42.890, "d": 93.4 / 42.890 * 2.1505, "s": 93.4,
      "c": 93.4 * 11.652, "b": 93.4 * 11.652 * 4.586}
NB = dict(NA)
NB["c"] = 3096.9 / 2
NB["b"] = 9460.30 / 2

# (name, mass MeV, quark content, sector/J)
# 重子: p/n/Λ/Σ+/Ξ0 已喺 scripts/41 (octet, J=1/2) — 呢度只有 decuplet (J=3/2) 新牌
BARYONS_DEC = {
    "Delta(1232)": (1232.0, ["u", "u", "u"]),   # J=3/2
    "Sigma*(1385)": (1383.7, ["u", "d", "s"]),
    "Xi*(1530)": (1535.0, ["u", "s", "s"]),
    "Omega(1672)": (1672.45, ["s", "s", "s"]),
}
MESON_VP = {
    "rho(770)": (775.11, ["u", "d"]),       # J=1 vs pi0 J=0
    "K*(892)": (895.55, ["d", "s"]),
    "phi(1020)": (1019.461, ["s", "s"]),
    "D*(2010)": (2010.26, ["c", "d"]),
    "B*(5325)": (5325.2, ["b", "d"]),
    "eta_c(1S)": (2983.9, ["c", "c"]),
    "eta_b(1S)": (9398.0, ["b", "b"]),
}
# octet 對應 (scripts/41 data — 同一 nodes)
OCTET = {
    "p": (938.272088, ["u", "u", "d"]),
    "n": (939.565421, ["u", "d", "d"]),
    "Lambda": (1115.683, ["u", "d", "s"]),
    "Sigma+": (1189.37, ["u", "u", "s"]),
    "Xi0": (1314.86, ["u", "s", "s"]),
}
# vector-pseudoscalar 對 (PDG)
VP_PAIRS = [("rho(770)", "pi0", 134.9768), ("K*(892)", "K0", 497.611),
            ("D*(2010)", "D0", 1864.84), ("B*(5325)", "B0", 5279.63),
            ("phi(1020)", "eta_s(est)", None), ("eta_c(1S)", "J/psi_p", 3096.9),
            ("eta_b(1S)", "Upsilon_p", 9460.30)]
# φ: 用純 s 估算? 唔 — φ−η 混合唔乾淨, 用 φ−η 但標明混合 (描述)
VP_PAIRS_CLEAN = [("rho(770)", 134.9768), ("K*(892)", 497.611),
                  ("D*(2010)", 1864.84), ("B*(5325)", 5279.63),
                  ("eta_c(1S)", 3096.9), ("eta_b(1S)", 9460.30)]

def R(name, ms, scheme):
    return (name[0] - sum(scheme[m] for m in ms)) / M0

print("═══ §1 樣本外 decuplet R_h (NB 主方案) ═══")
decR = {}
for nm, (m, ms) in BARYONS_DEC.items():
    r = R((m,), ms, NB)
    decR[nm] = round(r, 4)
    print(f"  {nm:>14s} {m:9.3f}  nodes={ms}  R_h = {r:8.4f} M₀")

print("\n═══ §2 decuplet-octet 等味分裂 vs 候選 H1 = F₈/2·M₀ = 10.5 M₀ ═══")
PAIRS = [("Delta(1232)", "p"), ("Sigma*(1385)", "Lambda"), ("Xi*(1530)", "Xi0"), ("Omega(1672)", "Sigma+")]
# Ω 冇直 octet 對 (sss octet 唔存在) — 用 Σ+ 對當近似? 唔 — 只用 3 對真等味/近味對
PAIRS = [("Delta(1232)", "p"), ("Sigma*(1385)", "Lambda"), ("Xi*(1530)", "Xi0")]
H1 = 21 / 2  # 10.5
hits = 0
for bn, on in PAIRS:
    mb, msb = BARYONS_DEC[bn]
    mo, mso = OCTET[on]
    # R diff (NB 方案 — 重味冇, c/b 唔涉及, 所以 NB=NA 一致)
    rb = (mb - sum(NB[m] for m in msb)) / M0
    ro = (mo - sum(NB[m] for m in mso)) / M0
    d = rb - ro
    ok3 = abs(d - H1) <= 0.3  # 3σ*, σ*=0.1
    hits += ok3
    print(f"  {bn:>14s} − {on:>7s}: R {rb:7.4f} − {ro:7.4f} = {d:7.4f} M₀ vs {H1}  "
          f"{'✅' if ok3 else '✗'} (dev {abs(d-H1):.2f} M₀)")
    print(f"      nodes: {msb} (sum {sum(NB[m] for m in msb):8.3f}) vs {mso} (sum {sum(NB[m] for m in mso):8.3f})"
          f" — 純自旋對應 {'✅' if sum(NB[m] for m in msb)==sum(NB[m] for m in mso) else '味差已計'}")

print("\n═══ §3 decuplet 內部分裂 (J=3/2 家族等差) ═══")
names = list(BARYONS_DEC.keys())
vals = [(BARYONS_DEC[n][0] - sum(NB[m] for m in BARYONS_DEC[n][1])) / M0 for n in names]
for i in range(len(names) - 1):
    print(f"  {names[i+1]} − {names[i]}: {vals[i+1]-vals[i]:+.3f} M₀ ({(BARYONS_DEC[names[i+1]][0]-BARYONS_DEC[names[i]][0]):.2f} MeV)")

print("\n═══ §4 向量−偽純量分裂 (J=1 − J=0, 同 nodes) ═══")
splits = []
for vn, pt in VP_PAIRS_CLEAN:
    mv, msv = MESON_VP[vn]
    d = (mv - pt) / M0
    splits.append(d)
    print(f"  {vn:>14s} − ps: {d:7.3f} M₀ ({(mv-pt):7.2f} MeV)")
mono = all(splits[i] > splits[i + 1] for i in range(len(splits) - 1))
print(f"  單調減細 (味 sector 加大): {'✅ 5/5' if mono else '✗'}   — 現象層記錄")
# 補: J/ψ−ηc, ϒ−ηb
for vn, pt, lab in (("eta_c(1S)", 3096.9, "J/psi"), ("eta_b(1S)", 9460.30, "Upsilon")):
    mv0 = MESON_VP[vn][0]
    print(f"  {lab} − {vn}: {(mv0-pt)/M0:7.3f} M₀ ({(mv0-pt):7.2f} MeV)")

print("\n═══ §5 判決 ═══")
print(f"  H1 (F₈/2 = 10.5 M₀): {hits}/3 等味對命中 (P3A ≤3σ*)")
dec_pos = all(decR[nm] > (OCTET[on][0] - sum(NB[m] for m in OCTET[on][1])) / M0
              for nm, on in PAIRS)
print(f"  P3B decuplet>octet 符號: {'✅' if dec_pos else '✗'}")

OUT = {"M0": M0, "H1": H1, "decuplet_R": decR,
       "octet_R": {n: round((m - sum(NB[q] for q in ms)) / M0, 4) for n, (m, ms) in OCTET.items()},
       "pair_splits": {f"{bn}-{on}": round((BARYONS_DEC[bn][0]-sum(NB[m] for m in BARYONS_DEC[bn][1]))/M0
                      - (OCTET[on][0]-sum(NB[m] for m in OCTET[on][1]))/M0, 4) for bn, on in PAIRS},
       "decuplet_internal": {f"{names[i+1]}-{names[i]}": round(vals[i+1]-vals[i], 4)
                             for i in range(len(names)-1)},
       "vp_splits": {vn: round(d, 4) for vn, d in zip([p[0] for p in VP_PAIRS_CLEAN], splits)},
       "monotone": mono,
       "P3A_hits": hits, "P3B_sign": dec_pos,
       "verdict": "closed-if-P3A" if (hits == 3 and dec_pos) else "honest-negative-or-partial"}
with open("data/42_spin_sector_out_of_sample.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("  data/42_spin_sector_out_of_sample.json 寫入完成")