# 导入 requests：发 HTTP 请求的第三方库
import requests
# 导入 json：Python 内置的 JSON 翻译官（不用装）
import json
# 导入 os：操作系统功能，建目录、拼路径
import os

# ============ 第 1 步：建输出目录 ============
# os.makedirs 会创建目录（含多级），exist_ok=True 表示「已经有了也别报错」
os.makedirs("输出", exist_ok=True)

# ============ 第 2 步：请求接口 ============
# jsonplaceholder 的用户列表接口，一次返回 10 条
resp = requests.get("https://jsonplaceholder.typicode.com/users", timeout=10)

# ============ 第 3 步：解析成 Python 对象 ============
# .json() 把 JSON 文本翻译成 list（这次是列表，因为接口返回多条）
data = resp.json()

# 打印它是什么类型、有多少条
print("数据类型：", type(data))
print("条数：", len(data))

# ============ 第 4 步：存成 JSON 文件 ============
# 路径用 os.path.join 拼，比手写 "输出/users.json" 更稳（Windows 和 Linux 分隔符不同）
file_path = os.path.join("输出", "users.json")

# with open(...) as f 的意思是：打开文件 → 用完自动关（不用手动 close）
# 写文件模式 "w" = 覆盖写（文件已存在会清空）；encoding="utf-8" = 用 UTF-8 存中文
# ensure_ascii=False 让中文保持原样；indent=2 缩进 2 格
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("已保存到：", file_path)

# ============ 第 5 步：读回来核对（关键！不能只存不验）============
with open(file_path, "r", encoding="utf-8") as f:
    back = json.load(f)      # json.load = 直接读文件版

print("读回的类型：", type(back))
print("读回的条数：", len(back))
print("第 1 个人的姓名：", back[0]["name"])
print("第 1 个人的城市：", back[0]["address"]["city"])      # 两层嵌套
print("第 1 个人的公司：", back[0]["company"]["name"])      # 两层嵌套
