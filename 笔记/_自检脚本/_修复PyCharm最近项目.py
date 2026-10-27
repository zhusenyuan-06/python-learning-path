# -*- coding: utf-8 -*-
"""修复 PyCharm 的「最近项目」列表 —— 目录重组后旧路径全部失效。

作用：把 recentProjects.xml 里的旧路径批量改成新路径，
这样 PyCharm 欢迎界面里的最近项目直接能点开。

注意：PyCharm 运行中会在退出时把内存配置写回、覆盖这个修改。
所以必须「完全退出 PyCharm」→ 改 → 重开。
"""
import os
import shutil
import sys
import time

F = r"C:\Users\15816\AppData\Roaming\JetBrains\PyCharmCE2024.2\options\recentProjects.xml"

# 必须按路径长度从长到短替换，否则短路径会先命中、把长路径截断
MAP = [
    ("D:/我的项目/自动化办公/自动化办公",
     "D:/AI应用工程师/06-练习-Office自动化脚本集/我的项目/自动化办公/自动化办公"),
    ("D:/我的项目/自动化办公",
     "D:/AI应用工程师/06-练习-Office自动化脚本集/我的项目/自动化办公"),
    ("D:/pythonProject",
     "D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject"),
    ('value="D:/"', 'value="D:/AI应用工程师"'),
]


def main():
    if not os.path.exists(F):
        raise SystemExit("找不到配置文件: %s" % F)

    with open(F, encoding="utf-8") as f:
        s = f.read()

    if "D:/AI应用工程师" in s:
        print("[OK] 已经是新路径了，不需要改")
        return

    bak = F + ".bak_%s" % time.strftime("%Y%m%d_%H%M%S")
    shutil.copy2(F, bak)
    print("[1] 已备份 -> %s" % os.path.basename(bak))

    for old, new in MAP:
        n = s.count(old)
        if n:
            s = s.replace(old, new)
            print("    %-38s -> 替换 %d 处" % (old, n))

    with open(F, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)
    print("[2] 已写入新配置")

    # 校验
    with open(F, encoding="utf-8") as f:
        s2 = f.read()
    print("\n=== 校验：剩余的 D 盘路径 ===")
    import re
    paths = sorted(set(re.findall(r'D:/[^"<]*', s2)))
    for p in paths:
        exists = os.path.exists(p.replace("/", "\\"))
        print("  %-72s %s" % (p, "存在 ✅" if exists else "不存在 ❌"))


if __name__ == "__main__":
    main()
