# -*- coding: utf-8 -*-
"""生成 11-16 下午档用的多天新闻数据 + 实跑算出全部期望值

为什么要有这份数据：
    练习/数据/news_示例.csv 的「日期」列 15 行全是 2026-11-14、「星期」列全是「星期六」，
    拿它练筛选 → 筛什么都命中 15 行，等于没筛。所以另造一份「跨 10 天」的表：
    · 新闻标题全部沿用 api-demo 的真实新闻
    · 日期从 2026-11-14 起排开
    · 星期由 datetime 从日期【推导】（不手写，避免写错）
"""
import datetime
from pathlib import Path

import pandas as pd

根 = Path(__file__).resolve().parents[2]   # 脚本在 笔记/_自检脚本/ → 退两级到仓库根
数据目录 = 根 / "练习" / "数据"

原 = pd.read_csv(数据目录 / "news_示例.csv")
标题 = list(原["新闻内容"])

# 每天分几条：合计必须等于 15
分布 = [3, 1, 2, 2, 1, 1, 2, 1, 1, 1]  # 11-14 起共 10 天
assert sum(分布) == len(标题), "分布条数与标题数对不上"

行 = []
序号 = 0
起 = datetime.date(2026, 11, 14)
星期名 = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
for i, 条数 in enumerate(分布):
    日 = 起 + datetime.timedelta(days=i)
    for _ in range(条数):
        序号 += 1
        行.append({
            "序号": 序号,
            "日期": 日.isoformat(),
            "新闻内容": 标题[序号 - 1],
            "星期": 星期名[日.weekday()],   # 由日期推导
        })

df = pd.DataFrame(行)
输出 = 数据目录 / "news_多天版.csv"
df.to_csv(输出, index=False, encoding="utf-8-sig")
print("✅ 已生成:", 输出, df.shape)

# 读回来验证（模拟用户读）
df2 = pd.read_csv(输出)
print("回读 shape:", df2.shape)
print()
print(df2[["序号", "日期", "星期"]].to_string())
print()
print("=== 星期分布（期望值来源，全部由代码算）===")
for w in 星期名:
    print("  %s: %d 条" % (w, (df2["星期"] == w).sum()))
print()
print("=== 日期分布 ===")
for d, n in df2["日期"].value_counts().sort_index().items():
    print("  %s (%s): %d 条" % (d, df2.loc[df2["日期"] == d, "星期"].iloc[0], n))
print()
print("=== 关键词命中（用于 OR 筛选练习）===")
for kw in ["英伟达", "银行", "雨雪", "考研", "奔驰", "百草枯"]:
    print("  含 %-6s : %d 条" % (kw, df2["新闻内容"].str.contains(kw).sum()))
print()
print("=== 序号统计 ===")
print("  最大序号:", df2["序号"].max(), "| 最小序号:", df2["序号"].min(), "| 总数:", len(df2))
print("  含'考试'的行序号:", list(df2.loc[df2["新闻内容"].str.contains("考试"), "序号"]))
