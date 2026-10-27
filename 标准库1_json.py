# 标准库1_json.py
# 只学 3 个函数，10 分钟搞定

import json

print("=" * 50)
print("json 只干一件事：字典 <--> 字符串 互转")
print("=" * 50)
print()

# ---------- 1. dumps：字典变成字符串 ----------
订单 = {"菜名": "青菜", "重量": 12.5, "送到": "珑湖湾"}

字符串 = json.dumps(订单, ensure_ascii=False)
print("① 原字典：", 订单)
print("   类型是：", type(订单))
print()
print("② dumps 之后：", 字符串)
print("   类型是：", type(字符串))
print()

# ---------- 2. loads：字符串变回字典 ----------
字典 = json.loads(字符串)
print("③ loads 之后：", 字典)
print("   类型是：", type(字典))
print()
print("④ 来回转了一圈，数据一样吗？", 字典 == 订单)
print()

# ---------- 3. indent：让 JSON 好看点（给人看的时候用）----------
好看 = json.dumps(订单, ensure_ascii=False, indent=2)
print("⑤ 加了 indent=2 之后：")
print(好看)
print()

print("=" * 50)
print("记住这 3 个就够了：")
print("  json.dumps(对象)  →  对象变字符串（往外发）")
print("  json.loads(字符串) →  字符串变对象（往里收）")
print("=" * 50)


# 【作业】把下面这段补完，预测输出后再运行
订单2 = {"菜名": "排骨", "重量": 15.0, "送到": "阳光城"}
s = json.dumps(订单2, ensure_ascii=False)
print(s)
# ① 用 dumps 把它变成字符串，存到 变量s
# ② 打印 s 的类型
# ③ 把 s 变回字典
# ④ 打印 "排骨" 这个值（提示：字典取值用 ["键名"]）

# 再加一题：
# ⑤ 如果 订单2 里多一个键 "备注": "不要葱"，
#    dumps 出来的字符串里会多出什么？































