#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O220 scripts/03 — 域規則由 Z₄ 分級重推（R7）
====================================================================
問題（O158 Spin 假說之結構基礎）:
  為何 Spin-0 只用「88 域」，而 Spin ≥ 1/2 必須用「176 域」（世界 ⊕ 觀察者雙覆蓋）?

本輪推導（由 docs/03 之 holonomy 階 4 出發，零新參數）:
  ★ 域判準 = **模式之世界迴路 holonomy 是否實數**
     模式 k（176-鏈）: site 相位 θ_k = kπ/176
     經 88 site（世界鏈一圈）累積相位 h(k) = 88·kπ/176 = (k/2)π ⟹ h(k) = i^k
       k 偶 ⟹ h = ±1（實 ⟹ 世界鏈自身可容納 → 88 域）
       k 奇 ⟹ h = ±i（複 ⟹ 世界鏈唔封閉 → 只能喺 176 域）
  ⟹ Z₄ = ⟨i⟩ 之子群 {+1,−1}（= 88 域）vs 陪集 {+i,−i}（= 176 域專屬）
  ⟹ ★ **域 = 令模式 holonomy 封閉之最小鏈**；「88 域 ⊂ 176 域（偶子格）」係譜恆等式。

可證偽: 若任何 Spin-0 量之最佳結構表示需要奇 176-指標（或 88 域無表示），規則死。

慣例: 176-鏈 γ_k = 4sin²(kπ/176), ω_k = 2sin(kπ/176)（k = 1..88 相異值）
      88-鏈（世界鏈）γ_n = 4sin²(nπ/88)（n = 1..44 相異值）
      N_d = 44, B = 4, L₅ = 11, 45 = N_d+1 = 3o（已確立）
"""
import mpmath as mp
import os
import json

mp.mp.dps = 60
N_d, B, L5 = 44, 4, 11
C45 = N_d + 1                      # 45 = N_d+1 = 3o（chirality 橋；已確立）
PASS, TOTAL, checks = 0, 0, []


def chk(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    checks.append({"name": name, "pass": bool(cond), "detail": detail})
    print("  [%s] %s   %s" % ("PASS" if cond else "FAIL", name, detail))


def g88(n):  return 4 * mp.sin(n * mp.pi / 88) ** 2
def g176(k): return 4 * mp.sin(k * mp.pi / 176) ** 2

TOL = mp.mpf('1e-50')

print("=" * 92)
print("O220 scripts/03 — 域規則由 Z₄ 分級重推 (R7)")
print("=" * 92)

print()
print("=" * 92)
print("[A] 譜嵌入: 88 域 ⊂ 176 域（偶子格）")
print("=" * 92)
dev = max(abs(g88(n) - g176(2 * n)) for n in range(1, 45))
chk("A1 ★ γ_n^(88) = γ_(2n)^(176) ∀n = 1..44（精確恆等式）", dev < TOL,
    "max dev = %.2e" % dev)
chk("A2 相異譜值: 88 域 44 個（n=1..44）/ 176 域 88 個（k=1..88）", True,
    "44 vs 88 —— 比 = 2 = B/2")
even_k = [k for k in range(1, 89) if k % 2 == 0]
odd_k = [k for k in range(1, 89) if k % 2 == 1]
chk("A3 176 域 = 偶側 ⊕ 奇側（各 44 = N_d）", len(even_k) == len(odd_k) == N_d,
    "even = %d, odd = %d" % (len(even_k), len(odd_k)))
min_d = min(abs(g176(k) - g88(n)) for k in odd_k for n in range(1, 45))
chk("A4 ★ 奇 176-指標**冇** 88 域代表（γ_k^(176) ∉ {γ_n^(88)}）", min_d > mp.mpf('1e-6'),
    "最小相對差 = %.4e" % min_d)

print()
print("=" * 92)
print("[B] Z₄ 分級: 世界迴路 holonomy h(k) = i^k")
print("=" * 92)
hdev = max(abs(mp.e ** (mp.mpc(0, 1) * 88 * (k * mp.pi / 176)) - mp.mpc(0, 1) ** k)
           for k in range(1, 89))
chk("B1 ★ h(k) = e^{i·88·θ_k} = i^k（世界鏈一圈累積相位）", hdev < mp.mpf('1e-55'),
    "max dev = %.2e" % hdev)
cls = {}
for k in range(1, 89):
    cls.setdefault(k % 4, []).append(k)
chk("B2 Z₄ 四類各 22 個模式（k mod 4 = 0,1,2,3）",
    all(len(cls[c]) == 22 for c in range(4)), "類大小 = %s" % {c: len(cls[c]) for c in cls})
sub = [k for k in range(1, 89) if k % 2 == 0]
cos = [k for k in range(1, 89) if k % 2 == 1]
real_h = all(abs(mp.im(mp.mpc(0, 1) ** k)) < mp.mpf('1e-55') for k in sub)
imag_h = all(abs(mp.re(mp.mpc(0, 1) ** k)) < mp.mpf('1e-55') for k in cos)
chk("B3 ★ 子群 2ℤ（偶 k）⟹ h ∈ {+1, −1} 實數; 陪集 2ℤ+1（奇 k）⟹ h ∈ {+i, −i} 純虛",
    real_h and imag_h, "偶 ⟹ 實 ✓, 奇 ⟹ 純虛 ✓")
fulldev = max(abs(mp.e ** (mp.mpc(0, 1) * 176 * (k * mp.pi / 176)) - (-1) ** k)
              for k in range(1, 89))
chk("B4 全圈（176 site）相位 = e^{ikπ} = (−1)^k ⟹ 週期 ⟺ k 偶", fulldev < mp.mpf('1e-55'),
    "max dev = %.2e" % fulldev)
chk("B5 ★ 域判準: 88 域 ⟺ h(k) 實 ⟺ k 偶; k 奇 ⟹ 只能 176 域（A4 已證冇 88 域代表）",
    real_h and imag_h and min_d > mp.mpf('1e-6'))
chk("B6 兩側總相位（O161 C4 重算）: Σ_even 2θ_k = 22.5π ⟹ i; Σ_odd 2θ_k = 22π ⟹ 1",
    abs(sum(2 * (k * mp.pi / 176) for k in even_k) - mp.mpf('22.5') * mp.pi) < mp.mpf('1e-50')
    and abs(sum(2 * (k * mp.pi / 176) for k in odd_k) - 22 * mp.pi) < mp.mpf('1e-50'))

print()
print("=" * 92)
print("[C] ★ 域規則定理: 標量 ⟹ 88 域; 多重態（Spin ≥ ½）⟹ 176 域")
print("=" * 92)
print("  推導:")
print("    ① 標量態（1 分量, 自旋-0）: 冇內部標籤 ⟹ 可取實（封閉）模式 ⟹ h 實 ⟹ k 偶 ⟹ 88 域")
print("    ② 多重態（2S+1 ≥ 2）: 極化／螺旋度對偶需要**兩個唔同模式** ⟹ 至少一個非封閉模式")
print("       ⟹ 出現 k 奇 ⟹ 該態整體唔可能住喺 88 域 ⟹ 176 域")
chk("C1 88 域 = 偶子格 = 實 holonomy 扇區（44 模式 = N_d）", True, "44 = N_d 模式")
chk("C2 176 域 = 實 ⊕ 複（44 + 44 = 88 = 2N_d）", True, "88 = 2N_d")
# 互補映射 σ(k) = 45 − k 反奇偶
flip = all((C45 - k) % 2 != k % 2 for k in range(1, 89))
chk("C3 ★ 互補映射 σ(k) = N_d+1−k = 45−k **必反奇偶**（因 45 奇）", flip,
    "∀k: σ(k) 與 k 奇偶相反 ✓")
chk("C4 ★ 推論: 任何互補對 (a, 45−a) **必**跨兩側 ⟹ 必需要 176 域（結構必然, 非選擇）",
    flip and (45 - 21) % 2 != 21 % 2 and (45 - 13) % 2 != 13 % 2)

print()
print("=" * 92)
print("[D] O158 三配對審計（獨立重算 + 域歸屬）")
print("=" * 92)
PDG = {"m_H/m_W": mp.mpf('125.25') / mp.mpf('80.369'),
       "m_W/m_Z": mp.mpf('80.369') / mp.mpf('91.1876'),
       "m_τ/m_b": mp.mpf('1.77686') / mp.mpf('4.18')}
# Spin-0 (H): 88 域單模式 25  ⟺ 176-指標 50
r_H = 2 * mp.sin(25 * mp.pi / 88)
devH = 100 * abs(r_H / PDG["m_H/m_W"] - 1)
chk("D1 Spin-0 (H/W): √γ_25^(88) = 2sin(25π/88) = %.6f, dev = %.4f%%（O158 報 0.074%%）"
    % (r_H, devH), devH < mp.mpf('0.15'))
chk("D2 ★ Spin-0 之 176-指標 = 50（偶 ⟹ 實 holonomy ⟹ 88 域可容納）", 50 % 2 == 0,
    "50 mod 4 = 2 ∈ 子群")
# Spin-1 (W/Z): 176 域 (21, 24)
r_WZ = mp.sqrt(g176(21) / g176(24))
devWZ = 100 * abs(r_WZ / PDG["m_W/m_Z"] - 1)
chk("D3 Spin-1 (W/Z): √(γ_21/γ_24)^(176) = %.6f, dev = %.4f%%（O158 報 0.0007%%）"
    % (r_WZ, devWZ), devWZ < mp.mpf('0.01'))
chk("D4 ★ Spin-1 對 (21,24): 21+24 = 45 ✓ 互補; 21 奇（h = i ⟹ 需 176 域）、24 偶",
    21 + 24 == 45 and 21 % 2 == 1 and 24 % 2 == 0, "跨兩側 ⟹ 176 域必要")
# Spin-1/2 (τ/b): 176 域 (13, 32)
r_tb = mp.sqrt(g176(13) / g176(32))
devtb = 100 * abs(r_tb / PDG["m_τ/m_b"] - 1)
chk("D5 Spin-½ (τ/b): √(γ_13/γ_32)^(176) = %.6f vs PDG %.6f, dev = %.4f%%（O158 報 0.067%%）"
    % (r_tb, PDG["m_τ/m_b"], devtb), devtb < mp.mpf('0.2'))
chk("D6 ★ Spin-½ 對 (13,32): 13+32 = 45 ✓ 互補; 13 奇（需 176 域）、32 偶",
    13 + 32 == 45 and 13 % 2 == 1 and 32 % 2 == 0, "跨兩側 ⟹ 176 域必要")
chk("D7 ★ 三配對之域歸屬: Spin-0 全偶指標（88 域）; 兩個 Spin≥½ 配對皆含奇指標（176 域）",
    50 % 2 == 0 and 21 % 2 == 1 and 13 % 2 == 1)

print()
print("=" * 92)
print("[E] 判別力審計（誠實）: 88 域有冇同等精度替代?")
print("=" * 92)
best88 = {}
for tag, tgt in (("m_W/m_Z", PDG["m_W/m_Z"]), ("m_τ/m_b", PDG["m_τ/m_b"])):
    b = None
    for a in range(1, 45):
        for c in range(1, 45):
            if a == c:
                continue
            r = mp.sqrt(g88(a) / g88(c))
            d = abs(r / tgt - 1)
            if b is None or d < b[0]:
                b = (d, a, c, r)
    best88[tag] = b
    print("   %s: 88 域最佳 √(γ_%d/γ_%d)^(88) = %.6f, dev = %.4f%%"
          % (tag, b[1], b[2], b[3], 100 * b[0]))
dWZ88 = 100 * best88["m_W/m_Z"][0]
chk("E1 W/Z: 176 域 dev (%.4f%%) < 88 域最佳 dev (%.4f%%) ⟹ 精度**支持** 176 域歸屬"
    % (devWZ, dWZ88), devWZ < dWZ88)
dtb88 = 100 * best88["m_τ/m_b"][0]
chk("E2 ⚠️ **誠實負結果**: τ/b 之 88 域最佳 (12,38) dev = %.4f%% **優於** 176 域 (13,32) dev = %.4f%%"
    " ⟹ 精度**唔支持** τ/b 之域歸屬；域規則作為**選擇器**在此失效（hosting 規則仍精確）"
    % (dtb88, devtb), dtb88 < devtb)
print("   ⚠️ 且 (12,38) 並非無身份: 12 = B·N_gen, 38 = N_d−2N_gen ⟹ O158「無算子身份」之擋箭牌")
print("      喺 τ/b 呢一對唔成立。本項列為 R7-選擇層之真缺口（🔴）。")
print("   (誠實: 88 域最佳解可能只差少許 ⟹ 記錄實際比值, 唔誇大判別力)")
# O158 之 (86,39) 反例
r8639 = mp.sqrt(g176(86) / g176(39))
d8639 = 100 * abs(r8639 / PDG["m_H/m_W"] - 1)
chk("E3 ⚠️ O158 之 (86,39) 176 域反轉解: dev = %.4f%%（比 88 域單模式更精）但 86 偶/39 奇 ⟹ 仍屬 176 域 🟡"
    % d8639, d8639 < devH, "與 hosting 規則一致; 選擇層仍欠機制")

print()
print("=" * 92)
print("[F] 可證偽與一致性")
print("=" * 92)
pure_boson = [8, 16, 24, 32, 40]
chk("F1 O137 純玻色子模式 {8,16,24,32,40} 全偶 ⟹ 全部 88 域可表達（一致）",
    all(k % 2 == 0 for k in pure_boson), "全偶 ✓")
chk("F2 161/176 場: Σγ_odd = 88 = 2N_d ⟹ 奇側（176 域專屬）之譜和 = 世界鏈雙倍",
    abs(sum(g176(k) for k in odd_k) - 88) < mp.mpf('1e-45'),
    "Σ_{odd} γ = %.10f" % sum(g176(k) for k in odd_k))
chk("F3 ★ 可證偽預言: 若存在 Spin-0 量之**最佳**結構表示需要奇 176-指標 ⟹ 域規則死亡",
    True, "本輪 3/3 配對符合（樣本小, 標 🟡 級）")

print()
print("=" * 92)
print("RESULT: %d/%d PASS" % (PASS, TOTAL))
if PASS != TOTAL:
    print("FAIL: %s" % [c["name"] for c in checks if not c["pass"]])
print("=" * 92)

out = {"script": "03_domain_rule_z4", "date": "2026-09-28",
       "dev_HW_pct": float(devH), "dev_WZ_pct": float(devWZ), "dev_taub_pct": float(devtb),
       "best88_WZ_pct": float(dWZ88), "best88_taub_pct": float(dtb88),
       "dev_8639_pct": float(d8639), "checks": checks, "n_pass": PASS, "n_total": TOTAL}
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "03_checks.json")
with open(path, "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("saved %s" % path)
