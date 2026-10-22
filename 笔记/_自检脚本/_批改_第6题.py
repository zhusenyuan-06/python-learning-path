# -*- coding: utf-8 -*-
"""第 6 题：strip 到底去掉什么"""
words = ["hello,", "hello", "world!"]

print("=== 用户版（只 lower，不 strip）===")
counts = {}
for w in words:
    w = w.lower()
    counts[w] = counts.get(w, 0) + 1
print(counts)
print(">>> 'hello,' 和 'hello' 是两个词，同一个 hello 被算成 1 次而不是 2 次")
print()

print("=== strip 到底去掉什么？实测 ===")
print('"  hello  ".strip()      ->', repr("  hello  ".strip()), "  <- 去掉【空白】")
print('"hello".strip()          ->', repr("hello".strip()), "  <- 没空白可去")
print('"hello,".strip()         ->', repr("hello,".strip()), "  <- 逗号【还在】！")
print('"hello\\n".strip()        ->', repr("hello\n".strip()), "  <- 换行被去掉")
print('"\\thello".strip()        ->', repr("\thello".strip()), "  <- 制表符被去掉")
print()
print(">>> 结论：strip() 默认只去【空白字符】，标点它不管！")
print()

print("=== 要去标点，必须把标点当参数传进去 ===")
print('"hello,".strip(".,!?")    ->', repr("hello,".strip(".,!?")))
print('"hello，".strip("。，！？") ->', repr("hello，".strip("。，！？")), "  <- 中文标点自己传")
print()

print("=== 完整正确版（去标点 + 去空词）===")
counts2 = {}
for w in words:
    w = w.lower().strip(".,!?")
    if not w:            # 空词保护（E19）
        continue
    counts2[w] = counts2.get(w, 0) + 1
print(counts2)
print(">>> hello 正确地算成了 2 次")
print()

print("=== 演示 E19：strip 后变空串 ===")
bad_words = ["hello", "!!!", "...", "world"]
counts3 = {}
for w in bad_words:
    w = w.lower().strip(".,!?")
    print("  处理后 w =", repr(w))
    counts3[w] = counts3.get(w, 0) + 1
print("结果:", counts3)
print(">>> 空串 '' 混进词频了！")
print()

print("=== 加了 if not w 之后 ===")
counts4 = {}
for w in bad_words:
    w = w.lower().strip(".,!?")
    if not w:
        continue
    counts4[w] = counts4.get(w, 0) + 1
print("结果:", counts4)
print(">>> 干净了")
print()

print("=== 更省事的写法：strip 传参数 + 一行搞定 ===")
import re
counts5 = {}
for w in bad_words:
    w = re.sub(r"[^\w\s]", "", w.lower()).strip()   # 去掉所有非字母数字下划线
    if not w:
        continue
    counts5[w] = counts5.get(w, 0) + 1
print("结果:", counts5)
print(">>> re 是正则模块，中文标点英文标点全清，但 strip 传参更简单够用")
