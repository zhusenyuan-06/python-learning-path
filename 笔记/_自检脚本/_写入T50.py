# -*- coding: utf-8 -*-
"""写入 T50（Bash heredoc 吞反斜杠 → Python 源码被写坏）"""
import json
import datetime
from pathlib import Path

坑文件 = Path(r'D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject/笔记/工具链/工具链坑.json')

d = json.loads(坑文件.read_text(encoding='utf-8'))
print('原有条数:', len(d['items']))
已有 = {it['id'] for it in d['items']}

新坑 = {
    'id': 'T50',
    'title': '用 Bash heredoc 写含反斜杠的 Python 源码 → 反斜杠被吞，文件当场语法错',
    'hits': 1,
    'severity': '高',
    '场景': '用 `python - <<\'PY\'` 往 .py 文件里写代码，代码里有 \\n 之类转义',
    '现象': '写完后跑文件直接 SyntaxError: unterminated string literal —— 注释里的 "\\n".join(...) 被从中间截断成两行',
    '原因': 'heredoc 内容里的反斜杠 + n 被当成真换行处理，落盘时字符串字面量被拆断',
    '教训': '⛔ 用 heredoc 写「要被执行的 Python 源码」时，反斜杠是隐形炸弹 ⛔ 同一个坑我早就记过（T40 附近那条），但当时只当路径问题，没意识到它会破坏源码',
    '怎么防': '① 写 .py 源码用 Write/Edit 工具，不要用 heredoc ② 必须用 heredoc 时，反斜杠用 chr(92) 构造 ③ 写完立刻 ast.parse() 做语法检查，别直接跑',
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
