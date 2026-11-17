# -*- coding: utf-8 -*-
"""写入工具链坑 T44 / T45（2026-11-17 18:10~18:30，写 SQL API 讲义时踩的）

T44: SQLite 文件被「测试用的写操作」撑大 —— rollback 也救不回来，文件大小/hash 都变了
T45: `with sqlite3.connect(...)` 只管【事务】，不管【关连接】 —— 出了 with 块连接还开着
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
        "id": "T44",
        "title": "SQLite 文件被「测试用的写操作」撑大 —— rollback 也救不回来",
        "symptom": "2026-11-17 18:10 我在写 API 讲义的配套样例，为了演示 rowcount，\n"
                   "跑了一句：cur.execute(\"UPDATE 新闻 SET 新闻内容 = 新闻内容 WHERE 序号 = 1\")\n"
                   "（改的是自己跟自己一样的值，无意义 UPDATE）\n"
                   "然后 con.rollback()。\n"
                   "结果数据是好的（15 行不变），但【文件大小变了】：\n"
                   "  之前 8192 字节 → 之后 12288 字节（多出 1 个空洞页 freelist）\n"
                   "  git hash-object 也从 8f02fdb8… 变成了 1b1b44c7…\n"
                   "→ 也就是说我把【被 git 跟踪的数据文件】改成了另一个字节序列。\n"
                   "虽然数据完全等价，但版本库里躺着两个不同的文件。",
        "cause": "SQLite 的写事务会先扩展数据库文件，再在事务内部修改页面。\n"
                 "rollback 只回滚【数据内容】，【文件结构】不会缩回去（freelist 页留着）。\n"
                 "→ 一次无意义的 UPDATE 就足以让被跟踪的 .sqlite 文件 hash 变化。\n"
                 "  真正的危险不是数据错，是【版本库里多了个字节不同的同名文件】，\n"
                 "  以后 diff 会显示「二进制文件有变化」，看不懂也定位不了。",
        "solutions": [
            "【铁律】写操作（UPDATE/INSERT/DELETE/CREATE/DROP）一律在【副本】上做。\n"
            "  副本 = shutil.copyfile(库路径, 临时路径)，测完删副本。\n"
            "  正主 .sqlite 文件在整个测试过程中只被 SELECT。",
            "【通用推广】不只是 SQLite —— 任何二进制数据文件（.db/.sqlite/.xlsx/.parquet）\n"
            "  被「读-改-写」过之后，字节层面都可能变。别拿被跟踪的二进制文件做实验。",
            "【误改后的恢复】git checkout -- <路径> 就能回到仓库里的版本。\n"
            "  本次：git checkout -- 练习/数据/新闻库.sqlite → 8192 字节、hash 回到 8f02fdb8… ✅\n"
            "  （前提是【数据没变】，否则要重建 + 独立重算验证）",
            "【自查】改完二进制文件后跑一次：\n"
            "  git hash-object <路径>  vs  git ls-files -s <路径>   ← 两者应完全一致",
            "【教训】T42 说「破坏性测试用副本」，这次证明范围要更广：\n"
            "  不只是【会删文件的操作】，【任何会写文件的操作】都要用副本。",
        ],
        "tags": ["SQLite", "二进制文件", "测试", "副本", "rollback", "freelist", "hash", "git"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    },
    {
        "id": "T45",
        "title": "`with sqlite3.connect(...)` 只管【事务】，不管【关连接】 —— 出了 with 块连接还开着",
        "symptom": "我以为 `with sqlite3.connect(库路径) as con:` 出了块就自动关连接了，\n"
                   "于是把它当成「最安全的写法」写进讲义，还在表格里写「with 不会忘关」。\n"
                   "本机一测：\n"
                   "  with sqlite3.connect(tmp) as con:\n"
                   "      con.execute(\"SELECT 1\")\n"
                   "  con.execute(\"SELECT 1\")   # ← 【不报错】！连接还活着\n"
                   "→ 我写的讲义是错的。\n"
                   "而且因为连接没关，临时文件 os.remove() 报 PermissionError，脚本直接崩。",
        "cause": "Python 的 `with` 语义是「对象有 __enter__/__exit__ 就调它」。\n"
                 "sqlite3.Connection 的 __exit__ 做的是【事务处理】：\n"
                 "  · 正常退出 → commit\n"
                 "  · 抛异常   → rollback\n"
                 "它【不做】close()。这是 Python 数据库 API 的通用设计（DB-API 2.0 规范）。\n"
                 "→ 「with = 自动关」是直觉，但那是文件对象 open() 的行为，不是连接的。\n"
                 "  区别：open() 的 __exit__ 会 close；connect() 的 __exit__ 只管事务。",
        "solutions": [
            "【区分两种 with】\n"
            "  with open(path) as f:      → __exit__ 会【关文件】\n"
            "  with sqlite3.connect(p) as con: → __exit__ 只管【事务】，不关连接",
            "【要既提交又关闭】用 contextlib.closing（本机实测有效）：\n"
            "  from contextlib import closing\n"
            "  with closing(sqlite3.connect(p)) as con:\n"
            "      con.execute(\"INSERT ...\")\n"
            "      con.commit()        # closing 只管关，不管提交，得自己写\n"
            "  实测：出了块 con.execute() → ProgrammingError: Cannot operate on a closed database.",
            "【最保险】直接写 close()，别指望 with：\n"
            "  con = sqlite3.connect(p)\n"
            "  try:\n"
            "      con.execute(\"...\")\n"
            "      con.commit()\n"
            "  finally:\n"
            "      con.close()          # ← 一定会关",
            "【症状识别】如果脚本末尾报 PermissionError（文件删不掉），\n"
            "  先怀疑「连接没关」，而不是「文件被占用」。\n"
            "  验证：出块后 con.execute('SELECT 1') 看还通不通。",
            "【通用】任何「with 块」都要问一句：__exit__ 到底做了什么？\n"
            "  别把「文件对象的 with」的心智模型套到「连接对象的 with」上。",
        ],
        "tags": ["SQLite", "with", "上下文管理器", "事务", "close", "contextlib", "权限错误"],
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
