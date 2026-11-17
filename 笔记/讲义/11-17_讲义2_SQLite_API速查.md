# 11-17 讲义二：SQL 概念 + sqlite3 API 速查（1h）

> 对应日程：11-16 晚上「📌 SQL：SELECT/WHERE 概念 0.5h」
> 上游：`笔记/讲义/11-17_讲义_SQL_SELECT与WHERE.md`（语法篇：SELECT 骨架 + WHERE 七种写法 + 六个坑）
> **本篇是「概念篇 + API 篇」** —— 讲 SQL 到底在解决什么问题，以及 Python 侧的 API 到底有哪些、每个返回什么
> 配套可跑文件：`练习/_参考样例_SQLite_API.py`（**本讲义每一行输出都能用它复现**）
> 数据：`练习/数据/新闻库.sqlite`（表 `新闻`，15 行 4 列）

> ⚠️ **本文所有输出都是实跑出来的**（Python 3.12.7 / `D:\AAAA`，SQLite 3.45.3）。
> 复习时自己跑 `_参考样例_SQLite_API.py`，每一段都能对上。

---

## 零、这份怎么用

| 你现在的状态 | 读哪节 |
|---|---|
| 「我能跑 SELECT 了，但说不清它到底在干什么」 | **第一节 + 第二节** |
| 「我忘了某个 API 叫什么 / 返回什么」 | **第五节（API 全表）** |
| 「我写完了但不知道对不对」 | **第六节（三个语义陷阱）** |
| 「我想直接上手做题」 | 跳到 **第八节**，回第一份讲义看语法 |

---

## 一、概念篇：SQL 到底在解决什么问题

### 1.1 一句话

**pandas 把整张表搬进你的内存再筛；SQL 让数据库自己筛，只把你要的那几行送回来。**

同样是「找出所有星期二的新闻」，两种做法：

```
pandas（你 11-16 学的）                SQL（今天）
─────────────────────────            ─────────────────────────
df = pd.read_csv("新闻.csv")   ← 15 行全进内存
df[df["星期"] == "星期二"]     ← Python 在内存里逐行判断
                                    con.execute(
                                      "SELECT 新闻内容 FROM 新闻
                                       WHERE 星期 = '星期二'")
                                    ↑ 数据库自己去磁盘上筛，只送 2 行回来
```

### 1.2 为什么这件事在你的方向上重要

你做 AI 应用工程师，**数据从哪来？**

| 场景 | 数据来源 | 怎么拿 |
|---|---|---|
| RAG 知识库 | MySQL / PostgreSQL 里的文档表 | `SELECT` |
| Agent 的「查数据库」工具 | 后端业务库 | `SELECT` |
| 爬来的新闻存起来 | SQLite / MySQL | `INSERT` + `SELECT` |
| 爬虫日志 / 调用记录 | SQLite | `SELECT` + `WHERE` |

**JD 里点名要 SQL 的有 4 份**（JD-01/02/03/06），要求原文是「了解 MySQL/PostgreSQL，做基本数据查询」。

「基本数据查询」= `SELECT` + `WHERE` = **今天这两篇讲义的全部内容**。

### 1.3 三层心智模型：库 / 表 / 行

```
文件层：新闻库.sqlite        ← 一个文件就是一个库（SQLite 的特点）
  └── 表层：新闻            ← 一个库里可以有多张表
        ├── 列：序号 / 日期 / 新闻内容 / 星期   ← 表头，是 schema
        └── 行：15 条记录，每行 4 个值           ← 数据本体
```

**「查询」= 在表里挑行（WHERE）＋ 挑列（SELECT）＋ 排序（ORDER BY）＋ 限制条数（LIMIT）。**

SQL 就是一门**描述你想看什么**的语言，不是命令式的「怎么做」。你写「给我星期二的标题」，数据库自己决定用不用索引、先筛哪列。

### 1.4 SQL 的执行顺序（**跟书写顺序不一样**）

这是**最容易考、也最容易忘**的一条：

```
书写顺序（你写的）        实际执行顺序（数据库做的）
──────────────────      ──────────────────────────
SELECT 列                 ① FROM 新闻        ← 先找表
FROM 表                   ② WHERE 条件       ← 再筛行
WHERE 条件                ③ SELECT 列        ← 再挑列
ORDER BY 排               ④ ORDER BY 排      ← 再排序
LIMIT 几条                ⑤ LIMIT 几条       ← 最后截断
```

**为什么重要**：如果你在 `WHERE` 里用了一个只存在于 `SELECT` 别名里的东西，**会报错**；反过来 `ORDER BY` 可以用别名（实测通过）。

**实测证据 1**：列名不存在 → 无论有没有匹配行**都**报错（说明列名是**解析期**就检查的）

```
SELECT 不存在的列 FROM 新闻 WHERE 序号 > 100
→ OperationalError: no such column: 不存在
```

**实测证据 2（最硬）**：`EXPLAIN QUERY PLAN` —— 让数据库自己吐执行计划

```python
cur.execute("EXPLAIN QUERY PLAN SELECT 新闻内容 FROM 新闻 WHERE 星期 = ? ORDER BY 序号 ASC LIMIT 3", ("星期二",))
# → (4, 0, 0, 'SCAN 新闻')          ← 先扫全表
```

有 `GROUP BY` 时，能看到分组发生在扫表**之后**：

```python
cur.execute("EXPLAIN QUERY PLAN SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期")
# → (6, 0, 0, 'SCAN 新闻')
# → (8, 0, 0, 'USE TEMP B-TREE FOR GROUP BY')    ← 扫完之后才分组
```

**实测证据 3**：聚合函数是在 **WHERE 筛完的行集**上算的

```python
cur.execute("SELECT COUNT(*), MAX(序号) FROM 新闻 WHERE 序号 = 99999").fetchone()
# → (0, None)      ← 没有匹配行 → 计数 0，最大值 None
cur.execute("SELECT COUNT(*), MAX(序号) FROM 新闻 WHERE 序号 = 1").fetchone()
# → (1, 1)         ← 有匹配行 → 在筛后的 1 行上算
```

> ⚠️ **我原本想用 `SELECT 1/0` 来证明，但那是错的** —— SQLite 里 `1/0` 返回 `NULL` **不报错**（实测 `(None,)`）。**别拿「不报错」当执行顺序的证据**，用 `EXPLAIN QUERY PLAN`。

---

## 二、概念篇：数据在 Python 里长什么样

### 2.1 一条 SELECT 的完整旅程

```python
import sqlite3
from pathlib import Path

库路径 = Path(__file__).parent / "数据" / "新闻库.sqlite"

con = sqlite3.connect(库路径)      # ① 打开文件，得到一个连接
cur = con.cursor()                 # ② 在连接上开一个游标（发命令用）
cur.execute("SELECT 序号, 星期 FROM 新闻 LIMIT 1")   # ③ 发 SQL
行 = cur.fetchone()                # ④ 取一行 → (1, '星期六')
con.close()                        # ⑤ 关连接
```

**五步固定套路**，后面所有变体都是它。

### 2.2 返回值的三个层级（**最容易混**）

| 你拿到的 | 类型 | 长什么样 | 什么时候 |
|---|---|---|---|
| `cur.fetchone()` | `tuple` 或 `None` | `(1, '星期六')` | 取一行 |
| `cur.fetchall()` | `list[tuple]` | `[(1, '星期六'), (2, '星期日')]` | 取全部 |
| `cur.fetchall()[0][0]` | `int` / `str` | `1` | 压平成纯值 |

**为什么 fetchall 给的是元组？** 因为数据库的一行可能有 4 列，Python 不知道你要几列，所以每行统一用元组装。

**元组长度 = 你 SELECT 了几列**（实测）：

```sql
SELECT * FROM 新闻 LIMIT 1          → (1, '2026-11-14', '新一轮大范围雨雪来袭…', '星期六')   长度 4
SELECT 序号, 星期 FROM 新闻 LIMIT 1  → (1, '星期六')                                              长度 2
SELECT 新闻内容 FROM 新闻 LIMIT 1    → ('新一轮大范围雨雪来袭…',)                                  长度 1
```

### 2.3 压平成纯列表

```python
[行[0] for 行 in cur.fetchall()]     # [(标题,), (标题,)] → [标题, 标题]
```

这是列表推导式的典型用法：**对每个元素做一次同样的提取，组成新列表**。

---

## 三、概念篇：五个概念分清楚（`SELECT` / `WHERE` / `JOIN` / `GROUP BY` / `ORDER BY`）

> JOIN / GROUP BY 属于 11-18 的排期，这里只做**位置感**，让你知道整张地图长什么样。

| # | 关键词 | 干什么 | 作用在哪个维度 | 你现在会了吗 |
|---|---|---|---|---|
| 1 | `SELECT 列` | **挑列** | 列（横向） | ✅ 今天 |
| 2 | `WHERE 条件` | **筛行** | 行（纵向） | ✅ 今天 |
| 3 | `ORDER BY 排` | **排序** | 行（纵向） | ✅ 今天（`ASC`/`DESC`） |
| 4 | `LIMIT n` | **截断** | 行（纵向） | ✅ 今天 |
| 5 | `GROUP BY 分组` | **分组 + 聚合**（每组算一个数） | 行（纵向） | ⏳ 11-18 |
| 6 | `JOIN 表` | **横向拼表**（把两张表按某个键接起来） | 列（横向） | ⏳ 11-19 |

**记忆锚点**：

- 改**列**的 → `SELECT` / `JOIN`
- 改**行**的 → `WHERE` / `ORDER BY` / `LIMIT` / `GROUP BY`

---

## 四、概念篇：一条 SQL 里的两个世界（**值 vs 标识符**）

这是 SQL 最容易咬人的地方 —— **不加引号的字符串，会被当成列名**。

```sql
SELECT 序号 FROM 新闻 WHERE 星期 = '星期二'
                              ↑ 带引号 = 字符串值
SELECT 序号 FROM 新闻 WHERE 星期 = 星期二
                              ↑ 不带引号 = 当成列名 → 报错
```

**实测报错**：

```
OperationalError: no such column: 星期二
```

**规则**：**字符串值用单引号**；列名/表名如果是中文或含特殊字符，用双引号包起来最保险。

⚠️ 但 SQLite 有一个兼容性缺陷（**本机实测**）：它把双引号也当字符串处理，所以 `"星期二"` **不报错**。这是 SQLite 特有的宽容，别的数据库不一定认。

---

## 五、⭐ API 篇：sqlite3 全表（**这一节是速查手册**）

### 5.1 模块级（`import sqlite3` 之后）

| 名字 | 类型 | 干什么 | 什么时候用 |
|---|---|---|---|
| `sqlite3.connect(路径)` | 函数 | **打开一个数据库文件，返回 Connection** | 每次操作的第 ① 步 |
| `sqlite3.Connection` | 类 | 连接对象的类型 | 一般用不上 |
| `sqlite3.Cursor` | 类 | 游标的类型 | 一般用不上 |
| `sqlite3.Row` | 类 | **按列名取值的行类型** | 想用 `行["序号"]` 而不是 `行[0]` |
| `sqlite3.Error` | 异常 | **所有 sqlite3 异常的祖先** | `except sqlite3.Error` 兜底 |
| `sqlite3.DatabaseError` | 异常 | 数据库逻辑错误 | 少用 |
| `sqlite3.OperationalError` | 异常 | **语法错、表/列不存在、库被锁** | **最常遇到** |
| `sqlite3.IntegrityError` | 异常 | 唯一约束/外键冲突 | 写数据时会遇到 |
| `sqlite3.ProgrammingError` | 异常 | **对象已关闭还去用** | 忘了 close |
| `sqlite3.InterfaceError` | 异常 | 接口用错 | 少用 |

**⭐ 继承关系（实测 `__mro__`）**：

```
Exception
 └─ sqlite3.Error                      ← 抓这个最保险
     └─ sqlite3.DatabaseError
         ├─ sqlite3.OperationalError    ← 不存在的表/列、语法错
         ├─ sqlite3.IntegrityError      ← UNIQUE constraint failed
         ├─ sqlite3.ProgrammingError    ← Cannot operate on a closed database
         ├─ sqlite3.DataError
         └─ sqlite3.InternalError
```

**⚠️ `except` 该写哪个？**

| 写 `except sqlite3.Error` | 写 `except sqlite3.OperationalError` | 写 `except sqlite3.DatabaseError` |
|---|---|---|
| ✅ 抓**所有** sqlite3 错误 | ✅ 只抓「表/列不存在、语法错、库被锁」 | ✅ 抓 DatabaseError 这一层（含下面三个子类） |

**实测**：`except sqlite3.DatabaseError` **能**抓住 `no such table`（因为 `OperationalError` 是 `DatabaseError` 的子类）。

```python
try:
    con.execute("SELECT * FROM 没有这张表")
except sqlite3.DatabaseError as e:
    print("✅ 抓到了，类型 =", type(e).__name__)   # → ✅ 抓到了，类型 = OperationalError
```

**所以**：`OperationalError` 是**更精确**的选择（只抓语法/表列问题），`DatabaseError` 也能抓但范围更大。**别写 `except Exception`** —— 那会把你的代码 bug 一起吞掉。

**实测的四种典型报错**：

| 场景 | 异常类型 | 消息 |
|---|---|---|
| 列名不存在 | `OperationalError` | `no such column: 不存在` |
| 表名不存在 | `OperationalError` | `no such table: 没有这张表` |
| 语法错 | `OperationalError` | `near "SELCT": syntax error` |
| 唯一约束冲突 | `IntegrityError` | `UNIQUE constraint failed: t.id` |
| 连接已关闭还调用 | `ProgrammingError` | `Cannot operate on a closed database.` |

**⚠️ 注意**：`no such table` / `no such column` 报的是 `OperationalError`，而 `OperationalError` 是 `DatabaseError` 的子类 —— 所以 `except sqlite3.DatabaseError` **能**抓住它（实测）。但 `except sqlite3.DatabaseError` 范围更大；**想只抓「表/列不存在、语法错」就写 `OperationalError`**。

### 5.2 Connection 对象（`con`）的方法

| 方法 | 干什么 | 实测返回 / 效果 |
|---|---|---|
| `con.cursor()` | 开一个游标 | `Cursor` 对象 |
| `con.execute(sql, params=())` | **直接执行并返回一个游标**（省掉 `cursor()`） | `Cursor` 对象（可接 `.fetchone()`） |
| `con.executemany(sql, 参数列表)` | 批量执行同一条语句 | 实测插入 3 条 |
| `con.commit()` | **提交事务**（写操作必须） | 写操作持久化 |
| `con.rollback()` | 回滚未提交的改动 | 数据还原 |
| `con.close()` | 关连接 | 再用会报 `ProgrammingError` |
| `con.rollback()` 后再 `close()` | — | 未提交的写操作**被回滚** |
| `con.row_factory` | 设成 `sqlite3.Row` → 行能按列名取 | 实测 `r["序号"]` 可用 |
| `con.total_changes` | 累计改动行数 | 插入后 = 1（**rollback 也不回退**） |
| `con.in_transaction` | 当前是否在事务中 | 刚连上 = `False`；INSERT 后 = `True` |
| `con.isolation_level` | 事务隔离级别，`''` = 默认 | `connect(路径, isolation_level=None)` = **自动提交** |
| `con.autocommit` | Python 3.12 新增的自动提交开关 | 实测默认 `-1`（= 旧式行为） |

**`con.execute()` 快捷方式实测**：

```python
con.execute("SELECT COUNT(*) FROM 新闻").fetchone()   # → (15,)
```

一行顶三行。但**多步查询还是用游标更清楚** —— 因为游标能复用。

### 5.3 Cursor 对象（`cur`）的方法

| 方法 | 干什么 | 实测返回 |
|---|---|---|
| `cur.execute(sql)` | 执行一条 SQL | `Cursor`（可链式） |
| `cur.execute(sql, (a, b))` | **参数化执行**（防注入） | `Cursor` |
| `cur.execute(sql, {"k": v})` | **命名参数**（`:k` 占位） | 实测 `{'id': 1, 'name': '张三'}` 可用 |
| `cur.fetchone()` | 取**下一行** | `tuple` / **无结果时 `None`** |
| `cur.fetchmany(n)` | 取**接下来 n 行** | `list[tuple]` |
| `cur.fetchall()` | 取**剩下全部** | `list[tuple]` |
| `cur.description` | **列名信息** | SELECT 后 = 元组列表；非 SELECT = `None` |
| `cur.rowcount` | 受影响行数 | SELECT = **`-1`**；UPDATE = 实际条数 |
| `cur.lastrowid` | 最后插入的自增主键 | 插入后 = `3` |
| `cur.close()` | 关游标 | 再用报 `ProgrammingError` |
| `cur.row_factory` | 单独给这个游标设行类型 | — |

**⭐ 结果集是「流」的**（实测，这是最容易误解的一条）：

```python
cur.execute("SELECT 序号 FROM 新闻 LIMIT 5")
cur.fetchmany(2)    # → [(1,), (2,)]
cur.fetchmany(2)    # → [(3,), (4,)]      ← 接着上次的位置，不是从头
cur.fetchall()      # → [(5,)]            ← 只剩最后一条
```

**同一个游标重新 `execute` 会覆盖上一次结果**（实测）：

```python
cur.execute("SELECT 序号 FROM 新闻 ORDER BY 序号 ASC LIMIT 3")
cur.fetchall()          # → [(1,), (2,), (3,)]
cur.execute("SELECT 星期 FROM 新闻 LIMIT 2")
cur.fetchall()          # → [('星期六',), ('星期六',)]   ← 上次的结果没了
```

### 5.4 `sqlite3.Row`：让行能按列名取

**实测的完整能力**：

```python
con.row_factory = sqlite3.Row
r = con.execute("SELECT id, name FROM t").fetchone()

list(r.keys())   # → ['id', 'name']
r["name"]        # → '张三'      ← 按名字
r[0], r[1]      # → 1, '张三'    ← 按位置也能用
len(r)           # → 2
dict(r)          # → {'id': 1, 'name': '张三'}
list(r)          # → [1, '张三']
```

**什么时候用**：
- 只需要一两列 → **用默认 tuple**（`行[0]` 更快，不用记列名）
- 要多列、要按名字取 → **用 `sqlite3.Row`**
- `con.row_factory` 会**被 `con.execute()` 返回的游标继承**（实测）

### 5.5 参数化：`?` 与 `:name`

```python
# 位置参数（qmark）—— Python 的 sqlite3 默认风格
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = ?", ("星期二",))

# 命名参数 —— SQL 里写 :name，传字典
cur.execute("INSERT INTO t (id,name) VALUES (:id, :name)", {"id": 1, "name": "张三"})
cur.execute("SELECT name FROM t WHERE id = :i", {"i": 2})
```

**本机 `sqlite3.paramstyle` = `'qmark'`**（实测），即 `?` 是默认占位符。

**为什么必须参数化**（不是「更规范」，是**防注入**）：

```python
# ❌ 危险：用户输入直接拼进 SQL
sql = "SELECT 序号 FROM 新闻 WHERE 星期 = '%s'" % 用户输入
# 用户输入一个 ' 就能闭合引号，后面全是他的代码

# ✅ 安全：值和代码分离
cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = ?", (用户输入,))
```

---

## 六、⭐ 三个语义陷阱（**API 层面最容易踩的**）

### 陷阱 1 · `commit()` 不写，写的操作等于没写

**实测**：

```python
con.execute("CREATE TABLE t (x INT)")
con.execute("INSERT INTO t VALUES (1)")
con.close()          # 没 commit
# 重新打开
con = sqlite3.connect(同一个文件)
con.execute("SELECT COUNT(*) FROM t").fetchone()   # → (0,)   数据没了
```

**但表还在**（DDL 在 SQLite 里会自动提交，DML 不会）。

**规则**：

| 操作 | 要 commit 吗 |
|---|---|
| `SELECT` | ❌ 不用（只读） |
| `INSERT` / `UPDATE` / `DELETE` | ✅ **必须** |
| `CREATE TABLE` / `DROP TABLE` | SQLite 里自动提交了，但**写了 commit 更保险** |

**三个解决方案**（任选）：

```python
# 方案 A：手动 commit
con.execute("INSERT ...")
con.commit()
con.close()

# 方案 B：with 语句 —— 退出时自动 commit，异常时自动 rollback
with sqlite3.connect(库路径) as con:
    con.execute("INSERT ...")
    con.execute("UPDATE ...")
# ← 出了块，自动提交（事务结束了）
# ⚠️ 但连接【没关】！需要 con.close()（见下面的坑）

# 方案 C：完全自动提交
con = sqlite3.connect(库路径, isolation_level=None)
```

**⚠️ `with` 的两个坑（都实测过）**：

**坑 A：块里抛异常 → 数据回滚，但表已经建好了**

```
with 退出后行数 = 0     ← INSERT 回滚了
表存在 = True          ← CREATE TABLE 没回滚
```

**坑 B：⭐ `with` 不会关闭连接！**

```python
with sqlite3.connect(库路径) as con:
    con.execute("SELECT 1")
# 出了块，连接【还开着】
con.execute("SELECT 1")   # → 不报错！说明连接还活着
```

**`with sqlite3.connect(...)` 管的是「事务」，不是「连接的生命周期」**：

| | `with` 管不管 |
|---|---|
| 正常退出 → commit | ✅ 管 |
| 抛异常 → rollback | ✅ 管 |
| **关闭连接** | ❌ **不管** |

**所以 `with` 写法仍然要写 `close()`**。最保险的完整写法：

```python
with sqlite3.connect(库路径) as con:
    con.execute("INSERT ...")
con.close()          # ← with 不会帮你关，得自己关
```

或者用 `contextlib.closing`（**本机已测**）—— 它**只管关连接，不管提交**：

```python
from contextlib import closing
with closing(sqlite3.connect(库路径)) as con:
    con.execute("INSERT ...")
    con.commit()      # closing 只管关，不管提交
```

**实测**：出了 `closing` 块 → `con.execute()` 报 `ProgrammingError: Cannot operate on a closed database.`，文件也能删了 → **连接确实关了**。

### 陷阱 2 · `rowcount` 对 SELECT 是 `-1`，不是行数

**实测**：

```python
cur.execute("SELECT 序号 FROM 新闻")
cur.rowcount      # → -1      ← SELECT 没有「影响行数」的概念
cur.execute("UPDATE 新闻 SET 序号 = 序号 WHERE 序号 = 1")
cur.rowcount      # → 1       ← UPDATE 才有
```

**要 SELECT 的行数 → 用 `COUNT(*)`，不要用 `rowcount`**：

```python
cur.execute("SELECT COUNT(*) FROM 新闻").fetchone()[0]   # → 15
```

> ⚠️ **上面那个 UPDATE 千万别在正主库上跑** —— 就算后面 `rollback()` 了，SQLite 文件也会因为写事务而**变大**（实测 8192 → 12288 字节，多出一个空洞页，hash 也变了）。
> **写操作一律在副本上做。**（对应 T42）

### 陷阱 3 · 忘了 `close()` → 文件被占住

**实测**：`connect()` 之后不关连接 → **文件改不了名、删不掉、git 也提交不了**。

而且：

```python
con.close()
con.execute("SELECT 1")   # → ProgrammingError: Cannot operate on a closed database.
con.close()               # → 关两次，不报错 ✅
```

---

## 七、⭐ 三个 Python 层的「等价写法」对照

同一个查询，三种写法：

```python
# 写法 1：游标（标准，练习文件就用这个）
con = sqlite3.connect(库路径)
cur = con.cursor()
cur.execute("SELECT 新闻内容 FROM 新闻 WHERE 星期 = ?", ("星期二",))
结果 = [行[0] for 行 in cur.fetchall()]
con.close()

# 写法 2：快捷（省一行）
con = sqlite3.connect(库路径)
结果 = [行[0] for 行 in con.execute("SELECT 新闻内容 FROM 新闻 WHERE 星期 = ?", ("星期二",)).fetchall()]
con.close()

# 写法 3：with（自动提交事务，但连接还是要自己关）
with sqlite3.connect(库路径) as con:
    结果 = [行[0] for 行 in con.execute("SELECT 新闻内容 FROM 新闻 WHERE 星期 = ?", ("星期二",)).fetchall()]
con.close()          # ← with 不会帮你关！
```

**三种写法实测结果完全一样**：`['...标题...', '...标题...']`

**该用哪个？**

| 场景 | 用哪个 |
|---|---|
| 练习 / 学习阶段 | 写法 1（**看得见每一步**） |
| 写生产代码、批量写数据 | 写法 3 + **记得补 `con.close()`** |
| 只查一次、图省事 | 写法 2 |

---

## 八、接下来做什么

### 8.1 你现在能做的

1. 跑 `练习/_参考样例_SQLite_API.py`，把每一段输出和本讲义对上
2. 读 `笔记/讲义/11-17_讲义_SQL_SELECT与WHERE.md` 的第五节（WHERE 七种写法）+ 第六节（六个坑）
3. 做 `练习/11.17练习_SQL_SELECT与WHERE.py` 的 8 题 —— **每题都是「五步套路换个 SQL」**

### 8.2 还没学的（别提前看）

| 内容 | 排期 | 关键点 |
|---|---|---|
| `GROUP BY` + `ORDER BY` + `LIMIT` | 11-18 上午 | 分组聚合、排序取前 N |
| `JOIN` | 11-19 | 横向拼表，**JD-01 明确点名** |
| 写操作（`INSERT`/`UPDATE`） | 之后 | 现在只用 `SELECT` 就够 |

### 8.3 ⚠️ 一个提醒

**你现在的载体是 SQLite，不是 MySQL。**

SQLite 的兼容缺陷（双引号当字符串、`==`、小写 `and`）在 MySQL/PostgreSQL 上**不成立**。
**写代码永远用「单引号 + 一个等号 + 大写 AND」** —— 这样你的 SQL 换到任何数据库都能跑。

---

## 附：本讲义的四个「我自己也写错了」

写这份讲义时，我先写了几个「常见说法」，一跑发现**跟实测相反**：

| 我原本以为 | 实测 |
|---|---|
| `OperationalError` 不是 `DatabaseError` 的子类，`except DatabaseError` 抓不住它 | ❌ **我错了** —— 它是子类，`except DatabaseError` **能**抓到（实测 `__mro__`） |
| `with` 块里没 commit，退出后数据一定在 | ❌ INSERT 回滚了，只有 DDL 留下 |
| `with sqlite3.connect()` 退出后连接就关了 | ❌ **它只管事务，不管关连接**（实测：退出后 `con.execute()` 还能用） |
| `rowcount` 在 SELECT 后是 0 | ❌ 是 **-1** |
| `fetchmany()` 每次都从头取 | ❌ 是**接着上次的位置**取 |
| `SELECT 1/0` 能证明 WHERE 先执行 | ❌ SQLite 里 `1/0` 返回 NULL **不报错** → 改用 `EXPLAIN QUERY PLAN` |

> 这条铁律已经进工具链坑库：**T41 —— 讲「X 会报错 / X 会返回什么」之前必须本机实跑。**

---

## 自测题（不看上面，闭卷答）

1. `cur.fetchone()` 在没有结果时返回什么？`cur.fetchall()` 呢？
2. `cur.fetchall()` 返回的每个元素是什么类型？长度由什么决定？
3. 为什么 `SELECT 新闻内容 FROM 新闻` 返回的行长度是 1，而不是 4？
4. `cur.rowcount` 在 SELECT 之后是多少？想要行数该用什么？
5. `INSERT` 之后忘了 `commit()` 就 `close()`，数据还在吗？表还在吗？
6. `cur.description` 在执行 INSERT 之后是什么？
7. `fetchmany(2)` 连续调两次，第二次拿到的是不是从第一行开始？
8. `sqlite3.Row` 相比默认的 tuple，多了哪个能力？
9. `except sqlite3.DatabaseError` 能抓住 `no such table` 吗？（提示：看 `__mro__`）
10. 「星期二」不加引号会报什么错？为什么？
11. `SELECT 1/0 FROM 新闻 WHERE 序号 = 99999` 为什么不报错？这说明什么？**（注意：这题的答案不是你想的那个）**
12. `with sqlite3.connect(...)` 的块里抛异常了，数据会怎样？**它会关闭连接吗？**
13. `sqlite3.Row` 的 `keys()` 返回什么？
14. `cur.lastrowid` 什么时候用得上？
