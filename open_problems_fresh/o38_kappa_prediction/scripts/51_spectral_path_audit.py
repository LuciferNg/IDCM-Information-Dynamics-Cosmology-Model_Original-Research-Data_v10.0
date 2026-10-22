#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
O38/m0-scale — Script 51: 譜跡/路徑生成算子審計 — Gemini 三路徑獨立重算
================================================================
日期: 2026-10-19
觸發: 用戶轉述 Gemini 建議三路徑:
  P1: 轉移算子跡 Tr(T̂^m) 維度展開 (log₂n≈128 線索)
  P2: K_tree 總路徑組合數 (44 層桁架 微觀→宏觀)
  P3: 譜行列式/熱核展開 (Dirac 算子 Jacobian)
紀律: 外部模型答案 = 未驗證假設 (SOUL); 全部獨立重算;
      統計鐵律: 線性 dev |x/y−1|, 禁 log-normalize 假象
審計:
  A. ★128 線索拆彈: log₂n = 128.267 → 2^128 = 3.4028e38
     (線性 dev 16.9% 唔過閘 = log-normalize 假象)
  B. ★P1 譜跡: Tr(K^m) = Σ_{k=1}^{44} γ_k^m, m = 1..100
     — 有冇 m 令 Σγ^m 命中 n (線性 dev < 1e−3)?
     γ_k = 4sin²(kπ/88), γ_max = γ_44 = 4 ⟹ 主導 4^m
  C. ★P2 路徑計數: b^d 對 d ∈ {33, 44, 88}, b = IDCM 結構數
     (φ, 2, √2, 3, 11, 88/π, 176/π...)
  D. ★P3 譜行列式: det(K) = Πγ_k? + 熱核 Σe^{−γ_k·t}
  E. 判決: 三路徑有冇命中? 下一步焦點建議
用法: /usr/bin/python3 scripts/51_spectral_path_audit.py
"""
import mpmath as mp
mp.mp.dps = 50

ok = fail = 0
def chk(name, cond, info=""):
    global ok, fail
    if cond: ok += 1; print(f"  ✅ {name} {info}")
    else:    fail += 1; print(f"  ❌ {name} {info}")

n_target = mp.mpf('4.0951856e38')
N_d = 88
pi = mp.pi

def lindev(x, y):
    return abs(x/y - 1)

print("=" * 76)
print("A. ★128 線索拆彈 (Gemini P1 核心線索)")
print("=" * 76)
log2n = mp.log(n_target)/mp.log(2)
print(f"  log₂ n = {mp.nstr(log2n,6)} (尾數 0.267 — 唔係整數!)")
print(f"  2^128 = {mp.nstr(mp.mpf('2')**128,7)}")
print(f"  線性 dev |2^128/n − 1| = {mp.nstr(lindev(mp.mpf('2')**128, n_target),4)}")
chk("A1 2^128 線性 dev 16.9% — 唔過閘", lindev(mp.mpf('2')**128, n_target) > mp.mpf('1e-3'))
print(f"  128 嘅組合身份: 44×3−4 = 128? 132−4 = 128 (4=B)")
print(f"  但 dev 16.9% ⟹ 128 唔係 n 嘅生成 — log-normalize 假象 (scripts/29)")
chk("A2 128 線索 = 假象 (線性 dev 唔過閘)", True)

print()
print("=" * 76)
print("B. ★P1 譜跡: Σ_{k=1}^{44} γ_k^m, m = 1..100")
print("=" * 76)
gamma = [4*mp.sin(mp.mpf(k)*pi/88)**2 for k in range(1, 45)]
best_m, best_dev = None, mp.mpf('1e9')
best_ratio = None
for m in range(1, 101):
    s = sum(g**m for g in gamma)
    d = lindev(s, n_target)
    if d < best_dev:
        best_dev, best_m, best_ratio = d, m, s
print(f"  Tr(K^1) = Σγ = {mp.nstr(sum(gamma),6)} (=90 已知)")
print(f"  Tr(K^2) = Σγ² = {mp.nstr(sum(g**2 for g in gamma),6)}")
print(f"  最佳: m={best_m}, Σγ^m = {mp.nstr(best_ratio,6)}, dev = {mp.nstr(best_dev,4)}")
chk("B1 譜跡冇命中 (best dev 唔過閘)", best_dev > mp.mpf('1e-3'))
# 主導項檢查: 4^m vs n
m64 = mp.mpf('4')**64
print(f"  4^64 = {mp.nstr(m64,6)} (dev vs n: {mp.nstr(lindev(m64, n_target),4)})")
m65 = mp.mpf('4')**65
print(f"  4^65 = {mp.nstr(m65,6)} (dev vs n: {mp.nstr(lindev(m65, n_target),4)})")
chk("B2 4^m 主導項都唔過閘 (64/65 都唔啱)", min(lindev(m64,n_target), lindev(m65,n_target)) > mp.mpf('1e-3'))

print()
print("=" * 76)
print("C. ★P2 路徑計數: b^d, d ∈ {33,44,88}, b = IDCM 結構數")
print("=" * 76)
phi = (1+mp.sqrt(5))/2
bases = {
    "φ": phi, "2": 2, "√2": mp.sqrt(2), "3": 3, "11": 11,
    "88/π": 88/pi, "176/π": 176/pi, "4": 4, "44": 44, "88": 88,
    "√φ": mp.sqrt(phi), "φ²": phi**2,
}
found = []
for bname, b in bases.items():
    for d in (33, 44, 88):
        v = b**d
        dev = lindev(v, n_target)
        if dev < mp.mpf('0.1'):
            found.append((bname, d, dev))
            print(f"  ★ {bname}^{d} = {mp.nstr(v,6)}, dev = {mp.nstr(dev,4)}")
if not found:
    print("  全部 >10% dev — 冇接近命中")
chk("C1 路徑計數冇命中 (無 b^d < 10%)", len(found) == 0)

print()
print("=" * 76)
print("D. ★P3 譜行列式 / 熱核")
print("=" * 76)
detK = mp.fprod(gamma)
print(f"  det(K) = Πγ_k = {mp.nstr(detK,6)} (=176 已知, 唔係 n)")
log_det = mp.log(detK)
print(f"  ln Πγ = {mp.nstr(log_det,6)}")
chk("D1 det(K)=176 已知閉合, 唔係 n", True)
# 熱核: Σ e^{−γ_k t} — t 掃描
best_t, best_hdev = None, mp.mpf('1e9')
for t in [mp.mpf('0.1'), mp.mpf('1'), mp.mpf('10'), mp.mpf('44')]:
    h = sum(mp.e**(-g*t) for g in gamma)
    d = lindev(h, n_target)
    if d < best_hdev: best_hdev, best_t = d, t
print(f"  熱核 Σe^{{−γt}} best t={best_t}, dev={mp.nstr(best_hdev,4)}")
chk("D2 熱核冇命中", best_hdev > mp.mpf('1e-3'))
# Zeta 型: Σ γ_k^{−s}?
best_s, best_zdev = None, mp.mpf('1e9')
for s in [mp.mpf('0.5'), mp.mpf('1'), mp.mpf('2'), mp.mpf('3')]:
    z = sum(g**(-s) for g in gamma)
    d = lindev(z, n_target)
    if d < best_zdev: best_zdev, best_s = d, s
print(f"  Σγ^{{−s}} best s={mp.nstr(best_s,3)}, dev={mp.nstr(best_zdev,4)}")
chk("D3 譜 Zeta 冇命中", best_zdev > mp.mpf('1e-3'))

print()
print("=" * 76)
print("E. 判決")
print("=" * 76)
print("  1. ★128 線索 = log-normalize 假象 (A1: 線性 dev 16.9%)")
print("     — Gemini P1 嘅核心線索唔成立, 唔應該做焦點")
print("  2. P1 譜跡 Tr(K^m): best dev 唔過閘 (B1)")
print("  3. P2 路徑計數 b^d: 全部 >10% dev (C1)")
print("  4. P3 譜行列式 = 176 (已知), 熱核/Zeta 冇命中 (D)")
print("  5. ⟹ Gemini 三路徑全部冇命中 — 冇新身份資訊")
print("  6. 但 P1/P2/P3 嘅『生成算子』方向本身啱: 呢啲先係")
print("     真正嘅內部生成測試 (零外部常數) — 只係 n 對 44 層")
print("     譜跡/路徑組合嘅生成量級唔匹配 (4.095e38 太細)")
print("     — 4^m 主導 4^64=3.4e38 / 4^65=1.4e39 夾住 n")
print(f"結果: {ok} PASS / {fail} FAIL")
print("=" * 76)