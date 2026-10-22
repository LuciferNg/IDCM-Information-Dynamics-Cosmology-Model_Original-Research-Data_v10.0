# O225 R32 合約 —— `r32-crit3-misc2-v1`（CRIT-3：三層族之充要條件（分塊行和）；MISC-2：orbit 型別混合之殘餘機制）

> **見數前凍結**（執行 `scripts/118`／`119` 之前）。凍結指紋：`data/117_r32_freeze.json`。
> 承接：**CRIT-3**（R27 立；`docs/59`）：三層族 `Kt³ = Kt²·ρ(tie,type)`（第三層類數 **4** ⟹ **4096** 表）下 R27 之精化判準相符 4064/4096、**32 反例**（全屬「判據假 ∧ `R ≡ 0`」= 漏判）；**MISC-2**（R28 立；`docs/61`）：4 orbit 中 2 混合；以 `c ↦ −c`（外部分）細分後 4→3 仍餘 1 混合。

## §0 凍結物件

`Kt²[s][a]`（R27 之二層表，由 `mask ∈ [0,256)` 參數化）、第三層類集 `CLS := {(0 if tie else 1, type)}`（|CLS| = 4）、
`ρ ∈ {±1}^4`；`R³(s) := Σ_a ρ_{cls(s,a)}·Kt²[s][a]`；R27 之精化判準 `crit2(mask) := tie_odd ∧ double_odd`；
31 軸對、`PAIR[0][a] = (sgn⟨U_a,KV₀⟩, firstsgn(U_a×KV₀))`、`types`。精確算術；唯讀 O222。

## §1 Part P —— CRIT-3：三層族之充要條件

- **P1（量測）**：類和矩陣 `P[c][s] := Σ_{a ∈ cls_c} Kt²[s][a]`（4×120）之逐 mask 零欄結構；`R³ ≡ 0` 之解集 `S(mask) := {ρ ∈ {±1}⁴ : Σ_c ρ_c P[c][·] ≡ 0}`。
- **P2（★ 預註冊）**：**`S(mask)` 皆為「子立方」（subcube）** —— 即存在 `Z(mask) ⊆ CLS` 使 `S(mask) = {ρ : ρ|_{Z} 自由、ρ|_{CLS∖Z} 固定}`（大小 = `2^{|Z|}`）。
- **P3（★ 預註冊）**：**`crit2(mask) ⟹ (全 +1) ∈ S(mask)`**（判據之充分性，全 256）；且 `S(mask) ⊋ {全+1}` 之 mask 數 = **32**（R27 之反例數）。
- **P4（導出之真充要）**：新判準 `CRIT3(mask, ρ) := (R³ ≡ 0) ⟺ ρ ∈ S(mask)` 之檢核必 4096/4096；並報 **`|Z|` 之分佈** 與 `Z` 與 `mask` 之關係（是否 `Z = 判據所對應之補集`）。

## §2 Part Q —— MISC-2：orbit 型別混合之殘餘機制

- **Q1（量測）**：4 個 orbit 之型別組成、各 orbit 之 `PAIR-key` 集（`orbit_of(0, a)`）之 cardinality 與型別分佈（複核 R28 之 `G4`／`G5`）。
- **Q2（★ 預註冊）**：**「型別混合 orbit」⟺「該 orbit 之 `PAIR-key` 集含 ≥ 2 個型別相異之 key」**（即混合由 key-型別對應而非更深不變量所致）。
- **Q3（否證備援）**：若 Q2 否證，報各 orbit 之 key × 型別交叉表，定位殘餘混合之欄。

## §3 判決規則

逐項 PASS／FAIL；否證之預註冊**原樣保留 FAIL**，另立 `-c`。兩條獨立實作（`118` 直算；`119` 另路：`P` 以逐欄累加重算、`S` 以網格枚舉獨立重建）。禁用 `math`／`random`／`numpy`／`scipy`／`statistics`／`cmath`／`secrets`／`decimal`／`mpmath`。唯讀 O222；不寫入他 O 檔。

## §4 產物

`docs/68_r32_contract.md`（本檔）｜`scripts/117_r32_contract.py`｜`scripts/118_r32_machine.py`｜`scripts/119_r32_audit.py`｜`docs/69_r32_results.md`｜`data/117–119_*.json`｜register `O225/R32`（＋ CRIT-3／MISC-2）。
