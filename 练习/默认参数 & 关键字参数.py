#def f(x, y=10):
#    return x + y

#print(f(5))          # 期望 15（y 用默认 10）
#print(f(5, 20))      # 期望 25（y 传 20）
#print(f(x=5, y=20))  # 期望 25（关键字传参）
#print(f(y=20, x=5))  # 期望 25（关键字，顺序随便）




#def greet(name, greeting="你好"):
 #   return f'{name},{greeting}'
    # TODO: 用 return 返回一句话，格式："打招呼语，名字"
    # 提示：用 f-string，像 return f"{greeting}，{name}"
# 下面 3 行测试不用改，直接跑：
#print(greet("小明"))                    # 期望 你好，小明
#print(greet("小明", "Hi"))             # 期望 Hi，小明
#print(greet("小红", greeting="早安"))   # 期望 早安，小红




def add(a, b=0):
    return a + b

print(add(3))      # 期望 3（b 用默认 0）
print(add(3, 5))   # 期望 8
