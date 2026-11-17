# 11-16 讲义：pandas 读与查看 + 筛选增删列（1.5h）

> 对应日程：11-16 上午「pandas 读 CSV/Excel + 查看（2h）」+ 下午「pandas 筛选/增删列（2h）」
> 产出文件：`练习/11.15练习_pandas读CSV与查看.py`（8 题）、`练习/11.17练习_pandas筛选与增删列.py`（8 题）
> 可跑参考样例：`练习/_参考样例_pandas讲义.py`（讲义里每一段输出都能用它复现）
> 上游：11-14 re 正则、11-11 os/datetime、11-03 文件读写/csv/json
> 下游：**11-16 晚上 SQL `SELECT/WHERE`**（同一件事的另一套语言）、11-18 SQLite 查 CSV

> ⚠️ **本文所有输出都是实跑出来的**（pandas 2.2.2 / Python 3.12.7，本机 `D:\AAAA`）。
> 复习时自己跑 `_参考样例_pandas讲义.py`，每一段都能对上。

---

## 一、这 1.5h 到底解决什么问题

**一句话：pandas 是「用代码操作表格」的工具，替你干 Excel 的活。**

为什么学这个：

| | 干同一件事的方式 | 适合什么 |
|---|---|---|
| Excel | 点鼠标 | 一次性的、看得到的表 |
| **pandas** | 写代码 | **重复的、要进程序的、要跟别的数据拼的** |
| SQL | 写代码 | 数据量超大、在数据库里 |

你是要当 AI 应用工程师 —— 后面做 RAG 要处理知识库、做 Agent 要处理工具返回的数据、做作品要处理爬来的新闻，**全是表格**。pandas 是这层的基本功。

---

## 二、两个核心对象（记住这一句就够）

```
DataFrame = 表格（二维，有行有列，每列有名字）
Series    = 表格里的【一列】（一维，也带行标签）
```

**一个 DataFrame 可以理解成「多个 Series 按列拼在一起」。**

```python
import pandas as pd
from pathlib import Path

df = pd.read_csv(Path(__file__).parent / "数据" / "news_示例.csv")
type(df)   # DataFrame
df.shape   # (15, 4)

一列 = df["星期"]
type(一列)   # Series
一列.shape   # (15,)
```

`index` = 行标签，默认是 `0,1,2,...` —— **它是行号，不是数据本身**。你也可以把 `序号` 列设成 index，但初学阶段别折腾。

---

## 三、读文件（以及那个 BOM 坑）

```python
df  = pd.read_csv(CSV路径)     # 逗号分隔的 .csv
df2 = pd.read_excel(EXCEL路径)  # .xlsx（本机 openpyxl 3.1.5 已装）
```

两者返回的都是 DataFrame，shape 一样：`(15, 4)`。

### ⭐ 坑1 · 路径：Windows 反斜杠会被当转义符

```python
# ❌ 千万别这么写
df = pd.read_csv("D:\AI应用工程师\news.csv")     # \A \n 都被当转义符
# ✅ 用 pathlib
df = pd.read_csv(Path(__file__).parent / "数据" / "news_示例.csv")
```

### ⭐ 坑2 · 编码：Excel 另存的 CSV 带 BOM

本练习的 `news_示例.csv` **真带 BOM**（开头 3 字节 `EF BB BF`，实测确认）：

```
用 encoding='utf-8' 读它 → 第一列名变成 '序号'（多了个隐形 BOM 字符）
用 encoding='utf-8-sig'   → 正常
```

pandas 2.x 默认已经能自动处理，但**你用标准库 `open()` / `csv` 读时会踩**。看到列名莫名多一个 `\ufeff`，就是编码选错了。

---

## 四、看：先摸清表的形状，再看内容

```python
df.shape      # (15, 4)          行数, 列数
df.columns    # Index(['序号', '日期', '新闻内容', '星期'], dtype='object')
df.head(3)    # 前 3 行【数据】
df.tail(2)    # 后 2 行【数据】
df.info()     # 每列：名字 / 类型 / 非空数量
df.dtypes     # 每列的数据类型
df.describe() # 数值列的统计摘要
```

### ⭐ 坑3 · `head()` 给的是**数据行**，不是表头

这是对应错题 **E37「f-string 里一个 `{}` 都没有」的同类**：

> **名字对了，取出来的东西不是你要的那个。**

`df.head(3)` 是「前 3 条新闻」，表头在 `df.columns` 里。

---

## 五、选：单列和多列的括号不一样（最容易混）

```python
df["星期"]              # 单列 → Series
df[["日期", "星期"]]      # 多列 → DataFrame
```

**多列必须用方括号套方括号。** 写 `df["日期", "星期"]` 会报 `KeyError`。

```python
df["星期"].shape           # (15,)      ← Series
df[["日期", "星期"]].shape  # (15, 2)   ← DataFrame
```

还要知道这两个（后面取行会用到）：

```python
df.iloc[0]        # 第 0 行 → Series
df.iloc[0, 1]     # 第 0 行、第 1 列的那个值 → '2026-11-14'
```

> ⚠️ `df["新闻内容"][0]` 现在（本机 pandas 2.2.2）**还能用，不报错也不警告**，
> 但这是**已废弃**的写法，未来版本会失效。**统一用 `df["新闻内容"].iloc[0]`。**
> ——「现在能用」不等于「可以这么写」，这类事在 Python 里特别多。

---

## 六、类型：三层结构，一次讲清

```python
df.dtypes
# 序号       int64
# 日期      object
# 新闻内容    object
# 星期      object
```

`object` = 「Python 层面的对象」，在 pandas 里通常就是 **字符串**。

### info() 的信息量比 dtypes 多一层

`df.info()` 给的是「每列有多少个**非空**值」：

```
 #   Column  Non-Null Count  Dtype
 0   序号      15 non-null     int64
 1   日期      15 non-null     object
 ...
```

### 空值总数：两个 `sum()` 不是一个意思

```python
df.isna().sum().sum()
#     ↑        ↑    ↑
#   判断缺失  沿列求和  再求和
```

| 步骤 | 返回 | 含义 |
|---|---|---|
| `df.isna()` | DataFrame | 15×4 的**布尔表**，缺失处是 True |
| `.sum()` | Series（4 个数） | 沿**列**求和 → 每列各有几个缺失 |
| `.sum()` | int（1 个数） | 把 4 个数加成 1 个 → 总缺失数 |

本数据实测 `= 0`（没有缺失）。

> **别用 `count()`**：那个是数**非空**的，方向正好反了。

### ⭐ 坑4 · dtype 对象 vs 纯字符串（要 `json.dumps` 时踩）

```python
dict(df.dtypes)            # {'序号': dtype('int64'), ...}  ← 装的是 dtype 对象
dict(df.dtypes.astype(str)) # {'序号': 'int64', ...}        ← 装的是纯字符串
```

两者比较时都能用（`dtype('int64') == 'int64'` → True），但：

```python
json.dumps(dict(df.dtypes))
# ❌ TypeError: Object of type Int64DType is not JSON serializable
json.dumps(dict(df.dtypes.astype(str)))
# ✅ '{"序号": "int64", ...}'
```

**要存成 JSON / 要发给前端 → 必须 `astype(str)`。**

---

## 七、筛选：pandas 里的 WHERE

（这节是 11-16 下午档的内容。SQL 的 `WHERE` 和这里是**同一件事**，明天晚上你会看到它们的对应关系。）

```python
多天 = pd.read_csv(数据目录 / "news_多天版.csv")

单条件 = 多天[多天["星期"] == "星期二"]
单条件.shape          # (2, 4)
list(单条件["序号"])  # [7, 8]
```

### ⭐ 坑5 · pandas 条件用 `&` `|`，**不是** Python 的 `and` `or`

```python
# ❌ 报错
多天[(多天["星期"] == "星期一") and (多天["序号"] > 5)]
# ValueError: The truth value of a Series is ambiguous.

# ✅ 正确
多天[(多天["星期"] == "星期一") & (多天["序号"] > 5)]
# → shape (2, 4), 序号 [6, 15]
```

**为什么？** `and` 是 Python 的**逻辑运算符**，它问「这个 Series 是真还是假」—— 而 Series 有 15 个元素，没有单一的「真假」，所以歧义。
`&` 是**逐元素**运算：左边算出一列 True/False，右边算出一列 True/False，然后逐行 AND。

**两边都要加括号** —— `&` 的优先级比 `==` 高，不加括号会先算错。

### ⭐ 坑6 · `str.contains` 默认是**正则**，不是字面量

```python
多天[多天["新闻内容"].str.contains("银行") | 多天["新闻内容"].str.contains("雨雪")]
# → 序号 [1, 4]

# 但换个关键词就出事：
多天[多天["新闻内容"].str.contains("1.")]              # 4 行  ← '.' 在正则里 = 任意字符
多天[多天["新闻内容"].str.contains("1.", regex=False)]  # 1 行  ← 真·字面量
```

`.` 匹配了「10 月」「120 人」「16 日」这些。

**要字面量就加 `regex=False`。** 这条和 11-14 re 正则那节是同一个坑的正反面：正则很强大，所以**默认值是正则这件事本身就危险**。

---

## 八、增删改列

```python
# 加【数值列】
加数值列 = 多天.copy()
加数值列["双倍序号"] = 加数值列["序号"] * 2
list(加数值列["双倍序号"])[:3]   # [2, 4, 6]

# 加【字符串列】
加字符串列 = 多天.copy()
加字符串列["标签"] = 加字符串列["星期"] + "-" + 加字符串列["序号"].astype(str)
list(加字符串列["标签"])[:3]     # ['星期六-1', '星期六-2', '星期六-3']

# 删列
删列 = 多天.drop(columns=["新闻内容"])
list(删列.columns)     # ['序号', '日期', '星期']

# 改列名
改名列 = 多天.rename(columns={"序号": "编号"})
list(改名列.columns)   # ['编号', '日期', '新闻内容', '星期']
```

### ⭐ 坑7 · 数字列 + 字符串列不能直接相加

```python
# ❌ TypeError: can only concatenate str (not "int") to str
加字符串列["标签"] = 加字符串列["星期"] + "-" + 加字符串列["序号"]

# ✅ 先把数字列转成字符串
加字符串列["标签"] = 加字符串列["星期"] + "-" + 加字符串列["序号"].astype(str)
```

### ⭐ 坑8 · 先筛选再改列要 `.copy()`

```python
子 = 多天[多天["序号"] > 5]
子["新列"] = 1        # ⚠️ SettingWithCopyWarning —— 你改的可能不是"你以为的那张表"
子 = 多天[多天["序号"] > 5].copy()   # ✅ 明确复制一份
```

---

## 九、⚠️ 五个**静默**出错的写法（不报错，但结果是错的）

这五个是本节最值钱的部分 —— 它们**不会报错**，你只会觉得"怎么结果不对"。

### ① `sort_values` 不接返回值 = 哑弹

```python
多天.sort_values(by="序号", ascending=False)      # ❌ 这一行等于没写
多天["序号"][:3]                                  # [1, 2, 3] 顺序没变！

结果 = 多天.sort_values(by="序号", ascending=False)  # ✅ 接住才生效
结果["序号"][:3]                                    # [15, 14, 13]
```

**pandas 的大部分「改」操作都返回新表，不接返回值 = 白写。** 这条已登记为错题 **E43**。

同类：`drop()`、`rename()`、`sort_values()`、`copy()`。

### ② `list(df)` 给的是**列名**，不是数据

```python
list(df)           # ['序号', '日期', '新闻内容', '星期']  ← 列名！
list(df.head(0))   # ['序号', '日期', '新闻内容', '星期']  ← 完全一样，head(0) 多余
list(df.columns)   # 同上，但这是标准写法
list(df["序号"])    # [1, 2, 3, ...]  ← 要【值】得用这个
```

**要哪列就 `df["列名"]`，要列表就外面套 `list()`。**

### ③ 全局 `df` 会被别的函数污染

```python
全局df = pd.read_csv(CSV路径)

def A_全局加列():
    全局df["污染列"] = 1
    return len(全局df.columns)

def B_另一个函数():
    df = 全局df        # 只是引用同一个对象
    return len(df.columns)

B_另一个函数()      # 4
A_全局加列()
B_另一个函数()      # 5  ← 被污染了
```

**每个函数自己 `read_csv`，别用全局的。** 好处：函数之间互不影响，改一个不影响另一个。

### ④ pandas 的自动类型推断是双刃剑

```python
df = pd.read_csv("数据.csv")
df["编号"][0]      # '007' 读进来变成 7 —— 前导零没了！
```

要保原样：`pd.read_csv("数据.csv", dtype={"编号": str})`。

### ⑤ `len(整列)` ≠ `len(筛选结果)`

```python
len(df["星期"])          # 15  ← 整列多长
len(筛选后的表)          # 2   ← 筛出来几条
```

题目问「有几条符合条件」，答的是**第二个**。这个我在批改时抓过一次。

---

## 十、今天真正要记住的 8 件事

1. **DataFrame = 表格，Series = 一列**；`df["列名"]` 拿 Series，`df[["列1","列2"]]` 拿 DataFrame
2. **路径用 pathlib**，别手写反斜杠字符串
3. **BOM** → 看到 `\ufeff` 就想到编码
4. **`head()` 是数据行，表头在 `columns`**
5. **`dtypes` 用 `astype(str)` 才能 json  dumps**
6. **条件用 `&` `|`，两边加括号**，不用 `and` `or`
7. **`str.contains` 默认正则**，要字面量加 `regex=False`
8. **返回新表的方法必须接返回值**（sort_values / drop / rename）

---

## 十一、自测题（不看上面，闭卷答）

1. `df[["日期", "星期"]]` 返回什么类型？shape 是多少？
2. `df["序号"][0]` 和 `df["序号"].iloc[0]` 有区别吗？为什么推荐后者？
3. `df.isna().sum()` 和 `df.isna().sum().sum()` 分别返回什么？
4. 为什么 `dict(df.dtypes)` 不能直接 `json.dumps`？
5. `多天[(多天["序号"] > 5) and (多天["星期"] == "星期一")]` 报什么错？错在哪？
6. `str.contains("10 月")` 和 `str.contains("10 月", regex=False)` 结果会一样吗？
7. `多天.sort_values(by="序号")` 写完不接返回值，表格顺序会变吗？
8. 题目问「星期二有几条」，`len(df["星期"])` 和正确答案是几？

---

## 十二、接下来做什么

**11-16 晚上：SQL `SELECT/WHERE`（0.5h）**

你会发现今晚的 SQL 和今天这两节**是同一件事的两套语言**：

| pandas（今天） | SQL（明天晚上） |
|---|---|
| `df[df["星期"] == "星期二"]` | `SELECT ... FROM 新闻 WHERE 星期 = '星期二'` |
| `df[(cond1) & (cond2)]` | `WHERE cond1 AND cond2` |
| `df["新闻内容"].str.contains("银行")` | `WHERE 新闻内容 LIKE '%银行%'` |
| `len(筛出来的表)` | `COUNT(*)` |

**今天你在 pandas 上栽的坑，明天在 SQL 里会以另一种形式再出现一次**（比如 SQL 里字符串要用单引号、`=` 不是 `==`）。

> 📎 **完整讲义在 `笔记/讲义/11-17_讲义_SQL_SELECT与WHERE.md`**（含 6 个实测出来的坑、pandas↔SQL 完整对照表）
> **可跑样例 `练习/_参考样例_SQL讲义.py`** —— 讲义里每个输出都能复现
> 练习在 `练习/11.17练习_SQL_SELECT与WHERE.py`

数据库已经建好了：`练习/数据/新闻库.sqlite`（表 `新闻`，15 行 4 列，和今天的数据同源）。

**11-18 上午：SQLite 实操② —— `GROUP BY` + `ORDER BY` + `LIMIT`**（今天没学的两样）

---

## 附：这份讲义的三个"我自己也写错了"

1. **讲义初稿里我写「`df["列"][0]` 会报错」** —— 实跑发现**本机 pandas 2.2.2 不报错也不警告**，
   只是官方废弃了。已改成如实表述。
2. **我手抄了 15 条新闻标题写进练习的期望值** —— 自检脚本比对数据库时发现**我抄的是编的**（只有前 5 条碰巧对上）。
   已改成**程序从数据库生成**。这条教训：**期望值永远不要手抄**。
3. **讲义里第一版写的 `json.dumps(dict(df.dtypes))` 说得太含糊** —— 实测确认它**真的会抛 TypeError**，
   不是"可能存不进去"。已改成确切结论。
