# open_review.py —— 一键打开今天的周四大复习卷
# 2026-10-29 · 阶段1 第5周
#
# ---------------------------------------------------------------
# 这个文件回答一个问题：复习卷在磁盘深处，怎么一键打开？
#
# 为什么不让 bat 直接写中文路径：
#   cmd 读批处理文件时，文件内容里的中文按 ANSI 解释，
#   UTF-8 存的中文路径会变成乱码 → 找不到文件。
#   （今晚写《修复GitHub访问_v2.bat》时就踩过类似的编码坑）
#   所以：bat 内容全 ASCII，路径由这个 py 用 glob 去找。
#   py 源码是 UTF-8，Python 3 默认按 UTF-8 读，中文没问题。
#
# 怎么用：
#   双击桌面「打开复习卷.bat」，它会调本文件，
#   本文件用系统默认程序打开复习卷（VS Code / 记事本都行）。
# ---------------------------------------------------------------

import glob
import os
import re
import sys
from pathlib import Path

# 笔记目录（用 Path 拼，避免手写长反斜杠）
NOTES = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")

# 要排除的文件
#   └─ 「答案与讲解」= 答案卷，做题时绝不能提前打开
#   └─ 「使用说明」= 操作手册，不是卷子
EXCLUDE = ("答案", "使用说明")


def find_review():
    """找出今天的复习卷。

    逐行拆解：
        glob.glob(模式)
          └─ 按【通配符模式】找文件，比遍历目录再判断快
          └─ 模式里的 * 可以代表任意长度的字符
          └─ 周四大复习_*.md 会同时匹配到「复习卷」和「答案与讲解」
            和「使用说明」—— 所以下面还要排除

        排序：
          └─ 文件名里带日期（2026-10-29），所以按文件名倒序排，
            最新的排在最前面 → 取第 0 个就是最新的那份
            （比按修改时间排更稳：万一你复制过一份，修改时间会乱）

        re.search(数字)
          └─ 正则：从文件名里抠出日期，用来排除「使用说明」这种
            不带日期的文件
    """
    pattern = str(NOTES / "周四大复习_*.md")
    files = sorted(glob.glob(pattern), reverse=True)
    for f in files:
        name = os.path.basename(f)
        if any(x in name for x in EXCLUDE):
            continue                       # 答案卷/说明文档，跳过
        if not re.search(r"\d{4}-\d{2}-\d{2}", name):
            continue                       # 文件名里没有日期的，跳过
        return f
    return None


def main():
    path = find_review()
    if not path:
        print("[X] 没找到复习卷。")
        print("    应该在：%s" % (NOTES / "周四大复习_YYYY-MM-DD_复习卷.md"))
        print("    跑一下：\"D:\\AAAA\\python.exe\" 错题追踪器.py plan 6 生成")
        input("\n按回车键关闭...")
        return 1

    print("复习卷：%s" % path)
    print("正在用系统默认程序打开 ...")
    # os.startfile(路径) = 用【系统默认程序】打开这个文件
    #   └─ .md 在你机器上默认是 VS Code 或记事本
    #   └─ 比自己拼 start 命令稳，也不会有引号问题
    try:
        os.startfile(path)
    except Exception as e:
        print("[!] 自动打开失败：%s" % e)
        print("    请手动打开上面的路径。")
        input("\n按回车键关闭...")
        return 1

    print()
    print("=" * 60)
    print("  作答流程")
    print("=" * 60)
    print("  1. 每题只先看「❌ 错在这」那段代码")
    print("  2. 在「你的作答」框里写三样：")
    print("     ① 这段代码错在哪")
    print("     ② 改写后的代码")
    print("     ③ 改完之后凭什么就「跑得对」了")
    print("  3. 9 题全做完，再逐题记结果（别一题一题提前记）：")
    print()
    print('     cd /d "D:\\AI应用工程师\\01-学习仓库-Python学习路径\\pythonProject\\笔记"')
    print('     "D:\\AAAA\\python.exe" 错题追踪器.py record E15 pass "你的理解"')
    print('     "D:\\AAAA\\python.exe" 错题追踪器.py record E01 fail "又错在哪"')
    print()
    print("  4. 全做完收尾：")
    print('     "D:\\AAAA\\python.exe" 错题追踪器.py render')
    print('     "D:\\AAAA\\python.exe" 错题追踪器.py stats')
    print()
    print("  提示：答案卷（答案与讲解.md）要等你交卷后我再给你，")
    print("        提前看等于没做。")
    input("\n按回车键关闭...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
