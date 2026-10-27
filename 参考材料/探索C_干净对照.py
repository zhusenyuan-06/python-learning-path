# 探索C_干净对照.py
# 证明：「不报错」不是因为 import 没用，而是因为名字早就被绑定了

print("=" * 62)
print("实验 1：新文件，第一次用就调用（没 import）")
print("=" * 62)

# 这里直接调用，什么都不 import
try:
    生成配送单("珑湖湾")
except NameError as e:
    print(f"❌ NameError: {e}")
    print("   ↑ 报错原因：当前文件里根本没有这个名字")
print()

print("=" * 62)
print("实验 2：先 import，再调用（同一个文件里）")
print("=" * 62)

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "教学"))

from 配送工具 import 生成配送单

生成配送单("珑湖湾", "青菜", "豆腐", 供应商="鑫鑫")
print("✅ 没报错 —— 因为第 30 行已经把名字绑进来了")
print()

print("=" * 62)
print("实验 3：⭐ 关键！import 写在文件「最末尾」，调用写在「最前面」")
print("=" * 62)

print("  ↓↓↓ 第 40 行，调用 ↓↓↓")
try:
    生成配送单2("珑湖湾")
except NameError as e:
    print(f"❌ NameError: {e}")
    print("   ↑ 报错了！import 在下面，但上面用不到它")
print()

print("  ↓↓↓ 第 60 行，import ↓↓↓")
from 配送工具 import 生成配送单 as 生成配送单2
print("  （import 执行完了，现在名字才绑定）")
print()

print("=" * 62)
print("实验 4：⭐⭐ 关键中的关键！换个文件就不灵了")
print("=" * 62)
print("  你的文件里 import 过 配送工具 —— 那只是「你的文件」能用")
print("  换到 另一个文件 里，必须【重新 import】一次")
print()
print("  验证方法：新建一个空文件，只写一行调用，不写 import → 立刻 NameError")
print()

print("=" * 62)
print("结论")
print("=" * 62)
print("1. import 不是「从这一行往下生效」，是「把名字绑进整个文件」")
print("2. 但 Python 从上往下执行，所以【调用写在 import 前面】照样 NameError")
print("3. 每个 .py 文件都有自己独立的命名空间，A 文件 import 了，B 文件还得自己 import")
