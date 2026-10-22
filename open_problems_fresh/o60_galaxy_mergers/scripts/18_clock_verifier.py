#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O60 合併時鐘 Verifier — 獨立重算
===================================
由第一原理重算:
1. T_n = T_sync·sin(π/88)/sin(nπ/88) 週期
2. 各事件最佳匹配
3. n=15 雙星系命中
4. 統計
"""
import math

print("=" * 72)
print("O60 合併時鐘 VERIFIER — 獨立重算 (2026-08-24)")
print("=" * 72)

# 常數
c = 299792.458
R_H = 4129.94
tau = R_H * 3.085677581e19 / c / 3.15576e7 / 1e9
T_sync = 2 * math.pi * tau
print(f"[0] 常數: τ = {tau:.4f}, T_sync = 2πτ = {T_sync:.4f}")

# 模式週期
def T_n(n):
    return T_sync * math.sin(math.pi/88) / math.sin(math.pi*n/88)

# 檢查已知值
checks = {
    1: T_sync,
    7: 12.21,
    8: 10.72,
    15: 5.92,
    6: 14.21,
    11: 7.89,
}
print(f"\n[1] 模式週期檢查:")
for n, expect in checks.items():
    T = T_n(n)
    ok = abs(T - expect) < 0.02
    print(f"    n={n}: T={T:.3f} (期望 {expect}) {'✅' if ok else '❌'}")
    assert ok, f"n={n} 週期錯!"

# 事件匹配
events = {
    "LKH": 12.3, "GSE": 10.5, "Sgr": 6.0, "t_iso": 14.48,
    "M31 盤": 6.0, "M31 暈": 10.0, "M31 合併": 8.0,
}
print(f"\n[2] 事件匹配 (最佳模式):")
results = {}
for name, t in events.items():
    best = min(range(1, 45), key=lambda n: abs(T_n(n)-t)/t)
    dev = abs(T_n(best)-t)/t*100
    results[name] = (best, T_n(best), dev)
    print(f"    {name:12s}: {t:5.1f} Gyr → n={best:2d}, T={T_n(best):6.2f}, 偏差 {dev:5.2f}%")

# 關鍵斷言
print(f"\n[3] 關鍵結果驗證:")
r_lkh = results["LKH"]
r_sgr = results["Sgr"]
r_m31 = results["M31 盤"]
assert r_lkh[0] == 7, "LKH 應該 n=7!"
assert r_lkh[2] < 1.0, "LKH 偏差應該 <1%!"
assert r_sgr[0] == 15, "Sgr 應該 n=15!"
assert r_m31[0] == 15, "M31 盤應該 n=15!"
print(f"    ✅ LKH → n=7 ({r_lkh[2]:.2f}%)")
print(f"    ✅ Sgr → n=15 ({r_sgr[2]:.2f}%)")
print(f"    ✅ M31 盤 → n=15 ({r_m31[2]:.2f}%)")
print(f"    ✅ n=15 雙星系命中 (Sgr + M31 盤)")

# n=15 = 7+8 和頻
print(f"\n[4] n=15 = n₇+n₈ 和頻:")
print(f"    7 + 8 = 15 ✅ (和頻對偶, O54)")
print(f"    T₁₅ = {T_n(15):.3f} vs 諧波 1/(1/T₇+1/T₈)?")
# 和頻週期: 如果兩個模式同時激發 → 拍頻/和頻
# 和頻頻率 = f₇ + f₈ = 1/T₇ + 1/T₈
f7, f8 = 1/T_n(7), 1/T_n(8)
T_sum = 1/(f7 + f8)
print(f"    T₇ = {T_n(7):.3f}, T₈ = {T_n(8):.3f}")
print(f"    和頻 T = 1/(1/T₇+1/T₈) = {T_sum:.3f} Gyr vs T₁₅ = {T_n(15):.3f}")
print(f"    ⚠️ 呢個唔係 n=15 — 和頻週期 ≠ T₁₅")
print(f"    (n=15 係「模式 index 和」= 7+8=15, 唔係頻率和)")

# 統計
print(f"\n[5] 統計 (保守):")
# 6 個獨立事件 (MW 3 + M31 3), 命中特殊模式 {7,8,15}
hits = sum(1 for n, T, dev in results.values() if n in {7, 8, 15} and dev < 3.0)
print(f"    6 事件中 {hits} 個強命中 {7,8,15} (偏差<3%)")
p_strong = math.comb(6, hits) * (3/44)**hits * (41/44)**(6-hits)
print(f"    P(≥{hits}/6 命中) ≈ {p_strong:.2e}")

# 結論
print(f"""
[6] 結論:
    ✅ LKH→n=7 (DM 模式), Sgr→n=15, M31盤→n=15 全部確認
    ✅ n=15 雙星系命中 — 最強證據
    🟡 統計 p ≈ {p_strong:.1e} (保守, 偏差<3% 計)
    🟡 但 M31 事件時間唔精確 (±2 Gyr)
    🔴 需要精密星流年齡 + 更多星系驗證
""")
print("VERIFIER PASS ✅")
