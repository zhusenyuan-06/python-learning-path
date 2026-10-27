# -*- coding: utf-8 -*-
"""
工具链坑追踪器 —— 记录「不是 Python，但让我卡住过」的坑

为什么单独建一个清单
--------------------
错题追踪器记的是 Python 概念题（每周四出卷考）。
但这几个月真正卡住我的往往不是 Python，而是：
  - git 配置（单值键覆盖、多 IP 重试）
  - 网络排障（DNS / TCP / 代理三层怎么分）
  - Windows 环境（hosts 权限、GBK 码页、CRLF）
  - Claude Code / WorkBuddy 使用（沙箱限制、工具坑）

这些坑的特点：
  1. **不需要每周考**（不像 E01 if 缺 else 那样反复犯）
  2. 但**一旦忘了就要重新排查半小时**
  3. 所以目标是：**查得到 + 不重复踩**，不是"反复复习到掌握"

设计
----
1. 每条记录：标题 / 症状 / 原因 / 解法 / 标签 / 踩的次数
2. 踩的次数越高 → 排在越前面（说明这个坑很隐蔽）
3. 每次再踩 → 次数 +1，自动更新"最近一次"
4. 有 `solutions` 字段可以追加"新的解法"（同一个坑，不同环境可能不同解法）

命令
----
  python 工具链坑.py ls              列出全部坑（按踩坑次数排序）
  python 工具链坑.py stats           统计概览
  python 工具链坑.py show T03        看某条详情
  python 工具链坑.py add "标题" "症状" "原因" "解法" "标签1,标签2"
  python 工具链坑.py hit T03 "备注"  又踩了一次 → 次数 +1
  python 工具链坑.py fix T03 "新解法" 追加一个解法
  python 工具链坑.py render          重新生成 工具链坑.md
"""

import datetime
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE, "工具链坑.json")
MD_PATH = os.path.join(BASE, "工具链坑.md")


# ---------------------------------------------------------------- 数据读写
def load():
    if not os.path.exists(JSON_PATH):
        return {"items": [], "updated": datetime.date.today().isoformat()}
    with open(JSON_PATH, encoding="utf-8") as f:
        return json.load(f)


def save(db):
    db["updated"] = datetime.date.today().isoformat()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    render(db)


def today():
    return datetime.date.today().isoformat()


def next_id(db):
    """生成下一个不重复的 T 编号。

    和错题追踪器同样的考虑：不能只靠 max()，
    并发写入可能撞号，所以扫描全部取最大值再 +1。
    """
    used = set()
    for it in db.get("items", []):
        i = it.get("id", "")
        if i.startswith("T") and i[1:].isdigit():
            used.add(int(i[1:]))
    n = 0
    while True:
        n += 1
        if n not in used:
            return "T%02d" % n


# ---------------------------------------------------------------- 排序
def priority(items):
    """踩得多的排前面；次数相同则最近踩的排前面。"""
    a = sorted(items, key=lambda x: x.get("last_hit", ""), reverse=True)
    return sorted(a, key=lambda x: x.get("hits", 1), reverse=True)


# ---------------------------------------------------------------- 渲染
def render(db):
    items = db.get("items", [])
    lines = []
    lines.append("# 工具链坑清单")
    lines.append("")
    lines.append("> 记录**不是 Python、但让我卡住过**的坑：git 配置 / 网络排障 / Windows 环境 / AI 工具使用。")
    lines.append("> 目标不是「每周复习」，而是**查得到 + 不重复踩**。")
    lines.append("> 数据文件：`工具链坑.json`　|　更新：" + db.get("updated", today()))
    lines.append("")
    lines.append("**共 %d 条**" % len(items))
    lines.append("")

    if not items:
        lines.append("（暂无记录）")
    else:
        lines.append("---")
        lines.append("")
        lines.append("## 目录")
        lines.append("")
        for it in priority(items):
            lines.append("- [%s](#%s) %s" % (it["id"], it["id"].lower(), it["title"]))
        lines.append("")
        lines.append("---")
        lines.append("")

        for it in priority(items):
            lines.append('<a id="%s"></a>' % it["id"].lower())
            lines.append("")
            lines.append("## %s · %s" % (it["id"], it["title"]))
            lines.append("")
            lines.append("| 项 | 内容 |")
            lines.append("|---|---|")
            lines.append("| 踩过次数 | **%d** |" % it.get("hits", 1))
            lines.append("| 标签 | %s |" % ("、".join(it.get("tags", [])) or "—"))
            lines.append("| 第一次 | %s |" % it.get("first_hit", "—"))
            lines.append("| 最近一次 | %s |" % it.get("last_hit", "—"))
            lines.append("")
            lines.append("**症状（当时看到什么）**")
            lines.append("")
            lines.append("```text")
            lines.append(it.get("symptom", "—"))
            lines.append("```")
            lines.append("")
            lines.append("**原因（为什么会这样）**")
            lines.append("")
            lines.append(it.get("cause", "—"))
            lines.append("")
            lines.append("**解法（怎么解决）**")
            lines.append("")
            for s in it.get("solutions", []):
                lines.append("- " + s)
            lines.append("")
            if it.get("note"):
                lines.append("**备注**：" + it["note"])
                lines.append("")

    with open(MD_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------- 命令
def cmd_ls(db):
    items = db.get("items", [])
    print("工具链坑清单（按踩坑次数排序）")
    print("=" * 60)
    if not items:
        print("（暂无记录）")
        return
    for it in priority(items):
        print("%-5s %d次  %s" % (it["id"], it.get("hits", 1), it["title"]))
        print("      标签: %s" % ("、".join(it.get("tags", [])) or "—"))
    print("=" * 60)
    print("共 %d 条" % len(items))


def cmd_stats(db):
    items = db.get("items", [])
    print("工具链坑统计（更新于 %s）" % db.get("updated", today()))
    print("-" * 50)
    print("总条目数        : %d" % len(items))
    print("累计踩坑次数    : %d" % sum(i.get("hits", 1) for i in items))
    if items:
        top = priority(items)
        print()
        print("最隐蔽的坑 TOP:")
        for it in top[:5]:
            print("  %s 犯 %d 次 —— %s" % (it["id"], it.get("hits", 1), it["title"]))
    # 按标签统计
    tag_count = {}
    for it in items:
        for t in it.get("tags", []):
            tag_count[t] = tag_count.get(t, 0) + 1
    if tag_count:
        print()
        print("按标签:")
        for t, c in sorted(tag_count.items(), key=lambda x: -x[1]):
            print("  %-10s %d 条" % (t, c))


def cmd_show(db, tid):
    for it in db.get("items", []):
        if it["id"].lower() == tid.lower():
            print("=" * 60)
            print("%s · %s" % (it["id"], it["title"]))
            print("踩过 %d 次 | %s | 最近 %s" % (
                it.get("hits", 1),
                "、".join(it.get("tags", [])) or "无标签",
                it.get("last_hit", "—")))
            print("=" * 60)
            print()
            print("【症状】")
            print(it.get("symptom", "—"))
            print()
            print("【原因】")
            print(it.get("cause", "—"))
            print()
            print("【解法】")
            for s in it.get("solutions", []):
                print("  - " + s)
            if it.get("note"):
                print()
                print("【备注】" + it["note"])
            return
    print("没找到 %s" % tid)


def cmd_add(db, title, symptom, cause, solution, tags):
    item = {
        "id": next_id(db),
        "title": title,
        "symptom": symptom,
        "cause": cause,
        "solutions": [solution],
        "tags": [t.strip() for t in tags.split(",") if t.strip()],
        "hits": 1,
        "first_hit": today(),
        "last_hit": today(),
    }
    db.setdefault("items", []).append(item)
    save(db)
    print("已添加 %s · %s" % (item["id"], title))


def cmd_hit(db, tid, note):
    for it in db.get("items", []):
        if it["id"].lower() == tid.lower():
            it["hits"] = it.get("hits", 1) + 1
            it["last_hit"] = today()
            if note:
                it["note"] = (it.get("note", "") + " | " + note).strip(" |")
            save(db)
            print("%s 又踩了一次，次数 %d" % (it["id"], it["hits"]))
            return
    print("没找到 %s" % tid)


def cmd_fix(db, tid, solution):
    for it in db.get("items", []):
        if it["id"].lower() == tid.lower():
            it.setdefault("solutions", []).append(solution)
            save(db)
            print("%s 已追加解法（共 %d 条）" % (it["id"], len(it["solutions"])))
            return
    print("没找到 %s" % tid)


def cmd_render(db):
    render(db)
    print("已重新生成 %s" % MD_PATH)


# ---------------------------------------------------------------- 入口
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    db = load()
    cmd = sys.argv[1]

    if cmd == "ls":
        cmd_ls(db)
    elif cmd == "stats":
        cmd_stats(db)
    elif cmd == "show" and len(sys.argv) >= 3:
        cmd_show(db, sys.argv[2])
    elif cmd == "add" and len(sys.argv) >= 6:
        cmd_add(db, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5],
                sys.argv[6] if len(sys.argv) >= 7 else "")
    elif cmd == "hit" and len(sys.argv) >= 3:
        cmd_hit(db, sys.argv[2], sys.argv[3] if len(sys.argv) >= 4 else "")
    elif cmd == "fix" and len(sys.argv) >= 4:
        cmd_fix(db, sys.argv[2], sys.argv[3])
    elif cmd == "render":
        cmd_render(db)
    else:
        print(__doc__)
        print("命令拼错了。可用：ls / stats / show / add / hit / fix / render")


if __name__ == "__main__":
    main()
