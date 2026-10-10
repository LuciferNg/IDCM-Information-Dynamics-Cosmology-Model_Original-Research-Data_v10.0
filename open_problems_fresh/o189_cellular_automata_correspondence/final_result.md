# O189 — IDCM ↔ 細胞自動機結構對應

## 狀態: 🟡 部分閉合（R1，2026-10-10；四路線 59/59 PASS）

## 結論
IDCM 88-site 鏈同 CA 家族**同格但不同 module**：生成元係 radius-1 線性局部規則（CHL 類、平移等變、Fourier 可對角化），但任何單一 ECA 都複製唔到其軌跡（256 窮舉零命中）；88-ring 動力學屬 class II⁺（準週期、等距、bounded），非 class IV；起手式「O222 已證通用計算」聲稱經審計為無據（REFUTED-as-written）。

## 關鍵公式
- H_Lap = 2I − S − S⁻¹（88×88；γ_n = 4sin²(πn/88), Σ=90）
- 傳播子 |ψ_j(t)| = |J_{|j−j₀|}(2t)|（Bessel，冇嚴格光錐）
- ω₁/ω₂ = 1/(2cos(π/88)) 無理（Niven）⟹ 準週期
- 環 ε-水平閉合 t=12；τ-map（τ≈14 lattice units）nnz = 88²

## 依賴
O222 → O231 → O189；τ = 1/ω_ring (O121)；譜 (O221)

## 密度基準
- N_search = 256（ECA 窮舉）, 盲測 min err 911/2112 > 0 ⟹ 零命中
- 正對照：唯一命中 [110]（finder 有效）
- 純代數恆等式（容量/譜/Bessel）: N_search = 1

---

## R2（2026-10-10，append 水位）

- **mod-q 商群投影 = 線性 CA**（scripts/05, 20/20）：π_q∘F = F_q∘π_q（q ∈ {2,3,5,7,13}）；q=2 ⟹ **F mod 2 = Rule 90**（2I≡0，零擬合）；負對照實矩陣 50/50 失敗
- **2-adic 合併**：γ₀=0 ↔ γ₄₄=4 (mod 2) ⟹ kernel(F mod 2) = span{1, (−1)^j}（nullity 2）；奇 p nullity 1
- **R-C 已回答**（coarse-grain 動力學兼容）；新殘餘：連續流 2-adic、period-248 閉式
- 累計 79 檢查（59+20），零放寬

---

## R3（2026-10-10，append 水位）

- **殘餘①閉合（scripts/06, 8/8）**：連續流 U(t) ∉ M₈₈(ℤ) for 所有非零代數 t（Lindemann＋Kronecker 定理）⟹ 連續時間冇模 q 商群（t=0 唯一）；商群唯一通道 = 生成元映射（R2）
- **殘餘②閉合（scripts/07, 7/7）**：period 248 = 8×31 = 2³(2⁵−1)——8 = Frobenius 重數 (x^11−1)^8；31 = ord(λ+λ⁻¹)（GF(2¹⁰)）；300 seeds lcm=248
- **R-D 閉合（scripts/08+08b）**：ε-CHL 律 r_ε(t) = 2t + C_eff(ln 1/ε)^{2/3} t^{1/3}，C_eff = 1.3106[1−(ln t)/(2ln 1/ε)]^{2/3}；**v1 預註冊 0/4 FAIL（原樣保留）**，v2 修正律 3/3
- 累計 97 PASS（59+20+18）＋ 4 記錄 FAIL；R-A（理論整體計算類）唯一剩低