# -*- coding: utf-8 -*-
"""写入工具链坑 T30（2026-11-14 晚，push 收尾时踩的）

T30: 校验远端不能用 ls-remote —— 它和 push 走同一条链路，
     窗口一关就误判成「推送失败」，其实早就推上去了
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

if any(x["id"] == "T30" for x in db["items"]):
    print("⚠️ T30 已存在，跳过")
else:
    db["items"].append({
        "id": "T30",
        "title": "校验远端别只用 ls-remote —— 它和 push 走同一条链路，窗口一关就误判「推送失败」",
        "symptom": "2026-11-14 20:05 跑 push_github.sh：\n"
                   "  push 那一步明确成功：\"2ed19b9..c28e835  main -> main\"（git 的成功输出格式）\n"
                   "  紧接着第 3 步校验：git ls-remote → 连不上\n"
                   "  → 脚本报「不一致，请复查」，退出码 1\n"
                   "重试 ls-remote（走 DNS 路）→ Connection was reset，两条路都连不上。\n"
                   "但用完全独立的通道（GitHub 网页）一查，c28e835 就在远端，push 早就成功了。",
        "cause": "**push 和 ls-remote 走的是同一条网络链路**（同一个 github.com 边缘 IP 池）。\n"
                 "校园网下这个窗口只开几十秒（T20/T28）：push 抢在窗口末尾成功了，\n"
                 "紧接着的 ls-remote 就撞上窗口关闭 → 连接被 reset。\n"
                 "→ 校验工具和被校验对象共享同一个故障域，校验结果不可信。\n"
                 "T18 记的是「push 报失败但其实推上去了」；T30 是它的镜像：「push 报成功但校验说失败了」。",
        "solutions": [
            "【判据先分清】git push 输出 \"<old>..<new>  <branch> -> <branch>\" 就是成功，"
            "这是服务端 ref 真的更新了才会出现的格式",
            "【校验换通道】ls-remote 失败时，改用【完全独立的通道】验证：GitHub 网页 commits 页 / GitHub API",
            "【实测】2026-11-14 用网页通道查 GitHub commits 页，一次就看到 c28e835 在远端 —— "
            "而同一时刻 ls-remote 连续失败 2 次",
            "【脚本改造】push_github.sh 的校验逻辑要改成三级：① ls-remote（快）→ ② GitHub API（api.github.com，"
            "不同边缘段 T17）→ ③ 网页（最独立）；三级全挂才判失败",
            "【心法】**校验工具不能和被校验对象共享故障域** —— 同一条链路上，一次成功一次失败不代表推送有问题，"
            "只代表链路抖了",
            "【补充】GitHub API 校验命令：curl -s https://api.github.com/repos/<user>/<repo>/commits/main "
            "→ 取 .sha 与本地 git rev-parse HEAD 比对",
        ],
        "tags": ["push", "ls-remote", "校验", "误判", "假失败", "T18", "故障域", "GitHub API"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    })
    print("✅ 已写入 T30")

gzk.save(db)
print("✅ 已保存并 render")
