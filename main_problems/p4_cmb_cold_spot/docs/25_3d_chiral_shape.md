# 25 — 3D chiral shape 生成 (2026-10-20)

## 狀態: 🟢 已生成 — A₅ 60 節點網格 + 左右手 enantiomer 標定

## 背景

執行 register `cmb_cold_spot/3d-chiral-shape`（調律者 2026-10-11 定案, 僅註冊，
本 session 生成）：IDCM CMB 文檔大量但冇帶手性絕對形狀 3D model → 生成 3D 網格
model 帶左右手 enantiomer 標定（以 5.3402° 為標定尺）。**禁在未經盲測結構確認
前貼物理標籤**（遵守, 本記錄只做幾何手性標定, 無物理命名）。

## 輸入

- `data/a5_nodes.txt`（60 節點 RA/Dec, Planck SMICA 錨定 30/30）
- `data/faces.txt`（62 面 = 20Δ + 30□ + 12⬠, V60 E120 F62, χ=2）

## 判據（O213 scripts/10 全數值重現, docs/09 C5-C17）

| 量 | 計算值 | O213 期望 | 判定 |
|:--|:--|:--|:--|
| dev proper (I) | 0.000097° | <1e-3 | ✅ A₅=精確 I-軌道 |
| dev improper (−I) | 5.340202° | ~5.34 | ✅ 嚴格手性 |
| δ_m (seed→最近 2-fold 軸) | 2.670063° | 2.670063 | ✅ C8 |
| 對極 −v 距離 | 5.340200° | 2δ_m=5.3402 | ✅ C13/C15 |
| 手性偽標量 χ | −2.670063° | ±2.670063 | ✅ C16 |
| mirror(A₅) 殘餘 | 5.340200° | >0 (5.34) | ✅ C17 |
| |Sym| det 分佈 | 60 proper / 0 improper | I (60) 手性 | ✅ |

⟹ **A₅ = 嚴格手性, 偽標量 χ = −2.670063° 定義絕對 sense**（與 O213 R5 閉合一致）

## 輸出（data/）

- `rhombicosa_3d.obj` — reference（R, χ=−2.670063°）, V=60 E=120 F=62
- `rhombicosa_enantiomer_R.obj` — R enantiomer（同 reference）
- `rhombicosa_enantiomer_L.obj` — L enantiomer（mirror, χ=+2.670063°）
- `rhombicosa_3d_chirality.txt` — 六判據標定記錄
- `scripts/29_3d_chiral_model.py` — 生成 script（OBJ + chirality gauge, 可重現）

## 標定尺

5.3402° = 2δ_m = mirror residual = 對極距離 —— L/R 兩 enantiomer 之間嘅區分尺度。
χ ≠ 0 ⟹ 兩 sense 可區分（非約定）; 反射 ⟹ χ → −χ。

## 依賴

cmb_cold_spot → O213（R5 手性閉合）→ O223（|GeoAut|=60 chiral I）→ o185/IF4 → O7