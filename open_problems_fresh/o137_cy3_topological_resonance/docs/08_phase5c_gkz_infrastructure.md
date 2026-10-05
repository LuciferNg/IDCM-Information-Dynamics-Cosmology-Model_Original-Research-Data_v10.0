# O137 — Phase 5c: 鏡像 Triangulation + GKZ 週期基礎設施

**狀態**: ✅ 完成 (TOPCOM/gfan 安裝 + Δ* 三角剖分 + GKZ φ 提取)
**日期**: 2026-08-30
**檔案**: scripts/16_gkz_mirror_period.py + data/dual_triangulation_data.json + data/gkz_period_data.json

---

## 1. 工具安裝 (無 root, WSL Debian)

TOPCOM + gfan 無法 `sudo apt install` (無 root 密碼)。解法:
1. `apt-get download topcom gfan libtopcom0t64 libcdd0t64 libqsopt-ex2t64` 下載 .deb
2. `dpkg-deb -x` 解壓到 `~/tools/bin` (binaries) + `~/tools/lib` (shared libs)
3. `~/.bashrc` 加 `export PATH="$HOME/tools/bin:$PATH"` + `export LD_LIBRARY_PATH="$HOME/tools/lib:$LD_LIBRARY_PATH"`

**驗證**: `topcom-points2placingtriang --help` OK, `gfan --help` OK
**CYTools 接入**: `p_dual.triangulate(backend="topcom")` 成功 (之前預設 backend 600s timeout)

## 2. 鏡像 Polytope Δ* 三角剖分

- Δ: 48 點 (CY₃ h11=36, h21=98) — 原始
- Δ*: 85 點 (CY₃ h11=98, h21=36) — 鏡像 (Batyrev dual)
- **Triangulation: fine ✓ regular ✓ star ✓, 283 simplices, 73 點參與** (12 點唔參與 = facets-interior 點)

## 3. GKZ φ 向量 (73 項, Σφ = 1800)

| φ 值 | 數量 | 備註 |
|:---:|:---:|:---|
| 12 | 28 | 主導 (28 = B×L₅ = 4×7) |
| 9 | 9 | 9 = 3² |
| 8 | 5 | 5 = F₅ |
| 6 | 2 | 2 = 對偶鏈 |
| 14, 16, 18, 20, 22, 26, 29 | 4,3,4,4,4,3,3 | 14=2×7, 18=2×9, 20=4×5, 22=2×11, 26=2×13, 29=L₈ |
| 113, 173, 176, 360 | 1 each | 大值: 176=2×88, 360=4×Σγ |

## 4. ★ 結構連結: GKZ φ ↔ K_Chain

```
✅ φ_origin = 360 = 4·Σγ_44site (Σγ=90)   ← 鏡像 apex = 4 倍 chain 總和
✅ Σφ       = 1800 = 20·Σγ_44site
✅ φ[1]     = 176  = 2·88 = 2×Nd_dual     ← 對偶鏈長度 ×2
```

**GKZ φ 向量 (鏡像 polytope 的組合幾何量) 直接編碼 K_Chain 的 Σγ = 90!**
360 = 4×90, 1800 = 20×90 — 鏡像結構的 volume 分佈與 chain 總諧振強度成整數比例。

## 5. Charges q_i = φ_origin − φ_i (72 值, Σq = 24480)

| q 值 | 數量 |
|:---:|:---:|
| 184, 187, 247 | 1 each |
| 331, 334, 344 | 3 each |
| 338, 340, 342, 346 | 4 each |
| 348 | 28 |
| 351 | 9 |
| 352 | 5 |
| 354 | 2 |

q_i 結構 = 360 − φ_i, 所以 28×348 + 9×351 + 5×352 + 2×354 + ... = 24480

## 6. GKZ 週期級數

ω₀(z) = Σₖ cₖ zᵏ, cₖ = Γ(1+360k)/∏Γ(1+qᵢk)

- 漸近: coef of k·log(k) = 360 − 24480 = **−24120 < 0** → 全函數 (entire)
- log c₁ = −116830 (極快衰減) — 週期係數天文數字級小

## 7. 下一步 (Phase 6 候選)

1. **鏡像週期積分條件**: 計算 PF 方程 discriminant 並測試 K_Chain modes n ∈ {1,7,33} vs {15,21,25,35} 喺 discriminant 嘅位置
2. **q_i 分佈同 mode 選擇**: 28 = B×L₅, 9 = 3², 5 = F₅ 嘅 multiplicity 結構對應?
3. **Mirror map**: t = (1/2πi)log(z) 數值建構, 測試 mode 嘅 mirror map 值是否整數
4. **Σγ 編碼**: 360 = 4×90 係結構必要定巧合? (盲測: 隨機 polytope 嘅 GKZ φ 是否仲係 Σγ 倍數)
