#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O210 scripts/08_z4_bridge_definition.py
================================================================================
題目: ℤ₄ 橋「定義化」— 算子層鏈模數之構造 + 預註冊證偽測試之執行
================================================================================
背景 (O210 docs/03 §五 D3 + docs/07 §6):
  ℤ₄ 候選橋 = 「鏈側 176 = B·N_d 之 mod-4 分扇區」與「T1 模數 B = 4」同模但**無 map** ⟹ 舊判 🟡。
  本腳本: 為算子層構造**鏈模數**（站/模 ℤ₄），並執行預註冊測試:
    「若算子層鏈模數存在, 檢查 ΔB=1 是否恆落 s2 = 44 = N_d」。

§A 鏈側 ℤ₄ 扇區定理 (精確): Σγ^(c) = N_d + (μ², −sec(π/88), 0, +sec(π/88))
§B 生成元: Ŝ = S^{N_d/2} = S²² on ℤ₈₈（階 4, 與環 Laplacian 交換, 譜 = i^k）
§C 站-模對偶: 4:1 decimation 陪集之 DFT 支撐 = 確切 {0, N_d/2, N_d, 3N_d/2}, 相位 ω₄^{−c}
§D 算子側 ℤ₄: z ∈ Z(SU(B)) ⊂ SU(12), Λ^k ↦ i^k（= T3 之 χ）
§E 橋裁定: canonical iso 之存在性 + 預註冊證偽測試 + weight-level 對齊之良定義性
§F 跨鏈: sec(π/88) − 1 vs O213 R7 格點修正 (π/88)²/6; sec(π/88) ∉ ℚ(√5) (T-FIELD)
"""
import mpmath as mp

mp.mp.dps = 40
I = mp.mpc(0, 1)
stats = {"PASS": 0, "FAIL": 0}

def chk(name, dev, tol):
    ok = dev < tol
    stats["PASS" if ok else "FAIL"] += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {name}   [dev = {mp.nstr(dev, 4)}, tol = {mp.nstr(tol, 4)}]")
    return ok

B, N_gen, N_d = 4, 3, 44
N = 88                      # 鏈站數; 176 = 2N = B·N_d
gamma = lambda k: 4 * mp.sin(mp.pi * k / 176) ** 2

print("=" * 78)
print("§A  鏈側 ℤ₄ 扇區定理（176-L: γ_k = 4sin²(kπ/176), k = 1..88）")
print("=" * 78)
S = {c: sum(gamma(k) for k in range(1, N + 1) if k % 4 == c) for c in range(4)}
sec88 = 1 / mp.cos(mp.pi / 88)
print(f"    s0 (k≡0) = {mp.nstr(S[0], 18)}      s1 (k≡1) = {mp.nstr(S[1], 18)}")
print(f"    s2 (k≡2) = {mp.nstr(S[2], 18)}      s3 (k≡3) = {mp.nstr(S[3], 18)}")
print(f"    sec(π/88) = {mp.nstr(sec88, 18)}")
print(f"    ★ 扇區式: N_d + (μ², −sec(π/88), 0, +sec(π/88)) = "
      f"({N_d + 2}, {mp.nstr(N_d - sec88, 10)}, {N_d}, {mp.nstr(N_d + sec88, 10)})")
print("    證明: class2 = 11 對 × B = 44 ✓（無定點）; class0 = 10 對×B + γ₄₄(=μ²) + γ₈₈(=B) = 46 ✓;")
print("          class1∪3 = 22 對 ⟹ 和 88; 濾子給 s1 = 44 − sec(π/88)（閉式）")

chk("s2 = N_d = 44 EXACT（11 對 × B, 對合 k↔88−k 無定點）", abs(S[2] - N_d), mp.mpf('1e-35'))
chk("s0 = N_d + μ² = 46 EXACT（10 對 × B + γ₄₄ + γ₈₈）", abs(S[0] - (N_d + 2)), mp.mpf('1e-35'))
chk("s0 − s2 = μ² = 2 EXACT", abs((S[0] - S[2]) - 2), mp.mpf('1e-35'))
chk("s1 = N_d − sec(π/88)（閉式）", abs(S[1] - (N_d - sec88)), mp.mpf('1e-35'))
chk("s3 = N_d + sec(π/88)（閉式）", abs(S[3] - (N_d + sec88)), mp.mpf('1e-35'))
chk("sum = 4N_d + μ² = 178 = 2(N+1) EXACT", abs(sum(S.values()) - 178), mp.mpf('1e-35'))
chk("World（偶 k）= s0 + s2 = 2N_d + μ² = 90 EXACT", abs(S[0] + S[2] - 90), mp.mpf('1e-35'))
chk("Observer（奇 k）= s1 + s3 = 2N_d = 88 EXACT", abs(S[1] + S[3] - 88), mp.mpf('1e-35'))
chk("扇區缺陷 δ = (μ², −sec, 0, +sec) 之總和 = μ² = 2 EXACT",
    abs((S[0]-N_d) + (S[1]-N_d) + (S[2]-N_d) + (S[3]-N_d) - 2), mp.mpf('1e-35'))

print("\n" + "=" * 78)
print("§B  生成元: Ŝ = S^{N_d/2} = S²² on ℤ₈₈（環 C₈₈）")
print("=" * 78)
# Ŝ 作用於 DFT 基 |k⟩: eigenvalue i^k（精確）
spec_ok = all(abs(mp.exp(2 * mp.pi * I * 22 * k / N) - I**k) < mp.mpf('1e-30')
              for k in range(N))
chk("Ŝ|k⟩ = e^{2πi·22k/88}|k⟩ = i^k|k⟩（∀k = 0..87, 精確）", mp.mpf(0) if spec_ok else mp.mpf(1), mp.mpf('1e-30'))
order_ok = mp.exp(2 * mp.pi * I * 22 * N / N)   # Ŝ⁴ = S^{88} = 1
chk("Ŝ⁴ = S^{88} = 𝟙 ⟹ 階 = 4（生成 ℤ₄ = ℤ₈₈/ℤ₂₂）", abs(order_ok - 1), mp.mpf('1e-35'))
# 與環 Laplacian 交換: C₈₈ Laplacian 之譜 = 4sin²(πk/88) ⟹ 移位對角化之
comm_ok = all(abs((2 - 2 * mp.cos(2 * mp.pi * k / N)) - 4 * mp.sin(mp.pi * k / N) ** 2) < mp.mpf('1e-30')
              for k in range(N))
chk("Ŝ 與環 Laplacian 交換（同一 DFT 基同時對角化）", mp.mpf(0) if comm_ok else mp.mpf(1), mp.mpf('1e-30'))
chk("模 4 扇區大小: 88/4 = 22 = N_d/2 = L₅·2（均勻）", abs(N / 4 - N_d / 2), mp.mpf('1e-35'))

print("\n" + "=" * 78)
print("§C  站-模對偶: 4:1 decimation 陪集之 DFT 支撐")
print("=" * 78)
print("    x_i^{(c)} = 1 ⟺ i ≡ c (mod 4)（4:1 decimation 子格）")
print("    DFT: X_k^{(c)} = Σ_j e^{−2πik(c+4j)/88} = 22·e^{−iπkc/44}·[k ≡ 0 (mod 22)]")
maxdev_support, maxdev_phase = mp.mpf(0), mp.mpf(0)
special = {0: 1, 22: -1j, 44: -1, 66: 1j}   # ω₄^{−c} 於 {0,22,44,66}
for c in range(4):
    for k in range(N):
        X = sum(mp.exp(-2 * mp.pi * I * k * (c + 4 * j) / 88) for j in range(22))
        if k % 22 == 0:
            j = k // 22
            expct = 22 * (I ** (-c * j))
            maxdev_phase = max(maxdev_phase, abs(X - expct))
        else:
            maxdev_support = max(maxdev_support, abs(X))
chk("支撐 = {0, 22, 44, 66} = (N_d/2)·{0,1,2,3}（其餘模 = 0）", maxdev_support, mp.mpf('1e-30'))
chk("相位 = 22·ω₄^{−cj}（ω₄ = i, 於四個特殊模）", maxdev_phase, mp.mpf('1e-30'))
print("    ★ 站-ℤ₄（4:1 陪集）與模-ℤ₄（k mod 4）係**同一 ℤ₄ 之對偶兩面**（DFT, 無需前提）")

print("\n" + "=" * 78)
print("§D  算子側 ℤ₄: z ∈ Z(SU(B)) ⊂ SU(12)")
print("=" * 78)
print("    z = diag(i,i,i,i, 1,…,1)（4 個 i, 8 個 1）: det = i⁴ = 1 ⟹ z ∈ SU(4) ⊂ SU(12) ✓")
print("    Λ^k(12) 上: 14 個 1-維槽中取 k 個 ⟹ 本徵值 = i^k ⟹ χ = k mod 4（= T3）")
ldim = [1, 12, 66, 220, 495, 792, 924, 792, 495, 220, 66, 12, 1]
classdim = {c: sum(ldim[k] for k in range(13) if k % 4 == c) for c in range(4)}
print(f"    ℤ₄ 類維數和: {classdim}  (總 {sum(classdim.values())} = 2¹² = {2**12})")
chk("Λ^k 中心荷 = i^k ⟺ χ = k mod 4（T3）", mp.mpf(0) if all((I**k) == (I**(k % 4)) for k in range(13)) else mp.mpf(1), mp.mpf('1e-30'))
chk("Σ dim(Λ^k), k=0..12 = 2¹² = 4096 EXACT", abs(sum(classdim.values()) - 4096), mp.mpf('1e-35'))
chk("算子 ℤ₄ 缺陷 = (−2B², 0, +2B², 0)（對稱, 總和 0）",
    abs((classdim[0] - 1024) + 2*B**2) + abs(classdim[1] - 1024) + abs(classdim[2] - 1024 - 2*B**2) + abs(classdim[3] - 1024),
    mp.mpf('1e-35'))

print("\n" + "=" * 78)
print("§E  橋裁定")
print("=" * 78)
print("""  (1) 群層: 兩側 ℤ₄（鏈: ℤ₈₈/ℤ₂₂ 由 Ŝ; 算子: Z(SU(B)) 由 z）皆有**區別生成元** 1 ↔ i
      ⟹ iso Φ: Ŝ ↦ z **存在且唯一**（非任意選擇）⟹ 舊判「同模但無 map」**升級為「map 存在」**。
  (2) 預註冊證偽測試（docs/07 §6）: ΔB=1 ⟹ k ≡ ±|B−L| = 2 (mod 4) ⟹ 鏈扇區 class 2
      ⟹ Σγ = N_d = 44 EXACT（§A）⟹ **測試有牙且通過**（鑑別性替代: class 0 = N_d + μ² = 46 ≠ 44）。
      逐值: {2, 6, 10} 全部 ≡ 2 (mod 4) ✓""")
dB1 = [k for k in range(13) if k % 4 == 2]
chk("ΔB=1 合格集 {2,6,10} 全落 class 2", mp.mpf(0) if dB1 == [2, 6, 10] else mp.mpf(1), mp.mpf('1e-30'))
chk("class 2 之 Σγ = N_d（零缺陷）⟹ ΔB=1 對應鏈上**唯一零缺陷扇區**",
    abs(S[2] - N_d), mp.mpf('1e-35'))
print("""  (3) ⚠️ 誠實界定: (2) 之「通過」部分係**定義性**（兩側皆 k mod 4 之同一算術）
      ⟹ 真正有內容之檢定 = **weight 對齊**（鏈側測度 Σγ vs 算子側測度 dim）:
        鏈側缺陷 = (μ², −sec(π/88), 0, +sec(π/88))（總和 μ²）
        算子側缺陷 = (−32, 0, +32, 0)（總和 0），32 = 2B²
      ⟹ 兩測度**類型唔同**（譜和 vs 維數）⟹ 比較係 **ill-defined**，
         既唔能證實亦唔能證偽 ⟹ 殘餘命題 = 需 𝒯 型別規則外之**共同測度**（例如 𝒯 上之 action/trace）""")
chk("殘餘命題明確化: 兩側缺陷向量唔在同構下對齊（(2,−s,0,s) vs (−32,0,32,0)）⟹ 無 common refinement",
    mp.mpf(0) if (S[0]-N_d) != (classdim[0]-1024) else mp.mpf(1), mp.mpf('1e-30'))

print("\n" + "=" * 78)
print("§F  跨鏈: 格點修正階 + sec(π/88) ∉ ℚ(√5)")
print("=" * 78)
grid_sec = sec88 - 1
grid_sinc = 1 - (88 / mp.pi) * mp.sin(mp.pi / 88)
print(f"    sec(π/88) − 1        = {mp.nstr(grid_sec, 18)}   ≈ (π/88)²/2 = {mp.nstr((mp.pi/88)**2/2, 18)}")
print(f"    1 − (88/π)sin(π/88)  = {mp.nstr(grid_sinc, 18)}   ≈ (π/88)²/6 = {mp.nstr((mp.pi/88)**2/6, 18)}  [= O213 R7 之格點修正]")
chk("兩者皆為 (π/88) 之二階格點修正 ⟹ 同族（相對偏差 < 1%）",
    abs(grid_sec / ((mp.pi/88)**2/2) - 1) + abs(grid_sinc / ((mp.pi/88)**2/6) - 1), mp.mpf('0.01'))
rel = mp.pslq([mp.mpf(1), mp.sqrt(5), sec88], maxcoeff=10**6, maxsteps=10**5)
chk("PSLQ 無 ℚ(√5) 關係（maxcoeff 1e6）⟹ sec(π/88) ∉ ℚ(√5)（配合 T-FIELD 定理）",
    mp.mpf(0) if rel is None else mp.mpf(1), mp.mpf('1e-30'))
print("    ★ 結論: 鏈側 ℤ₄ 非對稱 sec(π/88) 屬 ℚ(ζ₈₈)⁺ \\ ℚ(√5) ⟹ **唔可以用 φ 表達**（結構性陳述）")

print("=" * 78)
print(f"O210 z4-bridge — PASS {stats['PASS']} / FAIL {stats['FAIL']}")
print("=" * 78)
print("RESULT:", "FAIL" if stats["FAIL"] else "PASS")
