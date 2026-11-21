# 11-21 讲义：SQLite → MySQL 语法差异对照

> 对应日程：11-20 下午「📌 SQLite→MySQL 语法差异对照（0.5h，从 11-19 晚顺延）」  
> 覆盖范围：JD-01 原文「了解 MySQL/PostgreSQL，做基本数据查询」→ **只对照基本查询，不装 MySQL**  
> 上游：`11-19_讲义_SQL复盘.md`（SQLite 侧全部实跑过）  
> 查证日期：2026-11-21

> ✅ **状态：本人已核对修改 + 三题已作答**（2026-11-21）。8 点对照表 + 三道自测题均经本人过目确认，第四节的答案由助手口语化、本人对照修改。日程表状态列待本人脱稿讲清后自行回填。

---

## 一、8 点对照表（SQLite 侧 = 你已实跑；MySQL 侧 = 本次查证）

| # | 对照点            | SQLite（你已学·实跑）                                                        | MySQL（本次查证）                                                                                | 差异一句话                                                                | 出处                                                |
| - | -------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- | ------------------------------------------------- |
| 1 | 字符串引号          | 单引号 `'星期二'`；双引号会被当字符串（SQLite 兼容缺陷，DQS）                                | 单引号 `'星期二'`；双引号默认也当字符串，**除非开 `ANSI_QUOTES` 模式（此时双引号变标识符）**                                 | 两边都推荐单引号；真正的差异在标识符引用                                                 | MySQL 8.0 String Literals；SQLite quirks.html §DQS |
| 2 | 相等比较           | `=` 和 `==` 都能跑（讲义提过 `==` 不报错）                                         | 只用 `=`；`==` 不是合法运算符 → 语法错误                                                                 | SQLite 比较宽松支持 `==`，MySQL 只认 `=`，迁移时要统一写 `=`                          | SQL 方言通用规则                                        |
| 3 | 参数占位符          | Python `sqlite3` 用 `?`，单元素带尾逗号 `("%金融%",)`                            | Python 驱动（PyMySQL / mysql-connector）用 `%s`：`cursor.execute("... WHERE 星期 = %s", ("星期二",))` | **这是驱动层差异，不是 SQL 本身**；换库要换占位符                                        | PyMySQL 用法；devhelper.tools 注入防护示例                 |
| 4 | 分页             | `LIMIT 3` / `LIMIT 3 OFFSET 2`                                        | `LIMIT 3` / `LIMIT 2, 3`（offset 在前，count 在后）/ `LIMIT 3 OFFSET 2`                           | MySQL 多一种 `LIMIT offset, count` 写法，**顺序不能记反**                        | Wikibooks SQL Dialects Reference                  |
| 5 | GROUP BY 选非聚合列 | 允许 `SELECT 序号, COUNT(*) FROM 新闻 GROUP BY 星期`（宽松，取组内任一行）               | **默认报错 ERROR 1055**（`ONLY_FULL_GROUP_BY`，MySQL 5.7.5+ 默认开启）                                | SQLite 的宽松行为是迁移第一坑；MySQL 要求 SELECT 列必须在 GROUP BY 里或被聚合               | MySQL 官方文档 §14.19.3；报错原文见下节                       |
| 6 | 包住表名/列名        | 双引号 `"列名"` 或方括号 `[列名]`                                                | **反引号** `` `列名` ``                                                                         | 标识符引用符号不同； MySQL 开 `ANSI_QUOTES` 后才用双引号                              | devhelper.tools「dialect map」                      |
| 7 | 自增主键           | `id INTEGER PRIMARY KEY AUTOINCREMENT`（**必须写 `INTEGER`，写 `INT` 不生效**） | `id INT AUTO_INCREMENT PRIMARY KEY`（必须带索引/主键）                                              | 关键字位置不同；SQLite 的 `AUTOINCREMENT` 用 `sqlite_sequence` 记历史最大值、不复用已删 ID | CSDN SQLite vs MySQL 对比；ipipp.com 语法差异总结          |
| 8 | 空值替换           | `IFNULL(x, 0)` / `COALESCE(x, 0, ...)`                                | `IFNULL(x, 0)` / `COALESCE(x, 0, ...)`                                                     | **这一条两者通用、无差异** —— 特意列出来：不是每点都有差异。                                   | SQLite/MySQL 函数文档                                 |

## 二、ERROR 1055 报错原文（已核实，非手写简化版）

```
ERROR 1055 (42000): Expression #1 of SELECT list is not in GROUP BY clause
and contains nonaggregated column 'mydb.t.address' which is not functionally
dependent on columns in GROUP BY clause; this is incompatible with
sql_mode=only_full_group_by
```

出处：MySQL 官方文档 <https://dev.mysql.com/doc/refman/5.7/en/group-by-handling.html>

**三种解法**（从上轮讲义坑 5 的"别依赖宽松行为"接上）：

1. 把非聚合列加进 `GROUP BY` → `GROUP BY 星期, 序号`
2. 用 `ANY_VALUE(序号)` 明确告诉 MySQL「随便取哪个都行」
3. `SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));`（仅应急，不推荐）

## 三、一条贯穿原则（迁移不踩坑）

讲义里那句「写代码永远用**单引号 + 一个等号 + 大写 AND**」现在有了完整解释：

- 单引号 → 避开第 1 点（双引号在两库含义不同）
- 一个等号 → 避开第 2 点（`==` 在 MySQL 报错）
- 大写 `AND` → SQL 关键字不区分大小写，但统一风格便于 review

再加两条（本次新增）：

- **参数化用对应驱动的占位符**（第 3 点）：`?` ≠ `%s`
- **SELECT 列必须能解释**（第 5 点）：要么在 GROUP BY 里，要么被聚合

---

## 四、自测三题（我答的，助手把它讲口语了）

### 题 1 · `SELECT 序号` 被 MySQL 拒

我原来写的是「GROUP BY 只写了星期，但 SELECT 里除了 COUNT(*) 还选了序号」。换个说法：

MySQL 默认开着 `ONLY_FULL_GROUP_BY`，它的规矩是——你按星期分组，那 SELECT 里就只能放「星期」这种分组的列，或者 `COUNT(*)` 这种算出来的东西。「序号」既没拿来分组，也没被算，那一个星期底下有好几行，到底给你显示哪个序号？它觉得这事儿说不清，就报错 1055 了。

SQLite 没这规矩，它随便抓一行给你，**不报错，但结果是瞎抓的**。所以 MySQL 报错其实是在提醒我：这句本来就不该这么写。

怎么改？最干净的是把「序号」直接删掉——我本来要的就是「每个星期有几条」，序号压根用不上：

```sql
SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期
```

另外两条路：`GROUP BY 星期, 序号`（能跑，但每个序号都成了一组，COUNT 全是 1，意思变了）；`ANY_VALUE(序号)`（强行告诉它随便取一个，取哪个无所谓时才用）。

### 题 2 · `?` 搬进 PyMySQL

我原来写的是「这是驱动层差异，不是 SQL 本身」。说人话：

`?` 这个问号不是 SQL 的规定，是 **Python 那个数据库模块自己定的**。`sqlite3` 认 `?`，PyMySQL 认 `%s`。SQL 句子一个字没改，变的是「Python 怎么把值填进去」这一层。所以搬过去的时候，`?` 得换成 `%s`，不然参数对不上。

还有个容易踩的坑：`%s` 长得像 Python 的 `%` 字符串格式化，但它不是。值照样是用元组单独传给 `execute` 的，由驱动去转义，所以还是防注入的。千万别手贱写成 `sql % ("星期二",)`，那就又变回字符串拼接、把注入漏洞请回来了。

### 题 3 · `SELECT "星期二"`

我原来写的是「SQLite 双引号先当列名找，找不到才回退当字符串」。展开讲：

在 SQLite 里，双引号是**先当列名去表里找**的。表里没有叫「星期二」的列，它才退一步当字符串用，于是每行都返回「星期二」这个词。

MySQL 默认双引号就是字符串，结果一样——**但前提是你没开 `ANSI_QUOTES`**。这个模式一开，双引号就变成「包列名」的了，同一句话直接报「未知列」。

所以结论就一句：字符串老老实实写单引号。双引号这东西，换个库、甚至同一个库换个配置，意思都可能变。

> 销账标准：本人能脱稿讲清这三题（不看讲义）+ 路径发助手核对 → 才回填日程表状态列。
