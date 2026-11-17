# -*- coding: utf-8 -*-
"""
日程表回填：11-17 上午/下午两档（PDF 解析线）销账
- 只改【每日计划】表 R52 C9（状态栏），不动 5/6/7 列排期
- 幂等：目标值已写入则不重复改
- 先备份到 D:\\AI应用工程师\\09-求职资产\\
- 绝对路径（不用 ../../ 相对写法，见工具链坑 T40）
"""
import shutil
import datetime
from pathlib import Path

import openpyxl

表路径 = Path(r'C:/Users/15816/Desktop/AI应用工程师学习日程表_已按摸底调整.xlsx')
归档位 = Path(r'D:/AI应用工程师/09-求职资产')
工作表名 = '每日计划'
行号 = 52  # 11-17

现在 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

目标值 = (
    '🟡 部分完成 11-17（%s 回填）｜'
    '上午 ✅ PyPDF2/pdfplumber 解析 PDF 文本 —— 实际做成 PDF 解析线整条：'
    '讲义 笔记/讲义/11-17_讲义_PDF解析.md（367 行）+ 可跑样例 练习/_参考样例_PDF解析.py（309 行）+ '
    '练习 练习/11.17练习_PDF解析.py（6 题，本机实跑 6/6 全绿）；'
    '从 2 库扩到 3 库对比（PyPDF2 3.0.1 / pdfplumber 0.11.10 / pymupdf），'
    '98 页实测 pymupdf 0.77~0.8 秒 ≪ PyPDF2 24~27 秒 ≪ pdfplumber 46~48 秒（快 29~35 倍）｜'
    '下午 ✅ 提取课件某页文本 —— 6 题全部做完并在作答区逐行写教学注释：'
    '数页数 8 / 取第 3 页 / 拼全文 / 找关键词页 [1,3,6] / 找扫描页 44 / 存进 SQLite 8 行；'
    '素材是 Downloads 里 6 份真实课件 PDF（主素材《计算机网络基础》复习题-答案版 8 页，'
    '反面素材《大学物理实验（一）》讲义 98 页含 44 个扫描页，第 4~47 页连续）｜'
    '晚上 ✅ 看 JD 15min（JD-10~14 已登记）｜'
    '✅ 📌 SQL 概念线 —— 实际做的是 SELECT/WHERE 两份讲义（比原排的 JOIN 更前置）｜'
    '❌ 📌 SQL 练习 8 题只写了第 1 题 → 已排到 11-18 上午｜'
    '❌ 📌 SQL：JOIN 连接表 + SQLite 实操① 未做 → 顺延到 11-18 下午｜'
    '❌ 复习 1.5h 未做 → 顺延到 11-18 晚上（与原复习档合并）｜'
    '11-17 收尾：工具链坑 45→50 条（T46 讲「PDF 提不出文字」前必须实跑 / T47 三库提取文本不一致 / '
    'T48 表格在第几页得逐页试 / T49 页眉差异 / T50 heredoc 吞转义）；'
    'git commit ×12（15:12 → 19:12），尚未 push｜'
    '⚠️ 上午/下午两档是今晚跨档补做，不等于 11-17 当天学过'
) % 现在

备份位 = 归档位 / ('日程表.回填PDF解析备份_%s.xlsx' %
                datetime.datetime.now().strftime('%Y%m%d_%H%M'))
归档位.mkdir(parents=True, exist_ok=True)
assert not 备份位.exists(), '备份位已存在，停止以免覆盖'
shutil.copy2(表路径, 备份位)
print('✅ 已备份:', 备份位)

wb = openpyxl.load_workbook(表路径)
ws = wb[工作表名]

旧值 = ws.cell(行号, 9).value
print('\n--- 改前状态栏 ---')
print(旧值)

if 旧值 == 目标值:
    print('\n= 状态栏已是目标值，无需改动（幂等）')
else:
    ws.cell(行号, 9).value = 目标值
    wb.save(表路径)
    print('\n✔ 已写入 R%d C9' % 行号)

# 改后复读校验
wb2 = openpyxl.load_workbook(表路径)
新值 = wb2[工作表名].cell(行号, 9).value
assert 新值 == 目标值, '回写校验失败：状态栏与目标值不一致'
print('✅ 回写校验通过，长度', len(str(新值)))
print('✅ 排期列未动：E列=%r F列=%r G列=%r' % (
    ws.cell(行号, 5).value, ws.cell(行号, 6).value, ws.cell(行号, 7).value))
print('备份位:', 备份位)
