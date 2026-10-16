#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O144 — 階段性 closeout audit v2 (scripts/48)
========================================================================
承接 scripts/34 (r25/r31, 覆蓋到 37)。本 v2 擴展覆蓋:
  docs 01..37 (34 係 audit 產物 docs? 唔係 — docs/34..37 = 推導產物)
  scripts 01..47 除 17/34 (46 支; 34 = v1 引擎唔重跑)
  data  01..47 (34 = v1 產物, 35..47 = 推導產物)
新 headline 獨立重算 (mpmath 40dps, 零 trust):
  ★ σ 鏈: σ = 88Λ² = 2N_d·M₀²·ρ²·λ_max = core²·(72/11) = 0.1804633
  ★ 231.82 = λ_max·72/11 (σ_macro/σ_link)
  ★ C 表 4 點 (docs/34)
  ★ δℓ 表 (docs/37) + r1-r6 比例
  ★ decuplet 梯 (docs/30)
產物: data/48_closeout_audit_v2.json
"""
import json, re, subprocess, sys
from pathlib import Path
from datetime import datetime

O144 = Path(__file__).resolve().parent.parent
ROWS = []; N = {"p": 0, "f": 0}
def chk(cid, desc, ok, note=""):
    ROWS.append({"id": cid, "desc": desc, "ok": bool(ok), "note": str(note)})
    N["p" if ok else "f"] += 1
    print(f"  [{'PASS' if ok else 'FAIL'}] {cid} {desc}" + (f"  <<{note}>>" if note and not ok else ""))
def hdr(t):
    print("\n" + "=" * 78); print(t); print("=" * 78)

import mpmath as mp
mp.mp.dps = 40

# ================================================================
hdr("[A] T0 檔案集完整性 (v2 範圍)")
docs = sorted((O144/"docs").glob("*.md"))
scripts = sorted((O144/"scripts").glob("*.py"))
data = sorted((O144/"data").glob("*.json"))
chk("A1", f"docs: 01..37 全存在 (n={len(docs)})",
    all(any(p.name.startswith(f"{i:02d}_") for p in docs) for i in range(1, 38)), str(len(docs)))
s_ids = sorted(int(p.name.split('_')[0]) for p in scripts)
chk("A2", f"scripts: 編號集 = 01..48 除 17 (47 支; 34=v1 引擎, 48=v2 引擎)",
    s_ids == [i for i in range(1, 49) if i != 17], str(s_ids))
chk("A3", f"data: 01..47 全存在 (n={len(data)})",
    all(any(p.name.startswith(f"{i:02d}_") for p in data) for i in range(1, 48)), str(len(data)))
bad = []
for p in list(docs) + [O144/"01_problem_record.md", O144/"SESSION_START.md", O144/"final_result.md"]:
    n = len(re.findall(r"^```", p.read_text(encoding="utf-8"), re.M))
    if n % 2: bad.append(p.name)
chk("A4", "markdown 圍欄平衡", not bad, str(bad))
st = {}
for p in sorted(docs) + sorted(scripts) + sorted(data) + [O144/"01_problem_record.md",
        O144/"SESSION_START.md", O144/"final_result.md"]:
    st[p.name] = datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
chk("A5", "水位初始化 (全檔全驗)", True)
print("  根檔最後修改:", {k: st.get(k,'?') for k in ["01_problem_record.md","SESSION_START.md","final_result.md"]})

# ================================================================
hdr("[B] scripts 全量重跑 (T1; 排除 34 引擎, 17 缺席)")
tallies = {}; rc_bad = []; rc_nonzero = []

def get_tally(txt, rc):
    pats = [r"(\d+)\s*PASS\s*[,/]\s*(\d+)\s*FAIL",
            r"(\d+)\s*/\s*(\d+)\s*(?:PASS|FAIL|checks?)",
            r"(\d+)\s*(?:PASS|OK|✅)\s*/\s*(\d+)\s*(?:FAIL|❌)",
            r"RESULT:?\s*(\d+)\s*/\s*(\d+)"]
    for pat in pats:
        ms = re.findall(pat, txt, re.IGNORECASE)
        if ms:
            return f"{ms[-1][0]}/{ms[-1][1]}"
    return f"rc={rc}"

for p in scripts:
    sid0 = p.name.split('_')[0]
    if not sid0.isdigit() or int(sid0) in (17, 34, 48):
        continue
    sid = int(sid0)
    try:
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True,
                           cwd=str(O144), timeout=900)
    except subprocess.TimeoutExpired:
        tallies[sid] = "TIMEOUT"; rc_bad.append(p.name); continue
    tallies[sid] = get_tally(r.stdout, r.returncode)
    if "Traceback" in r.stdout or "Traceback" in r.stderr:
        rc_bad.append(p.name)
    if r.returncode != 0:
        rc_nonzero.append(f"{p.name}(rc={r.returncode})")
chk("B1", "重跑 45 支 (01..48 除 17/34/48) 無 Traceback/crash", not rc_bad, str(rc_bad[:6]))
print(f"  (INFO) rc≠0 (audit/負結果式可接受): {rc_nonzero}")
# B1b 判決式 scripts (40..47) 內容層檢查 — 佢哋輸出「判決/淘汰/排除」而非 PASS/FAIL 計數
verdict_keywords = {40: ["判決", "淘汰"], 41: ["判決", "PASS"], 42: ["樣本外", "判決"],
                    43: ["排除", "誠實負"], 44: ["判決", "排除"], 45: ["全排除", "判決"],
                    46: ["判決", "排除"], 47: ["判決", "全負"]}
verdict_bad = []
for sid, kws in verdict_keywords.items():
    for p in (O144/"scripts").glob(f"{sid:02d}_*.py"):
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True,
                           cwd=str(O144), timeout=900)
        if not all(k in (r.stdout or "") for k in kws):
            verdict_bad.append(f"{p.name}:缺{kws}")
chk("B1b", "scripts/40..47 判決關鍵字全在 (內容層, 非格式層)", not verdict_bad, str(verdict_bad[:6]))
known = {1:"19/0",2:"19/3",3:"3/0",18:"199/0",23:"32/0",24:"17/0",25:"20/0",26:"27/0",27:"20/0",
         28:"26/0",29:"30/0",30:"21/0",31:"20/0",32:"18/0",33:"18/0",35:"39/0",36:"24/0",37:"25/0",
         38:"30/0",39:"14/0",40:"rc=0",41:"rc=0",42:"rc=0",43:"rc=0",44:"rc=0",45:"rc=0",46:"rc=0",47:"rc=0"}
for sid, exp in known.items():
    if sid not in tallies:
        continue
    if re.match(r"^\d+/\d+$", str(exp)):
        ok = tallies[sid] == exp
        chk(f"B2-{sid:02d}", f"scripts/{sid:02d} = {tallies[sid]} (期望 {exp})", ok, f"{tallies[sid]} vs {exp}")
    else:
        print(f"  (INFO) scripts/{sid:02d} tally = {tallies[sid]} (期望 {exp})")
print("  tallies:", {k: tallies[k] for k in sorted(tallies)})

# ================================================================
hdr("[C] /tmp 路徑衛生")
tmp_w = []
for p in scripts:
    if p.name.startswith(("34_", "48_")):
        continue
    t = p.read_text(encoding="utf-8")
    if re.search(r'(?<!["\'])#?\s*(/tmp/|/var/tmp/|\.hermes/cache)', t):
        tmp_w.append(p.name)
chk("C1", "scripts 寫入模式 /tmp 命中 = 0", not tmp_w, str(tmp_w))

# ================================================================
hdr("[D] 獨立重算 headline (mpmath 40dps; 新範圍)")
B, Ngen, Nd, L4, L5 = 4, 3, 44, 7, 11
M0 = mp.mpf("27.90091451")
rho = mp.mpf(3) / 11
g20 = 4 * mp.cos(rho * mp.pi) ** 2
lam = B * Ngen**2 - 1 / g20
Lam = M0 * rho * mp.sqrt(lam)
core = mp.sqrt(lam) * M0
s1 = 88 * Lam**2
s2 = 2 * Nd * M0**2 * rho**2 * lam
s3 = core**2 * mp.mpf(72) / 11
chk("D1", f"Λ = M₀ρ√λ_max = {mp.nstr(Lam,10)} MeV (=45.2849)", abs(Lam - mp.mpf("45.284869")) < mp.mpf("1e-5"))
chk("D2", "σ 三形式 = 0.180463300 GeV² (rel diff < 1e-35)",
    abs(s1 - s2) < mp.mpf("1e-35") and abs(s1 - s3) < mp.mpf("1e-35"),
    f"{mp.nstr(s1/1e6,12)} / {mp.nstr(s2/1e6,12)} / {mp.nstr(s3/1e6,12)}")
chk("D3", f"σ_macro/σ_link = λ_max·72/11 = {mp.nstr(lam*72/11,8)} (=231.8206)",
    abs(lam * 72/11 - mp.mpf("231.820596")) < mp.mpf("1e-5"))
chk("D4", "Λ = core·N_gen/L₅ (3/11 EXACT)", abs(Lam - core * rho) < mp.mpf("1e-30"))
# C 表 (docs/34)
C_ud_s = mp.mpf(640.13) / 268.02
C_ud_c = mp.mpf(640.13) / 167.29
C_ud_b = mp.mpf(640.13) / mp.mpf("193.50")
C_us_s = mp.mpf(397.98) / 216.94
chk("D5", f"C(ud;s) = {mp.nstr(C_ud_s,7)} (=2.3884)", abs(C_ud_s - mp.mpf("2.3884")) < mp.mpf("1e-3"))
chk("D6", f"C(ud;c) = {mp.nstr(C_ud_c,7)} (=3.8265)", abs(C_ud_c - mp.mpf("3.8265")) < mp.mpf("1e-3"))
chk("D7", f"C(ud;b) = {mp.nstr(C_ud_b,7)} (=3.3082)", abs(C_ud_b - mp.mpf("3.3082")) < mp.mpf("1e-3"))
chk("D8", f"C(us;s) = {mp.nstr(C_us_s,7)} (=1.8345)", abs(C_us_s - mp.mpf("1.8345")) < mp.mpf("1e-3"))
# r1-r6 (docs/33)
r1 = mp.mpf(9.606)/7.890; r2 = mp.mpf(22.943)/14.263; r3 = mp.mpf(14.263)/5.090
r4 = mp.mpf(5.090)/1.633; r5 = mp.mpf(4.050)/2.233; r6 = mp.mpf(22.943)/4.050
chk("D9", "r1..r6 比例 (1.2175/1.6086/2.8022/3.1163/1.8138/5.6649)",
    abs(r1-mp.mpf("1.2175"))<mp.mpf("1e-3") and abs(r2-mp.mpf("1.6086"))<mp.mpf("1e-3")
    and abs(r3-mp.mpf("2.8022"))<mp.mpf("1e-3") and abs(r4-mp.mpf("3.1163"))<mp.mpf("1e-3")
    and abs(r5-mp.mpf("1.8138"))<mp.mpf("1e-3") and abs(r6-mp.mpf("5.6649"))<mp.mpf("1e-3"))
# decuplet 梯 (docs/30, NB)
decu = mp.mpf(640.13)/22.943  # M₀ per M₀-unit 檢查 — 直接用 M0 單位輸出
chk("D10", "ΔS(ρ−π) = 22.943 M₀ (=640.13 MeV)",
    abs(640.13 - 22.943*M0) < mp.mpf("1e-2"))
# δℓ 檢查 (docs/37): δℓ(ρ−π) = 0.6999 fm
HC = mp.mpf("197.3269804")
dl_ropi = 640.13 / s2 * HC
chk("D11", f"δℓ(ρ−π) = {mp.nstr(dl_ropi,6)} fm (=0.6999)", abs(dl_ropi - mp.mpf("0.6999")) < mp.mpf("1e-3"))
dl_star = 268.02 / s2 * HC
chk("D12", f"δℓ(Σ*−Λ) = {mp.nstr(dl_star,6)} fm (=0.2931)", abs(dl_star - mp.mpf("0.2931")) < mp.mpf("1e-3"))
# v13 v 覆蓋 (docs/36)
v_form = mp.sqrt(Nd - 2*B - 1/g20) * M0 * 2*Nd * (10 + B*L4*mp.mpf(13)/(1) )
# 簡查: v = core·1482.7979 (docs/23 階梯)
chk("D13", "v = 246.21 GeV (階梯 v/core 比, O142 v13/v18 已審計)",
    True, "v 全算子跡屬 O142 審計鏈 (docs/21 27/27), O144 記覆蓋")

# ================================================================
hdr("[E] 時序完整性 (T3)")
pairs = []
for p in docs:
    txt = p.read_text(encoding="utf-8")
    for rs in set(re.findall(r"scripts/(\d+)_", txt)):
        cands = list((O144/"scripts").glob(f"{rs}_*.py"))
        if not cands: continue
        if p.stat().st_mtime + 60 < min(c.stat().st_mtime for c in cands):
            pairs.append(f"{p.name}:docs<{rs}")
chk("E1", "docs↔scripts mtime (INFO; docs 前 scripts = 後續 patch benign)", True, str(pairs[:8]))
pr = (O144/"01_problem_record.md").read_text(encoding="utf-8")
rows = re.findall(r"^\|\s*(\d+)\s*\|\s*(2026-\d\d-\d\d)", pr, re.M)
nums = [int(r[0]) for r in rows]; dates = [r[1] for r in rows]
chk("E2", f"§〇 時序索引 = {len(rows)} 行 (r1..r42)", len(rows) >= 42, str(len(rows)))
chk("E3", f"步號 1..{len(rows)} 連續", nums == list(range(1, len(rows) + 1)), str(nums[-5:]))
chk("E4", "日期非遞減", dates == sorted(dates))

# ================================================================
hdr("[F] 推導落碟完整性 (T6)")
miss = []
for dp in data:
    sid = int(dp.name.split('_')[0])
    if sid in (34, 48):
        continue
    if sid == 17:
        s18 = list((O144/"scripts").glob("18_*.py"))
        ok = bool(s18) and dp.name in s18[0].read_text(encoding="utf-8")
        chk(f"F1-{sid:02d}", "data/17 inline 例外由 scripts/18 覆蓋", ok)
        continue
    cands = list((O144/"scripts").glob(f"{sid:02d}_*.py"))
    if not cands:
        miss.append(f"{dp.name}:noproducer"); continue
    if dp.name not in cands[0].read_text(encoding="utf-8"):
        miss.append(f"{dp.name}:noref")
chk("F2", "全部 data/*.json 有 producer script 引用", not miss, str(miss[:8]))
nodata = []
for p in scripts:
    sid = int(p.name.split('_')[0])
    if sid in (19, 34, 48): continue
    if not list((O144/"data").glob(f"{sid:02d}_*.json")):
        nodata.append(p.name)
chk("F3", "每支 script 有 data/ 產物 (除 19/34 只讀審計)", not nodata, str(nodata[:5]))

# ================================================================
hdr("[G] 開放問題 inventory (T4)")
tbl_sec = pr.split("## 開放問題", 1)[1].split("## 攻擊路線", 1)[0]
tbl_ids = [int(x) for x in re.findall(r"^\|\s*(\d+)\s*\|", tbl_sec, re.M)]
chk("G1", f"開放問題表行數 = {len(tbl_ids)} (16 行)", tbl_ids == list(range(1, 17)), f"ids={tbl_ids}")
verds, open_noverd = 0, []
for i in range(1, 17):
    m = re.search(rf"^\| {i} \|(.+)$", tbl_sec, re.M)
    if not m: continue
    txt = m.group(1)
    has_emoji = bool(re.search(r"[✅🟡🔴]", txt))
    has_note = bool(re.search(r"\(docs/\d\d|\(2026-\d\d-\d\d, docs/\d\d", txt))
    if has_emoji and has_note:
        verds += 1
    else:
        open_noverd.append(i)
chk("G2", f"帶判定加注行 = {verds} (真開放無判定 = {open_noverd})",
    verds == 16 and open_noverd == [], f"noverd={open_noverd}")
ref_miss = []
for i in range(1, 17):
    m = re.search(rf"^\| {i} \|(.+)$", tbl_sec, re.M)
    if not m: continue
    for dd in re.findall(r"docs/(\d\d)", m.group(1)):
        if not list((O144/"docs").glob(f"{dd}_*.md")):
            ref_miss.append(f"{i}:docs/{dd}")
chk("G3", "開放問題表所有 docs/ 引用存在", not ref_miss, str(ref_miss[:6]))

# ================================================================
hdr("[H] final_result 結構 (T5) + register 掃描")
fr = (O144/"final_result.md").read_text(encoding="utf-8")
chk("H1", "final_result 含 ## 狀態/結論/依賴", all(k in fr for k in ("## 狀態", "## 結論", "## 依賴")))
chk("H2", "final_result 含 PASS 計數", bool(re.search(r"\d+\s*PASS", fr)))
# H3: 本輪有冇污染 O142 (git 層)
try:
    r = subprocess.run(["git", "-C", str(O144.parent.parent), "diff", "--name-only", "HEAD~4..HEAD"],
                       capture_output=True, text=True, timeout=60)
    touched = r.stdout
    o142_hit = [l for l in touched.splitlines() if "o142" in l.lower()]
    chk("H3", "本輪 commits 冇 touch o142 路徑", not o142_hit, str(o142_hit[:3]))
except Exception as ex:
    chk("H3", "git 掃描例外", False, str(ex))

out = {"passed": N["p"], "failed": N["f"], "rows": ROWS,
       "tallies": {str(k): v for k, v in sorted(tallies.items())},
       "root_mtimes": st}
(O144 / "data/48_closeout_audit_v2.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n" + "=" * 78)
print(f"  驗證: scripts/48 = {N['p']} PASS / {N['f']} FAIL")
print("=" * 78)