# -*- coding: utf-8 -*-
"""第 5 题：类型不统一到底怎么炸"""
contacts = {
    "小明": {"电话": 13800138000},
    "小红": {"电话": "13900139000"}
}

print("=== 隐患 1：拼接 ===")
try:
    r = "电话：" + contacts["小明"]["电话"]
    print("结果:", r)
except Exception as e:
    print("报错:", type(e).__name__, "|", e)
print()

print("=== 隐患 2：比较 ===")
print("'13900139000' == 13900139000 ?", "13900139000" == 13900139000)
print(">>> 明明是同一个号码，却判定为【不相等】—— 静默错误！")
print()

print("=== 隐患 3：排序 ===")
try:
    lst = sorted([13800138000, "13900139000"])
    print("结果:", lst)
except Exception as e:
    print("报错:", type(e).__name__, "|", e)
print()

print("=== 隐患 4：存文件再读回来 ===")
import json, tempfile, os
p = os.path.join(tempfile.gettempdir(), "_t.json")
with open(p, "w", encoding="utf-8") as f:
    json.dump(contacts, f, ensure_ascii=False)
with open(p, encoding="utf-8") as f:
    back = json.load(f)
print("读回来:", back)
print("小明的电话类型:", type(back["小明"]["电话"]).__name__)
print(">>> 数字又变回数字了，类型【不稳定】")
os.remove(p)
print()

print("=== 第 3 问：前导 0 ===")
phone = "01390139000"      # 字符串，前导0 保住
print("字符串存:", phone, "-> 长度", len(phone))
num = 13901390000          # 数字，前导0 没了
print("数字存:  ", num, "-> 长度", len(str(num)))
print()
print("更狠的：Excel 打开手机号列，自动识别成数字，前导0 全丢")
print("真实事故：座机号 010-8888 存成数字后变成 108888")
print()

print("=== 统一成字符串（正确）===")
good = {
    "小明": {"电话": "13800138000"},
    "小红": {"电话": "13900139000"}
}
print(good)
print("拼接:", "电话：" + good["小明"]["电话"])
print("比较:", good["小红"]["电话"] == "13900139000")
