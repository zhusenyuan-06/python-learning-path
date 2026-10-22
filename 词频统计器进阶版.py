# 词频统计器进阶版 —— 分步骨架（核心逻辑由你填）
# 运行前：把 test.txt 放到同目录，或改下面 path 为你的文件路径

# ---- 第 1 步：读文件 ----
path = "test.txt"                       # ← 换成你的 txt 文件名 / 路径
# with 打开会自动关文件；encoding="utf-8" 防中文乱码
with open(path, encoding="utf-8") as f:
    text = f.read()                     # 一次性读全部内容为字符串

# ---- 第 2 步：切词 ----
words = text.split()                    # 按空白切成 list（句子 → 一个个词）

# ---- 第 3 步：字典统计词频（这行你昨天写过）----
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1

# ---- 第 4 步：排序取前 5（今天的核心难点，你来写！）----
# 提示：
#   counts.items()  -> 得到一堆 (词, 次数) 的元组
#   sorted(..., key=lambda x: x[1], reverse=True) -> 按"次数"从大到小排
#   [ :5 ] -> 只要前 5 个

top5 = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]

# ---- 第 5 步：打印结果 ----
for word, cnt in top5:
    print(word, cnt)


# ============ 参考答案（写完上面再往下看，别偷看）============
# top5 = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
