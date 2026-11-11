# API 数据落地练习（venv + requests + JSON + CSV）

**把数据从网上抓下来、解析成 Python 对象、再存成能反复用的本地文件** —— 6 个脚本，一条链路走通。

这是我学 Python 第三阶段（requests / API 调用）的练习项目。跟前几个作品最大的不同是：**它解决的不是「怎么算」，而是「怎么从外面拿数据、并且保证拿到的数据是对的」**。

> **为什么这一节重要**：作品①「课程问答 RAG 机器人」的 **ingest 层**干的就是这件事 ——
> 把外部资料抓下来、清洗好、存进本地知识库。这个项目是那条链路的**第一块砖**。

---

## 功能

- [x] **独立虚拟环境**：`.venv` 隔离，全局 405 个包 vs 抽屉 6 个包，同一台机器两个 requests 版本并存
- [x] **第一次 GET**：状态码 / 响应头 / 正文切片
- [x] **看清请求和响应长什么样**：用 httpbin 回声壁把请求原样照回来
- [x] **JSON 解析**：`resp.text`（字符串）→ `resp.json()`（字典）的类型差异
- [x] **错误处理**：先判状态码再解析 / `raise_for_status()` + try/except 双写法
- [x] **存成 JSON**：嵌套取值 → `json.dump` → **读回来核对**
- [x] **存成 CSV**：嵌套数据拍平成表格 → **Excel 双击打开不乱码**

---

## 快速开始

### 第 0 步：建虚拟环境（**第一次运行前必做**）

```bash
cd projects/api-demo

# 用完整路径建，不依赖 PATH 里的 python 是谁
D:\AAAA\python.exe -m venv .venv

# 激活（PowerShell）
.\.venv\Scripts\Activate.ps1

# ★ 关键对照实验：此刻 import requests 应该报「找不到」
python -c "import requests"
```

**期望看到**：`ModuleNotFoundError: No module named 'requests'`

> 为什么期待它报错？因为全局（Anaconda base）**已经装了 requests 2.32.3**。
> 你现在进了空抽屉，所以找不到 —— **看到这个报错，才说明 venv 真的起作用了**。

### 装依赖

```bash
python -m pip install -r requirements.txt
```

### 跑脚本（**必须用抽屉里的 python**）

```bash
# Windows
.\.venv\Scripts\python.exe 01_第一次GET.py

# 或者激活之后直接写 python
python 01_第一次GET.py
```

> ⚠️ **别用 `D:\AAAA\python.exe` 跑** —— 全局也装了 requests，代码照样跑通，
> 但你等于白建了抽屉，而且以后会遇到「我这儿能跑、别人那儿报错」。
> **命令里写哪个 python，就用哪个环境。**

---

## 6 个脚本在干什么

| 脚本 | 干什么 | 关键产出 |
|---|---|---|
| `01_第一次GET.py` | 请求百度，打印状态码 / Content-Type / 正文前 200 字 | 认识 response 对象的三个属性 |
| `02_第一次GET_httpbin.py` | 改打 httpbin「回声壁」 | **看清请求和响应的真实结构** |
| `03_解析JSON.py` | 解析 JSON，故意撞一次 404 | `text` vs `json()` 的类型差异 + 异常链 |
| `04_正确的错误处理.py` | 两种错误处理写法 | 先判状态码 / `raise_for_status()` |
| `05_存成JSON.py` | 抓 10 个用户 → 存 JSON → 读回核对 | 嵌套取值 + `json.dump` |
| `06_存成CSV.py` | 抓 15 条新闻 → 拍平成表格 → 存 CSV | 三个 CSV 落地的坑 |

---

## 真实运行输出

### 02 · 回声壁把你发出的请求原样照回来

```text
状态码： 200
正文前 500 字： {
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Host": "httpbin.org",
    "User-Agent": "python-requests/2.34.2"
  },
  "method": "GET",
  "origin": "<你的公网IP，已脱敏>",
  "url": "https://httpbin.org/get"
}

Content-Type： application/json
```

**三个必须看懂的地方**：

| 字段 | 说明 |
|---|---|
| `"method": "GET"` / `"url"` | 你发出去的请求 —— 对上了 |
| `"headers"` | **requests 自动加的**，你一个都没写 |
| `"User-Agent": "python-requests/2.34.2"` | ⚠️ **requests 默认不伪装**。真浏览器会发 `Mozilla/5.0 ...` 一大串，有些网站直接拒绝带 `python-requests` 的请求 |

> ⚠️ `"origin"` 是**你的公网 IP**，会被服务端看到 —— 贴输出到网上前记得脱敏。

### 03 · `text` 和 `json()` 是两个东西

```text
data 的类型： <class 'dict'>
请求方法： GET
请求头里的 Host： httpbin.org
args 的类型： <class 'dict'> 内容： {}

========== 下面故意踩一个坑 ==========
状态码： 404
❌ 解析失败，异常类型： JSONDecodeError
   错误信息： Expecting value: line 1 column 1 (char 0)
```

### 05 · 存成 JSON 并读回核对

```text
数据类型： <class 'list'>
条数： 10
已保存到： 输出\users.json
读回的类型： <class 'list'>
读回的条数： 10
第 1 个人的姓名： Leanne Graham
第 1 个人的城市： Gwenborough
第 1 个人的公司： Romaguera-Crona
```

### 06 · 拍平成 CSV

```text
data 里有哪些字段： ['date', 'news', 'cover', 'tip', 'image', 'link', 'created',
 'created_at', 'updated', 'updated_at', 'day_of_week', 'lunar_date',
 'api_updated', 'api_updated_at']
新闻条数： 15
已保存到： 输出\news.csv
第0行（4列）： ['序号', '日期', '新闻内容', '星期']
第1行（4列）： ['1', '2026-11-11', '前 10 个月我国货物贸易进出口 44.81 万亿元，同比增长 20%...', '星期三']
第2行（4列）： ['2', '2026-11-11', '数据显示：我国算力总规模已达到 310 万 PFLOPS，位居世界第二', '星期三']
```

> **注意「读回来核对」这一步不能省** —— 只写不验，文件坏了你也不知道。
> 每一行都得是 4 列，行数也得对得上。

---

## 技术点

### 1. venv 隔离：到底隔的是什么

**它不是虚拟机，就是一个普通目录 + 一套独立的包仓库。**

```
.venv\
    Scripts\              ← python.exe、pip.exe、Activate.ps1
    Lib\site-packages\    ← 装进来的包放这（空的时候几乎是空的）
    pyvenv.cfg            ← 记着「我的母体解释器是 D:\AAAA\python.exe」
```

隔离靠两件事：

| 机制 | 干什么 |
|---|---|
| `pyvenv.cfg` 里的 `include-system-site-packages = false` | **隔离总开关** —— 抽屉没权限去看全局的包 |
| 激活时把 `Scripts` 插到 PATH 最前面 | 让 `python` 命令先命中抽屉里那个副本 |

**本机实测对比**：

| | 全局（Anaconda base） | 抽屉（`.venv`） |
|---|---|---|
| 包的个数 | **405 个**（`pip freeze` 口径） | **6 个** |
| requests 版本 | **2.32.3** | **2.34.2** |
| 体积 | 几百 MB | **14 MB** |

**两个版本同时存在、互不干扰。** 这就是为什么必须有 venv：没有它，这两个版本**只能留一个**，先装的被后装的顶掉，旧项目当场崩。

**⚠️ 一个反直觉的事实**：venv **只隔离第三方包**（`site-packages`），**标准库（json / os / sys / re…）还是共用母体的**。

证据就藏在 traceback 里 —— 同一个报错里两条路径同时出现：

```text
File "D:\AAAA\Lib\json\__init__.py"                            ← 全局母体的标准库
File "...\api-demo\.venv\Lib\site-packages\requests\models.py"  ← 抽屉里的第三方包
```

**「激活」不是隔离的必需品** —— 隔离是 venv **本身**的属性，激活只是让你能直接敲 `python` 而不用打一长串路径。工程上更推荐不激活，直接用 `.\.venv\Scripts\python.exe`，谁用都一清二楚。

### 2. `requests` 是什么

**一个第三方库，唯一作用：让 Python 能上网访问网址、把内容拿回来。** 没有它，Python 程序**完全不能联网**。

| 代码 | 意思 |
|---|---|
| `resp = requests.get(网址)` | 「请求」发出去，「响应」收回来，收回来这个整体叫 `resp` |
| `resp.status_code` | 状态码 → 200 成功 / 404 没有 / 500 服务器崩了 |
| `resp.headers` | 响应头 → 像字典，用 `.get("Content-Type")` 取 |
| `resp.text` | 正文 → 一大坨字符串 |
| `resp.text[:200]` | 切片，取前 200 个字符（跟 `列表[:5]` 一个道理） |

### 3. `text` vs `json()`：一个是字符串，一个是对象

```
type(resp.text)        = <class 'str'>    ← 只是「长得像 JSON 的字符串」
resp.text[0]           = '{'              ← 它的第一个字符是花括号
type(resp.json())      = <class 'dict'>   ← 这才是真正的字典
resp.json()["method"]  = GET              ← 能用「键」取值了
```

**关键**：`resp.text` 拿到的是一大坨文本，**没法**用 `data["method"]` 取键 —— 因为它本质是字符串。

`resp.json()` 干的事：**把这坨文本翻译成真正的 Python 对象**（dict / list / 数字 / 字符串）。

### 4. JSON 存储：`json` 模块的四对函数

| 函数 | 干什么 | 去哪 |
|---|---|---|
| `json.loads(字符串)` | JSON **文本** → Python 对象 | 内存里 |
| `json.dumps(对象)` | Python 对象 → JSON **字符串** | 内存里 |
| `json.load(文件对象)` | JSON 文件 → Python 对象 | 文件 → 内存 |
| `json.dump(对象, 文件对象)` | Python 对象 → JSON 文件 | 内存 → 文件 |

**规律**：带 `s` 的在内存里转换，**不带 `s` 的直接读写文件**。

写文件时两个关键参数：

```python
json.dump(data, f, ensure_ascii=False, indent=2)
                     ↑              ↑
                 中文不转义      缩进 2 格，人能看
```

### 5. CSV 落地：三个参数缺一不可

```python
with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["序号", "日期", "新闻内容", "星期"])   # 表头
    writer.writerows(rows)                                 # 写所有数据行
```

| 参数 | 干什么 | 不写会怎样 |
|---|---|---|
| `encoding="utf-8-sig"` | 加 BOM 头 | **Excel 双击打开中文乱码**（Python 读却完全正常） |
| `newline=""` | 关闭行分隔符转换 | **Windows 上每行之间多出空行** |
| `csv.writer` | 按逗号分隔写，自动处理引号转义 | 字段里有逗号就串列 |

---

## 我踩过的坑（这里最值钱）

### 坑 1：venv 建了但跑代码时又绕回全局 —— **等于白建**

```text
D:\AAAA\python.exe 05_存成JSON.py          ← 全局！
.\.venv\Scripts\python.exe 05_存成JSON.py  ← 抽屉（该用这个）
```

**代码照样跑通了**（全局也装了 requests），但这等于**整个对照实验白做了一半**。

**教训**：**命令里写哪个 python，就用哪个环境 —— 隔离只在你明确指定时才生效。**

### 坑 2：404 → JSONDecodeError，**真正的原因被藏起来了**

```
状态码 = 404   Content-Type = text/html; charset=utf-8   正文长度 = 0
直接 .json() 报错 -> JSONDecodeError : Expecting value: line 1 column 1 (char 0)
```

**为什么**：404 的返回是 **HTML（而且正文是空的）**，不是 JSON。你不去看状态码就直接 `.json()` → 当场炸。

**这个坑非常高频**：「接口调不通 → 报错 JSONDecodeError → 但真正的原因只是 404」。

**正确顺序永远是：先看 `status_code`，确认 200 了再 `.json()`。**

### 坑 3：traceback 里为什么有**两段**异常

```text
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
        ↑ 原始错误：标准库 json 解析失败
        ↓ "During handling of the above exception, another exception occurred"
requests.exceptions.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
        ↑ requests 接住后重新包装成自己的异常再抛（好处：消息里带上了是哪个 URL 出错）
```

那句英文的意思是：「处理上一个异常的过程中，又发生了另一个异常」。

**实跑结论**：`requests.exceptions.JSONDecodeError` **是** `json.JSONDecodeError` 的**子类** → 所以你写 `except json.JSONDecodeError` 一样能抓住它。

### 坑 4：`timeout` 不写，程序会**永久挂在那里**

```python
requests.get.__defaults__          # = (None,)
```

`None` = **永不超时**。对方服务器卡住 → 你的程序不报错、不结束，就那么挂着。

**所有网络请求都必须写 `timeout=10`。**

### 坑 5：`newline=""` **只能加在写的那一侧**

我一开始以为读侧也要加 —— **受控实验跑完才发现读侧加不加都一样**。

实测矩阵（写侧决定文件干不干净）：

| 写侧 | 文件含 `CR CR LF`？ | 读回每行列数 |
|---|---|---|
| 有 `newline=""` | **False** | `[4, 4]` ✅ |
| 无 `newline=""` | **True** | `[4, 0, 4, 0]` ❌ 多出 0 列空行 |

**原因**：`csv.writer` 自己会在每行末尾写 `\r\n`。而 Windows 的文本层看到 `\n` 就自动补一个 `\r` → 文件里变成 `\r\r\n` → 读回来就是多出一行空。

### 坑 6：`ensure_ascii=False` 在**英文数据上测不出来**

我一开始用 jsonplaceholder（全英文）测，开不开参数**输出完全一样** —— 差点以为这参数没用。

**其实是数据里根本没中文，坑显不出来。**

换成 60s 的全中文接口，坑立刻现形。

**教训**：**同一个参数，必须拿能显形的数据去测。** 测出来「没区别」时，先怀疑是**测试数据不对**，不是怀疑参数没用。

### 坑 7：键名写错**不报错**，只会悄悄返回兜底值

我给某个接口写代码时用了 `book.get("author", ["未知作者"])` —— 结果**每一行的作者列都是「未知作者」**，而且**没有任何报错**。

因为那个接口真实的键叫 **`author_name`**，不叫 `author`。

**查法**（写代码前先做这一步）：

```python
print(list(book.keys()))     # 打印接口真实的所有键名
```

**这是最难查的一类 bug** —— 能跑、能出结果，只是结果是错的。

### 坑 8：`utf-8-sig` vs `utf-8`：**Python 说没问题，Excel 说有问题**

用 BOM 嗅探模拟 Excel 双击（先看有没有 BOM，没有就按本地 ANSI/GBK 猜）：

```text
utf-8-sig → 嗅到 BOM → 按 UTF-8 解码 → '序号,日期,新闻内容,星期'  ✅
utf-8    → 无 BOM      → 按 GBK 猜   → '搴忓彿,鏃ユ湡,鏂伴椈鍐呭'   ❌ 乱码
```

**字节级证据**：`utf-8-sig` 开头多 3 个字节 `EF BB BF`（BOM）。Excel 靠它认出编码；纯 `utf-8` 没有 BOM，Excel 就按本地 ANSI 猜 → 猜错就乱码。

**但 Python 读回来两种都对** —— 因为 Python 明确知道自己用的什么编码。

**这就是「静默错误」的完美案例**：同一个文件，Python 说没问题，Excel 说有问题，而**你的代码从头到尾没报错**。

---

## 静默错误的三种形态（这节最该记住）

| 形态 | 表现 | 为什么难发现 |
|---|---|---|
| **键名写错** | 取不到值 → 悄悄返回兜底值 | 不报错，只是结果是错的 |
| **Python 正常 / Excel 乱码** | 同一文件，两个环境两种结论 | 取决于谁来读 |
| **`ensure_ascii` 在英文数据上失效** | 参数看起来没用 | 测试数据没让它显形 |

**共同的破法只有一个**：**先确认「这个坑在什么条件下才会显形」，再挑能让它显形的数据去测。**

---

## 已知限制

### ⚠️ ① 依赖外部 API，本项目**不保证一直能跑**

`httpbin.org` / `jsonplaceholder.typicode.com` / `60s.viki.moe` 都是**第三方免费接口**，它们可能改接口、限流或下线。

**跑不起来先看这个**，别急着自己改代码。

### ⚠️ ② 没做重试和退避

真实工程里应该：失败后等一下再重试、连着失败几次就放弃。现在是**一次失败就抛异常**。

### ⚠️ ③ 没有写单元测试

6 个脚本都是**手动跑 + 肉眼核对**。没有 `pytest`、没有 `assert` —— 这是一个**真实的缺口**，不是风格问题。

### ⚠️ ④ `输出/` 不进版本库

`输出/` 里是每次运行才生成的数据（内容会变），所以加进了 `.gitignore`。
**代码进仓库，运行数据不进** —— 但这也意味着 clone 下来要先跑一遍才有数据。

### ⚠️ ⑤ `requirements.txt` 里有个练手包的残留

`tabulate==0.10.0` 是我拿它练 `pip install / uninstall` 用的，已经卸载了但清单是**快照**、没刷新。

```bash
# 重新生成一份干净的
python -m pip freeze > requirements.txt
```

---

## 文件说明

```
projects/api-demo/
├── .venv/                    ← 虚拟环境（自动生成，已被 .gitignore 忽略）
├── 01_第一次GET.py           ← 第一次请求：状态码 / 响应头 / 正文切片
├── 02_第一次GET_httpbin.py   ← 回声壁：看清请求与响应的结构
├── 03_解析JSON.py            ← text vs json()，故意撞一次 404
├── 04_正确的错误处理.py        ← 两种错误处理写法
├── 05_存成JSON.py            ← 嵌套取值 → 存 JSON → 读回核对
├── 06_存成CSV.py             ← 拍平成表格 → 存 CSV → 读回核对
├── requirements.txt          ← 依赖清单（pip freeze 生成）
├── README.md                 ← 就是这个文件
└── 输出/                      ← 运行时数据（已 gitignore）
    ├── users.json
    └── news.csv
```

---

## 更新记录

| 日期 | 内容 |
|---|---|
| 2026-11-11 | 项目建立。上午一次做完 4 环：venv + pip → requests + 第一次 GET → 解析 JSON + 错误处理 → 调公开 API + 存文件。踩坑 8 个，全部实跑复现（CSV 三坑做了正反双向实验；`newline` 做了 2×2 组合矩阵）。补完 03 让它接住异常、不再直接崩 |
