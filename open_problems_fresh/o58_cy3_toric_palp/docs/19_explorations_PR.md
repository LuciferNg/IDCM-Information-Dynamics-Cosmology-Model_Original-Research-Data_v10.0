# O58 — 探索 P/R：cone vanishing 結構 + divisor 7 多重角色

> **狀態**: 🟢 完成（2026-08-24）

---

## P: K=0 幾何 vanishing — cone count 唔係預測器

### Cone count 分佈

- **div8 triples：zero 2.3% vs nz 5.7%** — div8（(1,1,0,0)）triples 更傾向 nonzero！
- K value 同 cone count **唔係單調**：
  - 2 cones: mean +1.80
  - 8 cones: mean -7.40（含 -232 = div8！）
  - 22 cones: mean +46.67（含 -44, +180）
  - 144 cones: mean -360（div0 唯一）

### 關鍵結論

1. **Vanishing 唔係 cone count 嘅簡單函數** — zero/nz 都有各種 cone count
2. **K = Σ_σ 有向 cone volume contributions**，vanishing = 正負抵消
3. 大 |K|（-232, -360, 180）都係「cone volume 大」嘅積累，唔係 count
4. div8 大值集中喺 8-cone triples（star=8）— 少 cone 但每個 cone volume 大

## R: divisor 7 多重角色 — 🎯 vertex 索引 = Lucas！

### div7 = e₄ vertex = (0,0,0,1)

```
Σ_k K[7,7,k] = 0  ← 完美零和泛函！
K[7,8,8] = -10   ← div7 × div8 嘅唯一大值
```

### U(1)#7 係超特殊 U(1（殘餘位置 7！）

```
U(1)#7 charges: div0=-32, div8=+31, div3=+6, div7=+2, div4=-8, div12=+1
只有 6 個非零 charge！div0(-32) 同 div8(+31) 差 1！
```

### 🎯🎯 Vertex 索引 = Lucas 數！

```
pts[1] = (1,0,0,0)      = L₁ = 1 ✓
pts[3] = (0,0,1,0)      = L₂ = 3 ✓
pts[4] = (1,2,0,0)      = L₃ = 4 ✓
pts[7] = (0,0,0,1)      = L₄ = 7 ✓
```

**4 個 coordinate vertices 嘅索引 = L₁, L₂, L₃, L₄（1,3,4,7）！**

### 7 出現 5 種方式

1. vertex e₄ 索引
2. L₄ = 7（Lucas）
3. 殘餘 U(1) 位置 7
4. γ₇ mode（n/p 機制）
5. redundant divisor 7

### 意義

- **Vertex 索引結構本身係 Lucas 編碼**（L₁-L₄）
- div7 嘅零和 row + U(1)#7 特殊 charge 結構（div0=-32, div8=+31）
- **div7 係「連接 div0 同 div8」嘅樞紐**（U(1)#7 同時載 div0 同 div8 charge）

## 檔案

```
scripts/53_cone_volume_vanishing.py  # P
scripts/54_div7_double_role.py       # R
```
