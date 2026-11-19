# -*- coding: utf-8 -*-
"""JOIN 课堂演示 · 全部跑真库，不口算

运行：
    D:\\AAAA\\python.exe JOIN课堂演示.py

配套讲义：笔记/讲义/11-18_讲义_JOIN连接表.md
配套练习：练习/11.18练习_JOIN连接表.py   ← 你的 4 个 TODO 在那边，这里不动
"""

import os
import sqlite3

库路径 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "数据", "JOIN练习库.sqlite")


def 打印(sql, 标题, 显示表头=True):
    """跑一条 SQL，把结果原样打出来。"""
    print()
    print("=" * 70)
    print(f"▶ {标题}")
    print(f"  SQL: {sql}")
    print("-" * 70)
    try:
        行 = 库.execute(sql).fetchall()
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")
        return None
    if 显示表头 and 行:
        列名 = [d[0] for d in 库.execute(sql).description]
        print("  " + " | ".join(str(c) for c in 列名))
        print("  " + "-" * 40)
        for r in 行:
            print("  " + " | ".join("<NULL>" if v is None else str(v) for v in r))
    print(f"  → {len(行)} 行")
    return 行


库 = sqlite3.connect(库路径)

# ─────────────────────────────────────────────────────────────
print("第 0 幕 · 两张表原样长什么样")
# ─────────────────────────────────────────────────────────────
打印("SELECT * FROM 新闻 ORDER BY 序号 ASC", "新闻表（15 行）")
打印("SELECT * FROM 星期对照 ORDER BY 编号 ASC", "星期对照表（5 行，故意只有工作日）")

# ─────────────────────────────────────────────────────────────
print()
print("第 1 幕 · 纵向筛（你 11-17/11-18 已经会的）")
# ─────────────────────────────────────────────────────────────
打印("SELECT 序号, 星期 FROM 新闻 WHERE 星期 = '星期一' ORDER BY 序号 ASC",
      "WHERE 纵向筛：只在一张表里挑行")

# ─────────────────────────────────────────────────────────────
print()
print("第 2 幕 · 横向拼：INNER JOIN vs LEFT JOIN")
# ─────────────────────────────────────────────────────────────
打印("SELECT 新闻.序号, 新闻.星期, 星期对照.类型 "
     "FROM 新闻 JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
     "ORDER BY 新闻.序号 ASC",
     "INNER JOIN：两边都对得上才输出")

打印("SELECT 新闻.序号, 新闻.星期, 星期对照.类型 "
     "FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
     "ORDER BY 新闻.序号 ASC",
     "LEFT JOIN：左边全保留，对不上的填 NULL")

内 = 库.execute("SELECT COUNT(*) FROM 新闻 JOIN 星期对照 ON 新闻.星期 = 星期对照.星期").fetchone()[0]
左 = 库.execute("SELECT COUNT(*) FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期").fetchone()[0]
漏 = [r[0] for r in 库.execute(
    "SELECT 新闻.序号 FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
    "WHERE 星期对照.编号 IS NULL ORDER BY 新闻.序号 ASC")]
print()
print("=" * 70)
print(f"▶ 行数账：INNER = {内} 行，LEFT = {左} 行，差 {左 - 内} 行")
print(f"  差掉的 {len(漏)} 行序号 = {漏}")
print("  原因：这 6 条全是休息日（星期六×4 + 星期日×2），对照表只录了 5 个工作日")
print("=" * 70)

# ─────────────────────────────────────────────────────────────
print()
print("第 3 幕 · 四个必踩的坑（每条都真跑给你看报错）")
# ─────────────────────────────────────────────────────────────
打印("SELECT 新闻.序号 FROM 新闻 JOIN 星期对照 ON 新闻.星期 = 星期对照.名称",
      "坑1 · ON 两边列名不一致 → no such column")

打印("SELECT 序号, 星期 FROM 新闻 JOIN 星期对照 ON 新闻.星期 = 星期对照.星期",
      "坑2 · SELECT 同名列不写表名 → ambiguous column name")

打印("SELECT 新闻.序号 FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
     "WHERE 星期对照.编号 = NULL",
      "坑3 · 用 = NULL → 一行都查不到（不报错，但结果是空）")

打印("SELECT 新闻.序号 FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
     "WHERE 星期对照.编号 IS NULL ORDER BY 新闻.序号 ASC",
      "坑3 · 用 IS NULL → 正确查出那 6 行")

打印("SELECT 新闻.序号 FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
     "WHERE 星期对照.类型 = '工作日' ORDER BY 新闻.序号 ASC",
      "坑4 · WHERE 写在 ON 后面 → NULL 行被筛掉，LEFT 白用了（只剩 9 行）")

打印("SELECT 新闻.序号 FROM 新闻 LEFT JOIN 星期对照 "
     "ON 新闻.星期 = 星期对照.星期 AND 星期对照.类型 = '工作日' "
     "ORDER BY 新闻.序号 ASC",
      "坑4 · 条件写进 ON → 15 行全在（对不上的仍是 NULL）")

# ─────────────────────────────────────────────────────────────
print()
print("第 4 幕 · JOIN + GROUP BY")
# ─────────────────────────────────────────────────────────────
打印("SELECT 星期对照.类型, COUNT(*) AS n "
     "FROM 新闻 JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
     "GROUP BY 星期对照.类型 "
     "ORDER BY n DESC, 星期对照.类型 ASC",
     "子句顺序：SELECT → FROM → JOIN → ON → GROUP BY → ORDER BY")

# ─────────────────────────────────────────────────────────────
print()
print("第 5 幕 · Python 侧写法（和 11-18 上午的 GROUP BY 练习只差两处）")
# ─────────────────────────────────────────────────────────────
cur = 库.cursor()
cur.execute("SELECT 新闻.序号, 星期对照.类型 FROM 新闻 "
            "JOIN 星期对照 ON 新闻.星期 = 星期对照.星期 "
            "ORDER BY 新闻.序号 ASC")
结果 = cur.fetchall()
print(f"  fetchall() 返回 {类型(结果).__name__}，长度 {len(结果)}")
print(f"  第 1 个元素是 {结果[0]}，类型 {type(结果[0]).__name__}  ← 两列就是 tuple，不用压平")
print(f"  前 3 行：{结果[:3]}")

库.close()
print()
print("=" * 70)
print("✅ 演示跑完。现在去填 11.18练习_JOIN连接表.py 里的 4 个 TODO")
print("=" * 70)
