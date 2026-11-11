# 导入 requests：发 HTTP 请求的第三方库
import requests
# 导入 csv：Python 内置的表格读写模块
import csv
# 导入 os：操作系统功能，建目录、拼路径
import os

# 建输出目录（exist_ok=True = 已经有了也不报错）
os.makedirs("输出", exist_ok=True)

# 请求 60s 接口（今天 2026-11-11，接口返回当天的数据）
resp = requests.get("https://60s.viki.moe/v2/60s", timeout=15)

# 先看状态码再决定要不要解析（你 04 学过的顺序）
if resp.status_code != 200:
    print("请求失败，状态码：", resp.status_code)
else:
    # 解析成 Python 对象
    result = resp.json()

    # ★★ 这里有两层：先拿到壳里的 data，再从 data 里拿各字段
    data = result["data"]

    # 先把接口真实的键名打印出来看看（写代码前先看清楚有哪些字段）
    print("data 里有哪些字段：", list(data.keys()))
    print("新闻条数：", len(data["news"]))

    # ★★ 拍平：把 list 里的每个字符串，变成表格里的一行
    # 表头（4 列）——「序号」是我们自己加的，接口没有
    rows = []
    for i, news_item in enumerate(data["news"], start=1):
        rows.append([
            i,                          # 序号（enumerate 从 1 开始数）
            data["date"],               # 日期
            news_item,                  # 新闻内容（这一条）
            data["day_of_week"],        # 星期几
        ])

    # 存成 CSV
    file_path = os.path.join("输出", "news.csv")

    # ★★ 三个关键参数，缺一不可：
    #   encoding="utf-8-sig"  Excel 双击打开不乱码
    #   newline=""            不写的话 Windows 上每行之间会多出空行
    #   csv.writer            把每行按逗号分隔写出，自动处理引号转义
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["序号", "日期", "新闻内容", "星期"])   # 表头
        writer.writerows(rows)                                 # 写所有数据行

    print("已保存到：", file_path)

    # ★★ 读回来核对 —— 不能只写不验
    with open(file_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            print(f"第{i}行（{len(row)}列）：", row)
            if i >= 3:      # 只看前 4 行（表头 + 3 条）
                break
