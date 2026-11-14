# -*- coding: utf-8 -*-
"""给日程表 2026-11-14 收尾回填 + 11-15 标注（幂等）

11-14 实际做的（远超计划）：
  · 补做 11-12 周四三档（07/08/09 三脚本 + 复习卷 7 题 + 答案卷）
  · 补 11-13 两档（09 脚本 + W46 周复盘）
  · 补 11-09 两笔（re 正则基础 + 提取日期/邮箱）—— 比钉死的 11-21/11-22 早 7 天
  · LeetCode 125 题面骨架（练习文件 + 10 用例 + 两种解法提示），代码未写
  · 日程表销账 ×3 次、工具链坑 T25/T26、git commit ×4

11-14 未做：LeetCode 代码、Streamlit 界面 → 都顺延
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

    # ================= R49：11-14 =================
    r49 = 找行(ws, "2026-11-14")
    assert r49 is not None, "找不到 11-14 那行"
    旧状态 = str(ws.cell(r49, 9).value or "")
    if "11-14 收尾" in 旧状态:
        print("⚠️  R49 状态列已含「11-14 收尾」，跳过（幂等）")
    else:
        旧e = str(ws.cell(r49, 5).value or "")
        assert "LeetCode" in 旧e, f"R49 上午内容对不上：{旧e!r}"
        ws.cell(r49, 5).value = (
            "LeetCode 简单 1 道（1.5h）｜作品化：给通讯录 CLI 加 Streamlit 界面（1.5h）"
            "｜⏳ 11-14 只备了题面：产出 练习/11.14练习_LeetCode_验证回文串.py"
            "（LeetCode 125 验证回文串 · 题面 + 10 个自测用例 + 正则法/双指针两种解法提示 + 三处坑提醒）"
            "，代码（TODO 1/TODO 2）未写 → 📌 顺延 11-15 上午；"
            "Streamlit 界面未做 → 📌 顺延 11-19 上午（跟 SQL 地基并排）"
        )
        ws.cell(r49, 9).value = (
            "⏳ 部分完成 11-14（当天实际做的全是补欠账，不是这行原计划的两件事）"
            "｜✅ 补 11-12 周四三档（07/08/09 + 复习卷 7 题 + 答案卷）"
            "｜✅ 补 11-13 两档（09 脚本 + W46 周复盘）"
            "｜✅ 补 11-09 两笔（re 正则 2h + 提取日期/邮箱 1.5h，比钉死的 11-21/11-22 早 7 天）"
            "｜✅ LeetCode 125 题面备好（10 用例 + 两种解法提示）"
            "｜⬜ LeetCode 代码未写 → 顺延 11-15 上午"
            "｜⬜ Streamlit 未做 → 顺延 11-19 上午"
            "｜ 晚上 休息（计划内，不计）"
            " ｜ 11-14 收尾：错题池 40→41（新登记 E42 findall/finditer 返回类型）；"
            "工具链坑 24→26 条（T25 PyCharm 中文命名组误报 / T26 输出必须实跑验证）"
        )
        print("  R49 上午 + 状态列 → 已回填")

    # ================= R50：11-15 标注补账 =================
    r50 = 找行(ws, "2026-11-15")
    assert r50 is not None, "找不到 11-15 那行"
    旧e50 = str(ws.cell(r50, 5).value or "")
    if "补 11-14" not in 旧e50:
        ws.cell(r50, 5).value = (
            "轻量 1h（1h）｜📌 补 11-14 上午 LeetCode 简单 1 道（1.5h）"
            " —— 产出已备好：练习/11.14练习_LeetCode_验证回文串.py"
            "（125 验证回文串，10 个自测用例，两种解法提示），今天把 TODO 1/TODO 2 写完跑绿即可"
        )
        print("  R50 上午 → 已标注补账")
    else:
        print("  R50 上午 → 已含补账标注，跳过")

    wb.save(PATH)
    print("✅ 已保存")

    # ================= 回读校验 =================
    wb2 = openpyxl.load_workbook(PATH, data_only=True)
    ws2 = wb2["每日计划"]
    for 日期 in ["2026-11-13", "2026-11-14", "2026-11-15"]:
        r = 找行(ws2, 日期)
        print(f"✅ 回读 {日期} 状态:", str(ws2.cell(r, 9).value)[:80])
    print("✅ sheet 列表:", wb2.sheetnames)


if __name__ == "__main__":
    main()
