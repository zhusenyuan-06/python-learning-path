"""把 2026-10-29 当天新犯的错登记进错题追踪池。

为什么要用脚本而不是手敲命令：
  错题写法里有引号、换行、反斜杠，手敲 bash 参数容易被 shell 吃掉。
  这里用 subprocess 传数组，参数原样送达。

只做一件事：调 add 命令。JSON 是唯一真源，追踪器自己负责写。
"""
import subprocess
import sys
from pathlib import Path

PY = r"D:\AAAA\python.exe"
TRACKER = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记\错题追踪器.py")

# (标题, 错误写法, 正确写法, 标签)
NEW_ERRORS = [
    (
        "open(path, 'w') 会先清空再写 —— 中途失败留下 0 字节文件",
        "with open(DATA_FILE, 'w', encoding='utf-8') as f:\n"
        "    f.write(json.dumps(tasks))\n"
        "# tasks 未定义 → 崩溃。但 open('w') 已经把旧文件清空了",
        "open(path,'w') 的语义是「不存在则创建 + 存在则清空」，不是「追加」。\n"
        "所以写之前必须保证待写内容已经准备好（变量有值、不依赖未定义的东西）\n"
        "另外：备份用 'a'，读用 'r'，写新内容用 'w'",
        "文件读写,持久化,w模式",
    ),
    (
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
        "顺序错：先存盘后改内存 —— 存进去的是旧值",
        "save_tasks(tasks)   # ← 先写磁盘\n"
        "add_task(tasks, text)  # ← 后改内存",
        "add_task(tasks, text)   # ① 先改内存\n"
        "save_tasks(tasks)       # ② 再写磁盘\n"
        "只要数据变了就要重新存一遍，顺序不能反 —— 反了等于白存",
        "持久化,顺序,数据流",
    ),
    (
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


def run(args):
    r = subprocess.run([PY, str(TRACKER)] + args, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main():
    ok = True
    for title, wrong, right, tags in NEW_ERRORS:
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
    code, out, err = run(["record", "E01", "fail", REGRESS_NOTE])
    print(("OK " if code == 0 else "[X]") + " E01 记一次 fail（今天又犯）")
    if out:
        for line in out.splitlines():
            print("     " + line)
    if err:
        print("     stderr: " + err.splitlines()[0])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
