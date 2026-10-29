# 待办工具_持久化.py
# 2026-10-29 · 阶段1 第5周 · 上午任务
#
# 带「文件持久化」的命令行待办工具：
#   内存里的任务  --save_tasks-->  todos.json（磁盘）
#   内存里的任务  <--load_tasks--  todos.json（磁盘）
#
# 跑法：python 待办工具_持久化.py
# 数据：同目录下自动生成 todos.json（每次运行都会覆盖它）
#
# ---------------------------------------------------------------
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
#     save_tasks(tasks)      ← 每次改动都写回磁盘
#   这样程序退出后，任务还在磁盘上，下次启动还能读回来。
# ---------------------------------------------------------------

import json
from os import path

DATA_FILE = "todos.json"          # 数据文件名（相对路径：相对于本文件所在目录）


# ============================================================
# 第 1 部分：存 —— 内存 → 磁盘
# ============================================================
def save_tasks(tasks):
    """把 tasks 列表写进 todos.json 文件。

    逐行拆解：
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            └─ "w" = 写模式（write）。⚠️ 打开的瞬间会先把文件【清空】。
            └─ encoding="utf-8" = 用 UTF-8 编码，中文才不会变成乱码
            └─ as f = 把打开的文件对象起名叫 f，后面就用 f 来操作它
            └─ with = 「用完自动关」。出了这个缩进块，文件自动关闭，不用手写 close()

            f.write(json.dumps(tasks, ensure_ascii=False))
            └─ json.dumps(列表) = 把 Python 对象变成一段【字符串】
            └─ ensure_ascii=False = 不要把中文转成 \\uXXXX（E21）
            └─ f.write(字符串) = 把这段字符串写进文件
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks, ensure_ascii=False))


# ============================================================
# 第 2 部分：读 —— 磁盘 → 内存
# ============================================================
def load_tasks():
    """从 todos.json 读回 tasks 列表。读不到就返回空列表。

    三个必须挡住的坑：
        1. 文件不存在（第一次运行时必然没有）→ 不能直接 open，会报错
        2. 模式必须用 "r"（read），不能用 "w"！用 "w" 会把文件清空
        3. 文件存在但是空的（0 字节）→ 不能直接丢给 json.loads，会抛异常
    """
    # 坑 1：文件不在？先问一句在不在，不在就返回空列表
    if not path.exists(DATA_FILE):
        return []

    # 坑 2：用 "r" 读，不是 "w"。r = read，只读不改
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        内容 = f.read()          # f.read() = 把文件里全部内容读成一个字符串

    # 坑 3：读到的是空字符串（0 字节文件）？直接返回空列表
    if 内容 == "":
        return []

    # 正常情况：字符串 → 列表
    return json.loads(内容)      # json.loads(字符串) = 把【字符串】变回 Python 对象


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

    逐行拆解：
        isinstance(tasks, list)
        └─ 检查 tasks 是不是 list 类型，返回 True / False
        └─ isinstance(x, 类型) = 「x 是不是这个类型」

        if n < 1 or n > len(tasks):
        └─ len(tasks) = 列表里有几个元素
        └─ or = 或者（两个条件满足一个就行）
        └─ 这行 = 「n 小于 1，或者 n 大于总条数」→ 说明编号越界了

        tasks[n - 1]["done"] = True
        └─ 【重点】列表从 0 开始数，用户说「第 1 条」对应列表里的 tasks[0]
        └─ 所以要 n - 1
        └─ ["done"] = 取字典里 "done" 这个键
        └─ = True = 把这个键的值改成 True
        └─ （就地改一个键，不用重新赋值整个字典，也不用 return）
    """
    if not isinstance(tasks, list):
        return "错误：tasks 必须是列表"
    if not isinstance(n, int):
        return "错误：n 必须是整数"
    if n < 1 or n > len(tasks):
        return f"错误：n 必须在 1~{len(tasks)} 之间"
    tasks[n - 1]["done"] = True
    return tasks


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
    # ① 启动：从磁盘把任务读回来（原来这里是 tasks = []，永远是空的）
    tasks = load_tasks()
    print("=== 极简待办工具（带持久化）===")
    print(f"已载入 {len(tasks)} 条任务")
    # f"已载入 {len(tasks)} 条任务" → len(tasks) 是条数，{ } 里塞进去
    print("命令：add <任务> / list / done <编号> / quit")

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
            n = int(cmd[5:])
            # cmd[5:] = "done 1" 切掉前 5 个字符 "done " → "1"
            # int("1") = 把字符串 "1" 转成数字 1
            #   不转的话，mark_done 里的 isinstance(n, int) 会直接报错

            mark_done(tasks, n)
            # 改内存：把第 n 条的 "done" 改成 True

            save_tasks(tasks)
            # 再写磁盘

            print(f"已完成第 {n} 条")

        else:
            # 上面全都没匹配上，才走到这里
            print("未知命令，输入 add / list / done / quit")


# ============================================================
# 程序入口
# ============================================================
# __name__ 在「直接运行这个文件」时是 "__main__"，被别的文件 import 时是模块名
# 所以这行的意思是：只有「直接运行本文件」时才启动，被别人 import 时不启动
# 这是 Python 的标准写法 —— 保证这个文件既能当程序跑，也能当工具被别人调用
if __name__ == "__main__":
    run_cli()
