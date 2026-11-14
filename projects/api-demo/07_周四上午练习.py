# 07_周四上午练习.py
# 2026-11-12 周四上午档补做（11-14 执行）
# 目标：GET+查询参数 / POST+JSON / 异常封装
# 规则：先自己写，卡住了再翻提示或来问我

# 导入 requests：它把「发一个 HTTP 请求」包装成了一行调用，比自带的 urllib 短得多
import requests


# ============ 题1：GET + 查询参数 ============
# 目标：GET https://httpbin.org/get，带上查询参数 name=周四 & page=1
# 提示：requests.get(url, params={...}, timeout=10)
#       服务器收到的参数会回显在响应的 args 字段里
def 题1():
    # 发 GET 请求：第 2 个位置参数就是查询参数表；timeout=10 表示最多等 10 秒
    r = requests.get("https://httpbin.org/get", {"name": 1, "周四": 1}, timeout=10)

    # 打印状态码：服务器的一句话答复（200 成功 / 404 没有 / 500 服务器崩了）
    print(r.status_code)

    # 打印 args：服务器回显它实际收到的参数，用它来验证参数有没有正确传过去
    print(r.json()["args"])

    # 打印 url：拼好参数后的完整地址，能直观看到参数是怎么接到 ? 后面的
    print(r.json()["url"])


# ============ 题2：POST + JSON ============
# 目标：POST https://httpbin.org/post，发送 JSON {"name": "你的名字", "task": "周四练习"}
# 提示：requests.post(url, json={...}, timeout=10)
#       服务器会把你发的 JSON 原样回显在返回体的 "json" 键里
def 题2():
    # 发 POST 请求：json= 会把 dict 自动序列化成 JSON，并顺手设好 Content-Type 请求头
    r = requests.post("https://httpbin.org/post", json={"name": "你的名字", "task": "周四练习"}, timeout=10)

    # 打印状态码：POST 成功同样是 200
    print(r.status_code)

    # 打印 "json" 键：服务器把你刚发的 JSON 原样回显，用来确认「发出去的」和「收到的」一致
    print(r.json()["json"])


# ============ 题3：异常封装 safe_get ============
# 要求：把「发请求 + 判断成功 + 解析 JSON + 兜住异常」封成一个能重复用的函数
# 提示：网络层错误（连不上、超时）都属于 requests.RequestException 的子类
#       4xx/5xx 用 resp.raise_for_status() 转成 HTTPError（它也是 RequestException 的子类）
def safe_get(url, timeout=5):
    """返回 (状态码, 数据)；失败返回 (None, 错误信息)"""
    try:
        # 发请求并限制超时：没有 timeout 的话对方一卡住，你的程序就永久挂着不报错
        r = requests.get(url, timeout=timeout)

        # 状态码是 4xx/5xx 时，这一行会自动抛 HTTPError，让错误走统一的 except 分支
        r.raise_for_status()

        # 解析 JSON 正文：只有确认不是错误码，才敢把正文当 JSON 解析
        data = r.json()

        # 成功路径：把状态码和解析出的数据一起交回去，调用者才拿得到结果
        return (r.status_code, data)

    except requests.exceptions.JSONDecodeError as e:
        # 正文不是合法 JSON（比如对方给你返回了一个 HTML 错误页）
        return (None, f"返回的不是JSON: {e}")

    except requests.exceptions.HTTPError as e:
        # 服务器明确回了错误码：说明「连上了，但对方拒绝了」
        return (None, f"HTTP错误: {e}")

    except requests.RequestException as e:
        # 基类兜底：连不上、超时、DNS 解析失败等网络层错误，全靠这一行接住
        # 必须放最后：它是上面两个异常的父类，放前面会把子类一起吃掉
        return (None, f"请求失败({type(e).__name__}): {e}")


# ============ 自测 ============
def 自测():
    # 场景1 正常返回：应该拿到 (200, {...})
    print("【场景1 正常】", safe_get("https://httpbin.org/get"))

    # 场景2 服务器回 500：走 HTTPError 分支
    print("【场景2 服务器500】", safe_get("https://httpbin.org/status/500"))

    # 场景3 域名根本解析不了：走 RequestException 基类分支
    print("【场景3 域名不存在】", safe_get("https://this-domain-not-exist-abc123.com/get"))


if __name__ == "__main__":
    # 只有直接运行本文件才执行；被别的文件 import 时不会跑（写库的标准习惯）
    题1()
    题2()
    自测()
