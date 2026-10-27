#def my_sum(*args):
 #   total = 0
  #  for n in args:
   #     total += n
    #return total

#print(my_sum(1, 2, 3))        # 期望 6
#print(my_sum(1, 2, 3, 4, 5))  # 期望 15
#print(my_sum(10))             # 期望 10





#def show_info(**kwargs):
 #   for k,v in kwargs.items():
  #      print(f'{k},{v}')
# TODO: 遍历 kwargs，把每个 "键: 值" 打印出来
    # 提示：kwargs 是字典 → 用 for k, v in kwargs.items(): 再 print
    # 复习踩坑本第 12 条：字典遍历 items()

# 下面测试不用改，直接跑：
#show_info(name="小明", age=20, major="AI应用")
#show_info(city="上海", weather="晴")



def f(a, b, *args, **kwargs):
    print("固定参数:", a, b)
    print("多余位置参数:", args)
    print("关键字参数:", kwargs)

f(1, 2, 3, 4, 5, x=10, y=20)
