with open("文本.txt", encoding="utf-8") as f:
    text = f.read()                      # 1. 读文件

words = text.split()                     # 2. 切词
stopwords = {"the", "is", "and", "to", "in", "a", "of", "that"}

counts = {}
for w in words:                          # 3. ⭐ 这行你漏了
    w = w.lower().strip(".,!?")          # 4. 清洗：全小写 + 去两端标点
    if w in stopwords:                   # 5. 判断（是 w，不是 words）
        continue                         # 6. 停用词 → 跳过本轮
    counts[w] = counts.get(w, 0) + 1     # 7. 计数

# 任务1：top N
top_n = 3# ← 想看前几名，改这里
after = sorted(counts.items(), key=lambda x: x[1], reverse=True)
t = after[:top_n]
for w, c in t:
    print(w, c)


# 任务2：只出现1次的词
once = {w for w, c in counts.items() if c == 1}    # ← 集合推导式
print("只出现1次的词:", len(once))                          # → 15


print(sorted(counts.items(), key=lambda x: x[1], reverse=True))






