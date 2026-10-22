#!/usr/bin/env python3
"""
批量建立 O76-O87 新 O 系列 (O72 未完成工作移交)
"""
import os

BASE = os.path.expanduser("~/Projects/IDCM/IDCM-v10.0/open_problems_fresh")

# (編號, slug, 標題, 來源, 前置, 定位, 問題, 優先度)
SERIES = [
    ("76", "z_redshift_translation", "z 紅移翻譯 (非膨脹紅移)",
     "O72 H6 (docs/12, 19)",
     "O51 (D_app), O73 (ω_ring), O72 (docs/01-19)",
     "IDCM 冇膨脹 → z 紅移點嚟? 建立 D_app(ℓ) ↔ 距離-紅移關係, 用 LCDM 語言解釋全部紅移觀測 (超新星, BAO, CMB)。",
     "★★★"),
    ("77", "occam_deep", "Occam 對照深化",
     "O72 H7 (docs/04, 12)",
     "O73 (ω_ring 鎖定), O72 (docs/04 Occam 表)",
     "ΛCDM 6 參數 ↔ IDCM 結構完整對照: 每個參數嘅 IDCM 對應/取代/缺口。加入 H1-H5 發現 (ω_ring 鎖定, 44 系樽頸)。",
     "★★"),
    ("78", "observer_reframing", "觀察者 re-framing (90/88 形而上學?)",
     "O72 H8 (docs/12)",
     "O72 (docs/13 H2 平凡發現)",
     "「世界/觀察者 90/88」係咪形而上學? 90/88 已證係平凡奇偶性質 (H2), re-framing 意義下降 — 純數學 re-framing (冇「觀察者」字眼) 定係放棄?",
     "★★"),
    ("79", "postdiction_vs_prediction", "post-diction vs blind prediction",
     "O72 H9 (docs/06, 12)",
     "O73 (7 預言), O72 (docs/06)",
     "所有 IDCM 閉合係 post-diction 定 blind prediction? 完整清單: 每個閉合係「閉合前已有預言」定「閉合後貼標籤」? O73 7 預言 (P1-P7) 嘅真實預言性。",
     "★★"),
    ("80", "wfield_lagrangian", "W-field Lagrangian (L_W ↔ QFT)",
     "O72 H10 (docs/12, 17, 18)",
     "O39 (SSB 勢), O62 (V_Λ), O72 (docs/17-18)",
     "W-field 嘅完整 Lagrangian: 由 O39 SSB 勢 V(W)=−μ²|W|²+λ|W|⁴ 出發, 建立 free+interaction 完整 QFT 語言 (kinetic, potential, gauge?)。",
     "★★"),
    ("81", "eom_unification", "EOM 統一 (free 定 sine-Gordon?)",
     "O72 場論學家 Q3 (docs/17)",
     "O39 (SSB), 調律者框架 (sine-Gordon), O72 (docs/17)",
     "場論學家 Q3: 兩個框架並存 (free lattice scalar + sine-Gordon 調律者), 冇統一 Lagrangian。統一 EOM/勢: free 定 sine-Gordon? 定係兩者不同極限?",
     "★★★"),
    ("82", "mass_generation", "質量生成翻譯 (γ_k ↔ 粒子質量, 1-loop 自能)",
     "O72 場論學家 Q8 (docs/17, 18)",
     "O54 (SM 質量閉合), O36 (質量生成 = 二階自能), O72 (docs/18)",
     "場論學家 Q8: 質量喺 QFT 係 Yukawa/Higgs 產生, γ_k 係 ring 模式頻率, 點解等於粒子質量? 需要完整 1-loop 自能計算 Σ(p), 由 Lagrangian 推導 m_e/m_μ/m_τ。",
     "★★★"),
    ("83", "correlator_cmb", "Correlator ⟨φφ⟩ ↔ C_ℓ",
     "O72 場論學家 Q5 (docs/17, 18)",
     "cmb_cl (C_ℓ 閉合), O72 (docs/18)",
     "場論學家 Q5: 譜 ≠ correlator。定義 ⟨φ(x)φ(y)⟩ (2-point function), 由 Lagrangian 推導 CMB C_ℓ, 唔係拼湊。",
     "★★★"),
    ("84", "vacuum_energy_unified", "真空能統一 (90/88/283.0821) + renormalization",
     "O72 場論學家 Q7 (docs/17)",
     "O39 (⟨W⟩²=61.5), O62 (V_Λ=283.0821), O72 (docs/17)",
     "場論學家 Q7: 90 (44-site 譜和), 88/90 (88-site 奇偶), 283.0821 (V_Λ), −61.5 (V_min) — 四個「能量」冇統一框架。建立 renormalization scheme, 統一真空能。",
     "★★"),
    ("85", "su12_breaking", "SU(12) → SM breaking chain",
     "O72 場論學家 Q6 (docs/17, 18)",
     "O59 (su(12)), O54 (CKM/PMNS), O53 (CY₃)",
     "場論學家 Q6: SU(12) 係 global 定 gauge? 冇 gauge boson。建立 SU(12) → SU(3)×SU(2)×U(1) breaking chain, gauge boson 質量 (Higgs 機制)。",
     "★★★"),
    ("86", "sm_gr_coupling", "SM × IDCM × GR 耦合 Lagrangian",
     "O72 場論學家 Q10 (docs/17, 18)",
     "O39 (SSB), O73 (ω_ring), O62 (V_Λ)",
     "場論學家 Q10 (致命): 冇 SM × IDCM × GR 耦合。建立 metric coupling, 定義 spacetime 身份 (FLRW 係 approximation?)。z 紅移 (O76) 係前置。",
     "★★★"),
    ("87", "mode_1496_physics", "1496 模式物理 (或者放棄)",
     "O72 H5 延伸 (docs/16)",
     "O61 (通量子 66/90), O72 (docs/16)",
     "1496 = 44×34 複合模式冇粒子譜對應 (SM ~100)。搵物理 (計算/通信?) 或者正式放棄「1496 有物理」claim。",
     "★★"),
]

def mkdirs(path):
    for sub in ["docs", "scripts", "data"]:
        os.makedirs(os.path.join(path, sub), exist_ok=True)

def write_problem_record(num, slug, title, source, prereq, positioning, prio):
    question = positioning  # 定位已包含問題描述
    return f"""# O{num} — {title}

> **日期**: 2026-08-25
> **狀態**: 🔴 **已註冊 — 待攻堅 (O72 移交)**
> **來源**: {source}
> **前置**: {prereq}
> **定位**: {positioning}
> **優先度**: {prio}

---

## 一、問題

{question}

## 二、已知結構 (O72 已確立)

```
🟢 參考 O72 docs (見前置)
```

## 三、攻擊路線

```
1. 待攻堅 (由 O72 SESSION_START 移交)
```

## 四、驗證標準

```
✅ 待建立
```

## 五、狀態

```
🔴 已註冊 — 待攻堅
```
"""

def write_session_start(num, slug, title):
    return f"""# O{num} — SESSION START

> **Session**: 2026-08-25 (由 O72 移交)
> **狀態**: 🔴 已註冊 — 待攻堅

---

## 定位

{title} — 由 O72 未完成工作移交。

## 交接點

```
來源: O72 docs/19_unfinished_inventory.md
狀態: 🔴 未開始
```

## 相關資源

```
- O72 docs/19_unfinished_inventory.md — 移交清單
- O72 docs/01-18 — 背景
```
"""

created = []
for num, slug, title, source, prereq, positioning, prio in SERIES:
    path = os.path.join(BASE, f"o{num}_{slug}")
    mkdirs(path)
    write_problem_record(
        num, slug, title, source, prereq, positioning, prio
    )
    with open(os.path.join(path, "docs/01_problem_record.md"), "w") as f:
        f.write(write_problem_record(num, slug, title, source, prereq, positioning, prio))
    with open(os.path.join(path, "SESSION_START.md"), "w") as f:
        f.write(write_session_start(num, slug, title))
    created.append(f"o{num}_{slug}")

print(f"✅ 建立 {len(created)} 個 O 系列:")
for c in created:
    print(f"  {c}")
