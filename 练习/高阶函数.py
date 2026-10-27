from statsmodels.graphics.tukeyplot import results


def apply(f, x):
    return f(x)

print(apply(lambda x: x * 2, 5))         # 期望 10
print(apply(lambda s: s.upper(), "hi"))  # 期望 HI
print(apply(abs, -7))                    # 期望 7



# ③ 自己写：把函数 f 作用到 lst 的每个元素，返回新列表
def apply_to_list(f, lst):
    result = []
    for x in lst:  # ① 填什么（提示：我们要遍历谁）
        result.append(f(x))  # ② 填什么（提示：把"f 作用到 x 上"的结果放进去）
    return result  # ③ 填什么（提示：把整个 result 交出去）
    # TODO: 遍历 lst，把 f(x) 一个个放进新列表，最后 return
        # ← 删掉这一行，换成你的实现（2~3 行）


# 下面测试不用改：
print(apply_to_list(lambda x: x * x, [1, 2, 3, 4]))      # 期望 [1, 4, 9, 16]
print(apply_to_list(lambda s: s.upper(), ["hi", "ok"]))  # 期望 ['HI', 'OK']
print(apply_to_list(abs, [-1, 2, -3]))                   # 期望 [1, 2, 3]


def a(f,n):
    b = []
    for x in n:
        b.append(f(n))
    return b


# ④ 把一组温度从摄氏度转成华氏度：(C*9/5)+32
print(apply_to_list(lambda c: c * 9/5 + 32, [0, 100, 30]))
# 期望 [32.0, 212.0, 86.0]

