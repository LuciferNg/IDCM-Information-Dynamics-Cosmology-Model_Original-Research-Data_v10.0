#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O225 scripts/123 -- R33 收口批之 register 批次（list-form subprocess，無 shell quoting）。
用法: /usr/bin/python3 scripts/123_r33_register_batch.py   （由作業層以 execute_code 視需要增補久執行）"""
import io
import json
import os
import subprocess
import sys

R0 = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
P = R0 + '/problem_register/register.py'
REF = 'open_problems_fresh/o225_mechanism_born_forcing/docs/71_r33_results.md'
N1 = '閘 120=5/5 OPEN；機器 121=7/7；審計 122=4/4。MECH-1 否定閉合（512 完備類全測）；STT-1 正面閉合（S_TT為0 ⟺ 階2 centralizer 對合；50/50 且非零 0/12）；Z10-1 正面閉合（Z10 = φ-聯集；5 對純類）；Z10-2 閉合（F2 複核）；MISC-2 否定閉合（4 元組混合格）。校正：R31 P2 ✗ = 88-子域假象；凍結 T3 0/50 = 全欄判準。'
N2 = '否定閉合：512 完備候選類（7 符號分量子集乘積 × 零/型別過濾）全 30 T-欄無一與 const8 相符 ⟹ dind 於 V(a) 恆定不由 u 之符號結構（本類）決定。'
N3 = '正面閉合：S_TT(a,g)=0 ⟺ 存在階 2 σ∈C(g)（欄 a 域、tie/dind 不變、逐項反號）：零鍵 50/50、非零 0/12（T4 no-go 複核 ✓）。校正：R31 P2 ✗ = 88-子域假象；凍結 T3 0/50 = 全欄判準域（三者自洽）。'
N4 = '正面閉合：全作用簽名 φ 之等價類 60、Z10 混合類 0 ⟹ Z10 = φ-聯集；Z10 展 5 純類（各 2 元：9/21、15/31、57/67、77/87、111/117）。'
N5 = '閉合：F2 複核 const8=[39,40,41,42,51,52,53,54]（30 T-欄）⟹ W_a 為空 ⟺ dind 於 V(a) 恆定；機制殘餘 ≡ MECH-1（已否定閉合）。'
N6 = '否定閉合：混合 orbit 內 4 元組簽名格含混合型別格（例 (1,-1,-1,1) 含 edge/face/vertex）⟹ 4 元組之任何函數不可分型別。'


_LEDGER = os.path.join(R0, 'problem_register', 'register.jsonl')


def _seen(pid, kind, ref):
    try:
        for line in io.open(_LEDGER, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            if e.get('pid') == pid and e.get('kind') == kind and e.get('ref') == ref:
                return True
    except Exception:
        return False
    return False


def run(args):
    pid = args[1] if len(args) > 1 else ''
    kind = args[0]
    ref = None
    for i, a in enumerate(args):
        if a == '--ref' and i + 1 < len(args):
            ref = args[i + 1]
    if ref and _seen(pid, kind, ref):
        print('skip(已存在) %s %s %s' % (kind, pid, ref), flush=True)
        return
    r = subprocess.run(['/usr/bin/python3', P] + args, capture_output=True, text=True, cwd=R0)
    print((r.stdout + r.stderr).strip().splitlines()[-1][:140], flush=True)


def main():
    run(['register', '--pid', 'O225/R33', '--title',
         'R33：五項 🟡 收口批（MECH-1/STT-1/Z10-1/Z10-2/MISC-2 全閉合）', '--state', 'closed', '--ref', REF, '--note', N1])
    run(['close', '--pid', 'O225/MECH-1', '--ref', REF, '--note', N2])
    run(['close', '--pid', 'O225/STT-1', '--ref', REF, '--note', N3])
    run(['close', '--pid', 'O225/Z10-1', '--ref', REF, '--note', N4])
    run(['close', '--pid', 'O225/Z10-2', '--ref', REF, '--note', N5])
    run(['close', '--pid', 'O225/MISC-2', '--ref', REF, '--note', N6])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())