# O73 — docs/21: 上下文壓縮交接 (Compaction Handoff)

> **日期**: 2026-09-25 (第 6 輪結束時)
> **用途**: 本 session 之上下文壓縮交接 — 令壓縮後之新 context 無需依賴舊上下文記憶即可接續
> **指令依據**: 用戶第 7 點「以上全部完成後執行本session的上下文壓縮」
> **前例**: O86 `docs/07_compaction_handoff.md` (2026-09-25)

---

## §1 session DB 身份 (壓縮後必須用 DB 核對，勿信摘要內之 id)

```text
本 session DB id 沿革:
  20260924_235439_90d5cb   (09-24 23:44 → 09-25 13:03)  ← 壓縮摘要攜帶此 id
  → rollover →
  20260925_130605_9f896f   (09-25 13:03 → ...)          ← DB 現行 id (title「執行O73更改參數名稱」)

查詢範式 (唯讀):
  sqlite3 "file:$HOME/.hermes/state.db?mode=ro" \
    "SELECT id,role,substr(content,1,400) FROM messages
     WHERE session_id='20260925_130605_9f896f' ORDER BY id DESC LIMIT 40"

⚠️ 只用 '%O73%' / '%ω_ring%' 會命中 621 個 session (通用詞污染) —
   必須用 O73 專屬 token: o73_h0_first_principles / verify_all / O5-x / docs/16_o215 / scripts/2x
```

## §2 專案位置 (注意 .0)

```text
專案根: /home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/     ← 有 ".0"!
O73:    open_problems_fresh/o73_h0_first_principles/
⚠️ /home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh 係空殼 — 寫入會靜默丟失
⚠️ background shell 之 python3 = miniforge 空環境 (缺 scipy/mpmath) → 一律用 /usr/bin/python3
```

## §3 本輪 (第 6 輪) 已完成 — commit `38ba444`

```text
✅ 1. 驗證: 32 scripts 全 exit=0 (25a v1 存檔 exit=1 = 預期, 41/8);
        verify_all 206/206; scripts/25 99/99 + 4 NOTE; 26 13/13; 27 19/19; 28 13/13; 29 9/9
✅ 2. session-DB 對帳 (用戶第 2 點): 全庫普查 → 17 關鍵 session → 248 寫入事件 / 44 檔 →
        1,327 訊息 → 431 token → 182 未命中 → 真缺口 2 項 → 補記 docs/14 §13.2
        ★ 補記 1: 45/ω_ring = 0.61991986 (冇身份) + R_world×C_energy = 91.7775 (冇身份)
        ★ 補記 2: 55/56 = 0.9821428571 vs Planck 0.981916 → dev +0.0231035% (0.73σ)
✅ 3. 時序完整性: 248 事件有序; git 逐 commit 無回溯重寫; 歷史值原文保留 (ka 1.47e40 / docs/02 H1 / P7)
        ★ 範圍紀律: 外部 (O169 / O215) 對 O73 之寫入 100% 限 SESSION_START.md (append-only)
✅ 4. 未閉合項檢查: SESSION_START / 01_problem_record / README / final_result 全檢 (見 §4–§6)
        時序索引: 01_problem_record rows 1–122 (第 6 輪 = 111–122)
✅ 5. final_result.md 依 RESULT_TEMPLATE 重建 (狀態/結論/關鍵公式/開放項/驗證/依賴/檔案)
✅ 7. 本檔 (docs/21) = 壓縮交接; 開放問題清單見 §4–§6
```

## §4 O73 尚未閉合之項 (本 O 側)

```text
本 O 自身推導鏈: 零缺口 🟢 (verify_all 206/206)

🟡 O5-2 剩餘 m 簡併      m ∈ {5,6,7}; m=6=2N_gen 首選 (m*=6.20); 需 SH0ES 高 z rung / DESI z<0.5 / CMB-S4
🟡 O5-4 BBN 鎖語義       本 O 已落註 (docs/04 §6/§7); 待上游 (O215/O163/O14/O38/bbn) 採納
🟡 命名規範 Ω→f          數值已同步 (f_baryon = 1/20, f_dm = 4/15); 待用戶確認 f_* 前綴
🔴 c 之絕對值            仍需 1 個有量綱錨 (維度定理 — 任何理論皆同; 誠實邊界, 非可解缺口)
🔴 上層 README O73 行     stale (見 §6)
```

## §5 其他 session 交接到 O73 之開放問題 (全庫掃描結果)

| 來源 O | 事項 | 狀態 | 本 O 處置 |
|:-------|:-----|:-----|:---------|
| **O215** (`65e2ebd` 09-22) | Ω_b 版本統一 (19/450 vs 3/60) | ✅ **已判定** | `docs/16` (scripts/27) → `Ω_b = 3/60 = 1/20`; 框架級採納待用戶 |
| **O169** (`f816ca1` 09-24) | E(0) = 1 低 ℓ 修正形式 | ✅ **已重驗** | `docs/18` (scripts/26 13/13); 剩 m 簡併 🟡 |
| **O170** (09-23) | N4: h_lad stale + SH0ES 匹配失效 | ✅ **已交收** | 交 h0_tension (`09_o170_n4_handoff.md`); 翻譯層分析 `10_translation_layer_analysis.md`; 已回寫 O169 |
| **O212** (09-24) | O212-3 Ω_b 版本統一 | ✅ **已判定** | 同 O5-1 (`docs/16`) |
| **O212** (09-24) | H5: BBN 鎖 Ω_b 敏感度重算 | ✅ **已重算** | `docs/17` (scripts/28) — 19/450 → 72.7143; 3/60 → 66.8199 |
| **O212** (09-24) | O212-1 錨之絕對值 / 重力階層 m_p/m_Pl | 🔴 **未處理** | 去向 = **O86** (非 O73); 本 O §7 維度定理已界定其為「1 dof 錨」 |
| **O203** (09-18) | 「O73 等數據 gated 預言」交回 O73 session | 🟡 **已收列** | = `docs/19` 等數據項 (H7 P1–P5); 無本 O 側動作 |
| **O213** (09-24) | R9 環尺度 R_world 之絕對值 | 🔴 **未處理** | 去向 = O86 ↔ O212; 本 O `docs/14` §9.3 已界定 (sector dof = 1) |
| **O99** (09-23) | docs/04 §3 色散需求降級 + ka 標籤 | ✅ **已註** | `docs/15` §6.1 (1 TeV = 1.47e43) |
| **O204** (09-18) | POINTER ×3 (m_ρ² / W₀ / τ_hop 約定) | ✅ **已吸收** | `docs/15` §1.1; 三 POINTER 原文保留於 root |
| **O171** (09-17) | R_world 分解閉合 (互相引用) | ✅ **閉環** | `docs/14` §1 (O171 docs/29 ↔ O73 docs/14) |
| **O75** (09-17) | 命名收編 N1–N6 (O203 提交) | 🟡 **已收列** | 數值同步於 `docs/06` §3.2; 待用戶確認前綴 |

## §6 待用戶裁決 (2 項 — 本輪未動手)

```text
① 框架級採納 Ω_b = 1/20 (影響 O215 / O163 / O14 / O38 / bbn)
   - O215/O163: 正式採納 + docs/04 BBN 鎖值同步 (72.73 → 66.888)
   - O38/O34:   m_7 錨定裁定 (裸 72.59 → 13.8002 MeV; CMB 67.4 → 13.2984, −3.64%)
   - O14:       φ-form 鏈 (2φ⁻¹/(5(φ⁴−1))) 正式撤回 (O163 已用 CMB χ²=32.9 證偽)
   - bbn:       Ω_b = 1/20 下 BBN 豐度預言重算
② 上層 README.md O73 行 stale (open_problems_fresh/README.md 第 12 行)
   - 仍寫「BBN 鎖定 → ω_ring = 72.73」/「Ω_b = 19/450」/「剩餘 = 等數據 + O75」
   - ⚠️ 該檔在 O73 目錄以外 → 依紀律本輪未寫入
   - 附: O73 目錄自身無 README.md (210 個 O 目錄中僅 24 個有 ⇒ 非強制慣例)
```

## §7 復原指引 (壓縮後第一步)

```text
1. 讀本檔 (docs/21) + docs/19 (剩餘總表) + docs/20 (DB 對帳) → 即掌握全貌
2. 驗證現狀: cd $O73 && /usr/bin/python3 scripts/verify_all.py   → 應 206/206 PASS
3. 未閉合項: 讀 final_result.md §開放項 (已依 RESULT_TEMPLATE 重建)
4. 如需 DB 核對: 用 §1 之 sqlite 範式 (唯讀副本, 勿直接寫 state.db)
5. 寫入紀律: 只可寫 O73 目錄; 其他 O 只可 append SESSION_START.md
```
