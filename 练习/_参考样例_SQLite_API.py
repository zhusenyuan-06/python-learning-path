# -*- coding: utf-8 -*-
"""
参考样例：11-17 讲义二《SQL 概念 + sqlite3 API 速查》
==================================================

配套讲义：笔记/讲义/11-17_讲义2_SQLite_API速查.md

用法：
    D:\\AAAA\\python.exe _参考样例_SQLite_API.py

本文件的每一段输出，都能在讲义里找到对应段落（逐字一致）。
所有结论都是本机实测（Python 3.12.7 / SQLite 3.45.3）。
"""

import os
import sqlite3
import tempfile
from pathlib import Path

数据目录 = Path(__file__).parent / "数据"
库路径 = 数据目录 / "新闻库.sqlite"


def 分隔(标题):
    print()
    print("=" * 68)
    print(标题)
    print("=" * 68)


def 临时库(名字="_api_临时.sqlite"):
    """造一个临时库路径 —— 破坏性测试一律用副本，绝不碰新闻库.sqlite。"""
    p = Path(tempfile.gettempdir()) / 名字
    if p.exists():
        try:
            os.remove(p)
        except PermissionError:
            pass
    return p


# ══════════════════════════════════════════════════════════════════════
# 【零】环境事实
# ══════════════════════════════════════════════════════════════════════
分隔("【零】环境事实（本机实测）")

print("sqlite3 模块版本     =", sqlite3.version)
print("SQLite 引擎版本      =", sqlite3.sqlite_version)
print("sqlite_version_info  =", sqlite3.sqlite_version_info)
print("paramstyle（占位风格）=", sqlite3.paramstyle, "  ← qmark 表示用 ? 占位")
print("apilevel             =", sqlite3.apilevel)
print("threadsafety        =", sqlite3.threadsafety)
print("库文件               =", 库路径)
print("库文件存在           =", 库路径.exists(), "| 大小 =", 库路径.stat().st_size, "字节")


# ══════════════════════════════════════════════════════════════════════
# 【一】概念：三层心智模型（库 / 表 / 行）
# ══════════════════════════════════════════════════════════════════════
分隔("【一】概念：库 → 表 → 列 → 行")

con = sqlite3.connect(库路径)
cur = con.cursor()

cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
print("库里有哪些表：")
for 名, 建表语句 in cur.fetchall():
    print(f"   表名 = {名}")
    print(f"   建表语句 = {建表语句}")

cur.execute("PRAGMA table_info(新闻)")
print()
print("表「新闻」的列（PRAGMA table_info）：")
print("   列名".ljust(10), "| 类型".ljust(12), "| 非空 | 主键")
for _编号, 列名, 类型, 非空, 默认值, 主键 in cur.fetchall():
    print(f"   {列名}".ljust(10), "|", str(类型).ljust(12), "|", 非空, "  |", 主键)

cur.execute("SELECT COUNT(*) FROM 新闻")
print()
print("总行数 =", cur.fetchone()[0])

con.close()


# ══════════════════════════════════════════════════════════════════════
# 【二】概念：一条 SELECT 的完整旅程 + 返回值三层
# ══════════════════════════════════════════════════════════════════════
分隔("【二】概念：五步固定套路 + 返回值的三层")

con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 序号, 星期 FROM 新闻 LIMIT 1")
行 = cur.fetchone()
con.close()

print("第①步 con = sqlite3.connect(库路径) →", type(con).__name__)
print("第②步 cur = con.cursor()            →", type(cur).__name__)
print("第③步 cur.execute(...)              →", type(cur).__name__, "(execute 也返回游标)")
print("第④步 行 = cur.fetchone()           →", 行, "| 类型 =", type(行).__name__)
print("第⑤步 con.close()                   → 释放文件占用")

print()
print("返回值的三层：")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 序号, 星期 FROM 新闻 LIMIT 3")
单行 = cur.fetchone()
print("   第1层 cur.fetchone()  →", 单行, "| 类型 =", type(单行).__name__)
cur.execute("SELECT 序号, 星期 FROM 新闻 LIMIT 3")
全部 = cur.fetchall()
print("   第2层 cur.fetchall()  →", 全部, "| 类型 =", type(全部).__name__)
print("   第3层 全部[0][0]      →", 全部[0][0], "| 类型 =", type(全部[0][0]).__name__)
con.close()

print()
print("元组长度 = SELECT 了几列（实测）：")
for sql, 说明 in [
    ("SELECT * FROM 新闻 LIMIT 1", "SELECT *"),
    ("SELECT 序号, 星期 FROM 新闻 LIMIT 1", "两列"),
    ("SELECT 新闻内容 FROM 新闻 LIMIT 1", "一列"),
]:
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute(sql)
    r = cur.fetchone()
    print(f"   {说明:<12} → 长度 {len(r)} | {r}")
    con.close()

print()
print("压平成纯列表（列表推导式）：")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 新闻内容 FROM 新闻 ORDER BY 序号 ASC LIMIT 2")
print("   原始 =", cur.fetchall())
cur.execute("SELECT 新闻内容 FROM 新闻 ORDER BY 序号 ASC LIMIT 2")
print("   压平 =", [行[0] for 行 in cur.fetchall()])
con.close()


# ══════════════════════════════════════════════════════════════════════
# 【三】概念：SQL 的执行顺序（跟书写顺序不一样）
# ══════════════════════════════════════════════════════════════════════
分隔("【三】概念：书写顺序 ≠ 执行顺序")

print("书写顺序（你写的）      实际执行顺序（数据库做的）")
print("   SELECT 列        →   ① FROM 表")
print("   FROM 表          →   ② WHERE 条件")
print("   WHERE 条件       →   ③ SELECT 列")
print("   ORDER BY 排      →   ④ ORDER BY 排")
print("   LIMIT 几条       →   ⑤ LIMIT 几条")

print()
print("实测证据 1：列名不存在会报错（解析期就检查，有没有匹配行都报）")
con = sqlite3.connect(库路径)
cur = con.cursor()
try:
    cur.execute("SELECT 不存在的列 FROM 新闻 WHERE 序号 > 100")
except Exception as e:
    print("   →", type(e).__name__, ":", e)
con.close()

print()
print("实测证据 2（最硬）：EXPLAIN QUERY PLAN —— 让数据库自己吐执行计划")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("EXPLAIN QUERY PLAN SELECT 新闻内容 FROM 新闻 WHERE 星期 = ? ORDER BY 序号 ASC LIMIT 3", ("星期二",))
for 行 in cur.fetchall():
    print("   ", 行, "  ← 先扫全表")
print()
print("   对比：有 GROUP BY 时")
cur.execute("EXPLAIN QUERY PLAN SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期")
for 行 in cur.fetchall():
    print("   ", 行, "  ← 扫完之后才分组")
con.close()

print()
print("实测证据 3：聚合函数是在 WHERE 筛完的行集上算的")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT COUNT(*), MAX(序号) FROM 新闻 WHERE 序号 = 99999")
print("   无匹配行 →", cur.fetchone())
cur.execute("SELECT COUNT(*), MAX(序号) FROM 新闻 WHERE 序号 = 1")
print("   有匹配行 →", cur.fetchone())
con.close()

print()
print("⚠️ 反面教材：我原本想用 1/0 证明，但那是错的")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 1/0 FROM 新闻 WHERE 序号 = 1")
print("   SQLite 里 1/0 →", cur.fetchone(), "  ← 返回 NULL，不报错！")
print("   → 别拿「不报错」当执行顺序的证据，用 EXPLAIN QUERY PLAN")
con.close()

print()
print("实测证据 4：ORDER BY 可以用 SELECT 里的别名")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 序号 AS 编号, 星期 FROM 新闻 ORDER BY 编号 LIMIT 2")
print("   →", cur.fetchall())
con.close()


# ══════════════════════════════════════════════════════════════════════
# 【四】概念：值 vs 标识符（不加引号 = 当成列名）
# ══════════════════════════════════════════════════════════════════════
分隔("【四】概念：值 vs 标识符")

con = sqlite3.connect(库路径)
cur = con.cursor()
print("✅ 带单引号 = 字符串值：")
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = '星期二' ORDER BY 序号 ASC")
print("   →", [行[0] for 行 in cur.fetchall()])

print()
print("❌ 不带引号 = 当成列名 → 报错：")
try:
    cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = 星期二")
except Exception as e:
    print("   →", type(e).__name__, ":", e)

print()
print("⚠️ 但 SQLite 有个兼容性缺陷：双引号它也当字符串（实测不报错）")
try:
    cur.execute('SELECT 序号 FROM 新闻 WHERE 星期 = "星期二" ORDER BY 序号 ASC')
    print("   →", [行[0] for 行 in cur.fetchall()], " ← SQLite 认了，别的数据库不一定认")
except Exception as e:
    print("   →", type(e).__name__, ":", e)
con.close()


# ══════════════════════════════════════════════════════════════════════
# 【五】API 篇：模块级 + Connection + Cursor 全表
# ══════════════════════════════════════════════════════════════════════
分隔("【五】API：模块级")

print("sqlite3 里跟 sqlite3.Error 有关的公开名字：")
异常们 = [n for n in dir(sqlite3) if n.endswith("Error")]
for 名 in 异常们:
    print(f"   {名:<20} MRO = {[c.__name__ for c in getattr(sqlite3, 名).__mro__[:4]]}")

print()
print("实测：except sqlite3.DatabaseError 能抓住 no such table 吗")
con = sqlite3.connect(库路径)
try:
    con.execute("SELECT * FROM 没有这张表")
except sqlite3.DatabaseError as e:
    print("   ✅ 抓到了，类型 =", type(e).__name__, "| 消息 =", e)
con.close()

print()
print("实测：四种典型报错分别是什么异常类型")
tmp = 临时库("_api_异常.sqlite")
con = sqlite3.connect(tmp)
con.execute("CREATE TABLE t (id INT PRIMARY KEY, name TEXT)")
con.execute("INSERT INTO t (id, name) VALUES (1, '张三')")
for 说明, 动作 in [
    ("列名不存在", lambda: con.execute("SELECT 不存在 FROM t")),
    ("表名不存在", lambda: con.execute("SELECT * FROM 没有这张表")),
    ("语法错误",   lambda: con.execute("SELCT * FROM t")),
    ("唯一约束冲突", lambda: con.execute('INSERT INTO t (id,name) VALUES (1, "dup")')),
]:
    try:
        动作()
        print(f"   {说明:<12} → 不报错")
    except Exception as e:
        print(f"   {说明:<12} → {type(e).__name__}: {e}")
con.close()
try:
    os.remove(tmp)
except PermissionError:
    pass

分隔("【五】API：Connection 对象")

con = sqlite3.connect(库路径)
cur = con.cursor()
print("con.cursor()        →", type(cur).__name__)
print("con.execute(...)    →", type(con.execute("SELECT 1 FROM 新闻 LIMIT 1")).__name__, "(直接返回一个游标)")
print("con.rowcount?       → 无（rowcount 在 Cursor 上）")
print("con.row_factory     =", con.row_factory, "(默认 None → 行是普通 tuple)")
print("con.total_changes   =", con.total_changes)
print("con.in_transaction  =", con.in_transaction, "(刚连上)")
print("con.isolation_level =", repr(con.isolation_level), "(默认 '' = 旧式事务)")
print("con.autocommit      =", con.autocommit, "(Python 3.12 新增；-1 = 旧式行为)")

print()
print("Connection 公开方法：")
print("   ", [n for n in dir(con) if not n.startswith("_") and callable(getattr(con, n, None))])

con.close()

分隔("【五】API：Cursor 对象")

con = sqlite3.connect(库路径)
cur = con.cursor()
print("Cursor 公开方法：")
print("   ", [n for n in dir(cur) if not n.startswith("_") and callable(getattr(cur, n, None))])
con.close()

分隔("【五】API：三个取数方法")

con = sqlite3.connect(库路径)
cur = con.cursor()

cur.execute("SELECT 序号 FROM 新闻 WHERE 序号 = 99999")
print("无结果时：")
print("   cur.fetchone() →", repr(cur.fetchone()), "  ← None")
print("   cur.fetchall() →", repr(cur.fetchall()), "  ← []（空列表，不是 None）")

print()
print("结果集是「流」的：")
cur.execute("SELECT 序号 FROM 新闻 LIMIT 5")
print("   fetchmany(2) →", cur.fetchmany(2))
print("   fetchmany(2) →", cur.fetchmany(2), "  ← 接着上次的位置，不是从头")
print("   fetchall()   →", cur.fetchall(), "  ← 只剩最后一条")

print()
print("同一个游标重新 execute 会覆盖上一次结果：")
cur.execute("SELECT 序号 FROM 新闻 ORDER BY 序号 ASC LIMIT 3")
print("   第一次 fetchall →", cur.fetchall())
cur.execute("SELECT 星期 FROM 新闻 LIMIT 2")
print("   第二次 fetchall →", cur.fetchall(), "  ← 上次的结果没了")
con.close()

分隔("【五】API：description / rowcount / lastrowid")

tmp = 临时库("_api_临时1.sqlite")
con = sqlite3.connect(tmp)
cur = con.cursor()
cur.execute("CREATE TABLE t (x INT)")
print("CREATE 后 cur.description =", cur.description)
cur.execute("INSERT INTO t VALUES (1)")
print("INSERT 后 cur.description =", cur.description, "  ← 非 SELECT 一律是 None")
cur.execute("SELECT x FROM t")
print("SELECT 后 cur.description =", cur.description)
print("   列名 =", [d[0] for d in cur.description])

print()
cur.execute("SELECT x FROM t")
print("SELECT 后 cur.rowcount =", cur.rowcount, "  ← -1，不是行数")
cur.execute("UPDATE t SET x = x WHERE x = 1")
print("UPDATE 后 cur.rowcount =", cur.rowcount, "  ← 实际影响行数")
print("cur.lastrowid         =", cur.lastrowid, "  ← 最后插入的自增主键")
con.close()
try:
    os.remove(tmp)
except PermissionError:
    pass

分隔("【五】API：sqlite3.Row")

con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE t (id INT, name TEXT)")
con.execute("INSERT INTO t VALUES (1, '张三')")
r = con.execute("SELECT id, name FROM t").fetchone()
print("类型          =", type(r).__name__)
print("list(r.keys())=", list(r.keys()))
print('r["name"]     =', r["name"], "  ← 按名字")
print("r[0], r[1]    =", r[0], r[1], "  ← 按位置也能用")
print("len(r)        =", len(r))
print("dict(r)       =", dict(r))
print("list(r)       =", list(r))
con.close()

print()
print("con.row_factory 会被 con.execute() 返回的游标继承：")
con = sqlite3.connect(":memory:")
con.row_factory = sqlite3.Row
con.execute("CREATE TABLE t (id INT, name TEXT)")
con.execute("INSERT INTO t VALUES (1, '张三')")
r2 = con.execute("SELECT id, name FROM t").fetchone()
print("   →", type(r2).__name__, "| r2['name'] =", r2["name"])
con.close()

分隔("【五】API：参数化（? 与 :name）")

con = sqlite3.connect(库路径)
cur = con.cursor()
print("位置参数 ?：")
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = ? ORDER BY 序号 ASC", ("星期二",))
print("   →", [行[0] for 行 in cur.fetchall()])

print()
print("命名参数 :name：")
tmp = 临时库("_api_临时2.sqlite")
con2 = sqlite3.connect(tmp)
con2.execute("CREATE TABLE t (id INT, name TEXT)")
con2.execute("INSERT INTO t (id,name) VALUES (:id, :name)", {"id": 1, "name": "张三"})
con2.execute("INSERT INTO t (id,name) VALUES (:id, :name)", {"id": 2, "name": "李四"})
print("   写入后 →", con2.execute("SELECT * FROM t").fetchall())
print("   查询   →", con2.execute("SELECT name FROM t WHERE id = :i", {"i": 2}).fetchall())
con2.close()
try:
    os.remove(tmp)
except PermissionError:
    pass
con.close()

print()
print("❌ 危险：拼字符串（注入风险）")
print("   sql = \"SELECT 序号 FROM 新闻 WHERE 星期 = '%s'\" % 用户输入")
print("   用户输入一个 ' 就能闭合引号，后面全是他的代码")
print()
print("✅ 安全：参数化，值和代码分离")
print("   cur.execute(\"SELECT 序号 FROM 新闻 WHERE 星期 = ?\", (用户输入,))")


# ══════════════════════════════════════════════════════════════════════
# 【六】三个语义陷阱
# ══════════════════════════════════════════════════════════════════════
分隔("【六】陷阱 1：commit 不写 = 写的操作等于没写")

tmp = 临时库("_api_临时3.sqlite")
con = sqlite3.connect(tmp)
con.execute("CREATE TABLE t (x INT)")
con.execute("INSERT INTO t VALUES (1)")
con.close()          # 没 commit
con = sqlite3.connect(tmp)
存在 = con.execute("SELECT name FROM sqlite_master WHERE name='t'").fetchone()
行数 = con.execute("SELECT COUNT(*) FROM t").fetchone()[0] if 存在 else "表不存在"
print("没 commit 就 close →")
print("   表存在 =", bool(存在), "  ← DDL 在 SQLite 里自动提交了")
print("   行数   =", 行数, "  ← DML 回滚了，数据没了")
con.close()
try:
    os.remove(tmp)
except PermissionError:
    pass

print()
print("三个解决方案：")
print("   A 手动：con.execute(...) ; con.commit() ; con.close()")
print("   B with：with sqlite3.connect(库路径) as con: ...   ← 退出自动 commit，异常自动 rollback")
print("   C 自动提交：sqlite3.connect(库路径, isolation_level=None)")

print()
print("⚠️ 实测：with sqlite3.connect() 【不会关闭连接】")
tmp = 临时库("_api_with.sqlite")
with sqlite3.connect(tmp) as con:
    con.execute("CREATE TABLE t (x INT)")
    con.execute("INSERT INTO t VALUES (1)")
print("   with 块已退出")
try:
    con.execute("SELECT 1")
    print("   → with 退出后还能用！说明连接【还开着】")
except Exception as e:
    print("   →", type(e).__name__, ":", e)
print("   with 管的是【事务】：正常退出→commit，抛异常→rollback；它【不管】关连接")
con.close()
try:
    os.remove(tmp)
    print("   关掉后文件才能删")
except PermissionError:
    print("   删不掉（连接还占着）")

print()
print("对比：contextlib.closing —— 它【只管关连接】，不管提交")
from contextlib import closing
tmp2 = 临时库("_api_closing.sqlite")
with closing(sqlite3.connect(tmp2)) as con2:
    con2.execute("CREATE TABLE t (x INT)")
    con2.execute("INSERT INTO t VALUES (1)")
    con2.commit()      # closing 不管提交，得自己写
print("   with 块已退出")
try:
    con2.execute("SELECT 1")
    print("   → 还能用！说明 closing 没关")
except Exception as e:
    print("   →", type(e).__name__, ":", e, " ← closing 确实关了连接")
try:
    os.remove(tmp2)
    print("   文件能删 → 连接确实关了")
except PermissionError:
    print("   删不掉")
except FileNotFoundError:
    print("   文件已经不在了（前面删掉了）")

print()
print("实测：isolation_level=None = 自动提交")
tmp = 临时库("_api_临时4.sqlite")
con = sqlite3.connect(tmp, isolation_level=None)
print("   isolation_level =", repr(con.isolation_level))
con.execute("CREATE TABLE t (x INT)")
con.execute("INSERT INTO t VALUES (1)")
con.close()
con = sqlite3.connect(tmp)
print("   关掉再读行数 =", con.execute("SELECT COUNT(*) FROM t").fetchone()[0], "  ← 数据留下了")
con.close()
try:
    os.remove(tmp)
except PermissionError:
    pass

print()
print("实测：with 块里抛异常 → INSERT 回滚，但 CREATE TABLE 留下")
tmp = 临时库("_api_临时5.sqlite")
con5 = None
try:
    with sqlite3.connect(tmp) as con5:
        con5.execute("CREATE TABLE t (x INT)")
        con5.execute("INSERT INTO t VALUES (1)")
        raise ValueError("故意炸")
except ValueError as e:
    print("   捕获到:", e)
con5.close()          # with 抛异常了也不关连接 → 得自己关
con = sqlite3.connect(tmp)
存在 = con.execute("SELECT name FROM sqlite_master WHERE name='t'").fetchone()
行数 = con.execute("SELECT COUNT(*) FROM t").fetchone()[0] if 存在 else "表不存在"
print("   表存在 =", bool(存在), " | 行数 =", 行数)
con.close()
try:
    os.remove(tmp)
except PermissionError:
    pass

分隔("【六】陷阱 2：rowcount 对 SELECT 是 -1")

# ⚠️ UPDATE 必须在【副本】上做 —— 绝不动正主 新闻库.sqlite（T42）
副本 = 临时库("_api_rowcount.sqlite")
import shutil
shutil.copyfile(库路径, 副本)
con = sqlite3.connect(副本)
cur = con.cursor()
cur.execute("SELECT 序号 FROM 新闻")
print("SELECT 后 cur.rowcount =", cur.rowcount, "  ← -1")
cur.execute("UPDATE 新闻 SET 新闻内容 = 新闻内容 WHERE 序号 = 1")
print("UPDATE 后 cur.rowcount =", cur.rowcount)
con.rollback()
print("要 SELECT 的行数 → 用 COUNT(*)：")
cur.execute("SELECT COUNT(*) FROM 新闻")
print("   →", cur.fetchone()[0])
con.close()
try:
    os.remove(副本)
except PermissionError:
    pass

print()
print("（UPDATE 跑在副本上，正主 新闻库.sqlite 一行没动 —— 见 T42）")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT COUNT(*) FROM 新闻")
print("正主库行数 =", cur.fetchone()[0])
con.close()

分隔("【六】陷阱 3：忘了 close / 关了还拿来用")

con = sqlite3.connect(库路径)
con.close()
try:
    con.execute("SELECT 1")
except Exception as e:
    print("close 后再 execute →", type(e).__name__, ":", e)
con.close()
print("close() 关两次 → 不报错 ✅")

con = sqlite3.connect(库路径)
cur = con.cursor()
cur.close()
try:
    cur.execute("SELECT 1")
except Exception as e:
    print("cursor.close() 后再 execute →", type(e).__name__, ":", e)
con.close()


# ══════════════════════════════════════════════════════════════════════
# 【七】三种等价写法，结果完全一样
# ══════════════════════════════════════════════════════════════════════
分隔("【七】三种 Python 写法，结果完全一样")

SQL = "SELECT 新闻内容 FROM 新闻 WHERE 星期 = ? ORDER BY 序号 ASC"

print("写法 1：游标（标准，练习文件用这个）")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute(SQL, ("星期二",))
结果1 = [行[0] for 行 in cur.fetchall()]
con.close()
print("   →", 结果1)

print()
print("写法 2：快捷（省一行）")
con = sqlite3.connect(库路径)
结果2 = [行[0] for 行 in con.execute(SQL, ("星期二",)).fetchall()]
con.close()
print("   →", 结果2)

print()
print("写法 3：with（自动提交事务，但连接还是要自己关）")
with sqlite3.connect(库路径) as con:
    结果3 = [行[0] for 行 in con.execute(SQL, ("星期二",)).fetchall()]
con.close()          # ← with 不会帮你关！
print("   →", 结果3)

print()
print("三种写法一致 =", 结果1 == 结果2 == 结果3)


# ══════════════════════════════════════════════════════════════════════
# 收工
# ══════════════════════════════════════════════════════════════════════
分隔("全部输出结束 —— 这些和讲义二里写的【逐字一致】")
print("下一步：跑 练习/11.17练习_SQL_SELECT与WHERE.py（8 题）")
print("       或回 笔记/讲义/11-17_讲义_SQL_SELECT与WHERE.md 看语法")
