# -*- coding: utf-8 -*-
"""11.18 练习：GROUP BY / COUNT + ORDER BY / LIMIT（对应日程 11-18 上午档「📌 SQL 实操②：GROUP BY/COUNT + ORDER BY/LIMIT 聚合统计 1h」）

════════════════════════════════════════════════════════════════════
这个文件分【五段】，顺序别搞乱：

  📘 【讲解区】只读 —— 今天三样东西的概念速览，只有这一处讲语法
  🅰️ 【任务区】只读 —— 7 个任务，标明要做什么、期望什么
  ✍️ 【作答区】—— 你写代码的地方（TODO 1-① …）
  ✅ 【自动检查】—— 跑完看这里，别改
  🔒 【参考答案】—— 放最后，做完再看

⭐ 作答区【故意不给 SQL 语句片段】：
   只在上面的讲解区讲过一次语法，答的时候要自己从讲解区「回忆」写法。
   这叫「提取练习」，比你直接抄一遍有效得多。

⭐⭐ 每个任务函数都有【返回值约定】：
   自动检查会【真的调用你写的函数】，拿它的 return 值跟期望比对。
   所以 —— 打印出来不算数，必须把结果 return 出来。

⭐ 今天和昨天最大的不同：
   昨天 SELECT 一列 → fetchall() 回来是 [('值',), ...]，要用 [行[0] for 行 in ...] 压平。
   今天 SELECT 两列（星期 + 条数）→ fetchall() 回来直接就是 [('星期一', 3), ...]
   —— 两列元组，正好是你要的形状，【不用压平】。

⭐ 数据从哪来：
   练习/数据/新闻库.sqlite（已建好，8 KB）
   里面一张表 `新闻`，15 行 4 列：序号 / 日期 / 新闻内容 / 星期
   （真实数据，来自你 api-demo 的新闻采集）

════════════════════════════════════════════════════════════════════
"""

import sqlite3
from pathlib import Path

# ── 数据库路径（用 pathlib，不要手写反斜杠字符串）────────────────────
数据目录 = Path(__file__).parent / "数据"
库路径 = 数据目录 / "新闻库.sqlite"

# ############################################################################
# 📘 【讲解区 · 只读】—— GROUP BY / ORDER BY / LIMIT 概念速览
# ############################################################################
print("=" * 68)
print("📘 讲解区 · GROUP BY / COUNT + ORDER BY / LIMIT")
print("=" * 68)
print("""
【这三种东西各自解决什么】

  GROUP BY   把行按某个列「分堆」，一堆算一个结果   pandas: df.groupby("星期")
  COUNT(*)   数「有几行」                        pandas: .size()
  ORDER BY   把结果「排序」                      pandas: df.sort_values(...)
  LIMIT      只取「前 N 行」                     pandas: df.head(N)

  ⭐ 关键区别：
      WHERE  筛的是【行】（单条新闻）
      GROUP BY 算的是【组】（一堆新闻）

【为什么必须有 GROUP BY】

  想回答「每个星期各有几条」，不用 GROUP BY 得写 7 遍：
      SELECT COUNT(*) FROM 新闻 WHERE 星期 = '星期一';
      SELECT COUNT(*) FROM 新闻 WHERE 星期 = '星期二';
      ...还要写 5 遍

  用 GROUP BY，一句：
      SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期;

【五步套路：跟昨天一模一样，一个字没改】

  con = sqlite3.connect(库路径)        # ① 连上
  cur = con.cursor()                   # ② 拿话筒
  cur.execute("SELECT ... GROUP BY ...")   # ③ 说 SQL（只改这句）
  结果 = cur.fetchall()                # ④ 收结果
  con.close()                          # ⑤ 关电话
  return 结果                          # ⚠️ 必须 return

【今天第 4 步的差别 ⚠️ 别踩】

  昨天 SELECT 一列 → fetchall() 回来 [('值',), ...] → 要用 [行[0] for 行 in ...] 压平
  今天 SELECT 两列 → fetchall() 回来 [('星期一', 3), ...] → 【不用压平】，直接就是你要的

  元组长度 = 你 SELECT 了几列。

【子句顺序（背下来，LIMIT 永远最后）】

  WHERE  →  GROUP BY  →  HAVING  →  ORDER BY  →  LIMIT
  筛行      分堆        筛组      排序        截断

【七个必记的写法】

  分组计数   SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期
  起别名     SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期
  排序       ... GROUP BY 星期 ORDER BY n DESC        （ASC 升序是默认值）
  截断       ... GROUP BY 星期 ORDER BY n DESC LIMIT 3
  先筛行     SELECT 星期, COUNT(*) FROM 新闻 WHERE 序号 <= 10 GROUP BY 星期
  筛组       ... GROUP BY 星期 HAVING COUNT(*) >= 2

【⭐ 坑 1 · ORDER BY 并列时顺序【不确定】】

  新闻库里有 3 个「2 条」的星期。ORDER BY n DESC 只说了「按条数降序」，
  没说「条数一样时按什么排」→ 那一档顺序由数据库自己定，换台机器可能就变了。

  ⭐ 解法：加次级排序键
        ORDER BY n DESC, 星期 ASC
     意思是「先按 n 降序，n 一样时再按星期升序」→ 顺序完全确定。

【⭐ 坑 2 · 中文排序不是「按星期几的顺序」】

  实测 ORDER BY 星期 ASC →
        星期一, 星期三, 星期二, 星期五, 星期六, 星期四, 星期日

  「星期三」排在「星期二」【前面】！因为数据库按【字符编码】排，
  「三」的编码比「二」大。要「真正的星期顺序」得自己指定排序依据。

【⭐ 坑 3 · WHERE 筛行、HAVING 筛组，位置不能换】

  找「条数 >= 2 的星期」→ 条件是关于【组】的 → 用 HAVING
  WHERE 写在 GROUP BY 【之前】；HAVING 写在 GROUP BY 【之后】

【两个坑跟昨天一脉相承】

  坑 A · LIMIT 必须在 ORDER BY 后面 —— 先排序才知道哪几行是「前 N 行」
  坑 B · 不写 ORDER BY，数据库不保证返回顺序（今天多了一层：写了也可能不够）

  📎 完整讲解见：笔记/讲义/11-18_讲义_GROUP_BY与ORDER_BY_LIMIT.md
""")
print("=" * 68)

# ############################################################################
# 🅰️ 【任务区 · 只读】—— 7 个任务
# ############################################################################
print("🅰️ 任务区：7 个任务，全部写在下面的 ✍️ 作答区")
print("   数据库：练习/数据/新闻库.sqlite，表 `新闻`（15 行 4 列）")
print()
print("   ⭐ 每个任务都是一个函数，都要【return】，不要只 print")
print("   ⭐ 今天的结果形状是 list[tuple]，两列元组，【不用压平】")
print()

# ── 任务清单（期望值由 SQL 实际跑出来，不是手数）──────────────────────
任务说明 = [
    ("任务1_每星期条数",
     "每个星期各有几条新闻，按【星期】从小到大排",
     "list[tuple]，7 行，形如 [('星期一', 3), ...]"),

    ("任务2_按条数降序",
     "每个星期各有几条，按【条数】从多到少排；条数一样时按星期从小到大",
     "list[tuple]，7 行，第一行是 ('星期六', 4)"),

    ("任务3_最多的前三名",
     "新闻最多的 3 个星期（条数多的在前，条数一样时星期小的在前）",
     "list[tuple]，3 行：('星期六', 4), ('星期一', 3), ('星期二', 2)"),

    ("任务4_先筛行再分堆",
     "只看序号 1 到 10 的新闻，每个星期各有几条，按星期从小到大",
     "list[tuple]，6 行，形如 [('星期一', 2), ...]"),

    ("任务5_最少的那天",
     "新闻最少的是星期几？条数一样时取星期小的那个",
     "list[tuple]，1 行，形如 [('星期三', 1)]"),

    ("任务6_筛出条数多的组",
     "只保留条数 >= 2 的星期，按条数从多到少，条数一样时星期小的在前",
     "list[tuple]，5 行：('星期六', 4), ('星期一', 3), ('星期二', 2), ('星期五', 2), ('星期日', 2)"),

    ("任务7_综合筛选",
     "只保留条数 >= 2 的星期，然后取其中条数最多的【一个】",
     "list[tuple]，1 行：('星期六', 4)"),
]

for 名, 描述, 期望 in 任务说明:
    print("  【%s】" % 名)
    print("     要做：%s" % 描述)
    print("     期望：%s" % 期望)
    print()

# ############################################################################
# ✍️ 【作答区】—— 你写代码的地方
# ############################################################################
print("✍️ 作答区：7 个 TODO，写完直接跑本文件看检查结果")
print()

# ── 每题的期望值（由 SQL 实际跑出来，并已用标准库 csv 独立重算核对一致）──
期望_1 = [
    ('星期一', 3),
    ('星期三', 1),
    ('星期二', 2),
    ('星期五', 2),
    ('星期六', 4),
    ('星期四', 1),
    ('星期日', 2),
]
期望_2 = [
    ('星期六', 4),
    ('星期一', 3),
    ('星期二', 2),
    ('星期五', 2),
    ('星期日', 2),
    ('星期三', 1),
    ('星期四', 1),
]
期望_3 = [
    ('星期六', 4),
    ('星期一', 3),
    ('星期二', 2),
]
期望_4 = [
    ('星期一', 2),
    ('星期三', 1),
    ('星期二', 2),
    ('星期六', 3),
    ('星期四', 1),
    ('星期日', 1),
]
期望_5 = [
    ('星期三', 1),
]
期望_6 = [
    ('星期六', 4),
    ('星期一', 3),
    ('星期二', 2),
    ('星期五', 2),
    ('星期日', 2),
]
期望_7 = [
    ('星期六', 4),
]


def 任务1_每星期条数():
    """返回 list[tuple]：每个星期各有几条，按星期升序。"""
    # TODO 1-① 在下面写你的代码
    # ── 这题在问什么 ─────────────────────────────
    # 「15 条新闻，每个星期各有几条？」
    # 不用 GROUP BY 得写 7 遍「COUNT(*) + WHERE 星期=X」；用 GROUP BY 一句就分好堆。
    con = sqlite3.connect(库路径)  # ① 连上数据库（Path 对象直接传，不用手写反斜杠）
    cur = con.cursor()  # ② 拿一支「话筒」——游标，后面所有 SQL 都通过它发出去
    # ③ 说 SQL —— 这句拆成 4 块看：
    #    SELECT 星期, COUNT(*)  取「星期」列 + 数出每堆有几行（COUNT(*) 数的是行数）
    #    FROM 新闻             数据来自哪张表
    #    GROUP BY 星期        按星期分堆，一堆算一个结果
    #    ORDER BY 星期 ASC    结果按星期升序排（⚠️ 按【字符编码】排，不是「星期几」的顺序）
    cur.execute("SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期 ORDER BY 星期 ASC")
    # ④ 收结果 —— 今天 SELECT 两列，fetchall() 回来直接就是 [('星期一', 3), ...]
    #    两列元组正好是要求的形状，【不用像昨天那样压平】
    结果 = cur.fetchall()
    con.close()  # ⑤ 关电话（不关也能跑，但会占着文件句，习惯性关掉）
    return 结果  # ⚠️ 必须 return —— 自动检查只看返回值，不 return 一律判错


def 任务2_按条数降序():
    """返回 list[tuple]：每星期条数，按条数降序 + 星期升序。"""
    # TODO 2-① 在下面写你的代码
    # ── 这题在问什么 ─────────────────────────────
    # 「哪个星期新闻最多」→ 按条数从多到少排。
    # ⚠️ 本题两个关键点：
    #   1) COUNT(*) AS n —— 给聚合列起别名 n，否则 ORDER BY 里没法引用它
    #   2) ORDER BY n DESC, 星期 ASC —— 【次级排序键】，这题真正的考点
    #      数据库里有 3 个「2 条」的星期（星期二 / 星期五 / 星期日）并列，
    #      只写 ORDER BY n DESC，这一档谁在前是【不确定】的（换机器/换版本可能就变了）；
    #      加了 ", 星期 ASC" 才完全确定 —— 意思是「先按 n 降序，n 一样时再按星期升序」。
    con = sqlite3.connect(库路径)  # ① 连上
    cur = con.cursor()  # ② 拿话筒
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n DESC, 星期 ASC")
    #    SELECT 星期, COUNT(*) AS n   取星期列 + 计数并起名 n
    #    GROUP BY 星期                按星期分堆
    #    ORDER BY n DESC, 星期 ASC    主键 n 降序；并列时用星期升序兜底
    结果 = cur.fetchall()  # ④ 收结果（两列元组，不用压平）
    con.close()  # ⑤ 关电话
    return 结果  # ⚠️ 必须 return


def 任务3_最多的前三名():
    """返回 list[tuple]：条数最多的 3 个星期。"""
    # TODO 3-① 在下面写你的代码
    # ── 这题在问什么 ─────────────────────────────
    # 「新闻最多的 3 个星期是哪三个」→ 第2题原封不动，再加一句 LIMIT 3。
    # ⭐ 子句顺序是死的：WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
    #    LIMIT 永远在最后 —— 不先排序，数据库不知道哪几行算「前 3 名」。
    con = sqlite3.connect(库路径)  # ① 连上
    cur = con.cursor()  # ② 拿话筒
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n DESC, 星期 ASC LIMIT 3")
    #    ... ORDER BY n DESC, 星期 ASC  先定好顺序
    #    LIMIT 3                      再截断，只留前 3 行
    结果 = cur.fetchall()  # ④ 收结果（3 行，两列元组）
    con.close()  # ⑤ 关电话
    return 结果  # ⚠️ 必须 return


def 任务4_先筛行再分堆():
    """返回 list[tuple]：序号 <= 10 的新闻，按星期分组计数。"""
    # TODO 4-① 在下面写你的代码
    # ── 这题在问什么 ─────────────────────────────
    # 「只看序号 1~10 的新闻，每个星期各有几条」→ 筛行 + 分堆，一个组合。
    # ⭐ 顺序不能反：先 WHERE 筛掉不要的行，再 GROUP BY 分堆。
    #    （写反了 SQL 直接报错，因为分堆之后没有「行」可以筛了。）
    # ⭐ 参数化：WHERE 后面用 ? 占位，值通过第二个参数传进去（这里传 (10,)）。
    #    注意 (10,) 末尾的逗号 —— 单元素元组的标志，写成 (10) 就不是元组了。
    con = sqlite3.connect(库路径)  # ① 连上
    cur = con.cursor()  # ② 拿话筒
    cur.execute("SELECT 星期, COUNT(*) FROM 新闻 WHERE 序号 <= ? GROUP BY 星期 ORDER BY 星期 ASC", (10,))
    #    WHERE 序号 <= ?      先筛行：只留序号 1~10（? 的值 = 10）
    #    GROUP BY 星期       再分堆
    #    ORDER BY 星期 ASC   按星期升序
    结果 = cur.fetchall()  # ④ 收结果（6 行：10 行新闻只落在 6 个星期里）
    con.close()  # ⑤ 关电话
    return 结果  # ⚠️ 必须 return


def 任务5_最少的那天():
    """返回 list[tuple]：新闻最少的星期（1 行）。"""
    # TODO 5-① 在下面写你的代码
    # ── 这题在问什么 ─────────────────────────────
    # 「新闻最少的是星期几」→ 把第2题的 DESC 改成 ASC（升序 = 从少到多），再 LIMIT 1 取头一个。
    # ⭐ 还是要留 ", 星期 ASC"：并列最少时（比如有 2 个星期都只有 1 条），
    #    取哪个才确定 —— 靠次级键定死，别让数据库自己挑。
    con = sqlite3.connect(库路径)  # ① 连上
    cur = con.cursor()  # ② 拿话筒
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n ASC, 星期 ASC LIMIT 1")
    #    ORDER BY n ASC      条数【升序】→ 最少的排第一
    #    , 星期 ASC         并列时按星期升序兜底
    #    LIMIT 1            只取第 1 行 → 唯一答案
    结果 = cur.fetchall()  # ④ 收结果（1 行，形如 [('星期三', 1)]）
    con.close()  # ⑤ 关电话
    return 结果  # ⚠️ 必须 return


def 任务6_筛出条数多的组():
    """返回 list[tuple]：条数 >= 2 的星期。"""
    # TODO 6-① 在下面写你的代码
    # ── 这题在问什么 ─────────────────────────────
    # 「只保留条数 >= 2 的星期」→ 第一次用 HAVING。
    # ⭐⭐ WHERE 和 HAVING 的分工（本题核心）：
    #    WHERE   筛【行】—— 单条新闻层面的条件，写在 GROUP BY 之前
    #    HAVING  筛【组】—— 一堆新闻算完之后的条件，写在 GROUP BY 之后
    #    这里要筛的是「条数」，条数是组算出来的 → 只能用 HAVING，写 WHERE 会报错。
    # ⭐ 参数化：(2,) 末尾逗号别丢。条件写在 HAVING 后面，位置不能和 WHERE 换。
    con = sqlite3.connect(库路径)  # ① 连上
    cur = con.cursor()  # ② 拿话筒
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 HAVING COUNT(*) >= ? ORDER BY n DESC, 星期 ASC",
                (2,))
    #    GROUP BY 星期               先分堆
    #    HAVING COUNT(*) >= ?       再筛掉条数不够的组（? 的值 = 2）
    #    ORDER BY n DESC, 星期 ASC  剩下的按条数降序排
    结果 = cur.fetchall()  # ④ 收结果（5 行）
    con.close()  # ⑤ 关电话
    return 结果  # ⚠️ 必须 return


def 任务7_综合筛选():
    """返回 list[tuple]：条数 >= 2 的星期里条数最多的那一个。"""
    # TODO 7-① 在下面写你的代码
    # ── 这题在问什么 ─────────────────────────────
    # 「条数 >= 2 的星期里，条数最多的那一个」→ 第6题 + LIMIT 1。
    # ⭐ 逻辑顺序：先 HAVING 剔掉不合格的组，再在【剩下的】里面排序取第一。
    #    LIMIT 1 放在最后 —— 它截的是「排好序之后的第 1 行」，
    #    写在 HAVING 前面就会变成「先截断再筛」，答案就错了。
    con = sqlite3.connect(库路径)  # ① 连上
    cur = con.cursor()  # ② 拿话筒
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 HAVING COUNT(*) >= ? ORDER BY n DESC, 星期 ASC LIMIT 1",
                (2,))
    #    GROUP BY 星期               分堆
    #    HAVING COUNT(*) >= ?       筛掉条数 < 2 的组
    #    ORDER BY n DESC, 星期 ASC  合格的组按条数降序
    #    LIMIT 1                    取排第一的那个
    结果 = cur.fetchall()  # ④ 收结果（1 行：('星期六', 4)）
    con.close()  # ⑤ 关电话
    return 结果  # ⚠️ 必须 return


# ############################################################################
# ✅ 【自动检查】—— 真的调用你写的函数，拿 return 值比对
# ############################################################################
print()
print("=" * 68)
print("✅ 自动检查")
print("=" * 68)

通过数 = 0
失败数 = 0


def 记一条(题号, 过了, 说明):
    """记一条检查结果：通过了打勾，没过打叉，并把说明打印出来。"""
    global 通过数, 失败数
    if 过了:
        通过数 += 1
        print("  ✅ 第%s题  %s" % (题号, 说明))
    else:
        失败数 += 1
        print("  ❌ 第%s题  %s" % (题号, 说明))


def 取返回值(函数):
    """调用用户写的函数，拿到返回值。

    关键：必须真的【调用】它，不能自己算答案（那样你 TODO 一行不写也全绿）。
    """
    try:
        结果 = 函数()
    except Exception as e:
        return ("异常", "%s: %s" % (type(e).__name__, e))
    if 结果 is None:
        return ("没有return", "函数没有 return，检查区读不到结果")
    return ("有", 结果)


def 判定_元组列表(实际, 期望):
    """比对 list[tuple]：长度一致，且每个元组的第 0、1 个元素都对得上。"""
    if 实际[0] != "有":
        return False
    值 = 实际[1]
    if not isinstance(值, (list, tuple)):
        return False
    if len(值) != len(期望):
        return False
    for 实际项, 期望项 in zip(值, 期望):
        if isinstance(实际项, (list, tuple)):
            if tuple(实际项) != tuple(期望项):
                return False
        else:
            if 实际项 != 期望项:
                return False
    return True


def 描述(实际):
    """把实际结果缩成一行短文字，给检查结果用。"""
    if 实际[0] != "有":
        return 实际[1]
    值 = 实际[1]
    try:
        return "%d 行 | %s" % (len(值), str(值)[:70])
    except Exception:
        return str(值)[:70]


# 第1题
记一条("1", 判定_元组列表(取返回值(任务1_每星期条数), 期望_1),
       "每星期条数 —— %s" % 描述(取返回值(任务1_每星期条数)))

# 第2题
记一条("2", 判定_元组列表(取返回值(任务2_按条数降序), 期望_2),
       "按条数降序 —— %s" % 描述(取返回值(任务2_按条数降序)))

# 第3题
记一条("3", 判定_元组列表(取返回值(任务3_最多的前三名), 期望_3),
       "最多的前三名 —— %s" % 描述(取返回值(任务3_最多的前三名)))

# 第4题
记一条("4", 判定_元组列表(取返回值(任务4_先筛行再分堆), 期望_4),
       "先筛行再分堆 —— %s" % 描述(取返回值(任务4_先筛行再分堆)))

# 第5题
记一条("5", 判定_元组列表(取返回值(任务5_最少的那天), 期望_5),
       "最少的那天 —— %s" % 描述(取返回值(任务5_最少的那天)))

# 第6题
记一条("6", 判定_元组列表(取返回值(任务6_筛出条数多的组), 期望_6),
       "筛出条数多的组 —— %s" % 描述(取返回值(任务6_筛出条数多的组)))

# 第7题
记一条("7", 判定_元组列表(取返回值(任务7_综合筛选), 期望_7),
       "综合筛选 —— %s" % 描述(取返回值(任务7_综合筛选)))

print()
if 失败数 == 0:
    print("🎉 7 题全过")
else:
    print("还有 %d 题没过 —— 看上面每条后面写的提示" % 失败数)

# ############################################################################
# 🔒 【参考答案】—— 做完再看
# ############################################################################
print()
print("=" * 68)
print("🔒 参考答案（自己做完了再看）")
print("=" * 68)
print('''
def 任务1_每星期条数():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期 ORDER BY 星期 ASC")
    结果 = cur.fetchall()
    con.close()
    return 结果


def 任务2_按条数降序():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n DESC, 星期 ASC")
    结果 = cur.fetchall()
    con.close()
    return 结果


def 任务3_最多的前三名():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n DESC, 星期 ASC LIMIT 3")
    结果 = cur.fetchall()
    con.close()
    return 结果


def 任务4_先筛行再分堆():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 星期, COUNT(*) FROM 新闻 WHERE 序号 <= ? GROUP BY 星期 ORDER BY 星期 ASC", (10,))
    结果 = cur.fetchall()
    con.close()
    return 结果


def 任务5_最少的那天():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 ORDER BY n ASC, 星期 ASC LIMIT 1")
    结果 = cur.fetchall()
    con.close()
    return 结果


def 任务6_筛出条数多的组():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 HAVING COUNT(*) >= ? ORDER BY n DESC, 星期 ASC",
                (2,))
    结果 = cur.fetchall()
    con.close()
    return 结果


def 任务7_综合筛选():
    con = sqlite3.connect(库路径)
    cur = con.cursor()
    cur.execute("SELECT 星期, COUNT(*) AS n FROM 新闻 GROUP BY 星期 HAVING COUNT(*) >= ? ORDER BY n DESC, 星期 ASC LIMIT 1",
                (2,))
    结果 = cur.fetchall()
    con.close()
    return 结果
''')

print()
print("⭐ 今天三个坑的正解，用在上面代码里：")
print("  坑1 ORDER BY 并列顺序不定 →  加次级排序键：ORDER BY n DESC, 星期 ASC")
print("  坑2 中文按编码排序        →  别指望按星期几排；要语义顺序自己指定依据")
print("  坑3 WHERE 筛行/HAVING 筛组 →  WHERE 在 GROUP BY 前，HAVING 在 GROUP BY 后")
print()
print("  另记：LIMIT 必须在 ORDER BY 后面；SELECT 两列时 fetchall() 不用压平。")
