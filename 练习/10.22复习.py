contacts = {
    "小明": {"电话": '13800138000'},
    "小红": {"电话": "13900139000"}
}

def c(name):
    if name not in contacts:
        print('查无此人')
    else:
        print(contacts[name]["电话"])

def a(name, p):
    if name in contacts:
        print("已存在，未覆盖")
    contacts[name] = {"电话": p}

c("小刚")          # 查一个不存在的人
a("小明", "13700137000")
print(contacts)





