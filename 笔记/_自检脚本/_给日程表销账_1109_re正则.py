# -*- coding: utf-8 -*-
"""给日程表 2026-11-09 欠账销账（re 正则基础 + 提取日期/邮箱），幂等

改动点：
  R44（11-09 周一）下午「re 正则基础（2h）」→ 标记 11-14 补做完成
  R44（11-09 周一）晚上「提取文本中的日期/邮箱（1.5h）」→ 标记 11-14 补做完成
  R44（11-09 周一）第 9 列状态栏 → 追加 11-14 销账说明

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

    r44 = 找行(ws, "2026-11-09")
    assert r44 is not None, "找不到 11-09 那行"
    print(f"  R44 = 第 {r44} 行")

    旧状态 = str(ws.cell(r44, 9).value or "")
    if "11-14 销账" in 旧状态:
        print("⚠️  R44 状态列已含「11-14 销账」，跳过（幂等）")
        return

    # ---- 下午：re 正则基础 ----
    旧f = str(ws.cell(r44, 6).value or "")
    assert "re 正则基础" in 旧f, f"R44 下午内容对不上：{旧f!r}"
    ws.cell(r44, 6).value = (
        "re 正则基础（2h）｜📌 欠 11-09，✅ 已于 11-14 晚补做完成"
        " —— 产出：练习/11.14练习_re正则基础.py（8 个任务全跑通，exit 0）"
        " + 练习/_参考样例_re语法.py（10 段语法样例，全部实跑）"
        " + 笔记/讲义/11-14_讲义_re正则.md（12 节，输出全部实跑可复现）"
        "；新登记 E42「findall 返回字符串列表 / finditer 返回 Match 对象」"
    )
    print("  R44 下午 → 已销账")

    # ---- 晚上：提取文本中的日期/邮箱 ----
    旧g = str(ws.cell(r44, 7).value or "")
    assert "日期" in 旧g and "邮箱" in 旧g, f"R44 晚上内容对不上：{旧g!r}"
    ws.cell(r44, 7).value = (
        "练习：提取文本中的日期/邮箱（1.5h）｜盯 2028 届校招/实习公告 15min"
        " ｜📌 欠 11-09，✅ 已于 11-14 晚补做完成"
        " —— 产出：练习/11.14练习_re正则基础.py 任务 6/7"
        "（日期 / 中文日期 / 邮箱 / 手机号 四条正则全部跑通，"
        "wangwu@school.edu.cn 多段域名完整截出；"
        "re.search → 判空 → group → datetime.strptime → 写文件全链路走通，"
        "产出 练习/_输出_re正则演示/日期.txt）"
    )
    print("  R44 晚上 → 已销账")

    # ---- 状态列（第 9 列）追加 ----
    ws.cell(r44, 9).value = 旧状态 + (
        " ｜ 11-14 销账：⬜ 下午 re 正则基础 ✅ 11-14 晚补做完成"
        "（讲义 + 语法样例 + 练习 3 个文件，新登记 E42）；"
        "⬜ 晚上 提取日期/邮箱 ✅ 11-14 晚一并完成"
        "（任务 6/7 跑通，产出 _输出_re正则演示/日期.txt）"
        " —— ⚠️ 本次由 AI 补齐代码（用户写任务 1-③ 时卡在 findall/finditer 返回类型），"
        "文字回答（任务 3-③ / 任务 8 自测题）留给用户自己写。"
    )
    print("  R44 状态列 → 已追加 11-14 销账说明")

    wb.save(PATH)
    print("✅ 已保存")

    # ---- 回读校验 ----
    wb2 = openpyxl.load_workbook(PATH, data_only=True)
    ws2 = wb2["每日计划"]
    r = 找行(ws2, "2026-11-09")
    print("✅ 回读 11-09 下午:", str(ws2.cell(r, 6).value)[:70], "...")
    print("✅ 回读 11-09 晚上:", str(ws2.cell(r, 7).value)[:70], "...")
    print("✅ 回读 11-09 状态:", str(ws2.cell(r, 9).value)[-90:])
    r14 = 找行(ws2, "2026-11-14")
    print("✅ 回读 11-14 状态（应仍为空）:", repr(ws2.cell(r14, 9).value))
    print("✅ sheet 列表:", wb2.sheetnames)


if __name__ == "__main__":
    main()
