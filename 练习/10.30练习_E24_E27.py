# 10.30 练习 · E24 + E27（今天两道必做题）
# 2026-10-30 · 阶段1 第5周 · 上午任务（复习补讲）
#
# ---------------------------------------------------------------
# ⚠️ 这个文件是给你【动手写】的，不是给你看的。
#    答案在：笔记/讲义/10-30_答案与讲解_E24_E27.md
#    ⚠️ 先写完再去看答案。先看答案 = 没练。
#
# 今天要练的两个点：
#   E24  open(path,'w') 是「开门」不是「存东西」→ 改【顺序】/ 原子替换
#   E27  同一段 with open(...) 出现第二次就该抽成函数
#
# 讲义：笔记/讲义/10-30_补讲_E24_E27.md
#
# 📋 11-01 批改结果：
#   E24 🔴 fail —— 写法C 的结构你写对了（tmp → os.replace → 清 tmp → raise），
#                  但 os.replace 写在了 with 【里面】，Windows 上每次都炸
#   E27 ✅ pass —— 抽函数这件事做对了（两份 with open 全消失，全文只剩 1 份）
#   批改已写回本文件：你的原答案全部保留为注释，正确版本在下面。
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
    # 🔴 你 11-01 写的原版（保留对照）—— 结构完全正确，只错一处「时机」：
    #
    #     tmp = path + ".tmp"
    #     try:
    #         with open(tmp, "w", encoding="utf-8") as f:
    #             f.write(json.dumps(tasks, ensure_ascii=False))
    #             os.replace(tmp, path)      # ←🔴 就在这里！文件还开着就 replace
    #     except Exception:
    #         if os.path.exists(tmp):
    #             os.remove(tmp)
    #         raise
    #
    #     实测（Windows 10/11）：
    #         PermissionError: [WinError 32] 另一个程序正在使用此文件，
    #         进程无法访问：'xxx.tmp' -> 'xxx.json'
    #
    #     也就是说：这版代码【存成功的那条路】永远炸，只有 json.dumps
    #     先崩的时候才「表现得正常」—— 是不是很讽刺？
    #
    # ⚠️ 为什么官方自测还是全绿？
    #     因为 自测_练习1 只喂了「会崩的数据」，走的是 json.dumps 先崩那条路，
    #     压根没测过「存成功」！  ← 这就是【测试覆盖不全】的典型假绿
    #     （教训：自测全绿 ≠ 代码对，一定要有一条「成功路径」的用例）
    #
    # ⚠️ 为什么 Windows 会这样、Linux 不会？
    #     Windows 上文件被打开时，句柄默认【不允许被重命名/替换】（没有 FILE_SHARE_DELETE）
    #     → 文件还开着就 os.replace → 被系统拒绝 (WinError 32)
    #     Linux 上文件句柄和文件名是分开的，unlink 一个还开着的文件完全没问题。
    #     ⚠️ 所以这种 bug 在你本机一测就炸，别人写博客/教程可能还是对的 ——
    #        「我这里能跑」不等于「到处都能跑」。
    #
    # ✅ 修正版：with 结束（= 文件已关闭）之后，再 os.replace
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(tasks, ensure_ascii=False))
        # ↑ 到这里 with 已经结束，tmp 文件【已经关闭】，Windows 才肯让我们替换它
        os.replace(tmp, path)              # 写【成功】了才替换正式文件（原子）
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)                 # 崩了清理垃圾，不留 .tmp
        raise                              # 必须再抛出，不然调用方以为存成功了


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


def 自测_练习1_成功路径():
    """🔴 补测：官方自测漏掉的「存成功」那条路。

    没有这一条，os.replace 写在 with 里面这种 bug 照样能骗过自测（全绿）。
    """
    import shutil
    import tempfile

    work = tempfile.mkdtemp()
    path = os.path.join(work, "todos.json")
    try:
        try:
            save_tasks([{"text": "买菜", "done": False}], path)
        except Exception as e:
            print("❌ 成功路径失败：%s: %s" % (type(e).__name__, e))
            print("   → 存盘这条路是坏的！去看 os.replace 是不是写在 with 里面")
            return

        if not os.path.exists(path):
            print("❌ 成功路径失败：文件根本没生成")
            return
        内容 = open(path, encoding="utf-8").read()
        if "买菜" in 内容:
            print("✅ 成功路径通过：数据真的写进去了（%s）" % 内容)
        else:
            print("❌ 成功路径失败：文件内容不对 → %s" % 内容)
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


# 🔴 你 11-01 写的原版（保留对照）：
#
# def a(tasks):
#     with open(DATA_FILE, "w", encoding="utf-8") as f:
#         f.write(json.dumps(tasks, ensure_ascii=False))
#
# ✅ 批改：
#   · E27 的核心你做对了 ✅ —— 两份 with open 都从函数体里消失了，
#     全文只剩 1 份（官方自测 检查① 检查①b 检查② 全过）
#   · 但有两个扣分点：
#     ① 函数名 a 没有含义。抽函数是为了【复用】，名字得让人一眼看懂
#        （a / f / tmp 这种名字，抽出来也没人敢用）
#     ② 更要紧：抽出来的这一份是【裸 open('w')】—— E24 的老坑原封不动
#        搬进了新函数。你练习 1 刚写好的安全版 save_tasks 就摆在上面，
#        却没复用它。
#        「抽函数」只做了一半：既要【只写一份】，这一份还得【是对的】。
#        （真实项目里最常见的事故：抽出去了，但抽出来的是那个有 bug 的版本）


def 保存任务(tasks, path=None):
    """把 tasks 存盘 —— 全文件唯一一份写文件的代码。

    ⚠️ 注意这里为什么用 path=None 而不是 path=DATA_FILE：
        默认参数【在函数定义时】就绑定了当时的值。
        写成 path=DATA_FILE，等于把此刻的 "todos.json" 焊死进函数里；
        后面测试里改 DATA_FILE 就【不影响】这个函数 → 存到错地方去。
        用 path=None + 运行时再读 DATA_FILE，才是活的。
    """
    if path is None:
        path = DATA_FILE          # 运行时才读全局，改了 DATA_FILE 才生效
    save_tasks(tasks, path)       # 复用练习1 的原子写入，不重复写文件逻辑


def add_task(tasks, text):
    """加一条任务。

    ✅ 写文件的代码已抽走，这里只管业务逻辑。
    """
    tasks.append({"text": text, "done": False})

    保存任务(tasks)

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

    保存任务(tasks)

    return tasks


# ---------------------------------------------------------------
# ⬇️⬇️⬇️ 你的答案区（11-01 批改后补全） ⬇️⬇️⬇️
# ---------------------------------------------------------------
#
# 【你的答案区 · 按这 4 步写】
#
# ① 重复的写文件代码在第 ____ 行 和 第 ____ 行
#    → 原稿：第 165-166 行（add_task 里）、第 186-187 行（mark_done 里）
#    （你现在写的是自己文件里的行号，标对位置就行 ✅）
#
# ② 抽出来的函数：保存任务（内部复用练习1 的 save_tasks）
#
# ③ 改写后的 add_task / mark_done：见上（只留业务逻辑 + 调用 保存任务(tasks)）
#
# ④ 改完后全文 with open 出现的次数：__1__ （应该是 1）  ← ✅ 你写对了
#    原来两处重复的代码你删了吗？__删了__ （应该是「删了」）  ← ✅ 你写对了
#
# ⚠️ 但 ① ② ③ 你没填 —— 「抽函数」这个动作本身你做对了，
#    可「为什么抽、抽成什么样」没写下来 = 没进脑子里。
#    这正是巩固清单第五节的结论：
#      「写下来的那部分，才是真正记住的那部分。」
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
# 🎯 E24 补救小测（做完这 3 行，你就能补回 1 次 pass → 1/2）
# ============================================================
# 📋 11-01 批改：3 个答案【全对】，但—— 这个小测作废了，是我的锅。
#     因为这 3 个答案就写在本文件里（第 88-89 行、第 94-97 行、第 111 行），
#     你抄了一遍而已，等于【什么都没测】。
#     抄 = 「读懂」，≠ 「自己想得出来」。
#     → 所以 E24 的 pass 不在这儿拿，在【变式】那份文件里拿（那里没有答案可抄）。
#
# (1) 你原来那版把 os.replace 写在 with 【里面】，在 Windows 上会报什么错？
#     （提示：错误码是 WinError 32）
#     答：另一个程序正在使用此文件                      ← ✅ 意思对
#     （完整的报错是：PermissionError: [WinError 32] 另一个程序正在使用此文件，
#       进程无法访问：'xxx.tmp' -> 'xxx.json'
#       答全一点要带：① 异常类型 PermissionError ② 错误码 WinError 32）
#
# (2) 为什么官方自测 全绿，却没发现这个 bug？一句话。
#     答：因为 自测_练习1 只喂了会崩的数据（那个 set），走的是「json.dumps 先崩」那条路 —— 压根没测过「存成功」。
#     ← ✅ 对（但这句是我批注里的原话，属于抄）
#
# (3) 修正版为什么要把 os.replace 挪到 with 【外面】？一句话。
#     答：with 结束 = 文件已关闭 = Windows 才肯放行
#     ← ✅ 对（同样是抄我批注里的原话）
#
# ⚠️ 这三条抄完之后，请你自己重新回答一遍【不看本文件】：
#     把手机/文件关掉，凭记忆写出：① 报的什么错 ② 为什么不报错 ③ 为什么要挪出去
#     写出来的才是你的。写不出来也没关系 —— 那就说明这题还没过。
# ============================================================


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
    print("---- 练习 1 补测（成功路径 · 官方自测漏掉的那条）----")
    自测_练习1_成功路径()
    print()
    print("---- 练习 2 自测 ----")
    自测_练习2()
    print()
    print("=" * 60)
    print("写完之后：去 笔记/讲义/10-30_答案与讲解_E24_E27.md 对答案")
    print("=" * 60)
