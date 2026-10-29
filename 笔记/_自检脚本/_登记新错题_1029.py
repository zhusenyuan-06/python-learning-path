# _登记新错题_1029.py —— 把今天犯的 5 类新错登记进错题追踪池
# 2026-10-29 · 阶段1 第5周 · 晚上复习前
#
# ---------------------------------------------------------------
# 这个文件回答一个问题：今天写代码时犯的错，怎么才能进错题本？
#
# 规矩（你自己定的）：
#   「这周写新代码遇到的、清单里没记的错误，当场 add 进去，下卷必考。
#     当天不登记 = 白踩。」
#
# 为什么不用手敲命令：
#   错题写法里有引号、换行、反斜杠，比如：
#       "with open(DATA_FILE, 'w') as f:\n    f.write(...)"
#   手敲进 bash 会被 shell 吃掉 —— 引号会被拆、\n 会变成真换行、
#   > 会被当成重定向符。所以改成用 subprocess 传【数组】：
#   数组里的每个元素原样送达，不经过 shell 解析，一个字符都不会丢。
#
# 只做一件事：调 错题追踪器.py 的 add / record 命令。
# JSON（错题追踪.json）是唯一真源，写入全权交给追踪器自己负责，
# 这个脚本一行都不碰那个文件。
#
# ⚠️ 这个脚本是【一次性】的 —— 登记完就没用了，留在仓库里当记录。
#    真正常用的命令还是直接敲：
#        "D:\AAAA\python.exe" 错题追踪器.py add "标题" "错误写法" "正确写法" "标签"
# ---------------------------------------------------------------

import subprocess
import sys
from pathlib import Path

# r"..." = 原始字符串（raw string）
#   └─ 作用：反斜杠不做转义。r"D:\AAAA\python.exe" 里的 \A、\A 就是字面的 \A
#   └─ 不加 r 的话，\A 会被当成转义序列（虽然这里恰好不出错，但会弹警告）
#   └─ Windows 路径必须用正斜杠或双反斜杠，用 r".." + 正斜杠最省心
PY = r"D:\AAAA\python.exe"

# Path(...) = pathlib 的路径对象，比字符串路径好用（能自动处理分隔符）
#   └─ 这个路径是【绝对路径】，所以在哪个目录跑这个脚本都能找到追踪器
TRACKER = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记\错题追踪器.py")

# 要登记的 5 条新错。
# 每条是 4 个元素的元组：(标题, 错误写法, 正确写法, 标签)
#   └─ 元组用小括号，一旦写出来就不能改（想改得重新建一个）
#   └─ 列表用方括号，可以增删 —— 这里用列表是因为要 for 循环遍历
#   └─ 标签用逗号分隔的字符串（不是列表），追踪器内部会 split(",")
NEW_ERRORS = [
    (
        # ⚠️ E24（新增）：今天真实踩过 —— 教学/todos.json 变成 0 字节
        "open(path, 'w') 会先清空再写 —— 中途失败留下 0 字节文件",
        # 错误写法用 \n 表示换行（这是普通字符串，不是 r""）
        #   └─ 相邻的多个字符串字面量会自动拼接，Python 允许这么写
        "with open(DATA_FILE, 'w', encoding='utf-8') as f:\n"
        "    f.write(json.dumps(tasks))\n"
        "# tasks 未定义 → 崩溃。但 open('w') 已经把旧文件清空了",
        "open(path,'w') 的语义是「不存在则创建 + 存在则清空」，不是「追加」。\n"
        "所以写之前必须保证待写内容已经准备好（变量有值、不依赖未定义的东西）\n"
        "另外：备份用 'a'，读用 'r'，写新内容用 'w'",
        "文件读写,持久化,w模式",
    ),
    (
        # ⚠️ E25（新增）：今天真实踩过 —— if path.exists(DATA_FILE) not in tasks
        "'not in' 和 'not' 混淆 —— not in 后面必须跟容器",
        "if path.exists(DATA_FILE) not in tasks:\n"
        "    tasks = []",
        "if not path.exists(DATA_FILE):\n"
        "    tasks = []\n"
        "# not in 是「成员判断」，右边必须是 list/dict/set/str 这类容器\n"
        "# not 是「布尔取反」，右边是单个布尔值\n"
        "# path.exists() 返回 True/False，不是容器，不能放在 not in 右边",
        "条件判断,not,in,布尔",
    ),
    (
        # ⚠️ E26（新增）：今天真实踩过 —— save_tasks 排在了 add_task 前面
        "顺序错：先存盘后改内存 —— 存进去的是旧值",
        "save_tasks(tasks)   # ← 先写磁盘\n"
        "add_task(tasks, text)  # ← 后改内存",
        "add_task(tasks, text)   # ① 先改内存\n"
        "save_tasks(tasks)       # ② 再写磁盘\n"
        "只要数据变了就要重新存一遍，顺序不能反 —— 反了等于白存",
        "持久化,顺序,数据流",
    ),
    (
        # ⚠️ E27（新增）：今天真实踩过 —— 误删了 add 分支的 add_task
        "复制粘贴的代码块：改一处会漏另一处",
        "# add 分支里被误删了一行 add_task(tasks, text)\n"
        "# 因为 quit 分支里有一份几乎一样的代码，长得太像，改错了地方",
        "同一段逻辑只写一份，其余地方调用同一个函数：\n"
        "elif cmd == 'quit':\n"
        "    save_tasks(tasks)   # 不复制粘贴写文件的代码\n"
        "写文件、读文件、格式化输出这类操作，永远只写一份",
        "复制粘贴,代码复用,重构",
    ),
    (
        # ⚠️ E28（新增）：今天真实踩过 —— IndentationError @ 173
        "缩进栈层级不匹配 —— docstring 多缩进一层就报 IndentationError",
        "if cmd.startswith('add '):\n"
        "    if len(cmd) > 4:\n"
        "        \"\"\"\n"
        "        这里缩进 16 格了\n"
        "        \"\"\"\n"
        "    add_task(tasks, text)   # ← 这行回到 12 格，栈里没有 → 报错",
        "Python 的缩进是「层级栈」，不是「对齐美观」：\n"
        "同一层级必须缩进完全相同，多一格少一格都算新的层级\n"
        "另外：放在 if 分支里的 docstring 只是没用上的字符串字面量，别放那儿",
        "缩进,IndentationError,docstring",
    ),
]

# 今天的 E01 又犯了（函数分支没写 return → 返回 None → len(None) 报 TypeError）
REGRESS_NOTE = "又犯了：load_tasks 的分支没写 return，返回 None 导致 len(None) 报 TypeError"


# ============================================================
# 调追踪器的通用包装
# ============================================================
def run(args):
    """执行一条 错题追踪器.py 命令，返回 (退出码, 标准输出, 标准错误)。

    逐行拆解：
        subprocess.run([PY, str(TRACKER)] + args, ...)
          └─ [PY, str(TRACKER)] + args = 列表相加，把两个列表拼成一个
             完整命令行：python 追踪器.py add 标题 错误写法 正确写法 标签
          └─ 关键：因为传的是【列表】而不是一整条字符串，
             subprocess 不经过 shell，参数原样送达 —— 引号、换行、
             反斜杠都不会被吃掉（这正是要用脚本而不是手敲的原因）

        capture_output=True = 把 stdout 和 stderr 收进返回值，
                               不往终端打印（我们要先处理再决定怎么显示）
        text=True            = 把收到的 bytes 自动解码成 str
        encoding="utf-8"     = 明确用 UTF-8 解码，中文才不会乱码
                               （⚠️ 依赖系统默认编码是常见的翻车点）

        r.returncode = 进程的退出码（0 = 成功，非 0 = 失败）
        r.stdout.strip() = 去掉首尾空白，让输出干净点
    """
    r = subprocess.run([PY, str(TRACKER)] + args, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


# ============================================================
# 主流程：逐条登记
# ============================================================
def main():
    """把 NEW_ERRORS 里的每条都 add 进去，最后给 E01 记一次 fail。

    逐行拆解：
        ok = True = 记一个「全部成功」的标记
          └─ 用来做最后的退出码：只要有一条失败，整体就算失败

        for title, wrong, right, tags in NEW_ERRORS:
          └─ for 循环直接【拆元组】：每次循环把 4 个元素分别绑到 4 个变量名
          └─ 顺序必须和建元组时一致：标题、错误写法、正确写法、标签

        code, out, err = run([...])
          └─ 左边 3 个变量对应右边返回的 3 个值（元组解包）

        status = "OK " if code == 0 else "[X]"
          └─ 三元表达式：退出码 0 就是成功

        if code != 0: ok = False
          └─ 有一条失败就把标记翻成 False，但【继续往下跑】
            —— 别的条目还是值得登记，不能因为一条失败就全停

        out.splitlines()[0] = 按行切分取第一行（只要摘要，不用全贴）
          └─ 三元表达式再套一层：万一 out 是空串，splitlines() 返回空列表，
            取 [0] 会 IndexError，所以先判断有没有行

        sys.exit(0 if ok else 1)
          └─ 退出码给外层看：0 = 全成功，1 = 有失败
          └─ 为什么要设这个？因为如果用 CI / 自动化调用，
            退出码是唯一的「成功失败」信号
    """
    ok = True
    for title, wrong, right, tags in NEW_ERRORS:
        # ["add", 标题, 错误写法, 正确写法, 标签] —— 正好是追踪器 add 命令的格式
        code, out, err = run(["add", title, wrong, right, tags])
        status = "OK " if code == 0 else "[X]"
        if code != 0:
            ok = False
        print(f"{status} {title}")
        if out:
            print(f"     {out.splitlines()[0] if out.splitlines() else out}")
        if err:
            print(f"     stderr: {err.splitlines()[0]}")

    print()
    # record = 记录一次复习结果。E01 今天在写代码时又犯了，
    # 记 fail 会让它的「连续答对」计数清零 → 下周四必然排进卷子
    code, out, err = run(["record", "E01", "fail", REGRESS_NOTE])
    print(("OK " if code == 0 else "[X]") + " E01 记一次 fail（今天又犯）")
    if out:
        for line in out.splitlines():
            print("     " + line)
    if err:
        print("     stderr: " + err.splitlines()[0])

    sys.exit(0 if ok else 1)


# __name__ == "__main__" = 只在【直接运行】这个文件时才执行 main()
#   └─ 被 import 时不执行，别人可以安全地 import 里面的函数
if __name__ == "__main__":
    main()
