# -*- coding: utf-8 -*-
"""
10.31 变式练习 —— E24 / E27（防照抄版，约 25 分钟）

为什么要有这个文件：
    10.30练习_E24_E27.py 的答案，我在 10.30练习_改bug.py 里已经给过你了。
    再让你原样抄一遍，等于测的是「记不记得」，不是「懂不懂」。
    所以这个文件全是【新场景】，没有现成答案可抄。

要记的两件事：
    E24  open(path, 'w') 的破坏性发生在【开门那一刻】，不是写入那一刻
    E27  同一段逻辑只写一份 —— 出现第 3 份的时候，更要想抽函数
"""

import json
import os


# ============================================================
# 变式 1【E24】不是照着写，是推出来
# ============================================================
# 场景：下面这段代码已经写好了。请你【推】它在三种情况下各会留下什么。
#
# def 保存(path, 数据):
#     with open(path, "w", encoding="utf-8") as f:
#         f.write(json.dumps(数据))
#
# 情况①  数据 = {"任务": ["买菜"]}（正常）        → 文件内容是？
# 答："任务": ["买菜"]
#     ← ✅ 对（完整的是 {"任务": ["买菜"]}）
#
# 情况②  数据 = {"标签": {"今天", "必须"}}（set）
#        json.dumps 会在写文件时崩（TypeError）    → 文件里留下什么？
# 答：空
#     ← ✅ 对！这就是 E24 的命门：文件被清空成【0 字节】，旧数据没了，
#        而且【没有任何报错提示你数据丢了】—— 只有程序自己知道出了事。
#
# 情况③  磁盘写到一半满了，f.write 只落下一半      → 文件里留下什么？
# 答：不知道
#     ← 🟡 正确答案是【半截 JSON】：文件不为空，但内容不完整，
#        之后 json.load(f) 会抛 JSONDecodeError。
#        ⚠️ 对比一下这两种坏法（很重要）：
#            0 字节  → 一眼看出坏了（文件是空的）
#            半截 JSON → 更阴险（看起来有内容，其实是废的）
#        两种都是「静默错误」—— 所以光看「文件存在」不能代表数据是好的。
#
# ------------------------------------------------------------------
# 接着回答：
#
# (1) 这段代码的问题出在哪【一行】？正确顺序应该是什么？
#     （提示：先算内容再开门，还是先开门再算内容？）
# 答：先算后开门
#     ← ✅ 对！这就是 E24 的正解：东西没备好，就别开门。
#
# (2) 'w' / 'a' / 'r' 三种模式，对【已经存在的文件】分别做什么？
#     'w' →写入
#     'a' →不知道
#     'r' →读取
#     ← 🟡 'r' 对、'w' 方向对但不完整、'a' 没答上来。完整版：
#       'w' → 不存在则【创建】；存在则【清空】再写（破坏性！）
#       'a' → 不存在则【创建】；存在则在【末尾追加】，不清空（这就是它跟 w 的唯一区别）
#       'r' → 【只读】，打开时不会动文件内容
#       'x' → 不存在才创建（已存在直接报错，防误覆盖，用得少但要知道）
#       'b' → 二进制
#
# (3) 为什么「备份/追加」必须用 'a'，不能用 'w'？一句话。
# 答：用w会清空
#     ← ✅ 对
#
# (4) 如果我只是想让代码「别把旧数据弄丢」，最低成本的改法是什么？
#     （就改一行 / 一行代码）
# 答：忘了
#     ← 🟡 其实就【挪一行位置】，代码一个字都不用改：
#
#         def 保存(path, 数据):
#             内容 = json.dumps(数据, ensure_ascii=False)   # ← 先算（崩也不碰文件）
#             with open(path, "w", encoding="utf-8") as f:   # ← 再开门
#                 f.write(内容)
#
#         💡 你 (1) 答的「先算后开门」和这题问的是同一件事 ——
#            你答对了【原理】，只是没把它落成【代码】。
#            这就是「骨架对、细节缺」：原理通了，动手写的时候手跟不上。
#
# 🆕 附加一问（E24 的灵魂，答对了这题 E24 就算过）：
#
# (5) 这段代码里，【旧数据】是在哪一刻被弄没的？
#     注意问的不是「哪一行代码写错了」，而是「哪个时刻」
#     答：w的时候被清空了
#     ← ✅ 对！这就是 E24 的灵魂。
#        精确版：旧数据是在 open(path,'w') 【开门那一刻】没的 ——
#        不是 json.dumps 崩的那一刻，也不是 f.write 失败的那一刻。
#        我实测给你看（一个字都没写！）：
#            开门前: [原来的数据] 17 bytes
#            开门后（一个字没写）: '' 0 bytes
#        → 连一行字都不写，文件已经空了。
#
#        💡 这就是为什么「先算后开门」能救命：
#           崩在 json.dumps → 门还没开 → 旧数据安然无恙
#           崩在 f.write    → 门开了 → 旧数据已经没了（顶多剩半截）
#
#        🆕 由此推出一条通用心法（E24 带走）：
#           「会破坏数据的动作 = open('w')、os.remove、shutil.rmtree」
#           → 它们不是「写」的动作，是【开门/拆房】的动作。
#           → 所以规矩是：破坏性动作尽量【排最后】，先备好内容再开门。
# ============================================================


# ============================================================
# 变式 2【E27】这里有三份复制粘贴
# ============================================================
# 下面是【故意写成复制粘贴版】的三个函数。
# 注意：10.30 那份只有两份（add_task / mark_done），这次多了一个 delete_task。
# 复制粘贴写到第 3 份的时候，漏改的地方会更多 —— 这就是 E27 的痛点。
# 你的任务（4 步）：
#   ① 指出重复的写文件代码在【哪几行】（行号写出来）
#   ② 抽成一个函数（自己起名）
#   ③ 改写这三个函数，让它们【调用】这个函数
#   ④ 把原来那三份重复代码【全部删掉】
#
# 验收：改完之后，这三个函数体里都不能再出现 with open
#
# ⚠️ add_task / mark_done / delete_task 自己的业务逻辑是对的，别动它们，
#    你只处理【写文件】这一块。
# ---------------------------------------------------------------

DATA_FILE = "todos.json"

# 🔴 你 11-01 写的原版（保留对照）：
#
# def 保存文件(tasks, path="todos.json"):
#     tmp = path + ".tmp"                        # 临时文件，必须和正式文件同目录
#     try:
#         with open(tmp, "w", encoding="utf-8") as f:
#             f.write(json.dumps(tasks, ensure_ascii=False))
#         os.replace(tmp, path)                  # 写【成功】了才替换正式文件
#     except Exception:
#         if os.path.exists(tmp):
#             os.remove(tmp)                     # 崩了清理垃圾，不留 .tmp
#         raise
#
# ✅ 批改：结构【全对】—— os.replace 在 with 外面（Windows 上能跑）、原子替换、
#          清 tmp、raise，四件事一个不缺。上一次练习A 那个 WinError 32 你避开了 👏
#
# 🔴 但有一个真 bug：默认参数 path="todos.json" 把【路径焊死】了。
#
#    自测_变式2 会做这件事：
#        global DATA_FILE
#        DATA_FILE = os.path.join(work, "todos.json")   ← 改成临时目录里的路径
#    然后期望 add_task 写到【新的 DATA_FILE】。
#    但你的 保存文件(tasks) 走的是默认值 "todos.json"（相对路径 = 当前目录），
#    结果：数据写到了【项目目录根下】，而自测去临时目录找 → 找不到 → ❌失败。
#
#    实测（我跑过）：
#        ✅ add_task 里没有 with open 了
#        ✅ mark_done 里没有 with open 了
#        ✅ delete_task 里没有 with open 了
#        ❌ 检查③失败：文件根本没生成
#        （然后项目根目录多出一个 todos.json —— 就是它跑偏留下的）
#
#    ⚠️ 原理：默认参数是在【函数定义那一刻】求值的，不是调用时。
#              def f(path=DATA_FILE) → 此刻的 "todos.json" 被永久焊进函数里，
#              后面谁改 DATA_FILE 都不影响 f。
#              def f(path=None)      → 每次调用时再判断，才跟得上变化。
#
#    这就是「配置/路径」类参数必须用 None 占位的原因 —— 记下来，E29。


def 保存文件(tasks, path=None):
    """全文件唯一一份写文件的代码（原子写入）。"""
    if path is None:
        path = DATA_FILE          # ← 运行时才读全局，改了 DATA_FILE 才生效
    tmp = path + ".tmp"           # 临时文件，必须和正式文件同目录
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(tasks, ensure_ascii=False))
        os.replace(tmp, path)      # 写【成功】了才替换正式文件（原子）
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)         # 崩了清理垃圾，不留 .tmp
        raise


def add_task(tasks, text):
    """加一条任务。

    ✅ 写文件的代码已抽走，这里只管业务逻辑。
    """
    tasks.append({"text": text, "done": False})

    保存文件(tasks)

    return tasks


def mark_done(tasks, n):
    """把第 n 条任务标记为已完成。

    ✅ 写文件的代码已抽走，这里只管业务逻辑。
    """
    if not isinstance(tasks, list):
        return "错误：tasks 必须是列表"
    if not isinstance(n, int):
        return "错误：n 必须是整数"
    if n < 1 or n > len(tasks):
        return f"错误：n 必须在 1~{len(tasks)} 之间"

    tasks[n - 1]["done"] = True

    保存文件(tasks)

    return tasks


def delete_task(tasks, n):
    """删掉第 n 条任务。

    ✅ 写文件的代码已抽走，这里只管业务逻辑。
    """
    if not isinstance(tasks, list):
        return "错误：tasks 必须是列表"
    if not isinstance(n, int):
        return "错误：n 必须是整数"
    if n < 1 or n > len(tasks):
        return f"错误：n 必须在 1~{len(tasks)} 之间"

    del tasks[n - 1]

    保存文件(tasks)
    return tasks


# ---------------------------------------------------------------
# ⬇️⬇️⬇️ 你的答案写在这里 ⬇️⬇️⬇️
# ---------------------------------------------------------------
#
# ① 重复的写文件代码在第 _88，89___ 行、第 __108，109__ 行、第 __128，129__ 行
#
# ② 抽出来的函数：
#
#    def _保存文件（tasks）：
#           tmp = path + ".tmp"
#     try:
#         with open(tmp, "w", encoding="utf-8") as f:
#             f.write(json.dumps(tasks, ensure_ascii=False))
#         # ↑ 到这里 with 已经结束，tmp 文件【已经关闭】，Windows 才肯让我们替换它
#         os.replace(tmp, path)              # 写【成功】了才替换正式文件（原子）
#     except Exception:
#         if os.path.exists(tmp):
#             os.remove(tmp)                 # 崩了清理垃圾，不留 .tmp
#         raise
#
#
# ③ 改写后的三个函数：
#
#    def add_task(tasks, text):
#       tasks.append({"text": text, "done": False})
#       保存文件（tasks）
#
#     return tasks
#
#    def mark_done(tasks, n):
#            if not isinstance(tasks, list):
#         return "错误：tasks 必须是列表"
#     if not isinstance(n, int):
#         return "错误：n 必须是整数"
#     if n < 1 or n > len(tasks):
#         return f"错误：n 必须在 1~{len(tasks)} 之间"
#
#     tasks[n - 1]["done"] = True
#
#     保存文件（tasks）
#
#     return tasks
#


#    def delete_task(tasks, n):
#           if not isinstance(tasks, list):
#         return "错误：tasks 必须是列表"
#     if not isinstance(n, int):
#         return "错误：n 必须是整数"
#     if n < 1 or n > len(tasks):
#         return f"错误：n 必须在 1~{len(tasks)} 之间"
#
#     del tasks[n - 1]
#
#     保存文件（tasks）
#
#     return tasks
#
# ④ 改完后，这三个函数体里 with open 出现次数：____ （应该是 0）
#    抽出来的那个函数里 with open 出现次数：____ （应该是 1）
#
# ⬇️⬇️⬇️ 在上面写代码 ⬇️⬇️⬇️


# ============================================================
# 变式 2 · 自动自测（写完上面三个函数再跑）
# ============================================================
def 自测_变式2():
    """检验：三份复制粘贴有没有真的抽成一份，功能还在不在。"""
    import inspect
    import shutil
    import tempfile

    print("---- 检查①：三个函数体里还有没有 with open ----")
    for 函数名 in ("add_task", "mark_done", "delete_task"):
        源码 = inspect.getsource(eval(函数名))
        if "with open" in 源码:
            print("❌ %s 里还有 with open，重复代码没抽干净" % 函数名)
        else:
            print("✅ %s 里没有 with open 了" % 函数名)

    print()
    print("---- 检查②：全文件里应该【只剩 1 份】with open ----")
    # ⚠️ 2026-11-01 批改时把这个检查改好了：
    #    原来我写死了候选名单 ("save_tasks", "保存任务", "写文件")，
    #    你把函数起名叫「保存文件」→ 检查② 直接找不到人，还报 ⚠️ —— 假警报。
    #    教训：检查逻辑不能靠【猜函数名】，要靠【特征】去找。
    #    这里改成：扫描本文件里所有函数，谁的源码里带 with open 谁就是那唯一一份。
    import sys as _sys
    本模块 = _sys.modules[__name__]
    带open的 = []
    for 名, 函 in inspect.getmembers(本模块, inspect.isfunction):
        if 名.startswith("自测"):
            continue                       # 自测代码自己要用 with open，不算
        if "with open" in inspect.getsource(函):
            带open的.append(名)
    if len(带open的) == 1:
        print("✅ 检查②通过：全文件只有 %s 里留着 with open（唯一那一份）" % 带open的[0])
    elif len(带open的) == 0:
        print("❌ 检查②失败：一份 with open 都没有 —— 你是不是把写文件的代码删没了？")
    else:
        print("❌ 检查②失败：还有 %d 处 with open（%s），重复没抽干净"
              % (len(带open的), "、".join(带open的)))

    print()
    print("---- 检查③：功能还在不在（加任务 → 标记完成 → 删除 → 读回来）----")
    work = tempfile.mkdtemp()
    global DATA_FILE
    原来的 = DATA_FILE
    DATA_FILE = os.path.join(work, "todos.json")
    try:
        tasks = []
        tasks = add_task(tasks, "写作业")
        tasks = add_task(tasks, "跑步")
        tasks = add_task(tasks, "洗澡")
        tasks = mark_done(tasks, 1)
        tasks = delete_task(tasks, 2)
        print("内存里的任务: %s" % tasks)
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, encoding="utf-8") as f:
                盘上 = json.load(f)
            print("磁盘上的任务: %s" % 盘上)
            if len(盘上) == 2 and 盘上[0]["done"] is True and 盘上[0]["text"] == "写作业":
                print("✅ 检查③通过：三个功能 + 存盘，全部正常")
            else:
                print("❌ 检查③失败：磁盘内容不对（期望 2 条，第1条已完成且是'写作业'）")
        else:
            print("❌ 检查③失败：文件根本没生成")
    finally:
        DATA_FILE = 原来的
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 60)
    print("10.31 变式 · E24 / E27")
    print("=" * 60)
    print()
    print("⚠️ 先把变式1 的问答和变式2 的代码写完，再来跑自测。")
    print()
    print("---- 变式 2 自测 ----")
    自测_变式2()
    print()
    print("=" * 60)
    print("写完后对答案：笔记/10-30_答案与讲解_E24_E27.md")
    print("=" * 60)
