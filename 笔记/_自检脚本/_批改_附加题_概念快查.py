# -*- coding: utf-8 -*-
"""附加题 E16 + 概念快查 A~G 全部实测"""

print("=" * 60)
print("【附加题 E16】keys() + x[1]")
print("=" * 60)
counts = {"data": 2, "learn": 3, "code": 2, "python": 5}
r = sorted(counts.keys(), key=lambda x: x[1])
print("r =", r)
print("每词的第2个字母:", {w: w[1] for w in counts})
print(">>> 不报错，按【第2个字母】排：a(ata? no) 看下面")
print("    data->a, learn->e, code->o, python->y")
print("    排序: a < e < o < y  -> data, learn, code, python")
print()

print("=" * 60)
print("【A】dict 三种遍历")
print("=" * 60)
d = {"a": 1, "b": 2}
print("d.keys()   ->", d.keys(), "类型:", type(d.keys()).__name__)
print("d.values() ->", d.values(), "类型:", type(d.values()).__name__)
print("d.items()  ->", d.items(), "类型:", type(d.items()).__name__)
print()

print("=" * 60)
print("【B】set 四运算")
print("=" * 60)
A = {1, 2, 3}
B = {3, 4, 5}
print("A | B (并) ->", A | B)
print("A & B (交) ->", A & B)
print("A - B (差) ->", A - B)
print("A ^ B (对称差) ->", A ^ B, "  <- 在A或B但不同时在两者")
print()

print("=" * 60)
print("【C】三种查法")
print("=" * 60)
stu = {"小明": {"语文": 90, "数学": 85}}
print('stu["小明"]["语文"]            ->', stu["小明"]["语文"])
print('stu.get("小刚", {}).get("语文") ->', stu.get("小刚", {}).get("语文"), "(两层各配默认值，安全)")
try:
    stu.get("小刚").get("语文")
except Exception as e:
    print('stu.get("小刚").get("语文")   -> 报错:', type(e).__name__, "|", e)
print()

print("=" * 60)
print("【D】三个推导式的类型")
print("=" * 60)
counts = {"a": 3, "b": 1, "c": 3}
print("{w for ...}      ->", {w for w, c in counts.items() if c == 1}, "类型:", type({w for w, c in counts.items() if c == 1}).__name__)
print("{w: c for ...}    ->", {w: c for w, c in counts.items() if c == 1}, "类型:", type({w: c for w, c in counts.items() if c == 1}).__name__)
print("[w for ...]      ->", [w for w, c in counts.items() if c == 1], "类型:", type([w for w, c in counts.items() if c == 1]).__name__)
print()

print("=" * 60)
print("【E】三个字符串方法")
print("=" * 60)
s = "  Hello, World!  "
print("原串:", repr(s))
print("s.strip() ->", repr(s.strip()), "  # 去首尾空白")
print("s.lower() ->", repr(s.lower()), "  # 全变小写")
print("s.split() ->", s.split(), "  # 按空白切成列表")
print()

print("=" * 60)
print("【F】谁能原地改")
print("=" * 60)
s = "hello"
try:
    s[0] = "H"
except Exception as e:
    print("字符串 s[0]='H' -> 报错:", type(e).__name__, "|", e)
lst = [1, 2, 3]
lst[0] = 99
print("列表 lst[0]=99 -> 成功:", lst)
print(">>> 因为字符串是【不可变】，列表是【可变】")
print()

print("=" * 60)
print("【G】sorted vs sort")
print("=" * 60)
orig = [3, 1, 2]
r1 = sorted(orig)
print("sorted(orig) 返回:", r1, " | 原列表:", orig, "  <- 原列表不变")
r2 = sorted(orig)
orig2 = [3, 1, 2]
ret = orig2.sort()
print("lst.sort() 返回:", ret, " | 原列表:", orig2, "  <- 返回 None！原列表被改了")
print()
print(">>> 关键：lst.sort() 返回 None，不能写 x = lst.sort()")
