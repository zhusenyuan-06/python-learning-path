# 09_综合_API取数存CSV.py
# 2026-11-13 周五上午档补做（11-14 执行）
#
# 这一档叫「综合」，综合的是什么？
#   11-11 你把「请求 → 解析 → 存 JSON → 存 CSV」这条链路走通了（05/06 脚本）
#   11-12 你把「失败要重试、哪些才该重试」学会了（08 脚本）
#   今天 = 把这两样【焊成一件东西】：一个能拿去用的「取数并存表」工具
#
# ★ 本文件是你第 10 个作品。做完请在根 README 速览表加一行。

import os            # 建目录、拼路径
import csv           # 表格读写
import time          # 退避等待（重试时用）
import requests      # 发 HTTP 请求

# ================================================================
# 第一部分：从 08 复制过来的重试封装（已按通用版改造）
# ================================================================
# 为什么复制而不是 import？
#   08 的文件名以数字开头（08_xxx），Python 的 import 语句不接受这种名字；
#   而且练习阶段每个脚本都要能单独双击跑通。
#   ★ 生产项目里应该把它抽成独立模块（api_client.py）再 import —— 这条先记着。

def safe_get(url, timeout=5):
    """请求一次，失败时把「错在哪一类」也带回来。
    返回 (状态码, 数据, 错误类型, 错误详情)
    """
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()      # 4xx/5xx 在这里抛 HTTPError
        return (r.status_code, r.json(), None, None)
    except requests.exceptions.JSONDecodeError as e:
        return (None, None, "JSONDecodeError", f"返回的不是JSON: {e}")
    except requests.exceptions.HTTPError as e:
        return (e.response.status_code, None, "HTTPError", f"HTTP错误: {e}")
    except requests.RequestException as e:
        # 基类兜底，必须放最后（它是上面两个的父类，放前面会把子类吃掉）
        return (None, None, type(e).__name__, f"请求失败: {e}")


def get_with_retry(url, retries=2, timeout=5, backoff=1):
    """带重试的 GET：网络层错误/5xx/429 会重试，4xx 直接带错误走人。"""
    for i in range(retries + 1):
        print(f"  → 第 {i+1} 次尝试：{url}")

        状态码, 数据, 错误类型, 详情 = safe_get(url, timeout)

        if 状态码 is not None and 状态码 < 400:
            return (状态码, 数据, 错误类型, 详情)

        # 4xx（除 429）是你请求写错了，重试一万次结果一样
        不可重试 = (错误类型 == "JSONDecodeError") or \
                  (状态码 is not None and 400 <= 状态码 < 500 and 状态码 != 429)
        if 不可重试:
            return (状态码, 数据, 错误类型, 详情)

        if i < retries:
            print(f"  → 等待 {backoff*(i+1)} 秒后重试")
            time.sleep(backoff * (i + 1))

    return (None, None, "重试耗尽", f"重试{retries}次仍失败")


# ================================================================
# 第二部分：存表 —— 把你 06 脚本里的「一次性代码」改造成「可复用函数」
# ================================================================
# 06 里这段是一次性代码：跑一次、贴在一个文件里、换个 API 就得重写。
# 现在把它变成一个【任何 API 都能套】的函数 —— 这就是「作品化」的第一步。

def 存成CSV(数据行, 文件路径, 表头):
    """把二维列表写成 CSV 文件。

    数据行：[[序号, 日期, 内容, 星期], ...]   每个内层列表是一行
    文件路径：例如 os.path.join("输出", "news.csv")
    表头：    ["序号", "日期", "内容", "星期"]
    """
    with open(文件路径, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(表头)  # 表头
        writer.writerows(数据行)  # 写所有数据行
    # ✅ TODO 1.（11-14 已完成）关键就一句：把「硬编码」换成「参数」
    #   06 里写死的是：文件路径 = "输出/news.csv"、表头 = ["序号", "日期", ...]
    #   这里写的是：文件路径 = 文件路径、表头 = 表头
    #   → 以后换任何 API，这个函数一行都不用改 —— 这就是「可复用」的含义


# ================================================================
# 第三部分：取数 —— 请求 + 解析 + 拍平成表格行
# ================================================================

def 取新闻():
    """调公开 API 取当天的 60 秒新闻，返回 (表格行, 表头)。

    返回的 表格行 形如：[[1, "2026-11-14", "新闻内容...", "星期五"], ...]
    """
    # ✅ TODO 2.（11-14 已完成）三步：请求 → 剥外壳 → 拍平成表格行
    状态码, 数据, 错误类型, 详情 = get_with_retry("https://60s.viki.moe/v2/60s", retries=2, timeout=15)

    # 第①步的后续：状态码是 None，说明连都没连上（或者重试耗尽）→ 直接失败返回
    # ⚠️ 用 is None 不是 == None：None 表示「没有值」，判断「有没有值」要用 is
    if 状态码 is None:
        print(f"取数失败：{错误类型} / {详情}")
        # ⚠️⚠️ 这里必须 return 两个值，不能 return 状态码！
        #    因为主流程写的是 表格行, 表头 = 取新闻()，只返回一个值会直接崩：
        #    TypeError: cannot unpack non-iterable int
        return (None, None)

    # 第②步：剥掉外壳。接口返回的是 {"code":200, "data":{...}}，真正的内容在 data 里
    data = 数据["data"]
    print("data 里有哪些字段：", list(data.keys()))

    # 第③步：把 news 列表里的每一条新闻拍平成表格的一行
    #   news 是 list，每个元素本身就是一条新闻字符串
    表格行 = []
    for 序号, 新闻 in enumerate(data["news"], start=1):   # start=1 → 序号从 1 开始数
        表格行.append([序号, data["date"], 新闻, data["day_of_week"]])

    # 表头也要一起返回 —— 主流程要把它传给 存成CSV()
    return (表格行, ["序号", "日期", "新闻内容", "星期"])


# ================================================================
# 第四部分：主流程 —— 把三块焊起来
# ================================================================

def 主流程():
    print("=" * 50)
    print("【第1步】取数")
    表格行, 表头 = 取新闻()

    if 表格行 is None:
        print("取数失败，本档结束（看看上面的错误类型）")
        return

    print(f"取到 {len(表格行)} 条新闻")

    print("=" * 50)
    print("【第2步】存表")
    os.makedirs("输出", exist_ok=True)          # 建目录，已存在也不报错
    文件路径 = os.path.join("输出", "news_综合版.csv")
    存成CSV(表格行, 文件路径, 表头)
    print("已保存到：", 文件路径)

    print("=" * 50)
    print("【第3步】读回校验 —— 不能只写不验")
    with open(文件路径, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            print(f"第{i}行（{len(row)}列）：{row}")
            if i >= 3:      # 只看表头 + 前 3 条
                break

    # ================================================================
    # 第五部分：自测 —— 证明「重试封装」真的接进来了
    # ================================================================
    print("=" * 50)
    print("【自测】同一个封装，分别打三个不同的目标")
    for 名字, 地址 in [
        ("正常", "https://httpbin.org/get"),
        ("404（不该重试）", "https://httpbin.org/status/404"),
        ("500（该重试）", "https://httpbin.org/status/500"),
    ]:
        print("-" * 40)
        print(f"场景：{名字}")
        状态码, 数据, 错误类型, 详情 = get_with_retry(地址, retries=2)
        print(f"  结果：状态码={状态码} 错误类型={错误类型}")
        # ★ 观察重点：404 场景只尝试 1 次，500 场景尝试 3 次
        #   —— 同一个封装，因为「错误类型 + 状态码」不同，做出了不同的决策


if __name__ == "__main__":
    主流程()
