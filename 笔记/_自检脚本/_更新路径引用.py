# -*- coding: utf-8 -*-
"""目录重组后，统一更新所有文档/脚本里的旧路径引用。

旧 → 新
  D:\\pythonProject              → D:\\AI应用工程师\\01-学习仓库-Python学习路径\\pythonProject
  D:\\kb                         → D:\\AI应用工程师\\07-知识库-LLM-Wiki\\kb
  D:\\MLP_MNIST_实验             → D:\\AI应用工程师\\04-作品-MLP手写神经网络\\MLP_MNIST_实验
  D:\\幼儿园菜                   → D:\\AI应用工程师\\02-作品-幼儿园菜汇总工具\\幼儿园菜
  D:\\作品①课程问答RAG机器人     → D:\\AI应用工程师\\03-作品-课程问答RAG机器人\\作品①课程问答RAG机器人
  D:\\每日总结                   → D:\\AI应用工程师\\08-学习日志-每日总结\\每日总结
  D:\\我的项目                   → D:\\AI应用工程师\\06-练习-Office自动化脚本集\\我的项目
"""
import os
import re

ROOT = r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject"

MAP = [
    (r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject",
     r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject"),
    (r"D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject",
     r"D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject"),
    (r"D:\AI应用工程师\07-知识库-LLM-Wiki\kb",
     r"D:\AI应用工程师\07-知识库-LLM-Wiki\kb"),
    (r"D:\AI应用工程师\04-作品-MLP手写神经网络\MLP_MNIST_实验",
     r"D:\AI应用工程师\04-作品-MLP手写神经网络\MLP_MNIST_实验"),
    (r"D:\AI应用工程师\02-作品-幼儿园菜汇总工具\幼儿园菜",
     r"D:\AI应用工程师\02-作品-幼儿园菜汇总工具\幼儿园菜"),
    (r"D:\AI应用工程师\03-作品-课程问答RAG机器人\作品①课程问答RAG机器人",
     r"D:\AI应用工程师\03-作品-课程问答RAG机器人\作品①课程问答RAG机器人"),
    (r"D:\AI应用工程师\08-学习日志-每日总结\每日总结",
     r"D:\AI应用工程师\08-学习日志-每日总结\每日总结"),
    (r"D:\AI应用工程师\06-练习-Office自动化脚本集\我的项目",
     r"D:\AI应用工程师\06-练习-Office自动化脚本集\我的项目"),
]

TARGET_EXT = {".md", ".py", ".sh", ".txt", ".json"}
changed = {}

for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__")]
    for fn in filenames:
        if os.path.splitext(fn)[1].lower() not in TARGET_EXT:
            continue
        p = os.path.join(dirpath, fn)
        try:
            with open(p, encoding="utf-8") as f:
                s = f.read()
        except Exception:
            continue
        orig = s
        for old, new in MAP:
            s = s.replace(old, new)
        if s != orig:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(s)
            rel = os.path.relpath(p, ROOT)
            changed[rel] = sum(1 for a, b in zip(orig.splitlines(), s.splitlines()) if a != b)
            print("  改了 %-52s (%d 行)" % (rel, changed[rel]))

print("\n共修改 %d 个文件" % len(changed))
