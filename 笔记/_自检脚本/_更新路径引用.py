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
    # ---- 2026-11-01 目录重构（作品化 + 笔记分类）----
    # 错题追踪器 → 第 4 个作品 projects/error-tracker/
    ("笔记/错题追踪器.py", "projects/error-tracker/错题追踪器.py"),
    ("笔记\\错题追踪器.py", "projects\\error-tracker\\错题追踪器.py"),
    ("笔记/错题追踪器_README.md", "projects/error-tracker/README.md"),
    ("笔记\\错题追踪器_README.md", "projects\\error-tracker\\README.md"),
    ("笔记/错题追踪.json", "projects/error-tracker/错题追踪.json"),
    ("笔记\\错题追踪.json", "projects\\error-tracker\\错题追踪.json"),
    ("笔记/错题追踪.md", "projects/error-tracker/错题追踪.md"),
    ("笔记\\错题追踪.md", "projects\\error-tracker\\错题追踪.md"),
    # 笔记/ 按类型分层
    ("笔记/周四大复习_", "笔记/复习卷/周四大复习_"),
    ("笔记\\周四大复习_", "笔记\\复习卷\\周四大复习_"),
    ("笔记/10-30_答案与讲解_", "笔记/讲义/10-30_答案与讲解_"),
    ("笔记\\10-30_答案与讲解_", "笔记\\讲义\\10-30_答案与讲解_"),
    ("笔记/10-30_补讲_", "笔记/讲义/10-30_补讲_"),
    ("笔记\\10-30_补讲_", "笔记\\讲义\\10-30_补讲_"),
    ("笔记/10-30_错题巩固清单.md", "笔记/讲义/10-30_错题巩固清单.md"),
    ("笔记\\10-30_错题巩固清单.md", "笔记\\讲义\\10-30_错题巩固清单.md"),
    ("笔记/10-28_三道变式题_批改与解析.md", "笔记/讲义/10-28_三道变式题_批改与解析.md"),
    ("笔记\\10-28_三道变式题_批改与解析.md", "笔记\\讲义\\10-28_三道变式题_批改与解析.md"),
    ("笔记/第1-4周总复习清单.md", "笔记/讲义/第1-4周总复习清单.md"),
    ("笔记\\第1-4周总复习清单.md", "笔记\\讲义\\第1-4周总复习清单.md"),
    ("笔记/学习总结_2026-10-27_模块与导入.md", "笔记/讲义/学习总结_2026-10-27_模块与导入.md"),
    ("笔记\\学习总结_2026-10-27_模块与导入.md", "笔记\\讲义\\学习总结_2026-10-27_模块与导入.md"),
    ("笔记/周复盘_", "笔记/周复盘/周复盘_"),
    ("笔记\\周复盘_", "笔记\\周复盘\\周复盘_"),
    ("笔记/周复盘模板_", "笔记/周复盘/周复盘模板_"),
    ("笔记\\周复盘模板_", "笔记\\周复盘\\周复盘模板_"),
    ("笔记/JD能力缺口登记_2026-10-27.md", "笔记/求职/JD能力缺口登记_2026-10-27.md"),
    ("笔记\\JD能力缺口登记_2026-10-27.md", "笔记\\求职\\JD能力缺口登记_2026-10-27.md"),
    ("笔记/能力缺口清单.md", "笔记/求职/能力缺口清单.md"),
    ("笔记\\能力缺口清单.md", "笔记\\求职\\能力缺口清单.md"),
    ("笔记/求职路线评估_诚实版.md", "笔记/求职/求职路线评估_诚实版.md"),
    ("笔记\\求职路线评估_诚实版.md", "笔记\\求职\\求职路线评估_诚实版.md"),
    ("笔记/资产盘点_2026-10-27.md", "笔记/求职/资产盘点_2026-10-27.md"),
    ("笔记\\资产盘点_2026-10-27.md", "笔记\\求职\\资产盘点_2026-10-27.md"),
    ("笔记/三件缺失事_操作手册.md", "笔记/求职/三件缺失事_操作手册.md"),
    ("笔记\\三件缺失事_操作手册.md", "笔记\\求职\\三件缺失事_操作手册.md"),
    ("笔记/工具链坑", "笔记/工具链/工具链坑"),
    ("笔记\\工具链坑", "笔记\\工具链\\工具链坑"),
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
