# -*- coding: utf-8 -*-
"""
*args / **kwargs 对照实验

运行方式：PyCharm 里右键本文件 → Run 'args_kwargs_对照实验'
每段实验之间有 ===== 分隔，盯住"参数到底去哪了"
"""

print("===== 实验 1：*args 把多出来的位置参数装进一个元组 =====")


def f1(固定1, 固定2, *args, **kwargs):
    print("  固定1 =", 固定1)
    print("  固定2 =", 固定2)
    print("  args   =", args, "  类型:", type(args).__name__)
    print("  kwargs =", kwargs, "  类型:", type(kwargs).__name__)


f1(1, 2, 3, 4, 5, x=10, y=20)


print()
print("===== 实验 2：只给 *args，不给 **kwargs =====")


def f2(固定, *args):
    print("  固定 =", 固定)
    print("  args =", args)


f2("A", 1, 2, 3)
try:
    f2("A", 1, 2, x=10)
except TypeError as e:
    print("  报错啦 ->", e)


print()
print("===== 实验 3：把两个星号都去掉，会发生什么 =====")


def f3(a, b, args, kwargs):
    print("  a =", a, "| b =", b, "| args =", args, "| kwargs =", kwargs)


print("  先只传 4 个位置参数：")
f3(1, 2, 3, 4)
print("  再多传一个 x=10：")
try:
    f3(1, 2, 3, 4, x=10, y=20)
except TypeError as e:
    print("  报错啦 ->", e)
print("  对比实验1：f1(1,2,3,4,5,x=10) 是能跑的 —— 差别就在那两个星号")


print()
print("===== 实验 4：调用时用 * 和 ** 把容器拆开传进去 =====")


def f4(a, b, *args, **kwargs):
    print("  a =", a, "| b =", b, "| args =", args, "| kwargs =", kwargs)


数据 = [3, 4, 5]
标签 = {"x": 10, "y": 20}
f4(1, 2, *数据)
f4(1, 2, *数据, x=10)
f4(1, 2, *数据, **标签)


print()
print("===== 实验 5：*args 的杀手锏 —— 万能转发 =====")


def 我的打印(*内容, **选项):
    """把收到的原样转交给内置 print"""
    print(*内容, **选项)


我的打印("苹果", "香蕉", "橘子")
我的打印("苹果", "香蕉", "橘子", sep=" | ")
我的打印("苹果", "香蕉", end="")
print("   <- 上面 end 吃掉了换行")


print()
print("===== 实验 6：混合使用时，位置参数和关键字参数怎么分家 =====")


def f6(必填, *args, **kwargs):
    print("  必填 =", 必填, "| args =", args, "| kwargs =", kwargs)


f6(1, 2, 3, 4, 5, 名字="小明")
