text = "apple banana apple orange banana apple"
words = text.split()#将text按照空白切分成一个列表
d = {}
for w in words:
    d[w] = d.get(w, 0) + 1#d.get（）就是在字典里取值
print(d)
#第 1 次遇到 "apple"：字典是空的 → d.get("apple", 0) 返回 0 → 0 + 1 = 1 → d["apple"] = 1 •
# 第 2 次遇到 "apple"：已有 "apple":1 → d.get("apple", 0) 返回 1 → 1 + 1 = 2 → d["apple"] = 2