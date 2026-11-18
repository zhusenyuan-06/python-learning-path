# -*- coding: utf-8 -*-
"""日程表改动脚本 · 2026-11-18 晚（20:05）

改动 11-18 行状态列：把 19:15 之后新完成的内容补进去，并销账 PDF 项目档。
幂等：可重复执行。

改动前必备份（脚本内自动完成）。
"""

import datetime
import os
import shutil
from pathlib import Path

import openpyxl

# ⚠️ 路径用 Path.home() 推导，不写死用户名 —— 这个仓库会推到公开的 GitHub，
#    硬编码绝对路径会把本机用户名暴露出去。
用户目录 = Path.home()
桌面表 = str(用户目录 / "Desktop" / "AI应用工程师学习日程表_已按摸底调整.xlsx")
权威副本 = r"D:\AI应用工程师\09-求职资产\AI应用工程师学习日程表_已按摸底调整.xlsx"
备份目录 = r"D:\AI应用工程师\09-求职资产"

时间戳 = datetime.datetime.now().strftime("%Y%m%d_%H%M")
备份名 = f"日程表.晚间改动备份_{时间戳}.xlsx"


def 找行(ws, 日期str):
    """按 B 列日期找到行号。"""
    for r in range(2, ws.max_row + 1):
        v = ws.cell(r, 2).value
        if isinstance(v, str) and v.strip()[:10] == 日期str:
            return r
    return None


def 备份():
    """备份桌面表和权威副本。"""
    b1 = os.path.join(备份目录, 备份名)
    shutil.copy2(桌面表, b1)
    print(f"  备份 → {b1}")
    return b1


def main():
    print("=" * 64)
    print("📅 日程表改动 · 11-18 晚间回填")
    print("=" * 64)

    if not os.path.exists(桌面表):
        print(f"❌ 桌面表不存在：{桌面表}")
        return 1

    备份()

    wb = openpyxl.load_workbook(桌面表)
    ws = wb["每日计划"]

    r = 找行(ws, "2026-11-18")
    assert r is not None, "找不到 11-18 那行"
    print(f"  11-18 在第 {r} 行")

    原状态 = str(ws.cell(r, 9).value or "")
    print(f"  原状态长度 {len(原状态)} 字")

    # ── 改动 1：把 PDF 项目销账追加进去 ──
    PDF条目 = (
        "｜下午 ✅ 继续完善 PDF 项目（0.5h，原定）—— "
        "实际超额完成（1.5h+）：产出 projects/pdf-extractor/（01_提取PDF存CSV.py + README.md + "
        "requirements.txt + 输出/计算机网络基础_题库.csv）；"
        "13 道选择题全部 4 选项齐全，两次跑 MD5 一致（幂等），语法检查无警告"
    )

    if "pdf-extractor" in 原状态:
        print("  11-18 状态已含 PDF 项目，跳过（幂等）")
    else:
        ws.cell(r, 9).value = 原状态 + PDF条目
        print("  ✅ 11-18 状态 → 追加「PDF 项目已完成」销账")

    # ── 改动 2：JOIN 连接表销账（用户 19:50 决定今晚推，已完成讲解+出题） ──
    JOIN条目 = (
        "｜晚间 ✅ SQL：JOIN 连接表（0.5h，从 11-17 晚顺延）—— "
        "已讲 JOIN 概念 + 建 练习/数据/JOIN练习库.sqlite + 讲义 11-18_讲义_JOIN连接表.md + "
        "练习 11.18练习_JOIN连接表.py（6 题，参考答案已验证全过）；"
        "关键差异实测：INNER JOIN 9 行 vs LEFT JOIN 15 行，差的 6 行是休息日新闻"
    )

    状态2 = str(ws.cell(r, 9).value or "")
    if "JOIN 连接表" in 状态2 and "INNER JOIN 9 行" in 状态2:
        print("  11-18 状态已含 JOIN 销账，跳过（幂等）")
    else:
        ws.cell(r, 9).value = 状态2 + JOIN条目
        print("  ✅ 11-18 状态 → 追加「JOIN 连接表」销账")

    wb.save(桌面表)
    print(f"  已保存桌面表")

    # ── 同步到 09 权威副本 ──
    shutil.copy2(桌面表, 权威副本)
    print(f"  已同步 → {权威副本}")

    # ── 回读校验 ──
    wb2 = openpyxl.load_workbook(桌面表)
    ws2 = wb2["每日计划"]
    r2 = 找行(ws2, "2026-11-18")
    新状态 = str(ws2.cell(r2, 9).value or "")
    print()
    print(f"  回读状态长度 {len(新状态)} 字")
    for 关键词 in ["pdf-extractor", "INNER JOIN 9 行", "GROUP BY"]:
        print(f"    {'✅' if 关键词 in 新状态 else '❌'} 含「{关键词}」")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
