# -*- coding: utf-8 -*-
"""
参考样例：SQL SELECT / WHERE（讲义 11-17 的配套可跑文件）
讲义里每一段输出都能用这个文件复现。
直接运行本文件即可看到全部输出。

⚠️ 本文件【只读】数据库，不 INSERT / 不 DELETE / 不 DROP。
   练习文件「11.17练习_SQL_SELECT与WHERE.py」才让你动手。
"""
import sqlite3
import os
from pathlib import Path

数据目录 = Path(__file__).parent / "数据"
库路径 = 数据目录 / "新闻库.sqlite"


def 分隔(标题):
    print()
    print("=" * 68)
    print(标题)
    print("=" * 68)


# ═════════════════════════════════════════════════════════════════════════
分隔("【一】SQL 是什么：五步固定套路")

print("""连上 → 拿话筒 → 说 SQL → 收结果 → 关电话

第 1 步 con = sqlite3.connect(库路径)   连上数据库文件""")
con = sqlite3.connect(库路径)
print("  con =", type(con).__name__, "| 库路径 =", 库路径.name)

print()
print("第 2 步 cur = con.cursor()           拿一个游标（发命令用）")
cur = con.cursor()
print("  cur =", type(cur).__name__)

print()
print('第 3 步 cur.execute("SELECT * FROM 新闻 LIMIT 2")   执行 SQL')
cur.execute("SELECT * FROM 新闻 LIMIT 2")
print("  已执行")

print()
print("第 4 步 cur.fetchall()                一次把结果全捞回来")
行们 = cur.fetchall()
print("  返回类型 =", type(行们).__name__, "| 行数 =", len(行们))
print("  第 1 行 =", 行们[0])
print("  第 1 行是", type(行们[0]).__name__, "| 长度 =", len(行们[0]))

print()
print("第 5 步 con.close()                   关掉连接")
con.close()
print("  已关闭")


# ═════════════════════════════════════════════════════════════════════════
分隔("【二】数据形状：list[tuple] 怎么变成 list[str]")

con = sqlite3.connect(库路径)
cur = con.cursor()

print('SELECT 新闻内容 FROM 新闻 ORDER BY 序号 ASC   →  只取 1 列')
cur.execute("SELECT 新闻内容 FROM 新闻 ORDER BY 序号 ASC")
原始 = cur.fetchall()
print("  第 1 个元素 =", 原始[0])
print("  类型 =", type(原始[0]).__name__, "| 长度 =", len(原始[0]), "← 1 列所以元组里就 1 个")

print()
print("列表推导式 [行[0] for 行 in ...]  →  把每个元组拆开")
扁平 = [行[0] for 行 in 原始]
print("  第 1 个元素 =", 扁平[0])
print("  类型 =", type(扁平[0]).__name__)
print("  长度 =", len(扁平))
con.close()


# ═════════════════════════════════════════════════════════════════════════
分隔("【三】SELECT 骨架：选哪些列")

con = sqlite3.connect(库路径)
cur = con.cursor()

print("① SELECT *（全部 4 列）")
cur.execute("SELECT * FROM 新闻 LIMIT 1")
print("  ", cur.fetchone())

print()
print("② SELECT 序号, 星期（2 列）")
cur.execute("SELECT 序号, 星期 FROM 新闻 LIMIT 1")
print("  ", cur.fetchone())

print()
print("③ SELECT 新闻内容（1 列）")
cur.execute("SELECT 新闻内容 FROM 新闻 LIMIT 1")
print("  ", cur.fetchone())

print()
print("④ cur.description —— 游标自己告诉你每列叫什么")
cur.execute("SELECT 序号, 日期, 新闻内容, 星期 FROM 新闻 LIMIT 1")
print("  ", [d[0] for d in cur.description])
con.close()


# ═════════════════════════════════════════════════════════════════════════
分隔("【四】WHERE 六种条件写法")

con = sqlite3.connect(库路径)
cur = con.cursor()


def 查(sql, 说明):
    cur.execute(sql)
    结果 = cur.fetchall()
    print("  %-46s → %s" % (说明, 结果))


print("① 等于        WHERE 星期 = '星期二'")
查("SELECT 序号 FROM 新闻 WHERE 星期 = '星期二'", "星期 = '星期二'")

print()
print("② 不等于      WHERE 星期 <> '星期六'")
查("SELECT 序号 FROM 新闻 WHERE 星期 <> '星期六'", "星期 <> '星期六'")

print()
print("③ 多条件与    WHERE 星期 = '星期一' AND 序号 > 5")
查("SELECT 序号 FROM 新闻 WHERE 星期 = '星期一' AND 序号 > 5", "星期一 AND 序号>5")

print()
print("④ 多条件或    WHERE 新闻内容 LIKE '%银行%' OR 序号 = 1")
查("SELECT 序号 FROM 新闻 WHERE 新闻内容 LIKE '%银行%' OR 序号 = 1", "含'银行' OR 序号=1")

print()
print("⑤ 模糊匹配    WHERE 新闻内容 LIKE '%雨雪%'")
查("SELECT 序号 FROM 新闻 WHERE 新闻内容 LIKE '%雨雪%'", "含'雨雪'")

print()
print("⑥ 区间        WHERE 序号 BETWEEN 3 AND 8")
查("SELECT 序号 FROM 新闻 WHERE 序号 BETWEEN 3 AND 8", "序号 BETWEEN 3 AND 8")

print()
print("⑦ 多值        WHERE 星期 IN ('星期五', '星期日')")
查("SELECT 序号 FROM 新闻 WHERE 星期 IN ('星期五', '星期日')", "星期五 IN 星期日")
con.close()


# ═════════════════════════════════════════════════════════════════════════
分隔("【五】COUNT(*) 数条数")

con = sqlite3.connect(库路径)
cur = con.cursor()

cur.execute("SELECT COUNT(*) FROM 新闻")
print("  SELECT COUNT(*) FROM 新闻                →", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM 新闻 WHERE 星期 = '星期二'")
print("  COUNT(*) + WHERE 星期='星期二'            →", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM 新闻 WHERE 新闻内容 LIKE '%金融%'")
print("  COUNT(*) + WHERE 内容 LIKE '%金融%'       →", cur.fetchone()[0])
con.close()

print()
print("（新闻表里没有 NULL，所以 COUNT(*) 和 COUNT(列) 一样。演示差异用临时表：）")
import tempfile
临时库 = Path(tempfile.gettempdir()) / "_sql讲义_nulltest.sqlite"
if 临时库.exists():
    os.remove(临时库)
con = sqlite3.connect(临时库)
cur = con.cursor()
cur.execute("CREATE TABLE t (a INT, b TEXT)")
cur.executemany("INSERT INTO t VALUES (?,?)", [(1, "x"), (None, "y"), (3, None)])
for 说明, sql in [
    ("COUNT(*)", "SELECT COUNT(*) FROM t"),
    ("COUNT(a)", "SELECT COUNT(a) FROM t"),
    ("COUNT(b)", "SELECT COUNT(b) FROM t"),
    ("WHERE a = NULL", "SELECT * FROM t WHERE a = NULL"),
    ("WHERE a IS NULL", "SELECT * FROM t WHERE a IS NULL"),
]:
    cur.execute(sql)
    print("  %-18s → %s" % (说明, cur.fetchall()))
con.close()
os.remove(临时库)
print("  ← WHERE a = NULL 永远空！NULL 要用 IS NULL 比")


# ═════════════════════════════════════════════════════════════════════════
分隔("【六】ORDER BY / LIMIT（先会用，明天的 GROUP BY 才是重头）")

con = sqlite3.connect(库路径)
cur = con.cursor()

cur.execute("SELECT 序号 FROM 新闻 ORDER BY 序号 DESC LIMIT 3")
print("  ORDER BY 序号 DESC LIMIT 3  →", [行[0] for 行 in cur.fetchall()])

cur.execute("SELECT 序号 FROM 新闻 LIMIT 3")
print("  不写 ORDER BY              →", [行[0] for 行 in cur.fetchall()], "← 不保证顺序！")
con.close()


# ═════════════════════════════════════════════════════════════════════════
分隔("【七】坑1：字符串必须用【单引号】")

con = sqlite3.connect(库路径)
cur = con.cursor()

print("""❌ 不加引号：WHERE 星期 = 星期二  ← 真报错""")
try:
    cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = 星期二")
    print("   结果 =", cur.fetchall())
except sqlite3.OperationalError as e:
    print("   报错 =", e)

print()
print("✅ 单引号：WHERE 星期 = '星期二'")
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = '星期二'")
print("   结果 =", [行[0] for 行 in cur.fetchall()])
con.close()

print()
print("⚠️ 但是—— SQLite 比你想的宽容（这三条【都不报错】）：")
con = sqlite3.connect(库路径)
cur = con.cursor()
for 说明, sql in [
    ("双引号  WHERE 星期 = \"星期二\"", 'SELECT 序号 FROM 新闻 WHERE 星期 = "星期二"'),
    ("两个等号 WHERE 星期 == '星期二'", "SELECT 序号 FROM 新闻 WHERE 星期 == '星期二'"),
    ("小写 and", "SELECT 序号 FROM 新闻 WHERE 星期 = '星期一' and 序号 > 5"),
]:
    cur.execute(sql)
    print("   %-32s → %s" % (说明, [行[0] for 行 in cur.fetchall()]))
con.close()
print("   ↑ SQLite 兼容各种数据库，故意放宽了标准（官方叫 misfeature）。")
print("     换 MySQL / PostgreSQL → 这三条全部报错。")
print("     所以永远写：单引号 + 一个等号 + 大写 AND。")


# ═════════════════════════════════════════════════════════════════════════
分隔("【八】坑2：Python 的 = 和 SQL 的 = 不是一回事")

print("""Python:   a == b      （两个等号）表示「相等」
Python:   a = b        （一个等号）表示「赋值」
SQL:      WHERE 星期 = '星期二'    （一个等号）表示「相等」
SQL 里【没有】== 这个写法。

⚠️ 实测：SQLite 认 == （跟双引号、小写 and 一样，都是兼容性 misfeature）。
   MySQL 也认，PostgreSQL 会直接报错。→ 统一写一个等号。""")

con = sqlite3.connect(库路径)
cur = con.cursor()
print("❌ 把 == 带进 SQL（SQLite 能跑，但换库就废）：")
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 == '星期二'")
print("   SQLite 结果 =", [行[0] for 行 in cur.fetchall()])
con.close()


# ═════════════════════════════════════════════════════════════════════════
分隔("【九】坑3：AND 连接的是【两个条件】，对应 pandas 的 &")

print("""SQL:      WHERE 星期 = '星期一' AND 序号 > 5     ← AND 连接【两个条件】

Python:   df[(df["星期"] == "星期一") & (df["序号"] > 5)]   ← & 连接，且两边要加括号

⚠️ 实测：SQLite 也认小写 and（同样属于兼容性 misfeature）。
   但语义不一样 —— Python 的 and 是逻辑运算符，SQL 的 AND 是条件连接。""")

con = sqlite3.connect(库路径)
cur = con.cursor()
print("小写 and（SQLite 能跑，但别这么写）：")
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = '星期一' and 序号 > 5")
print("   结果 =", [行[0] for 行 in cur.fetchall()])

print()
print("✅ 大写 AND：")
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = '星期一' AND 序号 > 5")
print("   结果 =", [行[0] for 行 in cur.fetchall()])
con.close()


# ═════════════════════════════════════════════════════════════════════════
分隔("【十】坑4：不 close() → 文件被占住")

print("""con = sqlite3.connect(库路径)   # 连接开着
os.remove(库路径)                # → OSError: 文件被占用，删不掉

con.close()                      # 关掉
os.remove(库路径)                # → 成功

本文件不演示真删你的数据库（危险），只演示「同一个文件能不能改名」。""")

测试文件 = 数据目录 / "_占用测试.sqlite"
con = sqlite3.connect(测试文件)
con.execute("CREATE TABLE t (x INT)")
con.commit()
try:
    os.rename(测试文件, 测试文件.with_suffix(".renamed"))
    print("  连接开着时改名 → 成功（Windows 上这一步可能侥幸成功）")
except OSError as e:
    print("  连接开着时改名 → OSError:", e)
finally:
    con.close()

if 测试文件.with_suffix(".renamed").exists():
    os.rename(测试文件.with_suffix(".renamed"), 测试文件)
if 测试文件.exists():
    os.remove(测试文件)
print("  清理完成，测试文件已删除:", not 测试文件.exists())


# ═════════════════════════════════════════════════════════════════════════
分隔("【十一】坑5：连错了路径不会报错，会【悄悄建一个新空库】")

错路径 = 数据目录 / "新闻库.sqlit"          # 故意少个 e
print("  故意写错:", 错路径.name)
con = sqlite3.connect(错路径)
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("  连上了，但没有表:", cur.fetchall())
con.close()
print("  静默生成了一个新的空库文件:", 错路径.exists(), "← 连错路径【不报错】，只是查不到数据")
if 错路径.exists():
    os.remove(错路径)


# ═════════════════════════════════════════════════════════════════════════
分隔("【十二】SQL 注入：为什么不能把用户输入拼进 SQL")

print("""❌ 危险写法（把用户输入拼进字符串）：
    sql = "SELECT * FROM 新闻 WHERE 星期 = '%s'" % 用户输入

用户输入一个 ' 就能把引号闭合，后面全是他的代码。
这就是 SQL 注入 —— 是真漏洞，不是"不规范"。""")

危险输入 = "星期二' OR '1'='1"
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = '%s'" % 危险输入)
print("  危险写法查到的 =", [行[0] for 行 in cur.fetchall()], "← 全部 15 条都漏出来了！")
con.close()

print()
print("✅ 正确写法：参数化（? 占位符）")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = ?", (危险输入,))
print("  参数化查到的   =", [行[0] for 行 in cur.fetchall()], "← 0 条，输入被当成【数据】而不是【代码】")
con.close()


# ═════════════════════════════════════════════════════════════════════════
分隔("【十三】对照：pandas 和 SQL 是同一件事的两套语言")

import pandas as pd

df = pd.read_csv(数据目录 / "news_多天版.csv")

print("pandas：df[df['星期'] == '星期二']")
print("  →", list(df[df["星期"] == "星期二"]["序号"]))

print()
print("SQL   ：SELECT 序号 FROM 新闻 WHERE 星期 = '星期二'")
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = '星期二'")
print("  →", [行[0] for 行 in cur.fetchall()])
con.close()

print()
print("两边结果一样 —— 这就是「同一件事两套语言」。")


# ═════════════════════════════════════════════════════════════════════════
分隔("【十四】收工：整套模板（8 道题都是这个骨架）")

print("""
import sqlite3
from pathlib import Path

库路径 = Path(__file__).parent / "数据" / "新闻库.sqlite"

def 你的函数():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT ... FROM 新闻 WHERE ...")     # ← 换中间这句
    结果 = [行[0] for 行 in cur.fetchall()]           # ← 换最后的加工
    con.close()
    return 结果                                        # ← 必须 return！
""")

print("=" * 68)
print("全部输出结束 —— 这些和讲义里写的【逐字一致】")
print("=" * 68)
