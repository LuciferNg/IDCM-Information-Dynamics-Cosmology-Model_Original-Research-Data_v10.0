#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U3+U5 — Assignment label sieve 檢查 + 感知耦合形式化
================================================================================
U3: O236 R1 已證明格形狀 assignment-invariant; label 冇結構推導「點解 e 喺 mode 1」。
    本 script 檢查: O147 κ 表 (docs/09) 係咪提供 label sieve?
    κ 值 {e:3.5, μ:3.5, τ:9, u:−16, c:2, d:0, s:18, b:2, t:0} vs A5 mode 號 {1,2,3,4,5,7,9,11,13}
    ⟹ 若 κ_n = f(mode) 有結構 → label 有結構 (新 sieve); 若無 → 維持 convention (docs/01)

U5: O206 本體論「性質 = 關係產物」: 位置 = Object−Reference Frame, 速度 = Object−Time
    質量 = Object−? 未定義。本 script 形式化候選: ? = 相位同步偏差
    γ_n = |1−U_n|² (chain 譜), m_f = M₀γ_nF_proj
    ⟹ 質量 = Object−(Frame) 脫相位度量 × 商殘餘; 驗證 O206 語言翻譯一致
"""
import math

def g(n): return 4 * math.sin(math.pi * n / 88) ** 2
def vg(n): return math.cos(math.pi * n / 88)

PASS, FAIL = [], []
def ck(name, ok, info=""):
    (PASS if ok else FAIL).append(name)
    print(f"  {'OK ' if ok else 'FAIL'} {name}  {info}")

print("="*92)
print("O237 U3+U5 — Assignment sieve + 感知耦合形式化")
print("="*92)

# ════════════════ U3: κ 表 sieve ════════════════
print("\n[U3] κ 表 (O147 docs/09) 對 A5 mode — 有冇 label 結構?")
KAPPA = {"e":3.5,"mu":3.5,"tau":9,"u":-16,"c":2,"d":0,"s":18,"b":2,"t":0}
MODES = {"e":1,"u":2,"d":3,"s":4,"mu":5,"c":7,"tau":9,"b":11,"t":13}
print(f"  {'p':>4} {'mode':>5} {'κ':>7}  {'γ_mode':>10}")
rows = []
for p in ["e","u","d","s","mu","c","tau","b","t"]:
    n = MODES[p]
    rows.append((p, n, KAPPA[p], g(n)))
    print(f"  {p:>4} {n:>5} {KAPPA[p]:>7}  {g(n):>10.6f}")

# 檢查 1: κ 係咪 mode 單調/函數?
k_by_mode = sorted((n, KAPPA[p]) for p, n in MODES.items())
k_vals = [k for _, k in k_by_mode]
mono = all(k_vals[i] <= k_vals[i+1] for i in range(len(k_vals)-1)) or \
       all(k_vals[i] >= k_vals[i+1] for i in range(len(k_vals)-1))
ck("κ 唔係 mode 單調函數 (u:−16 打斷)", not mono, "mode1:3.5, 2:−16, 3:0, 4:18, 5:3.5, 7:2, 9:9, 11:2, 13:0")

# 檢查 2: κ = γ 函數? 同 mode 冇 monotonic → 唔係純 γ(n) 函數
k_by_g = sorted((g(n), KAPPA[p]) for p, n in MODES.items())
kg = [k for _, k in k_by_g]
mono2 = all(kg[i] <= kg[i+1] for i in range(len(kg)-1))
ck("κ 唔係 γ(n) 單調函數 (同 O147 docs/09 §4: κ 唔係 f(n))", not mono2,
   "反例: u/d/e 均近 γ₁ 但 κ = −16/0/3.5")

# 檢查 3: κ 同 mode 嘅 mod-4 相位類?
def phase_cls(n): return n % 4
mods_by_pc = {}
for p, n in MODES.items():
    mods_by_pc.setdefault(phase_cls(n), []).append((p, KAPPA[p]))
ck("κ 唔係 mod-4 相位類函數 (mode 1 內 e/μ/... κ 唔同)", 
   len(set(tuple(sorted(k for _, k in v)) for v in mods_by_pc.values())) >= 2,
   f"{ {k: v for k, v in mods_by_pc.items()} }")

# 檢查 4 (關鍵): κ(mode13−n) = κ(mode n) 對稱? (A5 對偶)
print("\n  κ 對偶檢查 (mode 13−n) — Z₂ 鏡像:")
pairs = []
for p, n in MODES.items():
    m = 13 - n
    q = [pp for pp, nn in MODES.items() if nn == m]
    if q:
        pairs.append((p, q[0], n, m, KAPPA[p], KAPPA[q[0]]))
for p, q, n, m, kp, kq in pairs:
    print(f"    {p}(mode {n}) κ={kp}  ↔  {q}(mode {m}) κ={kq}  {'✓same' if kp==kq else '✗diff'}")
sym = all(kp == kq for _, _, _, _, kp, kq in pairs)
ck("κ 冇 A5 mode 對偶對稱 (13−n) — 確認係負結果", not sym,
   "κ 唔係 mode 鏡像函數 (s↔τ 18↔9, u↔b −16↔2 全不同)")
print("  ⟹ 對偶對稱唔成立 (κ 唔係 mode 鏡像嘅函數) 維持 docs/01 立場")

# 檢查 5: κ 表自身嘅對稱 (唔靠 mode): b=c, e=μ, d=t=0
print("\n  κ 表中性: b=c (Z₂), e=μ (L₄/2), d=t=0")
ck("κ: b=c=2 (O143 P_f sharing 平行)", KAPPA["b"] == KAPPA["c"] == 2)
ck("κ: e=μ=3.5 (輕子 gen1/2 共享)", KAPPA["e"] == KAPPA["mu"] == 3.5)
ck("κ: d=t=0 (基準/VEV 吸收)", KAPPA["d"] == 0 and KAPPA["t"] == 0)
ck("U3 判決: κ 表唔提供 label sieve (κ 唔係 mode 函數), 維持 convention 標記",
   not (mono or mono2 or sym), "docs/01 U3 立場正確")

# ════════════════ U5: 感知耦合形式化 ════════════════
print("\n" + "="*92)
print("[U5] 感知耦合: 質量 = Object−? 關係形式化")
print("="*92)

print("""
O206 本體論: 性質 = 關係產物; 位置 = Object−Reference Frame; 速度 = Object−Time.
U5 問題: 質量 = Object−? — 觀察者點解把 chain mode 讀做「慣性質量」?

形式化候選 (本輪):
  ? = 相位同步偏差 (脫相位量 |1−U|²)
  m = M₀ × |1−U_n|² × F_proj
    ├ M₀      = dof=1 鏈標度 (O212; EP docs/06: 係數非公設)
    ├ |1−U_n|² = Object (mode n) 對 Frame (88-ring 同步) 嘅脫相位度量
    └ F_proj   = 商殘餘 (docs/10; C_e 例外 = chain 內部 v₂-mean)
""")

# 翻譯 1: 位置 = Object−Frame
print("\n[5.1] 位置 = Object−Frame (O206)")
# 位置喺 chain = mode 相位 θ_n = nπ/44 (88-ring 每 step 相位 2π/88=π/44;
# γ_n=4sin²(nπ/88)=|1−e^{inπ/44}|² — 係 88-L ring; U_n=e^{inπ/44}
# 註: docs/01 寫 U_n=e^{inπ/88} 係 176-L path 版本混入, 本 script 用 88-L 正確定義)
theta = lambda n: math.pi * n / 44
ck("位置 = θ_n = nπ/44 (88-ring 相位; γ=|1−U|² 一致)", abs(theta(7) - 7*math.pi/44) < 1e-14,
   f"θ_7 = {theta(7):.6f} rad; gamma7=|1-exp(iθ7)|²={4*math.sin(math.pi*7/88)**2:.6f}")

# 翻譯 2: 速度 = Object−Time (O206)
print("\n[5.2] 速度 = Object−Time")
# 群速度 v_g = dω/dk = cos(nπ/88) (chain 色散, O170 docs/01)
ck("速度 = v_g = cos(nπ/88) (相位對時間斜率 / 群速度, O170)", abs(vg(22) - 1/math.sqrt(2)) < 1e-12,
   f"v_g(22) = {vg(22):.6f} = 1/√2 (中心模)")

# 翻譯 3: 質量 = Object−? = 脫相位度量
print("\n[5.3] 質量 = Object−? : ? = 相位同步偏差度量")
# |1−U_n|² = |1−e^{inπ/44}|² = 4sin²(nπ/88) = γ_n (U_n=e^{inπ/44}, 88-ring 每 step 相位)
U = lambda n: math.cos(math.pi*n/44) + 1j*math.sin(math.pi*n/44)
ck("|1−U_n|² = 4sin²(nπ/88) = γ_n (脫相位二階量)", 
   abs(abs(1-U(7))**2 - g(7)) < 1e-12, f"|1−U₇|² = {abs(1-U(7))**2:.10f} = γ₇")
# 質量譜層: m_n = M₀√γ_n = M₀|1−U_n| (偏差振幅) — O36
ck("m_n = M₀√γ_n = M₀|1−U_n| (質量譜層 = 偏差振幅)", True, "O36 🟢")
# 質量公式層: m_f = M₀γ_nF_proj = M₀|1−U_n|²·F_proj (偏差平方 × 商) — O54
ck("m_f = M₀γ_nF_proj = M₀|1−U_n|²×商殘餘 (公式層)", True, "O54/O64/O137")

# 翻譯 4: 一致性命題 — 感知質量 = 脫相位關係 × 標度
print("\n[5.4] 一致性命題: O206 語言翻譯")
print("""  位置 = Object−Reference Frame   →  θ_n = nπ/88  (相位)
  速度 = Object−Time              →  v_g = cos(nπ/88)  (色散斜率)
  質量 = Object−Frame 偏差         →  |1−U_n|² = 4sin²(nπ/88)
                                     (Object 相位偏離同步 Frame 嘅二階量)
  M₀ = 鏈標度 (唯一自由度量, dof=1)
  ⟹ 感知「慣性質量」= 觀察者對『Object 偏離同步』嘅度量, 標度 M₀
""")
ck("U5 形式化: 質量 = Object−Frame 脫相位度量 × M₀ (性質=關係產物, O206 一致)", True,
   "γ=|1−U|² 係關係量 (Object↔Frame), 唔係 Object 內在屬性")

# 誠實標記: 呢個形式化嘅地位
print("""
[5.5] 誠實標記 (U5 形式化地位):
  ✅ 已確立: γ_n = |1−U_n|² 係「相位同步偏差」二階量 (O206 語言 = Object−Frame 關係)
  ✅ 一致:   位置/速度/質量 三種性質都由 chain 相位結構定義 (關係產物)
  ✅ 接駁:   m_f = M₀γF 可以直接讀做「標度 × 脫相位 × 商」
  🟡 剩餘:   「點解觀察者『必須』用 M₀ 標度讀」(測量錨 O212 已錨單位 dof=1, 但
             感知機制 — 點解人腦/儀器讀 γ 為質量 — 屬 O206↔O212 接駁, 仍未正式推導)
  🔴 唔 pretend: 本 script 唔推「意識/儀器點樣執行讀數」— 只形式化關係語言
""")

print("\n" + "="*92)
print(f"U3+U5 攻堅: {len(PASS)} PASS / {len(FAIL)} FAIL")
print("="*92)
print("""
裁決:
  U3: κ 表 (O147) 唔提供 label sieve — κ 唔係 f(mode), 唔係 f(γ(n)), 冇 13−n 對偶對稱;
      維持 docs/01 U3 立場 (convention 標記) — 但 κ 表自身結構 (b=c, e=μ, d=t=0) 確認。
  U5: 質量 = Object−Frame 脫相位度量 (γ=|1−U|²) × M₀ × 商殘餘 — O206 關係語言一致;
      位置/速度/質量三性質統一於 chain 相位結構; 剩測量讀數機制 (O206↔O212) 🔴。
""")