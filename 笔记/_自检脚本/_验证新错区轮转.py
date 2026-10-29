"""独立验证 _recent_new 的「没练过的先上」排序是否真的生效。

为什么写这个测试：
  自动化在 commit a7e87b7 里声称「实测：把 E24/E25 标记为已练过后，
  下一期新错区自动换成 E26/E27」。这话不能只信它的说法，
  得自己跑一遍 —— 而且必须用**副本**跑，绝不能动真的错题追踪.json。

验证三件事：
  ① 当前状态：9 题都记了 pending（pending 不算练过）→ 新错区应该还是 E24/E25
  ② 把 E24/E25 标成已练过（模拟你今晚做完这两题）→ 新错区应该换成 E26/E27
  ③ 练过的题往后排，但不会消失（还在池子里，只是排队）
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

BASE = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")
sys.path.insert(0, str(BASE))

import importlib.util

spec = importlib.util.spec_from_file_location("tracker", BASE / "错题追踪器.py")
tracker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracker)


def new_zone_ids(db, days=7):
    """模拟 cmd_plan 的新错区取题：_recent_new 取前 2。"""
    return [it["id"] for it in tracker._recent_new(db, days)[:2]]


def main():
    db = json.loads((BASE / "错题追踪.json").read_text(encoding="utf-8"))

    print("=== ① 真实数据当前状态 ===")
    zone = new_zone_ids(db)
    print("    新错区会抽到：" + " ".join(zone))
    e24 = tracker.find(db, "E24")
    print("    E24 的 history：%s" % (e24.get("history", []),))
    print("    E24 被真正练过次数：%d（pending 不算）" % tracker._answered(e24))

    print()
    print("=== ② 用副本模拟「E24/E25 今晚做完了」 ===")
    tmp = Path(tempfile.mkdtemp())
    bak = tmp / "错题追踪.json"
    shutil.copy2(BASE / "错题追踪.json", bak)
    db2 = json.loads(bak.read_text(encoding="utf-8"))
    for pid in ("E24", "E25"):
        it = tracker.find(db2, pid)
        it.setdefault("history", []).append({
            "date": "2026-10-29", "result": "pass", "note": "模拟：今晚做对了"
        })
    zone2 = new_zone_ids(db2)
    print("    新错区会抽到：" + " ".join(zone2))
    ok = zone2 == ["E26", "E27"] or zone2 == ["E27", "E26"]
    print("    → %s" % ("✅ 符合预期：已练过的 E24/E25 让位给 E26/E27" if ok
                       else "❌ 不符合预期：还是 " + " ".join(zone2)))

    print()
    print("=== ③ 练过的题还在池子里吗（只是排队，不是消失）===")
    still = [it["id"] for it in tracker.active_items(db2) if it["id"] in ("E24", "E25")]
    print("    E24/E25 状态：%s" % (still or "不在 active 池里了"))
    print("    → %s" % ("✅ 还在，会在后面几期轮到" if len(still) == 2 else "❌ 丢了"))

    print()
    print("=== ④ 真实数据没被动过（校验和）===")
    live = (BASE / "错题追踪.json").read_bytes()
    same = live == bak.read_bytes()
    print("    → %s" % ("✅ 真实 json 与副本一致，测试全程只读真数据" if same
                       else "❌ 真实 json 被改动了！"))

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
