"""生成 2026-10-29 的周四大复习卷文件（答案剥离版）。

三条硬规则：
1. **答案绝不进卷子** —— 卷子只用 JSON 里的 `bad` 字段，
   `good`（✅ 应该怎么写）只留在答案卷，结构上杜绝剧透。
2. **题目顺序以 `plan 6` 的输出为准** —— 追踪器怎么排，这里就怎么排，
   不自己另搞一套优先级。
3. **必须带最近一周的新错题** —— 追踪器 2026-10-29 起默认就留 2 个坑位
   给新错（`plan N` 不用再加 --new），否则新错（occurrences=1）
   永远排在高频题后面抽不到。

为什么用脚本而不是命令行内联：
  Markdown 里的 ``` 会被 bash 吃掉（命令替换 + 重定向），写进脚本文件就没这问题。
"""
import io
import json
import re
import subprocess
from pathlib import Path

BASE = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")
PY = r"D:\AAAA\python.exe"
TRACKER = BASE / "错题追踪器.py"
JSON_PATH = BASE / "错题追踪.json"
OUT = BASE / "周四大复习_2026-10-29_复习卷.md"

Q_RE = re.compile(r"^第 (\d+) 题\s+(E\d+)\s+(.*)$", re.M)

HEAD = """# 周四大复习 · 复习卷 · 2026-10-29（周四）

> **本卷共 {n} 题**：第一部分 {n_core} 题是「必考区」（犯过 ≥2 次的高频顽固题），
> 第二部分 {n_new} 题是「本周新错区」（最近 7 天你亲手登记的新错）。
>
> **答案不在这个文件里。** 写完一整份再对照讲解：
> `周四大复习_2026-10-29_答案与讲解.md`（等你交卷后我单独生成，现在还没写）。

## 作答规则

1. **先别翻答案**。每题只看 ❌ 那段代码，自己说出哪里错、自己改写。
2. 写不出来就写"不会" —— 那也是有用的信息，别空着蒙。
3. **建议每题 10 分钟**；卡住的题标个记号先跳，最后回头攻。
4. **做完整份再 record**（不要一题一题提前记）：

```
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> pass "你的理解"
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> fail "又错在哪"
```

5. 全卷做完后收尾：

```
"D:\\AAAA\\python.exe" 错题追踪器.py render   # 重新生成错题追踪.md
"D:\\AAAA\\python.exe" 错题追踪器.py stats    # 看池子还剩几题
```

| 题号 | ID | 考点 | 犯过几次 | 区 |
|---|---|---|---|---|
{table}

> 答错不丢人，答错不记才丢人。
> 第一部分那几题是**你反复犯过的**（E15 犯了 5 次、E01/E02 各 4 次）；
> 第二部分那几题是**你这周刚犯的** —— 趁热打铁比放到下个月便宜得多。

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
"""


def _q_block(idx, it):
    """一题：题目 + 涉及标签 + ❌错在这 + 留白作答区。**不含 ✅。**"""
    tags = " / ".join(it.get("tags", [])) or "—"
    occ = it.get("occurrences", 0)
    L = []
    L.append("## 第 %d 题（%s）· %s" % (idx, it["id"], it["title"]))
    L.append("")
    L.append("**涉及标签**：%s　｜　**犯过 %d 次**　｜　**连对 %d/%d**"
             % (tags, occ, it.get("streak", 0), it.get("need", 2)))
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
    r = subprocess.run(
        [PY, str(TRACKER), "plan", "6"],
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

    rows = []
    for idx, pid in order:
        it = by_id[pid]
        zone = "必考区" if idx <= n_core else "本周新错区"
        rows.append("| %d | %s | %s | %d | %s |"
                    % (idx, pid, it["title"].replace("|", "/"), it.get("occurrences", 0), zone))
    table = "\n".join(rows)

    body = []
    for idx, pid in order:
        body.append(_q_block(idx, by_id[pid]))

    text = HEAD.format(n=len(order), n_core=n_core, n_new=n_new, table=table)
    text += "\n".join(body)
    text += TAIL

    # 4) 自检：卷子里绝不能出现答案标记
    assert "✅ 应该" not in text, "答案泄漏进卷子了！"
    assert "✅ 正确写法" not in text, "答案泄漏进卷子了！"

    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("已保存：" + str(OUT))
    print("题数：%d（必考区 %d + 本周新错区 %d）" % (len(order), n_core, n_new))
    print("大小：" + str(OUT.stat().st_size) + " 字节")
    print("题目：" + " ".join(pid for _, pid in order))


if __name__ == "__main__":
    main()
