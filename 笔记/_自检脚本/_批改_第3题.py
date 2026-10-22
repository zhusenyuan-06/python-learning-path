# -*- coding: utf-8 -*-
"""第 3 题：B 方案真的更适合吗？用真实场景检验"""
contacts = {"小明": {"电话": "13800138000", "备注": "同事"}}

def a_方案B(name, p):
    """B：明确覆盖，直接赋值"""
    contacts[name] = {"电话": p}
    return "已更新"

def a_方案A(name, p):
    """A：明确不覆盖"""
    if name in contacts:
        return "已存在，未覆盖"
    contacts[name] = {"电话": p}
    return "已添加"

print("=== 场景：用户不小心输了个已存在的名字 ===")
print("添加前:", contacts)
print()
r = a_方案B("小明", "13911112222")
print("B 返回:", r)
print("添加后:", contacts)
print(">>> 备注'同事'没了，旧电话 13800138000 没了")
print("    用户以为自己'添加'了一个人，实际上抹掉了原来的数据")
print()

print("=== A 方案同样操作 ===")
contacts2 = {"小明": {"电话": "13800138000", "备注": "同事"}}
r2 = a_方案A("小明", "13911112222")
print("A 返回:", r2)
print("添加后:", contacts2)
print(">>> 数据没动，且明确告诉用户'已存在，未覆盖'")
print()

print("=== 但如果 B 改个名，就完全合法 ===")
def update_contact(name, p):
    """明确是'更新'操作，覆盖就是预期行为"""
    contacts[name] = {"电话": p}
    return "已更新"
r3 = update_contact("小明", "13911112222")
print("update_contact 返回:", r3)
print(">>> 函数名说明了意图，没有歧义 -> B 是对的")
