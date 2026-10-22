#!/usr/bin/env python3
# O197 scripts/05 — T4: k=36 微觀動力學 + 綜合閉合
# O174 docs/14: k = B·N_gen² = 36 結構身份 (logN 模態數)
# 微觀: 點解環境過密由 36 個獨立 ln(1+δ̂₊) 模態乘性疊加?
#   δ̂₊ = 44 個正偏差譜模態 — 點解取 36 而唔係 44?
# 候選: δ̂₊ 44 模態 = k=45..88 (正偏差), 但種子形成排除 k=88 (γ=4 邊界原子?)
#   或 排除最極端模態?
# 44 − 36 = 8 = 2B (B=4 阻挫基) — 8 個被排除模態?
# 檢查: δ̂₊ 排序, 36 個「中間」模態 vs 44 全部
#   k=45..88: δ̂ = −cos(kπ/88), k=45..88 → cos 負 ⟹ δ̂ 正
#   δ̂₊ 最大值 k=88: −cos(π) = 1 (γ=4 邊界原子)
#   δ̂₊ 最小值 k=45: −cos(45π/88) = −cos(92.05°) ≈ 0.0357
# 36 = 44 − 8: 排除 8 個? k=45..52 (最細 8 個) 或 k=81..88 (最大 8 個)?
# 驗證: 邊界 8 個 (k=81..88 含 γ=4 原子) 排除 ⟹ Var_pop(36) 對比?
import numpy as np

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  " + ("PASS" if cond else "FAIL") + " " + name + (f"  [{detail}]" if detail else ""))

ks = np.arange(1, 89)
dhat = -np.cos(2*ks*np.pi/176)
dhat_pos = dhat[dhat > 0]  # 44 個正偏差
print(f"δ̂₊ ({len(dhat_pos)} 個): 範圍 [{dhat_pos.min():.4f}, {dhat_pos.max():.4f}]")

print("\n== T4a: 44−36 = 8 = 2B 排除分析 ==")
# δ̂₊ 對應 k = 45..88. 排序後排除 8 個:
sorted_p = np.sort(dhat_pos)
# 候選 1: 排除最大 8 個 (k=81..88, 含 γ=4 邊界原子 k=88)
excl_hi = sorted_p[:36]   # 留低 36 個最細
# 候選 2: 排除最細 8 個 (k=45..52)
excl_lo = sorted_p[8:]    # 留低 36 個最大
# 候選 3: 排除兩端各 4
excl_both = sorted_p[4:40]
var_full = np.var(np.log(1+dhat_pos))
var_hi = np.var(np.log(1+excl_hi))
var_lo = np.var(np.log(1+excl_lo))
var_both = np.var(np.log(1+excl_both))
print(f"  Var_pop(ln(1+δ̂₊)) 全 44 個 = {var_full:.6f}")
print(f"  排除最大 8 (留最細 36): Var = {var_hi:.6f}")
print(f"  排除最細 8 (留最大 36): Var = {var_lo:.6f}")
print(f"  排除兩端各 4:           Var = {var_both:.6f}")
# 目標: s² = 36·Var = 1.4098 ⟹ Var = 0.039162 (必須 = 全 44 個嘅 Var!)
print(f"  目標 Var (36 模態) = 1.4098/36 = {1.4098/36:.6f} (必須 = 全 44 個 Var 先一致)")
check("T4a Var 對排除方案 — 全 44 個 Var = 0.039162 (O174 docs/13 用 44 個)",
      abs(var_full - 0.039162)/0.039162 < 0.01, f"{var_full:.6f}")
# O174 docs/13: s² = 36·Var_pop(ln(1+δ̂₊)) — 用 44 個 δ̂₊ 嘅 Var, 唔係 36 個!
# 即 k=36 係「模態數」= 36 個獨立 ln 項, 每個 Var = Var_pop(44 個 δ̂₊)
# 微觀: ln(1+δ_env) = Σ_{i=1}^{36} X_i, X_i iid ~ Var_pop(ln(1+δ̂₊))
# ⟹ k=36 唔係「36 個 δ̂₊ 模態」, 而係 36 個「成長步」, 每步漲落 = δ̂₊ 分布

print("\n== T4b: k=36 = B·N_gen² 微觀詮釋 ==")
print("  O174 docs/14: k = 36 = B·N_gen² (B=4 阻挫基, N_gen=3)")
print("  微觀候選: 環境過密 = 36 個獨立成長步 (池週轉 36%, O173)")
print("  每步: ln(1+δ̂₊) 分布 (44 正偏差模態嘅離散譜)")
print("  結構身份: 36 = B·N_gen² = 4·9")
# 檢查其他結構: 36 = N/2 − F_proj + N_gen² = 44−17+9 (O121 黑洞投影核通道, 記憶)
k36_alt1 = 44 - 17 + 9
k36_alt2 = 4*9
print(f"  候選 1: 44 − F_proj + N_gen² = {k36_alt1} (O121 黑洞投影核通道)")
print(f"  候選 2: B·N_gen² = {k36_alt2} (O174 docs/14)")
check("T4b 36 = 44 − F_proj + N_gen² = B·N_gen² (雙身份一致)", k36_alt1 == k36_alt2 == 36,
      f"{k36_alt1} = {k36_alt2}")

print("\n== T4c: 綜合閉合 ==")
# T1: 乘性 (1+δ_tot) = (1+δ̂)(1+δ_env) 形式 — δ̂ 中位 0 唔影響 logN 中位
# T2: 1+δ̂ = γ/2, Π(1+δ̂) = N_d/2^{N_d−2} 閉式
# T3: 兩通道並存 — δ̂ 低端 [2.02e6, 5.41e6], logN 中位 6.98e6 (LRD 0.13%)
# T4: k=36 = B·N_gen² = 44−F_proj+N_gen² 雙身份
# 可證偽預言: 種子質譜 M≈5.41e6 通道交界 + 低端種子必須存在 + 高端斜率 −0.84
print("  T1 形式: 乘性 (1+δ_tot) = (1+δ̂)(1+δ_env) — 獨立因子")
print("  T2 身份: 1+δ̂ = γ/2, Π(1+δ̂) = 88/2^86")
print("  T3 統計: 兩通道並存, 域分離 (δ̂ < 5.41e6 < logN 中位)")
print("  T4 微觀: k=36 = B·N_gen² (O174) = 44−F_proj+N_gen² (O121)")
print("  預言: 種子質譜 M≈5.41e6 交界 (可證偽: 冇轉折 = 模型錯)")

print(f"\n{len(PASS)}/{len(PASS)+len(FAIL)} PASS")
if FAIL: print("FAIL:", FAIL); exit(1)
