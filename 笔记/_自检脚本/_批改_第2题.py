# -*- coding: utf-8 -*-
"""第 2 题：逐个拆解变量名复用的三处"""
from collections import Counter

print("=== 【第 1 处】sum_list 里的 nums ===")
def sum_list_错(nums):
    nums = 0
    for i in nums:      # nums 已经是 int 了
        nums += i
    return nums
try:
    sum_list_错([1, 2, 3])
except Exception as e:
    print("报错:", type(e).__name__, "|", e)
print()

print("=== 【第 2 处】counts 既是字典又是次数 ===")
t = {"python": 5, "data": 2}
counts = t            # counts 是「词->次数」的字典
for w, counts in t.items():
    print("  循环里 counts =", counts, "(类型:", type(counts).__name__, ")")
print("  循环结束后 counts =", counts, "(类型:", type(counts).__name__, ")")
print("  >>> 字典被覆盖成了一个 int")
print()

print("=== 【第 3 处】循环变量泄漏 ===")
t2 = {"python": 5, "data": 2}
for w, c in t2.items():
    pass
print("  出了循环 w =", repr(w), " c =", repr(c))
print("  >>> w 和 c 还在作用域里，类型已经被换掉了")
print()

print("=== for w, counts in t  (漏了 .items()) ===")
for w, counts in t:
    print(w, counts)
print()

print("=== 正确版 ===")
def sum_list(nums):
    total = 0
    for i in nums:
        total += i
    return total

print("sum_list([1,2,3]) =", sum_list([1, 2, 3]))
for w, c in t.items():
    print("  ", w, c)
