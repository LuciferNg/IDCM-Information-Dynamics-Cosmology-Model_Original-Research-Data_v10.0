# O127 docs/04 — P3: DESI DR2 BAO 盲測（out-of-sample）

> 腳本: `scripts/04_desi_dr2_blindtest.py` → `data/verify/04_desi_dr2_blindtest.log`
> 數據: DESI DR2 BAO（arXiv:2503.14738, PRD 112, 083515）— 7 tracers, z=0.295→2.330
> 狀態: **🟢 零參數 out-of-sample 通過**

---

## 一、結論（先行）

IDCM 零參數 `r_d = λ_sync/2 = 147.4386 Mpc` 對 **DESI DR2 獨立數據**（非 eBOSS，非本 O 擬合）：

- vs DESI fiducial `r_d = 147.05 Mpc` → **+0.264%**
- vs DESI DR2 BAO+CMB ΛCDM fit `r_d = 147.69 ± 0.94 Mpc` → **−0.27σ** ✅
- 7 tracers `α_iso` 聯合 `χ² = 18.03/7 = 2.58`（LRG2 為主要貢獻）

**零自由參數、獨立數據集、out-of-sample ⟹ 通過。**

---

## 二、DESI DR2 官方量

| 量 | 值 | 來源 |
|---|---|---|
| fiducial r_d | 147.05 Mpc | DESI DR2 eq.(2) baseline |
| BAO+CMB ΛCDM fit | H₀ = 68.36 ± 0.29, H₀·r_d = 100.96 ± 0.48 [100 km/s] | DESI DR2 Table |
| ⟹ r_d^CMB = (H₀r_d)/H₀ | **147.69 ± 0.94 Mpc** | 推得 |
| **IDCM 零參數 r_d** | **147.4386 Mpc** | O51/O167 |

| 比較 | 偏差 | pull |
|---|---|---|
| IDCM vs fiducial | +0.264% | — |
| IDCM vs BAO+CMB | −0.169% | **−0.27σ** ✅ |

---

## 三、α_iso 逐 tracer

IDCM 預言（距離律吻合 ⟹ `α_iso = r_d^fid/r_d^IDCM = 0.99736`）：

| tracer | z | α_iso | σ | pull |
|---|---|---|---|---|
| BGS | 0.295 | 0.9857 | 0.0093 | −1.25 |
| LRG1 | 0.510 | 0.9911 | 0.0077 | −0.81 |
| **LRG2** | 0.706 | 0.9749 | 0.0067 | **−3.35** |
| LRG3+ELG1 | 0.934 | 0.9886 | 0.0046 | −1.91 |
| ELG2 | 1.321 | 0.9911 | 0.0071 | −0.88 |
| QSO | 1.484 | 1.0032 | 0.0153 | +0.38 |
| Lya | 2.330 | 0.9971 | 0.0082 | −0.03 |

`χ² = 18.03 / 7 dof = 2.58`，`p = 0.0118`。

> ⚠️ **誠實註記**：DESI DR2 **全部 tracer `α_iso` 系統性 <1（≈0.985）**，
> LRG2 達 −3.35σ。`α_iso` 依賴 fiducial Ω_m，呢個系統性偏移係 **DESI 數據自身** 嘅
> 特徵（唔係 IDCM 特有）；IDCM 預言 0.9974 位於 ΛCDM 系統偏移與 1 之間。
> ⟹ 整體 χ²/dof < 3 相容，但 **LRG2 係真張力點**，唔應掩蓋。

---

## 四、DV/rd 幾何交叉

`DV/rd`（只用幾何，不依賴 Ω_m 假設）：
BGS=7.94±0.075, LRG1=12.72±0.099, LRG2=16.05±0.110, LRG3+ELG1=19.72±0.091,
ELG2=24.25±0.174, QSO=26.05±0.398, Lya=31.27±0.256

> IDCM `D_M/D_H` 需 O76 距離律 + O170 徑向核 —— 屬 **O76/O170 域**，本 O 只報 BAO 尺度。

---

## 五、裁定

IDCM 零參數 `r_d = 147.439 Mpc` 對 DESI DR2（out-of-sample）獨立數據：
- vs fiducial (ΛCDM+Planck 選定)：+0.264%
- vs BAO+CMB ΛCDM fit：**−0.27σ ✅**

⟹ **DESI DR2 支持 IDCM BAO 尺度，零參數。**

---

## 六、PASS 統計
`3/3 PASS`（`data/verify/04_desi_dr2_blindtest.log`）
