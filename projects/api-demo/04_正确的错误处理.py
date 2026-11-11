# ⚠️ timeout 一定要写：不写的话，对方服务器卡住，你的程序就永久挂在那里（不报错、不结束）

# 导入 requests：Python 自带的 urllib 也能上网，但 requests 把发 HTTP 请求包装成了一行调用
import requests

# 【方法一】先判断状态码，再决定要不要解析（最直白、最常见）
# timeout=10 的意思是「最多等 10 秒」，超过就抛 Timeout 异常，不会永远挂着
resp = requests.get("https://httpbin.org/get", timeout=10)

if resp.status_code == 200:
    data = resp.json()          # 只有确认是 200 才去解析
    print("解析成功：", data)
else:
    print("请求失败了，状态码：", resp.status_code)
    print("服务器返回的内容：", resp.text[:200])   # 404 的正文是空的，这里会打印空

print()
print("=" * 40)

# 【方法二】让 requests 自己检查，出错就抛异常，用 try/except 接住
try:
    resp2 = requests.get("https://httpbin.org/get", timeout=10)
    resp2.raise_for_status()      # 状态码是 4xx/5xx 时，这一行会自动抛 HTTPError
    data2 = resp2.json()
    print("解析成功：", data2)
except requests.exceptions.HTTPError as e:
    print("HTTP 错误：", e)
except requests.exceptions.JSONDecodeError as e:
    print("返回的不是 JSON：", e)
