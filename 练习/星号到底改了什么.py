# -*- coding: utf-8 -*-
"""
星号到底改了什么 —— 固定插座 vs 口袋

同一个例子的两种写法，并排跑给你看差别。

运行方式：PyCharm 里右键本文件 → Run '星号到底改了什么'
"""

print("===== A. 同样 4 个形参，两种写法 =====")


def f1(a, b, *args, **kwargs):
    print("   a=%r  b=%r  args=%r  kwargs=%r" % (a, b, args, kwargs))


def f3(a, b, args, kwargs):
    print("   a=%r  b=%r  args=%r  kwargs=%r" % (a, b, args, kwargs))


print("   f1 的形参：a, b, *args, **kwargs   <- 后两个是【口袋】")
print("   f3 的形参：a, b, args, kwargs      <- 四个都是【固定插座】")


print()
print("===== B. 位置实参：从左往右，一个对一个 =====")
print("   f1(1, 2, 3, 4, 5)")
f1(1, 2, 3, 4, 5)
print("     -> 1->a   2->b   3,4,5 装进 args 口袋（口袋能装几个都行）")
print("   f3(1, 2, 3, 4)")
f3(1, 2, 3, 4)
print("     -> 1->a   2->b   3->args   4->kwargs   （4 个插座刚好用完，没有口袋）")


print()
print("===== C. 位置实参给多了会怎样 =====")
print("   f1(1,2,3,4,5,6,7,8)")
f1(1, 2, 3, 4, 5, 6, 7, 8)
print("   f3(1,2,3,4,5)")
try:
    f3(1, 2, 3, 4, 5)
except TypeError as e:
    print("     报错 ->", e)


print()
print("===== D. 关键字实参给多了会怎样 =====")
print("   f1(1,2,x=10)")
f1(1, 2, x=10)
print("   f3(1,2,x=10)")
try:
    f3(1, 2, x=10)
except TypeError as e:
    print("     报错 ->", e)


print()
print("===== E. 两种报错的说法不一样（很关键）=====")
print("   位置参数多了 -> 'takes N positional arguments but M were given'")
print("                     意思是：插座不够，没地方插")
print("   关键字多了   -> 'got an unexpected keyword argument'")
print("                     意思是：找不到一个叫这个名字的插座，也没有口袋")


print()
print("===== F. args / kwargs 这两个名字本身没有魔法 =====")


def f4(a, b, *其他, **额外):
    print("   其他=%r   额外=%r" % (其他, 额外))


f4(1, 2, 3, 4, 名称="张三")
print("   换成中文名完全一样 —— 真正干活的是 * 和 **，不是那两个单词")


print()
print("===== G. 口袋的容量 =====")
print("   固定插座必须【恰好够用】，少一个报错：")
try:
    f3(1, 2, 3)
except TypeError as e:
    print("     ", e)
print("   口袋可以是 0 个：")
f1(1, 2)
print("   口袋可以是 100 个：")
f1(1, 2, *range(100))
