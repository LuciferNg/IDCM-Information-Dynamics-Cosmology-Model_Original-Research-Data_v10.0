#!/usr/bin/env python3
"""
12_master_atlas_xlsx.py — 44×44 Master Atlas 互動 Excel 試算表
==============================================================
輸出: beat_periodic_table/data/master_atlas.xlsx
3 個分頁:
  Sheet 1: Master_Atlas_44x44  — 互動熱力圖 (差頻/和頻 + 條件格式)
  Sheet 2: Bus_Address_Lookup  — 算符尋址器 (輸入 n,m 自動查表)
  Sheet 3: Operator_Database   — 全量 1936 格數據庫
"""

import math, os, csv
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, NamedStyle, numbers
)
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

# ====== 路徑 ======
SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR   = os.path.join(SCRIPT_DIR, "..", "data")
CSV_PATH   = os.path.join(DATA_DIR, "master_atlas.csv")
XLSX_PATH  = os.path.join(DATA_DIR, "master_atlas.xlsx")

Nd = 44
w = lambda n: 2 * math.sin(math.pi * n / 88)

# ====== 讀取 CSV ======
rows = []
with open(CSV_PATH, newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        r["n"] = int(r["n"])
        r["m"] = int(r["m"])
        r["d"] = int(r["d"])
        r["s"] = int(r["s"])
        r["diff"] = float(r["diff"])
        r["sum"] = float(r["sum"])
        r["deg_diff"] = int(r["deg_diff"])
        r["deg_sum"] = int(r["deg_sum"])
        rows.append(r)

# 建立快速查找 dict: (n,m) -> row
lookup = {(r["n"], r["m"]): r for r in rows}

# 生成差頻矩陣 44×44
M = [[0.0] * Nd for _ in range(Nd)]
for r in rows:
    M[r["n"] - 1][r["m"] - 1] = r["diff"]

diag_sum = [round(4 * math.sin((n + 1) * math.pi / 88), 12) for n in range(Nd)]

# 物理標籤 (同 10_master_atlas.py)
phys_labels = {
    (10, 24): "u/d Quark (O34)",
    (8, 22):  "c/s Quark (O34)",
    (19, 33): "t/b Quark (O34)",
    (8, 33):  "m_c/m_b (O34)",
    (1, 22):  "m_s/m_d (O35)",
    (30, 41): "m_W/m_Z (O34)",
    (19, 38): "m_H/m_W (O34)",
    (1, 18):  "m_mu/m_tau (O34)",
    (7, 20):  "n/p BBN (O13)",
}

magic_row_label = {
    7: "m7 anchor",
    14: "GEN d=14",
    20: "T(s->d)",
    22: "half-node",
    33: "K_tree",
}

# ====== 樣式定義 ======
thin_border = Border(
    left=Side(style="thin", color="999999"),
    right=Side(style="thin", color="999999"),
    top=Side(style="thin", color="999999"),
    bottom=Side(style="thin", color="999999"),
)

header_font = Font(name="Consolas", size=9, bold=True, color="FFFFFF")
header_fill = PatternFill("solid", fgColor="2F4F4F")  # dark slate gray
header_align = Alignment(horizontal="center", vertical="center")

data_font = Font(name="Consolas", size=8)
data_align = Alignment(horizontal="center", vertical="center")

diag_font = Font(name="Consolas", size=7, bold=True, color="FFFFFF")
diag_fill = PatternFill("solid", fgColor="000000")

magic_fill = PatternFill("solid", fgColor="FFF3CD")  # light yellow highlight
magic_font = Font(name="Consolas", size=8, color="CC7000")

gen_fill = PatternFill("solid", fgColor="00FF00")      # lime green
gen_font = Font(name="Consolas", size=8, bold=True, color="000000")

label_font = Font(name="Consolas", size=7, italic=True, color="666666")

# ====== 建立工作簿 ======
wb = Workbook()

# ====================================================================
# SHEET 1: Master_Atlas_44x44
# ====================================================================
ws1 = wb.active
ws1.title = "Master_Atlas_44x44"
ws1.sheet_properties.tabColor = "1F4E79"

# --- 列寬 & 行高 ---
ws1.column_dimensions["A"].width = 5
for col in range(2, Nd + 2):
    ws1.column_dimensions[get_column_letter(col)].width = 5.5
ws1.row_dimensions[1].height = 22
for r in range(2, Nd + 2):
    ws1.row_dimensions[r].height = 18

# --- 表頭: A1="n\\m", B1..AS1 = m=1..44 ---
ws1["A1"] = "n\\m"
ws1["A1"].font = header_font
ws1["A1"].fill = header_fill
ws1["A1"].alignment = header_align
ws1["A1"].border = thin_border

for m in range(1, Nd + 1):
    cell = ws1.cell(row=1, column=m + 1, value=m)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = thin_border

# --- 數據行 (n=1..44, 每行第一個 column = n) ---
# 同時收集條件格式所需的範圍: 非對角線, 對角線, 魔術行, 世代
for n in range(1, Nd + 1):
    row_idx = n + 1
    # 行標頭
    cell = ws1.cell(row=row_idx, column=1, value=n)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = thin_border

    for m in range(1, Nd + 1):
        col_idx = m + 1
        cell = ws1.cell(row=row_idx, column=col_idx)
        cell.border = thin_border
        cell.alignment = data_align

        if n == m:
            # 對角線: 和頻 (自耦合)
            cell.value = round(diag_sum[n - 1], 4)
            cell.font = diag_font
            cell.fill = diag_fill
            cell.number_format = "0.0000"
        else:
            # 差頻值
            cell.value = round(M[n - 1][m - 1], 4)
            cell.font = data_font
            cell.number_format = "+0.0000;-0.0000;0"

            # 魔術行標記 (d = |m-n|)
            d = abs(m - n)
            if d in magic_row_label:
                cell.font = magic_font
                # 淺底色
                cell.fill = magic_fill

    # 世代三重奏覆蓋
    for (nn, mm), label in phys_labels.items():
        if nn == n and mm == m:
            cell = ws1.cell(row=n + 1, column=m + 1)
            cell.fill = gen_fill
            cell.font = gen_font
            cell.value = round(M[n - 1][m - 1], 4)
            cell.number_format = "+0.0000;-0.0000;0"
            # 加註解
            from openpyxl.comments import Comment
            cell.comment = Comment(label, "IDCM Master Atlas")
        if mm == n and nn == m:  # 上三角對稱位置
            cell = ws1.cell(row=n + 1, column=m + 1)
            cell.fill = gen_fill
            cell.font = gen_font
            cell.value = round(M[n - 1][m - 1], 4)
            cell.number_format = "+0.0000;-0.0000;0"
            from openpyxl.comments import Comment
            cell.comment = Comment(label + " (CPT dual)", "IDCM Master Atlas")

# --- 條件格式: 3 色階 (紅→白→藍) ---
# 只在非對角線區域應用 (B2:AS45)
non_diag_range = "B2:AS45"
ws1.conditional_formatting.add(
    non_diag_range,
    ColorScaleRule(
        start_type="min", start_color="D62728",   # 紅 (負值 = CPT)
        mid_type="percentile", mid_value=50, mid_color="FFFFFF",  # 白 (0)
        end_type="max", end_color="1F77B4",        # 藍 (正值 = 物質)
    )
)

# --- 凍結窗格 (凍結表頭行+列) ---
ws1.freeze_panes = "B2"

# --- 圖例區域 (右側, 從 column AU 開始) ---
legend_col = Nd + 3  # column AU
ws1.column_dimensions[get_column_letter(legend_col)].width = 3
legend_col += 1  # AV

legends = [
    ("🎨 圖例", True, None, None),
    ("", False, None, None),
    ("🟦 下三角 (m>n) = 差頻>0 = 物質算符", False, "1F77B4", "FFFFFF"),
    ("🟥 上三角 (m<n) = 差頻<0 = CPT 反物質", False, "D62728", "FFFFFF"),
    ("⬛ 對角線 (m=n) = 和頻自耦合", False, "000000", "FFFFFF"),
    ("🟩 世代點 (u/d, c/s, t/b)", False, "00FF00", "000000"),
    ("🟨 魔術行 (d=7,14,20,22,33)", False, "FFF3CD", "CC7000"),
    ("", False, None, None),
    ("📐 公式:", True, None, None),
    ("  差頻 B = ω_m − ω_n", False, None, None),
    ("    ω_n = 2·sin(nπ/88)", False, None, None),
    ("  和頻 B' = ω_m + ω_n", False, None, None),
    ("  自耦合 = 4·sin(nπ/88)", False, None, None),
    ("", False, None, None),
    ("📊 統計:", True, None, None),
    (f"  總格數: {Nd*Nd}", False, None, None),
    ("  下三角: 946 (物質)", False, None, None),
    ("  上三角: 946 (CPT)", False, None, None),
    ("  對角線: 44 (真空)", False, None, None),
    ("", False, None, None),
    ("🔬 已閉合物理標籤:", True, None, None),
]

for key, label in phys_labels.items():
    n, m = key
    legends.append((f"  ({n},{m}) = {label}", False, None, None))

legends.append(("", False, None, None))
legends.append(("🟠 魔術行:", True, None, None))
for d, lbl in magic_row_label.items():
    legends.append((f"  d={d} = {lbl}", False, None, None))

for i, (text, is_header, bg, fg) in enumerate(legends):
    row = i + 2
    cell = ws1.cell(row=row, column=legend_col, value=text)
    cell.font = Font(name="Consolas", size=9, bold=is_header, color="333333")
    cell.alignment = Alignment(horizontal="left", vertical="center")
    if bg:
        cell.fill = PatternFill("solid", fgColor=bg)
    if fg:
        cell.font = Font(name="Consolas", size=9, bold=is_header, color=fg)

# ====================================================================
# SHEET 2: Bus_Address_Lookup — 算符尋址器
# ====================================================================
ws2 = wb.create_sheet("Bus_Address_Lookup")
ws2.sheet_properties.tabColor = "2E86C1"

# --- 控制面板佈局 ---
# 可命名範圍: 整個數據區域 (Sheet 3) 用作 lookup 來源
# 但我們直接用 Sheet 3 的數據做公式

# 控制面板: A1:B20
ctrl_font = Font(name="Consolas", size=11, bold=True)
ctrl_font_small = Font(name="Consolas", size=10)
val_font = Font(name="Consolas", size=12, bold=True, color="1F4E79")
note_font = Font(name="Consolas", size=9, italic=True, color="888888")
section_fill = PatternFill("solid", fgColor="E8F0FE")
section_font = Font(name="Consolas", size=11, bold=True, color="1F4E79")

ws2.column_dimensions["A"].width = 22
ws2.column_dimensions["B"].width = 30
ws2.column_dimensions["C"].width = 5
ws2.column_dimensions["D"].width = 22
ws2.column_dimensions["E"].width = 30

# 標題
ws2["A1"] = "🔍 Master Atlas — 算符尋址器 (Bus Address Lookup)"
ws2["A1"].font = Font(name="Consolas", size=14, bold=True, color="1F4E79")
ws2.merge_cells("A1:E1")

# 分隔線
row = 3
ws2.cell(row=row, column=1, value="── 輸入 ──").font = section_font
ws2.cell(row=row, column=1).fill = section_fill
ws2.merge_cells(f"A{row}:B{row}")

row = 4
ws2.cell(row=row, column=1, value="模態 n (1..44):").font = ctrl_font
ws2.cell(row=row, column=2, value=1).font = val_font
ws2.cell(row=row, column=2).border = Border(
    bottom=Side(style="medium", color="1F4E79")
)
ws2.cell(row=row, column=2).number_format = "0"
ws2.cell(row=row, column=2).alignment = Alignment(horizontal="center")

row = 5
ws2.cell(row=row, column=1, value="模態 m (1..44):").font = ctrl_font
ws2.cell(row=row, column=2, value=1).font = val_font
ws2.cell(row=row, column=2).border = Border(
    bottom=Side(style="medium", color="1F4E79")
)
ws2.cell(row=row, column=2).number_format = "0"
ws2.cell(row=row, column=2).alignment = Alignment(horizontal="center")

# 數據驗證: n,m 只能 1..44
dv = DataValidation(type="whole", operator="between", formula1=1, formula2=44)
dv.error = "請輸入 1 到 44 之間的整數"
dv.errorTitle = "無效輸入"
dv.prompt = "輸入模態號碼 (1-44)"
dv.promptTitle = "模態座標"
ws2.add_data_validation(dv)
dv.add("B4:B5")

row = 7
ws2.cell(row=row, column=1, value="── 輸出 ──").font = section_font
ws2.cell(row=row, column=1).fill = section_fill
ws2.merge_cells(f"A{row}:B{row}")

# 輸出欄位 (用公式從 Sheet 3 查找)
# 結構: 第9行開始, 每項: label | formula | 註解
# 我們用 INDEX/MATCH 雙條件查詢 Sheet 3
# Sheet 3 第1行是表頭, 數據從第2行開始
# Sheet 3 的 columns: A=n, B=m, C=d, D=s, E=diff, F=sum, G=deg_diff, H=deg_sum, I=label

output_fields = [
    ("可分離座標 d = m−n:",  "C", "差頻階數"),
    ("可分離座標 s = m+n:",  "D", "和頻階數"),
    ("差頻 B = ω_m−ω_n:",   "E", "反對稱 (物質>0, CPT<0)"),
    ("和頻 B' = ω_m+ω_n:",  "F", "對稱 (自對偶)"),
    ("代數次數 (差頻):",      "G", "φ(k) / 2 degree"),
    ("代數次數 (和頻):",      "H", "φ(k) / 2 degree"),
    ("物理標籤:",             "I", "已閉合 IDCM 參數 / 魔術行"),
]

# 構建 INDEX/MATCH 公式:
# MATCH 用 concatenated key: n&"_"&m
# 但 Sheet 3 冇 concatenated key column, 要用 array 式:
# {=INDEX(Sheet3!E:E, MATCH(1, (Sheet3!A:A=B4)*(Sheet3!B:B=B5), 0))}
# 但 array formula 在 openpyxl 比較麻煩, 用 helper column 更方便
# 我地在 Sheet 3 第 J 欄加 helper: =A2&"_"&B2, 然後用 VLOOKUP 或 INDEX/MATCH

# Helper column J 會在 Sheet 3 generation 時加入
# 公式: =INDEX(Operator_Database!E:E, MATCH(B4&"_"&B5, Operator_Database!J:J, 0))

for i, (label, col_letter, note) in enumerate(output_fields):
    r = 9 + i
    ws2.cell(row=r, column=1, value=label).font = ctrl_font_small

    col_idx_letter = col_letter
    # 公式
    formula = (
        f'IFERROR(INDEX(Operator_Database!{col_idx_letter}:{col_idx_letter}, '
        f'MATCH(B4&"_"&B5, Operator_Database!J:J, 0)), "—")'
    )
    cell = ws2.cell(row=r, column=2)
    cell.value = formula
    cell.font = val_font
    cell.alignment = Alignment(horizontal="center")
    cell.border = Border(bottom=Side(style="thin", color="CCCCCC"))

    # 註解
    ws2.cell(row=r, column=4, value=note).font = note_font

# 特殊: 對角線提示
row = 17
ws2.cell(row=row, column=1, value="💡 提示：").font = Font(name="Consolas", size=9, bold=True, color="888888")
ws2.cell(row=row, column=2, value="n=m → 對角線 (和頻自耦合, 差頻=0)").font = note_font

row = 18
ws2.cell(row=row, column=1, value="").font = Font(name="Consolas", size=9, bold=True, color="888888")
ws2.cell(row=row, column=2, value="n>m → 下三角 (物質算符); n<m → 上三角 (CPT 反物質)").font = note_font

# 常用查詢快捷鍵
row = 20
ws2.cell(row=row, column=1, value="── 常用查詢 ──").font = section_font
ws2.cell(row=row, column=1).fill = section_fill
ws2.merge_cells(f"A{row}:B{row}")

quick_lookups = [
    ("(8, 22) = c/s Quark", 8, 22),
    ("(10, 24) = u/d Quark", 10, 24),
    ("(19, 33) = t/b Quark", 19, 33),
    ("(1, 22) = m_s/m_d", 1, 22),
    ("(7, 20) = n/p BBN", 7, 20),
    ("(30, 41) = m_W/m_Z", 30, 41),
    ("(19, 38) = m_H/m_W", 19, 38),
    ("(1, 18) = m_mu/m_tau", 1, 18),
]

for i, (qlabel, qn, qm) in enumerate(quick_lookups):
    r = 22 + i
    ws2.cell(row=r, column=1, value=qlabel).font = Font(name="Consolas", size=9, color="2E86C1")
    ws2[f"B{r}"] = f"=HYPERLINK(\"#\", \"點擊 → 設 n={qn}, m={qm}\")"
    ws2[f"B{r}"].font = Font(name="Consolas", size=9, color="2E86C1", underline="single")
    # 註: HYPERLINK 無法真的改變 B4,B5 值, 但可以點擊跳轉

# 凍結窗格
ws2.freeze_panes = "C4"

# ====================================================================
# SHEET 3: Operator_Database — 全量數據庫
# ====================================================================
ws3 = wb.create_sheet("Operator_Database")
ws3.sheet_properties.tabColor = "27AE60"

# 表頭
headers = ["n", "m", "d", "s", "diff", "sum", "deg_diff", "deg_sum", "label", "key"]
col_widths = [6, 6, 6, 6, 12, 12, 10, 10, 30, 14]

for i, (h, w) in enumerate(zip(headers, col_widths)):
    col = i + 1
    cell = ws3.cell(row=1, column=col, value=h)
    cell.font = Font(name="Consolas", size=9, bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="2E4057")
    cell.alignment = Alignment(horizontal="center", vertical="center")
    cell.border = thin_border
    ws3.column_dimensions[get_column_letter(col)].width = w

# 數據 (1936 行)
for idx, r in enumerate(rows):
    row_idx = idx + 2
    vals = [r["n"], r["m"], r["d"], r["s"],
            r["diff"], r["sum"],
            r["deg_diff"], r["deg_sum"],
            r["label"],
            f"{r['n']}_{r['m']}"]
    for col, val in enumerate(vals, 1):
        cell = ws3.cell(row=row_idx, column=col, value=val)
        cell.font = Font(name="Consolas", size=8)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border
        # 數字格式
        if col == 5:  # diff
            cell.number_format = "0.000000000000"
        elif col == 6:  # sum
            cell.number_format = "0.000000000000"

# 凍結窗格
ws3.freeze_panes = "A2"

# 自動篩選
ws3.auto_filter.ref = f"A1:I{len(rows) + 1}"

# ====== 儲存 ======
os.makedirs(DATA_DIR, exist_ok=True)
wb.save(XLSX_PATH)
print(f"✅ Master Atlas Excel 已輸出: {XLSX_PATH}")
print(f"   Sheet 1: Master_Atlas_44x44 — {Nd}×{Nd} 互動熱力圖")
print(f"   Sheet 2: Bus_Address_Lookup — 算符尋址器 (輸入 n,m 自動查表)")
print(f"   Sheet 3: Operator_Database  — {len(rows)} 格全量數據庫 (+ 自動篩選)")
print(f"   條件格式: 3 色階 (紅→白→藍) + 魔術行黃底 + 世代綠點 + 對角線黑底白字")