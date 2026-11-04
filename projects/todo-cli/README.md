# 待办工具 CLI

命令行版待办工具，支持添加任务、查看列表、标记完成，任务存在本地 JSON 文件里 —— 程序关了再开，任务还在。

我学完「函数封装 + 文件读写」后写的第一个能存数据的项目。待办工具终于让我的数据活了下来，不再局限于一次的任务中，这一个也是从 0 到 1 的一个小小的进步。

---

## 功能

- [x] 添加任务：`add <任务文字>`
- [x] 查看列表：`list`
- [x] 标记完成：`done <编号>`
- [x] **删除任务**：`del <编号>`（2026-11-04 下午档新增）
- [x] 退出保存：`quit`（退出时自动写回文件）
- [x] **数据持久化**：任务存在 `todos.json` 里，退出程序不丢，下次启动还在
- [x] **原子写入**：保存时先写临时文件再原子替换，写入中途崩溃也不会丢数据（2026-11-04 上午档新增）

---

## 快速开始

```bash
python todo_cli.py
```

**实际运行输出**（这段是真实跑出来的，不是手编的）：

```text
=== 极简待办工具（带持久化）===
已载入 0 条任务
命令：add <任务> / list / done <编号> / quit / del <编号>
> 已添加：写作业
> 已添加：跑步
> 已添加：背单词
> 1. 写作业 [未完成]
2. 跑步 [未完成]
3. 背单词 [未完成]
> 已完成第 2 条
> 已删除第 1 条：写作业
> 1. 跑步 [已完成]
2. 背单词 [未完成]
> 再见！
```

> **怎么看这段输出**：`>` 是程序打印的输入提示符。上面这段是把命令用管道喂给程序跑出来的，
> 所以你**看不到自己敲的命令**（管道不回显）；手动敲着玩时 `>` 后面会跟着你敲的字，
> 比如 `> add 写作业`，下一行才是 `已添加：写作业`。
>
> 另外注意第一行是「已载入 **0** 条任务」—— 这是第一次运行，磁盘上还没有数据文件。
> 「已载入 3 条任务」那种画面要第二次启动才出现（见下）。
>
> ⚠️ 最后那段还演示了一个**容易忽略的行为**：`del 1` 删掉了「写作业」之后，
> 原来第 2 条「跑步」**变成了第 1 条** —— **编号会重排**。
> 所以「已完成第 2 条」和「已删除第 1 条」之后看到的编号不是同一套编号了，别混。

**重新启动程序**（这才是持久化的意义 —— 上面的任务还在）：

```text
=== 极简待办工具（带持久化）===
已载入 2 条任务
命令：add <任务> / list / done <编号> / quit / del <编号>
> 1. 跑步 [已完成]
2. 背单词 [未完成]
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

  > ✅ **2026-11-04 已落地**：这段写法已经搬进本项目的 `save_tasks`，见下面「已修 4」。

### 6. 原子写入：临时文件 + `os.replace`（2026-11-04 上午档）

- **不这么写会怎样**：`open(path, "w")` 是「开门就清空」，只要 open 执行了，旧内容就没了。
  哪怕后面 `json.dumps` 崩了，文件已经是 0 字节 —— 用户所有任务当场蒸发。
- **现在这么写**：写临时文件 → 写成功了才 `os.replace` 原子替换。**正式文件全程只有两种状态**：
  「旧的完整数据」或「新的完整数据」，**没有中间态**。
- **`os.replace` 是什么**：操作系统层面的**原子改名**（一条系统调用完成），
  **不是**「删旧的 + 复制新的」两步 —— 所以不存在「删完了还没复制完」的窗口期。
- **为什么必须有 `except` + `raise`**：崩了要清掉 `.tmp`（不留垃圾），
  **而且必须把异常再抛出去** —— 不 raise 的话调用方以为存成功了，实际没存。
  这跟 E01「提示了却照样执行」是同一类静默错误。

### 7. 命令解析：`startswith` 必须带结尾空格（2026-11-04 下午档）

- **不这么写会怎样**：`cmd.startswith("del")` 看起来对，但它会**同时匹配**「delete」「delicious」这类词，
  更坑的是**用户光敲 `del`（不带编号）**时也会匹配上 → `cmd[4:]` 切出空串 → `int("")` 抛 `ValueError`。
- **现在这么写**：`cmd.startswith("del ")` —— **末尾那个空格是命令的一部分**。
  空格的作用就是「把命令和参数分开」，让「只有命令没有参数」的情况**根本进不来**。

---

## ✅ 已修复的限制（2026-11-03 / 11-04）｜目前零遗留

> **2026-11-04 更新**：11-01 列的 4 条限制已**全部修完**（11-03 修 3 条，11-04 修 2 条），
> 另修了 4 个隐藏限制/bug。**目前没有未修的限制了** —— 下面全部是「已修」的记录。
>
> **2026-11-03 那次修的是**：第 1 条（`done abc` 崩溃）、第 2 条（坏 JSON 崩溃）、
> 隐藏第 5 条（`DATA_FILE` 相对路径），外加 3 个静默 bug。
> **11-04 修的是**：第 4 条（裸 `open('w')` → 原子写入）、第 5 条（没有删除命令）。

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

### ✅ 已修 4｜`save_tasks` 还是裸 `open('w')`（11-04 上午档修好）

**当时的问题**：直接 `open(DATA_FILE, "w")` 写。万一 `json.dumps` 在写之前崩溃的话，正式文件就已经被清空，
文件内 0 字节，导致用户所有任务没了。

**最讽刺的地方**：`load_tasks` 特意挡了「0 字节文件」这个情况，但**写的时候自己还在制造 0 字节文件**。

**现在怎么修的**（`save_tasks` 改成「临时文件 + 原子替换」）：

```python
TMP_FILE = DATA_FILE.with_name(DATA_FILE.name + ".tmp")   # 临时文件，和正式文件同目录

def save_tasks(tasks):
    try:
        with open(TMP_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(tasks, ensure_ascii=False))
        os.replace(TMP_FILE, DATA_FILE)          # ← 原子替换，操作系统层面改名
    except Exception:
        if TMP_FILE.exists():
            TMP_FILE.unlink()                    # 崩了就清掉临时文件，不留垃圾
        raise                                     # 再把异常抛出去，不能吞
```

**为什么这样就安全了**：
- 正式文件在**整个写入过程中都是完整的** —— 它要么是「旧的完整数据」，要么是「新的完整数据」，**没有中间态**。
- `os.replace(源, 目标)` 是操作系统层面的**原子改名**，不是「删旧的 + 复制新的」两步，所以不存在「删完还没复制完」的窗口期。
- 崩了 → `except` 清掉 `.tmp` → `raise` 让调用方知道「没存成功」。**不 raise 的话，调用方以为存成功了，实际没存** —— 这跟 E01「提示了却照样执行」是同一类错。

**验收**（4 项单测 + 深度时序验证 + 3 轮端到端，全过）：
- 正常保存：内容读回来一致 ✅
- 保存后**没有残留 `.tmp` 文件** ✅
- 故意让写入崩溃：正式文件**还是旧数据**（77 字节完好），`.tmp` 被清理 ✅
- 深度时序验证：`replace` 之前正式文件是 77 字节，`replace` 之后是 116 字节 —— **全程没有 0 字节中间态** ✅
- 端到端：从 `C:\Windows\Temp` 运行程序，数据仍在项目目录 ✅

> ⚠️ **Windows 特有的坑**：`os.replace` 写在 `with` 里面会报
> `PermissionError: [WinError 32] 另一个程序正在使用此文件` ——
> 因为 Windows 上文件被打开的时候不允许被重命名/替换（句柄没带 `FILE_SHARE_DELETE`）。
> Linux 上没这个问题，所以这种错**本机一测就炸，别人写的可能还是对的**。
> **所以 `os.replace` 必须在 `with` 块【外面】。**

### ✅ 已修 5｜没有删除命令（11-04 下午档修好）

**当时的问题**：现在只能加任务和标记完成，**删不掉一条做错的事** —— 加错了只能留着。

**现在怎么修的**（新增 `del_task` 函数 + `del <编号>` 命令）：

```python
def del_task(tasks, n):
    if not isinstance(tasks, list):                # 守卫①：tasks 必须是列表
        return False, "错误：tasks 必须是列表"
    if isinstance(n, bool) or not isinstance(n, int):  # 守卫②：n 必须是整数（bool 是 int 的子类）
        return False, "错误：n 必须是整数"
    if n < 1 or n > len(tasks):                    # 守卫③：编号范围（挡住 n=0 和负数）
        return False, f"错误：编号必须在 1~{len(tasks)} 之间"
    被删 = tasks.pop(n - 1)                        # pop 会返回被删的元素
    return True, f"已删除第 {n} 条：{被删['text']}"
```

命令分支：

```python
elif cmd.startswith("del "):        # ⚠️ 必须带结尾空格
    try:
        n = int(cmd[4:])
    except ValueError:
        print("编号得是数字，比如 del 1")
        continue
    成功, 消息 = del_task(tasks, n)
    if not 成功:
        print(消息)
        continue
    save_tasks(tasks)
    print(消息)
```

**验收**（9 项边界实测，全过）：`del 1` / `del 999` / `del -1` / `del 0` / `del abc` / `del 1x` / 只敲 `del` / 两个空格 —— 全部正确处理，**程序不崩**。

> **三个关键点**：
> ① **`startswith("del ")` 必须带结尾空格** —— 不带的话，用户光敲 `del`（不带编号）会误入编号解析分支，
>    `cmd[4:]` 切出空串，`int("")` 抛 ValueError。已记为 **E33**。
> ② **`pop(i)` vs `del tasks[i]`**：前者**返回**被删的元素（所以能打印「已删除第 N 条：xxx」），
>    后者只删不返。返回值能带信息，这是选 `pop` 的理由。
> ③ **编号会重排** —— 删掉第 2 条后，原来的第 3 条变成第 2 条。这跟 `done` 的行为一样，但更值得提醒用户。

> ⚠️ **注意 `del -1` 为什么没删掉最后一条**：`tasks[-1]` 在 Python 里是合法的（负数索引），
> 所以 `del -1` **本来会真的删掉最后一条**。挡住它的是守卫③的 `n < 1` 检查 ——
> 这就是 11-03 `done -1` 学费的直接应用（错题本 E-相关条目同源）。

### 接下来想加的

- `find <关键字>` —— 按关键字搜索任务
- 清空已完成
- **优先级** —— 现在 `done` 只有 True/False，分不出「今天必须做」和「有空再说」
- 写之前自动备份一份 `todos.json.bak`
- `edit <编号> <新文字>` —— 修改任务内容（比删了重加体验好）

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

### 坑 5：`raise` 缩进掉出 `except` 块 —— 语法全绿，运行时才炸（11-04 上午档）

这个是我 11-04 上午写原子写入时踩的，**最阴险的一个**，因为它**语法检查完全通过**。

**错在哪**：我写的是

```python
try:
    with open(TMP_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks, ensure_ascii=False))
    os.replace(TMP_FILE, DATA_FILE)
except Exception:
    if TMP_FILE.exists():
        TMP_FILE.unlink()
    raise          # ❌ 这里本意是「在 except 里重新抛出」
```

但我实际的缩进让 `raise` **掉出了 `except` 块**（跟 `except` 平级，或者更外层）。
Python 允许在 `except` 块**外面**写一个裸 `raise` —— **语法上完全合法**，静态检查一点问题都看不出来。

**运行时才炸**：

```text
RuntimeError: No active exception to reraise
```

翻译成人话：**「没有正在处理的异常可以重新抛出」** —— 因为此刻根本不在 except 块里。

**更糟的是它会掩盖真正的错误**：我本来的 `except` 是要清理 `.tmp` 并重新抛出原始异常的。
`raise` 掉出去之后，**原始的那个异常被 `RuntimeError` 盖住了** —— 我根本看不出到底是哪里出的问题。

**为什么这个坑特别危险**：
- 语法检查全绿 → 你以为写对了
- 只有**真的跑到那行**才会炸 → 如果这个分支平时走不到，测试也可能测不出来
- 一旦炸，报的还是一个**误导性的**异常名

**改对之后**（`raise` 必须和 `except` 里的其他语句**平级**，即缩进 8 格）：

```python
except Exception:
    if TMP_FILE.exists():
        TMP_FILE.unlink()
    raise          # ✅ 与 if 平级，在 except 块内
```

> **口诀**：`raise` 前面那行缩进多少，`raise` 就是多少 —— 它属于**当前所在的块**。
> 写完 `except:` 块，养成习惯**用鼠标往左推一下 `raise`**，看它有没有退出 except 块。
>
> 已登记为 **E32**。

---

### 坑 6：`startswith("del")` 少一个空格，命令解析全乱（11-04 下午档）

**错在哪**：

```python
elif cmd.startswith("del"):        # ❌ 少了结尾空格
    n = int(cmd[4:])                # 光敲 "del" 时 cmd[4:] 是空串 → int("") → ValueError
```

**为什么少空格是错的**：`startswith("del")` 会把**所有以 "del" 开头的字符串**都吃进来 ——
不只是 `del 3`，连 `delete`、`delicious` 都会匹配。

更实际的问题是**用户光敲 `del` 不带编号**（很常见，就是想看看用法）→ 进了这个分支 →
`cmd[4:]` 切出空串 → `int("")` 抛 `ValueError: invalid literal for int()` → **程序崩给用户看一整页红字**。

**改对之后**：

```python
elif cmd.startswith("del "):       # ✅ 结尾那个空格是命令的一部分
    try:
        n = int(cmd[4:])
    except ValueError:
        print("编号得是数字，比如 del 1")
        continue
```

**那个空格的真正作用**：它把「命令」和「参数」分开，让**「只有命令没有参数」这种情况根本进不来**。
没有参数 → 不匹配 → 落到「未知命令」提示 → 用户看到的是人话，不是报错栈。

> **口诀**：`startswith` 里带结尾空格 = 严格匹配命令本身；
> 不带 = 模糊匹配前缀，很容易误伤。
>
> 已登记为 **E33**。

---

## 更新记录

| 日期 | 内容 |
|---|---|
| 2026-10-29 | 初版：3 个业务函数 + 文件持久化雏形 |
| 2026-10-29 | 补 README（功能 / 技术点 / 4 个踩坑复盘），3 条验收全部通过 |
| 2026-11-01 | README 细节打磨：修正运行输出块（首跑应为「已载入 0 条任务」）、补「数据文件在哪」一节、补第 5 条技术点（`open('w')` 是开门不是追加 / 写法C 原子替换 / Windows WinError 32 坑）、新增「已知限制 / 下一步」一节 |
| 2026-11-03 | **改代码 + 同步 README**：修 11-01 的 4 条限制中的 3 条（第1条 `try/except ValueError`、第2条 `try/except json.JSONDecodeError`、隐藏第5条 `Path(__file__).parent` 绝对路径），并额外修 3 个 bug（`done 999` 谎报成功 / `done -1` 负数索引 / `isinstance` 挡不住 bool）；核心改动是 **`mark_done` 返回值设计统一为 `(成功标志, 消息)`**；README 同步：技术点第 3 条改「三道守卫」、「数据文件在哪」改 pathlib 版、「已知限制」拆成「已修 3 条 + 还没修 2 条」并补写 3 个 bug 复盘 |
| 2026-11-04 上午 | **修第 4 条限制：原子写入**。`save_tasks` 改成「临时文件 + `os.replace` 原子替换 + 失败清理 + `raise`」，正式文件全程无 0 字节中间态。验收 4 项单测 + 深度时序验证 + 3 轮端到端（含从 `C:\Windows\Temp` 运行）全过。README 同步：新增技术点第 6 条、新增踩坑坑 5（`raise` 缩进掉出 except 块 → 语法全绿但运行时 `RuntimeError`，已登记 E32） |
| 2026-11-04 下午 | **修第 5 条限制：新增 `del <编号>` 命令**。新增 `del_task` 函数（3 道守卫：类型/整数/范围），用 `pop(n-1)` 而不是 `del` 是为了能打印被删内容。验收 9 项边界实测（`del 1`/`999`/`-1`/`0`/`abc`/`1x`/光敲 `del`/两空格）全过。README 同步：功能清单 +2、新增技术点第 7 条、新增踩坑坑 6（`startswith` 少结尾空格 → 命令误匹配，已登记 E33） |
| 2026-11-04 晚上 | **LeetCode 167 两数之和 II**：练习文件 `练习/11.04练习_LeetCode_两数之和II.py` 完成（双指针 O(n) + 双循环暴力 O(n²) 双版本对照，17 个固定用例 + 20 组随机对照全过）。**README 的「已知限制」到此清零 —— 11-01 列的 4 条限制 + 4 个隐藏限制全部修完** |
