# 1. 最基础的 lambda：乘 2
f = lambda x: x * 2
print(f(5))          # 期望 10

# 2. 多个参数
add = lambda a, b: a + b
print(add(3, 5))     # 期望 8

# 3. 你见过的：sorted 配 lambda 按"值"排序（词频项目用过）
pairs = [("apple", 3), ("banana", 1), ("orange", 5)]
pairs.sort(key=lambda x: x[1])     # 按每个元组的第 1 格（次数）升序排
print(pairs)       # 期望 [('banana', 1), ('apple', 3), ('orange', 5)]



# 1. 判断偶数：传一个数 n，返回 True/False
is_even = lambda n: n%2 == 0        # ← 填表达式（复习 % ：偶数就是 n 除以 2 余 0）
print(is_even(4))    # 期望 True
print(is_even(7))    # 期望 False

# 2. 问候语：传名字 name，返回 "你好，<名字>"
greet = lambda name: f'你好，{name}'       # ← 填表达式（用 f-string）
print(greet("小明"))  # 期望 你好，小明


# ④-1 按价格从高到低排（用 sorted + lambda）
fruits = [("apple", 8), ("banana", 3), ("orange", 12), ("grape", 20)]

result = sorted(fruits,key=lambda x: x[1],reverse=True)      # ← 用 sorted(fruits, key=lambda ..., reverse=True) 补全
print(result)
# 期望 [('grape', 20), ('orange', 12), ('apple', 8), ('banana', 3)]


# ④-2 换个"排序依据"：按单词长度从短到长排（练 key 换成 len）
words = ["apple", "hi", "banana", "ok"]

lens = sorted(words,key=lambda x: len(x))        # ← 用 sorted(words, key=lambda ...) 补全
print(lens)
# 期望 ['hi', 'ok', 'apple', 'banana']
