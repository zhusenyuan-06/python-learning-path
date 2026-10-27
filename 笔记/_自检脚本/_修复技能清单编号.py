# -*- coding: utf-8 -*-
"""修复《AI应用工程师技能清单.xlsx》「使用说明」sheet 的编号顺序。

背景：批量插入第 6 条说明时插在了第 7 行，把原来的第 5 条挤到第 8 行，
导致列表变成「... 4. / 6. / 5.」。这里把顺序摆正。
"""
import openpyxl

PATH = r"C:\Users\15816\Desktop\AI应用工程师技能清单.xlsx"

wb = openpyxl.load_workbook(PATH)
ws = wb["使用说明"]

# 收集所有非空说明行
items = []
for r in range(1, ws.max_row + 1):
    v = ws.cell(r, 1).value
    if isinstance(v, str) and v.strip():
        items.append((r, v.strip()))

print("插入前：")
for r, v in items:
    print("  r%-3d %s" % (r, v[:100]))

# 找到以 "5. " 和 "6. " 开头的两行，把「内容」互换位置，使编号重新连续
row5 = row6 = None
for r, v in items:
    if v.startswith("5. "):
        row5 = r
    elif v.startswith("6. "):
        row6 = r
if row5 is None or row6 is None:
    raise SystemExit("找不到 5./6. 两行，实际: %s" % [v[:20] for _, v in items])

v5 = ws.cell(row5, 1).value
v6 = ws.cell(row6, 1).value
ws.cell(row5, 1).value = v6      # "6. ..." 往上挪
ws.cell(row6, 1).value = v5      # "5. ..." 往下挪

wb.save(PATH)

print("\n插入后：")
wb2 = openpyxl.load_workbook(PATH)
ws2 = wb2["使用说明"]
for r in range(1, ws2.max_row + 1):
    v = ws2.cell(r, 1).value
    if isinstance(v, str) and v.strip():
        print("  r%-3d %s" % (r, v.strip()[:110]))

# 结构复核
ws3 = wb2["技能清单"]
print("\n结构复核: dims=%dx%d  auto_filter=%s" % (ws3.max_row, ws3.max_column, ws3.auto_filter.ref))
for dv in ws3.data_validations.dataValidation:
    print("数据验证:", dv.formula1, dv.sqref)
print("条件格式条数:", sum(len(x.rules) for x in ws3.conditional_formatting))
