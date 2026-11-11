# _参考样例_os_datetime语法.py
# 只看语法，别抄任务 —— 正式任务是同目录的 11.11练习_os与datetime.py
# 本文件每一段都能直接跑，跑出来的输出就是讲义里引用的「真实输出」
#
# 复习价值：这些是 os / datetime 里 90% 会用到的写法

import os
from datetime import datetime, date, timedelta
from pathlib import Path

BASE = Path(__file__).parent          # 这个文件自己所在的目录（绝对路径）
DEMO = BASE / "_输出_os_datetime演示"  # 演示用目录，跑完可以删

print("=" * 62)
print("① os.getcwd()：程序「当前在哪个目录」")
print("=" * 62)
print("  os.getcwd()          =", os.getcwd())
print("  __file__             =", __file__)
print("  Path(__file__).parent =", BASE)
print()
print("  ⚠️ 这两个不一样：")
print("     getcwd() 是【你启动程序时所在的目录】")
print("     __file__ 是【脚本文件自己所在的位置】")
print("     → 想操作文件，必须用 __file__ 定位，不能用 cwd")

print()
print("=" * 62)
print("② os.path.join：拼路径（别用 + 号）")
print("=" * 62)
print('  join("输出", "a.txt")      =', os.path.join("输出", "a.txt"))
print('  join("D:/x", "y/z.txt")    =', os.path.join("D:/x", "y/z.txt"))
print('  join("输出", "相对.txt")   =', os.path.join("输出", "相对.txt"))
print('  join("输出", "/a.txt")     =', os.path.join("输出", "/a.txt"), " ← 坑：前面的被吃掉了")
print('  join("输出", "D:/x.txt")   =', os.path.join("输出", "D:/x.txt"), " ← 坑：也被吃掉")

print()
print("=" * 62)
print("③ os.path.splitext：拆成「主名 + 扩展名」")
print("=" * 62)
for 名字 in ["报告.pdf", "a.tar.gz", ".gitignore", "无扩展名"]:
    print(f"  splitext({名字!r}) = {os.path.splitext(名字)}")

print()
print("=" * 62)
print("④ os.walk：递归遍历目录树")
print("=" * 62)
DEMO.mkdir(parents=True, exist_ok=True)          # 建目录（多级 + 已存在不报错）
(DEMO / "子目录").mkdir(exist_ok=True)
(DEMO / "说明.txt").write_text("hello", encoding="utf-8")
(DEMO / "子目录" / "里面的.txt").write_text("world", encoding="utf-8")
for 根, 目录们, 文件们 in os.walk(DEMO):
    print(f"  根目录：{根}")
    print(f"    子目录：{目录们}")
    print(f"    文件  ：{文件们}")

print()
print("=" * 62)
print("⑤ os.path.getmtime + datetime.fromtimestamp：文件最后修改时间")
print("=" * 62)
样例 = BASE / "文本.txt"
if 样例.exists():
    时间戳 = 样例.stat().st_mtime
    print("  st_mtime（原始时间戳）=", 时间戳)
    print("  fromtimestamp 转换后  =", datetime.fromtimestamp(时间戳))
    print("  strftime 排版后        =", datetime.fromtimestamp(时间戳).strftime("%Y-%m-%d %H:%M:%S"))
else:
    print("  （找不到 文本.txt，跳过）")

print()
print("=" * 62)
print("⑥ now / today / date.today —— 三个「现在」的区别")
print("=" * 62)
print("  datetime.now()   =", datetime.now(), " 类型:", type(datetime.now()))
print("  datetime.today() =", datetime.today())
print("  date.today()     =", date.today(), " 类型:", type(date.today()))
print("  → date 只有「哪一天」，datetime 连几点几分都有")

print()
print("=" * 62)
print("⑦ strftime：把时间对象排版成字符串")
print("=" * 62)
t = datetime(2026, 11, 7, 9, 5, 3)
print("  时间对象 =", t)
print("  %Y-%m-%d %H:%M:%S =", t.strftime("%Y-%m-%d %H:%M:%S"))
print("  ⚠️ %m = 月份，%M = 分钟（只差一个大小写）")
print("     %m =", t.strftime("%m"), "  %M =", t.strftime("%M"))
print("  %A 星期 =", t.strftime("%A"))
print("  isoformat() =", t.isoformat(), " ← 存 JSON / 当文件名都好用")

print()
print("=" * 62)
print("⑧ strptime：把字符串解析回日期")
print("=" * 62)
s = "2026-11-07"
print('  strptime("2026-11-07", "%Y-%m-%d") =', datetime.strptime(s, "%Y-%m-%d"))
try:
    datetime.strptime(s, "%Y/%m/%d")
except ValueError as e:
    print("  ⚠️ 格式串写错 →", type(e).__name__, ":", e)
    print("     （是 ValueError，不是 TypeError —— 类型对但值不合理）")

print()
print("=" * 62)
print("⑨ timedelta：算时间差")
print("=" * 62)
起点 = datetime(2026, 11, 1)
终点 = datetime(2026, 11, 11)
差 = 终点 - 起点
print("  终点 - 起点 =", 差)
print("  .days =", 差.days, "  .total_seconds() =", 差.total_seconds())
负差 = 起点 - 终点
print("  起点 - 终点 =", 负差, " .days =", 负差.days, " .total_seconds() =", 负差.total_seconds())
print("  ⚠️ .days 只看「整天数」，不足一天的部分被丢掉（且负数向下取整）：")
半日差 = 终点 - 终点.replace(hour=0) - timedelta(hours=1)
print("     差 1 小时 → .days =", 半日差.days, " .seconds =", 半日差.seconds, " .total_seconds() =", 半日差.total_seconds())
print("     所以要精确秒数一律用 .total_seconds()")
print("  终点 + 7 天 =", 终点 + timedelta(days=7))

print()
print("=" * 62)
print("⑩ os.environ：环境变量")
print("=" * 62)
print("  环境变量总数：", len(os.environ))
print("  有 PATH 吗：", "PATH" in os.environ)
print("  取一个没设过的：", os.environ.get("MY_API_KEY", "（没设）"))
print("  → API key / token 应该放这里，不要写死在代码里")

print()
print("=" * 62)
print("⑪ os.makedirs + os.listdir：建目录 / 列目录")
print("=" * 62)
print("  mkdir 前 exists =", DEMO.exists())
DEMO.mkdir(parents=True, exist_ok=True)
print("  mkdir 后 exists =", DEMO.exists())
print("  listdir =", sorted(os.listdir(DEMO)))
print("  ⚠️ listdir 顺序【不保证】，要用就自己 sorted()")

print()
print("=" * 62)
print("⑫ os.mkdir vs os.makedirs：建目录的两个坑")
print("=" * 62)
try:
    os.mkdir(str(DEMO / "深" / "更深"))        # 父目录不存在
except FileNotFoundError as e:
    print("  mkdir 建多级 →", type(e).__name__, ":", e)
    print("     （父目录不在，它不会帮你建）")
os.makedirs(str(DEMO / "深" / "更深"), exist_ok=True)
print("  makedirs 建多级 → 成功，exists =", (DEMO / "深" / "更深").exists())
try:
    os.makedirs(str(DEMO / "深" / "更深"))     # 已存在，不带 exist_ok
except FileExistsError as e:
    print("  makedirs 再建一次（没写 exist_ok）→", type(e).__name__, ":", e)
    print("     → 所以要写 exist_ok=True")

print()
print("=" * 62)
print("⑬ 给文件起名带时间戳（实战最常用的一招）")
print("=" * 62)
now = datetime.now()
文件名 = "导出_" + now.strftime("%Y%m%d_%H%M%S") + ".csv"
print("  生成的文件名 =", 文件名)
print("  isoformat  版 =", "导出_" + now.isoformat() + ".csv")
print("  ⚠️ 文件名里【不能】用 : —— Windows 不允许")
try:
    bad = "导出_" + now.strftime("%Y-%m-%d %H:%M:%S") + ".csv"
    with open(str(DEMO / bad), "w", encoding="utf-8") as f:
        f.write("x")
except OSError as e:
    print("     用 %H:%M:%S 直接当文件名 →", type(e).__name__, ":", e)
    print("     → 所以文件名里用 %H%M%S（去掉冒号），只在【显示】时才加冒号")

print("  ⚠️⚠️ 但 pathlib 的 write_text 会【静默失败】（Windows ADS 备用数据流）:")
try:
    静默 = DEMO / "报告:2026.txt"
    静默.write_text("我是正文内容", encoding="utf-8")
    print("     write_text 写 '报告:2026.txt' → 报成功，但磁盘上只有:", sorted(os.listdir(DEMO)))
    print("     主文件 '报告' 的大小 =", os.path.getsize(DEMO / "报告"), "← 内容跑到 ADS 里去了")
    print("     → 所以【写文件名相关的文件优先用 open()】—— 它会明确报错，不会静默丢内容")
    (DEMO / "报告").unlink(missing_ok=True)
except Exception as e:
    print("     →", type(e).__name__, ":", e)
