# -*- coding: utf-8 -*-
"""验证候选 B 是否真的存在于用户今天写的 10.21练习.py 的代码路径里。"""
import io, os, re, sys

# 2026-10-27 目录重组后：10.21练习.py 和 文本.txt 都搬到 练习/ 了
练习目录 = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "练习",
)

print("=" * 62)
print("用户 10.21练习.py 的清洗循环（原文）")
print("=" * 62)
src = open(os.path.join(练习目录, "10.21练习.py"), encoding="utf-8").read()
for i, ln in enumerate(src.splitlines(), 1):
    if 5 <= i <= 13:
        print("%2d| %s" % (i, ln))

print()
print("=" * 62)
print("用用户的原文逻辑 + 真实文本.txt 跑一遍")
print("=" * 62)
text = open(os.path.join(练习目录, "文本.txt"), encoding="utf-8").read()
words = text.split()
stopwords = {"the", "is", "and", "to", "in", "a", "of", "that"}

# ❌ 用户当前写法
counts = {}
for w in words:
    w = w.lower().strip(".,!?")
    if w in stopwords:
        continue
    counts[w] = counts.get(w, 0) + 1
print("❌ 用户当前写法 ->", "空串键存在?" , "" in counts, "| 空串计数:", counts.get(""))

print()
print("→ 现在的 文本.txt 里没有【纯标点的独立词】，所以问题没暴露。")
print("→ 但只要原文里出现 \"...\" 或 \"!!!\" 这种独立成词的标点，就会计进去：")
words2 = words + ["...", "!!!"]
counts2 = {}
for w in words2:
    w = w.lower().strip(".,!?")
    if w in stopwords:
        continue
    counts2[w] = counts2.get(w, 0) + 1
print("   加入两个纯标点词后 ->", counts2, "| 空串计数:", counts2.get(""))

print()
print("=" * 62)
print("✅ 修法：strip 之后加 if w 判断")
print("=" * 62)
counts3 = {}
for w in words2:
    w = w.lower().strip(".,!?")
    if not w:          # ← 少了这一行，空串就会进统计
        continue
    if w in stopwords:
        continue
    counts3[w] = counts3.get(w, 0) + 1
print("✅ 加了判断 ->", counts3, "| 空串键存在?", "" in counts3)
