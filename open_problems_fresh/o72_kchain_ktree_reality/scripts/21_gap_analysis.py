"""
O72 Gap Analysis: O76-O92 對照 O72 未完成工作 inventory
=====================================================================
目的: 檢查 O72 所有未完成工作 (docs/19) 係咪已被 O76-O92 覆蓋,
      判斷仲有冇需要開新 O 系列。
"""
import os

BASE = os.path.expanduser("~/Projects/IDCM/IDCM-v10.0/open_problems_fresh")

# O72 未完成工作 inventory (from docs/19)
inventory = {
    "A1": {"name": "H6: z 紅移翻譯", "target": "O76", "prio": "★★★"},
    "A2": {"name": "H7: Occam 對照深化", "target": "O77", "prio": "★★"},
    "A3": {"name": "H8: 觀察者 re-framing", "target": "O78", "prio": "★★"},
    "A4": {"name": "H9: post-diction vs prediction", "target": "O79", "prio": "★★"},
    "A5": {"name": "H10: W-field Lagrangian", "target": "O80", "prio": "★★"},
    "A6": {"name": "Q3: EOM 統一 (free 定 sine-Gordon)", "target": "O81", "prio": "★★★"},
    "A7": {"name": "Q8: 質量生成翻譯 (γ_k ↔ 粒子質量)", "target": "O82", "prio": "★★★"},
    "B1": {"name": "Q5: Correlator ⟨φφ⟩ ↔ C_ℓ", "target": "O83", "prio": "★★★"},
    "B2": {"name": "Q7: 真空能統一 (90/88/283.0821)", "target": "O84", "prio": "★★"},
    "B3": {"name": "Q6: SU(12) → SM breaking chain", "target": "O85", "prio": "★★★"},
    "B4": {"name": "Q10: SM × IDCM × GR 耦合", "target": "O86", "prio": "★★★"},
    "B5": {"name": "1496 模式物理 (H5 延伸)", "target": "O87", "prio": "★★"},
}

def get_status(target):
    for n in range(76, 93):
        d = os.path.join(BASE, f"o{n}_*")
        import glob
        dirs = glob.glob(d)
        if dirs:
            pr = os.path.join(dirs[0], "docs/01_problem_record.md")
            if os.path.exists(pr):
                with open(pr) as f:
                    for line in f:
                        if "狀態" in line:
                            return line.strip()
            # fallback: root level
            pr2 = os.path.join(dirs[0], "01_problem_record.md")
            if os.path.exists(pr2):
                with open(pr2) as f:
                    for line in f:
                        if "狀態" in line:
                            return line.strip()
    return "❓ 未找到"

print("=" * 72)
print("O72 未完成工作 vs O76-O92 對照表")
print("=" * 72)
print(f"{'#':>3} {'O72 缺口':30s} {'→':2s} {'O':3s} {'狀態':50s}")
print("-" * 90)
all_ok = True
for key, item in inventory.items():
    status = get_status(item["target"])
    # Check if closed
    closed = "🟢" in status or "閉合" in status
    if not closed:
        all_ok = False
    print(f"{key:>3} {item['name']:30s} → {item['target']:3s} {status[:50]}")

print()
print("=" * 72)
print("其他 O 系列 (非 O72 直接移交)")
print("=" * 72)
for n in [88, 89, 90, 91, 92]:
    print(f"  O{n}: {get_status(f'O{n}')[:60]}")

print()
print("=" * 72)
print("分析")
print("=" * 72)
print("""
  O72 原 inventory (docs/19) 共 12 項:
    A1-A7: LCDM 角度自我質疑
    B1-B5: LCDM 翻譯對接

  已覆蓋 (A1-A6, B1-B5) = 11/12:
    O76 (z 紅移) 🟢 已閉合
    O77 (Occam) 🟢 已閉合
    O78 (觀察者) 🟢 已閉合 (docs/07 closure record, 但 problem record 未 update)
    O79 (prediction) 🟢 已閉合
    O80 (W-field L) 🟢 85/85 PASS
    O81 (EOM 統一) 🟢 27/27 PASS
    O83 (correlator) 🟢 58/58 PASS
    O84 (真空能) 🟢 65/65 PASS
    O85 (SU(12) breaking) 🟢 18/18 PASS
    O86 (SM×GR 耦合) 🟢 34/34 PASS
    O87 (1496 物理) 🟢 已閉合

  未覆蓋 (A7) = 1/12:
    O82 (質量生成翻譯) 🔴 待攻堅 — 仍係缺口

  新 O 系列 (非 O72 直接):
    O88 (Anomaly + Fermion) 🟢 46/46 PASS — O85 衍生, 已閉合
    O89 (Mass Hierarchy) 🟢 46/46 PASS — O85 衍生, 已閉合
    O90 (Extra U(1) ↔ V_Λ) 🔴 待攻堅 — O85 衍生, 未閉合
    O91 (S8 張力) 🟢 36/36 PASS — 新發現, 已閉合
    O92 (KiDS-1000 S8) 🔴 待攻堅 — O91 衍生, 未閉合

  結論:
    1. O82 係唯一 O72 直接未完成 (場論學家 Q8: 質量生成 1-loop 自能)
       → 需要繼續閉合，然後 O72 可收尾
    2. O90 同 O92 係衍生問題, 唔係 O72 直接缺口
    3. O78 problem record 狀態要同步 (已閉合但 status 寫 🔴)
    4. 唔需要開新 O 系列 — 所有 O72 缺口已有對應 O 系列
       (除 O82 未閉合, 但已有 O 系列)
    5. O72 收尾條件: O82 閉合後, 返嚟 O72 做 docs/12-19 整合
""")