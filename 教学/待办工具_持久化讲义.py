# 待办工具_持久化讲义.py
# 2026-10-29 上午任务：给「待办工具」加上文件持久化雏形
#
# 用法：① 先读完【讲义】→ ② 补【作业】里的留白 → ③ 跑【验收测试】
# 已有底稿：练习/待办工具.py（add_task / list_tasks / mark_done / run_cli 都写好了）
#
# ⚠️ 这是「只读讲义」，别在这里写答案。
#    你的答案写在 → 练习/待办工具_持久化.py

import json
import os
from os import path

DATA_FILE = "todos.json"


# ============================================================
# 【讲义 1】为什么内存存不住
# ============================================================
print("=" * 58)
print("讲义 1：为什么「存一下」必须靠文件")
print("=" * 58)
print()
print("你现在的 run_cli() 里有一行：tasks = []")
print("这行在【程序启动时执行一次】，tasks 是内存里的一个空列表。")
print()
print("  你 add 了 3 条任务 → 它们确实在 tasks 里 → list 能打印出来")
print("  但你输入 quit → 函数返回 → 内存被回收 → tasks 没了")
print()
print("  结论：内存 = 活着的时候才有，程序一关就清零。")
print("        想让任务活过这次运行，必须【写到磁盘】，下次再【读回来】。")
print()
print("  这就是「持久化」：内存态 → 磁盘态 → 内存态 的一个来回。")
print()


# ============================================================
# 【讲义 2】存成什么格式？为什么是 JSON
# ============================================================
print("=" * 58)
print("讲义 2：存成什么格式")
print("=" * 58)
print()
print("你的 tasks 长这样（一个 list，里面装 dict）：")
print('    [{"text": "写作业", "done": False}, {"text": "跑步", "done": True}]')
print()
print("三个候选：")
print()
print("  A. 纯文本 txt，每行一条")
print('     写作业|FALSE')
print("     ✅ 人能直接看懂            ❌ 存不了 done 以外的字段")
print("     ❌ 任务文字里有 '|' 就乱了   ❌ 以后想加优先级/时间戳要重写")
print()
print("  B. JSON")
print('     [{"text": "写作业", "done": false}]')
print("     ✅ 标准库自带 json 模块（你 10-27 已经学过）")
print("     ✅ list/dict 原样存取，结构不丢")
print("     ✅ 以后想加字段直接加         ← 选它")
print()
print("  C. 自己造格式")
print("     ❌ 纯属重复造轮子")
print()
print("  你已经学过的两个工具（复习一下，今天直接用）：")
print("    教学/标准库1_json.py    → json.dumps / json.loads / ensure_ascii=False")
print("    教学/标准库3_os_path.py → path.join / path.exists")
print()


# ============================================================
# 【讲义 3】两个函数长什么样
# ============================================================
print("=" * 58)
print("讲义 3：save_tasks / load_tasks 的职责")
print("=" * 58)
print()
print("  save_tasks(tasks)  内存 → 磁盘   「把列表存起来」")
print("  load_tasks()       磁盘 → 内存   「把列表读回来」")
print()
print("  写文件三步：")
print("    1. 打开文件  open(DATA_FILE, \"w\", encoding=\"utf-8\")")
print('    2. 写内容    f.write(json.dumps(tasks, ensure_ascii=False))')
print("    3. 关文件    with 语句会自动帮你关")
print()
print("  读文件三步：")
print("    1. 判断在不在 path.exists(DATA_FILE) —— 第一次运行时它不存在")
print("    2. 读内容    f.read()")
print("    3. 变回列表  json.loads(字符串)")
print()
print("  ⚠️ 今天的三个高频考点（都在你错题本里）：")
print("     E21  json.dumps 忘写 ensure_ascii=False → 中文变 \\uXXXX")
print("     E13  字符串方法返回【新值】，不改原变量 → 别以为 dumps 改了 tasks")
print("     E17  浅拷贝 → dict(a) 只复制外层")
print("     E19  strip 后可能是空串 → 空文件被 json.loads 会直接崩")
print()


# ============================================================
# 【作业】留白区 —— 这里你自己写
# ============================================================

# ---------- 作业 1：save_tasks(tasks) ----------
def save_tasks(tasks):
    """把 tasks 列表存进 DATA_FILE。

    提示：
      · 用 with open(DATA_FILE, "w", encoding="utf-8") as f:
      · 写进去的是 json.dumps(tasks, ensure_ascii=False)
      · 别忘 ensure_ascii=False，否则中文变成 \\uXXXX（E21）
    """
    # ← 作业 1：在这里写
    pass


# ---------- 作业 2：load_tasks() ----------
def load_tasks():
    """从 DATA_FILE 读回 tasks 列表。

    提示（按顺序想）：
      1. 如果文件不在        → 返回 []（第一次运行必须这样，否则崩）
      2. 读出字符串          → f.read()
      3. 如果读出来是空字符串 → 返回 []（别直接丢给 json.loads，会抛异常）
      4. 否则 json.loads(字符串) → 返回列表
    """
    # ← 作业 2：在这里写
    pass


# ---------- 作业 3：接进 run_cli ----------
def run_cli_persistent():
    """带持久化的主函数：启动时读，退出时写。

    提示（要改两处）：
      A. 函数第一行：tasks = load_tasks()   ← 启动时读回来
         （原来的 tasks = [] 要换掉，否则永远是空的）
      B. quit 那一支：save_tasks(tasks) 之后再 print("再见！")
         （一定要【先存再退出】，顺序反了就存了个空）
      C. 原来那个 tasks = [] 那行删掉
    """
    tasks = []
    print("=== 极简待办工具（带持久化）===")
    print(f"已从 {DATA_FILE} 载入 {len(tasks)} 条任务")
    print("命令：add <任务> / list / done <编号> / quit")

    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue

        if cmd == "quit":
            # ← 作业 3：在这里补 save_tasks(tasks)
            print("再见！")
            break
        elif cmd == "list":
            list_tasks(tasks)
        elif cmd.startswith("add "):
            text = cmd[4:]
            add_task(tasks, text)
            save_tasks(tasks)          # ← 建议：每次改动都存一下
            print(f"已添加：{text}")
        elif cmd.startswith("done "):
            n = int(cmd[5:])
            mark_done(tasks, n)
            save_tasks(tasks)          # ← 建议：每次改动都存一下
            print(f"已完成第 {n} 条")
        else:
            print("未知命令，输入 add / list / done / quit")


# ---------- 把练习/待办工具.py 里的三个函数原样搬过来 ----------
def add_task(tasks, text):
    """把一条任务（dict）加到 tasks 列表，返回新列表"""
    tasks.append({"text": text, "done": False})
    return tasks


def list_tasks(tasks):
    """打印所有任务；空列表提示'暂无任务'"""
    if not tasks:
        print("暂无任务")
        return
    for i, t in enumerate(tasks, 1):
        status = "已完成" if t["done"] else "未完成"
        print(f"{i}. {t['text']} [{status}]")


def mark_done(tasks, n):
    """把第 n 条任务标记为已完成（n 从 1 开始计）"""
    if not isinstance(tasks, list):
        return "错误：tasks 必须是列表"
    if not isinstance(n, int):
        return "错误：n 必须是整数"
    if n < 1 or n > len(tasks):
        return f"错误：n 必须在 1~{len(tasks)} 之间"
    tasks[n - 1]["done"] = True
    return tasks


# ============================================================
# 【验收测试】写完作业后，把下面这行取消注释，逐条验证
# ============================================================

# if __name__ == "__main__":
#     run_cli_persistent()
