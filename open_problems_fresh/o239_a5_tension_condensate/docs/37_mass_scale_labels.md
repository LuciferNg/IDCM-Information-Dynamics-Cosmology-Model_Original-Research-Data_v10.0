# O239 docs/37 — 質量數據 scale 標注表 + mixed-scale 穩健檢定（2026-10-12）

> **日期**: 2026-10-12（調律者: 「現在公式中的質量數據能標是否2GeV」）
> **Script**: `45_mass_scale_labels.py`（4/4）· **logs**: `logs/45.txt`、
> **data**: `data/45_mass_scale_labels.json`
> **一句話**: **9 點 PAIR 質量只有 u/d/s 3/9 係 MS̄(2GeV); c/b 係 MS̄(m_c/m_b);
> e/μ/τ/t 係 pole——data/09 mass9 本身係 mixed-scale 冇標 scheme。但按 scale
> 分組 fit α: pole +1.96σ / 2GeV +1.14σ / 全體 +0.10σ, 全部 <2σ ⟹ α=φ²
> 喺唔同 scale 子集各自成立, scale 混雜係『數據容器』, 唔係 α=φ² 引擎**

---

## 〇、調律者問題

「現在公式中的質量數據能標是否2GeV」——閉合式 m=M₀|Δm|^φ² fit 用嘅
9 點質量數據, 係咪統一 2GeV? 要標清楚。

## 一、★scale 標注表（PDG2024 標準報值）

| 粒子 | n | mass (MeV) | scheme | scale | 2GeV? |
|:--|:--|:--|:--|:--|:--|
| t | 1 | 172690 | pole | pole 主報; MS̄(m_t)=162.5 另報 | ❌ |
| b | 2 | 4180 | MS̄ | μ=m_b | ❌ |
| τ | 3 | 1776.86 | pole | pole (lepton 冇 running) | ❌ |
| c | 4 | 1270 | MS̄ | μ=m_c | ❌ |
| μ | 5 | 105.658 | pole | pole (lepton 冇 running) | ❌ |
| s | 7 | 93.4 | MS̄ | μ=2 GeV | ✅ |
| d | 9 | 4.67 | MS̄ | μ=2 GeV | ✅ |
| u | 11 | 2.16 | MS̄ | μ=2 GeV | ✅ |
| e | 13 | 0.511 | pole | pole (lepton 冇 running) | ❌ |

**只有 3/9 係 2GeV**。data/09 `mass9` 淨係裸數值, 冇 scheme/scale 欄——
今次補完標注表（S2 確認）。

## 二、★mixed-scale 穩健檢定（S3, 按 scale 分組 fit α）

| 組 | n | α | dev vs φ² |
|:--|:--|:--|:--|
| pole {e,μ,τ,t} | 4 | 2.7188 ± 0.0515 | +1.96σ |
| 2GeV {u,d,s} | 3 | 3.9135 ± 1.1369 | +1.14σ（3 點誤差大） |
| mc,m_b {c,b} | 2 | 2 點唔 fit 斜率 | — |
| 全體 | 9 | 2.6333 ± 0.1532 | +0.10σ |

**全部 <2σ ⟹ α=φ² 喺唔同 scale 子集各自成立**。
注意 pole 組 +1.96σ 貼近 2σ 邊緣（t 同 e 兩端拉高）——誠實標記:
單獨 pole 組係「勉強過關」; 全體 fit 最穩（+0.10σ）。

## 三、結論

1. **閉合式輸入係 mixed-scale**（PDG 標準做法, 唔係 bug）——只有
   u/d/s 係 2GeV, c/b 係 m_c/m_b, lepton/t 係 pole
2. **scale 混雜係容器, 唔係引擎**: α=φ² 唔依賴「全部 2GeV」呢個假設——
   拆開 scale 子集各自都成立（或至少 <2σ）
3. 之後引用閉合式質量數據, 要附標注表（scheme/scale/2GeV?）——
   特別係同其它版本（v1.1 ratio / v2 RGI）比較時, 唔可以當全部 2GeV

## 四、後續

- 若想進一步: 全 2GeV 統一 scale 對照（u/d/s/c/b all MS̄(2GeV)）——
  但 PDG 唔提供 c/b @2GeV 常用報值, 要 FLAG/HPQCD 另計, 唔係本 O 必要
- freeze v3 判決表（scripts/29 J1–J7）唔受影響——譜指數層面結論維持
  （v1.0 標注已明: u/d/s=2GeV, c/b=m_c/m_b, lepton/t=pole）
- O247 承接（天然污染/核子層）一樣要用標注表做輸入引用