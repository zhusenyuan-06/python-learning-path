# -*- coding: utf-8 -*-
"""第 4 题：验证用户答案 + 空字典边界"""
counts = {"python": 5, "data": 2, "learn": 3, "code": 2}

print("=== 用户版（无 reverse=True）===")
after = sorted(counts.items(), key=lambda x: x[1])
print("完整排序:", after)
print("after[0] =", after[0], "  <- 用户答对了")
print()

print("=== 正确版（reverse=True）===")
after2 = sorted(counts.items(), key=lambda x: x[1], reverse=True)
print("完整排序:", after2)
print("after2[0] =", after2[0], "  <- 次数最多的排第一")
print()

print("=== 并列时谁在前？（稳定排序）===")
print("data 和 code 都是 2 次，谁在前面？", "-> data" if after[0][0] == "data" else "-> code")
print("原因：sorted 是【稳定排序】，次数相同的保持【原来字典里的顺序】")
print("      字典里 data 在 code 前面（插入顺序），所以 data 排前面")
print()

print("=== 第 3 问：空字典 ===")
empty = {}
after3 = sorted(empty.items(), key=lambda x: x[1])
print("sorted 结果:", after3, "(空列表，不报错)")
try:
    print(after3[0])
except Exception as e:
    print(">>> 报错:", type(e).__name__, "|", e)
print()

print("=== 边界安全写法 ===")
top = sorted(empty.items(), key=lambda x: x[1], reverse=True)
print("空字典安全取值:", top[0] if top else "（没有数据）")
print()
counts2 = {"python": 5}
top2 = sorted(counts2.items(), key=lambda x: x[1], reverse=True)
print("非空时:", top2[0] if top2 else "（没有数据）")
