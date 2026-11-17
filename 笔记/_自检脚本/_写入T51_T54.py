# -*- coding: utf-8 -*-
"""写入 T51~T54（2026-11-17 19:2x push GitHub 实战踩坑：探针全灭但 DNS 解析出的 IP 才能 push）"""
import json
import datetime
from pathlib import Path

坑文件 = Path(r'D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject/笔记/工具链/工具链坑.json')

d = json.loads(坑文件.read_text(encoding='utf-8'))
print('原有条数:', len(d['items']))
已有 = {it['id'] for it in d['items']}

新坑们 = [
    {
        'id': 'T51',
        'title': '探针扫 140.82.x 官方段全灭时别放弃 —— DNS 解析出来的那个 IP 恰恰是唯一能 push 的',
        'hits': 1,
        'severity': '高',
        '场景': '2026-11-17 19:26 往 GitHub 推 13 个 commit，push_github.sh 探活 + 逐 IP push 全部失败',
        '现象': '探针 20 个 140.82.x 官方 IP：绝大多数 tls/http 超时，活的几个分别报 403 / schannel missing close_notify；'
                '走 DNS 路（学校解析到 20.27.177.113）也 21 秒连不上 → 脚本判「两条路都不通」',
        '原因': '探针（T31）只扫 140.82.x + 少量亚太候选，没把「当前 DNS 实际解析到的 IP」当 push 候选；'
                '而这次真正能完成 POST 的是 20.27.177.113 —— 正是学校 DNS 给的那个地址',
        '教训': '⛔ 「探针没扫到活 IP」≠「推不上去」⛔ 学校 DNS 解析到的节点未必是镜像，可能就是能用的边缘节点',
        '怎么防': '① push 候选集 = 探针活 IP ∪ DNS 解析 IP ∪ 手动确认过的常备 IP ② 两者都失败时先做 POST 探针再下结论（T52）'
                  '③ 别因为「看起来是校园镜像」就排除它',
        '实测结果': '绑 github.com → 20.27.177.113 后 git push 一次成功：bdbea34..acdaeb1  main -> main',
        '发现时间': '2026-11-17',
    },
    {
        'id': 'T52',
        'title': '判断某个 IP 能不能 push，用 curl POST 探针（秒级），别拿 git push 试错（每错一次 21 秒）',
        'hits': 1,
        'severity': '高',
        '场景': '一轮探活拿到 6 个「活 IP」，逐个 git push 试错',
        '现象': '每个失败 IP 都要等 21 秒超时，6 个 IP ≈ 2 分钟，还是没推上去；而且 git 的报错（403 / schannel 错误）'
                '看不出到底差在哪',
        '原因': 'git push 是「认证 + POST packfile」的复合动作，失败原因被混在一条 fatal 里；'
                '而判断「这台机器能不能收我的 POST、凭据对不对」只需一次裸 POST',
        '教训': '⛔ 「探活」只测了 GET（info/refs），推不推得上去要看 POST 通道 ⛔ T16 说 GET 通≠POST 通，但没说怎么测 POST',
        '怎么防': 'POST 探针（秒级，判读见下）：\n'
                  'curl -s -o /dev/null -w "%{http_code}" --resolve github.com:443:$IP -u "user:token" \\\n'
                  '  -X POST -H "Content-Type: application/x-git-upload-pack-request" --data 0000 \\\n'
                  '  https://github.com/OWNER/REPO.git/git-receive-pack\n'
                  '判读：200=认证通过可推｜404=这台是 api 段机器（拿 web 端点问它）｜403=凭据/权限没带上｜'
                  '400=机器在但请求体不合法｜000=链路不通',
        '实测结果': '8 个 IP 一次扫完（18 秒）：20.27.177.113→200、20.200.245.247→200、4.237.22.38→200、'
                    '140.82.121.6→400、140.82.112.5/114.5→404（api 段机器）、4.237.22.39→403、20.205.243.168→400',
        '发现时间': '2026-11-17',
    },
    {
        'id': 'T53',
        'title': 'curl 能 POST 通、git 却连不上时，别急着把 IP 判死 —— 两者的 TLS/HTTP 栈不一样',
        'hits': 1,
        'severity': '中',
        '场景': '同一次排查里：curl（系统 Schannel 版）对 20.27.177.113 POST 返回 200，git 却报「21 秒连不上」',
        '现象': '同一个 IP、同一个端口，curl 秒回 200，git 却超时 21 秒 → 差点判成「IP 死了」而错过唯一可用节点',
        '原因': 'git 用自带的 libcurl，curl 命令行用的是另一套（后端/CA/TLS 参数都不同）；校园网/运营商链路对两者的处理不一样',
        '教训': '⛔ 「curl 通」和「git 通」是两个独立事实 ⛔ 换 IP 之前先把两种客户端的表现都摆出来',
        '怎么防': '① 先用 curl POST 探针筛出候选 IP，再用 git push 验证（curl 筛，git 推）② '
                  'git 侧失败时先比状态码矩阵，别把「curl 通但 git 不通」直接等同于「IP 不可用」',
        '发现时间': '2026-11-17',
    },
    {
        'id': 'T54',
        'title': 'GitHub 加速镜像（gh-proxy 等）只代理 GET，push 会回「No anonymous write access」',
        'hits': 1,
        'severity': '中',
        '场景': 'HTTPS 直连和绑 IP 都不通时，试着走 gh-proxy.com / ghfast.top / ghproxy.net 等镜像',
        '现象': '① curl GET info/refs 一律 200（看着很美）② 真正 push 时 gh-proxy 回 '
                '「remote: No anonymous write access.」→ Authentication failed ③ 另外 GCM 里没有镜像 host 的凭据条目，'
                'git 报「Cannot prompt because user interactivity has been disabled」',
        '原因': '这类镜像的机制是「代理用自己的账号去拉」，不转发客户端的 Authorization 头，'
                '所以只读不写；GCM 的 credential.helper=manager 只认 github.com 一个 host',
        '教训': '⛔ 镜像能 ls-remote 通 ≠ 能 push ⛔ GIT_TERMINAL_PROMPT=0 时连 GIT_ASKPASS 都不会被问（要留 =1）',
        '怎么防': '① 镜像只当【校验通道】（T30 的独立通道之一）② 镜像 push 要 URL 内嵌 token 或 '
                  '-c credential.helper= + GIT_ASKPASS 且 GIT_TERMINAL_PROMPT=1 ③ '
                  '看到 "No anonymous write access" 直接判定此路只读，别再试',
        '实测结果': 'gh-proxy.com 的 ls-remote 成功（读到远端 sha）→ 正好用来做 T30 的独立校验；push 失败如上',
        '发现时间': '2026-11-17',
    },
]

added = 0
for 坑 in 新坑们:
    if 坑['id'] in 已有:
        print('跳过已存在:', 坑['id'])
        continue
    d['items'].append(坑)
    added += 1
    print('✅ 写入', 坑['id'], 坑['title'][:46])

d['updated'] = datetime.datetime.now().strftime('%Y-%m-%d')
坑文件.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
print('新增 %d 条，现共 %d 条' % (added, len(d['items'])))
