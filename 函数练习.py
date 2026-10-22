#def avg(nums):                       # def 函数名(参数):
 #   return sum(nums) / len(nums)
#print(avg([1,2,3,4]))



# 练习1：加法
#def add(a, b):
    #return int(a) + int(b)


# 练习2：判断偶数
#def is_even(n):
    #while True:
#  if n%2 == 0:
#        return True
      #  else:
#        return False
 # TODO: 返回 n 是不是偶数（结果是 True 或 False，复习 %）


# 练习3：打招呼
#def greet(name):
    #return f'你好,{name}'
    # TODO: 返回 "你好，" + name


# 试一下（这几个 print 不用改，直接跑）：
#print(add(3, 5))        # 期望 8
#print(is_even(4))       # 期望 True
#print(is_even(7))       # 期望 False
#print(greet("小明"))     # 期望 你好，小明



def count_words(text):
    words = text.split()
    counts = {}
    for w in words:
        counts[w] = counts.get(w, 0) + 1
    return counts          # ← 放循环外面，返回整个字典

print(count_words("apple banana apple"))   # {'apple': 2, 'banana': 1}

    # 提示：就三步
    # 1. 用 text.split() 把句子切成词列表
    # 2. 用字典统计词频（你在"词频.py"里写过：d[w] = d.get(w, 0) + 1）
    # 3. 用 return 把这个字典交出来（不是 print！）



