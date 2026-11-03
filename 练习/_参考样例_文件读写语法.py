# 参考样例：文件读写 + pathlib 语法
# ⚠️ 这个文件只讲【语法怎么写】，里面【没有今天的题目答案】。
#    看完关掉，然后从空白写 11.03练习_文件读写与pathlib.py

# ---------- open() 写 ----------
with open("demo.txt", "w", encoding="utf-8") as f:
    f.write("hello\n")
    f.writelines(["a\n", "b\n"])       # 一次写多行

# ---------- open() 读：两种方式，别混 ----------
with open("demo.txt", "r", encoding="utf-8") as f:
    content = f.read()                 # 一次性全读成一个大字符串
    print(content)

with open("demo.txt", "r", encoding="utf-8") as f:
    for line in f:                     # 一行一行读，大文件必须用这种
        print(line.strip())            # strip() 去掉行尾换行符

# ---------- 读的三种写法，各返回什么不一样 ----------
with open("demo.txt", "r", encoding="utf-8") as f:
    content = f.read()                 # → 字符串，整个文件的内容
    print(content)

with open("demo.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()              # → 列表，每个元素是一行（带 \n）
    print(len(lines))                  # 数行数就用它

with open("demo.txt", "r", encoding="utf-8") as f:
    for line in f:                     # → 一次只给你一行
        print(line[:5])                # 切片取每行前 5 个字符

# ⚠️ with 块一结束，门就关了
# with open("demo.txt", "r", encoding="utf-8") as f:
#     pass
# print(f.read())      # ❌ ValueError: I/O operation on closed file

# ⚠️ 坑：split("\n") 比 readlines() 多一个空元素
# "a\nb\n".split("\n")        → ['a', 'b', '']   长度 3
# len("a\nb\n".readlines())   → 2

# ⚠️ 坑：列表里多个字符串，逗号写在引号【外面】
# ["a\n", "b\n"]              ✅ 正确
# ["a\n" "b\n"]               ❌ 错，这是【字符串拼接】，合成 "a\nb\n" 一个元素

# ---------- pathlib ----------
from pathlib import Path

p = Path(".")                         # 当前目录
print(p.resolve())                    # 转成绝对路径

for f in p.glob("*.txt"):             # 找当前目录下所有 txt
    print(f.name)

for f in p.glob("*.py"):
    print(f.name, f.stat().st_size)    # 文件名 + 字节大小

target = Path("输出") / "结果.txt"     # 拼路径（用 / 运算符，别用 + 拼字符串）
target.parent.mkdir(parents=True, exist_ok=True)   # 建目录，父目录不存在也能建
print(target.resolve())               # 看最终路径长什么样
