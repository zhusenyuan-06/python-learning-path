# 模块本质探针.py
# 不是答案，是 X 光片：看清「模块」到底是什么

print("=" * 60)
print("一、模块就是「一个 .py 文件」")
print("=" * 60)
print("配送工具.py 里有 1 个函数：生成配送单")
print("import 配送工具  →  相当于把那个文件的代码「搬」到这个文件里")
print()

print("=" * 60)
print("二、搬过来的不只是函数，还有模块里的所有名字")
print("=" * 60)

import 配送工具

# 打印模块里都有什么（dir = 列出模块内的名字）
print("dir(配送工具) 里有：")
for 名字 in dir(配送工具):
    if not 名字.startswith("_"):
        print(f"    {名字}")
print()

print("=" * 60)
print("三、模块的身份：它有「身份证」")
print("=" * 60)
print("配送工具.__name__      =", 配送工具.__name__)
print("配送工具.__file__      =", 配送工具.__file__.split("\\")[-1])
print()

print("=" * 60)
print("四、import 的两种「时机」—— 这是真实项目里最常踩的坑")
print("=" * 60)
print("写法 A：import 整个模块 → 模块顶层代码**立刻执行**")
print("写法 B：from 模组 import 函数 → 只拿函数，模块顶层代码**也执行**")
print("（两者都会执行模块顶层！想「延迟执行」要用 importlib）")
print()

print("=" * 60)
print("五、import 会缓存：同一个文件不会被执行两次")
print("=" * 60)
import 配送工具          # 第 2 次 import 同一个模块
import 配送工具 as dd    # 第 3 次，起了别名
print("两个名字指向的是不是同一个模块？", 配送工具 is dd)
print("→ 是的。模块只加载一次，之后都从缓存里拿。")
print()

print("=" * 60)
print("六、__name__ 的魔法：直接运行 vs 被导入")
print("=" * 60)
print("在 配送工具.py 里写：print('我是', __name__)")
print("  直接运行 配送工具.py      → 打印「我是 __main__」")
print("  被别的文件 import 进来   → 打印「我是 配送工具」")
print()
print("这就是为什么很多项目底部都有这行：")
print('    if __name__ == "__main__":')
print("        main()")
print("→ 只有「直接运行这个文件」时才执行下面的代码")
