# -*- coding: utf-8 -*-
"""
参考样例：pandas 读与查看（讲义 11-16 的配套可跑文件）
讲义里每一段输出都能用这个文件复现。
直接运行本文件即可看到全部输出。
"""
from pathlib import Path

import pandas as pd

数据目录 = Path(__file__).parent / "数据"
CSV路径 = 数据目录 / "news_示例.csv"
EXCEL路径 = 数据目录 / "news_示例.xlsx"

print("=" * 68)
print("【一】读文件")
print("=" * 68)
df = pd.read_csv(CSV路径)
print("df = pd.read_csv(CSV路径)")
print("  type(df) =", type(df).__name__)
print("  shape    =", df.shape)
print()

df2 = pd.read_excel(EXCEL路径)
print("df2 = pd.read_excel(EXCEL路径)")
print("  type(df2) =", type(df2).__name__)
print("  shape     =", df2.shape)
print()

print("=" * 68)
print("【二】看形状和列名")
print("=" * 68)
print("df.shape   =", df.shape)
print("df.columns =", list(df.columns))
print("len(df.columns) =", len(df.columns))
print()

print("=" * 68)
print("【三】head / tail —— 是【数据行】，不是表头")
print("=" * 68)
print("df.head(3) 的 shape =", df.head(3).shape)
print(df.head(3).to_string())
print()
print("df.tail(2):")
print(df.tail(2).to_string())
print()

print("=" * 68)
print("【四】选一列 / 选多列")
print("=" * 68)
一列 = df["星期"]
print("df['星期'] 的 type =", type(一列).__name__, "| shape =", 一列.shape)
print("  前 5 个值:", list(一列)[:5])
print()
多列 = df[["日期", "星期"]]
print("df[['日期','星期']] 的 type =", type(多列).__name__, "| shape =", 多列.shape)
print("  ⚠️ 多列必须用【方括号套方括号】，单列用【单层方括号】")
print()

print("=" * 68)
print("【五】dtypes / info")
print("=" * 68)
print("df.dtypes:")
print(df.dtypes.to_string())
print()
print("dict(df.dtypes) =", dict(df.dtypes))
print("  值[序号] 的类型 =", type(dict(df.dtypes)["序号"]))
print("  ⚠️ dtype 对象比较时能当字符串用，但 json.dumps 存不进去")
print("dict(df.dtypes.astype(str)) =", dict(df.dtypes.astype(str)))
print()
print("df.info():")
df.info()
print()
print("空值总数 df.isna().sum().sum() =", df.isna().sum().sum())
print("  第一次 sum() = 沿【列】求和 → 每列各有几个缺失（得到 Series）")
print("  第二次 sum() = 把这几个数加成 1 个总数（得到 int）")
print()

print("=" * 68)
print("【六】筛选（pandas 里的 WHERE）")
print("=" * 68)
多天 = pd.read_csv(数据目录 / "news_多天版.csv")
print("多天.shape =", 多天.shape)
print()

单条件 = 多天[多天["星期"] == "星期二"]
print("多天[多天['星期'] == '星期二']")
print("  shape =", 单条件.shape, "| 序号 =", list(单条件["序号"]))
print()

多条件 = 多天[(多天["星期"] == "星期一") & (多天["序号"] > 5)]
print("多天[(多天['星期'] == '星期一') & (多天['序号'] > 5)]")
print("  ⚠️ pandas 用 & | ，不是 Python 的 and or")
print("  shape =", 多条件.shape, "| 序号 =", list(多条件["序号"]))
print()

关键词 = 多天[多天["新闻内容"].str.contains("银行") | 多天["新闻内容"].str.contains("雨雪")]
print("多天[多天['新闻内容'].str.contains('银行') | ...contains('雨雪')]")
print("  shape =", 关键词.shape, "| 序号 =", list(关键词["序号"]))
print()

字面量 = 多天[多天["新闻内容"].str.contains("1.")]
字面量2 = 多天[多天["新闻内容"].str.contains("1.", regex=False)]
print("⚠️ str.contains 默认是【正则】：")
print("   contains('1.')            →", len(字面量), "行  ← '.' 在正则里 = 任意一个字符")
print("   contains('1.', regex=False) →", len(字面量2), "行  ← 真·字面量")
print()

print("=" * 68)
print("【七】增删改列")
print("=" * 68)
加数值列 = 多天.copy()
加数值列["双倍序号"] = 加数值列["序号"] * 2
print("加数值列['双倍序号'] = 加数值列['序号'] * 2")
print("  前 3 个:", list(加数值列["双倍序号"])[:3])
print()

加字符串列 = 多天.copy()
加字符串列["标签"] = 加字符串列["星期"] + "-" + 加字符串列["序号"].astype(str)
print("加字符串列['标签'] = 加字符串列['星期'] + '-' + 加字符串列['序号'].astype(str)")
print("  ⚠️ 数字列和字符串列不能直接相加，要先 .astype(str)")
print("  前 3 个:", list(加字符串列["标签"])[:3])
print()

删列 = 多天.drop(columns=["新闻内容"])
print("删列 = 多天.drop(columns=['新闻内容'])")
print("  columns =", list(删列.columns))
print()

改名列 = 多天.rename(columns={"序号": "编号"})
print("改名列 = 多天.rename(columns={'序号': '编号'})")
print("  columns =", list(改名列.columns))
print()

print("=" * 68)
print("【八】⚠️ 三个会静默出错的写法")
print("=" * 68)
哑弹 = 多天.copy()
哑弹.sort_values(by="序号", ascending=False)
print("1) sort_values 不接返回值 = 哑弹")
print("   不接 → 前 3 个序号:", list(哑弹["序号"])[:3], "（顺序没变，等于没写）")
接住 = 多天.sort_values(by="序号", ascending=False)
print("   接住 → 前 3 个序号:", list(接住["序号"])[:3], "（倒序生效）")
print()

print("2) list(df) 给的是【列名】，不是数据")
print("   list(df)         =", list(多天))
print("   list(df.head(0)) =", list(多天.head(0)), "← 完全一样，head(0) 多余")
print("   list(df.columns) =", list(多天.columns), "← 标准写法")
print()

print("3) 全局 df 会被别的函数污染")
全局df = pd.read_csv(数据目录 / "news_多天版.csv")


def A_全局加列():
    全局df["污染列"] = 1
    return len(全局df.columns)


def B_另一个函数():
    df = 全局df
    return len(df.columns)


print("   调用 A_全局加列() 前，B 看到的列数 =", B_另一个函数())
A_全局加列()
print("   调用 A_全局加列() 后，B 看到的列数 =", B_另一个函数(), "← 被污染了")
print("   → 每个函数自己 read_csv，别用全局的")
print()

print("=" * 68)
print("【九】四个常见报错的真实原因")
print("=" * 68)
try:
    未定义变量 = 多天["不存在的列"]
except KeyError as e:
    print("① df['不存在的列'] →", type(e).__name__, ":", e)
try:
    错条件 = 多天[多天["序号"] > 5 and 多天["星期"] == "星期一"]
except ValueError as e:
    print("② 用 and/or 连接 pandas 条件 →", type(e).__name__, ":", str(e)[:90])
try:
    类型混比 = 多天[多天["序号"] > "5"]
except TypeError as e:
    print("③ 数字列和字符串比大小 →", type(e).__name__, ":", str(e)[:90])
try:
    print("④", 多天["新闻内容"][0])
except Exception as e:
    print("④ 旧版按位置取行 →", type(e).__name__, ":", str(e)[:90])
