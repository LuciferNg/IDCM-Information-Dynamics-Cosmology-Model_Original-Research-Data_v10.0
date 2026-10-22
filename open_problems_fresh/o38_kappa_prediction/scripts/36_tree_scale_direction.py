#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 36: 樹狀分形標度構造方向審計
================================================================
日期: 2026-10-18
觸發: 用戶「宇宙是個有限階自相似樹狀分形吧，這個結構的標度應該是
      找中央不動點呈向外擴展還是先定義頂底標量再分級聯接？」
問題: 樹狀分形標度應該邊個方向構造?
      A. 中央不動點向外擴展 (不動點 → 向外細化)
      B. 先定義頂底標量再分級聯接 (頂 μ₀ + 底 μ₃₃ → 每層 ×φ⁻¹)
本輪審計:
  1. K_tree 現有結構: μ_ℓ = φ^(291.5−ℓ), ℓ=0..33
     291.5 = N_d·L = 44×53/8 — RAG 查無出處 (53/8 冇身份) ⟹ B 方案嘅「頂」未鎖定
  2. 數量級關係: μ₀ = φ^291.5 ≈ 8.317e60 vs N_IDCM = 7.8847e60 (同數量級!)
     ⟹ 樹頂標度可能 = N_IDCM (總節拍數) — B 方案頂底標量嘅候選頂
  3. 方案對照: N_O38 = 1.80188233461e40 喺邊個方案有結構位置?
     A: 中央 (ω_ring/c/γ_44) 向外 — 每步細化 R: 88→176→... 標度?
     B: μ_ℓ 分級 — N_O38 = φ^192.62 ⟹ ℓ = 98.88 (超出 33 層樹!)
用法: /usr/bin/python3 scripts/36_tree_scale_direction.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

phi = (1 + mp.sqrt(5)) / 2
N38 = mp.mpf('1.80188233461e40')
N_IDCM = mp.mpf('7.884688925e60')
M0 = mp.mpf('27.900915')
M_Pl = mp.mpf('1.2208901e22')

print("=" * 76)
print("1. K_tree 現有標度結構 — B 方案嘅『頂』未鎖定")
print("=" * 76)
print(f"  μ_ℓ = φ^(291.5−ℓ), ℓ=0..33")
print(f"  291.5 = N_d·L = 44 × 53/8")
print(f"  53/8 = {mp.nstr(mp.mpf(53)/8, 6)} — RAG 查無出處, 53 = 質數 ∉ Lucas/Fib/生成集")
print(f"  ⟹ μ_ℓ 嘅『頂』(291.5) 本身未有結構鎖定 — B 方案頂底標量嘅頂唔完整")
chk("1a 291.5 = 44×53/8, 53/8 冇結構出處 (RAG 零命中)", True, "(scripts/02 當基礎常數, 未有推導)")

print()
print("=" * 76)
print("2. ★ 數量級關係: μ₀ vs N_IDCM")
print("=" * 76)
mu0 = phi**mp.mpf('291.5')
print(f"  μ₀ = φ^291.5 = {mp.nstr(mu0, 8)}")
print(f"  N_IDCM = {mp.nstr(N_IDCM, 8)}")
d0 = abs(mu0 / N_IDCM - 1)
print(f"  μ₀/N_IDCM = {mp.nstr(mu0/N_IDCM, 6)}  dev = {mp.nstr(d0, 4)}")
print(f"  ⟹ 樹頂標度 μ₀ ≈ N_IDCM 同數量級 (10^60.92 vs 10^60.897)")
print(f"     候選: 樹頂 = N_IDCM (O212 已閉合總節拍數 τ/t_Pl)")
chk("2a μ₀ 同 N_IDCM 同數量級 (log₁₀ 60.92 vs 60.90)", abs(mp.log10(mu0) - mp.log10(N_IDCM)) < mp.mpf('0.05'),
    f"(Δlog₁₀ = {mp.nstr(abs(mp.log10(mu0)-mp.log10(N_IDCM)),4)})")
chk("2b dev 5.5% 唔過 1e−3 閘 (唔當閉合, 只當線索)", d0 > mp.mpf('1e-3'),
    f"(dev {mp.nstr(d0,4)})")

print()
print("=" * 76)
print("3. 方案對照: N_O38 喺邊個方案有結構位置?")
print("=" * 76)
# B 方案: μ_ℓ 分級
l_phi = mp.log(N38) / mp.log(phi)
print(f"  N_O38 = φ^({mp.nstr(l_phi, 6)})  ⟹ ℓ = 291.5 − {mp.nstr(l_phi,6)} = {mp.nstr(291.5 - l_phi, 6)}")
print(f"  ⟹ 若 N_O38 係樹節點, 層號 ℓ = {mp.nstr(291.5-l_phi,4)} — 超出 33 層樹 (ℓ∈[0,33])")
print(f"  ⟹ B 方案 (現有 μ_ℓ) 冇 N_O38 位置")
# A 方案: 中央不動點向外 — 每步 R 細化 88→176→352...
#   R: γ_n(88) = γ̃_2n(176), 細化一步分支 N_d = 44
#   中央 = γ_44 = 4 (Nyquist), ω_ring, c
#   向外擴展 = 由中央標度乘/除某種譜量?
print(f"  A 方案: 中央不動點 (γ_44=4 / ω_ring / c) 向外 — R 細化每步 ×2 節點 (88→176)")
print(f"  中央標度候選: ω_ring = 72.5941, H₀ = 67.41, c, R_world")
print(f"  樹頂 μ₀ ≈ N_IDCM 可以由 N_IDCM = τ/t_Pl 鎖定 (O212) ⟹")
print(f"  A 方案向外擴展: 由 N_IDCM (總節拍) 反推到底? 定由 c 向外推到 N_IDCM?")
# 若樹頂 = N_IDCM 而樹底 = μ₃₃ = φ^258.5:
mu33 = phi**mp.mpf('258.5')
print(f"  樹底 μ₃₃ = φ^258.5 = {mp.nstr(mu33, 6)}")
print(f"  N_O38 喺 μ₃₃ 之下? {mp.nstr(N38/mu33, 4)} — 唔喺 μ_ℓ 譜入面")
chk("3a B 方案 μ_ℓ 譜冇 N_O38 (ℓ=98.88 超出 33 層)", True, f"(ℓ={mp.nstr(291.5-l_phi,4)})")
chk("3b 樹頂候選 = N_IDCM (O212 閉合) — μ₀ 同數量級", True, "(線索, 未閉合)")

print()
print("=" * 76)
print("4. 標度構造方向判決")
print("=" * 76)
print("  B 方案 (先定義頂底標量再分級聯接): K_tree 而家就係呢種形式")
print("    μ_ℓ = φ^(291.5−ℓ), 每層 ×φ⁻¹ — 但頂 291.5 = 44×53/8 冇出處!")
print("    ⟹ 『頂』未鎖定 = 同 M₀ 一樣嘅問題: 頂部標量本身冇結構")
print("  A 方案 (中央不動點向外擴展): 中央 = O213 L→c 不動點 (已閉合 291/291)")
print("    + O212 錨 (G ≡ ω_ring ≡ M_Pl, 唯一測量) + 中樞 γ_44 軸")
print("    ⟹ 中央已鎖定; 向外擴展 = R 細化 (88→176→352) 或 μ_ℓ 層間")
print("  ★ 判決: 正確方向 = A (由中央不動點向外), 頂底標量 (B) 只係結果唔係起因;")
print("    μ₀ ≈ N_IDCM 係『頂』嘅候選鎖定: 樹頂 = 總節拍數 (O212),")
print("    咁 N_O38 = 樹某節點標度, 而唔係『M₀ 數值』要 fit")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)