# 10.30 练习 · E24 + E27（今天两道必做题）
# 2026-10-30 · 阶段1 第5周 · 上午任务（复习补讲）
#
# ---------------------------------------------------------------
# ⚠️ 这个文件是给你【动手写】的，不是给你看的。
#    答案在：笔记/10-30_答案与讲解_E24_E27.md
#    ⚠️ 先写完再去看答案。先看答案 = 没练。
#
# 今天要练的两个点：
#   E24  open(path,'w') 是「开门」不是「存东西」→ 改【顺序】/ 原子替换
#   E27  同一段 with open(...) 出现第二次就该抽成函数
#
# 讲义：笔记/10-30_补讲_E24_E27.md
# ---------------------------------------------------------------

import json
import os


# ============================================================
# 练习 1 · 写一个「崩了也绝不毁数据」的 save_tasks
# ============================================================
# ---------------------------------------------------------------
# 要求（4 条，缺一条就算没做完）：
#   ① 用【写法 C】：写临时文件 → os.replace 原子替换
#   ② 崩在【任何一步】，已有的 todos.json 都必须完好
#   ③ 崩溃时不留垃圾（不能留下 .tmp 文件）
#   ④ 函数要能指定存到哪个路径（方便你自己测的时候用临时文件）
#
# 提示：
#   · import os
#   · tmp = path + ".tmp"          ← 临时文件，必须和正式文件【同目录】
#   · os.replace(tmp, path)        ← 写成功了才替换正式文件
#   · except 里：先 os.remove(tmp)，再 raise
#     （raise 很重要！不 raise 的话，调用方以为存成功了，实际没存）
#
# ⚠️ 这段是【故意写错的】，别直接抄，看看你自己能不能一眼看出错在哪：
# ---------------------------------------------------------------
def save_tasks_错误示范(tasks, path="todos.json"):
    """❌ 这是错的示范：崩溃会毁掉旧数据。

    错在哪（自己找，找不到再看讲义）：
      · with open(path, "w") 会在【开门那一刻】把文件清空
      · json.dumps 在【开门之后】才执行 → 中间崩了就留 0 字节
      · 没有临时文件 → 没有原子替换
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks, ensure_ascii=False))
    # ⚠️ 特别注意：json.dumps(tasks) 是在 with 【里面】算的。
    #    如果 tasks 是坏的（None / 不可序列化对象），这里就崩，
    #    而文件已经被清空了。
    #    —— 这就是「开门」和「存东西」被混成一件事的代价。


# ---------------------------------------------------------------
# ⬇️⬇️⬇️ 你的答案写在这里 ⬇️⬇️⬇️
# ---------------------------------------------------------------
def save_tasks(tasks, path="todos.json"):
    """把 tasks 列表安全地写进 path。

    要求：任何一步崩溃都不破坏已有的 path 文件。

    你的实现要点（写完对照一下）：
      ① 先 json.dumps —— 还是先 open？想想 E24
      ② 临时文件叫什么名字？为什么必须同目录？
      ③ 什么时候才替换正式文件？
      ④ 崩了以后怎么清理？要不要 raise？
    """
    # ← 练习 1：在这里写
    pass


# ============================================================
# 练习 1 · 自测（写完 save_tasks 再跑这个）
# ============================================================
# 下面这个测试会故意让保存过程崩掉，然后检查你的 todos.json 有没有保住。
# ⚠️ 它用的是临时目录，不会碰你真实的 todos.json。


def 自测_练习1():
    """检验 save_tasks 是否做到了「崩了也不毁数据」。"""
    import shutil
    import tempfile

    work = tempfile.mkdtemp()
    path = os.path.join(work, "todos.json")

    try:
        # 先造一份「已有数据」
        with open(path, "w", encoding="utf-8") as f:
            f.write('[{"text": "买菜", "done": false}]')
        旧内容 = os.path.getsize(path)
        print("崩溃前: %d bytes" % 旧内容)

        # 喂一个【真的会让 json.dumps 崩掉】的东西
        # ⚠️ 为什么用 set 而不是 dict？
        #    json.dumps({"a": 1}) 是【合法的】，set 才是 JSON 不支持的类型。
        #    （TypeError: Object of type set is not JSON serializable）
        崩了 = False
        try:
            save_tasks({"任务": [{"文字": "买菜"}], "标签": {"紧急": {"今天", "必须"}}}, path)
        except Exception as e:
            崩了 = True
            print("💥 如期崩溃: %s" % e)

        if not 崩了:
            print("❌ 没有崩溃！你的 save_tasks 可能根本没写东西（还是 pass？）")
            print("   → 检查①/② 的结论无效，先把 save_tasks 写出来再说")

        # 关键检查 ①：原文件还在吗？
        if not 崩了:
            print("⏸️ 跳过检查①②（没有崩溃，测不出安全性）")
        elif os.path.exists(path):
            新大小 = os.path.getsize(path)
            if 新大小 == 旧内容:
                print("✅ 检查①通过：原文件完好（%d bytes）" % 新大小)
            else:
                print("❌ 检查①失败：原文件被破坏了（%d → %d bytes）" % (旧内容, 新大小))
        else:
            print("❌ 检查①失败：原文件直接没了")

        # 关键检查 ②：有 .tmp 残留吗？
        if 崩了:
            残留 = [f for f in os.listdir(work) if f.endswith(".tmp")]
            if 残留:
                print("❌ 检查②失败：留下垃圾文件 %s" % 残留)
            else:
                print("✅ 检查②通过：没有 .tmp 残留")

    finally:
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# 练习 2 · 抽出重复的写文件代码
# ============================================================
# ---------------------------------------------------------------
# 背景：下面这份代码是【故意写成「复制粘贴版」】的。
#       add_task 和 mark_done 各自都写了一遍写文件的代码。
#       这就是 E27 说的「复制粘贴病」。
#
# 你的任务（4 步）：
#   ① 指出重复的写文件代码在【哪几行】（把行号写在你自己的答案里）
#   ② 把这段逻辑抽成一个函数
#   ③ 改写 add_task / mark_done，让它们【调用】这个函数
#   ④ 把原来那几份重复的代码【全部删掉】（不是留着不用，是删掉）
#
# 验收：改完之后全文 grep "with open" 应该【只剩 1 处】
#
# ⚠️ 注意：add_task / mark_done 本身的业务逻辑（append / 改 done）
#    是对的，不要动它们。你只处理【写文件】这一块。
# ---------------------------------------------------------------

DATA_FILE = "todos.json"


def add_task(tasks, text):
    """加一条任务。

    ❌ 这里混进了写文件的代码（复制粘贴来的第 1 份）
    """
    tasks.append({"text": text, "done": False})

    # ❌ 重复的第 1 份写文件代码
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks, ensure_ascii=False))

    return tasks


def mark_done(tasks, n):
    """把第 n 条任务标记为已完成。

    ❌ 这里也混进了写文件的代码（复制粘贴来的第 2 份）
    """
    if not isinstance(tasks, list):
        return "错误：tasks 必须是列表"
    if not isinstance(n, int):
        return "错误：n 必须是整数"
    if n < 1 or n > len(tasks):
        return f"错误：n 必须在 1~{len(tasks)} 之间"

    tasks[n - 1]["done"] = True

    # ❌ 重复的第 2 份写文件代码（和上面那份几乎一模一样）
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(json.dumps(tasks, ensure_ascii=False))

    return tasks


# ---------------------------------------------------------------
# ⬇️⬇️⬇️ 你的答案写在这里 ⬇️⬇️⬇️
# ---------------------------------------------------------------
#
# 【你的答案区 · 按这 4 步写】
#
# ① 重复的写文件代码在第 ____ 行 和 第 ____ 行
#    （提示：一份在 add_task 里，一份在 mark_done 里）
#
# ② 抽出来的函数（自己起名，建议 save_tasks）：
#
#    def __________:
#        ...
#
# ③ 改写后的 add_task：
#
#    def add_task(tasks, text):
#        ...
#
#    改写后的 mark_done：
#
#    def mark_done(tasks, n):
#        ...
#
# ④ 改完后全文 with open 出现的次数：____ （应该是 1）
#    原来两处重复的代码你删了吗？____ （应该是「删了」）
#
# ⬇️⬇️⬇️ 在上面写代码 ⬇️⬇️⬇️


# ============================================================
# 练习 2 · 自测
# ============================================================
def 自测_练习2():
    """检验重复代码是否真的抽走了。

    检查两件事：
      ① add_task / mark_done 的【函数体里】还有没有 with open
      ② 加任务 → 存盘 → 读回来，功能还是对的
    """
    import inspect
    import shutil
    import tempfile

    # 检查 ①：只看这两个函数的源码，不看整个文件
    # （整个文件里还有错误示范 + 自测代码在用 with open，不该算进去）
    for 函数名 in ("add_task", "mark_done"):
        源码 = inspect.getsource(eval(函数名))
        if "with open" in 源码:
            print("❌ 检查①失败：%s 里还有 with open，重复代码没抽干净" % 函数名)
        else:
            print("✅ 检查①通过：%s 里没有 with open 了" % 函数名)

    # 检查 ①b：抽出来的函数里应该【有】with open（那才是唯一一份）
    if "save_tasks" in dir():
        源码 = inspect.getsource(save_tasks)
        if "with open" in 源码:
            print("✅ 检查①b通过：save_tasks 里保留着唯一那一份 with open")
        else:
            print("⚠️ 检查①b：save_tasks 里没有 with open，确认一下你抽对了没")

    # 检查 ②：功能还在不在
    work = tempfile.mkdtemp()
    global DATA_FILE
    原来的 = DATA_FILE
    DATA_FILE = os.path.join(work, "todos.json")
    try:
        tasks = []
        tasks = add_task(tasks, "写作业")
        tasks = add_task(tasks, "跑步")
        tasks = mark_done(tasks, 1)
        print("内存里的任务: %s" % tasks)
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, encoding="utf-8") as f:
                盘上 = json.load(f)
            print("磁盘上的任务: %s" % 盘上)
            if len(盘上) == 2 and 盘上[0]["done"] is True:
                print("✅ 检查②通过：加任务 + 标记完成 + 存盘，功能正常")
            else:
                print("❌ 检查②失败：磁盘内容不对")
        else:
            print("❌ 检查②失败：文件根本没生成")
    finally:
        DATA_FILE = 原来的
        shutil.rmtree(work, ignore_errors=True)


# ============================================================
# 运行入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("10.30 练习 · E24 + E27")
    print("=" * 60)
    print()
    print("⚠️ 先把上面两个练习写完，再来跑自测。")
    print()
    print("---- 练习 1 自测 ----")
    自测_练习1()
    print()
    print("---- 练习 2 自测 ----")
    自测_练习2()
    print()
    print("=" * 60)
    print("写完之后：去 笔记/10-30_答案与讲解_E24_E27.md 对答案")
    print("=" * 60)
