# 11-18 讲义：GROUP BY / COUNT + ORDER BY / LIMIT（1h）

> 对应日程：11-18 上午「📌 SQL 实操②：GROUP BY/COUNT + ORDER BY/LIMIT 聚合统计 1h」
> 上游：11-17 讲义 SQL SELECT / WHERE（8 题已过）｜ 下游：11-18 下午 SQL JOIN 连接表 + SQLite 实操①
> 配套练习：`练习/11.18练习_GROUP_BY与ORDER_BY_LIMIT.py`（7 题，写完跑文件内检查）
> 数据：`练习/数据/新闻库.sqlite`（表 `新闻`，15 行 4 列：序号 / 日期 / 新闻内容 / 星期）

> ⚠️ **本文所有 SQL 输出都是实跑出来的**（Python 3.12.7 / `D:\AAAA`，SQLite 3.x 自带）。
> 复习时自己跑一遍，每段都能对上。

---

## 一、这三种东西各自解决什么问题

前面 8 题都是「**筛行**」——选哪些行、每行取哪列。今天学的是「**汇总结论**」。

| | 干什么 | pandas 对应 | 一句话 |
|---|---|---|---|
| `GROUP BY` | 把行按某个列**分堆**，一堆算一个结果 | `df.groupby("星期")` | 分组 |
| `COUNT(*)` | 数**有几行** | `.size()` | 计数 |
| `ORDER BY` | 把结果**排序** | `df.sort_values(...)` | 排序 |
| `LIMIT` | 只取**前 N 行** | `df.head(N)` | 截断 |

**关键区别：`WHERE` 筛的是「行」，`GROUP BY` 算的是「组」。**

### 为什么必须有 GROUP BY

想回答「每个星期各有几条新闻」，不用 GROUP BY 的话，你得写 7 遍：

```sql
SELECT COUNT(*) FROM 新闻 WHERE 星期 = '星期一';   -- 3
SELECT COUNT(*) FROM 新闻 WHERE 星期 = '星期二';   -- 2
...还要写 5 遍
```

用 GROUP BY，一句：

```sql
SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期;
```

一次出 7 行。**这就是「一次问清楚所有分组」的价值。**

---

## 二、五步套路不变，只换第三步（说 SQL）

昨天学的 connect → cursor → execute → fetchall → close，**一个字都不用改**。今天只改 `execute` 里那句 SQL。

```python
import sqlite3
from pathlib import Path

库路径 = Path(__file__).parent / "数据" / "新闻库.sqlite"

def 你的函数():
    con = sqlite3.connect(库路径)          # ① 连上
    cur = con.cursor()                     # ② 拿话筒
    cur.execute("SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期")   # ③ 说 SQL（今天改这句）
    结果 = cur.fetchall()                  # ④ 收结果
    con.close()                            # ⑤ 关电话
    return 结果                            # ⚠️ 必须 return
```

⚠️ **注意第 4 步变了**：昨天 `SELECT 一列` 时，`fetchall()` 回来是 `[('值',), ...]`，要用 `[行[0] for 行 in ...]` 压平。
今天 `SELECT 两列`（星期 + 条数），`fetchall()` 回来是 `[('星期一', 3), ...]` —— **两列元组，正好就是你要的形状，不用压平**。

> 元组长度 = 你 SELECT 了几列（讲义 11-17 第三节的结论，这里再用一次）。

---

## 三、GROUP BY：分堆 + 计数

```sql
SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期;
```

读法：**「按星期分堆，每堆数几行，把（星期，几条）给我」**

实测输出：

```
[('星期一', 3), ('星期三', 1), ('星期二', 2), ('星期五', 2), ('星期六', 4), ('星期四', 1), ('星期日', 2)]
```

拆开看这个结果：

| 星期 | 条数 |
|---|---|
| 星期一 | 3 |
| 星期二 | 2 |
| 星期三 | 1 |
| 星期四 | 1 |
| 星期五 | 2 |
| 星期六 | 4 |
| 星期日 | 2 |

加起来 3+2+1+1+2+4+2 = 15 ✅ 对上了总行数。

### 3.1 AS：给列起别名

```sql
SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期;
```

`AS n` = 给「条数」这一列起个短名字叫 `n`。起别名后，**ORDER BY 里就能用 `n`**，省得写一长串 `COUNT(*)`。

> 也可以 `SELECT 星期 AS 星期名, COUNT(*) AS n ...`，随便起。

### 3.2 GROUP BY 后面跟 WHERE：先筛行，再分堆

```sql
SELECT 星期, COUNT(*) FROM 新闻 WHERE 序号 <= 10 GROUP BY 星期;
```

顺序是固定的：**`WHERE`（筛行）在 `GROUP BY`（分堆）之前**。

实测输出（只数序号 1~10 的新闻）：

```
[('星期一', 2), ('星期三', 1), ('星期二', 2), ('星期六', 3), ('星期四', 1), ('星期日', 1)]
```

对比一下全部 15 条时的结果：星期二从 2 → 2（不变），星期六从 4 → 3（少了一条），星期一从 3 → 2（少了一条）。
**差的正好是被 WHERE 筛掉的那几行。** 这就是 WHERE 在分堆前生效的意思。

---

## 四、ORDER BY：排序

```sql
SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n DESC;
```

读法：**「分堆计数后，按 n 从大到小排」**

实测输出：

```
[('星期六', 4), ('星期一', 3), ('星期二', 2), ('星期五', 2), ('星期日', 2), ('星期三', 1), ('星期四', 1)]
```

| 关键字 | 意思 |
|---|---|
| `ASC` | 升序（小的在前）—— **默认值，不写就是它** |
| `DESC` | 降序（大的在前） |

### ⚠️ 坑 1（今天最该撞的）：并列时顺序是**不确定的**

看上面结果里 3 个「2」：星期二、星期五、星期日。它们的顺序**看起来**有规律，其实是碰巧。

SQL 只说了「按 n 降序」，没说「n 相同的时候按什么排」→ 那一档的顺序由数据库自己决定，**换台机器、换个版本可能就变了**。

**实测证据**（同一份数据，只改次级排序键）：

```sql
-- 只写 ORDER BY n DESC
[('星期六', 4), ('星期一', 3), ('星期二', 2), ('星期五', 2), ('星期日', 2), ...]
-- 加了次级排序键 ORDER BY n DESC, 星期 ASC
[('星期六', 4), ('星期一', 3), ('星期二', 2), ('星期五', 2), ('星期日', 2), ...]
```

**这次碰巧一样，但不敢保证下次一样。**

**正确解法：加次级排序键**——

```sql
ORDER BY n DESC, 星期 ASC
```

意思是「先按 n 降序，n 一样时再按星期升序」。这样顺序就**完全确定**了。

> 💡 **这跟昨天讲义里的坑一脉相承**：不写 ORDER BY，数据库不保证返回顺序。
> 今天多了一层：**写了 ORDER BY 也不一定够**——并列的那一档还需要指定第二排序键。

### ⚠️ 坑 2：中文排序不是「按星期几的顺序」

实测 `ORDER BY 星期 ASC`：

```
[('星期一',), ('星期三',), ('星期二',), ('星期五',), ('星期六',), ('星期四',), ('星期日',)]
```

**星期三 排在 星期二 前面！** 因为数据库按**字符编码**排，不是按「周一到周日」的语义排。「三」的编码比「二」大，所以三在前。

→ 想要「真正的星期顺序」，得自己指定一个排序依据，不能靠中文直接排。

### ORDER BY 可以用别名，也可以用表达式

```sql
ORDER BY n DESC          -- 用别名（推荐）
ORDER BY COUNT(*) DESC   -- 用表达式，也行
```

---

## 五、LIMIT：只取前几行

```sql
SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n DESC, 星期 ASC LIMIT 3;
```

读法：**「分堆计数，排序，取前 3 行」**

实测输出：

```
[('星期六', 4), ('星期一', 3), ('星期二', 2)]
```

这就是「**新闻最多的 3 个星期**」。

### LIMIT 的位置：永远在最后

SQL 子句的执行顺序（**背下来**）：

```
WHERE  →  GROUP BY  →  HAVING  →  ORDER BY  →  LIMIT
筛行      分堆        筛组      排序        截断
```

`LIMIT` 必须在 `ORDER BY` 后面——**先排序，才知道哪几行是「前 N 行」**。反过来的 SQL 是语法错误。

---

## 六、HAVING：筛「组」（不是筛行）

`WHERE` 筛的是**行**（分堆之前），`HAVING` 筛的是**组**（分堆之后）。

想找「新闻条数 ≥ 2 的星期」——这个条件是关于**组**的，WHERE 用不上：

```sql
SELECT 星期, COUNT(*) AS n
FROM 新闻
GROUP BY 星期
HAVING COUNT(*) >= 2
ORDER BY n DESC, 星期 ASC;
```

实测输出：

```
[('星期六', 4), ('星期一', 3), ('星期二', 2), ('星期五', 2), ('星期日', 2)]
```

星期三、星期四（各 1 条）被滤掉了。

### 对照表：WHERE vs HAVING

| | WHERE | HAVING |
|---|---|---|
| 筛什么 | **行**（分堆前的单条新闻） | **组**（分堆后的每个星期） |
| 位置 | GROUP BY **之前** | GROUP BY **之后** |
| 例子 | `WHERE 序号 <= 10` | `HAVING COUNT(*) >= 2` |

---

## 七、pandas ↔ SQL 对照表（**这一页最值钱**）

| pandas | SQL |
|---|---|
| `df["星期"].unique()` | `SELECT DISTINCT 星期` |
| `df.groupby("星期").size()` | `GROUP BY 星期` + `COUNT(*)` |
| `df.groupby("星期").size().sort_values(ascending=False)` | `GROUP BY 星期 ORDER BY n DESC` |
| `df.head(3)` | `LIMIT 3` |
| `df[df["序号"] <= 10]` | `WHERE 序号 <= 10` |
| `df.groupby("星期").size()[lambda s: s >= 2]` | `GROUP BY 星期 HAVING COUNT(*) >= 2` |

**实测验证同一件事两套语言：**

```
pandas：df.groupby('星期').size().sort_values(ascending=False)
   →  星期六 4, 星期一 3, 星期二 2, 星期五 2, 星期日 2, 星期三 1, 星期四 1

SQL   ：SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n DESC, 星期 ASC
   →  [('星期六', 4), ('星期一', 3), ('星期二', 2), ('星期五', 2), ('星期日', 2), ...]
```

**两边一模一样。** 左边你在 pandas 上学过，右边今天一句 SQL 搞定。

---

## 八、今天真正要记住的 6 件事

1. **五步套路不变**，只改 `execute` 里那句 SQL
2. **`SELECT 两列 → fetchall() 直接就是 list[tuple]`，不用压平**（元组长度 = 列数）
3. **子句顺序**：`WHERE → GROUP BY → HAVING → ORDER BY → LIMIT`，LIMIT 永远最后
4. **`WHERE` 筛行、`HAVING` 筛组**，位置不能换
5. **`ORDER BY` 并列时顺序不确定** → 要加次级排序键（`ORDER BY n DESC, 星期 ASC`）
6. **中文排序是按编码排的**，不是按语义（星期三 排在 星期二 前）

---

## 九、自测题（不看上面，闭卷答）

1. `GROUP BY` 和 `WHERE` 的作用顺序差在哪？`HAVING` 排在哪？
2. `SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期` 每行元组长度是几？`行[0]` 和 `行[1]` 分别是啥？
3. `ORDER BY n DESC` 里的 `n` 从哪来？不写 `AS n` 会怎样？
4. `ORDER BY` 的 `ASC` / `DESC` 分别是什么方向？不写默认哪个？
5. 为什么 `ORDER BY n DESC` 还不够稳？加什么才稳？
6. 「新闻最多的 3 个星期」用一句 SQL 怎么写？子句顺序是什么？
7. `LIMIT 3` 能写在 `ORDER BY` 前面吗？为什么？
8. 中文排序 `ORDER BY 星期 ASC`，「星期三」会排在「星期二」前面还是后面？为什么？
9. 想找「条数 ≥ 2 的星期」，用 WHERE 还是 HAVING？两者位置分别在哪？
10. `SELECT COUNT(*) FROM 新闻` 回来是 `[(15,)]` 还是 `[15]`？为什么？
11. pandas 里 `df.groupby("星期").size()` 对应 SQL 哪一句？
12. `SELECT 星期 FROM 新闻 GROUP BY 星期` 和 `SELECT DISTINCT 星期 FROM 新闻` 有区别吗？

---

## 十、接下来做什么

**先做练习**：`练习/11.18练习_GROUP_BY与ORDER_BY_LIMIT.py`（7 题，每题一个函数，都要 `return`）

7 题 = 今天三样东西的组合：

| 题 | 考什么 |
|---|---|
| 1 | GROUP BY + COUNT（基础分堆） |
| 2 | ORDER BY DESC + 次级排序键（坑 1） |
| 3 | ORDER BY + LIMIT（取前 3） |
| 4 | WHERE + GROUP BY（先筛行再分堆） |
| 5 | ORDER BY ASC + LIMIT 1（取最少的那天） |
| 6 | HAVING（筛组） |
| 7 | HAVING + ORDER BY + LIMIT（综合） |

**然后：11-18 下午 `SQL：JOIN 连接表`（0.5h）+ `SQLite 实操①：建表灌数 + JOIN 查询`（1h）**——今天没学的最后一样。

预告 JOIN 长什么样（还没建表，先看骨架）：

```sql
SELECT 新闻.序号, 新闻.星期, 分类.名称
FROM 新闻
JOIN 分类 ON 新闻.序号 = 分类.序号;
```

「把两张表按某个共同列接起来」——语法不难，明天连着 SQLite 建表一起练。
