# _基准_串行vs并发探测.py —— 量化「探活必须并发」这条结论
# 2026-10-29 · 晚上 · 工具链排障
#
# ---------------------------------------------------------------
# 这个文件回答一个问题：把 hosts 修复工具的探活改成并发，到底值不值？
#
# 为什么需要这个基准：
#   直接拿真网做端到端计时【不可比】—— GitHub 边缘 IP 的可用窗口
#   只开几十秒，两次运行之间网络状态就变了。
#   2026-10-29 实测：同一份工具，串行 45 秒 / 并发 51 秒，
#   但那只是因为第二次运行时 raw 段的抖动方向相反，不反映算法差异。
#
# 干净基准怎么造：
#   用 192.0.2.0/24 —— 这是 RFC 5737 保留的「文档测试段」，
#   全球范围内【永远不可达】，任何人 ping 都超时。
#   于是每次探测都必然耗满超时时间，结果 100% 可复现，
#   测出来的差值 = 纯粹的「串行 vs 并发」算法差。
#
# 结论（2026-10-29 实测）：
#   串行 N 个死 IP = N × tries × 超时
#   并发 N 个死 IP = 1 × tries × 超时（全部同时跑）
#   → N=20 时差 20 倍。而 GitHub 的可用窗口只有几十秒，
#     串行版扫完窗口早关了，工具必然白跑。
# ---------------------------------------------------------------

import importlib.util
import os
import sys
import time

# ============================================================
# 载入被测对象：仓库根目录的 gh_hosts_fix.py
#   └─ 用 importlib 按【文件路径】加载，因为它带中文注释但文件名是英文，
#     直接 import 也行，但按路径加载更稳（不依赖 sys.path 和工作目录）
# ============================================================
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#   └─ 连续三次 dirname 剥掉三层：
#     __file__      = .../pythonProject/笔记/_自检脚本/本文件.py
#     dirname #1    = .../pythonProject/笔记/_自检脚本
#     dirname #2    = .../pythonProject/笔记
#     dirname #3    = .../pythonProject          ← 仓库根目录，gh_hosts_fix.py 在这
#   └─ 剥三层是因为本文件被放在「笔记/_自检脚本」两层子目录里

spec = importlib.util.spec_from_file_location(
    "ghfix", os.path.join(BASE, "gh_hosts_fix.py"))
ghfix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ghfix)
#   └─ exec_module = 真正执行这个 .py 文件（模块顶部的代码跑起来）

# ============================================================
# 基准参数
# ============================================================
N = 10            # 探测多少个「死 IP」
TIMEOUT = 4       # 单次探测的超时秒数（比默认 6 小一点，缩短基准时长）
TRIES = 3         # 每个 IP 重试几次（和工具默认一致）

# 保留测试段（RFC 5737 TEST-NET-1）的 IP —— 永远不可达
DEAD = ["192.0.2.%d" % i for i in range(1, N + 1)]
#   └─ %d = 十进制整数占位符
#   └─ 生成 192.0.2.1 ~ 192.0.2.10，个个都是黑洞


def bench_serial():
    """串行探测：一个个来，返回耗时秒数。

    逐行拆解：
      1. start = time.time()     → 记开始时刻（时间戳，浮点秒）
      2. for ip in DEAD           → 挨个探
      3. ghfix.probe(...)         → 探一个 IP（内部会重试 tries 次）
      4. return time.time()-start → 减去开始时刻 = 总耗时
      └─ 关键：串行总耗时 = Σ 每个 IP 的耗时，是【累加】的
    """
    start = time.time()
    #   └─ time.time() 返回「自 1970-01-01 起的秒数」（浮点）
    for ip in DEAD:
        #   └─ 一次一个，等这个跑完才跑下一个
        ghfix.probe("github.com", ip, "/login", timeout=TIMEOUT, tries=TRIES)
        #   └─ 探的是 github.com，但 IP 是黑洞 → 必然连不上 → 返回 "000"
    return time.time() - start


def bench_parallel():
    """并发探测：一次全上，返回耗时秒数。

    逐行拆解：
      1. start = time.time()                  → 记开始时刻
      2. ghfix.pick_ip(DEAD, ...)              → 工具里的并发版
      3. return time.time()-start             → 总耗时
      └─ 关键：并发总耗时 ≈ 【最慢的那一个】IP 的耗时，不是累加
    """
    start = time.time()
    ghfix.pick_ip(DEAD, "github.com", "/login", strict_200=True,
                  workers=N, timeout=TIMEOUT, tries=TRIES)
    #   └─ workers=N = 一人一个，全同时上
    #   └─ pick_ip 会返回 None（全是黑的），这里不关心返回值，只测时间
    return time.time() - start


def main():
    print("=" * 66)
    print("  基准：串行 vs 并发（探测 %d 个必然不可达的 IP）" % N)
    print("  IP 段：192.0.2.0/24（RFC 5737 保留测试段，全球不可达）")
    print("  单次超时 %ds，重试 %d 次" % (TIMEOUT, TRIES))
    print("=" * 66)
    print()

    t_serial = bench_serial()
    print("  串行版：%6.1f 秒" % t_serial)
    #   └─ %6.1f = 宽度 6、右对齐、1 位小数

    t_par = bench_parallel()
    print("  并发版：%6.1f 秒" % t_par)
    print()

    if t_par > 0:
        print("  倍数：串行是并发的 %.1f 倍" % (t_serial / t_par))
    #   └─ 理论值应该 ≈ N（10 倍），差一点点是因为线程启动开销

    print()
    print("  换算到真实场景（GitHub 工具的候选池）：")
    print("    web 段 %d 个 + api 段 %d 个 + raw 段 %d 个 = %d 个候选"
          % (len(ghfix.WEB_CANDS), len(ghfix.API_CANDS),
             len(ghfix.RAW_CANDS),
             len(ghfix.WEB_CANDS) + len(ghfix.API_CANDS) + len(ghfix.RAW_CANDS)))
    print("    串行最坏：%d 个 × %d 次重试 × %ds ≈ %.0f 秒"
          % (len(ghfix.WEB_CANDS) + len(ghfix.API_CANDS) + len(ghfix.RAW_CANDS),
             TRIES, TIMEOUT,
             (len(ghfix.WEB_CANDS) + len(ghfix.API_CANDS) + len(ghfix.RAW_CANDS))
             * TRIES * TIMEOUT))
    print("    并发最坏：3 段 × %d 次重试 × %ds ≈ %.0f 秒"
          % (TRIES, TIMEOUT, 3 * TRIES * TIMEOUT))
    print()
    print("  而 GitHub 的可用窗口实测只有【几十秒】——")
    print("  串行版扫完，窗口早关了，工具白跑。")
    print()
    print("  ⚠️ 本基准只测【算法耗时】，与真实网络状态无关，结果可复现。")


if __name__ == "__main__":
    main()
    #   └─ 直接运行这个文件时才执行（被 import 时不会自动跑）
