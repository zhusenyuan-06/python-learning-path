#age = input("你几岁？")
#print(f"明年你" + str([age+1]) + "岁")   # 一跑就报 TypeError


counts = {}
words = ["苹果", "香蕉", "苹果", "橘子", "香蕉", "苹果"]
for w in words:
    counts[w] = counts.get(w, 0) + 1   # 第一次遇到新词就崩
print(counts)


def avg(nums):
    result = sum(nums) / len(nums)   # IndentationError
    return result


#with open('data.txt', encoding="utf-8") as f:
 #   if 'data.txt'
  #  for line in f:
   #     print(line.strip())


def make_user(**kwargs):
    user = {}
    for k, v in kwargs.items():        # 报错：dict 不能直接这样解包
        user[k] = v
    return user
print(make_user(name="小红", age=18))



def my_sum(*args):

    n = 0
    for i in args:
        n+= i
    return n


print(my_sum(1, 2, 3))          # 6
print(my_sum(10, 20, 30, 40))   # 100



def greet(n,*args):
    for h in args:
        print(n,h)

greet("你好", "小明", "小红", "小刚")
# 输出：
# 你好, 小明
# 你好, 小红
# 你好, 小刚



def print_info(**kwargs):
    for k,v in kwargs.items():
        print(k,v)
    print(f'共传了{len(kwargs)}项信息')
print_info(姓名="小明", 年龄=20, 城市="北京")
# 姓名: 小明
# 年龄: 20
# 城市: 北京
# 共 3 项信息














