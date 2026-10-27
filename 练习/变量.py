x = 10
def change():
    x = 5         # 在函数里新建了一个局部 x，没碰外面的
    print(x)      # 5
change()
print(x)          # 你猜 → 10（外面的 x 还是 10）


x = 3
def add_ten(x):
    return x + 10

print(add_ten(x))   # 期望 13
print(x)            # 期望 3（没被改）



n = 100
def f():
    print(n)
    n = 200
f()
