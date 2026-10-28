# -*- coding: utf-8 -*-
"""校验 README 里的图片链接和文件链接是否真实存在"""
import os
import re

ROOT = r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject"
README = os.path.join(ROOT, "README.md")

with open(README, encoding="utf-8") as f:
    src = f.read()

print("=" * 70)
print("① 图片链接检查")
print("=" * 70)
图片 = re.findall(r'<img\s+src="([^"]+)"', src)
if not 图片:
    print("  （没有图片）")
坏 = 0
for p in 图片:
    存在 = os.path.exists(os.path.join(ROOT, p))
    print(f"  {'✅' if 存在 else '❌'} {p}")
    if not 存在:
        坏 += 1

print()
print("=" * 70)
print("② 仓库内文件链接检查（相对链接）")
print("=" * 70)
链接 = re.findall(r'\]\((?!https?://)([^)#]+)\)', src)
for p in 链接:
    存在 = os.path.exists(os.path.join(ROOT, p))
    print(f"  {'✅' if 存在 else '❌'} {p}")
    if not 存在:
        坏 += 1

print()
print("=" * 70)
print("③ README 里「怎么跑」的路径是否真实存在")
print("=" * 70)
for p in ["小项目_多模块demo", "projects/contact-book", "笔记",
          "小项目_多模块demo/main.py", "projects/contact-book/contact_book.py",
          "笔记/错题追踪器.py", "笔记/工具链坑.py", "笔记/错题追踪.md"]:
    存在 = os.path.exists(os.path.join(ROOT, p))
    print(f"  {'✅' if 存在 else '❌'} {p}")
    if not 存在:
        坏 += 1

print()
print("=" * 70)
print("④ 截图目录里有哪些文件（README 引用之外的多余文件要清理）")
print("=" * 70)
截图目录 = os.path.join(ROOT, "截图")
引用集 = set(os.path.basename(p) for p in 图片)
for f in sorted(os.listdir(截图目录)):
    标记 = "← 被引用" if f in 引用集 else "← 未被引用（可删）"
    print(f"  {f}  {标记}")

print()
print("=" * 70)
print(f"结果：{坏} 个问题")
print("=" * 70)
