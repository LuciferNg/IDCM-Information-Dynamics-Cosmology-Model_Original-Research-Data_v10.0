# G2 未來預註冊盲測 protocol 模板 — 102 號 (2026-10-17)

> **背景**: 87 號裁決「出路②未來真預註冊採納為 protocol（唔影響現狀）」；
> 102 號落實：56/58 兩輪盲測結構歸納成可重用 template 並驗證
> **Script**: `102_g2_protocol_template.py` → `data/102_g2_protocol_template.json`

---

## 結果: **13/13 PASS — G2 Protocol 模板落實**

## ✅ 56/58 兩輪全部符合 P1-P5

```
Round1 (56): B={55,68,74,81} C={46,56,62,73} seed=20261017 — 5/5 PASS
Round2 (58): B={54,67,75,80,83} C={52,59,82,84,86} seed=20261018 — 5/5 PASS
           (P1 域定義 / P2 候選 mirror 規則 / P3 對照 seed /
            P4 判準預註冊 / P5 剔除+無重疊)
C. 合併 n=18 (B 9 + C 9) — 59 號結果 B 3/9 = C 3/9 平手 ✅
```

## ★ G2 Future Protocol 模板（出路②落實, 可重用）

```
【用途】未來任何 magic label / 88-site 身份預測嘅盲測標準
【時序】LOCK commit → 唔可查身份 → 到期 UNLOCK → 再查
P1 域定義    被測域明確（如 k∈[45,87] 88-site 專屬高半側）
P2 候選生成   規則寫死（HALF mirror / Fib mirror / 任何結構規則）
             ⟹ B 集合（預言全部命中）
P3 對照生成   seed 固定 + 明文寫死 ⟹ C 集合（同 size 隨機對照）
P4 判準預註冊 sin(kπ/176) 或 4sin²(·) 喺「已閉合 md/scripts」出現
             — 禁 unlock 後先定義判準
P5 剔除規則   已消費候選剔除; 已已知 label 剔除; LOCK 後禁改 B/C
評估        超幾何檢驗（B vs C 命中數）+ 兩輪合併權力
            預先定義 PASS 閾值（5σ 或等效）; n 喺 LOCK 前聲明
失敗處理    合併 FAIL ⟹ 唔加第三輪（59 號先例）;
            改候選規則要全新 LOCK（唔 reuse 消費樣本）
================================================================
```

## ★ 意義

- 87 號「出路②採納」由口頭裁決變成可執行 template — G2 嘅唯一
  正向出路（未來真預註冊）而家有標準
- 56/58 兩輪示範本來就符合 P1-P5 — 程序一致性獲證
- 唔影響現狀: G2 維持 🔴規則 + 🟡存在性（唔會因 template 存在
  而升 PASS — 需要全新預註冊輪先可以）

## 檔案
```
102_g2_protocol_template.py
data/102_g2_protocol_template.json
```