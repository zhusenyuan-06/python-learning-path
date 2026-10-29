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
TODAY = "2026-10-29"

Q_RE = re.compile(r"^第 (\d+) 题\s+(E\d+)\s+(.*)$", re.M)

HEAD = """# 周四大复习 · 复习卷 · 2026-10-29（周四）

> **本卷共 {n} 题**：第一部分 {n_core} 题是「必考区」（犯过 ≥2 次的高频顽固题），
> 第二部分 {n_new} 题是「本周新错区」（最近 7 天你亲手登记的新错），
> 附加 {n_extra} 题是「今日新错加练」（今天 10-29 登记、但新错区只留了 {n_new} 个坑位，
> 剩下的几条不能因为「没抽到」就不考）。
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
> 后两部分那几题是**你这周刚犯的** —— 趁热打铁比放到下个月便宜得多。
> 附加那几题是今天下午刚踩的，**做的时候要能说出「我当时为什么会这么写」**。

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


def _q_block(idx, it, zone=""):
    """一题：题目 + 涉及标签 + ❌错在这 + 留白作答区。**不含 ✅。**

    为什么这里【绝对不能出现 ✅】：
        这份文件是给你做的卷子，你要在上面自己写。
        如果答案在同一页，你眼睛一扫就看到了，等于没做。
        所以答案只从 JSON 的 good 字段取，放进另一个文件
        （答案与讲解.md），交卷后才给。

    逐行拆解：
        zone="" = 默认参数：调用时不给 zone 就用空字符串
          └─ 默认参数必须放在【所有普通参数后面】，所以只能加在最后

        tags = " / ".join(it.get("tags", [])) or "—"
          └─ .get("tags", []) = 取标签列表，没有就给空列表
          └─ " / ".join(列表) = 用 " / " 把列表拼成字符串
          └─ or "—" = 如果拼出来是空字符串，就换成破折号占位
            （or 的短路写法：左边为假就取右边）

        L = [] = 建一个空列表当「行缓冲区」
          └─ 为什么不直接用一个大字符串 +=？
            因为 += 反复拼大字符串效率低（每次都要复制一遍），
            列表追加再 join 更快。

        L.append("## 第 %d 题（%s）· %s" % (idx, it["id"], it["title"]))
          └─ % 格式化：%d 整数、%s 字符串
          └─ % 的老式写法（Python 3.6 以后也支持 f-string，但 % 兼容性最好）

        ("　｜　**%s**" % zone) if zone else ""
          └─ 三元表达式：zone 有值就显示区名，没有就显示空串
          └─ 注意这里用【全角空格　】分隔，跟 Markdown 里的排版配套

        "```python" / "```" = Markdown 的代码块围栏
          └─ 围栏包住的是【等宽字体】，缩进才不会乱

        it.get("bad", "").rstrip() = 取「错误写法」并去掉尾部空白
          └─ rstrip() = 只去右边空白，左边缩进保留
            （lstrip() 会把代码块的缩进干掉！）
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
    """生成复习卷文件：跑追踪器拿题目顺序 → 从 JSON 取详情 → 拼 Markdown。

    逐行拆解：
        subprocess.run([PY, str(TRACKER), "plan", "6"], ...)
          └─ 调追踪器的 plan 命令，题数 6
          └─ capture_output=True = 收下 stdout/stderr，不直接打屏
          └─ text=True + encoding="utf-8" = 输出按 UTF-8 解码成 str
          └─ 为什么不自己实现取题逻辑？因为追踪器才是唯一真源，
            这里【只做排版】，不另搞一套优先级（否则两边会打架）

        if r.returncode != 0: raise SystemExit(...)
          └─ SystemExit("消息") = 抛出一个退出异常并打印消息
          └─ 比起 print 完再 exit，好处是错误信息不会和正常输出混在一起

        order = [(int(m.group(1)), m.group(2)) for m in Q_RE.finditer(r.stdout)]
          └─ Q_RE.finditer(文本) = 用正则找到所有匹配，返回匹配对象序列
          └─ m.group(1) = 第 1 个捕获组（题号），m.group(2) = 第 2 组（题号 E15）
          └─ int(...) = 把字符串转成整数，才能排序和比较

        db = json.loads(JSON_PATH.read_text(encoding="utf-8"))
          └─ 从 JSON 取每道题的完整详情（标签、犯过几次、错误写法…）
          └─ plan 的输出只有标题，详情得来这里拿

        by_id = {it["id"]: it for it in db["items"]}
          └─ 字典推导式 = 建一个「题号 → 题目对象」的对照表
          └─ 这样 by_id["E15"] 就能直接拿到那道题，O(1) 查找

        second_idx = r.stdout.find("【第二部分")
          └─ .find(子串) = 找子串第一次出现的位置，找不到返回 -1
          └─ 用它切分「必考区」和「新错区」两段

        used = {pid for _, pid in order} = 集合推导式
        extra_ids = [...] = 今天新登记、但没进主区的题（加练区）
          └─ it.get("first_seen", "") == TODAY = 「今天登记的」
          └─ and it["id"] not in used = 且没被主区选上
          └─ 道理：新错区只有 2 个坑位，今天一口气登记 5 条，
            剩下 3 条不能因为「没抽到」就不考 —— 今天犯的错今晚放过 = 白踩

        return "\n".join(L)
          └─ 把行列表拼成完整文本；join(列表) 里列表是字符串列表
    """
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

    # 3b) 加练区 = 今天新登记、但没进主区的错题
    #     新错区只留 2 个坑位，今天一登记就是 5 条 —— 剩下的不能因为
    #     「没抽到」就不考，那等于今天犯的错今晚放过。
    used = {pid for _, pid in order}
    extra_ids = [it["id"] for it in db["items"]
                 if it["status"] == "active"
                 and it.get("first_seen", "") == TODAY
                 and it["id"] not in used]

    zones = {}
    for idx, pid in order:
        zones[pid] = "必考区" if idx <= n_core else "本周新错区"

    rows = []
    for idx, pid in order:
        it = by_id[pid]
        rows.append("| %d | %s | %s | %d | %s |"
                    % (idx, pid, it["title"].replace("|", "/"), it.get("occurrences", 0),
                       zones[pid]))
    for i, pid in enumerate(extra_ids):
        idx = len(order) + i + 1
        it = by_id[pid]
        zones[pid] = "今日新错加练"
        rows.append("| %d | %s | %s | %d | %s |"
                    % (idx, pid, it["title"].replace("|", "/"), it.get("occurrences", 0),
                       zones[pid]))
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

    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("已保存：" + str(OUT))
    print("题数：%d（必考区 %d + 本周新错区 %d + 今日新错加练 %d）"
          % (len(order) + len(extra_ids), n_core, n_new, len(extra_ids)))
    print("大小：" + str(OUT.stat().st_size) + " 字节")
    print("题目：" + " ".join(pid for _, pid in order)
          + (" | 加练 " + " ".join(extra_ids) if extra_ids else ""))


if __name__ == "__main__":
    main()
