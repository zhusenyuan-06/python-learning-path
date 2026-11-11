# 导入 requests：Python 自带的 urllib 也能上网，但 requests 把发 HTTP 请求包装成了一行调用
import requests

# 请求 httpbin 的回声壁
resp = requests.get("https://httpbin.org/get")

# .json() 把 JSON 文本翻译成 Python 的 dict（不是字符串！）
data = resp.json()

# 打印类型，亲眼看看它现在是 dict
print("data 的类型：", type(data))

# 取顶层的键：字典取值写法是 data["键名"]
print("请求方法：", data["method"])

# 取嵌套的值：data["headers"] 本身也是字典，再从里面取一层
print("请求头里的 Host：", data["headers"]["Host"])

# requests 自动加的 User-Agent（注意它没伪装成浏览器）
print("User-Agent：", data["headers"]["User-Agent"])

# args 是一个空字典，打印它的类型和内容
print("args 的类型：", type(data["args"]), "内容：", data["args"])

print()
print("========== 下面故意踩一个坑 ==========")

# httpbin 提供的测试接口：这个会返回 404
resp404 = requests.get("https://httpbin.org/status/404")

# 先看状态码
print("状态码：", resp404.status_code)

# 然后直接 .json() —— 会抛 JSONDecodeError
# 这里用 try/except 接住，是为了让脚本能跑完；不接的话程序会直接崩在这行
# 想看完整 traceback（两段异常链），把下面的 except 段删掉再跑一次
try:
    data404 = resp404.json()
    print("解析结果：", data404)
except requests.exceptions.JSONDecodeError as e:
    print("❌ 解析失败，异常类型：", type(e).__name__)
    print("   错误信息：", e)
    print()
    print("为什么会这样：")
    print("  404 返回的正文是 HTML（而且是空的），不是 JSON")
    print("  空正文 → json 解析器在第 0 个字符就找不到任何值 → JSONDecodeError")
    print("  所以正确顺序是：先看 status_code，确认 200 了再 .json()")
    print()
    print("★ 异常链（traceback 里为什么有两段）：")
    print("   第 1 段：json.decoder.JSONDecodeError  ← 原始错误（标准库 json 抛的）")
    print("   第 2 段：requests.exceptions.JSONDecodeError  ← requests 接住后重新包装再抛")
    print("   requests 的这个异常是 json 那个的【子类】，所以 except json.JSONDecodeError 也能抓住它")
