班级A = {"小明": {"语文": 90, "数学": 85},
         "小红": {"语文": 70, "数学": 89}}

班级B = {"小刚": {"语文": 95, "数学": 92},
         "小丽": {"语文": 88, "数学": 78}}

# 合并两个 dict
总表 = dict(班级A); 总表.update(班级B)
print(总表)

def sum_list(nums):
    n = 0
    for i in nums:
        n+= i
    return n


d = []
for name,object in 总表.items():
    fenshu = list(object.values())
    zongfen = sum_list(fenshu)
    d.append((name,zongfen))
print(d)
# 第3步：按总分从高到低排序，取前3名
排名 = sorted(d, key=lambda x:x[1], reverse=True)
前3 = 排名[:3]
print(前3)
# 第4步：打印前三名，带名次
for i, (名字, 总分) in enumerate(前3, 1):
    print(i, 名字, 总分)
