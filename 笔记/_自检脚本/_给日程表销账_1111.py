# -*- coding: utf-8 -*-
"""给日程表 2026-11-11 完成项销账（幂等，可重复运行）

改动点：
  1. R44（11-09 周一）上午 os/datetime → 标记为 11-11 余量段已完成
  2. R46（11-11 周三）三档全部销账（上午 requests GET+JSON / 下午 公开API存文件 / 晚上 补11-10晚笔记）
  3. R45（11-10 周二）上午 venv+pip、下午 requests 安装 → 标记 11-11 上午已完成
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

    # ---- R44：11-09 上午 os/datetime，顺延 11-11 完成 ----
    r44 = 找行(ws, "2026-11-09")
    assert r44 is not None, "找不到 11-09 那行"
    旧 = ws.cell(r44, 5).value
    assert "os / datetime" in str(旧), f"R44 上午内容对不上：{旧!r}"
    ws.cell(r44, 5).value = (
        "os / datetime 常用（2h）｜📌 欠 11-09，✅ 已于 11-11 下午（余量段）完成"
        " —— 产出：练习/11.11练习_os与datetime.py（7 任务全完成，跑通 exit 0）"
        " + 笔记/讲义/11-11_讲义_os与datetime.md（358 行）"
        " + 练习/_参考样例_os_datetime语法.py（13 段语法样例）"
    )
    print(f"  R44 上午: {str(旧)[:40]}... → 已销账")

    # R44 下午（re 正则）、晚上（提取日期/邮箱）仍未做 —— 保留原样，只在状态列说明
    旧状态 = ws.cell(r44, 9).value
    状态 = (
        (str(旧状态) + " ｜ ") if 旧状态 else ""
    ) + (
        "11-11 销账：上午 os/datetime 已于 11-11 下午余量段完成 ✅（产出 3 个文件，"
        "讲义 358 行 + 练习 7 任务全通 + 语法样例 13 段）；"
        "⬜ 下午 re 正则基础未做；⬜ 晚上 提取日期/邮箱未做 —— "
        "这两项已具备前置条件（os/datetime + strptime 已就位），明日 11-12 可直接开。"
    )
    ws.cell(r44, 9).value = 状态
    print(f"  R44 状态列: → {状态[:60]}...")

    # ---- R46：11-11 当天三档全部销账 ----
    r46 = 找行(ws, "2026-11-11")
    assert r46 is not None, "找不到 11-11 那行"

    ws.cell(r46, 5).value = (
        "requests 发 GET + 解析 JSON（2h）｜📌 明日 ③ ✅ 已完成 11-11 上午"
        " —— 产出 projects/api-demo/01_第一次GET.py ~ 04_正确的错误处理.py（4 个脚本）"
    )
    ws.cell(r46, 6).value = (
        "调一个公开 API（如天气）存文件（2h）｜📌 明日 ④ ✅ 已完成 11-11 上午"
        " —— 产出 projects/api-demo/05_存成JSON.py + 06_存成CSV.py + requirements.txt + README.md（作品 9 成立）"
    )
    ws.cell(r46, 7).value = (
        "补 11-10 晚笔记（1.5h）｜盯 2028 届校招/实习公告 15min ✅ 已完成 11-11 上午"
        " —— 产出 笔记/讲义/11-11_笔记_API链与三个元教训.md（485 行，11 个反思段全完成）"
        " + 笔记/周复盘/周复盘模板_2026-W44.md（新增欠账排序原则）"
    )
    旧46 = ws.cell(r46, 9).value
    ws.cell(r46, 9).value = (
        (str(旧46) + " ｜ ") if 旧46 else ""
    ) + (
        "✅ 已完成 11-11（上午 API 链 4 环全通 + 作品 9 成立 + 笔记定稿；"
        "下午 os/datetime 2h 余量段完成 —— 错题池 36→39 新登记 E37/E38/E39）"
    )
    print(f"  R46 三档 + 状态列 → 已销账")

    # ---- R45：11-10 上午 venv+pip、下午 requests 安装 → 实际 11-11 上午做的 ----
    r45 = 找行(ws, "2026-11-10")
    assert r45 is not None, "找不到 11-10 那行"
    旧e = ws.cell(r45, 5).value
    ws.cell(r45, 5).value = (
        "venv 虚拟环境 + pip 装包（2h）｜📌 欠 11-10，✅ 已于 11-11 上午完成"
        " —— API 链第 1 环（projects/api-demo/.venv + requirements.txt）"
    )
    旧f = ws.cell(r45, 6).value
    ws.cell(r45, 6).value = (
        "第一个第三方库：requests 安装（2h）｜📌 欠 11-10，✅ 已于 11-11 上午完成"
        " —— API 链第 2 环（在项目 .venv 里装 requests，不污染全局）"
    )
    旧45 = ws.cell(r45, 9).value
    ws.cell(r45, 9).value = (
        (str(旧45) + " ｜ ") if 旧45 else ""
    ) + (
        "11-11 销账：⬜ 上午 venv+pip ✅ 11-11 上午已做；⬜ 下午 requests 安装 ✅ 11-11 上午已做；"
        "⬜ 晚上 笔记 ✅ 11-11 上午已做（11-11_笔记_API链与三个元教训.md）"
    )
    print(f"  R45 上午/下午 + 状态列 → 已销账")

    wb.save(PATH)
    print(f"✅ 已保存")

    # ---- 回读校验 ----
    wb2 = openpyxl.load_workbook(PATH, data_only=True)
    ws2 = wb2["每日计划"]
    for 日期, 列名 in [("2026-11-09", "11-09"), ("2026-11-10", "11-10"), ("2026-11-11", "11-11")]:
        r = 找行(ws2, 日期)
        print(f"✅ 回读 {列名}: 上午={str(ws2.cell(r,5).value)[:55]}...")
        print(f"          状态={str(ws2.cell(r,9).value)[:55]}...")
    print("✅ sheet 列表:", wb2.sheetnames)


if __name__ == "__main__":
    main()
