"""并发探测 GitHub 边缘 IP 的真实可用性（TLS 握手 + HTTP /login）。

为什么不用 curl 串行：串行每个 IP 最长 6 秒，扫 60 个要 6 分钟。
用线程池并发，同样的活 10 秒内跑完。

判定标准（两层）：
  1) TCP 能不能连上 443
  2) TLS 握手能不能成功 + 用 github.com 做 SNI（边缘 IP 只认自己的域名，
     拿错 SNI 会 421/证书错）
  3) 真正发一次 HTTP GET /login 看状态码是不是 200
只报 200 的，因为 git push 走的就是这条链路。
"""
import socket
import ssl
import sys
from concurrent.futures import ThreadPoolExecutor

CTX = ssl.create_default_context()


def check(ip, host="github.com", path="/login"):
    try:
        sock = socket.create_connection((ip, 443), timeout=4)
    except Exception as e:
        return (ip, host, "tcp-fail", str(e)[:40])
    try:
        ssock = CTX.wrap_socket(sock, server_hostname=host)
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            "User-Agent: probe\r\n"
            "Connection: close\r\n\r\n"
        )
        ssock.sendall(req.encode())
        data = ssock.recv(200).decode("latin-1", "ignore")
        code = data.split(" ")[1] if " " in data else "?"
        ssock.close()
        return (ip, host, code, "")
    except Exception as e:
        try:
            sock.close()
        except Exception:
            pass
        return (ip, host, "tls/http-fail", str(e)[:40])


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "web"
    if mode == "web":
        # web 段：.3 / .4 / .5 / .6（.5/.6 多为 api 段，web 也可能通）
        cands = [f"140.82.{b}.{s}" for b in range(110, 126) for s in (3, 4, 5, 6)]
        host = "github.com"
        # github.com/login 返回 200 才算活
        ok_codes = {"200"}
    else:
        cands = [f"140.82.{b}.{s}" for b in range(110, 126) for s in (5, 6)]
        host = "api.github.com"
        # api.github.com 根路径本来就没页面（返回 404），
        # 所以「拿到任何 HTTP 响应」就说明链路是通的
        ok_codes = {"200", "404", "400", "403", "301", "302"}

    print(f"=== 扫描 {host} （{len(cands)} 个候选）===", flush=True)
    live = []
    with ThreadPoolExecutor(max_workers=32) as ex:
        for ip, h, code, note in ex.map(lambda i: check(i, host), cands):
            if code in ok_codes:
                live.append(ip)
                print(f"    {ip:16s} {code}  <== 活", flush=True)
            elif code not in ("tcp-fail",):
                print(f"    {ip:16s} {code}  {note}", flush=True)
    print("")
    print("可用列表（按顺序尝试）:")
    print(" ".join(live) if live else "  （本次扫描没有活 IP）")
    # 机器可读格式，给 push_github.sh 用（避免 bash 里解析中文输出）
    print("LIVE_IPS=" + " ".join(live))


if __name__ == "__main__":
    main()
