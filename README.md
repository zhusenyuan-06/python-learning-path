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
├── projects/
│   └── contact-book/            # ★ 作品 1：通讯录 CLI
│       ├── contact_book.py      # 主程序（5 个函数封装）
│       ├── README.md            # 作品说明
│       └── requirements.txt     # 依赖说明
├── 10.xx练习.py          # 每日练习，按日期命名
├── 待办工具.py            # 小项目
├── 猜数字小游戏___重构.py
├── 文本.txt              # 词频统计的输入数据
├── 笔记/
│   ├── 第1-4周总复习清单.md      # 知识点 + 我的坑
│   ├── 错题追踪.md                # 每周复习池（自动生成）
│   ├── 错题追踪.json              # 错题数据源
│   ├── 错题追踪器.py              # 追踪器程序
│   ├── 周四大复习_使用说明.md      # 每周四的复习流程
│   ├── 求职路线评估_诚实版.md      # 对自己学习计划的评估
│   ├── JD能力缺口登记_2026-10-27.md # 能力缺口对照表
│   └── 周复盘模板_2026-W44.md     # 每周复盘模板
└── .gitignore
```

---

## 作品

| 项目 | 说明 | 技术点 |
|---|---|---|
| **通讯录 CLI** ⭐ | 命令行版通讯录，增删改查 + 统计未填邮箱 + 双层遍历展示 | dict 套 dict、函数封装、安全查询 .get()、防覆盖 |
| **错题追踪器** | 命令行工具，管理自己的错题池。每周四自动出复习卷，连续答对 2 次才算掌握，再犯门槛 +1 | dict 嵌套、JSON 读写、CLI 参数、状态机 |
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

---

## 联系

持续更新中。
