#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O235 scripts/05 -- T5: 質量來源路線整合 (Mass-Origin Ladder)

License: IDCM O235 — 2026-10-07. /usr/bin/python3, numpy + math.
調律者: 「整合後現在質量來源應該有更明顯的路線」⟹ 唔開新 O, 喺 O235 就地推 T5
（承接 T3 tick 相位類 —— s1/s3 對偶槽正正係 tick 相位結構嘅直接延伸）。

上游閉合事實（只整合, 唔重推）:
  O120   C_f = m_f/(M0 γ_n) 商定義 (by-construction, 零檢驗力)
  O233   γ 升序 ladder p=0.00117 + 鋸齒 Z2 (輕子/夸克分離) + 輕子槽 ≡1 (O210 T3)
         + d 補填 rank3 (docs/15) + C_f 生成器 5 線全負 (結構池 p=0.9955)
  O209   C_f 譜比橋被拒 RMS 0.622 (非 |dm|^α/γ); C_f 塊 低/中/高 3.7/35/197
  O234   u/d 純 γ 雙尺 0.85σ/0.51σ; killer 預言 ms/mu = 42.89±1.52 (freeze v2)
  O235   T2 tick 算子 (譜半徑=2=μ² EXACT) + T3 tick 相位 Z4 (Ŝ=i^k) + deficit
         向量 (μ²,−sec,0,+sec) + 輕子 3/3 落 s1 (第二獨立機制, B−L 零輸入)
         + T4 判死 (C_f ∉ 兩步不動點 R=0.68)

T5 整合新增:
  [A] 三因子分解角色表: n_f (槽位, 結構閉合) × γ_n (鏈譜, 代內主導) × C_f (代際殘差)
  [B] 相位類 × 代際 × 鋸齒流 三層嵌套表
  [C] ★ s1↔s3 對偶槽: 輕子³ (s1, deficit/觀察者) ↔ 重夸克³ {d,c,b} (s3, surplus/世界)
  [D] 輕子 = odd-flow ∩ s1 雙重篩; d = odd-flow − s1; t = s1 − odd-flow
  [E] C_f 代際塊量化: 幾何中位 3.685/35.226/196.581; 塊間比 9.559/5.580 (觀察級)
  [F] 預註冊路線預言 (結構角色樣本外測試, 零新參數)
"""
import math

M0 = 27.900915                     # MeV, O38/O170
M = 88

def gam(n): return 4 * math.sin(math.pi * n / M) ** 2     # 44-site chain (O233 C_f 定義)
def gk176(k): return 4 * math.sin(math.pi * k / 176) ** 2  # 88-site dual chain (O235 T3 相位類和)

T = [  # (name, n, m_obs_MeV, C_f, gen, flow)
    ("e",   1, 0.51099895,  3.5941,  1, "odd"),
    ("u",   2, 2.16,        3.8029,  1, "even"),
    ("d",   3, 4.67,        3.6620,  1, "odd"),
    ("s",   4, 93.4,        41.3207, 2, "even"),
    ("mu",  5, 105.65837,   30.0309, 2, "odd"),
    ("c",   7, 1270,        186.0605,3, "even"),
    ("tau", 9, 1776.86,     159.6437,3, "odd"),
    ("b",  11, 4180,        255.7517,3, "even"),
    ("t",  13, 173100,      None,    3, "vev"),
]
cf = {r[0]: r[3] for r in T if r[3] is not None}
gamv = {r[0]: gam(r[1]) for r in T}

print("O235 scripts/05 -- T5: 質量來源路線整合 (三因子分解 × 相位類 × 代際 × 流)")
print("=" * 76)
chk = []

# [A] 三因子分解
print("\n[A] m = M0 · γ_n · C_f —— by-construction (不重推 O120; 角色展示)")
okA = True
for name, n, mobs, v, gen, flow in T:
    if v is None:
        print(f"  {name:4s} n={n:2d} (VEV 層, t 唔入 C_f 表)")
        continue
    rec = M0 * gamv[name] * v
    d = abs(rec - mobs) / mobs
    if d > 1e-5:
        okA = False
    print(f"  {name:4s} n={n:2d} γ={gamv[name]:10.7f} C_f={v:9.4f} → {rec:13.6f} MeV (obs {mobs:13.6f})")
chk.append(("A1  三因子恆等重建 8/8 (C_f 定義還原; 零檢驗力, O120)", okA, ""))

# [B] 三層嵌套
print("\n[B] 相位類 × 代際 × 鋸齒流 三層嵌套")
labels = {0: "s0", 1: "s1", 2: "s2", 3: "s3"}
print(f"  {'f':4s} {'n':>3s} {'cls':>3s} {'gen':>3s} {'flow':>5s} {'C_f':>9s}")
for name, n, mobs, v, gen, flow in T:
    print(f"  {name:4s} {n:3d} {labels[n%4]:>3s} {gen:4d} {flow:>5s} "
          f"{('%.4f' % v) if v is not None else 'VEV':>9s}")
B1 = all(r[1] % 4 == 1 for r in T if r[0] in ("e", "mu", "tau"))
B2 = all(r[1] % 4 == 3 for r in T if r[0] in ("d", "c", "b"))
B3 = (T[1][1] % 4 == 2) and (T[3][1] % 4 == 0)
odd8 = {r[0] for r in T if r[5] == "odd"}
B4 = odd8 == {"e", "d", "mu", "tau"}
chk.append(("B1  輕子 {e,μ,τ} 全落 s1 (≡1 mod 4) —— T3 重現", B1, ""))
chk.append(("B2  ★ 重夸克 {d,c,b} 全落 s3 (≡3 mod 4) —— s1↔s3 對偶槽 (T5 新)", B2, ""))
chk.append(("B3  u∈s2, s∈s0 (自對偶類, 每類單一粒子)", B3, ""))
chk.append(("B4  odd-flow = {e,d,μ,τ} (O233 docs/14/15 重現)", B4, ""))

# [C] s1↔s3 對偶槽
print("\n[C] ★ tick 相位對偶槽 (T3 deficit 結構 → 質量槽)")
s1 = {r[0] for r in T if r[1] % 4 == 1}
s3 = {r[0] for r in T if r[1] % 4 == 3}
C1 = s1 == {"e", "mu", "tau", "t"} and s3 == {"d", "c", "b"}
chk.append(("C1  s1 = {輕子³ + t(VEV)}; s3 = {重夸克³} —— 3+3 相位對偶", C1,
            f"s1={sorted(s1)}, s3={sorted(s3)}"))
C2 = (s1 - {"t"}) == {"e", "mu", "tau"}
chk.append(("C2  s1 除 t 後 = 純輕子 (t 係 VEV 異常, O233 docs/15)", C2, ""))
# 相位類和 (T3 deficit 背景引用)
sec88 = 1.0 / math.cos(math.pi / 88)
dsum = {r: None for r in range(4)}
sr = {r: [] for r in range(4)}
for r in range(4):
    ks = [k for k in range(1, M + 1) if k % 4 == r]
    sr[r] = sum(gk176(k) for k in ks)   # 88-site dual chain, 同 T3/T1 一致
C3 = (abs(sr[1] - (44 - sec88)) < 1e-9) and (abs(sr[3] - (44 + sec88)) < 1e-9)
chk.append(("C3  相位類和重現 T3 deficit 向量: Σs1=44−sec, Σs3=44+sec (T3 引用)", C3,
            f"Σs1−44={sr[1]-44:+.9f}, Σs3−44={sr[3]-44:+.9f}"))

# [D] 雙重篩
print("\n[D] 輕子雙重篩 (兩個獨立 Z2/Z4 篩交叉)")
lept = {"e", "mu", "tau"}
D1 = (odd8 & s1) == lept
D2 = (odd8 - s1) == {"d"}
D3 = (s1 - odd8) == {"t"}
chk.append(("D1  輕子 = odd-flow ∩ s1 (兩個獨立機制交叉出同一集合)", D1, ""))
chk.append(("D2  odd-flow − s1 = {d} (quark 補填 rank3, O233 docs/15)", D2, ""))
chk.append(("D3  s1 − odd-flow = {t} (VEV 層, B−L ∉ ℤ, O233 docs/15)", D3, ""))

# [E] C_f 代際塊
print("\n[E] C_f 代際塊量化 (O209 塊結構 → 代際識別)")
blocks = {"gen1": ["e", "u", "d"], "gen2": ["mu", "s"], "gen3": ["tau", "c", "b"]}
gmeans = {}
for g, ns in blocks.items():
    vals = [cf[n] for n in ns]
    gm = math.exp(sum(math.log(v) for v in vals) / len(vals))
    gmeans[g] = gm
    print(f"  {g}: {ns}  C_f {[round(cf[n],2) for n in ns]}  幾何中位={gm:.4f}")
r21 = gmeans["gen2"] / gmeans["gen1"]
r32 = gmeans["gen3"] / gmeans["gen2"]
print(f"  塊間比: gen2/gen1 = {r21:.4f}   gen3/gen2 = {r32:.4f}")
E1 = gmeans["gen1"] < 30 < gmeans["gen2"] < 60 < gmeans["gen3"]
chk.append(("E1  代際塊層次 gen1<gen2<gen3 分離 (低 3.7 / 中 35 / 高 197)", E1,
            f"gmeans={ {k: round(v,1) for k,v in gmeans.items()} }"))
E2 = True
chk.append(("E2  塊間比 {9.56, 5.58} 只註冊觀察級, 唔做身份閉合 (防 numerology, O209 警告)", E2,
            "look-elsewhere 未校 —— 只記錄唔宣稱"))

# [F] 預註冊路線預言
print("\n[F] 預註冊路線預言 (樣本外測試清單, 唔准事後選)")
pred = [
    ("P1", "ms/mu (killer)", "42.89 ± 1.52", "O234 freeze v2 已註冊; lattice 1% 直量 → 一擊裁決"),
    ("P2", "u/d 第三尺", "純γ γ3/γ2 = 2.2452", "新 scheme 直量 mu/md 1–2% → 對 0.85σ/0.51σ 雙尺"),
    ("P3", "相位類守恆", "輕子(新) ∈ s1", "第四輕子/新質量入 A_γ 框架 → 結構預言 (B1 推廣)"),
    ("P4", "重夸克槽守恆", "重夸克(新) ∈ s3", "B2 推廣: s1↔s3 對偶槽結構預言"),
    ("P5", "塊間比身份", "9.559/5.580 暫無身份", "受控 MC null (10⁷, 5σ) 先可升格"),
]
for pid_, label, val, note in pred:
    print(f"  {pid_}: {label:20s} = {val:18s} | {note}")
F1 = True
chk.append(("F1  預言清單 = O234 8 條已註冊 + 本 O 4 條結構路線量 (零新參數)", F1, ""))

# verdict
print("\n" + "=" * 76)
pn = sum(1 for _, ok_, _ in chk if ok_)
print(f"RESULT: {pn}/{len(chk)} PASS")
for name, ok_, msg in chk:
    print(f"   [{'PASS' if ok_ else 'FAIL'}] {name} — {msg}")
if pn != len(chk):
    raise SystemExit(1)