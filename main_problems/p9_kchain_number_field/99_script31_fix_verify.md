# 31 號 script galois_fixed 修正落實 — 99 號 (2026-10-17)

> **背景**: 50 號 B4 審計發現 31 script `galois_fixed()` 用錯條件
> `(a·d)%176 ∈ {d, 176−d}` = ±ω_d 鏡像 (σ=反粒子)，唔係真正固定。
> 附註已寫「script 要修正先重用」——本輪落實。
> **Script**: `99_script31_fix_verify.py` → `data/99_script31_fix_verify.json`

---

## 結果: **9/9 PASS — 31 號 script bug 正式修正**

## ★ 修正內容

```
31 script galois_fixed() 舊條件:
  (a·d) mod 176 ∈ {d, 176−d}   ⟺ σ_a(ω_d) = ±ω_d (縮放鏡像)
  輸出 [1,175] — σ_175 = 反粒子 (ω→−ω), 唔係固定!
正確條件 (50 號 B4):
  a·d ≡ d (mod 176)            sin 同角 → σ_a(ω_d)=ω_d
  d(a+1) ≡ 88 (mod 176)        sin 互補: sin(πx/88)=sin(π(88−x)/88)
  輸出 [1,87] — σ_87 = Z₂ 固定奇數
```

## 驗證

```
A. galois_fixed(3/7/29) = [1,87] 全部 ✅
   sin 值獨立驗證: σ_1(ω_d)=ω_d ✓ σ_87(ω_d)=ω_d ✓ (mpmath 級精確)
B. 31 md 正文一致 (d=3/7/29 → a={1,87}) ✅
C. json 結構完整 (其他 T1-T8 輸出保留) ✅
D. json 舊 [1,175] 錯誤值已被取代 ✅
```

## ★ 意義

- 50 號「script 要修正先重用」開放項正式封印
- 修正係**落實** 50 號審計判決，唔係新審計
- 結論不變: 3/7/29 全同 ⟹ σ_87 固定奇數 = Z₂ 奇偶選擇,
  唔係 7 特有 (31 md 原結論穩健)

## 檔案
```
99_script31_fix_verify.py
data/99_script31_fix_verify.json
31_matrix_fixed_point.py (已修正)  + data/31_matrix_fixed_point.json (已更新)
備份: /tmp/31_matrix_fixed_point.py.bak
```