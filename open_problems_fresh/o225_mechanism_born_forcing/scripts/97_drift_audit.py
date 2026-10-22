#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/97 -- 漂移對帳：凍結 data JSON ↔ 當日重跑 ↔ 歷史日誌（三方）。

分類：match（三方一致）／drift_counts（n/m 不同）／drift_tags（n/m 同但 FAIL tag 集不同）／
      no_frozen（無凍結 JSON 可對）／no_log（無歷史日誌）。唯讀；出 data/97_drift_audit.json。
用法: /usr/bin/python3 scripts/97_drift_audit.py
"""
import io, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
D, L = os.path.join(BASE, 'data'), os.path.join(BASE, 'logs')
SW = json.load(io.open(os.path.join(D, '92_audit_sweep.json'), encoding='utf-8'))
RES_RE = re.compile(r'RESULT:\s*(\d+)\s*/\s*(\d+)')
FAIL_RE = re.compile(r'^\[FAIL\]\s*(\S+)', re.M)


def frozen(num):
    for f in sorted(os.listdir(D)):
        if f.startswith(num + '_') and f.endswith('.json'):
            try:
                d = json.load(io.open(os.path.join(D, f), encoding='utf-8'))
            except Exception:
                continue
            r = None
            if isinstance(d.get('res'), list) and len(d['res']) == 2 and all(isinstance(x, int) for x in d['res']):
                r = tuple(d['res'])
            elif isinstance(d.get('pass'), int) and isinstance(d.get('total'), int):
                r = (d['pass'], d['total'])
            elif isinstance(d.get('checks'), list) and d['checks']:
                r = (sum(1 for c in d['checks'] if (c.get('ok') if isinstance(c, dict) else c)), len(d['checks']))
            if r:
                return {'file': f, 'res': r, 'fails': sorted(d.get('fails') or [])}
    return None


def hist(num, name):
    for f in sorted(os.listdir(L)):
        if f.startswith(num + '_') and f.endswith('.out') and not f.startswith('92_'):
            t = io.open(os.path.join(L, f), encoding='utf-8', errors='replace').read()
            ms = list(RES_RE.finditer(t))
            if ms:
                return {'file': f, 'res': (int(ms[-1].group(1)), int(ms[-1].group(2))),
                        'fails': sorted(set(FAIL_RE.findall(t)))}
    return None


def main():
    rows = []
    for name in sorted(SW):
        v = SW[name]; num = name[:2]
        if not num.isdigit():
            continue
        rr = v.get('res')
        # [null,null] 視為「不以 RESULT 行表態」（合約閘）——不可當成 (None,None) 元組
        run = {'res': (tuple(rr) if (rr and all(isinstance(x, int) for x in rr)) else None),
               'fails': sorted(v.get('fails') or [])}
        fz, hi = frozen(num), hist(num, name)
        tags_diff = bool(hi and run['fails'] != hi['fails'])
        pt = v.get('pass_tags')
        if run['res'] is None and fz and isinstance(pt, int) and pt == fz['res'][0] and fz['res'][0] == fz['res'][1]:
            cls = 'match_gate'          # 合約閘：不以 RESULT 行表態，改以 PASS 標籤數對齊凍結 JSON
        elif run['res'] is None:
            cls = 'no_result'
        elif fz and run['res'] != fz['res']:
            cls = 'drift_counts'
        elif fz and run['fails'] and fz['fails'] and run['fails'] != fz['fails']:
            cls = 'drift_tags'
        elif hi and run['res'] != hi['res']:
            cls = 'drift_vs_log'
        elif tags_diff:
            cls = 'drift_tags_vs_log'
        elif tags_diff is False and hi:
            cls = 'match_log'
        elif fz:
            cls = 'match_frozen'
        else:
            cls = 'no_evidence'
        rows.append({'script': name, 'run': run, 'frozen': fz, 'hist': hi, 'class': cls})
    summ = {}
    for r in rows:
        summ[r['class']] = summ.get(r['class'], 0) + 1
    out = {'script': '97_drift_audit', 'summary': summ, 'rows': rows}
    io.open(os.path.join(D, '97_drift_audit.json'), 'w', encoding='utf-8').write(json.dumps(out, indent=1, ensure_ascii=False))
    print('=' * 112)
    print('O225 scripts/97 -- 三方對帳（凍結 JSON ↔ 當日重跑 ↔ 歷史日誌）；共 %d 支' % len(rows))
    print('=' * 112)
    print('分類 = %s' % summ)
    ml = [r for r in rows if r['class'] in ('match_log', 'match_gate')]
    print('match（重跑↔歷史日誌 n/m 及 FAIL tag 集全同，或合約閘 PASS 標籤對齊凍結 JSON）= %d 支' % len(ml))
    for c in ('drift_counts', 'drift_tags', 'drift_vs_log', 'drift_tags_vs_log', 'match_gate', 'no_evidence', 'no_result'):
        bad = [r for r in rows if r['class'] == c]
        if not bad:
            continue
        print('\n[%s] %d 支：' % (c, len(bad)))
        for r in bad[:30]:
            print('  %-26s 重跑=%s 凍結=%s 日誌=%s' % (r['script'], r['run']['res'],
                  (r['frozen'] or {}).get('res'), (r['hist'] or {}).get('res')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
