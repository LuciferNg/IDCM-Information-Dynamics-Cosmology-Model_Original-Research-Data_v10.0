#!/usr/bin/env python3
"""O142 scripts/26 — 未審計文檔/腳本審計引擎（2026-10-24）

範圍（相對 docs/12、17、20、21、27 已審範圍之外）：
  scripts: 15_v17, 15_v18, 16_v22, 17_v23, 18_v24, 19_v25, 20_v26, 21_v27, 22_v28, 23_v29, 24, 25
  docs   : 22,23,24,25,26,28,29,30,31,32,33,34,35,36,37,38,39

Phase A：逐個副程式重跑（每個 timeout 900s），記錄 exit code + PASS/FAIL 行 + 與 doc 宣稱比對
Phase B：由上游原定義獨立重算核心常量（mpmath 60 dps），唔讀任何 doc 數值
Phase C：輸出 JSON 摘要 → data/audit_20261024/summary_26.json

用法: /usr/bin/python3 scripts/26_audit_unaudited.py [--only A|B]
"""
import json
import os
import re
import subprocess
import sys
import time

from mpmath import mp, mpf, sqrt, cos, sin, pi, log

mp.dps = 60
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(HERE, 'data', 'audit_20261024')
LOGDIR = os.path.join(OUTDIR, 'logs')
os.makedirs(LOGDIR, exist_ok=True)

UNAUD = [
    ('15_v17_residual_attack.py', '22_v17_residual_attack.md', None),
    ('15_v18_core_closure.py', '23_v18_core_closure.md', '4/4'),
    ('16_v22_r4_generation_closure.py', '28_v22_r4_generation_closure.md', '5/5'),
    ('17_v23_90_47_samesource.py', '29_v23_90_47_samesource.md', '7/7'),
    ('18_v24_shadow_identity.py', '30_v24_shadow_identity.md', '5/5'),
    ('19_v25_alpha_integer_necessity.py', '31_v25_alpha_integer_necessity.md', '4/4'),
    ('20_v26_z_alpha_tautology.py', '32_v26_z_alpha_tautology.md', '5/5'),
    ('21_v27_residual_mechanism_test.py', '33_v27_residual_mechanism_test.md', '4/4'),
    ('22_v28_counting_fix.py', '34_v28_counting_fix.md', '7/7'),
    ('23_v29_floor_round_integration.py', '35_v29_floor_round_integration.md', '9/9'),
    ('24_lambda_scale_adjudication.py', '36_lambda_scale_adjudication.md', '11/11'),
    ('25_m4_a_identity.py', '38_m4_a_spectral_identity.md', None),
]


def phase_a():
    rows = []
    for script, doc, expect in UNAUD:
        t0 = time.time()
        p = os.path.join(HERE, 'scripts', script)
        try:
            r = subprocess.run(['/usr/bin/python3', p], cwd=HERE, capture_output=True,
                               text=True, timeout=900,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
            out, err, rc = r.stdout, r.stderr, r.returncode
        except subprocess.TimeoutExpired as e:
            t_out = e.stdout or ''
            out = t_out.decode('utf-8', 'replace') if isinstance(t_out, bytes) else t_out
            err, rc = 'TIMEOUT', -9
        dt = time.time() - t0
        logp = os.path.join(LOGDIR, script.replace('.py', '.log'))
        with open(logp, 'w', encoding='utf-8') as fh:
            fh.write(f'# {script}  rc={rc}  {dt:.1f}s\n')
            fh.write(out)
            if err:
                fh.write('\n--- STDERR ---\n' + err)
        # PASS/FAIL 探測（格式 A: "N PASS / M FAIL"；格式 B: "N/M PASS"）
        m = re.findall(r'(\d+)\s*PASS\s*/\s*(\d+)\s*(?:FAIL|FLAG)', out)
        if m:
            got = f'{m[-1][0]}/{m[-1][1]}FAIL'
        else:
            p = re.findall(r'(\d+)\s*/\s*(\d+)\s*(?:PASS|ok|✅)', out, re.I)
            got = f'{p[-1][0]}/{p[-1][1]}' if p else '—'
        n_pass = len(re.findall(r'\[PASS\]|✅', out))
        n_fail = len(re.findall(r'\[FAIL\]|🔴\s*(?:FAIL)', out))
        claimed = expect
        got_pass = int(re.match(r'(\d+)', got).group(1)) if got != '—' else None
        claim_pass = int(claimed.split('/')[0]) if claimed else None
        ok = (rc == 0) and (claim_pass is None or got_pass == claim_pass)
        rows.append(dict(script=script, doc=doc, rc=rc, secs=round(dt, 1),
                         claimed=claimed, got=got, claim_pass=claim_pass, got_pass=got_pass,
                         n_pass_markers=n_pass, n_fail_markers=n_fail,
                         log=os.path.relpath(logp, HERE), verdict='✅' if ok else '🔴'))
        print(f'  {script:38s} rc={rc:2d} {dt:6.1f}s  宣稱={str(claimed):>6s} 實測={got:>6s} '
              f'{"✅" if ok else "🔴"}')
    return rows


def phase_b():
    """獨立重算：全部由 0,1 定義起（唔讀 doc、唔用 script 中間值）"""
    N_d, N_gen, L4, L5, B, F5, F7 = 44, 3, 7, 11, 4, 5, 29   # N_d=44 ⟹ 2N_d=88=ring
    ring = 88
    g1 = 4 * sin(pi / ring) ** 2
    rho = mpf(N_gen) / L5
    g20 = 4 * cos(rho * pi) ** 2
    lam = B * N_gen ** 2 - 1 / g20
    M0 = mpf('27.900915')
    Lam = rho * sqrt(lam) * M0
    g7 = 4 * sin(7 * pi / ring) ** 2
    v = sqrt(lam) * M0 * (2 * N_d) * (2 * F5 + B * L4 * g7) / 1000  # GeV
    checks = [
        ('γ₁', g1, '0.0050957707794929', 1e-14),
        ('γ₂₀=4cos²(ρπ)', g20, '1.71537032345343', 1e-14),
        ('λ_max=36−1/γ₂₀', lam, '35.4170355017063', 1e-13),
        ('Λ_IDCM [MeV]', Lam, '45.2848693374', 1e-11),
        ('v [GeV] (v13 值)', v, '246.2105', 1e-6),
        ('Σγ (n=1..44)', sum(4 * sin(n * pi / ring) ** 2 for n in range(1, 45)), '90', 1e-12),
        ('σ_macro=88Λ² [GeV²]', 88 * (Lam / 1000) ** 2, '0.1804633', 1e-6),
        ('σ_macro/σ_link=λ_max·72/11', lam * 72 / 11, '231.8206', 1e-5),
    ]
    rows = []
    for name, val, claim, tol in checks:
        dev = abs(val - mpf(claim)) / abs(mpf(claim))
        ok = dev <= max(tol, mpf('1e-15'))
        rows.append(dict(name=name, computed=mp.nstr(val, 14), doc_claim=claim,
                         rel_dev=f'{float(dev):.3e}', verdict='✅' if ok else '🔴'))
        print(f'  {name:30s} 算={mp.nstr(val, 14):>20s}  doc={claim:>18s} '
              f'dev={float(dev):.2e} {"✅" if ok else "🔴"}')
    return rows


def phase_c():
    """文檔數字獨立驗算：逐條由定義重算（唔讀 script 輸出）"""
    from mpmath import exp
    N_d, N_gen, L4, L5, B, F5 = 44, 3, 7, 11, 4, 5
    ring = 88
    lam = B * N_gen ** 2 - 1 / (4 * cos(mpf(N_gen) / L5 * pi) ** 2)
    core = sqrt(lam) * mpf('27.900915')
    g7 = 4 * sin(7 * pi / ring) ** 2
    v = core * (2 * N_d) * (2 * F5 + B * L4 * g7)
    a_inv_obs = mpf('137.035999074')
    alpha_obs = 1 / a_inv_obs
    C = [
        # (doc, 描述, computed, claim, tol)
        ('22', 'mode 20 = N_d−2B·N_gen', mpf(N_d - 2 * B * N_gen), '20', 0),
        ('22', 'v/Λ', v / (lam ** mpf('0.5') * mpf('27.900915') * N_gen / L5), '5436.9258', 1e-6),
        ('22', 'R1 dev vs 166.0064', abs(core - mpf('166.0064')) / mpf('166.0064') * 100, '0.0229635', 1e-6),
        ('23', '72/11 = 2N_d·N_gen²/L₅²', mpf(72) / 11, str(mpf(2 * N_d * 9) / 121), 1e-18),
        ('23', 'σ = core²·72/11 [GeV²]', (core / 1000) ** 2 * mpf(72) / 11, '0.18046330', 1e-7),
        ('28', 'core full-M₀ [MeV]', sqrt(lam) * mpf('27.9009145112'), '166.044517995', 1e-9),
        ('28', 'dev full-M₀ [%]', abs(sqrt(lam) * mpf('27.9009145112') - mpf('166.0064')) / mpf('166.0064') * 100, '0.0229618', 1e-5),
        ('29', '90 = 2N_d + B/2', mpf(2 * N_d + B // 2), '90', 0),
        ('29', '47 = L₄² − B/2', mpf(L4 ** 2 - B // 2), '47', 0),
        ('29', '53 = L₄² + B', mpf(L4 ** 2 + B), '53', 0),
        ('29', 'Σ4sin²(kπ/68), k=1..33', sum(4 * sin(k * pi / 68) ** 2 for k in range(1, 34)), '66', 1e-13),
        ('30', 'E(136)/mc² (α=1/137 結構值)', sqrt(1 - (mpf(136) / 137) ** 2), '0.1206037', 1e-6),
        ('31', '1/(1/137.035999074) − 137', a_inv_obs - 137, '0.035999074', 1e-8),
        ('31', 'dev [%]', (a_inv_obs - 137) / 137 * 100, '0.0262774', 1e-5),
        ('33', '(α/π)·137 (α=1/137)', 1 / pi, '0.31833', 1e-4),
        ('33', 'ratio (1/π) / δ', (1 / pi) / (a_inv_obs - 137), '8.8424', 1e-3),
        ('33', 'Q* = exp(δ/(2/(3π)))', exp((a_inv_obs - 137) / (2 / (3 * pi))), '1.18484', 1e-4),
        ('34', '137α', 137 * alpha_obs, '0.999737', 1e-5),
        ('34', '138α', 138 * alpha_obs, '1.007035', 1e-5),
        ('34', 'E(137)/mc²', sqrt(1 - (137 * alpha_obs) ** 2), '0.0229233', 1e-5),
        ('35', '137.036−127.930', a_inv_obs - mpf('127.930'), '9.105999074', 1e-8),
        ('35', '(137.036−137)+(128−127.930)', (a_inv_obs - 137) + (128 - mpf('127.930')), '0.106', 1e-3),
    ]
    rows = []
    print('\n=== Phase C: 文檔數字獨立驗算 ===')
    for doc, name, val, claim, tol in C:
        c = mpf(claim)
        dev = abs(val - c)
        rel = dev / abs(c) if c != 0 else dev
        ok = rel <= mpf(str(tol)) if tol else dev == 0
        rows.append(dict(doc=doc, name=name, computed=mp.nstr(val, 12), claim=claim,
                         rel_dev=f'{float(rel):.2e}', verdict='✅' if ok else '🔴'))
        print(f'  docs/{doc:3s} {name:30s} 算={mp.nstr(val, 12):>15s} 文件={claim:>15s} '
              f'dev={float(rel):.1e} {"✅" if ok else "🔴"}')
    return rows


if __name__ == '__main__':
    mode = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'all'
    out = {}
    if mode in ('all', '--only A', 'A'):
        print('=== Phase A: 未審計腳本重跑 ===')
        out['A'] = phase_a()
    if mode in ('all', '--only B', 'B'):
        print('\n=== Phase B: 核心常量獨立重算 ===')
        out['B'] = phase_b()
    if mode in ('all', '--only C', 'C'):
        out['C'] = phase_c()
    p = os.path.join(OUTDIR, 'summary_26.json')
    with open(p, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    print(f'\nJSON → {p}')
    bad = [r for r in out.get('A', []) if r['verdict'] != '✅'] + \
          [r for r in out.get('B', []) if r['verdict'] != '✅'] + \
          [r for r in out.get('C', []) if r['verdict'] != '✅']
    print(f'總計異常 = {len(bad)}')
    sys.exit(1 if bad else 0)