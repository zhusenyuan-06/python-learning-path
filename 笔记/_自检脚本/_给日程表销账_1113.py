# -*- coding: utf-8 -*-
"""给日程表 2026-11-13 完成项销账（幂等，可重复运行）

改动点：
  R48（11-13 周五）上午「综合：API 数据存 CSV」→ 标记 11-14 补做完成
  R48（11-13 周五）下午「周复盘」→ 标记 11-14 补做完成
  R48（11-13 周五）晚上「休息」→ 计划内，不动

不动 11-14 那行：上午两档（LeetCode + Streamlit）都还没做，属于真欠账。
"""
import datetime
import os
import shutil
import openpyxl

PATH = r"C:\Users\15816\Desktop\AI应用工程师学习日程表_已按摸底调整.xlsx"
备份目录 = r"D:\AI应用工程师\09-求职资产"


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

    r48 = 找行(ws, "2026-11-13")
    assert r48 is not None, "找不到 11-13 那行"
    print(f"  R48 = 第 {r48} 行")

    旧状态 = str(ws.cell(r48, 9).value or "")
    if "11-14 补做" in 旧状态:
        print("⚠️  R48 状态列已含「11-14 补做」，跳过（幂等）")
        return

    # ---- 上午：综合 API 数据存 CSV ----
    旧e = str(ws.cell(r48, 5).value or "")
    assert "API 数据存 CSV" in 旧e, f"R48 上午内容对不上：{旧e!r}"
    ws.cell(r48, 5).value = (
        "综合：API 数据存 CSV（2h）｜📌 欠 11-13，✅ 已于 11-14 晚补做完成"
        " —— 产出：projects/api-demo/09_综合_API取数存CSV.py（8.3KB，两个 TODO 全填）"
        " + 输出/news_综合版.csv（16 行 × 4 列，utf-8-sig + CRLF 实测正常）"
        " + projects/api-demo/README.md 更新（作品 10「综合 API 取数工具」成立）"
    )
    print(f"  R48 上午: {旧e[:30]}... → 已销账")

    # ---- 下午：周复盘 ----
    旧f = str(ws.cell(r48, 6).value or "")
    assert "周复盘" in 旧f, f"R48 下午内容对不上：{旧f!r}"
    ws.cell(r48, 6).value = (
        "周复盘（2h）｜📌 欠 11-13，✅ 已于 11-14 晚补做完成"
        " —— 产出：笔记/周复盘/周复盘_2026-W46.md（19.3KB，ISO 周次 W46 = 11-09~11-15，"
        "六段结构齐全；三个进步 / 欠账补账日期 / 给自己的话已起草待修改）"
    )
    print(f"  R48 下午: {旧f[:30]}... → 已销账")

    # ---- 状态列（第 9 列） ----
    ws.cell(r48, 9).value = (
        "✅ 已完成 11-14 补做（原计划 11-13 当天未做，延至 11-14 晚补做完毕）"
        "｜上午 ✅ 09_综合_API取数存CSV.py + 输出/news_综合版.csv（作品 10 成立）"
        "｜下午 ✅ 周复盘_2026-W46.md"
        "｜晚上 休息（计划内，不计）"
    )
    print("  R48 状态列 → 已销账")

    wb.save(PATH)
    print("✅ 已保存")

    # ---- 回读校验 ----
    wb2 = openpyxl.load_workbook(PATH, data_only=True)
    ws2 = wb2["每日计划"]
    r = 找行(ws2, "2026-11-13")
    print("✅ 回读 11-13 上午:", str(ws2.cell(r, 5).value)[:70], "...")
    print("✅ 回读 11-13 下午:", str(ws2.cell(r, 6).value)[:70], "...")
    print("✅ 回读 11-13 状态:", str(ws2.cell(r, 9).value)[:70], "...")
    # 顺带确认 11-14 那行还是空的（真欠账没误销）
    r14 = 找行(ws2, "2026-11-14")
    print("✅ 回读 11-14 状态（应仍为空）:", repr(ws2.cell(r14, 9).value))
    print("✅ sheet 列表:", wb2.sheetnames)


if __name__ == "__main__":
    main()
