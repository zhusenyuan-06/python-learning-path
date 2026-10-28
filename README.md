# Python 学习路径 · 从零到 AI 应用工程师

<div align="center">

**朱森源** · 民办本科大三 · 求职方向：AI 应用工程师

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/GitHub-100%25-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/zhusenyuan-06/python-learning-path)
[![进度](https://img.shields.io/badge/学习进度-第%205%20周%20%2F%2016%20周-97CA00?style=flat-square)](#成长轨迹)

</div>

---

## 我是谁

民办本科大三学生，**从 `print("hello")` 开始学 Python**，目标是把 AI 应用工程师的岗位拿下。

我不写"认真负责"这种空话。能证明的是：

- **5 个可运行项目** —— 不是片段，是能 `python xxx.py` 直接跑起来的
- **22 条错题追踪记录** —— 自己写的系统，每周四自动出卷，连对 2 次才算掌握
- **12 条工具链坑** —— git / 网络 / Windows 环境的坑，踩一次记一次
- **真实交付经验** —— 幼儿园菜品汇总工具已打包交付园方使用（**数据已脱敏**）

<div align="center">
  <img src="截图/05-幼儿园菜汇总.png" width="820" alt="幼儿园菜品配送汇总工具运行效果">
  <br><sub>作品 1 · 幼儿园菜品配送汇总工具（已交付园方使用 —— 344 种食材自动归入 9 大类，逐行重算并对账）<br>图由交付的 output/汇总表 Excel 直接读出，不是手绘示意图</sub>
</div>

---

## 作品速览

> 找工作的看这一节就够了。想看我怎么学的，往下滚到 [成长轨迹](#成长轨迹)。

| # | 项目 | 说明 | 技术点 |
|---|---|---|---|
| 1 | **[幼儿园菜品配送汇总工具](projects/幼儿园菜汇总工具/README.md)** ⭐ | **已交付园方使用的真实项目**（数据已脱敏）。把每月送货单丢进去，自动按 9 大类汇总成带图表的 Excel：344 种食材自动归类、逐行重算金额并与表内小计对账、多供应商分表 + 全园合并 | pandas 数据清洗、openpyxl 读写、YAML 配置化规则、Excel 原生图表、公式缓存值处理、多种表格格式兼容、PyInstaller 打包 |
| 2 | **[多模块配送单生成器](小项目_多模块demo/README.md)** ⭐ | 完整项目结构：入口 / 配置 / 业务 / 工具四层分离，CSV 读数据 → 算账 → 校验 → 出表格。改一个参数全局生效 | 模块拆分、跨文件 import、`__name__` 入口守卫、csv 读写、os.path 路径、f-string |
| 3 | **[通讯录 CLI](projects/contact-book/README.md)** ⭐ | 命令行版通讯录，增删改查 + 统计未填邮箱 + 双层遍历展示 | dict 套 dict、函数封装、安全查询 `.get()`、防覆盖 |
| 4 | **[错题追踪器](笔记/错题追踪器_README.md)** | 管理自己的错题池。每周四自动出复习卷，连续答对 2 次才退场，再犯门槛 +1。已积累 22 题 / 37 次犯错 | dict 嵌套、JSON 读写、CLI 参数、状态机、优先级排序 |
| 5 | **[工具链坑追踪器](笔记/工具链坑_README.md)** | 记录非 Python 的坑（git 配置 / 网络排障 / Windows 环境），踩一次计数 +1 自动排序。已积累 12 条 / 14 次踩坑 | JSON 读写、CLI 参数、Markdown 渲染、标签系统 |

> 五个项目**都有独立 README**（链接直达），里面是真实运行输出、技术点原因和踩坑复盘。

### 练习片段（不是项目，不计入上面的数量）

这三个是**学习时的练习文件**，不是能拿出手的项目 —— 所以我单独列出来，不混进项目数里：

| 文件 | 行数 | 是什么 |
|---|---|---|
| [`练习/词频统计器进阶版.py`](练习/词频统计器进阶版.py) | 32 行 | 教学骨架：读文件 → 切词 → 字典计数 → 排序取 TOP N。文件里带着「核心逻辑由你填」和参考答案 |
| [`练习/词频.py`](练习/词频.py) | 8 行 | 最小的词频演示，就是 `d.get(w, 0) + 1` 那一句 |
| [`练习/待办工具.py`](练习/待办工具.py) | 63 行 | 待办 CLI 骨架：add / list / done / quit |

> 它们记录的是**我学到哪一步了**，不是**我能交付什么**。

<div align="center">
  <img src="截图/04-多模块项目结构.png" width="820" alt="多模块项目结构">
  <br><sub>作品 2 · 多模块配送单生成器 —— 四层结构：依赖单向不循环，改一个文件不会碰坏其它模块</sub>
</div>

### 怎么跑

```bash
# 作品 1：幼儿园菜品配送汇总工具（数据已脱敏，原样可跑）
cd projects/幼儿园菜汇总工具
python src/run.py check      # 只读取 + 对账，不出汇总表
python src/run.py report     # 出正式汇总表到 output/

# 作品 2：多模块配送单生成器
cd 小项目_多模块demo
python main.py

# 作品 3：通讯录 CLI
cd projects/contact-book
python contact_book.py

# 作品 4：错题追踪器
cd 笔记
python 错题追踪器.py stats        # 看池子里还剩几题
python 错题追踪器.py plan 6        # 生成本周复习卷

# 作品 5：工具链坑追踪器
cd 笔记
python 工具链坑.py ls
```

---

## 成长轨迹

> 这一节给面试官看 —— **我学了什么、怎么学的、踩过什么坑**。

### 学习方式

| 原则 | 具体做法 |
|---|---|
| **不复制粘贴** | 每个项目从空文件手写 |
| **写完必跑** | 不靠"看起来对"，靠输出说话 |
| **错题追踪** | 所有踩过的坑记进系统，每周四复习直到不再犯 |
| **静默错误优先** | 能跑但结果是错的错，比会报错的错更值得警惕 |

### 学习路线（16 周 · 当前第 5 周）

| 周次 | 阶段 | 内容 | 状态 |
|---|---|---|---|
| 1-2 | 阶段 1 | 变量 / 类型 / 运算符 / 字符串 / 分支 / 循环 | ✅ |
| 3-4 | 阶段 1 | 函数 / 作用域 / 字典 / 列表 / 集合 / 推导式 | ✅ |
| 5 | 阶段 1 | 文件读写 / JSON / 异常 / **`*args` `**kwargs`** / **模块与导入** | 🔄 进行中 |
| 6-8 | 阶段 1 | csv / json / 异常 / 重命名 / 词频作品化 | ⬜ |
| 9-12 | 阶段 2 | requests / pandas / PDF 解析 / SQLite / API 调用 | ⬜ |
| 13-16 | 阶段 3 | RAG 原理 / LangChain 认知 / FastAPI / Claude Code 协作 | ⬜ |

> 16 周计划全部落在一张表里，**每天做什么、做到没有，逐格可查**。

### 我踩过的坑（精选）

完整的在 [`笔记/错题追踪.md`](笔记/错题追踪.md)（22 条，每周四抽考）。

#### 静默错误：代码能跑，但结果是错的

```python
# ❌ 缺 .strip() —— "python." 和 "python" 被当成两个词
w = w.lower()

# ✅
w = w.lower().strip(".,!?")
```

```python
# ❌ 缺 reverse=True —— 排出来的"前 N 名"其实是最后 N 名
after = sorted(counts.items(), key=lambda x: x[1])

# ✅
after = sorted(counts.items(), key=lambda x: x[1], reverse=True)
```

```python
# ❌ if 缺 return —— 提示了"未覆盖"，照样覆盖了
if 姓名 in contacts:
    print("已存在，未覆盖")
contacts[姓名] = {...}

# ✅ 有 return 就停在那
if 姓名 in contacts:
    return "已存在，未覆盖"
```

#### 变量角色混用（同一个病根犯了 4 次）

```python
# ❌ 入参被覆盖成累加器
def sum_list(nums): nums = 0

# ✅ 一个名字从头到尾只干一件事
def sum_list(nums):
    total = 0
    for i in nums:
        total += i
    return total
```

#### key= 传函数本身，不带括号

```python
sorted(d, key=pinjun)      # ✅
sorted(d, key=pinjun())    # ❌ TypeError
```

#### 中文变乱码：json.dumps 忘写 ensure_ascii=False

```python
# ❌ 中文变成 \u83dc\u540d
s = json.dumps(订单)

# ✅ 跟中文打交道，dumps 永远写死 ensure_ascii=False
s = json.dumps(订单, ensure_ascii=False)
```

---

## 目录结构

```
pythonProject/
├── projects/                    # ★ 作品集（HR 点开就看这里）
│   ├── 幼儿园菜汇总工具/         # 作品 1：已交付园方的菜品配送汇总（数据已脱敏）
│   │   ├── src/                 # 7 个脚本：读取 / 归类 / 出表 / 造样本
│   │   ├── config/              # categories.yaml（9 大类规则）+ mapping.xlsx（344 种食材）
│   │   ├── input/               # 脱敏后的原始送货单
│   │   ├── output/              # 生成的汇总表
│   │   └── data/月度台账.csv      # 趋势图数据源
│   └── contact-book/            # 作品 3：通讯录 CLI
├── 小项目_多模块demo/           # 作品 2：四层架构示例
│   ├── README.md                # 作品说明：结构图 + 真实输出 + 踩坑
│   ├── main.py                  # 入口层：只组装
│   ├── config.py                # 配置层：常量 + 路径
│   ├── business.py              # 业务层：业务规则
│   ├── utils/helpers.py         # 工具层：与业务无关
│   └── data/菜单.csv            # 数据
├── 练习/                        # 我写的代码，按日期/主题命名
├── 教学/                        # 概念讲解 + 可运行示例
├── 参考材料/                    # 讲义 / 探针脚本 / 答案
├── 笔记/                        # 学习笔记 + 两个追踪器
│   ├── 错题追踪器.py / .json / .md
│   ├── 错题追踪器_README.md     # 作品 4 说明
│   ├── 工具链坑.py / .json / .md
│   ├── 工具链坑_README.md        # 作品 5 说明
│   ├── 周复盘_*.md
│   └── 学习总结_*.md
├── 截图/                        # README 用图
└── push*.sh                     # git 推送辅助（本地，不上传）
```

> 目录约定：`练习/` 是我写的、`教学/` 是学的、`参考材料/` 是查阅的、`projects/` 是能拿出手的。

---

## 技术栈

- **Python 3.12** —— 基础语法、函数、容器、文件/JSON/CSV 读写、模块化设计
- **标准库** —— `dict` / `list` / `set` / `tuple`、`json`、`csv`、`os.path`、`datetime`
- **工程化** —— Git / GitHub（日常提交）、PyCharm、venv + PyInstaller 打包交付
- **进行中** —— requests、pandas、SQLite、FastAPI、RAG 检索增强

---

## 更新记录

| 日期 | 内容 |
|---|---|
| 2026-09-28 | 环境安装、第一个程序 |
| 2026-10-17 | 函数、作用域、`sum_list` 重构 |
| 2026-10-19 | dict 增删改查、嵌套 dict、双层遍历 |
| 2026-10-20 | set 运算、三大容器方法、选型三问 |
| 2026-10-21 | 词频统计、通讯录（dict of dict） |
| 2026-10-22 | 大复习 + 错题追踪系统 + 合并排序练习 |
| 2026-10-27 | 通讯录作品化 + JD 能力缺口登记 + `*args`/`**kwargs` + 模块与导入 + 目录重组 |
| 2026-10-28 | README 改造成作品集主页（A+B 合一）+ 终端截图生成 |
| 2026-10-28 | **作品 1「幼儿园菜品配送汇总工具」脱敏后并入仓库**（344 种食材→9 大类、逐行重算与对账、多供应商分表 + 全园合并、Excel 原生图表） |
| 2026-10-28 | **补齐作品 2 / 4 / 5 的独立 README**（真实运行输出 + 技术点原因 + 踩坑复盘）｜作品速览改为「5 个可运行项目」，词频统计 / 待办工具诚实降级为「练习片段」 |
| 2026-10-28 | **清理仿真终端截图**：删掉 3 张「模拟终端」图及其生成脚本（图与 README 文字对不上，且 macOS 窗口框与 Windows 环境矛盾），改为真实架构图 + 由交付 Excel 直接读出的图表 |

---

## 联系

持续更新中 · 欢迎交流技术

[GitHub](https://github.com/zhusenyuan-06/python-learning-path) · 邮箱见 GitHub 主页
