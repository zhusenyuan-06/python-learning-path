"""把 T20 写进工具链坑（JSON 是真源），并同步 MD。

T20 = 今天 19:00-19:20 实测出的新教训：
  「探活 ≠ 可用」——探活和真正 push 之间隔十几秒，这十几秒里 IP 池就换了一轮。
  所以正确姿势不是「探到一个就用」，而是「探到全部活的，操作时逐个轮换」。
  以及：串行 curl 探活 64 个 IP 要 6 分钟（窗口早就过期），
  必须并发探（Python 线程池，10 秒扫完 64 个）。

为什么单独记一条而不是改 T19：
  T19 说「可达 IP 集合随时段轮换」；T20 补的是「怎么应对轮换」——
  这是两个层面的知识，混在一起会让 T19 变得没法用。
"""
import io
import json
from pathlib import Path

BASE = Path(r"D:\AI应用工程师\01-学习仓库-Python学习路径\pythonProject\笔记")
JSON_PATH = BASE / "工具链坑.json"
MD_PATH = BASE / "工具链坑.md"

T20 = {
    "id": "T20",
    "title": "探活结果会过期 —— 探活和操作之间隔十几秒，IP 池就换了一轮，必须「探全 + 操作时轮换」",
    "symptom": "2026-10-29 19:20，push_github.sh v2 的流程是「curl 串行探活 → 取第一个 200 的 → 绑定 → push」。\n结果：探活阶段 140.82.113.3 返回 200，脚本绑上它，紧接着的 push 三次全败：\n    第 1 次：Recv failure: Connection was reset\n    第 2、3 次：Failed to connect to github.com:443 after 21084 ms\n同一个 IP，探活时是通的，push 时已经死了。\n换用 Python 线程池并发重扫同一批 IP（相隔不到 2 分钟），140.82.113.3 已经不在 200 列表里了，活的是 140.82.113.4。",
    "cause": "两个原因叠在一起：\n① **时间差**：探活和真正 push 之间隔着提交、git 打包、鉴权等十几秒。这十几秒里 GitHub 边缘 IP 的可达集合会换一轮（T19 已验证：19:00 和 19:05 看到的是完全不同的两个集合）。所以「探活时的结论」在「操作时」已经过期 —— 这是**决策时刻**和**执行时刻**分离导致的，不是网络本身抖。\n② **串行探活太慢**：v2 用 curl 逐个试，每个 IP 最多等 6 秒，扫 64 个候选要 6 分钟。等探完，第一个 IP 早就凉透了，等于「用 6 分钟前的信息做决策」。\n另外还有一个隐性坑：**api 段不能用 200 判定**。api.github.com 的根路径本来就没有页面，返回 404 才是正常的，用「必须是 200」当活的标准会把整段 api IP 全判死。",
    "solutions": [
        "**并发探活，别串行**：写一个 Python 探针（socket.create_connection + ssl 握手 + 发一次 HTTP GET），用 ThreadPoolExecutor 32 并发。64 个 IP 从 6 分钟压到 ~10 秒。仓库里已有 `probe_gh.py`，实测 10 秒内扫完 web 段 64 个 + api 段 32 个候选。",
        "**探活要拿全，不是拿一个**：把「第一个 200 就 break」改成「收集所有活的」，push 时逐个轮换绑定 —— 这才是唯一能对抗「决策时刻 ≠ 执行时刻」的办法：既然会过期，那就在过期前多试几个。",
        "**轮换要在绑定层做，不是在 curl 层做**：git 的 curloptResolve 是单值键（T01/T19），所以每次尝试前必须 `git config --global --unset-all` 再 `--add` 新 IP —— 同一个 URL 永远只留一个。",
        "**判定标准按 host 分开**：github.com 用 `/login` 看 200；api.github.com 根路径返回 404/400 都算**活**（能拿到任何 HTTP 响应就说明 TLS 握手和链路都通了）。探针里已经按 ok_codes 区分。",
        "**push 失败后先校验远端再重试**：可能是假失败（T18）。三次都失败时用 `git ls-remote` 比对 HEAD，一致就算成功。",
        "**已落地**：push_github.sh 升级到 v3 —— 「并发探活拿全 → 逐个 IP 轮换绑定 → 每个都 ls-remote 校验 → 全部失败再报」。2026-10-29 19:22 实测一次通过（绑定 140.82.112.3，push 102e78d..286c3a4，远端校验一致）。",
    ],
    "hits": 1,
    "tags": ["GitHub", "push", "网络", "IP轮换", "并发探活"],
}

MD_SECTION = """
## ⚠️ T20 二次实战（2026-10-29 19:20 实测推翻了我自己的第一版结论）

**T19 说「可达 IP 集合会轮换」—— 知道了，但还不够用。**

v2 脚本按 T19 的结论改成了「探活 → 绑单 IP → 立刻推」，结果照样失败：

```
=== 1/4 探测可用 IP（web 段）===
    140.82.112.3  no
    140.82.113.3  OK          ← 探活时是通的
--- 绑定 140.82.113.3 ---
第 1 次推送：Recv failure: Connection was reset
第 2 次推送：Failed to connect to github.com:443 after 21084 ms
第 3 次推送：Failed to connect to github.com:443 after 21037 ms
```

**同一个 IP，探活时 200，push 时已死。** 隔了不到 2 分钟，我用 Python 并发重扫同一批 IP：

```
140.82.113.3  ← 已经不在 200 列表里了
140.82.113.4  ← 活的是这个
```

### 我漏掉的两件事

**① 「探活」和「操作」是两个时刻。** 探活完还要提交、git 打包、鉴权，这十几秒里 IP 池就换了一轮。
**用 6 分钟前的信息做决策，必然过期。**

**② 串行探活太慢，等于自己给自己制造过期。** v2 用 curl 逐个试，每个 IP 最多等 6 秒，扫 64 个候选要 6 分钟 —— 等探完，第一个 IP 早就凉透了。

### v3 的解法：探全 + 轮换

既然「会过期」是常态，那就不赌某一个 IP 活着：

```
并发探活（10 秒扫完 64 个）
    → 收集【全部】活的 IP
    → 逐个绑定、逐个 push、逐个 ls-remote 校验
    → 第一个失败就换下一个
```

Python 线程池并发探活（`probe_gh.py`），64 个 IP 从 6 分钟压到 10 秒：

```python
with ThreadPoolExecutor(max_workers=32) as ex:
    for ip, h, code, note in ex.map(lambda i: check(i, host), cands):
        ...
```

### 顺带修掉一个隐性坑：api 段不能用 200 判定

`api.github.com` 的根路径本来就没页面，**返回 404 才是正常的**。用「必须是 200」当活的标准，会把整段 api IP 全部误判成死的：

```python
if mode == "web":
    ok_codes = {"200"}              # github.com/login 返回 200
else:
    ok_codes = {"200","404","400","403","301","302"}
    # api 段：拿到任何 HTTP 响应就说明 TLS 握手和链路都通了
```

### v3 实测

```
web 段活 IP: 140.82.112.3 140.82.112.4 140.82.113.3 140.82.113.4
              140.82.114.3 140.82.114.4 140.82.116.3 140.82.116.4
              140.82.121.3 140.82.121.4
api 段绑到 140.82.112.5
--- 尝试 github.com -> 140.82.112.3 ---
   102e78d..286c3a4  main -> main
本地: 286c3a4...  远端: 286c3a4...   ✅ 一致
```

**一句话记住**：T19 告诉你「池子会换」，T20 告诉你「换了怎么办」—— **探活要快、要全，操作时要能轮换**。

"""


def main():
    data = json.load(io.open(JSON_PATH, encoding="utf-8"))
    items = data["items"]
    if any(x["id"] == "T20" for x in items):
        print("T20 已存在，跳过 JSON 写入")
    else:
        items.append(T20)
        data["updated"] = "2026-10-29"
        io.open(JSON_PATH, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, indent=2)
        )
        print(f"JSON 已更新：T20 写入，共 {len(items)} 条")

    md = io.open(MD_PATH, encoding="utf-8").read()
    if "## ⚠️ T20 二次实战" in md:
        print("MD 已含 T20 章节，跳过")
    else:
        md = md.rstrip() + "\n" + MD_SECTION
        # 更新统计行
        md = md.replace("共 19 条", "共 20 条")
        io.open(MD_PATH, "w", encoding="utf-8").write(md)
        print("MD 已更新：追加 T20 章节")

    # 自检
    d2 = json.load(io.open(JSON_PATH, encoding="utf-8"))
    print(f"自检：JSON {len(d2['items'])} 条，更新时间 {d2['updated']}")
    m2 = io.open(MD_PATH, encoding="utf-8").read()
    for line in m2.splitlines():
        if "T20" in line and line.startswith("#"):
            print("  MD:", line)


if __name__ == "__main__":
    main()
