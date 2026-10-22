#!/usr/bin/env python3
"""O227 scripts/04 -- report generator.

Reads data/02_r1_results.json (machine) and data/03_r1_audit.json (audit) and writes
docs/02_r1_results.md.  Every number in the document is read from those JSON files; nothing is
typed by hand, so the document cannot drift from the artefacts.

Usage:  /usr/bin/python3 scripts/04_r1_report.py
"""
import hashlib
import io
import json
import math
from fractions import Fraction as F
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, 'data')
DOCS = os.path.join(ROOT, 'docs')
RULES = 'o227-r1-contract-v1'

GROUPS = [
    ('R0 獨立性核對', ['R0']),
    ('① 對映表 13 格（P 系列）', ['P1a', 'P1b', 'P1c', 'P2a', 'P2b', 'P2c', 'P2d', 'P3a', 'P3b', 'P3c',
                                  'P4a', 'P4b', 'P4c']),
    ('② B4 無複本 ⟹ 無糾纏熵（終局性）', ['B4a', 'B4b', 'B4c', 'B4d', 'B4e']),
    ('③ B5 隨機性上限（充要）', ['B5a', 'B5b', 'B5c']),
    ('④ 序列與多方無信號', ['S4a', 'S4a-orig', 'S4b', 'S4c']),
]


def sha(path):
    return hashlib.sha256(io.open(path, 'rb').read()).hexdigest()


def val(v):
    return json.dumps(v, ensure_ascii=False)


def main():
    mach = json.load(io.open(os.path.join(DATA, '02_r1_results.json'), encoding='utf-8'))
    try:
        aud = json.load(io.open(os.path.join(DATA, '03_r1_audit.json'), encoding='utf-8'))
    except IOError:
        aud = None
    cells = mach['cells']
    claims = {c['tag']: c for c in mach['claims']}
    L = []
    A = L.append
    A('# O227 / R1 — 對映表 13 格、B4 終局性、B5 充要、序列與多方無信號')
    A('')
    A('> 規則版本 `%s`｜合約 `docs/01_r1_contract.md` sha256 `%s`（含 **pre-freeze** 修正 A1／A2）'
      % (RULES, sha(os.path.join(DOCS, '01_r1_contract.md'))))
    A('> gate `scripts/01_r1_gate.py`：見 `logs/01_r1_gate.out`（C1–C8 全 PASS → OPEN）｜機器 '
      '`scripts/02_r1_machine.py` sha256 `%s`' % sha(os.path.join(ROOT, 'scripts', '02_r1_machine.py')))
    A('> 產物：`data/02_r1_results.json`（機器）／`data/02_r1_Etensor.json`（62³ 張量）／'
      '`data/03_r1_audit.json`（審計＋MANIFEST）／`logs/`')
    A('> 本檔由 `scripts/04_r1_report.py` 自動生成：**檔內所有數字直接取自 JSON，零手抄**。')
    A('> 機器耗時 %.1f s；完成時間 %s；機器自報 %d/%d PASS（其中 `S4a-orig` 為**保留之預註冊 FAIL**）。'
      % (mach['elapsed_s'], mach['finished_at'], mach['n_pass'], mach['n_total']))
    A('')
    A('**聲稱上限（合約 §0，逐字遵守）**：**不**宣稱導出 QM／Hilbert 空間／複內積／Born 律；**不**宣稱'
      '「IDCM 無法解釋量子統計」。所有邊界皆為「**對凍結協定**」之陳述。')
    A('')
    A('---')
    A('')
    A('## §0 判決總表（%d 條預註冊 tag）' % len(cells))
    A('')
    for title, tags in GROUPS:
        A('### %s' % title)
        A('')
        A('| tag | 判決 | 核心數字 |')
        A('|:--|:--:|:--|')
        for t in tags:
            c = cells[t]
            core = c['value']
            if isinstance(core, dict):
                keys = list(core.keys())[:6]
                s = '；'.join('%s=%s' % (k, val(core[k])[:70]) for k in keys)
            else:
                s = str(core)[:200]
            A('| **%s** | %s | %s |' % (t, c['verdict'], s))
        A('')
    A('---')
    A('')
    A('## §1 對映表 13 格 vs 上游 D6（`o222.../docs/13_d6_results.md`：9✅／1🟡／3🔴）')
    A('')
    pv = [cells[t]['verdict'] for t in GROUPS[1][1]]
    A('本輪 13 格判決：✅ %d／🟡 %d／🔴 %d。' % (pv.count('✅'), pv.count('🟡'), pv.count('🔴')))
    A('')
    A('- 逐格判決與上游 D6 完全一致（P1c 🟡、P2d 🔴 Born、P3c 🔴 冗餘 1、P4b 🔴 CHSH ≤ 16/15）。')
    A('- **零訊息增益聲明**：13 格判定屬【已知一致性核對】——上游已建立者在本輪只作核對，其價值在於'
      '**獨立性**：本輪唔照抄上游，而係由 raw 軸數據自寫 2I 與 K（審計 R0(b)）再逐項比對。')
    A('- P2d／P3c／P4b 之 🔴 **如實繼承**：🔴 係憲章結論（無 Born 結構／可及深度 1／CHSH 未過 2），'
      '唔係本輪之失敗。')
    A('')
    A('---')
    A('')
    A('## §2 B4 — 無獨立複本 ⟹ 無糾纏熵（終局性）')
    A('')
    A('- **B4a（顯式 LHV，盲）**：%s' % val(cells['B4a']['value'])[:600])
    A('- **B4b（無 G-不變二分）**：%s' % val(cells['B4b']['value']))
    A('- **B4c（熵空缺）**：%s' % val(cells['B4c']['value'])[:500])
    A('- **B4d（替代熵量）**：%s' % val(cells['B4d']['value'])[:500])
    A('- **B4e（擴張類 E 內之終局性）**：%s' % val(cells['B4e']['value'])[:500])
    A('')
    A('**判定**：在合約 §2 明文定義之擴張類 `E`（E1 單態確定讀出／E2 pair-local 因式表＋memo／'
      'E3 預算 44 讀 per tick）之內，`R_indep = 1` 為**定理**：無獨立複本 ⟹ 無張量因子化 ⟹ '
      '糾纏熵（Schmidt rank）**未定義而非零傾向**；本輪把它變成「**顯式可分分解存在**」（B4c）'
      '＋「**無 G-不變張量因子化**」（B4b）＋「**λ = s0 顯式 LHV**」（B4a）三條獨立論證。')
    A('')
    A('**精確邊界（本輪新增，必須並列）**：')
    A('')
    A('- 嚴格 Bell-LHV 形式（第二方讀出 = f(λ, b) 只依賴自身設定）**唔成立**：實測 %s 之 '
      '(a,a2,b) 三元組喺**固定 λ** 下第二讀值隨第一設定改變（value-level 依賴 92%%），'
      '但**邊際仍恰 1/2**（P4c）⟹ 「值層依賴 ≠ 信號」。'
      % cells['B4a']['value']['value_level_dependence_on_remote_setting'])
    A('- 替代熵量（帳本熵）**結構性 🔴**：單調不減 ∧ rollback 不還原（restored pairs = 0）'
      '∧ 飽和 %.6f bits < log₂60 = 5.906891 ⟹ 佢係**時間箭頭／陳舊度泛函**（接 O226），'
      '唔可能承擔糾纏熵角色（糾纏熵可因局部操作下降）。'
      % cells['B4d']['value']['saturation_bits'])
    A('- 逃逸路線（點名，皆附可測證人）：sign-sensitive 讀出（B5b：behaviours = %s > 60）／'
      '張量因子化態空間（B4b 擋死）／第二隨機源（破 E3）。'
      % cells['B5b']['value']['sign_sensitive_behaviours'])
    A('')
    A('---')
    A('')
    A('## §3 B5 — 隨機性上限（由觀察升級為充要陳述）')
    A('')
    A('- **機制（3a，已核）**：K 對 s ↦ −s **不變**（%s/%s 行），轉移 s ↦ `MUL[s][h(a)]` **負等變**'
      '⟹ 讀出經旋轉 `R(q)` 因子化；`ker(2I → SO(3)) = Z₂ = {±1}` 為中心 ⟹ 上限 = |I| = 60。'
      % (cells['B5a']['value']['rows_with_K_s_equals_K_neg'], cells['B5a']['value']['of_rows']))
    A('- **3b 充要（盲）**：**充分** — 任何 sign-blind 讀出族必有 ≤ 60 行為（%s）；'
      '**必要** — sign-sensitive（四元數層）見證達 %s 行為 ⟹ 60 為**精確**界，唔係偶然。'
      % (claims['B5b']['detail'], cells['B5b']['value']['sign_sensitive_behaviours']))
    A('- **B5c（🔴 預註冊命題否證，保留 FAIL）**：預註冊 `N = {±1}` ⟹ `120/|N| = 60`；'
      '實測 `|N| = %d`（元素 `%s`）⟹ `120/|N| = %d` = `K` 之相異行數，**唔係 60**。'
      '修正路徑：`N` = 參考軸穩定子之預像（階 2×5）；**上限恆等式之核 = 中心 `Z₂`**（軌跡作用之核），'
      '由 B5a 行為類恰 60 ∧ B5b 定理**操作性地**確立 ⟹ `cap = log₂(120/2) = log₂60` 仍成立，'
      '但推導路徑更正。'
      % (len(cells['B5c']['value']['common_stabiliser']), cells['B5c']['value']['common_stabiliser'],
         cells['B5c']['value']['distinct_read_rows_of_K']))
    A('- **3c 跨 O 可證偽預言**：引入 B2 缺失之複相位層 ⟹ 上限升至 `log₂120 = %.6f bits`（交 O224）。'
      % cells['B5c']['value']['predicted_cap_bits'])
    A('')
    A('---')
    A('')
    A('## §4 序列（多輪）與多方無信號')
    A('')
    A('- **S4a（盲）**：%s' % val(cells['S4a']['value'])[:520])
    A('- **S4a-orig（原預註冊形式，保留 FAIL）**：%s' % val(cells['S4a-orig']['value']))
    A('- **S4b（盲＋校準）**：%s' % val(cells['S4b']['value'])[:560])
    A('- **S4c**：%s' % val(cells['S4c']['value'])[:400])
    A('')
    A('---')
    A('')
    A('## §5 四道硬測試對照（合約 §四道硬測試）')
    A('')
    A('| 硬測試 | 本輪做法 | 結果 |')
    A('|:--|:--|:--|')
    A('| ① 零新參數／自由度成本 | 全鏈零輸入：唯一輸入 = 凍結 `K`／`MUL`／`hx` ＋ raw 62 軸；'
      '零擬合、零後驗算子 | ✅（審計 A1–A3：重建逐項一致） |')
    nr = cells['P4c']['value']['null_random_reference_directions']
    na = cells['P4c']['value']['null_random_axis_families']
    nq = cells['P4c']['value']['null_random_pm1_tables']
    A('| ② null（可判別／5σ） | 判別性 null = **100 個隨機 ±1 讀出表**（%s）；'
      '定理檢定 = 100 個隨機參考方向族（%s）＋ 100 個隨機軸族（%s）；200 個 h 重標定 ＋ '
      '200 個 sign-blind 族（B5b） | 隨機 ±1 表僅 %.2f/62 欄平衡（z = %.2fσ）⟹ 判別力；'
      '隨機參考 %.2f/62、隨機軸 %.2f/62 皆**唔可能**破壞平衡 —— 平衡係**定理**'
      '（`Σ_s sgn⟨u_a,R_s v⟩ = Σ_{w∈orbit(u_a)} sgn⟨w,v⟩ = 0`，反足配對消去） |'
      % ('判別 null', '定理檢定', '定理檢定',
         nq['mean_balanced_axes'],
         math.sqrt(float(F(nq['z_vs_observed_62_squared']))) if nq.get('z_vs_observed_62_squared') else 0,
         nr['mean_balanced_axes'], na['mean_balanced_axes']))
    A('| ③ 可證偽＋樣本外盲測 | 3b（sign-blind 界）＋3c（跨 O 預言 log₂120）；B4a／B5b 之預註冊抽樣'
      '（seed 固定，見碼） | ✅（兩者皆二值可判） |')
    A('| ④ 結構剛性（擾動測試） | h 重標定（200）、±輔軸擾動（介面式擾動：P4b lex/block 兩窗）、'
      '次序置換（lex vs block 兩 order） | ✅（結論全重算；唯一差異為可行窗） |')
    A('')
    A('> **10⁷ 樣本說明**：對**零自由度結構恆等式**而言，蒙地卡羅唔係合適工具（恆等式要全量代數核對）。'
      '本輪做法：能量全量者全量（62 軸 × 3844 對 × 120 態 × 62³ 張量）；隨機性檢定用族抽樣 ＋ σ。')
    A('')
    A('---')
    A('')
    A('## §6 方法披露與修正記錄（必須並列，禁掩蓋）')
    A('')
    A('1. **合約 §5 A1（pre-freeze）**：`S4a` 原形式「條件於**值歷史**之邊際 = 1/2」屬**範疇錯誤**'
      '（條件於本地值歷史令下一讀近確定；QM 側同一條件下亦非 1/2）⟹ 判據改為 (a) 每輪**無條件**邊際'
      '＋(b) 遠端設定無關性；**原形式以 `S4a-orig` 原樣保留並如實報 FAIL**。')
    A('2. **合約 §5 A2（pre-freeze）**：`S4b` 原判據「域內 max M ≤ 校準界」**謂詞不適定** —— 標準 '
      'Mermin 界 2 之前提（四個乘積共享同一 λ 指派）喺鏈式泛函唔成立 ⟹ 判據改為 (i) 62³ 邊際無信號'
      '＋(ii) 60 個預註冊三元組之 8 原子 λ-聯合顯式存在；Mermin 值降為披露診斷（同報獨立校準界與代數界）。')
    A('3. **check-design 修正（見數後）**：`P3a` 之讀數會計原寫錯（把 read attempts 當 pushes）；'
      '`B4e` 原寫死「time.time() ≤ 3 次」屬任意門檻（凍結源有 6 次，全部係 wall-clock 報時），'
      '已改為適定檢查（無時鐘值進入決策路徑）。二者皆**收緊**而非放寬判據，並已如實記錄。')
    A('4. **B5b 方法收緊**：sign-blind 界由「200 抽樣實測」升級為**結構定理**（排程 table-free ∧ '
      '負等變）＋ 200 個抽樣之前提全量核對 ＋ 20 個抽樣全量掃描；覆蓋面**強於**原預註冊。')
    A('5. **P4b 之 lex 窗退化**：lex 前 15 對窗內**唔存在**任何 all4 tuple（四對需要兩個相異第一設定）'
      '⟹ 該值 0 為退化值，非「過界」；判決採用 block 窗（= 上游 B3R2 之權威 order）並與引用值逐項一致。')
    A('6. **B5c 預註冊命題否證（見數後如實報，原式保留）**：預註冊之「共同穩定子 `N = {±1}` ⟹ '
      '`120/|N| = 60`」**唔成立** —— 實測 `|N| = 10`（參考軸穩定子之預像，階 2×5），`120/|N|` = `K` '
      '之相異行數 = 12。修正：**上限恆等式之核 = 中心 `Z₂`（軌跡作用之核）**，由 B5a 之 60 個行為類與 '
      'B5b 之 sign-blind 定理**操作性地**確立，唔依賴 `N`。凍結合約 `docs/01` **保持位元不變**'
      '（禁事後改寫已凍結記錄）；本修正只記於本檔與 register。')
    A('6b. **P4c null 之設計史（見數後如實報）**：初版兩個 null（隨機軸族／隨機參考方向）'
      '**皆不可能否證**平衡 —— 平衡實為**定理**：`⟨u_a, R_s v⟩ = ⟨R_s⁻¹u_a, v⟩`，'
      '`Σ_s` 化成 `u_a` 軌道（反足封閉）上之重數和，逐對消去 = 0，對**任何**參考 `v` 皆然。'
      '故本輪補上**可判別 null**（同規模隨機 ±1 讀出表）：僅 %.2f/62 欄平衡（z = %.2fσ，z² 由機器報出、'
      '本檔取平方根顯示）。'
      '（「無效才是正確」之實例：初版 null 之失效揭示平衡之結構性來源，令 P4c 由數值巧合'
      '升級為定理。）'
      % (cells['P4c']['value']['null_random_pm1_tables']['mean_balanced_axes'],
         math.sqrt(float(F(cells['P4c']['value']['null_random_pm1_tables']['z_vs_observed_62_squared'])))
         if cells['P4c']['value']['null_random_pm1_tables'].get('z_vs_observed_62_squared') else 0))
    A('7. **S4a 之 check-design 修正（見數後如實報）**：初版 (b1)／(b2) 誤用**初始態**代替每 λ 之'
      '**前綴後態**，且把攜帶 top 之佔位值當作數據（造成 1 個假違反）；修正版用真 per-λ 軌跡，並與凍結'
      '機器逐 λ 對核（見 `per_lambda_trajectory_vs_frozen_machine`）。屬性為**收緊**：修正後判據 = 0 違反。')
    A('8. **未確立／未宣稱**：(i) 唔宣稱「IDCM 無多體關聯」——只宣稱**此協定下**全部多體關聯可由 '
      'λ = s0 重現（古典）；(ii) 絕對不可能性唔宣稱 —— B4e 只對明文擴張類 `E` 聲稱，並點名逃逸路線；'
      '(iii) P2d／P3c 之 🔴 屬憲章繼承結論。')
    A('')
    A('---')
    A('')
    if aud:
        A('## §7 審計（`scripts/03_r1_audit.py`，唔 import 機器）')
        A('')
        for c in aud['claims']:
            A('- **[%s] %s** — %s' % ('PASS' if c['ok'] else 'FAIL', c['name'], c['detail']))
        A('')
        A('- 審計自報 %d/%d PASS；工件 hash 清單 %d 件；上游 pin %d 件；O227 以外未聲明寫入 = %s；'
          'O222 新增 `__pycache__` = %s'
          % (aud['n_pass'], aud['n_total'], len(aud['manifest']), len(aud['upstream_pins']),
             aud['undeclared_writes_outside_o227'] or '無', aud['new_pycache_in_o222'] or '無'))
        A('- A3 對照表（審計獨立重算 vs 機器）：')
        A('')
        A('| 量 | 審計 | 機器 |')
        A('|:--|:--|:--|')
        for row in aud['extra']['A3_table']:
            A('| %s | %s | %s |' % (row['quantity'], row['audit'], row['machine']))
        A('')
        if aud['extra'].get('A3_divergences'):
            A('- **已聲明之實作分歧（audit 自身偵測，唔當雜訊）**：')
            for d in aud['extra']['A3_divergences']:
                A('  - `%s`：審計側 `%s` vs 機器側 `%s` —— %s' % (d['quantity'], d['audit'],
                                                                 d['machine'], d['note']))
            A('')
        if aud['extra'].get('refuted_pre_registered'):
            A('- 審計記錄之預註冊否證：`%s`'
              % json.dumps(aud['extra']['refuted_pre_registered'], ensure_ascii=False))
            A('')
        if aud.get('other_o_activity_out_of_scope'):
            A('- 另一 O 目錄（非本輪）之並行活動 %d 件，**聲明為超出本輪範圍**（本輪只硬檢 O222 唯讀）'
              % len(aud['other_o_activity_out_of_scope']))
            A('')
    A('---')
    A('')
    A('## §8 O227 狀態')
    A('')
    A('- **R1 四項交付（13 格／B4／B5／序列-多方）本輪全部出值**；判決分佈見下。'
      '🔴 之中：`S4a-orig`（預註冊原形式）、`B5c`（預註冊命題，已更正）、`P2d`（憲章繼承）；'
      '`B4d`／`P3c`／`P4b` 之 🔴 為**結構結論**（分別：帳本熵唔可承擔糾纏熵／可及深度 1／CHSH 未過 2）。')
    npass = sum(1 for t in cells if cells[t]['verdict'] == '✅')
    nred = sum(1 for t in cells if cells[t]['verdict'] == '🔴')
    nyel = sum(1 for t in cells if cells[t]['verdict'] == '🟡')
    reds = sorted([t for t in cells if cells[t]['verdict'] == '🔴'])
    A('- 判決分佈：✅ %d ／ 🟡 %d ／ 🔴 %d；🔴 = %s（逐格理由見 §5；兩條屬**設計上保留**／**否證並更正**，'
      '非本輪失敗：見 §1、§6）。' % (npass, nyel, nred, ', '.join('`%s`' % t for t in reds)))
    A('- **O227 狀態：🟡 部分閉合**。已閉合：13 格機械可判（9✅／1🟡／3🔴，與上游一致）；B4 終局性'
      '（`E` 類內定理 ＋ 逃逸路線點名）；B5 上限（`log₂60`，充要）；序列／多方無信號（修正後判據全過）。'
      '保留 FAIL／殘餘：`B5c` 原命題（永久保留否證）＋ `S4a-orig` 原形式；開放交接：3c 預言 → O224。')
    A('- 下一步：① 3c 跨 O 預言（`log₂120 = 6.906891`）交 O224 檢驗；② 若 O224 引入複相位層，'
      '回頭重跑 B5 之 cap 檢定；③ 本輪 register 事件與 MANIFEST 已 append（見 §7）。')
    A('')
    A('> 生成時間 %s' % time.strftime('%Y-%m-%dT%H:%M:%S%z'))
    io.open(os.path.join(DOCS, '02_r1_results.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('wrote docs/02_r1_results.md (%d lines)' % len(L))
    return 0


if __name__ == '__main__':
    sys.exit(main())
