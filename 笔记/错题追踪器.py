# -*- coding: utf-8 -*-
"""
错题追踪器 —— 支撑「每周四复习同一个问题，直到它不再出现」

设计要点
--------
1. 每条错题有 occurrences（累计犯过几次）。犯得越多，复习时优先级越高。
2. 连续答对 streak 次才算「已掌握」，从复习池里退场（不再占用每周时间）。
3. 已掌握的问题一旦再犯 → regress → 重新进池，而且通关门槛 +1（上限 4）。
   越容易反复，收得越严 —— 这是「直到不再出现为止」的机制。

命令
----
  python 错题追踪器.py ls                列出待复习清单（按优先级排序）
  python 错题追踪器.py stats             统计概览
  python 错题追踪器.py plan 5            生成本周复习卷（含错/对代码对照）
  python 错题追踪器.py plan 5            默认：固定留 2 个坑位给「本周新错」
  python 错题追踪器.py plan 5 --no-new   关掉新错区，只考老题（总题数不变）
  python 错题追踪器.py show E01          看某题详情
  python 错题追踪器.py add "标题" "错误写法" "正确写法" "标签1,标签2"
  python 错题追踪器.py record E01 pass|fail ["备注"]
  python 错题追踪器.py regress E01       已掌握的题又出现了 → 重新激活
  python 错题追踪器.py render            重新生成 错题追踪.md
"""

import datetime
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE, "错题追踪.json")
MD_PATH = os.path.join(BASE, "错题追踪.md")

REVIEW_LIKE = ["复习", "复盘", "补强", "巩固", "练习", "改错", "改 bug", "找错", "查漏"]
REVIEW_TITLE = "周四大复习：错题重练 + 查漏补缺（2h）"


# ---------------------------------------------------------------- 数据读写
def load():
    with open(JSON_PATH, encoding="utf-8") as f:
        db = json.load(f)
    if "skills" not in db:
        db["skills"] = []
    return db


def save(db):
    db["updated"] = datetime.date.today().isoformat()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    render(db)


def today():
    return datetime.date.today().isoformat()


def next_id(db):
    """生成下一个不重复的 ID。

    注意：不能只靠 max()，因为并发写入（比如自动化任务和我同时登记）
    可能导致同号。这里扫描全部 E 数字取最大值，并额外检查候选号是否已被占用。
    """
    used = set()
    for it in db["items"]:
        i = it.get("id", "")
        if i.startswith("E") and i[1:].isdigit():
            used.add(int(i[1:]))
    n = 0
    while True:
        n += 1
        if n not in used:
            return "E%02d" % n


# ---------------------------------------------------------------- 核心逻辑
def priority(items):
    """出现次数多的优先；次数相同则最近犯的优先。"""
    a = sorted(items, key=lambda x: x["last_seen"], reverse=True)
    return sorted(a, key=lambda x: x["occurrences"], reverse=True)


def active_items(db):
    return [it for it in db["items"] if it["status"] == "active"]


def mastered_items(db):
    return [it for it in db["items"] if it["status"] == "mastered"]


def need_of(it):
    return it.get("need", 2)


def find(db, pid):
    for it in db["items"]:
        if it["id"] == pid:
            return it
    return None


def cmd_ls(db):
    items = priority(active_items(db))
    if not items:
        print("复习池是空的 —— 全都掌握了。可以去加新问题了。")
        return
    print("待复习清单（按优先级）\n" + "=" * 60)
    for it in items:
        tag = "【高频】" if it["occurrences"] >= 2 else ""
        print("%-5s %s %s" % (it["id"], tag, it["title"]))
        print("      犯过 %d 次 | 首犯 %s | 最近 %s | 连对 %d/%d"
              % (it["occurrences"], it["first_seen"], it["last_seen"],
                 it.get("streak", 0), need_of(it)))
    print("\n共 %d 题在池子里。" % len(items))


def cmd_stats(db):
    act = active_items(db)
    mas = mastered_items(db)
    high = [it for it in act if it["occurrences"] >= 2]
    print("错题追踪器 统计（更新于 %s）" % db.get("updated", "?"))
    print("-" * 46)
    print("在池子里（每周必考） : %d" % len(act))
    print("  其中高频（≥2次）    : %d" % len(high))
    print("已掌握（已退场）      : %d" % len(mas))
    print("历史累计错题          : %d" % len(db["items"]))
    tot = sum(it["occurrences"] for it in db["items"])
    print("累计犯错次数          : %d" % tot)
    if high:
        print("\n顽固问题 TOP:")
        for it in sorted(high, key=lambda x: -x["occurrences"])[:5]:
            print("  %s 犯 %d 次 —— %s" % (it["id"], it["occurrences"], it["title"]))


def cmd_show(db, pid):
    it = find(db, pid)
    if not it:
        print("找不到 %s" % pid)
        return
    print("=" * 60)
    print("%s  %s" % (it["id"], it["title"]))
    print("状态: %s | 犯过 %d 次 | 首犯 %s | 最近 %s | 连对 %d/%d"
          % (it["status"], it["occurrences"], it["first_seen"], it["last_seen"],
             it.get("streak", 0), need_of(it)))
    print("标签: %s" % ", ".join(it.get("tags", [])))
    print("\n❌ 错误写法:\n%s" % it.get("bad", ""))
    print("\n✅ 正确写法:\n%s" % it.get("good", ""))
    print("\n出处: %s" % ", ".join(it.get("source", [])))
    if it.get("history"):
        print("\n复习流水:")
        for h in it["history"]:
            print("  %s  %-4s %s" % (h["date"], h["result"], h.get("note", "")))


def cmd_add(db, title, bad, good, tags):
    it = {
        "id": next_id(db),
        "title": title,
        "bad": bad,
        "good": good,
        "tags": [t.strip() for t in tags.split(",") if t.strip()] if tags else [],
        "occurrences": 1,
        "first_seen": today(),
        "last_seen": today(),
        "streak": 0,
        "need": 2,
        "status": "active",
        "source": [],
        "history": [{"date": today(), "result": "new", "note": "首次登记"}],
    }
    db["items"].append(it)
    print("已登记 %s：%s" % (it["id"], it["title"]))
    print("→ 已进入复习池，会在每周四被抽到。")


def cmd_record(db, pid, result, note=""):
    it = find(db, pid)
    if not it:
        print("找不到 %s" % pid)
        return
    d = today()
    if result == "pass":
        it["streak"] = it.get("streak", 0) + 1
        it["history"].append({"date": d, "result": "pass", "note": note})
        if it["streak"] >= need_of(it):
            it["status"] = "mastered"
            it["mastered_on"] = d
            print("✅ %s 连续答对 %d 次 → 已掌握，退出复习池。" % (it["id"], it["streak"]))
            print("   （如果以后再犯，会自动重新激活，而且门槛会更高）")
        else:
            print("✅ %s 答对（连对 %d/%d），下次复习继续考。" % (it["id"], it["streak"], need_of(it)))
    else:
        it["streak"] = 0
        it["occurrences"] += 1
        it["last_seen"] = d
        if it["status"] == "mastered":
            it["status"] = "active"
            it["need"] = min(4, need_of(it) + 1)
            it.pop("mastered_on", None)
            print("🔴 %s 又犯了！重新进池，通关门槛提高到 %d 次。" % (it["id"], it["need"]))
        else:
            print("🔴 %s 又犯了。连续答对清零（仍需连对 %d 次）。" % (it["id"], need_of(it)))
        it["history"].append({"date": d, "result": "fail", "note": note})
        print("   → 下周四必考，且会排在高频区。")


def cmd_regress(db, pid, note=""):
    it = find(db, pid)
    if not it:
        print("找不到 %s" % pid)
        return
    it["status"] = "active"
    it["streak"] = 0
    it["occurrences"] += 1
    it["last_seen"] = today()
    it["need"] = min(4, need_of(it) + 1)
    it.pop("mastered_on", None)
    it["history"].append({"date": today(), "result": "fail", "note": note or "日常练习中再次出现"})
    print("🔴 %s 已掌握但又出现 → 重新激活，门槛升到 %d 次。" % (it["id"], it["need"]))


def cmd_add_skill(db, title, source):
    skills = db.setdefault("skills", [])
    n = 0
    for sk in skills:
        if sk["id"].startswith("S") and sk["id"][1:].isdigit():
            n = max(n, int(sk["id"][1:]))
    sk = {
        "id": "S%02d" % (n + 1),
        "title": title,
        "from_jd": source,
        "priority": "high",
        "status": "todo",
        "notes": "",
        "created": today(),
    }
    skills.append(sk)
    print("已登记能力缺口 %s：%s" % (sk["id"], title))
    if source:
        print("   来源: %s" % source)


def cmd_skills(db):
    skills = db.get("skills", [])
    if not skills:
        print("还没有登记能力缺口。")
        print("用法: 错题追踪器.py skill \"FastAPI 写 GET 接口\" \"某某JD\"")
        return
    print("能力缺口清单（从 JD 里读出来的、你还不会的）")
    print("=" * 60)
    todo = [s for s in skills if s.get("status") != "done"]
    done = [s for s in skills if s.get("status") == "done"]
    for sk in todo:
        print("  %-5s %s" % (sk["id"], sk["title"]))
        if sk.get("from_jd"):
            print("        来源: %s" % sk["from_jd"])
    if done:
        print("\n已完成:")
        for sk in done:
            print("  %-5s [已会] %s" % (sk["id"], sk["title"]))
    print("\n共 %d 项待补，%d 项已会" % (len(todo), len(done)))


def _print_q(idx, it):
    tag = "【高频 %d 次】" % it["occurrences"] if it["occurrences"] >= 2 else ""
    print("\n第 %d 题  %s  %s%s" % (idx, it["id"], it["title"], tag))
    print("  涉及: %s" % ", ".join(it.get("tags", [])))
    print("  ❌ 错在这:\n%s" % _indent(it.get("bad", "")))
    print("  ✅ 应该:\n%s" % _indent(it.get("good", "")))
    print("  " + "-" * 56)
    print("  ✍️ 先自己写一遍再对答案")


def _recent_new(db, days=7):
    """最近 N 天「新登记」的错题（first_seen 落在窗口内），按新近倒序。

    为什么必须单独开一段：
      priority() 只按 occurrences 排序，而新错 occurrences 一律 = 1。
      只要池里还有犯过 ≥2 次的题，plan N 就永远抽不到这些新错 ——
      它们会一直排在队列尾巴上，直到别的题先毕业为止。
      新错不趁热复习，等它攒到 2 次时反而更贵（同一个错误重复得更快）。
    """
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    items = [it for it in db["items"]
             if it["status"] == "active" and it.get("first_seen", "") >= cutoff]
    items.sort(key=lambda x: (x.get("first_seen", ""), x.get("last_seen", "")),
               reverse=True)
    return items


def cmd_plan(db, n, with_new=True, new_days=7, new_cap=2):
    """生成复习卷。

    取题规则（2026-10-29 改）：
      ① 先给「最近 new_days 天新登记的错题」留 new_cap 个坑位
      ② 剩下的名额按老规则（犯过次数多的优先）填
      ③ **总题数恒为 n**（不够就少几题，绝不超）

    为什么改（2026-10-29 发现的自我饿死循环）：
      老规则只按 occurrences 排序，而新错 occurrences 一律 = 1。
      池里只要还有犯过 ≥2 次的题，plan N 就永远抽不到新错 ——
      新错排最后 → 进不了卷 → 没人复习 → 次数不涨 → 永远排最后。
      今晚实测：池里 27 题，plan 6 全被 10-21~10-28 的老高频题占满，
      当天亲手犯的 E24~E28 一道没进卷。
      所以必须**用坑位强制留出**，不能指望它靠排序挤进去。
    """
    all_items = priority(active_items(db))

    # ---- 第一步：新错区（占坑位）----
    # 注意 min(new_cap, n)：n 比坑位数还小时（plan 1 / plan 0），
    # 新错区也得跟着收缩，否则总数会超过 n（plan 1 会出 2 题）。
    new_items, dropped = [], 0
    if with_new and n > 0:
        cand = _recent_new(db, new_days)
        new_items = cand[:min(new_cap, n)]
        dropped = len(cand) - len(new_items)

    # ---- 第二步：老规则区（排除已被新错区占用的，剩下的名额填这里）----
    new_ids = {it["id"] for it in new_items}
    core = [it for it in all_items if it["id"] not in new_ids][: max(0, n - len(new_items))]

    if not core and not new_items:
        print("复习池是空的。")
        return
    print("=" * 62)
    print("周四大复习 · 复习卷（%d 题）" % (len(core) + len(new_items)))
    print("=" * 62)
    if core:
        print("【第一部分 · 必考区】按犯过次数排的老题（%d 题）" % len(core))
        for i, it in enumerate(core, 1):
            _print_q(i, it)
    if new_items:
        print()
        print("【第二部分 · 本周新错区】最近 %d 天新登记的错，一周内必须过一遍（%d 题）"
              % (new_days, len(new_items)))
        for i, it in enumerate(new_items, len(core) + 1):
            _print_q(i, it)
        if dropped:
            print("  （本周新登记 %d 条，本卷收录 %d 条，其余 %d 条排在下一卷）"
                  % (len(new_items) + dropped, len(new_items), dropped))
    print("\n" + "=" * 62)
    print("答完用：python 错题追踪器.py record <ID> pass|fail")


def _indent(s):
    return "\n".join("    " + ln for ln in s.splitlines()) if s else "    （无）"


# ---------------------------------------------------------------- Markdown
def render(db):
    act = priority(active_items(db))
    mas = mastered_items(db)
    high = [it for it in act if it["occurrences"] >= 2]
    L = []
    A = L.append
    A("# 错题追踪清单（每周四复习池）")
    A("")
    A("> 更新于 %s ｜ 在池 %d ｜ 其中高频 %d ｜ 已掌握 %d"
      % (db.get("updated", "?"), len(act), len(high), len(mas)))
    A(">")
    A("> **规则**：犯过的错进池 → 每周四必考 → 连续答对 %d 次才算掌握、退场" % 2)
    A("> → 掌握后再犯，立刻重新激活且门槛 +1。**同一问题会一直考到它真的不再出现。**")
    A("")
    A("---")
    A("")
    A("## 🔴 高频问题（犯过 ≥2 次，每周四优先考）")
    A("")
    if high:
        A("| ID | 问题 | 犯过 | 首犯 | 最近 | 连对/门槛 | 标签 |")
        A("|---|---|---|---|---|---|---|")
        for it in high:
            A("| %s | %s | %d | %s | %s | %d/%d | %s |"
              % (it["id"], it["title"], it["occurrences"], it["first_seen"],
                 it["last_seen"], it.get("streak", 0), need_of(it),
                 ", ".join(it.get("tags", []))))
    else:
        A("（暂无）")
    A("")
    A("## 🟡 一次性问题（也每周考，但排在高频后面）")
    A("")
    once = [it for it in act if it["occurrences"] < 2]
    if once:
        A("| ID | 问题 | 犯过 | 首犯 | 最近 | 标签 |")
        A("|---|---|---|---|---|---|")
        for it in once:
            A("| %s | %s | %d | %s | %s | %s |"
              % (it["id"], it["title"], it["occurrences"], it["first_seen"],
                 it["last_seen"], ", ".join(it.get("tags", []))))
    else:
        A("（暂无）")
    A("")
    A("## ✅ 已掌握（已退场，再犯会被抓回来）")
    A("")
    if mas:
        A("| ID | 问题 | 犯过 | 掌握于 | 标签 |")
        A("|---|---|---|---|---|")
        for it in mas:
            A("| %s | %s | %d | %s | %s |"
              % (it["id"], it["title"], it["occurrences"],
                 it.get("mastered_on", "?"), ", ".join(it.get("tags", []))))
    else:
        A("（暂无）")
    A("")
    A("---")
    A("")
    A("## 📋 全部错题详录（错/对代码对照）")
    A("")
    for it in db["items"]:
        A("### %s %s" % (it["id"], it["title"]))
        A("")
        A("- **状态**：%s ｜ **犯过 %d 次** ｜ 首犯 %s ｜ 最近 %s ｜ 连对 %d/%d"
          % (it["status"], it["occurrences"], it["first_seen"], it["last_seen"],
             it.get("streak", 0), need_of(it)))
        if it.get("source"):
            A("- **出处**：%s" % ", ".join(it["source"]))
        if it.get("tags"):
            A("- **标签**：%s" % ", ".join(it["tags"]))
        A("")
        A("```python")
        A("# ❌ " + it["title"])
        A(it.get("bad", ""))
        A("```")
        A("")
        A("```python")
        A("# ✅ 正确写法")
        A(it.get("good", ""))
        A("```")
        A("")
        if it.get("history"):
            A("复习流水：")
            A("")
            for h in it["history"]:
                mark = {"pass": "✅ 对", "fail": "🔴 错", "new": "＋ 新",
                        "pending": "📝 待答", "explain": "📖 讲解"}.get(h["result"], h["result"])
                A("- %s %s%s" % (h["date"], mark, ("　" + h["note"]) if h.get("note") else ""))
            A("")
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------- CLI
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    db = load()
    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd in ("ls", "list"):
        cmd_ls(db)
    elif cmd == "stats":
        cmd_stats(db)
    elif cmd == "plan":
        flags = [a for a in args if a.startswith("--")]
        nums = [a for a in args if not a.startswith("--")]
        n = int(nums[0]) if nums else 5
        # 默认就带「本周新错区」；--no-new 可以关掉，--new 保留是为了兼容旧习惯
        with_new = "--no-new" not in flags
        cmd_plan(db, n, with_new=with_new)
    elif cmd == "show":
        cmd_show(db, args[0])
    elif cmd == "add":
        if len(args) < 3:
            print('用法: add "标题" "错误写法" "正确写法" "标签1,标签2"')
            return
        cmd_add(db, args[0], args[1], args[2], args[3] if len(args) > 3 else "")
        save(db)
    elif cmd == "record":
        if len(args) < 2:
            print("用法: record <ID> pass|fail [备注]")
            return
        cmd_record(db, args[0], args[1], args[2] if len(args) > 2 else "")
        save(db)
    elif cmd == "pending":
        # 复习卷已出、用户还没作答时记一笔 —— 不动 streak，不虚报
        if len(args) < 2:
            print("用法: pending <ID> [备注]")
            return
        it = find(db, args[0])
        if not it:
            print("找不到 %s" % args[0])
            return
        it["history"].append({"date": today(), "result": "pending",
                              "note": args[1] if len(args) > 1 else "复习卷已出，待作答"})
        print("📝 %s 已记为待答（连对计数保持 %d/%d，不虚报）"
              % (it["id"], it.get("streak", 0), need_of(it)))
        save(db)
    elif cmd == "regress":
        cmd_regress(db, args[0], args[1] if len(args) > 1 else "")
        save(db)
    elif cmd == "skill":
        if len(args) < 1:
            print("用法: skill \"能力缺口标题\" [来源JD]")
            return
        cmd_add_skill(db, args[0], args[1] if len(args) > 1 else "")
        save(db)
    elif cmd == "skills":
        cmd_skills(db)
    elif cmd == "render":
        render(db)
        print("已重新生成 %s" % MD_PATH)
    else:
        print("未知命令: %s（用无参数运行看帮助）" % cmd)


if __name__ == "__main__":
    main()
