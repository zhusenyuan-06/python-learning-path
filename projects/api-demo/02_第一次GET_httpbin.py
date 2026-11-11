# 导入 requests：Python 自带的 urllib 也能上网，但 requests 把发 HTTP 请求包装成了一行调用
import requests

# 用 GET 请求 httpbin 的回声壁（GET = 只拿不改）
# 发出去的叫「请求」，收回来的叫「响应」，requests.get() 返回的就是那个响应对象
resp = requests.get("https://httpbin.org/get")

# 打印状态码（服务器的一句话答复：200 成功 / 404 没有 / 500 服务器崩了）
print("状态码：", resp.status_code)

# 打印响应正文的前 500 字（切片 [:500] 取前 500 个字符）
print("正文前 500 字：", resp.text[:500])

# 打印响应头里的 Content-Type（headers 是字典，用 .get 取值）
print("Content-Type：", resp.headers.get("Content-Type"))

# 【加这一行】把整个响应头都打出来，看看服务器到底附赠了什么
print("全部响应头：", resp.headers)
