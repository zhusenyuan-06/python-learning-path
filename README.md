# Python 学习路径 · 从零到 AI 应用工程师

> 一个民办本科大三学生的 Python 自学记录。
> 从 2026-09-28 的 `print("hello")` 开始，到能独立写出完整项目。

---

## 这是什么

这是我学习 Python 的过程代码和笔记。**不是教程，是学习轨迹**——包含改对的地方，也包含改错的地方。

### 学习方式

- **不复制粘贴**：每个项目都从空文件手写
- **写完必跑**：不靠"看起来对"，靠输出说话
- **错题追踪**：所有踩过的坑记录在 `笔记/错题追踪.md`，每周复习直到不再犯
- **静默错误优先**：能跑但结果是错的错，比会报错的错更值得警惕

---

## 目录结构

```
pythonProject/
├── projects/                    # ★ 作品集（HR 点开就看这里）
│   └── contact-book/            # 作品 1：通讯录 CLI
│       ├── contact_book.py      # 主程序（5 个函数封装）
│       ├── README.md            # 作品说明
│       └── requirements.txt     # 依赖说明
├── 练习/                        # 我写的代码，按日期/主题命名
│   ├── 10.8陪练.py ~ 10.27练习.py   # 每日练习（时间顺序）
│   ├── 10.27练习_模块.py             # import 4 种写法 + 观察表
│   ├── 变量.py / 类型.py / 奇偶数.py    # 基础
│   ├── 函数练习.py / 匿名函数.py / 高阶函数.py
│   ├── 两数之和.py / 两数之和——重构.py   # 重构前后对照
│   ├── 待办工具.py / 猜数字小游戏___重构.py
│   ├── 词频.py / 词频统计器进阶版.py
│   ├── BMI练习.py / 灵活参数.py / 默认参数 & 关键字参数.py
│   └── 文本.txt / test.txt      # 上面两个词频脚本的输入数据
├── 教学/                        # 讲师内容（概念讲解 + 可运行示例）
│   ├── 标准库1_json.py          # json.dumps / json.loads
│   ├── 标准库2_csv.py           # csv.reader / csv.writer
│   ├── 标准库3_os_path.py       # path.join / dirname / basename / exists
│   ├── ensure_ascii对比.py      # 常见坑：中文变 \uXXXX
│   └── 配送工具.py              # 被练习 import 的模块
├── 参考材料/                    # 讲义 / 探针脚本 / 答案（要查才翻）
│   ├── 模块与导入_讲义.py        # 5 站正式讲义
│   ├── 模块本质探针.py          # 模块是什么
│   ├── 探索C_干净对照.py         # import 报错时机的对照实验
│   ├── 谁导入了我.py / main守卫演示.py  # __name__ 的两种取值
│   ├── 10.27练习_探针.py        # 参数分流 X 光片
│   ├── 模块与导入_3问答案.py     # 三层架构 Q&A
│   └── 标准库1_json_作业答案.py
├── 小项目_多模块demo/           # 完整项目示例（三层架构）
│   ├── main.py                  # 入口层：只组装
│   ├── config.py                # 配置层：常量 + 路径
│   ├── business.py              # 业务层：业务规则
│   ├── utils/helpers.py         # 工具层：与业务无关
│   └── data/菜单.csv            # 数据
├── 笔记/                        # 学习笔记 + 追踪器
│   ├── 错题追踪器.py / .json / .md      # 错题追踪（每周四复习）
│   ├── 工具链坑.py / .json / .md        # 非 Python 的坑
│   ├── 周复盘_2026-W44.md               # 本周复盘
│   ├── 学习总结_2026-10-27_模块与导入.md  # 每日学习总结
│   ├── 资产盘点_2026-10-27.md           # 全部资产盘点
│   ├── 能力缺口清单.md / JD能力缺口登记_2026-10-27.md
│   └── _自检脚本/                        # 校验与自动化脚本
├── 求职资产快照/                 # 技能清单的 git 版本（保险层）
├── push.sh / save_token.sh     # git 推送辅助脚本（本地用，已 gitignore）
└── .gitignore
```

> 📌 **目录约定**：`练习/` 是我写的、`教学/` 是学的、`参考材料/` 是查阅的、`projects/` 是能拿出手的。

---

## 作品

| 项目 | 说明 | 技术点 |
|---|---|---|
| **通讯录 CLI** ⭐ | 命令行版通讯录，增删改查 + 统计未填邮箱 + 双层遍历展示 | dict 套 dict、函数封装、安全查询 .get()、防覆盖 |
| **多模块配送单生成器** ⭐ | 完整项目结构：入口 / 配置 / 业务 / 工具四层分离，csv 读数据 → 算账 → 校验 → 出表格 | 模块拆分、跨文件 import、`__name__` 入口守卫、csv 读写、os.path 路径、f-string |
| **错题追踪器** | 命令行工具，管理自己的错题池。每周四自动出复习卷，连续答对 2 次才算掌握，再犯门槛 +1 | dict 嵌套、JSON 读写、CLI 参数、状态机 |
| **工具链坑追踪器** | 记录非 Python 的坑（git 配置 / 网络排障 / Windows 环境），踩一次计数+1 自动排序 | JSON 读写、CLI 参数、Markdown 渲染 |
| **词频统计** | 读文本 → 清洗 → 计数 → 排序 → 取 TOP N | 文件读写、字典计数、排序、推导式 |
| **待办工具** | 命令行待办事项 | 函数拆分、数据持久化 |

---

## 我踩过的坑（精选）

这些是真实犯过的错，完整的在 `笔记/错题追踪.md`。

### 静默错误：代码能跑，但结果是错的

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

### 变量角色混用（同一个病根犯了 4 次）

```python
# ❌ 入参被覆盖成累加器
def sum_list(nums): nums = 0

# ❌ 字典被覆盖成整数
for w, counts in t: print(w, counts)   # AttributeError

# ✅ 一个名字从头到尾只干一件事
def sum_list(nums):
    total = 0
    for i in nums:
        total += i
    return total
```

### key= 传函数本身，不带括号

```python
sorted(d, key=pinjun)      # ✅
sorted(d, key=pinjun())    # ❌ TypeError
```

---

## 技术栈

- Python 3.12
- 标准库为主：`dict` / `list` / `set` / `tuple`、`json`、`csv`、`pathlib`、`re`
- 工具：PyCharm、Git

---

## 更新记录

| 日期 | 内容 |
|---|---|
| 2026-09-28 | 环境安装、第一个程序 |
| 2026-10-17 | 函数、作用域、`sum_list` 重构 |
| 2026-10-19 | dict 增删改查、嵌套 dict、双层遍历 |
| 2026-10-20 | set 运算、三大容器方法、选型三问 |
| 2026-10-21 | 词频统计（读文件→dict 计数）、通讯录（dict of dict） |
| 2026-10-22 | 大复习 + 错题追踪系统 + 合并排序练习 |
| 2026-10-27 | 通讯录整理成独立作品（`projects/contact-book/`）+ 补 README + 登记 JD 能力缺口 |
| 2026-10-27 晚 | `*args`/`**kwargs` 练习 + 模块与导入（5 站）+ 多模块 demo 项目 + 目录重组 |

---

## 联系

持续更新中。
