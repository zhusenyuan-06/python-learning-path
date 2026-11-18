# -*- coding: utf-8 -*-
"""11.18 练习 · SQL JOIN 连接表（6 题）

════════════════════════════════════════════════════════════════════
今天上午你学会了 GROUP BY（把一张表纵向分堆），
这一题是它的自然延伸：JOIN（把两张表横向拼起来）。

库里有什么：
    表 新闻      —— 15 行，列：序号 / 日期 / 新闻内容 / 星期
    表 星期对照  —— 5 行，列：星期 / 编号 / 类型
                    ⚠️ 只录了【工作日】5 个，休息日故意没录！
                       这是本题的命门所在

两张表的共同键：都是「星期」这一列。
════════════════════════════════════════════════════════════════════

⭐ 你要填的地方有 4 个（标了 ★TODO）：
    1) 建对照表     —— CREATE TABLE + INSERT
    2) 内连接       —— JOIN ... ON ...
    3) 左连接       —— LEFT JOIN ... ON ...
    4) 连接后分组   —— JOIN + GROUP BY 一起用

⭐⭐ 关键概念（先看懂，再写代码）：
    INNER JOIN（也叫 JOIN）→ 两边【都】对得上才输出，对不上的行直接丢
    LEFT JOIN              → 左边【全部保留】，右边对不上就填 NULL

⭐⭐⭐ 三个必踩的坑：
    坑1  ON 条件两边的列名必须一致：都是「星期」，不能一个写星期一个写名称
    坑2  SELECT 里两张表的列同名会打架 → 必须写「表名.列名」
    坑3  LEFT JOIN 的 WHERE 写在 ON 后面会把 NULL 行又筛掉（先 ON 再 WHERE 的顺序）
"""

import sqlite3

# ═════════════════════════════════════════════════════════════════════
# 路径配置
# ═════════════════════════════════════════════════════════════════════
import os

库路径 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "数据", "JOIN练习库.sqlite")


# ═════════════════════════════════════════════════════════════════════
# ★TODO 1 —— 建「星期对照」表并灌数据
# ═════════════════════════════════════════════════════════════════════
def 建星期对照表(库):
    """在库里建「星期对照」表，并灌入 5 个工作日的数据。

    ⚠️ 真实数据长这样（照抄，别自己编）：
        星期一 | 1 | 工作日
        星期二 | 2 | 工作日
        星期三 | 3 | 工作日
        星期四 | 4 | 工作日
        星期五 | 5 | 工作日

    💡 提示（你昨天已经会了）：
        cur = 库.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS 星期对照 ('
                    '星期 TEXT PRIMARY KEY, 编号 INTEGER, 类型 TEXT)')
        cur.executemany('INSERT OR REPLACE INTO 星期对照 VALUES (?, ?, ?)', [...])
        库.commit()

    ⚠️⚠️ 血泪坑（我写这个文件时真踩了）：
        docstring 里【绝对不能】再出现三个引号！
        我原来在提示里写了 cur.execute 后面跟三个引号的写法，
        结果那对三引号被 Python 当成了【文档字符串的结束标记】，
        后面的 SQL 片段全被当成普通代码解析 → IndentationError。
        记住：docstring 里要举三引号的例子，用单引号代替。
    """
    raise NotImplementedError("TODO 1：还没写")


# ═════════════════════════════════════════════════════════════════════
# ★TODO 2 —— 内连接
# ═════════════════════════════════════════════════════════════════════
def 内连接取序号与类型(库):
    """内连接新闻表和星期对照表，返回 [(序号, 类型), ...]，按序号升序。

    只输出【两边都对得上】的行 —— 休息日的新闻对不上，会被丢掉。

    期望：9 行（工作日新闻）

    💡 提示：
        SELECT 新闻.序号, 星期对照.类型
        FROM 新闻
        JOIN 星期对照 ON 新闻.星期 = 星期对照.星期
        ORDER BY 新闻.序号 ASC

    ⚠️ 坑1：ON 两边都写「星期」，列名必须一致
    ⚠️ 坑2：SELECT 里「序号」两张表都有，必须写「表名.列名」
    """
    raise NotImplementedError("TODO 2：还没写")


# ═════════════════════════════════════════════════════════════════════
# ★TODO 3 —— 左连接
# ═════════════════════════════════════════════════════════════════════
def 左连接取全部序号(库):
    """左连接，返回 [(序号, 类型), ...]，按序号升序。

    新闻表 15 行【一行都不能丢】，休息日的「类型」是 None（SQL 里的 NULL）。

    期望：15 行，其中 6 行的类型是 None

    💡 提示：
        把上一题的 JOIN 换成 LEFT JOIN，其他基本不变

    ⚠️ 注意：题目要求【只取前 8 行】来看效果，其余不查也行，
            但函数返回的必须是完整 15 行（别被题目里的「前8行」带偏）
    """
    raise NotImplementedError("TODO 3：还没写")


# ═════════════════════════════════════════════════════════════════════
# ★TODO 4 —— 连接 + 分组（JOIN 和 GROUP BY 一起用）
# ═════════════════════════════════════════════════════════════════════
def 连接后按类型分组统计(库):
    """内连接后按「类型」分组统计条数，返回 [(类型, 条数), ...]。

    ⚠️ 这题考的是【JOIN + GROUP BY 组合】——两个一起用，顺序是死的：

        SELECT ... FROM 表1 JOIN 表2 ON ... WHERE ... GROUP BY ... ORDER BY ...

    期望：[(('工作日', 9),)]  ← 只有一种类型，所以只有一组

    💡 提示：
        SELECT 星期对照.类型, COUNT(*) AS n
        FROM 新闻 JOIN 星期对照 ON 新闻.星期 = 星期对照.星期
        GROUP BY 星期对照.类型
        ORDER BY n DESC, 星期对照.类型 ASC
    """
    raise NotImplementedError("TODO 4：还没写")


# ═════════════════════════════════════════════════════════════════════
# 以下是【自动检查区】，你填完上面 4 个 TODO 就能直接跑
# ═════════════════════════════════════════════════════════════════════

def 题目1():
    """建表并灌数据（幂等：重复跑不会报错、不会重复灌）。"""
    库 = sqlite3.connect(库路径)
    try:
        建星期对照表(库)
        行 = 库.execute("SELECT COUNT(*) FROM 星期对照").fetchone()[0]
        print(f"   对照表已建，{行} 行")
        return 行
    finally:
        库.close()


def 题目2():
    """内连接：应得 9 行，全部是「工作日」。"""
    库 = sqlite3.connect(库路径)
    try:
        结果 = 内连接取序号与类型(库)
        print(f"   内连接返回 {len(结果)} 行")
        print(f"   前 3 行：{结果[:3]}")
        期望行数 = 9
        if len(结果) != 期望行数:
            print(f"❌ 行数不对：期望 {期望行数}，实际 {len(结果)}")
            print("   💡 提示：INNER JOIN 会丢掉对不上的行（休息日新闻）")
            return False
        if any(类型 != "工作日" for _, 类型 in 结果):
            print("❌ 有类型不是「工作日」的行")
            return False
        print("✅ 第2题  内连接 9 行全为工作日")
        return True
    finally:
        库.close()


def 题目3():
    """左连接：应得 15 行，其中 6 行类型为 None。"""
    库 = sqlite3.connect(库路径)
    try:
        结果 = 左连接取全部序号(库)
        print(f"   左连接返回 {len(结果)} 行")
        空数 = sum(1 for _, 类型 in 结果 if 类型 is None)
        print(f"   其中类型为 None 的有 {空数} 行")
        期望行数 = 15
        期望空数 = 6
        if len(结果) != 期望行数:
            print(f"❌ 行数不对：期望 {期望行数}（一行都不能丢），实际 {len(结果)}")
            print("   💡 提示：LEFT JOIN 左边全保留；写成 JOIN 就只剩 9 行了")
            return False
        if 空数 != 期望空数:
            print(f"❌ None 行数不对：期望 {期望空数}，实际 {空数}")
            return False
        print("✅ 第3题  左连接 15 行、6 行 None")
        return True
    finally:
        库.close()


def 题目4():
    """连接 + 分组：应得 [('工作日', 9)]。"""
    库 = sqlite3.connect(库路径)
    try:
        结果 = 连接后按类型分组统计(库)
        print(f"   分组结果：{结果}")
        期望 = [("工作日", 9)]
        if 结果 != 期望:
            print(f"❌ 不对：期望 {期望}，实际 {结果}")
            return False
        print("✅ 第4题  JOIN + GROUP BY 分组统计")
        return True
    finally:
        库.close()


def 题目5():
    """左连接中「没匹配上」的新闻序号 —— 考 IS NULL 的用法。"""
    库 = sqlite3.connect(库路径)
    try:
        cur = 库.cursor()
        cur.execute("""
            SELECT 新闻.序号
            FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期
            WHERE 星期对照.编号 IS NULL
            ORDER BY 新闻.序号 ASC
        """)
        结果 = [r[0] for r in cur.fetchall()]
        print(f"   没匹配上的序号：{结果}")
        期望 = [1, 2, 3, 4, 13, 14]
        if 结果 != 期望:
            print(f"❌ 不对：期望 {期望}，实际 {结果}")
            print("   💡 提示：NULL 不能用 = 比较，只能用 IS NULL 判断")
            return False
        print("✅ 第5题  IS NULL 找出没匹配上的 6 条")
        return True
    finally:
        库.close()


def 题目6():
    """对比：INNER 9 行 vs LEFT 15 行 —— JOIN 的核心行为。"""
    库 = sqlite3.connect(库路径)
    try:
        cur = 库.cursor()
        cur.execute("SELECT COUNT(*) FROM 新闻 JOIN 星期对照 ON 新闻.星期 = 星期对照.星期")
        内 = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM 新闻 LEFT JOIN 星期对照 ON 新闻.星期 = 星期对照.星期")
        左 = cur.fetchone()[0]
        print(f"   INNER={内} 行，LEFT={左} 行，差 {左 - 内} 行")
        if (内, 左) != (9, 15):
            print(f"❌ 不对：期望 INNER=9 / LEFT=15，实际 {内}/{左}")
            return False
        print("✅ 第6题  INNER 丢 6 行、LEFT 全保留")
        return True
    finally:
        库.close()


def main():
    print("=" * 64)
    print("🔗 SQL JOIN 连接表（6 题）")
    print("=" * 64)

    库 = sqlite3.connect(库路径)
    try:
        新闻行数 = 库.execute("SELECT COUNT(*) FROM 新闻").fetchone()[0]
    finally:
        库.close()
    print(f"📦 新闻表 {新闻行数} 行；对照表将由你建（5 个工作日）\n")

    检查项 = [
        ("第1题  建表灌数", 题目1),
        ("第2题  内连接 9 行", 题目2),
        ("第3题  左连接 15 行", 题目3),
        ("第4题  JOIN+GROUP BY", 题目4),
        ("第5题  IS NULL 找漏配", 题目5),
        ("第6题  INNER vs LEFT 对比", 题目6),
    ]

    通过 = 0
    失败 = []
    for 名字, 函数 in 检查项:
        print(f"▶ {名字}")
        try:
            if 函数():
                通过 += 1
        except NotImplementedError as e:
            print(f"⏳ 还没做：{e}")
            失败.append(名字)
        except Exception as e:
            print(f"❌ 报错：{type(e).__name__}: {e}")
            失败.append(名字)
        print()

    print("=" * 64)
    if not 失败:
        print(f"🎉 {len(检查项)} 题全过！")
    else:
        print(f"还有 {len(失败)} 题没过：{'、'.join(失败)}")
    print("=" * 64)


if __name__ == "__main__":
    main()
