# O189 docs/05 — mod-q 商群投影 = 線性 CA（R2，R-C 攻堅）

> **2026-10-10 | R2 | 產物: `scripts/05_mod2_quotient.py`（20/20 PASS）、`data/05_mod2_quotient.json`、`logs/05_mod2_quotient.out`**

---

## 一、結論（先寫死）

🟢 **R-C 已回答（動力學兼容嘅粗粒化存在，且精確）**：
1. **mod-2 商群投影係 IDCM 生成元嘅精確粗粒化**：F = 2I − S − S⁻¹ 有整數矩陣 ⟹ 投影 π: ℤ^88 → F₂^88 係環同態 ⟹ `π(Fψ) = M·π(ψ)` 精確可交換（200 seeds 零例外），其中 **M = S + S⁻¹ ≡ Rule 90 環映射**——**零擬合，純由 F mod 2 推導**（2I ≡ 0）；
2. **普遍化**：對任意模 q ∈ {3,5,7,13}，mod-q 商群都係 ℤ/q 上嘅線性 CA（規則多項式 P_q(x) = 2 − x − x⁻¹）——intertwinement 50 seeds 各零例外；
3. **負對照**：隨機實矩陣（非整數）唔 intertine（50/50 不匹配）⟹ 「整數生成元」係呢個結構嘅本質條件；
4. **kernel 結構**：nullity(F mod 2) = 2（rank 86），kernel = span{1, (−1)^j}——**2-adic 合併**：γ₀ = 0 同 γ₄₄ = 4 都 ≡ 0 (mod 2) ⟹ mod-2 世界分唔到「零模 vs Nyquist 模」；奇數 p（p∤88）nullity = 1（只剩常數模）。

## 二、核心定理（結構推導，非擬合）

```
F := 2I − S − S⁻¹        (IDCM ring generator, integer matrix)
π_q: ℤ^88 → (ℤ/q)^88     (component-wise mod q, ring homomorphism)

定理 1 (intertwiner):    π_q ∘ F = F_q ∘ π_q ,  F_q := F mod q
定理 2 (q=2 還原):       F mod 2 = S + S⁻¹ = M  =  Rule-90 ring map
                         (since 2I ≡ 0 mod 2 — the identity term vanishes)
定理 3 (kernel 維數):    dim ker F_q = mult_gcd((x−1)² 型因子, x^88−1)
                         p=2 : (x+1)²【x^88−1 = (x^11−1)^8, (x+1) mult 8】
                               ⟹ nullity 2 = span{const, alternating}
                         p odd, p∤88 : (x−1)¹ ⟹ nullity 1 = {const}
```

**2-adic 合併嘅物理意義**：γ₀ = 0（平移模）同 γ₄₄ = 4（Nyquist 模，即 R1 已見嘅最高能模）喺 mod-2 底下**冇分別**——二元世界睇唔出連續世界「最低＝最高」嘅對跖結構。R1 scripts/02 量到 Rule-90 nullity 2 同 period 248 而家**有完整結構解釋**（商群 kernel ＋ gcd 重數），唔再係孤例。

## 三、結果表

| 檢查 | 值 | 狀態 |
|:---|:---|:---:|
| F 整數；F mod 2 == M（Rule 90） | 精確矩陣恆等 | 🟢 |
| F·1 = 0；F·(−1)^j = 4·(−1)^j | 精確整數 | 🟢 |
| 2-adic 合併 γ₀=0 ↔ γ₄₄=4 | 兩者 ≡ 0 (mod 2) | 🟢 |
| Intertwinement π(Fψ)=Mπ(ψ)（200 seeds） | 零例外 | 🟢 |
| 冪版本 π(F^kψ)=M^kπ(ψ)（k=2..8） | 零例外 | 🟢 |
| mod-q 普遍化（q=3,5,7,13，50 seeds 各） | 零例外 | 🟢 |
| **負對照**（隨機實矩陣） | 50/50 不匹配 | 🟢 |
| nullity mod 2 / 3 / 5 / 7 | **2 / 1 / 1 / 1** | 🟢 |
| kernel 基（mod 2） | {const, alternating} | 🟢 |
| Rule-90 軌道不變量 | preperiod 3–4, period **248**（兩 seeds 同） | 🟢 |
| 軌道級恆等（20 seeds × 64 steps） | bit-for-bit | 🟢 |

## 四、判讀

1. **R-C 嘅答案**：「quantize 之後演化仲係咪同一系統」——**係，喺商群意義下**：mod-q 商群演化 = ℤ/q 上嘅線性 CA（P_q(x) = 2 − x − x⁻¹），同原生成元**精確可交換**。q=2 係特殊而對跖嘅一員（identity 項消失 ⟹ Rule 90）。R1 嘅「容量恆等（q=2 ⟺ 88 bits）」而家升級做「**動力學恆等（q=2 ⟺ Rule 90 軌跡）**」。
2. **結構身份**：F = M + 2I —— IDCM 生成元 = Rule-90 映射 + 一個「偶部」。連續世界嘅 γ_n = 4sin²(πn/88)（R1 已用）落喺 mod-2 商群時，**只有 γ ≡ 0 (mod 2) 嘅模**先睇得到——gamma 空間嘅「偶數特徵值」正正係 kernel。
3. **誠實邊界**：unitary 連續流 U(t) = e^{−iFt} 嘅矩陣含 sin/cos（非整數）⟹ mod-2 intertwinement **唔延伸**到連續時間；本結果鎖定喺「生成元作為 CA map」嘅離散整數方案（R1 docs/02 已用同一定義 F 為 radius-1 規則）。連續流嘅 2-adic 行為（如 t 為某 dyadic 分數）未答——留 R-後續。

## 五、等價 / 模擬 / 類比（S3 判準）

- **等價**：🟢 喺商群層——π∘F = M∘π 精確（mod-2 世界嘅 IDCM ≅ Rule 90）；連續層唔等價（🟢 已界線）
- **模擬**：🟢 喺商群層係**投影**（surjective homomorphism），唔係模擬——比模擬更強（結構保真）
- **類比**：🟢 R1「Fourier module 不同」結論嘅深化版：ℂ-module → F₂-module 嘅商群投影係唯一精確「降維」通道

## 六、四道硬測試

① 自由度：零新參數（規則由生成元推導） ✅
② MC null：intertwinement 係恆等式（N_search = 1），200 seeds 為執行驗證非擬合 ✅
③ 可證偽：任何單一反例（window 內 mismatch）即倒 ✅
④ 結構剛性：負對照（隨機實矩陣 50/50 失敗）證明「整數性」係必要條件 ✅

## 七、殘餘（R2 後，同 O 續）

1. Unitary 連續流嘅 2-adic 行為（e^{−iFt} 非整數；dyadic-t 版本未答）——R-後續候選；
2. Rule-90 周期 248 嘅閉式（248 = 2³·31；與 ord(2 mod 88) 系 2^k 週期之關係未閉）；
3. R-A（理論整體計算類）、R-D（Bessel 尾一般律）照舊留 O189。

## 八、檔案

- `scripts/05_mod2_quotient.py`：20/20 PASS（GF(q) elimination 自包含，無 numpy 依賴外掛）
- `data/05_mod2_quotient.json`；`logs/05_mod2_quotient.out`
- 引用：R1 docs/02（生成元定義、Rule-90 數據）、docs/03（class II⁺）、O222（語義層）、Hedlund 1969（CA 代數）