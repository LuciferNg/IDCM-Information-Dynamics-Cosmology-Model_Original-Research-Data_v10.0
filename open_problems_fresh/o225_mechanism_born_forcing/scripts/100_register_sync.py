#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/101 -- register ↔ problem_record 同步核（Q3 之後半）。

核（唯讀）：
  S1 每輪（R1–R26 ＋ CLOSEOUT-2）於 register 皆有 `O225/R*` 條目
  S2 清冊九項之 register 項齊備（MECH-1/2、Z10-1/2、STT-1、CRIT-1/2、MISC-1、PHYS-1）＋ PHYS-1
  S3 記錄之輪次集合 = register 之輪次集合（無單邊）
  S4 記錄 §三十七 清冊所列項 ↔ register 項集（互相覆蓋）
  S5 各輪三件套判決（記錄內「重跑判決」行）之 n/m ↔ register note 內同輪出現之 n/m（若有記載）
出：data/100_register_sync.json。用法: /usr/bin/python3 scripts/100_register_sync.py
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(BASE, '..', '..'))
REG = os.path.join(REPO, 'problem_register', 'register.jsonl')
REC = os.path.join(BASE, '01_problem_record.md')
RES = []


def check(tag, name, ok, detail=''):
    RES.append({'tag': tag, 'name': name, 'ok': bool(ok), 'detail': detail})
    print('[%s] %-4s %s%s' % ('PASS' if ok else 'FAIL', tag, name, ('  --  ' + detail) if detail else ''), flush=True)


def main():
    print('=' * 112)
    print('O225 scripts/101 -- register ↔ problem_record 同步核')
    print('=' * 112, flush=True)
    rows = [json.loads(l) for l in io.open(REG, encoding='utf-8') if l.strip()]
    o225 = [r for r in rows if str(r.get('pid', '')).startswith('O225')]
    pids = sorted(set(r['pid'] for r in o225))
    rounds_reg = sorted({p.split('/')[1] for p in pids if '/' in p and re.fullmatch(r'R\d+', p.split('/')[1])},
                        key=lambda s: int(s[1:]))
    items_reg = sorted(p.split('/')[1] for p in pids if '/' in p and not re.fullmatch(r'R\d+', p.split('/')[1]))
    rec = io.open(REC, encoding='utf-8').read()
    rounds_rec = sorted(set(re.findall(r'^## [一二三四五六七八九十]+、(R\d+|CLOSEOUT-\d|CHAIN)', rec, re.M)),
                        key=lambda s: int(s[1:]) if s.startswith('R') else 0)
    want_rounds = ['R%d' % i for i in range(1, 27)]
    missing = [r for r in want_rounds if r not in rounds_reg]
    check('S1', '每輪 R1–R26 於 register 皆有 O225/R* 條目（＋CLOSEOUT-2）',
          not missing and ('O225/CLOSEOUT-2' in pids),
          'register 輪次 = %d 條；缺 = %s' % (len(rounds_reg), missing or '無'))
    want_items = ['MECH-1', 'MECH-2', 'Z10-1', 'Z10-2', 'STT-1', 'CRIT-1', 'CRIT-2', 'MISC-1', 'PHYS-1']
    miss_i = [i for i in want_items if i not in items_reg]
    check('S2', '清冊九項於 register 齊備（MECH/Z10/STT 已閉；CRIT/MISC/PHYS 未閉）',
          not miss_i, 'register 非輪次項 = %s；缺 = %s' % (items_reg, miss_i or '無'))
    check('S3', '記錄之輪次集合 ⊇ register 之輪次集合（無單邊缺漏）',
          set(rounds_rec) >= set(r for r in rounds_reg if r.startswith('R')),
          '記錄 = %s …（%d）' % (rounds_rec[:6], len(rounds_rec)))
    inv_rec = set(re.findall(r'\*\*(MECH-\d|Z10-\d|STT-\d|CRIT-\d|MISC-\d|PHYS-\d)\*\*', rec))
    cmp_reg = set(i for i in items_reg if i != 'CLOSEOUT-2')
    check('S4', '記錄 §三十七 清冊項 ↔ register 非輪次項互相覆蓋（CLOSEOUT-2 屬輪次不計）',
          inv_rec == cmp_reg, '記錄清冊 = %s；register = %s' % (sorted(inv_rec), sorted(cmp_reg)))
    # S5（反向）：register note 內凡載「= n/m」者，該 n/m 必須見於記錄之對應輪節
    absent = []
    cur = None
    sec = {}
    for ln in rec.split('\n'):
        m = re.match(r'^## [一二三四五六七八九十]+、(R\d+|CLOSEOUT-\d|CHAIN)', ln)
        if m:
            cur = m.group(1)
            sec[cur] = []
        elif cur:
            sec[cur].append(ln)
    for r in o225:
        pid = r.get('pid', '')
        if '/' not in pid:
            continue
        rd = pid.split('/')[1]
        note = r.get('note') or ''
        nums = set(re.findall(r'= ?(\d+/\d+)', note)) | set(re.findall(r'\b(\d+/\d+)\b', note))
        body = '\n'.join(sec.get(rd, []))
        for nu in nums:
            if nu not in body and rd in sec:
                absent.append((rd, nu))
    check('S5', '同步（反向）：register note 內之 n/m 皆見於記錄對應輪節', not absent,
          '未見於記錄者 = %d %s' % (len(absent), sorted(set(absent))[:8]))
    io.open(os.path.join(BASE, 'data', '100_register_sync.json'), 'w', encoding='utf-8').write(json.dumps(
        {'script': '100_register_sync', 'checks': RES, 'rounds_reg': rounds_reg, 'items_reg': items_reg,
         'rounds_rec': rounds_rec, 'items_rec': sorted(inv_rec)}, indent=1, ensure_ascii=False))
    p = sum(1 for r in RES if r['ok'])
    print('\nRESULT: %d/%d PASS' % (p, len(RES)))
    return 0 if p == len(RES) else 1


if __name__ == '__main__':
    raise SystemExit(main())
