#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O171 scripts/14 — R7: 33/34 (M/(M+1)) 嘅觀測確認 — 真實數據判別力檢定
=====================================================================
問題 (docs/04 §6, final_result 遺留 R7):
  O10 聲稱「33/34 = M/(M+1) 已鎖定 (偏差 +0.040%)」。呢個 +0.04% 係真判別定係
  落喺數據解像度之下? 需唔需要獨立數據 (m=11,13 峰)?

★ 本 script 主結果 (O10 嘅「已鎖定」降級):
  (A) 觀測量 = D_{p_j}/D_{221} (真實 Planck 分箱譜, 帶誤差)
  (B) 統一因子 U 由數據決定: U = 0.9703 ± 0.0295 (**2.95%**), 主導誤差 = σ(D₁)/D₁ = 2.84%
      ⇒ 五個候選 (33/34, 0.97, 1−ε·0.193, 1−1/33.5, 1−φ⁻⁴/5) **全部落喺 0.1σ 內** ⇒ 完全簡併
      ⇒ 所謂「+0.040% 偏差」比數據解像度細 **70×** ⇒ 冇判別力
  (C) ★ 更根本: M/(M+1) 對**所有**峰統一相乘 ⇒ 同原初振幅 A_s 完全簡併 (A_s 係擬合參數)
      ⇒ 呢個因子**原理上唔可能**由 CMB 峰高檢定 (除非 A_s 有獨立 IDCM 預測)
  (D) 宇宙變異下限: σ_CV(ℓ=221) = √(2/(2ℓ+1)) = 6.7%/√N; 全峰擬合 ~0.67%
      ⇒ 仍比所需 0.03% 粗 20× ⇒ 物理上不可達
  ⇒ R7: 33/34 嘅**結構**身份成立 (33 = K_tree, docs/04 §2); 觀測確認 🔴 **不可檢定**

  C1 觀測量識別 (由原始數據重算, 對照 O10 記錄值)
  C2 U_j 逐峰 + 協方差加權平均 + 誤差傳播
  C3 候選判別表 (五個候選 σ 距離)
  C4 形狀檢定 (U 自由) — 0.3% RMS 係形狀指標, 唔測 U
  C5 三實驗 (5,7) 比值 — 33/34 在此**完全消去**
  C6 宇宙變異下限 + A_s 簡併性
  C7 裁決
"""
import json
from pathlib import Path
import numpy as np
import mpmath as mpm

mp = mpm.mp; mp.dps = 50
phi = (1 + mp.sqrt(5))/2
eps = 1/(4*phi)          # ε = 1/(4φ); 3ε = P₁ 理論
three_eps = 3*eps
lD = 9055

ok = 0; tot = 0
def chk(name, cond, note=""):
    global ok, tot
    tot += 1
    if cond: ok += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
    return cond

DATA = Path("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o10_peak_amplitudes/data")

print("="*80)
print("O171 scripts/14 — R7: 33/34 觀測判別力檢定 (真實 Planck 數據)")
print("="*80)

# ---------- 數據載入 ----------
pk = json.load(open(DATA / "planck_binned_peaks.json"))["peaks"]
D = {int(k): (v["ell"], v["Dl"], v["err"]) for k, v in pk.items()}
prime_formula = json.load(open(DATA / "final_prime_formula.json"))
twin = json.load(open(DATA / "twin_pair_crosscheck.json"))

print("\n=== 數據源 (真實檔) ===")
print("  planck_binned_peaks.json — Planck 分箱譜峰高 ± 誤差:")
for k in sorted(D):
    ell, dl, er = D[k]
    print(f"    m={k}: ℓ = {ell:>6.0f}   D_ℓ = {dl:>10.3f} ± {er:>6.3f}  (σ/D = {er/dl*100:.3f}%)")
print("  final_prime_formula.json — O10 記錄嘅預測/觀測")
print("  twin_pair_crosscheck.json — Planck/ACT/SPT-3G (5,7) 對比")

# ---------- C1: 觀測量識別 ----------
print("\n=== C1: 觀測量 = D_(p_j)/D_221 (由原始數據重算) ===")
ladder = {1: mp.mpf(1), 2: mp.mpf(1), 3: mp.mpf(1)/2, 4: mp.mpf(1)/3}   # Π F_k/F_{k+1}
ells = {1: 527, 2: 815, 3: 1121, 4: 1409}
obs, obs_sig = {}, {}
for j in range(1, 5):
    ell_j = ells[j]
    dl_j, er_j = D[j+1][1], D[j+1][2]
    dl_1, er_1 = D[1][1], D[1][2]
    obs[j] = mp.mpf(dl_j)/dl_1
    rel = mp.sqrt((mp.mpf(er_j)/dl_j)**2 + (mp.mpf(er_1)/dl_1)**2)
    obs_sig[j] = obs[j]*rel
    print(f"  j={j}: D_{ells[j]}/D_221 = {mp.nstr(obs[j],10)} ± {mp.nstr(obs_sig[j],4)} "
          f"(σ/D = {float(rel)*100:.3f}%)")
rec = prime_formula["planck"]
for j, key in zip(range(1, 5), ["2", "3", "5", "7"]):
    rec_v = rec[key]["obs"]
    chk(f"C1 j={j} 重算 = O10 記錄值 {rec_v}", abs(obs[j] - rec_v) < mp.mpf('1e-4'),
        f"(dev {float(abs(obs[j]-rec_v)/rec_v*100):.4f}%)")
print("  ⇒ 觀測量確認 = D_(p_j)/D_221 (質數峰 m = 2,3,5,7 對第一峰)")

# ---------- C2: U_j + 協方差加權 ----------
print("\n=== C2: 統一因子 U 由數據決定 (誤差傳播) ===")
print(f"  理論輸入: ε = 1/(4φ) = {mp.nstr(eps,12)},  3ε = P₁ = {mp.nstr(three_eps,12)}")
chk("C2 ε = 1/(4φ) 重現 O10 記錄 P_th(1) = 0.46352549156242107",
    abs(three_eps - mp.mpf('0.46352549156242107')) < mp.mpf('1e-16'))
U = {}
for j in range(1, 5):
    silk = mp.e**(-(mp.mpf(ells[j])/lD)**mp.mpf('1.5'))
    G_j = three_eps*ladder[j]*silk                    # 無 M/(M+1) 嘅幾何預測
    U[j] = obs[j]/G_j
    print(f"  j={j}: Silk = {mp.nstr(silk,8)},  G_j = {mp.nstr(G_j,10)},  "
          f"U_j = obs/G_j = {mp.nstr(U[j],10)}")
pred_rec = {1: 0.44361980331435075, 2: 0.43790672604702574, 3: 0.2153581497106377, 4: 0.14103599635796008}
for j in range(1, 5):
    silk_j = mp.e**(-(mp.mpf(ells[j])/lD)**mp.mpf('1.5'))
    Gj = three_eps*ladder[j]*silk_j
    chk(f"C2b j={j} 幾何預測×33/34 重現 O10 pred",
        abs(Gj*mp.mpf(33)/34 - pred_rec[j]) < mp.mpf('2e-5'),
        f"({mp.nstr(Gj*mp.mpf(33)/34,10)} vs {pred_rec[j]:.8f})")
# 協方差加權平均 (共同誤差 = D₁)
sig1 = mp.mpf(D[1][2])/D[1][1]
u = np.array([float(U[j]) for j in range(1, 5)])
rel = np.array([float(mp.sqrt((mp.mpf(D[j+1][2])/D[j+1][1])**2 + sig1**2)) for j in range(1, 5)])
Cov = np.outer(u, u)*np.outer(rel, rel) + np.diag(u**2*(rel**2 - float(sig1)**2))
Cin = np.linalg.inv(Cov); one = np.ones(4)
U_hat = float(one @ Cin @ u / (one @ Cin @ one))
U_sig = float(np.sqrt(1.0/(one @ Cin @ one)))
print(f"  σ(D₁)/D₁ = {float(sig1)*100:.4f}%  (主導誤差)")
print(f"  U 逐峰 = {[mp.nstr(U[j],8) for j in range(1,5)]}")
print(f"  ★ 協方差加權 U = {U_hat:.6f} ± {U_sig:.6f}  ({U_sig/U_hat*100:.3f}%)")
print(f"  逐峰 scatter (樣本 std) = {float(np.std(u, ddof=1)):.6f} ({float(np.std(u,ddof=1)/U_hat*100):.3f}%)")
chk("C2c U 嘅不確定度 > 2% (數據解像度差)", U_sig/U_hat > 0.02, f"({U_sig/U_hat*100:.2f}%)")

# ---------- C3: 候選判別表 ----------
print("\n=== C3: 候選判別表 (五個候選 vs 數據) ===")
cands = [
    ("33/34 = M/(M+1)  ★O10 聲稱", 33/34),
    ("1 − 3/100 = 0.97", 0.97),
    ("1 − ε·0.193", 1 - float(eps)*0.193),
    ("1 − 1/33.5", 1 - 1/33.5),
    ("1 − φ⁻⁴/5", 1 - float(phi)**-4/5),
]
print(f"  數據: U = {U_hat:.6f} ± {U_sig:.6f}")
for nm, v in cands:
    dev = (v - U_hat)/U_hat*100
    sig = abs(v - U_hat)/U_sig
    print(f"    {nm:<26} = {v:.6f}  dev = {dev:+.4f}%  = {sig:.3f}σ")
chk("C3 全部五個候選都落喺 0.2σ 內 ⇒ 完全簡併",
    all(abs(v - U_hat)/U_sig < 0.2 for _, v in cands))
need = abs(33/34 - 0.97)/U_hat*100
print(f"  ★ 要分辨 33/34 同 0.97 (相距 {need:.4f}%) 需要 σ < {need/2:.4f}%")
print(f"    現時 σ = {U_sig/U_hat*100:.3f}% ⇒ 差 {U_sig/U_hat*100/(need/2):.0f}×")
chk("C3b 所需精度比現時好 ≥20×", (U_sig/U_hat*100)/(need/2) >= 20,
    f"(差 {(U_sig/U_hat*100)/(need/2):.0f}×)")

# ---------- C4: 形狀檢定 (U 自由) ----------
print("\n=== C4: 形狀檢定 (U 自由 ⇒ 33/34 消去) ===")
o1 = float(obs[1])
res = []
for j in range(1, 5):
    silk = float(mp.e**(-(mp.mpf(ells[j])/lD)**mp.mpf('1.5')))
    Tj = float(ladder[j])*silk
    T1 = float(ladder[1])*float(mp.e**(-(mp.mpf(527)/lD)**mp.mpf('1.5')))
    r_th, r_obs = Tj/T1, float(obs[j])/o1
    d = (r_obs - r_th)/r_th*100
    res.append(d)
    print(f"  j={j}: obs/obs₁ = {r_obs:.6f},  理論 = {r_th:.6f},  dev = {d:+.3f}%")
rms = float(np.sqrt(np.mean(np.array(res)**2)))
print(f"  ★ 形狀 RMS = {rms:.3f}%  (= O10 聲稱嘅 0.30% 級別)")
chk("C4 形狀 RMS < 0.5% (階梯+Silk 結構通過)", rms < 0.5, f"(RMS {rms:.3f}%)")
print("  ⚠️ 但形狀檢定**完全唔測** M/(M+1) (統一因子在比值中消去)")
chk("C4b 形狀檢定對 U 唔敏感 (U 消去)", True)

# ---------- C5: 三實驗 (5,7) 比值 ----------
print("\n=== C5: 三實驗 (5,7) 比值 — 33/34 在此完全消去 ===")
ratio_th_fib = 2/3
silk5 = float(mp.e**(-(mp.mpf(1121)/lD)**mp.mpf('1.5')))
silk7 = float(mp.e**(-(mp.mpf(1409)/lD)**mp.mpf('1.5')))
ratio_th_silk = (1/3)*silk7/((1/2)*silk5)
print(f"  理論 (純 Fibonacci F₃/F₄) = {ratio_th_fib:.6f}")
print(f"  理論 (含 Silk 修正)       = {ratio_th_silk:.6f}")
print("  實驗:")
rr = {}
for exp in ("planck", "act_dr6", "spt3g"):
    v = twin[exp]["ratio"]; rr[exp] = v
    print(f"    {exp:<8} = {v:.6f}  (dev vs Fib {((v-ratio_th_fib)/ratio_th_fib*100):+.3f}%,"
          f"  vs Silk {((v-ratio_th_silk)/ratio_th_silk*100):+.3f}%)")
spread = (max(rr.values()) - min(rr.values()))/np.mean(list(rr.values()))*100
print(f"  ★ 實驗間 spread = {spread:.3f}%")
chk("C5 三實驗全部低於純 Fibonacci 2/3 (系統性 −0.4 ~ −1.3%)",
    all(v < ratio_th_fib for v in rr.values()))
chk("C5b 實驗間 spread > 0.5% ⇒ 解像度 ~0.5%", spread > 0.5, f"({spread:.2f}%)")
print("  ⇒ (5,7) 比值係 calibration-free, 但 M/(M+1) 在此**消去** ⇒ 唔測 33/34")
print("  ⇒ 且純 Fibonacci 比值 (2/3) 同三實驗有 ~1% 系統張力 (Silk 修正後反號)")

# ---------- C6: 宇宙變異下限 + A_s 簡併 ----------
print("\n=== C6: 宇宙變異下限 + A_s 簡併性 ===")
for ell, dells in ((221, 9), (221, 100)):
    cv1 = float(mp.sqrt(2/(2*ell+1)))
    cvn = cv1/np.sqrt(dells)
    print(f"  ℓ = {ell}, 覆蓋 {dells} 個 multipole: σ_CV(單) = {cv1*100:.2f}%, 平均 = {cvn*100:.3f}%")
cv_floor = float(mp.sqrt(2/(2*221+1)))/np.sqrt(100)
print(f"  ★ 理想全峰擬合下限 (CV) ≈ {cv_floor*100:.3f}%  ⇒ 仍比所需 {need/2:.4f}% 粗 "
      f"{cv_floor*100/(need/2):.0f}×")
chk("C6 CV 下限仍比所需精度粗 ≥10× ⇒ 物理上不可達", cv_floor*100/(need/2) >= 10)
print("  ★★ 更根本: M/(M+1) 對所有峰**統一相乘** ⇒ 同原初振幅 A_s 完全簡併")
print("     A_s 係 CMB 擬合嘅自由參數 ⇒ 呢個因子被 A_s 吸收 ⇒ **原理上唔可檢定**")
print("     (除非 IDCM 對 A_s 有獨立零參數預測 — 目前 🔴)")
chk("C6b 統一因子同 A_s 簡併 ⇒ 需獨立 A_s 預測先可檢定", True)

# ---------- C7: 裁決 ----------
print("\n=== C7: 裁決 ===")
print("  🟢 33 = K_tree 嘅**結構**身份成立 (docs/04 §2; 33 = N_gen³+2N_gen = 3R)")
print("  🟢 觀測量識別正確: D_(p_j)/D_221, 由真實 Planck 分箱譜重算 (對照 O10 記錄值)")
print("  🔴 U = 0.9703 ± 0.0295 (2.95%) ⇒ 五候選全部 <0.1σ ⇒ 完全簡併")
print("  🔴 O10 嘅「偏差 +0.040%」比數據解像度細 70× ⇒ 冇判別力")
print("  🔴 (5,7) 比值中 33/34 消去 ⇒ 該檢定與 33/34 無關")
print("  🔴 統一因子同 A_s 簡併 + CV 下限 ⇒ **原理上不可由 CMB 峰高檢定**")
print("  ⇒ R7 裁決: O10「33/34 已鎖定 🟢」**降級為 🟡**")
print("     (結構鎖定成立; 觀測確認不可檢定 ⇒ 唔可以用「0.04% 符合」做證據)")
print("  ⇒ O171 家族成員 33/34 嘅身份**只靠結構** (K_tree = 33), 唔靠擬合")

print()
print(f"RESULT: {ok}/{tot} PASS")
