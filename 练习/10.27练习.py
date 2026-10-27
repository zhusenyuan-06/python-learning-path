def f(a, b, *args, **kwargs):
    return a, b, args, kwargs

print(f(1, 2, 3, 4, x=10, y=20))
print(3 * 10)      # 乘法
print(3 ** 10)     # 幂


def my_sum(*args):
    # 求所有数字的和
    n = 0
    for i in args:
        n += i
    return n


print(my_sum(1, 2, 3, 4))
print(my_sum(1,2,3,4,5,6,7))

def show_info(**kwargs):
    # 遍历 kwargs，把每个 "键: 值" 打印出来
    for a,b in kwargs.items():
        print(a,b)

show_info(name="小明", age=20)



# 你要定义：
def 汇总配送单(园所名, *菜单, **附加):
    print("园所:", 园所名)
    print("菜单:", ", ".join(菜单))
    for 键, 值 in 附加.items():
        print(键 + ":", 值)

# 这样调用它：
汇总配送单("珑湖湾", "青菜", "豆腐", "排骨", 供应商="鑫鑫", 日期="2026-09-15")

# 期望打印出这 4 项（格式你自己定，能都打出来就算对）：
#   园所: 珑湖湾
#   菜单: 青菜, 豆腐, 排骨
#   供应商: 鑫鑫
#   日期: 2026-09-15




















