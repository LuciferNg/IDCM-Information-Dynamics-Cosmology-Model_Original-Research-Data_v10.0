# O176 docs/02 — R1/P12′ 裁決: 最大 BLAGN 樣本 vs 種子先行軌跡 🟡→🔴(定量)/✅(結構)

> **日期**: 2026-09-13 · **Script**: `scripts/02_p12_trajectory_test.py` · **數據**: Kocevski+2025 (arXiv:2510.07376), Zhang+2026 (arXiv:2606.02773), Billand+2025 (A&A 706 A29)

## 一、樣本

**Kocevski+2025**: 70 BLAGN @ 3<z<7 (CEERS/JADES/RUBIES NIRSpec G395M), 43% LRD。
本 session parse 69 條 (表內 69, 論文自報 70 — 差 1 條, 不影響中位數):
M_BH = single-epoch virial (Hα/Hβ); M_* = 2D 表面亮度分解 + SED。
**Zhang+2026**: 98 光譜確認 LRD @ 3<z<7, 六深場, halo 質量由 clustering 推導。
**Billand+2025**: z<4 LRD 後代, Sérsic 分解 + 純恆星 SED。

## 二、P12′ 預言 vs 觀測 (Script 02 輸出)

```
P12':  ratio(t) = (1/306)(13.8 Gyr / t)^1.74      (O173 docs/18, α=1.74 兩點錨定)
```

| z bin | N (LRD) | obs 中位 | P12′ | dev (dex) |
|:---|:---:|:---:|:---:|:---:|
| 3-4 | 17 (4) | **0.17%** | 11.6% | **-1.84** |
| 4-5 | 16 (5) | 2.29% | 19.5% | -0.93 |
| 5-6 | 18 (14) | 6.84% | 30.2% | -0.64 |
| 6-7 | 8 (6) | 5.82% | 43.8% | -0.88 |

LRD-only 中位: z=3-4: 6.0% (N=4), z=4-5: 8.1% (N=5), z=5-6: 7.9% (N=14), z=6-7: 9.4% (N=6)
→ LRD-only dev: -0.28, -0.38, -0.58, -0.67 dex (全部偏低, 但 LRD 子集大致平 ~7.5%)

## 三、斜率 (α) 裁決

```
Paper medians:     z<4: 0.15%  |  z~5.5: 4%  |  z=6-7: 7%
factor z=3.5->6.5: obs 47x (paper forward-model: 197x = +2.294 dex ± 0.751, >3σ)
alpha_eff(obs)   = 5.04   vs   P12' alpha = 1.74
```

- **觀測下降比 P12′ 陡 3 倍** (α_eff≈5 vs 1.74) — 下降集中喺 z<4→z=6.5 段
- P12′ 嘅 (13.8/t)^1.74 形狀太溫和, 喺 z=3.5 預言 11.6% 但觀測已收斂到 ~0.15%

## 四、結構確認 (種子先行不變)

三條獨立線全部支持「核先、宿主遲到」結構:

1. **Zhang+2026 halo 增長**: LRD halo 由 z~7.5: log M_h≲10.1 → z~3.5: ~10^11.3
   (增長 >1 dex), 而 **BH 質量「little evolution」** → ratio 下降由宿主組裝驅動
2. **Zhang+2026 收斂**: z>4 過重, **z~3.5 向本地 M_*-M_BH 關係收斂** (>5σ 環境轉變)
3. **Billand+2025 後代**: z=3 後代核保持紅而緊湊, 外圍 250→600 pc 增長, M_*→10^10
   — **核心不滅, 宿主完成**; z=5-7 LRD 數密度 == z=3 post-LRD 數密度 (10^-4.15 Mpc⁻³)

→ 種子先行 (O173 P12 詮釋) 係正確結構; **錯嘅係 P12′ 定量曲線** (α=1.74 錨喺
極端對象 JADES GN 1146115 = 49%, 上包絡而非中位軌跡)。

## 五、裁決

| 項 | 裁決 |
|:---|:---|
| P12 種子先行結構 | ✅ **確認** (三線獨立) |
| P12′ 曲線 (α=1.74, 49% 錨) | 🔴 **定量否決** — 中位軌跡低 0.3-1.8 dex, 斜率陡 3× |
| 過重是否真實 | ✅ 50/70 高 1-2 dex (paper), intrinsic >3σ above local RV15 |
| z<4 收斂 | ✅ 0.15% ≈ local (RV15 0.1%) — P12′ 預言 11.6% 錯 |

## 六、誠實系統差

- M_BH ±1 dex 系統差 (virial vs electron scattering — 若唔係 virial, 過重部分消失)
- 宿主 M_* 可能低估 factor 60-70× (核光污染, Pacucci+2023) → ratio 高估
- z<4 樣本以 non-LRD 為主 (藍 AGN, 宿主高 1 dex) → all-sample 中位唔係 LRD 測量;
  LRD-only z=3-4 N=4 太少
- 選擇效應: 低 z LRD 更難認 (藍宿主稀釋 V-shape) → LRD-only ratio 可能高估

## 七、行動

1. **重新錨定 P12′** → 註冊新 O (O177): 中位軌跡 ratio(z=3.5)=0.15% ↔ ratio(z=6.5)=7%,
   α_eff≈5.0 (或 LRD-only 平軌 ~7.5%) — 需結構推導, 唔係兩點擬合
2. R1 宿主×306 直接測試: Kocevski+25 z~5.5 中位 4% → M_host = M_BH×(1/0.04) = 25×M_BH?
   唔係 — 呢個係 ratio, 唔係 M_BH×306 嘅宿主總質量。R1 嘅 M_host=M_BH×306 測試
   要 z=0 最終質量閉合: M_host,final = M_BH×306 仍未被 z>3 數據直接否決 (host 未完成)
3. 等 Ishikawa+26 IFU 分解宿主質量擴大樣本
