# 标准库2_csv.py
# 只学 1 个函数：怎么把 csv 读成一堆行

import csv

print("=" * 50)
print("csv：表格文件 <--> 列表的列表")
print("=" * 50)
print()

# 先造一个 csv 文件试试
文件名 = "临时测试.csv"

要写的内容 = [
    ["菜名", "重量", "金额"],
    ["青菜", "12.5", "38.50"],
    ["豆腐", "8.0", "16.00"],
]

# 写文件
with open(文件名, "w", encoding="utf-8", newline="") as f:
    写手 = csv.writer(f)
    写手.writerows(要写的内容)

print("① 已经写好了文件：", 文件名)
print("   打开看看内容：")
with open(文件名, "r", encoding="utf-8") as f:
    for 一行 in f:
        print("      ", 一行.rstrip())
print()

# ---------- 唯一要学的：reader ----------
print("② 用 csv.reader 读回来：")
with open(文件名, "r", encoding="utf-8", newline="") as f:
    for 一行 in csv.reader(f):
        print("      ", 一行)
print()

print("③ 注意每行的类型：")
with open(文件名, "r", encoding="utf-8", newline="") as f:
    for 一行 in csv.reader(f):
        print("      ", 一行, "→ 各格类型：", [type(格).__name__ for 格 in 一行])
print()

print("=" * 50)
print("记住：")
print("  csv.reader(f)  →  一行一行给你，每行是一个列表")
print("  ⚠️ 读出来全是【字符串】，要算数得自己转 float()")
print("=" * 50)
