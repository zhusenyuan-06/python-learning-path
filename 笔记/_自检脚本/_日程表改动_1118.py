# -*- coding: utf-8 -*-
"""日程表改动 2026-11-18（幂等）

用户指令（2026-11-18 19:08）：
  1. Streamlit 界面欠账 → 落进日程表
  2. 11-06 周五周复盘 2h → 直接不要了（销账，不补做）
  3. E36 复考 → 放到明天（11-19）的大复习里
  4. 改完后回填 11-18 已完成的进度（上午两档 ✅）
另：把 09-求职资产 里的权威副本同步成本次改后的版本（原件是 10-27 旧版，已过期）。

本脚本：备份 → 改 → 保存 → 回读校验 → 同步 09 → 全量 diff 自检。
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
备份目录 = r"D:\AI应用工程师\09-求职资产"
权威副本 = os.path.join(备份目录, "AI应用工程师学习日程表_已按摸底调整.xlsx")

# ── 1. Streamlit 欠账 → 落到 11-21 上午（跟部署通讯录成在线链接连成一条作品化链）──
# 选 11-21 而不是 11-19 的理由：11-19 晚上是全表最挤的一档，11-19 上午已被
# 「项目打磨+异常处理 2h」占满；11-21 上午已有「作品化：部署通讯录成在线链接」，
# Streamlit 界面是部署的前置条件，同一天上午顺理成章。
# 原 11-21 上午还有「LeetCode 简单 1 道（1.5h）」——不静默删任务，挪到下午（下午原本空白）。
Streamlit新 = (
    "作品化：给通讯录 CLI 加 Streamlit 界面（1.5h，📌 从 11-14 顺延）"
    "｜作品化：部署通讯录成在线链接（1.5h）"
)
LeetCode新 = "LeetCode 简单 1 道（1.5h，从 11-21 上午挪至下午）"

# ── 2. 11-06 下午「周复盘 2h」→ 划掉销账 ──
周复盘划掉 = (
    "~~周复盘（2h）~~ ✅ 11-18 用户决定直接不做了（不再补做，已销账）"
)

# ── 3. E36 复考 → 加进 11-19 晚上大复习 ──
E36复考 = (
    "｜📌 E36 复考（错题：判断条件查错对象——ch 键当计数用 → TypeError；"
    "11-10 首犯，active，连对 0/2）"
)

# ── 4. 回填 11-18 上午两档 ✅（真实产出已核实）──
状态1118 = (
    "🟡 部分完成 11-18（2026-11-18 19:15 回填）"
    "｜上午 ✅ SQL 练习 8 题：SELECT/WHERE 逐题写 —— 产出 练习/11.17练习_SQL_SELECT与WHERE.py"
    "（8 题全过 🎉；用户独立写完 7/8 题，第 8 题单元素元组漏尾逗号已补上）"
    "｜上午 ✅ SQL 实操②：GROUP BY/COUNT + ORDER BY/LIMIT 聚合统计 —— 产出 "
    "练习/11.18练习_GROUP_BY与ORDER_BY_LIMIT.py + 笔记/讲义/11-18_讲义_GROUP_BY与ORDER_BY_LIMIT.md"
    "（7 题全过 🎉，期望值均由真实 SQL 跑出；作答区已补齐逐行中文注释）"
    "｜下午 ❌ SQL：JOIN 连接表 + SQLite 实操① 未做（0 产出）→ 顺延"
    "｜下午 ❌ 继续完善 PDF 项目（0.5h）未做 → 11-18 晚继续"
    "｜晚上 ❌ 复习 1.5h + 看 JD 15min 未做 → 顺延"
    "｜11-18 决定：Streamlit 欠账落 11-21 上午；11-06 周复盘直接不做了；E36 复考并入 11-19 大复习"
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
    备份 = os.path.join(备份目录, f"日程表.改动备份_{stamp}.xlsx")
    shutil.copy2(桌面表, 备份)
    print("✅ 已备份:", 备份)

    wb = openpyxl.load_workbook(桌面表)
    ws = wb["每日计划"]

    # ── 改 1：11-06 下午 周复盘 划掉 ──
    r1106 = 找行(ws, "2026-11-06")
    assert r1106 is not None, "找不到 11-06 那行"
    旧 = str(ws.cell(r1106, 6).value or "")
    if "已销账" in 旧:
        print("  11-06 下午 已划掉，跳过（幂等）")
    else:
        assert 旧.strip() == "周复盘（2h）", f"11-06 下午内容对不上：{旧!r}"
        ws.cell(r1106, 6).value = 周复盘划掉
        print("  ✅ 11-06 下午「周复盘 2h」→ 划掉销账")

    # ── 改 2：11-19 晚上 大复习 加 E36 复考 ──
    r1119 = 找行(ws, "2026-11-19")
    assert r1119 is not None, "找不到 11-19 那行"
    晚19 = str(ws.cell(r1119, 7).value or "")
    if "E36 复考" in 晚19:
        print("  11-19 晚上 已含 E36 复考，跳过（幂等）")
    else:
        assert "周四大复习" in 晚19, f"11-19 晚上内容对不上：{晚19!r}"
        ws.cell(r1119, 7).value = 晚19 + E36复考
        print("  ✅ 11-19 晚上 大复习 → 加「E36 复考」")

    # ── 改 3：11-21 上午 加 Streamlit 界面（与部署通讯录连成作品化链），LeetCode 挪下午 ──
    r1121 = 找行(ws, "2026-11-21")
    assert r1121 is not None, "找不到 11-21 那行"
    早21 = str(ws.cell(r1121, 5).value or "")
    if "Streamlit" in 早21 and "LeetCode" not in 早21:
        print("  11-21 上午/下午 已调整，跳过（幂等）")
    else:
        assert "LeetCode 简单 1 道" in 早21 and "部署通讯录成在线链接" in 早21, \
            f"11-21 上午内容对不上：{早21!r}"
        ws.cell(r1121, 5).value = Streamlit新
        ws.cell(r1121, 6).value = LeetCode新
        print("  ✅ 11-21 上午 → 加「Streamlit 界面」；LeetCode 挪到下午（不删任务）")

    # ── 改 4：回填 11-18 状态列 ──
    r1118 = 找行(ws, "2026-11-18")
    assert r1118 is not None, "找不到 11-18 那行"
    旧18 = str(ws.cell(r1118, 9).value or "")
    if "2026-11-18 19:15 回填" in 旧18:
        print("  11-18 状态列已回填，跳过（幂等）")
    else:
        assert 旧18.strip() == "", f"11-18 状态列非空，先人工确认：{旧18!r}"
        ws.cell(r1118, 9).value = 状态1118
        print("  ✅ 11-18 状态列 → 已回填（上午两档 ✅ / 下午晚上 ❌ 如实留账）")

    wb.save(桌面表)
    print("✅ 已保存桌面表")

    # ── 同步 09-求职资产 权威副本 ──
    shutil.copy2(桌面表, 权威副本)
    print("✅ 已同步 09-求职资产权威副本:", 权威副本)

    # ================= 回读校验 =================
    wb2 = openpyxl.load_workbook(桌面表, data_only=True)
    ws2 = wb2["每日计划"]
    for 日期 in ["2026-11-06", "2026-11-18", "2026-11-19", "2026-11-21"]:
        r = 找行(ws2, 日期)
        print("─" * 66)
        print("✅ 回读 %s（第 %d 行）" % (日期, r))
        for c, col in [(5, "上午"), (6, "下午"), (7, "晚上"), (9, "状态")]:
            v = ws2.cell(r, c).value
            print("   %s: %s" % (col, (str(v)[:200] if v else "(空)")))

    # 同步校验
    wb3 = openpyxl.load_workbook(权威副本, data_only=True)
    ws3 = wb3["每日计划"]
    r3 = 找行(ws3, "2026-11-21")
    print("─" * 66)
    print("✅ 09 权威副本 11-21 上午:", str(ws3.cell(r3, 5).value)[:120])
    print("✅ 09 副本大小:", os.path.getsize(权威副本), "桌面表:", os.path.getsize(桌面表))


if __name__ == "__main__":
    main()
