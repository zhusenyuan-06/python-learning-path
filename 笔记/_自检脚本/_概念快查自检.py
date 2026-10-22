# -*- coding: utf-8 -*-
"""概念快查：本周一~周三新学的内容，确认没有概念空白。答案先跑真实代码。"""

def hr(t):
    print("\n" + "=" * 62)
    print(t)

hr("概念1：dict 三种遍历的区别")
d = {"a": 1, "b": 2}
print("d.keys()   ->", list(d.keys()), "  类型:", type(list(d.keys())).__name__)
print("d.values() ->", list(d.values()))
print("d.items()  ->", list(d.items()))
print("list(d)     ->", list(d), " ← 等价于 list(d.keys())")

hr("概念2：set 的运算符 vs 方法")
A = {1, 2, 3}
B = {3, 4, 5}
print("A | B  (并集) ->", A | B, " == A.union(B):", A.union(B))
print("A & B  (交集) ->", A & B, " == A.intersection(B):", A.intersection(B))
print("A - B  (差集) ->", A - B, " == A.difference(B):", A.difference(B))
print("A ^ B  (对称差)->", A ^ B)
print("❌ list 没有 | 和 & :")
try:
    print([1, 2] | [3])
except Exception as e:
    print("   TypeError:", e)

hr("概念3：嵌套 dict 的三种查法")
stu = {"小明": {"语文": 90, "数学": 85}}
print("1) 直接下标   ->", stu["小明"]["语文"])
print("2) 两层安全查 ->", stu.get("小刚", {}).get("语文", "无此人"))
print("3) 只查一层   ->", stu.get("小刚"), " ← 拿到 None，不是 dict")
try:
    print(stu.get("小刚").get("语文"))
except Exception as e:
    print("   ❗只查一层再链式 ->", type(e).__name__, ":", e)

hr("概念4：字典推导式 vs 集合推导式")
counts = {"a": 3, "b": 1, "c": 3}
print("集合推导式 {表达式 for ...} ->", {w for w, c in counts.items() if c == 1})
print("字典推导式 {键: 值 for ...} ->", {w: c for w, c in counts.items() if c == 1})
print("列表推导式 [表达式 for ...] ->", [w for w, c in counts.items() if c == 1])
print("→ 冒号在不在，决定是 dict 还是 set")

hr("概念5：strip / lower / split 各自做什么")
s = "  Hello, World!  "
print("原始       ->", repr(s))
print("s.strip()  ->", repr(s.strip()), "  ← 只去两端空白")
print("s.lower()  ->", repr(s.lower()), "  ← 转小写")
print("s.split()  ->", s.split(), "  ← 按空白切分")
print("s.strip('!')->", repr(s.strip("!")), "  ← 去两端指定的字符")

hr("概念6：字符串 vs 列表 —— 哪个能改")
s = "abc"
try:
    s[0] = "x"
except Exception as e:
    print("❌ 字符串不能改 ->", type(e).__name__, ":", e)
lst = ["a", "b"]
lst[0] = "x"
print("✅ 列表可以改 ->", lst)
print("→ 字符串的「改」= 生成新字符串重新赋值")

hr("概念7：sorted vs sort")
lst = [3, 1, 2]
r = sorted(lst)
print("sorted(lst) ->", r, " | lst 本身 ->", lst, " ← 返回新list，原list不变")
lst2 = [3, 1, 2]
r2 = lst2.sort()
print("lst.sort()  -> 返回", r2, " | lst2 本身 ->", lst2, " ← 原地排序，返回 None")
