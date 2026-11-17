# -*- coding: utf-8 -*-
"""
日程表改动：SQL 学习与学校作业彻底解绑 + 11-16 下午档假欠账销账
- 幂等：重复执行结果一致
- 先备份：备份到 D:\\AI应用工程师\\09-求职资产\\
- 绝对路径（不用 ../../ 相对写法，见工具链坑 T40）
"""
import shutil
import datetime
from pathlib import Path

import openpyxl

表路径 = Path(r'C:/Users/15816/Desktop/AI应用工程师学习日程表_已按摸底调整.xlsx')
归档位 = Path(r'D:/AI应用工程师/09-求职资产')
工作表名 = '每日计划'

备份位 = 归档位 / ('日程表.SQL解绑备份_%s.xlsx' %
                datetime.datetime.now().strftime('%Y%m%d_%H%M'))
归档位.mkdir(parents=True, exist_ok=True)
assert not 备份位.exists(), '备份位已存在，停止以免覆盖'
shutil.copy2(表路径, 备份位)
print('✅ 已备份:', 备份位)

wb = openpyxl.load_workbook(表路径)
ws = wb[工作表名]

改动清单 = []


def 改(行, 列, 新值, 说明):
    旧值 = ws.cell(行, 列).value
    if 旧值 == 新值:
        print('  = 无变化  R%d C%d  %s' % (行, 列, 说明))
        return
    assert 新值 is not None, '新值不能为 None'
    ws.cell(行, 列).value = 新值
    改动清单.append((行, 列, 旧值, 新值, 说明))
    print('  ✔ R%d C%d  %s' % (行, 列, 说明))


print('\n=== 1. SQL 学习载体与依据（作业解绑）===')

# R51 (11-16) 晚上：SQL 项加独立依据标注（不提"作业"，只留依据）
改(51, 7,
   '笔记（1.5h）｜看 JD 15min｜📌 SQL：SELECT/WHERE 概念（0.5h）〔依据 JD-01/JD-02 硬要求〕',
   '11-16 晚上：SQL 项标注独立依据（JD 硬要求）')

# R52 (11-17) 晚上：Navicat+MySQL 实操 → SQLite 实操①（零安装）
改(52, 7,
   '复习（1.5h）｜看 JD 15min｜📌 SQL：JOIN 连接表（0.5h）｜SQLite 实操①：建表灌数 + JOIN 查询（1h）',
   '11-17 晚上：Navicat+MySQL 实操 → SQLite 实操①（本机未装 Navicat/MySQL，SQLite 零成本且覆盖 JOIN）')

# R53 (11-18) 上午：SQLite 查 CSV → SQLite 实操②（补 GROUP BY / ORDER BY 两样）
改(53, 5,
   '综合项目启动：课件 PDF→提取文本→存 CSV（2h）｜📌 SQL 实操②：GROUP BY/COUNT + ORDER BY/LIMIT 聚合统计（1h）',
   '11-18 上午：补 GROUP BY/ORDER BY（原计划漏掉这两样）')

# R54 (11-19) 晚上：复盘档补 MySQL 关键词覆盖（不装 MySQL，用语法差异对照）
改(54, 7,
   '周四大复习：错题重练 + 查漏补缺（2h）｜查《错题追踪.md》高频题 + 本周新错｜📌 SQL 复盘 + 整理成笔记（1h）｜SQLite→MySQL 语法差异对照（覆盖 JD-01 MySQL 关键词，不装 MySQL）｜对照《能力缺口清单》验收',
   '11-19 晚上：复盘档补 MySQL 语法差异对照')

print('\n=== 2. 11-16 下午档假欠账销账（实际 11-17 已完成）===')
改(51, 9,
   '🟡 部分完成 11-16（2026-11-17 17:25 回填：上午 + 下午两档均已销账，晚上档如实留账）｜'
   '上午 ✅ pandas 读 CSV/Excel + 查看 —— 实际于 11-15 晚上提前完成，产出 练习/11.15练习_pandas读CSV与查看.py'
   '（8 题全绿；文件内自动检查 + 独立脚本用标准库 csv 重算真相，双重验证；数据文件 练习/数据/news_示例.csv + .xlsx '
   '为真实新闻数据，CSV 真带 utf-8-sig BOM）｜'
   '下午 ✅ pandas 筛选/增删列 —— 实际于 11-17 16:45 完成，产出 练习/11.17练习_pandas筛选与增删列.py'
   '（8 题全绿；文件内自动检查 + 独立脚本用标准库 csv 重算真相，双重验证；数据文件 练习/数据/news_多天版.csv，'
   '横跨 11-14~11-23 共 10 天，星期由 datetime 从日期推导）｜'
   '晚上 ❌ 笔记 1.5h + 看 JD 15min + 📌 SQL SELECT/WHERE 概念 0.5h 未做'
   '（11-16 原本还列有学校作业实验项，已于 11-17 从学习计划移除 —— 那是学校作业，不是学习素材，不计欠账）｜'
   '⚠️ 注：11-16 当天无任何学习产出，销的两档均为跨天完成，不等于当天学过',
   '11-16 状态栏：销下午档 + 简化作业表述')

wb.save(表路径)
print('\n✅ 已保存到:', 表路径)
print('   实际改动单元格数:', len(改动清单))
for 行, 列, 旧, 新, 说明 in 改动清单:
    print('   R%d C%d  %s' % (行, 列, 说明))
print('\n备份位:', 备份位)
