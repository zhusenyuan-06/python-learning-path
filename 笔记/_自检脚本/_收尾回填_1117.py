# -*- coding: utf-8 -*-
"""
11-17 收尾回填：把「收尾」事实更新进状态栏（只改 R52 C9）
- 幂等：目标句已写入则跳过
- 先备份到 D:\\AI应用工程师\\09-求职资产\\
- 绝对路径（见工具链坑 T40）
"""
import shutil
import datetime
from pathlib import Path

import openpyxl

表路径 = Path(r'C:/Users/15816/Desktop/AI应用工程师学习日程表_已按摸底调整.xlsx')
归档位 = Path(r'D:/AI应用工程师/09-求职资产')
工作表名 = '每日计划'
行号 = 52  # 11-17

旧收尾 = ('11-17 收尾：工具链坑 45→50 条（T46 讲「PDF 提不出文字」前必须实跑 / T47 三库提取文本不一致 / '
           'T48 表格在第几页得逐页试 / T49 页眉差异 / T50 heredoc 吞转义）；'
           'git commit ×12（15:12 → 19:12），尚未 push')

新收尾 = ('11-17 收尾：工具链坑 45→55 条（T46~T50 讲义/解析类：讲「PDF 提不出文字」前必须实跑 / 三库提取文本不一致 / '
           '表格在第几页得逐页试 / 页眉差异 / heredoc 吞转义；T51~T55 push 实战：探针全灭别放弃·DNS 解析出的那个 IP 才是唯一能 push 的 / '
           '用 curl POST 探针判 IP 而非拿 git push 试错 / curl 通≠git 通且双向都会不一致 / gh-proxy 等镜像只代理 GET 只能当校验通道 / '
           '探针 200≠能 push·判据只有 git 实推）；'
           'git commit ×15（15:12 → 19:50）已全部 push（远端 main = 074682a，ls-remote + GitHub API 双通道校验一致）；'
           'push 流程升级 v4：新增 工具/push_post_probe.py + 1.5/4 POST 探针步骤 + 2.5/4 裸 DNS 兜底，升级后一次跑通')

备份位 = 归档位 / ('日程表.收尾回填备份_%s.xlsx' %
                datetime.datetime.now().strftime('%Y%m%d_%H%M'))
归档位.mkdir(parents=True, exist_ok=True)
assert not 备份位.exists(), '备份位已存在，停止以免覆盖'
shutil.copy2(表路径, 备份位)
print('✅ 已备份:', 备份位)

wb = openpyxl.load_workbook(表路径)
ws = wb[工作表名]
旧值 = ws.cell(行号, 9).value

assert isinstance(旧值, str) and 旧值, '状态栏为空，停止'
if 新收尾 in 旧值:
    print('= 状态栏已是最新收尾句，无需改动（幂等）')
elif 旧收尾 in 旧值:
    新值 = 旧值.replace(旧收尾, 新收尾)
    ws.cell(行号, 9).value = 新值
    wb.save(表路径)
    print('✔ 已更新 R%d C9 的收尾句' % 行号)
else:
    print('[X] 旧收尾句没找到，状态栏可能已被改过 —— 不动，退出')
    print('当前收尾片段:', 旧值[-200:])
    raise SystemExit(1)

wb2 = openpyxl.load_workbook(表路径)
校验 = wb2[工作表名].cell(行号, 9).value
assert 新收尾 in 校验, '回写校验失败'
print('✅ 回写校验通过，状态栏长度', len(str(校验)))
print('   排期列未动：E=%r F=%r G=%r' % (
    ws.cell(行号, 5).value, ws.cell(行号, 6).value, ws.cell(行号, 7).value))
print('备份位:', 备份位)
