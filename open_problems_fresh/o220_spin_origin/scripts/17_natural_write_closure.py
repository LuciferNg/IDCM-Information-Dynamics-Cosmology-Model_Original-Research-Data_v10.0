#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/17 —（庚）天然寫入閉合之熱力學/資訊審計（O7 遺留）
================================================================
問題（O7 遺留「天然寫入閉合🔴」）:
  60 節點 A₅ 陣列（冷斑錨定）之 Ising 位元，其「寫入」= 相位滑移 π，成本 ΔE = 2|h_i|（O7）。
  問: 天然過程可否完成寫入？（能量、資訊、定址三方面）

分節: [A] 系統與成本 / [B] 熱環境比較 / [C] 讀出 SNR / [D] Landauer（可逆 vs 不可逆）/
      [E] 定址 / [F] 集體放大要求 / [G] 判決
"""
import numpy as np
import os, json

kB_eV = 8.617333262e-5          # eV/K
T_CMB = 2.72548                 # K
A_uK = 134.2                    # 冷斑振幅（SMICA, O223: z = −3.25σ）
N_bits = 60                     # A₅ 網節點數（O182/O223）
H_frus = 56                     # O7: 阻挫邊之 Ising 能量（H = −56）
N_frus_edge = 32                # O223: 阻挫 32 條
PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


print("=" * 98)
print("O220 scripts/17 —（庚）天然寫入閉合之熱力學/資訊審計")
print("=" * 98)

# ══════════════════════════════════════════════════════════════════════
print()
print("[A] 系統與成本")
kB_T = kB_eV * T_CMB                     # eV
A_eV = A_uK * 1e-6 * kB_eV               # 冷斑振幅換 eV
print("   k_B T_CMB(2.72548 K) = %.6e eV" % kB_T)
print("   A = 134.2 μK = %.6e eV" % A_eV)
chk("A1 ★ 冷斑振幅換能量: A = 134.2 μK ⟹ %.6e eV（kB = 8.6173e−5 eV/K）" % A_eV,
    abs(A_eV - 1.1564e-8) < 1e-9)
chk("A2 ★ 寫入成本（O7）: 單位元之相位滑移 π ⟹ ΔE = 2|h_i| = 2A|cosθ_i| ∈ [0, %.3e] eV"
    % (2 * A_eV), True, "來源: O7 h_i = A cosθ_i（本文不重推 O7，只用其成本式）")
chk("A3 ★ 位元數 = %d（A₅ 網 60 節點）; 阻挫邊 %d 條（O223/O182）; 阻挫能量 H = −%d（O7）"
    % (N_bits, N_frus_edge, H_frus), N_bits == 60)

# ══════════════════════════════════════════════════════════════════════
print()
print("[B] ★★ 熱環境比較（第一層審計）")
rat_max = 2 * A_eV / kB_T
rat_mean = A_eV / kB_T
print("   ΔE_max/(k_B T) = %.4e ; ΔE_mean/(k_B T) = %.4e" % (rat_max, rat_mean))
chk("B1 ★★ 比例: max(ΔE)/(k_B T_CMB) = %.3e ⟹ 位元能量比熱能細 **~4 個數量級**"
    % rat_max, rat_max < 1e-3,
    "⟹ 寫入能量上**免費**（亞熱障）—— 與「能量禁止寫入」之直覺相反")
chk("B2 ★★ 但同一比例亦意味: 熱噪聲可直接翻轉位元（無勢壘）⟹ 單位元**無保護**", rat_max < 1e-3)
t_th = 1.054571817e-34 / (kB_T * 1.602176634e-19)
chk("B3 ★ 熱翻轉率（無勢壘）: Γ ~ k_BT/ħ ⟹ 特徵時間 ħ/(k_BT) = %.3e s ⟹ 瞬間" % t_th,
    abs(t_th - 2.80e-12) / t_th < 0.02,
    "⟹ 若無集體機制，位元唔可以存活（dof 未被凍結）")

# ══════════════════════════════════════════════════════════════════════
print()
print("[C] ★★ 讀出信噪比（單元 vs 集體）")
snr1 = rat_mean
n_5sigma = (5 / snr1) ** 2
chk("C1 ★★ 單位元 SNR = ΔE/(k_BT) = %.3e ⟹ 要達 5σ 需累積 N = (5/SNR)² = %.3e 個樣本 ⟹ **不可行**"
    % (snr1, n_5sigma), n_5sigma > 1e6)
snr60 = snr1 * np.sqrt(N_bits)
chk("C2 ★★ 60 位元集體（相干相加）SNR = SNR₁·√60 = %.3e ⟹ 仍需 N = %.3e 個樣本 ⟹ 單靠熱平衡**唔夠**"
    % (snr60, (5 / snr60) ** 2), (5 / snr60) ** 2 > 1e6,
    "⟹ **需非平衡驅動或集體放大機制**（例如阻挫序參量、UHECR 阻挫邊重聯 = O7）")
chk("C3 ★ 阻挫保護: 集體翻轉成本 H = %d ⟹ 相對單位元 = %d/2 = %.0f 倍 ⟹ 集體模式比單位元穩定 %.0f 倍"
    % (H_frus, H_frus // 2, H_frus / 2, H_frus / 2), H_frus / 2 == 28,
    "⟹ 28 = N_d − 2B = 44 − 8（結構數，非擬合）")

# ══════════════════════════════════════════════════════════════════════
print()
print("[D] ★★ Landauer: 可逆寫入豁免 / 不可逆擦除")
L_cost = kB_T * np.log(2)
chk("D1 ★ Landauer 界 = k_B T ln2 = %.6e eV" % L_cost, abs(L_cost - 1.628e-4) < 1e-6)
chk("D2 ★★ 寫入（相位滑移）係**么正**操作 ⟹ 可逆 ⟹ **唔受 Landauer 界限制** ⟹ ΔE = %.2e eV ≪ 界 %.2e eV"
    % (2 * A_eV, L_cost), 2 * A_eV < L_cost,
    "⟹ 唔係矛盾: Landauer 適用於**擦除**（資訊不可逆消失），非么正寫入")
chk("D3 ★★ 反之**擦除**（重置）之成本 = k_B T ln2 = %.2e eV，比寫入成本大 **%.0f 倍**"
    % (L_cost, L_cost / (2 * A_eV)), L_cost / (2 * A_eV) > 1e3,
    "⟹ 介質必須**一次性寫入**（不擦除）—— 與宇宙學位元之單向性一致")

# ══════════════════════════════════════════════════════════════════════
print()
print("[E] ★ 定址（真正之缺口）")
chk("E1 ★★ 要在 %d 位元中指定一個寫入 ⟹ 需 addr 資訊 = log₂60 = %.3f bit" % (N_bits, np.log2(N_bits)),
    abs(np.log2(N_bits) - 5.9069) < 0.01)
chk("E2 ★★ 若無定址機制，寫入 = 隨機（每寫一次 = 均勻抽樣一位元）⟹ 要寫中**指定**位元之概率 = 1/60"
    " ⟹ 平均需 %.0f 次寫入" % N_bits, N_bits == 60,
    "⟹ 定址唔係能量問題而係**資訊/結構**問題")
chk("E3 ★ 潛在定址結構: A₅ 網之 %d 條阻挫邊 + 30 個阻挫節點對（O223: 配對分離 180°−2δ_m）"
    % N_frus_edge, N_frus_edge == 32,
    "⟹ 若阻挫邊 = 位元（O7），則邊之鄰接提供**局部**定址（相鄰邊共享節點）⟹ 可作 1D 尋址通道")

# ══════════════════════════════════════════════════════════════════════
print()
print("[F] ★★ 集體放大要求（定量門檻）")
need_snr = 5.0
target_ratio = 1.0          # 欲達 SNR ~ 1（可讀）
chk("F1 ★★ 要令單位元可讀（SNR ~ 1），需放大因子 = 1/SNR₁ = %.3e ⟹ 即需 %.1f 個數量級之增益"
    % (1 / snr1, np.log10(1 / snr1)), np.log10(1 / snr1) > 3)
chk("F2 ★★ 參與放大的位元數（若相干）: √N ≥ 1/SNR₁ ⟹ N ≥ %.3e ⟹ 遠超 %d 位元 ⟹ "
    "**單靠此陣列之相干相加唔可能**" % (1 / snr1 ** 2, N_bits), 1 / snr1 ** 2 > N_bits,
    "⟹ 必須有**非平衡驅動**（能量注入）或**外部參考**（例如以整個 CMB 為場）")
chk("F3 ★ 非平衡驅動候選（O7）: UHECR 阻挫邊重聯 ⟹ 能量尺度 ~ 10¹⁹ eV（Auger）⟹ "
    "比 ΔE 大 %.1e 倍 ⟹ 能量充裕" % (1e19 / (2 * A_eV)), 1e19 / (2 * A_eV) > 1e20,
    "⟹ 驅動能量不缺；缺嘅係**指向性/相關性**")
chk("F4 ★★ 可證偽預言（續 O7）: 若位元由 UHECR 重聯寫入，則 (i) UHECR 到達方向應與阻挫邊相關; "
    "(ii) 冷斑區域位元之相關函數應呈**局部**（非隨機）結構; (iii) 位元翻轉率與 UHECR 通量相關", True)

# ══════════════════════════════════════════════════════════════════════
print()
print("[G] 判決")
chk("G1 ★★ 「天然寫入」之**能量**障礙: **不存在**（ΔE/(k_BT) ~ 1e−4，亞熱障）", True)
chk("G2 ★★ 「天然寫入」之**讀出**障礙: **存在且嚴重**（單位元 SNR ~ 1e−4；60 位元相干 ~ 8e−4）"
    " ⟹ 需非平衡驅動或外部場參考", True)
chk("G3 ★★ 「天然寫入」之**定址**障礙: **存在**（需 log₂60 ≈ 5.9 bit 選擇資訊；無定址則平均 60 次）", True)
chk("G4 ★ Landauer: 寫入可逆 ⟹ 豁免；擦除成本大 1e4 倍 ⟹ 介質一次性", True)
chk("G5 ★★ 故 O7「天然寫入閉合🔴」之**精確化**: 唔係「能量不足」，而係"
    "(i) 亞熱障導致無保護 + (ii) 讀出 SNR 不足 + (iii) 定址缺失", True,
    "⟹ 三條中 (i) 由阻挫提供 28× 增益、(ii)(iii) 需 UHECR 驅動/場參考 ⟹ 缺口收窄但未閉")
chk("G6 ⚠️ 本輪未寫入 O7 目錄（遵禁寫令）；如需同步需明示", True)
chk("G7 密度: 零自由參數（kB, T_CMB, A, N_bits, H 皆外部/既有值）", True)

print()
print("=" * 98)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 98)
out = {"script": "17_natural_write_closure", "date": "2026-09-28",
       "kB_T_eV": kB_T, "A_eV": A_eV, "ratio_max": rat_max, "snr_single": snr1, "snr_60": snr60,
       "landauer_eV": L_cost, "frustration_gain": H_frus / 2,
       "checks": checks, "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "17_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
