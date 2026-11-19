# -*- coding: utf-8 -*-
"""生成 2026-11-19（周四）的周四大复习卷文件（答案剥离版）。

基于 _生成复习卷_1105.py，改了四处：

1. **题数 5 → 6**：plan 5 的 5 题 + E36（今日指定复考）。
   E36 为什么不自然进卷：
     · 它的 occurrences = 1 → 排不进「必考区」（那里按犯过次数降序取）
     · 它的 first_seen = 11-10 → 早于 7 天窗口（cutoff = 11-12）→ 进不了「加练区」
     · 结果：11-10 首犯、至今一次没被考过 —— 又一次「自我饿死」
   处理：手动加到必考区尾部，理由写进卷头。

2. **第八节「上下文规范」全部落实**（11-14 新增，之前几卷没做全）：
   1105 脚本直接用 JSON 的 bad 字段，但 E02/E05/E15/E42/E43 的 bad 是**脱离上下文的片段**，
   变量从哪来、谁调用、期望输出是什么全都没有 → 拿到题目也没法动手改。
   这里给每题补一段「上下文补齐」文本（只含错误版本，绝不含正确写法）。

3. **第九节「题干/作答分区」**：Markdown 复习卷本身是题面 + 留白，天然分区；
   关键是代码块只放错误版本，答案只在答案卷。

4. **答案泄漏自检加强**：1105 只查「✅」，这里额外查 "应该" / "正确写法" / "修法" 等字样。

三条硬规则（沿用 10-29）：
   1. 答案绝不进卷子 —— 只用 bad 字段 + 上下文补齐（补齐文本里也不含正确写法）
   2. 题目顺序以 plan 5 的输出为准，E36 追加在必考区尾部
   3. 必须带最近一周的新错题 —— 追踪器默认留 2 个坑位
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject")
BASE = ROOT / "笔记"
TRACKER = ROOT / "projects" / "error-tracker" / "错题追踪器.py"
JSON_PATH = ROOT / "projects" / "error-tracker" / "错题追踪.json"
OUT = BASE / "复习卷" / "周四大复习_2026-11-19_复习卷.md"
PY = r"D:\AAAA\python.exe"
TODAY = "2026-11-19"
CUTOFF = "2026-11-12"          # 今天往前 7 天

# 今日指定复考题：11-10 首犯、streak 0/2、至今一次没被任何一卷考过。
# 它既排不进必考区（occ=1）、又进不了加练区（first_seen 早于 cutoff），
# 属于「自我饿死」的又一变体 —— 手动补位。
FORCE_EXTRA = ["E36"]

Q_RE = re.compile(r"^第 (\d+) 题\s+(E\d+)\s+(.*)$", re.M)

# ─────────────────────────────────────────────────────────────────────
# 第八节：上下文补齐（只给错误版本 + 期望/实际对照，绝不含正确写法）
# ─────────────────────────────────────────────────────────────────────
CONTEXT = {
    "E02": """# 场景：统计一个词库里每个词的出现次数，并算出所有数字的总和
# 完整可运行片段（10-20 那次练习里你写的版本）：

# ---- 数据准备 ----
文章 = "python is good python is easy"
b = [3, 7, 12, 5]               # 待求和的数字列表
t = {"python": 3, "is": 2}       # 词 → 次数
counts = t                       # ⚠️ counts 现在是「词 → 次数」这个字典

def sum_list(nums):
    nums = 0                        # ❌ 错误1：入参 nums 被覆盖成累加器
    for i in nums:                  #    nums 现在是 int，for 迭代 int → TypeError
        nums += i
    return nums

for w, counts in t.items():        # ❌ 错误2：counts 循环后变成 int（字典被顶掉了）
    print(w, counts)

print(sum_list(b))                  # ❌ 错误3：循环变量泄漏到循环外
print(counts.items())               # ← 此刻 counts 已经是 int，这里就炸

# 期望输出：
#   python 3
#   is 2
#   27          ← 3+7+12+5
# 实测输出：
#   TypeError: 'int' object is not iterable
#   （nums 在函数第 1 行就被自己改成了 0，for 循环直接炸）
#
# ⚠️ 三处的共同病根是「同一个名字前后扮演两个角色」：
#    · nums 先是「参数（列表）」，被改成了「累加器(int)」
#    · counts 先是「字典」，被循环变量顶成了「次数(int)」
#    · 循环变量跑出了循环作用域，泄漏到外面
#   拿到变量名先问一句：这位置它该是什么类型？""",

    "E15": """# 场景：统计一篇文章的词频，并按词频从高到低排出排行榜；顺便做通讯录去重
# 完整可运行片段（10-21 那次练习里你写的版本）：

文章 = "Hello, world! Hello python. python is good."
counts = {}                       # 词 → 次数
contacts = {"小明": {"电话": "13800138000"}}

for w in 文章.split():            # split() 按空格切
    w = w.lower()                 # ❌ 错误1：缺 .strip() → "hello," 和 "hello" 算成两个词
    counts[w] = counts.get(w, 0) + 1

after = sorted(counts.items(), key=lambda x: x[1])   # ❌ 错误2：缺 reverse=True → 升序

姓名, 新电话 = "小明", "13911112222"
if 姓名 in contacts: print("未覆盖")   # ❌ 错误3：缺 return → 照样往下覆盖
contacts[姓名] = {"电话": 新电话}

print(counts)
print(after)
print(contacts)
# 期望输出：
#   词频里 "hello" 应该是 2（不是 1），且 "hello," 不该单独存在
#   排行榜第一条应该是次数最多的词（降序）
#   contacts["小明"]["电话"] 应该还是 "13800138000"（提示"未覆盖"就不该覆盖）
# ⚠️ 三处都不报错、不报警，输出看着挺像回事""",

    "E05": """# 场景：维护一份通讯录，每个人的电话既要能存进去，也要能发短信
# 完整可运行片段（10-27 那次练习里你写的版本）：

contacts = {
    "小明": {"电话": 13800138000},   # ❌ 错误：数字
    "小红": {"电话": "13900139000"}  # 字符串
}

# 调用现场：把电话号码拼成一条短信正文
def 发短信(姓名, 正文):
    电话 = contacts[姓名]["电话"]
    return f"发到 {电话}：{正文}"    # 数字也能拼进 f-string，不报错

print(发短信("小明", "晚上一起吃饭吗"))
print(发短信("小红", "晚上一起吃饭吗"))

# 然后要做「按电话查人」：
def 按电话找人(电话):
    for 姓名, 信息 in contacts.items():
        if 信息["电话"] == 电话:     # ❌ 这里开始出事
            return 姓名
    return None

print(按电话找人("13900139000"))    # 期望 "小红"
print(按电话找人(13900139000))      # 期望 "小明"
# 实测：第二个调用返回 None
# ⚠️ 不报错 —— 数字和字符串比永远 False，静默查不到人""",

    "E35": """# 场景：判断「一组计数里是不是全都是 0」（LeetCode 242 有效的字母异位词）
# 完整可运行片段（11-10 你自己写的第一版）：

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        d = {}                        # 字符 → 出现次数，s 和 t 共用这一个
        for ch in s:
            d[ch] = d.get(ch, 0) + 1  # 遍历 s：加一
        for ch in t:
            d[ch] = d.get(ch, 0) - 1  # 遍历 t：减一
        if d.values():                # ❌ 错误：values() 返回的是【视图对象】不是列表
            return True               #    视图对象只要字典非空就【永远为真】
        return False

# 调用与实测：
print(Solution().isAnagram("rat", "car"))   # 期望 False，实际打印 True  ← 静默错误
print(Solution().isAnagram("aab", "abb"))   # 期望 False，实际打印 True
# ⚠️ 不崩、不报警、一律返回 True —— LeetCode 官方那 2 个用例还能【蒙对】
#    暴露条件：t 是 s 的真子集（如 'aab' vs 'ab'）→ 减一不产生负数 → 走不到提前返回""",

    "E36": """# 场景：判断两个字符串是不是字母异位词（LeetCode 242）
# 完整可运行片段（11-10 你自己写的第一版，同一个文件里的另一个错误）：

class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        d = {}                        # 字符 → 出现次数，s 和 t 共用这一个
        for ch in s:
            d[ch] = d.get(ch, 0) + 1  # 遍历 s：加一
        for ch in t:
            d[ch] = d.get(ch, 0) - 1  # 遍历 t：减一
            if ch <= -1:              # ❌ 错误：判断的是【字符】不是【计数】
                return False           #    ch 是 str，跟 int 比 → TypeError
            # 这里还少了最终判定

# 调用与实测：
print(Solution().isAnagram("rat", "car"))
# 实测输出：
#   TypeError: '<=' not supported between instances of 'str' and 'int'
# ⚠️ 脑子里想的是「计数变负了」，手下写的是「字符变负了」——
#    概念抓对了，但落笔落到了另一层：计数住在 d[ch] 里（键是 ch，值是 d[ch]）""",

    "E42": """# 场景：从一段混杂文本里把所有的数字片段抠出来，并打印它们各自的位置
# 完整可运行片段（11-14 你写的那版）：

import re

文本 = "订单A123已完成，金额456元，编号B78待发货"

for i in re.findall(r'\\d+', 文本):
    print(i.group(), i.span())   # ❌ findall 给的是 str，没有 .group()

# 期望输出（每个数字 + 它在文本里的起止位置）：
#   123 (3, 6)
#   456 (10, 13)
#   78  (18, 20)
# 实测输出：
#   AttributeError: 'str' object has no attribute 'group'
# ⚠️ 不崩、不报警 —— 除非你正好调了 .group()，否则你只会拿到一串裸字符串，
#    根本不知道自己是在拿「文本」还是「匹配对象」""",

    "E43": """# 场景：把一张成绩单按序号从大到小排，再把不合格的剔掉
# 完整可运行片段（11-17 你写的那版）：

import pandas as pd

df = pd.DataFrame({
    "姓名": ["张三", "李四", "王五"],
    "序号": [3, 1, 2],
    "分数": [88, 95, 60]
})

df.sort_values(by='序号', ascending=False)   # ❌ 错误：返回值没接住 → 哑弹
df = df[df["分数"] >= 60]                     # 这一行接了，所以过滤生效了

print(df)
# 期望输出（按序号倒序 3,2,1）：
#      姓名  序号  分数
#   0  张三    3   88
#   2  王五    2   60
#   1  李四    1   95
# 实测输出：
#      姓名  序号  分数
#   0  张三    3   88
#   1  李四    1   95
#   2  王五    2   60
# ⚠️ 顺序完全没变 —— 排序那行等于没写，但它长得像一行正经代码""",
}


HEAD = """# 周四大复习 · 复习卷 · 2026-11-19（周四）

> **本卷共 {n} 题**：第一部分 {n_core} 题是「必考区」（犯过 ≥2 次的高频顽固题，
> 外加今天指定复考的一题），第二部分 {n_new} 题是「本周新错区」
> （最近 7 天你亲手登记的新错）。
>
> **答案不在这个文件里。** 写完一整份再对照讲解：
> `周四大复习_2026-11-19_答案与讲解.md`（等你交卷后我单独生成，现在还没写）。
>
> 📌 **第 {n_core} 题（E36）是今天点名要复考的**：11-10 你手写第一版时就栽在这，
> 到现在**一次都没被任何一卷考过** —— 它 occ=1 排不进必考区、first_seen 又早于
> 7 天窗口进不了加练区，属于「自我饿死」的又一变体，所以今天手动补位。

## 作答规则

1. **先别翻答案**。每题只看 ❌ 那段代码，自己说出哪里错、自己改写。
2. 写不出来就写"不会" —— 那也是有用的信息，别空着蒙。
3. **建议每题 12 分钟**；卡住的题标个记号先跳，最后回头攻。
4. **题目给你完整上下文**（变量从哪来、函数被谁调用、期望输出是什么）——
   拿到片段就能直接改；**不要凭空脑补一个你猜的版本**再改。
5. **做完整份再 record**（不要一题一题提前记）：

```
cd "D:\\AI应用工程师\\01-学习仓库-Python学习路径\\pythonProject\\projects\\error-tracker"
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> pass "你的理解"
"D:\\AAAA\\python.exe" 错题追踪器.py record <题号> fail "又错在哪"
```

6. 全卷做完后收尾：

```
"D:\\AAAA\\python.exe" 错题追踪器.py render   # 重新生成错题追踪.md
"D:\\AAAA\\python.exe" 错题追踪器.py stats    # 看池子还剩几题
```

| 题号 | ID | 考点 | 犯过几次 | 连对 | 区 |
|---|---|---|---|---|---|
{table}

> 答错不丢人，答错不记才丢人。
> 第一部分那几题是**你反复犯过的**（E02 犯了 8 次、E15 7 次、E05 4 次）——
> 这几题是整个池子的"顶流"，错了要当场改对。
> 第二部分是**你这周亲手登记的新错**（E43 是 11-17 刚登记的）。
> E36 是**你 11-10 手写第一版时就栽的**，跟 E35 出自同一个练习文件。

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

    第八节规范：优先用 CONTEXT 里补齐过的上下文（带变量来源 + 调用现场 +
    期望 vs 实际），CONTEXT 里没有的才退回 JSON 的 bad 字段。
    """
    tags = " / ".join(it.get("tags", [])) or "—"
    occ = it.get("occurrences", 0)
    code = CONTEXT.get(it["id"], it.get("bad", "").rstrip())
    L = []
    L.append("## 第 %d 题（%s）· %s" % (idx, it["id"], it["title"]))
    L.append("")
    L.append("**涉及标签**：%s　｜　**犯过 %d 次**　｜　**连对 %d/%d**%s"
             % (tags, occ, it.get("streak", 0), it.get("need", 2),
                ("　｜　**%s**" % zone) if zone else ""))
    L.append("")
    L.append("```python")
    L.append(code.rstrip())
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

    # 3c) 今日指定复考（FORCE_EXTRA）：occ=1 排不进必考区、first_seen 早于窗口
    #     进不了加练区 —— 手动补位到必考区尾部
    force_ids = [pid for pid in FORCE_EXTRA
                 if pid in by_id and by_id[pid]["status"] == "active"
                 and pid not in used]
    for pid in force_ids:
        used.add(pid)

    zones = {}
    for idx, pid in order:
        zones[pid] = "必考区" if idx <= n_core else "本周新错区"
    for pid in force_ids:
        zones[pid] = "必考区 · 今日指定复考"
    for pid in extra_ids:
        zones[pid] = "本周新错加练"

    rows = []
    all_ids = [pid for _, pid in order] + force_ids + extra_ids
    for i, pid in enumerate(all_ids, 1):
        it = by_id[pid]
        rows.append("| %d | %s | %s | %d | %d/%d | %s |"
                    % (i, pid, it["title"].replace("|", "/"), it.get("occurrences", 0),
                       it.get("streak", 0), it.get("need", 2), zones[pid]))

    body = []
    for idx, pid in order:
        body.append(_q_block(idx, by_id[pid], zones[pid]))
    off = len(order)
    for i, pid in enumerate(force_ids):
        body.append(_q_block(off + i + 1, by_id[pid], zones[pid]))
    off += len(force_ids)
    for i, pid in enumerate(extra_ids):
        body.append(_q_block(off + i + 1, by_id[pid], zones[pid]))

    n_core_total = n_core + len(force_ids)
    text = HEAD.format(n=len(all_ids), n_core=n_core_total,
                       n_new=n_new, table="\n".join(rows))
    text += "\n".join(body)
    text += TAIL

    # 4) 自检：卷子里绝不能出现答案标记
    for bad_mark in ("✅ 应该", "✅ 正确写法", "修法：", "✅", "应该：", "正确写法"):
        assert bad_mark not in text, "答案泄漏进卷子了！%s" % bad_mark
    # 每题都得有上下文（第八节）：代码块不能少于 8 行
    assert text.count("```python") == len(all_ids), "有题没渲染代码块"
    assert text.count("### 你要做的") == len(all_ids), "有题没渲染作答区"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("已保存：" + str(OUT))
    print("题数：%d（必考区 %d + 本周新错区 %d + 加练 %d）"
          % (len(all_ids), n_core_total, n_new, len(extra_ids)))
    print("大小：" + str(OUT.stat().st_size) + " 字节")
    print("题目：" + " ".join(all_ids))
    print("指定复考：" + (" ".join(force_ids) or "无"))
    print("加练：" + (" ".join(extra_ids) or "无"))
    print("自检：答案标记 0 处 / 代码块 %d 个 / 作答区 %d 个"
          % (text.count("```python"), text.count("### 你要做的")))


if __name__ == "__main__":
    main()
