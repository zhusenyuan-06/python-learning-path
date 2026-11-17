# -*- coding: utf-8 -*-
"""写入 T49（验证判据本身也会错 —— 全文 == 的陷阱）"""
import json
import datetime
from pathlib import Path

坑文件 = Path(r'D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject/笔记/工具链/工具链坑.json')

d = json.loads(坑文件.read_text(encoding='utf-8'))
print('原有条数:', len(d['items']))

已有 = {it['id'] for it in d['items']}

新坑 = {
    'id': 'T49',
    'title': '验证两个库的输出时，别拿「全文 ==」当判据 —— 排版差异会被误判成内容错误',
    'hits': 1,
    'severity': '高',
    '场景': '用另一个库独立重算 PDF 提取结果，验证自己的答案',
    '现象': 'pymupdf 拼全文 5400 字符 vs pdfplumber 5462 字符 → 判「不一致」，差点以为自己答案写错',
    '原因': '两库对【页眉页脚的位置】和【空白符】处理不同。实测：去空白后长度完全相同（4878=4878）、字符频次完全相同，差别只是页眉在每页开头还是结尾',
    '教训': '⛔ 全文 == 是最脆的判据 —— 换库/换版本/换页眉就挂。⛔ 而且看到不一致时，【先怀疑判据，再怀疑被验证对象】（T38 的翻版）',
    '怎么防': '等价判据：去空白 + 去页眉页脚（re.sub 删「第N页，共M页」）后比字符多重集 Counter；或只比关键词 + 长度区间 + 页数三个弱约束',
    '发现时间': '2026-11-17',
}

added = 0
if 新坑['id'] in 已有:
    print('跳过已存在:', 新坑['id'])
else:
    d['items'].append(新坑)
    added = 1
    print('✅ 写入', 新坑['id'], 新坑['title'][:44])

d['updated'] = datetime.datetime.now().strftime('%Y-%m-%d')
坑文件.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
print('新增 %d 条，现共 %d 条' % (added, len(d['items'])))
