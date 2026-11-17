# -*- coding: utf-8 -*-
"""参考样例：PDF 解析三库对比 —— 练习/11.17练习_PDF解析.py 里每个结论都能在这里复现

运行：D:\\AAAA\\python.exe 练习\\_参考样例_PDF解析.py
"""
import time
from pathlib import Path

import PyPDF2
import pdfplumber
import pymupdf

素材目录 = Path(r"C:/Users/15816/Downloads")
主素材 = 素材目录 / "《计算机网络基础》复习 题-答案版.pdf"
扫描素材 = 素材目录 / "《大学物理实验（一）》讲义.pdf"
工程素材 = 素材目录 / "2025-2026-1工程数学复习题.pdf"


def 分隔(标题):
    print()
    print("=" * 66)
    print(标题)
    print("=" * 66)


# ---------------------------------------------------------------- 【一】
分隔("【一】三个库怎么打开同一个 PDF（同一份文件，结果一样）")

print("文件：", 主素材.name)
print("大小：%.1f MB" % (主素材.stat().st_size / 1024 / 1024))

print()
print("── PyPDF2 ──")
r = PyPDF2.PdfReader(str(主素材))
print("  len(reader.pages)      =", len(r.pages))
print("  reader.is_encrypted    =", r.is_encrypted)
t = r.pages[0].extract_text()
print("  pages[0].extract_text() = %r" % (t[:50] + "..."))

print()
print("── pdfplumber ──")
with pdfplumber.open(str(主素材)) as pdf:
    print("  len(pdf.pages)         =", len(pdf.pages))
    t2 = pdf.pages[0].extract_text()
    print("  pages[0].extract_text() = %r" % (t2[:50] + "..."))
print("  ⚠️ with 出了块，文件才关闭")

print()
print("── pymupdf ──")
doc = pymupdf.open(str(主素材))
print("  doc.page_count         =", doc.page_count)
t3 = doc[0].get_text()
print("  doc[0].get_text()       = %r" % (t3[:50] + "..."))
print("  ⚠️ pymupdf 不会自动关，必须自己 doc.close()")
doc.close()

print()
print("三个库取到的文字【是不是一回事】？")
r = PyPDF2.PdfReader(str(主素材))
a = r.pages[0].extract_text()
with pdfplumber.open(str(主素材)) as pdf:
    b = pdf.pages[0].extract_text()
d = pymupdf.open(str(主素材))
c = d[0].get_text()
d.close()
print("  字符数：PyPDF2=%d  pdfplumber=%d  pymupdf=%d" % (len(a), len(b), len(c)))
print()
print("  ⭐ 首行对比（同一页，三个库给的开头不一样）：")
print("    PyPDF2    : %r" % a[:20])
print("    pdfplumber: %r" % b[:20])
print("    pymupdf   : %r" % c[:20])
print()
print("  → 页眉「第1 页，共8 页」：pymupdf ✅ 保留 | PyPDF2 ✅ 保留（但没空格）| pdfplumber ❌ 丢掉")
print("  → 空格处理：pymupdf 保留原空格 | PyPDF2/pdfplumber 不加空格")
print("  → ⭐ 所以【校验文本不能直接比字符串】，要比关键词、去空格后比、或只比长度")


# ---------------------------------------------------------------- 【二】
分隔("【二】⭐⭐⭐ 坑 2：扫描图片页提取不到文字（今天最大的坑）")

doc = pymupdf.open(str(扫描素材))
print("文件：", 扫描素材.name)
print("总页数：", doc.page_count)

扫描页 = []
有文字页 = []
for i in range(doc.page_count):
    文字 = doc[i].get_text().strip()
    图片数 = len(doc[i].get_images())
    if len(文字) == 0:
        扫描页.append(i + 1)
    else:
        有文字页.append(i + 1)
    if i < 6:
        print("  第%2d页  文字%4d字  图片%d张  %s" % (
            i + 1, len(文字), 图片数,
            "← 扫描页（无文字层）" if len(文字) == 0 else ""))
doc.close()

print()
print("  有文字的页：%d 页" % len(有文字页))
print("  扫描图片页：%d 页  → %s" % (len(扫描页), 扫描页[:12]))
print("  扫描页区间：第 %d 页 ~ 第 %d 页（连续）" % (扫描页[0], 扫描页[-1]))
print()
print("  ⭐ 这就是真实项目里最常见的坑：")
print("     PDF 看着有 98 页，你以为能全提取，实际只有 54 页有文字。")
print("     剩下 44 页要靠 OCR（本机没装 pytesseract）。")
print()
print("  → 判断扫描页的办法：get_images() 数量 > 0")


# ---------------------------------------------------------------- 【三】
分隔("【三】⭐ 坑 3：页码从 0 开始")

doc = pymupdf.open(str(主素材))
print("  doc[0] = 人的第 1 页：%r" % doc[0].get_text()[:24].replace("\n", " "))
print("  doc[1] = 人的第 2 页：%r" % doc[1].get_text()[:24].replace("\n", " "))
print("  doc[2] = 人的第 3 页：%r" % doc[2].get_text()[:24].replace("\n", " "))
print()
print("  → 人说「第 3 页」= 代码里 doc[2]")
doc.close()


# ---------------------------------------------------------------- 【四】
分隔("【四】⭐ 坑 4：关文件的方式不一样")

print("  pdfplumber：必须 with，出了块才关")
with pdfplumber.open(str(主素材)) as pdf:
    print("    with 块内：len(pdf.pages) =", len(pdf.pages))
print("    with 块外：文件已关闭（不能再用）")
print()
print("  pymupdf：不会自动关，要自己 close()")
doc = pymupdf.open(str(主素材))
print("    close 前：doc.page_count =", doc.page_count)
doc.close()
try:
    doc[0].get_text()
    print("    close 后还能用 → 反直觉")
except Exception as e:
    print("    close 后：%s: %s" % (type(e).__name__, e))
print()
print("  PyPDF2：不用手动关（读文件读完就完）")


# ---------------------------------------------------------------- 【五】
分隔("【五】⭐ 坑 5：表格要页面上真有表格线")

print("  逐页扫一遍，看哪几页有表格：")
for 文件, 标签 in [(主素材, "《计算机网络基础》"), (工程素材, "《工程数学复习题》")]:
    with pdfplumber.open(str(文件)) as pdf:
        有表 = []
        for i, pg in enumerate(pdf.pages[:6]):
            tb = pg.extract_tables()
            if tb:
                有表.append((i + 1, len(tb)))
        print("  %-22s 前6页里有表格的页：%s" % (标签, 有表 if 有表 else "无"))

print()
print("  《计算机网络基础》第 5 页有一张答案对照表，提出来长这样：")
with pdfplumber.open(str(主素材)) as pdf:
    tb = pdf.pages[4].extract_tables()
    for row in tb[0]:
        print("      ", [str(c).replace("\n", "") if c else "" for c in row])

print()
print("  《工程数学复习题》第 4 页：")
with pdfplumber.open(str(工程素材)) as pdf:
    tb = pdf.pages[3].extract_tables()
    for row in tb[0]:
        print("      ", [str(c)[:14] if c else "" for c in row])

print()
print("  ⭐ 关键点：这两份 PDF 的【第 1 页都提取不到表格】，")
print("     但第 4/5 页有 —— 说明【表格在哪页得逐页试】，不能假设。")
print("  → 题目里写着「表格」，不代表第 1 页就有表格线")


# ---------------------------------------------------------------- 【六】
分隔("【六】⭐ 性能对比：98 页物理讲义")

p = 扫描素材
t0 = time.time()
r = PyPDF2.PdfReader(str(p))
_ = [pg.extract_text() for pg in r.pages]
t_pypdf2 = time.time() - t0

t0 = time.time()
with pdfplumber.open(str(p)) as pdf:
    _ = [pg.extract_text() for pg in pdf.pages]
t_plumb = time.time() - t0

t0 = time.time()
d = pymupdf.open(str(p))
_ = [pg.get_text() for pg in d]
d.close()
t_mu = time.time() - t0

print("  PyPDF2       %6.2f 秒" % t_pypdf2)
print("  pdfplumber   %6.2f 秒" % t_plumb)
print("  pymupdf      %6.2f 秒  ⚡ 最快" % t_mu)
print()
print("  pymupdf 比 PyPDF2 快 %.0f 倍，比 pdfplumber 快 %.0f 倍" % (t_pypdf2 / t_mu, t_plumb / t_mu))
print()
print("  → 真实项目里 PDF 有几百页时，这个差别就是「能不能跑完」的差别")


# ---------------------------------------------------------------- 【七】
分隔("【七】⭐ pymupdf 独有的两个能力（另两个库没有）")

doc = pymupdf.open(str(主素材))
pg = doc[0]

print("  ① 搜索关键词位置（另两个库做不到）：")
for 词 in ["时延", "TCP", "IP"]:
    命中 = pg.search_for(词)
    print("     search_for(%-6r) → %d 处，位置 %s" % (词, len(命中),
          [tuple(round(v) for v in r) for r in 命中[:2]]))

print()
print("  ② 按块/按词提取（带坐标）：")
块 = pg.get_text("blocks")
词集 = pg.get_text("words")
print("     get_text('blocks') → %d 个块" % len(块))
print("       第1块: 坐标 %s" % (tuple(round(v) for v in 块[0][:4]),))
print("     get_text('words')  → %d 个词" % len(词集))
print("       第1词: %r 坐标 %s" % (词集[0][4], tuple(round(v) for v in 词集[0][:4])))
doc.close()

print()
print("  → 做「按版面还原」「只取某区域」「找关键词在第几页第几行」时才需要")


# ---------------------------------------------------------------- 【八】
分隔("【八】⭐ 落库：提取出来不存下来等于没做")

import sqlite3

库 = Path(__file__).parent / "_临时_PDF样例.sqlite"
if 库.exists():
    库.unlink()

doc = pymupdf.open(str(主素材))
con = sqlite3.connect(str(库))
cur = con.cursor()
cur.execute("CREATE TABLE 页文本 (页码 INTEGER, 文字 TEXT)")
for i in range(doc.page_count):
    cur.execute("INSERT INTO 页文本 (页码, 文字) VALUES (?, ?)", (i + 1, doc[i].get_text()))
con.commit()
doc.close()

行数 = cur.execute("SELECT COUNT(*) FROM 页文本").fetchone()[0]
print("  存进去 %d 行" % 行数)
cur.execute("SELECT 页码, LENGTH(文字) FROM 页文本")
print("  每页字数：", cur.fetchall())
print("  ⚠️ LENGTH() 是 SQLite 的函数（不是 Python 的 len()）—— 写成 长度() 会报 no such function")
cur.execute("SELECT 文字 FROM 页文本 WHERE 页码 = 1")
print("  抽第1页前50字：", cur.fetchone()[0][:50])
con.close()
库.unlink()
print("  ✅ 已删除临时库（不留在仓库里）")
print()
print("  ⚠️ 这里踩过的坑：")
print("     1) 不 con.commit() → 关连接时数据回滚（行数变 0）")
print("     2) 路径写错 → sqlite3.connect 静默创建一个 0 字节假库，不报错")
print("     3) with sqlite3.connect() 只管事务【不管关连接】→ 要用 contextlib.closing")

print()
print("=" * 66)
print("✅ 参考样例跑完")
print("=" * 66)
