# 标准库3_os_path.py
# 只学 1 个问题：路径怎么拼才不出错

import os
from os import path

print("=" * 50)
print("os.path：拼路径")
print("=" * 50)
print()

# ---------- 核心：为什么不能用 + 拼路径 ----------
print("① 错误的拼法：")
错 = "D:/项目" + "/子目录" + "/文件.txt"
print("   ", 错)
print("   ❌ Windows 上凑合能用，Mac/Linux 上直接崩")
print()

# ---------- 正确：os.path.join ----------
print("② 正确的拼法：")
对 = path.join("D:/项目", "子目录", "文件.txt")
print("   ", 对)
print("   ✅ 自动用当前系统的分隔符")
print()

# ---------- 2 个超常用 ----------
print("③ os.path.dirname：去掉文件名，剩目录")
print("   ", path.dirname("D:/项目/子目录/文件.txt"))
print()

print("④ os.path.basename：去掉目录，剩文件名")
print("   ", path.basename("D:/项目/子目录/文件.txt"))
print()

print("⑤ os.path.exists：文件在不在")
print("   ", path.exists("D:/项目/子目录/文件.txt"))
print("   ", path.exists("标准库3_os_path.py"))
print()

print("=" * 50)
print("记住 4 个：")
print("  path.join(...)        拼路径")
print("  path.dirname(...)     取目录")
print("  path.basename(...)    取文件名")
print("  path.exists(...)      在不在")
print("=" * 50)
