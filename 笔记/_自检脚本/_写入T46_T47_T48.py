# -*- coding: utf-8 -*-
"""写入 T46/T47/T48 三条工具链坑（PDF 解析这轮踩的）"""
import json
import datetime
from pathlib import Path

坑文件 = Path(r'D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject/笔记/工具链/工具链坑.json')

d = json.loads(坑文件.read_text(encoding='utf-8'))
print('原有条数:', len(d['items']))

已有 = {it['id'] for it in d['items']}

新坑 = [
    {
        'id': 'T46',
        'title': '讲「某 PDF 提取不出文字」前必须实跑 —— 扫描件是隐形杀手',
        'hits': 1,
        'severity': '高',
        '场景': '用 PyPDF2/pdfplumber/pymupdf 解析 PDF 文本',
        '现象': 'PDF 明明 98 页，extract_text() 却有 44 页返回空字符串 —— 那些页是扫描图片，没有文字层',
        '原因': '扫描件页面里只有一张图，没有嵌入字体，PDF 文本层是空的。三个库都一样，不是库的 bug',
        '教训': '⛔ 「能打开、能读页数」≠「每页都有文字」。提取前必须先统计：多少页有文字、多少页是空',
        '怎么防': '写代码前先跑一遍逐页统计：有文字页数 / 空文本页数。判扫描页：pymupdf 的 len(page.get_images()) > 0',
        '发现时间': '2026-11-17',
    },
    {
        'id': 'T47',
        'title': '三个 PDF 库提取的文本【不完全一样】—— 不能直接比字符串',
        'hits': 1,
        'severity': '中',
        '场景': '校验 PDF 提取结果 / 写测试断言',
        '现象': '同一页：PyPDF2 保留页眉但无空格、pdfplumber 丢掉页眉、pymupdf 保留页眉且保留空格。三者字符数 748 / 794 / 777',
        '原因': '三个库的版面还原算法不同：pdfminer 系（pdfplumber）和 PyPDF2 对页眉页脚和空白符的处理不一致',
        '教训': '⛔ 断言不能写 extract_text() == 期望字符串（换库就挂）。只能比关键词、去空格后比、或只比长度',
        '怎么防': '断言用「包含某关键词」+「长度区间」+「页数」三个弱约束，不做全文相等',
        '发现时间': '2026-11-17',
    },
    {
        'id': 'T48',
        'title': '「这个 PDF 没有表格」这种结论，只能在【逐页试过】后说',
        'hits': 1,
        'severity': '中',
        '场景': '用 pdfplumber.extract_tables() 提表格',
        '现象': '测第 1 页表格数=0，就下了「这份 PDF 没表格」的结论；实际第 5 页有 14 列的答案对照表、第 6 页有 3 张表',
        '原因': '表格是按页面的线框（lines/rects）检测的，每页独立，我偷懒只测了第 1 页',
        '教训': '⛔ 只测一页就下全文结论 = 抽样偏差。跟「git status 只看一个文件就报账」是同一类错',
        '怎么防': '涉及「有没有 X」的结论，必须遍历全部（或明确的全部范围）再下。样本量 = 1 的时候要显式标注「仅测了第 N 页」',
        '发现时间': '2026-11-17',
    },
]

added = 0
for it in 新坑:
    if it['id'] in 已有:
        print('跳过已存在:', it['id'])
        continue
    d['items'].append(it)
    added += 1
    print('✅ 写入', it['id'], it['title'][:40])

d['updated'] = datetime.datetime.now().strftime('%Y-%m-%d')
坑文件.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
print('新增 %d 条，现共 %d 条' % (added, len(d['items'])))
