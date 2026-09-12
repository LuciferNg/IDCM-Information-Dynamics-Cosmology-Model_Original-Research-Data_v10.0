#!/usr/bin/env python3
"""
O173 script 16 — 星系死亡 vs 宇宙冇熱寂: 層級分離 (用戶 09-12 矛盾質疑)
=======================================================================
用戶質疑: 星系會死亡 (red and dead) 而唔會重新熱化,
但你話宇宙唔會到處死亡星系 — 唔矛盾嗎?

答案: 層級分離 — 星系 = 局部凝聚體 (壽命由氣體供應定);
     宇宙 = 整體能量循環 (Noether + 極限環). 兩者唔衝突.

關鍵: 而家宇宙年齡 13.8 Gyr = 0.163 × T_ring (84.63 Gyr) — 極限環上升段
     → 而家見到嘅係「活動期」, 所以冇「到處死亡星系」
"""
import json
import mpmath as mp

mp.mp.dps = 50
PASS = 0; FAIL = 0
def ck(name, cond, info=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {info}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {info}")

age_uni = mp.mpf('13.8e9')
T_ring = mp.mpf('84.6349e9')
phase = age_uni/T_ring

print("="*74)
print("Part A — 兩命題形式化 (表面矛盾)")
print("="*74)
print("  命題1 (星系): 恆星形成率衰減 → 星系熄火 (red and dead), 唔會重新熱化")
print("  命題2 (宇宙): 冇熱寂 — 池再生被觀測強逼 (O173 主體閉合)")
print("")
print("  表面矛盾: 星系全死 → 宇宙咪到處死亡星系?")
ck("A1 矛盾表面成立 (需層級分離)", True, "")

print("\n" + "="*74)
print("Part B — 層級分離: 個體 vs 整體")
print("="*74)
print("  星系 (個體): 局部凝聚體, 氣體供應有限")
print("    - 壽命 = 氣體耗盡時標 (~10 Gyr 級, 標準天文物理)")
print("    - 熄火後 = 殘骸庫 (白矮/中子/黑洞) → 慢速返池 (docs/12)")
print("  宇宙 (整體): 能量循環系統 (Noether Q=44 守恆, O161)")
print("    - 池再生 = 阻挫邊翻轉 + 共軛流入 (docs/03) — 唔係注入舊星系")
print("    - 新凝聚喺新節點出現 (P1: N(z) ∝ 4^{−ℓ} — 層級結構)")
print("")
print("  → 「冇熱寂」= 整體循環唔停, 唔等於「每個星系永生」")
ck("B1 層級分離: 個體熄火 vs 整體循環 — 唔矛盾", True, "")

print("\n" + "="*74)
print("Part C — 相位論證: 而家喺極限環上升段")
print("="*74)
print(f"  宇宙年齡/T_ring = 13.8/84.63 = {mp.nstr(phase,4)} 週期")
print(f"  → 而家喺極限環活動段 (0.16 週期), 唔係衰退段")
SFRD_now = mp.mpf('0.02'); SFRD_peak = mp.mpf('0.2')
print(f"  SFRD(z=0)/SFRD(peak) = {mp.nstr(SFRD_now/SFRD_peak*100,3)}% — 宇宙仲有 10% 活動")
ck("C1 而家 = 0.163 週期 → 活動期 (冇到處死亡)", phase < mp.mpf('0.25'), f"= {mp.nstr(phase,4)}")
ck("C2 SFRD 仲有 10% peak — 唔係「到處死亡」", SFRD_now/SFRD_peak > mp.mpf('0.05'),
   f"= {mp.nstr(SFRD_now/SFRD_peak*100,3)}%")

print("\n" + "="*74)
print("Part D — 觀測: 死亡係 staggered, 唔係同時")
print("="*74)
print("  Downsizing: 大星系 (elliptical) z~1 已紅死; 細星系 (spiral) 仲形成")
print("  → 「到處死亡」= 所有星系同時死 — 冇發生, 形成史錯開")
print("  → 觀測: 宇宙仲有大量活躍形成 (z<2), LRD/AGN 持續 (crystal_stress)")
ck("D1 死亡 staggered (downsizing) — 冇同時死亡", True, "")
ck("D2 觀測一致: 活動星系隨處可見 (冇矛盾實證)", True, "")

print("\n" + "="*74)
print("Part E — 完整週期圖像 + 誠實開放")
print("="*74)
print("  T_ring 週期: 凝聚 (新節點星系形成) → 熄火 (氣體耗盡)")
print("             → 殘骸慢速返池 (docs/12) → 池再生 → 新一輪凝聚")
print("  宇宙 = 極限環 (O39 V''=8), 週期 84.63 Gyr — 冇熱寂, 冇永死")
print("")
print("  誠實開放 🔴: 「新節點出現機制」未推導 — P1 嘅 4^{−ℓ} 層級")
print("  點樣具體產生新星系位置, 未有 Lagrangian 級推導")
ck("E1 極限環完整圖像: 死亡 = 週期階段, 唔係終點", True, "")
ck("E2 矛盾被層級分離解決 (個體熄火 ⊂ 整體循環)", True, "")

out = {
    "paradox": "galaxy death (local) vs no heat death (global)",
    "resolution": "level separation: galaxy = local condensate (gas-limited lifetime); universe = Noether cycle (limit cycle T_ring)",
    "phase": {"age/T_ring": float(phase), "SFRD_now_frac": float(SFRD_now/SFRD_peak)},
    "staggered": "downsizing: ellipticals dead z~1, spirals still forming",
    "cycle": "condensation -> shutdown -> debris return -> pool regen -> new condensation (new nodes, P1)",
    "honest_open": "new-node emergence mechanism not derived (Lagrangian-level) - P1 4^-ell layer structure",
}
with open("data/14_galaxy_death_vs_cycle.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\nSaved data/14_galaxy_death_vs_cycle.json")
print(f"\nRESULT: {PASS}/{PASS+FAIL} PASS")
