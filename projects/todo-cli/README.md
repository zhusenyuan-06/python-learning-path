# 待办工具 CLI

命令行版待办工具，支持添加任务、查看列表、标记完成，任务存在本地 JSON 文件里 —— 程序关了再开，任务还在。

我学完「函数封装 + 文件读写」后写的第一个能存数据的项目。待办工具终于让我的数据活了下来，不再局限于一次的任务中，这一个也是从 0 到 1 的一个小小的进步。

---

## 功能

- [x] 添加任务：`add <任务文字>`
- [x] 查看列表：`list`
- [x] 标记完成：`done <编号>`
- [x] 退出保存：`quit`（退出时自动写回文件）
- [x] **数据持久化**：任务存在 `todos.json` 里，退出程序不丢，下次启动还在

---

## 快速开始

```bash
python todo_cli.py
```

**实际运行输出**（这段是真实跑出来的，不是手编的）：

```text
=== 极简待办工具（带持久化）===
已载入 0 条任务
命令：add <任务> / list / done <编号> / quit
> 已添加：写作业
> 已添加：跑步
> 已添加：背单词
> 1. 写作业 [未完成]
2. 跑步 [未完成]
3. 背单词 [未完成]
> 已完成第 2 条
> 1. 写作业 [未完成]
2. 跑步 [已完成]
3. 背单词 [未完成]
> 再见！
```

> **怎么看这段输出**：`>` 是程序打印的输入提示符。上面这段是把命令用管道喂给程序跑出来的，
> 所以你**看不到自己敲的命令**（管道不回显）；手动敲着玩时 `>` 后面会跟着你敲的字，
> 比如 `> add 写作业`，下一行才是 `已添加：写作业`。
>
> 另外注意第一行是「已载入 **0** 条任务」—— 这是第一次运行，磁盘上还没有数据文件。
> 「已载入 3 条任务」那种画面要第二次启动才出现（见下）。

**重新启动程序**（这才是持久化的意义 —— 上面的任务还在）：

```text
=== 极简待办工具（带持久化）===
已载入 3 条任务
命令：add <任务> / list / done <编号> / quit
> 1. 写作业 [未完成]
2. 跑步 [已完成]
3. 背单词 [未完成]
> 再见！
```

---

## 数据文件在哪（第一次用必看）

任务存在 **`todos.json`** 里，它在**脚本自己所在的目录**（`projects/todo-cli/`），**不在**你运行程序时所在的目录：

```bash
cd D:/某个目录
python D:/AI应用工程师/.../projects/todo-cli/todo_cli.py
# → todos.json 依然在 D:/AI应用工程师/.../projects/todo-cli/ 里，不会跑到 D:/某个目录
```

原因：`DATA_FILE = Path(__file__).parent / "todos.json"` —— `__file__` 是当前脚本的路径，
`Path(__file__).parent` 取它的目录，`/ "todos.json"` 拼上文件名。**数据就钉在脚本旁边了。**

> **2026-11-03 之前**：这里写的是 `DATA_FILE = "todos.json"`（相对路径），
> 相对的是**当前工作目录**（命令行所在的目录），不是脚本所在目录 —— 这两件事经常不一样。
> 我第一次就以为它会跟着脚本走，结果在别的目录跑出了一个**另一个** `todos.json**，差点以为数据丢了。
> 那次踩坑促成了 11-03 的第 5 条限制修复。

---

## 技术点

### 1. 文件持久化：内存 ↔ 磁盘

- **不这么写会怎样**：只把任务存在列表里，程序一退出内存就被系统回收，任务全没了，等于每次打开都是空白的
- **现在这么写**：加两个函数 —— `save_tasks` 负责内存 → 磁盘，`load_tasks` 负责磁盘 → 内存。主循环里遵循「启动时读一次、每次改动写一次、退出前再写一次」，任务就活过了这次运行

### 2. 读写模式：`"w"` 和 `"r"` 不能混

- **不这么写会怎样**：我在 `load_tasks` 里手滑写成了 `"w"`。`open(path, "w")` 的完整语义是「不存在就创建 + 存在就清空」，所以文件当场被清成 0 字节，紧接着写入那步又因为变量没定义崩了 —— 结果留下一个 0 字节的空壳，任务一条都没存进去
- **现在这么写**：读用 `"r"`，写用 `"w"`，两个值不交叉

### 3. 三道守卫：文件不在 / 文件是空的 / 文件内容是坏的

- **不这么写会怎样**：删掉第一道守卫 → `open(..., "r")` 打开一个不存在的文件 → `FileNotFoundError`，程序连第一行任务都读不到就崩；删掉第二道守卫 → `json.loads("")` → `JSONDecodeError: Expecting value`；删掉第三道守卫 → 文件有内容但**内容是坏的**（断电写到一半、手滑用记事本改过）→ 一样抛 `JSONDecodeError`
- **现在这么写**（2026-11-03 补上第三道）：

  ```python
  if not DATA_FILE.exists():          # 守卫①：文件不在
      return []
  with open(DATA_FILE, "r", encoding="utf-8") as f:
      内容 = f.read()
  if 内容 == "":                      # 守卫②：0 字节空文件
      return []
  try:
      return json.loads(内容)         # 守卫③：内容是坏的 json
  except json.JSONDecodeError:
      print("数据文件坏了，可能是上次写入中途断电")
      return []
  ```

  **三道守卫守的是三个完全不同的错误，一个都不能省。**
  注意第 ③ 道必须写全名 `json.JSONDecodeError`（带 `json.` 前缀），
  只写 `JSONDecodeError` 会 NameError —— 它不在 Python 内置命名空间里。

### 4. JSON 序列化：`dumps` 和 `loads`

- **不这么写会怎样**：`json.dumps(tasks)` 忘了 `ensure_ascii=False` → 中文全变成 `\uXXXX`。数据其实没坏（程序读回来还是对的），但人眼看不了 —— 这类「程序没坏、人看不见」的错最容易滑过去，我错题本里记成 E21
- **现在这么写**：`dumps` 是往外倒（对象 → 字符串），`loads` 是往里装（字符串 → 对象），永远成对出现

### 5. 破坏性动作要排最后：`open(path, "w")` 是「开门」不是「追加」

- **不这么写会怎样**：直接 `open(path, "w")` 写进去 —— 文件不存在的话就会创建文件，但是如果说文件存在了，就会**先清空文件的内容**，而且这个清空发生在 **`open()` 执行的那一瞬间**。也就是说**只要 open 执行了，旧内容就已经没了，哪怕后面一个字都没写**。

  这就是「崩了留下 0 字节」的真相 —— 崩在 `json.dumps` 上的时候，文件早就被清空了：

  ```python
  # ❌ 错的写法
  with open(DATA_FILE, "w", encoding="utf-8") as f:
      f.write(json.dumps(tasks))     # ← dumps 崩了，可文件已经是 0 字节了
  ```

- **现在这么写**：两条规矩

  1. **把「可能失败的操作」挪到「破坏性操作」前面** —— 先把内容算出来，崩在这一步，文件压根没被碰过
  2. **更稳的是写法C：先写到临时文件**，只有临时文件**完整写成功之后**，才执行 `os.replace(tmp, path)`；中途如果崩了就要先 `os.remove(tmp)` 清掉垃圾，**再 `raise`**（不 raise 的话，调用方以为存成功了，实际没存）

  ```python
  # ✅ 写法C：临时文件 + 原子替换
  tmp = path + ".tmp"                        # 临时文件，必须和正式文件同目录
  try:
      with open(tmp, "w", encoding="utf-8") as f:
          f.write(json.dumps(tasks, ensure_ascii=False))
      os.replace(tmp, path)                  # ← 必须在 with 块【外面】
  except Exception:
      if os.path.exists(tmp):
          os.remove(tmp)                     # 清掉垃圾，不留 .tmp
      raise                                  # 必须再抛出去
  ```

  ⚠️ **一个 Windows 特有的坑**：`os.replace` 写在 `with` 里面会报
  `PermissionError: [WinError 32] 另一个程序正在使用此文件` ——
  因为 Windows 上文件被打开的时候不允许被重命名/替换（句柄没带 `FILE_SHARE_DELETE`）。
  Linux 上没这个问题（文件句柄和文件名是分开的），所以这种错**本机一测就炸，别人写的可能还是对的**。

  > 这也是本项目现在 `save_tasks` 还没做到的事 —— 原因和怎么改，见下面「已知限制」第 3 条。

---

## ✅ 已修复（2026-11-03）｜仍在的已知限制

> **2026-11-03 更新**：11-01 列的 4 条限制已修 3 条，另有 1 条隐藏限制也修了。
> 下面先列出**已修的**（附实际修法和验收结果），再列**还没做的**。

### ✅ 已修 1｜输入 `done abc` 会直接崩

**当时的问题**：`int("abc")` 抛 `ValueError`，用户看到的是一整页红色报错栈，不是人话。

**现在怎么修的**（`run_cli()` 里）：

```python
try:
    n = int(cmd[5:])
except ValueError:
    print("编号得是数字，比如 done 1")
    continue
```

**验收**：`done abc` → 打印「编号得是数字，比如 done 1」，程序不崩，继续等下一条命令。

> ⚠️ 顺带记一个坑：**`except` 必须写具体异常类，不能光写 `except:`**。
> 裸 `except:` 会把任何错都吞掉，程序出错时你连错在哪都不知道 —— 这正是我错题本里的 E15「静默错误」。
> 另外 `ValueError` 和 `TypeError` 别搞混：
> **TypeError = 类型都不对（`int(None)`）；ValueError = 类型对但值不合理（`int("abc")`）** —— 已记为 E30。

### ✅ 已修 2｜`todos.json` 内容坏了会崩

**当时的问题**：文件有内容但是坏 JSON 时，`json.loads` 抛 `JSONDecodeError` 直接崩。
两道守卫挡的是「① 文件不存在 ② 文件是 0 字节」，**第 3 种情况没挡**。

**现在怎么修的**（`load_tasks()` 里加了第三道守卫）：

```python
try:
    return json.loads(内容)
except json.JSONDecodeError:
    print("数据文件坏了，可能是上次写入中途断电")
    return []
```

**验收**：把 `todos.json` 写成半截 JSON（`{"text":`）再启动 → 打印提示，不崩，当作空任务继续跑。

> 「三道守卫守的是三个完全不同的错误，一个都不能省」—— 现在真的是三道了。

### ✅ 已修 3（隐藏的第 5 条）｜`DATA_FILE` 是相对路径

**当时的问题**：`DATA_FILE = "todos.json"` 相对的是**当前工作目录**，不是脚本所在目录。
换个目录运行就生成另一个数据文件，看起来像"数据丢了"。

**现在怎么修的**：

```python
from pathlib import Path
DATA_FILE = Path(__file__).parent / "todos.json"
```

**验收**：从 `C:\` 运行 `python D:/.../todo_cli.py`，数据仍在项目目录里，`C:\` 下没有多出文件。

> pathlib 是"面向对象"的新写法（官方现在推它），比老式 `os.path.join(dirname(abspath(__file__)), ...)`
> 三层嵌套好记多了。**Path 对象可以直接喂给 `open()` / `.exists()`，不用转字符串。**

### 🐛 顺带修的 3 个 bug（都是"程序没崩但结果是错的"）

这 3 个是我自己 code review 时跑测试跑出来的，**都不在原来的限制清单里**：

| Bug | 现象 | 根因 | 现在怎么修的 |
|---|---|---|---|
| `done 999` | 打印「已完成第 999 条」，**其实一条都没改** | `mark_done` 的返回值**被丢弃**了，调用方不知道成功没成功 | `mark_done` 改成**永远返回 `(成功标志, 消息)`**，调用方 tuple unpacking 判断 |
| `done -1` | **真的改掉了最后一条**，还打印「已完成第 -1 条」 | Python 负数索引不报错，`tasks[-1]` 就是最后一条 | `mark_done` 里的 `n < 1` 检查挡住了（之前有检查，但返回值被丢了） |
| `done True` | 把第 1 条标成完成 | **`bool` 是 `int` 的子类**，`isinstance(True, int)` 是 True | 加 `isinstance(n, bool) or not isinstance(n, int)` |

**核心改动：返回值设计统一**

```python
# 改前：成功返回列表，失败返回字符串 → 类型不统一，调用方没法用统一方式判断
def mark_done(tasks, n):
    if n < 1 or n > len(tasks):
        return f"错误：n 必须在 1~{len(tasks)} 之间"
    ...
    return tasks

# 改后：永远返回 (成功标志, 消息)
def mark_done(tasks, n):
    if n < 1 or n > len(tasks):
        return False, f"错误：编号必须在 1~{len(tasks)} 之间"
    ...
    return True, f"已完成第 {n} 条"

# 调用方：tuple unpacking，无脑解包
成功, 消息 = mark_done(tasks, n)
if not 成功:
    print(消息)
    continue
```

> **教训**：一个函数如果"有时返回 A、有时返回 B"，调用方就没法用统一方式判断成功失败，
> 迟早会有人把返回值扔掉 —— 然后 bug 就来了。**要么统一返回一种类型，要么明确文档化"可能返回什么"。**

### ⏳ 还没修 1｜`save_tasks` 还是裸 `open('w')`

直接 `open(DATA_FILE, "w")` 写。万一 `json.dumps` 在写之前崩溃的话，正式文件就已经被清空，
文件内 0 字节，导致用户所有任务没了。

**最讽刺的地方**：`load_tasks` 特意挡了「0 字节文件」这个情况，但**写的时候自己还在制造 0 字节文件**。

**打算怎么修**：把上面技术点第 5 条的写法C 搬过来（tmp + `os.replace` + 失败清理 + `raise`）。

**这一条的额外价值**：我在同一个项目里，先用一天学了原子写入，第二天就把它用进自己的项目 ——
**错题本和作品之间是闭环的**。

> **2026-11-04 待办**（已写进日程表）

### ⏳ 还没修 2｜没有删除命令

现在只能加任务和标记完成，**删不掉一条做错的事** —— 加错了只能留着。

**打算怎么修**：加 `del <编号>`，走和 `done` 一样的边界检查（编号必须是整数、必须在 1~总数 之间）。

> **2026-11-04 待办**（已写进日程表）

### 接下来想加的

- `find <关键字>` —— 按关键字搜索任务
- 清空已完成
- **优先级** —— 现在 `done` 只有 True/False，分不出「今天必须做」和「有空再说」
- 写之前自动备份一份 `todos.json.bak`

---

## 我踩过的坑（这里最值钱）

### 坑 1：读文件的代码里用了 `"w"`

这是我写 `load_tasks` 时第一次跑就炸的地方 —— 我把 `save_tasks` 的代码整段复制过来改了改，结果模式忘了从 `"w"` 换成 `"r"`。

```python
# ❌ 错的写法
with open(DATA_FILE, "w", encoding="utf-8") as f:   # ← 读文件却用了 "w"
    f.write(json.dumps(tasks, ensure_ascii=False))
```

**错在哪**：`open(path, "w")` 的语义是「不存在就创建，存在就清空」。这行一执行，`todos.json` 立刻变成 0 字节；紧接着 `json.dumps(tasks)` 因为 `tasks` 在这个函数里根本没定义，直接抛 NameError。

于是就出现了一个特别有信息量的现场：**文件停在 0 字节**。清空那一步生效了，写入那一步没生效 —— 0 字节不是巧合，是「清空成功 + 写入失败」的精确指纹。

同一个函数里我还写了一句更离谱的：

```python
if path.exists(DATA_FILE) not in tasks:   # ← not in 后面要跟容器，这里跟的是 True/False
```

`not in` 后面必须是一个容器（列表、字符串），而 `path.exists()` 返回的是布尔值。我想要的其实是「如果文件不存在」，正确写法是 `if not path.exists(DATA_FILE):`。

**改对之后**：

```python
# ✅ 现在 todo_cli.py 里 load_tasks 的写法
if not path.exists(DATA_FILE):     # 不在 → 返回空列表（注意：不创建文件，创建是 save 的活）
    return []

with open(DATA_FILE, "r", encoding="utf-8") as f:   # r = 只读不动
    内容 = f.read()

if 内容 == "":                      # 0 字节的空壳也要挡
    return []

return json.loads(内容)
```

**我现在的习惯**：现在我每次写 `open` 都会先想一遍：w 是我来定内容，r 是我只看不动。写读文件的代码时绝对不能写成 w。

---

### 坑 2：先存盘再改内存，存进去的是旧数据

```python
# ❌ 错的写法
elif cmd.startswith("add "):
    text = cmd[4:]
    save_tasks(tasks)      # ← 先存了
    add_task(tasks, text)  # ← 后改（我第一次干脆把这行删了）
    print(f"已添加：{text}")
```

**错在哪**：程序明明打印了「已添加：写作业」，但接着 `list` 出来是「暂无任务」，`todos.json` 里躺着一个 `[]`。

**打印成功 ≠ 数据进去了。** 存盘那一刻内存里还是旧的，存进去的自然就是旧的；等内存改完再存，就没人再触发一次存盘了。这个坑跟我在通讯录项目里踩的「提示了未覆盖但实际覆盖了」是同一类 —— **屏幕上的话和真实状态对不上**，不报错，只 quietly 地把数据弄丢。

**改对之后**：

```python
# ✅ 顺序：先改内存，再写磁盘
add_task(tasks, text)   # ① 先改内存
save_tasks(tasks)       # ② 再写磁盘
```

**我现在的习惯**：现在我写 add/done 分支的时候都会先注意一下是否是改完之后才保存。

---

### 坑 3：函数里一条 `return` 都没有

**错在哪**：我第一版的 `load_tasks` 从头到尾没写 `return`。函数没有 `return` 时默认返回 `None`，那调用它的 `len(tasks)` 就会炸 `TypeError`。而且分支一多，「每条路都有出口」这件事就特别容易漏 —— 我当时有 `if / else` 两条岔路，一个出口都没给。

**改对之后**：每个分支都给一个明确的出口 —— `return []` 或 `return json.loads(内容)`。

```python
if not path.exists(DATA_FILE):
    return []                    # 出口 1
with open(DATA_FILE, "r", encoding="utf-8") as f:
    内容 = f.read()
if 内容 == "":
    return []                    # 出口 2
return json.loads(内容)          # 出口 3
```

**我现在的习惯**：现在写函数我会先看有没有 return，尤其是有多个分支的。

---

### 坑 4：改代码时删错了行 / 缩进多打了 4 个空格

这两个小错凑一起，害我第一次运行直接崩。

**错在哪（一）：缩进层级对不上**

```python
if cmd == "quit":                    # 缩进 8
    # ← 作业 3：在这里补 save_tasks(tasks)
        """把 tasks 列表存进 DATA_FILE。   # ← 缩进 16，就多打了 4 格
        ...
        """
    with open(DATA_FILE, "w", ...) as f:   # ← 缩进 12
```

报错：`IndentationError: unindent does not match any outer indentation level`。

Python 的缩进不是「对齐好看」，是**层级栈**。`if` 在 8 格 → 它的块体是 12 格；但注释不算语句，块体缩进由第一条**真实语句**决定 → 那段 docstring 落在 16 格，栈就变成 `[0, 8, 16]`，下一行回到 12 格，**12 不在栈里**，直接报错。

而且那段 docstring 本来就不该存在 —— docstring 必须是**函数体的第一行**才有意义，放在 `if` 分支里，它只是一段没人用的字符串字面量。

**错在哪（二）：删错行**

修缩进的时候，我要删的是 `quit` 分支里重复的 `with open(...)`，结果手滑把 `add` 分支里的 `add_task(tasks, text)` 删了。于是任务根本加不进去，验收第 1 条直接挂。

**改对之后**：docstring 整段删掉，换成一行 `save_tasks(tasks)`；`add_task(tasks, text)` 加回 `add` 分支。

**我现在的习惯**：注意格式缩进是否正确。

---

## 更新记录

| 日期 | 内容 |
|---|---|
| 2026-10-29 | 初版：3 个业务函数 + 文件持久化雏形 |
| 2026-10-29 | 补 README（功能 / 技术点 / 4 个踩坑复盘），3 条验收全部通过 |
| 2026-11-01 | README 细节打磨：修正运行输出块（首跑应为「已载入 0 条任务」）、补「数据文件在哪」一节、补第 5 条技术点（`open('w')` 是开门不是追加 / 写法C 原子替换 / Windows WinError 32 坑）、新增「已知限制 / 下一步」一节 |
| 2026-11-03 | **改代码 + 同步 README**：修 11-01 的 4 条限制中的 3 条（第1条 `try/except ValueError`、第2条 `try/except json.JSONDecodeError`、隐藏第5条 `Path(__file__).parent` 绝对路径），并额外修 3 个 bug（`done 999` 谎报成功 / `done -1` 负数索引 / `isinstance` 挡不住 bool）；核心改动是 **`mark_done` 返回值设计统一为 `(成功标志, 消息)`**；README 同步：技术点第 3 条改「三道守卫」、「数据文件在哪」改 pathlib 版、「已知限制」拆成「已修 3 条 + 还没修 2 条」并补写 3 个 bug 复盘 |
