# probe_gh.py —— GitHub 边缘 IP 并发探针
# 2026-10-29 · 阶段1 第5周 · 工具链排障（T19 / T20）
#
# ---------------------------------------------------------------
# 这个文件回答一个问题：GitHub 的边缘 IP 到底哪个能连上？
#
# 背景（你自己踩过的坑）：
#   git push 时报 "Recv failure: Connection was reset"，
#   但 curl 一下别的站点全是 200 —— 说明不是网断了，是 GitHub 这条线被掐。
#   查 git config 发现绑了 140.82.121.3，这个 IP 当天已经死了。
#   于是要不停换 IP 试 —— 但「用哪个 IP」没人能提前告诉你。
#
# 这个文件做什么：
#   把 140.82.110~125 的 .3/.4/.5/.6 全扫一遍，
#   告诉你哪些「真的能完成一次 HTTPS 请求」，并按顺序列出来。
#
# 为什么要并发（这是 T20 的核心教训）：
#   串行 curl 逐个试，每个 IP 最多等 6 秒，扫 64 个要 6 分钟。
#   而 GitHub 的可达 IP 集合是【随时段轮换】的 —— 6 分钟后你探到的
#   第一个 IP 早就死了，等于用 6 分钟前的信息做决策。
#   改成线程池并发后，64 个 IP 10 秒扫完，信息还热着。
#
# 跑法：
#   python probe_gh.py web    # 扫 github.com
#   python probe_gh.py api    # 扫 api.github.com
#
# 输出最后一行是 LIVE_IPS=...，给 push_github.sh 直接读
# （bash 解析中文输出很麻烦，所以额外给一行机器可读的）。
# ---------------------------------------------------------------

import socket
import ssl
import sys
from concurrent.futures import ThreadPoolExecutor

# ssl.create_default_context() = 造一个「标准」的 SSL 配置
#   └─ 默认会校验证书链 + 域名，所以后面 wrap_socket 时必须传对 server_hostname
#   └─ 单独造一次复用给所有 IP，别在循环里反复造（造一次不便宜）
CTX = ssl.create_default_context()


# ============================================================
# 单个 IP 的探活：能不能真的完成一次 HTTPS 请求
# ============================================================
def check(ip, host="github.com", path="/login"):
    """探测一个 IP 是否可用。返回 (ip, host, 状态码或失败标记, 备注)。

    判定分三步，任何一步过了都算数：
        1) TCP 能不能连上 443        → 不行就是 "tcp-fail"
        2) TLS 握手能不能成功        → 不行就是 "tls/http-fail"
        3) 真的发一次 HTTP GET       → 拿到状态码就算「链路是通的」

    为什么第 3 步要用 GET /login 而不是只握手：
        光握手成功不代表能拿到正常响应。GitHub 边缘节点对没带对
        Host / SNI 的请求会直接甩 421 或证书错误。
        真正发一次请求，才能确认这条链路跟 git push 走的是同一条。
    """
    # ---- 第 1 步：TCP 连接 ----
    try:
        # socket.create_connection((ip, 443), timeout=4)
        #   └─ (ip, 443) = 连这个 IP 的 443 端口（HTTPS 默认端口）
        #   └─ timeout=4 = 最多等 4 秒，连不上就抛异常（不能无限等）
        sock = socket.create_connection((ip, 443), timeout=4)
        #   └─ 成功时 sock 是一个已经建立连接的 socket 对象
    except Exception as e:
        # 宽泛捕获：这里故意不区分具体异常类型，因为【连不上】这件事
        # 有很多种原因（超时 / 拒绝 / 路由不可达），对我们要的信息来说
        # 它们是同一件事：这个 IP 不可用。
        # ⚠️ E15 静默错误三件套的反面教材 —— 宽泛 except 会吞掉真错误。
        #   这里安全，是因为返回值里带了 e 的描述，信息没丢。
        return (ip, host, "tcp-fail", str(e)[:40])

    try:
        # ---- 第 2 步：TLS 握手 ----
        # CTX.wrap_socket(sock, server_hostname=host)
        #   └─ 把【普通 socket】包成【加密 socket】
        #   └─ server_hostname=host 是 SNI：告诉对方「我要访问的是 github.com」
        #     这一步很关键 —— 边缘 IP 身上可能挂着好几个域名的证书，
        #     SNI 不对就会证书不匹配（虽然这里用默认校验会直接抛异常）
        ssock = CTX.wrap_socket(sock, server_hostname=host)

        # ---- 第 3 步：发一次真实的 HTTP 请求 ----
        # 手写 HTTP 请求头，是因为 http.client 太啰嗦，这里只需要最简的一行
        req = (
            f"GET {path} HTTP/1.1\r\n"       # 请求行：方法 + 路径 + HTTP 版本
            f"Host: {host}\r\n"              # Host 头必须写对，否则边缘节点不认
            "User-Agent: probe\r\n"         # 伪装成普通客户端
            "Connection: close\r\n\r\n"      # 请求完就关，别等 keep-alive
        )
        #   └─ \r\n 是 HTTP 规定的「行结束符」（不是 \n！Linux/Windows 差异就在这）
        #   └─ 最后那个空的 \r\n = 请求头和正文之间的分隔
        #   └─ 整个字符串用 f-string 拼，{path} {host} 是变量插值
        ssock.sendall(req.encode())
        #   └─ .encode() = str → bytes（网络只能传字节）
        #   └─ sendall 而不是 send：send 可能只发一半，sendall 保证发完

        # recv(200) = 最多收 200 字节（HTTP 响应头的第一段就够拿状态码了）
        # .decode("latin-1", "ignore") = bytes → str
        #   └─ 为什么用 latin-1 而不是 utf-8：latin-1 是「每个字节映射成一个字符」，
        #     永远不会解码失败。响应头是 ASCII，用 utf-8 也行但 latin-1 更稳。
        #     "ignore" = 遇到解不了的字节就丢掉（第二个参数是错误处理策略）
        data = ssock.recv(200).decode("latin-1", "ignore")

        # HTTP 响应第一行长这样： "HTTP/1.1 200 OK\r\n..."
        # split(" ") 按空格切成 ["HTTP/1.1", "200", "OK\r\n..."]
        # [1] 就是 "200" —— 状态码
        code = data.split(" ")[1] if " " in data else "?"
        #   └─ 三元表达式：如果条件为真取前面的值，否则取后面的
        #   └─ 为什么要判断 " " in data：万一收到的是空响应，split 会返回
        #     只有 1 个元素的列表，取 [1] 会 IndexError 崩掉

        ssock.close()          # 关掉加密 socket
        return (ip, host, code, "")
    except Exception as e:
        # 握手或收发阶段失败
        try:
            sock.close()       # 兜底把裸 socket 也关掉，别泄漏连接
        except Exception:
            pass               # 已经断了就无所谓，别让 close 的异常掩盖真错误
        return (ip, host, "tls/http-fail", str(e)[:40])


# ============================================================
# 主流程：决定扫哪些 IP、怎么判定活、怎么打印
# ============================================================
def main():
    # sys.argv[1] = 命令行第一个参数（sys.argv[0] 是脚本名本身）
    # 三元表达式：给了参数就用参数，没给就默认 "web"
    mode = sys.argv[1] if len(sys.argv) > 1 else "web"

    if mode == "web":
        # web 段候选：140.82.110 ~ 140.82.125，每个 b 配 .3/.4/.5/.6 四种
        #   └─ 这是一个【列表推导式】：for b 循环 range，for s 循环 (3,4,5,6)
        #   └─ f"..." 是 f-string，把 {b} {s} 的值填进去
        #   └─ 一共 16 × 4 = 64 个候选
        cands = [f"140.82.{b}.{s}" for b in range(110, 126) for s in (3, 4, 5, 6)]
        host = "github.com"
        # github.com/login 是个真页面，返回 200 才算活
        ok_codes = {"200"}
        #   └─ {..} 是集合（set），用 in 判断快
    else:
        # api 段候选：只扫 .5 / .6（GitHub 的 api 边缘节点是另一个网段）
        cands = [f"140.82.{b}.{s}" for b in range(110, 126) for s in (5, 6)]
        host = "api.github.com"
        # ⚠️ 这里踩过坑：api.github.com 的根路径【本来就没有页面】，
        #   正常返回就是 404。第一次写的时候按「必须 200」判活，
        #   结果整段 api IP 全被判成死的 —— 判据错了，不是网络错了。
        #   改法：拿到任何 HTTP 响应就说明 TLS 握手和链路都通了。
        ok_codes = {"200", "404", "400", "403", "301", "302"}

    # flush=True = 立刻把这一行打印出来，不等缓冲区满
    #   └─ 为什么要？因为并发跑要好几秒，不 flush 你会盯着屏幕空白，
    #     以为卡死了
    print(f"=== 扫描 {host} （{len(cands)} 个候选）===", flush=True)

    live = []       # 存所有判定为「活」的 IP，保持发现顺序
    # ThreadPoolExecutor(max_workers=32) = 32 个线程的线程池
    #   └─ with = 用完自动关（不关会挂住程序不退出）
    #   └─ 32 是并发上限，太高会被对方限流，太低浪费时间
    with ThreadPoolExecutor(max_workers=32) as ex:
        # ex.map(函数, 可迭代对象) = 把每个元素丢给函数跑，**按原顺序返回结果**
        #   └─ lambda i: check(i, host) = 一个匿名函数，等价于
        #     def f(i): return check(i, host)
        #   └─ 注意 map 是「并发跑、按序出」，所以打印顺序和候选顺序一致
        for ip, h, code, note in ex.map(lambda i: check(i, host), cands):
            if code in ok_codes:
                live.append(ip)                       # 记下来，push 时按这个顺序试
                print(f"    {ip:16s} {code}  <== 活", flush=True)
                #   └─ {ip:16s} = 格式化输出，左对齐占 16 个字符宽
                #     （:16 后面跟 s 表示字符串 + 左对齐；:>16 才是右对齐）
            elif code not in ("tcp-fail",):
                # tcp-fail 的 IP 直接不打印 —— 太多噪音
                # 但 tls/http-fail 要打：它说明「连上了但握手失败」，
                # 这类情况可能是 TLS 配置问题，值得看一眼
                print(f"    {ip:16s} {code}  {note}", flush=True)

    print("")
    print("可用列表（按顺序尝试）:")
    print(" ".join(live) if live else "  （本次扫描没有活 IP）")
    #   └─ " ".join(列表) = 用空格把列表拼成字符串
    #   └─ 三元表达式：live 非空就拼，否则给一句人话

    # 机器可读格式，给 push_github.sh 用
    #   └─ 为什么不直接解析上面那行中文？因为 bash 里处理中文字符串
    #     要考虑编码问题，很容易踩坑。多打一行纯 ASCII 最省心。
    print("LIVE_IPS=" + " ".join(live))


# __name__ == "__main__" 是 Python 的约定：
#   直接运行这个文件时 __name__ 就是 "__main__" → 执行 main()
#   被别的文件 import 时 __name__ 是模块名 → 不执行 main()
#   这样别人 import 里面的函数时不会意外开始扫 IP
if __name__ == "__main__":
    main()
