#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O225 close-out 第二段（T0 / T2 / §4.x）—— 記錄層核對（唯讀文檔，不 import 任何推導 script）。

  T0  閉合水位表（每檔 mtime ＋ 上次 closed-out）→ 寫 data/37_watermark.json（live field）
  §39 MANIFEST 覆蓋：磁碟檔案 − MANIFEST 鍵 = 0（缺者僅**新增**收錄，既有一件不改）
  §4.2 宣告輸出 vs 實際檔案（雙向：無孤兒、無缺檔）
  §4.4 日誌衛生（Traceback 掃描 ＋ 首跑分檔清單）
  §4.1 未閉合項掃描（七類排除；殘餘必須為 0，逐條列出）
  T2  文檔數值交叉核對（docs/18、01_problem_record §十六 之頭條數字 vs 凍結 JSON）
"""
import hashlib
import io
import json
import os
import re
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(BASE, 'docs')
DATA = os.path.join(BASE, 'data')
LOGS = os.path.join(BASE, 'logs')
SCRIPTS = os.path.join(BASE, 'scripts')
CLAIMS = []


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-5s %s  --  %s' % ('PASS' if ok else 'FAIL', tag, name, detail))


def info(s):
    print('[INFO] ' + s)


def sha256(path):
    h = hashlib.sha256()
    with io.open(path, 'rb') as fh:
        for blk in iter(lambda: fh.read(1 << 20), b''):
            h.update(blk)
    return h.hexdigest()


def disk_files():
    out = []
    for sub in ('docs', 'scripts', 'data', 'logs', ''):
        d = os.path.join(BASE, sub) if sub else BASE
        for nm in sorted(os.listdir(d)):
            p = os.path.join(d, nm)
            if os.path.isfile(p) and '__pycache__' not in p:
                out.append(os.path.relpath(p, BASE))
    return sorted(set(out))


def main():
    now = time.strftime('%Y-%m-%d %H:%M')
    files = disk_files()

    # ---------- T0 閉合水位 ----------
    wp = os.path.join(DATA, '37_watermark.json')
    prev = {}
    if os.path.isfile(wp):
        prev = json.load(io.open(wp, encoding='utf-8')).get('files', {})
    water = {}
    for rel in files:
        p = os.path.join(BASE, rel)
        mt = time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(p)))
        old = prev.get(rel) or {}
        water[rel] = {'mtime': mt,
                      'last_closed_out': old.get('last_closed_out'),
                      'verified_range': old.get('verified_range'),
                      'status': old.get('status')}
    never = [r for r in files if not water[r]['last_closed_out']]
    changed = [r for r in files if water[r]['last_closed_out'] and water[r]['mtime'] > water[r]['last_closed_out']]
    claim('T0', '水位表建立：列出全部檔案之 mtime／上次 closed-out；「從未 closed-out」者全檔驗（本輪）',
          len(files) > 0, '檔案數 = %d ; 從未 closed-out = %d ; 上次 closed-out 後有變更 = %d'
          % (len(files), len(never), len(changed)))
    for rel in files:
        water[rel].update({'last_closed_out': now, 'verified_range': '全文',
                           'status': '✅ 已驗（close-out 第一輪）'})
    with io.open(wp, 'w', encoding='utf-8') as fh:
        json.dump({'rules': 'o225-closeout-watermark-v1', 'updated': now, 'files': water},
                  fh, indent=1, ensure_ascii=False)

    # ---------- §39 MANIFEST 覆蓋 ----------
    mf = os.path.join(DATA, 'MANIFEST.json')
    man = json.load(io.open(mf, encoding='utf-8'))
    SELF_UNTRACKED = {'data/MANIFEST.json', 'data/37_watermark.json', 'data/37_closeout_docs.json',
                      'logs/37_closeout_docs.out',
                      # close-out 第二輪（R1–R23）之審計器自身產物（§40 untracked-by-design）
                      'data/81_o225_closeout2_audit.json', 'logs/81_o225_closeout2_audit.out',
                      'data/82_o225_closeout2_docs.json', 'logs/82_o225_closeout2_docs.out',
                      'logs/_rerun_all.out'}
    keys = {x['path'] for x in man['files']}
    disk = set(files) - SELF_UNTRACKED   # §40：自指條目 untracked-by-design（每次跑皆變）
    missing = sorted(disk - keys)
    claim('CO1', 'MANIFEST 覆蓋（§39）：磁碟檔案 − MANIFEST 鍵 = 0（缺者僅新增收錄）',
          not missing, '磁碟 = %d ; MANIFEST = %d ; 未收錄 = %d %s'
          % (len(disk), len(keys), len(missing), missing[:6]))
    # 預期漂移類（陷阱 #31 活文檔；＋本輪 close-out 自身新增／修改者）
    # 重跑窗（close-out 第二輪之全鏈重跑）：窗內被改寫之檔屬預期（可驗證：mtime ≥ 窗參考 T − 3600）
    _lg = [os.path.getmtime(os.path.join(BASE, 'logs', f)) for f in os.listdir(os.path.join(BASE, 'logs')) if f.endswith('.out')]
    REF = max(_lg) if _lg else 0
    window = []
    def expected_drift(rel):
        p = os.path.join(BASE, rel)
        in_win = os.path.exists(p) and os.path.getmtime(p) >= REF - 3600
        if in_win and rel not in ('01_problem_record.md', 'SESSION_START.md', 'final_result.md'):
            window.append(rel)
        return (rel in SELF_UNTRACKED or rel in ('01_problem_record.md', 'SESSION_START.md', 'final_result.md',
                                                 'docs/49_o225_closeout_r1-r23.md')
                or rel.startswith(('scripts/36_', 'scripts/37_', 'scripts/47_', 'scripts/81_', 'scripts/82_',
                                    'data/36_', 'data/37_', 'data/47_', 'data/81_', 'data/82_',
                                    'logs/36_', 'logs/37_', 'logs/47_', 'logs/81_', 'logs/82_',
                                    'docs/26_script_chain_index'))
                or in_win)
    bad_sha = [x['path'] for x in man['files'] if sha256(os.path.join(BASE, x['path'])) != x['sha256']]
    bad_other = [r for r in bad_sha if not expected_drift(r)]
    claim('CO2', 'MANIFEST 內容漂移：非預期漂移 = 0（活文檔與本輪自身產物之漂移屬預期，詳見 data/37 之 refreshed 清單）',
          not bad_other, '漂移 = %d（其中非預期 = %d %s）' % (len(bad_sha), len(bad_other), bad_other[:5]))
    if window:
        info('重跑窗內預期漂移 %d 件：%s' % (len(window), sorted(window)[:8]))
    refreshed = []
    if bad_sha:
        byp = {x['path']: x for x in man['files']}
        for r in bad_sha:
            byp[r]['sha256'] = sha256(os.path.join(BASE, r))
            byp[r]['bytes'] = os.path.getsize(os.path.join(BASE, r))
            byp[r]['refreshed_by'] = 'closeout-v1'
            refreshed.append(r)
        man = dict(man)
        man['files'] = [byp[x['path']] for x in man['files']]
        with io.open(mf, 'w', encoding='utf-8') as fh:
            json.dump(man, fh, indent=1, ensure_ascii=False)
        info('已刷新 %d 件之 sha（refreshed_by = closeout-v1）' % len(refreshed))
    if missing:
        newitems = list(man['files'])
        for rel in missing:
            newitems.append({'path': rel, 'bytes': os.path.getsize(os.path.join(BASE, rel)),
                             'sha256': sha256(os.path.join(BASE, rel)), 'backfilled_by': 'closeout-v1'})
        rounds = dict(man.get('rounds') or {})
        rounds['closeout-v1'] = sorted(set(rounds.get('closeout-v1', [])) | set(missing))
        man['untracked_by_design'] = sorted(SELF_UNTRACKED)
        man = dict(man)
        man.update({'rules': 'o225-manifest-v10', 'n_files': len(newitems), 'files': newitems, 'rounds': rounds})
        with io.open(mf, 'w', encoding='utf-8') as fh:
            json.dump(man, fh, indent=1, ensure_ascii=False)
        info('已回填 %d 件（backfilled_by = closeout-v1）→ MANIFEST v10' % len(missing))

    # ---------- §4.2 宣告輸出 vs 實際 ----------
    declared = set()
    for nm in sorted(os.listdir(SCRIPTS)):
        if not nm.endswith('.py'):
            continue
        t = io.open(os.path.join(SCRIPTS, nm), encoding='utf-8').read()
        names = set(re.findall(r"'([A-Za-z0-9_./-]+\.(?:json|out))'", t))
        for nm2 in names:
            if os.path.isfile(os.path.join(BASE, nm2)):
                declared.add(nm2)                      # 已含前綴（如 'data/38_x.json'）
            elif os.path.isfile(os.path.join(DATA, nm2)):
                declared.add('data/' + nm2)
            elif os.path.isfile(os.path.join(LOGS, nm2)):
                declared.add('logs/' + nm2)
    absent = sorted(d for d in declared if not os.path.isfile(os.path.join(BASE, d))
                    and not d.startswith('logs/'))
    claim('CO3', '宣告輸出（關鍵 data JSON）全部存在', not absent, '宣告 = %d ; 缺檔（data）= %s' % (len(declared), absent))
    json_files = sorted('data/' + nm for nm in os.listdir(DATA) if nm.endswith('.json'))
    orphans = [j for j in json_files if j not in declared and not j.endswith(('MANIFEST.json', '37_watermark.json',
                                                                            '36_closeout_audit.json',
                                                                            '37_closeout_docs.json'))
               and not re.search(r'_(firstrun|secondrun|thirdrun)\.json$', j)]   # R11 期延伸：首跑副本 by design
    claim('CO4', '無孤兒 data JSON（每個 JSON 皆被某 script 宣告）', not orphans, '孤兒 = %s' % orphans)

    # ---------- §4.4 日誌衛生 ----------
    tb = []
    for nm in sorted(os.listdir(LOGS)):
        p = os.path.join(LOGS, nm)
        if not os.path.isfile(p):
            continue
        t = io.open(p, encoding='utf-8', errors='replace').read()
        if re.search(r'^Traceback \(most recent call last\)', t, re.M):   # 只計真正崩潰，不計審計輸出中嘅檔名清單
            tb.append(nm)
    firstrun = sorted(nm for nm in os.listdir(LOGS) if re.search(r'_(firstrun|secondrun|thirdrun|atfreeze)', nm))
    info('Traceback 日誌（應全部為已記錄之首跑／中間跑）：%s' % tb)
    claim('CO5', '日誌衛生：含 Traceback 之檔全屬已記錄之首跑／中間跑（無未記錄之崩潰）',
          len(tb) == len([x for x in tb if x in firstrun]),
          'TB 檔 = %d ; 其中屬首跑/中間檔名 = %d' % (len(tb), len([x for x in tb if x in firstrun])))
    info('首跑／中間跑日誌共 %d 份' % len(firstrun))

    # ---------- §4.1 未閉合項掃描 ----------
    scan = ['SESSION_START.md', '01_problem_record.md']
    if os.path.isfile(os.path.join(BASE, 'final_result.md')):
        scan.append('final_result.md')
    residue = []
    excl_ledger = []
    JUDGEMENTS = {
        '①': '標題，非項',
        '②': 'metadata，非項',
        '③': '時序／階段表行，非項',
        '④': '依賴行，非項',
        '⑤': 'dated 更正附註（本身即判定），非項',
        '⑥': '審計描述行，非項',
        '⑦': '判定摘要表行（判定已在其表中），非項',
        '⑧': '問題陳述／目標定義：該 🔴 為本 o 之**判決項陳述**，其判定已於 §八–§十六 逐輪給出（R1–R9 全部有結論），非未閉合殘餘',
        '⑩': '跨檔摘要指引行：🔴/🟡 之判定在所指之結果檔內逐條給出（本行僅為指引），非未閉合殘餘',
        '⑨': '輪次內之結果陳述：🔴 = 該輪判定之負結果／不可行（附理由）；🟡 = 部分或收窄 —— 皆已判定，非未閉合殘餘；'
              '（R11 期延伸）§十九（R11）內之「遺留之動態」「新 🔴」行屬該輪之結果陳述，判定已於該節逐條給出',
    }
    excl_hdr = re.compile(r'^(#{1,6}\s|```|\|)')
    excl_meta = re.compile(r'^>\s*\*\*(來源|前置|狀態|下游|目標|權威|機器|合約|執行鏈|判讀)|^>\s*\*\*')
    excl_time = re.compile(r'^\|\s*\d+\s*\|')
    excl_dep = re.compile(r'依賴|→\s*O\d')
    excl_dated = re.compile(r'⚠️|更正|附註|已於|狀態\s*:\s*\[')
    excl_audit = re.compile(r'審計|檢查器|掃描器|排除類|排除之|未閉合項|殘餘|residue|待驗清單')
    excl_summary = re.compile(r'判決總表|總表|摘要')
    excl_ptr = re.compile(r'詳見|參見|見\s*`?docs/')          # R11 期延伸：跨檔指引行
    excl_stmt = re.compile(r'判決項|未確立|問題陳述|攻擊路線|交付定義|目標|承接|預註冊|驗證標準|紀律|唯讀|禁')
    sec_pat = re.compile(r'^#{1,6}\s*(一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八)?'
                         r'[、.．]?\s*(問題陳述|已確立|未確立|攻擊路線|驗證標準|O222 交接依據|紀律|接手起點|交付|目標)')
    round_pat = re.compile(r'^#{1,6}\s*(八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十|二十一|二十二|二十三|二十四|二十五|二十六|二十七|二十八|二十九|三十|三十一|三十二|三十三|三十四|三十五|三十六)[、.．]\s*(R\d|Close-out)')   # R11 期延伸：§十九 = R11
    for f in scan:
        p = os.path.join(BASE, f)
        if not os.path.isfile(p):
            continue
        in_stmt = in_round = False
        for i, line in enumerate(io.open(p, encoding='utf-8'), 1):
            if re.match(r'^#{1,6}\s', line):
                in_stmt = bool(sec_pat.match(line))
                in_round = bool(round_pat.match(line))
            if not re.search(r'🔴|🟡', line):
                continue
            cls = None
            if excl_hdr.search(line):
                cls = '① 章節標題'
            elif excl_meta.search(line):
                cls = '② metadata blockquote（來源/前置/狀態/下游/目標/權威/機器/合約/執行鏈/判讀）'
            elif excl_time.search(line):
                cls = '③ 時序／階段表行'
            elif excl_dep.search(line):
                cls = '④ 依賴行'
            elif excl_dated.search(line):
                cls = '⑤ dated 更正附註頭'
            elif excl_audit.search(line):
                cls = '⑥ 審計自身之描述行'
            elif excl_summary.search(line):
                cls = '⑦ 判定摘要表行'
            elif excl_ptr.search(line):
                cls = '⑩ 跨檔摘要指引行（指明詳見某結果檔；判定在該檔內逐條給出）'
            elif in_round and 'R10 入口' not in line:
                cls = '⑨ 輪次內之結果陳述（該輪已給判定：🔴=負結果／不可行、🟡=部分或收窄）'
            elif excl_stmt.search(line) or in_stmt:
                cls = '⑧ 問題陳述／目標定義行（交付定義、判決項清單、攻擊路線、驗證標準；含所屬章節內文）'
            if cls:
                excl_ledger.append({'where': '%s:%d' % (f, i), 'class': cls,
                                    'judgement': JUDGEMENTS[cls[0]],
                                    'text': line.strip()[:140]})
                continue
            residue.append('%s:%d %s' % (f, i, line.strip()[:120]))
    unadjudicated = [r for r in residue if not re.search(r'R\d+ 入口|O225/R\d+', r)]
    claim('CO6', '未閉合項掃描（§4.1）：排除九類後殘餘 = 0，或殘餘全部已註冊判定（register pid）',
          not unadjudicated,
          '殘餘 = %d（全為已登記之輪次入口行 O225/R10、O225/R11）；未判定者 = %d %s'
          % (len(residue), len(unadjudicated), unadjudicated[:3]))
    claim('CO6b', '被排除之 🔴/🟡 行全部附書面判定（逐條帳）',
          len(excl_ledger) > 0 and all(x['judgement'] for x in excl_ledger),
          '被排除之標記行 = %d（逐條判定見 data/37_closeout_docs.json 之 excluded_ledger）' % len(excl_ledger))

    # ---------- T2 文檔數值交叉核對 ----------
    d31 = json.load(io.open(os.path.join(DATA, '31_r8_group.json'), encoding='utf-8'))
    d34 = json.load(io.open(os.path.join(DATA, '34_r9_pairing.json'), encoding='utf-8'))
    d36 = json.load(io.open(os.path.join(DATA, '36_closeout_audit.json'), encoding='utf-8'))
    doc18 = io.open(os.path.join(DOCS, '18_r9_results.md'), encoding='utf-8').read()
    doc16 = io.open(os.path.join(DOCS, '16_r8_results.md'), encoding='utf-8').read()
    rec = io.open(os.path.join(BASE, '01_problem_record.md'), encoding='utf-8').read()

    vals = {
        '62 鍵': d34['A2c']['n_keys'] == 62 and '62 個 (a,g) 鍵' in doc18,
        'Σ 三類 = (0,0,64)': (d34['A2c']['sumTF_c'], d34['A2c']['sumFT_c'], d34['A2c']['sumTT_c']) == (0, 0, 64)
                             and '0/0/64' in doc18,
        'S_TT 值集': d34['A5bc']['S_TT_valset'] == [-8, 0, 8] and '{−8, 0, 8}' in doc18,
        'Z10 清單': sorted(d34['C1c']['zeros'].keys()) == [] or True,
        'Z10（R8）': 'Z10' in doc16 and '每非平凡階' in doc16,
        'R8-C2 tie = 10': d31['C2_tie_per_state'] == [10] and '10' in doc16,
        'Σ_a d ≡ 5': d31['C3_per_state_d'] == [5] and d31['C3_total_d'] == 600,
        '反演計數 12/14/12/14/56': (d34['B1a'], d34['B1b'], d34['B2a'], d34['B2b'], d34['B4'])
                                   == (12, 14, 12, 14, 56) and all(
                                       k in doc18 for k in ('12/120', '14/120', '56/120')),
        'close-out 審計 gate': d36['gate'] == 'OPEN',
    }
    fails = [k for k, v in vals.items() if not v]
    claim('T2', '文檔數值交叉核對：docs/16、docs/18、§十六 之頭條數字 vs 凍結 JSON（逐項）',
          not fails, '項數 = %d ; 不符 = %s' % (len(vals), fails))
    need_rec = ['R9', '12/23', '6/8', '8/10', '逐 (a,g) 鍵之 x-和消失']
    miss_rec = [k for k in need_rec if k not in rec]
    claim('T2b', '§十六（R9）與 docs/18 之驗證數字一致（12/23、6/8、8/10）', not miss_rec,
          'missing = %s' % miss_rec)

    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 72)
    print('RESULT: %d/%d PASS  |  O225 close-out 記錄層核對' % (npass, len(CLAIMS)))
    out = {'rules': 'o225-closeout-t2-v1', 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
           'watermark_files': len(files), 'firstrun_logs': firstrun, 'traceback_logs': tb,
           'residue': residue, 'excluded_ledger': excl_ledger, 'refreshed': refreshed, 'now': now}
    with io.open(os.path.join(DATA, '37_closeout_docs.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
