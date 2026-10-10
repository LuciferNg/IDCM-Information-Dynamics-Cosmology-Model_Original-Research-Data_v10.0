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