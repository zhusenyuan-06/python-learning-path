import 配送工具

print("=== 探索 A 复现：函数名写错 ===")
try:
    配送工具.生成配送单表("珑湖湾")
except AttributeError as e:
    print(f"AttributeError: {e}")

print()
print("=== 探索 B 复现：模块名写错 ===")
try:
    import 配送工具x
except ModuleNotFoundError as e:
    print(f"ModuleNotFoundError: {e}")

print()
print("=== 探索 C 复现：新文件没 import 就用 ===")
try:
    生成配送单("珑湖湾")
except NameError as e:
    print(f"NameError: {e}")

print()
print("=== 补充：import 时模块顶层的 print 会不会执行？ ===")
print("→ 看下面这行输出，验证「导入模块 = 执行模块顶层代码」")
