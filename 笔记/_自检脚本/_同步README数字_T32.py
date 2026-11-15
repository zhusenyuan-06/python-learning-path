# -*- coding: utf-8 -*-
"""同步 README 里的工具链坑数字：31 条 / 39 次 → 32 条 / 40 次"""
import io
import os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

改动 = [
    ("README.md", [
        ("- **31 条工具链坑** —— git / 网络 / Windows 环境的坑，踩一次记一次",
         "- **32 条工具链坑** —— git / 网络 / Windows 环境的坑，踩一次记一次"),
        ("已积累 31 条 / 39 次踩坑", "已积累 32 条 / 40 次踩坑"),
        ("工具链坑 26→31 条", "工具链坑 26→32 条"),
    ]),
    ("笔记/工具链/工具链坑_README.md", [
        ("**补入 T25~T31**", "**补入 T25~T32**"),
        ("→ **31 条 / 39 次**", "→ **32 条 / 40 次**"),
    ]),
]

for 路径, 对 in 改动:
    s = io.open(路径, encoding="utf-8").read()
    for 旧, 新 in 对:
        if 旧 not in s:
            print("⚠️ 没找到：%s（%s）" % (路径, 旧[:40]))
            continue
        s = s.replace(旧, 新)
    io.open(路径, "w", encoding="utf-8").write(s)
    print("✅ 已更新", 路径)
