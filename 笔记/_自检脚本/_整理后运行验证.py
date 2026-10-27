# -*- coding: utf-8 -*-
"""整理后真实运行验证：跑一遍看有没有运行期错误"""
import os
import subprocess

ROOT = r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject"
PY = r"D:\AAAA\python.exe"

# (相对路径, 期望输出里应含的关键词)  关键词为空 = 只看是否报错
用例 = [
    (os.path.join("练习", "10.21练习.py"), None),
    (os.path.join("练习", "10.27练习.py"), "园所"),
    (os.path.join("练习", "10.27练习_模块.py"), "园所"),
    (os.path.join("练习", "词频统计器进阶版.py"), None),
    (os.path.join("教学", "标准库1_json.py"), "菜名"),
    (os.path.join("教学", "标准库2_csv.py"), "菜名"),
    (os.path.join("教学", "标准库3_os_path.py"), "dirname"),
    (os.path.join("教学", "ensure_ascii对比.py"), "菜名"),
    (os.path.join("参考材料", "模块本质探针.py"), "生成配送单"),
    (os.path.join("参考材料", "探索C_干净对照.py"), "NameError"),
    (os.path.join("参考材料", "谁导入了我.py"), "计算总价"),
    (os.path.join("参考材料", "_验证报错.py"), "AttributeError"),
    (os.path.join("参考材料", "main守卫演示.py"), "我是工具函数"),
    (os.path.join("参考材料", "10.27练习_探针.py"), "菜单"),
    (os.path.join("参考材料", "标准库1_json_作业答案.py"), "排骨"),
    (os.path.join("参考材料", "模块与导入_3问答案.py"), "Q1"),
    (os.path.join("小项目_多模块demo", "main.py"), "园所"),
    (os.path.join("projects", "contact-book", "contact_book.py"), None),
]

好 = 0
坏 = 0
print("=" * 78)
print("真实运行验证")
print("=" * 78)
for rel, 关键词 in 用例:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        print(f"  ⚠️  {rel}  —— 文件不存在")
        坏 += 1
        continue
    try:
        r = subprocess.run(
            [PY, p], capture_output=True, text=True, timeout=60,
            encoding="utf-8", errors="replace",
            cwd=os.path.dirname(p),
        )
    except Exception as e:
        print(f"  ❌ {rel}  —— 异常 {str(e)[:50]}")
        坏 += 1
        continue

    out = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0:
        最后 = [x for x in out.strip().split("\n") if x.strip()]
        print(f"  ❌ {rel}  退出码 {r.returncode}")
        print(f"      {最后[-1][:74] if 最后 else '(无输出)'}")
        坏 += 1
    elif 关键词 and 关键词 not in out:
        print(f"  ⚠️  {rel}  —— 没找到关键词「{关键词}」")
        坏 += 1
    else:
        print(f"  ✅ {rel}")
        好 += 1

print()
print(f"通过 {好} / {好+坏}")
