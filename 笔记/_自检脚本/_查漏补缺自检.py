# -*- coding: utf-8 -*-
"""查漏补缺：验证本周代码里发现的新错误模式（写错/写对对照）。"""

def hr(t):
    print("\n" + "=" * 62)
    print(t)

# ------------------------------------------------------------ 新错误 A：浅拷贝
hr("候选 A：dict(a) / a.copy() 是【浅拷贝】——内层 dict 仍共享")
班级A = {"小明": {"语文": 90, "数学": 85}}
总表 = dict(班级A)
总表.update({"小红": {"语文": 70, "数学": 89}})
print("合并后 总表 =", 总表)
print("班级A 有没有被影响 ->", 班级A)

总表["小明"]["语文"] = 99          # 改总表里的内层
print("\n改完 总表['小明'] =", 总表["小明"])
print("班级A['小明']      =", 班级A["小明"], "  ← ❗被一起改了！")

班级A2 = {"小明": {"语文": 90, "数学": 85}}
总表2 = {k: dict(v) for k, v in 班级A2.items()}   # 逐层复制
总表2["小明"]["语文"] = 99
print("\n✅ 逐层复制后 班级A2 =", 班级A2, " 总表2 =", 总表2)

import copy
班级A3 = {"小明": {"语文": 90, "数学": 85}}
总表3 = copy.deepcopy(班级A3)
总表3["小明"]["语文"] = 99
print("✅ deepcopy 后 班级A3 =", 班级A3)

# ------------------------------------------------------------ 新错误 B：strip 后空串
hr("候选 B：strip 后可能变成空串，空串被算进词频")
words = ["hello", "...", "!!!", "world"]
counts = {}
for w in words:
    w = w.lower().strip(".,!?")
    counts[w] = counts.get(w, 0) + 1
print("❌ 不判空 ->", counts, " ← 出现了空字符串键 ''")

counts2 = {}
for w in words:
    w = w.lower().strip(".,!?")
    if w:
        counts2[w] = counts2.get(w, 0) + 1
print("✅ 判空   ->", counts2)

# ------------------------------------------------------------ 新错误 C：update 静默覆盖
hr("候选 C：update() 遇到同名 key 静默覆盖，不报错")
a = {"小明": {"语文": 90, "数学": 85}}
b = {"小明": {"语文": 70, "数学": 89}}
总 = dict(a)
总.update(b)
print("❌ update 后 ->", 总, " ← a 的语文 90 被 b 的 70 顶掉了，且没有任何提示")
print("   a 本身没变:", a)

# ------------------------------------------------------------ 新错误 D：+= 与可变默认值
hr("候选 D：可变默认参数")
def f(x, lst=[]):
    lst.append(x)
    return lst
print("❌ ->", f(1), f(2), " ← 第二次带上了上次的 1")

def g(x, lst=None):
    if lst is None:
        lst = []
    lst.append(x)
    return lst
print("✅ ->", g(1), g(2))

# ------------------------------------------------------------ 新错误 E：str.strip 只去两端
hr("候选 E：strip 只去两端，中间的标点不去")
print("'a,b,c'.strip(',') ->", repr("a,b,c".strip(",")))
print("'..hi..'.strip('.')  ->", repr("..hi..".strip(".")))
print("中间标点要靠 split/translate，不是 strip")
