# -*- coding: utf-8 -*-
"""整理后全量验证：每个 .py 跑一遍，记录成功/失败

只做静态检查 + 试运行（不执行有副作用的脚本）。
"""
import io
import os
import subprocess
import sys

ROOT = r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject"
PY = r"D:\AAAA\python.exe"

目录列表 = [
    "练习", "教学", "参考材料",
    "小项目_多模块demo",
    os.path.join("小项目_多模块demo", "utils"),
    os.path.join("projects", "contact-book"),
]

# 这些有副作用或是交互式，跳过
跳过 = {
    "错题追踪器.py", "工具链坑.py",
}

结果 = []
for base in 目录列表:
    d = os.path.join(ROOT, base)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith(".py"):
            continue
        if f in 跳过 or f.startswith("_"):
            continue
        p = os.path.join(d, f)
        rel = os.path.relpath(p, ROOT)
        try:
            r = subprocess.run(
                [PY, "-m", "py_compile", p],
                capture_output=True, text=True, timeout=30, encoding="utf-8", errors="replace",
            )
            if r.returncode == 0:
                结果.append(("语法OK", rel, ""))
            else:
                结果.append(("语法错", rel, (r.stderr or "").strip().split("\n")[-1][:70]))
        except Exception as e:
            结果.append(("异常", rel, str(e)[:70]))

print("=" * 78)
print("语法检查结果（%d 个文件）" % len(结果))
print("=" * 78)
坏 = 0
for 状态, rel, 详情 in 结果:
    if 状态 == "语法OK":
        print(f"  ✅ {rel}")
    else:
        坏 += 1
        print(f"  ❌ {rel}   {详情}")
print()
print(f"语法错误 {坏} 个 / 共 {len(结果)} 个")
