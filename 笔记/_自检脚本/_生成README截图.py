# -*- coding: utf-8 -*-
"""生成终端样式的截图（PNG），用于 README 作品展示。

用法：python 生成截图.py
输出：截图/ 目录下的 PNG
"""
import os
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.rcParams["font.sans-serif"] = [
    "Microsoft YaHei", "Segoe UI Emoji", "Segoe UI Symbol", "SimHei", "DejaVu Sans",
]
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["axes.unicode_minus"] = False

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
截图目录 = os.path.join(ROOT, "截图")
os.makedirs(截图目录, exist_ok=True)

# 配色
BG = "#1E1E2E"
CHROME = "#313244"
FG = "#CDD6F4"
GREEN = "#A6E3A1"
BLUE = "#89B4FA"
YELLOW = "#F9E2AF"
RED = "#F38BA8"
TEAL = "#94E2D5"

# (输出文件名, 标题, [(命令行, 输出或None)], 高亮行集合)
任务 = [
    (
        "01-通讯录CLI.png",
        "通讯录 CLI · 增删改查 + 统计",
        [
            ("python contact_book.py", None),
            ("=== 查询 ===", None),
            ("小明的电话: 13800138888", "out"),
            ("小刚的邮箱: xg@mail.com", "out"),
            ("小丽的电话: 查无此人", "err"),
            ("", None),
            ("=== 添加 ===", None),
            ("已添加 小芳", "out"),
            ("小芳 已经在通讯录里了，未覆盖", "warn"),
            ("", None),
            ("=== 统计 ===", None),
            ("没填邮箱的: ['小玉', '小芳'] 共 2 人", "out"),
        ],
    ),
    (
        "02-多模块配送单.png",
        "多模块配送单 · 入口/配置/业务/工具 四层分离",
        [
            ("python main.py", None),
            ("==================================================", None),
            ("配送单生成器 · 阳光城 · 2026-10-27", "head"),
            ("==================================================", None),
            ("园所: 阳光城", "out"),
            ("菜单: 青菜12.5kg, 豆腐8.0kg, 排骨15.0kg, ...", "out"),
            ("", None),
            ("总价:   266.10 元", "out"),
            ("均价:   44.35 元", "out"),
            ("种类数: 6", "out"),
            ("", None),
            ("[注意] 需要留意：", "warn"),
            ("   - 总价 266.10 低于起送金额 300.00", "warn"),
            ("", None),
            ("  【原始菜单数据】", "head"),
            ("   菜名     | 重量     | 金额", "out"),
            ("   青菜     | 12.5   | 38.50", "out"),
            ("   排骨     | 15.0   | 128.00", "out"),
        ],
    ),
    (
        "03-错题追踪器.png",
        "错题追踪器 · 每周四自动出卷，连续答对 2 次才退场",
        [
            ("python 错题追踪器.py stats", None),
            ("错题追踪器 统计（更新于 2026-10-27）", "head"),
            ("----------------------------------------------", None),
            ("在池子里（每周必考） : 22", "out"),
            ("  其中高频（≥2次）    : 8", "warn"),
            ("已掌握（已退场）      : 1", "out"),
            ("历史累计错题          : 23", "out"),
            ("累计犯错次数          : 37", "out"),
            ("", None),
            ("顽固问题 TOP:", "head"),
            ("  E15 犯 5 次 —— 静默错误三件套（缺 strip / reverse / else）", "err"),
            ("  E02 犯 4 次 —— 同一个变量名承担两种角色", "err"),
            ("  E01 犯 3 次 —— if 缺 else/return：提示了却照样执行", "err"),
        ],
    ),
    (
        "04-多模块项目结构.png",
        "项目结构 · 每一层只干一件事",
        [
            ("小项目_多模块demo/", "head"),
            ("├── main.py              入口层：只组装", "out"),
            ("├── config.py            配置层：常量 + 路径", "out"),
            ("├── business.py          业务层：业务规则", "out"),
            ("└── utils/", None),
            ("    ├── __init__.py       标记为包", "out"),
            ("    └── helpers.py       工具层：与业务无关", "out"),
            ("", None),
            ("依赖方向（单向，不循环）：", "head"),
            ("  main.py → business.py → config.py / helpers.py", "out"),
            ("", None),
            ("改一个参数只动一个文件：", "head"),
            ("  改 config.py 的起送金额 → 全项目自动生效", "out"),
        ],
    ),
]

颜色 = {
    None: FG,
    "out": FG,
    "err": RED,
    "warn": YELLOW,
    "head": TEAL,
    "cmd": BLUE,
}


def 画一张(文件名, 标题, 行列表, 高亮行集合):
    n = len(行列表) + 3
    fig_h = max(2.4, 0.30 * n + 0.9)
    fig = plt.figure(figsize=(9.2, fig_h), dpi=150)
    fig.patch.set_facecolor(BG)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch(
        (0.012, 0.03), 0.976, 0.94,
        boxstyle="round,pad=0.006,rounding_size=0.012",
        facecolor="#181825", edgecolor=CHROME, linewidth=1.2, zorder=0,
    ))
    # 标题栏（用一个方块盖住圆角，再在上面画圆角，模拟 macOS 窗口）
    ax.add_patch(plt.Rectangle((0.012, 0.795), 0.976, 0.095,
                               facecolor=CHROME, edgecolor="none", zorder=1))
    for i, c in enumerate([RED, YELLOW, GREEN]):
        ax.add_patch(plt.Circle((0.045 + i * 0.028, 0.885), 0.011, color=c, zorder=3))
    ax.text(0.5, 0.885, 标题, color=FG, fontsize=11.5,
            ha="center", va="center", zorder=3,
            family="Microsoft YaHei")

    # 文本
    y = 0.755
    dy = 0.755 / max(1, len(行列表))
    for i, (文本, 类型) in enumerate(行列表):
        if 文本 == "":
            y -= dy * 0.6
            continue
        if 文本.startswith("python "):
            c = BLUE
            前缀 = "$ "
            显示 = 前缀 + 文本
        else:
            c = 颜色.get(类型, FG)
            显示 = 文本
        if i in 高亮行集合:
            ax.add_patch(FancyBboxPatch(
                (0.025, y - dy * 0.40), 0.95, dy * 0.86,
                boxstyle="square,pad=0",
                facecolor="#313244", edgecolor="none", alpha=0.55, zorder=1,
            ))
        ax.text(0.038, y, 显示, color=c, fontsize=9.6,
                ha="left", va="center", zorder=3,
                family="Microsoft YaHei")
        y -= dy

    路径 = os.path.join(截图目录, 文件名)
    fig.savefig(路径, facecolor=BG, dpi=150)
    plt.close(fig)
    print("  ✅", 文件名)


print("生成截图中...")
for 文件名, 标题, 行列表 in 任务:
    高亮 = set()
    for i, (t, 类型) in enumerate(行列表):
        if 类型 in ("head", "warn", "err") or t.startswith("python "):
            高亮.add(i)
    画一张(文件名, 标题, 行列表, 高亮)
print(f"\n全部完成 → {截图目录}")
