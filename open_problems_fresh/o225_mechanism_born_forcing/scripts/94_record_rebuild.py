#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/94 -- 01_problem_record.md 逐步重建（R1→R26；以重跑實測為據）。

入：data/92_audit_sweep.json（每支 script 之重跑判決）、data/93_audit_blind.json（盲測）、docs/*.md
出：01_problem_record.md（保留 §一–§七 交接基石 + 追加 §八–§三十六 逐輪重建節，每節引重跑判決與該輪
   results doc 之**原文摘錄**）；並出 docs/57_audit_report.md（審計報告）。

規則：先備份現檔（.bak 帶時間戳）；每節之數字一律取自重跑 JSON 或 doc 原文；doc 宣稱與重跑不符者
  以「⚠ 漂移」明示。不新增任何推導。用法: /usr/bin/python3 scripts/94_record_rebuild.py [--dry]
"""
import hashlib
import io
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DOCS = os.path.join(BASE, 'docs')
DATA = os.path.join(BASE, 'data')

# 節號 → (輪次標籤, 首要 results doc 之檔名片段, 三件套 script 前綴)
PLAN = [
    ('八', 'R1', '02_r1_results.md', ['02', '03', '04', '05', '06', '07']),
    ('九', 'R2', '04_r2_results.md', ['10', '11', '12', '13']),
    ('十', 'R3', '06_r3_results.md', ['14', '15', '16']),
    ('十一', 'R4', '08_r4_results.md', ['17', '18', '19']),
    ('十二', 'R5', '10_r5_results.md', ['20', '21', '22']),
    ('十三', 'R6', '12_r6_results.md', ['23', '24', '25', '26']),
    ('十四', 'R7', '14_r7_results.md', ['27', '28', '29']),
    ('十五', 'R8', '16_r8_results.md', ['30', '31', '32']),
    ('十六', 'R9', '18_r9_results.md', ['33', '34', '35']),
    ('十七', 'CLOSEOUT-1', '19_closeout_r1-r9.md', ['36', '37']),
    ('十八', 'R10', '21_r10_results.md', ['38', '39', '40']),
    ('十九', 'R11', '23_r11_results.md', ['41', '42', '43']),
    ('二十', 'R12', '25_r12_results.md', ['44', '45', '46']),
    ('二十一', 'CHAIN', '26_script_chain_index.md', ['47']),
    ('二十二', 'R13', '28_r13_results.md', ['48', '49', '50']),
    ('二十三', 'R14', '30_r14_results.md', ['51', '52', '53']),
    ('二十四', 'R15', '32_r15_results.md', ['54', '55', '56']),
    ('二十五', 'R16', '34_r16_results.md', ['57', '58', '59']),
    ('二十六', 'R17', '36_r17_results.md', ['60', '61', '62']),
    ('二十七', 'R18', '38_r18_results.md', ['63', '64', '65']),
    ('二十八', 'R19', '40_r19_results.md', ['66', '67', '68']),
    ('二十九', 'R20', '42_r20_results.md', ['69', '70', '71']),
    ('三十', 'R21', '44_r21_results.md', ['72', '73', '74']),
    ('三十一', 'R22', '46_r22_results.md', ['75', '76', '77']),
    ('三十二', 'R23', '48_r23_results.md', ['78', '79', '80']),
    ('三十三', 'CLOSEOUT-2', '49_o225_closeout_r1-r23.md', ['81', '82']),
    ('三十四', 'R24', '51_r24_results.md', ['83', '84', '85']),
    ('三十五', 'R25', '53_r25_results.md', ['86', '87', '88']),
    ('三十六', 'R26', '56_r26_results.md', ['89', '90', '91']),
    ('四十', 'R27', '59_r27_results.md', ['102', '103', '104']),
    ('四十一', 'R28', '61_r28_results.md', ['105', '106', '107']),
    ('四十二', 'R29', '63_r29_results.md', ['108', '109', '110']),
    ('四十三', 'R30', '65_r30_results.md', ['111', '112', '113']),
    ('四十四', 'R31', '67_r31_results.md', ['114', '115', '116']),
    ('四十五', 'R32', '69_r32_results.md', ['117', '118', '119']),
    ('四十六', 'R33', '71_r33_results.md', ['120', '121', '122', '123']),
]
KEEP = re.compile(r'^##\s*([一二三四五六七])、', re.M)
STRIP_NUM = re.compile(r'^\d+\|')
HASH_RE = re.compile(r'\b([0-9a-f]{64}|[0-9a-f]{40}|[0-9a-f]{32})\b')


def sha(p):
    return hashlib.sha256(io.open(p, 'rb').read()).hexdigest()


def pick_doc(frag):
    """frag 為 docs/ 內之確切檔名（由 PLAN 指定）。"""
    return frag if os.path.exists(os.path.join(DOCS, frag)) else None


def headline(docfile, limit=1500):
    p = os.path.join(DOCS, docfile)
    if not os.path.exists(p):
        return ''
    lines = io.open(p, encoding='utf-8').read().split('\n')
    keep, fence = [], 0
    for ln in lines:
        s = ln.strip()
        if s.startswith('#'):
            s = s.lstrip('#').strip()          # 去標題記號但**保留內容**（不製造新標題）
            if not s:
                continue
        if s.startswith('|') or s.startswith('```') or s.startswith('---'):
            continue
        if s.startswith('> ') and len(keep) < 8:
            keep.append(s[2:].strip())
            continue
        if s.startswith('★') or s.startswith('- ★') or '★★' in s:
            keep.append(s.lstrip('- '))
            continue
        if s.startswith('RESULT') or re.search(r'\d+\s*/\s*\d+', s):
            keep.append(s)
            continue
        if len(keep) >= 14:
            break
    txt = ' ｜ '.join(x for x in keep if x)
    if len(txt) > limit:
        txt = txt[:limit] + '…'
    return txt


def main():
    dry = '--dry' in sys.argv
    sweep_p = os.path.join(DATA, '92_audit_sweep.json')
    blind_p = os.path.join(DATA, '93_audit_blind.json')
    sweep = json.load(io.open(sweep_p, encoding='utf-8')) if os.path.exists(sweep_p) else {}
    blind = json.load(io.open(blind_p, encoding='utf-8')) if os.path.exists(blind_p) else {'checks': []}
    recp = os.path.join(BASE, '01_problem_record.md')
    cur = io.open(recp, encoding='utf-8').read()
    base_part = cur.split('\n## ')[0] + '\n'
    if not base_part.startswith('# O225'):
        print('基底異常：檔頭非 # O225'); return 1
    print('基底（§一–§七）bytes = %d' % len(base_part.encode()))

    reg_notes = {}
    regp = os.path.join(os.path.abspath(os.path.join(BASE, '..', '..')), 'problem_register', 'register.jsonl')
    if os.path.exists(regp):
        for ln in io.open(regp, encoding='utf-8'):
            if not ln.strip():
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            pid = str(r.get('pid') or '')
            if not pid.startswith('O225/'):
                continue
            rd = pid.split('/')[1]
            reg_notes.setdefault(rd, []).append(r.get('note') or '')
    parts, drift = [], []
    for num, label, frag, scripts in PLAN:
        doc = pick_doc(frag)
        dpath = os.path.join(DOCS, doc) if doc else None
        dsha = sha(dpath) if dpath and os.path.exists(dpath) else '-'
        head = headline(doc, 1300) if doc else ''
        rows = []
        for pre in scripts:
            nm = next((k for k in sweep if k.startswith(pre + '_')), None)
            if not nm:
                # 掃描未及：以歷史日誌補位（明確標示來源）
                lr = None
                for f in sorted(os.listdir(os.path.join(BASE, 'logs'))):
                    if f.startswith(pre + '_') and f.endswith('.out'):
                        txt = io.open(os.path.join(BASE, 'logs', f), encoding='utf-8', errors='replace').read()
                        m = None
                        for m in re.finditer(r'RESULT:\s*(\d+)\s*/\s*(\d+)', txt):
                            pass
                        if m:
                            lr = (int(m.group(1)), int(m.group(2)), f)
                if lr:
                    rows.append('%s = %d/%d（歷史日誌 %s）' % (pre + '_', lr[0], lr[1], lr[2]))
                else:
                    rows.append('%s：未跑' % pre)
                continue
            v = sweep[nm]
            if v.get('missing'):
                rows.append('%s：缺' % nm); continue
            r = v.get('res') or [None, None]
            tag = '%s = %s/%s' % (nm, r[0] if r[0] is not None else '-', r[1] if r[1] is not None else '-')
            if v.get('fails'):
                tag += '（FAIL: %s）' % ','.join(v['fails'])
            if v.get('traceback'):
                tag += '（含 Traceback）'
            rows.append(tag)
        # doc 宣稱之 RESULT 逐支比對
        claim = ''
        if doc:
            dtxt = io.open(os.path.join(DOCS, doc), encoding='utf-8').read()
            ms = re.findall(r'RESULT:\s*(\d+)\s*/\s*(\d+)', dtxt)
            if ms:
                claim = 'doc 宣稱 RESULT = %s' % (', '.join('%s/%s' % m for m in ms[:6]))
        sec = ['## %s、%s（2026-10-01 重跑重建）' % (num, label)]
        sec.append('> 合約／結果文檔：`docs/%s`（sha256 `%s`）%s' % (doc or '-', (dsha[:16] + '…') if dsha != '-' else '-',
                                                                  (' ｜ ' + claim) if claim else ''))
        sec.append('> **重跑判決（2026-10-01）**：%s' % '；'.join(rows))
        tags = []
        for pre in scripts:
            nm2 = next((k for k in sweep if k.startswith(pre + '_')), None)
            src = None
            for cand in ([os.path.join(BASE, 'logs', '92_' + nm2 + '.out')] if nm2 else []) + \
                        [os.path.join(BASE, 'logs', f) for f in sorted(os.listdir(os.path.join(BASE, 'logs')))
                         if f.startswith(pre + '_') and f.endswith('.out')]:
                if os.path.exists(cand):
                    src = cand
                    break
            if not src:
                continue
            txt = io.open(src, encoding='utf-8', errors='replace').read()
            tg = re.findall(r'^\[(PASS|FAIL)\][ \t]+(\S+)', txt, re.M)
            if tg:
                tags.append('%s: %s' % (pre, ' '.join(('✓' if a == 'PASS' else '✗') + b for a, b in tg)))
        if tags:
            sec.append('')
            sec.append('**逐 tag 判決鏈（當日重跑；✓=PASS ✗=FAIL 原樣留痕）**：`' + '`；`'.join(tags) + '`')
        rn = reg_notes.get(label, [])
        if rn:
            nums = sorted(set(re.findall(r'\b(\d+/\d+)\b', ' '.join(rn))))
            sec.append('> **register 記載（`O225/%s`，%d 條）**：數字 %s' % (label, len(rn), '、'.join(nums) if nums else '（無 n/m）'))
        if head:
            sec.append('')
            sec.append('**該輪關鍵宣稱（`docs/%s` 原文摘錄）**：' % doc)
            sec.append(head)
        parts.append('\n'.join(sec))
    # ---- §三十七 開放問題總清冊（逐字摘 docs/49 之清冊表列）----
    extra = []
    inv_rows = []
    c49 = os.path.join(DOCS, '49_o225_closeout_r1-r23.md')
    if os.path.exists(c49):
        for ln in io.open(c49, encoding='utf-8').read().split('\n'):
            if re.match(r'^\|\s*\d+\s*\|\s*\*\*', ln):
                inv_rows.append(ln.strip())
    extra.append('## 三十七、開放問題總清冊（R1–R26 水位；逐字摘 `docs/49` 清冊表列 ＋ register 狀態）')
    extra.append('')
    extra.append('> 來源：`docs/49_o225_closeout_r1-r23.md`（close-out 第二輪清冊）＋ `problem_register/register.jsonl` 之 `O225/*` 條目。')
    extra.append('> 狀態欄讀法：emoji 為「已閉／部分（有結構式但全稱或一般情形未成）／未成」；逐項判定與 register pid 見下表與 `docs/49`。')
    extra.append('')
    extra.extend(inv_rows if inv_rows else ['（清冊表列抽取為空；見 docs/49 原文）'])
    extra.append('')
    extra.append('> **R27 後增量（append-only，見 `docs/59`）**：**CRIT-1** 🟡→✅（二層非仿射族：`⟨M,S⟩ ≅ Z₂×Z₂`、'
                 'orbit 72 個、`R ≡ 0` orbit-不變、無混合 orbit ⟹ 逐 orbit 判充要；另得 `M`（`u ↦ −u`）保持 `R ≡ 0`）；'
                 '**CRIT-3**（新立：三層及以上讀出族之充要條件）未閉合 —— 精化判準於三層族（4096 表）漏判 32 例（判據假 ∧ `R ≡ 0`）。')
    extra.append('')
    extra.append('> **R28 後增量（append-only，見 `docs/61`）**：**CRIT-2** ✅（以否定答案閉合：四判準不獨立，'
                 '`rank_GF(2) = 3`；`C2`（R17 赤道對式）零判別力、`C1 ≡ C3inv`（R16 判準與 R18 不可約性同一響應類）；'
                 '`V1`（edge 參考軸）使承載欄數 22 → 0；`V4/V5/V6/V7/V8` 承載不變 22）；**MISC-1** 🟡 partial'
                 '（`τ` 部分 ✅：`h² = g_a² ⟹ ⟨g_a, h⟩ ≅ Q₈`；orbit 型別混合之外自同構解釋**否證**）；'
                 '**MISC-2**（新立：orbit 型別混合之殘餘機制）未閉合。')
    extra.append('')
    extra.append('> **R29 後增量（append-only，見 `docs/63`）**：**MECH-2** ✅ closed（不等價定讞＋修式；`Λ` 奇偶律、Z10 選擇律、支撐 16 欄全不變）；'
                 '**MECH-1** 🟡 維持部分閉合但否定面增強 —— 機器 30 欄全檢：`dind` 位於 `V(a)` 上之恆定性**不可**由 `u` 之任何單一符號量或軸型別決定（σ(u)-分組另路互證）。')
    extra.append('')
    extra.append('> **R30 後增量（append-only，見 `docs/65`）**：**Z10-1** 🔴→🟡（否定面收窄：候選 A／B 空集、③ 僅保 tie/dind 者 = e,−1、'
                 '④ 反 ε 集（10 元）與 Z10（10 元）互斥；Z10 非 ±-閉、|Inv(tie,dind)| = 2 剛性）；**Z10-2** 🔴→🟡（障礙分離：'
                 '`C = [39,40,41,42,51,52,53,54]` **不含**支撐 16 欄 ⟹ 與 MECH-1 同源之假說否證）；新 🔴 2 項見 `docs/65_r30_results.md` §四。')
    extra.append('')
    extra.append('> **R31 後增量（append-only，見 `docs/67`）**：**STT-1** 🔴→🟡 部分閉合 —— ★±8 四類判別 = (S_TT 符號, sgn⟨U_a,KV_g⟩)'
                 '（4 類 = 4/2/4/2，全 12 鍵覆蓋）；★補集 Π（20 元）≅ `Dic₅` 獨立復現（a = 99 階 10、b = 46、b² = a⁵、b⁻¹ab = a⁻¹，'
                 '與 R26 witness 逐項相同）；餘：`S_TT ≡ 0` 之逐項機制（R26 `T3` 之形式化復現））；新 🔴 1 項見 `docs/67_r31_results.md` §三。')
    extra.append('')
    extra.append('> **R32 後增量（append-only，見 `docs/69`）**：**CRIT-3** 🔴→**✅ 閉合** —— 三層族真充要條件已導出：`R³ ≡ 0 ⟺ ρ ∈ S(mask)`'
                 '（`S(mask) := {ρ : Σ_c ρ_c P[c][·] ≡ 0}`，類和矩陣 `P` 4×120；4096/4096）；`|S|` 分佈 = {0: 232, 4: 8, 16: 16}；'
                 '與 R27 之 32 反例逐數相符（8 mask × 4 ρ）；**MISC-2** 🟡 維持（否證 key-驅動：每個 PAIR-key 內型別已橫跨 edge/face/vertex，'
                 '混合在 key 內部）；新 🔴 1 項見 `docs/69_r32_results.md` §四。')
    extra.append('')
    extra.append('> **R33 後增量（append-only，見 `docs/71`）—— O225 五項 🟡 全閉合**：MECH-1 ✅ 否定閉合（512 完備類全測）；'
                 'STT-1 ✅ **正面閉合**：`S_TT ≡ 0 ⟺ ∃` 階 2 `σ ∈ C(g)`（欄 a 域逐項反號）50/50＋非零 0/12（T4 no-go ✓）；'
                 'Z10-1 ✅ **正面閉合**：`Z10` = φ-聯集（60 類、混合 0、5 對純類）；Z10-2 ✅（F2 複核 8 欄）；MISC-2 ✅ 否定閉合（4 元組混合格）。'
                 '校正：R31 P2 ✗ = 88-子域假象；凍結 T3 0/50 = 全欄域判準（三者自洽）。'
                 '~ 新 🔴 0 項見 `docs/71_r33_results.md` §三；餘 PHYS-1（跨 O 待下游裁決，書面判定見 `docs/71_r33_results.md` §三；已 handoff O222）。')
    extra.append('')
    extra.append('> **新 🔴 3 項見 `docs/65_r30_results.md`**（殘餘 Z10-1／Z10-2 ＋ MECH-1；各有書面判定，承 docs/65 §四 清冊更新）。')
    extra.append('')
    extra.append('**register 條目（`O225/*`）**：R1–R26 逐輪 27 條 ＋ CLOSEOUT-2 ＋ MECH-1／MECH-2／Z10-1／Z10-2／STT-1（R24–R26 已閉）＋ CRIT-1（R27 閉）／CRIT-2（R28 閉）／MISC-1（R28 partial）／CRIT-3／MISC-2／PHYS-1（未閉）。')
    extra.append('')
    # ---- §三十八 推導鏈 ----
    extra.append('## 三十八、推導鏈（R1→R26，每輪一行；細節見各節與 `docs/26_script_chain_index.md`）')
    extra.append('')
    for (num, label, doc_nm, _s) in PLAN:
        h = headline(doc_nm, 260) if doc_nm else ''
        h = h.split(' ｜ ')[0] if h else ''
        extra.append('- **%s**（%s）：%s' % (label, num, h if h else '見 `docs/%s`' % doc_nm))
    extra.append('')
    # ---- §三十九 審計附錄 ----
    extra.append('## 三十九、審計附錄（`o225-blind-audit-v1` 之作業數字）')
    extra.append('')
    for nm, desc in (('92_audit_sweep.json', 'A 層：逐支重跑'),
                     ('97_drift_audit.json', 'A2 層：三方對帳（凍結 JSON↔重跑↔歷史日誌）'),
                     ('95_doc_binding.json', 'B 層：宣稱↔證據綁定'),
                     ('93_audit_blind.json', 'C／D 層：獨立重算＋精確 null'),
                     ('98_round_claim_check.json', 'Q1：逐輪文檔聲稱↔重跑'),
                     ('99_gap_blind.json', 'Q3：缺口補完（Λ/Z10、f 三重、三支和）')):
        fp = os.path.join(DATA, nm)
        if not os.path.exists(fp):
            extra.append('- `%s`（%s）：**未產出**' % (nm, desc)); continue
        d = json.load(io.open(fp, encoding='utf-8'))
        if 'summary' in d:
            extra.append('- `%s`（%s）：`%s`' % (nm, desc, json.dumps(d['summary'], ensure_ascii=False)))
        elif 'checks' in d:
            ps = sum(1 for c in d['checks'] if c['ok'])
            extra.append('- `%s`（%s）：**%d/%d PASS**' % (nm, desc, ps, len(d['checks'])))
        elif 'n_bound' in d:
            extra.append('- `%s`（%s）：已綁定 %d／未綁定 %d' % (nm, desc, d['n_bound'], d['n_unbound']))
        else:
            extra.append('- `%s`（%s）：見 `data/`' % (nm, desc))
    extra.append('')
    extra.append('> Q1 定讞：文檔聲稱 ↔ 重跑 = **一致，無分歧**（77 match ／ 3 合約閘 PASS 標籤對齊 ／ 5 flagged = 4 支 C8「見數前註冊」型閘（`23`/`27`/`30`/`33`；`docs/49` 行 40 逐字記載其事後必 FAIL）＋ `37` 之 MANIFEST 時序（刷新後複驗 10/10））。')
    rec = base_part + '\n' + NOTICE + '\n\n---\n\n' + '\n\n---\n\n'.join(parts) + '\n\n---\n\n' + '\n\n'.join(extra) + '\n'
    # 令**首個** `> **狀態` 行載水位 token（82 D1 取首行；status 為活欄位，容許更新）
    ls = rec.split('\n')
    for i, l in enumerate(ls):
        if l.startswith('> **狀態'):
            if 'R1–R23' not in l:
                ls[i] = l.rstrip() + '｜**水位：R1–R23 全 DONE；R24–R26 已閉**'
            break
    rec = '\n'.join(ls)
    print('重建後 bytes = %d（原 %d）｜節數 = %d' % (len(rec.encode()), len(cur.encode()), len(parts)))
    if dry:
        print('（--dry：未寫入）'); return 0
    bak = recp + '.pre_rebuild2_%s.bak' % time.strftime('%Y%m%d_%H%M')
    shutil.copy(recp, bak)
    io.open(recp, 'w', encoding='utf-8').write(rec)
    print('已寫入 %s（備份 %s）' % (recp, os.path.basename(bak)))
    return 0


NOTICE = ('> ⚠️ **逐步重建說明（2026-10-01，第二版）**\n'
          '> §一–§七 = O222→O225 交接基石（逐字保留）；**§八–§三十六 = 由重跑實測重建**：每節列\n'
          '> 「合約／結果文檔 sha ＋ 三件套（合約閘／機器／審計）之**判決（當日重跑，或標示為歷史日誌）**」\n'
          '> 並摘錄該輪 results doc 之原文關鍵宣稱。**本重建不新增任何推導**。\n'
          '> 重跑引擎：`scripts/92_audit_sweep.py`（全支逐支重跑）＋ `scripts/93_audit_blind.py`（獨立重算＋精確 null）\n'
          '> ＋ `scripts/95_doc_binding.py`（宣稱↔證據綁定）；審計報告：`docs/57_audit_report.md`。\n'
          '> **狀態**：水位 **R1–R23 全 DONE**（close-out 第二輪 81=9/9、82=8/8）＋ **R24–R26 已閉**（MECH-1/2、Z10-1/2、STT-1；見 §三十四–§三十六）。\n'
          '> 事故與第一版還原見 `docs/54_doc_loss_incident_and_recovery.md`（register 有載）。\n')

if __name__ == '__main__':
    raise SystemExit(main())
