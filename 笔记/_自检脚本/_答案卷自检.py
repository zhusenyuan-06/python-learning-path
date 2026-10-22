# -*- coding: utf-8 -*-
"""答案卷专用：把每一小问的真实输出跑出来，不口算。"""

def hr(t):
    print("\n" + "=" * 60)
    print(t)

# 第 4 题补充：空字典
hr("第4题-3：counts 为空 {}")
counts = {}
after = sorted(counts.items(), key=lambda x: x[1])
print("✅ 不报错 ->", after, "| after[0] ->", end=" ")
try:
    print(after[0])
except Exception as e:
    print(type(e).__name__, ":", e)

# 第 6 题：words 真实计数
hr("第6题-1：words = ['hello,', 'hello', 'world!']")
words = ["hello,", "hello", "world!"]
counts = {}
for w in words:
    w = w.lower()
    counts[w] = counts.get(w, 0) + 1
print("❌ 不 strip ->", counts)

counts2 = {}
for w in words:
    w = w.lower().strip(".,!?")
    if w:
        counts2[w] = counts2.get(w, 0) + 1
print("✅ strip+空词过滤 ->", counts2)

# strip 到底去掉什么
hr("第6题-3：strip() 的语义")
s = "  Python  "
print("默认 strip() ->", repr(s.strip()))
s2 = "，你好。世界！"
print("中文标点 strip(\"，。！？\") ->", repr(s2.strip("，。！？")))
s3 = "abc.,!?"
print("混合 strip(\".,!?\") ->", repr(s3.strip(".,!?")))
print("注意：strip 只去两端，不去中间")

# 第 5 题：手机号前导 0 / 数字统一会怎样
hr("第5题：为什么统一成字符串")
import json
d = {"小明": {"电话": "013800138000"}, "小红": {"电话": "13900139000"}}
print("字符串保留前导0 ->", d["小明"]["电话"], "| len =", len(d["小明"]["电话"]))
print("如果统一成数字 ->", int(d["小明"]["电话"]), "前导0丢了")
print("JSON 里数字不带引号 ->", json.dumps({"电话": 13800138000}, ensure_ascii=False))
print("JSON 里字符串带引号 ->", json.dumps({"电话": "13800138000"}, ensure_ascii=False))
try:
    print(int(13800138000) + 1)
    print("int 也能相加 -> 但号码不该做运算")
except Exception as e:
    print(e)
print("int 转 str 后: ", type(str(13800138000)).__name__)

# 第 3 题：if/elif/else 链里对应的坑
hr("第3题-3：if/elif/else 链的坑")
x = 5
if x > 10:
    r = "大"
elif x > 3:
    r = "中"
else:
    r = "小"
print("有 else 的完整链 ->", r)
x = 50
if x > 10:
    r = "大"
elif x > 3:
    r = "中"
print("缺 else 的链，x=50 ->", r, "(x=1 时会 NameError)")
try:
    x = 1
    if x > 10:
        r = "大"
    elif x > 3:
        r = "中"
    print(r)
except Exception as e:
    print("x=1 时 ->", type(e).__name__, ":", e)

# 第 2 题：报错名字
hr("第2题-3：sum_list 的真实报错")
def sum_list(nums):
    nums = 0
    for i in nums:
        nums += i
    return nums
try:
    sum_list([1, 2, 3])
except Exception as e:
    print("❌ ->", type(e).__name__, ":", e)

def sum_list2(nums):
    total = 0
    for i in nums:
        total += i
    return total
print("✅ ->", sum_list2([1, 2, 3]))

# 第 2 题补充：for w, counts in t 解包报错
hr("第2题补充：for w, counts in t")
t = {"python": 5, "data": 2}
try:
    for w, counts in t:
        print(w, counts)
except Exception as e:
    print("❌ ->", type(e).__name__, ":", e)
print("→ t.items() 才对：")
for w, counts in t.items():
    print("  ", w, counts)

# 第 1 题：三处一起改写后的完整跑法
hr("第1题：完整改写版跑一遍")
counts = {"hello,": 1, "hello": 1, "python.": 1, "data": 2}
words = list(counts.keys())
out = {}
for w in words:
    w = w.lower().strip(".,!?")
    if w:
        out[w] = out.get(w, 0) + 1
after = sorted(out.items(), key=lambda x: x[1], reverse=True)
print("改写后 ->", after)
print("第一名:", after[0], "（次数最多）")

# E16 完整
hr("E16：keys() + x[1]")
counts = {"data": 2, "learn": 3, "code": 2, "python": 5}
r = sorted(counts.keys(), key=lambda x: x[1])
print("❌ 不报错 ->", r)
print("第2个字母 ->", [(w, w[1]) for w in r])
r2 = sorted(counts.items(), key=lambda x: x[1], reverse=True)
print("✅ 正确写法 ->", r2)
