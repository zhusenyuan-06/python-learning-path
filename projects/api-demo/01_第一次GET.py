# 导入 requests 库：Python 自带的 urllib 也能上网，但写起来又长又难懂，
# requests 把「发一个 HTTP 请求」这件事包装成了一行调用
import requests

# 用 GET 方式请求一个网址（GET 的意思是「只拿、不改」）
# 发出去的叫「请求」，收回来的叫「响应」，requests.get() 返回的就是那个响应对象
resp = requests.get("https://www.baidu.com")

# 响应对象身上有三样最常用的东西：
#   .status_code —— 状态码，服务器的一句话答复（200 成功 / 404 没有 / 500 服务器崩了）
#   .headers      —— 响应头，服务器附赠的说明（内容是什么格式、多大等）
#   .text         —— 响应正文，服务器真正给的数据（这里是网页文本）
print("状态码：", resp.status_code)
print("Content-Type：", resp.headers.get("Content-Type"))
print("正文前 200 字：", resp.text[:200])
