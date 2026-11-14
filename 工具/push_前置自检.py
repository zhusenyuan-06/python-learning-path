# -*- coding: utf-8 -*-
"""push 前置自检 —— 每次 push GitHub 之前必须先跑这个

用法：
    python 工具/push_前置自检.py          # 自检 + 打印必读坑清单
    python 工具/push_前置自检.py --brief  # 只打印坑清单标题

为什么要有这个脚本：
    「工具链坑」写在文档里不会自己生效 —— 真正被 push 坑到的时候，
    人往往想不起去翻清单（今天 19:20~19:50 就是这么绕的）。
    所以把「开工前必读的那几条坑」直接打印到屏幕上，
    让它变成流程的一部分，而不是靠记性。

覆盖的坑（详见 笔记/工具链/工具链坑.md）：
    T12 四步诊断法 / T13 dry-run 假绿 / T14 代理要 unset / T16 GET≠POST
    T17 web/api 分段 / T18 假失败先查远端 / T19 git config 绑 IP 会过期
    T20 IP 池会轮换 / T22 探活必须并发 / T23 多 IP 要逐个试
    T24 GitCode 脚本退出码骗人 / T27 相对路径+吞 stderr 会静默失败
    T28 DNS 可能被劫持到校园镜像
"""
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
PITFALL_JSON = os.path.abspath(
    os.path.join(REPO, "笔记", "工具链", "工具链坑.json"))

# push 相关的坑：编号 -> 一句话提醒
PUSH_PITFALLS = {
    "T12": "别急着换 IP —— 先按四步诊断法走（DNS → 代理 → 直连 → 再换 IP）",
    "T13": "git push --dry-run 在「本地==远端」时根本不触发认证，会给你假绿",
    "T14": "WorkBuddy 注入的本地代理会让 GitHub 连不通 —— 直连 200、走代理 000",
    "T16": "GitHub 的 GET 通道通 ≠ POST 通道通 —— 换 IP 时要按方法分开测",
    "T17": "github.com 和 api.github.com 不在同一批边缘 IP —— 绑错会被 301 弹走",
    "T18": "git push 报「失败」但服务端其实已经推上去了 —— 别急着重推，先 ls-remote 比对",
    "T19": "git config 里 curloptResolve 绑的 IP 会整段过期 —— 用 git config 改，别碰 hosts",
    "T20": "探活结果会过期 —— 探活和 push 之间别插 sleep，IP 池十几秒就换一轮",
    "T22": "探活必须并发 —— GitHub 可用窗口只开几十秒，串行扫完窗口早关了",
    "T23": "同一轮探活出的多个 IP 必须逐个 push 试 —— 只试第一个会漏",
    "T24": "push_gitcode.sh 失败却照样打印「[OK]」—— 退出码骗人，要看 ls-remote",
    "T27": "脚本里的相对路径 + 被 2>/dev/null 吞掉的 stderr —— 会伪装成「网络问题」",
    "T28": "学校 DNS 可能把 github.com 解析到校园镜像 —— 先 nslookup 看解析到哪",
}


def hr(char="─", n=64):
    print(char * n)


def tip(t):
    print("\033[33m  ⚠ %s\033[0m" % t) if sys.stdout.isatty() else print("  [!] %s" % t)


def ok(t):
    print("\033[32m  ✓ %s\033[0m" % t) if sys.stdout.isatty() else print("  [ok] %s" % t)


def bad(t):
    print("\033[31m  ✗ %s\033[0m" % t) if sys.stdout.isatty() else print("  [X] %s" % t)


def run(cmd):
    """Windows 上 nslookup/git 的输出是 GBK（cp936），强制用 errors='replace' 兜住，
       否则 subprocess 的解码线程会抛 UnicodeDecodeError（2026-11-14 实测）。"""
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           encoding="gbk", errors="replace", timeout=25)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return "<命令出错: %s>" % e


def show_pitfalls():
    print()
    hr("═")
    print("  📌 每次 push GitHub 前必读的坑（共 %d 条）" % len(PUSH_PITFALLS))
    hr("═")
    for tid in sorted(PUSH_PITFALLS, key=lambda x: int(x[1:])):
        print("  %-4s %s" % (tid, PUSH_PITFALLS[tid]))
    hr("═")
    print("  完整清单：笔记/工具链/工具链坑.md")
    print("  完整流程：工具/push_github.sh")
    print()


def check_dns():
    """T28：DNS 可能把 github.com 解析到校园镜像"""
    out = run("nslookup github.com")
    ips = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0].isdigit() and ":" in parts[0]:
            ip = parts[1]
            if ip.count(".") == 3 and not ip.startswith("140.82"):
                ips.append(ip)
    if not ips:
        tip("DNS 解析结果没识别出来（nslookup 格式可能变了）—— 手动确认一下")
        return
    for ip in ips:
        if ip.startswith("140.82."):
            ok("DNS github.com -> %s（GitHub 官方段，正常）" % ip)
        else:
            tip("DNS github.com -> %s（非官方段，可能是校园镜像/加速节点）" % ip)
            print("      → 探针扫的是 140.82.x.x，和这条不是同一批机器（T28）")
            print("      → DNS 这条路可能时段性限流，两条路都要试，别只押一条")


def check_bindings():
    """T19：git config 里绑定的 IP 会过期"""
    out = run('git config --global --get-regexp "curloptResolve"')
    if not out.strip():
        ok("git config 里没有 curloptResolve 绑定（干净）")
        return
    for line in out.strip().splitlines():
        tip("存在绑定（可能已过期，T19）：%s" % line.strip())
    print("      → 探活命中新 IP 后重新绑定；清绑定：")
    print("        git config --global --unset-all "
          "\"http.https://github.com/.curloptResolve\"")


def check_remote():
    """origin 必须指向 GitHub，不能是 GitCode（T24）"""
    out = run("git remote -v")
    if "origin" not in out:
        bad("没有 origin remote")
        return
    seen = set()
    for line in out.splitlines():
        if not line.startswith("origin"):
            continue
        parts = line.split()
        url = parts[1] if len(parts) > 1 else ""
        if url in seen:      # fetch/push 两行 URL 相同，去重只报一次
            continue
        seen.add(url)
        if "github.com" in url:
            ok("origin 指向 GitHub：%s" % url)
        else:
            tip("origin 不是 GitHub：%s" % url)


def check_uncommitted():
    out = run("git status --porcelain")
    if out.strip():
        n = len([x for x in out.strip().splitlines() if x.strip()])
        tip("有 %d 处未提交改动 —— push_github.sh 会自动 git add -A + commit" % n)
    else:
        ok("工作区干净")


def main():
    brief = "--brief" in sys.argv
    print()
    print("=" * 64)
    print("  GitHub push 前置自检   %s" % __import__("datetime").date.today())
    print("=" * 64)

    show_pitfalls()
    if brief:
        return 0

    print("  【自检】")
    check_dns()
    check_bindings()
    check_remote()
    check_uncommitted()
    print()
    print("  自检完成。可以跑：bash 工具/push_github.sh \"<提交信息>\"")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
