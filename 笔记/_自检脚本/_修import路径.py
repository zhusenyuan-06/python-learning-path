# -*- coding: utf-8 -*-
"""修 import 路径：让搬过家的文件还能 import 到 配送工具

做法：在 import 之前插一行 sys.path 拼接，把「教学/」目录加进搜索路径。
这是 Python 官方推荐的标准做法（比写死绝对路径好，目录再搬也不失效）。
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
目标 = os.path.join(ROOT, "教学", "配送工具.py")

# 需要修的文件：凡是需要 import 配送工具 的
待修 = []
for base in ("练习", "参考材料"):
    d = os.path.join(ROOT, base)
    if not os.path.isdir(d):
        continue
    for f in os.listdir(d):
        if f.endswith(".py"):
            待修.append(os.path.join(d, f))

补丁 = (
    "import os\n"
    "import sys\n"
    "sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), \"..\", \"教学\"))\n"
)

改了 = []
for p in 待修:
    with io.open(p, encoding="utf-8") as f:
        src = f.read()
    if "import 配送工具" not in src and "from 配送工具 import" not in src:
        continue
    if "sys.path.insert" in src:
        print(f"  [跳过] 已修过: {os.path.relpath(p, ROOT)}")
        continue
    # 在第一行 import 配送工具 之前插入 sys.path 补丁
    lines = src.split("\n")
    新行 = []
    插入了 = False
    for 行 in lines:
        if (not 插入了) and re.match(r"^\s*(import 配送工具|from 配送工具 import)", 行):
            新行.append(补丁.rstrip("\n"))
            新行.append("")
            插入了 = True
        新行.append(行)
    if not 插入了:
        continue
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(新行))
    改了.append(os.path.relpath(p, ROOT))
    print(f"  [已修] {os.path.relpath(p, ROOT)}")

print()
print(f"共修了 {len(改了)} 个文件")
print("补丁内容（每个文件 import 之前插入）：")
print("  " + 补丁.replace("\n", "\n  ").strip())
