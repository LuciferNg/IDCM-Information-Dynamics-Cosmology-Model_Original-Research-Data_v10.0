# O203 — docs/02: S2 R_world 雙維度 PSLQ + null control (scripts/02, 6/6 PASS)

> **日期**: 2026-09-17 | **Script**: `scripts/02_s2_twodim_pslq.py` | **mpmath 50 dps + numpy float null**

## 一、問題形式化

O73 H1: R_world = c/ω_ring EXACT (re-label)。O203 C2 假說: 加速率維度 v_sync 可能有結構分解。
因 R_world = c/ω_ring 精確, 任何「分解」R_world = (v_sync/ω_ring)·(c/v_sync) 係 tautology —
**除非** (1±β)^p·φ^q·(n/m) ≈ 1 非平凡成立 (β = v_sync/c), 或者 1/β 有獨立結構身份。

## 二、T1: 1/β vs 結構常數庫

| 候選 | 1/β | 庫最近值 | 裁決 |
|:---|:---|:---|:---|
| c/45 | 45 | N_d+1 (EXACT) | **tautology** (自己定義) |
| c/88 | 88 | 2N_d (EXACT) | **tautology** (自己定義) |
| c/44 | 44 | N_d (EXACT) | **tautology** |
| c/2 | 2 | μ² (EXACT) | **tautology** |
| c/11 | 11 | L₅ (EXACT) | **tautology** |
| c·sin(π/88) | 28.0172 | 28 (dev 0.06%) | 🟡 trap window — **唔收** |
| c·cos(π/88) | 1.00064 | 1 (dev 0.06%) | 平凡 |
| c(1−π/44) | 1.07689 | — | 冇身份 |

**trap-window 近miss (π 有理近似, 唔係結構)**:
- csc(π/88) ≈ 28 (dev 0.06%): 小角展開 csc x ≈ 1/x → 88/π ≈ 28.011, 28 = 4L₄ 純 π-rational 近似
- 1−π/44 ≈ 13/14 (dev 0.003%): π ≈ 22/7 嘅化身 (1−1/14 = 13/14 vs 1−π/44)
- 45/88 ≈ 23/45 (dev 0.05%): (45·45 − 88·23)/(88·45) = 1/3960 純有理近miss (docs/04)

## 三、T2: (1±β)^p·φ^q ≈ 1 (p,q 非零, |p|≤30, |q|≤20) — 全滅

| 候選 | best dev | (p, q) | p-value (uniform/1-n/trig null) |
|:---|:---|:---|:---|
| C_energy (1/45) | 2.3e-3 | (−22, 1) | 0.22 / 0.09 / 0.18 — 背景 |
| λ_sync/T_ring (1/88) | 1.3e-1 | — | 背景 |
| sin(π/88) | 8.7e-3 | — | 背景 |
| cos(π/88) | 2.0e-2 | — | 背景 |
| 1−π/44 | 6.5e-3 | — | 背景 |
| O7 (1/44) | 1.6e-3 | (21, 1) | 0.15 / 0.07 / 0.12 — 背景 |
| Γ 對偶 (1/2) | 4.4e-3 | — | 背景 |

- **所有候選 best dev ≥ 1.6e-3 (0.16%)**, p-value 全部 ≈ 背景 (0.07–0.99)
- null 分佈: uniform median 5.9e-3 / 1-n median 0.167 / trig median 7.3e-3 — 候選冇一個顯著好過隨機
- **C4 判準: R_world = ω_ring·(1±β)^p·φ^q 形式冇任何結構命中**

## 四、T5: ★ 獨立長度定理 (速率維度惰性 — 核心定理)

```
所有 corpus 長度 L 都滿足 L = R_world × (無量綱常數):
  λ_sync = L_ring/88 → 2π/88·R_world      r_s = λ_sync/2 → π/88·R_world
  r_d = πR/88·420/421 → 0.03562·R_world   λ_44 = L_ring/44 → 2π/44·R_world
  R_world/88, R_world/45, hop len = λ_sync/44 → 全部 ∝ R_world
```
**推論**: ω_ring = βc/λ_struct 永遠需要 R_world 做輸入 (λ_struct ∝ R_world) ⟹
**任何自洽 v_sync = βc (β 無量綱譜) 都唔可以獨立推導 ω_ring**。
R_world = c/ω_ring 嘅 re-label 判決喺雙維度下**維持** (O73 H2 喺速率維度確認)。

## 五、判決

1. **C2 證偽**: R_world 冇雙維度結構 — (1±β)^p·φ^q 形式全滅 + null 背景; 1/β 全係 tautology 或 trap-window 近miss。
2. **C4 過關 (以否定形式)**: 結構分解唔存在, 「R_world 加入 v_sync 後嘅結構分解」被 null 排除。
3. **交付 (B) 達成**: 證明「任何自洽同步速率都唔改變 R_world = c/ω_ring re-label 判決」= 速率維度正式排除。
