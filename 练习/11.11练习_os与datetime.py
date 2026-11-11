# 11.11 练习：os / datetime
# 对应日程：11-09 上午「os / datetime 常用（2h）」｜📌 欠 11-09，顺延 11-11 余量段
#
# ⚠️ 这 2h 的定位（先看这段，别走偏）：
#   os        = 跟操作系统打交道（找文件、建目录、读环境变量）
#   datetime  = 跟时间打交道（现在几点、格式化、算间隔）
#   它们是【下游】的垫脚石 —— 11-09 晚上那个「提取文本中的日期/邮箱」
#   要靠 datetime.strptime 把字符串变回时间对象，今天学的每个函数都用得上。
#
# 规则：
#   1. 本文件所有代码自己写，写不出来先写 # TODO 占位，别翻聊天记录抄
#   2. 语法样例在同目录 _参考样例_os_datetime语法.py —— 只看语法，别抄任务
#   3. 所有【TODO】都要替换成真代码；跑不通先自己读红字，卡 10 分钟以上再问
#   4. 演示目录统一建在 练习/_输出_os_datetime演示/，别往仓库根目录扔垃圾
#
# ⚠️ 本文件里的「我写的第一版」等你自己写完后我再补 —— 现在只有任务和空位。
from os.path import exists
from pathlib import Path
import os
from datetime import datetime, date, timedelta

from win32comext.mapi.mapitags import PR_START_DATE

# 这个文件自己所在的目录（绝对路径）—— 别用 os.getcwd()，理由见任务 1
BASE = Path(__file__).parent
DEMO = BASE / "_输出_os_datetime演示"


# =============================================================================
# 任务 1：搞清楚「我在哪」和「文件在哪」（15min）
#
#   ① 打印 os.getcwd()
#   ② 打印 Path(__file__).parent
#   ③ 解释：为什么脚本里定位文件要用 __file__，不能用 getcwd()
#
#   ⚠️ 这个坑你踩过：11-04 在 C 盘目录运行 .\.venv\... 就是因为
#      「当前目录」≠「脚本所在目录」。这次要能一句话说清区别。
# =============================================================================

# TODO 1-①：打印 os.getcwd()
print(os.getcwd())
# TODO 1-②：打印 Path(__file__).parent
print(Path(__file__).parent)
# TODO 1-③：用文字回答（写在下面这行注释里，写完把「未填」改掉）
# 我的回答：Path(__file__).parent是脚本文件自己所在的目录,getcwd() 是你敲命令时终端所在的文件夹，
# 跟脚本文件在哪没关系。换台电脑、换个文件夹运行，同一个脚本就会找不到文件 —— 所以要用 __file__ 定位。


# =============================================================================
# 任务 2：目录体检（15min）
#
#   对 DEMO 这个目录做四件事：
#   ① 用 os.path.exists 看它在不在
#   ② 用 os.makedirs 建它（记得 exist_ok=True，不建也行，但要写出来）
#   ③ 在里面建一个 "子目录"，再用 os.listdir 列出 DEMO 里的东西（记得 sorted）
#   ④ 在 DEMO 里写两个文件：a.txt、b.md，然后列出【所有 .txt 文件】
#
#   💡 为什么这题重要：作品「批量重命名」的核心就是
#      「先列清单 → 再判断 → 再动手」三步，第 1 步就是 listdir。
# =============================================================================

# TODO 2-①
print(os.path.exists(DEMO))
# TODO 2-②
os.makedirs(DEMO,exist_ok=True)
# TODO 2-③
os.makedirs(DEMO / '子目录',exist_ok=True)
print(sorted(os.listdir(DEMO)))
# TODO 2-④
子目录 = DEMO/"子目录"
(DEMO / "a.txt").write_text("内容", encoding="utf-8")
(子目录 / "b.txt").write_text("内容", encoding="utf-8")
print("所有 .txt 文件：", [str(p.relative_to(DEMO)) for p in DEMO.rglob("*.txt")])

# =============================================================================
# 任务 3：文件名拆解（15min）
#
#   给定文件名列表，用 os.path.splitext 把每个拆成「主名 + 扩展名」：
#       ["报告.pdf", "a.tar.gz", ".gitignore", "无扩展名"]
#
#   打印成对齐的表格：文件名 | 主名 | 扩展名
#
#   ⚠️ 思考题（写在注释里）：
#      ".gitignore" 拆出来扩展名是什么？这在「只处理 .py 文件」的逻辑里
#      会不会出事？（这题跟 batch-rename 作品的过滤条件直接相关）
#
#   再加一个：用 os.path.join 拼 "输出" + "报告.txt"
#   ⚠️ 思考题：join("输出", "D:/绝对路径.txt") 会得到什么？为什么？
# =============================================================================

文件名列表 = ["报告.pdf", "a.tar.gz", ".gitignore", "无扩展名"]

# TODO 3-①：循环 + splitext，打印表格
for 名 in 文件名列表:
    主名, 扩展名 = os.path.splitext(名)        # ← 填 splitext
    print(f"{名} | {主名} | {扩展名}")# ← 填表格那行

# TODO 3-②：回答思考题（改掉「未填」）
# 关于 .gitignore：不会报错，但是有一个问题就是拓展名变成了空，想专门处理 .gitignore 这种点开头的文件时，splitext 帮不了你，得靠 名.startswith(".") 判断。

# TODO 3-③：join 拼路径 + 回答思考题
print(os.path.join("输出", "报告.txt"))
# 关于 join 被吃掉路径：会得到D:/绝对路径.txt，因为有绝对路径的时候join会直接使用绝对路径


# =============================================================================
# 任务 4：时间格式化（20min）
#
#   ① 打印现在的完整时间：datetime.now()
#   ② 用 strftime 排成三种格式：
#        "2026-11-11 13:45:00"   （%Y-%m-%d %H:%M:%S）
#        "20261111_134500"       （%Y%m%d_%H%M%S）← 当文件名用
#        "2026年11月11日"        （%Y年%m月%d日）
#   ③ 再打一个「昨天同一天」的：用 now - timedelta(days=1)
#   ④ 算一下：距离 2028-06-30（你毕业那天）还有多少天
#
#   ⚠️ 必答题（写在注释里）：
#      %m 和 %M 只差一个大小写，分别是什么？
#      如果你把「分钟」写成 %m，会得到什么看似合理但完全错误的结果？
#
#   💡 ④ 的算法：终点 - 起点 = timedelta → .days 就是天数
#      （注意：终点要比起点晚，所以顺序别写反）
# =============================================================================

# TODO 4-①
print(datetime.now())
# TODO 4-②
now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))   # 2026-11-11 15:14:19
print(now.strftime("%Y%m%d_%H%M%S"))       # 20261111_151419
print(now.strftime("%Y年%m月%d日"))        # 2026年11月11日

# TODO 4-③
print(datetime.now() - timedelta(days=1))
# TODO 4-④
毕业 = datetime(2028, 6, 30)
print((毕业 - datetime.now()).days)        # 596
# TODO 4-⑤：回答必答题（改掉「未填」）
# %m 和 %M：小写是月，大写是分,如果弄反了都是数字很难发现


# =============================================================================
# 任务 5：字符串 → 时间对象（20min）★ 今天的核心
#
#   ① 把 "2026-11-07" 用 datetime.strptime 变成时间对象，打印出来
#   ② 从这个对象里取出：年、月、日、星期几
#   ③ 再把 "2026年11月07日" 解析出来（格式串自己写）
#   ④ 故意用错的格式串解析 "2026-11-07"，用 try/except 接住并打印异常类型
#      （提示：格式串写成 "%Y/%m/%d"）
#
#   ⚠️ 必答题（写在注释里）：
#      任务 4 的 strftime 是「时间 → 字符串」，这个 strptime 是反方向
#      「字符串 → 时间」。为什么你需要反向？
#      （答案跟日程表上 11-09 晚上「提取文本中的日期/邮箱」直接相关：
#       提取出来的日期是【字符串】，要跟今天比大小，必须先变回时间对象）
#
#   ⚠️ ④ 的异常是 ValueError 还是 TypeError？为什么？
#      （这题跟错题池 E30 是同一个考点）
# =============================================================================

# TODO 5-①
dt = datetime.strptime("2026-11-07", "%Y-%m-%d")
print(dt)      # 2026-11-07 00:00:00
# TODO 5-②
print(dt.year, dt.month, dt.day)      # 2026 11 7
print(dt.weekday())                   # 5
print(["一","二","三","四","五","六","日"][dt.weekday()])

# TODO 5-③
dt2 = datetime.strptime("2026年11月07日", "%Y年%m月%d日")

# TODO 5-④
try:
    datetime.strptime("2026-11-07", "%Y/%m/%d")
except ValueError as e:
    print(type(e).__name__, e)

# TODO 5-⑤：回答必答题（改掉「未填」）
#为什么需要反向解析：字符串比只会比相同位置数字的大小
#更准确地说：字符串比大小比的是【字典序】，只在「格式完全统一 + 月日都补零」时才碰巧等于时间先后。
#实测翻车案例：'2026-2-1' vs '2026-10-1'
#   字符串比：False（说 2月1日 < 10月1日）
#   实际时间：True （说 2月1日 > 10月1日）  ← 结果完全相反！因为 '2' 的编码 > '1'
#而正则提取出来的日期格式是五花八门的（11/07/2026、2026年11月7日、11-7-2026），
#格式一不统一，字典序立刻失效。
#所以必须先用 strptime 把字符串变回【时间对象】，才能跟 datetime.now() 比大小、算「距今多少天」。
#一句话：strftime 负责「往外输出」，strptime 负责「把外面进来的东西接住并变成能算的对象」。

# TODO 5-⑥：回答 ValueError vs TypeError（改掉「未填」）
#TypeError = 「类型不对」—— 传了个整数给它、或者对象没有这个属性
#ValueError = 「类型对，但值不对」—— 传的是字符串（类型对），但内容跟格式串对不上
#


# =============================================================================
# 任务 6：算间隔（15min）
#
#   ① 用 timedelta 算：现在 - 7 天前 = 多少天
#   ② 算一个「不足一天」的例子：现在 - 1 小时，
#      打印 .days、.seconds、.total_seconds()
#      ⚠️ 看清楚 .days 是不是你以为的那个数
#   ③ 给「昨天」的文件打标记：判断某个文件是不是 7 天前修改的
#      （用 os.path.getmtime + datetime.fromtimestamp，跟今天比）
#   ④ 给上面那个文件算「多少天没动」，用 .days
#
#   💡 ③ 的价值：这正是「清理旧文件」「找出过期缓存」的原型，
#      也是你 11-09 晚上做日期提取时最需要的比较逻辑。
# =============================================================================

# TODO 6-①
now = datetime.now()
七天前 = now - timedelta(days=7)
间隔 = now - 七天前
print("现在 - 7天前 =", 间隔)
print("  .days =", 间隔.days)                    # 7
print("  .total_seconds() =", 间隔.total_seconds())  # 604800.0

# TODO 6-②
一小时内 = now - timedelta(hours=1)
不足一天 = now - 一小时内
print("现在 - 1小时前 =", 不足一天)
print("  .days =", 不足一天.days)                # 0  ← 不足一天就是 0
print("  .seconds =", 不足一天.seconds)          # 3600
print("  .total_seconds() =", 不足一天.total_seconds())  # 3600.0

# TODO 6-③
# 先造一个「7 天前修改过」的文件 —— os.utime 专门用来改文件的修改时间
旧文件 = DEMO / "旧文件.txt"
旧文件.write_text("我是 7 天前改的\n", encoding="utf-8")
七日前时间戳 = (now - timedelta(days=7)).timestamp()
os.utime(旧文件, (七日前时间戳, 七日前时间戳))

时间戳 = os.path.getmtime(旧文件)                # 1793777652.23 ← 秒数，不是时间对象
修改时间 = datetime.fromtimestamp(时间戳)        # ← 这行才是关键：秒 → 时间对象
print("旧文件 getmtime（时间戳）=", 时间戳)
print("旧文件最后修改 =", 修改时间.strftime("%Y-%m-%d %H:%M:%S"))

# TODO 6-④
距今 = now - 修改时间
print("距今 =", 距今, "| .days =", 距今.days)   # 7
print("是不是 7 天前改的？", 距今.days >= 7)      # True

# 顺带：造一个 3 天前的对比一下
三天前文件 = DEMO / "三天前.txt"
三天前文件.write_text("x\n", encoding="utf-8")
三天前时间戳 = (now - timedelta(days=3)).timestamp()
os.utime(三天前文件, (三天前时间戳, 三天前时间戳))
三天前修改时间 = datetime.fromtimestamp(os.path.getmtime(三天前文件))
print("三天前那个文件 .days =", (now - 三天前修改时间).days)  # 3


# =============================================================================
# 任务 7：收尾（10min）
#
#   ① 把任务 2~6 的关键结果写进 DEMO/学习报告.txt（用 pathlib 的 write_text）
#   ② 打印这个文件的绝对路径和大小（os.path.getsize）
#   ③ 打印今天的日期（date.today()）和星期几
#
#   ⚠️ 注意：文件名别带冒号 —— Windows 不允许。这是你会在 ⑬ 段亲手撞到的。
# =============================================================================

# TODO 7-①
# 把任务 2~6 的关键结果收集起来，最后一次性写进文件
报告 = []
报告.append("=== os / datetime 学习报告 ===")
报告.append("生成时间：" + now.strftime("%Y-%m-%d %H:%M:%S"))
报告.append("")
报告.append("【任务2】DEMO 里的东西：" + str(sorted(os.listdir(DEMO))))
报告.append("【任务2】所有 .txt 文件：" + str([str(p.relative_to(DEMO)) for p in DEMO.rglob("*.txt")]))
报告.append("【任务3】splitext：报告.pdf → " + str(os.path.splitext("报告.pdf")))
报告.append("【任务3】join：输出 + 报告.txt → " + os.path.join("输出", "报告.txt"))
报告.append("【任务4】三种格式：" + now.strftime("%Y-%m-%d %H:%M:%S")
             + " / " + now.strftime("%Y%m%d_%H%M%S")
             + " / " + now.strftime("%Y年%m月%d日"))
报告.append("【任务4】距离 2028-06-30 还有 " + str((datetime(2028, 6, 30) - now).days) + " 天")
报告.append("【任务5】strptime 解析结果：" + str(datetime.strptime("2026-11-07", "%Y-%m-%d")))
报告.append("【任务6】7 天前的间隔：" + str(间隔.days) + " 天")
报告.append("【任务6】旧文件最后修改：" + 修改时间.strftime("%Y-%m-%d %H:%M:%S"))
报告.append("")
报告.append("今天是 " + date.today().isoformat()
             + " 星期" + ["一", "二", "三", "四", "五", "六", "日"][date.today().weekday()])

报告路径 = DEMO / "学习报告.txt"
报告路径.write_text("\n".join(报告), encoding="utf-8")
print("报告已写入：")
print(报告路径.read_text(encoding="utf-8"))

# TODO 7-②
print("绝对路径 =", 报告路径.resolve())
print("文件大小 =", os.path.getsize(报告路径), "字节")   # pathlib 版：报告路径.stat().st_size

# TODO 7-③
今天 = date.today()
print("今天 =", 今天)
print("星期几 =", ["一", "二", "三", "四", "五", "六", "日"][今天.weekday()])


# =============================================================================
# 【交卷前自查】
#
#   [ ] 所有 TODO 都写完了，没有「未填」残留
#   [ ] 脚本能一次跑完，不报错
#   [ ] 打印出来的数字我【亲眼核对过】，不是"看着像对的"
#   [ ] 任务 3 的两个思考题、任务 4/5 的必答题、都在注释里写了自己的话
#   [ ] 没有在仓库根目录留下垃圾文件（演示文件都在 _输出_os_datetime演示/ 里）
#
# 写完之后告诉我，我来跑、逐题批改、把你的真实错误登记进错题池。
# =============================================================================
