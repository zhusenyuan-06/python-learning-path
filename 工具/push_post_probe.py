# -*- coding: utf-8 -*-
"""
POST 探针 —— 判断哪些 IP 能真正接收 git push（T51/T52/T53）

为什么需要它
------------
旧的 push 流程是「探活 GET → 逐个 git push 试错」：
  - 探活只测 GET（info/refs），推不推得上去要看 POST 通道（T16）
  - 每个失败 IP 要等 21 秒超时，6 个 IP 就是两分钟，还推不上去
今天实测：探针扫的 140.82.x 官方段全灭，真正能 push 的 20.27.177.113
          正是【学校 DNS 解析出来的那个地址】（T51）

本脚本做的事
------------
  候选 IP = DNS 解析结果 ∪ 常备实测可用 IP ∪ 命令行传入的探针活 IP
  对每个候选发一次裸 POST /git-receive-pack，看状态码（T52 判读表）：
    200 = 认证通过，能推   404 = 这台是 api 段机器（拿 web 端点问它）
    403 = 凭据/权限没带上   400 = 机器在但请求体不合法
    000 = 链路不通

输出
----
  POST_OK_IP=<ip1> <ip2> ...   （200 的那些，按可用性排序）

安全
----
  token 不出现在命令行：写进临时 netrc 文件，curl 用 --netrc-file 读，跑完删。
"""
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

OWNER = 'zhusenyuan-06'
REPO = 'python-learning-path'
仓库根 = r'D:/AI应用工程师/01-学习仓库-Python学习路径/pythonProject'

# ---- 1. 候选 IP ----
候选 = []


def 加(ip):
    if ip and ip not in 候选:
        候选.append(ip)


# 1) DNS 实际解析（T51 的主角往往在这里）
try:
    for info in socket.getaddrinfo('github.com', 443, proto=socket.IPPROTO_TCP):
        加(info[4][0])
except Exception as e:
    print('  [!] DNS 解析失败:', e)

# 2) 常备实测可用 IP（2026-11-17 实测 POST 返回 200）
for ip in ('20.27.177.113', '20.200.245.247', '4.237.22.38'):
    加(ip)

# 3) 命令行传入的（探针活 IP）
for ip in sys.argv[1:]:
    for x in ip.split():
        加(x)

# ---- 2. 取 token（写进临时 netrc，不进命令行）----
token = None
try:
    p = subprocess.run(['git', 'credential', 'fill'],
                       input='protocol=https\nhost=github.com\n\n',
                       capture_output=True, text=True, cwd=仓库根, timeout=60)
    for line in p.stdout.splitlines():
        if line.startswith('password='):
            token = line.split('=', 1)[1]
            break
except Exception as e:
    print('  [!] 取 token 失败:', e)

if not token:
    print('  [!] 没有 GitHub token，跳过 POST 探针')
    print('POST_OK_IP=')
    sys.exit(0)

netrc = Path(tempfile.gettempdir()) / '_gh_post_probe_netrc'
netrc.write_text('machine github.com\nlogin %s\npassword %s\n' % (OWNER, token),
                 encoding='utf-8')

env = dict(os.environ)
for k in ('http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY'):
    env.pop(k, None)
env['NO_PROXY'] = '*'

# ---- 3. 逐个 POST 探针 ----
ok = []
for ip in 候选:
    cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
           '--max-time', '12',
           '--netrc-file', str(netrc),
           '--resolve', 'github.com:443:%s' % ip,
           '-X', 'POST',
           '-H', 'Content-Type: application/x-git-upload-pack-request',
           '--data', '0000',
           'https://github.com/%s/%s.git/git-receive-pack' % (OWNER, REPO)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
        code = (r.stdout or '').strip() or 'ERR'
    except Exception:
        code = 'ERR'
    判读 = {'200': '✅ 认证通过·候选优先（不代表 git 能连上 · T55）', '404': 'api 段机器',
            '403': '凭据/权限没过', '400': '机器在·请求体不合法',
            '000': '链路不通（但 git 实推可能反而能用 · T53）'}.get(code, '')
    print('  POST %-16s -> %-4s %s' % (ip, code, 判读), flush=True)
    if code == '200':
        ok.append(ip)

try:
    netrc.unlink()
except Exception:
    pass

print('POST_OK_IP=%s' % ' '.join(ok))
