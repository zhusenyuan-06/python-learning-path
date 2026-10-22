# -*- coding: utf-8 -*-
"""批改第 1 题：对比用户答案与标准答案的实际行为"""
from collections import Counter

words = ["hello,", "hello", "world!"]
counts = Counter()
for w in words:
    w = w.lower()          # 用户版本：没 strip
    counts[w] = counts.get(w, 0) + 1
print("用户版(无strip) :", dict(counts))

counts2 = Counter()
for w in words:
    w = w.lower().strip(".,!?")   # 标准版
    counts2[w] = counts2.get(w, 0) + 1
print("标准版(strip)   :", dict(counts2))
print()

# ---------- ③ 用户版：加 else 但没 return ----------
contacts = {"小明": {"电话": "13800138000"}}

def a_user(name, p):
    if name in contacts:
        print("未覆盖")
    else:
        print("查无此人")      # 用户加的 else
    contacts[name] = {"电话": p}   # 照样往下走！

print("=== 用户版 a('小明', '13911112222') ===")
a_user("小明", "13911112222")
print("结果 contacts['小明'] =", contacts["小明"])
print(">>> 打印了'未覆盖'，但数据已经被覆盖了 —— 问题没解决")
print()

# ---------- ③ 标准版：return ----------
contacts2 = {"小明": {"电话": "13800138000"}}

def a_std(name, p):
    if name in contacts2:
        return "未覆盖"       # 立刻停，后面不执行
    contacts2[name] = {"电话": p}
    return "已添加"

print("=== 标准版 a('小明', '13911112222') ===")
r = a_std("小明", "13911112222")
print("返回值:", r)
print("结果 contacts['小明'] =", contacts2["小明"])
print(">>> 数据没被动过，函数直接返回了")
print()

# ---------- 反例证明 else 不管用 ----------
print("=== 证明：加 else 依然会覆盖 ===")
contacts3 = {"小红": {"电话": "13500135000"}}
def a_else(name, p):
    if name in contacts3:
        print("  未覆盖")
    else:
        print("  查无此人")
    contacts3[name] = {"电话": p}

a_else("不存在的人", "13000000000")
print("  新人加进去了:", contacts3["不存在的人"])
print("  但如果 name 已存在，照样被覆盖 -> else 拦不住")
