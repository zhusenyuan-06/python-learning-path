# -*- coding: utf-8 -*-
"""
SQL 练习自检脚本（幂等 + 自愈）
① 校验练习文件里的 期望_1 是否与数据库真实数据一致
   —— 不一致就【自动重写】成程序生成的真实值（避免手抄）
② 重新校验（必须一致）
③ 生成答案版跑一遍，必须 8 题全绿（证明期望值本身对）
"""
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

根 = Path(__file__).resolve().parents[2]
练习目录 = 根 / "练习"
练习文件 = 练习目录 / "11.17练习_SQL_SELECT与WHERE.py"
临时文件 = 练习目录 / "_临时_答案版_SQL.py"

con = sqlite3.connect(str(练习目录 / "数据" / "新闻库.sqlite"))
真实标题 = [r[0] for r in con.execute("SELECT 新闻内容 FROM 新闻 ORDER BY 序号 ASC")]
con.close()

源 = 练习文件.read_text(encoding="utf-8")


def 取出期望1(文本):
    """取出 期望_1 列表。

    注意：期望_1 是用 %r（repr）写的 —— Python 的 repr 对含中文的字符串
    会输出【单引号】形式，所以不能用找双引号的正则，必须 ast.literal_eval。
    """
    import ast
    块 = re.search(r"期望_1 = \[(.*?)\n\]", 文本, re.S).group(1)
    条 = []
    for 行 in 块.splitlines():
        行 = 行.strip().rstrip(",")
        if not 行:
            continue
        条.append(ast.literal_eval(行))
    return 条


def 生成期望1块(标题们):
    行们 = ["    %r," % t for t in 标题们]
    return "期望_1 = [\n" + "\n".join(行们) + "\n]"


print("=" * 70)
print("① 校验 期望_1（手抄必错，改成程序生成）")
print("=" * 70)
当前 = 取出期望1(源)
print("   文件里的条数: %d | 数据库真实条数: %d" % (len(当前), len(真实标题)))

if 当前 == 真实标题:
    print("   ✅ 已与数据库一致，不用改")
else:
    不同的 = [i for i in range(max(len(当前), len(真实标题)))
               if (当前[i] if i < len(当前) else None) !=
                  (真实标题[i] if i < len(真实标题) else None)]
    print("   ❌ 不一致，差异位置: 第 %s 条" % 不同的[:6])
    新块 = 生成期望1块(真实标题)
    源 = re.sub(r"期望_1 = \[.*?\n\]", 新块, 源, count=1, flags=re.S)
    练习文件.write_text(源, encoding="utf-8")
    print("   ✅ 已用【数据库真实值】重写练习文件里的 期望_1")
    # 重新读一遍校验
    源 = 练习文件.read_text(encoding="utf-8")
    assert 取出期望1(源) == 真实标题, "重写后仍不一致，停止"
    print("   ✅ 重写后复读校验通过")

# ══ ② 生成答案版 ═════════════════════════════════════════════
答案实现 = {
    1: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 新闻内容 FROM 新闻 ORDER BY 序号 ASC")
    结果 = [行[0] for 行 in cur.fetchall()]
    con.close()
    return 结果''',
    2: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM 新闻 WHERE 星期 = ?", ("星期二",))
    条数 = cur.fetchone()[0]
    cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = ? ORDER BY 序号 ASC", ("星期二",))
    序号们 = [行[0] for 行 in cur.fetchall()]
    con.close()
    return 条数, 序号们''',
    3: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 = ? AND 序号 > ? ORDER BY 序号 ASC",
                ("星期一", 5))
    结果 = [行[0] for 行 in cur.fetchall()]
    con.close()
    return 结果''',
    4: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 序号 FROM 新闻 WHERE 新闻内容 LIKE ? OR 新闻内容 LIKE ? ORDER BY 序号 ASC",
                ("%银行%", "%雨雪%"))
    结果 = [行[0] for 行 in cur.fetchall()]
    con.close()
    return 结果''',
    5: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 <> ? AND 序号 <= ? ORDER BY 序号 ASC",
                ("星期六", 6))
    结果 = [行[0] for 行 in cur.fetchall()]
    con.close()
    return 结果''',
    6: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 序号 FROM 新闻 WHERE 序号 BETWEEN ? AND ? ORDER BY 序号 ASC", (3, 8))
    结果 = [行[0] for 行 in cur.fetchall()]
    con.close()
    return 结果''',
    7: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 序号 FROM 新闻 WHERE 星期 IN (?, ?) ORDER BY 序号 ASC",
                ("星期五", "星期日"))
    结果 = [行[0] for 行 in cur.fetchall()]
    con.close()
    return 结果''',
    8: '''    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM 新闻 WHERE 新闻内容 LIKE ?", ("%金融%",))
    结果 = cur.fetchone()[0]
    con.close()
    return 结果''',
}

新源 = 源
for 题号, 实现 in 答案实现.items():
    模式 = r"(def 任务%d_.*?\n    \"\"\".*?\"\"\"\n)    # TODO %d-① 在下面写你的代码\n    pass" % (题号, 题号)
    新源, n = re.subn(模式, lambda m, imp=实现: m.group(1) + imp, 新源, flags=re.S)
    assert n == 1, "第%d题替换失败（找到 %d 处）" % (题号, n)

临时文件.write_text(新源, encoding="utf-8")
print()
print("=" * 70)
print("② 跑答案版（必须 8 题全绿）")
print("=" * 70)
out = subprocess.run([sys.executable, str(临时文件)], capture_output=True, text=True,
                     encoding="utf-8", errors="replace", cwd=str(练习目录))
for l in out.stdout.splitlines():
    s = l.strip()
    if s.startswith(("✅", "❌", "🎉")) or s.startswith("还有"):
        print("   " + s)

全绿 = ("🎉 8 题全过" in out.stdout) and ("❌" not in out.stdout)
print()
print("答案版结论:", "8 题全绿 ✅（期望值本身正确）" if 全绿 else "❌ 未全绿")
if not 全绿:
    print(out.stderr[-800:])

临时文件.unlink()
print("临时文件已清理 → 存在:", 临时文件.exists())
