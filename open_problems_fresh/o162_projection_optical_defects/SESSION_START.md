# SESSION_START — O162 開項

> **日期**: 2026-09-08 (HKT)
> **狀態**: 開項 bootstrap — 01_problem_record.md 已建立, 未有推導
> **背景**: 用戶指令「開新O162, 物質投影時的光學缺陷（紫邊、失焦、銳化、移位等）」

## 會話起點快照 (2026-09-08)

- **問題**: 世界 (even) → 觀察者 (odd) 投影作為成像系統; 光學缺陷目錄
  (紫邊/失焦/銳化/移位) ↔ IDCM 結構量一一映射
- **研究問題**: R1 OTF/PSF, R2 紫邊/色差, R3 失焦, R4 銳化/振鈴,
  R5 移位, R6 調律者 = 光學校正?
- **錨點**: S1 (O159 BVP/μ²), S2 (O149 v_g), S3 (O157 γ₈₈), S4 (O156 尺度家),
  S5 (O161 相位), S6 (O140 FSR), S7 (44-mode chain)
- **目錄**: `open_problems_fresh/o162_projection_optical_defects/`
  (01_problem_record.md 已寫; docs/ scripts/ data/ 待推導時建立)

## 反幻覺鐵律 (開項即寫)

1. 光學詞彙只係翻譯層 — 每個缺陷必須 trace 到譜量先算閉合
2. 紫邊唔等於電磁色散 — 冇波長, 只有模式 index k
3. 量→譜慣例: 176-Laplacian 主譜 / 44-mode v_g = c·cos(nπ/88)
4. Gibbs 8.95% 未核身份前唔當閉合
5. φ-power 禁數值分解; 失焦 N 只喺框架尺度集
6. 0.1222° (O156) 只可以重新詮釋, 唔可以重新擬合
