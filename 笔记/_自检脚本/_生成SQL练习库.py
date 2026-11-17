# -*- coding: utf-8 -*-
"""
生成 SQL 练习用的 SQLite 库 + 算出 8 题期望值
- 数据源：练习/数据/news_多天版.csv（10 天真实新闻，15 行 4 列）
- 期望值全部由代码算，不手数
"""
import csv
import io
import sqlite3
from pathlib import Path

根 = Path(__file__).resolve().parents[2]
数据目录 = 根 / "练习" / "数据"
CSV路径 = 数据目录 / "news_多天版.csv"
库路径 = 数据目录 / "新闻库.sqlite"

原始 = CSV路径.read_bytes()
文本 = 原始.decode("utf-8-sig")
行 = list(csv.DictReader(io.StringIO(文本)))
print("源数据: %d 行, 列=%s" % (len(行), list(行[0].keys())))

# ── 建库（幂等：先删旧库）────────────────────────────────────
if 库路径.exists():
    库路径.unlink()
    print("已删除旧库:", 库路径)

con = sqlite3.connect(str(库路径))
cur = con.cursor()
cur.execute("""
CREATE TABLE 新闻 (
    序号   INTEGER PRIMARY KEY,
    日期   TEXT,
    新闻内容 TEXT,
    星期   TEXT
)
""")
cur.executemany(
    "INSERT INTO 新闻 (序号, 日期, 新闻内容, 星期) VALUES (?, ?, ?, ?)",
    [(int(r["序号"]), r["日期"], r["新闻内容"], r["星期"]) for r in 行],
)
con.commit()
print("建表完成，表=新闻，共 %d 行" % cur.execute("SELECT COUNT(*) FROM 新闻").fetchone()[0])
print("表结构:")
for r in cur.execute("PRAGMA table_info(新闻)"):
    print("   ", r)
con.close()

# ── 用 SQL 算期望值 ─────────────────────────────────────────
con = sqlite3.connect(str(库路径))
cur = con.cursor()


def q(sql, 参数=()):
    return cur.execute(sql, 参数).fetchall()


期望 = {}

# 1 查全部新闻标题（单列）
期望[1] = [r[0] for r in q("SELECT 新闻内容 FROM 新闻 ORDER BY 序号")]

# 2 星期二有几条 + 序号
期望[2] = (q("SELECT COUNT(*) FROM 新闻 WHERE 星期 = ?", ("星期二",))[0][0],
          [r[0] for r in q("SELECT 序号 FROM 新闻 WHERE 星期 = ? ORDER BY 序号", ("星期二",))])

# 3 多条件 AND：星期一 且 序号 > 5
期望[3] = [r[0] for r in q("SELECT 序号 FROM 新闻 WHERE 星期 = ? AND 序号 > ? ORDER BY 序号",
                        ("星期一", 5))]

# 4 关键词 OR：含 银行 或 含 雨雪
期望[4] = [r[0] for r in q(
    "SELECT 序号 FROM 新闻 WHERE 新闻内容 LIKE ? OR 新闻内容 LIKE ? ORDER BY 序号",
    ("%银行%", "%雨雪%"))]

# 5 NOT：不是星期六的，序号 <= 6
期望[5] = [r[0] for r in q("SELECT 序号 FROM 新闻 WHERE 星期 <> ? AND 序号 <= ? ORDER BY 序号",
                        ("星期六", 6))]

# 6 BETWEEN：序号在 3 到 8 之间（含两端）
期望[6] = [r[0] for r in q("SELECT 序号 FROM 新闻 WHERE 序号 BETWEEN ? AND ? ORDER BY 序号", (3, 8))]

# 7 IN：星期是 星期五 或 星期日
期望[7] = [r[0] for r in q("SELECT 序号 FROM 新闻 WHERE 星期 IN (?, ?) ORDER BY 序号",
                        ("星期五", "星期日"))]

# 8 统计：每个星期各有几条（GROUP BY）
期望[8] = dict(q("SELECT 星期, COUNT(*) FROM 新闻 GROUP BY 星期 ORDER BY 星期"))

con.close()

print()
print("=" * 70)
print("8 题期望值（由 SQL 算，不是手数）")
print("=" * 70)
for k in sorted(期望):
    v = 期望[k]
    s = repr(v)
    print("%d. %s" % (k, s[:150] + ("…" if len(s) > 150 else "")))

# ── 独立通道验证：用标准库 csv 重算，与 SQL 结果比对 ────────
print()
print("=" * 70)
print("独立验证：标准库 csv 重算 vs SQL 结果")
print("=" * 70)


def 序号(x):
    return int(x)


独立 = {}
独立[1] = [r["新闻内容"] for r in 行]
独立[2] = (len([r for r in 行 if r["星期"] == "星期二"]),
          [序号(r["序号"]) for r in 行 if r["星期"] == "星期二"])
独立[3] = [序号(r["序号"]) for r in 行 if r["星期"] == "星期一" and 序号(r["序号"]) > 5]
独立[4] = [序号(r["序号"]) for r in 行
         if "银行" in r["新闻内容"] or "雨雪" in r["新闻内容"]]
独立[5] = [序号(r["序号"]) for r in 行
         if r["星期"] != "星期六" and 序号(r["序号"]) <= 6]
独立[6] = [序号(r["序号"]) for r in 行 if 3 <= 序号(r["序号"]) <= 8]
独立[7] = [序号(r["序号"]) for r in 行 if r["星期"] in ("星期五", "星期日")]
独立[8] = {}
for r in 行:
    独立[8][r["星期"]] = 独立[8].get(r["星期"], 0) + 1

全对 = True
for k in sorted(期望):
    同 = (期望[k] == 独立[k])
    全对 &= 同
    print("  第%d题: %s" % (k, "一致 ✅" if 同 else "❌ SQL=%r 独立=%r" % (期望[k], 独立[k])))
print()
print("独立验证结论:", "8 题全部一致 ✅" if 全对 else "❌ 有不一致")
print("库路径:", 库路径, "(%.1f KB)" % (库路径.stat().st_size / 1024))
