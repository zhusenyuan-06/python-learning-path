# -*- coding: utf-8 -*-
"""写入工具链坑 T41 / T42 / T43（2026-11-17 17:40~18:00，写 SQL 讲义时踩的）

T41: 讲「某种写法会报错」之前必须在本机实跑 —— SQLite 的兼容性 misfeature
     让「双引号 / == / 小写 and / 反引号 / 方括号」全部不报错（常见说法全错）
T42: 测试破坏性行为（删除/占用）要拿【副本】测，别拿正主测 —— 我把新闻库.sqlite 删了
T43: 文件系统里【不存在】的路径，git status 可能仍报成未跟踪 —— 用 git add --dry-run 验真
"""
import datetime
import os
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.join(HERE, "..", "工具链", "工具链坑.py")

spec = importlib.util.spec_from_file_location("gzk", TRACK)
gzk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gzk)

db = gzk.load()
今天 = datetime.date.today().isoformat()

新增 = [
    {
        "id": "T41",
        "title": "讲「某个写法会报错」之前必须在本机实跑 —— SQLite 的兼容性 misfeature 让常见说法全错",
        "symptom": "2026-11-17 17:30 写 SQL 讲义，我按常见经验写「坑」：\n"
                   "  ❌ 双引号 WHERE 星期 = \"星期二\"  → 双引号在 SQL 里是标识符引号，会报错\n"
                   "  ❌ 两个等号 WHERE 星期 == '星期二' → SQL 里没有 ==，会报错\n"
                   "  ❌ 小写 and → 必须大写 AND，会报错\n"
                   "本机一跑，【三条全部不报错，还返回正确结果】：\n"
                   "  双引号   → [7, 8]   ✅\n"
                   "  ==       → [7, 8]   ✅\n"
                   "  小写 and → [6, 15]  ✅\n"
                   "补测发现反引号（MySQL 风格）、方括号（MSSQL 风格）、全小写关键字 —— 也全认。\n"
                   "真正会报错的只有【不加引号】：no such column: 星期二\n"
                   "→ 如果我没实跑就写进讲义，就会把 3 条【假坑】教给你，\n"
                   "  而你按「标准写法」写反而是对的 —— 讲义就成了误导。",
        "cause": "SQLite 为了兼容各种数据库，故意放宽了 SQL 标准：\n"
                 "  · 关键字大小写不敏感\n"
                 "  · 双引号里的名字如果【找不到对应列】，会退化成字符串字面量\n"
                 "    （SQLite 官方文档叫它 double-quoted string literal misfeature）\n"
                 "  · 额外接受反引号、方括号\n"
                 "  · == 被当 = 的别名\n"
                 "MySQL 也认 == 和双引号（默认模式），但 PostgreSQL 会直接报错。\n"
                 "→ 所以「在 SQLite 上跑通了」≠「这是标准写法」。",
        "solutions": [
            "【铁律】写讲义/文档里任何「X 会报错」的断言之前，先在本机跑一遍。\n"
            "  一行就够：cur.execute(sql) 然后看有没有抛异常。",
            "【三段写法】讲一个写法时，同时给「本机实测结果」+「别的数据库会怎样」+\n"
            "  「所以推荐怎么写」。三段缺一，讲义就会误导人。",
            "【不要照抄别人的坑清单】包括我自己以前写的。\n"
            "  常见说法（双引号报错、== 报错、小写 and 报错）在 SQLite 上全是错的。",
            "【怎么自测方言宽容度】一次性跑一遍这些变体，看哪些认：\n"
            "  双引号 / == / 小写 and / 全小写 / 反引号 / 方括号 /\n"
            "  数值列用单引号 / 数值列用 LIKE / LIKE 的 % 和 _",
            "【真会报错的只有一种】不加引号的裸标识符 → no such column: X\n"
            "  → 教学重点应该放在「字符串必须加引号」，不是「别用双引号」。",
        ],
        "tags": ["SQL", "SQLite", "讲义", "教学", "misfeature", "实跑验证", "方言差异"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    },
    {
        "id": "T42",
        "title": "测破坏性行为（删除/占用/锁）要拿【副本】测 —— 拿正主测把新闻库.sqlite 删了",
        "symptom": "2026-11-17 17:47 我想给讲义加一段「不 close() 会锁住文件」的演示，\n"
                   "于是写了个测试脚本：connect → 建表 → os.remove(库路径) → 看是否报错。\n"
                   "结果：\n"
                   "  · 连接开着时删 → 被 safe-delete 拦截（走回收站失败）→ 报 OSError\n"
                   "  · close 之后删 → 【成功】\n"
                   "→ 我正在用的 练习/数据/新闻库.sqlite 被我自己的测试删掉了。\n"
                   "  它是 8 题练习的数据源，没了练习立刻跑不了。\n"
                   "（同一次事故还暴露了 safe-delete 沙箱：连空文件删除也会被拦，报 trash-failed）",
        "cause": "我想验证的命题是「sqlite 连接开着时文件被锁」，\n"
                 "但我用的【被测对象】正是【生产数据】本身。\n"
                 "→ 测试脚本和真实数据共用同一个路径 = 测试即破坏。\n"
                 "  正确做法：os.path.join(tmpdir, 'test.sqlite') 或 copy 一份再测。",
        "solutions": [
            "【正解】破坏性测试一律用副本：\n"
            "  测试文件 = 数据目录 / '_占用测试.sqlite'   ← 专用测试文件名\n"
            "  测完 os.remove(测试文件)，绝不用库路径。",
            "【删之前先问】这个路径是不是别人正在用的？先 git ls-files 查它是否被跟踪 ——\n"
            "  被跟踪 = 是仓库资产 = 不能拿来做破坏性实验。",
            "【误删后的正确恢复流程】（这次用上了）：\n"
            "  ① 找数据源 —— 本次是 数据/news_多天版.csv（同源，15 行）\n"
            "  ② 按原 schema 重建（sqlite_master 里读到的 CREATE TABLE 语句）\n"
            "  ③ 【用独立通道重算期望值】—— 标准库 csv 跑一遍，跟 SQL 结果比对，全部一致才算恢复\n"
            "  ④ git hash-object 对比原文件 → 8f02fdb86858b7917df5cc376c082d46726d7b33，\n"
            "     与 git 里存的完全一致 → 逐字节恢复成功",
            "【教训】测「删除」「占用」「权限」这类行为，永远先问：\n"
            "  「我拿的是副本吗？」—— 事故的代价和这个问题的答案成正比。",
        ],
        "tags": ["SQLite", "测试", "误删", "破坏性操作", "数据安全", "恢复", "独立重算"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    },
    {
        "id": "T43",
        "title": "文件系统里【不存在】的路径，git status 可能仍报成未跟踪 —— 用 git add --dry-run 验真",
        "symptom": "2026-11-17 17:55 git status 报了一个未跟踪项：\n"
                   "    ?? \"练习/数据/文件夹\"\n"
                   "但用三种方式查都查不到这个东西：\n"
                   "  · ls -la 练习/数据/        → 只有 4 个文件\n"
                   "  · os.walk / os.scandir      → 只有 4 个文件\n"
                   "  · PowerShell Get-ChildItem -Force → 只有 4 个文件\n"
                   "  · [System.IO.Directory]::GetFileSystemEntries → 只有 4 个文件（还打了 UTF16 字节）\n"
                   "→ git status 和真实文件系统【对不上】。\n"
                   "而且 git add -A --dry-run 报的是【另一个路径】：练习/库文件路径。",
        "cause": "两件事叠在一起：\n"
                 "  ① git status 的输出经过引号转义（core.quotepath），中文路径显示成八进制，\n"
                 "     我按八进制反解时解错了字符 —— 解出来是「数据文件夹」，其实是「库文件路径」。\n"
                 "     → 【看到中文路径的八进制转义时，先用 -z 或 --dry-run 拿真实路径】。\n"
                 "  ② 真正的垃圾文件是 练习/库文件路径（0 字节），\n"
                 "     由练习文件讲解区里的示例代码片段 sqlite3.connect(\"库文件路径\") 被执行时生成 ——\n"
                 "     sqlite3.connect 遇到不存在的路径会【静默创建】一个新库文件。",
        "solutions": [
            "【拿真实路径的三个办法】\n"
            "  git status --porcelain -z | tr '\\0' '\\n'      ← -z 不转义\n"
            "  git ls-files --others --exclude-standard -z | xxd   ← 直接看字节\n"
            "  git add -A --dry-run                              ← 告诉 git「如果真提交会加哪些」",
            "【git status 和 git add 报的路���不一样时】→ 相信 git add --dry-run，\n"
            "  因为它走的是真实索引更新路径，status 可能带缓存。",
            "【根因修法】讲解区/文档里的示例代码，不要放【看起来能直接跑】的 connect 调用。\n"
            "  我把 sqlite3.connect(\"库文件路径\") 改成了 sqlite3.connect(库路径)，\n"
            "  指向真实变量 —— 既不会误建文件，也更接近实际用法。",
            "【通用】任何「库/连接会创建文件」的 API（sqlite3.connect、open(..., 'w')、\n"
            "  pd.to_csv、Path.touch）出现在示例里，都要检查它指向哪。",
        ],
        "tags": ["git", "中文路径", "转义", "octal", "dry-run", "sqlite3.connect", "静默创建"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    },
]

for 条目 in 新增:
    if any(x["id"] == 条目["id"] for x in db["items"]):
        print("⚠️ %s 已存在，跳过" % 条目["id"])
    else:
        db["items"].append(条目)
        print("✅ 已写入 %s" % 条目["id"])

gzk.save(db)
print("✅ 已保存并 render")
