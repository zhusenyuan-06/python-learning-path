# _演示_open_w清空.py —— 亲眼看一次「0 字节文件」是怎么来的
# 2026-10-29 · 晚上 · 复习 E24 的配套演示
#
# ---------------------------------------------------------------
# 这个文件回答一个问题：为什么会出现 0 字节的 todos.json？
#
# 昨晚 17:29 的现场（你亲眼见过）：
#   教学/todos.json 变成 0 字节。
#   当时我们说「open(path,'w') 会先清空」——但那只是结论，不是理解。
#   今天你答 E24 时把方向搞反了（以为该把 'w' 改成 'r'），
#   说明这个知识点你**记住了结论，没理解机制**。
#
# 这个脚本做三件事，每件都真跑一遍给你看：
#   场景 A：先开文件写 → 中途崩溃 → 旧数据没了（0 字节）
#   场景 B：先把内容算好再开文件 → 中途崩溃 → 旧数据完好
#   场景 C：写临时文件再原子替换 → 中途崩溃 → 旧数据完好
#
# ⚠️ 全部在临时目录里跑，不碰你的真实 todos.json。
# ---------------------------------------------------------------

import io
import json
import os
import shutil
import tempfile

# 场景里用到的文件名
#   └─ 固定用这一个名字，让三个场景的起点完全一样，对比才公平
DATA = "todos.json"


def show(tag, path):
    """打印文件当前状态（字节数 + 内容）。

    逐行拆解：
      1. os.path.getsize(path)      → 拿文件占多少字节（0 字节就返回 0）
      2. io.open(path, encoding=...) → 以「只读」方式打开文件，拿回文件对象
      3. .read()                     → 把整个文件读成一个字符串
      4. print(...)                  → 按固定宽度打印：标签、字节数、内容
      └─ 第 4 行里的 %r = repr，把换行/空格原样显示出来
         （否则空文件打印出来是 ''，肉眼看不出和 ' ' 的区别）
    """
    size = os.path.getsize(path)
    #   └─ getsize 只读元信息，不打开文件，文件不存在会直接抛异常
    content = io.open(path, encoding="utf-8").read()
    #   └─ 默认模式是 "r"（只读），所以这里绝不会清空文件 —— 演示时特意用 r
    print("    %-8s %4d bytes  内容=%r" % (tag, size, content[:40]))
    #   └─ %r = repr，把换行和空格原样显示出来（不然空文件看不出区别）
    #   └─ content[:40] = 只看前 40 个字符，够看又不会刷屏


def scenario_a(work):
    """场景 A：先开文件，再算内容 —— 中途崩溃会丢数据。

    逐行拆解：
      1. print(...)            → 打印场景标题
      2. os.path.join(work, DATA) → 拼出这个场景专属的文件路径
      3. io.open(path,"w").write(...) → 先造一份「已有数据」的文件当起点
      4. show("崩溃前", path)   → 打印崩溃前的文件状态（应该有 22 字节）
      5. try: ... except NameError → 故意让它崩，捕获住不让程序直接退出
      6. show("崩溃后", path)   → 打印崩溃后的文件状态（会看到 0 字节）
      └─ 第 5 步的 except 是关键：不接住的话脚本会直接死，
         后面那句 show("崩溃后") 就永远跑不到，你就看不到现场了

    ⚠️ 本场景对应错题 E24（open(path,'w') 先清空后写）
    """
    print("场景 A：先 open(...,'w')，再准备内容（你昨晚的写法）")
    path = os.path.join(work, DATA)
    #   └─ join = 拼接路径分隔符，比手写 "work\\todos.json" 跨平台更稳

    # 先造一个「已有数据」的文件
    io.open(path, "w", encoding="utf-8").write('[{"任务": "买菜"}]')
    #   └─ 这行故意用 "w"：文件本来不存在，"w" 会创建它
    #   └─ 这一步是「布置现场」，不是在演示丢数据，别和下面的 bug 混为一谈
    show("崩溃前", path)
    print("    ↓ 现在执行有 bug 的代码：tasks 还没定义就 f.write(tasks)")

    try:
        # 这就是昨晚那段代码的骨架
        with open(path, "w", encoding="utf-8") as f:      # ← ① 这里已经把文件清空了
            #   └─ with = 「用完自动关门」，不管里面是正常跑完还是抛异常
            #   └─ with 后面 as f = 把打开的文件对象起名叫 f
            #   └─ ⚠️ 关键：执行到这一行的那一刻，文件已经被清空成 0 字节了
            #   └─ 这就是 E24 的全部秘密：开门和存东西是【两件事】
            f.write(json.dumps(tasks))                    # ← ② tasks 未定义 → NameError
            #   └─ json.dumps(tasks) 需要一个真实存在的变量 tasks
            #   └─ 昨晚你漏了 tasks = add_task(...) 这一行 → NameError
    except NameError as e:
        #   └─ 只接 NameError（变量不存在），其它异常照常往上抛
        print("    💥 崩溃：%s" % e)
        #   └─ %s = 把异常对象转成文字打印出来

    show("崩溃后", path)
    print("    ⚠️ 文件内容没了 —— 这就是 0 字节的现场")
    #   └─ 注意：文件【还在】，只是变成 0 字节 —— 这就是最坑的地方
    #   └─ 你不会收到「文件丢了」的提示，只会发现数据凭空消失
    print()


def scenario_b(work):
    """场景 B：先把内容算好，再开文件 —— 中途崩溃不丢数据。

    逐行拆解：
      1. print(...)             → 打印场景标题
      2. 造起点文件 + show(...)   → 和场景 A 完全一样的起点，保证可比
      3. try: 内容 = json.dumps(tasks)  → 【先算】，崩在这一行
      4. with open(...) as f: f.write(内容) → 【后开门】，这一行根本没执行到
      5. show("崩溃后", path)    → 文件仍是 22 字节，旧数据完好
      └─ 场景 A 和 B 的代码几乎一样，唯一的区别就是这两行的【顺序】

    ⚠️ 本场景是 E24 的正解：改【顺序】，不是改模式
    """
    print("场景 B：先把内容算好，再 open(...,'w')")
    path = os.path.join(work, DATA)
    io.open(path, "w", encoding="utf-8").write('[{"任务": "买菜"}]')
    #   └─ 和场景 A 完全一样的起点 —— 对比实验的唯一变量只能是「顺序」
    show("崩溃前", path)
    print("    ↓ 执行改好的代码：tasks 还是没定义")

    try:
        内容 = json.dumps(tasks)                          # ← ① 先算，崩在这
        #   └─ 这一行在「开门」之前执行，所以此刻文件还是完好的
        #   └─ 变量名叫「内容」而不是 content，是为了让你一眼看懂中文含义
        with open(path, "w", encoding="utf-8") as f:      # ← ② 文件还没被碰过
            #   └─ 场景 A 崩在②之后、①之前；场景 B 崩在①、②之前
            #   └─ 差一行的顺序，结果差一个「数据还在不在」
            f.write(内容)
            #   └─ 写的是一个【已经算好的字符串】，不是现算
    except NameError as e:
        print("    💥 崩溃：%s" % e)

    show("崩溃后", path)
    print("    ✅ 旧数据完好 —— 因为崩在 open 之前，文件根本没被开过")
    #   └─ 这就是「open('w') 是开门动作，不是存东西动作」的实际含义
    print()


def scenario_c(work):
    """场景 C：写临时文件 + 原子替换 —— 最稳的做法。

    逐行拆解：
      1. tmp = path + ".tmp"     → 临时文件名，和正式文件【同目录】同盘
      2. with open(tmp,"w")     → 先写临时文件（正式文件一个字节都没动）
      3. os.replace(tmp, path)  → 写成功了才覆盖正式文件（这一步是原子的）
      4. except 里 os.remove(tmp) → 崩了就删掉临时文件，别留垃圾
      └─ 第 3 步的 os.replace 在同一文件系统上是「原子操作」：
         不存在「复制到一半」的中间状态，要么全成功要么全没发生

    ⚠️ 这是数据库、配置中心、git 都在用的「原子替换」模式
    """
    print("场景 C：写临时文件，成功后再 os.replace 覆盖（工程标准做法）")
    path = os.path.join(work, DATA)
    io.open(path, "w", encoding="utf-8").write('[{"任务": "买菜"}]')
    show("崩溃前", path)
    print("    ↓ 执行：写临时文件时崩溃")

    tmp = path + ".tmp"
    #   └─ 临时文件必须在【同一个目录】，否则 os.replace 会跨文件系统失败
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            #   └─ 注意：这里开的是 tmp，不是 path —— 正式文件还好好着呢
            f.write(json.dumps(tasks))                    # ← 崩在这
            #   └─ 崩了也只是临时文件是残缺的，正式文件毫发无损
        os.replace(tmp, path)                             # ← 只有成功才会执行到这
        #   └─ os.replace = 原子覆盖，旧文件瞬间换成新文件
        #   └─ 中间没有「半新半旧」的中间态，这是它比普通覆盖强的地方
    except NameError as e:
        print("    💥 崩溃：%s" % e)
        if os.path.exists(tmp):
            os.remove(tmp)                                # ← 清理临时文件
            #   └─ 删掉半成品，避免下次运行被当成有效数据读进去

    show("崩溃后", path)
    print("    ✅ 旧数据完好 —— 临时文件被丢弃，原文件一个字节都没动")
    print("    💡 这是数据库、配置中心、git 都在用的「原子替换」模式")
    print()


def main():
    """整个脚本的入口。

    逐行拆解：
      1. print("=" * 66)  → 打印一条分隔线（"=" 重复 66 次）
      2. tempfile.mkdtemp() → 在系统临时目录建一个【随机名】的文件夹
      3. try: ... finally: → 无论如何都要清理临时文件夹
      4. shutil.rmtree(work, ignore_errors=True) → 整个文件夹删掉
         └─ ignore_errors=True = 删不掉也别报错（可能是文件被占用）
      5. if __name__ == "__main__": → 只有直接运行这个文件时才调 main()
         └─ 被别的文件 import 时不会自动执行（这是 Python 的标准写法）
    """
    print("=" * 66)
    print("  0 字节文件是怎么来的 —— 三个场景真跑一遍")
    print("=" * 66)
    print()

    work = tempfile.mkdtemp()
    #   └─ mkdtemp = make directory temp
    #   └─ 为什么要用临时目录？因为场景 A 会故意把文件搞坏，
    #     绝不能发生在你的真实 todos.json 上
    try:
        scenario_a(work)
        scenario_b(work)
        scenario_c(work)
    finally:
        #   └─ finally 块【无论有没有异常】都会执行 —— 保证临时目录被清理
        shutil.rmtree(work, ignore_errors=True)
        #   └─ rmtree = 递归删除整棵目录树（remove tree）

    print("=" * 66)
    print("  三个场景，同一个崩溃点，结果完全不同：")
    print("=" * 66)
    print("    A  先开文件再算内容  →  💥 原文件被清空 → 0 字节")
    print("    B  先算内容再开文件  →  ✅ 崩在 open 之前 → 原文件完好")
    print("    C  写临时文件再替换  →  ✅ 崩在 replace 之前 → 原文件完好")
    print()
    print("  记住这句话：**open('w') 是「开门」的动作，不是「存东西」的动作。**")
    print("            崩溃发生在「开门之后、存进去之前」，数据就没了。")
    print("            所以正解永远是：先把要存的东西准备好，再开门。")


if __name__ == "__main__":
    #   └─ 这个文件被直接运行时，__name__ 等于 "__main__"，条件成立 → 执行 main()
    #   └─ 被别人 import 时，__name__ 是模块名，条件不成立 → 不自动执行
    main()
