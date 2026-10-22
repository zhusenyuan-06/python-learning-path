hong = {"曼德尔超算": 20,"留声机": 10,"复苏呼吸机": 40,"步战车模型": 30 }
#增
if "人头像" not in hong:
    hong["人头像"] = 50
#改
hong["曼德尔超算"] = 90
#查
print(hong.get("留声机"))
#删
hong_gai = hong.pop("步战车模型")
#遍历
for k,v in hong.items():
    print(f'{k},{v}')
#判断key在不在
print("留声机" in hong)
print("金条" in hong)

if "金条" in hong:
    print('有这个红')
else:
    print('没有这个红')

print(f'{hong}')




dechi = {
    '狗弘': {'滑膛枪': 1, '怀表': 2, '卫星锅': 3},
    'm14水瓶座': {'人头像': 1, '化石': 1, '高级咖啡豆': 1},
}

#往内层加一条数据（d["外层"]["内层"] = 值）
dechi['狗弘']['扫地机器人'] = 1

print(dechi['狗弘']['滑膛枪'])

for ren,i in dechi.items():
    print(f'====={ren}====')
    for wu,count in i.items():
        print(f'{ren} {wu}:{count}')



students = {"小明": {"语文": 90, "数学": 85}, "小红": {"语文": 70, "数学": 89}}
students['小明']['英语'] = 100
print(students.get('小刚',{}))
students['小明']['语文'] = 99
print(students)

for r,i in students.items():
    print(f'====={r}====')
    for k,s in i.items():
        print(f'{r} {k}:{s}')

scores = students['小明']        # 先定位一个学生
b = list(scores.values())        # 才是 [99, 85, 100]

def sum_list(nums):
    n = 0
    for i in nums:
        n+= i
    return n

print(f'小明总成绩{sum_list(b)}')

























