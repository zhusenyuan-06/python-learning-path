# _验证新错区轮转.py —— 独立验证「没练过的先上」排序真的生效
# 2026-10-29 · 阶段1 第5周 · 晚上复习前
#
# ---------------------------------------------------------------
# 这个文件回答一个问题：自动化说的「实测已练过就换人」是真的吗？
#
# 背景：
#   自动化在 commit a7e87b7 里声称：
#     「实测：把 E24/E25 标记为已练过后，下一期新错区自动换成 E26/E27」
#   这话不能只信它的说法，得自己跑一遍。
#
# 为什么要用【副本】跑：
#   错题追踪.json 是唯一真源，里面记着你 46 次犯错的真实历史。
#   测试如果直接改它，就等于把真题答案改掉了。
#   所以：先复制一份到临时目录，在副本上模拟，全部验证完再删掉副本，
#   最后用校验和确认真文件一个字节都没被动过。
#
# 验证四件事：
#   ① 当前状态：9 题都记了 pending（pending 不算练过）→ 新错区应该还是 E24/E25
#   ② 把 E24/E25 标成已练过（模拟你今晚做完这两题）→ 新错区应该换成 E26/E27
#   ③ 练过的题往后排，但不会消失（还在池子里，只是排队）
#   ④ 真实数据没被动过（校验和对比）
# ---------------------------------------------------------------

import json
import shutil
import sys
import tempfile
from pathlib import Path

# 笔记目录的绝对路径
BASE = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")

# sys.path.insert(0, ...) = 把这个目录插到「模块搜索路径」的最前面
#   └─ 作用：之后 import 错题追踪器 就能直接找到（虽然中文名也能 import，
#     但下面我们用的是更稳的 importlib 方式）
sys.path.insert(0, str(BASE))

import importlib.util

# importlib.util = 专门用来【按文件路径】加载模块的工具
#   └─ 为什么不用普通 import？因为模块文件名是中文「错题追踪器」，
#     import 中文名虽然合法，但在不同终端/编码环境下容易出问题；
#     按路径加载就没有这个坑
#
# spec_from_file_location("tracker", 路径) = 造一份「加载说明书」
#   └─ "tracker" 是加载后模块在内存里的名字（可以随便起）
#   └─ 第二个参数是 .py 文件的路径
spec = importlib.util.spec_from_file_location("tracker", BASE / "错题追踪器.py")

# module_from_spec(spec) = 按说明书造出模块对象（此时还没执行代码）
tracker = importlib.util.module_from_spec(spec)

# exec_module(tracker) = 真正执行这个 .py 文件（模块顶部的代码跑起来）
#   └─ 执行完，tracker 就变成了「能调用里面所有函数」的模块
spec.loader.exec_module(tracker)


# ============================================================
# 小工具：算出「新错区会抽到哪几题」
# ============================================================
def new_zone_ids(db, days=7):
    """模拟 cmd_plan 的新错区取题逻辑：_recent_new 取前 2。

    为什么不直接调 cmd_plan：
        cmd_plan 是打印给人看的，测试要看的是【题号列表】，
        所以这里只借用它内部用的 _recent_new，单独算一遍。

    逐行拆解：
        [it["id"] for it in ...] = 列表推导式
          └─ 对可迭代对象里的每个元素算出结果，收集成新列表
          └─ 这里就是把「题目对象列表」变成「题号字符串列表」
        tracker._recent_new(db, days)[:2]
          └─ 前导下划线 _recent_new 是「内部函数」的约定
            （表示不建议外部直接用，但测试里用它是合理的）
          └─ [:2] = 切片，取前 2 个（跟 cmd_plan 里 new_cap=2 对齐）
    """
    return [it["id"] for it in tracker._recent_new(db, days)[:2]]


# ============================================================
# 主流程
# ============================================================
def main():
    """跑四项验证，最后用校验和确认真数据零改动。"""
    # ---- ① 真实数据当前状态 ----
    # json.loads(字符串) = 把 JSON 文本变成 Python 对象（字典/列表）
    #   └─ 对应 json.dumps 的逆运算
    # .read_text(encoding="utf-8") = 读文件并按 UTF-8 解码成 str
    db = json.loads((BASE / "错题追踪.json").read_text(encoding="utf-8"))

    print("=== ① 真实数据当前状态 ===")
    zone = new_zone_ids(db)
    print("    新错区会抽到：" + " ".join(zone))
    # tracker.find(db, "E24") = 按 id 在 db 里找那道题（找不到返回 None）
    e24 = tracker.find(db, "E24")
    print("    E24 的 history：%s" % (e24.get("history", []),))
    # .get("history", []) = 取这个键，没有就给个默认值 []（不会 KeyError）
    print("    E24 被真正练过次数：%d（pending 不算）" % tracker._answered(e24))
    #   └─ _answered 只数 result 是 pass/fail 的记录，pending 不算
    #   └─ 这正是要验证的核心：pending ≠ 练过

    print()
    print("=== ② 用副本模拟「E24/E25 今晚做完了」 ===")
    # tempfile.mkdtemp() = 在系统临时目录建一个随机名字的新目录
    #   └─ 用完 shutil.rmtree 删掉，不留垃圾
    tmp = Path(tempfile.mkdtemp())
    bak = tmp / "错题追踪.json"
    # shutil.copy2(源, 目标) = 复制文件（2 = 连修改时间/权限一起复制）
    shutil.copy2(BASE / "错题追踪.json", bak)

    # 在【副本】上读出数据来改
    db2 = json.loads(bak.read_text(encoding="utf-8"))
    for pid in ("E24", "E25"):
        it = tracker.find(db2, pid)
        # .setdefault("history", []) = 有就用，没有就建一个空列表再返回
        #   └─ 一次调用搞定「取出来 + 没有就创建」
        it.setdefault("history", []).append({
            "date": "2026-10-29", "result": "pass", "note": "模拟：今晚做对了"
        })
        #   └─ .append(字典) = 往列表尾部塞一条记录
        #   └─ result="pass" = 这道题被真正练过了

    zone2 = new_zone_ids(db2)
    print("    新错区会抽到：" + " ".join(zone2))
    # 顺序可能是 E26 E27 也可能 E27 E26，所以两种都算通过
    ok = zone2 == ["E26", "E27"] or zone2 == ["E27", "E26"]
    print("    → %s" % ("✅ 符合预期：已练过的 E24/E25 让位给 E26/E27" if ok
                       else "❌ 不符合预期：还是 " + " ".join(zone2)))

    print()
    print("=== ③ 练过的题还在池子里吗（只是排队，不是消失）===")
    # tracker.active_items(db2) = 只取还在池子里的题（status == "active"）
    still = [it["id"] for it in tracker.active_items(db2) if it["id"] in ("E24", "E25")]
    print("    E24/E25 状态：%s" % (still or "不在 active 池里了"))
    print("    → %s" % ("✅ 还在，会在后面几期轮到" if len(still) == 2 else "❌ 丢了"))
    #   └─ still or "不在..." = 三元表达式的简写版：
    #      still 非空就用 still，空就用后面那句

    print()
    print("=== ④ 真实数据没被动过（校验和）===")
    # .read_bytes() = 读成原始字节（不解码），用来做「一字节不差」的对比
    live = (BASE / "错题追踪.json").read_bytes()
    same = live == bak.read_bytes()
    print("    → %s" % ("✅ 真实 json 与副本一致，测试全程只读真数据" if same
                       else "❌ 真实 json 被改动了！"))

    # 清理临时目录（ignore_errors=True = 删不掉也别报错，测试不该因清理失败而崩）
    shutil.rmtree(tmp, ignore_errors=True)


# __name__ == "__main__" = 只在直接运行本文件时执行
if __name__ == "__main__":
    main()
