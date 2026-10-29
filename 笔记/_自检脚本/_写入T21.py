"""把 T21 写进工具链坑（JSON 是真源），并同步 MD。

T21 = 今天 19:15~19:35 排障时连踩的两个「判定/转义」级别的坑：

坑 A：**bat 的 `echo` 里 `>` 是重定向符，会把 Python 代码行吃掉**
  现象：修复GitHub访问_v2.bat 用 `>> tmp echo <python代码>` 逐行拼 py 文件，
        跑出来报 IndentationError @ line 25。
  真相：`echo     if len(parts) >= 2:` 里的 `>=` 被 cmd 当成
        「把 `= 2:` 当成输出文件名」，于是**这一行从临时 py 里消失了**，
        后面的行整体上移一行 → 缩进错位 → IndentationError。
  教训：**不要在 bat 里拼代码**。Python 独立成文件，bat 只负责提权+调用。

坑 B：**curl 连不上时输出的 http_code 是 "000"，不是状态码**
  现象：自制的 probe() 判定写成 `len(code)==3 and code.isdigit()`，
        结果 000 也被判成"活"，差点把死 IP 写进 hosts。
  真相：000 = TCP/TLS 都没建立，压根没有任何 HTTP 响应。
  教训：判定"链路通不通"必须**显式排除 000**。

坑 C（附带发现）：**这个网络对 raw.githubusercontent.com 有约 50% 丢包**
  连测 10 次：5 次 301、5 次 000。单次探测结果有一半是假的。
  教训：探测必须**重试**，规则是「任一次成功就算活，全失败才算死」。

为什么单独记一条而不是并进 T19/T20：
  T19/T20 讲的是「IP 会轮换、怎么应对」；
  T21 讲的是「探测和转义本身会骗你」—— 另一层面的坑，混进去会让前面两条失焦。
"""
import io
import json
from pathlib import Path

BASE = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")
JSON_PATH = BASE / "工具链坑.json"
MD_PATH = BASE / "工具链坑.md"

T21 = {
    "id": "T21",
    "title": "三个「会骗你」的东西：bat 的 echo 会吃掉 `>` 后的代码行 / curl 的 000 不是状态码 / 单次探测有一半是假的",
    "symptom": "【A】桌面《修复GitHub访问_v2.bat》双击后报：\n    The system cannot find the path specified.\n    File \"C:\\Users\\15816\\AppData\\Local\\Temp\\gh_fix2.py\", line 25\n      nm = parts[1].lower()\n    IndentationError: unexpected indent\n【B】自己写的 probe() 判定 `len(code)==3 and code.isdigit()`，\n    导致 curl 连不上时输出的 \"000\" 也被判成「链路是通的」——\n    dry-run 时 185.199.110.133（实际已不可达）被判 OK。\n【C】raw.githubusercontent.com 连测 10 次：301 000 301 000 301 000 301 301 000 000\n    —— 成功率只有 5/10，同一个 IP 同一命令时通时不通。",
    "cause": "【A】cmd.exe 的 echo 参数里，**> 和 >> 是重定向符**，不是普通字符。\n    `echo     if len(parts) >= 2:` 会被解析成「输出到名为 \"= 2:\" 的文件」，\n    于是这一行从临时 py 里**消失**，后面所有行整体上移一行 → 缩进错位。\n    根因不是缩进写错，是**用 bat 拼代码这条路本身就不该走**。\n【B】curl 的 -w \"%{http_code}\" 在连接失败时输出 **000**，它是 3 位数字、\n    isdigit() 为真 —— 于是「连都没连上」被当成了「拿到了响应」。\n    正确语义：000 = 没有 HTTP 响应，必须显式排除。\n【C】校园网对 raw.githubusercontent.com 所在的 185.199.x 段有约一半的丢包/限流，\n    连接会在 0.09 秒被 RST。**单次探测的结果有一半是假的。**",
    "solutions": [
        "**别在 bat 里拼代码**：Python 独立成 .py 文件，bat 只做「检查管理员 → 调 python → pause」。\n    路径用 `%~dp0` + **ASCII 文件名**（如 gh_hosts_fix.py），避免 bat 里出现中文路径的编码问题。\n    配套：桌面上放 v3 的 bat + py 两个文件，bat 找不到 py 就明确报错。",
        "**判定状态码必须显式排除 000**：`if len(code)==3 and code.isdigit() and code != \"000\"`。\n    而且判定标准要按 host 分开：github.com/login 稳定 200；api.github.com 根路径 301 属正常；raw 根路径也是 301。\n    一刀切要 200 会误杀。",
        "**探测必须重试**：规则是「任一次成功就算活（宽松），全都失败才算死（严格）」。\n    probe 内部循环 3 次，每次调一次 curl；3 次全 000 才判定为死。\n    这样两个方向的误判都能躲开。",
        "**探活别只探一次就用**：今天实测 20.27.177.113 在第 2 步（探 github.com）判死、\n    在第 4 步（探 api.github.com）判活 —— 同一个 IP 不同域名表现不同。\n    所以「现有绑定验证」和「新 IP 探测」要分别做，不能共用一次结论。",
        "**web 段和 api 段必须分开选**（T17 在浏览器侧同样成立）：\n    github.com / codeload / objects 用 web 段 IP；api.github.com 用 api 段 IP。\n    实测 Azure 中国段（20.x / 207.x）能同时承载，但 GitHub 美国边缘的 .3/.4 和 .5/.6 是不同网段。",
        "**写入必须有回滚**：新工具的做法是「备份 → 写 → 校验 → 不通过自动 copy 回来」。\n    校验要区分「致命问题（文件写坏了）」和「网络问题（可能只是抖动）」，\n    网络项重试 3 轮再判，避免误回滚。",
    ],
    "hits": 1,
    "tags": ["bat", "cmd转义", "curl", "000状态码", "探测重试", "hosts", "T17"],
}

MD_SECTION = """
## ⚠️ T21 三个「会骗你」的东西（2026-10-29 19:15~19:35 排障实测）

### 坑 A：bat 的 `echo` 会吃掉 `>` 后面的代码行

v2 修复工具用 `>> tmp echo <python代码>` 逐行拼一个临时 py 文件。跑出来：

```
File "C:\\Users\\15816\\AppData\\Local\\Temp\\gh_fix2.py", line 25
  nm = parts[1].lower()
IndentationError: unexpected indent
```

**不是缩进写错了。** 用 diag bat 实测复现（`笔记/_自检脚本/_诊断bat_echo缩进.py`）：

```
 24 | 期望 4 | 实际 4 |     parts = s.split()
 25 | 期望 4 | 实际 8 |         nm = parts[1].lower()   <<<< 不一致
```

第 25 行本该是 `if len(parts) >= 2:`，**它整个消失了**。

真相：**cmd.exe 的 `echo` 参数里 `>` 是重定向符**。
`echo     if len(parts) >= 2:` 被解析成「把 `= 2:` 当成输出文件名」，
这一行被重定向到了别处，临时 py 里就少了这么一行 → 后面的行整体上移 → 缩进错位。

> **结论：不要在 bat 里拼代码。**
> Python 独立成文件，bat 只负责「检查管理员 → 调 python → pause」。

### 坑 B：curl 的 `000` 不是状态码

自制的 probe() 判定写成：

```python
if len(code) == 3 and code.isdigit():      # ❌ "000" 也满足！
    return True
```

curl 连不上时 `-w "%{http_code}"` 输出的是 **`000`** —— 3 位数字、isdigit 为真，
于是「TCP 都没连上」被当成了「拿到了 HTTP 响应」。

```python
if len(code) == 3 and code.isdigit() and code != "000":   # ✅
```

而且判定标准要**按 host 分开**：
`github.com/login` 稳定 200；`api.github.com/` 根路径 301（跳主站）属正常；
`raw.githubusercontent.com/` 也是 301。一刀切要 200 会误杀。

### 坑 C：单次探测有一半是假的

```
raw.githubusercontent.com 连测 10 次：
301 000 301 000 301 000 301 301 000 000
成功率 5/10
```

校园网对 185.199.x 段有约 50% 丢包/限流，连接会在 0.09 秒被 RST。

> **探测必须重试。** 规则：**任一次成功就算活（宽松），全都失败才算死（严格）**。
> 这样「把活 IP 判死」和「把死 IP 判活」两个方向都能躲开。

### 附带发现：同一个 IP 对不同域名表现不同

今天实测 `20.27.177.113`：
- 探 `github.com`（第 2 步）→ 3 次全 000，判**死**
- 探 `api.github.com`（第 4 步）→ 通了，判**活**

所以「验证现有绑定」和「新 IP 探测」必须**分别做**，不能共用一次结论。

### v3 工具的最终形态

```
备份（桌面，带时间戳）
  → 探测（每个 IP 重试 3 次；web 段 / api 段 / raw 段分别选）
  → 组装（保留非 GitHub 的原有行 + 按块删掉旧 GitHub 段 + 写新块）
  → 写入（CRLF，UTF-8）
  → 校验（区分「文件坏了」和「网络抖」，网络项重试 3 轮）
  → 不通过自动 copy 备份回来
```

配套：`修复GitHub访问_v3.bat`（提权 + 调用，CRLF，全 ASCII）
　　　`gh_hosts_fix.py`（Python 本体，带完整逐行注释）

**一句话记住**：**转义和判定都会骗你** —— 别用 bat 拼代码，别信单次探测，写文件一定要有回滚。

"""


def main():
    data = json.loads(io.open(JSON_PATH, encoding="utf-8").read())
    items = data["items"]
    if any(x["id"] == "T21" for x in items):
        print("T21 已存在，跳过 JSON 写入")
    else:
        items.append(T21)
        data["updated"] = "2026-10-29"
        io.open(JSON_PATH, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, indent=2)
        )
        print(f"JSON 已更新：T21 写入，共 {len(items)} 条")

    md = io.open(MD_PATH, encoding="utf-8").read()
    if "## ⚠️ T21 三个「会骗你」的东西" in md:
        print("MD 已含 T21 章节，跳过")
    else:
        md = md.rstrip() + "\n" + MD_SECTION
        md = md.replace("共 20 条", "共 21 条")
        io.open(MD_PATH, "w", encoding="utf-8").write(md)
        print("MD 已更新：追加 T21 章节")

    d2 = json.loads(io.open(JSON_PATH, encoding="utf-8").read())
    print(f"自检：JSON {len(d2['items'])} 条，更新时间 {d2['updated']}")
    m2 = io.open(MD_PATH, encoding="utf-8").read()
    for line in m2.splitlines():
        if "T21" in line and line.startswith("#"):
            print("  MD:", line)


if __name__ == "__main__":
    main()
