#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O229 MANIFEST 重建器（verify/；唔計入 scripts 01–25 名單）
逐檔 sha256；§一 之 RESULT 由 logs/*.out 即時抽出（唔硬編碼）；輸出 MANIFEST.md + MANIFEST.json。
"""
import hashlib, json, os, re, subprocess, datetime
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {"MANIFEST.md", "MANIFEST.json"}
paths = []
for dp, dn, fs in os.walk(BASE):
    for f in fs:
        rel = os.path.relpath(os.path.join(dp, f), BASE)
        if rel in SKIP:
            continue
        paths.append(rel)
paths.sort()
def sha(p):
    h = hashlib.sha256()
    with open(os.path.join(BASE, p), "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
files = {p: {"bytes": os.path.getsize(os.path.join(BASE, p)), "sha256": sha(p)} for p in paths}
CONTRACTS = {}
for p, key in (("docs/00_contract.md", "R1"), ("docs/08_r2_contract.md", "R2"), ("docs/14_r3_contract.md", "R3"),
               ("docs/20_r4_contract.md", "R4"), ("docs/26_r5_contract.md", "R5")):
    if p in files:
        CONTRACTS[key] = {"file": p, "sha256": files[p]["sha256"]}
res = []
for p in sorted(files):
    if not p.startswith("logs/"):
        continue
    nm = os.path.basename(p)[:-4]
    if not re.match(r"^\d\d_", nm) or "pre_" in nm or "buggy" in nm or "abort" in nm:
        continue                                            # 排除更正前之舊記錄
    m = re.findall(r"(?m)^RESULT:\s*(\d+)/(\d+)\s*PASS", open(os.path.join(BASE, p), encoding="utf-8").read())
    if not m:
        continue
    res.append((nm, int(m[0][0]), int(m[0][1])))
# closeout 全鏈重跑閘（2026-10-04）：logs/closeout_*（還原後之尾部更新，非 \d\d_ ⟹ 唔入 res）
res_co = []
for p in sorted(files):
    if not p.startswith("logs/closeout_") or not p.endswith(".out"):
        continue
    m = re.findall(r"(?m)^RESULT:\s*(\d+)/(\d+)\s*PASS", open(os.path.join(BASE, p), encoding="utf-8").read())
    if m:
        res_co.append((os.path.basename(p)[9:-4], int(m[0][0]), int(m[0][1])))
ENG = {"R1": ["01", "02", "03", "04", "05", "06", "07", "08"], "R2": ["09", "10", "11"], "R3": ["13", "14", "15", "16"],
       "R4": ["18", "19", "20"], "R5": ["22", "23", "24"]}
AUD = {"R1": None, "R2": "12", "R3": "17", "R4": "21", "R5": "25"}
rounds = {k: [r for r in res if r[0][:2] in v] for k, v in ENG.items()}
audits = {k: ([r for r in res if r[0][:2] == v] or [None])[0] for k, v in AUD.items()}
counts = {}
for p in files:
    counts[p.split("/")[0] if "/" in p else "(root)"] = counts.get(p.split("/")[0] if "/" in p else "(root)", 0) + 1
today = datetime.date.today().isoformat()
L = []
L.append("# MANIFEST — O229（R1 ＋ R2 ＋ R3 ＋ R4 ＋ R5）")
L.append("")
L.append(f"> **日期**: {today} ｜ **檔案數**: {len(files)} 件（唔含本 MANIFEST 自身）")
for k in ("R1", "R2", "R3", "R4", "R5"):
    if k in CONTRACTS:
        L.append(f"> **凍結合約 {k}** `{CONTRACTS[k]['file']}` sha256 `{CONTRACTS[k]['sha256']}`")
L.append(f"> **規則版本**: o229-r1+r2+r3+r4+r5 contract v1 + closeout-{today}")
L.append("")
L.append("## 一、閘門")
for k in ("R1", "R2", "R3", "R4", "R5"):
    if rounds[k]:
        e = f"{sum(r[1] for r in rounds[k])}/{sum(r[2] for r in rounds[k])}（{len(rounds[k])} 引擎）"
        a = audits[k]
        L.append(f"**{k}** = {e}" + (f" ＋ 獨立核對 `{a[0]}` {a[1]}/{a[2]}" if a else ""))
if res_co:
    L.append("")
    L.append("**2026-10-04 全鏈 closeout 重跑閘（尾部更新，`logs/closeout_*`；正典 logs = R1–R5 era 記錄）**："
             + " ＋ ".join(f"`{nm}` {ps}/{tt}" for nm, ps, tt in res_co)
             + f" ⟹ 合計 {sum(r[1] for r in res_co)}/{sum(r[2] for r in res_co)}")
L.append("")
L.append("```")
for nm, ps, tt in res:
    L.append(f"{nm:34s} RESULT: {ps}/{tt} PASS")
L.append("```")
L.append("")
L.append("★ 各輪 closeout 時**整體重跑**，逐項 RESULT 與本表一致。")
L.append("★ 預註冊 FAIL 原樣保留 ＋ `-c` 校正（承 §F「無效才是正確」）：R1 1 條、R2 2 條、R3 6 條、R4 2 條、R5 5 條。")
L.append(f"★ 規模: " + "｜".join(f"{k} {v}" for k, v in sorted(counts.items())))
L.append("")
L.append("## 二、檔案清單（sha256 / bytes）")
L.append("")
L.append("| 檔 | bytes | sha256 |")
L.append("|:--|--:|:--|")
for p in paths:
    L.append(f"| `{p}` | {files[p]['bytes']} | `{files[p]['sha256'][:16]}…` |")
L.append("")
L.append("## 三、重建指令")
L.append("")
L.append("```bash")
L.append("cd open_problems_fresh/o229_mu2_b4_particle_accounting")
L.append("for i in $(seq -w 1 25); do /usr/bin/python3 scripts/${i}_*.py; done")
L.append("# 逐腳本 RESULT 應與本檔 §一 一致；08/12/17/21/25 為獨立核對器（唔 import 受核腳本）")
L.append("/usr/bin/python3 verify/third_route_arbiter.py   # 第三路線仲裁（唔計入 scripts 名單）")
L.append("```")
L.append("")
L.append("## 四、核心數字")
L.append("- " + " ／ ".join(f"{k} `{CONTRACTS[k]['sha256'][:16]}…`" for k in sorted(CONTRACTS)))
for k in ("R1", "R2", "R3", "R4", "R5"):
    if rounds[k]:
        a = audits[k]
        L.append(f"- {k} **{sum(r[1] for r in rounds[k])}/{sum(r[2] for r in rounds[k])}**（{len(rounds[k])} 引擎）"
                 + (f"＋核對 {a[1]}/{a[2]}" if a else ""))
L.append("- R5 核心: 端點鎖三項解剖 `137 = C(B²,2)+B²+1 = 120+16+1` ⟹ 「半結構」（120 之群階讀法僅在 16 態不可分下被排除）｜")
L.append("  函數正則類 112 項 / 234,136 形式 ⟹ 命中 270、含 B 228 條**全部**以 `B = 4` 為唯一正整數解（過定）｜")
L.append("  值層零判別力: `express(137) = 270` 排 34/34、同量級池 `p = 0.6238`、`max lock = 737 @ 16`｜")
L.append("  `-c6`: 25 初版 `2^B` 項漏乘 `den`（誤報 227/729）⟹ 更正後 25 = 23/23，第三路線 0 差異")
L.append("- R4 核心: 鏈長族 ℳ = {8,16,44,88,176,352,704} = {2^a·11^b} ⟹ 整數譜值集恰 {0, μ², B}；μ² 支撐秩 1、外部 0")
L.append("- R3 核心: 異常泛函恆等零 ⟹ 解集維數 2；譜整數性 ⟺ 階 ∈ {1,2,3,4,6}；端點鎖 4/34 = 11.76%")
L.append("- MC null（R1）: N = 10⁷, seed 229, 命中 13 ⟹ 1.30e-06（R4 精確校正 8/4885673）")
L.append("")
open(os.path.join(BASE, "MANIFEST.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
json.dump({"rules_version": f"o229-r1+r2+r3+r4+r5-contract-v1+closeout-{today}", "date": today,
           "contract_sha256": {v["file"].split("/")[-1]: v["sha256"] for v in CONTRACTS.values()},
           "gate": {nm: {"pass": ps, "total": tt} for nm, ps, tt in res},
           "totals": {k: {"pass": sum(r[1] for r in v), "total": sum(r[2] for r in v), "scripts": len(v),
                          "audit": ({"script": audits[k][0], "pass": audits[k][1], "total": audits[k][2]}
                                    if audits[k] else None)}
                      for k, v in rounds.items() if v},
           "file_count": len(files), "counts": counts, "files": files},
          open(os.path.join(BASE, "MANIFEST.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"MANIFEST 重建: {len(files)} 件；閘門 " +
      "｜".join(f"{k} {sum(r[1] for r in v)}/{sum(r[2] for r in v)}" for k, v in rounds.items() if v))
print("計數:", counts)
print("合約 sha256:", {k: v["sha256"][:16] for k, v in CONTRACTS.items()})
