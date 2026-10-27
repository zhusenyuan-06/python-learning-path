# utils/helpers.py —— 工具函数模块
# 职责：只放「通用工具函数」，不依赖具体业务
#
# 注意这个文件里没有一行是关于"配送单"的
# → 这样它可以被任何项目复用

import csv
import io


def 格式化金额(数字):
    """1234.5 → '1,234.50'"""
    return f"{数字:,.2f}"


def 读csv(路径):
    """读 csv 文件，返回列表的列表"""
    with open(路径, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))


def 写csv(路径, 行列表):
    """写 csv 文件"""
    with open(路径, "w", encoding="utf-8-sig", newline="") as f:
        写手 = csv.writer(f)
        写手.writerows(行列表)


def 统计(数字列表):
    """返回 (总和, 平均值, 最大值, 最小值, 个数)"""
    if not 数字列表:
        return 0, 0, 0, 0, 0
    return (
        sum(数字列表),
        round(sum(数字列表) / len(数字列表), 2),
        max(数字列表),
        min(数字列表),
        len(数字列表),
    )


def 表格(标题, 行列表):
    """把列表打印成一张对齐的表"""
    if not 行列表:
        print(f"  （{标题}）没有数据")
        return
    宽度 = max(len(str(格)) for 行 in 行列表 for 格 in 行)
    print(f"  【{标题}】")
    for 行 in 行列表:
        print("   " + " | ".join(str(格).ljust(宽度) for 格 in 行))
