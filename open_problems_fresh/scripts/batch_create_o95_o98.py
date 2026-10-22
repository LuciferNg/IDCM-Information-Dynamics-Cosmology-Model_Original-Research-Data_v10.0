#!/usr/bin/env python3
"""
批量建立 O95-O98 新 O 系列 (可疑點 #1, #2, #3, #8)
"""
import os

BASE = os.path.expanduser("~/Projects/IDCM/IDCM-v10.0/open_problems_fresh")

SERIES = [
    ("95", "44_necessity", "44 必然性 (指數 3,5 唯一性證明)",
     "O72 可疑點 #1 (★★★)", "O51, O72 H3 (docs/14), O56, O59",
     "O51 scripts/88 話「五層推導閉合」但係「44 符合所有結構約束」唔係「44 係唯一可能」。需要證明: 任何其他 N 都 fail 至少一個結構約束 (Lucas 積, 閉合網絡, T2/T3 鎖定, su(12) rank, 整數性)。\n\n★★★ 致命: 如果 44 唔係必然 → K_Chain 嘅 44-site 係 arbitrary → 成個結構係「fit」唔係「推導」",
     "★★★"),

    ("96", "su12_origin", "SU(12) 根源 (點解係 SU(12) 而唔係 SU(5)/SO(10)/E₆?)",
     "O72 可疑點 #2 (★★★)", "O85 (18/18), O59 (Z₃ orbifold), O88 (46/46), O89 (46/46)",
     "O85 閉合咗 breaking chain 但冇答「點解 SU(12)」。需要由第一性原理推導 SU(12) 嘅必然性。\n\n候選方向:\n  1. 12 = 4×3 = B×N_gen (K_Chain × K_Tree 張量積維度)\n  2. 12 = L₅+1 (Lucas 數 + 1, 幾何根源)\n  3. 12 = h¹¹ (CY₃ Kähler moduli 數)\n  → 但邊個係「原因」邊個係「後果」?\n\n★★★ 致命: 如果 SU(12) 係 arbitrary → GUT 群係「選擇」唔係「必然」",
     "★★★"),

    ("97", "phi_cosmic_origin", "φ 宇宙根源 (點解 golden ratio 出現?)",
     "O72 可疑點 #3 (★★)", "O51 (0,1→φ 數學必然), O72 H4 (L=53/8), O39 (SSB 勢)",
     "0,1 → φ 係數學必然 (x²+x-1=0 嘅正根)。但「點解宇宙用 φ 做尺度因子?」呢個可能係形而上學問題。\n\n需要區分:\n  1. φ 作為數學必然 (0,1 遞迴 → φ) — 冇得質疑\n  2. φ 作為宇宙尺度 — 點解宇宙嘅結構用 φ 而唔係 π/e/√2?\n\n★★ 重要: 影響可信度但唔致命 (如果 φ 係 fit 唔係必然, IDCM 仍然 work)",
     "★★"),

    ("98", "lcdm_ionization_deviation", "ΛCDM I 分歧 2.18% (ionization efficiency)",
     "O72 可疑點 #8 (★★★)", "O73 (docs/08), O76 (z 紅移), O86 (SM×IDCM×GR)",
     "O73 發現 ΛCDM 嘅 I (ionization efficiency, reionization optical depth) 同 IDCM 有 2.18% 分歧。\n\n無人解釋呢個分歧係:\n  - 「模型幾何差異」(IDCM 同 ΛCDM 嘅幾何唔同, 自然有分歧)\n  - 定係「IDCM 錯誤」(IDCM 嘅 reionization 預測出錯)\n\n需要獨立審計:\n  1. 檢查 O73 reionization 推導\n  2. 對比 Planck τ_reion 數據\n  3. 判定 2.18% 係「可接受嘅模型差異」定「結構性問題」\n\n★★★ 致命: 如果係後者 → 影響 O73 嘅 CMB 投影閉合",
     "★★★"),
]

def write_problem_record(num, slug, title, source, prereq, positioning, prio):
    return f"""# O{num} — {title}

> **創建日期**: 2026-08-27
> **狀態**: 🔴 **已註冊 — 待攻堅 (另一 session)**
> **來源**: {source}
> **前置**: {prereq}
> **定位**: {positioning.split(chr(10))[0]}
> **優先度**: {prio}

---

## 問題

{positioning}

## 攻擊路線

```\n🔴 待攻堅 (另一 session)\n```

## 驗證標準

```\n✅ 待攻堅時建立\n```

## 狀態

```
🔴 已註冊 — 待攻堅
```
"""

for num, slug, title, source, prereq, positioning, prio in SERIES:
    path = os.path.join(BASE, f"o{num}_{slug}")
    os.makedirs(os.path.join(path, "docs"), exist_ok=True)
    os.makedirs(os.path.join(path, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(path, "data"), exist_ok=True)
    
    # 01_problem_record.md
    with open(os.path.join(path, "docs/01_problem_record.md"), "w") as f:
        f.write(write_problem_record(num, slug, title, source, prereq, positioning, prio))
    
    # SESSION_START.md
    with open(os.path.join(path, "SESSION_START.md"), "w") as f:
        f.write(f"""# O{num} — SESSION START

> **Session**: 2026-08-27 (由 O72 可疑點 #{num} 開)
> **狀態**: 🔴 已註冊 — 待攻堅

---

## 定位

{title}

## 交接點

```
來源: {source}
前置: {prereq}
狀態: 🔴 待攻堅
```
""")
    
    print(f"✅ O{num} ({slug}) — 建立完成")

print(f"\n=== 全部建立完成 (O{list(zip(*SERIES))[0][0]}-O{list(zip(*SERIES))[-1][0]}) ===")