# -*- coding: utf-8 -*-
"""独立批改：调用用户写的函数，用标准库 csv 重算真相，两边比对。

不依赖练习文件里我写的检查区（万一期望值本身写错，那个检查会跟着一起错）。
"""
import csv
import importlib.util
import io
from pathlib import Path

练习目录 = Path(__file__).resolve().parents[2] / "练习"
练习文件 = 练习目录 / "11.17练习_pandas筛选与增删列.py"
数据文件 = 练习目录 / "数据" / "news_多天版.csv"

# ---------- 载入用户模块 ----------
spec = importlib.util.spec_from_file_location("用户作答", 练习文件)
用户模块 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(用户模块)

# ---------- 标准库重算真相 ----------
文本 = 数据文件.read_bytes().decode("utf-8-sig")
行 = list(csv.DictReader(io.StringIO(文本)))
def 序(x): return int(x)

真相 = {}
选 = [r for r in 行 if r["星期"] == "星期二"]
真相[1] = (len(选), [序(r["序号"]) for r in 选])
选 = [r for r in 行 if r["星期"] == "星期一" and 序(r["序号"]) > 5]
真相[2] = [序(r["序号"]) for r in 选]
选 = [r for r in 行 if ("银行" in r["新闻内容"]) or ("雨雪" in r["新闻内容"])]
真相[3] = [序(r["序号"]) for r in 选]
选 = [r for r in 行 if 序(r["序号"]) <= 10]
真相[4] = (max(序(r["序号"]) for r in 选), len(选))
真相[5] = [序(r["序号"]) * 2 for r in 行[:3]]
真相[6] = ["%s-%s" % (r["星期"], r["序号"]) for r in 行[:3]]
真相[7] = [c for c in 行[0] if c != "新闻内容"]
真相[8] = ["编号" if c == "序号" else c for c in 行[0]]

函数名 = {
    1: "任务1_筛选单条件", 2: "任务2_筛选多条件", 3: "任务3_筛选关键词",
    4: "任务4_筛选后统计", 5: "任务5_新增数值列", 6: "任务6_新增字符串列",
    7: "任务7_删除列", 8: "任务8_重命名列",
}

def 归一(v):
    """把 numpy 标量等统一成可比的原生类型（上次 T38 的教训）"""
    if isinstance(v, tuple):
        return tuple(归一(x) for x in v)
    if isinstance(v, list):
        return [归一(x) for x in v]
    if hasattr(v, "item") and not isinstance(v, (str, bytes)):
        try:
            return v.item()
        except Exception:
            return v
    return v

print("独立批改：调用用户函数 vs 标准库 csv 重算的真相")
print("-" * 74)
全过 = True
for i in range(1, 9):
    try:
        实际 = 归一(getattr(用户模块, 函数名[i])())
        期望 = 真相[i]
        同 = (实际 == 期望)
    except Exception as e:
        实际, 同 = "报错: %s: %s" % (type(e).__name__, e), False
    全过 &= 同
    print("第 %d 题 %-14s %s" % (i, 函数名[i], "✅ 一致" if 同 else "❌ 不一致"))
    if not 同:
        print("      用户函数返回：%r" % (实际,))
        print("      标准库真相：  %r" % (真相[i],))
print("-" * 74)
print("独立批改结论：", "8 题全部与标准库算出的真相一致 ✅" if 全过 else "❌ 有不一致")
