# O237 docs/04 — U2 攻堅記錄: F_proj 幾何生成 blind 測試（5 族負結果，收窄空間）

> **日期**: 2026-10-07 · **狀態**: 🔴 維持開放（docs/01 原判；本輪**收窄**咗候選空間）
> **腳本**: `scripts/03_fproj_generation_probe.py`（5/5 PASS）+ `scripts/04_fproj_kappa_projection.py`（1/1 PASS）
> **邊界**: 禁 C_f 池匹配（O208/O233/O235 三面負）；A5 合法 modes（O206 第十輪）；t 已歸 VEV 唔喺 C_f 範圍

---

## 一、A5 C_f 真值（O206 第十輪，本輪重現）

```
C_f = m / (M₀·γ_n),   M₀ = 27.9009 MeV
  e (n= 1): 3.5941      u (n= 2):  3.8029     d (n= 3):  3.6620
  s (n= 4): 41.3208     μ (n= 5): 30.0309     c (n= 7): 186.0606
  τ (n= 9): 159.6437    b (n=11): 255.7518
C_e 錨 = 3.5941 vs L₆/F₅ = 3.6  → dev −0.163% (O120 盲測接受)
```

## 二、五個 blind 候選族測試結果

| # | 候選族 | 形式 | 結果 |
|:-:|:-------|:-----|:-----|
| 1 | **γ 冪律** | C_f(p;n) = (γ_n/γ₁)^p·C_e | ❌ 最佳單一 p=0.3，max dev 94.17%（scripts/02 §2 重現 O206 之「非 γ 冪律」） |
| 2 | **2-adic 阻抗 Z(n)** | Z(n) = B^v₂(n) | ❌ C_f/Z 非常數（0.95 → 186），v₂ 分層冇對應 |
| 3 | **Φ=9 目錄 × 整數** | C_f ∈ Φ·{1..8} 或 Φ/{2..8} | ❌ 1% 窗命中率隨機 98.75%（目錄太密冇判別力）；**精確窗 0/8**（O206 第十輪權威，本輪重現） |
| 4 | **κ-三次不變量** | I₃(n) = 18·Σᵢ eᵢ(n)³, eᵢ(n)=2sin(nπi/88) | ❌ I₃/C_f spread 36.9×，冇單一標度 |
| 5 | **O145 sector v₂-mean** | C_f(φ-sector) = Σv₂(G)/\|G\| | ❌ 只有 G8 → 18/5 = C_e 成立（O145 錨，本輪重現）；G6 → 3/2、G9 → 0、G12 → 20/28=5/7，皆唔匹配 A5 C_f |

**結論**：現有 κ/Φ/2-adic 結構嘅「最自然」投影形式**冇一個**一次過生成 8 個 A5 C_f。C_e = 18/5 仍然係**唯一**有幾何生成嘅 F_proj（O145 2-adic + O120 盲測）。U2 維持 🔴。

## 三、「近命中」警告（唔可以當證據）

測試中意外出現嘅近命中：C_b = 255.7518 ≈ 256 = B⁴（dev 0.10%）、C_μ = 30.0309 ≈ 30 = 5×6（dev 0.10%）、
C_c = 186.0606 ≈ 31×6（dev 0.03%）。**全部係 C_f 池匹配陷阱**（O208 禁區）：三個近命中冇共同生成規則、
冇 operator identity、純粹係目錄密度效應（1% 窗隨機命中率 98.75% 已證明）。**明確列為 coincidence，禁引用**。

## 四、剩餘候選（下一步，唔喺本 O 推——docs/01 邊界；register handoff）

1. **R1 b**: κ 張量嘅非對角結構（κ_ijk = 18·δ_ijδ_jk 以外有冇 CY₃ 幾何修正項）——本輪只測咗對角 I₉
2. **R2**: φ=9 世代混合扇區 2-adic 正交（Z=0 恆等）接 C_f：O145 已證正交係恆等，但「正交 ⇒ 質量投影」尚未接線
3. **R3**: 2-adic 阻抗共振 O145 方法嘅 A5 版（Z(G_φ, n) 對 A5 mode 嘅實部模式）——本輪 Z=B^v² 版本已負；複阻抗 Z(G8,n) 未試

## 五、對 docs/01 嘅更新建議

- §三 U2「F_proj (15.5/37/13/33/44/1554)」**已過時**：O206 第十輪（10-06）已判 CSSG-v3 及 O64 嘅 assignment 非法（5/9），
  現行主 scheme = A5（O137 R22），C_f 值見 §一。本檔以 A5 值為準（append-only，docs/01 原文不變）。

## 六、檔案

```
scripts/03_fproj_generation_probe.py    5/5 PASS
logs/03_fproj_generation_probe.out
scripts/04_fproj_kappa_projection.py    1/1 PASS
logs/04_fproj_kappa_projection.out
scripts/05_fproj_impedance_probe.py     2/2 PASS   ← R3 補試
logs/05_fproj_impedance_probe.out
```

---

## 七、R3 補試（append-only，2026-10-07）

`scripts/05_fproj_impedance_probe.py`（2/2 PASS）——測試 docs/01 指定候選路線之 R3（O145 複阻抗 Z(G,n)）：

- Z(G8/G6/G9/G12, n) = Σ_{a∈G} exp(2πi·n·a/88)·v₂(a) 對 A5 mode n ∈ {1,2,3,4,5,7,9,11} 嘅實部/模 vs C_f
- Re Z(G8,n)/C_f spread 116×（比例性唔成立；注意 ReZ8 有正負，故用 |Re| spread）
- 全扇區相關 max |corr| = 0.6197（< 0.9，冇線性結構）
- ⟹ **R3 複阻抗家族亦為負**。U2 候選已全數清空：γ 冪律 / Z(n)=B^v2 / Φ×k / κ-三次不變量 / sector v2-mean / 複阻抗——C_e = Σv₂(G8)/|G8| = 18/5 仍係唯一由 2-adic 扇區生成嘅 F_proj。
- 剩餘唯一理論出口：R1b（κ_ijk=18·I₉ 嘅非對角修正）——需要新幾何輸入（O206 第十輪已定：C_f 生成器開放，等新幾何）。
- **U2 總結：🔴 維持開放**（docs/04 §五 一致；所有候選路線已負，等新幾何輸入）。

---

## 八、R1b-A5 判死定理（append-only，2026-10-07 續推）

`scripts/08_a5_geometry_no_go.py`（7/7 PASS）——**A₅ 節點幾何投影家族整族判死**（承接 O143 docs/08）：

- **頂點傳遞**：A₅ 60 節點圖 |Aut(G)|=120=I_h，I 軌道 = 60、I_h 軌道 = 60（單一軌道，幾何層＋組合層都係）
- **圖論量全部 node-agnostic**：度數 = 4、三角形數 = 1、WL 色 node9=node20（7/7 PASS）
- **距離分類 15 類 = 噪聲，唔係結構**：a5_nodes 原始座標有 0.075° 噪聲（O143 scripts/21 已知）；用冷斑方向經手性 I 群生成精確無噪聲軌道，距離包 = 1 類 ⟹ 任何「A₅ 節點距離/角度做投影」包含嘅 mode-依賴 **100% 係噪聲**
- **定理**：Aut(G)-invariant A₅ 幾何量 ⟹ 全粒子同值 ⟹ 同 8 個互異 F_proj（O206 第十輪）矛盾。唔係「未試夠」，係結構不可能
- **唯一出路**：非 Aut-invariant 輸入（sky-side 場）——但質量係內在結構，唔適用
- 三重封死：頂點傳遞 + O182（逐點鏈索引已否決）＋ O219（pt index = mode index 已否決）

**⟹ U2 候選空間再收窄**：γ 冪律 / Z(n) / Φ×k / κ-三次 / sector v2-mean / 複阻抗 / **A₅ 幾何** 全部判死。
剩餘唯一未封：**κ 非對角修正**——需真正 CY₃ 幾何（O70 dijk_intersection / Kähler cone 層，未接 F_proj），唔係 A₅ 圖。