# -*- coding: utf-8 -*-
"""给日程表 2026-11-15 收尾回填（幂等）

11-15 实际做的：
  · 上午：补 11-14 顺延的 LeetCode 125（验证回文串）—— 两解法写完跑绿，10 用例全过
  · 晚上（计划内休息，实际主动加练）：E02/E35 错题重练 —— 重做区 6 条检查全绿
  · 额外提前启动 11-16 上午档：pandas 读 CSV/Excel + 查看 —— 8 题全绿（双重验证）

同时销掉 11-14 状态栏里那条「⬜ LeetCode 代码未写 → 顺延 11-15 上午」。
"""
import datetime
import os
import shutil
import openpyxl

PATH = r"C:\Users\15816\Desktop\AI应用工程师学习日程表_已按摸底调整.xlsx"
备份目录 = r"D:\AI应用工程师\09-求职资产"

状态15 = (
    "✅ 已完成 11-15（原计划 1 档，实际 3 档 + 额外提前开了一档）"
    "｜上午 ✅ 补 11-14 顺延的 LeetCode 125 验证回文串：练习/11.14练习_LeetCode_验证回文串.py "
    "两解法（正则清洗法 + 双指针）写完跑绿，10 个用例全过"
    "｜晚上 ✅ E02/E35 错题重练（计划外主动加练）：练习/11.15练习_E02_E35重练.py —— "
    "第一版三题①「错在哪」全对、②「改写成正确版」三题同栽在"
    "「只解开变量冲突、没保住 return 契约」（return 出的是 int 不是字典 / 循环体 pass 从没比较过 / "
    "for 里 return 只走第一次迭代 + all-any 语义反了），讲解后重做区 6 条检查全绿"
    "｜📌 提前启动 11-16 上午档：pandas 读 CSV/Excel + 查看 —— "
    "练习/11.15练习_pandas读CSV与查看.py 8 题全绿（文件内自动检查 + 独立脚本用标准库 csv "
    "重算真相双重验证；数据文件练习/数据/news_示例.csv + .xlsx 为真实新闻数据，CSV 真带 BOM）"
    "｜下午 休息（计划内，不计）｜晚上 原计划休息，实际用来自习错题 + 提前开新档"
    "｜11-15 收尾：错题池 E02/E35 各 record pass → 连对各 1/2；"
    "工具链坑 26→38 条（本轮新登记 T36 自动检查没调用户代码 / T37 带提示的 pass 不算独立掌握 / "
    "T38 独立验证的判据自己也会错）；git commit ×3（e3a7803 / 919e967 / 23d17f2，本轮收尾时统一 push）"
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

    # ================= 11-14：销掉 LeetCode 顺延那条 =================
    r14 = 找行(ws, "2026-11-14")
    assert r14 is not None, "找不到 11-14 那行"
    旧14 = str(ws.cell(r14, 9).value or "")
    旧片段 = "｜⬜ LeetCode 代码未写 → 顺延 11-15 上午"
    新片段 = ("｜✅ LeetCode 代码已于 11-15 上午补做完成"
              "（练习/11.14练习_LeetCode_验证回文串.py 两解法 + 10 用例全绿）")
    if 旧片段 in 旧14:
        ws.cell(r14, 9).value = 旧14.replace(旧片段, 新片段)
        print("  R49(11-14) 状态列 → LeetCode 顺延已销账")
    else:
        print("  R49(11-14) 状态列 → 未找到待销片段，跳过（幂等）")

    # ================= 11-15：写状态栏 =================
    r15 = 找行(ws, "2026-11-15")
    assert r15 is not None, "找不到 11-15 那行"
    旧15 = str(ws.cell(r15, 9).value or "")
    if "11-15 收尾" in 旧15:
        print("  R50(11-15) 状态列已含「11-15 收尾」，跳过（幂等）")
    else:
        旧e15 = str(ws.cell(r15, 5).value or "")
        assert "补 11-14" in 旧e15, f"R50 上午内容对不上：{旧e15!r}"
        ws.cell(r15, 9).value = 状态15
        print("  R50(11-15) 状态列 → 已回填")

    wb.save(PATH)
    print("✅ 已保存")

    # ================= 回读校验 =================
    wb2 = openpyxl.load_workbook(PATH, data_only=True)
    ws2 = wb2["每日计划"]
    for 日期 in ["2026-11-13", "2026-11-14", "2026-11-15"]:
        r = 找行(ws2, 日期)
        文本 = str(ws2.cell(r, 9).value)
        print("─" * 60)
        print("✅ 回读 %s（第 %d 行）状态栏：" % (日期, r))
        print("   ", 文本[:300])
    print("✅ sheet 列表:", wb2.sheetnames)


if __name__ == "__main__":
    main()
