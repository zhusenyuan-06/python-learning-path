def say_hi(name):
    return f'你好,{name}'

print(say_hi("小明"))





def is_even(n):
    return n%2 == 0

print(is_even(7))
print(is_even(10))




def sum_list(nums):
    n = 0
    for i in nums:
        n+= i
    return n

print(sum_list([1, 2, 3, 4]))     # 期望 10
print(sum_list([100, 200]))       # 期望 300
print(sum_list([]))




def word_count(text):
    words = text.split()         # 第 1 步：怎么把字符串按空格拆
    counts = {}    # 第 2 步：拿个空 dict 装结果
    for w in words:      # 第 3 步：每个单词来一遍
        counts[w] = counts.get(w, 0) + 1              # 见到老词 +1；新词 get 返回 0，+1 正好是 1
    return counts


print(word_count("i love python and i love code"))  # {'i': 2, 'love': 2, 'python': 1, 'and': 1, 'code': 1}
print(word_count("hello world"))                    # {'hello': 1, 'world': 1}
print(word_count(""))                               # {}




