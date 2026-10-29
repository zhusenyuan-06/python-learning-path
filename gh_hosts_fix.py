# gh_hosts_fix.py —— 修复 Windows hosts 里的 GitHub 解析
# 2026-10-29 · 阶段1 第5周 · 工具链排障
#
# 配套文件：修复GitHub访问_v3.bat（双击它，它会调本文件）
#
# ---------------------------------------------------------------
# 这个文件回答一个问题：浏览器打不开 github.com，怎么修？
#
# 【环境事实（2026-10-29 实测）】
#   ① 系统 DNS 完全超时 —— nslookup github.com 四次全 timeout
#      → 所以 hosts 必须有绑定，没绑定浏览器根本打不开
#   ② 但 hosts 里绑的 185.199.110.133（raw/gist）已整段不可达
#      → 185.199.108~111 扫了 12 个候选全 000，是校园网掐了整个段
#   ③ Azure 中国段 20.27.177.113 连测 3 次全 200（0.57~0.79 秒）
#      → 它比 GitHub 美国边缘 140.82.x.x 稳定得多（后者十分钟换一轮）
#   ④ hosts 的标准内容（127.0.0.1 localhost 等）在 10-27 就被误删了，
#      三个备份都是同一份 457 字节，救不回来 → 本脚本补回来
#
# 【和 v2 的区别 —— 为什么重写】
#   v2 用 bat 的 `>> tmp echo <python代码>` 逐行拼一个临时 py 文件。
#   ❌ 这条路是错的：bat 里的 `>` 是重定向符，
#      那行 `echo     if len(parts) >= 2:` 里的 `>=` 被 cmd 解释成
#      「输出到名为 `= 2:` 的文件」，于是这一行从临时 py 里消失了，
#      后面的行整体上移一行 → IndentationError（实测复现，见
#      笔记/_自检脚本/_诊断bat_echo缩进.py）。
#   ✅ 本版：Python 独立成文件，bat 只负责提权 + 调用。
#      一个转义字符都不用经过 cmd。
#
# 【安全设计 —— 三道保险】
#   ① 改之前一定备份（桌面，带时间戳）
#   ② 最小改动：现有能用的绑定一律保留，只补缺的和修坏的
#   ③ 写完立刻校验，不通过自动回滚到备份
#
# 跑法：
#   "D:\AAAA\python.exe" gh_hosts_fix.py            # 正常修复
#   "D:\AAAA\python.exe" gh_hosts_fix.py --dry-run  # 只看会改成啥，不写
# ---------------------------------------------------------------

import datetime
import os
import shutil
import subprocess
import sys

# ---------------------------------------------------------------
# 常量
# ---------------------------------------------------------------

# hosts 文件的绝对路径
#   └─ Windows 的 hosts 不在 etc/hosts（在 Linux/macOS 才是），
#     是在 System32\drivers\etc\hosts
HOSTS = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                     "System32", "drivers", "etc", "hosts")

# 系统的 curl.exe（Windows 10 1803+ 自带）
#   └─ 用它做探测，因为 curl 支持 --resolve（强制指定 IP + 正确 SNI），
#     能测出「这个 IP 到底能不能承载这个域名」
CURL = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"),
                    "System32", "curl.exe")

# web 段候选：优先 Azure 中国段（稳定），再退到 GitHub 美国边缘（不稳）
#   └─ ⚠️ 顺序有意义：Azure 段能撑很久，美国边缘十分钟就换一轮
#   └─ 但 2026-10-29 19:2x 实测：Azure 段 20.27.177.113 也断了 ——
#     「可达 IP 会轮换」是普遍规律，不只美国边缘。
#     所以候选池要宽，探测要重试，工具要能随时重跑。
WEB_CANDS = [
    # --- Azure 中国区段（优先，实测更耐用）---
    "20.27.177.113", "20.200.245.247", "20.27.177.116",
    "20.207.73.82", "20.233.83.113", "20.90.168.113",
    # --- GitHub 美国边缘段（140.82.112.0/20，官方公布的那段）---
    "140.82.112.3", "140.82.112.4", "140.82.113.3", "140.82.113.4",
    "140.82.114.3", "140.82.114.4", "140.82.115.3", "140.82.115.4",
    "140.82.116.3", "140.82.116.4", "140.82.117.3", "140.82.117.4",
    "140.82.118.3", "140.82.118.4", "140.82.119.3", "140.82.119.4",
    "140.82.120.3", "140.82.120.4", "140.82.121.3", "140.82.121.4",
]

# api 段候选：GitHub 的 api 边缘是【另一段网段】（.5 / .6 结尾）
#   └─ 这就是 T17 的结论：api.github.com 用 web 段的 IP 会 301 出问题
#   └─ 但 Azure 段是例外（实测 20.27.177.113 能同时承载 web 和 api）
API_CANDS = [
    "20.27.177.113", "20.200.245.247", "20.27.177.116",
    "20.207.73.82", "20.233.83.113", "20.90.168.113",
    "140.82.112.5", "140.82.112.6", "140.82.113.5", "140.82.113.6",
    "140.82.114.5", "140.82.114.6", "140.82.116.5", "140.82.116.6",
    "140.82.121.5", "140.82.121.6",
]

# raw 段候选（raw.githubusercontent.com / gist.githubusercontent.com 用的 CDN 段）
#   └─ 现在整个 185.199.x 段在校园网不可达，探测只是确认一下，
#     万一哪天恢复了就能自动用上
RAW_CANDS = [
    "185.199.108.133", "185.199.109.133", "185.199.110.133", "185.199.111.133",
    "185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153",
]

# web 段要绑的域名（都走同一个 IP）
WEB_HOSTS = ["github.com", "api.github.com", "codeload.github.com",
             "objects.githubusercontent.com"]

# raw 段要绑的域名
RAW_HOSTS = ["raw.githubusercontent.com", "gist.githubusercontent.com"]

# 标准 hosts 模板（Windows 官方默认内容）
#   └─ 原来的内容在 10-27 被误删了，这里补回来
#   └─ 127.0.0.1 / ::1 localhost 我【取消注释】了 ——
#     新版 Windows 默认是注释掉的（说"localhost 由 DNS 解析"），
#     但显式写上更稳，有些本地服务（数据库、Redis）依赖它
STD_HEADER = """# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
#      102.54.94.97     rhino.acme.com          # source server
#       38.25.63.10     x.acme.com              # x client host

127.0.0.1       localhost
::1             localhost
"""


# ============================================================
# 工具函数
# ============================================================
def probe_once(host, ip, path="/", timeout=6):
    """只探一次，返回状态码字符串；"000" = 连不上。

    逐行拆解：
        subprocess.run([...])
          └─ 用【列表】传参数，不经过 shell，引号和 & 都不会被解释
          └─ --noproxy "*" = 不走任何代理（WorkBuddy/公司代理会让结果失真）
          └─ --resolve "域名:443:IP" = 强制用这个 IP 连接，
            但仍然用正确的 SNI 和 Host 头 —— 这才能测出
            「这个 IP 是否真的服务这个域名」
          └─ --connect-timeout / --max-time = 两道超时，防止卡死
          └─ -w "%{http_code}" = 结束后打印状态码
            ⚠️ 状态码判定不能一刀切要 200：
               api.github.com 的根路径会 301（跳主站，属正常）
               raw 根路径也是 301，只有 github.com/login 稳定是 200
    """
    cmd = [CURL, "-s", "-o", "nul", "--noproxy", "*",
           "--connect-timeout", "4", "--max-time", str(timeout),
           "--resolve", "%s:443:%s" % (host, ip),
           "-w", "%{http_code}", "https://%s%s" % (host, path)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 4)
    except Exception:
        return "000"
    code = (r.stdout or "").strip()
    # ⚠️ 必须是 3 位数字【且不是 000】
    #   000 = curl 连都没连上，不是有响应
    #   （第一版写成 isdigit() 就够了，把 "000" 也当成通过 —— 假阳性）
    if len(code) == 3 and code.isdigit() and code != "000":
        return code
    return "000"


def probe(host, ip, path="/", timeout=6, tries=3):
    """探测「某个 IP 能不能承载某个域名」，**最多试 tries 次**。

    为什么必须重试（2026-10-29 实测）：
      这个网络对 raw.githubusercontent.com 有约 50% 的丢包 ——
      连测 10 次是 5 次 301、5 次 000。
      单次探测的结果有一半是假的，会导致：
        · 把活 IP 判成死的 → 好绑定被换掉
        · 把死 IP 判成活的 → 死绑定被留下
      所以规则是：**任一次成功就算活**（宽松），
      全都失败才算死（严格）。
      这样两个方向都判对了。

    返回：第一次拿到的非 000 状态码；全失败则返回 "000"。
    """
    for _ in range(tries):
        code = probe_once(host, ip, path, timeout)
        if code != "000":
            return code
    return "000"


def probe_ok(host, ip, path="/", timeout=6, tries=3):
    """布尔版：链路是否通（任一次拿到非 000 的状态码就算通）。"""
    return probe(host, ip, path, timeout, tries) != "000"


def read_hosts(path):
    """读 hosts 全文。返回 (文本, 是否成功)。

    编码处理：
      Windows 的 hosts 可能是 UTF-8 / GBK / ANSI。
      逐个试，第一个能解的就用；全都失败就用 utf-8 + errors='replace'
      兜底（宁可有乱码也不能读不出来）。
    """
    for enc in ("utf-8", "mbcs", "latin-1"):
        try:
            with open(path, "r", encoding=enc, errors="replace") as f:
                return f.read(), True
        except Exception:
            continue
    return "", False


def write_hosts(path, text):
    """把文本写回 hosts。写之前会先把原文件备份。

    返回备份路径（失败返回 None）。

    ⚠️ 关键：必须用 newline='\r\n'
      Windows 的 hosts 期望 CRLF。用 LF 写的话，
      部分程序会解析异常（表现为「明明写进去了却没生效」）。
    """
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = os.path.join(os.path.expanduser("~"), "Desktop",
                          "hosts_backup_%s.bak" % stamp)
    try:
        shutil.copy2(path, backup)
    except Exception as e:
        print("  [!] 备份失败：%s" % e)
        return None
    with open(path, "w", encoding="utf-8", errors="replace", newline="\r\n") as f:
        f.write(text)
    return backup


def parse_github_entries(text):
    """从 hosts 文本里找出所有 GitHub 相关绑定。

    返回 [(域名小写, IP), ...]

    逐行拆解：
        for line in text.splitlines()
          └─ splitlines() 按行切分（自动处理 CRLF / LF）
        s = line.strip()
          └─ strip() 去掉首尾空白（行尾可能有 \r）
        if not s or s.startswith("#"):
          └─ 空行和注释行跳过
        parts = s.split()
          └─ 按空白切成列表：["20.27.177.113", "github.com"]
          └─ 分隔符是「连续空白」，多个空格也行
        if len(parts) >= 2:
          └─ 至少要有 IP 和域名两个部分
    """
    found = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) >= 2:
            name = parts[1].lower()
            if "github" in name:
                found.append((name, parts[0]))
    return found


def build_hosts(old_text, web_ip, api_ip, raw_ip, raw_ok):
    """组装新的 hosts 全文。

    组成结构：
        [1] 标准模板（补回被误删的 localhost 等）
        [2] 旧文件里【非 GitHub】的行原样保留（不能误删别人的东西）
        [3] 新的 GitHub 块（带起止标记，方便以后再删）

    逐行拆解：
        web_ip 和 api_ip 是【两个】IP
          └─ T17：api.github.com 和 github.com 在 GitHub 那边是不同的网段，
            用错会 301 出问题
          └─ 但 Azure 中国段是例外（实测同一个 IP 能同时承载两者），
            所以 api_ip 有可能和 web_ip 相同
    """
    kept = []
    in_old_block = False
    for line in old_text.splitlines():
        s = line.strip()
        low = s.lower()

        # --- 按【块】删除旧的 GitHub 段 ---
        #   不能只靠「这行含不含 GitHub」来判断 ——
        #   旧块里还有「# 原因：校园网 DNS 把 github.com 解析到不通的 IP」
        #   这种不含关键字的说明行。
        #   正确做法：遇到「开始」标记就进入删除状态，
        #   一直删到「结束」标记为止，整块拿掉。
        if not in_old_block:
            if s.startswith("#") and ("开始" in s or "fix start" in low
                                      or "加速开始" in s):
                in_old_block = True
                continue
        else:
            # 还在旧块里
            if s.startswith("#") and ("结束" in s or "fix end" in low
                                      or "加速结束" in s):
                in_old_block = False      # 遇到结束标记，退出删除状态
            continue                     # 旧块内的所有行一律丢掉

        if not s:
            continue                     # 空行不留（后面统一用 \n 连接）
        if s.startswith("#"):
            kept.append(line)            # 别的注释保留
            continue
        parts = s.split()
        if len(parts) >= 2 and "github" in parts[1].lower():
            continue                     # 旧的 GitHub 绑定，丢掉，下面重写
        kept.append(line)                # 别人的映射，【必须原样保留】

    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    block = [
        "",
        "==== GitHub fix start %s ====" % stamp,
        "# web 段：github.com / codeload / objects",
        "# 生成方式：双击桌面「修复GitHub访问_v3.bat」自动探测并写入",
        "# 注意：可达 IP 会随时间轮换，打不开时重新双击一次本工具即可",
        "%s    github.com" % web_ip,
        "%s    codeload.github.com" % web_ip,
        "%s    objects.githubusercontent.com" % web_ip,
    ]
    if api_ip:
        block.append("# api 段：GitHub 的 api 是另一段网段（T17），单独选")
        block.append("%s    api.github.com" % api_ip)
    else:
        block.append("# api 段本次没探测到可用 IP，api.github.com 暂时不绑定")
    if raw_ok and raw_ip:
        block.append("# raw 段：GitHub 静态资源 CDN（该段有约 50% 抖动，属校园网限制）")
        block.append("%s    raw.githubusercontent.com" % raw_ip)
        block.append("%s    gist.githubusercontent.com" % raw_ip)
    else:
        block.append("# raw 段当前不可达（185.199.x 整段被校园网限制）")
        block.append("# raw.githubusercontent.com 暂时打不开 —— 已知问题，不影响 git 操作")
        block.append("# gist.githubusercontent.com 暂时打不开 —— 已知问题，不影响 git 操作")
    block.append("==== GitHub fix end %s ====" % stamp)
    block.append("")

    return STD_HEADER + "\n".join(kept) + "\n".join(block) + "\n"


# ============================================================
# 主流程
# ============================================================
def main():
    """探测 → 组装 → 备份 → 写入 → 校验 → 失败回滚。

    逐行拆解：
        global HOSTS
          └─ global = 声明「我要改模块级变量」
            （函数里想修改全局变量必须先声明，否则会被当成新建局部变量）
          └─ 为什么要能改：测试时可以指向副本，
            先在副本上把「写入 + 校验 + 回滚」整条链路跑通，
            再让它动真的 hosts
        dry_run = "--dry-run" in sys.argv
          └─ 只看会改成啥，不真的写（先看再动手）
        text, ok = read_hosts(HOSTS)
          └─ 先读原文 —— 「保留非 GitHub 行」和「备份」都要用
        old = parse_github_entries(text)
          └─ 现有的 GitHub 绑定
        for name, ip in old:
          └─ 逐个验证现有绑定还活着吗
            活 → 保留（最小改动，别把好的搞坏）
            死 → 换新的
    """
    global HOSTS
    if "--hosts" in sys.argv:
        i = sys.argv.index("--hosts")
        if i + 1 < len(sys.argv):
            HOSTS = sys.argv[i + 1]

    dry_run = "--dry-run" in sys.argv

    print("=" * 62)
    print("  GitHub hosts 修复 v3   2026-10-29")
    print("=" * 62)
    print("  hosts 路径：%s" % HOSTS)
    print("  模式：%s" % ("只看不改（dry-run）" if dry_run else "真的修改"))
    print()

    # ---- 1. 读现状 ----
    text, ok = read_hosts(HOSTS)
    if not ok:
        print("[X] 读不到 hosts，退出")
        return 1
    old = parse_github_entries(text)
    print("[1] 现有 GitHub 绑定：")
    if old:
        for name, ip in old:
            print("      %-32s %s" % (name, ip))
    else:
        print("      （无）")
    print()

    # ---- 2. 逐个验证现有绑定 ----
    print("[2] 验证现有绑定是否还活着 ...")
    alive_web = []
    for name, ip in old:
        # github.com/login 稳定返回 200，用它做严格判定
        #   └─ 其它域名（api/codeload/objects）根路径可能 301，
        #     那是正常重定向，用「非 000」判定即可
        if name == "github.com":
            good = probe(name, ip, "/login") == "200"
        else:
            good = probe_ok(name, ip, "/")
        mark = "OK" if good else "死"
        print("      %-32s %-16s %s" % (name, ip, mark))
        # 只把【web 段】的域名收进候选池
        #   └─ api 段单独在第 4 步找（T17：不同网段）
        if good and name in ("github.com", "codeload.github.com",
                             "objects.githubusercontent.com"):
            if ip not in alive_web:
                alive_web.append(ip)
    print()

    # ---- 3. 找 web 段 IP ----
    web_ip = None
    for ip in alive_web:
        if probe("github.com", ip, "/login") == "200":
            web_ip = ip
            break
    if web_ip is None:
        print("[3] 现有 web 绑定全死，重新探测 web 段 ...")
        for ip in WEB_CANDS:
            if probe("github.com", ip, "/login") == "200":
                web_ip = ip
                print("      选中 %s" % ip)
                break
    else:
        print("[3] 沿用现有可用的 web IP：%s（最小改动）" % web_ip)
    if web_ip is None:
        print()
        print("[X] 找不到任何可用的 web IP —— 可能整个 GitHub 段此刻不可达")
        print("    过几分钟再跑一次，或改用 GitCode")
        return 2
    print()

    # ---- 4. 找 api 段 IP（T17：api 是另一段网段）----
    print("[4] 探测 api 段（api.github.com 是另一段网段）...")
    api_ip = None
    for ip in API_CANDS:
        # api 根路径返回 301 是正常的，所以用宽松判定
        if probe_ok("api.github.com", ip, "/"):
            api_ip = ip
            print("      选中 %s" % ip)
            break
    if api_ip is None and probe_ok("api.github.com", web_ip, "/"):
        # 兜底：web 段这个 IP 恰好也能承载 api（Azure 段就是这样）
        api_ip = web_ip
        print("      api 段没单独探到，但 web IP %s 也能承载 api，沿用它" % web_ip)
    if api_ip is None:
        print("      本次没找到可用 api IP")
    print()

    # ---- 5. 找 raw 段 IP ----
    print("[5] 探测 raw 段（raw/gist 用的 185.199.x 段）...")
    raw_ip, raw_ok = None, False
    for ip in RAW_CANDS:
        if probe_ok("raw.githubusercontent.com", ip, "/"):
            raw_ip, raw_ok = ip, True
            print("      选中 %s" % ip)
            break
    if not raw_ok:
        print("      整段当前不可达（校园网限制），会写成「已知问题」注释")
    print()

    # ---- 6. 组装 + 备份 + 写入 ----
    new_text = build_hosts(text, web_ip, api_ip, raw_ip, raw_ok)
    print("[6] 新 hosts 预览（前 25 行）：")
    for line in new_text.splitlines()[:25]:
        print("      " + line)
    print("      ... 共 %d 行" % len(new_text.splitlines()))
    print()

    if dry_run:
        print("[dry-run] 没有写入任何东西。去掉 --dry-run 就会真的改。")
        return 0

    # ---- 7. 备份 + 写入 ----
    backup = write_hosts(HOSTS, new_text)
    if backup is None:
        print("[X] 备份失败，没有写入（保险起见）")
        return 1
    print("[7] 已备份 → %s" % backup)
    print("    已写入 → %s" % HOSTS)
    print()

    # ---- 8. 校验（不通过就回滚）----
    #   ⚠️ 校验要区分两类问题：
    #     「致命」= 文件写坏了（localhost 丢了、绑定没写进去）→ 必须回滚
    #     「网络」= 连不上（可能是抖动）→ 重试几次再判，别误回滚
    print("[8] 校验 ...")
    check, _ = read_hosts(HOSTS)
    fatal = []
    if "127.0.0.1" not in check or "localhost" not in check:
        fatal.append("localhost 条目丢失")
    for name in ("github.com", "codeload.github.com",
                 "objects.githubusercontent.com"):
        if name not in check:
            fatal.append("%s 绑定丢失" % name)
    if api_ip and "api.github.com" not in check:
        fatal.append("api.github.com 绑定丢失")

    net_ok = False
    for _ in range(3):
        if probe("github.com", web_ip, "/login") == "200":
            net_ok = True
            break
    if not net_ok:
        fatal.append("github.com 连不通（已重试 3 轮）")

    if fatal:
        print("    [!] 校验不通过：%s" % "；".join(fatal))
        print("    自动回滚 ...")
        try:
            shutil.copy2(backup, HOSTS)
            print("    已回滚到备份，原文件恢复")
        except Exception as e:
            print("    [!] 回滚失败：%s（请手动从 %s 恢复）" % (e, backup))
        return 1
    print("    全部通过")
    print()
    print("=" * 62)
    print("  完成。现在开着的浏览器按 Ctrl+Shift+R 硬刷新。")
    print("  web IP : %s" % web_ip)
    print("  api IP : %s" % (api_ip or "（本次没探到，api 暂时不绑定）"))
    print("  raw IP : %s" % (raw_ip if raw_ok else "（当前不可达）"))
    print()
    print("  提醒：可达 IP 会随时间轮换。以后打不开 github.com，")
    print("        重新双击一次「修复GitHub访问_v3.bat」就行。")
    print("=" * 62)
    return 0


# __name__ == "__main__" = 只在直接运行时执行
if __name__ == "__main__":
    sys.exit(main())
