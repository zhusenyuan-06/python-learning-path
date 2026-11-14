# -*- coding: utf-8 -*-
"""写入工具链坑 T27 / T28（2026-11-14 晚，push 收尾时踩的）

T27: push_github.sh 里的 probe_gh.py 用相对路径调用 —— cd 到仓库根后找不到，
     再被 2>/dev/null 吞掉 stderr，探活「静默失败」被误判成网络问题
T28: 学校 DNS 把 github.com 解析到校园镜像节点（20.6.7.17），
     而探针只扫 140.82.x.x 官方段 —— 探针扫再多次也命中不了
"""
import datetime
import os
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.join(HERE, "..", "工具链", "工具链坑.py")

spec = importlib.util.spec_from_file_location("gzk", TRACK)
gzk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gzk)

db = gzk.load()
今天 = datetime.date.today().isoformat()

if any(x["id"] == "T27" for x in db["items"]):
    print("⚠️ T27 已存在，跳过")
else:
    db["items"].append({
        "id": "T27",
        "title": "push 脚本里的相对路径 + 被吞掉的 stderr —— 探活「静默失败」被误判成网络问题",
        "symptom": "2026-11-14 19:20 跑 工具/push_github.sh，脚本输出「本次扫描没有活 IP」，\n"
                   "但同一个人手动在 工具/ 目录下跑 probe_gh.py 却能扫出活 IP（140.82.113.4）。\n"
                   "脚本明明存在、Python 也没报找不到文件，探活却「一个活 IP 都没有」。",
        "cause": "脚本第 49 行 cd \"$GIT_DIR\"（仓库根），但第 72 行调用的是相对路径 "
                 "\"probe_gh.py\" —— 而这个文件实际在 工具/ 目录下。\n"
                 "→ 文件找不到 → Python 抛 FileNotFoundError → 但那行后面跟着 2>/dev/null，\n"
                 "   stderr 被整条丢弃 → 探活变量拿到空串 → 脚本走进「没有活 IP」分支。\n"
                 "→ 表现成「网络不通」，实际上脚本自己根本没跑起来。",
        "solutions": [
            "【根修】用绝对路径调用同目录脚本：\"$PY\" \"$SCRIPT_DIR/probe_gh.py\" web（SCRIPT_DIR=脚本自己所在目录）",
            "【防再犯】关键子命令【不要】加 2>/dev/null —— 至少探活这一步要让它把真错误打出来",
            "【自检手法】脚本跑不通时，先把子命令单独拎出来在同目录下手动跑一遍，看它到底报什么",
            "【通用心法】「脚本说网络问题」时，先分清三种可能：① 网络真不通 ② 依赖项没找到 ③ 脚本逻辑判断错。"
            "第 ②③ 种会被 stderr 静默 + 单一错误提示伪装成第 ① 种",
            "【反例留档】原 push_github.sh v3 里那行 2>/dev/null 掩盖了这个问题整整一轮排查",
        ],
        "tags": ["push", "脚本", "相对路径", "静默失败", "stderr", "2>/dev/null", "误判", "网络"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    })
    print("✅ 已写入 T27")

if any(x["id"] == "T28" for x in db["items"]):
    print("⚠️ T28 已存在，跳过")
else:
    db["items"].append({
        "id": "T28",
        "title": "学校 DNS 把 github.com 解析到校园镜像节点 —— 探针扫的网段和本机实际走的不是同一条路",
        "symptom": "2026-11-14 19:30 nslookup github.com 返回 20.6.7.17（不是 GitHub 官方 IP）。\n"
                   "而 probe_gh.py 扫的是 140.82.x.x 官方段，连续 10 轮全部「没有活 IP」。\n"
                   "但 18:36 同一台机器同一脚本还能推上去 —— 说明可用窗口是时段性的，不是段错了。",
        "cause": "校园网/DNS 做了重定向或加速，github.com 的解析结果指向校内镜像节点（20.6.7.17）。\n"
                 "这条链路的可达性和 140.82.x.x 完全无关 → 探针扫的是「另一批机器」，自然永远扫不到。\n"
                 "更麻烦的是：把 git config 里绑定的 IP 清掉、让 git 走 DNS 时，那条路也会被时段性限流 reset。\n"
                 "→ 结论：DNS 路和 IP 路是两条独立的、都会时段性失效的路，不能指望其中一条兜底。",
        "solutions": [
            "【先看清楚】push 失败第一步跑 nslookup github.com，确认本机 DNS 把它解析到哪 —— 这一步以前一直被跳过",
            "【两路并行】探针扫 140.82.x.x（官方段）+ 直连 DNS 解析出来的地址，两条路各自试",
            "【别死磕】校园网下 GitHub 可用窗口只有几十秒（T20/T22 已记），扫不到就等 5~10 分钟再跑，别连扫",
            "【备选】gitcode remote 已配好（国内线路），但需要先在网页建同名仓库，否则 403 仓库不存在",
            "【判断口诀】“我扫了 10 轮都没活 IP”有两种截然不同的原因：段错了（探针白扫） vs 时段没到（等就行）"
            "—— 用 nslookup 区分，别一律归因为“网络不稳”",
        ],
        "tags": ["DNS", "校园网", "github", "探针", "网段", "时段性限流", "push", "20.6.7.17"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    })
    print("✅ 已写入 T28")

gzk.save(db)
print("✅ 已保存并 render")
