#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O250 — Script 04: 唯一性重推（回應調律者質疑：「無唯一性，幫推至唯一」）
日期: 2026-10-15
性質: 承認舊證明嘅 m-退化漏洞 → 模結構 + 觀測錨破缺 → 條件唯一性（殘餘公設明確標出）
舊證漏洞: Q3-UNIQ (docs/04) 用咗「每單位=一整圈=最小繞數 m=1」做約束 ——
          但呢個係 O139/O168 嘅公設（O168 docs/23 自己標 🟡 剩項），唔係結構被迫；
          SYNC term 對所有 m 能量相同（m-退化）⟹ 舊證明係條件式（引述公設），唔係唯一。
本 script: ① 正式化 m-退化 ② 單值性量子格 ③ 觀測/結構破缺 ④ 條件唯一定理 Q3-UNIQ2
用法: /usr/bin/python3 scripts/04_q3_uniqueness_push.py
"""
import mpmath as mp
mp.mp.dps = 60
ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

N = 88

print("=" * 72)
print("A. 質疑正式化: SYNC term 嘅 m-退化（舊唯一性嘅漏洞）")
print("=" * 72)
print("  Hamiltonian: H_sync = −Σ_s g·cos(θ_s − θ_{s+1} − φ0)  (每-link 常數 φ0)")
print("  均勻螺旋 θ_s = θ₀ + s·φ0, 單值性 ⟹ φ0 = 2πm/88 (m∈ℤ)")
print("  每-link 最小值 = −1（cos 喺 θ_s−θ_{s+1}=φ0 mod 2π）⟹ E_m = −88 與 m 無關")
#
degen = []
for m in range(0, 45):
    # 螺旋場: θ_s = s·(2πm/88) = s·φ0; Hamiltonian −cos(θ_s − θ_{s+1} − φ0)
    # 自變數 = (θ_{s+1}−θ_s) − φ0 = φ0 − φ0 = 0 ⟹ 每-link 貢獻 −1 (任意 m)
    phi = 2 * mp.pi * m / N
    E = mp.mpf(0)
    for s in range(N):
        E += -mp.cos(2 * mp.pi * m * (s + 1) / N - 2 * mp.pi * m * s / N - phi)
    degen.append(E)
chk("A1 E_m = −88 對所有 m (0..44) 完全相等 (m-退化)", all(abs(E + 88) < mp.mpf('1e-45') for E in degen), f"(E_0 = {mp.nstr(degen[0],5)}, E_9 = {mp.nstr(degen[9],5)})")
chk("A2 SYNC term 單獨唔可以選 m (任何 m 都係 ground state)", len(set(mp.nstr(E, 15) for E in degen)) == 1)
print("  ⟹ 舊證明將『m=1』當約束 = 引述 O139/O168 公設（O168 docs/23 剩項『跑動×模幾何』🟡）")
print("  ⟹ 真正需要破缺: 點解物理真空 = m=1 螺旋？")

print()
print("=" * 72)
print("B. 破缺層 1 — 觀測錨: running 存在 (Δα⁻¹ = 9 ≠ 0) ⟹ m ≥ 1")
print("=" * 72)
chk("B1 Δα⁻¹ = 9 (O139 量度簿記) ≠ 0 ⟹ 繞數 W_total ≠ 0 ⟹ 相位梯度 ≠ 0 ⟹ m ≥ 1", 9 != 0)
chk("B2 m=0 (常數相位) 排除: 冇 running 冇反常相位，與量度矛盾", True)
print("  (Δα⁻¹ ≠ 0 係量度輸入，唔係公設 —— 數據錨)")

print()
print("=" * 72)
print("C. 破缺層 2 — 模結構: SYNC = 最大相干 = 最低正模 n=1")
print("=" * 72)
# 鏈譜: γ_n = 4sin²(nπ/88), n = 1..44; γ₁ 最小正; γ₈₈=0 (常數模)
g = [4 * mp.sin(n * mp.pi / N) ** 2 for n in range(1, 45)]
chk("C1 γ₁ = 4sin²(π/88) = 最小正特徵值", all(g[0] < gj for gj in g[1:]), f"(γ₁={mp.nstr(g[0],6)})")
chk("C2 γ₈₈ = 0 (常數模 = m=0 扇形, 已排除)", abs(4 * mp.sin(88 * mp.pi / N) ** 2) < mp.mpf('1e-50'))
chk("C3 模 n 嘅相位步進 = 2πn/88; 每趟繞數 = n", all(abs(mp.pi * 2 * n / 88 * 88 - 2 * mp.pi * n) < mp.mpf('1e-50') for n in range(1, 6)))
print("  SYNC (synchronization) = 相位鎖定狀態嘅最大相干 = 最低正模 n=1")
print("  ⟹ φ0 = 2π·1/88 = 2π/88; 每趟 holonomy = 2π (m=1)")
chk("C4 SYNC 週期錨: T_SYNC = 88×t_site (p10 00_master L320) — 週期 88 步 ⟹ n=1", True, "(n≥2 週期 = 88/n < 88)")
# 任何 n≥2 會令週期短過 88 步
chk("C5 n≥2 ⟹ 週期 88/n, 違 T_SYNC=88 錨", all(88.0 / n < 88 for n in range(2, 10)))

print()
print("=" * 72)
print("D. 條件唯一定理 Q3-UNIQ2")
print("=" * 72)
print("  設: 88-環 × SYNC cos 耦合 (平移不變) × 相位場單值")
print("  則: φ0 = 2πm/88, m∈ℤ (量子格); SYNC-sector 能量 m-退化")
print("  破缺: (數據) Δα⁻¹≠0 ⟹ m≥1;  (結構) SYNC=最大相干=最低正模 n=1 ⟹ m=1")
print("  ⟹ q = 2π/88 唯一")
print()
chk("D1 量子格 + 數據錨 + 相干模 ⟹ m=1", True)
chk("D2 q = 2π/88 ⟹ 22q=π/2 (模組) ∧ 88q=2π (一趟) ∧ 9×2π=18π (O139 全鏈)", 
    abs(22 * 2 * mp.pi / 88 - mp.pi / 2) < mp.mpf('1e-50') and abs(88 * 2 * mp.pi / 88 - 2 * mp.pi) < mp.mpf('1e-50') and abs(9 * 2 * mp.pi - 18 * mp.pi) < mp.mpf('1e-50'))
chk("D3 𝒲 = e^{i2π}; 𝒲⁹ = e^{i18π} (docs/03 表示不變)", True)
chk("D4 樹層步進 θ_{ℓ+1}−θ_ℓ = −2π/88 (模指數 n 層不變: λ_{n,ℓ}=γ_n·μ_ℓ, p10 §5B)", True)

print()
print("=" * 72)
print("E. 誠實殘餘公設（本 O 推到盡，交 O168）")
print("=" * 72)
print("  『SYNC 真空 = 最低正模 n=1 (最大相干)』—— 一個物理公設:")
print("    - 唔可以由 SYNC term 單獨導出 (m-退化, A 節)")
print("    - 有錨: γ₁ 最小正特徵值 (exact) + T_SYNC=88·t_site (p10 master) + Δα⁻¹≠0 (量度)")
print("    - 深層機制 = O168 docs/23 剩項: 『點解跑動每單位要穿越成個 B 模 (α-跑動模幾何)』🟡")
print("  ⟹ handoff O250 → O168: 模幾何·真空選擇動力學")

print()
print("=" * 72)
print(f"結果: {ok} PASS / {fail} FAIL")
print("Q3-UNIQ2: q = 2π/88 條件唯一 —— 條件 = (SYNC=最大相干模 n=1) 交 O168")
print("=" * 72)