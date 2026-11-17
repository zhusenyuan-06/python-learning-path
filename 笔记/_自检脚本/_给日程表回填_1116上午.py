# -*- coding: utf-8 -*-
"""给日程表 2026-11-16 回填（幂等）

背景：11-16 上午档「pandas 读 CSV/Excel + 查看」实际已于 11-15 晚上提前完成，
      但 11-16 状态栏一直空白 → 属于「假欠账」，本次只勾这一档。
      11-16 下午/晚上确实 0 产出（如实标未做 + 顺延，不虚报）。
"""
import datetime
import os
import shutil
import openpyxl

PATH = r"C:\Users\15816\Desktop\AI应用工程师学习日程表_已按摸底调整.xlsx"
备份目录 = r"D:\AI应用工程师\09-求职资产"

状态16 = (
    "🟡 部分完成 11-16（2026-11-17 15:10 回填：只销上午一档，其余如实留账）"
    "｜上午 ✅ pandas 读 CSV/Excel + 查看 —— 实际于 11-15 晚上提前完成，"
    "产出 练习/11.15练习_pandas读CSV与查看.py（8 题全绿；文件内自动检查 + "
    "独立脚本用标准库 csv 重算真相，双重验证；数据文件 练习/数据/news_示例.csv + "
    ".xlsx 为真实新闻数据，CSV 真带 utf-8-sig BOM）"
    "｜下午 ❌ pandas 筛选/增删列 未做（0 产出）→ 顺延 11-17"
    "｜晚上 ❌ 笔记 1.5h + SQL SELECT/WHERE 概念 0.5h + 教材《6-2 实验3》实验1 未做"
    "｜注：本行为跨天提前完成的销账，不代表 11-16 当天有学习产出"
)


def 找行(ws, 日期):
    for r in range(2, ws.max_row + 1):
        d = ws.cell(r, 2).value
        ds = str(d)[:10] if d is not None else ""
        if ds == 日期:
            return r
    return None


def main():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    os.makedirs(备份目录, exist_ok=True)
    备份 = os.path.join(备份目录, f"日程表.销账备份_{stamp}.xlsx")
    shutil.copy2(PATH, 备份)
    print("✅ 已备份:", 备份)

    wb = openpyxl.load_workbook(PATH)
    ws = wb["每日计划"]

    r16 = 找行(ws, "2026-11-16")
    assert r16 is not None, "找不到 11-16 那行"
    旧16 = str(ws.cell(r16, 9).value or "")
    if "2026-11-17 15:10 回填" in 旧16:
        print("  R51(11-16) 状态列已回填，跳过（幂等）")
    else:
        上午16 = str(ws.cell(r16, 5).value or "")
        assert "pandas 读 CSV/Excel" in 上午16, f"R51 上午内容对不上：{上午16!r}"
        assert 旧16.strip() == "", f"R51 状态列非空，先人工确认：{旧16!r}"
        ws.cell(r16, 9).value = 状态16
        print("  R51(11-16) 状态列 → 已回填（上午 ✅ / 下午 ❌ / 晚上 ❌）")

    wb.save(PATH)
    print("✅ 已保存")

    # ================= 回读校验 =================
    wb2 = openpyxl.load_workbook(PATH, data_only=True)
    ws2 = wb2["每日计划"]
    for 日期 in ["2026-11-15", "2026-11-16", "2026-11-17"]:
        r = 找行(ws2, 日期)
        文本 = str(ws2.cell(r, 9).value or "(空)")
        print("─" * 60)
        print("✅ 回读 %s（第 %d 行）状态栏：" % (日期, r))
        print("   ", 文本[:260])
    print("✅ sheet 列表:", wb2.sheetnames)


if __name__ == "__main__":
    main()
