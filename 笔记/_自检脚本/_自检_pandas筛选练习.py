# -*- coding: utf-8 -*-
"""T36 反向自检第②步：把参考答案灌进作答区 → 跑 → 必须全绿。

用法：在练习目录跑本脚本，它会生成 _临时_答案版.py 并自动运行、打印结果。
（生成的临时文件跑完即删，不留在仓库里）
"""
import re
import subprocess
import sys
from pathlib import Path

练习目录 = Path(__file__).resolve().parents[2] / "练习"   # 脚本在 笔记/_自检脚本/ → 退两级到仓库根
源文件 = 练习目录 / "11.17练习_pandas筛选与增删列.py"
临时文件 = 练习目录 / "_临时_答案版.py"

答案 = {
    "任务1_筛选单条件": """
    df = pd.read_csv(CSV路径)
    选中 = df[df['星期'] == '星期二']
    return len(选中), list(选中['序号'])
""",
    "任务2_筛选多条件": """
    df = pd.read_csv(CSV路径)
    选中 = df[(df['星期'] == '星期一') & (df['序号'] > 5)]
    return list(选中['序号'])
""",
    "任务3_筛选关键词": """
    df = pd.read_csv(CSV路径)
    选中 = df[(df['新闻内容'].str.contains('银行', regex=False))
            | (df['新闻内容'].str.contains('雨雪', regex=False))]
    return list(选中['序号'])
""",
    "任务4_筛选后统计": """
    df = pd.read_csv(CSV路径)
    选中 = df[df['序号'] <= 10]
    return int(选中['序号'].max()), len(选中)
""",
    "任务5_新增数值列": """
    df = pd.read_csv(CSV路径)
    df['双倍序号'] = df['序号'] * 2
    return list(df['双倍序号'].head(3))
""",
    "任务6_新增字符串列": """
    df = pd.read_csv(CSV路径)
    df['标签'] = df['星期'] + '-' + df['序号'].astype(str)
    return list(df['标签'].head(3))
""",
    "任务7_删除列": """
    df = pd.read_csv(CSV路径)
    新的 = df.drop(columns=['新闻内容'])
    return list(新的.columns)
""",
    "任务8_重命名列": """
    df = pd.read_csv(CSV路径)
    新的 = df.rename(columns={'序号': '编号'})
    return list(新的.columns)
""",
}

文本 = 源文件.read_text(encoding="utf-8")
for 名, 体 in 答案.items():
    模式 = re.compile(r"def %s\(\):.*?\n    pass" % re.escape(名), re.DOTALL)
    新块 = "def %s():\n%s" % (名, 体)
    文本, n = 模式.subn(lambda m: 新块, 文本)
    assert n == 1, "替换失败（匹配到 %d 次）：%s" % (n, 名)

临时文件.write_text(文本, encoding="utf-8")
print("已生成答案版：", 临时文件.name)
print("=" * 68)
结果 = subprocess.run([sys.executable, str(临时文件)], cwd=str(练习目录),
                  capture_output=True, text=True, encoding="utf-8")
print(结果.stdout)
if 结果.stderr:
    print("--- stderr ---")
    print(结果.stderr[-1500:])
临时文件.unlink(missing_ok=True)
print("=" * 68)
通过行数 = 结果.stdout.count("✅ 第")
失败行数 = 结果.stdout.count("❌ 第")
print("答案版自检：✅ %d 条通过 / ❌ %d 条失败" % (通过行数, 失败行数))
print("全绿" if 通过行数 == 8 and 失败行数 == 0 else "⚠️ 不是全绿，期望值或答案有问题")
