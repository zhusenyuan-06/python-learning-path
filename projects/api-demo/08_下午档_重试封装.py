# 08_下午档_重试封装.py
# 2026-11-12 周四下午档补做（11-14 执行）
# 目标：让 safe_get 报出「错在哪一类」，再封装一个会自动重试的版本

import time                        # 导入 time 模块，用它的 sleep 做退避等待
import requests                    # 导入 requests，把 HTTP 请求封装成一行调用


# ============ 第一步：升级 safe_get，让它能报出错误类型 ============
# 为什么要升级：失败时只返回一句错误信息，你分不清「连都没连上」和
# 「连上了但被拒绝」——而这两种错误该不该重试，完全是两回事
def safe_get(url, timeout=5):     # 定义函数：请求一次，失败时把错误类型和详情一起带回来
    """
    返回 (状态码, 数据, 错误类型, 错误详情)
    成功：    (200, {...}, None, None)
    HTTP错误： (404 或 500, None, "HTTPError", "错误详情...")
    网络错误： (None, None, "ConnectionError", "错误详情...")
    """
    try:                            # 把可能出错的代码全圈起来
        # 发请求并限制超时：没有 timeout 的话对方卡住，你的程序就永久挂着不报错
        r = requests.get(url, timeout=timeout)    # 发请求；timeout 是最多等几秒

        # 状态码是 4xx/5xx 时，这一行会自动抛 HTTPError，让错误走统一的 except 分支
        r.raise_for_status()        # 4xx/5xx 在这里抛 HTTPError，统一交给 except 处理

        # 解析 JSON 正文：只有确认不是错误码，才敢把正文当 JSON 解析
        data = r.json()             # 把正文解析成 Python 的 dict

        # 成功路径：把状态码和解析出的数据一起交回去，调用者才拿得到结果
        return (r.status_code, data, None, None)   # 成功：错误类型和详情都是 None

    except requests.exceptions.JSONDecodeError as e:   # 正文不是合法 JSON（对方给了 HTML 错误页）
        return (None, None, "JSONDecodeError", f"返回的不是JSON: {e}")   # 状态码未知 + 类型名 + 详情

    except requests.exceptions.HTTPError as e:         # 服务器明确回了错误码
        return (e.response.status_code, None, "HTTPError", f"HTTP错误: {e}")   # 从异常里掏出状态码

    except requests.RequestException as e:            # 基类兜底：连不上、超时、DNS 失败
        # 必须放最后：它是上面两个异常的父类，放前面会把子类一起吃掉
        return (None, None, type(e).__name__, f"请求失败: {e}")   # 没连上，状态码只能是 None


# ============ 第二步：写 get_with_retry ============
# 需求：失败后自动重试，最多试 retries+1 次；
#       并且要分「值得重试」和「不值得重试」
# 值得重试：网络层错误（ConnectionError / Timeout / ProxyError）、服务器错误 5xx、限流 429
# 不值得重试：4xx 里的 400/401/403/404 —— 你请求本身有问题，重试多少次结果都一样
def get_with_retry(url, retries=2, timeout=5, backoff=1):   # 带重试的 GET：失败会自动再试
    """返回 (状态码, 数据, 错误类型, 错误详情)；最多尝试 retries+1 次"""
    for i in range(retries + 1):                    # ① 循环次数 = 首次尝试 + retries 次重试
        print(f"  → 第 {i+1} 次尝试：{url}")          # 打印第几次，方便你观察重试了几次

        状态码, 数据, 错误类型, 详情 = safe_get(url, timeout)   # ② 拆包接收四个值

        if 状态码 is not None and 状态码 < 400:     # ③ 状态码存在且小于 400 = 成功
            return (状态码, 数据, 错误类型, 详情)     #    成功就收工，不再重试

        # ④ 默认「值得重试」，再明确排除不该重试的
        不可重试 = (错误类型 == "JSONDecodeError") or \
                  (状态码 is not None and 400 <= 状态码 < 500 and 状态码 != 429)
        if 不可重试:
            return (状态码, 数据, 错误类型, 详情)     # ⑤ 4xx 不重试，错误直接带出去

        if i < retries:                              # ⑥ 最后一轮就别白等了
            print(f"  → 等待 {backoff*(i+1)} 秒后重试")
            time.sleep(backoff * (i + 1))            # ⑦ 退避等待：1秒、2秒...

    return (None, None, "重试耗尽", f"重试{retries}次仍失败")   # ⑧ 兜底：可重试但一直失败


# ============ 自测 ============
def 自测():
    for 名字, 地址 in [                       # 四个场景依次测
        ("正常", "https://httpbin.org/get"),                 # 正常：一发就中
        ("500", "https://httpbin.org/status/500"),            # 服务器故障：值得重试
        ("404", "https://httpbin.org/status/404"),            # 找不到：不该重试
        ("域名不存在", "https://this-domain-not-exist-abc123.com/get"),   # 网络层错误：值得重试
    ]:
        print("=" * 40)                       # 分隔线，看清每个场景的边界
        print(名字, "->", get_with_retry(地址, retries=2))   # 调用并打印结果

    # TODO 13. 再自己加一个场景，验证「返回的不是 JSON 时不重试」：
    #         https://httpbin.org/html  返回的是 HTML，不是 JSON
    #         期望：只尝试 1 次就返回（因为错误类型是 JSONDecodeError）


if __name__ == "__main__":
    自测()                                # 只有直接运行本文件才执行，被 import 时不跑
