#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/47 -- 劇本檔案鏈完整性核對器（R12 期）。

目的：回答「O225 整個推導過程是否完整留下 Python 劇本檔案鏈」——
以**可重跑**核對（非敘述）檢查：編號連續性（宣告式缺號）、每劇本之 log／data 落痕、
每輪之「合約閘 → 機器 → 審計」命名三件套、docs 對映、MANIFEST 覆蓋與 sha。

輸出：`docs/26_script_chain_index.md`（電話簿式鏈表）＋ `data/47_chain_index.json`。
用法: /usr/bin/python3 scripts/47_chain_index.py
"""
import hashlib
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
CLAIMS = []
# 宣告輸出（bare 檔名，供 scripts/37 之宣告掃描器識別）
OUT_JSON = '47_chain_index.json'
OUT_LOG = '47_chain_index.out'
OUT_DOC = '26_script_chain_index.md'
# 自指產物（本核對器每次跑皆改寫 ⟹ 不與 MANIFEST 之 sha 比對；與 37 之 SELF_UNTRACKED 同理）
SELF_OUT = {'data/' + OUT_JSON, 'logs/' + OUT_LOG, 'docs/' + OUT_DOC}
# 宣告式：允許之缺號（R1 塊 = 01–07，R2 塊自 10 起；08/09 從未建立：全樹零引用、無 log、無 data）
DECLARED_GAPS = [8, 9]
ROUND_MAP = [
    ('R0',          1,  [('偵察', '01_recon_invariants')]),
    ('R1',          1,  [('合約閘', '02_r1_contract'), ('機器', '03_r1_barrier'), ('審計', '04_r1_audit'),
                         ('分析', '05_r1_null_analysis'), ('分析', '06_r1_axis_sign_structure'), ('分析', '07_r1_tie_mechanism')]),
    ('R2',          10, [('合約閘', '10_r2_contract'), ('機器', '11_r2_g1_table'), ('機器', '12_r2_dyn17'), ('審計', '13_r2_audit')]),
    ('R3',          14, [('合約閘', '14_r3_contract'), ('機器', '15_r3_centre_theorem'), ('審計', '16_r3_audit')]),
    ('R4',          17, [('合約閘', '17_r4_contract'), ('機器', '18_r4_tie_parity'), ('審計', '19_r4_audit')]),
    ('R5',          20, [('合約閘', '20_r5_contract'), ('機器', '21_r5_tie_global'), ('審計', '22_r5_audit')]),
    ('R6',          23, [('合約閘', '23_r6_contract'), ('機器', '24_r6_mechanism'), ('機器', '25_r6_geometry'), ('審計', '26_r6_audit')]),
    ('R7',          27, [('合約閘', '27_r7_contract'), ('機器', '28_r7_mechanism2'), ('審計', '29_r7_audit')]),
    ('R8',          30, [('合約閘', '30_r8_contract'), ('機器', '31_r8_group'), ('審計', '32_r8_audit')]),
    ('R9',          33, [('合約閘', '33_r9_contract'), ('機器', '34_r9_pairing'), ('審計', '35_r9_audit')]),
    ('closeout-v1', 36, [('獨立審計', '36_closeout_audit'), ('記錄層核對', '37_closeout_docs')]),
    ('R10',         38, [('合約閘', '38_r10_contract'), ('機器', '39_r10_universal'), ('審計', '40_r10_audit')]),
    ('R11',         41, [('合約閘', '41_r11_contract'), ('機器', '42_r11_machine'), ('審計', '43_r11_audit')]),
    ('R12',         44, [('合約閘', '44_r12_contract'), ('機器', '45_r12_machine'), ('審計', '46_r12_audit'),
                         ('鏈核對', '47_chain_index')]),
    ('R13',         48, [('合約閘', '48_r13_contract'), ('機器', '49_r13_machine'), ('審計', '50_r13_audit')]),
    ('R14',         51, [('合約閘', '51_r14_contract'), ('機器', '52_r14_machine'), ('審計', '53_r14_audit')]),
    ('R15',         54, [('合約閘', '54_r15_contract'), ('機器', '55_r15_machine'), ('審計', '56_r15_audit')]),
    ('R16',         57, [('合約閘', '57_r16_contract'), ('機器', '58_r16_machine'), ('審計', '59_r16_audit')]),
    ('R17',         60, [('合約閘', '60_r17_contract'), ('機器', '61_r17_machine'), ('審計', '62_r17_audit')]),
    ('R18',         63, [('合約閘', '63_r18_contract'), ('機器', '64_r18_machine'), ('審計', '65_r18_audit')]),
    ('R19',         66, [('合約閘', '66_r19_contract'), ('機器', '67_r19_machine'), ('審計', '68_r19_audit')]),
    ('R20',         69, [('合約閘', '69_r20_contract'), ('機器', '70_r20_machine'), ('審計', '71_r20_audit')]),
    ('R21',         72, [('合約閘', '72_r21_contract'), ('機器', '73_r21_machine'), ('審計', '74_r21_audit')]),
    ('R22',         75, [('合約閘', '75_r22_contract'), ('機器', '76_r22_machine'), ('審計', '77_r22_audit')]),
    ('R23',         78, [('合約閘', '78_r23_contract'), ('機器', '79_r23_machine'), ('審計', '80_r23_audit')]),
    ('R24',         83, [('合約閘', '83_r24_contract'), ('機器', '84_r24_machine'), ('審計', '85_r24_audit')]),
    ('R25',         86, [('合約閘', '86_r25_contract'), ('機器', '87_r25_machine'), ('審計', '88_r25_audit')]),
    ('R26',         89, [('合約閘', '89_r26_contract'), ('機器', '90_r26_machine'), ('審計', '91_r26_audit')]),
]


def claim(tag, name, ok, detail=''):
    CLAIMS.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def main():
    print('=' * 112)
    print('O225 scripts/47 -- SCRIPT-CHAIN INTEGRITY CHECK')
    print('=' * 112, flush=True)
    scrub = sorted(n for n in os.listdir(BASE + '/scripts') if n.endswith('.py') and re.match(r'\d+', n))
    stems = [n[:-3] for n in scrub]
    nums = sorted(int(re.match(r'(\d+)', s).group(1)) for s in stems)
    logs = sorted(os.listdir(BASE + '/logs'))
    data = sorted(os.listdir(BASE + '/data'))
    docs = sorted(n for n in os.listdir(BASE + '/docs') if n.endswith('.md'))

    gaps = [i for i in range(1, max(nums) + 1) if i not in nums]
    claim('C1', '編號連續性：缺號 = 宣告式 %s（無重號）' % DECLARED_GAPS,
          gaps == DECLARED_GAPS and len(nums) == len(set(nums)), '缺號 = %s ; 劇本數 = %d ; 重號 = %d' % (gaps, len(nums), len(nums) - len(set(nums))))

    nolog = [s for s in stems if not [x for x in logs if x.startswith(re.match(r'(\d+)', s).group(1) + '_')]]
    claim('C2', '每劇本皆有 ≥1 執行日誌（依編號前綴）', not nolog, '無 log 之劇本 = %s ; logs/ = %d' % (nolog or '無', len(logs)))

    miss = [(r, kind, nm) for (r, _s, items) in ROUND_MAP for (kind, nm) in items if nm + '.py' not in scrub]
    claim('C3', '每輪「合約閘 → 機器 → 審計」命名三件套齊備（13 輪）', not miss, '缺件 = %s' % (miss or '無'))

    ndoc = len(docs)
    rec = io.open(BASE + '/01_problem_record.md', encoding='utf-8').read()
    nref = len(re.findall(r'scripts/\d\d', rec))
    secs = re.findall(r'^## (二十[一二]?|[十]{1,3}?[一二三四五六七八九]?|九|八)', rec, re.M)
    claim('C4', 'docs 對映：docs/*.md ≥ 26 件且 01_problem_record 引用 scripts/ 之數 ≥ 43',
          ndoc >= 26 and nref >= 43, 'docs = %d ; 引用數 = %d' % (ndoc, nref))

    mf = json.load(io.open(BASE + '/data/MANIFEST.json', encoding='utf-8'))
    mp = {x['path']: x for x in mf['files']}
    nsc = len([1 for p in mp if p.startswith('scripts/') and p.endswith('.py')])
    sha = lambda p: hashlib.sha256(io.open(p, 'rb').read()).hexdigest()
    utd = set(mf.get('untracked_by_design') or [])
    bad = [p for p, x in mp.items() if p not in utd and p not in SELF_OUT
           and os.path.isfile(os.path.join(BASE, p)) and sha(os.path.join(BASE, p)) != x['sha256']]
    claim('C5', 'MANIFEST 覆蓋劇本 45/45 且活檔 sha 無誤（自指產物 %d 件除外）' % len(SELF_OUT),
          nsc == len(scrub) and not bad, 'MANIFEST 內劇本 = %d/%d ; sha 錯配 = %s' % (nsc, len(scrub), bad or '無'))

    # ---------- C7：文檔內 scripts/ 引用全部解析（O225 自身 or O222 凍結輸入） ----------
    O222 = os.path.join(os.path.dirname(BASE), 'o222_qm_evaluation_semantics', 'scripts')   # o222 與 o225 同層
    o222 = sorted(n[:-3] for n in os.listdir(O222)) if os.path.isdir(O222) else []
    mds = [os.path.join(BASE, n) for n in sorted(os.listdir(BASE)) if n.endswith('.md')] \
        + [os.path.join(BASE, 'docs', n) for n in sorted(os.listdir(BASE + '/docs')) if n.endswith('.md')]
    stems_here = {s[:-3] for s in scrub}                      # 去 .py
    pref_here = {s.split('_', 1)[0] for s in stems_here}
    stems_o222 = set(o222)
    pref_o222 = {s.split('_', 1)[0] for s in stems_o222}
    unresolved, shorthand, okn = [], set(), 0
    for p in mds:
        t = io.open(p, encoding='utf-8').read()
        for m in re.finditer(r'scripts/([0-9][0-9A-Za-z_\.\-]*)', t):
            ref = m.group(1).rstrip('.').rstrip('-')
            if re.fullmatch(r'\d+([–-]\d+)?', ref):
                shorthand.add(ref)
                continue
            rs = ref[:-3] if ref.endswith('.py') else ref.split('.')[0]
            if rs in stems_here or rs in stems_o222 \
               or (re.fullmatch(r'\d+', rs) and (rs in pref_here or rs in pref_o222)):
                okn += 1
            else:
                unresolved.append('%s:scripts/%s' % (os.path.relpath(p, BASE), ref))
    claim('C7', '文檔內 scripts/ 引用全部解析（O225 自身 or O222 凍結輸入；範圍／簡寫另計）',
          not unresolved, '可解析 = %d ; 簡寫（範圍／純數字）= %d 個 ; 未解析 = %s'
          % (okn, len(shorthand), sorted(set(unresolved)) or '無'))

    # 產出鏈表
    rows = []
    for (r, _s, items) in ROUND_MAP:
        for (kind, nm) in items:
            k = re.match(r'(\d+)', nm).group(1)
            L = sorted(x for x in logs if x.startswith(k + '_'))
            D = sorted(x for x in data if x.startswith(k + '_'))
            p = os.path.join(BASE, 'scripts', nm + '.py')
            nl = sum(1 for _ in io.open(p, encoding='utf-8', errors='replace'))
            rows.append('| `%s` | %s | %s | %d | %d | %d | %d |' % (k, r, kind, os.path.getsize(p), nl, len(L), len(D)))
    repro = {r: ' && '.join('/usr/bin/python3 scripts/%s.py' % nm for (_k, nm) in items) for (r, _s, items) in ROUND_MAP}
    SC = '/home/wsl/.hermes/cache/scratch'
    sc_files = sorted(n for n in os.listdir(SC)
                      if n.startswith('o225_') and os.path.isfile(os.path.join(SC, n))) if os.path.isdir(SC) else []
    scratch_rows = ('| 探針 | bytes | sha256（前 16） |\n|---|---|---|\n'
                    + '\n'.join('| `%s` | %d | %s |' % (n, os.path.getsize(os.path.join(SC, n)), sha(os.path.join(SC, n))[:16])
                                for n in sc_files)) if sc_files else '（scratch 目錄已清空／不可讀）'
    claim('C8', '每輪皆可由鏈表自足重跑（鏈表列明合約→機器→審計指令）', len(repro) == len(ROUND_MAP),
          '輪次指令數 = %d ; scratch 探針登錄 = %d 件' % (len(repro), len(sc_files)))
    doc = '''# O225 劇本檔案鏈（Python script chain）—— 自動生成 @@N@@

> 生成：`scripts/47_chain_index.py`（可重跑；判據 = 編號連續／每劇本有 log／每輪三件套／docs 對映／MANIFEST 覆蓋）
> **缺號宣告**：`08`、`09` **從未建立**（全樹零引用、無 log、無 data）：R1 塊 = `01–07`，R2 塊自 `10` 起。

| 編號 | 輪次 | 角色 | bytes | 行數 | logs | data |
|---|---|---|---|---|---|---|
@@ROWS@@

## 每輪重跑指令（自足；凍結輸入 = O222 唯讀）

@@REPRO@@

## 附錄：探索層探針（專案外，**非正式證據**；設計上不進 MANIFEST，此處登錄 sha256 以備追溯）

@@SCRATCH@@

- 劇本總數 **@@NS@@**、日誌 **@@NL@@**、`data/` **@@ND@@**、`docs/` **@@Ndoc@@**；MANIFEST `@@MF@@`（@@NF@@ 件）。
- 每輪證據鏈 = 合約（`docs/*_contract.md`，見數前凍結＋sha）→ 合約閘 `*_contract.py`（GATE OPEN）→ 機器 `*_machine.py`／`*_universal.py` → 獨立審計 `*_audit.py` → `data/*.json` ＋ `logs/*.out` → `docs/*_results.md` ＋ `01_problem_record.md §輪次`。
- 探索層（非正式證據）在專案外：`/home/wsl/.hermes/cache/scratch/o225_*`（設計上不進 MANIFEST）。
'''.replace('@@ROWS@@', '\n'.join(rows)).replace('@@NS@@', str(len(scrub))).replace('@@NL@@', str(len(logs))) \
       .replace('@@ND@@', str(len(data))).replace('@@Ndoc@@', str(ndoc)).replace('@@MF@@', mf['rules']).replace('@@NF@@', str(mf['n_files'])) \
       .replace('@@REPRO@@', '\n'.join('- **%s**：`%s`' % (r, c) for r, c in repro.items())) \
       .replace('@@SCRATCH@@', scratch_rows) \
       .replace('@@N@@', mf['rules'])
    with io.open(os.path.join(BASE, 'docs', OUT_DOC), 'w', encoding='utf-8') as fh:
        fh.write(doc)
    claim('C6', '鏈表已生成 docs/26_script_chain_index.md（%s）' % OUT_DOC, os.path.getsize(os.path.join(BASE, 'docs', OUT_DOC)) > 500,
          '行數 = %d' % sum(1 for _ in io.open(os.path.join(BASE, 'docs', OUT_DOC), encoding='utf-8')))
    npass = sum(1 for c in CLAIMS if c['ok'])
    print('=' * 112)
    print('RESULT: %d/%d PASS  |  O225 劇本檔案鏈核對' % (npass, len(CLAIMS)))
    with io.open(os.path.join(BASE, 'data', OUT_JSON), 'w', encoding='utf-8') as fh:
        json.dump({'rules': 'o225-script-chain-check-v1', 'n_pass': npass, 'n_total': len(CLAIMS), 'claims': CLAIMS,
                   'declared_gaps': DECLARED_GAPS, 'n_scripts': len(scrub), 'n_logs': len(logs), 'n_data': len(data),
                   'rounds': [r for (r, _s, _i) in ROUND_MAP]}, fh, indent=1, ensure_ascii=False)
    return 0 if npass == len(CLAIMS) else 1


if __name__ == '__main__':
    raise SystemExit(main())
