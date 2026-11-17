# -*- coding: utf-8 -*-
"""从学习计划中移除「教材《6-2 实验3》实验1（E-R图→表结构）」及其同源项（幂等）

背景：用户澄清 —— 桌面 zip「6-2 实验3 数据库数据表数据管理 发给学生.zip」里的
      「3-2 实验1 数据库设计——概念结构设计.docx」是【学校发给他的作业】，
      不是他要学的教材/素材，因此这批「教材实验」项不属于他的学习计划，予以移除。

处理范围（只动「当前计划」，历史快照不动）：
  1. 日程表 每日计划 R51（11-16）晚上栏 → 去掉「｜教材《6-2 实验3》实验1（E-R图→表结构）」
  2. 日程表 每日计划 R52（11-17）晚上栏 → 去掉「｜教材实验3（建表/增删改查）」
  3. 日程表 R51 状态栏 → 同步去掉「+ 教材《6-2 实验3》实验1 未做」（否则下次盘点又算成欠账）
  4. H 列（当日时长）不动 —— 实测口径：H = 各档时长求和取整到 0.5，
     教材实验项本来就没计入 H（11-16: 2+2+(1.5+0.25+0.5)=6.25→6；11-17: 2+2+(1.5+0.25+0.5+1)=7.25→7）
"""
import datetime
import os
import shutil

import openpyxl

PATH = r"C:\Users\15816\Desktop\AI应用工程师学习日程表_已按摸底调整.xlsx"
备份目录 = r"D:\AI应用工程师\09-求职资产"

要删的片段 = [
    "教材《6-2 实验3》实验1（E-R图→表结构）",
    "教材实验3（建表/增删改查）",
]


def 找行(ws, 日期):
    for r in range(2, ws.max_row + 1):
        d = ws.cell(r, 2).value
        ds = str(d)[:10] if d is not None else ""
        if ds == 日期:
            return r
    return None


def 清洗(文本):
    """从「A｜B｜C」里删掉指定的教材片段，并顺手收拾多余的分隔符"""
    out = 文本
    for 片段 in 要删的片段:
        out = out.replace("｜" + 片段, "")
        out = out.replace(片段 + "｜", "")
        out = out.replace(片段, "")
    # 收拾可能残留的空分隔 / 双分隔 / 尾部分隔
    while "｜｜" in out:
        out = out.replace("｜｜", "｜")
    if out.startswith("｜"):
        out = out[1:]
    if out.endswith("｜"):
        out = out[:-1]
    return out


def main():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    os.makedirs(备份目录, exist_ok=True)
    备份 = os.path.join(备份目录, f"日程表.移除教材作业备份_{stamp}.xlsx")
    shutil.copy2(PATH, 备份)
    print("✅ 已备份:", 备份)

    wb = openpyxl.load_workbook(PATH)
    ws = wb["每日计划"]

    r16 = 找行(ws, "2026-11-16")
    r17 = 找行(ws, "2026-11-17")
    assert r16 and r17, "找不到 11-16 / 11-17 那行"

    # ---- 1) 11-16 晚上栏（G 列 = 7）----
    旧16 = str(ws.cell(r16, 7).value or "")
    新16 = 清洗(旧16)
    if 新16 != 旧16:
        ws.cell(r16, 7).value = 新16
        print("  R51(11-16) 晚上栏 → 已移除教材实验1")
        print("     旧:", 旧16)
        print("     新:", 新16)
    else:
        print("  R51(11-16) 晚上栏 已无教材实验1，跳过（幂等）")

    # ---- 2) 11-17 晚上栏 ----
    旧17 = str(ws.cell(r17, 7).value or "")
    新17 = 清洗(旧17)
    if 新17 != 旧17:
        ws.cell(r17, 7).value = 新17
        print("  R52(11-17) 晚上栏 → 已移除教材实验3")
        print("     旧:", 旧17)
        print("     新:", 新17)
    else:
        print("  R52(11-17) 晚上栏 已无教材实验3，跳过（幂等）")

    # ---- 3) 11-16 状态栏：同步去掉教材实验的欠账描述 ----
    旧状态 = str(ws.cell(r16, 9).value or "")
    if "教材《6-2 实验3》实验1 未做" in 旧状态:
        新状态 = 旧状态.replace(
            "｜晚上 ❌ 笔记 1.5h + SQL SELECT/WHERE 概念 0.5h + 教材《6-2 实验3》实验1 未做",
            "｜晚上 ❌ 笔记 1.5h + 看 JD 15min + 📌 SQL SELECT/WHERE 概念 0.5h 未做"
            "（原「教材《6-2 实验3》实验1」已于 11-17 从学习计划移除 —— 那是学校作业，不是学习素材）",
        )
        assert 新状态 != 旧状态, "状态栏替换失败，停下来人工看"
        ws.cell(r16, 9).value = 新状态
        print("  R51(11-16) 状态栏 → 已同步去掉教材实验1 的欠账描述")
    else:
        print("  R51(11-16) 状态栏 已无教材实验1 欠账描述，跳过（幂等）")

    wb.save(PATH)
    print("✅ 已保存")

    # ================= 回读校验 =================
    wb2 = openpyxl.load_workbook(PATH, data_only=True)
    ws2 = wb2["每日计划"]
    print("─" * 72)
    for 日期 in ["2026-11-16", "2026-11-17"]:
        r = 找行(ws2, 日期)
        print("✅ 回读 %s（第 %d 行）" % (日期, r))
        print("   晚上栏:", str(ws2.cell(r, 7).value))
        print("   时长 H:", ws2.cell(r, 8).value)
        print("   状态栏:", str(ws2.cell(r, 9).value or "(空)")[:300])
        print()
    print("✅ sheet 列表:", wb2.sheetnames)

    # 全表扫一遍，确认没有残留的「教材」字样
    残留 = []
    for r in range(1, ws2.max_row + 1):
        for c in range(1, ws2.max_column + 1):
            v = ws2.cell(r, c).value
            if v and "教材" in str(v):
                残留.append((r, c, str(v)[:90]))
    print()
    print("=== 日程表内「教材」残留检查 ===")
    if 残留:
        for x in 残留:
            print("   ⚠️ R%d C%d: %s" % x)
    else:
        print("   ✅ 0 处残留")


if __name__ == "__main__":
    main()
