# -*- coding: utf-8 -*-
"""写入工具链坑 T39（2026-11-15 17:35，收尾 push 时踩的）

T39: 探针只认 200 → 把返回 404 的活 IP 判死 → 误报「GitHub 全挂」。
     加上「两条路都失败」其实是瞬时快照，等 40 秒重试 DNS 路就直接推成功了。
"""
import datetime
import os
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
TRACK = os.path.join(HERE, "..", "工具链", "工具链坑.py")

spec = importlib.util.spec_from_file_location("gzk", TRACK)
gzk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gzk)

db = gzk.load()
今天 = datetime.date.today().isoformat()

新增 = [
    {
        "id": "T39",
        "title": "探针只认 200 把 404 判成死 IP；且「两条路都不通」只是瞬时快照，重试 DNS 路就成功了",
        "symptom": "2026-11-15 17:30 收尾 push，走 push_github.sh：\n"
                   "  ① 前置自检正常打印 13 条坑；探针扫 78 个 IP → 报「本次扫描没有活 IP」\n"
                   "  ② 脚本改走 DNS 路 → Failed to connect ... after 21096 ms\n"
                   "  ③ 脚本结论：「两条路都不通 —— 等 5~10 分钟再跑」\n"
                   "但单独完整跑探针（不带 tail 截断）发现：\n"
                   "     140.82.112.6     404\n"
                   "     140.82.114.5     404\n"
                   "  → 404 说明 TCP 连上 + TLS 握手成功 + HTTP 有响应，【链路明明是活的】，\n"
                   "    只是被 web 段的 ok_codes = {\"200\"} 判成了死。\n"
                   "接着按 T23 手工绑这两个 IP 逐个试 push → 都返回 403（服务端拒绝，非网络故障）。\n"
                   "最后【什么都没改、只隔了约 40 秒】再试一次 DNS 路：\n"
                   "     df1f1a3..9d2b5e1  main -> main   退出码 0  ← 7 个 commit 全推上去了\n"
                   "→ 真实情况既不是「GitHub 全挂」，也不是「要等 5~10 分钟」。",
        "cause": "三个误判叠在一起：\n"
                 "  ① 【判据太严】web 段只认 200。api 段的注释里早就写过同一个坑\n"
                 "     「按必须 200 判活 → 整段 IP 全被判成死的，判据错了不是网络错了」，\n"
                 "     但 web 段没同步修。这是 T31 心法里的第 ③ 种：判定标准太严。\n"
                 "  ② 【403 被当网络故障】403 是服务端明确拒绝（凭证/SNI/镜像节点），\n"
                 "     和「连不上」是两件事，不该并入「网络不通」一起等。\n"
                 "  ③ 【把瞬时快照当恒定事实】T20 说的是「IP 池十几秒换一轮」，\n"
                 "     那「两条路都失败」也只代表刚才那一瞬；脚本建议等 5~10 分钟太久，\n"
                 "     实测 40 秒后 DNS 路就通了。\n"
                 "  ④ 附带：我用 `tail -60` 看探针输出，把 404 那几行截掉了，\n"
                 "     差点漏掉唯一的有效线索。",
        "solutions": [
            "【已修】probe_gh.py web 段 ok_codes 从 {\"200\"} 放宽为\n"
            "  {\"200\", \"404\", \"400\", \"403\", \"301\", \"302\"}（与 api 段一致）；\n"
            "  并把 200 排最前、其余降级为兜底 —— 避免 403 的 IP 抢在 200 前面试。",
            "【判定原则】拿到任何 HTTP 状态码 = 链路通；状态码只说明「服务端怎么回」，\n"
            "  不说明「网络通不通」。tcp-fail / tls/http-fail 才是网络问题。",
            "【403 单独归类】403 = 服务端拒绝，别跟超时混在一起等；\n"
            "  这时应换 IP 或改走 DNS 路，而不是继续在这条路上等窗口。",
            "【失败后立刻重试】两条路都失败 → 先【立刻】重试一次 DNS 路（40 秒级），\n"
            "  别真按脚本说的等 5~10 分钟。T20 的窗口轮换是双向的：会关也会开。",
            "【输出别截断】排查网络问题时不要用 tail -n 60 看探针结果 ——\n"
            "  活 IP 往往散落在中间。要看就存文件后 grep `<== 活` 或 `LIVE_IPS=`。",
            "【主判据不变】推成功只认 push 退出码 0 + `<old>..<new>  main -> main`（T30）。\n"
            "  本次网页独立通道给出的是缓存的旧 SHA c28e835，没推翻主判据；\n"
            "  再查 /commit/9d2b5e1 页面确认存在，才最终闭环。",
            "【已生效】T39 一句话摘要已加进 工具/push_前置自检.py 的 PUSH_PITFALLS，\n"
            "  下次 push 会和其他 13 条一起被打到屏幕上。",
        ],
        "tags": ["GitHub", "push", "探针", "判据", "T31", "T20", "T30", "误判", "404", "403"],
        "hits": 1,
        "first_hit": 今天,
        "last_hit": 今天,
    },
]

for 条目 in 新增:
    if any(x["id"] == 条目["id"] for x in db["items"]):
        print("⚠️ %s 已存在，跳过" % 条目["id"])
    else:
        db["items"].append(条目)
        print("✅ 已写入 %s" % 条目["id"])

gzk.save(db)
print("✅ 已保存并 render")
