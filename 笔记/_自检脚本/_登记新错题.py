# -*- coding: utf-8 -*-
"""登记本次查漏补缺发现的新错题（复用追踪器的 cmd_add + save，同一条路径）。"""
import os, sys
sys.path.insert(0, r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")
import importlib.util
spec = importlib.util.spec_from_file_location("zhuizong", r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记\错题追踪器.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

db = m.load()

# ---- 1. 浅拷贝：内层 dict 仍共享（出现在用户今天写的 10.22复习.2.py）
m.cmd_add(db,
    "浅拷贝：dict(a) / a.copy() 只复制外层，内层 dict 仍共享",
    """班级A = {"小明": {"语文": 90, "数学": 85}}
总表 = dict(班级A); 总表.update(班级B)   # ❌ 外层是新 dict，内层还是同一个对象

总表["小明"]["语文"] = 99
print(班级A["小明"])      # ❌ 变成 {'语文': 99, ...}，原数据被偷偷改了""",
    """# ✅ 逐层复制（只有两层，够用）
总表 = {k: dict(v) for k, v in 班级A.items()}
总表.update(班级B)

# ✅ 或者用标准库（层数不定时用它）
import copy
总表 = copy.deepcopy(班级A)
总表.update(班级B)

# 验证：改总表不影响班级A""",
    "浅拷贝,字典合并,静默错误,查漏补缺")

# ---- 2. update() 遇到同名 key 静默覆盖
m.cmd_add(db,
    "静默覆盖：update() 遇到同名 key 直接顶掉，不报错也没提示",
    """a = {"小明": {"语文": 90, "数学": 85}}
b = {"小明": {"语文": 70, "数学": 89}}
总 = dict(a)
总.update(b)
# ❌ 小明的语文从 90 变成 70，数据没了，全程无任何提示""",
    """# ✅ 合并前先看有没有重名
重名 = set(a) & set(b)
if 重名:
    print("⚠️ 同名 key，会被覆盖:", 重名)
    for k in 重名:
        print("  ", k, "旧:", a[k], "→ 新:", b[k])   # 先让你看见

总 = dict(a)
总.update(b)

# ✅ 真的要保留旧值，就合并而不是覆盖
总 = dict(a)
for k, v in b.items():
    总.setdefault(k, v)      # 已存在就保留旧的""",
    "字典合并,静默覆盖,静默错误,查漏补缺")

# ---- 3. strip 后可能产生空串，空串被算进词频
m.cmd_add(db,
    "strip 后可能变成空串，空串被算进词频",
    """for w in words:
    w = w.lower().strip(".,!?")
    if w in stopwords:
        continue
    counts[w] = counts.get(w, 0) + 1
# ❌ 原文里有 \"...\" / \"!!!\" 这种纯标点独立成词时，
#    strip 完变成空串 ''，照样进统计 → counts 里多出一个键 ''""",
    """for w in words:
    w = w.lower().strip(".,!?")
    if not w:                 # ← strip 之后必须判空
        continue
    if w in stopwords:
        continue
    counts[w] = counts.get(w, 0) + 1

# 验证：words 里加一个 \"...\"
# 没有 if not w → counts 里出现 '': 1
# 有  if not w → counts 里没有空串键""",
    "字符串,strip,词频,静默错误,查漏补缺")

m.save(db)
print("\n--- 登记完成 ---")
m.cmd_stats(db)
