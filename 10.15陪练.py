
#def func1(x):
#dict={}
 #   words = x.split()
#    for w in words:
   #     dict[w]=dict.get(w,0)+1


  #  top3 = sorted(dict.items(), key=lambda x: x[1], reverse=True)[:3]
 #   for word, cnt in top3:
#         print(word, cnt)
#    return dict
#print(func1("apple banana apple"))


def count_words(text, top_n=3):
    """统计 text 里每个词出现次数，按次数降序返回前 top_n 个 (词, 次数) 列表。"""
    counts = {}  # ← 局部变量，函数内建，函数外不污染
    for w in text.split():
        counts[w] = counts.get(w, 0) + 1

    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return top  # ← return，不 print


# 调用（启动用）
print(count_words("apple banana apple"))  # 原行为
print(count_words("apple banana apple orange apple", 5))  # 自定义 top_n












#f = lambda c: c * 1.8 + 32
#def show(x):

#    print("结果：", x)


#show(f(36))
#show(f(38))
#show(f(40))

# 常量起名（公式一目了然，谁都知道为啥乘 9/5 加 32）
FAHRENHEIT_PER_DEGREE_C = 9 / 5       # 1℃ 对应 1.8℉（写成 9/5 比 1.8 更"反推"）
CELSIUS_TO_FAHRENHEIT_OFFSET = 32      # 0℃ 是 32℉

def celsius_to_fahrenheit(c):
    """摄氏度 → 华氏度"""
    return c * FAHRENHEIT_PER_DEGREE_C + CELSIUS_TO_FAHRENHEIT_OFFSET

def show(label, value):
    """统一格式打印"""
    print(f"{label}: {value}")

# 批量算 + 批量打（for 循环，不重复 3 次）
temperatures = [36, 38, 40]
for t in temperatures:
    show(f"{t}℃", celsius_to_fahrenheit(t))

# 还能 return 出整个列表（不再绑死 print）
def batch_convert(cs):
    """批量把一组摄氏度转成华氏度，返回新列表"""
    return [celsius_to_fahrenheit(c) for c in cs]

print(batch_convert([36, 38, 40]))   # 期望 [96.8, 100.4, 104.0]
















class Helper:
    def __init__(self, data):
        self.data = data
    def get_evens(self):
        return list(filter(lambda x: x % 2 == 0, self.data))
    def get_odds(self):
        return list(filter(lambda x: x % 2 != 0, self.data))
    def get_summary(self):
        return f"偶数: {len(self.get_evens())} 个, 奇数: {len(self.get_odds())} 个"

nums = list(range(1, 11))
h = Helper(nums)
print(h.get_evens())
print(h.get_summary())













