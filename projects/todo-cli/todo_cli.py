# todo_cli.py —— 命令行待办工具（带 JSON 持久化）
# 2026-10-29 建 · 2026-11-03 升级（修 3 条限制 + 3 个 bug）· 11-04 升级（修第3条限制）
#
# 内存里的任务  --save_tasks-->  todos.json（磁盘）
# 内存里的任务  <--load_tasks--  todos.json（磁盘）
#
# 跑法：python todo_cli.py
# 数据：自动生成在【本脚本所在目录】的 todos.json（11-03 改：原来用相对路径，
#       换个目录运行就会在别处生成一个，看起来像"数据丢了"）
# 临时：存盘时会短暂出现一个 todos.json.tmp（11-04 原子写入用），
#       正常情况下它会被 os.replace 改名掉，目录里不会留下它
#
# ---------------------------------------------------------------
# 【改动历史】
#
# 2026-10-29 建
#   最初版本：内存里的任务，退出就丢
#
# 2026-11-03 升级（修了 3 条限制 + 修 3 个 bug）
#   改动 A（第5条限制）DATA_FILE 改成 Path(__file__).parent / "todos.json"
#                        → 数据文件永远跟着脚本走
#   改动 B（第1条限制）done abc 加 try/except ValueError → 不再崩
#   改动 C（第2条限制）json 内容损坏加 try/except json.JSONDecodeError → 不再崩
#   Bug 1 修        done 999 原本会打印"已完成第 999 条"（其实一条都没改）
#   Bug 2 修        done -1  原本会真的改掉最后一条（Python 负数索引）
#   Bug 3 修        isinstance(n, int) 挡不住 True（bool 是 int 的子类）
#
# 2026-11-04 升级（修了第3条限制 + 第4条限制 + 修 1 个 bug）
#   改动 D（第3条限制）save_tasks 改成【原子写入】
#                        → 先写 .tmp 临时文件，再用 os.replace 一次性替换
#                        → 断电/崩溃时正式文件永远保持"旧的完整数据"，不会变 0 字节
#   改动 E（第4条限制）加了 del <编号> 命令
#                        → 新函数 del_task()，三道守卫跟 mark_done 完全一样
#                        → 用 pop() 而不是 del 语句（pop 会返回被删的元素，能告诉用户删了哪条）
#   Bug 4 修        save_tasks 里 raise 的缩进掉出 except 块
#                        → 成功时也抛 RuntimeError: No active exception to reraise
#                        → 教训：缩进错误不一定报错，可能只是改变语义（E15 同款）
#
#   ✅ 11-01 列的 4 条限制 + 1 条隐藏限制，至此全部修完
#   遗留（11-05 起）无
# ---------------------------------------------------------------
#
# 这个文件回答一个问题：程序退出后，任务去哪了？
#
# 原来（练习/待办工具.py）：
#     def run_cli():
#         tasks = []          ← 这行一执行，tasks 就诞生了
#         ...
#     tasks 是【内存】里的一个列表。程序退出 → 内存被回收 → tasks 没了。
#
# 现在（这个文件）：
#     tasks = load_tasks()   ← 启动时从磁盘把任务读回来
#     ...
#     save_tasks(tasks)      # 每次改动都写回磁盘
#   这样程序退出后，任务还在磁盘上，下次启动还能读回来。
# ---------------------------------------------------------------

import json
import os
# ★ 标准库自带 json 模块，不需要 pip install
# json 只干一件事：Python 对象 ↔ 字符串 互转

from pathlib import Path
# ★ 标准库自带 pathlib，用来处理路径
# pathlib 是"面向对象"的新写法（官方现在推它），比老式的 os.path 拼接更安全

DATA_FILE = Path(__file__).parent / "todos.json"
TMP_FILE  = DATA_FILE.with_name(DATA_FILE.name + ".tmp")
# ★ 临时文件的位置：正式文件旁边多一个 .tmp 后缀
#   .../todo-cli/todos.json.tmp
#
# 逐个零件拆解：
#   DATA_FILE.name            = 'todos.json'（只有文件名，不含目录）
#   DATA_FILE.name + ".tmp"   = 'todos.json.tmp'（拼上后缀）
#   .with_name(新名字)         = 换掉【文件名】，目录部分原样不动
#
# ✅ 为什么用 with_name 而不是别的写法（11-04 实跑对比）：
#   with_name(DATA_FILE.name + ".tmp")  → todos.json.tmp  ← 用这个
#   with_suffix(".tmp")                  → todos.tmp      ← ❌ 扩展名被【替换】不是追加
#   with_name("todos.tmp") 写死          → todos.tmp      ← ⚠️ 名字写死，并发两个程序会撞车
#   str(DATA_FILE) + ".tmp"              → todos.json.tmp ← ⚠️ 结果一样，但退回字符串了
#
# ✅ 为什么保留 .json 在中间：
#   一眼看出"这是 todos.json 的临时版本"；
#   而且将来 glob("*.json") 扫正式文件时【扫不到】todos.json.tmp（它结尾是 .tmp）
#
# ⚠️ with_name 的坑（11-04 实跑）：
#   with_name("tmp")    → 不报错！返回 .../tmp（Python 3.12 不检查扩展名）
#   with_name("")       → ValueError: Invalid name ''（只有空字符串才报错）
#   → 教训：别靠"听起来会报错"来设计，得实跑
# ★ 数据文件的位置：【本脚本所在目录】/todos.json
#
# 逐个零件拆解：
#   Path(__file__)   = __file__ 是 Python 自动生成的变量 = 当前这个 .py 文件的路径
#                      用 Path() 把它变成【路径对象】（不是普通字符串了）
#   .parent          = 取所在目录（去掉文件名），这里是 .../projects/todo-cli/
#   / "todos.json"   = 在这个目录下放一个叫 todos.json 的文件
#
# ⚠️ 为什么不用相对路径 "todos.json"：
#   相对路径永远相对于【你运行程序时所在的目录】，不是脚本所在目录。
#   cd D:/别的目录 && python D:/.../todo_cli.py  →  todos.json 会生成在 D:/别的目录 里
#   （11-01 踩过这个坑，README 里记着"差点以为数据丢了"）
#
# ✅ pathlib 的额外好处：Path 对象可以直接喂给 open() / .exists()，不用转字符串
#   → 路径全程是【对象】，不会出现斜杠方向混乱、少斜杠的坑


# ============================================================
# 第 1 部分：存 —— 内存 → 磁盘
# ============================================================
def save_tasks(tasks):
    """把 tasks 列表写进 todos.json 文件。【原子写入】版（11-04 改）。

    ┌─────────────────────────────────────────────────────────────┐
    │ 为什么不能直接 open(DATA_FILE, "w")？                        │
    │                                                              │
    │ open(路径, "w") 一执行，文件【当场就被清空】。               │
    │ 从那一刻起，到 f.write() 写完为止，正式文件一直是 0 字节。  │
    │ 这中间只要出事（断电 / json.dumps 崩溃 / Ctrl+C），          │
    │ 用户的所有任务就全没了 —— 而且不留任何痕迹。               │
    │                                                              │
    │ 讽刺之处：load_tasks 特意挡住了"0 字节文件"，              │
    │ 但 save_tasks 自己还在制造 0 字节文件。                    │
    └─────────────────────────────────────────────────────────────┘

    现在的做法：【先在临时文件里写好，再一次性原子替换】

        ① open(TMP_FILE, "w")  → 写进 todos.json.tmp
           ⚠️ 清空的是 tmp（本来就是垃圾），正式文件一个字节都没动
        ② os.replace(TMP_FILE, DATA_FILE)  → 改名，一次性切换
        ③ 出错的话删掉 tmp，再 raise 把错误抛出去

    【逐行拆解】
        try:
        └─ 把可能出错的代码包起来

            with open(TMP_FILE, "w", encoding="utf-8") as f:
            └─ open(路径, 模式) = 打开文件的唯一入口
            └─ TMP_FILE = DATA_FILE.with_name(DATA_FILE.name + ".tmp")
                          = .../todos.json.tmp（目录跟着 DATA_FILE 走）
            └─ "w" = 写模式。⚠️ 打开的瞬间会把这个【临时】文件清空
            └─ encoding="utf-8" = 用 UTF-8 编码，中文才不会变成乱码
            └─ as f = 把打开的文件对象起名叫 f
            └─ with = 「用完自动关」。出了这个缩进块，文件自动关闭
              ⚠️ 关键：with 块【结束】时，缓冲区才会刷盘
                 块【内部】看 tmp 还是 0 字节是正常的！

                f.write(json.dumps(tasks, ensure_ascii=False))
                └─ json.dumps(列表) = 把 Python 对象变成一段【字符串】
                └─ ensure_ascii=False = 不要把中文转成 \\uXXXX（E21）
                └─ f.write(字符串) = 把这段字符串写进文件

            os.replace(TMP_FILE, DATA_FILE)
            └─ os.replace(源, 目标) = 把【源文件改名成目标文件名】
            └─ ⚠️ 参数顺序别反：源是 tmp，目标才是正式文件
            └─ 为什么这样就安全：
               改名是【操作系统层面的一次操作】，不是"删旧的 + 复制新的"
               → 要么全部完成，要么完全没动，中间没有"文件不存在"的状态
               → 这就是【原子】的含义：对外要么 0 变 1，绝不会是半成品
            └─ 实测（11-04 验证）：
               写 tmp 期间正式文件 = 77 字节（旧数据完好）
               replace 之后正式文件 = 116 字节（新数据）
               临时文件消失（replace 是改名，不是复制）

        except Exception:
        └─ 捕获任何异常。⚠️ 不能写裸 except:（那会把所有错都吞掉 = E15）
        └─ Exception = 所有【常规】异常的基类（不含 KeyboardInterrupt）

            if TMP_FILE.exists():
            └─ 出错了，tmp 文件是半成品，留着没用还占地方
                TMP_FILE.unlink()
                └─ unlink() = 删除文件（pathlib 的方法，等价于 os.remove）

            raise
            └─ ⚠️【必须写在这里，且缩进要与 if 平级】
            └─ raise 单独写 = 把当前这个异常【原样重新抛出去】
            └─ 不写 raise = 异常被吞掉 → 程序假装成功 → E15 静默错误
            └─ ⚠️⚠️ 11-04 踩过的坑：
               raise 一开始缩进错了（掉出 except 块），语法检查【完全通过】，
               但运行时抛 "RuntimeError: No active exception to reraise"
               → 教训：缩进错误不一定报错，可能只是悄悄改变语义
    """
    try:
        with open(TMP_FILE, "w", encoding="utf-8") as f:
            f.write(json.dumps(tasks, ensure_ascii=False))
        os.replace(TMP_FILE, DATA_FILE)

    except Exception:
        # ③ 清理：把没用的临时文件删掉
        if TMP_FILE.exists():
            TMP_FILE.unlink()
        raise


# ════════════════════════════════════════════════════════════════
# 📌 对照：11-03 之前的旧写法（留着当反面教材，【不要用】）
#
#     with open(DATA_FILE, "w", encoding="utf-8") as f:
#         f.write(json.dumps(tasks, ensure_ascii=False))
#
#     为什么不行：
#       open(DATA_FILE, "w") 一执行，正式文件就被清空了。
#       从这行到下一行之间，正式文件一直是 0 字节 —— 中途出事就全丢。
#       （11-04 改成了 tmp + os.replace，见上面 save_tasks）
# ════════════════════════════════════════════════════════════════


# ============================================================
# 第 2 部分：读 —— 磁盘 → 内存
# ============================================================
def load_tasks():
    """从 todos.json 读回 tasks 列表。读不到就返回空列表。

    四个必须挡住的坑（11-03 补上了第 4 条）：
        1. 文件不存在（第一次运行时必然没有）→ 不能直接 open，会报错
        2. 模式必须用 "r"（read），不能用 "w"！用 "w" 会把文件清空
        3. 文件存在但是空的（0 字节）→ 不能直接丢给 json.loads，会抛异常
        4. 文件有内容但内容是【坏的 json】→ json.loads 会抛 JSONDecodeError（11-03 新增）
    """
    # 坑 1：文件不在？先问一句在不在，不在就返回空列表
    if not DATA_FILE.exists():
        # ✅ 统一用 pathlib：DATA_FILE.exists() 比 path.exists(DATA_FILE) 更简洁
        # .exists() = 这个路径对应的文件/目录在不在，返回 True / False
        return []

    # 坑 2：用 "r" 读，不是 "w"。r = read，只读不改
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        内容 = f.read()          # f.read() = 把文件里全部内容读成一个字符串

    # 坑 3：读到的是空字符串（0 字节文件）？直接返回空列表
    if 内容 == "":
        return []

    # 坑 4：内容有但不是合法 json？（断电写到一半 / 手滑改过）
    try:
        return json.loads(内容)
    except json.JSONDecodeError:
        # ⚠️ 必须写全名 json.JSONDecodeError（带 json. 前缀）
        #    只写 JSONDecodeError 会 NameError —— 它不在 Python 内置命名空间里
        # JSONDecodeError = json 内容坏了的专用异常类
        print("数据文件坏了，可能是上次写入中途断电")
        return []
        # 返回空列表 = 当作"没有任务"继续跑，而不是让程序崩掉
        # ⚠️ 这里的 print 会显示在标题栏【前面】，因为 load_tasks() 在标题之前被调用
        #    → 11-03 已把调用挪到标题之后，问题解决


# ============================================================
# 第 3 部分：三个业务函数（和练习/待办工具.py 里的一样）
# ============================================================
def add_task(tasks, text):
    """加一条任务。

    任务长什么样：一个字典，两个键
        {"text": "写作业", "done": False}
        └─ "text"  = 任务文字（字符串）
        └─ "done" = 是否已完成（布尔值 True / False）

    逐行拆解：
        tasks.append({...})
        └─ append = 往列表【末尾】塞一个元素（list 专用方法）
        └─ {字典字面量} = 直接写出来的字典，Python 当场就造一个
        └─ "text": text  → 键固定叫 "text"，值是传进来的 text 参数
        └─ "done": False → 键固定叫 "done"，值先设成 False（还没做呢）

        return tasks
        └─ 【重点】list.append 其实是【就地修改】，它自己返回 None
        └─ 所以这里必须手动 return tasks，把列表还回去
        └─ ⚠️ 千万别写 tasks = tasks.append(...) —— 那样 tasks 会变成 None
    """
    tasks.append({"text": text, "done": False})
    return tasks


def list_tasks(tasks):
    """打印所有任务。

    逐行拆解：
        if not tasks:
        └─ not = 取反。not [] 是 True，not [1] 是 False
        └─ Python 老规矩：空列表是【假值】，非空列表是【真值】
        └─ 所以 if not tasks 就等于「如果列表是空的」
        └─ 这里的 return 是【提前结束函数】，不是返回列表

        for i, t in enumerate(tasks, 1):
        └─ for 循环，挨个遍历 tasks
        └─ enumerate(列表, 1) = 边遍历边发编号，从 1 开始
        └─ i = 编号，t = 当前那一条任务（它是个字典）
        └─ 不用 enumerate 的话，你得自己写 i = 0 然后每轮 i += 1

        status = "已完成" if t["done"] else "未完成"
        └─ 三元表达式。Python 的写法是「真值 if 条件 else 假值」
        └─ t["done"] = 取字典里 "done" 这个键的值
        └─ True → "已完成"，False → "未完成"

        print(f"{i}. {t['text']} [{status}]")
        └─ f"..." 是 f-string，{ } 里的会被替换成实际的值
        └─ {i} → 编号，{t['text']} → 任务文字，{status} → 状态
        └─ 引号和小方括号是固定格式，输出成 "1. 写作业 [未完成]"
    """
    if not tasks:
        print("暂无任务")
        return
    for i, t in enumerate(tasks, 1):
        status = "已完成" if t["done"] else "未完成"
        print(f"{i}. {t['text']} [{status}]")


def mark_done(tasks, n):
    """把第 n 条任务标记为已完成（n 从 1 开始数）。

    ★★★ 11-03 重大改动：返回值设计统一 ★★★
        【改前】成功返回 tasks（列表），失败返回 "错误：..."（字符串）
                → 类型不统一，调用方没法用统一方式判断，只能把返回值扔掉
                → 直接导致 Bug：done 999 会打印"已完成第 999 条"（其实一条都没改）

        【改后】永远返回 (成功标志, 提示信息) 两个值
                → 调用方无脑解包：成功, 消息 = mark_done(tasks, n)
                → 类型统一，不用 isinstance 去猜返回的是啥

    逐行拆解：
        isinstance(tasks, list)
        └─ 检查 tasks 是不是 list 类型，返回 True / False
        └─ isinstance(x, 类型) = 「x 是不是这个类型」

        isinstance(n, bool) or not isinstance(n, int)
        └─ ⚠️ 坑：bool 是 int 的子类！isinstance(True, int) 是 True
        └─ 所以光写 isinstance(n, int) 挡不住 True（done True 会把第1条标完成）
        └─ 必须额外加 isinstance(n, bool) 把它单独排除掉

        if n < 1 or n > len(tasks):
        └─ len(tasks) = 列表里有几个元素
        └─ or = 或者（两个条件满足一个就行）
        └─ 这行 = 「n 小于 1，或者 n 大于总条数」→ 说明编号越界了
        └─ ⚠️ 必须挡住 n < 1：Python 里 tasks[-1] 不是报错，是【最后一条】！
        └─    不挡的话 "done -1" 会真的改掉最后一条任务

        tasks[n - 1]["done"] = True
        └─ 【重点】列表从 0 开始数，用户说「第 1 条」对应列表里的 tasks[0]
        └─ 所以要 n - 1
        └─ ["done"] = 取字典里 "done" 这个键
        └─ = True = 把这个键的值改成 True
        └─ （就地改一个键，不用重新赋值整个字典，也不用 return）
    """
    if not isinstance(tasks, list):
        return False, "错误：tasks 必须是列表"

    if isinstance(n, bool) or not isinstance(n, int):
        # isinstance(n, bool) 放前面：bool 是 int 的子类，必须单独排除
        return False, "错误：n 必须是整数"

    if n < 1 or n > len(tasks):
        # 上下界都写清楚，用户才知道该输几
        return False, f"错误：编号必须在 1~{len(tasks)} 之间"

    tasks[n - 1]["done"] = True
    return True, f"已完成第 {n} 条"




def del_task(tasks, n):
    """删除第 n 条任务（n 从 1 开始数）。【11-04 新增】

    ★★★ 和 mark_done 完全一样的骨架，一样的三道守卫 ★★★
        这是 11-03 定下的规范：所有「按编号操作」的命令共用同一套写法。
        好处：审查时只要看守卫齐不齐，不用逐个函数重新判断。

    ┌─────────────────────────────────────────────────────────────┐
    │ ⚠️⚠️ 用户必须知道的一件事：编号会重排                          │
    │                                                              │
    │ 假设有 3 条：A / B / C                                       │
    │   用户输入 del 2  → 删掉 B → 剩下 A / C                      │
    │   此时 C 变成了【第 2 条】                                    │
    │   用户再输入 del 2 → 删掉的是 C，不是 B（因为 B 已经没了）    │
    │                                                              │
    │ 这不是 bug，是"按序号操作"的通病（1Notes 等工具也一样）。      │
    │ 对比：done 命令不会触发这个问题，因为它只改标记、不改顺序。   │
    └─────────────────────────────────────────────────────────────┘

    逐行拆解：
        if not isinstance(tasks, list):
        └─ 守卫①：tasks 必须是列表
        └─ isinstance(x, 类型) = 「x 是不是这个类型」
        └─ （和 mark_done 一致，防的是别人传错类型）

        if isinstance(n, bool) or not isinstance(n, int):
        └─ 守卫②：n 必须是【正整数】
        └─ ⚠️ 坑：bool 是 int 的子类！isinstance(True, int) 是 True
        └─ 所以光写 isinstance(n, int) 挡不住 True
        └─ 必须额外加 isinstance(n, bool) 把它单独排除掉
        └─ （和 mark_done 一致，11-03 已经踩过这个坑）

        if n < 1 or n > len(tasks):
        └─ 守卫③：上下界
        └─ len(tasks) = 列表里有几个元素
        └─ or = 或者（两个条件满足一个就行）
        └─ ⚠️⚠️【今天最重要的守卫】：必须挡住 n < 1
        └─    Python 里 tasks[-1] 不是报错，是【最后一条】！
        └─    不挡的话 "del -1" 会真的删掉最后一条任务
        └─    ⚠️ del 比 done 更危险：
        └─       done -1 只是把最后一条标成【已完成】，数据还在，能撤销
        └─       del -1 是【真删】，用户敲错一个负号，任务永久消失
        └─    （11-03 修 done -1 的时候就已经知道这个坑，今天是它的孪生兄弟）

        被删 = tasks.pop(n - 1)
        └─ 【重点】pop(下标) = 删掉该位置的元素，【并把它返回】
        └─ n - 1 = 列表从 0 开始数，用户说「第 1 条」对应 tasks[0]
        └─ 为什么要 pop 而不是 del tasks[n-1]：
        └─    del 只删不返回 → 想告诉用户"删的是哪条"就得先存再删，两行
        └─    pop 一次搞定：既删了，又拿到了被删的那个字典
        └─ 被删 = 一个字典 {"text": ..., "done": ...}
        └─ ⚠️ pop(-1) 会删最后一条 —— 所以上面守卫③必须先挡住

        return True, f"已删除第 {n} 条：{被删['text']}"
        └─ 和 mark_done 一样：永远返回 (成功标志, 提示信息) 两个值
        └─ 被删['text'] = 取被删任务里的任务文字 → 告诉用户删的是哪条
        └─ 比 mark_done 多带一句文字，因为删除是不可逆的，
        └─    用户需要知道"我刚才删掉的是哪个"，才能去别处找回来
    """
    # ① 类型守卫
    if not isinstance(tasks, list):
        return False, "错误：tasks 必须是列表"

    if isinstance(n, bool) or not isinstance(n, int):
        return False, "错误：n 必须是整数"

    # ② 上下界守卫（挡住负数！）
    if n < 1 or n > len(tasks):
        return False, f"错误：编号必须在 1~{len(tasks)} 之间"

    # ③ 真正删
    被删 = tasks.pop(n - 1)

    # ④ 返回统一格式
    return True, f"已删除第 {n} 条：{被删['text']}"


# ============================================================
# 第 4 部分：主循环
# ============================================================
def run_cli():
    """命令行主程序。

    关键顺序：
        启动时 → load_tasks() 把磁盘上的任务读进内存
        每次改动 → 先改内存，再 save_tasks() 写回磁盘
        退出时 → 最后再 save 一次，保证不丢
    """
    # ============================================================
    # 启动阶段
    # ============================================================
    print("=== 极简待办工具（带持久化）===")
    # ⚠️ 11-03 调整：标题先打印，再调 load_tasks()
    #    原因：load_tasks() 里的错误提示（比如"数据文件坏了"）应该在标题【之后】显示，
    #    原来标题在后面，用户先看到一句警告再看标题，顺序反了

    # ① 启动：从磁盘把任务读回来（原来这里是 tasks = []，永远是空的）
    tasks = load_tasks()
    print(f"已载入 {len(tasks)} 条任务")
    # f"已载入 {len(tasks)} 条任务" → len(tasks) 是条数，{ } 里塞进去
    print("命令：add <任务> / list / done <编号> / quit / del <编号>")

    # ============================================================
    # 主循环：不停地【读命令 → 判断 → 执行】
    # ============================================================
    while True:
        # while True = 死循环（条件永远为真），靠 break 跳出来
        cmd = input("> ").strip()
        # input("> ") = 先打印提示符 "> "，然后等用户敲一行，按回车后返回【字符串】
        # .strip() = 去掉首尾空格（用户手滑多敲一个空格也能识别）
        #   ⚠️ 少了 strip，用户输入 "quit " 带个空格，就匹配不上 —— E03/E19 同款

        if not cmd:
            # not cmd = 用户直接按了回车（cmd 是空字符串）
            continue
            # continue = 跳过本次循环，重新来一轮（注意：不是退出循环）

        if cmd == "quit":
            # == 是【比较】，两个等号才是相等；一个等号是赋值
            # 退出前最后一次存盘（先存，再告别）
            save_tasks(tasks)
            print("再见！")
            break
            # break = 直接跳出整个 while 循环，程序继续往下走（也就是退出本函数）

        elif cmd == "list":
            # elif = else if，前面的 if 没匹配上，才轮到这一支
            # list 只是看，没改动内存，所以不用存盘
            list_tasks(tasks)

        elif cmd.startswith("add "):
            # startswith("add ") = 开头是不是 "add "（带空格，所以光敲 "add" 不会误触发）
            text = cmd[4:]
            # cmd[4:] = 切片，从第 5 个字符切到最后
            #   "add 写作业" → 切掉前 4 个字符 "add " → "写作业"
            #   [] 里的冒号表示「一直到末尾」；写 cmd[:4] 才是「从头到第 4 个字符」

            add_task(tasks, text)
            # ① 先改内存：往 tasks 里加一条

            save_tasks(tasks)
            # ② 再写磁盘
            # ⚠️ 顺序绝对不能反！先存后改 = 存进去的是改之前的旧数据，等于白存

            print(f"已添加：{text}")

        elif cmd.startswith("done "):
            try:
                n = int(cmd[5:])
                # cmd[5:] = "done 1" 切掉前 5 个字符 "done " → "1"
                # int("1") = 把字符串 "1" 转成数字 1
                #   不转的话，mark_done 里的 isinstance(n, int) 会直接报错
            except ValueError:
                # ValueError = 「类型对但值不对」的异常：int("abc")、int("") 都是它
                # ⚠️ 必须指定具体异常类！裸写 except: 会把任何错都吞掉 = 静默错误（E15）
                print("编号得是数字，比如 done 1")
                continue
                # continue = 跳过本轮剩余代码，回到 while 下一轮
                #   注意：continue 必须缩进在 while 循环体内，不能跑到外面去

            成功, 消息 = mark_done(tasks, n)
            # ★ tuple unpacking（元组解包）：mark_done 永远返回 2 个值
            #   一次给两个变量接住，不需要 isinstance 去猜返回的是什么类型
            #   （11-03 之前这里是 mark_done(tasks, n) —— 返回值被扔了，
            #     导致 done 999 会打印"已完成第 999 条"，其实一条都没改）

            if not 成功:
                # not 成功 = 失败时
                print(消息)
                # 打印错误提示（消息 = "错误：编号必须在 1~2 之间"）
                continue
                # 失败就跳过本轮，不要往下走去 save_tasks 和打印"已完成"

            save_tasks(tasks)
            # 改成功了才写磁盘

            print(消息)
            # 消息 = "已完成第 1 条"

        elif cmd.startswith("del "):
            # ⚠️ 结尾那个空格【必须写】："del " 而不是 "del"
            #    带空格 = 只有用户真的敲了 "del" + 空格才进来
            #    不带空格 = 任何以 "del" 开头的东西都会进这个分支
            #    （11-04 踩过：写成了 startswith("del")，用户光敲 "del" 不带编号
            #      会被误判成"编号格式错误"，语义不对）
            #    对照上面：startswith("add ") / startswith("done ") 都带空格

            try:
                n = int(cmd[4:])
                # cmd[4:] = "del 1" 切掉前 4 个字符 "del " → "1"
                # int("1") = 把字符串 "1" 转成数字 1
                #   不转的话，del_task 里的 isinstance(n, int) 会直接报错
                #   ⚠️ cmd[4:] 的 4 = len("del ") —— 空格也算进去了
                #      写成 startswith("del") 的话这里得是 cmd[3:]，
                #      但那样 "del1" 这种输入会被切成 "1"，反而"能用"了 ——
                #      这种"能用"是巧合，不是设计，靠 startswith("del ") 统一
            except ValueError:
                # ValueError = 「类型对但值不对」的异常：int("abc")、int("") 都是它
                # ⚠️ 必须指定具体异常类！裸写 except: 会把任何错都吞掉 = 静默错误（E15）
                # 实测能挡住这几种（11-04）：
                #   del abc（不是数字）、del（没带编号）、del 1x（数字后面跟字母）
                print("编号得是数字，比如 del 1")
                continue
                # continue = 跳过本轮剩余代码，回到 while 下一轮
                #   注意：continue 必须缩进在 while 循环体内，不能跑到外面去

            成功, 消息 = del_task(tasks, n)
            # ★ tuple unpacking：del_task 永远返回 2 个值
            #   （和上面 done 分支一模一样 —— 11-03 定的规范，所有命令统一）

            if not 成功:
                # not 成功 = 失败时
                print(消息)
                # 打印错误提示（消息 = "错误：编号必须在 1~2 之间"）
                continue
                # 失败就跳过本轮，不往下走去 save_tasks
                # ⚠️ 关键：失败时【不能】写磁盘
                #    万一守卫没挡住、真的删错了，磁盘上的原数据就找不回来了

            save_tasks(tasks)
            # 删成功了才写磁盘（用 11-04 的原子写入，崩了也不会丢数据）

            print(消息)
            # 消息 = "已删除第 1 条：写作业"
            # ⚠️ 编号会重排：删完之后，后面所有任务的编号都往前挪了一位
            #    用户如果想删两条，得重新 list 看当前编号
            #    （这是"按序号操作"的通病，已写进 del_task 的 docstring）


        else:
            # 上面全都没匹配上，才走到这里
            print("未知命令，输入 add / list / done / quit / del")


# ============================================================
# 程序入口
# ============================================================
# __name__ 在「直接运行这个文件」时是 "__main__"，被别的文件 import 时是模块名
# 所以这行的意思是：只有「直接运行本文件」时才启动，被别人 import 时不启动
# 这是 Python 的标准写法 —— 保证这个文件既能当程序跑，也能当工具被别人调用
if __name__ == "__main__":
    run_cli()
