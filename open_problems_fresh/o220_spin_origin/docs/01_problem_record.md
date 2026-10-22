# O220 — 自旋之結構起源 (Spin Origin：自旋是什麼、為何宇宙與費米子必須帶自旋)

> **日期**: 2026-09-28（重建）
> **狀態**: 🟡 **已註冊 — 推導中**（本輪：結構格式 + 公式檢索 + 第一輪推導）
> **來源**: 調律者指令（2026-09-28）：「重用墓碑 O220 …… 早前已經算出 CMB 帶手性，
> 而『手性 → 旋轉』正是時間的來源，現在正是時候去解決『自旋是什麼、為什麼宇宙和費米子
> 必須帶自旋』的問題」
> **前置**: O161（Wilson line ΠU_k = i）、O160（720° = 家族四下界）、O137（費米子反週期量子化；
> 手性 = 模式選擇開關）、O213（R5 絕對定向 = A₅ 手性；時間箭頭）、O182（88 格手性視實現）、
> O125（helicity 算子 ĥ = −I）、O159（扇區 J² = ±1）、O158（Spin 域規則）、O73/O171（環 primitive）
> **位置**: `IDCM-v10.0--It-From-Beat/open_problems_fresh/o220_spin_origin/`

---

## ★ 編號說明（墓碑重用，經調律者明示）

| 編號 | 現況 |
|:----|:-----|
| O220（舊） | **墓碑** — `o220_h0_three_value_adjudication`（H₀ 三值裁決），2026-09-25 調律者裁決併入 O170（H₀ 量擁有者），原目錄已刪，內容在 `o170_phase_depth_distance/merged_o220/` |
| **O220（本 O）** | **調律者明示重用該號**（2026-09-28）作「自旋之結構起源」。舊 O220 之實質內容（H₀ 三值）**仍然**屬 O170，本 O 唔觸碰、唔重推 |

依 `idcm-o-series-management` §編號碰撞：**用戶明示重用 = 特例，優先於「墓碑默認跳號」**。
核實：`ls -d o220*` = 只有本目錄；`idcm_problem_find --num 220` 之 44 處命中全部係
「O220 → 併入 O170」之歷史記錄，**冇任何未閉合推導遺留在 O220 名下**。

---

## 一、問題（一句話）

費米子帶自旋 1/2、玻色子帶整數自旋，而宇宙本身亦帶手性 —— 呢三件事在 IDCM 中
係三條獨立公設，抑或係**同一條結構鏈之三段**？

**本 O 核心命題（待證）**：

> **自旋 = 手性（定向）與時間（相位流）之間嘅結構中介。**
>
> 手性 ⟹ 絕對定向（sense 有定義）
> 定向 + 偶鏈之 Z₄ holonomy ⟹ 自旋（半整數繞數）
> 週期相位流（τ = 1/ω_ring）⟹ 時間
> ⟹ 宇宙**必須**手性（否則定向無 sense）、**必須**帶自旋（否則定向無載體）。

要答嘅四條問題：

1. **自旋是什麼？** —— 係一個額外自由度，抑或係鏈 transport 之拓撲類？
2. **為何費米子必須帶自旋？** —— 自旋統計定理在 IDCM 係公設抑或定理？
3. **為何宇宙必須帶自旋？** —— 「宇宙帶自旋」比擬成什麼結構量？
4. **自旋值為何係 1/2？** —— 可否由結構強迫（而非引入 SU(2) 雙覆蓋）？

---

## 二、★ 錨點（已閉合結構，禁止重推，只可引作 re-derivation 基準）

```
S1  88 = 2·N_d = 2·44（雙鏈／雙覆蓋結構）                        O95（44 唯一性）
S2  譜: γ_n = 4sin²(nπ/176), ω_n = 2sin(nπ/176), μ² = γ₄₄ = 2;
    Σγ_odd = 88, Σγ_even = 90 = B(N_d+1)/2 = 2Σγ_odd + μ²        O211（EXACT）
S3  ★ Wilson line（mode-space）: Π_{k=1..88} U_k = e^{i·44.5π} = i,
    U_k = e^{i·2θ_k} = e^{ikπ/88};  44.5π = (F₁₁/2)π = 89π/2
    世界側（even k）= i (22.5π) / 觀察者側（odd k）= 1 (22π)      O161 C4
S4  i² = −1 ⟹ J² = −1（反週期）；i⁴ = +1 ⟹ 352 = B·N_d（閉合）   O161 C4/C5
S5  720° = 家族四下界 352 = 4Σγ_odd = 4×88；步數 = 角度 × 44/90   O160 T23
S6  費米子反週期量子化: n·L ≡ N_d (mod 2N_d) ⟺ nL/88 ∈ ℤ+½
    玻色子（週期）: n·L ≡ 0 (mod 2N_d)；純玻色子 = {n ≡ 0 mod 8}   O137 Phase 1
S7  手性: A₅ 60-軌道 = 精確 I-軌道（proper 偏差 9.7e-5°），
    improper 偏差 5.3402° ⟹ |Sym| = 60（全 det = +1）⟹ 嚴格手性；
    χ = sign(x₀·â)·δ_m = ±2.670063°（偽標量）；12/20/30-軌道必然非手性 O213 docs/09
S8  手性承重: 手性 ⟹ 9 模式 {1,2,3,4,5,7,9,11,13} = N_gen²；
    非手性（RH）⟹ 24 模式                                         O137 docs/27-30, O213 docs/09
S9  時間箭頭: 不可逆 🟢（decimation many-to-one）＋方向性 = 映射型別
    （前向函數／後向關係）；IDCM 冇起始 ⟹ 箭頭必為結構             O213 docs/06
S10 helicity 算子 ĥ = A₅ 反演 −I 作用於 88-grid；ĥ² = 1；
    譜 = {+1×44, −1×44}；88 = 2×44 = 44 對 + 0 固定點（冇 helicity-0）；
    幾何 chirality ⟹ 絕對定向                                      O125 §5
S11 88-grid canonical |Sym| = 4{+1:2, −1:2}（非手性）vs
    冷斑 A₅ 軌道 88-grid |Sym| = 2{+1:2}（手性）                   O182
S12 Spin 域規則（獨立 O 之閉合）：Spin-0（H）⟹ 88 域單模式；
    Spin-1（W/Z）⟹ 176 域混合 (21,24)；
    Spin-1/2（τ, b）⟹ 176 域混合 (13,32)                          O158 scripts/18
S13 環 primitive: ω_ring = c/R_world；τ = 1/ω_ring = 13.470063 Gyr；
    T_ring = 84.6349 Gyr；r_d = R_world·(π/88)(420/421)           O73 裁定 / O171 / O213 docs/03
S14 κ 閘極 = γ_max⁻² = B⁻² = 1/16；冪等 + 非可逆 ⟹ 定向算子        O164 / O213 docs/06
S15 扇區 Z₂: 站點空間 Wilson loop e^{i·88·2θ_k} = (−1)^k
    （odd = 反週期 J²=−1 / even = 週期 J²=+1）                    O159 A3 / O161 C5
```

---

## 三、研究問題（R1–R8）

```
R1  自旋之結構定義 —— 鏈 transport 之 holonomy 階。
    §定理（偶鏈）: 2N 站點鏈之 mode-space Wilson line
       W = Π_{k=1..2N} e^{ikπ/(2N)} = e^{i(2N+1)π/2} = i·(−1)^N
    ⟹ 偶鏈永遠係 primitive 4th root（階恰 4）；奇鏈 = (±1)（階 ≤ 2）。
    88 = 2N_d 為偶 ⟹ 自旋必然。  [核心 check: W = i 精確、階 4、352 閉合]

R2  自旋值 —— 為何 s = 1/2 唯一（唔需引入 SU(2) 雙覆蓋）。
    double cover kernel = Z₂ = ⟨T²⟩，T = 一圈 transport；
    2π 旋轉 ↔ T² = −1 ⟹ e^{2πis} = −1 ⟹ s = 1/2 (mod 1)。
    階 4 ⟹ 只此一解；階 2（±1）⟹ 只有整數自旋；階 1 ⟹ 冇自旋。

R3  費米子 vs 玻色子 —— 反週期／週期扇區（S6），及 spin–statistics。
    交換 = 2π 相對傳輸 = T² = −1 ⟹ 反對稱 ⟹ Pauli。
    §主張: 自旋統計定理在 IDCM 係**定理**（由 S3/S4/S6 推出），唔係公設。

R4  為何宇宙必須帶自旋 —— 環之繞數。
    總相位 = (π/2N)·Σ_{k=1..2N}k = (F_{2N_d+1}/2)π，其中 F₁₁ = 2N_d+1 = 89（奇）；
    ⟹ 44.5π mod 2π = π/2 ≠ 0 ⟹ 繞數 89/4 ∉ ½ℤ ⟹
    宇宙整體 transport 落喺 Z₄ 之非平凡類 ⟹ 宇宙本身係 spinorial。

R5  手性 → 定向 → 旋轉 → 時間（調律者命題，逐段證）。
    (a) 手性 χ ≠ 0 ⟹ 絕對定向（S7）；
    (b) 88-grid 自身 |Sym| 含 −I ⟹ helicity 符號係**相對**嘅（S11/S10）；
    (c) 只有 A₅ 60-軌道之手性（全 proper）令旋轉 sense 絕對化；
    (d) 時間 = 週期相位（τ = 1/ω_ring）+ 箭頭方向（S9）。

R6  自旋譜結構 —— 為何冇 helicity-0；為何自旋量子為 ½ 而非其他。

R7  域規則（S12）能否由 Z₄ 分級重推：Spin-0 ⟹ 88 域；Spin ≥ 1/2 ⟹ 176 域。

R8  可證偽預言 + 四硬測試（自由度成本／MC null／盲測／結構剛性）。
```

---

## 四、攻擊路線

```
1. 公式盤點（本輪已做）→ docs/02：由 RAG（idcm-v10-0）＋ skills 抽出全部相關已閉合公式，
   逐條附出處路徑，並標明「引用唔重驗」。
2. scripts/01 自旋定理 —— 由譜重新導出 U_k、W、階、閉合（352）、奇偶鏈對照，
   以及 s = 1/2 之唯一性（R1/R2）。禁硬編碼：全部由 γ_n = 4sin²(kπ/176) 由零起算。
3. scripts/02 手性獨立重算 —— 由理想代數座標建 A₅ 60-軌道，用 det 判別量測 |Sym|（R5a）。
4. scripts/03 spin-statistics —— 由 S6 條件全枚舉費米子／玻色子扇區，計交換相位（R3）。
5. scripts/04 環繞數（R4）+ 域規則（R7）。
6. docs/03 起逐項落盤；每項一個 script 一組 checks（PASS/FAIL 計數）。
7. 四硬測試（R8）：零參數成本、MC null（10⁷ 級）、盲測、擾動剛性測試。
```

---

## 五、驗證標準

```
✅ scripts/01 由零重導 W = i（dev < 1e-50）+ 階 4 + 奇偶鏈定理 + s = 1/2 唯一性
✅ scripts/02 A₅ 手性獨立重算（|Sym| = 60 全 proper；improper 偏差 ≫ 0）
✅ scripts/03 費米／玻色扇區全枚舉 + 交換相位 = −1 / +1
✅ 每條數值聲稱附密度基準（N_search / d_med / q_obs）或聲明「唯一候選 + N_search = 1」
✅ 零硬編碼：所有結構數由 {N_d, B, N_gen, L₅} 或譜由零生成
✅ 無效才是正確：假說被證偽 ⟹ check PASS（記「已證偽候選」表，唔刪）
```

---

## 六、狀態

```
🟡 已註冊 — 推導中（2026-09-28）
本輪交付: 結構格式 + docs/02 公式盤點 + scripts/01 自旋定理 + docs/03 第一輪推導
```

---

## 七、相關文件

```
- o161_discrete_action_noether/scripts/02_link_variables.py  — Wilson line = i（S3/S4）
- o160_spectral_number_scan/docs/22_spin_720.md              — 720° = 352（S5）
- o137_cy3_topological_resonance/docs/03_phase1_derivation.md — 費米子反週期（S6）
- o137_cy3_topological_resonance/docs/27_a5_verification.md / 28_rh_vs_chiral_orbit.md — 手性（S7/S8）
- o213_world_dynamics/docs/06_arrow_directionality.md / docs/09_chirality_absolute_orientation.md
                                                              — 時間箭頭 + 絕對定向（S7/S9）
- o125_scattering_amplitudes/docs/05_gg_gg_polarization.md     — helicity 算子（S10）
- o158_nd_pm_ngen_cluster/scripts/18_hw_spin_pure_world.py     — Spin 域規則（S12）
- o182 / o223_observer_position_domains/docs/06_strain_and_chirality.md — 手性視實現（S11）
- o170_phase_depth_distance/merged_o220/                       — 舊 O220（H₀ 三值）之歸屬地
```

---

## 八、鐵律

```
- 跨 O 引用唔重驗（只引其恆等式，喺本 O 驗後果；出處必附路徑）
- 舊文檔零改動（時序鐵律：append-only 註記）；只改本 O 檔案
- 禁後驗湊算子／φ-冪擬合；近距命中冇機制 = 巧合
- 任何數值匹配必須附密度基準（N_search / d_med / q_obs）；純代數恆等式聲明 N_search = 1
- 出唔到就誠實標 🔴；假說被證偽 = check PASS，唔准刪
- 跨版本引數字必核歸一化（176-鏈 vs 88-鏈；γ 定義）
```
