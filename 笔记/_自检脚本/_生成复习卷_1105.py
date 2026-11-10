"""生成 2026-11-05（周四）的周四大复习卷文件（答案剥离版）。

基于 _生成复习卷_1029.py，改了三处（都是 2026-11-01 目录重组 + 10-29 教训带来的）：

1. **路径全变了**（2026-11-01 目录重组）：
   错题追踪器从 `笔记/错题追踪器.py` 升为第 4 个作品 → `projects/error-tracker/错题追踪器.py`
   复习卷从 `笔记/` 根下 → `笔记/复习卷/`
   工具链坑从 `笔记/` 根下 → `笔记/工具链/`
   ⚠️ 这次如果照抄 10-29 的老路径，脚本会直接 FileNotFoundError。

2. **加练区规则升级**（10-29 的老规则不够用）：
   老规则 = 「今天登记、但没进主区」→ 只兜住当天登记的。
   本周实际登记了 E29(11-01) / E30(11-03) / E31(11-03) / E32(11-04) / E33(11-04)，
   其中 E29/E30/E31 **一次都没被任何一卷考过** —— 这正是 10-29 那条
   「自我饿死」教训的变体：只按「今天」兜底，隔天登记的照样饿死。
   新规则 = 「最近 7 天新登记 + 还在池里 + **从来没被真正练过**(pass/fail 次数=0)
   + 没进主区」→ 兜住 E29/E30/E31 这 3 条。
   仍然只取 `bad` 字段，答案永远不进卷子。

3. **plan 题数 6 → 5**（按本周任务要求）。

三条硬规则（沿用 10-29）：
1. **答案绝不进卷子** —— 只用 JSON 里的 `bad` 字段，`good`（应该怎么写）只留在答案卷。
2. **题目顺序以 `plan 5` 的输出为准** —— 追踪器怎么排这里就怎么排，不另搞一套优先级。
3. **必须带最近一周的新错题** —— 追踪器默认留 2 个坑位给新错，否则新错永远排在高频题后面抽不到。
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject")
BASE = ROOT / "笔记"
TRACKER = ROOT / "projects" / "error-tracker" / "错题追踪器.py"
JSON_PATH = ROOT / "projects" / "error-tracker" / "错题追踪.json"
OUT = BASE / "复习卷" / "周四大复习_2026-11-05_复习卷.md"
PY = r"D:\AAAA\python.exe"
TODAY = "2026-11-05"
CUTOFF = "2026-10-29"          # 今天往前 7 天

Q_RE = re.compile(r"^第 (\d+) 题\s+(E\d+)\s+(.*)$", re.M)

HEAD = """# 周四大复习 · 复习卷 · 2026-11-05（周四）

> **本卷共 {n} 题**：第一部分 {n_core} 题是「必考区」（犯过 ≥2 次的高频顽固题），
> 第二部分 {n_new} 题是「本周新错区」（最近 7 天你亲手登记的新错），
> 附加 {n_extra} 题是「本周新错加练」（这周登记、但新错区只留了 {n_new} 个坑位，
> 而且**一次都还没被考过**的几条 —— 不能因为「没抽到」就不考）。
>
> **答案不在这个文件里。** 写完一整份再对照讲解：
> `周四大复习_2026-11-05_答案与讲解.md`（等你交卷后我单独生成，现在还没写）。

## 作答规则

1. **先别翻答案**。每题只看 ❌ 那段代码，自己说出哪里错、自己改写。
2. 写不出来就写"不会" —— 那也是有用的信息，别空着蒙。
3. **建议每题 10 分钟**；卡住的题标个记号先跳，最后回头攻。
4. **做完整份再 record**（不要一题一题提前记）：

```
cd "D:\\AI应用工程师\\01-学习仓库-Python学习路径\\pythonProject\\projects\\error-tracker"
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> pass "你的理解"
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> fail "又错在哪"
```

5. 全卷做完后收尾：

```
"D:\\AAAA\\python.exe" 错题追踪器.py render   # 重新生成错题追踪.md
"D:\\AAAA\\python.exe" 错题追踪器.py stats    # 看池子还剩几题
```

| 题号 | ID | 考点 | 犯过几次 | 连对 | 区 |
|---|---|---|---|---|---|
{table}

> 答错不丢人，答错不记才丢人。
> 第一部分那几题是**你反复犯过的**（E15 犯了 6 次、E02 5 次、E05 3 次）——
> 这三题是整个池子的"顶流"，错了要当场改对。
> 后两部分那几题是**你这周刚犯的** —— 趁热打铁比放到下个月便宜得多。
> 附加那几题是**这周登记但一次都没被考过**的，做的时候要能说出
> 「我当时为什么会这么写」。

---

"""

TAIL = """
---

# 📌 最后一件事：这周写新代码时，有没有遇到清单里没记的错误？

哪怕是很小的、当时自己绕过去了的错误，都告诉我 —— 我当场登记进错题池，下卷必考。
**当天不登记 = 白踩。**

**我的新错误：**

```
```

（没有就写"这周没新的"。）

---

# 🔧 顺手记一个：周四复习时又卡在同一个地方？

如果是**工具链/环境**层面的坑（git 推不上去、编码乱码、路径找不到、
窗口一闪就没、目录被改没了……），顺手记一笔：

```
cd "D:\\AI应用工程师\\01-学习仓库-Python学习路径\\pythonProject\\笔记\\工具链"
"D:\\AAAA\\python.exe" 工具链坑.py hit Txx "这次的实际情况"
```

次数会涨，它会自动排到清单最前面 —— 下次撞上同一个坑，你就能第一时间想起来。
"""


def _answered(it):
    """真正练过几次（pass/fail 才算，pending 不算 —— 发出去了但没作答 = 没练过）。"""
    return len([h for h in it.get("history", []) if h.get("result") in ("pass", "fail")])


def _q_block(idx, it, zone=""):
    """一题：题目 + 涉及标签 + ❌错在这 + 留白作答区。**不含答案。**

    为什么这里【绝对不能出现答案标记】：
        这份文件是给你做的卷子，你要在上面自己写。
        如果答案在同一页，你眼睛一扫就看到了，等于没做。
        所以答案只从 JSON 的 good 字段取，放进另一个文件
        （答案与讲解.md），交卷后才给。
    """
    tags = " / ".join(it.get("tags", [])) or "—"
    occ = it.get("occurrences", 0)
    L = []
    L.append("## 第 %d 题（%s）· %s" % (idx, it["id"], it["title"]))
    L.append("")
    L.append("**涉及标签**：%s　｜　**犯过 %d 次**　｜　**连对 %d/%d**%s"
             % (tags, occ, it.get("streak", 0), it.get("need", 2),
                ("　｜　**%s**" % zone) if zone else ""))
    L.append("")
    L.append("```python")
    L.append(it.get("bad", "").rstrip())
    L.append("```")
    L.append("")
    L.append("### 你要做的")
    L.append("")
    L.append("1. 这段代码错在哪？逐行指出来（一句话就行）")
    L.append("2. 把它改写成正确版本")
    L.append("3. 说说：改完之后，凭什么就「跑得对」了？（原来为什么没报错）")
    L.append("")
    L.append("**你的作答：**")
    L.append("")
    L.append("```")
    L.append("①")
    L.append("")
    L.append("②")
    L.append("")
    L.append("改写后的代码：")
    L.append("")
    L.append("")
    L.append("③")
    L.append("```")
    L.append("")
    L.append("---")
    L.append("")
    return "\n".join(L)


def main():
    """跑追踪器拿题目顺序 → 从 JSON 取详情 → 拼 Markdown → 写文件。"""
    r = subprocess.run(
        [PY, str(TRACKER), "plan", "5"],
        capture_output=True, text=True, encoding="utf-8",
    )
    if r.returncode != 0:
        raise SystemExit("plan 失败：" + r.stderr)

    # 1) 题目顺序：以 plan 输出为准
    order = [(int(m.group(1)), m.group(2)) for m in Q_RE.finditer(r.stdout)]
    if not order:
        raise SystemExit("plan 没有输出题目，检查一下：\n" + r.stdout[:400])

    # 2) 详情从 JSON 取
    db = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_id = {it["id"]: it for it in db["items"]}

    # 3) 切分必考区 / 新错区
    second_idx = r.stdout.find("【第二部分")
    if second_idx == -1:
        n_core, n_new = len(order), 0
    else:
        n_core = len([m for m in Q_RE.finditer(r.stdout[:second_idx])])
        n_new = len(order) - n_core

    # 3b) 加练区 = 最近 7 天新登记 + 还在池里 + 从没被真正练过 + 没进主区
    used = {pid for _, pid in order}
    extra_ids = [it["id"] for it in db["items"]
                 if it["status"] == "active"
                 and it.get("first_seen", "") >= CUTOFF
                 and _answered(it) == 0
                 and it["id"] not in used]

    zones = {}
    for idx, pid in order:
        zones[pid] = "必考区" if idx <= n_core else "本周新错区"

    rows = []
    for idx, pid in order:
        it = by_id[pid]
        rows.append("| %d | %s | %s | %d | %d/%d | %s |"
                    % (idx, pid, it["title"].replace("|", "/"), it.get("occurrences", 0),
                       it.get("streak", 0), it.get("need", 2), zones[pid]))
    for i, pid in enumerate(extra_ids):
        idx = len(order) + i + 1
        it = by_id[pid]
        zones[pid] = "本周新错加练"
        rows.append("| %d | %s | %s | %d | %d/%d | %s |"
                    % (idx, pid, it["title"].replace("|", "/"), it.get("occurrences", 0),
                       it.get("streak", 0), it.get("need", 2), zones[pid]))
    table = "\n".join(rows)

    body = []
    for idx, pid in order:
        body.append(_q_block(idx, by_id[pid], zones[pid]))
    for i, pid in enumerate(extra_ids):
        body.append(_q_block(len(order) + i + 1, by_id[pid], zones[pid]))

    text = HEAD.format(n=len(order) + len(extra_ids), n_core=n_core,
                       n_new=n_new, n_extra=len(extra_ids), table=table)
    text += "\n".join(body)
    text += TAIL

    # 4) 自检：卷子里绝不能出现答案标记
    assert "✅ 应该" not in text, "答案泄漏进卷子了！"
    assert "✅ 正确写法" not in text, "答案泄漏进卷子了！"
    assert "✅" not in text, "卷子里出现了答案标记！"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("已保存：" + str(OUT))
    print("题数：%d（必考区 %d + 本周新错区 %d + 本周新错加练 %d）"
          % (len(order) + len(extra_ids), n_core, n_new, len(extra_ids)))
    print("大小：" + str(OUT.stat().st_size) + " 字节")
    print("题目：" + " ".join(pid for _, pid in order)
          + (" | 加练 " + " ".join(extra_ids) if extra_ids else ""))


if __name__ == "__main__":
    main()
