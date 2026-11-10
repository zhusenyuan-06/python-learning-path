"""修复工具链坑 T20/T21/T22 缺失的 first_hit / last_hit（2026-11-05）。

问题：
    这三条是通过一次性写入脚本（_写入T20/T21/T22.py）落库的，
    脚本作者忘了填 first_hit / last_hit —— 但 hits 写了 1。
    后果有两个：
      ① 渲染出来的 md 里「第一次 / 最近一次」两栏显示成「—」，看不出这坑多新
      ② `priority()` 排序键取到 None → 一旦排列不对就 TypeError 崩 ls/stats
         （代码那边已修 `or ""`，但数据本身也该补上）

为什么日期填 2026-10-29 —— 不是猜的，有三处硬证据：
    T20 symptom 里写着「2026-10-29 19:20，push_github.sh v2 ...」
    T21 symptom 里写着「2026-10-29 19:15~19:35 排障实测」
    T22 symptom 里写着「2026-10-29 20:26~20:29 实测」
    三份写入脚本的抬头也都是 2026-10-29
    且 工具链坑.json 的 updated 字段 = 2026-10-29

安全性：
    改前先备份 .json → 改 → 回读校验 → 再 render。
    JSON 在 git 里，改坏了可以 git checkout 回去。
"""
import json
import shutil
import subprocess
from pathlib import Path

BASE = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记\工具链")
JSON_PATH = BASE / "工具链坑.json"
BAK = BASE / "工具链坑.json.bak-20261105"
PY = r"D:\AAAA\python.exe"
SCRIPT = BASE / "工具链坑.py"
FIX_DATE = "2026-10-29"
TARGETS = ("T20", "T21", "T22")


def main():
    # 1) 备份
    shutil.copy2(JSON_PATH, BAK)
    print("已备份 -> " + str(BAK))

    # 2) 改：只填缺失的，已有值一律不动
    db = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    changed = []
    for it in db["items"]:
        if it["id"] in TARGETS:
            before = (it.get("first_hit"), it.get("last_hit"))
            if it.get("first_hit") is None:
                it["first_hit"] = FIX_DATE
            if it.get("last_hit") is None:
                it["last_hit"] = FIX_DATE
            after = (it.get("first_hit"), it.get("last_hit"))
            changed.append((it["id"], before, after))
    if not changed:
        print("没有需要修的条目（可能已经修过了）")
    for tid, b, a in changed:
        print("  %s: first_hit/last_hit %s -> %s" % (tid, b, a))

    db["updated"] = FIX_DATE
    JSON_PATH.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3) 回读校验
    db2 = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    left = [it["id"] for it in db2["items"]
            if it.get("last_hit") is None or it.get("first_hit") is None]
    print("回读校验：仍缺日期的条目 =", left or "无")

    # 4) 重新渲染 md
    r = subprocess.run([PY, str(SCRIPT), "render"], capture_output=True, text=True,
                       encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())


if __name__ == "__main__":
    main()
