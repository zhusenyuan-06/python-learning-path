import csv
# ★ 标准库自带 csv 模块，不需要 pip install
# csv = Comma-Separated Values，逗号分隔的值，本质就是"每行用逗号分隔的纯文本表格"

import json
# ★ 标准库自带 json 模块，用来读写 .json 文件

from pathlib import Path
# ★ 标准库自带 pathlib，用来处理路径（比手拼字符串安全）

# ---- 路径：源（读）和目标（写）必须分开 ----
源 = Path("..") / "projects" / "error-tracker" / "错题追踪.json"
# 源 = 要【读】的原始数据文件
# Path("..") = 上一级目录。脚本在 练习/ 下运行，而 projects/ 在它的上一级，所以要加 ".."
# / 运算符是 pathlib 拼路径的方式（不要用 + 拼字符串，那样会出斜杠方向的坑）
# ✅ 相对路径 "../../" 这类写法容易错，pathlib 拼出来的路径对象能直接给 open() 用，不用转字符串

目标 = Path("输出") / "错题表.csv"
# 目标 = 要【写】的 csv 文件
# ⚠️⚠️ 关键：源和目标必须是【两个不同的文件】
#    如果这里写成 源，那 open(源, "w") 会当场清空你的 29 条错题库（= 你的 E24 错题）

目标.parent.mkdir(parents=True, exist_ok=True)
# .parent = 取父目录（这里是 输出/）
# mkdir(parents=True) = 父目录不存在也一起建；exist_ok=True = 目录已存在也不报错

# ---- ① 读 json（"r"）----
with open(源, "r", encoding="utf-8") as f:
    # "r" = 读取模式。文件不存在会报 FileNotFoundError
    # ⚠️ 这里必须用 "r"！用 "w" 会先把错题库清空（E24 原地踩坑）
    数据 = json.load(f)["items"]          # 29 条错题，是个列表
    # json.load(f) = 把 json 文件解析成 Python 对象（这里是字典）
    # ["items"] = 从字典里取出 "items" 这个键的值 → 29 条错题的列表
    # 每一"条"是一个字典，字段有 id/title/tags/occurrences/status 等 14 个

# ---- ② 写 csv（"w"，目标是 csv 不是 json！）----
with open(目标, "w", encoding="utf-8", newline="") as f:
    # "w" = 写入模式（文件不存在就新建，存在就清空重写）
    # newline="" = ★ csv 模块的必备参数！不加的话 Windows 上每行后面会多一个空行
    writer = csv.writer(f)
    # csv.writer(f) = 造一个"写入器"，它知道怎么把 Python 的列表写成一行逗号分隔的文本
    writer.writerow(["编号", "标题", "状态", "标签", "犯过次数"])   # 表头 5 列
    # writerow() = 写一行。传一个列表，列表里几个元素就是几列
    for 条 in 数据:
        # 遍历 29 条错题，每轮拿到一条（是个字典）
        标签 = "|".join(条["tags"])        # ← 列表转字符串
        # ⚠️ 关键坑：条["tags"] 是列表 ['静默错误', '控制流', '函数']
        #    csv 只能写字符串，直接写列表会报 TypeError: expected str
        #    "|".join(...) = 用竖线把列表连成字符串 → "静默错误|控制流|函数"
        #    （分隔符用 | 不用 ,，因为逗号是 csv 自己的分隔符，用了会把表格搞乱）
        writer.writerow([条["id"], 条["title"], 条["status"], 标签, 条["occurrences"]])
        # 按【表头的顺序】把 5 个值排好写进去
        # 故意不导 bad/good/history 字段：它们里面有多行文本和逗号，会把表格结构搞乱

# ================= 任务 2：读回来 =================

with open(目标, "r", encoding="utf-8", newline="") as f:   # ← 读自己写的 csv
    # ★ 注意这里读的是 输出/错题表.csv（刚才写出来的），不是 json
    #   csv.reader 只能读 csv 格式，喂 json 给它会读出乱码或报错
    # newline="" 读的时候也要加，保持和写的时候一致
    reader = csv.reader(f)
    # csv.reader(f) = 造一个"读取器"，它按逗号把每行拆成一个列表
    表头 = next(reader)
    # next(reader) = 从读取器里取出【第一行】（表头），并把它从流里拿走
    # 关键：取走表头后，剩下的就全是数据行了
    数据行 = list(reader)
    # list(reader) = 把剩下的所有行读成一个列表
    # 现在 数据行 里有 29 个列表，每个列表 5 个元素，且全是【字符串】


# active 的错题
for 行 in 数据行:
    # 遍历每一行（每个"行"是个列表，索引 0~4 对应 5 列）
    if 行[2] == "active":        # 第3列是状态
        # 行[2] = 第 3 列（索引从 0 开始：0=编号, 1=标题, 2=状态, 3=标签, 4=犯过次数）
        # ⚠️ 读回来的都是字符串，所以要跟字符串 "active" 比较，不能写 行[2] == active
        print(行[0], 行[1])
        # 打印编号和标题
        # 实测结果：筛出 21 条 active（另外 8 条是 mastered）

# 按犯过次数倒序 —— 次数在第5列，是字符串，要 int()
排好的 = sorted(数据行, key=lambda 行: int(行[4]), reverse=True)
# ★ sorted(可迭代对象, key=排序依据, reverse=是否倒序)
#   key=lambda 行: int(行[4]) → 按第 5 列（犯过次数）排序
#   ⚠️ 关键：int(行[4]) 不能省！csv 读回来全是字符串，
#      不转 int 的话 "10" < "4"（字符串比大小按字典序），排序会完全错乱
#   reverse=True → 倒序（次数多的排前面）
# 实测结果：E15(6次) → E02(5次) → E01(4次) → E03(4次) → E04(3次)
for 行 in 排好的[:5]:
    # [:5] = 取前 5 个
    print(行[0], 行[1], 行[4])
    # 打印编号、标题、犯过次数
