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

# 然后直接 .json() —— 猜猜会怎么样
data404 = resp404.json()
print("解析结果：", data404)
